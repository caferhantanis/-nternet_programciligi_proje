// script.js - Öğrenci Bilgi Sistemi için JavaScript işlevleri

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap bileşenlerini etkinleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Silme işlemi onayı
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Bu kaydı silmek istediğinizden emin misiniz?')) {
                e.preventDefault();
            }
        });
    });
    
    // Form doğrulama
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Not değeri için ekstra doğrulama
    const notInput = document.querySelector('#deger');
    if (notInput) {
        notInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) this.value = 0;
            if (value > 100) this.value = 100;
        });
    }
    
    // Flash mesajlarını otomatik kapat
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(message);
            alert.close();
        }, 5000);
    });
    
    // Tablo sıralama
    const sortableTables = document.querySelectorAll('.sortable');
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', function() {
                const column = this.dataset.sort;
                const direction = this.classList.contains('asc') ? 'desc' : 'asc';
                
                // Tüm başlıkların sınıflarını temizle
                headers.forEach(h => h.classList.remove('asc', 'desc'));
                
                // Tıklanan başlığa sıralama sınıfı ekle
                this.classList.add(direction);
                
                // Tablo satırlarını sırala
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    let cellA = a.querySelector(`td:nth-child(${getColumnIndex(column) + 1})`).textContent;
                    let cellB = b.querySelector(`td:nth-child(${getColumnIndex(column) + 1})`).textContent;
                    
                    // Sayısal değerler için
                    if (!isNaN(cellA) && !isNaN(cellB)) {
                        cellA = parseFloat(cellA);
                        cellB = parseFloat(cellB);
                    }
                    
                    if (direction === 'asc') {
                        return cellA > cellB ? 1 : -1;
                    } else {
                        return cellA < cellB ? 1 : -1;
                    }
                });
                
                // Sıralanmış satırları tekrar ekle
                rows.forEach(row => tbody.appendChild(row));
            });
        });
        
        function getColumnIndex(columnName) {
            const headers = Array.from(table.querySelectorAll('th'));
            return headers.findIndex(h => h.dataset.sort === columnName);
        }
    });
    
    // İstatistikler sayfasındaki grafikleri çiz
    if (document.getElementById('ogrenciChart')) {
        drawStudentChart();
    }
    
    if (document.getElementById('dersChart')) {
        drawCourseChart();
    }
});

// Öğrenci not ortalamaları grafiği
function drawStudentChart() {
    const canvas = document.getElementById('ogrenciChart');
    const ctx = canvas.getContext('2d');
    
    // Veriyi grafikten al
    const labels = [];
    const data = [];
    
    document.querySelectorAll('.ogrenci-ortalama').forEach(item => {
        labels.push(item.dataset.name);
        data.push(parseFloat(item.dataset.average));
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Not Ortalaması',
                data: data,
                backgroundColor: 'rgba(74, 137, 220, 0.7)',
                borderColor: 'rgba(74, 137, 220, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Ders not ortalamaları grafiği
function drawCourseChart() {
    const canvas = document.getElementById('dersChart');
    const ctx = canvas.getContext('2d');
    
    // Veriyi grafikten al
    const labels = [];
    const data = [];
    
    document.querySelectorAll('.ders-ortalama').forEach(item => {
        labels.push(item.dataset.name);
        data.push(parseFloat(item.dataset.average));
    });
    
    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true
        }
    });
}

// Arama fonksiyonu
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toUpperCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        let found = false;
        const cells = rows[i].getElementsByTagName('td');
        
        for (let j = 0; j < cells.length; j++) {
            const cellText = cells[j].textContent || cells[j].innerText;
            
            if (cellText.toUpperCase().indexOf(filter) > -1) {
                found = true;
                break;
            }
        }
        
        rows[i].style.display = found ? '' : 'none';
    }
}