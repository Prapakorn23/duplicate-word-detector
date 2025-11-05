# คู่มือการตั้งค่าฐานข้อมูล
## Database Setup Guide - SQLite / PostgreSQL / MySQL

---

## 🎯 ภาพรวม

ระบบรองรับฐานข้อมูล 3 ประเภท:
- 🟢 **SQLite** - เริ่มต้นใช้งานง่าย (Default)
- 🔵 **PostgreSQL** - แนะนำสำหรับ Production
- 🟠 **MySQL/MariaDB** - Alternative สำหรับ Production

---

## 📊 เปรียบเทียบ Database Types

| Feature | SQLite | PostgreSQL | MySQL |
|---------|--------|------------|-------|
| **Installation** | ไม่ต้องติดตั้ง | ต้องติดตั้ง Server | ต้องติดตั้ง Server |
| **Setup** | ง่ายมาก | ปานกลาง | ปานกลาง |
| **Performance** | ดีสำหรับ read | ดีมากทุกด้าน | ดีมาก |
| **Concurrent Users** | 1-2 | หลายร้อย | หลายร้อย |
| **File Size** | เดียว | Server | Server |
| **Backup** | Copy file | pg_dump | mysqldump |
| **Best For** | Development | Production | Production |
| **Recommended** | ✅ เริ่มต้น | ✅ Production | ⚠️ Alternative |

---

## 🟢 Option 1: SQLite (Default)

### **ข้อดี:**
- ✅ ไม่ต้องติดตั้งอะไรเพิ่ม
- ✅ Setup ทันที
- ✅ เหมาะสำหรับ development
- ✅ Backup ง่าย (copy file)

### **ข้อจำกัด:**
- ⚠️ ไม่เหมาะสำหรับ concurrent users หลายคน
- ⚠️ Performance ต่ำกว่า Server databases

### **การตั้งค่า:**

**ไม่ต้องทำอะไร!** ใช้ได้เลย

```bash
python app.py
# → สร้าง data/parliament_words.db อัตโนมัติ
```

**Connection String:**
```
sqlite:///data/parliament_words.db
```

---

## 🔵 Option 2: PostgreSQL (แนะนำ)

### **ข้อดี:**
- ✅ Performance สูง
- ✅ รองรับ concurrent users ได้ดี
- ✅ Advanced features
- ✅ ACID compliance
- ✅ ตัวเลือก #1 สำหรับ Production

### **การติดตั้ง:**

#### **Windows:**

1. **ดาวน์โหลด PostgreSQL:**
   - ไปที่: https://www.postgresql.org/download/windows/
   - ดาวน์โหลด installer (เวอร์ชันล่าสุด)
   - รัน installer

2. **ระหว่างการติดตั้ง:**
   - เลือก Components: PostgreSQL Server, pgAdmin 4
   - ตั้ง Password สำหรับ postgres user
   - Port: 5432 (default)
   - จำ password ไว้!

3. **สร้าง Database:**
   ```sql
   -- เปิด pgAdmin 4 หรือ psql
   CREATE DATABASE parliament_words;
   
   -- ตั้ง encoding สำหรับภาษาไทย
   CREATE DATABASE parliament_words
     WITH ENCODING 'UTF8'
     LC_COLLATE='th_TH.UTF-8'
     LC_CTYPE='th_TH.UTF-8';
   ```

4. **ติดตั้ง Python driver:**
   ```bash
   pip install psycopg2-binary
   ```

5. **ตั้งค่า connection:**
   สร้างไฟล์ `.env` ที่ root:
   ```
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/parliament_words
   ```

#### **Linux (Ubuntu/Debian):**

```bash
# 1. ติดตั้ง PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 2. เข้าสู่ PostgreSQL
sudo -u postgres psql

# 3. สร้าง database
CREATE DATABASE parliament_words WITH ENCODING 'UTF8';

# 4. สร้าง user (ถ้าต้องการ)
CREATE USER parliament_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE parliament_words TO parliament_user;

# 5. Exit
\q

# 6. ติดตั้ง Python driver
pip install psycopg2-binary
```

