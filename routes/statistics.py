from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, FoodEntry
from sqlalchemy import func, and_, desc
import json

stats_bp = Blueprint('statistics', __name__)

@stats_bp.route('/statistics')
@login_required
def statistics():
    return render_template('statistics/dashboard.html')

@stats_bp.route('/api/nutrition-trends')
@login_required
def nutrition_trends():
    # Get time period from request (default to 7 days)
    days = int(request.args.get('days', 7))
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)  # -1 because we want to include today
    
    # Query daily nutrition totals
    daily_totals = db.session.query(
        FoodEntry.date_logged,
        func.sum(FoodEntry.calories).label('calories'),
        func.sum(FoodEntry.protein).label('protein'),
        func.sum(FoodEntry.carbs).label('carbs'),
        func.sum(FoodEntry.fat).label('fat')
    ).filter(
        FoodEntry.user_id == current_user.id,
        FoodEntry.date_logged >= start_date,
        FoodEntry.date_logged <= end_date
    ).group_by(FoodEntry.date_logged).order_by(FoodEntry.date_logged).all()
    
    # Prepare data for chart.js
    dates = []
    calories = []
    protein = []
    carbs = []
    fat = []
    
    # Create a dictionary to store values by date
    data_by_date = {}
    for day in (start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)):
        data_by_date[day] = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    
    # Fill in actual data
    for entry in daily_totals:
        data_by_date[entry.date_logged] = {
            'calories': float(entry.calories),
            'protein': float(entry.protein),
            'carbs': float(entry.carbs),
            'fat': float(entry.fat)
        }
    
    # Convert to lists for chart.js
    for date, values in sorted(data_by_date.items()):
        dates.append(date.strftime('%Y-%m-%d'))
        calories.append(values['calories'])
        protein.append(values['protein'])
        carbs.append(values['carbs'])
        fat.append(values['fat'])
    
    return jsonify({
        'labels': dates,
        'datasets': [
            {
                'label': 'Calories',
                'data': calories,
                'borderColor': '#00d2a3',
                'backgroundColor': 'rgba(0, 210, 163, 0.2)',
                'yAxisID': 'y-calories'
            },
            {
                'label': 'Protein (g)',
                'data': protein,
                'borderColor': '#ff6b6b',
                'backgroundColor': 'rgba(255, 107, 107, 0.2)',
                'yAxisID': 'y-macros'
            },
            {
                'label': 'Carbs (g)',
                'data': carbs,
                'borderColor': '#48dbfb',
                'backgroundColor': 'rgba(72, 219, 251, 0.2)',
                'yAxisID': 'y-macros'
            },
            {
                'label': 'Fat (g)',
                'data': fat,
                'borderColor': '#feca57',
                'backgroundColor': 'rgba(254, 202, 87, 0.2)',
                'yAxisID': 'y-macros'
            }
        ]
    })

@stats_bp.route('/api/macro-distribution')
@login_required
def macro_distribution():
    # Get time period from request (default to 7 days)
    days = int(request.args.get('days', 7))
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Query total macros for the period
    totals = db.session.query(
        func.sum(FoodEntry.protein).label('protein'),
        func.sum(FoodEntry.carbs).label('carbs'),
        func.sum(FoodEntry.fat).label('fat')
    ).filter(
        FoodEntry.user_id == current_user.id,
        FoodEntry.date_logged >= start_date,
        FoodEntry.date_logged <= end_date
    ).first()
    
    # Calculate percentages
    total_macros = float(totals.protein or 0) + float(totals.carbs or 0) + float(totals.fat or 0)
    
    if total_macros > 0:
        protein_pct = round((float(totals.protein or 0) / total_macros) * 100, 1)
        carbs_pct = round((float(totals.carbs or 0) / total_macros) * 100, 1)
        fat_pct = round((float(totals.fat or 0) / total_macros) * 100, 1)
    else:
        protein_pct = carbs_pct = fat_pct = 0
    
    return jsonify({
        'labels': ['Protein', 'Carbs', 'Fat'],
        'datasets': [{
            'data': [protein_pct, carbs_pct, fat_pct],
            'backgroundColor': ['#ff6b6b', '#48dbfb', '#feca57'],
            'borderColor': ['#ff5252', '#0abde3', '#ff9f43'],
            'borderWidth': 1
        }]
    })

@stats_bp.route('/api/food-categories')
@login_required
def food_categories():
    # Get time period from request (default to 7 days)
    days = int(request.args.get('days', 7))
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Query calories by food category
    category_totals = db.session.query(
        FoodEntry.food_category,
        func.sum(FoodEntry.calories).label('calories')
    ).filter(
        FoodEntry.user_id == current_user.id,
        FoodEntry.date_logged >= start_date,
        FoodEntry.date_logged <= end_date
    ).group_by(FoodEntry.food_category).all()
    
    # Prepare data for chart.js
    categories = []
    calories = []
    colors = {
        'fruit': '#ff9ff3',
        'vegetable': '#00d2a3',
        'meat': '#ff6b6b',
        'fish': '#48dbfb',
        'dairy': '#f5f6fa',
        'grain': '#feca57',
        'other': '#a4b0be'
    }
    
    background_colors = []
    
    for entry in category_totals:
        categories.append(entry.food_category.capitalize())
        calories.append(float(entry.calories))
        background_colors.append(colors.get(entry.food_category.lower(), '#a4b0be'))
    
    return jsonify({
        'labels': categories,
        'datasets': [{
            'label': 'Calories by Food Category',
            'data': calories,
            'backgroundColor': background_colors,
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }]
    })

