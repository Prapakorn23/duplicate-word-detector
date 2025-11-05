"""
PDF Processor with OCR Support
ระบบแปลงไฟล์ PDF เป็น text รองรับทั้ง PDF ข้อความและภาพ
"""

import os
from typing import Tuple, Optional
import io

# PDF Processing Libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# OCR Libraries (for image-based PDFs)
try:
    from pdf2image import convert_from_path, convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


class PDFProcessor:
    """ประมวลผลไฟล์ PDF และแปลงเป็น text"""
    
    def __init__(self):
        self.supported_methods = self._check_available_libraries()
    
    def _check_available_libraries(self) -> dict:
        """ตรวจสอบ libraries ที่สามารถใช้งานได้"""
        return {
            'pypdf2': PYPDF2_AVAILABLE,
            'pdfplumber': PDFPLUMBER_AVAILABLE,
            'ocr': PDF2IMAGE_AVAILABLE and PYTESSERACT_AVAILABLE
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[bool, str, str]:
        """
        แปลง PDF เป็น text โดยลองใช้หลายวิธี
        
        Args:
            pdf_path: path ของไฟล์ PDF
            
        Returns:
            Tuple of (success, text, method_used)
        """
        # ตรวจสอบว่าไฟล์มีอยู่จริง
        if not os.path.exists(pdf_path):
            return False, "", "ไม่พบไฟล์"
        
        # ลองใช้ pdfplumber ก่อน (แม่นยำที่สุด)
        if self.supported_methods['pdfplumber']:
            success, text = self._extract_with_pdfplumber(pdf_path)
            if success and text.strip():
                return True, text, "pdfplumber"
        
        # ลองใช้ PyPDF2
        if self.supported_methods['pypdf2']:
            success, text = self._extract_with_pypdf2(pdf_path)
            if success and text.strip():
                return True, text, "PyPDF2"
        
        # ถ้าไม่สามารถดึง text ได้ ให้ลอง OCR
        if self.supported_methods['ocr']:
            success, text = self._extract_with_ocr(pdf_path)
            if success and text.strip():
                return True, text, "OCR (Tesseract)"
        
        return False, "", "ไม่สามารถแปลง PDF ได้ กรุณาติดตั้ง libraries ที่จำเป็น"
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[bool, str]:
        """แปลง PDF ด้วย pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return True, text
        except Exception as e:
            print(f"pdfplumber error: {e}")
            return False, ""
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[bool, str]:
        """แปลง PDF ด้วย PyPDF2"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return True, text
        except Exception as e:
            print(f"PyPDF2 error: {e}")
            return False, ""
    
    def _extract_with_ocr(self, pdf_path: str) -> Tuple[bool, str]:
        """แปลง PDF ด้วย OCR (สำหรับ PDF ที่เป็นภาพ)"""
        try:
            # แปลง PDF เป็นรูปภาพ
            images = convert_from_path(pdf_path)
            
            text = ""
            # ใช้ OCR กับแต่ละหน้า
            for i, image in enumerate(images):
                # ใช้ Tesseract OCR (รองรับภาษาไทย)
                page_text = pytesseract.image_to_string(image, lang='tha+eng')
                text += page_text + "\n"
                print(f"OCR หน้า {i+1}/{len(images)} เสร็จสิ้น")
            
            return True, text
        except Exception as e:
            print(f"OCR error: {e}")
            return False, ""
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Tuple[bool, str, str]:
        """
        แปลง PDF จาก bytes เป็น text
        
        Args:
            pdf_bytes: PDF data เป็น bytes
            
        Returns:
            Tuple of (success, text, method_used)
        """
        try:
            # ลอง pdfplumber ก่อน
            if self.supported_methods['pdfplumber']:
                try:
                    text = ""
                    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    if text.strip():
                        return True, text, "pdfplumber"
                except:
                    pass
            
            # ลอง PyPDF2
            if self.supported_methods['pypdf2']:
                try:
                    text = ""
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    if text.strip():
                        return True, text, "PyPDF2"
                except:
                    pass
            
            # ลอง OCR (สำหรับ PDF ที่เป็นภาพ)
            if self.supported_methods['ocr']:
                try:
                    images = convert_from_bytes(pdf_bytes)
                    text = ""
                    for i, image in enumerate(images):
                        page_text = pytesseract.image_to_string(image, lang='tha+eng')
                        text += page_text + "\n"
                    if text.strip():
                        return True, text, "OCR (Tesseract)"
                except:
                    pass
            
            return False, "", "ไม่สามารถแปลง PDF ได้"
            
        except Exception as e:
            return False, "", f"เกิดข้อผิดพลาด: {str(e)}"
    
    def get_installation_instructions(self) -> dict:
        """คำแนะนำการติดตั้ง libraries"""
        instructions = {
            'basic': {
                'missing': [],
                'command': []
            },
            'ocr': {
                'missing': [],
                'command': []
            }
        }
        
        # ตรวจสอบ basic libraries
        if not PDFPLUMBER_AVAILABLE:
            instructions['basic']['missing'].append('pdfplumber')
        if not PYPDF2_AVAILABLE:
            instructions['basic']['missing'].append('PyPDF2')
        
        if instructions['basic']['missing']:
            instructions['basic']['command'] = f"pip install {' '.join(instructions['basic']['missing'])}"
        
        # ตรวจสอบ OCR libraries
        if not PDF2IMAGE_AVAILABLE:
            instructions['ocr']['missing'].append('pdf2image')
        if not PYTESSERACT_AVAILABLE:
            instructions['ocr']['missing'].append('pytesseract')
        
        if instructions['ocr']['missing']:
            instructions['ocr']['command'] = f"pip install {' '.join(instructions['ocr']['missing'])}"
            instructions['ocr']['note'] = "สำหรับ OCR ยังต้องติดตั้ง Tesseract-OCR: https://github.com/tesseract-ocr/tesseract"
        
        return instructions
    
    def check_pdf_type(self, pdf_path: str) -> str:
        """
        ตรวจสอบว่า PDF เป็นแบบ text หรือ image
        
        Returns:
            'text', 'image', หรือ 'unknown'
        """
        try:
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_path) as pdf:
                    if len(pdf.pages) > 0:
                        text = pdf.pages[0].extract_text()
                        if text and len(text.strip()) > 50:
                            return 'text'
                        else:
                            return 'image'
            return 'unknown'
        except:
            return 'unknown'

