# Backend Configuration
# Replace 'localhost' with your actual backend server IP address

# Local development (if backend is on same machine)
BACKEND_URL = "http://localhost:8000"

# Remote backend (replace with your actual IP and port)
# BACKEND_URL = "http://192.168.1.100:8000"
# BACKEND_URL = "http://10.0.0.50:8000"
# BACKEND_URL = "https://your-backend-domain.com"

# Backend API Endpoints (adjust these based on your actual API)
ENDPOINTS = {
    "health": "/api/health",
    "jobs": "/api/jobs",
    "candidates": "/api/candidates",
    "apply": "/api/jobs/{job_id}/apply",
    "analyze": "/api/analyze-resume",
    "auth": "/api/auth",
    "dashboard": "/api/dashboard",
    "reports": "/api/reports"
}

# API Settings
TIMEOUT = 30  # seconds
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB