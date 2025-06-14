from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, FoodEntry, WaterIntake, NutritionTip
from utils.nutrition_db import NutritionDatabase
import os
import uuid

nutrition_bp = Blueprint('nutrition', __name__)

# Helper functions to parse nutrition values that might be ranges
def parse_numeric_value(value, is_float=False):
    try:
        # If it's already a number or can be directly converted
        return float(value) if is_float else int(value)
    except (ValueError, TypeError):
        # If it's a string that might contain a range like '15-20'
        if isinstance(value, str):
            # Check if it's a range (contains a hyphen)
            if '-' in value:
                try:
                    # Split the range and get the average
                    parts = value.split('-')
                    if len(parts) == 2:
                        lower = float(parts[0].strip())
                        upper = float(parts[1].strip())
                        # Return the average of the range
                        result = (lower + upper) / 2
                        return result if is_float else int(result)
                except (ValueError, IndexError):
                    pass
        # Default fallback
        return 0.0 if is_float else 0

def parse_calories(calories_value):
    return parse_numeric_value(calories_value, is_float=False)

def parse_macros(macro_value):
    return parse_numeric_value(macro_value, is_float=True)

@nutrition_bp.route('/dashboard')
@login_required
def dashboard():
    # Get today's date
    today = request.args.get('date')
    if today:
        try:
            selected_date = datetime.strptime(today, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.utcnow().date()
    else:
        selected_date = datetime.utcnow().date()
    
    # Get nutrition data for the selected date
    nutrition_data = NutritionDatabase.get_daily_nutrition(current_user.id, selected_date)
    water_intake = NutritionDatabase.get_water_intake(current_user.id, selected_date)
    water_entries = NutritionDatabase.get_water_entries(current_user.id, selected_date)
    weekly_stats = NutritionDatabase.get_weekly_stats(current_user.id)
    
    # Get a nutrition tip
    tip = NutritionDatabase.get_nutrition_tip()
    
    # Calculate progress percentages
    calories_percent = round((nutrition_data['calories'] / current_user.calorie_goal) * 100) if current_user.calorie_goal > 0 else 0
    water_percent = round((water_intake / current_user.water_goal) * 100) if current_user.water_goal > 0 else 0
    
    # Ensure percentages don't exceed 100% for visual purposes
    calories_percent = min(calories_percent, 100)
    water_percent = min(water_percent, 100)
    
    # Format date for display
    formatted_date = selected_date.strftime('%B %d, %Y')
    
    # Get previous and next day for navigation
    prev_day = (selected_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_day = (selected_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template(
        'nutrition/dashboard.html',
        nutrition_data=nutrition_data,
        water_intake=water_intake,
        water_entries=water_entries,
        weekly_stats=weekly_stats,
        tip=tip,
        calories_percent=calories_percent,
        water_percent=water_percent,
        selected_date=selected_date,
        formatted_date=formatted_date,
        prev_day=prev_day,
        next_day=next_day
    )

@nutrition_bp.route('/add_food', methods=['GET', 'POST'])
@login_required
def add_food():
    if request.method == 'POST':
        try:
            # Check if this is from AI analysis with analysis_id
            analysis_id = request.form.get('analysis_id')
            if analysis_id:
                # Get the analysis data from session or database
                # For now, we'll try to extract it from the OpenRouterAI client
                from utils.openrouter_ai import OpenRouterAI
                openrouter_client = OpenRouterAI(current_app.config.get('OPENROUTER_API_KEY'))
                
                # Retrieve the cached analysis result
                analysis_result = openrouter_client.get_cached_analysis(analysis_id)
                
                if not analysis_result:
                    raise ValueError("Analysis result not found or expired")
                
                # Create food data from analysis result
                food_data = {
                    'food_description': analysis_result.get('food_description', 'Unknown Food'),
                    'calories': parse_calories(analysis_result.get('calories', 0)),
                    'protein': parse_macros(analysis_result.get('protein', 0)),
                    'carbs': parse_macros(analysis_result.get('carbs', 0)),
                    'fat': parse_macros(analysis_result.get('fat', 0)),
                    'quantity': 1.0,
                    'unit': 'serving',
                    'meal_type': 'other',
                    'food_category': 'other',
                    'date_logged': datetime.strptime(request.form.get('date_logged', datetime.utcnow().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
                    'image_url': analysis_result.get('image_url')
                }
                
                # Add optional fields if present in analysis result
                if 'fiber' in analysis_result:
                    food_data['fiber'] = float(analysis_result.get('fiber', 0))
                if 'sugar' in analysis_result:
                    food_data['sugar'] = float(analysis_result.get('sugar', 0))
                if 'sodium' in analysis_result:
                    food_data['sodium'] = float(analysis_result.get('sodium', 0))
                
                # Mark as AI analyzed
                food_data['ai_analyzed'] = True
            else:
                # Regular form submission
                food_data = {
                    'food_description': request.form.get('food_description'),
                    'calories': parse_calories(request.form.get('calories', 0)),
                    'protein': parse_macros(request.form.get('protein', 0)),
                    'carbs': parse_macros(request.form.get('carbs', 0)),
                    'fat': parse_macros(request.form.get('fat', 0)),
                    'quantity': float(request.form.get('quantity', 1)),
                    'unit': request.form.get('unit', 'serving'),
                    'meal_type': request.form.get('meal_type', 'other'),
                    'food_category': request.form.get('food_category', 'other'),
                    'date_logged': datetime.strptime(request.form.get('date_logged', datetime.utcnow().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                }
                
                # Add optional fields if present
                if 'fiber' in request.form:
                    food_data['fiber'] = float(request.form.get('fiber', 0))
                if 'sugar' in request.form:
                    food_data['sugar'] = float(request.form.get('sugar', 0))
                if 'sodium' in request.form:
                    food_data['sodium'] = float(request.form.get('sodium', 0))
                
                # Check if this is from AI analysis
                food_data['ai_analyzed'] = request.form.get('ai_analyzed') == 'true'
            
            # Add food entry to database
            entry = NutritionDatabase.add_food_entry(current_user.id, food_data)
            
            flash('Food entry added successfully!', 'success')
            
            # If this is an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'entry_id': entry.id})
            
            # Otherwise redirect to dashboard
            return redirect(url_for('nutrition.dashboard', date=food_data['date_logged'].strftime('%Y-%m-%d')))
            
        except Exception as e:
            current_app.logger.error(f"Error adding food: {str(e)}")
            flash(f'Error adding food entry: {str(e)}', 'danger')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)}), 400
            
            return redirect(url_for('nutrition.dashboard'))
    
    # GET request - show the add food form
    selected_date = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    return render_template('nutrition/add_food.html', selected_date=selected_date)

@nutrition_bp.route('/add_water', methods=['POST'])
@login_required
def add_water():
    try:
        amount_ml = int(request.form.get('amount_ml', 0))
        date_str = request.form.get('date_logged', datetime.utcnow().strftime('%Y-%m-%d'))
        date_logged = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if amount_ml <= 0:
            raise ValueError("Water amount must be positive")
        
        # Add water intake to database
        NutritionDatabase.add_water_intake(current_user.id, amount_ml, date_logged)
        
        # Get updated water intake for the day
        total_water = NutritionDatabase.get_water_intake(current_user.id, date_logged)
        water_percent = round((total_water / current_user.water_goal) * 100) if current_user.water_goal > 0 else 0
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'total_water': total_water,
                'water_percent': min(water_percent, 100)  # Cap at 100% for UI
            })
        
        flash('Water intake added successfully!', 'success')
        return redirect(url_for('nutrition.dashboard', date=date_str))
        
    except Exception as e:
        current_app.logger.error(f"Error adding water: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error adding water intake: {str(e)}', 'danger')
        return redirect(url_for('nutrition.dashboard'))

@nutrition_bp.route('/delete_food/<int:entry_id>', methods=['POST'])
@login_required
def delete_food(entry_id):
    try:
        entry = FoodEntry.query.get_or_404(entry_id)
        
        # Check if the entry belongs to the current user
        if entry.user_id != current_user.id:
            flash('You do not have permission to delete this entry.', 'danger')
            return redirect(url_for('nutrition.dashboard'))
        
        # Save the date before deleting
        date_str = entry.date_logged.strftime('%Y-%m-%d')
        
        # Delete the entry
        db.session.delete(entry)
        db.session.commit()
        
        flash('Food entry deleted successfully!', 'success')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        
        return redirect(url_for('nutrition.dashboard', date=date_str))
        
    except Exception as e:
        current_app.logger.error(f"Error deleting food: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error deleting food entry: {str(e)}', 'danger')
        return redirect(url_for('nutrition.dashboard'))

@nutrition_bp.route('/delete_water/<int:entry_id>', methods=['POST'])
@login_required
def delete_water(entry_id):
    try:
        entry = WaterIntake.query.get_or_404(entry_id)
        
        # Check if the entry belongs to the current user
        if entry.user_id != current_user.id:
            flash('You do not have permission to delete this entry.', 'danger')
            return redirect(url_for('nutrition.dashboard'))
        
        # Save the date before deleting
        date_str = entry.date_logged.strftime('%Y-%m-%d')
        
        # Delete the entry
        db.session.delete(entry)
        db.session.commit()
        
        flash('Water intake entry deleted successfully!', 'success')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get updated water intake for the day
            total_water = NutritionDatabase.get_water_intake(current_user.id, entry.date_logged)
            water_percent = round((total_water / current_user.water_goal) * 100) if current_user.water_goal > 0 else 0
            return jsonify({
                'success': True,
                'total_water': total_water,
                'water_percent': min(water_percent, 100)
            })
        
        return redirect(url_for('nutrition.dashboard', date=date_str))
        
    except Exception as e:
        current_app.logger.error(f"Error deleting water entry: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
        
        flash(f'Error deleting water entry: {str(e)}', 'danger')
        return redirect(url_for('nutrition.dashboard'))
