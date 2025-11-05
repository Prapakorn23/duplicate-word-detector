# Database API Documentation
## API สำหรับจัดการฐานข้อมูล

---

## 🎯 ภาพรวม

ระบบตรวจจับคำซ้ำมีฐานข้อมูล SQLite สำหรับ:
- 💾 บันทึกผลการวิเคราะห์
- 📊 ดึงประวัติการวิเคราะห์
- 🔍 ค้นหาและจัดการข้อมูล
- 📈 วิเคราะห์แนวโน้ม
- 🏷️ จัดกลุ่มด้วย Tags

---

## 📂 Database Schema

### **ตาราง 1: analysis_records**
เก็บบันทึกการวิเคราะห์หลัก

| Column | Type | คำอธิบาย |
|--------|------|----------|
| id | INTEGER | Primary Key (auto) |
| title | VARCHAR(255) | ชื่อการวิเคราะห์ |
| source_type | VARCHAR(50) | ประเภท (text/file/pdf) |
| source_filename | VARCHAR(255) | ชื่อไฟล์ |
| text_content | TEXT | เนื้อหา (1000 ตัวอักษรแรก) |
| total_words | INTEGER | จำนวนคำทั้งหมด |
| unique_words | INTEGER | จำนวนคำที่ไม่ซ้ำ |
| created_at | TIMESTAMP | วันที่สร้าง |
| updated_at | TIMESTAMP | วันที่อัพเดท |

### **ตาราง 2: word_frequencies**
เก็บความถี่ของแต่ละคำ

| Column | Type | คำอธิบาย |
|--------|------|----------|
| id | INTEGER | Primary Key (auto) |
| analysis_id | INTEGER | FK → analysis_records |
| word | VARCHAR(255) | คำ |
| frequency | INTEGER | ความถี่ |
| percentage | REAL | เปอร์เซ็นต์ |

### **ตาราง 3: categories**
เก็บหมวดหมู่ที่พบ

| Column | Type | คำอธิบาย |
|--------|------|----------|
| id | INTEGER | Primary Key (auto) |
| analysis_id | INTEGER | FK → analysis_records |
| category_name | VARCHAR(100) | ชื่อหมวดหมู่ |
| unique_words | INTEGER | จำนวนคำเฉพาะ |
| total_frequency | INTEGER | ความถี่รวม |
| percentage | REAL | เปอร์เซ็นต์ |

### **ตาราง 4: category_words**
เก็บคำในแต่ละหมวดหมู่

| Column | Type | คำอธิบาย |
|--------|------|----------|
| id | INTEGER | Primary Key (auto) |
| category_id | INTEGER | FK → categories |
| word | VARCHAR(255) | คำ |
| frequency | INTEGER | ความถี่ |

### **ตาราง 5: tags**
เก็บ tags สำหรับจัดกลุ่ม

| Column | Type | คำอธิบาย |
|--------|------|----------|
| id | INTEGER | Primary Key (auto) |
| name | VARCHAR(100) | ชื่อ tag (unique) |
| color | VARCHAR(20) | สี |
| created_at | TIMESTAMP | วันที่สร้าง |

### **ตาราง 6: analysis_tags**
ความสัมพันธ์ระหว่าง analysis และ tags

| Column | Type | คำอธิบาย |
|--------|------|----------|
| analysis_id | INTEGER | FK → analysis_records |
| tag_id | INTEGER | FK → tags |

---

## 🔌 API Endpoints

### **1. บันทึกการวิเคราะห์**

```http
POST /api/db/save
```

**Request Body:**
```json
{
  "title": "รายงานการประชุมสภา 5 พ.ย. 2568",
  "source_type": "pdf",
  "source_filename": "meeting_report.pdf",
  "text_content": "เนื้อหาข้อความ...",
  "analysis_result": {
    "total_words": 1234,
    "unique_words": 567,
    "word_frequency": {"คำ": 45, ...},
    "category_summary": [...]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": 1,
    "message": "บันทึกลงฐานข้อมูลเรียบร้อยแล้ว"
  }
}
```

---

### **2. ดึงรายการทั้งหมด**

```http
GET /api/db/list?limit=50&offset=0
```

