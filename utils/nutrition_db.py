from datetime import datetime, timedelta
from sqlalchemy import func, and_, desc
from models import db, FoodEntry, WaterIntake, NutritionTip, User

class NutritionDatabase:
    @staticmethod
    def get_daily_nutrition(user_id, date=None):
        """Get nutrition summary for a specific day"""
        if date is None:
            date = datetime.utcnow().date()
            
        # Get all food entries for the specified day
        entries = FoodEntry.query.filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date_logged == date
        ).all()
        
        # Calculate totals
        totals = {
            'calories': sum(entry.calories for entry in entries),
            'protein': sum(entry.protein for entry in entries),
            'carbs': sum(entry.carbs for entry in entries),
            'fat': sum(entry.fat for entry in entries),
            'fiber': sum(entry.fiber for entry in entries),
            'entries': entries
        }
        
        return totals
    
    @staticmethod
    def get_water_intake(user_id, date=None):
        """Get water intake for a specific day"""
        if date is None:
            date = datetime.utcnow().date()
            
        # Sum all water entries for the day
        result = db.session.query(func.sum(WaterIntake.amount_ml)).filter(
            WaterIntake.user_id == user_id,
            WaterIntake.date_logged == date
        ).scalar()
        
        return result or 0
    
    @staticmethod
    def get_water_entries(user_id, date=None):
        """Get individual water intake entries for a specific day"""
        if date is None:
            date = datetime.utcnow().date()
            
        # Get all water entries for the day, ordered by time
        entries = WaterIntake.query.filter(
            WaterIntake.user_id == user_id,
            WaterIntake.date_logged == date
        ).order_by(desc(WaterIntake.time_logged)).all()
        
        return entries  # Return 0 if no entries found
    
    @staticmethod
    def add_food_entry(user_id, food_data):
        """Add a new food entry to the database"""
        try:
            # Create new food entry
            entry = FoodEntry(
                user_id=user_id,
                food_description=food_data.get('food_description', 'Nutritional food item'),
                calories=food_data.get('calories', 0),
                protein=food_data.get('protein', 0),
                carbs=food_data.get('carbs', 0),
                fat=food_data.get('fat', 0),
                fiber=food_data.get('fiber', 0),
                sugar=food_data.get('sugar', 0),
                sodium=food_data.get('sodium', 0),
                quantity=food_data.get('quantity', 1),
                unit=food_data.get('unit', 'serving'),
                meal_type=food_data.get('meal_type', 'other'),
                food_category=food_data.get('food_category', 'other'),
                image_url=food_data.get('image_url'),
                ai_analyzed=food_data.get('ai_analyzed', False),
                date_logged=food_data.get('date_logged', datetime.utcnow().date())
            )
            
            db.session.add(entry)
            db.session.commit()
            return entry
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def add_water_intake(user_id, amount_ml, date=None):
        """Add a water intake entry"""
        if date is None:
            date = datetime.utcnow().date()
            
        try:
            water_entry = WaterIntake(
                user_id=user_id,
                amount_ml=amount_ml,
                date_logged=date
            )
            
            db.session.add(water_entry)
            db.session.commit()
            return water_entry
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_nutrition_tip(category=None):
        """Get a random nutrition tip, optionally filtered by category"""
        query = NutritionTip.query.filter(NutritionTip.is_active == True)
        
        if category:
            query = query.filter(NutritionTip.category == category)
            
        # Get a random tip
        tip = query.order_by(func.random()).first()
        
        # If no tip found in the specified category, get any tip
        if not tip and category:
            tip = NutritionTip.query.filter(NutritionTip.is_active == True).order_by(func.random()).first()
            
        return tip
    
    @staticmethod
    def get_weekly_stats(user_id, days=7):
        """Get nutrition statistics for the past X days"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)  # -1 because we want to include today
        
        # Get all food entries in the date range
        entries = FoodEntry.query.filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date_logged >= start_date,
            FoodEntry.date_logged <= end_date
        ).all()
        
        # Count days with entries
        days_logged = db.session.query(func.count(func.distinct(FoodEntry.date_logged))).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date_logged >= start_date,
            FoodEntry.date_logged <= end_date
        ).scalar() or 0
        
        # Calculate averages
        if entries:
            avg_calories = sum(entry.calories for entry in entries) / days_logged if days_logged > 0 else 0
            avg_protein = sum(entry.protein for entry in entries) / days_logged if days_logged > 0 else 0
            avg_carbs = sum(entry.carbs for entry in entries) / days_logged if days_logged > 0 else 0
            avg_fat = sum(entry.fat for entry in entries) / days_logged if days_logged > 0 else 0
        else:
            avg_calories = avg_protein = avg_carbs = avg_fat = 0
        
        return {
            'avg_calories': round(avg_calories, 1),
            'avg_protein': round(avg_protein, 1),
            'avg_carbs': round(avg_carbs, 1),
            'avg_fat': round(avg_fat, 1),
            'days_logged': days_logged,
            'total_days': days
        }
    
    @staticmethod
    def get_recent_entries(user_id, limit=5):
        """Get most recent food entries for a user"""
        entries = FoodEntry.query.filter(
            FoodEntry.user_id == user_id
        ).order_by(desc(FoodEntry.created_at)).limit(limit).all()
        
        return entries
