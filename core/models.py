"""
Database Models using SQLAlchemy ORM
รองรับ SQLite, PostgreSQL, และ MySQL
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import StaticPool
import os

Base = declarative_base()

# ตาราง Many-to-Many สำหรับ analysis_tags
analysis_tags_table = Table(
    'analysis_tags',
    Base.metadata,
    Column('analysis_id', Integer, ForeignKey('analysis_records.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class AnalysisRecord(Base):
    """บันทึกการวิเคราะห์หลัก"""
    __tablename__ = 'analysis_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # text, file, pdf
    source_filename = Column(String(255))
    text_content = Column(Text)  # เก็บ 1000 ตัวอักษรแรก
    total_words = Column(Integer, default=0)
    unique_words = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    word_frequencies = relationship('WordFrequency', back_populates='analysis', cascade='all, delete-orphan')
    categories = relationship('Category', back_populates='analysis', cascade='all, delete-orphan')
    tags = relationship('Tag', secondary=analysis_tags_table, back_populates='analyses')
    
    def to_dict(self):
        """แปลงเป็น dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'source_type': self.source_type,
            'source_filename': self.source_filename,
            'text_content': self.text_content,
            'total_words': self.total_words,
            'unique_words': self.unique_words,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class WordFrequency(Base):
    """ความถี่ของคำ"""
    __tablename__ = 'word_frequencies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('analysis_records.id', ondelete='CASCADE'), nullable=False)
    word = Column(String(255), nullable=False)
    frequency = Column(Integer, nullable=False)
    percentage = Column(Float, default=0.0)
    
    # Relationships
    analysis = relationship('AnalysisRecord', back_populates='word_frequencies')
    
    def to_dict(self):
        return {
            'word': self.word,
            'frequency': self.frequency,
            'percentage': self.percentage
        }


class Category(Base):
    """หมวดหมู่ที่พบ"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('analysis_records.id', ondelete='CASCADE'), nullable=False)
    category_name = Column(String(100), nullable=False)
    unique_words = Column(Integer, default=0)
    total_frequency = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)
    
    # Relationships
    analysis = relationship('AnalysisRecord', back_populates='categories')
    category_words = relationship('CategoryWord', back_populates='category', cascade='all, delete-orphan')
    
    def to_dict(self, include_words=False):
        result = {
            'id': self.id,
            'category_name': self.category_name,
            'unique_words': self.unique_words,
            'total_frequency': self.total_frequency,
            'percentage': self.percentage
        }
        if include_words:
            result['top_words'] = [w.to_dict() for w in self.category_words[:10]]
        return result


class CategoryWord(Base):
    """คำในแต่ละหมวดหมู่"""
    __tablename__ = 'category_words'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    word = Column(String(255), nullable=False)
    frequency = Column(Integer, nullable=False)
    
    # Relationships
    category = relationship('Category', back_populates='category_words')
    
    def to_dict(self):
        return {
            'word': self.word,
            'frequency': self.frequency
        }


class Tag(Base):
    """Tags สำหรับจัดกลุ่ม"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(20), default='#007BFF')
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    analyses = relationship('AnalysisRecord', secondary=analysis_tags_table, back_populates='tags')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

