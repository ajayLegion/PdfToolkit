# PDF Processing Engine

A comprehensive RESTful API service for PDF processing operations designed for enterprise BYOC (Bring Your Own Cloud) deployment.

## Features

- **PDF Merging**: Combine multiple PDF files into one
- **PDF Splitting**: Extract individual pages or page ranges
- **Image Conversion**: Convert PDF pages to PNG, JPEG, or TIFF
- **Metadata Extraction**: Retrieve comprehensive document information
- **PDF Compression**: Reduce file sizes with quality controls
- **Secure API**: Enterprise-grade authentication with API keys

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd pdf-processing-engine

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Set environment variables (optional)
export SESSION_SECRET="your-secret-key"
export DATABASE_URL="sqlite:///pdf_engine.db"
export ADMIN_PASSWORD="your-admin-password"
```

### 3. Run the Application

```bash
# Start the server
python main.py

# Or using gunicorn for production
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### 4. Access the Application

- Web Interface: http://localhost:5000
- API Documentation: http://localhost:5000/docs
- Health Check: http://localhost:5000/api/health

## API Usage

### Authentication

All API endpoints require an API key. Include it in your requests:

```bash
# Header method (recommended)
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/health

# Authorization header
curl -H "Authorization: Bearer your-api-key" http://localhost:5000/api/health
```

### Example Operations

#### Upload a PDF
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -F "file=@document.pdf" \
  http://localhost:5000/api/upload
```

#### Merge PDFs
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"files": ["doc1.pdf", "doc2.pdf"]}' \
  http://localhost:5000/api/merge
```

#### Split PDF
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"file": "document.pdf", "pages": {"start": 1, "end": 5}}' \
  http://localhost:5000/api/split
```

## File Limits

- Maximum file size: 50MB
- Supported format: PDF only
- Maximum merge files: 20 files
- Image DPI range: 72-600 DPI

## Enterprise Deployment

This engine is designed for BYOC deployment:

1. **Cloud Deployment**: Deploy on AWS, Azure, Google Cloud, or any cloud provider
2. **Container Support**: Ready for Docker and Kubernetes deployment
3. **Scalability**: Stateless design supports horizontal scaling
4. **Security**: API key authentication with user management
5. **Monitoring**: Health checks and job status tracking

## Project Structure

```
pdf-processing-engine/
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── models.py           # Database models
├── routes/             # API and web routes
│   ├── api.py         # REST API endpoints
│   └── web.py         # Web interface routes
├── services/          # Business logic
│   ├── pdf_processor.py  # Core PDF operations
│   └── auth.py        # Authentication services
├── utils/             # Utility functions
│   ├── file_handler.py   # File operations
│   └── validators.py  # Input validation
├── templates/         # HTML templates
├── static/           # CSS, JS, and assets
├── uploads/          # Temporary upload storage
└── processed/        # Processed file output
```

## API Endpoints

### Core Operations
- `POST /api/upload` - Upload PDF files
- `POST /api/merge` - Merge multiple PDFs
- `POST /api/split` - Split PDF into pages
- `POST /api/convert-to-images` - Convert to images
- `POST /api/metadata` - Extract metadata
- `POST /api/compress` - Compress PDF files

### Status & Management
- `GET /api/health` - Health check
- `GET /api/status/{job_id}` - Job status
- `GET /api/download/{filename}` - Download files
- `POST /api/cleanup` - Clean old files (admin)

## Development

### Local Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in debug mode
export FLASK_ENV=development
python main.py
```

### Testing
The application includes a web-based API testing interface at `/docs`.

## License

[Your License Here]

## Support

For enterprise support and deployment assistance, contact: [your-contact]