#### **macOS:**

```bash
# 1. ติดตั้ง PostgreSQL
brew install postgresql@15

# 2. Start service
brew services start postgresql@15

# 3. สร้าง database
createdb parliament_words

# 4. ติดตั้ง Python driver
pip install psycopg2-binary
```

### **Connection String:**
```
postgresql://username:password@host:port/database

ตัวอย่าง:
postgresql://postgres:mypassword@localhost:5432/parliament_words
```

---

## 🟠 Option 3: MySQL/MariaDB

### **ข้อดี:**
- ✅ Performance ดี
- ✅ รองรับ concurrent users
- ✅ ใช้กันแพร่หลาย
- ✅ มี GUI tools เยอะ

### **การติดตั้ง:**

#### **Windows:**

1. **ดาวน์โหลด MySQL:**
   - ไปที่: https://dev.mysql.com/downloads/installer/
   - ดาวน์โหลด MySQL Installer
   - รัน installer

2. **ระหว่างการติดตั้ง:**
   - เลือก: Developer Default
   - ตั้ง root password
   - Port: 3306 (default)

3. **สร้าง Database:**
   ```sql
   -- เปิด MySQL Workbench หรือ mysql CLI
   CREATE DATABASE parliament_words 
     CHARACTER SET utf8mb4 
     COLLATE utf8mb4_unicode_ci;
   ```

4. **ติดตั้ง Python driver:**
   ```bash
   pip install pymysql
   ```

5. **ตั้งค่า connection:**
   ```
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/parliament_words
   ```

#### **Linux (Ubuntu/Debian):**

```bash
# 1. ติดตั้ง MySQL
sudo apt update
sudo apt install mysql-server

# 2. Secure installation
sudo mysql_secure_installation

# 3. เข้าสู่ MySQL
sudo mysql

# 4. สร้าง database
CREATE DATABASE parliament_words CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 5. สร้าง user
CREATE USER 'parliament_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON parliament_words.* TO 'parliament_user'@'localhost';
FLUSH PRIVILEGES;

# 6. Exit
exit

# 7. ติดตั้ง Python driver
pip install pymysql
```

#### **macOS:**

```bash
# 1. ติดตั้ง MySQL
brew install mysql

# 2. Start service
brew services start mysql

# 3. Secure installation
mysql_secure_installation

# 4. สร้าง database
mysql -u root -p
CREATE DATABASE parliament_words CHARACTER SET utf8mb4;

# 5. ติดตั้ง Python driver
pip install pymysql
```

### **Connection String:**
```
mysql+pymysql://username:password@host:port/database

ตัวอย่าง:
mysql+pymysql://root:mypassword@localhost:3306/parliament_words
```

---

## ⚙️ การตั้งค่า

### **วิธีที่ 1: ใช้ Environment Variable**

สร้างไฟล์ `.env` ที่ root folder:

```bash
# .env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/parliament_words
```

ระบบจะอ่านอัตโนมัติเมื่อรัน

### **วิธีที่ 2: แก้ไขใน config.py**

แก้ไขไฟล์ `config/config.py`:

```python
# Database Configuration
DATABASE_URL = 'postgresql://postgres:mypassword@localhost:5432/parliament_words'
```

---

## 🔧 การเปลี่ยน Database

### **จาก SQLite → PostgreSQL:**

1. **Backup ข้อมูล SQLite:**
   ```bash
   # Export ข้อมูลทั้งหมด
   sqlite3 data/parliament_words.db .dump > backup.sql
   ```

2. **ติดตั้ง PostgreSQL และสร้าง database**

3. **เปลี่ยน connection string:**
   ```
   DATABASE_URL=postgresql://...
   ```

4. **รันโปรแกรม:**
   ```bash
   python app.py
   # → สร้างตารางใน PostgreSQL อัตโนมัติ
   ```

5. **Import ข้อมูล (ถ้าต้องการ):**
   - ใช้ migration tools หรือ
   - Import ข้อมูลด้วย script

