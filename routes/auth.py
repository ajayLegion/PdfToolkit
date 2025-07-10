from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User, db
from services.auth import generate_api_key
from utils.validators import validate_email, validate_username
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            logger.info(f"User {user.username} logged in successfully")
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('web.dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
            logger.warning(f"Failed login attempt for: {username}")
    
    return render_template('auth/login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required.')
        elif not validate_username(username):
            errors.append('Username must be 3-50 characters and contain only letters, numbers, and underscores.')
        elif User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if not email:
            errors.append('Email is required.')
        elif not validate_email(email):
            errors.append('Please enter a valid email address.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email address already registered.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/signup.html')
        
        try:
            # Create new user
            user = User(
                username=username,
                email=email,
                api_key=generate_api_key(),
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {username} ({email})")
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user account: {str(e)}")
            flash('An error occurred while creating your account. Please try again.', 'error')
    
    return render_template('auth/signup.html')

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logger.info(f"User {username} logged out")
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('web.index'))

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)

@bp.route('/regenerate-api-key', methods=['POST'])
@login_required
def regenerate_api_key():
    """Regenerate user's API key"""
    try:
        current_user.api_key = generate_api_key()
        db.session.commit()
        
        logger.info(f"API key regenerated for user: {current_user.username}")
        flash('API key regenerated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error regenerating API key: {str(e)}")
        flash('Error regenerating API key. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))