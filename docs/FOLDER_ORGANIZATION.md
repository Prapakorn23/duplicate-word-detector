# การจัดระเบียบ Folders อย่างละเอียด
## Detailed Folder Organization Guide

---

## 📁 โครงสร้าง Folders ทั้งหมด

```
📦 duplicate-word-detector/
│
├── 📱 Main Files (Root)
│   ├── app.py                      # Flask application (389 lines)
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # Main documentation
│   ├── QUICK_START.md             # 3-minute start guide
│   ├── PROJECT_STRUCTURE.md        # Structure documentation
│   ├── ORGANIZATION_SUMMARY.md     # Organization summary
│   ├── .gitignore                  # Git ignore rules
│   ├── run.bat                     # Windows quick start
│   └── run.sh                      # Linux/Mac quick start
│
├── 🧠 core/ - Core Business Logic
│   ├── __init__.py                 # Package exports
│   ├── duplicate_word_detector.py  # Word analysis (533 lines)
│   ├── word_categorizer.py         # Categorization (295 lines)
│   ├── pdf_processor.py            # PDF & OCR (245 lines)
│   └── performance_utils.py        # Performance (312 lines)
│
├── ⚙️ config/ - Configuration
│   ├── __init__.py                 # Package exports
│   └── config.py                   # All settings
│
├── 🌐 templates/ - HTML Templates
│   └── dashboard.html              # Main UI (300+ lines)
│
├── 🎨 static/ - Static Assets
│   ├── style.css                   # Styles (1,350+ lines)
│   ├── script.js                   # JavaScript (800+ lines)
│   └── *.png                       # Generated charts
│
├── 📚 docs/ - Documentation
│   ├── INDEX.md                    # Documentation index
│   ├── PDF_OCR_SETUP_GUIDE.md     # PDF/OCR installation
│   ├── PARLIAMENT_CATEGORIZATION_FEATURE.md
│   ├── CATEGORIZATION_IMPROVEMENT.md
│   ├── WIDGET_IMPROVEMENTS.md
│   ├── IMPROVEMENTS_SUMMARY.md
│   ├── COMPLETE_FEATURES_SUMMARY.md
│   ├── HOW_TO_RUN.md
│   └── FOLDER_ORGANIZATION.md      # This file
│
├── 🔧 scripts/ - Scripts
│   ├── install_windows.bat         # Windows installer
│   └── install_linux_mac.sh        # Linux/Mac installer
│
├── 📤 uploads/ (auto-created)
│   └── (temporary uploaded files)
│
├── 💾 cache/ (auto-created)
│   └── (*.pkl cache files)
│
└── 🐍 venv/ (optional)
    └── (Python virtual environment)
```

---

## 🎯 การจัดกลุ่มตามหน้าที่

### **Group 1: Entry Points & Config**
```
Root/
├── app.py          ← Main application
├── run.bat/sh      ← Quick launchers
└── requirements.txt ← Dependencies
```
**Purpose:** เริ่มต้นโปรแกรมและจัดการ dependencies

---

### **Group 2: Core Logic**
```
core/
├── duplicate_word_detector.py  ← Word analysis
├── word_categorizer.py         ← Categorization
├── pdf_processor.py            ← PDF processing
└── performance_utils.py        ← Performance
```
**Purpose:** Business logic ทั้งหมด

---

### **Group 3: Configuration**
```
config/
└── config.py  ← All settings
```
**Purpose:** Centralized configuration

---

### **Group 4: User Interface**
```
templates/
└── dashboard.html  ← HTML structure

static/
├── style.css       ← Styling
└── script.js       ← Client logic
```
**Purpose:** Frontend presentation

---

### **Group 5: Documentation**
```
docs/
├── INDEX.md        ← Start here
├── Installation/
├── Features/
├── UI-UX/
└── Reference/
```
**Purpose:** All documentation

---

