import requests
import streamlit as st
import json
from typing import Dict, List, Optional

class BackendAPIService:
    """Service class to handle all backend API communications"""
    
    def __init__(self, base_url: str):
        """
        Initialize the API service with the backend URL
        
        Args:
            base_url (str): The base URL of your backend API (e.g., "http://192.168.1.100:8000")
        """
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, files: Dict = None) -> Dict:
        """
        Make HTTP request to the backend API
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            data (Dict): JSON data to send
            files (Dict): Files to upload
            
        Returns:
            Dict: API response or error message
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method.upper() == 'POST':
                if files:
                    # For file uploads, don't set Content-Type header (let requests handle it)
                    headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
                    response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=self.headers, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=self.headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=10)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
            
            # Check if request was successful
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"data": response.text, "status_code": response.status_code}
                
        except requests.exceptions.ConnectionError:
            return {"error": f"Could not connect to backend at {url}. Please check if the backend is running."}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Please try again."}
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
    
    # === JOB MANAGEMENT ENDPOINTS ===
    
    def get_jobs(self, skip: int = 0, limit: int = 100) -> Dict:
        """Get all job postings from backend with pagination"""
        params = f"?skip={skip}&limit={limit}"
        return self._make_request('GET', f'/jobs/{params}')
    
    def create_job(self, job_data: Dict) -> Dict:
        """Create a new job posting"""
        # Format data according to backend API specification
        formatted_data = {
            "job_title": job_data.get("title", ""),
            "department": job_data.get("department", ""),
            "description": job_data.get("description", ""),
            "requirements": "\n".join(job_data.get("requirements", [])) if isinstance(job_data.get("requirements"), list) else job_data.get("requirements", "")
        }
        
        return self._make_request('POST', '/jobs/', data=formatted_data)
    
    def get_job_details(self, job_id: str) -> Dict:
        """Get details for a specific job"""
        return self._make_request('GET', f'/api/jobs/{job_id}')
    
    def update_job(self, job_id: str, job_data: Dict) -> Dict:
        """Update a job posting"""
        return self._make_request('PUT', f'/api/jobs/{job_id}', data=job_data)
    
    def delete_job(self, job_id: str) -> Dict:
        """Delete a job posting"""
        return self._make_request('DELETE', f'/api/jobs/{job_id}')
    
    def parse_job_document(self, job_doc_file) -> Dict:
        """Parse job description document to extract job details"""
        try:
            # Validate file type
            allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']
            allowed_extensions = ['.pdf', '.docx', '.doc']
            
            file_extension = job_doc_file.name.lower().split('.')[-1] if '.' in job_doc_file.name else ''
            
            if not any(job_doc_file.name.lower().endswith(ext) for ext in allowed_extensions):
                return {"error": f"Unsupported file type. Please upload PDF, DOC, or DOCX files only. Current file: {job_doc_file.name}"}
            
            # Reset file pointer to beginning
            job_doc_file.seek(0)
            
            files = {'job_doc': (job_doc_file.name, job_doc_file, job_doc_file.type)}
            
            # Debug info
            print(f"Uploading file: {job_doc_file.name}, size: {job_doc_file.size}, type: {job_doc_file.type}")
            
            # Only try the correct endpoint since we know what's available
            result = self._make_request('POST', '/jobs/parse-document', files=files)
            
            # Additional debug
            print(f"Parse document result: {result}")
            
            return result
            
        except Exception as e:
            print(f"Error in parse_job_document: {str(e)}")
            return {"error": f"File processing error: {str(e)}"}
    
    # === CANDIDATE MANAGEMENT ENDPOINTS ===
    
    def get_candidates(self, skip: int = 0, limit: int = 100) -> Dict:
        """Get all candidate applications with their scores and job details"""
        try:
            url = f"{self.base_url}/applications/"
            params = {
                'skip': skip,
                'limit': limit
            }
            print(f"Getting applications from: {url} with params: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                applications = response.json()
                print(f"Retrieved {len(applications)} applications")
                
                # Transform the data to match frontend expectations if needed
                candidates = []
                for app in applications:
                    candidate = {
                        'id': app.get('id'),
                        'name': f"Candidate {app.get('id', 'Unknown')}",  # Backend doesn't have candidate names yet
                        'job_role': app.get('job', {}).get('job_title', 'Unknown Position'),
                        'job_id': app.get('job_id'),
                        'score': app.get('relevance_score', 0),
                        'verdict': app.get('verdict', 'Medium'),
                        'missing_skills': app.get('missing_skills', []),
                        'feedback': app.get('feedback', ''),
                        'resume_file': app.get('resume_filename', 'resume.pdf'),
                        'application_date': app.get('application_date'),
                        'application_id': app.get('id')
                    }
                    candidates.append(candidate)
                
                return {"candidates": candidates, "total": len(candidates)}
            else:
                error_msg = f"Failed to get applications with status {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                print(error_msg)
                return {"error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting applications: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error getting applications: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
    
    def get_job_applicants(self, job_id: str) -> Dict:
        """Get applicants for a specific job - NOT AVAILABLE in current backend"""
        return {"error": "Job applicants endpoint not available in current backend"}
    
    def apply_to_job(self, job_id: str, resume_file, candidate_data: Dict = None) -> Dict:
        """Submit job application with resume"""
        try:
            # Prepare multipart form data
            files = {
                'resume_file': (resume_file.name if hasattr(resume_file, 'name') else 'resume.pdf', 
                               resume_file, 
                               'application/pdf')
            }
            
            url = f"{self.base_url}/jobs/{job_id}/apply"
            print(f"Applying to job {job_id} at: {url}")
            
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Application successful! Relevance score: {result.get('relevance_score', 'N/A')}")
                return result
            else:
                error_msg = f"Application failed with status {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                print(error_msg)
                return {"error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during job application: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error applying to job: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
    
    # === RESUME ANALYSIS ENDPOINTS ===
    
    def analyze_resume(self, resume_file, job_description: str = None) -> Dict:
        """Analyze resume against job requirements - NOT AVAILABLE in current backend"""
        return {"error": "Resume analysis endpoint not available in current backend"}
    
    def get_analysis_results(self, analysis_id: str) -> Dict:
        """Get resume analysis results - NOT AVAILABLE in current backend"""
        return {"error": "Analysis results endpoint not available in current backend"}
    
    # === USER MANAGEMENT ENDPOINTS ===
    
    def login(self, username: str, password: str, role: str) -> Dict:
        """Authenticate user - NOT AVAILABLE in current backend"""
        return {"error": "Authentication endpoints not available in current backend"}
    
    def register(self, user_data: Dict) -> Dict:
        """Register new user - NOT AVAILABLE in current backend"""
        return {"error": "User registration endpoint not available in current backend"}
    
 
    # === DASHBOARD & REPORTS ENDPOINTS ===
    
    def get_dashboard_metrics(self, role: str = "recruiter") -> Dict:
        """Get dashboard metrics from /metrics/ endpoint"""
        try:
            return self._make_request('GET', '/metrics/')
        except Exception as e:
            return {"error": f"Failed to get metrics: {str(e)}"}
    
    def get_metrics(self) -> Dict:
        """Get dashboard metrics - alias for get_dashboard_metrics"""
        return self.get_dashboard_metrics()
    
    def get_reports_data(self) -> Dict:
        """Get reports and analytics data - NOT AVAILABLE in current backend"""
        return {"error": "Reports endpoint not available in current backend"}
    
    # === HEALTH CHECK ===
    
    def get_available_endpoints(self) -> Dict:
        """Get available API endpoints - returning known endpoints since no OpenAPI docs"""
        # Backend now has these 6 endpoints
        known_endpoints = [
            "/jobs/parse-document",
            "/jobs/", 
            "/jobs/{job_id}/apply",
            "/applications/",
            "/metrics/",
            "/"
        ]
        return {"endpoints": known_endpoints}

    def health_check(self) -> Dict:
        """Check if backend API is healthy"""
        # Only try GET-compatible endpoints
        endpoints_to_try = ['/jobs/', '/']
        
        last_error = None
        for endpoint in endpoints_to_try:
            try:
                result = self._make_request('GET', endpoint)
                if "error" not in result:
                    return {"status": "healthy", "endpoint": endpoint}
                else:
                    last_error = result["error"]
            except Exception as e:
                last_error = str(e)
                continue
        
        # If none work, return connection error with details
        return {"error": f"Backend connection failed. Last error: {last_error}"}


# === STREAMLIT INTEGRATION HELPERS ===

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_api_service() -> BackendAPIService:
    """
    Get cached API service instance
    Uses session state backend URL instead of secrets
    """
    # Use session state backend URL (set in app.py initialization)
    backend_url = st.session_state.get("backend_url", "https://innomaticshackathonbackend-production.up.railway.app")
    
    return BackendAPIService(backend_url)


def test_backend_connection(api_service: BackendAPIService) -> bool:
    """Test if backend is reachable"""
    try:
        result = api_service.health_check()
        return "error" not in result
    except:
        return False


def handle_api_error(result: Dict, default_message: str = "An error occurred", show_error: bool = True) -> bool:
    """
    Handle API errors and show appropriate messages
    
    Args:
        result: API response dictionary
        default_message: Default error message
        show_error: Whether to display error messages in UI
    
    Returns:
        bool: True if there was an error, False if successful
    """
    if "error" in result:
        if show_error:
            st.error(f"❌ {result['error']}")
        return True
    return False


def show_backend_config():
    """Show backend configuration UI"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔗 Backend Configuration")
    
    # Input for backend URL
    new_url = st.sidebar.text_input(
        "Backend API URL:", 
        value=st.session_state.get("backend_url", "http://localhost:8000"),
        help="Enter the URL where your backend API is running"
    )
    
    if st.sidebar.button("Update Backend URL"):
        st.session_state.backend_url = new_url
        st.sidebar.success("✅ Backend URL updated!")
        st.rerun()
    
    # Test connection
    if st.sidebar.button("🔍 Test Connection"):
        api_service = get_api_service()
        if test_backend_connection(api_service):
            st.sidebar.success("✅ Backend connection successful!")
        else:
            st.sidebar.error("❌ Could not connect to backend")