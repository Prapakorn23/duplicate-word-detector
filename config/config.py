"""
Configuration file for Parliament Duplicate Word Detector
ไฟล์การตั้งค่าสำหรับระบบตรวจจับคำซ้ำ
"""

import os

# Application Settings
APP_NAME = "Parliament Duplicate Word Detector"
APP_VERSION = "4.0.0"
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

# File Upload Settings
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Supported File Types
ALLOWED_TEXT_EXTENSIONS = {'.txt', '.text'}
ALLOWED_PDF_EXTENSIONS = {'.pdf'}
ALLOWED_EXTENSIONS = ALLOWED_TEXT_EXTENSIONS | ALLOWED_PDF_EXTENSIONS

# Chart Settings
CHART_DPI = 300
CHART_DEFAULT_TOP_N = 10
CHART_COLORS = [
    '#007BFF', '#FF5733', '#FFEB3B', '#4A90E2', '#FF8A65',
    '#FFD54F', '#212121', '#FF7043', '#FFC107', '#FF9800'
]

# Thai Font Settings for Matplotlib
THAI_FONT_CANDIDATES = [
    'Tahoma', 'Arial', 'Microsoft Sans Serif', 'Segoe UI',
    'Calibri', 'Times New Roman', 'Courier New'
]
DEFAULT_FONT = 'DejaVu Sans'

# Analysis Settings
DEFAULT_FILTER_POS = True
DEFAULT_TARGET_POS = None

# Pagination Settings
DEFAULT_ITEMS_PER_PAGE = 25
ITEMS_PER_PAGE_OPTIONS = [10, 25, 50, 100]

# PDF Processing Settings
PDF_EXTRACTION_TIMEOUT = 300  # seconds
OCR_LANGUAGE = 'tha+eng'
OCR_DPI = 200

# Tesseract Configuration (Windows)
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Cache Settings
ENABLE_CACHE = True
CACHE_FOLDER = 'cache'

# Performance Settings
ENABLE_PERFORMANCE_TRACKING = True

# Export Settings
EXPORT_CSV_ENCODING = 'utf-8-sig'  # UTF-8 with BOM
EXPORT_TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'

# Session Settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'parliament-word-detector-secret-key-2025')

# Logging Settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# CORS Settings
CORS_ORIGINS = "*"

# UI Settings
NAVBAR_TITLE = "ระบบตรวจจับคำซ้ำ"
NAVBAR_SUBTITLE = "Duplicate Word Detector"

