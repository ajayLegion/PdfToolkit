# PDF Processing Engine

## Overview

This is a Flask-based RESTful API service for comprehensive PDF processing operations. The application provides endpoints for merging, splitting, converting, and manipulating PDF documents with enterprise-grade features including user authentication, job tracking, and file management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular Flask architecture with clear separation of concerns:

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite by default, configurable via DATABASE_URL environment variable
- **Authentication**: API key-based authentication system
- **File Processing**: PyPDF2 and PIL for PDF and image operations
- **Job Management**: Asynchronous job tracking with status monitoring

### Frontend Architecture
- **Templates**: Jinja2 templating with Bootstrap 5 dark theme
- **Static Assets**: Custom CSS and JavaScript for enhanced user experience
- **UI Framework**: Bootstrap with Feather icons
- **Client-side API**: JavaScript API client for testing and interaction

## Key Components

### Core Application (`app.py`)
- Flask application factory pattern
- SQLAlchemy database configuration with connection pooling
- Blueprint registration for modular routing
- File upload configuration with size limits (50MB)
- Automatic directory creation for uploads and processed files

### Data Models (`models.py`)
- **User Model**: Authentication with API keys, password hashing
- **ProcessingJob Model**: Job tracking with status, file references, and error handling
- Relationships between users and their processing jobs

### API Routes (`routes/api.py`)
- RESTful endpoints for PDF operations
- Job status tracking and monitoring
- Health check endpoint for service monitoring
- API key authentication enforcement

### Web Routes (`routes/web.py`)
- User dashboard for job management
- API documentation interface
- Testing interface for API operations

### Services Layer
- **PDF Processor** (`services/pdf_processor.py`): Core PDF manipulation logic
- **Authentication** (`services/auth.py`): API key generation and validation
- **File Handler** (`utils/file_handler.py`): Secure file operations and cleanup
- **Validators** (`utils/validators.py`): Input validation and PDF integrity checks

## Data Flow

1. **File Upload**: Users upload PDF files through API endpoints
2. **Validation**: Files are validated for type, size, and PDF integrity
3. **Job Creation**: Processing jobs are created and tracked in the database
4. **Processing**: PDF operations are performed using PyPDF2 and PIL
5. **Output Generation**: Processed files are saved to the output directory
6. **Status Updates**: Job status is updated throughout the process
7. **File Cleanup**: Old files are automatically cleaned up to manage storage

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **PyPDF2**: PDF reading, writing, and manipulation
- **PIL (Pillow)**: Image processing for PDF conversion
- **Werkzeug**: Security utilities and file handling

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Feather Icons**: Icon library for consistent UI
- **Custom CSS/JS**: Enhanced user experience and API testing

### Development Dependencies
- **Flask-Login**: User session management (partially implemented)
- **Werkzeug ProxyFix**: Production deployment support

## Deployment Strategy

### Environment Configuration
- **Database**: Configurable via DATABASE_URL (defaults to SQLite)
- **Session Secret**: Configurable via SESSION_SECRET environment variable
- **File Storage**: Local filesystem with configurable upload/output directories
- **Logging**: Debug level logging enabled for development

### Production Considerations
- ProxyFix middleware for reverse proxy deployment
- Connection pooling with automatic reconnection
- File size limits and security validations
- Automatic old file cleanup to manage storage

### Scalability Features
- Modular blueprint architecture for easy feature addition
- Job-based processing system ready for async/queue integration
- Database schema designed for multiple users and concurrent operations
- Stateless API design suitable for horizontal scaling

The application is designed to be easily deployable on platforms like Replit, with sensible defaults for development and configuration options for production deployment.