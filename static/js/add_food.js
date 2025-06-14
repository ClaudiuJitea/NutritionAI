/**
 * Add Food Form JavaScript for Diet & Nutrition AI Application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Nutrition Calculator
    initNutritionCalculator();
});

/**
 * Nutrition Calculator
 */
function initNutritionCalculator() {
    const calorieInput = document.getElementById('calories');
    const proteinInput = document.getElementById('protein');
    const carbsInput = document.getElementById('carbs');
    const fatInput = document.getElementById('fat');
    
    const calculatedCalories = document.getElementById('calculated-calories');
    const proteinCalories = document.getElementById('protein-calories');
    const carbsCalories = document.getElementById('carbs-calories');
    const fatCalories = document.getElementById('fat-calories');
    
    const proteinPercentage = document.getElementById('protein-percentage');
    const carbsPercentage = document.getElementById('carbs-percentage');
    const fatPercentage = document.getElementById('fat-percentage');
    
    // Calories per gram
    const PROTEIN_CAL_PER_GRAM = 4;
    const CARBS_CAL_PER_GRAM = 4;
    const FAT_CAL_PER_GRAM = 9;
    
    function updateCalculator() {
        const protein = parseFloat(proteinInput.value) || 0;
        const carbs = parseFloat(carbsInput.value) || 0;
        const fat = parseFloat(fatInput.value) || 0;
        
        const proteinCal = protein * PROTEIN_CAL_PER_GRAM;
        const carbsCal = carbs * CARBS_CAL_PER_GRAM;
        const fatCal = fat * FAT_CAL_PER_GRAM;
        
        const totalCal = proteinCal + carbsCal + fatCal;
        
        // Update calorie breakdown
        if (proteinCalories) proteinCalories.textContent = proteinCal.toFixed(0);
        if (carbsCalories) carbsCalories.textContent = carbsCal.toFixed(0);
        if (fatCalories) fatCalories.textContent = fatCal.toFixed(0);
        if (calculatedCalories) calculatedCalories.textContent = totalCal.toFixed(0);
        
        // Update calorie input if it's empty or if the difference is significant
        if (calorieInput && (calorieInput.value === '' || Math.abs(parseFloat(calorieInput.value) - totalCal) > 10)) {
            calorieInput.value = totalCal.toFixed(0);
        }
        
        // Update macro percentages
        if (totalCal > 0) {
            const proteinPct = (proteinCal / totalCal) * 100;
            const carbsPct = (carbsCal / totalCal) * 100;
            const fatPct = (fatCal / totalCal) * 100;
            
            if (proteinPercentage) proteinPercentage.textContent = proteinPct.toFixed(0) + '%';
            if (carbsPercentage) carbsPercentage.textContent = carbsPct.toFixed(0) + '%';
            if (fatPercentage) fatPercentage.textContent = fatPct.toFixed(0) + '%';
        } else {
            if (proteinPercentage) proteinPercentage.textContent = '0%';
            if (carbsPercentage) carbsPercentage.textContent = '0%';
            if (fatPercentage) fatPercentage.textContent = '0%';
        }
    }
    
    // Add event listeners to update the calculator
    if (proteinInput) proteinInput.addEventListener('input', updateCalculator);
    if (carbsInput) carbsInput.addEventListener('input', updateCalculator);
    if (fatInput) fatInput.addEventListener('input', updateCalculator);
    
    // Also update when calorie input changes significantly
    if (calorieInput) {
        calorieInput.addEventListener('input', function() {
            // If user manually enters calories, don't immediately recalculate
            // This allows them to enter a value without it being overwritten
        });
    }
    
    // Initial calculation
    updateCalculator();
}

/**
 * Food Category Selection
 */
function updateFoodCategoryIcon() {
    const categorySelect = document.getElementById('food_category');
    const categoryIcon = document.getElementById('category-icon');
    
    if (!categorySelect || !categoryIcon) return;
    
    const selectedOption = categorySelect.options[categorySelect.selectedIndex];
    const iconClass = selectedOption.getAttribute('data-icon') || 'fa-utensils';
    
    categoryIcon.className = `fas ${iconClass}`;
}

/**
 * Meal Type Selection
 */
function updateMealTypeIcon() {
    const mealTypeSelect = document.getElementById('meal_type');
    const mealTypeIcon = document.getElementById('meal-type-icon');
    
    if (!mealTypeSelect || !mealTypeIcon) return;
    
    const selectedOption = mealTypeSelect.options[mealTypeSelect.selectedIndex];
    const iconClass = selectedOption.getAttribute('data-icon') || 'fa-utensils';
    
    mealTypeIcon.className = `fas ${iconClass}`;
}
