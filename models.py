from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # User role and status
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)  # For account suspension
    last_login = db.Column(db.DateTime)
    
    # Daily nutrition goals
    calorie_goal = db.Column(db.Integer, default=2000)
    protein_goal = db.Column(db.Integer, default=150)  # in grams
    carbs_goal = db.Column(db.Integer, default=200)    # in grams
    fat_goal = db.Column(db.Integer, default=65)       # in grams
    fiber_goal = db.Column(db.Integer, default=30)     # in grams
    water_goal = db.Column(db.Integer, default=2500)   # in ml
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    food_entries = db.relationship('FoodEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    water_entries = db.relationship('WaterIntake', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_description = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, default=0.0)  # in grams
    carbs = db.Column(db.Float, default=0.0)    # in grams
    fat = db.Column(db.Float, default=0.0)      # in grams
    fiber = db.Column(db.Float, default=0.0)    # in grams
    sugar = db.Column(db.Float, default=0.0)    # in grams
    sodium = db.Column(db.Float, default=0.0)   # in mg
    
    quantity = db.Column(db.Float, default=1.0)
    unit = db.Column(db.String(50), default='serving')
    
    # Meal type (breakfast, lunch, dinner, snack)
    meal_type = db.Column(db.String(20), nullable=False, default='other')
    
    # Food category (fruit, vegetable, meat, grain, dairy, other)
    food_category = db.Column(db.String(20), nullable=False, default='other')
    
    image_url = db.Column(db.String(255))  # Optional image URL
    ai_analyzed = db.Column(db.Boolean, default=False)  # Whether this entry was analyzed by AI
    
    date_logged = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FoodEntry {self.food_description} - {self.calories} kcal>'

class WaterIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount_ml = db.Column(db.Integer, nullable=False)  # in milliliters
    date_logged = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    time_logged = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WaterIntake {self.amount_ml} ml>'

class NutritionTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tip_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')
    is_ai_generated = db.Column(db.Boolean, default=False)
    date_generated = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<NutritionTip {self.id}: {self.tip_text[:30]}...>'
