"""
โมเดลตรวจจับคำซ้ำจากข้อความภาษาไทย
ใช้ PyThaiNLP สำหรับการวิเคราะห์ Part-of-Speech และการนับความถี่ของคำ
ปรับปรุงประสิทธิภาพด้วย caching และ parallel processing
"""

import re
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# PyThaiNLP imports
import pythainlp
from pythainlp.tokenize import word_tokenize
from pythainlp.tag import pos_tag
from pythainlp.corpus import thai_stopwords
from pythainlp.util import normalize

# Import performance utilities
from .performance_utils import (
    PerformanceTracker, CacheManager, ParallelProcessor, 
    timing_decorator, get_performance_summary
)


class ThaiDuplicateWordDetector:
    """
    คลาสสำหรับตรวจจับคำซ้ำในข้อความภาษาไทย
    รองรับการกรองตาม Part-of-Speech และการวิเคราะห์ความถี่
    ปรับปรุงประสิทธิภาพด้วย caching และ parallel processing
    """
    
    def __init__(self):
        """เริ่มต้นโมเดล"""
        self.stopwords = set(thai_stopwords())
        self.word_frequency = Counter()
        self.pos_frequency = defaultdict(Counter)
        self.processed_texts = []
        
        # เพิ่มประสิทธิภาพ
        self.performance_tracker = PerformanceTracker()
        self.cache_manager = CacheManager()
        self.parallel_processor = ParallelProcessor()
        self._lock = threading.Lock()
        
    @timing_decorator("preprocess_text")
    def preprocess_text(self, text: str) -> str:
        """
        ทำความสะอาดข้อความก่อนการประมวลผล
        
        Args:
            text (str): ข้อความต้นฉบับ
            
        Returns:
            str: ข้อความที่ทำความสะอาดแล้ว
        """
        # ตรวจสอบ cache ก่อน
        cache_key = f"preprocess_{hash(text)}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # ลบตัวอักษรพิเศษและตัวเลขที่ไม่จำเป็น (รองรับทั้งไทยและอังกฤษ)
        text = re.sub(r'[^\u0E00-\u0E7F\u0041-\u005A\u0061-\u007A\s]', '', text)
        
        # ลบช่องว่างที่เกิน
        text = re.sub(r'\s+', ' ', text)
        
        # ปรับมาตรฐานข้อความ
        text = normalize(text)
        
        result = text.strip()
        
        # เก็บใน cache
        self.cache_manager.set(cache_key, result)
        
        return result
    
    @timing_decorator("tokenize_and_tag")
    def tokenize_and_tag(self, text: str) -> List[Tuple[str, str]]:
        """
        แยกคำและติดแท็ก Part-of-Speech
        
        Args:
            text (str): ข้อความที่ต้องการประมวลผล
            
        Returns:
            List[Tuple[str, str]]: รายการของ (คำ, POS tag)
        """
        # ตรวจสอบ cache ก่อน
        cache_key = f"tokenize_{hash(text)}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # แยกคำ (รองรับทั้งไทยและอังกฤษ)
        tokens = word_tokenize(text, engine='newmm')
        
        # ติดแท็ก POS (รองรับทั้งไทยและอังกฤษ)
        pos_tags = pos_tag(tokens, engine='perceptron')
        
        # เพิ่มการรองรับภาษาอังกฤษ
        enhanced_pos_tags = []
        for token, pos in pos_tags:
            # ถ้าเป็นคำภาษาอังกฤษ ให้กำหนด POS tag
            if re.match(r'^[a-zA-Z]+$', token):
                if len(token) > 3:
                    enhanced_pos_tags.append((token, 'NCMN'))  # คำนาม
                else:
                    enhanced_pos_tags.append((token, 'VACT'))  # กริยา
            else:
                enhanced_pos_tags.append((token, pos))
        
        # เก็บใน cache
        self.cache_manager.set(cache_key, enhanced_pos_tags)
        
        return enhanced_pos_tags
    
    def filter_by_pos(self, pos_tags: List[Tuple[str, str]], 
                      target_pos: List[str] = None) -> List[Tuple[str, str]]:
        """
        กรองคำตาม Part-of-Speech
        
        Args:
            pos_tags (List[Tuple[str, str]]): รายการของ (คำ, POS tag)
            target_pos (List[str]): รายการ POS tags ที่ต้องการ
            
        Returns:
            List[Tuple[str, str]]: คำที่กรองแล้ว
        """
        if target_pos is None:
            # กรองเฉพาะคำนามและกริยา
            target_pos = ['NOUN', 'VERB', 'NCMN', 'VACT', 'VSTA']
        
        filtered = []
        for word, pos in pos_tags:
            # กรองคำหยุดและคำสั้น
            if (word not in self.stopwords and 
                len(word) > 1 and 
                any(tag in pos for tag in target_pos)):
                filtered.append((word, pos))
        
        return filtered
    
    def analyze_text(self, text: str, 
                    filter_pos: bool = True,
                    target_pos: List[str] = None,
                    track_time: bool = True) -> Dict:
        """
        วิเคราะห์ข้อความและนับความถี่ของคำ
        
        Args:
            text (str): ข้อความที่ต้องการวิเคราะห์
            filter_pos (bool): ต้องการกรองตาม POS หรือไม่
            target_pos (List[str]): รายการ POS tags ที่ต้องการ
            track_time (bool): ต้องการติดตามเวลาหรือไม่
            
        Returns:
            Dict: ผลการวิเคราะห์
        """
        if track_time:
            self.performance_tracker.start_timing("analyze_text")
        
        # ทำความสะอาดข้อความ
        cleaned_text = self.preprocess_text(text)
        
        # แยกคำและติดแท็ก POS
        pos_tags = self.tokenize_and_tag(cleaned_text)
        
        # กรองตาม POS ถ้าต้องการ
        if filter_pos:
            pos_tags = self.filter_by_pos(pos_tags, target_pos)
        
        # นับความถี่ของคำ
        word_counts = Counter([word for word, pos in pos_tags])
        
        # นับความถี่ของ POS
        pos_counts = Counter([pos for word, pos in pos_tags])
        
        # บันทึกข้อมูล (ใช้ lock เพื่อความปลอดภัย)
        with self._lock:
            self.word_frequency.update(word_counts)
            for word, pos in pos_tags:
                self.pos_frequency[word][pos] += 1
            
            self.processed_texts.append({
                'original_text': text,
                'cleaned_text': cleaned_text,
                'word_count': len(word_counts),
                'total_words': len(pos_tags),
                'word_frequency': word_counts,
                'pos_frequency': pos_counts,
                'filtered_words': pos_tags,
                'analysis_time': time.time()
            })
        
        result = {
            'word_frequency': word_counts,
            'pos_frequency': pos_counts,
            'total_words': len(pos_tags),
            'unique_words': len(word_counts),
            'filtered_words': pos_tags
        }
        
        if track_time:
            duration = self.performance_tracker.end_timing("analyze_text")
            result['processing_time'] = duration
        
        return result
    
    def get_most_frequent_words(self, n: int = 20) -> List[Tuple[str, int]]:
        """
        ดึงคำที่มีความถี่สูงสุด
        
        Args:
            n (int): จำนวนคำที่ต้องการ
            
        Returns:
            List[Tuple[str, int]]: รายการคำและความถี่
        """
        return self.word_frequency.most_common(n)
    
    def get_word_pos_distribution(self, word: str) -> Dict[str, int]:
        """
        ดึงการกระจายของ POS tags สำหรับคำที่กำหนด
        
        Args:
            word (str): คำที่ต้องการดูการกระจาย
            
        Returns:
            Dict[str, int]: การกระจายของ POS tags
        """
        return dict(self.pos_frequency[word])
    
    def create_word_frequency_chart(self, n: int = 20, 
                                  figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        สร้างกราฟแสดงความถี่ของคำ
        
        Args:
            n (int): จำนวนคำที่ต้องการแสดง
            figsize (Tuple[int, int]): ขนาดของกราฟ
            
        Returns:
            plt.Figure: กราฟที่สร้างแล้ว
        """
        top_words = self.get_most_frequent_words(n)
        
        if not top_words:
            print("ไม่มีข้อมูลคำที่พบ")
            return None
        
        words, frequencies = zip(*top_words)
        
        plt.figure(figsize=figsize)
        plt.barh(range(len(words)), frequencies)
        plt.yticks(range(len(words)), words)
        plt.xlabel('ความถี่')
        plt.title(f'คำที่มีความถี่สูงสุด {n} คำ')
        plt.gca().invert_yaxis()
        
        # แก้ไขแกน X ให้แสดงจำนวนเต็ม
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_wordcloud(self, max_words: int = 100, 
                        figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        สร้าง Word Cloud
        
        Args:
            max_words (int): จำนวนคำสูงสุดใน Word Cloud
            figsize (Tuple[int, int]): ขนาดของกราฟ
            
        Returns:
            plt.Figure: Word Cloud ที่สร้างแล้ว
        """
        if not self.word_frequency:
            print("ไม่มีข้อมูลคำที่พบ")
            return None
        
        try:
            # สร้าง Word Cloud โดยไม่ใช้ฟอนต์เฉพาะ
            wordcloud = WordCloud(
                width=figsize[0]*100,
                height=figsize[1]*100,
                background_color='white',
                max_words=max_words,
                colormap='viridis',
                font_step=1,
                relative_scaling=0.5
            ).generate_from_frequencies(self.word_frequency)
            
            plt.figure(figsize=figsize)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Word Cloud ของคำที่พบ')
            
        except Exception as e:
            print(f"Error creating wordcloud: {e}")
            # สร้างกราฟแทน Word Cloud
            top_words = self.get_most_frequent_words(20)
            if top_words:
                words, frequencies = zip(*top_words)
                plt.figure(figsize=figsize)
                plt.barh(range(len(words)), frequencies)
                plt.yticks(range(len(words)), words)
                plt.xlabel('ความถี่')
                plt.title('คำที่มีความถี่สูงสุด (แทน Word Cloud)')
                plt.gca().invert_yaxis()
                
                # แก้ไขแกน X ให้แสดงจำนวนเต็ม
                plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
            else:
                plt.figure(figsize=figsize)
                plt.text(0.5, 0.5, 'ไม่มีข้อมูลคำ', ha='center', va='center', fontsize=16)
                plt.axis('off')
                plt.title('ไม่มีข้อมูลคำ')
        
        return plt.gcf()
    
    def create_interactive_chart(self, n: int = 20) -> go.Figure:
        """
        สร้างกราฟแบบ Interactive ด้วย Plotly
        
        Args:
            n (int): จำนวนคำที่ต้องการแสดง
            
        Returns:
            go.Figure: กราฟ Interactive
        """
        top_words = self.get_most_frequent_words(n)
        
        if not top_words:
            print("ไม่มีข้อมูลคำที่พบ")
            return None
        
        words, frequencies = zip(*top_words)
        
        fig = go.Figure(data=[
            go.Bar(
                x=frequencies,
                y=words,
                orientation='h',
                text=frequencies,
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>ความถี่: %{x}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f'คำที่มีความถี่สูงสุด {n} คำ',
            xaxis_title='ความถี่',
            yaxis_title='คำ',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def export_results(self, filename: str = 'word_analysis_results.xlsx', language: str = 'mixed'):
        """
        ส่งออกผลการวิเคราะห์เป็นไฟล์ Excel
        
        Args:
            filename (str): ชื่อไฟล์ที่ต้องการบันทึก
            language (str): ภาษาสำหรับการส่งออก ('mixed' = ทั้งไทยและอังกฤษ)
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # แผ่นข้อมูลความถี่ของคำ (ภาษาไทย)
            word_freq_df_thai = pd.DataFrame(
                self.word_frequency.most_common(),
                columns=['คำ', 'ความถี่']
            )
            word_freq_df_thai.to_excel(writer, sheet_name='ความถี่คำ', index=False)
            
            # แผ่นข้อมูลความถี่ของคำ (ภาษาอังกฤษ)
            word_freq_df_eng = pd.DataFrame(
                self.word_frequency.most_common(),
                columns=['Word', 'Frequency']
            )
            word_freq_df_eng.to_excel(writer, sheet_name='Word Frequency', index=False)
            
            # แผ่นข้อมูลสรุปการวิเคราะห์ (ภาษาไทย)
            summary_data_thai = []
            for i, text_data in enumerate(self.processed_texts):
                summary_data_thai.append({
                    'ข้อความที่': i+1,
                    'จำนวนคำทั้งหมด': text_data['total_words'],
                    'จำนวนคำเฉพาะ': text_data['word_count'],
                    'คำที่ซ้ำมากที่สุด': text_data['word_frequency'].most_common(1)[0][0] if text_data['word_frequency'] else 'ไม่มี',
                    'ความถี่สูงสุด': text_data['word_frequency'].most_common(1)[0][1] if text_data['word_frequency'] else 0
                })
            
            summary_df_thai = pd.DataFrame(summary_data_thai)
            summary_df_thai.to_excel(writer, sheet_name='สรุปการวิเคราะห์', index=False)
            
            # แผ่นข้อมูลสรุปการวิเคราะห์ (ภาษาอังกฤษ)
            summary_data_eng = []
            for i, text_data in enumerate(self.processed_texts):
                summary_data_eng.append({
                    'Text #': i+1,
                    'Total Words': text_data['total_words'],
                    'Unique Words': text_data['word_count'],
                    'Most Frequent Word': text_data['word_frequency'].most_common(1)[0][0] if text_data['word_frequency'] else 'None',
                    'Max Frequency': text_data['word_frequency'].most_common(1)[0][1] if text_data['word_frequency'] else 0
                })
            
            summary_df_eng = pd.DataFrame(summary_data_eng)
            summary_df_eng.to_excel(writer, sheet_name='Analysis Summary', index=False)
    
    def analyze_multiple_texts(self, texts: List[str], 
                              filter_pos: bool = True,
                              target_pos: List[str] = None,
                              parallel: bool = True) -> List[Dict]:
        """
        วิเคราะห์ข้อความหลายข้อความแบบขนาน
        
        Args:
            texts (List[str]): รายการข้อความที่ต้องการวิเคราะห์
            filter_pos (bool): ต้องการกรองตาม POS หรือไม่
            target_pos (List[str]): รายการ POS tags ที่ต้องการ
            parallel (bool): ใช้การประมวลผลแบบขนานหรือไม่
            
        Returns:
            List[Dict]: รายการผลการวิเคราะห์
        """
        if parallel and len(texts) > 1:
            # ใช้การประมวลผลแบบขนาน
            def analyze_single_text(text):
                return self.analyze_text(text, filter_pos, target_pos, track_time=False)
            
            results = self.parallel_processor.process_texts_parallel(texts, analyze_single_text)
        else:
            # ใช้การประมวลผลแบบปกติ
            results = []
            for text in texts:
                result = self.analyze_text(text, filter_pos, target_pos, track_time=False)
                results.append(result)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """ดึงสถิติประสิทธิภาพ"""
        return {
            'performance_tracker': self.performance_tracker.get_stats(),
            'cache_stats': self.cache_manager.get_stats(),
            'total_texts_processed': len(self.processed_texts),
            'total_words_processed': sum(text_data['total_words'] for text_data in self.processed_texts),
            'average_processing_time': self.performance_tracker.get_average_timing("analyze_text")
        }
    
    def clear_cache(self):
        """ล้าง cache"""
        self.cache_manager.clear()
    
    def reset(self):
        """รีเซ็ตข้อมูลทั้งหมด"""
        with self._lock:
            self.word_frequency.clear()
            self.pos_frequency.clear()
            self.processed_texts.clear()
            self.performance_tracker = PerformanceTracker()
            self.cache_manager.clear()


def main():
    """ฟังก์ชันหลักสำหรับการทดสอบ"""
    # สร้างโมเดล
    detector = ThaiDuplicateWordDetector()
    
    # ข้อความตัวอย่าง
    sample_texts = [
        "ประเทศไทยเป็นประเทศที่สวยงาม ประเทศไทยมีวัฒนธรรมที่หลากหลาย ประเทศไทยมีอาหารที่อร่อย",
        "การเรียนภาษาไทยเป็นเรื่องสำคัญ การเรียนภาษาไทยช่วยให้เข้าใจวัฒนธรรม การเรียนภาษาไทยเป็นประโยชน์",
        "เทคโนโลยีใหม่ๆ ทำให้ชีวิตสะดวกขึ้น เทคโนโลยีใหม่ๆ ช่วยในการทำงาน เทคโนโลยีใหม่ๆ มีประโยชน์มาก"
    ]
    
    print("=== การวิเคราะห์คำซ้ำในข้อความภาษาไทย ===\n")
    
    # วิเคราะห์ข้อความแต่ละข้อความ
    for i, text in enumerate(sample_texts, 1):
        print(f"ข้อความที่ {i}: {text}")
        result = detector.analyze_text(text)
        print(f"จำนวนคำทั้งหมด: {result['total_words']}")
        print(f"จำนวนคำเฉพาะ: {result['unique_words']}")
        print(f"คำที่ซ้ำมากที่สุด: {result['word_frequency'].most_common(3)}")
        print("-" * 50)
    
    # แสดงผลรวม
    print("\n=== ผลรวมการวิเคราะห์ ===")
    print(f"คำที่มีความถี่สูงสุด 10 คำ:")
    for word, freq in detector.get_most_frequent_words(10):
        print(f"  {word}: {freq} ครั้ง")
    
    # สร้างกราฟ
    print("\nกำลังสร้างกราฟ...")
    detector.create_word_frequency_chart(15)
    plt.savefig('word_frequency_chart.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # สร้าง Word Cloud
    detector.create_wordcloud()
    plt.savefig('wordcloud.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # สร้างกราฟ Interactive
    interactive_fig = detector.create_interactive_chart(15)
    if interactive_fig:
        interactive_fig.write_html('interactive_word_chart.html')
        interactive_fig.show()
    
    # ส่งออกผลลัพธ์
    detector.export_results()
    print("\nผลการวิเคราะห์ถูกบันทึกในไฟล์ 'word_analysis_results.xlsx'")


if __name__ == "__main__":
    main()
