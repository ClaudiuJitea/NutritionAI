/**
 * Dashboard JavaScript for Diet & Nutrition AI Application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Image Upload
    initImageUpload();
    
    // Initialize Image Preview Modal
    initImagePreviewModal();
    
    // Initialize Weekly Trends Chart
    initWeeklyTrendsChart();
    
    // Initialize Progress Bars
    initProgressBars();
});

/**
 * Image Upload and AI Analysis
 */
function initImageUpload() {
    const imageUploadForm = document.getElementById('image-upload-form');
    const imageInput = document.getElementById('image-input');
    const uploadBtn = document.querySelector('.upload-btn');
    const aiResults = document.querySelector('.ai-results');
    
    if (imageUploadForm && imageInput && uploadBtn) {
        // Prevent default form submission
        imageUploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
        });
        // The <label for="image-input"> (uploadBtn) will naturally trigger the file input when clicked.
        // Explicitly calling imageInput.click() in a JavaScript event handler for the label
        // can sometimes lead to the dialog appearing twice or other unexpected behavior.
        // We will rely on the default HTML behavior of the label.
        // uploadBtn.addEventListener('click', function() {
        //     imageInput.click();
        // });
        
        // Handle file selection
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // Show loading state
                aiResults.innerHTML = `
                    <div class="loading-state">
                        <div class="spinner"></div>
                        <p>Analyzing your food image...</p>
                    </div>
                `;
                
                // Create FormData object to handle the form submission with CSRF token
                const formData = new FormData(imageUploadForm);
                
                // Submit the form using fetch API to handle CSRF properly
                fetch(imageUploadForm.action, {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (!response.ok) {
                        // Try to parse the error response as JSON
                        return response.json()
                            .then(errData => {
                                // If errData.error exists, use it, otherwise use a generic message
                                throw new Error(errData.error || `Server error: ${response.status}`);
                            })
                            .catch(() => {
                                // If response.json() fails (e.g., error response wasn't JSON)
                                throw new Error(`Server error: ${response.status} - Invalid error response format.`);
                            });
                    }
                    return response.json(); // If response.ok, parse the success JSON body.
                })
                .then(data => {
                    // This 'data' is the parsed JSON from a successful (response.ok === true) response.
                    // The handleAIAnalysisResponse function itself checks for data.error for application-level errors.
                    handleAIAnalysisResponse(data);
                })
                .catch(error => { // Catches errors from fetch, .then() blocks, or response.json() parsing
                    aiResults.innerHTML = `
                        <div class="error-state">
                            <i class="fas fa-exclamation-circle"></i>
                            <h3>Analysis Failed</h3>
                            <p>${error.message}</p> <!-- Display the actual error message -->
                            <button class="btn btn-outline" onclick="location.reload()">
                                <i class="fas fa-redo"></i> Try Again
                            </button>
                        </div>
                    `;
                    console.error('Fetch Error:', error);
                });
                
                // Prevent the default form submission
                return false;
            }
        });
    }
}

/**
 * Image Preview Modal
 */
function initImagePreviewModal() {
    const modal = document.getElementById('image-preview-modal');
    const modalImage = document.getElementById('modal-image');
    const closeBtn = document.querySelector('.modal-content .close');
    const previewLinks = document.querySelectorAll('.food-image-preview');
    
    if (modal && modalImage && previewLinks.length) {
        previewLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const imageUrl = this.getAttribute('data-image');
                modalImage.src = imageUrl;
                modal.style.display = 'block';
            });
        });
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                modal.style.display = 'none';
            });
        }
        
        // Close when clicking outside the modal content
        window.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
}

/**
 * Add Food from AI Analysis
 */
function addFoodFromAnalysis(analysisId) {
    const addForm = document.getElementById('add-from-analysis-form');
    const analysisIdInput = document.getElementById('analysis-id');
    
    if (addForm && analysisIdInput) {
        analysisIdInput.value = analysisId;
        addForm.submit();
    }
}

/**
 * Update Calorie Progress Circle
 */
function updateCalorieProgressCircle(consumed, goal) {
    const circle = document.querySelector('.circle');
    if (!circle) return;
    
    // Calculate actual percentage (can be over 100%)
    const actualPercentage = Math.round((consumed / goal) * 100);
    
    // For the circle, we cap at 100% for visual display
    const displayPercentage = Math.min(actualPercentage, 100);
    
    // Update the circle fill
    const strokeDasharray = `${displayPercentage}, 100`;
    circle.style.strokeDasharray = strokeDasharray;
    
    // Update percentage text (show actual percentage, even if over 100%)
    const percentageText = document.querySelector('.percentage');
    if (percentageText) {
        percentageText.textContent = `${actualPercentage}%`;
        
        // Change color if over goal
        if (actualPercentage > 100) {
            percentageText.style.fill = 'var(--exceeded-color)';
        } else {
            percentageText.style.fill = ''; // Reset to default
        }
    }
    
    // Update remaining/extra text
    const remainingText = document.querySelector('.calorie-remaining');
    if (remainingText) {
        if (consumed > goal) {
            remainingText.textContent = `Extra: ${consumed - goal} kcal`;
            remainingText.style.color = 'var(--exceeded-color)';
        } else {
            remainingText.textContent = `Remaining: ${goal - consumed} kcal`;
            remainingText.style.color = ''; // Reset to default
        }
    }
    
    // Update color based on percentage
    if (actualPercentage > 100) {
        circle.style.stroke = 'var(--exceeded-color)';
    } else if (actualPercentage > 90) {
        circle.style.stroke = 'var(--warning-color)';
    } else {
        circle.style.stroke = 'var(--accent-color)';
    }
}

