"""
Core modules for Parliament Duplicate Word Detector
โมดูลหลักสำหรับระบบตรวจจับคำซ้ำรัฐสภา
"""

from .duplicate_word_detector import ThaiDuplicateWordDetector
from .word_categorizer import ParliamentWordCategorizer
from .pdf_processor import PDFProcessor
from .performance_utils import PerformanceTracker, CacheManager, ParallelProcessor, get_performance_summary
from .database_manager import DatabaseManager, Database
from .models import Base, AnalysisRecord, WordFrequency, Category, CategoryWord, Tag

__all__ = [
    'ThaiDuplicateWordDetector',
    'ParliamentWordCategorizer',
    'PDFProcessor',
    'PerformanceTracker',
    'CacheManager',
    'ParallelProcessor',
    'get_performance_summary',
    'DatabaseManager',
    'Database',
    'Base',
    'AnalysisRecord',
    'WordFrequency',
    'Category',
    'CategoryWord',
    'Tag'
]

__version__ = '4.1.0'

