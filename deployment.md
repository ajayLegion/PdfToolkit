# PDF Processing Engine - Deployment Guide

## Quick Download Methods

### Option 1: Download as ZIP from Replit
1. In the file explorer, click the three dots menu (⋯)
2. Select "Download as ZIP"
3. Extract the ZIP file on your local machine

### Option 2: Git Clone
```bash
# If you've connected this to a Git repository
git clone <your-repository-url>
cd pdf-processing-engine
```

## Local Development Setup

After downloading the project:

```bash
# 1. Install Python dependencies
pip install uv
uv sync

# 2. Set up environment variables (optional)
export SESSION_SECRET="your-secret-key"
export DATABASE_URL="sqlite:///pdf_engine.db"

# 3. Run the application
python main.py
```

## Enterprise Deployment Options

### 1. Docker Deployment

```bash
# Build and run with Docker
docker build -t pdf-engine .
docker run -p 5000:5000 pdf-engine

# Or use Docker Compose
docker-compose up
```

### 2. Cloud Deployment (AWS/Azure/GCP)

#### AWS EC2/ECS
```bash
# Upload your files to EC2 instance
scp -r pdf-processing-engine/ user@your-ec2-instance:/app/

# SSH into instance and run
ssh user@your-ec2-instance
cd /app/pdf-processing-engine
docker-compose up -d
```

#### Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image pdf-engine .
az container create --resource-group mygroup --name pdf-engine --image myregistry.azurecr.io/pdf-engine:latest
```

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy pdf-engine --source .
```

### 3. Kubernetes Deployment

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pdf-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pdf-engine
  template:
    metadata:
      labels:
        app: pdf-engine
    spec:
      containers:
      - name: pdf-engine
        image: your-registry/pdf-engine:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          value: "postgresql://user:pass@postgres:5432/pdf_engine"
---
apiVersion: v1
kind: Service
metadata:
  name: pdf-engine-service
spec:
  selector:
    app: pdf-engine
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## Environment Configuration

### Required Files
- All Python files (.py)
- Templates folder (HTML files)
- Static folder (CSS, JS)
- pyproject.toml and uv.lock (dependencies)

### Environment Variables
```bash
# Production settings
SESSION_SECRET=your-secure-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/pdf_engine
ADMIN_PASSWORD=secure-admin-password

# Optional settings
MAX_CONTENT_LENGTH=52428800  # 50MB in bytes
UPLOAD_FOLDER=uploads
PROCESSED_FOLDER=processed
```

## Security Considerations

1. **Change default admin password**
2. **Use strong SESSION_SECRET**
3. **Configure proper database credentials**
4. **Set up HTTPS/TLS in production**
5. **Implement rate limiting if needed**
6. **Regular security updates**

## Monitoring & Maintenance

### Health Checks
- GET `/api/health` - Application status
- Monitor file storage usage
- Database connection health

### File Cleanup
- Files auto-cleanup after 24 hours
- Manual cleanup via `/api/cleanup` endpoint
- Monitor disk space usage

## Integration Examples

### cURL Examples
```bash
# Health check
curl https://your-domain.com/api/health

# Upload and process
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -F "file=@document.pdf" \
  https://your-domain.com/api/upload

# Merge PDFs
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"files": ["doc1.pdf", "doc2.pdf"]}' \
  https://your-domain.com/api/merge
```

### Python Client Example
```python
import requests

class PDFEngineClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}
    
    def upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/api/upload",
                files={'file': f},
                headers=self.headers
            )
        return response.json()
    
    def merge_pdfs(self, filenames):
        response = requests.post(
            f"{self.base_url}/api/merge",
            json={'files': filenames},
            headers=self.headers
        )
        return response.json()

# Usage
client = PDFEngineClient('https://your-domain.com', 'your-api-key')
result = client.upload_file('document.pdf')
```

## Support

For deployment assistance or enterprise features:
- Review the web interface at `/docs`
- Check application logs for troubleshooting
- Monitor the `/api/health` endpoint
- Use the admin cleanup endpoint for maintenance