**Parameters:**
- `limit` (optional): จำนวนรายการ (default: 50)
- `offset` (optional): เริ่มจากรายการที่ (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "analyses": [
      {
        "id": 1,
        "title": "รายงานการประชุมสภา",
        "source_type": "pdf",
        "source_filename": "meeting.pdf",
        "total_words": 1234,
        "unique_words": 567,
        "created_at": "2025-11-05 15:30:00"
      }
    ],
    "total": 10,
    "limit": 50,
    "offset": 0
  }
}
```

---

### **3. ดึงข้อมูลตาม ID**

```http
GET /api/db/get/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "รายงานการประชุมสภา",
    "total_words": 1234,
    "unique_words": 567,
    "word_frequencies": [
      {"word": "การศึกษา", "frequency": 45, "percentage": 3.65}
    ],
    "categories": [
      {
        "category_name": "การศึกษา",
        "unique_words": 25,
        "total_frequency": 120,
        "percentage": 9.73,
        "top_words": [
          {"word": "การศึกษา", "frequency": 45}
        ]
      }
    ]
  }
}
```

---

### **4. ลบการวิเคราะห์**

```http
DELETE /api/db/delete/1
```

**Response:**
```json
{
  "success": true,
  "message": "ลบข้อมูลเรียบร้อยแล้ว"
}
```

---

### **5. อัพเดทชื่อ**

```http
PUT /api/db/update/1
```

**Request Body:**
```json
{
  "title": "รายงานการประชุมสภา (แก้ไข)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "อัพเดทชื่อเรียบร้อยแล้ว"
}
```

---

### **6. ค้นหา**

```http
GET /api/db/search?keyword=การศึกษา&limit=50
```

**Parameters:**
- `keyword` (required): คำค้นหา
- `limit` (optional): จำนวนผลลัพธ์

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "keyword": "การศึกษา",
    "count": 5
  }
}
```

---

### **7. สถิติฐานข้อมูล**

```http
GET /api/db/statistics
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_analyses": 150,
    "total_words_processed": 185670,
    "top_categories": [
      {
        "category_name": "การเมือง",
        "count": 45,
        "total": 12450
      }
    ],
    "top_words": [
      {
        "word": "รัฐสภา",
        "total_frequency": 340
      }
    ]
  }
}
```

---

### **8. แนวโน้มหมวดหมู่**

```http
GET /api/db/trends?days=30
```

**Parameters:**
- `days` (optional): จำนวนวันย้อนหลัง (default: 30)

**Response:**
```json
{
  "success": true,
  "data": {
    "trends": [
      {
        "category_name": "การเมือง",
        "occurrence_count": 25,
        "avg_frequency": 45.5,
        "sum_frequency": 1138
      }
    ],
    "period_days": 30
  }
}
```

---

### **9. จัดการ Tags**

#### **9.1 ดึงรายการ tags**
```http
GET /api/db/tags
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "สำคัญ",
      "color": "#FF0000",
      "created_at": "2025-11-05 10:00:00"
    }
  ]
}
```

#### **9.2 สร้าง tag ใหม่**
```http
POST /api/db/tags/create
```

**Request Body:**
```json
{
  "name": "ด่วน",
  "color": "#FF5733"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tag_id": 2,
    "message": "สร้าง tag เรียบร้อยแล้ว"
  }
}
```

#### **9.3 ติด tag**
```http
POST /api/db/tags/1/2
```
(analysis_id=1, tag_id=2)

**Response:**
```json
{
  "success": true,
  "message": "ติด tag เรียบร้อยแล้ว"
}
```

---

### **10. ส่งออกเป็น JSON**

```http
GET /api/db/export/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "...",
    "word_frequencies": [...],
    "categories": [...]
  }
}
```

---

## 💡 ตัวอย่างการใช้งาน

### **Use Case 1: บันทึกผลการวิเคราะห์**

```javascript
// หลังจากวิเคราะห์เสร็จ
const saveResult = await fetch('/api/db/save', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        title: 'รายงานการประชุม 5 พ.ย.',
        source_type: 'pdf',
        source_filename: 'meeting.pdf',
        text_content: fullText,
        analysis_result: analysisData
    })
});

const saved = await saveResult.json();
console.log('Saved with ID:', saved.data.analysis_id);
```

---

### **Use Case 2: แสดงประวัติการวิเคราะห์**

```javascript
// ดึงรายการ 10 รายการล่าสุด
const response = await fetch('/api/db/list?limit=10&offset=0');
const data = await response.json();

data.data.analyses.forEach(analysis => {
    console.log(`${analysis.title} - ${analysis.created_at}`);
});
```

---

### **Use Case 3: ค้นหาการวิเคราะห์**

```javascript
// ค้นหาคำว่า "การศึกษา"
const response = await fetch('/api/db/search?keyword=การศึกษา');
const data = await response.json();

console.log(`พบ ${data.data.count} รายการ`);
```

---

### **Use Case 4: วิเคราะห์แนวโน้ม**

```javascript
// ดูแนวโน้ม 30 วันที่ผ่านมา
const response = await fetch('/api/db/trends?days=30');
const data = await response.json();

data.data.trends.forEach(trend => {
    console.log(`${trend.category_name}: ${trend.occurrence_count} ครั้ง`);
});
```

---

## 🗄️ ตำแหน่งฐานข้อมูล

**ไฟล์:** `data/parliament_words.db`

**สร้างอัตโนมัติ:** เมื่อรันครั้งแรก

**ขนาด:** ขึ้นกับจำนวนการวิเคราะห์

---

## 🔐 Security

- ✅ ไม่มี SQL Injection (ใช้ parameterized queries)
- ✅ Cascade delete (ลบข้อมูลเกี่ยวข้องอัตโนมัติ)
- ✅ Transaction support
- ✅ Error handling

---

## 📊 Performance

