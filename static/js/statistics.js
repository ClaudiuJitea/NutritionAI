/**
 * Statistics Page JavaScript for Diet & Nutrition AI Application
 */

// Global chart instances to allow updating
let calorieChart, macroChart, categoryChart, goalChart;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize time range selector
    initTimeRangeSelector();
    
    // Initialize charts
    initCharts();
    
    // Initialize export buttons
    initExportButtons();
    
    // Load AI insights
    loadAIInsights();
});

/**
 * Time Range Selector
 */
function initTimeRangeSelector() {
    const timeRangeBtns = document.querySelectorAll('.time-range-btn');
    
    if (timeRangeBtns.length) {
        timeRangeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Remove active class from all buttons
                timeRangeBtns.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get time range
                const timeRange = this.getAttribute('data-range');
                
                // Update charts with new time range
                loadChartData(timeRange);
                
                // Update summary data
                loadSummaryData(timeRange);
                
                // Update AI insights
                loadAIInsights(timeRange);
            });
        });
        
        // Load data for default time range (first button)
        const defaultTimeRange = timeRangeBtns[0].getAttribute('data-range');
        loadChartData(defaultTimeRange);
        loadSummaryData(defaultTimeRange);
    }
}

/**
 * Initialize Charts
 */
function initCharts() {
    // Calorie Trend Chart
    initCalorieChart();
    
    // Macro Distribution Chart
    initMacroChart();
    
    // Food Categories Chart
    initCategoryChart();
    
    // Goal Achievement Chart
    initGoalChart();
}

/**
 * Initialize Calorie Trend Chart
 */
function initCalorieChart() {
    const ctx = document.getElementById('calorie-chart');
    if (!ctx) return;
    
    calorieChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Calories',
                data: [],
                borderColor: 'rgb(0, 210, 163)',
                backgroundColor: 'rgba(0, 210, 163, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Goal',
                data: [],
                borderColor: 'rgba(247, 201, 74, 0.5)',
                borderDash: [5, 5],
                borderWidth: 2,
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#a0a0a0'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                }
            }
        }
    });
}

/**
 * Initialize Macro Distribution Chart
 */
function initMacroChart() {
    const ctx = document.getElementById('macro-chart');
    if (!ctx) return;
    
    macroChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Protein', 'Carbs', 'Fat'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgb(74, 247, 166)',  // Protein
                    'rgb(247, 201, 74)',  // Carbs
                    'rgb(247, 74, 108)'   // Fat
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0a0a0',
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${percentage}% (${value}g)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Food Categories Chart
 */
function initCategoryChart() {
    const ctx = document.getElementById('category-chart');
    if (!ctx) return;
    
    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Calories by Food Category',
                data: [],
                backgroundColor: 'rgba(0, 210, 163, 0.7)',
                borderColor: 'rgb(0, 210, 163)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                }
            }
        }
    });
}

/**
 * Initialize Goal Achievement Chart
 */
function initGoalChart() {
    const ctx = document.getElementById('goal-chart');
    if (!ctx) return;
    
    goalChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Calories', 'Protein', 'Carbs', 'Fat', 'Water'],
            datasets: [{
                label: 'Goal Achievement (%)',
                data: [0, 0, 0, 0, 0],
                backgroundColor: 'rgba(0, 210, 163, 0.2)',
                borderColor: 'rgb(0, 210, 163)',
                pointBackgroundColor: 'rgb(0, 210, 163)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(0, 210, 163)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#a0a0a0'
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: '#a0a0a0',
                        z: 100
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#a0a0a0'
                    }
                }
            }
        }
    });
}

/**
 * Load Chart Data
 */
