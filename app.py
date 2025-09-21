import streamlit as st
from streamlit.components.v1 import html
from services.api_service import get_api_service, handle_api_error, show_backend_config, test_backend_connection

# --- Global Configuration and Session State Management ---
st.set_page_config(layout="wide", page_title="AI Resume Analyzer")

if "role" not in st.session_state:
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "show_analyze_modal" not in st.session_state:
    st.session_state.show_analyze_modal = False
if "show_create_job_modal" not in st.session_state:
    st.session_state.show_create_job_modal = False
if "show_details_modal" not in st.session_state:
    st.session_state.show_details_modal = False
if "show_feedback_modal" not in st.session_state:
    st.session_state.show_feedback_modal = False
if "show_application_feedback" not in st.session_state:
    st.session_state.show_application_feedback = False
if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
if "backend_url" not in st.session_state:
    st.session_state.backend_url = "https://synthetic-city-jimmy-demonstrates.trycloudflare.com"  # Default backend URL
if "use_backend" not in st.session_state:
    st.session_state.use_backend = True  # Toggle between backend and mock data
if "jobs_data" not in st.session_state:
    st.session_state.jobs_data = {}  # Initialize jobs data

# Auto-sync from backend if enabled and not already synced
if "backend_synced" not in st.session_state:
    st.session_state.backend_synced = False

if st.session_state.use_backend and not st.session_state.backend_synced:
    # Try to sync jobs from backend on first load
    try:
        api_service = get_api_service()
        result = api_service.get_jobs()
        if not handle_api_error(result, "Initial backend sync failed", show_error=False):
            # Clear mock data and load backend data
            st.session_state.jobs_data = {}
            if isinstance(result, list) and len(result) > 0:
                backend_jobs = {}
                for job in result:
                    job_title = job.get("job_title", "Unknown Job")
                    backend_jobs[job_title] = {
                        "title": job_title,
                        "department": job.get("department", "Engineering"),
                        "description": job.get("description", ""),
                        "requirements": job.get("requirements", "").split('\n') if isinstance(job.get("requirements"), str) else [],
                        "applicants": 0,
                        "avg_score": 0,
                        "id": job.get("id"),
                        "posted_date": job.get("posted_date"),
                        "is_active": job.get("is_active", True)
                    }
                st.session_state.jobs_data = backend_jobs
                st.session_state.backend_synced = True
    except Exception as e:
        # If backend sync fails, keep using mock data
        pass

# Use session state as the primary data source
JOBS_DATA = st.session_state.jobs_data

# --- BACKEND INTEGRATION FUNCTIONS ---
def sync_jobs_from_backend():
    """Sync job data from backend API"""
    if not st.session_state.use_backend:
        return
    
    try:
        api_service = get_api_service()
        result = api_service.get_jobs()
        
        if not handle_api_error(result, "Failed to fetch jobs from backend"):
            # Backend returns a list of jobs directly
            if isinstance(result, list):
                backend_jobs = {}
                for job in result:
                    # Convert backend format to frontend format
                    job_title = job.get("job_title", "Unknown Job")
                    backend_jobs[job_title] = {
                        "title": job_title,
                        "department": job.get("department", "Engineering"),
                        "description": job.get("description", ""),
                        "requirements": job.get("requirements", "").split('\n') if isinstance(job.get("requirements"), str) else [],
                        "applicants": 0,  # Backend doesn't provide this yet
                        "avg_score": 0,   # Backend doesn't provide this yet
                        "id": job.get("id"),
                        "posted_date": job.get("posted_date"),
                        "is_active": job.get("is_active", True)
                    }
                st.session_state.jobs_data.update(backend_jobs)
                print(f"Synced {len(backend_jobs)} jobs from backend")
            elif "jobs" in result:
                # Handle if backend wraps jobs in an object
                backend_jobs = {}
                for job in result["jobs"]:
                    job_title = job.get("job_title", "Unknown Job")
                    backend_jobs[job_title] = {
                        "title": job_title,
                        "department": job.get("department", "Engineering"),
                        "description": job.get("description", ""),
                        "requirements": job.get("requirements", "").split('\n') if isinstance(job.get("requirements"), str) else [],
                        "applicants": 0,
                        "avg_score": 0,
                        "id": job.get("id"),
                        "posted_date": job.get("posted_date"),
                        "is_active": job.get("is_active", True)
                    }
                st.session_state.jobs_data.update(backend_jobs)
                print(f"Synced {len(backend_jobs)} jobs from backend")
    except Exception as e:
        st.error(f" Backend sync error: {str(e)}")



def create_job_on_backend(job_data):
    """Create a new job on the backend"""
    if not st.session_state.use_backend:
        return True  # Skip backend call if not using backend
    
    try:
        api_service = get_api_service()
        result = api_service.create_job(job_data)
        
        if handle_api_error(result, "Failed to create job on backend"):
            return False
        
        st.success("Job created successfully on backend!")
        return True
    except Exception as e:
        st.error(f"❌ Backend error: {str(e)}")
        return False

def submit_application_to_backend(job_title, resume_file, candidate_data=None):
    """Submit job application to backend"""
    if not st.session_state.use_backend:
        return {"score": 75, "status": "success"}  # Mock response
    
    try:
        # Get job ID from jobs data
        job_data = st.session_state.jobs_data.get(job_title, {})
        job_id = job_data.get("id")
        
        if not job_id:
            st.error(f"❌ Job ID not found for '{job_title}'. Please refresh jobs from backend.")
            return None
        
        api_service = get_api_service()
        result = api_service.apply_to_job(job_id, resume_file, candidate_data)
        
        if handle_api_error(result, "Failed to submit application to backend"):
            return None
        
        return result
    except Exception as e:
        st.error(f"❌ Backend error: {str(e)}")
        return None

def analyze_resume_on_backend(resume_file, job_description=None):
    """Analyze resume using backend AI service"""
    if not st.session_state.use_backend:
        return {
            "score": 75,
            "verdict": "Medium",
            "summary": "Mock analysis - backend not connected",
            "gaps": ["Connect to backend for real analysis"],
            "suggestions": "Enable backend connection for AI-powered resume analysis"
        }
    
    try:
        api_service = get_api_service()
        result = api_service.analyze_resume(resume_file, job_description)
        
        if handle_api_error(result, "Failed to analyze resume on backend"):
            return None
        
        return result
    except Exception as e:
        st.error(f"❌ Backend error: {str(e)}")
        return None

def parse_job_document_on_backend(job_doc_file):
    """Parse job document using backend API to extract job details"""
    if not st.session_state.use_backend:
        return {
            "job_title": "Sample Job Title",
            "department": "Engineering", 
            "description": "Mock job description - backend not connected",
            "requirements": "Mock requirements - connect to backend for real parsing"
        }
    
    try:
        api_service = get_api_service()
        
        # First test if backend is reachable
        health_check = api_service.health_check()
        if "error" in health_check:
            st.error(f"🔌 Backend connection failed: {health_check['error']}")
            return None
        
        # Reset file pointer to beginning
        job_doc_file.seek(0)
        
        result = api_service.parse_job_document(job_doc_file)
        
        # Debug: Show raw response
        st.write("🐛 Debug - Raw API Response:", result)
        
        # Check for specific backend errors
        if "error" in result:
            error_msg = result["error"]
            if "secrets" in error_msg.lower():
                st.error("Backend Configuration Issue:")
                st.error(f"Error: {error_msg}")
                return None
        
        if handle_api_error(result, "Failed to parse job document on backend"):
            return None
        
        return result
    except Exception as e:
        st.error(f"❌ Backend error: {str(e)}")
        st.write(f"🐛 Exception details: {type(e).__name__}: {str(e)}")
        return None

