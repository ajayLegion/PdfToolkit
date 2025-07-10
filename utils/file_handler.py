import os
import time
import logging
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    """Save an uploaded file securely"""
    try:
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = secure_filename(file.filename)
        name, ext = os.path.splitext(original_name)
        filename = f"{name}_{timestamp}{ext}"
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        logger.info(f"File saved successfully: {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise e

def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def cleanup_old_files(directories, hours=24):
    """Remove files older than specified hours"""
    try:
        cutoff_time = time.time() - (hours * 3600)
        cleaned_count = 0
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
            
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                # Skip directories and .gitkeep files
                if os.path.isdir(file_path) or filename == '.gitkeep':
                    continue
                
                # Check file age
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.debug(f"Removed old file: {filename}")
                    except OSError as e:
                        logger.warning(f"Could not remove file {filename}: {str(e)}")
        
        logger.info(f"Cleanup completed: {cleaned_count} files removed")
        return cleaned_count
    
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise e

def validate_file_path(file_path, allowed_directories):
    """Validate that file path is within allowed directories"""
    try:
        abs_file_path = os.path.abspath(file_path)
        
        for allowed_dir in allowed_directories:
            abs_allowed_dir = os.path.abspath(allowed_dir)
            if abs_file_path.startswith(abs_allowed_dir):
                return True
        
        return False
    
    except Exception:
        return False

def get_file_info(file_path):
    """Get comprehensive file information"""
    try:
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': os.path.splitext(file_path)[1].lower(),
            'basename': os.path.basename(file_path)
        }
    
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return None
