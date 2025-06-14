from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from utils.openrouter_ai import OpenRouterAI
import os
import uuid
from datetime import datetime

api_bp = Blueprint('api', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@api_bp.route('/analyze_food_image', methods=['POST'])
@login_required
def analyze_food_image():
    # Check if image was uploaded
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Generate a unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file temporarily
            file.save(filepath)
            
            # Initialize OpenRouter AI client
            openrouter_client = OpenRouterAI(current_app.config.get('OPENROUTER_API_KEY'))
            
            # Analyze the image. The OpenRouterAI client is responsible for adding
            # 'image_url' and 'analysis_id' to the result upon success, or an 'error' key on failure.
            result = openrouter_client.analyze_food_image(filepath)
            
            if 'error' in result:
                # If the analysis client returned an error, forward it with a server error status
                current_app.logger.error(f"AI analysis failed: {result['error']}")
                return jsonify(result), 500
            
            # On success, return the analysis data with HTTP 200 OK
            return jsonify(result)
            
        except Exception as e: # Catch-all for unexpected errors (e.g., file operations, client init)
            current_app.logger.error(f"Unhandled error in analyze_food_image endpoint: {str(e)}")
            return jsonify({'error': "An unexpected server error occurred during image analysis."}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@api_bp.route('/nutrition_data/<date>', methods=['GET'])
@login_required
def get_nutrition_data(date):
    try:
        # Parse date string to date object
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Import here to avoid circular imports
        from utils.nutrition_db import NutritionDatabase
        
        # Get nutrition data
        nutrition_data = NutritionDatabase.get_daily_nutrition(current_user.id, date_obj)
        water_intake = NutritionDatabase.get_water_intake(current_user.id, date_obj)
        
        # Calculate percentages
        calories_percent = round((nutrition_data['calories'] / current_user.calorie_goal) * 100) if current_user.calorie_goal > 0 else 0
        protein_percent = round((nutrition_data['protein'] / current_user.protein_goal) * 100) if current_user.protein_goal > 0 else 0
        carbs_percent = round((nutrition_data['carbs'] / current_user.carbs_goal) * 100) if current_user.carbs_goal > 0 else 0
        fat_percent = round((nutrition_data['fat'] / current_user.fat_goal) * 100) if current_user.fat_goal > 0 else 0
        water_percent = round((water_intake / current_user.water_goal) * 100) if current_user.water_goal > 0 else 0
        
        # Format entries for JSON response
        formatted_entries = []
        for entry in nutrition_data['entries']:
            formatted_entries.append({
                'id': entry.id,
                'food_description': entry.food_description,
                'calories': entry.calories,
                'protein': entry.protein,
                'carbs': entry.carbs,
                'fat': entry.fat,
                'quantity': entry.quantity,
                'unit': entry.unit,
                'meal_type': entry.meal_type,
                'food_category': entry.food_category,
                'image_url': entry.image_url
            })
        
        return jsonify({
            'date': date,
            'calories': nutrition_data['calories'],
            'protein': nutrition_data['protein'],
            'carbs': nutrition_data['carbs'],
            'fat': nutrition_data['fat'],
            'water_intake': water_intake,
            'calories_percent': min(calories_percent, 100),  # Cap at 100% for UI
            'protein_percent': min(protein_percent, 100),
            'carbs_percent': min(carbs_percent, 100),
            'fat_percent': min(fat_percent, 100),
            'water_percent': min(water_percent, 100),
            'entries': formatted_entries,
            'goals': {
                'calories': current_user.calorie_goal,
                'protein': current_user.protein_goal,
                'carbs': current_user.carbs_goal,
                'fat': current_user.fat_goal,
                'water': current_user.water_goal
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting nutrition data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/generate_tip', methods=['GET'])
@login_required
def generate_tip():
    try:
        # Import here to avoid circular imports
        from utils.nutrition_db import NutritionDatabase
        
        # Get user's recent entries
        recent_entries = NutritionDatabase.get_recent_entries(current_user.id)
        
        # Format entries for the AI
        formatted_entries = []
        for entry in recent_entries:
            formatted_entries.append({
                'food_description': entry.food_description,
                'calories': entry.calories,
                'date_logged': entry.date_logged.strftime('%Y-%m-%d')
            })
        
        # Prepare user data
        user_data = {
            'recent_entries': formatted_entries
        }
        
        # Prepare goals
        goals = {
            'calories': current_user.calorie_goal,
            'protein': current_user.protein_goal,
            'carbs': current_user.carbs_goal,
            'fat': current_user.fat_goal
        }
        
        # Initialize OpenRouter AI client
        openrouter_client = OpenRouterAI(current_app.config.get('OPENROUTER_API_KEY'))
        
        # Generate personalized tip
        tip_result = openrouter_client.generate_personalized_tip(user_data, goals)
        
        return jsonify(tip_result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating tip: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/weekly_nutrition', methods=['GET'])
@login_required
def get_weekly_nutrition():
    try:
        # Import here to avoid circular imports
        from utils.nutrition_db import NutritionDatabase
        from datetime import datetime, timedelta
        
        # Get the last 7 days data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)  # 7 days including today
        
        # Get nutrition data for each day
        days = []
        calories = []
        protein = []
        carbs = []
        fat = []
        
        # Create day names (Mon, Tue, etc.)
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Fetch nutrition data for each day
        for i in range(7):
            date = start_date + timedelta(days=i)
            day_idx = date.weekday()  # 0 = Monday, 6 = Sunday
            day_name = day_names[day_idx]
            
            daily_nutrition = NutritionDatabase.get_daily_nutrition(current_user.id, date)
            
            days.append(day_name)
            calories.append(daily_nutrition['calories'])
            protein.append(daily_nutrition['protein'])
            carbs.append(daily_nutrition['carbs'])
            fat.append(daily_nutrition['fat'])
        
        return jsonify({
            'days': days,
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fat': fat
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting weekly nutrition data: {str(e)}")
        return jsonify({'error': str(e)}), 500