def generate_demo_job_data(filename):
    """Generate demo job data based on filename for fallback"""
    # Extract potential job info from filename
    filename_lower = filename.lower()
    
    if "frontend" in filename_lower or "ui" in filename_lower or "react" in filename_lower:
        return {
            "job_title": "Frontend Developer",
            "department": "Engineering",
            "description": "We are looking for a skilled Frontend Developer to join our dynamic team. You will be responsible for creating engaging user interfaces using modern web technologies.",
            "requirements": "• 3+ years of experience in React.js\n• Proficiency in HTML, CSS, JavaScript\n• Experience with modern frontend tools\n• Strong problem-solving skills"
        }
    elif "backend" in filename_lower or "api" in filename_lower or "server" in filename_lower:
        return {
            "job_title": "Backend Developer", 
            "department": "Engineering",
            "description": "Join our backend team to build scalable APIs and server-side applications. You will work on high-performance systems that power our platform.",
            "requirements": "• 3+ years of backend development experience\n• Proficiency in Python/Node.js\n• Database design and optimization\n• API development and microservices"
        }
    elif "data" in filename_lower or "analyst" in filename_lower:
        return {
            "job_title": "Data Analyst",
            "department": "Analytics", 
            "description": "We are seeking a Data Analyst to help drive business decisions through data insights and reporting.",
            "requirements": "• Strong SQL skills\n• Experience with Python/R\n• Data visualization tools\n• Statistical analysis background"
        }
    else:
        return {
            "job_title": "Software Engineer",
            "department": "Engineering",
            "description": "We are looking for a talented Software Engineer to help build innovative solutions and contribute to our growing platform.",
            "requirements": "• Bachelor's degree in Computer Science or related field\n• 2+ years of software development experience\n• Strong programming fundamentals\n• Collaborative team player"
        }

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6, .card-title {
        font-family: 'Poppins', sans-serif;
    }
    body {
        background-color: #f0f2f6;
    }
    .sidebar-wrapper {
        position: fixed;
        width: 256px;
        background-color: black;
        color: white;
        padding: 1.5rem 1rem;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        height: 100vh;
        z-index: 1000;
        top: 0;
        left: 0;
        box-sizing: border-box;
    }
    /* Ensure Streamlit's main content is centered */
    .stApp > div > div > div > div {
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
    }
    /* More specific targeting for Streamlit's content container */
    section.main > div.block-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 1rem 2rem !important;
    }
    /* Center content within columns */
    .stColumns > div {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    /* Ensure full width utilization within the centered container */
    .element-container, .stMarkdown, .stButton {
        width: 100%;
    }
    /* Main content container centering - Fixed sidebar offset */
    .main .block-container {
        max-width: calc(1200px + 256px) !important;
        margin: 0 auto !important;
        padding: 0.5rem 2rem 1rem 258px !important; /* Left padding instead of margin */
        width: 100% !important;
    }
    /* When no role is selected (landing page), no margin */
    .no-sidebar .main .block-container {
        margin-left: 0 !important;
        padding-left: 1rem !important;
        max-width: 1200px !important;
    }
    /* Header alignment - left aligned at top with proper spacing */
    .main h1, .main h2, .main h3 {
        text-align: left;
        margin-top: 0 !important;
        padding-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Proper page title spacing */
    .main h1:first-child {
        padding-top: 1rem !important;
        margin-bottom: 1rem !important;
    }
    /* Content structure alignment */
    .stMarkdown, .stSelectbox, .stTextInput, .stTextArea, 
    .stButton, .stMetric, .stDataFrame {
        margin-bottom: 1rem;
    }
    
    /* Form elements alignment */
    .stButton > button {
        margin-top: 0.5rem;
    }
    
    /* Section spacing */
    .section-spacing {
        margin: 1.5rem 0;
    }
    
    /* Center specific dashboard elements */
    .stMetric {
        text-align: center;
    }
    /* Reset text alignment for content that should be left-aligned */
    .stTextArea textarea, .stTextInput input, .stSelectbox, 
    .table-container, .job-posting-card, .summary-card,
    .stMarkdown p, .stMarkdown div {
        text-align: left !important;
    }
    /* Hide Streamlit sidebar on home page */
    .hide-sidebar .stSidebar {
        display: none;
    }
    .hide-sidebar .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
    }
    /* Hide only Streamlit's default page navigation, keep custom content */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebarNavItems"] {
        display: none !important;
    }
    /* Enhanced sidebar button styling */
    .stSidebar .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
        margin: 4px 0 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        width: 100% !important;
        font-size: 14px !important;
        min-height: 2.5rem !important;
    }
    .stSidebar .stButton > button:hover {
        background:#FAFA33 !important;
        color: #ffffff !important;
        transform: translateX(4px) !important;
        border: none !important;
    }
    .stSidebar .stButton > button:focus {
        box-shadow: #FAFA33 !important;
        outline: none !important;
        border: none !important;
    }
    .stSidebar .stButton > button:active {
        background: #FAFA33 !important;
        border: none !important;
    }
    .header {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 24px;
        background-color: white;
        border-bottom: 1px solid #E2E8F0;
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
    }
    .header > div {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    /* Center page content */
    .stApp > div:first-child {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    /* Center dashboard cards and grids */
    .card-grid {
        display: flex;
        justify-content: center;
        gap: 24px;
        margin: 24px auto;
        max-width: 1200px;
        flex-wrap: wrap;
    }
    /* Center table containers */
    .table-container {
        margin: 0 auto !important;
        max-width: 1200px !important;
    }
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 16px;
        margin: 6px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    .sidebar-nav-item:hover:not(.active) {
        background-color: #334155;
    }
    .sidebar-nav-item.active {
        background-color: #FAFA33;
        color: black;
        font-weight: 700;
    }
    .card-container-landing {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin-top: 50px;
    }
    .card-landing {
        background-color: #fff;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 30px;
        text-align: center;
        width: 350px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 2px solid transparent;
    }
    .card-landing:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        border-color: #a8d8e0;
    }
    .card-landing-icon {
        width: 80px;
        height: 80px;
        margin-bottom: 20px;
    }
    .card-landing-title {
        font-size: 1.5em;
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
    }
    .card-landing-description {
        color: #666;
        font-size: 0.9em;
    }
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 24px;
        margin-top: 24px;
    }
    .summary-card, .job-posting-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 2px solid rgba(212, 247, 76, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .summary-card::before, .job-posting-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
        pointer-events: none;
    }
    .summary-card:hover, .job-posting-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        border-color: rgba(212, 247, 76, 0.6);
    }
    .summary-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .job-posting-card {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .job-posting-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .table-container {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .table-responsive {
        overflow-x: auto;
    }
    .table {
        width: 100%;
        border-collapse: collapse;
    }
    .table th, .table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #F1F5F9;
    }
    .table th {
        color: #64748B;
        font-weight: 500;
    }
    .table tbody tr:hover {
        background-color: #F8FAFC;
    }
    .tag-high {
        background-color: #D1FAE5;
        color: #065F46;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.875rem;
    }
    .tag-medium {
        background-color: #FFFBEB;
        color: #78350F;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.875rem;
    }
    .tag-low {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.875rem;
    }
    .metric-score {
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        width: 80px;
        height: 80px;
    }
    .metric-circle-bg {
        stroke-width: 10;
        stroke: #E2E8F0;
        fill: transparent;
        r: 50;
        cx: 60;
        cy: 60;
    }
    .metric-circle-fill {
        stroke-width: 10;
        stroke-dasharray: 314.159;
        stroke-linecap: round;
        fill: transparent;
        r: 50;
        cx: 60;
        cy: 60;
        transition: stroke-dashoffset 0.5s ease-in-out;
        transform: rotate(-90deg);
        transform-origin: 50% 50%;
    }
    .metric-number {
        position: absolute;
        font-size: 24px;
        font-weight: 700;
    }
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
    }
    .modal-content {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        width: 100%;
        max-width: 768px;
        padding: 0;
    }
    .modal-header {
        padding: 24px;
        border-bottom: 4px solid;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .modal-tabs {
        padding: 24px;
        border-bottom: 1px solid #E2E8F0;
        display: flex;
        gap: 8px;
    }
    .tab-button {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 600;
        border-radius: 6px;
        transition: all 0.2s ease;
        background: none;
        border: none;
        cursor: pointer;
        color: #4B5563;
    }
    .tab-button.active {
        background-color: #E0E7FF;
        color: #312E81;
    }
    .modal-body {
        padding: 24px;
    }
    .file-upload-box {
        border: 2px dashed #CBD5E1;
        border-radius: 8px;
        padding: 24px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .file-upload-box:hover {
        border-color: #64748B;
    }
    .faq-item {
        background-color: #F8FAFC;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .st-emotion-cache-1cypcdb {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


# --- UTILITY FUNCTIONS FOR STYLING AND COMPONENTS ---
def get_score_color(score):
    if score >= 80: return "#10B981"
    if score >= 60: return "#F59E0B"
    return "#EF4444"

def get_fit_class(score):
    if score >= 80: return "high"
    if score >= 60: return "medium"
    return "low"

def get_tag_html(score, verdict=None):
    # If verdict is provided from backend, use it; otherwise calculate from score
    if verdict:
        verdict_lower = verdict.lower()
        if verdict_lower in ['high', 'excellent', 'strong']:
            return '<span class="tag-high">High Fit</span>'
        elif verdict_lower in ['medium', 'moderate', 'average']:
            return '<span class="tag-medium">Medium Fit</span>'
        else:  # low, poor, weak, etc.
            return '<span class="tag-low">Low Fit</span>'
    
    # Fallback to score-based calculation
    if score >= 80: return '<span class="tag-high">High Fit</span>'
    if score >= 60: return '<span class="tag-medium">Medium Fit</span>'
    return '<span class="tag-low">Low Fit</span>'

def render_score_circle(score, color=None):
    if color is None: color = get_score_color(score)
    stroke_offset = 314.159 * (1 - score / 100)
    st.markdown(f"""
        <div class="metric-score">
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                <circle class="metric-circle-bg" stroke="currentColor"></circle>
                <circle class="metric-circle-fill" stroke-dashoffset="{stroke_offset}" stroke="{color}"></circle>
            </svg>
            <span class="metric-number" style="color: {color};">{score}</span>
        </div>
    """, unsafe_allow_html=True)


# --- MODALS ---
@st.dialog("📄 Analyze New Resume")
def analyze_resume_modal():
    st.markdown("#### 👤 Candidate Information")
    col1, col2 = st.columns(2)
    
    with col1:
        candidate_name = st.text_input(
            "Candidate Name", 
            placeholder="e.g., John Doe", 
            key="analyze_candidate_name"
        )
    
    with col2:
        job_role = st.text_input(
            "Job Role", 
            placeholder="e.g., Frontend Developer", 
            key="analyze_job_role"
        )
    
    st.markdown("#### 📎 Upload Files")
    
    job_desc_file = st.file_uploader(
        "Job Description File",
        type=['txt', 'pdf', 'docx'],
        key="analyze_job_desc_file",
        help="Upload the job description document"
    )
    
    resume_file = st.file_uploader(
        "Candidate Resume File",
        type=['txt', 'pdf', 'docx'],
        key="analyze_resume_file", 
        help="Upload the candidate's resume document"
    )
    
    st.markdown("---")
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔄 Reset Form", key="reset_form", use_container_width=True):
            # Clear form by resetting session state keys
            for key in ['analyze_candidate_name', 'analyze_job_role', 'analyze_job_desc_file', 'analyze_resume_file']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col_btn2:
        if st.button("❌ Cancel", key="cancel_modal", use_container_width=True):
            st.rerun()
    
    with col_btn3:
        if st.button("🚀 Analyze", key="run_analysis", type="primary", use_container_width=True):
            # Validation
            if not candidate_name:
                st.error("Please enter candidate name")
            elif not job_role:
                st.error("Please enter job role")
            elif not job_desc_file:
                st.error("Please upload job description file")
            elif not resume_file:
                st.error("Please upload resume file")
            else:
                # Success - would run analysis here
                st.success(f"Starting analysis for {candidate_name} - {job_role}")
                # Close modal after short delay
                import time
                time.sleep(1)
                st.rerun()

@st.dialog("Candidate Details")
def view_details_modal(candidate_data):
    # Check if this is backend data (has application_id and missing_skills) or legacy data
    is_backend_data = 'application_id' in candidate_data and 'missing_skills' in candidate_data
    
    # Header section that matches the screenshot
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; color: #1e293b; font-size: 2rem; font-weight: 700;">{candidate_data['name']}</h1>
        <p style="color: #64748b; margin: 4px 0 12px 0; font-size: 1.1rem;">{candidate_data['job_role']}</p>
        {get_tag_html(candidate_data['score'], candidate_data.get('verdict'))}
    </div>
    """, unsafe_allow_html=True)
    
    if is_backend_data:
        # Enhanced tabs for backend data
        tabs = st.tabs(["👤 Overview", "🎯 Missing Skills", "💡 AI Feedback", "📋 Application Details"])
        
        with tabs[0]:
            # Layout with score circle and AI summary side by side
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Score circle
                score_color = get_score_color(candidate_data['score'])
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; margin-top: 20px;">
                    <div style="width: 100px; height: 100px; border-radius: 50%; border: 8px solid {score_color}; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; color: {score_color}; margin-bottom: 12px;">
                        {candidate_data['score']}
                    </div>
                    <p style="text-align: center; font-weight: 600; color:#475569; margin: 0;">Relevance Score</p>
                    <p style="text-align: center; font-weight: 600; color:#10b981; margin: 4px 0 0 0;">{candidate_data.get('verdict', 'Medium')} Fit</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### AI Assessment")
                feedback = candidate_data.get('feedback', 'Application processed successfully.')
                st.markdown(f'<p style="color:#475569; line-height: 1.6;">{feedback}</p>', unsafe_allow_html=True)
                
                # Quick stats
                st.markdown("#### Quick Stats")
                col2a, col2b = st.columns(2)
                with col2a:
                    missing_count = len(candidate_data.get('missing_skills', []))
                    st.metric("Missing Skills", missing_count)
                with col2b:
                    resume_file = candidate_data.get('resume_file', 'N/A')
                    st.markdown(f"**Resume:** {resume_file}")
        
        with tabs[1]:
            st.markdown("#### Missing Skills Analysis")
            missing_skills = candidate_data.get('missing_skills', [])
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin: 8px 0; padding: 8px; background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 4px;">
                        <span style="color: #ef4444; margin-right: 8px; font-weight: bold;">×</span>
                        <span style="color: #7f1d1d;">{skill}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("#### Recommendations")
                st.markdown(f"""
                <div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 16px; margin-top: 12px;">
                    <p style="color: #92400e; margin: 0; line-height: 1.6;">
                        Consider developing skills in: <strong>{', '.join(missing_skills[:3])}</strong>. 
                        These areas would significantly improve the candidate's match for this role.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("No missing skills identified! This candidate has excellent skill alignment.")
        
        with tabs[2]:
            st.markdown("#### Detailed AI Feedback")
            feedback = candidate_data.get('feedback', 'Application processed successfully.')
            st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
                <p style="color: #374151; line-height: 1.6; margin: 0;">{feedback}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Verdict-based additional insights
            verdict = candidate_data.get('verdict', 'Medium').lower()
            if verdict == 'high':
                st.success("This candidate is highly recommended for this position!")
            elif verdict == 'medium':
                st.info("This candidate shows potential with some areas for improvement.")
            else:
                st.warning("This candidate may need significant development to fit this role.")
        
        with tabs[3]:
            st.markdown("#### Application Information")
            
            col3a, col3b = st.columns(2)
            with col3a:
                if candidate_data.get('application_id'):
                    st.markdown(f"**Application ID:** {candidate_data['application_id']}")
                if candidate_data.get('resume_file'):
                    st.markdown(f"**Resume File:** {candidate_data['resume_file']}")
                st.markdown(f"**Job Applied For:** {candidate_data['job_role']}")
                
            with col3b:
                if candidate_data.get('application_date'):
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(candidate_data['application_date'].replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
                        st.markdown(f"**Applied:** {formatted_date}")
                    except:
                        st.markdown(f"**Applied:** {candidate_data['application_date']}")
                
                st.markdown(f"**Relevance Score:** {candidate_data['score']}/100")
                st.markdown(f"**Final Verdict:** {candidate_data.get('verdict', 'Medium')}")
    
    else:
        # Original tabs for legacy data
        tabs = st.tabs(["👤 Overview", "💡 AI Feedback", "📊 Comparison"])
        
        with tabs[0]:
            # Layout matching the screenshot with score circle and AI summary side by side
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Score circle that matches the screenshot
                score_color = get_score_color(candidate_data['score'])
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; margin-top: 20px;">
                    <div style="width: 100px; height: 100px; border-radius: 50%; border: 8px solid {score_color}; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; color: {score_color}; margin-bottom: 12px;">
                        {candidate_data['score']}
                    </div>
                    <p style="text-align: center; font-weight: 600; color:#475569; margin: 0;">Relevance Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### AI Summary")
                st.markdown(f'{candidate_data.get("summary", "Candidate assessment completed.")}')
                
                if candidate_data.get("gaps"):
                    st.markdown("#### Skill Gaps Identified")
                    for gap in candidate_data["gaps"]:
                        st.markdown(f'❌ {gap}')
        
        with tabs[1]:
            st.markdown("#### Highlighted Gaps")
            if candidate_data.get("gaps"):
                for gap in candidate_data["gaps"]:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin: 8px 0;">
                        <span style="color: #ef4444; margin-right: 8px;">●</span>
                        <span>{gap}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No significant gaps identified!")
                
            st.markdown("---")
            st.markdown("#### 💡 Improvement Feedback")
            st.info(candidate_data.get("suggestions", "Continue developing relevant skills and experience."))

        with tabs[2]:
            st.markdown("#### Score Comparison")
            
            # Get the job data for comparison
            job_data = JOBS_DATA.get(candidate_data['job_role'], {})
            avg_score = job_data.get('avg_score', 0)
            
            # Candidate score bar
            st.markdown(f"**Candidate Score**")
            st.markdown(f'<div style="color: {get_score_color(candidate_data["score"])}; font-weight: bold; float: right;">{candidate_data["score"]}</div>', unsafe_allow_html=True)
            st.progress(candidate_data['score'] / 100)
            
            # Average score bar  
            st.markdown(f"**Average for Role**")
            st.markdown(f'<div style="color: #64748b; font-weight: bold; float: right;">{avg_score}</div>', unsafe_allow_html=True)
            st.progress(avg_score / 100)
            
            st.markdown("---")
            st.markdown(f"This chart compares {candidate_data['name']}'s relevance score to the average score of all candidates who applied for the {candidate_data['job_role']} position.")
            
            if candidate_data['score'] > avg_score:
                st.success(f"This candidate scored {candidate_data['score'] - avg_score} points above average!")
            elif candidate_data['score'] < avg_score:
                st.warning(f"This candidate scored {avg_score - candidate_data['score']} points below average.")
            else:
                st.info("This candidate scored exactly at the average level.")
    
    with tabs[1]:
        st.markdown("#### Highlighted Gaps")
        if candidate_data.get("gaps"):
            for gap in candidate_data["gaps"]:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin: 8px 0;">
                    <span style="color: #ef4444; margin-right: 8px;">●</span>
                    <span>{gap}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No significant gaps identified!")
            
        st.markdown("---")
        st.markdown("#### 💡 Improvement Feedback")
        st.info(candidate_data["suggestions"])

    with tabs[2]:
        st.markdown("#### Score Comparison")
        
        # Get the job data for comparison
        job_data = JOBS_DATA.get(candidate_data['job_role'], {})
        avg_score = job_data.get('avg_score', 0)
        
        # Candidate score bar
        st.markdown(f"**Candidate Score**")
        st.markdown(f'<div style="color: {get_score_color(candidate_data["score"])}; font-weight: bold; float: right;">{candidate_data["score"]}</div>', unsafe_allow_html=True)
        st.progress(candidate_data['score'] / 100)
        
        # Average score bar  
        st.markdown(f"**Average for Role**")
        st.markdown(f'<div style="color: #64748b; font-weight: bold; float: right;">{avg_score}</div>', unsafe_allow_html=True)
        st.progress(avg_score / 100)
        
        st.markdown("---")
        st.markdown(f"This chart compares {candidate_data['name']}'s relevance score to the average score of all candidates who applied for the {candidate_data['job_role']} position.")
        
        if candidate_data['score'] > avg_score:
            st.success(f"This candidate scores {candidate_data['score'] - avg_score} points above average!")
        elif candidate_data['score'] < avg_score:
            st.warning(f"This candidate scores {avg_score - candidate_data['score']} points below average.")
        else:
            st.info("This candidate scores exactly at the average.")

@st.dialog("💼 Job Details")
def job_details_modal(job_title, job_data):
    # Back button
    if st.button("← Back to All Jobs", key="back_to_jobs"):
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content layout - using full width more effectively
    col_main, col_apply = st.columns([3, 2])
    
    with col_main:
        # Job title and department
        st.markdown(f"""
        <div style="margin-bottom: 32px;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #1e293b; margin: 0 0 8px 0; line-height: 1.2;">{job_title}</h1>
            <p style="color: #64748b; font-size: 1.125rem; margin: 0; font-weight: 500;">{job_data['department']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Job Description Section
        st.markdown("""
        <div style="margin-bottom: 32px;">
            <h3 style="font-size: 1.375rem; font-weight: 600; color: #1e293b; margin: 0 0 16px 0;">Job Description</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<p style='color: #475569; line-height: 1.7; font-size: 1rem; margin-bottom: 32px;'>{job_data['description']}</p>", unsafe_allow_html=True)
        
        # Requirements Section
        st.markdown("""
        <div style="margin-bottom: 16px;">
            <h3 style="font-size: 1.375rem; font-weight: 600; color: #1e293b; margin: 0 0 16px 0;">Requirements</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for i, requirement in enumerate(job_data['requirements']):
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
                <span style="color: #3b82f6; font-weight: 600; margin-right: 12px; margin-top: 2px;">•</span>
                <span style="color: #475569; line-height: 1.6; font-size: 1rem;">{requirement}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col_apply:
        # Application section with better styling
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 32px 24px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Upload Your Resume")
        st.markdown("<p style='color: #64748b; font-size: 0.925rem; margin-bottom: 20px;'>Share your resume to get personalized feedback</p>", unsafe_allow_html=True)
        
        # Enhanced file upload section
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'docx'],
            key=f"resume_upload_{job_title}",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.markdown("""
            <div style="background: #dcfce7; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; margin: 16px 0; text-align: center;">
                <div style="color: #16a34a; font-size: 2rem; margin-bottom: 8px;"></div>
                <p style="color: #15803d; margin: 0; font-weight: 600;">Resume uploaded successfully!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="border: 2px dashed #cbd5e1; border-radius: 12px; padding: 48px 20px; text-align: center; margin: 20px 0; background: #fafbfc;">
                <div style="color: #94a3b8; font-size: 3.5rem; margin-bottom: 16px;">📄</div>
                <p style="color: #64748b; margin: 0; font-weight: 600; font-size: 1rem;">Upload a file</p>
                <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.875rem;">TXT, PDF, DOCX</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced Get Feedback button
        if st.button("🚀 Get Feedback", type="primary", use_container_width=True, key=f"get_feedback_{job_title}"):
            if uploaded_file:
                # Prepare candidate data
                candidate_data = {
                    'name': f"Candidate {st.session_state.jobs_data[job_title]['applicants'] + 1}",
                    'job_role': job_title,
                }
                
                # Submit application to backend if enabled
                backend_result = submit_application_to_backend(job_title, uploaded_file, candidate_data)
                
                # Update the applicant count in session state
                if job_title in st.session_state.jobs_data:
                    st.session_state.jobs_data[job_title]['applicants'] += 1
                    
                    # Create a new candidate record for tracking
                    score = backend_result.get('relevance_score', 75) if backend_result else 75
                    new_candidate = {
                        'name': candidate_data['name'],
                        'job_role': job_title,
                        'score': score,
                        'verdict': backend_result.get('verdict', 'High' if score >= 80 else 'Medium' if score >= 60 else 'Low') if backend_result else 'Medium',
                        'resume_file': uploaded_file.name
                    }
                    
                    # Add to candidates data if you want to track individual applications
                    if 'new_applications' not in st.session_state:
                        st.session_state.new_applications = []
                    st.session_state.new_applications.append(new_candidate)
                
                # Show application feedback - create a session state to handle this after modal closes
                st.session_state.show_application_feedback = True
                st.session_state.feedback_job_title = job_title
                st.session_state.feedback_resume_name = uploaded_file.name
                st.session_state.feedback_backend_result = backend_result  # Store the full backend result
                
                success_message = "🎉 Application submitted!"
                if st.session_state.use_backend and backend_result:
                    success_message += f" Score: {backend_result.get('relevance_score', 'N/A')}"
                else:
                    success_message += " You'll receive feedback within 24 hours."
                    
                st.success(success_message)
                
                # Close current modal and show feedback
                st.rerun()
            else:
                st.error("Please upload your resume first!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced statistics section
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 24px;">
            <h4 style="color: #1e293b; margin: 0 0 16px 0; font-size: 1.125rem; font-weight: 600;">Application Stats</h4>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="color: #64748b; font-size: 0.925rem;">� Total Applications</span>
                <span style="color: #1e293b; font-weight: 700; font-size: 1rem;">{job_data['applicants']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b; font-size: 0.925rem;">📊 Average Score</span>
                <span style="color: #10b981; font-weight: 700; font-size: 1rem;">{job_data['avg_score']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

@st.dialog("➕ Create New Job Posting")
def create_job_posting_modal():
    st.markdown("Fill in the details below to create a new job posting:")
    
    # Document Upload Section - moved to top for auto-fill functionality
    st.markdown("### 📄 Auto-Fill from Document (Optional)")
    st.markdown("Upload a job description document to automatically populate the form fields below:")
    st.info("**Supported formats:** PDF, DOC, DOCX only. Other formats will be rejected by the backend.")
    
    job_doc_file = st.file_uploader(
        "Upload job description document",
        type=['pdf', 'docx', 'doc'],
        key="job_doc_upload",
        help="Upload a job description document (PDF, DOC, or DOCX) to auto-fill the form fields"
    )
    
    # Initialize session state for form fields if not exists
    if "parsed_job_title" not in st.session_state:
        st.session_state.parsed_job_title = ""
    if "parsed_department" not in st.session_state:
        st.session_state.parsed_department = ""
    if "parsed_description" not in st.session_state:
        st.session_state.parsed_description = ""
    if "parsed_requirements" not in st.session_state:
        st.session_state.parsed_requirements = ""
    if "parsing_completed" not in st.session_state:
        st.session_state.parsing_completed = False
    if "form_key_suffix" not in st.session_state:
        st.session_state.form_key_suffix = 0
    
    # Parse document when uploaded
    if job_doc_file and not st.session_state.parsing_completed:
        st.success(f"Document '{job_doc_file.name}' uploaded successfully!")
        
        # Parse button
        col_parse1, col_parse2, col_parse3 = st.columns([1, 2, 1])
        with col_parse2:
            if st.button(" Parse Document & Auto-Fill Form", type="primary", use_container_width=True):
                # Validate file type first
                allowed_extensions = ['.pdf', '.docx', '.doc']
                if not any(job_doc_file.name.lower().endswith(ext) for ext in allowed_extensions):
                    st.error(f" Unsupported file type: {job_doc_file.name}")
                    st.error(" Please upload PDF, DOC, or DOCX files only.")
                    st.stop()
                
                with st.spinner("Testing backend connection..."):
                    # First test backend connection
                    api_service = get_api_service()
                    health_result = api_service.health_check()
                    
                    if "error" in health_result:
                        st.error(f"Backend connection failed: {health_result['error']}")
                        st.info("Try these steps:")
                        st.info("1. Check if the backend URL is correct in the sidebar")
                        st.info("2. Ensure the backend server is running")
                        st.info("3. Click 'Test Connection' in the sidebar")
                    else:
                        st.success("Backend connected! Parsing document...")
                        
                        with st.spinner("Parsing document..."):
                            parsed_data = parse_job_document_on_backend(job_doc_file)
                            
                            if parsed_data:
                                # Update session state with parsed data
                                st.session_state.parsed_job_title = parsed_data.get("job_title", "")
                                st.session_state.parsed_department = parsed_data.get("department", "")
                                st.session_state.parsed_description = parsed_data.get("description", "")
                                st.session_state.parsed_requirements = parsed_data.get("requirements", "")
                                st.session_state.parsing_completed = True
                                
                                st.success("🎉 Document parsed successfully! Form fields updated below.")
                                st.info("👀 **Please review the auto-filled information and make any necessary changes before creating the job.**")
                                
                                # Show a preview of parsed data
                                with st.expander("📋 Parsed Data Preview", expanded=True):
                                    st.write("**Job Title:**", st.session_state.parsed_job_title)
                                    st.write("**Department:**", st.session_state.parsed_department)
                                    st.write("**Description:**", st.session_state.parsed_description[:200] + "..." if len(st.session_state.parsed_description) > 200 else st.session_state.parsed_description)
                                    st.write("**Requirements:**", st.session_state.parsed_requirements[:200] + "..." if len(st.session_state.parsed_requirements) > 200 else st.session_state.parsed_requirements)
                                    st.info("👇 **These values are automatically filled in the form below**")
                                
                                # Removed st.rerun() - fields will update on next interaction
                            else:
                                st.warning("Backend parsing failed. Using demo data...")
                                # Fallback to demo data based on filename
                                demo_data = generate_demo_job_data(job_doc_file.name)
                                st.session_state.parsed_job_title = demo_data["job_title"]
                                st.session_state.parsed_department = demo_data["department"]
                                st.session_state.parsed_description = demo_data["description"]
                                st.session_state.parsed_requirements = demo_data["requirements"]
                                st.session_state.parsing_completed = True
                                
                                st.info(" Demo data filled in. Please review and modify as needed before creating the job.")
                                
                                # Show a preview of demo data
                                with st.expander(" Demo Data Preview", expanded=True):
                                    st.write("**Job Title:**", st.session_state.parsed_job_title)
                                    st.write("**Department:**", st.session_state.parsed_department)
                                    st.write("**Description:**", st.session_state.parsed_description[:200] + "..." if len(st.session_state.parsed_description) > 200 else st.session_state.parsed_description)
                                    st.write("**Requirements:**", st.session_state.parsed_requirements[:200] + "..." if len(st.session_state.parsed_requirements) > 200 else st.session_state.parsed_requirements)
                                    st.info(" **These values are automatically filled in the form below**")
                                
                                # Removed st.rerun() - fields will update on next interaction
    
    # Show success message if parsing was completed
    elif st.session_state.parsing_completed:
        col_msg, col_clear = st.columns([3, 1])
        with col_msg:
            st.success(" Document parsing completed! Review the auto-filled fields below.")
            st.info("👀 **Please review and modify the information before creating the job.**")
        with col_clear:
            if st.button("Clear Form", help="Clear auto-filled data and start fresh"):
                # Clear all parsed data
                st.session_state.parsed_job_title = ""
                st.session_state.parsed_department = ""
                st.session_state.parsed_description = ""
                st.session_state.parsed_requirements = ""
                st.session_state.parsing_completed = False
                # Removed st.rerun() - just show message
                st.success("Form cleared! You can now fill manually or upload a new document.")
    
    st.markdown("---")
    st.markdown("### ✏️ Job Details")
    st.info(" **Review and edit the information below, then click 'Create Job' to save.**")
    
    # Job Title and Department in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        job_title = st.text_input(
            "Job Title",
            placeholder="e.g., Frontend Developer",
            key="new_job_title",
            value=st.session_state.parsed_job_title
        )
    
    with col2:
        department = st.text_input(
            "Department", 
            placeholder="e.g., Engineering",
            key="new_job_department",
            value=st.session_state.parsed_department
        )
    
    # Job Description
    job_description = st.text_area(
        "Job Description",
        placeholder="Provide a summary of the role...",
        height=120,
        key="new_job_description",
        value=st.session_state.parsed_description
    )
    
    # Requirements
    requirements_text = st.text_area(
        "Requirements",
        placeholder="List each requirement on a new line...",
        height=120,
        key="new_job_requirements",
        help="Enter one requirement per line",
        value=st.session_state.parsed_requirements
    )
    
    st.markdown("---")
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel", use_container_width=True, type="secondary"):
            st.rerun()
    
    with col2:
        if st.button("Create Job", use_container_width=True, type="primary"):
            if job_title and department and job_description and requirements_text:
                # Parse requirements (split by newlines and clean up)
                requirements_list = [req.strip() for req in requirements_text.split('\n') if req.strip()]
                
                # Prepare job data for backend
                job_data = {
                    'title': job_title,
                    'department': department,
                    'description': job_description,
                    'requirements': requirements_list,
                    'applicants': 0,
                    'avg_score': 0
                }
                
                # Add the new job to session state jobs_data (local storage)
                st.session_state.jobs_data[job_title] = job_data
                
                # Try to create job on backend if enabled
                backend_success = create_job_on_backend(job_data)
                
                if backend_success:
                    st.success(f" Job posting '{job_title}' created successfully!")
                    if st.session_state.use_backend:
                        st.info(" Synced with backend API")
                else:
                    st.warning(f" Job '{job_title}' created locally but backend sync failed")
                
                # Clear parsed data from session state
                if "parsed_job_title" in st.session_state:
                    del st.session_state.parsed_job_title
                if "parsed_department" in st.session_state:
                    del st.session_state.parsed_department
                if "parsed_description" in st.session_state:
                    del st.session_state.parsed_description
                if "parsed_requirements" in st.session_state:
                    del st.session_state.parsed_requirements
                if "parsing_completed" in st.session_state:
                    del st.session_state.parsing_completed
                
                # Small delay then rerun to close modal and refresh page
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error(" Please fill in all required fields")

@st.dialog("Application Feedback") 
def application_feedback_modal(app_data):
    # Header with job title
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h2 style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0 0 4px 0;">Application Feedback</h2>
            <p style="color: #64748b; margin: 0;">For: {app_data['job_title']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Orange progress bar
    st.markdown("""
        <div style="height: 4px; background: #f97316; border-radius: 2px; margin-bottom: 24px;"></div>
    """, unsafe_allow_html=True)
    
    # Check if we have backend data or fallback data
    is_backend_data = 'verdict' in app_data and 'feedback' in app_data
    
    if is_backend_data:
        # Create tabs for backend data
        tab1, tab2 = st.tabs(["👤 Overview", "🎯 Missing Skills"])
        
        with tab1:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                render_score_circle(app_data['score'])
                verdict = app_data.get('verdict', 'Medium')
                st.markdown(f'<p style="text-align: center; font-weight: 600; color:#475569; margin-top: 10px;">{get_tag_html(app_data["score"], verdict)}</p>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('### AI Feedback')
                feedback_text = app_data.get('feedback', 'Application processed successfully.')
                st.markdown(f'<p style="color:#475569; line-height: 1.6;">{feedback_text}</p>', unsafe_allow_html=True)
                
                # Show application details if available
                if app_data.get('application_id'):
                    st.markdown('### Application Details')
                    col2a, col2b = st.columns(2)
                    with col2a:
                        st.markdown(f"**Application ID:** {app_data['application_id']}")
                        if app_data.get('resume_filename'):
                            st.markdown(f"**Resume File:** {app_data['resume_filename']}")
                    with col2b:
                        if app_data.get('application_date'):
                            from datetime import datetime
                            try:
                                # Parse the datetime string and format it nicely
                                dt = datetime.fromisoformat(app_data['application_date'].replace('Z', '+00:00'))
                                formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
                                st.markdown(f"**Applied:** {formatted_date}")
                            except:
                                st.markdown(f"**Applied:** {app_data['application_date']}")
        
        with tab2:
            st.markdown('### Missing Skills')
            missing_skills = app_data.get('missing_skills', [])
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f'<p style="display: flex; align-items: center; gap: 8px; color: #EF4444;"><span style="font-size: 1.25em; line-height: 1; color: inherit;">&times;</span> {skill}</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #10b981;">✓ No missing skills identified!</p>', unsafe_allow_html=True)
            
            st.markdown('### Recommendations')
            if missing_skills:
                recommendations = f"Consider developing skills in: {', '.join(missing_skills[:3])}. These areas would significantly improve your match for this role."
            else:
                recommendations = "Great job! Your skills align well with the job requirements. Continue to strengthen your existing expertise."
            
            st.markdown(f'<div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 16px; margin-top: 12px;"><p style="color: #92400e; margin: 0; line-height: 1.6;">{recommendations}</p></div>', unsafe_allow_html=True)
    
    else:
        # Use original format for fallback data
        tab1, tab2 = st.tabs([" Overview", " Improvement Plan"])
        
        with tab1:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                render_score_circle(app_data['score'])
                st.markdown(f'<p style="text-align: center; font-weight: 600; color:#475569; margin-top: 10px;">{get_tag_html(app_data["score"])}</p>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('### AI Summary')
                st.markdown(f'<p style="color:#475569; line-height: 1.6;">{app_data.get("summary", "Application processed successfully.")}</p>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('### Focus Areas for Your Resume')
            for area in app_data.get("focus_areas", []):
                st.markdown(f'<p style="display: flex; align-items: center; gap: 8px; color: #EF4444;"><span style="font-size: 1.25em; line-height: 1; color: inherit;">&times;</span> {area}</p>', unsafe_allow_html=True)
            
            st.markdown('### AI-Powered Suggestions')
            suggestions = app_data.get("suggestions", "Continue to develop your skills and experience.")
            st.markdown(f'<div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 16px; margin-top: 12px;"><p style="color: #92400e; margin: 0; line-height: 1.6;">{suggestions}</p></div>', unsafe_allow_html=True)


# --- MAIN APP LAYOUTS ---
def render_landing_page():
    # Hide the sidebar on landing page and adjust main content
    st.markdown("""
    <style>
        .stSidebar {
            display: none !important;
        }
        .main .block-container {
            background: #111111 !important;
            margin-left: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: none !important;
            border-radius: 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        }
        body, html, .stApp {
            background: linear-gradient(135deg, #111111 0%, #222222 100%) !important;
            color: #e2e8f0 !important;
        }
        h1, h2, h3, h4, h5, h6, .card-title {
            color: #fafafa !important;
        }
        .card-container-landing, .card-landing {
            background: #18181b !important;
            color: #fafafa !important;
            border: 2px solid #222 !important;
        }
        .card-landing:hover {
            border-color: #FAFA33 !important;
            box-shadow: 0 8px 24px rgba(250,250,51,0.08);
        }
        .stButton > button {
            background: #FAFA33 !important;
            color: #111 !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align:center; padding-top: 50px;">', unsafe_allow_html=True)
    
    # Display your logo using Streamlit's image function
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
    with col_logo2:
        st.image("logo.png", width=150)
    
    st.markdown('<h1 style="display :flex ;justify-content: center; font-size: 2.5em; font-weight: 600; color: #333;">Welcome to the AI Resume Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="display: flex; justify-content: center; color: #666;">Please select your role to get started.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card-container-landing">', unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("I am a Recruiter", key="recruiter_btn", use_container_width=True):
                st.session_state.role = "recruiter"
                st.session_state.page = "dashboard"
                st.rerun()

        with btn_col2:
            if st.button("I am a Student", key="student_btn", use_container_width=True):
                st.session_state.role = "candidate"
                st.session_state.page = "dashboard"
                st.rerun()

def render_sidebar():
    # Simplified sidebar styling that doesn't interfere with button functionality
    st.markdown("""
    <style>
        /* Hide only the default Streamlit navigation */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [data-testid="stSidebarNavItems"] {
            display: none !important;
        }
        /* Custom sidebar background */
        .stSidebar {
            background: black !important;
        }
        .stSidebar > div {
            background: black !important;
        }
        /* Style the logo container */
        .sidebar-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }
        .role-badge {
            background: rgba(212, 247, 76, 0.2);
            color: #D4F74C;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-top: 8px;
            display: inline-block;
        }
        /* Enhanced sidebar button styling - using more specific selectors */
        .stSidebar .stButton > button {
            background: transparent !important;
            border: none !important;
            color: #e2e8f0 !important;
            font-weight: 500 !important;
            padding: 12px 16px !important;
            margin: 4px 0 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            text-align: left !important;
            width: 100% !important;
            font-size: 14px !important;
            min-height: 2.5rem !important;
        }
        .stSidebar .stButton > button:hover {
            background: #FAFA33 !important;
            color: #000000 !important;
            transform: translateX(4px) !important;
            border: none !important;
        }
        .stSidebar .stButton > button:focus {
            box-shadow: #FAFA33 !important;
            outline: none !important;
            border: none !important;
        }
        .stSidebar .stButton > button:active {
            background: #FAFA33 !important;
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    role = st.session_state.role
    current_page = st.session_state.page
    
    # Enhanced logo section with role badge
    with st.sidebar:
        # Center the logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=80)
        
        # Role badge below logo
        st.markdown(f"""
        <div style="text-align: center; margin-top: 8px;">
            <div class="role-badge">{role.title()}</div>
        </div>
        """, unsafe_allow_html=True)

    # Navigation items with custom styling
    if role == "recruiter":
        nav_items = [
            (" Dashboard", "dashboard"), 
            (" Job Postings", "job_postings"), 
            (" Candidates", "candidates"),
            (" Reports", "reports"), 
        ]
    else:
        nav_items = [
            (" Dashboard", "dashboard"), 
            (" Job Postings", "job_postings"), 
        ]
        
    for name, page in nav_items:
        if st.sidebar.button(name, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()

    # Styled Help & Support button
    if st.sidebar.button(" Help & Support", key="nav_help_support", use_container_width=True):
        st.session_state.page = "help_support"
        st.rerun()
    
    # Backend Configuration Section
    st.sidebar.markdown("---")
    
   
def render_header(title, subtitle, avatar_url=None):
    # Header container with top alignment
    st.markdown('<div style="margin-bottom: 2rem; padding-top: 0;">', unsafe_allow_html=True)
    
    st.markdown(f'<div style="text-align: left;"><h1 style="font-size: 1.5rem; font-weight: 700; color: #1E293B; margin: 0; margin-bottom: 0.25rem;">{title}</h1><p style="color: #64748B; margin: 0; text-transform: capitalize;">{subtitle}</p></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- PAGES ---
def recruiter_dashboard_page():
    render_header("Dashboard", "Recruiter View", "https://i.pravatar.cc/40?u=recruiter")
    
    # Get metrics from backend
    api_service = get_api_service()
    backend_metrics = api_service.get_metrics()
    
    if "error" in backend_metrics:
        st.error(f"Could not load dashboard metrics: {backend_metrics.get('error', 'Unknown error')}")
        return
    
    metrics_data = {
        "Total Candidates": backend_metrics.get("total_applications", 0),
        "Open Positions": backend_metrics.get("open_positions", 0),
        "High-Fit Candidates": backend_metrics.get("high_fit_candidates", 0),
        "Avg. Score": int(backend_metrics.get("avg_score", 0))
    }
    
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">Total Candidates</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{metrics_data["Total Candidates"]}</p></div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">Open Positions</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{metrics_data["Open Positions"]}</p></div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">High-Fit Candidates</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{metrics_data["High-Fit Candidates"]}</p></div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">Avg. Score</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{metrics_data["Avg. Score"]}</p></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="table-container" style="margin-top: 24px;">', unsafe_allow_html=True)
        st.markdown('<h2 style="font-size:1.25rem; font-weight:700; color:#1E293B; margin-bottom:16px;">Recent Candidates</h2>', unsafe_allow_html=True)
        
        # Get recent candidates from backend
        backend_candidates = api_service.get_candidates(limit=5)
        if "error" in backend_candidates:
            st.write("No candidates data available")
        else:
            candidates = backend_candidates if isinstance(backend_candidates, list) else backend_candidates.get("candidates", [])
            for i, app in enumerate(candidates[:5]):
                # Extract candidate name from resume filename
                resume_filename = app.get('resume_filename', '')
                if resume_filename:
                    # Extract name from filename like "john_doe_resume.pdf" -> "John Doe"
                    candidate_name = resume_filename.replace('_resume.pdf', '').replace('_', ' ').replace('.pdf', '').title()
                    if not candidate_name or candidate_name == '.Pdf':
                        candidate_name = f"Candidate {app.get('id', 'Unknown')}"
                else:
                    candidate_name = f"Candidate {app.get('id', 'Unknown')}"
                
                job_title = app.get('job', {}).get('job_title', 'Unknown Position')
                score = app.get('relevance_score', 0)
                
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #F1F5F9;">
                        <div style="flex: 1;">
                            <p style="font-weight:600; margin:0;">{candidate_name}</p>
                            <p style="color:#475569; font-size: 0.9em; margin:0;">{job_title}</p>
                        </div>
                        <div style="margin: 0 16px;">
                            {get_tag_html(score)}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="job-posting-card" style="margin-top: 24px;">', unsafe_allow_html=True)
        st.markdown('<h2 style="font-size:1.25rem; font-weight:700; color:#1E293B; margin-bottom:16px;">Active Job Postings</h2>', unsafe_allow_html=True)
        
        # Get jobs from backend
        backend_jobs = api_service.get_jobs()
        if "error" in backend_jobs:
            st.write("No jobs data available")
        else:
            jobs = backend_jobs if isinstance(backend_jobs, list) else backend_jobs.get("jobs", [])
            for i, job in enumerate(jobs):
                job_title = job.get('job_title', 'Unknown Job')
                # Count applications for this job
                applications_count = len([app for app in candidates if app.get('job_id') == job.get('id')])
                
                if st.button(f"{job_title} ({applications_count} applicants)", key=f"dash_job_{i}", use_container_width=True):
                    st.session_state.selected_job = job_title
                    st.session_state.page = "job_applicants"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def recruiter_job_postings_page():
    render_header("Job Postings", "Recruiter View", "https://i.pravatar.cc/40?u=recruiter")
    
    # Data source indicator
   
    
    
    # Add the create new job posting button with proper styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Create New Job Posting", key="create_job_btn", type="primary", use_container_width=True):
            create_job_posting_modal()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Active Job Postings")
    
    # Create a grid layout for job cards
    cols = st.columns(2)  # 2 columns for better layout
    
    for i, (job_title, data) in enumerate(st.session_state.jobs_data.items()):
        with cols[i % 2]:  # Alternate between columns
            with st.container():
                # Create a styled, clickable job card
                with st.container():
                    st.markdown(f"""
                    <div style="border: 2px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 16px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <h3 style="font-weight:600; color:#1E293B; margin:0 0 8px 0; font-size: 1.25rem;">📋 {job_title}</h3>
                        <p style="font-size:0.875rem; color:#64748B; margin:0 0 16px;">📍 {data['department']} Department</p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="font-size:1.125rem; font-weight:700; color:#1E293B; margin:0;">{data['applicants']}</p>
                                <p style="font-size:0.75rem; color:#64748B; margin:0;">👥 Applicants</p>
                            </div>
                            <div>
                                <p style="font-size:1.125rem; font-weight:700; color:#1E293B; margin:0;">{data['avg_score']}</p>
                                <p style="font-size:0.75rem; color:#64748B; margin:0;">📊 Avg. Score</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Make the card clickable with a prominent button
                    if st.button(f"👥 View {job_title} Applicants", key=f"job_card_click_{i}", use_container_width=True, type="primary"):
                        st.session_state.selected_job = job_title
                        st.session_state.page = "job_applicants"
                        st.rerun()
                    
                    # Optional secondary action for job details
                    if st.button(f"📋 View Job Details", key=f"job_details_{i}", type="secondary", use_container_width=True):
                        job_details_modal(job_title, data)

def recruiter_candidates_page():
    render_header("Candidates", "Recruiter View", "https://i.pravatar.cc/40?u=recruiter")
    
    # Get candidates from backend
    api_service = get_api_service()
    backend_candidates = api_service.get_candidates()
    
    if "error" in backend_candidates:
        st.error(f"Could not load candidates: {backend_candidates.get('error', 'Unknown error')}")
        return
    
    # Process candidates data
    candidates = backend_candidates if isinstance(backend_candidates, list) else backend_candidates.get("candidates", [])
    
    # Transform to consistent format
    processed_candidates = []
    for app in candidates:
        # Map backend verdict to expected format
        backend_verdict = app.get('verdict', 'Medium')
        if 'High' in backend_verdict:
            verdict = 'High'
        elif 'Medium' in backend_verdict:
            verdict = 'Medium'
        elif 'Low' in backend_verdict:
            verdict = 'Low'
        else:
            verdict = 'Medium'
        
        # Extract candidate name from resume filename
        resume_filename = app.get('resume_filename', '')
        if resume_filename:
            # Extract name from filename like "john_doe_resume.pdf" -> "John Doe"
            candidate_name = resume_filename.replace('_resume.pdf', '').replace('_', ' ').replace('.pdf', '').title()
            if not candidate_name or candidate_name == '.Pdf':
                candidate_name = f"Candidate {app.get('id', 'Unknown')}"
        else:
            candidate_name = f"Candidate {app.get('id', 'Unknown')}"
        
        candidate = {
            'id': app.get('id'),
            'name': candidate_name,
            'job_role': app.get('job', {}).get('job_title', 'Unknown Position'),
            'job_id': app.get('job_id'),
            'score': app.get('relevance_score', 0),
            'verdict': verdict,
            'missing_skills': app.get('missing_skills', []),
            'feedback': app.get('feedback', ''),
            'resume_file': app.get('resume_filename', 'resume.pdf'),
            'application_date': app.get('application_date'),
            'application_id': app.get('id')
        }
        processed_candidates.append(candidate)
    
    st.markdown('<div class="table-container" style="margin-top: 24px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size:1.25rem; font-weight:700; color:#1E293B; margin-bottom:16px;">All Candidates</h2>', unsafe_allow_html=True)
    
    # Filter controls
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    search_term = col1.text_input("Search by name...", label_visibility="collapsed")
    
    # Auto-sync candidates from backend if enabled and not already synced in this session
    if st.session_state.use_backend:
        # Check if we need to sync (use a session state flag to avoid repeated syncing)
        if "candidates_synced" not in st.session_state:
            st.session_state.candidates_synced = False
        
        # Fresh data is already loaded from backend via API calls
        st.session_state.candidates_synced = True
    
    job_role_filter = col2.selectbox("Job Role", ["All Job Roles"] + list(set([c['job_role'] for c in processed_candidates])))
    verdict_filter = col3.selectbox("Verdict", ["All Verdicts", "High", "Medium", "Low"])
    
    # Apply filters
    filtered_candidates = processed_candidates.copy()
    
    # Filter by search term (name) - case insensitive partial match
    if search_term and search_term.strip():
        filtered_candidates = [cand for cand in filtered_candidates 
                             if search_term.lower().strip() in cand['name'].lower()]
    
    # Filter by job role
    if job_role_filter and job_role_filter != "All Job Roles":
        filtered_candidates = [cand for cand in filtered_candidates 
                             if cand['job_role'] == job_role_filter]
    
    # Filter by verdict
    if verdict_filter and verdict_filter != "All Verdicts":
        filtered_candidates = [cand for cand in filtered_candidates 
                             if cand['verdict'] == verdict_filter]
    active_filters = []
    if search_term and search_term.strip():
        active_filters.append(f"Name: '{search_term}'")
    if job_role_filter and job_role_filter != "All Job Roles":
        active_filters.append(f"Role: {job_role_filter}")
    if verdict_filter and verdict_filter != "All Verdicts":
        active_filters.append(f"Verdict: {verdict_filter}")
    
    if active_filters:
        st.markdown(f"**Showing {len(filtered_candidates)} candidates** | Active filters: {' • '.join(active_filters)}")
    else:
        st.markdown(f"**Showing all {len(filtered_candidates)} candidates**")
    
    # Display filtered candidates
    if filtered_candidates:
        # Table headers
        header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([2, 2, 1, 2, 1])
        header_col1.markdown("**Candidate**")
        header_col2.markdown("**Job Role**")
        header_col3.markdown("**Score**")
        header_col4.markdown("**Verdict**")
        header_col5.markdown("**Action**")
        
        st.markdown("---")
        
        # Table rows
        for i, cand in enumerate(filtered_candidates):
            row_col1, row_col2, row_col3, row_col4, row_col5 = st.columns([2, 2, 1, 2, 1])
            
            with row_col1:
                st.markdown(f"**{cand['name']}**")
            
            with row_col2:
                st.markdown(cand['job_role'])
            
            with row_col3:
                # Show score as a simple number with color
                score_color = get_score_color(cand['score'])
                st.markdown(f'<p style="color: {score_color}; font-weight: bold; margin: 0;">{cand["score"]}</p>', unsafe_allow_html=True)
            
            with row_col4:
                st.markdown(get_tag_html(cand['score']), unsafe_allow_html=True)
            
            with row_col5:
                if st.button("View Details", key=f"view_details_table_{i}", type="secondary"):
                    view_details_modal(cand)
            
            # Add separator between rows
            if i < len(filtered_candidates) - 1:
                st.markdown("---")
    else:
        st.info("No candidates match the current filter criteria. Try adjusting your search terms.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def recruiter_reports_page():
    render_header("Reports", "Recruiter View", "https://i.pravatar.cc/40?u=recruiter")
    
    # Get metrics and candidates from backend
    api_service = get_api_service()
    backend_metrics = api_service.get_metrics()
    backend_candidates = api_service.get_candidates()
    
    if "error" in backend_metrics:
        st.error(f"Could not load metrics: {backend_metrics.get('error', 'Unknown error')}")
        return
    
    if "error" in backend_candidates:
        st.error(f"Could not load candidates: {backend_candidates.get('error', 'Unknown error')}")
        return
    
    # Get metrics data
    total_candidates = backend_metrics.get("total_applications", 0)
    avg_score = round(backend_metrics.get("avg_score", 0))
    high_fit_candidates = backend_metrics.get("high_fit_candidates", 0)
    
    # Process candidates data for detailed analytics
    candidates = backend_candidates if isinstance(backend_candidates, list) else backend_candidates.get("candidates", [])
    
    # Transform to consistent format
    processed_candidates = []
    for app in candidates:
        # Map backend verdict to expected format
        backend_verdict = app.get('verdict', 'Medium')
        if 'High' in backend_verdict:
            verdict = 'High'
        elif 'Medium' in backend_verdict:
            verdict = 'Medium'
        elif 'Low' in backend_verdict:
            verdict = 'Low'
        else:
            verdict = 'Medium'
        
        # Extract candidate name from resume filename
        resume_filename = app.get('resume_filename', '')
        if resume_filename:
            # Extract name from filename like "john_doe_resume.pdf" -> "John Doe"
            candidate_name = resume_filename.replace('_resume.pdf', '').replace('_', ' ').replace('.pdf', '').title()
            if not candidate_name or candidate_name == '.Pdf':
                candidate_name = f"Candidate {app.get('id', 'Unknown')}"
        else:
            candidate_name = f"Candidate {app.get('id', 'Unknown')}"
        
        candidate = {
            'id': app.get('id'),
            'name': candidate_name,
            'job_role': app.get('job', {}).get('job_title', 'Unknown Position'),
            'job_id': app.get('job_id'),
            'score': app.get('relevance_score', 0),
            'verdict': verdict,
            'missing_skills': app.get('missing_skills', []),
            'feedback': app.get('feedback', ''),
            'resume_file': app.get('resume_filename', 'resume.pdf'),
            'application_date': app.get('application_date'),
            'application_id': app.get('id')
        }
        processed_candidates.append(candidate)
    
    # Summary Metrics
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">Total Candidates Analyzed</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{total_candidates}</p></div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">Average Score</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{avg_score}</p></div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">High-Fit Candidates</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{high_fit_candidates}</p></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # First section: Candidate Verdict Distribution (full width)
    st.markdown('<div style="margin-top: 32px;">', unsafe_allow_html=True)
    
    # Verdict distribution section
    st.markdown('<div class="table-container" style="margin-top: 24px; padding: 20px; background: white; border-radius: 12px; border: 1px solid #e2e8f0; max-width: 600px; margin-left: auto; margin-right: auto;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 1.25rem; font-weight: 600; color: #1E293B; margin-bottom: 20px; text-align: center;">Candidate Verdict Distribution</h3>', unsafe_allow_html=True)
    
    # Calculate verdict distribution
    high_count = len([c for c in processed_candidates if c['verdict'] == 'High'])
    medium_count = len([c for c in processed_candidates if c['verdict'] == 'Medium'])
    low_count = len([c for c in processed_candidates if c['verdict'] == 'Low'])
    
    # Calculate percentages
    high_pct = (high_count / total_candidates * 100) if total_candidates > 0 else 0
    medium_pct = (medium_count / total_candidates * 100) if total_candidates > 0 else 0
    low_pct = (low_count / total_candidates * 100) if total_candidates > 0 else 0
    
    # Display verdict distribution bars
    verdict_data = [
        ("High Fit", high_count, high_pct, "#10b981"),
        ("Medium Fit", medium_count, medium_pct, "#f59e0b"),
        ("Low Fit", low_count, low_pct, "#ef4444")
    ]
    
    for verdict, count, percentage, color in verdict_data:
        st.markdown(f'''
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 0.875rem; color: #64748B;">{verdict}</span>
                <div style="text-align: right;">
                    <span style="font-size: 0.875rem; font-weight: 600; color: #1E293B;">{count}</span>
                    <span style="font-size: 0.75rem; color: #64748B; margin-left: 4px;">({percentage:.1f}%)</span>
                </div>
            </div>
            <div style="background: #f1f5f9; border-radius: 8px; height: 24px; overflow: hidden;">
                <div style="background: {color}; height: 100%; width: {percentage}%; border-radius: 8px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Second section: Average Score by Job (full width)
    st.markdown('<div style="margin-top: 32px;">', unsafe_allow_html=True)
    
    st.markdown('<div class="table-container" style="margin-top: 24px; padding: 20px; background: white; border-radius: 12px; border: 1px solid #e2e8f0; max-width: 800px; margin-left: auto; margin-right: auto;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 1.25rem; font-weight: 600; color: #1E293B; margin-bottom: 20px; text-align: center;">Average Score by Job</h3>', unsafe_allow_html=True)
    
    # Calculate average scores by job role
    job_scores = {}
    for job_title in st.session_state.jobs_data.keys():
        candidates_for_job = [c for c in processed_candidates if c['job_role'] == job_title]
        if candidates_for_job:
            avg = round(sum(c['score'] for c in candidates_for_job) / len(candidates_for_job))
            job_scores[job_title] = avg
    
    # Display horizontal bar chart
    for job_title, score in job_scores.items():
        # Calculate progress value (0-1)
        progress_value = score / 100.0
        
        # Color based on score
        if score >= 80:
            bar_color = "#6366f1"  # Blue
        elif score >= 60:
            bar_color = "#f59e0b"  # Orange
        else:
            bar_color = "#ef4444"  # Red
        
        st.markdown(f'''
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 0.875rem; color: #64748B;">{job_title}</span>
                <span style="font-size: 0.875rem; font-weight: 600; color: #1E293B;">{score}</span>
            </div>
            <div style="background: #f1f5f9; border-radius: 8px; height: 24px; overflow: hidden;">
                <div style="background: {bar_color}; height: 100%; width: {progress_value * 100}%; border-radius: 8px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Third section: Performance Table (full width)
    st.markdown('<div style="margin-top: 32px;">', unsafe_allow_html=True)
    
    st.markdown('<div class="table-container" style="margin-top: 24px; padding: 20px; background: white; border-radius: 12px; border: 1px solid #e2e8f0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 1.25rem; font-weight: 600; color: #1E293B; margin-bottom: 20px; text-align: center;">Performance by Job</h3>', unsafe_allow_html=True)
        
    # Create enhanced performance table with better alignment
    st.markdown('''
    <style>
        .performance-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .performance-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 20px 16px;
            text-align: center;
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
        }
        .performance-table th:first-child {
            text-align: left;
            min-width: 200px;
        }
        .performance-table th:last-child {
            border-right: none;
        }
        .performance-table td {
            padding: 18px 16px;
            text-align: center;
            border-bottom: 1px solid #f1f5f9;
            border-right: 1px solid #f1f5f9;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .performance-table td:first-child {
            text-align: left;
            font-weight: 600;
            color: #1e293b;
            background: #fafbfc;
        }
        .performance-table td:last-child {
            border-right: none;
        }
        .performance-table tr:hover td {
            background-color: #f8fafc;
        }
        .performance-table tr:hover td:first-child {
            background-color: #f1f5f9;
        }
        .high-fit { color: #10b981; font-weight: 700; }
        .medium-fit { color: #f59e0b; font-weight: 700; }
        .low-fit { color: #ef4444; font-weight: 700; }
        .score-cell { color: #1e293b; font-weight: 700; font-size: 1rem; }
        .count-cell { color: #64748b; font-weight: 600; }
    </style>
    <div style="overflow-x: auto; margin: 0; padding: 0;">
        <table class="performance-table">
            <thead>
                <tr>
                    <th>Job Title</th>
                    <th>Applicants</th>
                    <th>Avg. Score</th>
                    <th>High Fit</th>
                    <th>Medium Fit</th>
                    <th>Low Fit</th>
                </tr>
            </thead>
            <tbody>
    ''', unsafe_allow_html=True)
    
    # Generate enhanced table rows with better styling
    for i, job_title in enumerate(st.session_state.jobs_data.keys()):
        candidates_for_job = [c for c in processed_candidates if c['job_role'] == job_title]
        applicant_count = len(candidates_for_job)
        
        if candidates_for_job:
            avg_score = round(sum(c['score'] for c in candidates_for_job) / len(candidates_for_job))
            high_fit = len([c for c in candidates_for_job if c['verdict'] == 'High'])
            medium_fit = len([c for c in candidates_for_job if c['verdict'] == 'Medium'])
            low_fit = len([c for c in candidates_for_job if c['verdict'] == 'Low'])
        else:
            avg_score = 0
            high_fit = medium_fit = low_fit = 0
        
        st.markdown(f'''
        <tr>
            <td>{job_title}</td>
            <td class="count-cell">{applicant_count}</td>
            <td class="score-cell">{avg_score}</td>
            <td class="high-fit">{high_fit}</td>
            <td class="medium-fit">{medium_fit}</td>
            <td class="low-fit">{low_fit}</td>
        </tr>
        ''', unsafe_allow_html=True)
    
    st.markdown('''
            </tbody>
        </table>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def help_and_support_page():
    render_header("Help & Support", st.session_state.role.capitalize() + " View", "https://i.pravatar.cc/40?u=recruiter" if st.session_state.role == 'recruiter' else "https://i.pravatar.cc/40?u=candidate")

    # Center the content with proper spacing
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # FAQ Section with better styling
        st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 15px; margin-top: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h3 style="font-weight: 600; text-align: center; color: #1E293B; margin-bottom: 25px;">Frequently Asked Questions</h3>
        """, unsafe_allow_html=True)
        
        faqs = [
            "How does the AI analysis work?", 
            "What file types are supported for upload?", 
            "How accurate is the AI feedback?", 
            "Can I analyze multiple resumes at once?", 
            "Who can see my analysis results?"
        ]
        
        for i, faq in enumerate(faqs):
            st.markdown(f"""
            <div style="padding: 15px; margin: 10px 0; background: #f8fafc; border-radius: 8px; border-left: 4px solid #667eea;">
                <p style="margin: 0; font-weight: 500; color: #374151;">❓ {faq}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Contact Support Section with better layout
        st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 15px; margin-top: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h3 style="font-weight: 600; text-align: center; color: #1E293B; margin-bottom: 25px;">Contact Support</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Support options in centered columns
        support_col1, support_col2 = st.columns(2)
        
        with support_col1:
            st.markdown("""
            <div style="background: #f0f9ff; padding: 25px; border-radius: 12px; text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">📧</div>
                <h5 style="color: #1E293B; margin-bottom: 10px;">Email Support</h5>
                <p style="color: #64748B; margin-bottom: 15px;">Get assistance via email</p>
                <a href="mailto:support@innomatics.in" style="color: #667eea; font-weight: 600; text-decoration: none;">support@innomatics.in</a>
            </div>
            """, unsafe_allow_html=True)
        
        with support_col2:
            st.markdown("""
            <div style="background: #f0fdf4; padding: 25px; border-radius: 12px; text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">💬</div>
                <h5 style="color: #1E293B; margin-bottom: 10px;">Live Chat</h5>
                <p style="color: #64748B; margin-bottom: 15px;">Chat with a support agent now</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Center the button
            if st.button("🚀 Start Chat", type="primary", use_container_width=True):
                st.success("Chat feature coming soon!")

    # Additional help resources section
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Full width section for additional resources
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 15px; margin-top: 30px; text-align: center;">
        <h3 style="color: white; margin-bottom: 20px;">Need More Help?</h3>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 25px; font-size: 1.1rem;">
            Our comprehensive documentation and video tutorials can help you get the most out of the AI Resume Analyzer.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.2); padding: 15px 25px; border-radius: 8px; color: white;">
                📚 Documentation
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 15px 25px; border-radius: 8px; color: white;">
                🎥 Video Tutorials
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 15px 25px; border-radius: 8px; color: white;">
                🤝 Community Forum
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def candidate_dashboard_page():
    render_header("Dashboard", "Student View", "https://i.pravatar.cc/40?u=candidate")
    st.markdown("""
        <div style="background-color: white; padding: 24px; border-radius: 12px; margin-top: 24px;">
            <h3 style="font-weight: 600;">Welcome, Student!</h3>
            <p>Ready to land your dream job? Browse open positions and get instant AI feedback on your resume to improve your chances.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Add proper Streamlit button for navigation
    if st.button(" Browse Jobs", key="browse_jobs_btn", type="primary", use_container_width=True):
        st.session_state.page = "job_postings"
        st.rerun()
    
    st.markdown('<h3 style="font-weight: 600; margin-top: 24px;">My Applications</h3>', unsafe_allow_html=True)
    st.markdown('<p>No applications submitted yet. Browse job postings to apply for positions.</p>', unsafe_allow_html=True)

def candidate_job_postings_page():
    render_header("Job Postings", "Student View", "https://i.pravatar.cc/40?u=candidate")
    
    st.markdown("### Available Positions")
    st.markdown("Browse and apply to open positions that match your skills and interests.")
    
    # Create a grid layout for job cards
    cols = st.columns(2)  # 2 columns for better layout
    
    for i, (job_title, data) in enumerate(st.session_state.jobs_data.items()):
        with cols[i % 2]:  # Alternate between columns
            with st.container():
                # Create a styled job card
                st.markdown(f"""
                <div class="job-posting-card" style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 16px;">
                    <h3 style="font-weight:600; color:#1E293B; margin-top:0; margin-bottom: 8px;">{job_title}</h3>
                    <p style="font-size:0.875rem; color:#64748B; margin:0 0 12px;">📍 {data['department']} Department</p>
                    <p style="color: #475569; font-size: 0.9rem; line-height: 1.4; margin-bottom: 16px;">{data['description'][:120]}...</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div>
                            <p style="font-size:0.875rem; font-weight:600; color:#1E293B; margin:0;">👥 {data['applicants']} applicants</p>
                        </div>
                        <div>
                            <p style="font-size:0.875rem; font-weight:600; color:#10B981; margin:0;">📊 Avg: {data['avg_score']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add clickable buttons for each job using a single row
                if st.button(f"View Details • Quick Apply", key=f"candidate_job_action_{i}", type="primary", use_container_width=True):
                    job_details_modal(job_title, data)
                    st.success(f"Applied to {job_title}!")

def job_applicants_page():
    """Page showing applicants for a specific job role"""
    job_title = st.session_state.selected_job
    if not job_title:
        st.error("No job selected")
        return
    
    # Header with back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to All Jobs", key="back_to_jobs"):
            st.session_state.page = "job_postings"
            st.session_state.selected_job = None
            st.rerun()
    
    with col2:
        st.markdown(f'<h2 style="margin: 0;">Applicants for {job_title}</h2>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filter candidates by job role from backend
    api_service = get_api_service()
    backend_candidates = api_service.get_candidates()
    
    if "error" in backend_candidates:
        st.error(f"Error loading candidates: {backend_candidates['error']}")
        return
    
    candidates = backend_candidates if isinstance(backend_candidates, list) else backend_candidates.get("candidates", [])
    job_candidates = [cand for cand in candidates if cand.get('job', {}).get('job_title') == job_title]
    
    if not job_candidates:
        st.info(f"No applicants found for {job_title}")
        return
    
    # Table headers
    header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([2, 2, 1, 2, 1])
    header_col1.markdown("**Candidate**")
    header_col2.markdown("**Job Role**")
    header_col3.markdown("**Score**")
    header_col4.markdown("**Verdict**")
    header_col5.markdown("**Action**")
    
    st.markdown("---")
    
    # Display candidates
    for i, cand in enumerate(job_candidates):
        row_col1, row_col2, row_col3, row_col4, row_col5 = st.columns([2, 2, 1, 2, 1])
        
        # Extract data from backend format
        resume_filename = cand.get('resume_filename', '')
        if resume_filename:
            # Extract name from filename like "john_doe_resume.pdf" -> "John Doe"
            candidate_name = resume_filename.replace('_resume.pdf', '').replace('_', ' ').replace('.pdf', '').title()
            if not candidate_name or candidate_name == '.Pdf':
                candidate_name = f"Candidate {cand.get('id', 'Unknown')}"
        else:
            candidate_name = f"Candidate {cand.get('id', 'Unknown')}"
        
        job_role = cand.get('job', {}).get('job_title', 'Unknown Position')
        score = cand.get('relevance_score', 0)
        verdict = cand.get('verdict', 'Medium')
        
        # Map backend verdict to expected format
        if 'High' in verdict:
            verdict = 'High'
        elif 'Medium' in verdict:
            verdict = 'Medium'
        elif 'Low' in verdict:
            verdict = 'Low'
        else:
            verdict = 'Medium'
        
        with row_col1:
            st.markdown(f"**{candidate_name}**")
        
        with row_col2:
            st.markdown(job_role)
        
        with row_col3:
            # Show score as a circle like in the screenshot
            score_color = get_score_color(score)
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center;">
                <div style="width: 50px; height: 50px; border-radius: 50%; border: 4px solid {score_color}; display: flex; align-items: center; justify-content: center; font-weight: bold; color: {score_color};">
                    {score}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with row_col4:
            st.markdown(get_tag_html(score), unsafe_allow_html=True)
        
        with row_col5:
            if st.button("View Details", key=f"applicant_details_{i}", type="secondary"):
                # Create candidate object in expected format for modal
                candidate_obj = {
                    'id': cand.get('id'),
                    'name': candidate_name,
                    'job_role': job_role,
                    'score': score,
                    'verdict': verdict,
                    'missing_skills': cand.get('missing_skills', []),
                    'feedback': cand.get('feedback', ''),
                    'resume_file': cand.get('resume_filename', 'resume.pdf'),
                    'application_date': cand.get('application_date'),
                    'application_id': cand.get('id')
                }
                view_details_modal(candidate_obj)
        
        # Add separator between rows
        if i < len(job_candidates) - 1:
            st.markdown("---")


# --- Main App Logic ---
if st.session_state.role is None:
    # Home page - no sidebar, full width content
    render_landing_page()
else:
    # Render sidebar
    render_sidebar()
    
    # Main content without container columns - this allows proper centering
    if st.session_state.role == "recruiter":
        if st.session_state.page == "dashboard":
            recruiter_dashboard_page()
        elif st.session_state.page == "job_postings":
            recruiter_job_postings_page()
        elif st.session_state.page == "job_applicants":
            job_applicants_page()
        elif st.session_state.page == "candidates":
            recruiter_candidates_page()
        elif st.session_state.page == "reports":
            recruiter_reports_page()
        
        elif st.session_state.page == "help_support":
            help_and_support_page()
        else:
            recruiter_dashboard_page()
    else:
        if st.session_state.page == "dashboard":
            candidate_dashboard_page()
        elif st.session_state.page == "job_postings":
            candidate_job_postings_page()
       
        elif st.session_state.page == "help_support":
            help_and_support_page()
        else:
            candidate_dashboard_page()

    # Handle application feedback modal (when coming from job application)
    if st.session_state.get('show_application_feedback', False):
        # Use real backend data if available, otherwise use mock data
        backend_result = st.session_state.get('feedback_backend_result')
        
        if backend_result and not backend_result.get('error'):
            # Use real backend feedback data
            feedback_app_data = {
                'job_title': st.session_state.get('feedback_job_title', 'Unknown'),
                'score': backend_result.get('relevance_score', 75),
                'verdict': backend_result.get('verdict', 'Medium'),
                'missing_skills': backend_result.get('missing_skills', []),
                'feedback': backend_result.get('feedback', 'Application processed successfully.'),
                'application_id': backend_result.get('id'),
                'resume_filename': backend_result.get('resume_filename', 'resume.pdf'),
                'application_date': backend_result.get('application_date')
            }
        else:
            # Fallback to mock data if backend failed or not available
            feedback_app_data = {
                'job_title': st.session_state.get('feedback_job_title', 'Unknown'),
                'score': 82,
                'summary': 'A promising candidate with a good foundation in frontend technologies.',
                'focus_areas': ['Next.js', 'Storybook'],
                'suggestions': 'Your React skills are strong. To better match the role, gain some experience with server-side rendering using Next.js and documenting components with Storybook.'
            }
        
        # Reset the flag and show the modal
        st.session_state.show_application_feedback = False
        application_feedback_modal(feedback_app_data)