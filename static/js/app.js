// ============================
// FitOl - Ana JavaScript
// ============================

// Sidebar toggle (mobil)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// Flash mesajlarını otomatik kapat
document.addEventListener('DOMContentLoaded', function () {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(function () { flash.remove(); }, 300);
        }, 4000);
    });
});

// Besin arama fonksiyonu
function initFoodSearch() {
    const searchInput = document.getElementById('foodSearch');
    const resultsDiv = document.getElementById('searchResults');
    if (!searchInput || !resultsDiv) return;

    let timeout = null;

    searchInput.addEventListener('input', function () {
        const query = this.value.trim();
        clearTimeout(timeout);

        if (query.length < 2) {
            resultsDiv.classList.remove('show');
            return;
        }

        timeout = setTimeout(function () {
            fetch('/food/search?q=' + encodeURIComponent(query))
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.length === 0) {
                        resultsDiv.innerHTML = '<div class="search-item"><span class="search-item-name">Sonuç bulunamadı</span></div>';
                    } else {
                        resultsDiv.innerHTML = data.map(function (food) {
                            return '<div class="search-item" onclick="selectFood(\'' +
                                food.name.replace(/'/g, "\\'") + '\', ' +
                                food.calories + ', ' +
                                food.protein + ', ' +
                                food.carbs + ', ' +
                                food.fat + ')">' +
                                '<span class="search-item-name">' + food.name + ' <small style="color:var(--text-muted)">(' + food.unit + ')</small></span>' +
                                '<span class="search-item-cal">' + food.calories + ' kcal</span>' +
                                '</div>';
                        }).join('');
                    }
                    resultsDiv.classList.add('show');
                });
        }, 300);
    });

    // Dışarı tıklanınca kapat
    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
            resultsDiv.classList.remove('show');
        }
    });
}

// Seçilen yemeğin baz besin değerleri (porsiyon hesaplaması için)
var baseFoodValues = { calories: 0, protein: 0, carbs: 0, fat: 0 };

function selectFood(name, calories, protein, carbs, fat) {
    // Baz değerleri sakla
    baseFoodValues = {
        calories: parseFloat(calories),
        protein: parseFloat(protein),
        carbs: parseFloat(carbs),
        fat: parseFloat(fat)
    };

    document.getElementById('foodName').value = name;
    document.getElementById('searchResults').classList.remove('show');

    // Porsiyon tipine göre değerleri hesapla
    updatePortionValues();
}

// Porsiyon tipi veya miktar değiştiğinde değerleri güncelle
function updatePortionMultiplier() {
    updatePortionValues();
}

function updatePortionValues() {
    var portionType = document.getElementById('portionType');
    var portionAmount = document.getElementById('portionAmount');
    if (!portionType || !portionAmount) return;

    var selected = portionType.options[portionType.selectedIndex];
    var multiplier = parseFloat(selected.getAttribute('data-multiplier')) || 1;
    var amount = parseFloat(portionAmount.value) || 1;

    var totalMultiplier = multiplier * amount;

    var cal = Math.round(baseFoodValues.calories * totalMultiplier * 10) / 10;
    var pro = Math.round(baseFoodValues.protein * totalMultiplier * 10) / 10;
    var carb = Math.round(baseFoodValues.carbs * totalMultiplier * 10) / 10;
    var fat = Math.round(baseFoodValues.fat * totalMultiplier * 10) / 10;

    document.getElementById('foodCalories').value = cal;
    document.getElementById('foodProtein').value = pro;
    document.getElementById('foodCarbs').value = carb;
    document.getElementById('foodFat').value = fat;
}

// Egzersiz seçimi
function selectExercise(name, category) {
    const nameInput = document.getElementById('exerciseName');
    const catInput = document.getElementById('exerciseCategory');
    if (nameInput) nameInput.value = name;
    if (catInput) catInput.value = category;
}

// Modal
function openModal(id) {
    document.getElementById(id).classList.add('show');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}

// Chart.js varsayılan ayarlar
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#9ca3af';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';
    Chart.defaults.font.family = "'Inter', sans-serif";
}

// Haftalık kalori grafiği
function initWeeklyChart(labels, data) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Kalori (kcal)',
                data: data,
                backgroundColor: function (context) {
                    const chart = context.chart;
                    const { ctx: c, chartArea } = chart;
                    if (!chartArea) return '#10b981';
                    const gradient = c.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
                    gradient.addColorStop(1, 'rgba(20, 184, 166, 0.8)');
                    return gradient;
                },
                borderColor: '#10b981',
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

// Ölçüm grafiği
function initMeasurementChart() {
    const ctx = document.getElementById('measurementChart');
    if (!ctx) return;

    fetch('/measurement/chart-data?days=90')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Kilo (kg)',
                            data: data.weight,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Bel (cm)',
                            data: data.waist,
                            borderColor: '#f97316',
                            backgroundColor: 'rgba(249, 115, 22, 0.1)',
                            fill: false,
                            tension: 0.4,
                            pointRadius: 3,
                            pointHoverRadius: 5
                        },
                        {
                            label: 'Göğüs (cm)',
                            data: data.chest,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            fill: false,
                            tension: 0.4,
                            pointRadius: 3,
                            pointHoverRadius: 5
                        },
                        {
                            label: 'Kol (cm)',
                            data: data.arm,
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            fill: false,
                            tension: 0.4,
                            pointRadius: 3,
                            pointHoverRadius: 5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { usePointStyle: true, padding: 16 }
                        }
                    },
                    scales: {
                        y: {
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        });
}

// Rapor grafikleri
function initReportCharts(dailyData) {
    // Kalori giriş/çıkış grafiği
    const calChart = document.getElementById('calorieChart');
    if (calChart && dailyData) {
        new Chart(calChart, {
            type: 'line',
            data: {
                labels: dailyData.labels,
                datasets: [
                    {
                        label: 'Alınan Kalori',
                        data: dailyData.calories_in,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Yakılan Kalori',
                        data: dailyData.calories_out,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { usePointStyle: true }
                    }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Su grafiği
    const waterChart = document.getElementById('waterReportChart');
    if (waterChart && dailyData) {
        new Chart(waterChart, {
            type: 'bar',
            data: {
                labels: dailyData.labels,
                datasets: [{
                    label: 'Su (ml)',
                    data: dailyData.water,
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}

// Sayfa yüklendiğinde search'ü başlat
document.addEventListener('DOMContentLoaded', function () {
    initFoodSearch();
});