async function loadChartData(timeRange) {
    try {
        // Show loading state
        document.querySelectorAll('.chart-container').forEach(container => {
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = '<div class="loading-spinner"></div>';
            container.appendChild(loadingOverlay);
        });
        
        // Fetch data from API
        const data = await fetchData(`/api/statistics?range=${timeRange}`);
        
        // Remove loading overlays
        document.querySelectorAll('.loading-overlay').forEach(overlay => {
            overlay.remove();
        });
        
        // Update charts with new data
        updateCalorieChart(data.calorie_data);
        updateMacroChart(data.macro_data);
        updateCategoryChart(data.category_data);
        updateGoalChart(data.goal_data);
        
    } catch (error) {
        console.error('Error loading chart data:', error);
        
        // Remove loading overlays
        document.querySelectorAll('.loading-overlay').forEach(overlay => {
            overlay.remove();
        });
        
        // Show error state
        document.querySelectorAll('.chart-container').forEach(container => {
            container.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-exclamation-circle"></i>
                    <h3>Error Loading Data</h3>
                    <p>There was a problem loading your nutrition data. Please try again later.</p>
                </div>
            `;
        });
    }
}

/**
 * Update Calorie Chart
 */
function updateCalorieChart(data) {
    if (!calorieChart || !data) return;
    
    if (data.labels.length === 0) {
        // No data available
        document.getElementById('calorie-chart').parentNode.innerHTML = `
            <div class="no-data">
                <i class="fas fa-utensils"></i>
                <h3>No Calorie Data</h3>
                <p>Start logging your meals to see your calorie trends.</p>
            </div>
        `;
        return;
    }
    
    calorieChart.data.labels = data.labels;
    calorieChart.data.datasets[0].data = data.calories;
    calorieChart.data.datasets[1].data = data.goals;
    calorieChart.update();
}

/**
 * Update Macro Chart
 */
function updateMacroChart(data) {
    if (!macroChart || !data) return;
    
    if (data.protein === 0 && data.carbs === 0 && data.fat === 0) {
        // No data available
        document.getElementById('macro-chart').parentNode.innerHTML = `
            <div class="no-data">
                <i class="fas fa-chart-pie"></i>
                <h3>No Macro Data</h3>
                <p>Start logging your meals to see your macro distribution.</p>
            </div>
        `;
        return;
    }
    
    macroChart.data.datasets[0].data = [data.protein, data.carbs, data.fat];
    macroChart.update();
}

/**
 * Update Category Chart
 */
function updateCategoryChart(data) {
    if (!categoryChart || !data) return;
    
    if (data.labels.length === 0) {
        // No data available
        document.getElementById('category-chart').parentNode.innerHTML = `
            <div class="no-data">
                <i class="fas fa-tags"></i>
                <h3>No Category Data</h3>
                <p>Start logging your meals to see calories by food category.</p>
            </div>
        `;
        return;
    }
    
    categoryChart.data.labels = data.labels;
    categoryChart.data.datasets[0].data = data.values;
    
    // Generate gradient colors
    const colors = data.labels.map((_, index) => {
        const hue = (index * 30) % 360;
        return `hsla(${hue}, 70%, 60%, 0.7)`;
    });
    
    categoryChart.data.datasets[0].backgroundColor = colors;
    categoryChart.update();
}

/**
 * Update Goal Chart
 */
function updateGoalChart(data) {
    if (!goalChart || !data) return;
    
    if (!data.calories) {
        // No data available
        document.getElementById('goal-chart').parentNode.innerHTML = `
            <div class="no-data">
                <i class="fas fa-bullseye"></i>
                <h3>No Goal Data</h3>
                <p>Start logging your meals to see your goal achievement.</p>
            </div>
        `;
        return;
    }
    
    goalChart.data.datasets[0].data = [
        data.calories,
        data.protein,
        data.carbs,
        data.fat,
        data.water
    ];
    goalChart.update();
}

/**
 * Load Summary Data
 */
async function loadSummaryData(timeRange) {
    try {
        const summaryContent = document.querySelector('.summary-content');
        if (!summaryContent) return;
        
        // Show loading state
        summaryContent.innerHTML = '<div class="spinner"></div>';
        
        // Fetch data from API
        const data = await fetchData(`/api/summary?range=${timeRange}`);
        
        // Update summary content
        summaryContent.innerHTML = `
            <div class="summary-item">
                <div class="summary-label">Average Daily Calories</div>
                <div class="summary-value">${data.avg_calories} kcal</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Average Protein</div>
                <div class="summary-value">${data.avg_protein}g</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Average Carbs</div>
                <div class="summary-value">${data.avg_carbs}g</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Average Fat</div>
                <div class="summary-value">${data.avg_fat}g</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Average Water Intake</div>
                <div class="summary-value">${data.avg_water} ml</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Days Logged</div>
                <div class="summary-value">${data.days_logged} / ${data.total_days}</div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading summary data:', error);
        
        // Show error state
        const summaryContent = document.querySelector('.summary-content');
        if (summaryContent) {
            summaryContent.innerHTML = `
                <div class="error-state">
                    <p>Error loading summary data. Please try again later.</p>
                </div>
            `;
        }
    }
}

/**
 * Load AI Insights
 */
async function loadAIInsights(timeRange = 'week') {
    try {
        const insightsContent = document.querySelector('.insights-content');
        if (!insightsContent) return;
        
        // Show loading state
        insightsContent.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Generating AI insights based on your nutrition data...</p>
            </div>
        `;
        
        // Fetch data from API
        const data = await fetchData(`/api/insights?range=${timeRange}`);
        
        if (!data.insights || data.insights.length === 0) {
            insightsContent.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-lightbulb"></i>
                    <h3>No Insights Available</h3>
                    <p>Continue logging your nutrition data to receive personalized insights.</p>
                </div>
            `;
            return;
        }
        
        // Build insights HTML
        let insightsHTML = '';
        data.insights.forEach(insight => {
            let iconClass = 'fas fa-info-circle';
            let titleClass = 'neutral';
            
            if (insight.type === 'positive') {
                iconClass = 'fas fa-check-circle';
                titleClass = 'positive';
            } else if (insight.type === 'negative') {
                iconClass = 'fas fa-exclamation-circle';
                titleClass = 'negative';
            }
            
            insightsHTML += `
                <div class="insight-item">
                    <div class="insight-title ${titleClass}">
                        <i class="${iconClass}"></i>
                        ${insight.title}
                    </div>
                    <div class="insight-description">
                        ${insight.description}
                    </div>
                    ${insight.action ? `
                        <a href="${insight.action_url || '#'}" class="insight-action">
                            ${insight.action} <i class="fas fa-arrow-right"></i>
                        </a>
                    ` : ''}
                </div>
            `;
        });
        
        insightsContent.innerHTML = insightsHTML;
        
    } catch (error) {
        console.error('Error loading AI insights:', error);
        
        // Show error state
        const insightsContent = document.querySelector('.insights-content');
        if (insightsContent) {
            insightsContent.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <h3>Error Loading Insights</h3>
                    <p>There was a problem generating your nutrition insights. Please try again later.</p>
                </div>
            `;
        }
    }
}

/**
 * Initialize Export Buttons
 */
function initExportButtons() {
    const csvBtn = document.getElementById('export-csv');
    const jsonBtn = document.getElementById('export-json');
    const pdfBtn = document.getElementById('export-pdf');
    
    if (csvBtn) {
        csvBtn.addEventListener('click', function() {
            exportData('csv');
        });
    }
    
    if (jsonBtn) {
        jsonBtn.addEventListener('click', function() {
            exportData('json');
        });
    }
    
    if (pdfBtn) {
        pdfBtn.addEventListener('click', function() {
            exportData('pdf');
        });
    }
}

/**
 * Export Data
 */
function exportData(format) {
    const timeRangeBtn = document.querySelector('.time-range-btn.active');
    const timeRange = timeRangeBtn ? timeRangeBtn.getAttribute('data-range') : 'week';
    
    window.location.href = `/api/export?format=${format}&range=${timeRange}`;
}