/**
 * Update Water Progress
 */
function updateWaterProgress(consumed, goal) {
    const waterLevel = document.querySelector('.water-level');
    if (!waterLevel) return;
    
    const percentage = Math.min(Math.round((consumed / goal) * 100), 100);
    waterLevel.style.height = `${percentage}%`;
    
    // Update color based on percentage
    if (percentage < 30) {
        waterLevel.style.backgroundColor = 'var(--danger-color)';
    } else if (percentage < 60) {
        waterLevel.style.backgroundColor = 'var(--warning-color)';
    } else {
        waterLevel.style.backgroundColor = 'var(--info-color)';
    }
}

/**
 * Initialize Weekly Trends Chart
 */
function initWeeklyTrendsChart() {
    console.log('Initializing weekly trends chart');
    const chartCanvas = document.getElementById('weeklyTrendsChart');
    
    if (!chartCanvas) {
        console.error('Chart canvas element not found');
        return;
    }
    
    console.log('Chart canvas found, proceeding with initialization');
    
    // Create the chart with demo data immediately to ensure something displays
    const demoData = {
        days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        calories: [1800, 2100, 1950, 2000, 1700, 2200, 1900],
        protein: [65, 78, 72, 70, 60, 85, 68],
        carbs: [180, 210, 200, 205, 170, 220, 190],
        fat: [60, 70, 65, 68, 55, 75, 65]
    };
    
    createWeeklyTrendsChart(chartCanvas, demoData);
    
    // Then try to fetch real data and update the chart
    console.log('Fetching real data from API');
    fetch('/api/weekly_nutrition')
        .then(response => {
            if (!response.ok) {
                throw new Error(`API returned status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Successfully received data:', data);
            window.weeklyNutritionData = data;
            createWeeklyTrendsChart(chartCanvas, data);
        })
        .catch(error => {
            console.error('Error fetching weekly nutrition data:', error);
            // We already created the chart with demo data, so no further action needed
        });
}

/**
 * Create Weekly Trends Chart
 */
function createWeeklyTrendsChart(canvas, data) {
    console.log('Creating chart with data:', data);
    
    // If no data is provided, use demo data
    if (!data) {
        console.warn('No data provided, using demo data');
        data = {
            days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            calories: [1800, 2100, 1950, 2000, 1700, 2200, 1900],
            protein: [65, 78, 72, 70, 60, 85, 68],
            carbs: [180, 210, 200, 205, 170, 220, 190],
            fat: [60, 70, 65, 68, 55, 75, 65]
        };
    }
    
    try {
        // Create the chart
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (window.weeklyTrendsChart && typeof window.weeklyTrendsChart.destroy === 'function') {
            console.log('Destroying existing chart');
            window.weeklyTrendsChart.destroy();
        }
        
        // Set up chart options
        const options = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Calories (kcal)',
                        color: '#3dd598'
                    },
                    ticks: {
                        color: '#7b7f9e'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                y1: {
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Macros (g)',
                        color: '#7b7f9e'
                    },
                    ticks: {
                        color: '#7b7f9e'
                    },
                    grid: {
                        display: false
                    }
                },
                x: {
                    ticks: {
                        color: '#7b7f9e'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#7b7f9e',
                        boxWidth: 12,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(28, 28, 39, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#a9abb6',
                    borderColor: '#3dd598',
                    borderWidth: 1
                }
            }
        };
        
        // Create the chart
        window.weeklyTrendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.days,
                datasets: [
                    {
                        label: 'Calories (kcal)',
                        data: data.calories,
                        borderColor: '#3dd598',
                        backgroundColor: 'rgba(61, 213, 152, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y',
                        fill: true
                    },
                    {
                        label: 'Protein (g)',
                        data: data.protein,
                        borderColor: '#665df5',
                        backgroundColor: 'rgba(102, 93, 245, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1',
                        fill: true
                    },
                    {
                        label: 'Carbs (g)',
                        data: data.carbs,
                        borderColor: '#ffc542',
                        backgroundColor: 'rgba(255, 197, 66, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1',
                        fill: true
                    },
                    {
                        label: 'Fat (g)',
                        data: data.fat,
                        borderColor: '#ff575f',
                        backgroundColor: 'rgba(255, 87, 95, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1',
                        fill: true
                    }
                ]
            },
            options: options
        });
        
        console.log('Chart created successfully');
    } catch (error) {
        console.error('Error creating chart:', error);
    }
}

/**
 * Update Macro Progress Bars
 */
function updateMacroProgressBars(protein, proteinGoal, carbs, carbsGoal, fat, fatGoal) {
    // Protein progress
    const proteinProgress = document.querySelector('.progress-bar.protein');
    if (proteinProgress) {
        const proteinPercentage = Math.min(Math.round((protein / proteinGoal) * 100), 100);
        proteinProgress.style.width = `${proteinPercentage}%`;
    }
    
    // Carbs progress
    const carbsProgress = document.querySelector('.progress-bar.carbs');
    if (carbsProgress) {
        const carbsPercentage = Math.min(Math.round((carbs / carbsGoal) * 100), 100);
        carbsProgress.style.width = `${carbsPercentage}%`;
    }
    
    // Fat progress
    const fatProgress = document.querySelector('.progress-bar.fat');
    if (fatProgress) {
        const fatPercentage = Math.min(Math.round((fat / fatGoal) * 100), 100);
        fatProgress.style.width = `${fatPercentage}%`;
    }
}

/**
 * Initialize Progress Bars
 */
function initProgressBars() {
    // Set progress bar widths based on data-percent attributes
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const percent = parseFloat(bar.getAttribute('data-percent')) || 0;
        // Cap at 100% for UI
        bar.style.width = Math.min(percent, 100) + '%';
        
        // If percent is over 100%, make the bar red
        if (percent > 100) {
            bar.style.backgroundColor = 'var(--exceeded-color)';
        }
    });
    
    // Set water level height based on data-percent attribute
    const waterLevel = document.querySelector('.water-level');
    if (waterLevel) {
        const percent = parseFloat(waterLevel.getAttribute('data-percent')) || 0;
        // Cap at 100% for UI
        waterLevel.style.height = Math.min(percent, 100) + '%';
    }
    
    // Make macro values red when they exceed goals
    document.querySelectorAll('.macro-value').forEach(macroValue => {
        const isOver = macroValue.getAttribute('data-over') === 'True';
        if (isOver) {
            const actualValue = macroValue.querySelector('.actual-value');
            if (actualValue) {
                actualValue.style.color = 'var(--exceeded-color)';
            }
        }
    });
}

/**
 * Handle AI Image Analysis Response
 */
function handleAIAnalysisResponse(response) {
    const aiResults = document.querySelector('.ai-results');
    if (!aiResults) return;
    
    if (response.error) {
        // Show error state
        aiResults.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-circle"></i>
                <h3>Analysis Failed</h3>
                <p>${response.error}</p>
                <button class="btn btn-outline" onclick="location.reload()">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `;
        return;
    }
    
    // Show results
    aiResults.innerHTML = `
        <div class="result-container">
            <div class="result-image">
                <img src="${response.image_url}" alt="Food Image" class="food-image-preview" data-image="${response.image_url}">
            </div>
            
            <div class="nutritional-estimates">
                <h3><i class="fas fa-utensils"></i> ${response.food_description || response.food_name || 'Food Analysis'}</h3>
                <ul class="nutrition-list">
                    <li>
                        <span>Calories</span>
                        <span>${response.calories} kcal</span>
                    </li>
                    <li>
                        <span>Protein</span>
                        <span>${response.protein}g</span>
                    </li>
                    <li>
                        <span>Carbohydrates</span>
                        <span>${response.carbs}g</span>
                    </li>
                    <li>
                        <span>Fat</span>
                        <span>${response.fat}g</span>
                    </li>
                    <li>
                        <span>Serving Size</span>
                        <span>${response.serving_size || response.quantity + ' ' + response.unit || '1 serving'}</span>
                    </li>
                </ul>
            </div>
            
            <p class="result-disclaimer">This is an AI-generated estimate. Actual nutritional values may vary.</p>
            
            <div class="result-actions">
                <button class="btn btn-primary" onclick="addFoodFromAnalysis('${response.analysis_id}')">
                    <i class="fas fa-plus"></i> Add to Food Log
                </button>
            </div>
        </div>
    `;
    
    // Re-initialize image preview modal
    initImagePreviewModal();
}

/**
 * Fetch AI Nutrition Tip
 */
async function fetchNutritionTip() {
    try {
        const tipContainer = document.querySelector('.tip-content');
        if (!tipContainer) return;
        
        tipContainer.innerHTML = '<div class="spinner"></div><p>Generating personalized tip...</p>';
        
        const response = await fetchData('/api/nutrition-tip');
        
        if (response.tip) {
            tipContainer.innerHTML = `<p>${response.tip}</p>`;
        } else {
            tipContainer.innerHTML = '<p>Unable to generate a tip at this time. Please try again later.</p>';
        }
    } catch (error) {
        console.error('Error fetching nutrition tip:', error);
    }
}