@stats_bp.route('/api/goal-achievement')
@login_required
def goal_achievement():
    # Get time period from request (default to 7 days)
    days = int(request.args.get('days', 7))
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Query daily nutrition totals
    daily_totals = db.session.query(
        FoodEntry.date_logged,
        func.sum(FoodEntry.calories).label('calories')
    ).filter(
        FoodEntry.user_id == current_user.id,
        FoodEntry.date_logged >= start_date,
        FoodEntry.date_logged <= end_date
    ).group_by(FoodEntry.date_logged).all()
    
    # Count days where goals were met
    days_logged = len(daily_totals)
    days_goal_met = sum(1 for entry in daily_totals if entry.calories >= current_user.calorie_goal * 0.9 and entry.calories <= current_user.calorie_goal * 1.1)
    days_under_goal = sum(1 for entry in daily_totals if entry.calories < current_user.calorie_goal * 0.9)
    days_over_goal = sum(1 for entry in daily_totals if entry.calories > current_user.calorie_goal * 1.1)
    
    # Handle case where no data exists
    if days_logged == 0:
        days_no_data = days
        days_logged = days_goal_met = days_under_goal = days_over_goal = 0
    else:
        days_no_data = days - days_logged
    
    return jsonify({
        'labels': ['Within Goal Range', 'Under Goal', 'Over Goal', 'No Data'],
        'datasets': [{
            'data': [days_goal_met, days_under_goal, days_over_goal, days_no_data],
            'backgroundColor': ['#00d2a3', '#48dbfb', '#ff6b6b', '#a4b0be'],
            'borderColor': ['#00b894', '#0abde3', '#ff5252', '#747d8c'],
            'borderWidth': 1
        }]
    })

@stats_bp.route('/api/weekly-summary')
@login_required
def weekly_summary():
    # Get current week and previous week
    today = datetime.utcnow().date()
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    prev_week_start = current_week_start - timedelta(days=7)
    prev_week_end = current_week_start - timedelta(days=1)
    
    # Query current week totals
    current_week = db.session.query(
        func.avg(FoodEntry.calories).label('avg_calories'),
        func.avg(FoodEntry.protein).label('avg_protein'),
        func.avg(FoodEntry.carbs).label('avg_carbs'),
        func.avg(FoodEntry.fat).label('avg_fat')
    ).filter(
        FoodEntry.user_id == current_user.id,
        FoodEntry.date_logged >= current_week_start,
        FoodEntry.date_logged <= current_week_end
    ).first()
    
    # Query previous week totals
    prev_week = db.session.query(
        func.avg(FoodEntry.calories).label('avg_calories'),
        func.avg(FoodEntry.protein).label('avg_protein'),
        func.avg(FoodEntry.carbs).label('avg_carbs'),
        func.avg(FoodEntry.fat).label('avg_fat')
    ).filter(
        FoodEntry.user_id == current_user.id,
        FoodEntry.date_logged >= prev_week_start,
        FoodEntry.date_logged <= prev_week_end
    ).first()
    
    # Calculate percent changes
    def calc_percent_change(current, previous):
        if previous and previous > 0:
            return round(((current - previous) / previous) * 100, 1)
        return 0
    
    current_calories = float(current_week.avg_calories or 0)
    current_protein = float(current_week.avg_protein or 0)
    current_carbs = float(current_week.avg_carbs or 0)
    current_fat = float(current_week.avg_fat or 0)
    
    prev_calories = float(prev_week.avg_calories or 0)
    prev_protein = float(prev_week.avg_protein or 0)
    prev_carbs = float(prev_week.avg_carbs or 0)
    prev_fat = float(prev_week.avg_fat or 0)
    
    return jsonify({
        'current_week': {
            'avg_calories': round(current_calories, 1),
            'avg_protein': round(current_protein, 1),
            'avg_carbs': round(current_carbs, 1),
            'avg_fat': round(current_fat, 1)
        },
        'prev_week': {
            'avg_calories': round(prev_calories, 1),
            'avg_protein': round(prev_protein, 1),
            'avg_carbs': round(prev_carbs, 1),
            'avg_fat': round(prev_fat, 1)
        },
        'percent_change': {
            'calories': calc_percent_change(current_calories, prev_calories),
            'protein': calc_percent_change(current_protein, prev_protein),
            'carbs': calc_percent_change(current_carbs, prev_carbs),
            'fat': calc_percent_change(current_fat, prev_fat)
        }
    })
