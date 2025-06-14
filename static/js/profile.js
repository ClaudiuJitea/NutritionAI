/**
 * Profile Page JavaScript for Diet & Nutrition AI Application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form toggles
    initFormToggles();
    
    // Initialize delete account confirmation
    initDeleteAccountConfirmation();
    
    // Initialize nutrition goals form
    initNutritionGoalsForm();
});

/**
 * Form Toggles
 */
function initFormToggles() {
    // Password change form toggle
    const passwordChangeBtn = document.getElementById('toggle-password-form');
    const passwordForm = document.getElementById('password-change-form');
    
    if (passwordChangeBtn && passwordForm) {
        passwordChangeBtn.addEventListener('click', function() {
            const isVisible = passwordForm.style.display !== 'none';
            
            if (isVisible) {
                passwordForm.style.display = 'none';
                this.innerHTML = '<i class="fas fa-key"></i> Change Password';
            } else {
                passwordForm.style.display = 'block';
                this.innerHTML = '<i class="fas fa-times"></i> Cancel';
                
                // Reset form
                passwordForm.reset();
            }
        });
    }
    
    // Nutrition goals form toggle
    const goalsEditBtn = document.querySelector('.edit-goals-btn');
    const goalsDisplay = document.getElementById('goals-info-display');
    const goalsForm = document.getElementById('goals-form');
    
    if (goalsEditBtn && goalsDisplay && goalsForm) {
        goalsEditBtn.addEventListener('click', function() {
            const isEditing = goalsForm.style.display !== 'none';
            
            if (isEditing) {
                goalsForm.style.display = 'none';
                goalsDisplay.style.display = 'block';
                this.innerHTML = '<i class="fas fa-edit"></i> Edit Goals';
            } else {
                goalsForm.style.display = 'block';
                goalsDisplay.style.display = 'none';
                this.innerHTML = '<i class="fas fa-times"></i> Cancel';
            }
        });
    }
}

/**
 * Delete Account Confirmation
 */
function initDeleteAccountConfirmation() {
    const deleteAccountBtn = document.getElementById('delete-account-btn');
    const deleteModal = document.getElementById('delete-account-modal');
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    const confirmDeleteBtn = document.getElementById('confirm-delete');
    const deleteForm = document.getElementById('delete-account-form');
    
    if (deleteAccountBtn && deleteModal) {
        // Open modal
        deleteAccountBtn.addEventListener('click', function() {
            deleteModal.style.display = 'block';
        });
        
        // Close modal
        if (cancelDeleteBtn) {
            cancelDeleteBtn.addEventListener('click', function() {
                deleteModal.style.display = 'none';
            });
        }
        
        // Confirm delete
        if (confirmDeleteBtn && deleteForm) {
            confirmDeleteBtn.addEventListener('click', function() {
                deleteForm.submit();
            });
        }
        
        // Close when clicking outside the modal content
        window.addEventListener('click', function(e) {
            if (e.target === deleteModal) {
                deleteModal.style.display = 'none';
            }
        });
    }
}

/**
 * Nutrition Goals Form
 */
