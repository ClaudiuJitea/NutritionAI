/**
 * Authentication JavaScript for Diet & Nutrition AI Application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initFormValidation();
    
    // Initialize terms modal
    initTermsModal();
    
    // Initialize password visibility toggle
    initPasswordToggle();
    
    // Initialize nutrition calculator for registration page
    initNutritionCalculator();
});

/**
 * Form Validation
 */
function initFormValidation() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            
            let isValid = true;
            
            // Clear previous error messages
            clearErrors();
            
            // Validate email
            if (!email.value.trim()) {
                showError(email, 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }
            
            // Validate password
            if (!password.value.trim()) {
                showError(password, 'Password is required');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username');
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            const termsCheckbox = document.getElementById('terms');
            
            let isValid = true;
            
            // Clear previous error messages
            clearErrors();
            
            // Validate username
            if (!username.value.trim()) {
                showError(username, 'Username is required');
                isValid = false;
            } else if (username.value.length < 3) {
                showError(username, 'Username must be at least 3 characters');
                isValid = false;
            }
            
            // Validate email
            if (!email.value.trim()) {
                showError(email, 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }
            
            // Validate password
            if (!password.value.trim()) {
                showError(password, 'Password is required');
                isValid = false;
            } else if (password.value.length < 8) {
                showError(password, 'Password must be at least 8 characters');
                isValid = false;
            }
            
            // Validate confirm password
            if (password.value !== confirmPassword.value) {
                showError(confirmPassword, 'Passwords do not match');
                isValid = false;
            }
            
            // Validate terms
            if (termsCheckbox && !termsCheckbox.checked) {
                showError(termsCheckbox, 'You must agree to the terms and conditions');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
}

/**
 * Show error message
 */
function showError(input, message) {
    const formGroup = input.closest('.form-group');
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    
    formGroup.classList.add('error');
    formGroup.appendChild(errorElement);
}

/**
 * Clear all error messages
 */
function clearErrors() {
    const errorMessages = document.querySelectorAll('.error-message');
    const errorGroups = document.querySelectorAll('.form-group.error');
    
    errorMessages.forEach(error => error.remove());
    errorGroups.forEach(group => group.classList.remove('error'));
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Terms and Privacy Policy Modals
 */
function initTermsModal() {
    // Terms of Service modal
    const termsModal = document.getElementById('terms-modal');
    const termsLink = document.querySelector('.terms-link');
    const termsClose = document.querySelector('.terms-close');
    
    if (termsLink && termsModal) {
        termsLink.addEventListener('click', function(e) {
            e.preventDefault();
            termsModal.style.display = 'block';
        });
        
        if (termsClose) {
            termsClose.addEventListener('click', function() {
                termsModal.style.display = 'none';
            });
        }
    }
    
    // Privacy Policy modal
    const privacyModal = document.getElementById('privacy-modal');
    const privacyLink = document.querySelector('.privacy-link');
    const privacyClose = document.querySelector('.privacy-close');
    
    if (privacyLink && privacyModal) {
        privacyLink.addEventListener('click', function(e) {
            e.preventDefault();
            privacyModal.style.display = 'block';
        });
        
        if (privacyClose) {
            privacyClose.addEventListener('click', function() {
                privacyModal.style.display = 'none';
            });
        }
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target == termsModal) {
            termsModal.style.display = 'none';
        }
        if (event.target == privacyModal) {
            privacyModal.style.display = 'none';
        }
    });
}

/**
 * Nutrition Calculator for Registration
 */
function initNutritionCalculator() {
    const calorieGoal = document.getElementById('calorie_goal');
    const proteinGoal = document.getElementById('protein_goal');
    const carbsGoal = document.getElementById('carbs_goal');
    const fatGoal = document.getElementById('fat_goal');
    
    const calculatedCalories = document.getElementById('calculated-calories');
    const proteinCalories = document.getElementById('protein-calories');
    const carbsCalories = document.getElementById('carbs-calories');
    const fatCalories = document.getElementById('fat-calories');
    
    // Calories per gram
    const PROTEIN_CAL_PER_GRAM = 4;
    const CARBS_CAL_PER_GRAM = 4;
    const FAT_CAL_PER_GRAM = 9;
    
    function updateCalculator() {
        if (!proteinGoal || !carbsGoal || !fatGoal) return;
        
        const protein = parseFloat(proteinGoal.value) || 0;
        const carbs = parseFloat(carbsGoal.value) || 0;
        const fat = parseFloat(fatGoal.value) || 0;
        
        const proteinCal = protein * PROTEIN_CAL_PER_GRAM;
        const carbsCal = carbs * CARBS_CAL_PER_GRAM;
        const fatCal = fat * FAT_CAL_PER_GRAM;
        
        const totalCal = proteinCal + carbsCal + fatCal;
        
        if (proteinCalories) proteinCalories.textContent = proteinCal.toFixed(0);
        if (carbsCalories) carbsCalories.textContent = carbsCal.toFixed(0);
        if (fatCalories) fatCalories.textContent = fatCal.toFixed(0);
        if (calculatedCalories) calculatedCalories.textContent = totalCal.toFixed(0);
        
        // Update calorie goal input if it's empty
        if (calorieGoal && !calorieGoal.value) {
            calorieGoal.value = totalCal.toFixed(0);
        }
    }
    
    // Calculate macros based on calories
    function calculateMacros() {
        if (!calorieGoal) return;
        
        const calories = parseInt(calorieGoal.value) || 2000;
        
        // Default macro distribution (30% protein, 40% carbs, 30% fat)
        const proteinCalories = calories * 0.3;
        const carbsCalories = calories * 0.4;
        const fatCalories = calories * 0.3;
        
        // Convert to grams (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
        const protein = Math.round(proteinCalories / 4);
        const carbs = Math.round(carbsCalories / 4);
        const fat = Math.round(fatCalories / 9);
        
        // Update input values
        if (proteinGoal) proteinGoal.value = protein;
        if (carbsGoal) carbsGoal.value = carbs;
        if (fatGoal) fatGoal.value = fat;
        
        updateCalculator();
    }
    
    // Add event listeners to update the calculator
    if (proteinGoal) proteinGoal.addEventListener('input', updateCalculator);
    if (carbsGoal) carbsGoal.addEventListener('input', updateCalculator);
    if (fatGoal) fatGoal.addEventListener('input', updateCalculator);
    
    // Add event listener to calorie goal input
    if (calorieGoal) {
        calorieGoal.addEventListener('input', calculateMacros);
        
        // Initialize with default values if empty
        if (!calorieGoal.value) {
            calorieGoal.value = '2000';
            calculateMacros();
        }
    }
}

/**
 * Password Visibility Toggle
 */
function initPasswordToggle() {
    const toggleBtns = document.querySelectorAll('.password-toggle');
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const passwordInput = this.previousElementSibling;
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                this.setAttribute('title', 'Hide password');
            } else {
                passwordInput.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
                this.setAttribute('title', 'Show password');
            }
        });
    });
}

/**
 * Forgot Password
 */
function initForgotPassword() {
    const forgotLink = document.getElementById('forgot-password-link');
    const forgotForm = document.getElementById('forgot-password-form');
    const loginForm = document.getElementById('login-form');
    const backToLoginBtn = document.getElementById('back-to-login');
    
    if (forgotLink && forgotForm && loginForm) {
        forgotLink.addEventListener('click', function(e) {
            e.preventDefault();
            loginForm.style.display = 'none';
            forgotForm.style.display = 'block';
        });
        
        if (backToLoginBtn) {
            backToLoginBtn.addEventListener('click', function(e) {
                e.preventDefault();
                forgotForm.style.display = 'none';
                loginForm.style.display = 'block';
            });
        }
    }
}
