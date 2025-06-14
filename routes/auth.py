from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

auth_bp = Blueprint('auth', __name__)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    calorie_goal = IntegerField('Daily Calorie Goal', default=2000)
    protein_goal = IntegerField('Protein Goal (g)', default=150)
    carbs_goal = IntegerField('Carbs Goal (g)', default=200)
    fat_goal = IntegerField('Fat Goal (g)', default=65)
    water_goal = IntegerField('Water Goal (ml)', default=2500)
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('nutrition.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                calorie_goal=form.calorie_goal.data,
                protein_goal=form.protein_goal.data,
                carbs_goal=form.carbs_goal.data,
                fat_goal=form.fat_goal.data,
                water_goal=form.water_goal.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint' in str(e) and 'username' in str(e):
                form.username.errors.append('Username already taken. Please choose a different one.')
            elif 'UNIQUE constraint' in str(e) and 'email' in str(e):
                form.email.errors.append('Email already registered. Please use a different one.')
            else:
                flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form, title='Register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('nutrition.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            # Check if account is active
            if not user.is_active:
                flash('This account has been suspended. Please contact an administrator.', 'danger')
                return render_template('auth/login.html', form=form, title='Login')
                
            # Update last login time
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('nutrition.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    
    # Create a form for updating profile
    class UpdateProfileForm(FlaskForm):
        username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
        email = StringField('Email', validators=[DataRequired(), Email()])
        calorie_goal = IntegerField('Daily Calorie Goal', default=2000)
        protein_goal = IntegerField('Daily Protein Goal (g)', default=150)
        carbs_goal = IntegerField('Daily Carbs Goal (g)', default=200)
        fat_goal = IntegerField('Daily Fat Goal (g)', default=65)
        water_goal = IntegerField('Daily Water Goal (ml)', default=2500)
        submit = SubmitField('Update Profile')
        
        def validate_username(self, username):
            if username.data != current_user.username:
                user = User.query.filter_by(username=username.data).first()
                if user:
                    raise ValidationError('Username already taken. Please choose a different one.')
        
        def validate_email(self, email):
            if email.data != current_user.email:
                user = User.query.filter_by(email=email.data).first()
                if user:
                    raise ValidationError('Email already registered. Please use a different one.')
    
    form = UpdateProfileForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.calorie_goal.data = current_user.calorie_goal
        form.protein_goal.data = current_user.protein_goal
        form.carbs_goal.data = current_user.carbs_goal
        form.fat_goal.data = current_user.fat_goal
        form.water_goal.data = current_user.water_goal
    
    # Handle different form submissions based on update_type
    update_type = request.form.get('update_type', None)
    
    # Handle profile update
    if form.validate_on_submit() and (update_type is None or update_type == 'account'):
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.calorie_goal = form.calorie_goal.data
        current_user.protein_goal = form.protein_goal.data
        current_user.carbs_goal = form.carbs_goal.data
        current_user.fat_goal = form.fat_goal.data
        current_user.water_goal = form.water_goal.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.profile'))
    
    # Handle nutrition goals update
    elif update_type == 'goals':
        try:
            current_user.calorie_goal = int(request.form.get('calorie_goal', current_user.calorie_goal))
            current_user.protein_goal = int(request.form.get('protein_goal', current_user.protein_goal))
            current_user.carbs_goal = int(request.form.get('carbs_goal', current_user.carbs_goal))
            current_user.fat_goal = int(request.form.get('fat_goal', current_user.fat_goal))
            current_user.water_goal = int(request.form.get('water_goal', current_user.water_goal))
            
            db.session.commit()
            flash('Your nutrition goals have been updated!', 'success')
        except Exception as e:
            flash(f'Error updating nutrition goals: {str(e)}', 'danger')
            
        return redirect(url_for('auth.profile'))
    
    # Handle delete account
    elif update_type == 'delete_account':
        password = request.form.get('password')
        if password and current_user.check_password(password):
            user_id = current_user.id
            logout_user()
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('Your account has been permanently deleted.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('Error deleting account.', 'danger')
                return redirect(url_for('auth.profile'))
        else:
            flash('Incorrect password. Account deletion canceled.', 'danger')
            return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form, title='Profile')

@auth_bp.route('/export/csv')
@login_required
def export_csv():
    # Get user's nutrition data from the database
    from models import FoodEntry, WaterIntake
    import csv
    from io import StringIO
    from datetime import datetime
    from flask import Response
    
    # Create a StringIO object to write CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['Date', 'Food', 'Calories', 'Protein', 'Carbs', 'Fat', 'Water (ml)'])
    
    # Get food and water entries
    food_entries = FoodEntry.query.filter_by(user_id=current_user.id).all()
    water_entries = WaterIntake.query.filter_by(user_id=current_user.id).all()
    
    # Create a dictionary to store daily totals
    daily_data = {}
    
    # Process food entries
    for entry in food_entries:
        # Get date string from entry timestamp
        date_str = entry.time_logged.strftime('%Y-%m-%d') if hasattr(entry, 'time_logged') else \
                  entry.date_added.strftime('%Y-%m-%d') if hasattr(entry, 'date_added') else \
                  datetime.utcnow().strftime('%Y-%m-%d')
        
        if date_str not in daily_data:
            daily_data[date_str] = {
                'food': [],
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'water': 0
            }
        
        daily_data[date_str]['food'].append(entry.food_description)
        daily_data[date_str]['calories'] += entry.calories
        daily_data[date_str]['protein'] += entry.protein
        daily_data[date_str]['carbs'] += entry.carbs
        daily_data[date_str]['fat'] += entry.fat
    
    # Process water entries
    for entry in water_entries:
        # Get date string from entry timestamp
        date_str = entry.date_logged.strftime('%Y-%m-%d') if hasattr(entry, 'date_logged') else \
                  entry.time_logged.strftime('%Y-%m-%d') if hasattr(entry, 'time_logged') else \
                  datetime.utcnow().strftime('%Y-%m-%d')
        
        if date_str not in daily_data:
            daily_data[date_str] = {
                'food': [],
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'water': 0
            }
        
        daily_data[date_str]['water'] += entry.amount_ml
    
    # Write data rows
    for date_str, data in sorted(daily_data.items()):
        cw.writerow([
            date_str,
            ', '.join(data['food']) if data['food'] else 'No food entries',
            data['calories'],
            data['protein'],
            data['carbs'],
            data['fat'],
            data['water']
        ])
    
    # Create response
    output = si.getvalue()
    filename = f"nutrition_data_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@auth_bp.route('/export/json')
@login_required
def export_json():
    # Get user's nutrition data from the database
    from models import FoodEntry, WaterIntake
    import json
    from datetime import datetime
    from flask import Response
    
    # Get food and water entries
    food_entries = FoodEntry.query.filter_by(user_id=current_user.id).all()
    water_entries = WaterIntake.query.filter_by(user_id=current_user.id).all()
    
    # Create a dictionary to store daily totals
    daily_data = {}
    
    # Process food entries
    for entry in food_entries:
        # Get date string from entry timestamp
        date_str = entry.time_logged.strftime('%Y-%m-%d') if hasattr(entry, 'time_logged') else \
                  entry.date_added.strftime('%Y-%m-%d') if hasattr(entry, 'date_added') else \
                  datetime.utcnow().strftime('%Y-%m-%d')
        
        if date_str not in daily_data:
            daily_data[date_str] = {
                'food': [],
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'water': 0
            }
        
        daily_data[date_str]['food'].append(entry.food_description)
        daily_data[date_str]['calories'] += entry.calories
        daily_data[date_str]['protein'] += entry.protein
        daily_data[date_str]['carbs'] += entry.carbs
        daily_data[date_str]['fat'] += entry.fat
    
    # Process water entries
    for entry in water_entries:
        # Get date string from entry timestamp
        date_str = entry.date_logged.strftime('%Y-%m-%d') if hasattr(entry, 'date_logged') else \
                  entry.time_logged.strftime('%Y-%m-%d') if hasattr(entry, 'time_logged') else \
                  datetime.utcnow().strftime('%Y-%m-%d')
        
        if date_str not in daily_data:
            daily_data[date_str] = {
                'food': [],
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'water': 0
            }
        
        daily_data[date_str]['water'] += entry.amount_ml
    
    # Convert daily_data to a list for JSON serialization
    export_data = []
    for date_str, data in sorted(daily_data.items()):
        export_data.append({
            'date': date_str,
            'food': data['food'],
            'calories': data['calories'],
            'protein': data['protein'],
            'carbs': data['carbs'],
            'fat': data['fat'],
            'water': data['water']
        })
    
    # Create response
    output = json.dumps({
        'user': current_user.username,
        'export_date': datetime.now().strftime('%Y-%m-%d'),
        'nutrition_data': export_data
    }, indent=4)
    
    filename = f"nutrition_data_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.json"
    
    return Response(
        output,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
