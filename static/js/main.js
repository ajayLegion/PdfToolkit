// PDF Processing Engine - Main JavaScript

class PDFEngineAPI {
    constructor() {
        this.baseURL = window.location.origin;
        this.apiKey = null;
    }

    setApiKey(key) {
        this.apiKey = key;
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}/api${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    async healthCheck() {
        return this.makeRequest('/health');
    }

    async uploadFile(file, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);

        const headers = {};
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        try {
            const response = await fetch(`${this.baseURL}/api/upload`, {
                method: 'POST',
                headers,
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    }

    async mergePDFs(files) {
        return this.makeRequest('/merge', {
            method: 'POST',
            body: JSON.stringify({ files })
        });
    }

    async splitPDF(file, pages = null) {
        const payload = { file };
        if (pages) {
            payload.pages = pages;
        }

        return this.makeRequest('/split', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    async convertToImages(file, format = 'PNG', dpi = 300) {
        return this.makeRequest('/convert-to-images', {
            method: 'POST',
            body: JSON.stringify({ file, format, dpi })
        });
    }

    async extractMetadata(file) {
        return this.makeRequest('/metadata', {
            method: 'POST',
            body: JSON.stringify({ file })
        });
    }

    async compressPDF(file, quality = 'medium') {
        return this.makeRequest('/compress', {
            method: 'POST',
            body: JSON.stringify({ file, quality })
        });
    }

    async getJobStatus(jobId) {
        return this.makeRequest(`/status/${jobId}`);
    }

    downloadFile(filename) {
        const url = `${this.baseURL}/api/download/${filename}`;
        const headers = {};
        
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        
        // Add headers by opening in new window (limitation of browser security)
        if (this.apiKey) {
            window.open(`${url}?api_key=${this.apiKey}`);
        } else {
            window.open(url);
        }
    }
}

// Utility functions
class UIHelpers {
    static showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Find container or create one
        let container = document.querySelector('.alert-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'alert-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        container.appendChild(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.classList.remove('show');
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, 150);
            }
        }, 5000);
    }

    static showLoading(element, text = 'Processing...') {
        const spinner = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                ${text}
            </div>
        `;
        element.innerHTML = spinner;
        element.disabled = true;
    }

    static hideLoading(element, originalText = 'Submit') {
        element.innerHTML = originalText;
        element.disabled = false;
    }

    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    static validatePDFFile(file) {
        if (!file) {
            return { valid: false, error: 'No file selected' };
        }

        if (file.type !== 'application/pdf') {
            return { valid: false, error: 'File must be a PDF' };
        }

        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            return { valid: false, error: 'File size must be less than 50MB' };
        }

        return { valid: true };
    }
}

// File drop zone functionality
class DropZone {
    constructor(element, onFileDrop) {
        this.element = element;
        this.onFileDrop = onFileDrop;
        this.init();
    }

    init() {
        this.element.addEventListener('dragover', this.handleDragOver.bind(this));
        this.element.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.element.addEventListener('drop', this.handleDrop.bind(this));
    }

    handleDragOver(e) {
        e.preventDefault();
        this.element.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.element.classList.remove('drag-over');
    }

    handleDrop(e) {
        e.preventDefault();
        this.element.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        if (this.onFileDrop) {
            this.onFileDrop(files);
        }
    }
}

// Job status monitor
class JobMonitor {
    constructor(api) {
        this.api = api;
        this.activeJobs = new Set();
        this.intervalId = null;
    }

    addJob(jobId) {
        this.activeJobs.add(jobId);
        this.startMonitoring();
    }

    removeJob(jobId) {
        this.activeJobs.delete(jobId);
        if (this.activeJobs.size === 0) {
            this.stopMonitoring();
        }
    }

    startMonitoring() {
        if (!this.intervalId) {
            this.intervalId = setInterval(() => {
                this.checkJobs();
            }, 2000); // Check every 2 seconds
        }
    }

    stopMonitoring() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async checkJobs() {
        for (const jobId of this.activeJobs) {
            try {
                const status = await this.api.getJobStatus(jobId);
                this.updateJobStatus(jobId, status);

                if (status.status === 'completed' || status.status === 'failed') {
                    this.removeJob(jobId);
                }
            } catch (error) {
                console.error(`Error checking job ${jobId}:`, error);
            }
        }
    }

    updateJobStatus(jobId, status) {
        const statusElement = document.querySelector(`[data-job-id="${jobId}"]`);
        if (statusElement) {
            statusElement.textContent = status.status;
            statusElement.className = `badge ${this.getStatusBadgeClass(status.status)}`;
        }

        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('jobStatusUpdate', {
            detail: { jobId, status }
        }));
    }

    getStatusBadgeClass(status) {
        switch (status) {
            case 'pending': return 'bg-warning';
            case 'processing': return 'bg-info';
            case 'completed': return 'bg-success';
            case 'failed': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }
}

// Initialize global instances
window.pdfAPI = new PDFEngineAPI();
window.uiHelpers = UIHelpers;
window.jobMonitor = new JobMonitor(window.pdfAPI);

// Global event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all dropzones
    const dropZones = document.querySelectorAll('.dropzone');
    dropZones.forEach(zone => {
        new DropZone(zone, (files) => {
            const event = new CustomEvent('filesDropped', { detail: files });
            zone.dispatchEvent(event);
        });
    });

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Copy to clipboard functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn')) {
            const textToCopy = e.target.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                UIHelpers.showAlert('Copied to clipboard!', 'success');
            }).catch(() => {
                UIHelpers.showAlert('Failed to copy to clipboard', 'danger');
            });
        }
    });
});

// Export for use in other scripts
window.PDFEngine = {
    API: PDFEngineAPI,
    UIHelpers: UIHelpers,
    DropZone: DropZone,
    JobMonitor: JobMonitor
};
