class WordFrequencyAnalyzer {
    constructor() {
        this.currentData = null;
        this.showingAllChartWords = false;
        this.chart = null;
        this.currentPage = 1;
        this.itemsPerPage = 25;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupChart();
    }

    setupEventListeners() {
        // ปุ่มวิเคราะห์
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeText();
        });

        // ปุ่มรีเซ็ต
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetAnalysis();
        });

        // ปุ่มล้างข้อความ
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearText();
        });

        // ปุ่มอัปโหลดไฟล์
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileUpload(e);
        });

        // ปุ่มสลับแสดงทั้งหมด/Top 10 ในกราฟ
        document.getElementById('toggleChartBtn').addEventListener('click', () => {
            this.toggleChartView();
        });

        // ปุ่มส่งออกคำซ้ำ
        document.getElementById('exportDuplicatesBtn').addEventListener('click', () => {
            this.exportDuplicates();
        });
        
        // Pagination controls
        document.getElementById('itemsPerPage').addEventListener('change', (e) => {
            this.itemsPerPage = parseInt(e.target.value);
            this.currentPage = 1;
            if (this.wordFrequency && this.totalWords) {
                this.updateTable();
            }
        });
    }

    setupChart() {
        const ctx = document.getElementById('frequencyChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'ความถี่',
                    data: [],
                    backgroundColor: [
                        '#007BFF', '#FF5733', '#FFEB3B', '#4A90E2', '#FF8A65',
                        '#FFD54F', '#212121', '#FF7043', '#FFC107', '#FF9800'
                    ],
                    borderColor: [
                        '#0056B3', '#E64A19', '#F57F17', '#1976D2', '#D84315',
                        '#FFA000', '#000000', '#F4511E', '#FF8F00', '#F57C00'
                    ],
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(33, 33, 33, 0.95)',
                        titleColor: '#FFEB3B',
                        bodyColor: 'white',
                        borderColor: '#007BFF',
                        borderWidth: 2,
                        cornerRadius: 12,
                        displayColors: false,
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13,
                            weight: '500'
                        },
                        padding: 12,
                        callbacks: {
                            title: function(context) {
                                return `📊 คำ: ${context[0].label}`;
                            },
                            label: function(context) {
                                return `⚡ ความถี่: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: true,
                            color: 'rgba(0, 123, 255, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            color: '#212121',
                            font: {
                                size: 13,
                                weight: '600'
                            },
                            padding: 8
                        },
                        border: {
                            display: true,
                            color: '#007BFF',
                            width: 2
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 123, 255, 0.1)',
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: {
                            color: '#212121',
                            font: {
                                size: 13,
                                weight: '600'
                            },
                            stepSize: 1,
                            padding: 8
                        },
                        border: {
                            display: true,
                            color: '#007BFF',
                            width: 2
                        }
                    }
                },
                animation: {
                    duration: 1200,
                    easing: 'easeInOutQuart'
                },
                elements: {
                    bar: {
                        borderWidth: 2,
                        borderSkipped: false,
                    }
                }
            }
        });
    }

    async analyzeText() {
        const text = document.getElementById('textInput').value.trim();

        if (!text) {
            this.showAlert('กรุณาพิมพ์ข้อความที่ต้องการตรวจสอบคำซ้ำ', 'warning');
            return;
        }

        // แสดง Progress Bar
        this.showProgress(true);
        this.updateProgress(10, 'กำลังเริ่มวิเคราะห์ข้อความ...');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    filter_pos: true
                })
            });

            this.updateProgress(50, 'กำลังประมวลผลและนับความถี่ของคำ...');

            const result = await response.json();

            this.updateProgress(90, 'กำลังสร้างกราฟและรายงาน...');

            if (result.success) {
                this.currentData = result.data;
                this.displayResults(result.data);
                
                this.updateProgress(100, 'วิเคราะห์เสร็จสมบูรณ์!');
                
                // ซ่อน Progress Bar หลังจากเสร็จสิ้น
                setTimeout(() => {
                    this.showProgress(false);
                }, 1000);
                
                this.showAlert('ตรวจสอบคำซ้ำเสร็จสิ้น!', 'success');
            } else {
                this.showAlert(result.error || 'เกิดข้อผิดพลาดในการวิเคราะห์', 'danger');
                this.showProgress(false);
            }
        } catch (error) {
            this.showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ: ' + error.message, 'danger');
            this.showProgress(false);
        }
    }

    displayResults(data) {
        // ซ่อน Welcome Section
        document.getElementById('welcomeSection').style.display = 'none';
        
        // แสดง Results Section
        document.getElementById('resultsSection').style.display = 'block';
        
        // อัปเดต Stats ใน Results Section
        document.getElementById('totalWordsStat').textContent = data.total_words;
        document.getElementById('uniqueWordsStat').textContent = data.unique_words;

        // แสดงกราฟ
        this.updateChart(data.top_words);

        // แสดงหมวดหมู่คำ
        if (data.category_summary && data.top_words_by_category) {
            this.displayCategories(data.category_summary, data.top_words_by_category);
        }

        // แสดงตารางคำซ้ำ
        this.displayDuplicatesTable(data.word_frequency, data.total_words);
        
        // รีเซ็ต pagination
        this.currentPage = 1;

        // อัปเดตข้อมูลกราฟ
        this.updateChartInfo(data.word_frequency);

        // เพิ่ม animation
        document.getElementById('resultsSection').classList.add('fade-in');
        
        // เลื่อนหน้าไปที่ results section
        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 300);
    }

    displayCategories(categorySummary, topWordsByCategory) {
        const summaryContainer = document.getElementById('categorySummary');
        const accordionContainer = document.getElementById('categoryAccordion');
        
        // Clear previous content
        summaryContainer.innerHTML = '';
        accordionContainer.innerHTML = '';
        
        if (!categorySummary || categorySummary.length === 0) {
            summaryContainer.innerHTML = '<p class="text-muted">ไม่พบหมวดหมู่</p>';
            return;
        }
        
        // Display category chips
        const chipHTML = categorySummary.map(item => `
            <span class="category-chip badge bg-info me-2 mb-2">
                <i class="fas fa-tag me-1"></i>
                ${item.category}: ${item.total_frequency} คำ
            </span>
        `).join('');
        summaryContainer.innerHTML = chipHTML;
        
        // Display accordion items
        categorySummary.forEach((item, index) => {
            const categoryId = `category${index}`;
            const topWords = topWordsByCategory[item.category] || [];
            
            const accordionItem = `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading${categoryId}">
                        <button class="accordion-button ${index !== 0 ? 'collapsed' : ''}" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#collapse${categoryId}" 
                                aria-expanded="${index === 0}" aria-controls="collapse${categoryId}">
                            <strong>${item.category}</strong>
                            <span class="ms-auto me-3">
                                <span class="badge bg-primary">${item.unique_words} คำเฉพาะ</span>
                                <span class="badge bg-success">${item.total_frequency} ความถี่รวม</span>
                            </span>
                        </button>
                    </h2>
                    <div id="collapse${categoryId}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                         aria-labelledby="heading${categoryId}" data-bs-parent="#categoryAccordion">
                        <div class="accordion-body">
                            <h6 class="mb-3">
                                <i class="fas fa-star me-2 text-warning"></i>
                                คำที่พบบ่อยที่สุด 5 อันดับแรก:
                            </h6>
                            <div class="row g-2">
                                ${topWords.map(([word, freq], i) => `
                                    <div class="col-md-6">
                                        <div class="d-flex align-items-center p-2 bg-light rounded">
                                            <span class="badge bg-secondary me-2">${i + 1}</span>
                                            <span class="flex-grow-1"><strong>${word}</strong></span>
                                            <span class="badge bg-primary">${freq}</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            accordionContainer.insertAdjacentHTML('beforeend', accordionItem);
        });
    }

    clearText() {
        // ล้างเฉพาะข้อความใน textarea
        document.getElementById('textInput').value = '';
        document.getElementById('fileInput').value = '';
        
        // ล้าง visual feedback ของไฟล์
        const fileInput = document.getElementById('fileInput');
        fileInput.classList.remove('file-upload-success', 'file-upload-error');
        
        this.showAlert('ล้างข้อความเรียบร้อยแล้ว', 'info');
    }


    displayDuplicatesTable(wordFrequency, totalWords) {
        // เก็บข้อมูลไว้สำหรับ pagination
        this.wordFrequency = wordFrequency;
        this.totalWords = totalWords;
        
        // แสดงตารางด้วย pagination
        this.updateTable();
    }
    
    updateTable() {
        const tbody = document.getElementById('duplicatesTableBody');
        tbody.innerHTML = '';
        
        if (!this.wordFrequency || !this.totalWords) {
            return;
        }
        
        // แปลง wordFrequency เป็น array และเรียงลำดับ
        const sortedWords = Object.entries(this.wordFrequency)
            .sort((a, b) => b[1] - a[1]);
        
        // คำนวณ pagination
        const totalItems = sortedWords.length;
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = Math.min(startIndex + this.itemsPerPage, totalItems);
        
        // แสดงข้อมูลสำหรับหน้าปัจจุบัน
        const currentPageData = sortedWords.slice(startIndex, endIndex);
        
        currentPageData.forEach(([word, frequency], index) => {
            const globalIndex = startIndex + index;
            const percentage = ((frequency / this.totalWords) * 100).toFixed(1);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-primary">${globalIndex + 1}</span></td>
                <td><strong>${word}</strong></td>
                <td><span class="badge bg-success">${frequency}</span></td>
                <td>${percentage}%</td>
            `;
            tbody.appendChild(row);
        });
        
        // ถ้าไม่มีคำ
        if (sortedWords.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="4" class="text-center text-muted py-4">
                    <i class="fas fa-info-circle me-2"></i>
                    ไม่พบคำในข้อความนี้
                </td>
            `;
            tbody.appendChild(row);
        }
        
        // อัปเดต pagination controls
        this.updatePaginationControls(totalItems, totalPages);
    }
    
    updatePaginationControls(totalItems, totalPages) {
        const paginationInfo = document.getElementById('paginationInfo');
        const paginationControls = document.getElementById('paginationControls');
        
        if (!paginationInfo || !paginationControls) return;
        
        // อัปเดตข้อมูล pagination
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, totalItems);
        paginationInfo.textContent = `แสดง ${startItem}-${endItem} จาก ${totalItems} รายการ`;
        
        // สร้างปุ่ม pagination
        paginationControls.innerHTML = '';
        
        // ปุ่ม Previous
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        const prevLink = document.createElement('a');
        prevLink.className = 'page-link';
        prevLink.href = '#';
        prevLink.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.currentPage > 1) {
                this.goToPage(this.currentPage - 1);
            }
        });
        prevLi.appendChild(prevLink);
        paginationControls.appendChild(prevLi);
        
        // ปุ่มหมายเลขหน้า
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        // ปุ่มหน้าแรก
        if (startPage > 1) {
            const firstLi = document.createElement('li');
            firstLi.className = 'page-item';
            const firstLink = document.createElement('a');
            firstLink.className = 'page-link';
            firstLink.href = '#';
            firstLink.textContent = '1';
            firstLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPage(1);
            });
            firstLi.appendChild(firstLink);
            paginationControls.appendChild(firstLi);
            
            if (startPage > 2) {
                const ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item disabled';
                ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                paginationControls.appendChild(ellipsisLi);
            }
        }
        
        // ปุ่มหมายเลขหน้า
        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
            const pageLink = document.createElement('a');
            pageLink.className = 'page-link';
            pageLink.href = '#';
            pageLink.textContent = i.toString();
            pageLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPage(i);
            });
            pageLi.appendChild(pageLink);
            paginationControls.appendChild(pageLi);
        }
        
        // ปุ่มหน้าสุดท้าย
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item disabled';
                ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                paginationControls.appendChild(ellipsisLi);
            }
            
            const lastLi = document.createElement('li');
            lastLi.className = 'page-item';
            const lastLink = document.createElement('a');
            lastLink.className = 'page-link';
            lastLink.href = '#';
            lastLink.textContent = totalPages.toString();
            lastLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPage(totalPages);
            });
            lastLi.appendChild(lastLink);
            paginationControls.appendChild(lastLi);
        }
        
        // ปุ่ม Next
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === totalPages ? 'disabled' : ''}`;
        const nextLink = document.createElement('a');
        nextLink.className = 'page-link';
        nextLink.href = '#';
        nextLink.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.currentPage < totalPages) {
                this.goToPage(this.currentPage + 1);
            }
        });
        nextLi.appendChild(nextLink);
        paginationControls.appendChild(nextLi);
    }
    
    goToPage(page) {
        if (!this.wordFrequency || !this.totalWords) return;
        
        const sortedWords = Object.entries(this.wordFrequency).sort((a, b) => b[1] - a[1]);
        const totalPages = Math.ceil(sortedWords.length / this.itemsPerPage);
        
        console.log(`Going to page ${page}, total pages: ${totalPages}, items per page: ${this.itemsPerPage}`);
        
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.updateTable();
        }
    }

    updateChart(topWords) {
        // ดึงข้อมูลทั้งหมดและเรียงลำดับตามความถี่
        const allWords = Object.entries(this.currentData.word_frequency).sort((a, b) => b[1] - a[1]);
        
        // เลือกข้อมูลที่จะแสดงตามสถานะ
        const wordsToShow = this.showingAllChartWords ? allWords : allWords.slice(0, 10);

        const labels = wordsToShow.map(([word, freq]) => word);
        const data = wordsToShow.map(([word, freq]) => freq);

        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.update('active');
    }

    updateChartInfo(wordFrequency) {
        const totalWords = Object.keys(wordFrequency).length;
        const chartWordCount = this.showingAllChartWords ? totalWords : Math.min(10, totalWords);
        
        document.getElementById('chartWordCount').textContent = chartWordCount;
        document.getElementById('totalWordCount').textContent = totalWords;
    }


    toggleChartView() {
        this.showingAllChartWords = !this.showingAllChartWords;
        
        const toggleBtn = document.getElementById('toggleChartBtn');
        const title = document.getElementById('chartTitle');
        
        if (this.showingAllChartWords) {
            toggleBtn.innerHTML = '<i class="fas fa-compress me-1"></i> แสดง Top 10';
            title.textContent = 'กราฟความถี่ของคำ (ทั้งหมด)';
        } else {
            toggleBtn.innerHTML = '<i class="fas fa-expand me-1"></i> แสดงทั้งหมด';
            title.textContent = 'กราฟความถี่ของคำ (Top 10)';
        }
        
        // อัปเดตกราฟโดยใช้ข้อมูลเดียวกัน
        this.updateChart(this.currentData.top_words);
        this.updateChartInfo(this.currentData.word_frequency);
    }



    exportDuplicates() {
        if (!this.currentData) {
            this.showAlert('ยังไม่มีข้อมูลที่จะส่งออก', 'warning');
            return;
        }

        const wordFrequency = this.currentData.word_frequency;
        const totalWords = this.currentData.total_words;
        
        // แปลง wordFrequency เป็น array และเรียงลำดับ (ส่งออกคำทั้งหมด)
        const sortedWords = Object.entries(wordFrequency)
            .sort((a, b) => b[1] - a[1]);
        
        if (sortedWords.length === 0) {
            this.showAlert('ไม่มีคำที่จะส่งออก', 'info');
            return;
        }

        // สร้าง CSV content ที่มีทั้งภาษาไทยและอังกฤษ พร้อม BOM สำหรับรองรับฟอนต์ไทย
        let csvContent = '\uFEFF'; // UTF-8 BOM สำหรับรองรับฟอนต์ภาษาไทย
        csvContent += 'อันดับ,คำ,ความถี่,เปอร์เซ็นต์,Rank,Word,Frequency,Percentage\n';
        sortedWords.forEach(([word, frequency], index) => {
            const percentage = ((frequency / totalWords) * 100).toFixed(2);
            csvContent += `${index + 1},"${word}",${frequency},${percentage}%,${index + 1},"${word}",${frequency},${percentage}%\n`;
        });

        // สร้างไฟล์และดาวน์โหลด พร้อม charset UTF-8
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `duplicate_words_analysis_${new Date().getTime()}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showAlert('ส่งออกข้อมูลเรียบร้อยแล้ว!', 'success');
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        const fileInput = event.target;
        
        if (!file) {
            return;
        }

        // Reset visual state
        fileInput.classList.remove('file-upload-success', 'file-upload-error');

        // ตรวจสอบประเภทไฟล์
        const fileName = file.name.toLowerCase();
        const isPDF = fileName.endsWith('.pdf');
        const isTXT = fileName.endsWith('.txt') || fileName.endsWith('.text');
        
        if (!isPDF && !isTXT) {
            fileInput.classList.add('file-upload-error');
            this.showAlert('กรุณาเลือกไฟล์ .txt หรือ .pdf เท่านั้น', 'warning');
            event.target.value = '';
            return;
        }

        // ตรวจสอบขนาดไฟล์ (จำกัดที่ 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            fileInput.classList.add('file-upload-error');
            this.showAlert('ขนาดไฟล์ใหญ่เกินไป กรุณาเลือกไฟล์ที่มีขนาดไม่เกิน 10MB', 'warning');
            event.target.value = '';
            return;
        }

        // ถ้าเป็น PDF ให้ส่งไปประมวลผลที่ server
        if (isPDF) {
            this.uploadAndProcessPDF(file);
        } else {
            // อ่านไฟล์ text ธรรมดา
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const content = e.target.result;
                    
                    // ใส่ข้อความลงใน textarea
                    document.getElementById('textInput').value = content;
                    
                    // Auto-resize textarea
                    const textarea = document.getElementById('textInput');
                    textarea.style.height = 'auto';
                    textarea.style.height = textarea.scrollHeight + 'px';
                    
                    // แสดง visual feedback สำเร็จ
                    fileInput.classList.add('file-upload-success');
                    this.showAlert(`อัปโหลดไฟล์ "${file.name}" สำเร็จ`, 'success');
                    
                } catch (error) {
                    fileInput.classList.add('file-upload-error');
                    this.showAlert('เกิดข้อผิดพลาดในการอ่านไฟล์: ' + error.message, 'danger');
                    event.target.value = '';
                }
            };

            reader.onerror = () => {
                fileInput.classList.add('file-upload-error');
                this.showAlert('เกิดข้อผิดพลาดในการอ่านไฟล์', 'danger');
                event.target.value = '';
            };

            reader.readAsText(file, 'UTF-8');
        }
    }

    async uploadAndProcessPDF(file) {
        const fileInput = document.getElementById('fileInput');
        
        // แสดง Progress Bar
        this.showProgress(true);
        this.updateProgress(10, 'กำลังอัปโหลด PDF...');

        try {
            const formData = new FormData();
            formData.append('file', file);

            this.updateProgress(30, 'กำลังแปลง PDF เป็น text...');

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            this.updateProgress(60, 'กำลังวิเคราะห์ข้อความ...');

            const result = await response.json();

            this.updateProgress(90, 'กำลังสร้างกราฟและรายงาน...');

            if (result.success) {
                this.currentData = result.data;
                
                // ใส่ข้อความที่แปลงได้ลงใน textarea
                document.getElementById('textInput').value = result.data.content;
                
                // แสดงผลลัพธ์
                this.displayResults(result.data);
                
                this.updateProgress(100, 'วิเคราะห์ PDF เสร็จสมบูรณ์!');
                
                // ซ่อน Progress Bar
                setTimeout(() => {
                    this.showProgress(false);
                }, 1000);
                
                fileInput.classList.add('file-upload-success');
                this.showAlert(
                    `แปลง PDF "${file.name}" สำเร็จ (${result.data.extraction_method})`, 
                    'success'
                );
            } else {
                fileInput.classList.add('file-upload-error');
                this.showAlert(result.error || 'เกิดข้อผิดพลาดในการแปลง PDF', 'danger');
                this.showProgress(false);
                fileInput.value = '';
            }
        } catch (error) {
            fileInput.classList.add('file-upload-error');
            this.showAlert('เกิดข้อผิดพลาดในการอัปโหลด PDF: ' + error.message, 'danger');
            this.showProgress(false);
            fileInput.value = '';
        }
    }

    showProgress(show) {
        const progressContainer = document.getElementById('progressContainer');
        progressContainer.style.display = show ? 'block' : 'none';
    }

    updateProgress(percent, message) {
        const progressBar = document.getElementById('progressBar');
        const progressMessage = document.getElementById('progressMessage');
        const progressPercent = document.getElementById('progressPercent');
        
        progressBar.style.width = percent + '%';
        progressMessage.textContent = message;
        progressPercent.textContent = percent + '%';
    }

    showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto remove after 2 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 2000);
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    createVibrantConfetti() {
        const confettiContainer = document.createElement('div');
        confettiContainer.className = 'vibrant-confetti';
        document.body.appendChild(confettiContainer);

        const sparkles = ['⚡', '✨', '🌟', '💫', '⭐', '🔥', '💎', '🎆'];
        
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                const sparkle = document.createElement('div');
                sparkle.className = 'vibrant-sparkle';
                sparkle.textContent = sparkles[Math.floor(Math.random() * sparkles.length)];
                sparkle.style.left = Math.random() * 100 + '%';
                sparkle.style.animationDelay = Math.random() * 3 + 's';
                sparkle.style.fontSize = (Math.random() * 1 + 0.5) + 'rem';
                confettiContainer.appendChild(sparkle);

                setTimeout(() => {
                    if (sparkle.parentNode) {
                        sparkle.parentNode.removeChild(sparkle);
                    }
                }, 3000);
            }, i * 100);
        }

        setTimeout(() => {
            if (confettiContainer.parentNode) {
                confettiContainer.parentNode.removeChild(confettiContainer);
            }
        }, 5000);
    }

    resetAnalysis() {
        try {
            // ซ่อน Results Section
            document.getElementById('resultsSection').style.display = 'none';
            
            // แสดง Welcome Section
            document.getElementById('welcomeSection').style.display = 'block';
            
            // ล้างข้อมูลทั้งหมด
            document.getElementById('textInput').value = '';
            document.getElementById('fileInput').value = '';
            
            // ล้างตารางคำซ้ำ
            document.getElementById('duplicatesTableBody').innerHTML = '';
            
            // รีเซ็ตปุ่มสลับกราฟ
            this.showingAllChartWords = false;
            const toggleChartBtn = document.getElementById('toggleChartBtn');
            const chartTitle = document.getElementById('chartTitle');
            toggleChartBtn.innerHTML = '<i class="fas fa-expand me-1"></i> แสดงทั้งหมด';
            chartTitle.textContent = 'กราฟความถี่ของคำ (Top 10)';
            
            // ล้างข้อมูลกราฟ
            document.getElementById('chartWordCount').textContent = '0';
            document.getElementById('totalWordCount').textContent = '0';
            
            // ล้าง Stats
            document.getElementById('totalWordsStat').textContent = '0';
            document.getElementById('uniqueWordsStat').textContent = '0';
            
            // ล้างกราฟ
            if (this.chart) {
                this.chart.data.labels = [];
                this.chart.data.datasets[0].data = [];
                this.chart.update();
            }
            
            // ล้างข้อมูลทั้งหมด
            this.currentData = null;
            
            // ล้าง visual feedback ของไฟล์
            const fileInput = document.getElementById('fileInput');
            fileInput.classList.remove('file-upload-success', 'file-upload-error');
            
            // เลื่อนกลับไปที่ด้านบน
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            this.showAlert('รีเซ็ตการวิเคราะห์เรียบร้อยแล้ว', 'info');
        } catch (error) {
            this.showAlert('เกิดข้อผิดพลาดในการรีเซ็ต: ' + error.message, 'danger');
        }
    }
}

// Initialize the analyzer when the page loads
document.addEventListener('DOMContentLoaded', function() {
    new WordFrequencyAnalyzer();
});