function initNutritionGoalsForm() {
    const calorieInput = document.getElementById('calorie_goal');
    const proteinInput = document.getElementById('protein_goal');
    const carbsInput = document.getElementById('carbs_goal');
    const fatInput = document.getElementById('fat_goal');
    const waterInput = document.getElementById('water_goal');
    
    const proteinPercentInput = document.getElementById('protein_percent');
    const carbsPercentInput = document.getElementById('carbs_percent');
    const fatPercentInput = document.getElementById('fat_percent');
    
    // Add cancel button handler
    const cancelBtn = document.querySelector('.cancel-goals-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            // Hide form and show display
            document.getElementById('goals-form').style.display = 'none';
            document.getElementById('goals-info-display').style.display = 'block';
            
            // Update button text
            const editBtn = document.querySelector('.edit-goals-btn');
            if (editBtn) {
                editBtn.innerHTML = '<i class="fas fa-edit"></i> Edit';
            }
        });
    }
    
    // Calories per gram
    const PROTEIN_CAL_PER_GRAM = 4;
    const CARBS_CAL_PER_GRAM = 4;
    const FAT_CAL_PER_GRAM = 9;
    
    function updateMacroGrams() {
        const calories = parseFloat(calorieInput.value) || 0;
        const proteinPercent = parseFloat(proteinPercentInput.value) || 0;
        const carbsPercent = parseFloat(carbsPercentInput.value) || 0;
        const fatPercent = parseFloat(fatPercentInput.value) || 0;
        
        // Calculate grams based on percentages
        const proteinGrams = Math.round((calories * (proteinPercent / 100)) / PROTEIN_CAL_PER_GRAM);
        const carbsGrams = Math.round((calories * (carbsPercent / 100)) / CARBS_CAL_PER_GRAM);
        const fatGrams = Math.round((calories * (fatPercent / 100)) / FAT_CAL_PER_GRAM);
        
        // Update gram inputs
        if (proteinInput) proteinInput.value = proteinGrams;
        if (carbsInput) carbsInput.value = carbsGrams;
        if (fatInput) fatInput.value = fatGrams;
    }
    
    function updateMacroPercentages() {
        const calories = parseFloat(calorieInput.value) || 0;
        const proteinGrams = parseFloat(proteinInput.value) || 0;
        const carbsGrams = parseFloat(carbsInput.value) || 0;
        const fatGrams = parseFloat(fatInput.value) || 0;
        
        // Calculate calories from macros
        const proteinCal = proteinGrams * PROTEIN_CAL_PER_GRAM;
        const carbsCal = carbsGrams * CARBS_CAL_PER_GRAM;
        const fatCal = fatGrams * FAT_CAL_PER_GRAM;
        
        // Calculate percentages
        const proteinPercent = Math.round((proteinCal / calories) * 100);
        const carbsPercent = Math.round((carbsCal / calories) * 100);
        const fatPercent = Math.round((fatCal / calories) * 100);
        
        // Update percentage inputs
        if (proteinPercentInput) proteinPercentInput.value = proteinPercent;
        if (carbsPercentInput) carbsPercentInput.value = carbsPercent;
        if (fatPercentInput) fatPercentInput.value = fatPercent;
    }
    
    // Add event listeners
    if (proteinPercentInput) {
        proteinPercentInput.addEventListener('input', function() {
            // Ensure percentages don't exceed 100%
            const carbsPercent = parseFloat(carbsPercentInput.value) || 0;
            const fatPercent = parseFloat(fatPercentInput.value) || 0;
            const total = parseFloat(this.value) + carbsPercent + fatPercent;
            
            if (total > 100) {
                // Adjust other percentages proportionally
                const excess = total - 100;
                const otherTotal = carbsPercent + fatPercent;
                
                if (otherTotal > 0) {
                    const carbsNew = Math.max(0, Math.round(carbsPercent - (excess * (carbsPercent / otherTotal))));
                    const fatNew = Math.max(0, Math.round(fatPercent - (excess * (fatPercent / otherTotal))));
                    
                    carbsPercentInput.value = carbsNew;
                    fatPercentInput.value = fatNew;
                }
            }
            
            updateMacroGrams();
        });
    }
    
    if (carbsPercentInput) {
        carbsPercentInput.addEventListener('input', function() {
            // Ensure percentages don't exceed 100%
            const proteinPercent = parseFloat(proteinPercentInput.value) || 0;
            const fatPercent = parseFloat(fatPercentInput.value) || 0;
            const total = proteinPercent + parseFloat(this.value) + fatPercent;
            
            if (total > 100) {
                // Adjust other percentages proportionally
                const excess = total - 100;
                const otherTotal = proteinPercent + fatPercent;
                
                if (otherTotal > 0) {
                    const proteinNew = Math.max(0, Math.round(proteinPercent - (excess * (proteinPercent / otherTotal))));
                    const fatNew = Math.max(0, Math.round(fatPercent - (excess * (fatPercent / otherTotal))));
                    
                    proteinPercentInput.value = proteinNew;
                    fatPercentInput.value = fatNew;
                }
            }
            
            updateMacroGrams();
        });
    }
    
    if (fatPercentInput) {
        fatPercentInput.addEventListener('input', function() {
            // Ensure percentages don't exceed 100%
            const proteinPercent = parseFloat(proteinPercentInput.value) || 0;
            const carbsPercent = parseFloat(carbsPercentInput.value) || 0;
            const total = proteinPercent + carbsPercent + parseFloat(this.value);
            
            if (total > 100) {
                // Adjust other percentages proportionally
                const excess = total - 100;
                const otherTotal = proteinPercent + carbsPercent;
                
                if (otherTotal > 0) {
                    const proteinNew = Math.max(0, Math.round(proteinPercent - (excess * (proteinPercent / otherTotal))));
                    const carbsNew = Math.max(0, Math.round(carbsPercent - (excess * (carbsPercent / otherTotal))));
                    
                    proteinPercentInput.value = proteinNew;
                    carbsPercentInput.value = carbsNew;
                }
            }
            
            updateMacroGrams();
        });
    }
    
    // Update percentages when gram values change
    if (proteinInput) proteinInput.addEventListener('input', updateMacroPercentages);
    if (carbsInput) carbsInput.addEventListener('input', updateMacroPercentages);
    if (fatInput) fatInput.addEventListener('input', updateMacroPercentages);
    
    // Update both when calorie goal changes
    if (calorieInput) {
        calorieInput.addEventListener('input', function() {
            // Update grams based on current percentages
            updateMacroGrams();
        });
    }
}

/**
 * Export Data
 */
function exportUserData(format) {
    window.location.href = `/api/export-user-data?format=${format}`;
}
