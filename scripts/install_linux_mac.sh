#!/bin/bash

echo "========================================"
echo "ระบบตรวจจับคำซ้ำสำหรับรัฐสภาไทย"
echo "Parliament Duplicate Word Detector"
echo "========================================"
echo ""

echo "[1/3] กำลังติดตั้ง Python Libraries..."
pip3 install Flask flask-cors pythainlp pandas numpy matplotlib
echo ""

echo "[2/3] กำลังติดตั้ง PDF Libraries..."
pip3 install PyPDF2 pdfplumber
echo ""

echo "[3/3] กำลังติดตั้ง OCR Libraries (Optional)..."
pip3 install pdf2image pytesseract Pillow
echo ""

echo "========================================"
echo "✅ ติดตั้ง Python Libraries เสร็จสิ้น!"
echo "========================================"
echo ""

echo "⚠️  สำหรับ OCR (PDF ภาพ) ต้องติดตั้งเพิ่ม:"
echo ""

# ตรวจสอบ OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS - ติดตั้งด้วย Homebrew:"
    echo "   brew install tesseract tesseract-lang poppler"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux (Ubuntu/Debian):"
    echo "   sudo apt update"
    echo "   sudo apt install tesseract-ocr tesseract-ocr-tha poppler-utils"
fi

echo ""
echo "ทดสอบ Tesseract:"
echo "   tesseract --version"
echo "   tesseract --list-langs  # ต้องมี 'tha'"
echo ""

echo "========================================"
echo "🚀 พร้อมใช้งาน! รันด้วยคำสั่ง:"
echo "   python3 app.py"
echo "========================================"
echo ""

