/**
 * Main JavaScript for Diet & Nutrition AI Application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Flash Messages
    initFlashMessages();
    
    // Initialize User Dropdown
    initUserDropdown();
    
    // Initialize Date Navigation
    initDateNavigation();
    
    // Initialize Water Intake Form
    initWaterIntakeForm();
    
    // Initialize Delete Confirmations
    initDeleteConfirmations();
});

/**
 * Flash Messages
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash');
    
    flashMessages.forEach(flash => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            flash.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => {
                flash.remove();
            }, 300);
        }, 5000);
        
        // Close button
        const closeBtn = flash.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                flash.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => {
                    flash.remove();
                }, 300);
            });
        }
    });
}

/**
 * User Dropdown
 */
function initUserDropdown() {
    const userMenuToggle = document.querySelector('.user-menu-toggle');
    const userDropdown = document.querySelector('.user-dropdown');
    
    if (userMenuToggle && userDropdown) {
        userMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
        
        // Close when clicking outside
        document.addEventListener('click', function() {
            if (userDropdown.classList.contains('show')) {
                userDropdown.classList.remove('show');
            }
        });
        
        // Prevent closing when clicking inside dropdown
        userDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
}

/**
 * Date Navigation
 */
function initDateNavigation() {
    const prevDateBtn = document.querySelector('.prev-date');
    const nextDateBtn = document.querySelector('.next-date');
    const todayBtn = document.querySelector('.today-btn');
    const dateForm = document.getElementById('date-form');
    
    if (prevDateBtn && nextDateBtn && dateForm) {
        prevDateBtn.addEventListener('click', function() {
            const dateInput = document.getElementById('selected-date');
            if (dateInput) {
                const currentDate = new Date(dateInput.value);
                currentDate.setDate(currentDate.getDate() - 1);
                dateInput.value = formatDate(currentDate);
                dateForm.submit();
            }
        });
        
        nextDateBtn.addEventListener('click', function() {
            const dateInput = document.getElementById('selected-date');
            if (dateInput) {
                const currentDate = new Date(dateInput.value);
                currentDate.setDate(currentDate.getDate() + 1);
                dateInput.value = formatDate(currentDate);
                dateForm.submit();
            }
        });
        
        if (todayBtn) {
            todayBtn.addEventListener('click', function() {
                const dateInput = document.getElementById('selected-date');
                if (dateInput) {
                    dateInput.value = formatDate(new Date());
                    dateForm.submit();
                }
            });
        }
    }
}

/**
 * Format date as YYYY-MM-DD
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * Water Intake Form
 */
function initWaterIntakeForm() {
    const waterButtons = document.querySelectorAll('.btn-water');
    const waterForm = document.getElementById('water-form');
    const waterInput = document.getElementById('water-amount');
    
    if (waterButtons.length && waterForm && waterInput) {
        waterButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const amount = this.getAttribute('data-amount');
                waterInput.value = amount;
                waterForm.submit();
            });
        });
    }
}

/**
 * Delete Confirmations
 */
function initDeleteConfirmations() {
    const deleteForms = document.querySelectorAll('.delete-form');
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const confirmed = confirm('Are you sure you want to delete this item? This action cannot be undone.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Show a flash message programmatically
 */
function showFlashMessage(type, message) {
    const flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) return;
    
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    const flash = document.createElement('div');
    flash.className = `flash flash-${type}`;
    flash.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <span class="flash-close">&times;</span>
    `;
    
    flashContainer.appendChild(flash);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        flash.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => {
            flash.remove();
        }, 300);
    }, 5000);
    
    // Close button
    const closeBtn = flash.querySelector('.flash-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            flash.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => {
                flash.remove();
            }, 300);
        });
    }
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format date for display
 */
function formatDateForDisplay(dateString) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Calculate calories from macros
 */
function calculateCaloriesFromMacros(protein, carbs, fat) {
    const proteinCal = protein * 4;
    const carbsCal = carbs * 4;
    const fatCal = fat * 9;
    return proteinCal + carbsCal + fatCal;
}

/**
 * Calculate macro percentages
 */
function calculateMacroPercentages(protein, carbs, fat) {
    const proteinCal = protein * 4;
    const carbsCal = carbs * 4;
    const fatCal = fat * 9;
    const totalCal = proteinCal + carbsCal + fatCal;
    
    if (totalCal === 0) return { protein: 0, carbs: 0, fat: 0 };
    
    return {
        protein: Math.round((proteinCal / totalCal) * 100),
        carbs: Math.round((carbsCal / totalCal) * 100),
        fat: Math.round((fatCal / totalCal) * 100)
    };
}

/**
 * Debounce function to limit how often a function can be called
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

/**
 * AJAX request helper
 */
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

/**
 * Create a CSRF token header for AJAX requests
 */
function getCSRFHeader() {
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    return {
        'X-CSRFToken': token
    };
}