### **Group 6: Automation**
```
scripts/
├── install_windows.bat   ← Auto install
└── install_linux_mac.sh  ← Auto install
```
**Purpose:** Installation automation

---

### **Group 7: Generated & Temporary**
```
uploads/  ← Temporary files
cache/    ← Performance cache
static/*.png ← Generated charts
```
**Purpose:** Runtime artifacts

---

## 📝 File Naming Conventions

### **Python Modules:**
- `snake_case.py` - ทุกไฟล์
- `__init__.py` - Package initializer
- No spaces in filenames

### **Documentation:**
- `UPPERCASE_WORDS.md` - สำหรับเอกสารสำคัญ
- `README.md` - Main readme
- Descriptive names

### **Scripts:**
- `install_*.bat/sh` - Installation scripts
- `run.*` - Run scripts
- Clear purpose in name

---

## 🎨 Color Coding (for IDEs)

### **Recommended IDE Settings:**

| Folder | Color | Purpose |
|--------|-------|---------|
| `core/` | 🔵 Blue | Core logic |
| `config/` | 🟡 Yellow | Configuration |
| `templates/` | 🟢 Green | HTML |
| `static/` | 🟣 Purple | Assets |
| `docs/` | 🟠 Orange | Documentation |
| `scripts/` | 🔴 Red | Scripts |

---

## 🔍 Quick Find Guide

### **"ฉันต้องการ..."**

| Task | Location | File |
|------|----------|------|
| แก้ไข word analysis | `core/` | `duplicate_word_detector.py` |
| เพิ่มหมวดหมู่ | `core/` | `word_categorizer.py` |
| แก้ PDF processing | `core/` | `pdf_processor.py` |
| เปลี่ยนการตั้งค่า | `config/` | `config.py` |
| แก้ UI layout | `templates/` | `dashboard.html` |
| เปลี่ยนสี | `static/` | `style.css` |
| แก้ JavaScript | `static/` | `script.js` |
| อ่านคู่มือติดตั้ง | `docs/` | `PDF_OCR_SETUP_GUIDE.md` |
| ดูฟีเจอร์ | `docs/` | `COMPLETE_FEATURES_SUMMARY.md` |
| ติดตั้งอัตโนมัติ | `scripts/` | `install_*.bat/sh` |

---

## 📏 Folder Size Reference

| Folder | Files | Approx Size | Purpose |
|--------|-------|-------------|---------|
| `core/` | 5 | ~1,400 lines | Business logic |
| `config/` | 2 | ~100 lines | Settings |
| `templates/` | 1 | ~300 lines | HTML |
| `static/` | 3+ | ~2,150+ lines | CSS/JS/Images |
| `docs/` | 9 | ~75 pages | Documentation |
| `scripts/` | 2 | ~100 lines | Scripts |
| `uploads/` | - | Temp | Uploads |
| `cache/` | 20+ | Varies | Cache |

**Total Code:** ~4,000 lines  
**Total Docs:** ~75 pages  
**Total Project:** Professional grade

---

## 🎯 Benefits of This Organization

### **For Developers:**
✅ **Find files 3x faster**  
✅ **Understand structure immediately**  
✅ **Modify code with confidence**  
✅ **Add features easily**  

### **For Teams:**
✅ **Clear responsibility**  
✅ **Easy collaboration**  
✅ **Consistent structure**  
✅ **Standard workflow**  

### **For Project:**
✅ **Professional appearance**  
✅ **Easy to deploy**  
✅ **Scalable architecture**  
✅ **Maintainable codebase**  

---

## 📚 Related Documentation

- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - Overview
- [ORGANIZATION_SUMMARY.md](../ORGANIZATION_SUMMARY.md) - Summary
- [QUICK_START.md](../QUICK_START.md) - Getting started
- [INDEX.md](INDEX.md) - Documentation index

---

<div align="center">

**📁 Organized for Success**

**Everything in its right place! ✨**

</div>

