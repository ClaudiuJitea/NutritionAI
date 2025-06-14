from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Admin access decorator
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return login_required(decorated_function)

# User creation form for admins
class AdminCreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Admin Privileges')
    is_active = BooleanField('Active Account', default=True)
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

# User edit form for admins
class AdminEditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Admin Privileges')
    is_active = BooleanField('Active Account')
    submit = SubmitField('Update User')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users, title='Admin Dashboard')

@admin_bp.route('/user/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    form = AdminCreateUserForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                is_admin=form.is_admin.data,
                is_active=form.is_active.data,
                # Set default nutrition goals
                calorie_goal=2000,
                protein_goal=150,
                carbs_goal=200,
                fat_goal=65,
                fiber_goal=30,
                water_goal=2500
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {user.username} has been created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')
    
    return render_template('admin/create_user.html', form=form, title='Create User')

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow editing your own account through this interface
    if user.id == current_user.id:
        flash('You cannot edit your own account through this interface. Please use the profile page.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    form = AdminEditUserForm()
    
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin
        form.is_active.data = user.is_active
    
    if form.validate_on_submit():
        try:
            # Check if username or email is being changed and if it's already taken
            if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
                form.username.errors.append('Username already taken. Please choose a different one.')
                return render_template('admin/edit_user.html', form=form, user=user, title='Edit User')
            
            if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
                form.email.errors.append('Email already registered. Please use a different one.')
                return render_template('admin/edit_user.html', form=form, user=user, title='Edit User')
            
            user.username = form.username.data
            user.email = form.email.data
            user.is_admin = form.is_admin.data
            user.is_active = form.is_active.data
            
            db.session.commit()
            flash(f'User {user.username} has been updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', form=form, user=user, title='Edit User')

@admin_bp.route('/user/<int:user_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow suspending your own account
    if user.id == current_user.id:
        flash('You cannot suspend your own account.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status = "activated" if user.is_active else "suspended"
        flash(f'User {user.username} has been {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling user status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting your own account through this interface
    if user.id == current_user.id:
        flash('You cannot delete your own account through this interface. Please use the profile page.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'User {username} has been deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))
