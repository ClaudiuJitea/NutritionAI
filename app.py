from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User, NutritionTip
import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# Import blueprints
from routes.auth import auth_bp
from routes.nutrition import nutrition_bp
from routes.api import api_bp
from routes.statistics import stats_bp
from routes.admin import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nutrition_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Nutrition App startup')
    
    # Create database tables and handle migrations
    with app.app_context():
        # Check if we need to add new columns to User table
        try:
            # Try to access new columns to see if they exist
            User.query.filter(User.is_admin == True).first()
        except Exception as e:
            if 'no such column' in str(e).lower():
                app.logger.info('Adding new columns to User table...')
                # Add new columns using raw SQL
                with db.engine.connect() as conn:
                    # Check if columns exist before adding them
                    inspector = db.inspect(db.engine)
                    columns = [column['name'] for column in inspector.get_columns('user')]
                    
                    from sqlalchemy import text
                    if 'is_admin' not in columns:
                        conn.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                    if 'is_active' not in columns:
                        conn.execute(text("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                    if 'last_login' not in columns:
                        conn.execute(text("ALTER TABLE user ADD COLUMN last_login DATETIME"))
                    conn.commit()
                    app.logger.info('Database migration completed successfully!')
        
        # Now create any missing tables
        db.create_all()
        seed_initial_data()
    
    # Root route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('nutrition.dashboard'))
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

def seed_initial_data():
    """Seed initial data for the application"""
    # Create admin user if no users exist
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_active=True,
            calorie_goal=2000,
            protein_goal=150,
            carbs_goal=200,
            fat_goal=65,
            fiber_goal=30,
            water_goal=2500
        )
        admin_user.set_password('admin123')  # TODO: Change this default password after first login
        db.session.add(admin_user)
        db.session.commit()
        print('Created initial admin user: admin@example.com / admin123')
    
    # Add some default nutrition tips if none exist
    if NutritionTip.query.count() == 0:
        tips = [
            {
                'tip_text': 'Try to include a variety of colorful fruits and vegetables in your diet. Each color provides different phytonutrients and antioxidants that support your immune system and overall health.',
                'category': 'general'
            },
            {
                'tip_text': 'Stay hydrated! Water helps transport nutrients, regulate body temperature, and remove waste. Aim for at least 8 glasses (2 liters) daily.',
                'category': 'hydration'
            },
            {
                'tip_text': 'Include protein with each meal to help maintain muscle mass and keep you feeling full longer. Good sources include lean meats, fish, eggs, dairy, legumes, and tofu.',
                'category': 'protein'
            },
            {
                'tip_text': 'Choose whole grains over refined grains. Whole grains contain more fiber, vitamins, and minerals that are important for digestive health and sustained energy.',
                'category': 'carbs'
            },
            {
                'tip_text': 'Not all fats are bad! Include healthy fats from sources like avocados, nuts, seeds, and olive oil to support brain health and nutrient absorption.',
                'category': 'fat'
            },
            {
                'tip_text': 'Meal prep can save time and help you make healthier choices throughout the week. Try setting aside a few hours each weekend to prepare meals and snacks.',
                'category': 'planning'
            },
            {
                'tip_text': 'Read nutrition labels to make informed choices. Pay attention to serving sizes, added sugars, sodium, and the ingredients list.',
                'category': 'awareness'
            }
        ]
        
        for tip_data in tips:
            tip = NutritionTip(**tip_data)
            db.session.add(tip)
        
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
