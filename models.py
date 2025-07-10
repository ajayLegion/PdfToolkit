from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    api_key = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Override get_id to ensure it returns a string"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return True
    
    @property
    def is_anonymous(self):
        """Return True if the user is anonymous"""
        return False

class ProcessingJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    operation = db.Column(db.String(50), nullable=False)
    input_files = db.Column(db.Text)  # JSON array of file paths
    output_files = db.Column(db.Text)  # JSON array of file paths
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('jobs', lazy=True))
