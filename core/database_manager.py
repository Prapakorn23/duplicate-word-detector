"""
Database Manager with Multi-Database Support
รองรับ SQLite, PostgreSQL, และ MySQL
"""

from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool, NullPool
from contextlib import contextmanager
import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from .models import Base, AnalysisRecord, WordFrequency, Category, CategoryWord, Tag


class DatabaseManager:
    """จัดการฐานข้อมูลรองรับหลาย engines"""
    
    def __init__(self, database_url: str = None):
        """
        สร้าง DatabaseManager
        
        Args:
            database_url: Database connection string
                - SQLite: 'sqlite:///data/parliament_words.db'
                - PostgreSQL: 'postgresql://user:password@localhost/dbname'
                - MySQL: 'mysql+pymysql://user:password@localhost/dbname'
        """
        # ใช้ environment variable หรือ default เป็น SQLite
        if database_url is None:
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///data/parliament_words.db')
        
        self.database_url = database_url
        self.engine = self._create_engine(database_url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        # สร้างตารางทั้งหมด
        self._create_tables()
    
    def _create_engine(self, database_url: str):
        """สร้าง SQLAlchemy engine ตาม database type"""
        # ตรวจสอบว่าเป็น SQLite
        if database_url.startswith('sqlite'):
            # สร้าง directory สำหรับ SQLite
            db_path = database_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # SQLite config
            engine = create_engine(
                database_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # PostgreSQL / MySQL config
            engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        
        return engine
    
    def _create_tables(self):
        """สร้างตารางทั้งหมด"""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self):
        """Context manager สำหรับ database session"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_analysis(self, title: str, source_type: str, source_filename: str,
                     text_content: str, analysis_result: dict) -> int:
        """
        บันทึกผลการวิเคราะห์ลงฐานข้อมูล
        
        Returns:
            ID ของ analysis record ที่บันทึก
        """
        with self.get_session() as session:
            # สร้าง analysis record
            analysis = AnalysisRecord(
                title=title,
                source_type=source_type,
                source_filename=source_filename,
                text_content=text_content[:1000],  # เก็บแค่ 1000 ตัวอักษรแรก
                total_words=analysis_result.get('total_words', 0),
                unique_words=analysis_result.get('unique_words', 0)
            )
            session.add(analysis)
            session.flush()  # เพื่อได้ analysis.id
            
            # บันทึก word frequencies
            word_frequency = analysis_result.get('word_frequency', {})
            total_words = analysis_result.get('total_words', 0)
            
            for word, frequency in word_frequency.items():
                percentage = (frequency / total_words * 100) if total_words > 0 else 0
                wf = WordFrequency(
                    analysis_id=analysis.id,
                    word=word,
                    frequency=frequency,
                    percentage=percentage
                )
                session.add(wf)
            
            # บันทึก categories
            if 'category_summary' in analysis_result:
                for cat_info in analysis_result['category_summary']:
                    cat = Category(
                        analysis_id=analysis.id,
                        category_name=cat_info['category'],
                        unique_words=cat_info['unique_words'],
                        total_frequency=cat_info['total_frequency'],
                        percentage=(cat_info['total_frequency'] / total_words * 100) if total_words > 0 else 0
                    )
                    session.add(cat)
                    session.flush()  # เพื่อได้ cat.id
                    
                    # บันทึก category words
                    if 'categorized_words' in analysis_result:
                        cat_words = analysis_result['categorized_words'].get(cat_info['category'], {})
                        for word, freq in cat_words.items():
                            cw = CategoryWord(
                                category_id=cat.id,
                                word=word,
                                frequency=freq
                            )
                            session.add(cw)
            
            return analysis.id
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """ดึงข้อมูลการวิเคราะห์ตาม ID"""
        with self.get_session() as session:
            analysis = session.query(AnalysisRecord).filter_by(id=analysis_id).first()
            
            if not analysis:
                return None
            
            # ดึง word frequencies
            word_freqs = session.query(WordFrequency).filter_by(analysis_id=analysis_id)\
                .order_by(desc(WordFrequency.frequency)).all()
            
            # ดึง categories พร้อม top words
            categories_data = []
            categories = session.query(Category).filter_by(analysis_id=analysis_id)\
                .order_by(desc(Category.total_frequency)).all()
            
            for cat in categories:
                cat_dict = cat.to_dict(include_words=False)
                # ดึง top words
                top_words = session.query(CategoryWord).filter_by(category_id=cat.id)\
                    .order_by(desc(CategoryWord.frequency)).limit(10).all()
                cat_dict['top_words'] = [w.to_dict() for w in top_words]
                categories_data.append(cat_dict)
            
            # รวมข้อมูล
            result = analysis.to_dict()
            result['word_frequencies'] = [wf.to_dict() for wf in word_freqs]
            result['categories'] = categories_data
            
            return result
    
    def get_all_analyses(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """ดึงรายการการวิเคราะห์ทั้งหมด"""
        with self.get_session() as session:
            analyses = session.query(AnalysisRecord)\
                .order_by(desc(AnalysisRecord.created_at))\
                .limit(limit).offset(offset).all()
            
            return [a.to_dict() for a in analyses]
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """ลบการวิเคราะห์"""
        with self.get_session() as session:
            analysis = session.query(AnalysisRecord).filter_by(id=analysis_id).first()
            if analysis:
                session.delete(analysis)
                return True
            return False
    
    def update_analysis_title(self, analysis_id: int, new_title: str) -> bool:
        """อัพเดทชื่อการวิเคราะห์"""
        with self.get_session() as session:
            analysis = session.query(AnalysisRecord).filter_by(id=analysis_id).first()
            if analysis:
                analysis.title = new_title
                analysis.updated_at = datetime.now()
                return True
            return False
    
    def search_analyses(self, keyword: str, limit: int = 50) -> List[Dict]:
        """ค้นหาการวิเคราะห์"""
        with self.get_session() as session:
            analyses = session.query(AnalysisRecord).filter(
                (AnalysisRecord.title.like(f'%{keyword}%')) |
                (AnalysisRecord.source_filename.like(f'%{keyword}%'))
            ).order_by(desc(AnalysisRecord.created_at)).limit(limit).all()
            
            return [a.to_dict() for a in analyses]
    
    def get_statistics(self) -> Dict:
        """ดึงสถิติการใช้งานทั้งหมด"""
        with self.get_session() as session:
            # จำนวนการวิเคราะห์ทั้งหมด
            total_analyses = session.query(func.count(AnalysisRecord.id)).scalar()
            
            # คำทั้งหมดที่ประมวลผล
            total_words_processed = session.query(func.sum(AnalysisRecord.total_words)).scalar() or 0
            
            # หมวดหมู่ที่พบบ่อยที่สุด
            top_categories = session.query(
                Category.category_name,
                func.count(Category.id).label('count'),
                func.sum(Category.total_frequency).label('total')
            ).group_by(Category.category_name)\
             .order_by(desc('count')).limit(10).all()
            
            top_categories_list = [
                {
                    'category_name': cat[0],
                    'count': cat[1],
                    'total': cat[2]
                } for cat in top_categories
            ]
            
            # คำที่พบบ่อยที่สุดโดยรวม
            top_words = session.query(
                WordFrequency.word,
                func.sum(WordFrequency.frequency).label('total_frequency')
            ).group_by(WordFrequency.word)\
             .order_by(desc('total_frequency')).limit(20).all()
            
            top_words_list = [
                {
                    'word': word[0],
                    'total_frequency': word[1]
                } for word in top_words
            ]
            
            return {
                'total_analyses': total_analyses,
                'total_words_processed': total_words_processed,
                'top_categories': top_categories_list,
                'top_words': top_words_list
            }
    
    def get_category_trends(self, days: int = 30) -> List[Dict]:
        """วิเคราะห์แนวโน้มหมวดหมู่"""
        with self.get_session() as session:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            trends = session.query(
                Category.category_name,
                func.count(Category.id).label('occurrence_count'),
                func.avg(Category.total_frequency).label('avg_frequency'),
                func.sum(Category.total_frequency).label('sum_frequency')
            ).join(AnalysisRecord)\
             .filter(AnalysisRecord.created_at >= cutoff_date)\
             .group_by(Category.category_name)\
             .order_by(desc('occurrence_count')).all()
            
            return [
                {
                    'category_name': t[0],
                    'occurrence_count': t[1],
                    'avg_frequency': float(t[2]) if t[2] else 0,
                    'sum_frequency': t[3]
                } for t in trends
            ]
    
    def add_tag(self, name: str, color: str = '#007BFF') -> int:
        """เพิ่ม tag ใหม่"""
        with self.get_session() as session:
            # ตรวจสอบว่ามี tag นี้แล้วหรือไม่
            existing_tag = session.query(Tag).filter_by(name=name).first()
            if existing_tag:
                return existing_tag.id
            
            tag = Tag(name=name, color=color)
            session.add(tag)
            session.flush()
            return tag.id
    
    def get_tags(self) -> List[Dict]:
        """ดึงรายการ tags ทั้งหมด"""
        with self.get_session() as session:
            tags = session.query(Tag).order_by(Tag.name).all()
            return [t.to_dict() for t in tags]
    
    def tag_analysis(self, analysis_id: int, tag_id: int) -> bool:
        """ติด tag ให้กับการวิเคราะห์"""
        with self.get_session() as session:
            analysis = session.query(AnalysisRecord).filter_by(id=analysis_id).first()
            tag = session.query(Tag).filter_by(id=tag_id).first()
            
            if analysis and tag:
                if tag not in analysis.tags:
                    analysis.tags.append(tag)
                    return True
            return False
    
    def get_analyses_by_tag(self, tag_id: int, limit: int = 50) -> List[Dict]:
        """ดึงการวิเคราะห์ที่มี tag ที่กำหนด"""
        with self.get_session() as session:
            tag = session.query(Tag).filter_by(id=tag_id).first()
            if tag:
                analyses = tag.analyses[:limit]
                return [a.to_dict() for a in analyses]
            return []
    
    def get_total_count(self) -> int:
        """นับจำนวนการวิเคราะห์ทั้งหมด"""
        with self.get_session() as session:
            return session.query(func.count(AnalysisRecord.id)).scalar()
    
    def export_to_json(self, analysis_id: int) -> Optional[str]:
        """ส่งออกการวิเคราะห์เป็น JSON"""
        data = self.get_analysis_by_id(analysis_id)
        if data:
            return json.dumps(data, ensure_ascii=False, indent=2, default=str)
        return None
    
    def get_database_info(self) -> Dict:
        """ดึงข้อมูลเกี่ยวกับฐานข้อมูล"""
        db_type = 'Unknown'
        if self.database_url.startswith('sqlite'):
            db_type = 'SQLite'
        elif self.database_url.startswith('postgresql'):
            db_type = 'PostgreSQL'
        elif self.database_url.startswith('mysql'):
            db_type = 'MySQL/MariaDB'
        
        return {
            'type': db_type,
            'url': self.database_url.split('@')[-1] if '@' in self.database_url else self.database_url,
            'total_records': self.get_total_count()
        }
    
    def close(self):
        """ปิด connection pool"""
        self.Session.remove()
        self.engine.dispose()


# Backward compatibility - alias to DatabaseManager
Database = DatabaseManager

