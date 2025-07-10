from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import ProcessingJob, User
import json

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@bp.route('/docs')
def documentation():
    """API documentation page"""
    return render_template('documentation.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing recent jobs"""
    recent_jobs = ProcessingJob.query.filter_by(user_id=current_user.id)\
                                   .order_by(ProcessingJob.created_at.desc())\
                                   .limit(10).all()
    
    # Convert jobs to JSON-serializable format
    jobs_data = []
    for job in recent_jobs:
        job_data = {
            'id': job.id,
            'operation': job.operation,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'error_message': job.error_message
        }
        if job.completed_at:
            job_data['completed_at'] = job.completed_at.isoformat()
        if job.output_files:
            job_data['output_files'] = json.loads(job.output_files)
        jobs_data.append(job_data)
    
    return render_template('auth/dashboard.html', jobs=jobs_data)

@bp.route('/tools')
def tools():
    """PDF tools list page"""
    return render_template('tools.html')

@bp.route('/upload')
@login_required
def upload():
    """File upload and processing interface"""
    return render_template('upload.html')

@bp.route('/api-test')
def api_test():
    """API testing interface"""
    return render_template('api_test.html')