- ✅ Indexes สำหรับ queries ที่ใช้บ่อย
- ✅ Pagination support
- ✅ Efficient queries
- ✅ Connection pooling

---

## 🎯 Benefits

### **สำหรับรัฐสภา:**

✅ **ติดตามประวัติ** - ดูผลการวิเคราะห์ย้อนหลัง  
✅ **วิเคราะห์แนวโน้ม** - ดูว่าหัวข้อไหนถูกพูดถึงบ่อย  
✅ **จัดกลุ่มเอกสาร** - ใช้ tags จัดหมู่  
✅ **สร้างรายงาน** - Export ข้อมูลได้  
✅ **ค้นหาง่าย** - หาเอกสารเก่าได้เร็ว  

---

## 🚀 Quick Start

### **1. ฐานข้อมูลจะสร้างอัตโนมัติ:**
```bash
python app.py
# → สร้าง data/parliament_words.db อัตโนมัติ
```

### **2. ทดสอบ API:**

**บันทึกผลการวิเคราะห์:**
```bash
curl -X POST http://localhost:5000/api/db/save \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "source_type": "text", ...}'
```

**ดึงรายการ:**
```bash
curl http://localhost:5000/api/db/list
```

**ดูสถิติ:**
```bash
curl http://localhost:5000/api/db/statistics
```

---

## 📝 Error Handling

### **Common Errors:**

| Error | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| 404 | ไม่พบข้อมูล | ตรวจสอบ ID |
| 400 | ข้อมูลไม่ครบ | ส่งข้อมูลให้ครบ |
| 500 | Server error | ตรวจสอบ logs |

---

## 🔧 Advanced Features

### **Transaction Safety:**
```python
# บันทึกจะ rollback อัตโนมัติถ้าเกิด error
db.save_analysis(...)  # All or nothing
```

### **Cascade Delete:**
```python
# ลบ analysis จะลบข้อมูลเกี่ยวข้องทั้งหมด
db.delete_analysis(1)
# → ลบ word_frequencies
# → ลบ categories
# → ลบ category_words
```

### **Full-text Search:**
```python
# ค้นหาทั้ง title และ filename
db.search_analyses("การศึกษา")
```

---

## 📈 Use Cases

### **1. Dashboard สถิติรัฐสภา**
```
ดึงข้อมูล:
- GET /api/db/statistics → แสดงภาพรวม
- GET /api/db/trends → แสดงแนวโน้ม
```

### **2. ระบบจัดการเอกสาร**
```
- POST /api/db/save → บันทึกเอกสารใหม่
- GET  /api/db/list → แสดงรายการ
- GET  /api/db/search → ค้นหาเอกสาร
```

### **3. รายงานวิเคราะห์**
```
- GET /api/db/trends → วิเคราะห์แนวโน้ม 30/60/90 วัน
- GET /api/db/export/<id> → ส่งออกข้อมูลเป็น JSON
```

---

## 🎨 Integration Example

### **บันทึกอัตโนมัติหลังวิเคราะห์:**

```javascript
// ใน script.js - หลัง analyzeText()
async analyzeText() {
    // ... วิเคราะห์ข้อความ ...
    
    if (result.success) {
        // แสดงผล
        this.displayResults(result.data);
        
        // บันทึกลงฐานข้อมูล (ถ้าต้องการ)
        const saveResponse = await fetch('/api/db/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title: `การวิเคราะห์ ${new Date().toLocaleString('th-TH')}`,
                source_type: 'text',
                text_content: text,
                analysis_result: result.data
            })
        });
        
        const saved = await saveResponse.json();
        if (saved.success) {
            console.log('บันทึกแล้ว ID:', saved.data.analysis_id);
        }
    }
}
```

---

## 🗂️ Database Location

**Windows:**
```
C:\Users\[username]\Desktop\Parliament\Duplicate\duplicate-word-detector\data\parliament_words.db
```

**Linux/Mac:**
```
/home/[username]/duplicate-word-detector/data/parliament_words.db
```

---

## 🔄 Backup & Restore

### **Backup:**
```bash
# Copy database file
cp data/parliament_words.db data/backup_$(date +%Y%m%d).db
```

### **Restore:**
```bash
# Restore from backup
cp data/backup_20251105.db data/parliament_words.db
```

---

## 🎯 Best Practices

### **1. บันทึกข้อมูล:**
- ใช้ชื่อที่ descriptive
- บันทึกเฉพาะที่จำเป็น
- เก็บข้อความแค่ 1000 ตัวอักษร

### **2. ค้นหาข้อมูล:**
- ใช้ pagination (limit/offset)
- ระบุ keyword ที่ชัดเจน
- จำกัด limit ไม่เกิน 100

### **3. การลบข้อมูล:**
- ตรวจสอบก่อนลบ
- ใช้ soft delete ถ้าจำเป็น
- Backup ก่อนลบข้อมูลมาก

---

<div align="center">

**🗄️ Database API Ready!**

**10 Endpoints | Full CRUD | Statistics & Trends**

**Version 4.1 - Database Edition**

</div>

