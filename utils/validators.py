import os
import logging
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MIN_FILE_SIZE = 1024  # 1KB

def validate_pdf_file(file):
    """Validate uploaded PDF file"""
    try:
        # Check if file is provided
        if not file or not file.filename:
            return {'valid': False, 'error': 'No file provided'}
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return {'valid': False, 'error': 'File must be a PDF'}
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            return {'valid': False, 'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}
        
        if file_size < MIN_FILE_SIZE:
            return {'valid': False, 'error': f'File too small. Minimum size: {MIN_FILE_SIZE}B'}
        
        # Try to read PDF to verify it's valid
        try:
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            
            # Create a BytesIO object to test PDF reading
            import io
            pdf_stream = io.BytesIO(file_content)
            reader = PdfReader(pdf_stream)
            
            # Basic PDF validation
            if len(reader.pages) == 0:
                return {'valid': False, 'error': 'PDF file contains no pages'}
            
            # Check if PDF is encrypted (we'll handle this in processing)
            if reader.is_encrypted:
                logger.warning(f"Uploaded PDF is encrypted: {file.filename}")
        
        except Exception as pdf_error:
            return {'valid': False, 'error': f'Invalid PDF file: {str(pdf_error)}'}
        
        return {
            'valid': True, 
            'size': file_size,
            'pages': len(reader.pages) if 'reader' in locals() else None
        }
    
    except Exception as e:
        logger.error(f"Error validating PDF file: {str(e)}")
        return {'valid': False, 'error': 'File validation failed'}

def validate_operation_params(data, required=None, optional=None):
    """Validate parameters for PDF operations"""
    try:
        if not data:
            return {'valid': False, 'error': 'No data provided'}
        
        # Check required parameters
        if required:
            missing = [param for param in required if param not in data]
            if missing:
                return {'valid': False, 'error': f'Missing required parameters: {", ".join(missing)}'}
        
        # Validate specific parameter types and values
        if 'files' in data:
            if not isinstance(data['files'], list):
                return {'valid': False, 'error': 'Files parameter must be a list'}
            
            if len(data['files']) == 0:
                return {'valid': False, 'error': 'Files list cannot be empty'}
            
            # Validate each filename
            for filename in data['files']:
                if not isinstance(filename, str) or not filename.strip():
                    return {'valid': False, 'error': 'Invalid filename in files list'}
        
        if 'file' in data:
            if not isinstance(data['file'], str) or not data['file'].strip():
                return {'valid': False, 'error': 'File parameter must be a valid filename'}
        
        if 'pages' in data:
            pages = data['pages']
            if not isinstance(pages, dict):
                return {'valid': False, 'error': 'Pages parameter must be an object'}
            
            if 'start' in pages and (not isinstance(pages['start'], int) or pages['start'] < 1):
                return {'valid': False, 'error': 'Start page must be a positive integer'}
            
            if 'end' in pages and (not isinstance(pages['end'], int) or pages['end'] < 1):
                return {'valid': False, 'error': 'End page must be a positive integer'}
            
            if 'start' in pages and 'end' in pages and pages['start'] > pages['end']:
                return {'valid': False, 'error': 'Start page cannot be greater than end page'}
        
        if 'format' in data:
            valid_formats = ['PNG', 'JPEG', 'TIFF']
            if data['format'].upper() not in valid_formats:
                return {'valid': False, 'error': f'Invalid format. Supported: {", ".join(valid_formats)}'}
        
        if 'dpi' in data:
            dpi = data['dpi']
            if not isinstance(dpi, int) or dpi < 72 or dpi > 600:
                return {'valid': False, 'error': 'DPI must be an integer between 72 and 600'}
        
        if 'quality' in data:
            valid_qualities = ['low', 'medium', 'high']
            if data['quality'].lower() not in valid_qualities:
                return {'valid': False, 'error': f'Invalid quality. Supported: {", ".join(valid_qualities)}'}
        
        return {'valid': True, 'data': data}
    
    except Exception as e:
        logger.error(f"Error validating operation parameters: {str(e)}")
        return {'valid': False, 'error': 'Parameter validation failed'}

def validate_api_key_format(api_key):
    """Validate API key format"""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # API key should be alphanumeric and at least 32 characters
    if len(api_key) < 32:
        return False
    
    # Check if it contains only valid characters
    import string
    valid_chars = string.ascii_letters + string.digits + '-_'
    return all(c in valid_chars for c in api_key)

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False
    
    # Username should be 3-50 characters, alphanumeric with underscores
    if len(username) < 3 or len(username) > 50:
        return False
    
    import re
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
