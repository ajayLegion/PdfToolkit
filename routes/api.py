import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from services.pdf_processor import PDFProcessor
from services.auth import require_api_key
from utils.file_handler import save_uploaded_file, cleanup_old_files
from utils.validators import validate_pdf_file, validate_operation_params
from models import ProcessingJob, db

bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@bp.route('/status/<int:job_id>', methods=['GET'])
@require_api_key
def get_job_status(job_id):
    """Get the status of a processing job"""
    try:
        job = ProcessingJob.query.get_or_404(job_id)
        
        if job.user_id != request.current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        response = {
            'job_id': job.id,
            'operation': job.operation,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
        }
        
        if job.completed_at:
            response['completed_at'] = job.completed_at.isoformat()
        
        if job.error_message:
            response['error'] = job.error_message
            
        if job.output_files and job.status == 'completed':
            response['output_files'] = json.loads(job.output_files)
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/upload', methods=['POST'])
@require_api_key
def upload_file():
    """Upload a PDF file for processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate PDF file
        validation_result = validate_pdf_file(file)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['error']}), 400
        
        # Save the uploaded file
        filename = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'size': validation_result['size']
        })
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/merge', methods=['POST'])
@require_api_key
def merge_pdfs():
    """Merge multiple PDF files"""
    try:
        data = request.get_json()
        validation = validate_operation_params(data, required=['files'])
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        # Create processing job
        job = ProcessingJob(
            user_id=request.current_user.id,
            operation='merge',
            input_files=json.dumps(data['files']),
            status='processing'
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            # Process the PDFs
            processor = PDFProcessor()
            output_path = processor.merge_pdfs(
                data['files'], 
                current_app.config['UPLOAD_FOLDER'],
                current_app.config['PROCESSED_FOLDER']
            )
            
            # Update job status
            job.status = 'completed'
            job.output_files = json.dumps([output_path])
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'job_id': job.id,
                'message': 'PDFs merged successfully',
                'output_file': output_path
            })
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
            raise e
    
    except Exception as e:
        logger.error(f"Error merging PDFs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/split', methods=['POST'])
@require_api_key
def split_pdf():
    """Split a PDF file into individual pages"""
    try:
        data = request.get_json()
        validation = validate_operation_params(data, required=['file'])
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        # Create processing job
        job = ProcessingJob(
            user_id=request.current_user.id,
            operation='split',
            input_files=json.dumps([data['file']]),
            status='processing'
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            # Process the PDF
            processor = PDFProcessor()
            output_paths = processor.split_pdf(
                data['file'],
                current_app.config['UPLOAD_FOLDER'],
                current_app.config['PROCESSED_FOLDER'],
                data.get('pages')  # Optional page range
            )
            
            # Update job status
            job.status = 'completed'
            job.output_files = json.dumps(output_paths)
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'job_id': job.id,
                'message': 'PDF split successfully',
                'output_files': output_paths
            })
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
            raise e
    
    except Exception as e:
        logger.error(f"Error splitting PDF: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/convert-to-images', methods=['POST'])
@require_api_key
def convert_to_images():
    """Convert PDF pages to images"""
    try:
        data = request.get_json()
        validation = validate_operation_params(data, required=['file'])
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        # Create processing job
        job = ProcessingJob(
            user_id=request.current_user.id,
            operation='convert_to_images',
            input_files=json.dumps([data['file']]),
            status='processing'
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            # Process the PDF
            processor = PDFProcessor()
            output_paths = processor.convert_to_images(
                data['file'],
                current_app.config['UPLOAD_FOLDER'],
                current_app.config['PROCESSED_FOLDER'],
                format=data.get('format', 'PNG'),
                dpi=data.get('dpi', 300)
            )
            
            # Update job status
            job.status = 'completed'
            job.output_files = json.dumps(output_paths)
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'job_id': job.id,
                'message': 'PDF converted to images successfully',
                'output_files': output_paths
            })
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
            raise e
    
    except Exception as e:
        logger.error(f"Error converting PDF to images: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/metadata', methods=['POST'])
@require_api_key
def extract_metadata():
    """Extract metadata from a PDF file"""
    try:
        data = request.get_json()
        validation = validate_operation_params(data, required=['file'])
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        # Process the PDF
        processor = PDFProcessor()
        metadata = processor.extract_metadata(
            data['file'],
            current_app.config['UPLOAD_FOLDER']
        )
        
        return jsonify({
            'message': 'Metadata extracted successfully',
            'metadata': metadata
        })
    
    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/compress', methods=['POST'])
@require_api_key
def compress_pdf():
    """Compress a PDF file"""
    try:
        data = request.get_json()
        validation = validate_operation_params(data, required=['file'])
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        # Create processing job
        job = ProcessingJob(
            user_id=request.current_user.id,
            operation='compress',
            input_files=json.dumps([data['file']]),
            status='processing'
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            # Process the PDF
            processor = PDFProcessor()
            output_path, compression_ratio = processor.compress_pdf(
                data['file'],
                current_app.config['UPLOAD_FOLDER'],
                current_app.config['PROCESSED_FOLDER'],
                quality=data.get('quality', 'medium')
            )
            
            # Update job status
            job.status = 'completed'
            job.output_files = json.dumps([output_path])
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'job_id': job.id,
                'message': 'PDF compressed successfully',
                'output_file': output_path,
                'compression_ratio': compression_ratio
            })
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
            raise e
    
    except Exception as e:
        logger.error(f"Error compressing PDF: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/download/<filename>', methods=['GET'])
@require_api_key
def download_file(filename):
    """Download a processed file"""
    try:
        file_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/cleanup', methods=['POST'])
@require_api_key
def cleanup_files():
    """Clean up old files (admin only)"""
    try:
        if not request.current_user.username == 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        hours = data.get('hours', 24)  # Default to 24 hours
        
        cleaned_count = cleanup_old_files(
            [current_app.config['UPLOAD_FOLDER'], current_app.config['PROCESSED_FOLDER']],
            hours
        )
        
        return jsonify({
            'message': 'Cleanup completed successfully',
            'files_cleaned': cleaned_count
        })
    
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
