import os
import secrets
import logging
from functools import wraps
from flask import request, jsonify, current_app
from models import User

logger = logging.getLogger(__name__)

def generate_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = None
        
        # Check for API key in headers
        if 'X-API-Key' in request.headers:
            api_key = request.headers['X-API-Key']
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Check for API key in query parameters (less secure, for testing)
        if not api_key and 'api_key' in request.args:
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key
        user = User.query.filter_by(api_key=api_key).first()
        if not user or not user.is_active:
            return jsonify({'error': 'Invalid or inactive API key'}), 401
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def create_default_user():
    """Create a default admin user if none exists"""
    try:
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                api_key=generate_api_key(),
                is_active=True
            )
            admin_user.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
            
            from app import db
            db.session.add(admin_user)
            db.session.commit()
            
            logger.info(f"Created default admin user with API key: {admin_user.api_key}")
            return admin_user.api_key
    
    except Exception as e:
        logger.error(f"Error creating default user: {str(e)}")
        return None

def validate_api_request(required_fields=None):
    """Validate common API request requirements"""
    if not request.is_json:
        return {'valid': False, 'error': 'Request must be JSON'}
    
    data = request.get_json()
    if not data:
        return {'valid': False, 'error': 'Invalid JSON data'}
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {'valid': False, 'error': f'Missing required fields: {", ".join(missing_fields)}'}
    
    return {'valid': True, 'data': data}