---

## 📊 ตัวอย่าง Connection Strings

### **SQLite:**
```python
# Local file
DATABASE_URL='sqlite:///data/parliament_words.db'

# Absolute path (Windows)
DATABASE_URL='sqlite:///C:/data/parliament_words.db'

# In-memory (testing)
DATABASE_URL='sqlite:///:memory:'
```

### **PostgreSQL:**
```python
# Local
DATABASE_URL='postgresql://postgres:password@localhost:5432/parliament_words'

# Remote
DATABASE_URL='postgresql://user:pass@remote.server.com:5432/dbname'

# With options
DATABASE_URL='postgresql://user:pass@localhost/dbname?client_encoding=utf8'
```

### **MySQL:**
```python
# Local
DATABASE_URL='mysql+pymysql://root:password@localhost:3306/parliament_words'

# Remote
DATABASE_URL='mysql+pymysql://user:pass@remote.server.com:3306/dbname'

# With charset
DATABASE_URL='mysql+pymysql://user:pass@localhost/dbname?charset=utf8mb4'
```

---

## 🧪 ทดสอบ Connection

### **ทดสอบ SQLite:**
```bash
python -c "from core import DatabaseManager; db = DatabaseManager('sqlite:///test.db'); print('✅ SQLite OK')"
```

### **ทดสอบ PostgreSQL:**
```bash
python -c "from core import DatabaseManager; db = DatabaseManager('postgresql://postgres:password@localhost:5432/parliament_words'); print('✅ PostgreSQL OK')"
```

### **ทดสอบ MySQL:**
```bash
python -c "from core import DatabaseManager; db = DatabaseManager('mysql+pymysql://root:password@localhost:3306/parliament_words'); print('✅ MySQL OK')"
```

---

## 🔐 Security Best Practices

### **1. ไม่ควร hardcode password:**
```python
# ❌ Bad
DATABASE_URL = 'postgresql://user:password123@localhost/db'

# ✅ Good - ใช้ environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
```

### **2. ใช้ .env file:**
```bash
# .env (อย่า commit ลง git!)
DATABASE_URL=postgresql://...
SECRET_KEY=...
```

### **3. ใช้ Strong Password:**
- อย่างน้อย 12 ตัวอักษร
- ผสม ตัวพิมพ์ใหญ่-เล็ก, ตัวเลข, สัญลักษณ์

### **4. Limit Privileges:**
```sql
-- PostgreSQL
CREATE USER parliament_app WITH PASSWORD 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO parliament_app;

-- MySQL
CREATE USER 'parliament_app'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON parliament_words.* TO 'parliament_app'@'localhost';
```

---

## 🚀 Quick Start แต่ละแบบ

### **SQLite (ง่ายที่สุด):**
```bash
# ไม่ต้องตั้งค่าอะไร
python app.py
```

### **PostgreSQL:**
```bash
# 1. สร้าง database
createdb parliament_words

# 2. ติดตั้ง driver
pip install psycopg2-binary

# 3. ตั้งค่า .env
echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/parliament_words" > .env

# 4. รัน
python app.py
```

### **MySQL:**
```bash
# 1. สร้าง database
mysql -u root -p -e "CREATE DATABASE parliament_words CHARACTER SET utf8mb4;"

# 2. ติดตั้ง driver
pip install pymysql

# 3. ตั้งค่า .env
echo "DATABASE_URL=mysql+pymysql://root:password@localhost:3306/parliament_words" > .env

# 4. รัน
python app.py
```

---

## 📈 Performance Tips

### **PostgreSQL:**
```sql
-- เพิ่ม indexes สำหรับ performance
CREATE INDEX idx_analysis_created ON analysis_records(created_at DESC);
CREATE INDEX idx_word_freq ON word_frequencies(analysis_id, frequency DESC);
CREATE INDEX idx_category ON categories(analysis_id);

-- Analyze tables
ANALYZE analysis_records;
ANALYZE word_frequencies;
```

