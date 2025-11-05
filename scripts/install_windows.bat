@echo off
echo ========================================
echo ระบบตรวจจับคำซ้ำสำหรับรัฐสภาไทย
echo Parliament Duplicate Word Detector
echo ========================================
echo.

echo [1/3] กำลังติดตั้ง Python Libraries...
pip install Flask flask-cors pythainlp pandas numpy matplotlib
echo.

echo [2/3] กำลังติดตั้ง PDF Libraries...
pip install PyPDF2 pdfplumber
echo.

echo [3/3] กำลังติดตั้ง OCR Libraries (Optional)...
pip install pdf2image pytesseract Pillow
echo.

echo ========================================
echo ✅ ติดตั้ง Python Libraries เสร็จสิ้น!
echo ========================================
echo.

echo ⚠️  สำหรับ OCR (PDF ภาพ) ต้องติดตั้งเพิ่ม:
echo.
echo 1. Tesseract-OCR:
echo    - ดาวน์โหลด: https://github.com/UB-Mannheim/tesseract/wiki
echo    - ติดตั้งพร้อมเลือกภาษาไทย (Thai)
echo    - เพิ่ม PATH: C:\Program Files\Tesseract-OCR
echo.
echo 2. Poppler:
echo    - ดาวน์โหลด: http://blog.alivate.com.au/poppler-windows/
echo    - แตกไฟล์และเพิ่ม bin folder ใน PATH
echo.

echo ========================================
echo 🚀 พร้อมใช้งาน! รันด้วยคำสั่ง:
echo    python app.py
echo ========================================
echo.

pause

