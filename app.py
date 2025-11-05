"""
Flask Backend API สำหรับระบบตรวจจับคำซ้ำอัตโนมัติ
Duplicate Word Detector - Automatic Word Frequency Analysis System
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import os
import base64
import io
import time
import matplotlib
matplotlib.use('Agg')  # ใช้ backend ที่ไม่ต้องการ GUI
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from core.duplicate_word_detector import ThaiDuplicateWordDetector
from core.performance_utils import PerformanceTracker, CacheManager, ParallelProcessor, get_performance_summary
from core.word_categorizer import ParliamentWordCategorizer
from core.pdf_processor import PDFProcessor
from core.database_manager import DatabaseManager
from config.config import *
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# ตั้งค่า matplotlib สำหรับฟอนต์ไทย
import matplotlib.font_manager as fm

# หาฟอนต์ที่มีในระบบ
available_fonts = [f.name for f in fm.fontManager.ttflist]

# ลองหาฟอนต์ที่รองรับภาษาไทย
thai_font_candidates = [
    'Tahoma', 'Arial', 'Microsoft Sans Serif', 'Segoe UI', 
    'Calibri', 'Times New Roman', 'Courier New'
]

selected_font = 'DejaVu Sans'  # default
for font in thai_font_candidates:
    if font in available_fonts:
        selected_font = font
        break

plt.rcParams['font.family'] = selected_font
print(f"ใช้ฟอนต์: {selected_font}")

# สร้างโฟลเดอร์สำหรับเก็บไฟล์ชั่วคราว
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# ตัวแปรสำหรับเก็บข้อมูลการวิเคราะห์
analysis_data = {
    'detector': ThaiDuplicateWordDetector(),
    'categorizer': ParliamentWordCategorizer(),
    'pdf_processor': PDFProcessor(),
    'database': DatabaseManager(),
    'current_analysis': None,
    'performance_tracker': PerformanceTracker()
}


def create_chart_image(chart_type, data, filename):
    """สร้างภาพกราฟและบันทึกเป็นไฟล์"""
    try:
        if chart_type == 'word_frequency':
            words, frequencies = zip(*data)
            
            plt.figure(figsize=(14, 10))
            
            # สร้างกราฟแบบ horizontal bar ด้วยสี Vibrant theme
            colors = ['#007BFF', '#FF5733', '#FFEB3B', '#4A90E2', '#FF8A65', 
                     '#FFD54F', '#212121', '#FF7043', '#FFC107', '#FF9800']
            bars = plt.barh(range(len(words)), frequencies, 
                           color=[colors[i % len(colors)] for i in range(len(words))])
            
            # ตั้งค่าแกน Y
            plt.yticks(range(len(words)), words, fontsize=10)
            plt.gca().invert_yaxis()
            
            # ตั้งค่าแกน X
            plt.xlabel('ความถี่', fontsize=12, fontweight='bold')
            plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
            
            # เพิ่มค่าความถี่บนแท่งกราฟ
            for i, (word, freq) in enumerate(zip(words, frequencies)):
                plt.text(freq + 0.1, i, str(freq), 
                        va='center', ha='left', fontsize=9, fontweight='bold')
            
            # ตั้งค่าหัวข้อ
            plt.title(f'คำที่มีความถี่สูงสุด {len(words)} คำ', 
                     fontsize=14, fontweight='bold', pad=20)
            
            # เพิ่ม grid
            plt.grid(axis='x', alpha=0.3, linestyle='--')
            
            # ปรับ layout
            plt.tight_layout()
            
        # บันทึกไฟล์
        filepath = os.path.join(app.config['STATIC_FOLDER'], filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None


@app.route('/')
def index():
    """หน้าแรกของ Dashboard"""
    return render_template('dashboard.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """API สำหรับวิเคราะห์ข้อความ"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        filter_pos = data.get('filter_pos', True)
        target_pos = data.get('target_pos', None)
        
        if not text:
            return jsonify({'error': 'ไม่มีข้อความที่ส่งมา'}), 400
        
        # วิเคราะห์ข้อความ
        detector = analysis_data['detector']
        categorizer = analysis_data['categorizer']
        result = detector.analyze_text(text, filter_pos=filter_pos, target_pos=target_pos)
        
        # สร้างกราฟ
        top_words = detector.get_most_frequent_words(10)
        
        # สร้างกราฟความถี่
        freq_chart_path = create_chart_image('word_frequency', top_words, 'word_frequency.png')
        
        # จัดหมวดหมู่คำ
        word_freq_dict = dict(result['word_frequency'])
        categorized_words = categorizer.categorize_words(word_freq_dict)
        category_summary = categorizer.get_category_summary(categorized_words)
        top_words_by_category = categorizer.get_top_words_by_category(categorized_words, top_n=5)
        
        # บันทึกข้อมูลการวิเคราะห์
        analysis_data['current_analysis'] = {
            'text': text,
            'result': result,
            'top_words': top_words,
            'categorized_words': categorized_words,
            'category_summary': category_summary,
            'top_words_by_category': top_words_by_category,
            'charts': {
                'frequency_chart': freq_chart_path
            }
        }
        
        return jsonify({
            'success': True,
            'data': {
                'total_words': result['total_words'],
                'unique_words': result['unique_words'],
                'word_frequency': word_freq_dict,
                'pos_frequency': dict(result['pos_frequency']),
                'top_words': top_words,
                'categorized_words': {k: dict(v) for k, v in categorized_words.items()},
                'category_summary': [{'category': cat, 'unique_words': unique, 'total_frequency': freq} 
                                    for cat, unique, freq in category_summary],
                'top_words_by_category': {k: list(v) for k, v in top_words_by_category.items()},
                'charts': {
                    'frequency_chart': f'/static/word_frequency.png'
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/compare', methods=['POST'])
def compare_texts():
    """API สำหรับเปรียบเทียบข้อความหลายข้อความ"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts or len(texts) < 2:
            return jsonify({'error': 'ต้องมีข้อความอย่างน้อย 2 ข้อความ'}), 400
        
        # เปรียบเทียบข้อความ
        analyzer = analysis_data['analyzer']
        comparison_result = analyzer.compare_texts(texts)
        
        # สร้างกราฟเปรียบเทียบ
        comparison_chart_path = None
        if comparison_result['individual_results']:
            top_words = sorted(comparison_result['overall_frequency'].items(), 
                             key=lambda x: x[1], reverse=True)[:15]
            
            comparison_chart_path = create_chart_image(
                'word_frequency', 
                top_words, 
                'comparison_chart.png'
            )
        
        return jsonify({
            'success': True,
            'data': {
                'comparison_stats': comparison_result['comparison_stats'],
                'individual_results': comparison_result['individual_results'],
                'overall_frequency': comparison_result['overall_frequency'],
                'comparison_chart': f'/static/comparison_chart.png' if comparison_chart_path else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API สำหรับอัปโหลดไฟล์ (รองรับ .txt และ .pdf)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ไม่มีไฟล์ที่ส่งมา'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ไม่ได้เลือกไฟล์'}), 400
        
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            content = ""
            file_type = ""
            extraction_method = ""
            
            # ตรวจสอบประเภทไฟล์
            if filename.lower().endswith('.pdf'):
                # ประมวลผล PDF
                pdf_processor = analysis_data['pdf_processor']
                success, content, method = pdf_processor.extract_text_from_pdf(filepath)
                
                if not success:
                    # ลบไฟล์ที่อัปโหลด
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return jsonify({'error': f'ไม่สามารถแปลง PDF เป็น text ได้: {method}'}), 400
                
                file_type = "PDF"
                extraction_method = method
                
            else:
                # อ่านไฟล์ text ธรรมดา
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_type = "Text"
                    extraction_method = "Direct Read"
                except UnicodeDecodeError:
                    # ลองใช้ encoding อื่น
                    try:
                        with open(filepath, 'r', encoding='cp874') as f:
                            content = f.read()
                        file_type = "Text (TIS-620)"
                        extraction_method = "Direct Read (TIS-620)"
                    except:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        return jsonify({'error': 'ไม่สามารถอ่านไฟล์ได้ กรุณาตรวจสอบ encoding'}), 400
            
            # วิเคราะห์ไฟล์
            if not content.strip():
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': 'ไฟล์ว่างเปล่าหรือไม่มีข้อความ'}), 400
            
            detector = analysis_data['detector']
            categorizer = analysis_data['categorizer']
            result = detector.analyze_text(content, filter_pos=True)
            
            # สร้างกราฟ
            top_words = detector.get_most_frequent_words(20)
            freq_chart_path = create_chart_image('word_frequency', top_words, f'{filename}_frequency.png')
            
            # จัดหมวดหมู่คำ
            word_freq_dict = dict(result['word_frequency'])
            categorized_words = categorizer.categorize_words(word_freq_dict)
            category_summary = categorizer.get_category_summary(categorized_words)
            top_words_by_category = categorizer.get_top_words_by_category(categorized_words, top_n=5)
            
            # ลบไฟล์หลังประมวลผลเสร็จ
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
            
            return jsonify({
                'success': True,
                'data': {
                    'filename': filename,
                    'file_type': file_type,
                    'extraction_method': extraction_method,
                    'content': content[:500] + '...' if len(content) > 500 else content,
                    'total_words': result['total_words'],
                    'unique_words': result['unique_words'],
                    'word_frequency': word_freq_dict,
                    'top_words': top_words,
                    'categorized_words': {k: dict(v) for k, v in categorized_words.items()},
                    'category_summary': [{'category': cat, 'unique_words': unique, 'total_frequency': freq} 
                                        for cat, unique, freq in category_summary],
                    'top_words_by_category': {k: list(v) for k, v in top_words_by_category.items()},
                    'charts': {
                        'frequency_chart': f'/static/{filename}_frequency.png'
                    }
                }
            })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/export', methods=['POST'])
def export_results():
    """API สำหรับส่งออกผลลัพธ์"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'excel')
        filename = data.get('filename', 'analysis_results')
        
        if not analysis_data['current_analysis']:
            return jsonify({'error': 'ไม่มีข้อมูลการวิเคราะห์'}), 400
        
        detector = analysis_data['detector']
        
        if export_type == 'json':
            # ส่งออกเป็น JSON
            json_data = {
                'analysis_result': analysis_data['current_analysis']['result'],
                'top_words': analysis_data['current_analysis']['top_words'],
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            json_path = os.path.join(app.config['STATIC_FOLDER'], f'{filename}.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            return jsonify({
                'success': True,
                'download_url': f'/static/{filename}.json'
            })
        
        else:
            return jsonify({'error': 'รูปแบบการส่งออกไม่ถูกต้อง'}), 400
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/reset', methods=['POST'])
def reset_analysis():
    """API สำหรับรีเซ็ตการวิเคราะห์"""
    try:
        detector = analysis_data['detector']
        detector.reset()
        analysis_data['current_analysis'] = None
        
        return jsonify({'success': True, 'message': 'รีเซ็ตการวิเคราะห์เรียบร้อยแล้ว'})
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/static/<filename>')
def static_files(filename):
    """ให้บริการไฟล์ static"""
    return send_from_directory(app.config['STATIC_FOLDER'], filename)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API สำหรับดึงสถิติการใช้งาน"""
    try:
        detector = analysis_data['detector']
        
        stats = {
            'total_texts_analyzed': len(detector.processed_texts),
            'total_words_processed': sum(text_data['total_words'] for text_data in detector.processed_texts),
            'total_unique_words': len(detector.word_frequency),
            'most_frequent_word': detector.word_frequency.most_common(1)[0] if detector.word_frequency else None
        }
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/performance', methods=['GET'])
def get_performance_stats():
    """API สำหรับดึงสถิติประสิทธิภาพ"""
    try:
        detector = analysis_data['detector']
        performance_stats = detector.get_performance_stats()
        
        return jsonify({'success': True, 'data': performance_stats})
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500




@app.route('/api/check-pdf-support', methods=['GET'])
def check_pdf_support():
    """ตรวจสอบว่ารองรับ PDF และ OCR หรือไม่"""
    try:
        pdf_processor = analysis_data['pdf_processor']
        support_info = pdf_processor.supported_methods
        instructions = pdf_processor.get_installation_instructions()
        
        return jsonify({
            'success': True,
            'data': {
                'supported_methods': support_info,
                'installation_instructions': instructions
            }
        })
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


# ==================== Database API Endpoints ====================

@app.route('/api/db/save', methods=['POST'])
def save_to_database():
    """บันทึกผลการวิเคราะห์ลงฐานข้อมูล"""
    try:
        data = request.get_json()
        title = data.get('title', 'การวิเคราะห์')
        source_type = data.get('source_type', 'text')
        source_filename = data.get('source_filename', '')
        text_content = data.get('text_content', '')
        analysis_result = data.get('analysis_result', {})
        
        db = analysis_data['database']
        analysis_id = db.save_analysis(
            title=title,
            source_type=source_type,
            source_filename=source_filename,
            text_content=text_content,
            analysis_result=analysis_result
        )
        
        return jsonify({
            'success': True,
            'data': {
                'analysis_id': analysis_id,
                'message': 'บันทึกลงฐานข้อมูลเรียบร้อยแล้ว'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/list', methods=['GET'])
def list_analyses():
    """ดึงรายการการวิเคราะห์ทั้งหมด"""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        db = analysis_data['database']
        analyses = db.get_all_analyses(limit=limit, offset=offset)
        total_count = db.get_total_count()
        
        return jsonify({
            'success': True,
            'data': {
                'analyses': analyses,
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/get/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """ดึงข้อมูลการวิเคราะห์ตาม ID"""
    try:
        db = analysis_data['database']
        analysis = db.get_analysis_by_id(analysis_id)
        
        if analysis:
            return jsonify({
                'success': True,
                'data': analysis
            })
        else:
            return jsonify({'error': 'ไม่พบข้อมูลการวิเคราะห์'}), 404
            
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/delete/<int:analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    """ลบการวิเคราะห์"""
    try:
        db = analysis_data['database']
        success = db.delete_analysis(analysis_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'ลบข้อมูลเรียบร้อยแล้ว'
            })
        else:
            return jsonify({'error': 'ไม่พบข้อมูลที่ต้องการลบ'}), 404
            
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/update/<int:analysis_id>', methods=['PUT'])
def update_analysis(analysis_id):
    """อัพเดทชื่อการวิเคราะห์"""
    try:
        data = request.get_json()
        new_title = data.get('title')
        
        if not new_title:
            return jsonify({'error': 'กรุณาระบุชื่อใหม่'}), 400
        
        db = analysis_data['database']
        success = db.update_analysis_title(analysis_id, new_title)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'อัพเดทชื่อเรียบร้อยแล้ว'
            })
        else:
            return jsonify({'error': 'ไม่พบข้อมูลที่ต้องการอัพเดท'}), 404
            
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/search', methods=['GET'])
def search_analyses():
    """ค้นหาการวิเคราะห์"""
    try:
        keyword = request.args.get('keyword', '')
        limit = int(request.args.get('limit', 50))
        
        if not keyword:
            return jsonify({'error': 'กรุณาระบุคำค้นหา'}), 400
        
        db = analysis_data['database']
        results = db.search_analyses(keyword, limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'keyword': keyword,
                'count': len(results)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/statistics', methods=['GET'])
def get_db_statistics():
    """ดึงสถิติการใช้งานจากฐานข้อมูล"""
    try:
        db = analysis_data['database']
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/trends', methods=['GET'])
def get_category_trends():
    """ดึงแนวโน้มหมวดหมู่"""
    try:
        days = int(request.args.get('days', 30))
        
        db = analysis_data['database']
        trends = db.get_category_trends(days=days)
        
        return jsonify({
            'success': True,
            'data': {
                'trends': trends,
                'period_days': days
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/tags', methods=['GET'])
def get_all_tags():
    """ดึงรายการ tags ทั้งหมด"""
    try:
        db = analysis_data['database']
        tags = db.get_tags()
        
        return jsonify({
            'success': True,
            'data': tags
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/tags/create', methods=['POST'])
def create_tag():
    """สร้าง tag ใหม่"""
    try:
        data = request.get_json()
        name = data.get('name')
        color = data.get('color', '#007BFF')
        
        if not name:
            return jsonify({'error': 'กรุณาระบุชื่อ tag'}), 400
        
        db = analysis_data['database']
        tag_id = db.add_tag(name, color)
        
        return jsonify({
            'success': True,
            'data': {
                'tag_id': tag_id,
                'message': 'สร้าง tag เรียบร้อยแล้ว'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/tags/<int:analysis_id>/<int:tag_id>', methods=['POST'])
def add_tag_to_analysis(analysis_id, tag_id):
    """ติด tag ให้กับการวิเคราะห์"""
    try:
        db = analysis_data['database']
        success = db.tag_analysis(analysis_id, tag_id)
        
        return jsonify({
            'success': success,
            'message': 'ติด tag เรียบร้อยแล้ว' if success else 'Tag นี้ถูกติดไว้แล้ว'
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/db/export/<int:analysis_id>', methods=['GET'])
def export_analysis_json(analysis_id):
    """ส่งออกการวิเคราะห์เป็น JSON"""
    try:
        db = analysis_data['database']
        json_data = db.export_to_json(analysis_id)
        
        if json_data:
            return jsonify({
                'success': True,
                'data': json.loads(json_data)
            })
        else:
            return jsonify({'error': 'ไม่พบข้อมูล'}), 404
            
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


if __name__ == '__main__':
    # สร้างโฟลเดอร์ templates
    os.makedirs('templates', exist_ok=True)
    
    # ตรวจสอบ PDF support
    pdf_processor = analysis_data['pdf_processor']
    support = pdf_processor.supported_methods
    
    print("=" * 70)
    print("🏛️  ระบบตรวจจับคำซ้ำอัตโนมัติสำหรับรัฐสภาไทย")
    print("    Duplicate Word Detector System for Thai Parliament")
    print("=" * 70)
    print("📊 เข้าใช้งานที่: http://localhost:5000")
    print("-" * 70)
    print("📂 รองรับไฟล์:")
    print("   - Text Files (.txt)")
    print(f"   - PDF Files (.pdf) - Text: {'✅' if support['pdfplumber'] or support['pypdf2'] else '❌'}")
    print(f"   - PDF Files (.pdf) - Image (OCR): {'✅' if support['ocr'] else '❌'}")
    print("-" * 70)
    print("🔧 API Endpoints:")
    print("   Analysis:")
    print("   - POST /api/analyze              - วิเคราะห์ข้อความและตรวจสอบคำซ้ำ")
    print("   - POST /api/upload               - อัปโหลดไฟล์ (txt/pdf)")
    print("   - POST /api/compare              - เปรียบเทียบข้อความ")
    print("   - POST /api/export               - ส่งออกผลลัพธ์")
    print("")
    print("   Database:")
    print("   - POST   /api/db/save            - บันทึกผลลงฐานข้อมูล")
    print("   - GET    /api/db/list            - ดึงรายการทั้งหมด")
    print("   - GET    /api/db/get/<id>        - ดึงข้อมูลตาม ID")
    print("   - DELETE /api/db/delete/<id>     - ลบการวิเคราะห์")
    print("   - PUT    /api/db/update/<id>     - อัพเดทชื่อ")
    print("   - GET    /api/db/search          - ค้นหาการวิเคราะห์")
    print("   - GET    /api/db/statistics      - สถิติจากฐานข้อมูล")
    print("   - GET    /api/db/trends          - แนวโน้มหมวดหมู่")
    print("   - GET    /api/db/tags            - ดึงรายการ tags")
    print("   - POST   /api/db/tags/create     - สร้าง tag ใหม่")
    print("=" * 70)
    
    # แสดงคำเตือนถ้าไม่มี libraries สำหรับ PDF
    if not (support['pdfplumber'] or support['pypdf2']):
        print("⚠️  คำเตือน: ไม่พบ PDF libraries")
        print("   ติดตั้ง: pip install PyPDF2 pdfplumber")
    
    if not support['ocr']:
        print("ℹ️  ข้อมูล: OCR ไม่พร้อมใช้งาน (สำหรับ PDF ภาพ)")
        print("   ติดตั้ง: pip install pdf2image pytesseract")
        print("   และติดตั้ง Tesseract-OCR: https://github.com/tesseract-ocr/tesseract")
    
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