### **MySQL:**
```sql
-- เพิ่ม indexes
CREATE INDEX idx_analysis_created ON analysis_records(created_at DESC);
CREATE INDEX idx_word_freq ON word_frequencies(analysis_id, frequency DESC);

-- Optimize tables
OPTIMIZE TABLE analysis_records;
OPTIMIZE TABLE word_frequencies;
```

---

## 🔄 Migration & Backup

### **SQLite Backup:**
```bash
# Backup
cp data/parliament_words.db data/backup_$(date +%Y%m%d).db

# Restore
cp data/backup_20251105.db data/parliament_words.db
```

### **PostgreSQL Backup:**
```bash
# Backup
pg_dump -U postgres parliament_words > backup_20251105.sql

# Restore
psql -U postgres parliament_words < backup_20251105.sql
```

### **MySQL Backup:**
```bash
# Backup
mysqldump -u root -p parliament_words > backup_20251105.sql

# Restore
mysql -u root -p parliament_words < backup_20251105.sql
```

---

## 🛠️ Troubleshooting

### **Problem 1: "Can't connect to PostgreSQL"**

**Check:**
```bash
# PostgreSQL service running?
sudo service postgresql status  # Linux
brew services list              # macOS

# Can connect?
psql -U postgres -h localhost
```

**Fix:**
```bash
# Start service
sudo service postgresql start   # Linux
brew services start postgresql  # macOS
```

### **Problem 2: "Access denied for MySQL"**

**Fix:**
```sql
-- Reset password
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

### **Problem 3: "Database does not exist"**

**Fix:**
```bash
# PostgreSQL
createdb parliament_words

# MySQL
mysql -u root -p -e "CREATE DATABASE parliament_words CHARACTER SET utf8mb4;"
```

### **Problem 4: "Driver not installed"**

**Fix:**
```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install pymysql
```

---

## 🌐 Remote Database

### **PostgreSQL (Remote):**
```
DATABASE_URL=postgresql://user:pass@your-server.com:5432/parliament_words
```

### **MySQL (Remote):**
```
DATABASE_URL=mysql+pymysql://user:pass@your-server.com:3306/parliament_words
```

### **Security สำหรับ Remote:**
- ✅ ใช้ SSL/TLS
- ✅ Whitelist IP addresses
- ✅ ใช้ strong passwords
- ✅ Firewall configuration

---

## 📊 Database URL Format

### **General Format:**
```
dialect+driver://username:password@host:port/database
```

### **Components:**
- **dialect**: `postgresql`, `mysql`, `sqlite`
- **driver**: `psycopg2`, `pymysql`, (sqlite ไม่ต้องมี)
- **username**: database user
- **password**: user password
- **host**: server address (localhost, IP, domain)
- **port**: database port (5432, 3306, etc.)
- **database**: database name

---

## ✅ Checklist

### **SQLite:**
- [ ] ไม่ต้องทำอะไร ใช้ได้เลย!

### **PostgreSQL:**
- [ ] ติดตั้ง PostgreSQL server
- [ ] สร้าง database
- [ ] ติดตั้ง psycopg2-binary
- [ ] ตั้งค่า DATABASE_URL
- [ ] ทดสอบ connection

### **MySQL:**
- [ ] ติดตั้ง MySQL/MariaDB server
- [ ] สร้าง database (charset=utf8mb4)
- [ ] ติดตั้ง pymysql
- [ ] ตั้งค่า DATABASE_URL
- [ ] ทดสอบ connection

---

## 🎯 Recommendations

### **สำหรับ Development:**
→ ใช้ **SQLite** (ง่าย ไม่ต้อง setup)

### **สำหรับ Production (Single Server):**
→ ใช้ **PostgreSQL** (แนะนำ)

### **สำหรับ Production (Existing MySQL):**
→ ใช้ **MySQL** (ถ้ามี infrastructure อยู่แล้ว)

---

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

<div align="center">

**🗄️ รองรับ 3 Database Engines!**

**SQLite | PostgreSQL | MySQL**

**เลือกได้ตามความเหมาะสม! 🚀**

</div>

