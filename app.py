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
    st.session_state.backend_url = "https://innomaticshackathonbackend-production.up.railway.app"  # Default backend URL
if "use_backend" not in st.session_state:
    st.session_state.use_backend = True  # Toggle between backend and mock data
if "jobs_data" not in st.session_state:
    st.session_state.jobs_data = {}  # Initialize jobs data

# Clear any cached API service with old URL
if hasattr(st, '_legacy_caching') or hasattr(st.cache_data, 'clear'):
    try:
        from services.api_service import get_api_service
        get_api_service.clear()  # Clear cached API service
    except:
        pass  # Ignore if cache clearing fails

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
        # Default fallback for any filename that doesn't match patterns
        return {
            "job_title": "Software Engineer",
            "department": "Engineering",
            "description": "We are looking for a talented Software Engineer to help build innovative solutions and contribute to our growing platform.",
            "requirements": "• Bachelor's degree in Computer Science or related field\n• 2+ years of software development experience\n• Strong programming fundamentals\n• Collaborative team player"
        }


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
            return '<span>High Fit</span>'
        elif verdict_lower in ['medium', 'moderate', 'average']:
            return '<span>Medium Fit</span>'
        elif st.session_state.role == "candidate":  # low, poor, weak, etc.
            return '<span>Low Fit</span>'
    
    # Fallback to score-based calculation
    if score >= 80: return '<span>High Fit</span>'
    if score >= 60: return '<span>Medium Fit</span>'
    return '<span>Low Fit</span>'

def render_score_circle(score, color=None):
    st.metric(label="Relevance Score", value=f"{score}%")


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
            elif st.session_state.role == "candidate":
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
    st.subheader(candidate_data['name'])
    st.write(candidate_data['job_role'])
    st.markdown(get_tag_html(candidate_data['score'], candidate_data.get('verdict')), unsafe_allow_html=True)
    
    if is_backend_data:
        # Enhanced tabs for backend data
        tabs = st.tabs(["Overview", "Missing Skills", "AI Feedback", "Application Details"])
        
        with tabs[0]:
            # Layout with score circle and AI summary side by side
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Score circle
                render_score_circle(candidate_data['score'])
                st.write(f"{candidate_data.get('verdict', 'Medium')} Fit")
            
            with col2:
                st.subheader("AI Assessment")
                feedback = candidate_data.get('feedback', 'Application processed successfully.')
                st.write(feedback)
                
                # Quick stats
                st.subheader("Quick Stats")
                col2a, col2b = st.columns(2)
                with col2a:
                    missing_count = len(candidate_data.get('missing_skills', []))
                    st.metric("Missing Skills", missing_count)
                with col2b:
                    resume_file = candidate_data.get('resume_file', 'N/A')
                    st.write(f"**Resume:** {resume_file}")
        
        with tabs[1]:
            st.subheader("Missing Skills Analysis")
            missing_skills = candidate_data.get('missing_skills', [])
            if missing_skills:
                for skill in missing_skills:
                    st.write(f"❌ {skill}")
                
                st.subheader("Recommendations")
                st.info(f"Consider developing skills in: {', '.join(missing_skills[:3])}.")
            elif st.session_state.role == "candidate":
                st.success("No missing skills identified! This candidate has excellent skill alignment.")
        
        with tabs[2]:
            st.subheader("Detailed AI Feedback")
            feedback = candidate_data.get('feedback', 'Application processed successfully.')
            st.write(feedback)
            
            # Verdict-based additional insights
            verdict = candidate_data.get('verdict', 'Medium').lower()
            if verdict == 'high':
                st.success("This candidate is highly recommended for this position!")
            elif verdict == 'medium':
                st.info("This candidate shows potential with some areas for improvement.")
            elif st.session_state.role == "candidate":
                st.warning("This candidate may need significant development to fit this role.")
        
        with tabs[3]:
            st.subheader("Application Information")
            
            col3a, col3b = st.columns(2)
            with col3a:
                if candidate_data.get('application_id'):
                    st.write(f"**Application ID:** {candidate_data['application_id']}")
                if candidate_data.get('resume_file'):
                    st.write(f"**Resume File:** {candidate_data['resume_file']}")
                st.write(f"**Job Applied For:** {candidate_data['job_role']}")
                
            with col3b:
                if candidate_data.get('application_date'):
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(candidate_data['application_date'].replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
                        st.write(f"**Applied:** {formatted_date}")
                    except:
                        st.write(f"**Applied:** {candidate_data['application_date']}")
                
                st.write(f"**Relevance Score:** {candidate_data['score']}/100")
                st.write(f"**Final Verdict:** {candidate_data.get('verdict', 'Medium')}")
    
    elif st.session_state.role == "candidate":
        # Original tabs for legacy data
        tabs = st.tabs(["Overview", "AI Feedback", "Comparison"])
        
        with tabs[0]:
            # Layout matching the screenshot with score circle and AI summary side by side
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Score circle that matches the screenshot
                render_score_circle(candidate_data['score'])
                st.write("Relevance Score")
            
            with col2:
                st.subheader("AI Summary")
                st.write(candidate_data.get("summary", "Candidate assessment completed."))
                
                if candidate_data.get("gaps"):
                    st.subheader("Skill Gaps Identified")
                    for gap in candidate_data["gaps"]:
                        st.write(f'❌ {gap}')
        
        with tabs[1]:
            st.subheader("Highlighted Gaps")
            if candidate_data.get("gaps"):
                for gap in candidate_data["gaps"]:
                    st.write(f"❌ {gap}")
            elif st.session_state.role == "candidate":
                st.success("No significant gaps identified!")
                
            st.markdown("---")
            st.subheader("💡 Improvement Feedback")
            st.info(candidate_data.get("suggestions", "Continue developing relevant skills and experience."))

        with tabs[2]:
            st.subheader("Score Comparison")
            
            # Get the job data for comparison
            job_data = JOBS_DATA.get(candidate_data['job_role'], {})
            avg_score = job_data.get('avg_score', 0)
            
            # Candidate score bar
            st.write(f"**Candidate Score**")
            st.progress(candidate_data['score'] / 100)
            
            # Average score bar  
            st.write(f"**Average for Role**")
            st.progress(avg_score / 100)
            
            st.markdown("---")
            st.write(f"This chart compares {candidate_data['name']}'s relevance score to the average score of all candidates who applied for the {candidate_data['job_role']} position.")
            
            if candidate_data['score'] > avg_score:
                st.success(f"This candidate scored {candidate_data['score'] - avg_score} points above average!")
            elif candidate_data['score'] < avg_score:
                st.warning(f"This candidate scored {avg_score - candidate_data['score']} points below average.")
            elif st.session_state.role == "candidate":
                st.info("This candidate scored exactly at the average level.")
    
    with tabs[1]:
        st.subheader("Highlighted Gaps")
        if candidate_data.get("gaps"):
            for gap in candidate_data["gaps"]:
                st.write(f"❌ {gap}")
        elif st.session_state.role == "candidate":
            st.success("No significant gaps identified!")
            
        st.markdown("---")
        st.subheader("💡 Improvement Feedback")
        st.info(candidate_data["suggestions"])

    with tabs[2]:
        st.subheader("Score Comparison")
        
        # Get the job data for comparison
        job_data = JOBS_DATA.get(candidate_data['job_role'], {})
        avg_score = job_data.get('avg_score', 0)
        
        # Candidate score bar
        st.write(f"**Candidate Score**")
        st.progress(candidate_data['score'] / 100)
        
        # Average score bar  
        st.write(f"**Average for Role**")
        st.progress(avg_score / 100)
        
        st.markdown("---")
        st.write(f"This chart compares {candidate_data['name']}'s relevance score to the average score of all candidates who applied for the {candidate_data['job_role']} position.")
        
        if candidate_data['score'] > avg_score:
            st.success(f"This candidate scores {candidate_data['score'] - avg_score} points above average!")
        elif candidate_data['score'] < avg_score:
            st.warning(f"This candidate scores {avg_score - candidate_data['score']} points below average.")
        elif st.session_state.role == "candidate":
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
        st.title(job_title)
        st.subheader(job_data['department'])
        
        # Job Description Section
        st.subheader("Job Description")
        st.write(job_data['description'])
        
        # Requirements Section
        st.subheader("Requirements")
        
        for i, requirement in enumerate(job_data['requirements']):
            st.write(f"• {requirement}")
    
    with col_apply:
        # Application section with better styling
        st.markdown("### Upload Your Resume")
        st.write("Share your resume to get personalized feedback")
        
        # Enhanced file upload section
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'docx'],
            key=f"resume_upload_{job_title}",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.success("Resume uploaded successfully!")
        elif st.session_state.role == "candidate":
            st.warning("Please upload a file")
        
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
                elif st.session_state.role == "candidate":
                    success_message += " You'll receive feedback within 24 hours."
                    
                st.success(success_message)
                
                # Close current modal and show feedback
                st.rerun()
            elif st.session_state.role == "candidate":
                st.error("Please upload your resume first!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced statistics section
        st.subheader("Application Stats")
        st.write(f"Total Applications: {job_data['applicants']}")
        st.write(f"Average Score: {job_data['avg_score']}")

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
                elif st.session_state.role == "candidate":
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
            elif st.session_state.role == "candidate":
                st.error(" Please fill in all required fields")

@st.dialog("Application Feedback") 
def application_feedback_modal(app_data):
    # Header with job title
    st.subheader("Application Feedback")
    st.write(f"For: {app_data['job_title']}")
    
    # Check if we have backend data or fallback data
    is_backend_data = 'verdict' in app_data and 'feedback' in app_data
    
    if is_backend_data:
        # Create tabs for backend data
        tab1, tab2 = st.tabs(["Overview", "Missing Skills"])
        
        with tab1:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                render_score_circle(app_data['score'])
                verdict = app_data.get('verdict', 'Medium')
                st.write(f"Fit: {verdict}")
            
            with col2:
                st.subheader('AI Feedback')
                feedback_text = app_data.get('feedback', 'Application processed successfully.')
                st.write(feedback_text)
                
                # Show application details if available
                if app_data.get('application_id'):
                    st.subheader('Application Details')
                    col2a, col2b = st.columns(2)
                    with col2a:
                        st.write(f"**Application ID:** {app_data['application_id']}")
                        if app_data.get('resume_filename'):
                            st.write(f"**Resume File:** {app_data['resume_filename']}")
                    with col2b:
                        if app_data.get('application_date'):
                            from datetime import datetime
                            try:
                                # Parse the datetime string and format it nicely
                                dt = datetime.fromisoformat(app_data['application_date'].replace('Z', '+00:00'))
                                formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
                                st.write(f"**Applied:** {formatted_date}")
                            except:
                                st.write(f"**Applied:** {app_data['application_date']}")
        
        with tab2:
            st.subheader('Missing Skills')
            missing_skills = app_data.get('missing_skills', [])
            if missing_skills:
                for skill in missing_skills:
                    st.write(f"❌ {skill}")
            elif st.session_state.role == "candidate":
                st.success('✓ No missing skills identified!')
            
            st.subheader('Recommendations')
            if missing_skills:
                recommendations = f"Consider developing skills in: {', '.join(missing_skills[:3])}. These areas would significantly improve your match for this role."
            elif st.session_state.role == "candidate":
                recommendations = "Great job! Your skills align well with the job requirements. Continue to strengthen your existing expertise."
            
            st.info(recommendations)
    
    elif st.session_state.role == "candidate":
        # Use original format for fallback data
        tab1, tab2 = st.tabs([" Overview", " Improvement Plan"])
        
        with tab1:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                render_score_circle(app_data['score'])
                st.write(f"Fit: {get_tag_html(app_data['score'])}")
            
            with col2:
                st.subheader('AI Summary')
                st.write(app_data.get("summary", "Application processed successfully."))
        
        with tab2:
            st.subheader('Focus Areas for Your Resume')
            for area in app_data.get("focus_areas", []):
                st.write(f"❌ {area}")
            
            st.subheader('AI-Powered Suggestions')
            suggestions = app_data.get("suggestions", "Continue to develop your skills and experience.")
            st.info(suggestions)


# --- MAIN APP LAYOUTS ---
def render_landing_page():
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    
    # Display your logo using Streamlit's image function
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
    with col_logo2:
        st.image("logo.png", width=150)
    
    st.header("Welcome to the AI Resume Analyzer")
    st.write("Please select your role to get started.")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("---")
        
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
    with st.sidebar:
        # Center the logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=80)
        
        st.write(f"Role: **{st.session_state.role.capitalize() if st.session_state.role else 'Guest'}**")

    # Navigation items with custom styling
    if st.session_state.role == "recruiter":
        nav_items = [
            ("Dashboard", "dashboard"), 
            ("Job Postings", "job_postings"), 
            ("Candidates", "candidates"),
            ("Reports", "reports"), 
        ]
    elif st.session_state.role == "candidate":
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Job Postings", "job_postings"),
        ]
    else:
        # Guest role - no navigation items
        nav_items = []

        
    for name, page in nav_items:
        if st.sidebar.button(name, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()

    if st.sidebar.button("Help & Support", key="nav_help_support", use_container_width=True):
        st.session_state.page = "help_support"
        st.rerun()
    
    st.sidebar.markdown("---")
    
    
def render_header(title, subtitle, avatar_url=None):
    st.header(title)
    st.write(subtitle)


# --- PAGES ---
def recruiter_dashboard_page():
    try:
        render_header("Dashboard", "Recruiter View", "https://i.pravatar.cc/40?u=recruiter")
        
        st.subheader("📊 Dashboard Overview")
        
        # Get metrics from backend
        api_service = get_api_service()
        backend_metrics = api_service.get_metrics()
        
        if "error" in backend_metrics:
            st.error(f"Could not load dashboard metrics: {backend_metrics.get('error', 'Unknown error')}")
            st.info("Displaying demo data while backend is unavailable.")
            
            # Use fallback demo data
            metrics_data = {
                "Total Candidates": 24,
                "Open Positions": 3,
                "High-Fit Candidates": 8,
                "Avg. Score": 76
            }
        else:
            # Use actual backend data
            metrics_data = {
                "Total Candidates": backend_metrics.get("total_applications", 0),
                "Open Positions": backend_metrics.get("open_positions", 0),
                "High-Fit Candidates": backend_metrics.get("high_fit_candidates", 0),
                "Avg. Score": int(backend_metrics.get("avg_score", 0))
            }
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        # Always provide fallback content
        st.subheader("📊 Dashboard Overview")
        st.info("Using demo data due to loading error.")
        metrics_data = {
            "Total Candidates": 10,
            "Open Positions": 2,
            "High-Fit Candidates": 4,
            "Avg. Score": 65
        }
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Candidates", metrics_data["Total Candidates"])
    with col2: st.metric("Open Positions", metrics_data["Open Positions"])
    with col3: st.metric("High-Fit Candidates", metrics_data["High-Fit Candidates"])
    with col4: st.metric("Avg. Score", metrics_data["Avg. Score"])

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Recent Candidates")
        
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
                
                st.write(f"**{candidate_name}** - {job_title} ({score}%) - {get_tag_html(score)}")
                
                
    with col2:
        st.subheader("Active Job Postings")
        
        # Get jobs from backend
        backend_jobs = api_service.get_jobs()
        if "error" in backend_jobs:
            st.write("No jobs data available")
        elif st.session_state.role == "candidate":
            jobs = backend_jobs if isinstance(backend_jobs, list) else backend_jobs.get("jobs", [])
            for i, job in enumerate(jobs):
                job_title = job.get('job_title', 'Unknown Job')
                applications_count = len([app for app in candidates if app.get('job_id') == job.get('id')])
                
                if st.button(f"{job_title} ({applications_count} applicants)", key=f"dash_job_{i}", use_container_width=True):
                    st.session_state.selected_job = job_title
                    st.session_state.page = "job_applicants"
                    st.rerun()
                
def recruiter_job_postings_page():
    render_header("Job Postings", "Recruiter View", "https://i.pravatar.cc/40?u=recruiter")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Create New Job Posting", key="create_job_btn", type="primary", use_container_width=True):
            create_job_posting_modal()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Active Job Postings")
    
    cols = st.columns(2)
    
    for i, (job_title, data) in enumerate(st.session_state.jobs_data.items()):
        with cols[i % 2]:
            st.subheader(job_title)
            st.write(f"Department: {data['department']}")
            st.write(f"Applicants: {data['applicants']}")
            st.write(f"Avg. Score: {data['avg_score']}")
            
            if st.button(f"View {job_title} Applicants", key=f"job_card_click_{i}", use_container_width=True, type="primary"):
                st.session_state.selected_job = job_title
                st.session_state.page = "job_applicants"
                st.rerun()
            
            if st.button(f"View Job Details", key=f"job_details_{i}", type="secondary", use_container_width=True):
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
    
    processed_candidates = []
    for app in candidates:
        backend_verdict = app.get('verdict', 'Medium')
        if 'High' in backend_verdict:
            verdict = 'High'
        elif 'Medium' in backend_verdict:
            verdict = 'Medium'
        elif 'Low' in backend_verdict:
            verdict = 'Low'
        else:
            verdict = 'Medium'
        
        resume_filename = app.get('resume_filename', '')
        if resume_filename:
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
    
    st.subheader("All Candidates")
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    search_term = col1.text_input("Search by name...", label_visibility="collapsed")
    
    if st.session_state.use_backend:
        if "candidates_synced" not in st.session_state:
            st.session_state.candidates_synced = False
        
        st.session_state.candidates_synced = True
    
    job_role_filter = col2.selectbox("Job Role", ["All Job Roles"] + list(set([c['job_role'] for c in processed_candidates])))
    verdict_filter = col3.selectbox("Verdict", ["All Verdicts", "High", "Medium", "Low"])
    
    filtered_candidates = processed_candidates.copy()
    
    if search_term and search_term.strip():
        filtered_candidates = [cand for cand in filtered_candidates 
                             if search_term.lower().strip() in cand['name'].lower()]
    
    if job_role_filter and job_role_filter != "All Job Roles":
        filtered_candidates = [cand for cand in filtered_candidates 
                             if cand['job_role'] == job_role_filter]
    
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
        st.write(f"**Showing {len(filtered_candidates)} candidates** | Active filters: {' • '.join(active_filters)}")
    elif st.session_state.role == "candidate":
        st.write(f"**Showing all {len(filtered_candidates)} candidates**")
    
    if filtered_candidates:
        header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([2, 2, 1, 2, 1])
        header_col1.markdown("**Candidate**")
        header_col2.markdown("**Job Role**")
        header_col3.markdown("**Score**")
        header_col4.markdown("**Verdict**")
        header_col5.markdown("**Action**")
        
        st.markdown("---")
        
        for i, cand in enumerate(filtered_candidates):
            row_col1, row_col2, row_col3, row_col4, row_col5 = st.columns([2, 2, 1, 2, 1])
            
            with row_col1:
                st.write(f"**{cand['name']}**")
            
            with row_col2:
                st.write(cand['job_role'])
            
            with row_col3:
                st.write(cand["score"])
            
            with row_col4:
                st.markdown(get_tag_html(cand['score']), unsafe_allow_html=True)
            
            with row_col5:
                if st.button("View Details", key=f"view_details_table_{i}", type="secondary"):
                    view_details_modal(cand)
            
            if i < len(filtered_candidates) - 1:
                st.markdown("---")
    elif st.session_state.role == "candidate":
        st.info("No candidates match the current filter criteria. Try adjusting your search terms.")
    

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
    
    processed_candidates = []
    for app in candidates:
        backend_verdict = app.get('verdict', 'Medium')
        if 'High' in backend_verdict:
            verdict = 'High'
        elif 'Medium' in backend_verdict:
            verdict = 'Medium'
        elif 'Low' in backend_verdict:
            verdict = 'Low'
        else:
            verdict = 'Medium'
        
        resume_filename = app.get('resume_filename', '')
        if resume_filename:
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
    st.subheader("Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Candidates Analyzed", total_candidates)
    col2.metric("Average Score", avg_score)
    col3.metric("High-Fit Candidates", high_fit_candidates)
    
    st.subheader("Candidate Verdict Distribution")
    
    high_count = len([c for c in processed_candidates if c['verdict'] == 'High'])
    medium_count = len([c for c in processed_candidates if c['verdict'] == 'Medium'])
    low_count = len([c for c in processed_candidates if c['verdict'] == 'Low'])
    
    st.write(f"High Fit: {high_count}")
    st.progress(high_count / total_candidates if total_candidates > 0 else 0)
    
    st.write(f"Medium Fit: {medium_count}")
    st.progress(medium_count / total_candidates if total_candidates > 0 else 0)
    
    st.write(f"Low Fit: {low_count}")
    st.progress(low_count / total_candidates if total_candidates > 0 else 0)
    
    st.subheader("Average Score by Job")
    
    job_scores = {}
    for job_title in st.session_state.jobs_data.keys():
        candidates_for_job = [c for c in processed_candidates if c['job_role'] == job_title]
        if candidates_for_job:
            avg = round(sum(c['score'] for c in candidates_for_job) / len(candidates_for_job))
            job_scores[job_title] = avg
    
    for job_title, score in job_scores.items():
        st.write(f"**{job_title}**")
        st.progress(score / 100.0)
    
    st.subheader("Performance by Job")
    
    st.write("This table provides detailed performance metrics for each job posting.")
    
    job_data_list = []
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
        
        job_data_list.append({
            "Job Title": job_title,
            "Applicants": applicant_count,
            "Avg. Score": avg_score,
            "High Fit": high_fit,
            "Medium Fit": medium_fit,
            "Low Fit": low_fit
        })
    
    st.table(job_data_list)


def help_and_support_page():
    render_header("Help & Support", (st.session_state.role.capitalize() if st.session_state.role else "Guest") + " View", "https://i.pravatar.cc/40?u=recruiter" if st.session_state.role == 'recruiter' else "https://i.pravatar.cc/40?u=candidate")

    st.subheader("Frequently Asked Questions")
    
    faqs = [
        "How does the AI analysis work?", 
        "What file types are supported for upload?", 
        "How accurate is the AI feedback?", 
        "Can I analyze multiple resumes at once?", 
        "Who can see my analysis results?"
    ]
    
    for faq in faqs:
        st.write(f"❓ {faq}")
    
    st.subheader("Contact Support")
    
    support_col1, support_col2 = st.columns(2)
    
    with support_col1:
        st.write("Email Support")
        st.write("Get assistance via email")
        st.write("support@innomatics.in")
    
    with support_col2:
        st.write("Live Chat")
        st.write("Chat with a support agent now")
        
        if st.button("🚀 Start Chat", type="primary", use_container_width=True):
            st.success("Chat feature coming soon!")
    
    st.markdown("---")
    st.subheader("Need More Help?")
    st.write("Our comprehensive documentation and video tutorials can help you get the most out of the AI Resume Analyzer.")
    
    col_docs, col_tutorials, col_forum = st.columns(3)
    with col_docs:
        st.button("📚 Documentation", use_container_width=True)
    with col_tutorials:
        st.button("🎥 Video Tutorials", use_container_width=True)
    with col_forum:
        st.button("🤝 Community Forum", use_container_width=True)


def candidate_dashboard_page():
    render_header("Dashboard", "Student View", "https://i.pravatar.cc/40?u=candidate")
    st.subheader("Welcome, Student!")
    st.write("Ready to land your dream job? Browse open positions and get instant AI feedback on your resume to improve your chances.")
    
    if st.button(" Browse Jobs", key="browse_jobs_btn", type="primary", use_container_width=True):
        st.session_state.page = "job_postings"
        st.rerun()
    
    st.subheader("My Applications")
    st.write("No applications submitted yet. Browse job postings to apply for positions.")

def candidate_job_postings_page():
    render_header("Job Postings", "Student View", "https://i.pravatar.cc/40?u=candidate")
    
    st.subheader("Available Positions")
    st.write("Browse and apply to open positions that match your skills and interests.")
    
    cols = st.columns(2)
    
    for i, (job_title, data) in enumerate(st.session_state.jobs_data.items()):
        with cols[i % 2]:
            st.subheader(job_title)
            st.write(f"Department: {data['department']}")
            st.write(f"Description: {data['description'][:120]}...")
            st.write(f"Applicants: {data['applicants']}")
            st.write(f"Avg. Score: {data['avg_score']}")
            
            if st.button(f"View Details • Quick Apply", key=f"candidate_job_action_{i}", type="primary", use_container_width=True):
                job_details_modal(job_title, data)
                st.success(f"Applied to {job_title}!")

def job_applicants_page():
    """Page showing applicants for a specific job role"""
    job_title = st.session_state.selected_job
    if not job_title:
        st.error("No job selected")
        return
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to All Jobs", key="back_to_jobs"):
            st.session_state.page = "job_postings"
            st.session_state.selected_job = None
            st.rerun()
    
    with col2:
        st.header(f"Applicants for {job_title}")
    
    st.markdown("---")
    
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
    
    header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([2, 2, 1, 2, 1])
    header_col1.markdown("**Candidate**")
    header_col2.markdown("**Job Role**")
    header_col3.markdown("**Score**")
    header_col4.markdown("**Verdict**")
    header_col5.markdown("**Action**")
    
    st.markdown("---")
    
    for i, cand in enumerate(job_candidates):
        row_col1, row_col2, row_col3, row_col4, row_col5 = st.columns([2, 2, 1, 2, 1])
        
        resume_filename = cand.get('resume_filename', '')
        if resume_filename:
            candidate_name = resume_filename.replace('_resume.pdf', '').replace('_', ' ').replace('.pdf', '').title()
            if not candidate_name or candidate_name == '.Pdf':
                candidate_name = f"Candidate {cand.get('id', 'Unknown')}"
        elif st.session_state.role == "candidate":
            candidate_name = f"Candidate {cand.get('id', 'Unknown')}"
        
        job_role = cand.get('job', {}).get('job_title', 'Unknown Position')
        score = cand.get('relevance_score', 0)
        verdict = cand.get('verdict', 'Medium')
        
        if 'High' in verdict:
            verdict = 'High'
        elif 'Medium' in verdict:
            verdict = 'Medium'
        elif 'Low' in verdict:
            verdict = 'Low'
        elif st.session_state.role == "candidate":
            verdict = 'Medium'
        
        with row_col1:
            st.write(f"**{candidate_name}**")
        
        with row_col2:
            st.write(job_role)
        
        with row_col3:
            st.write(score)
        
        with row_col4:
            st.markdown(get_tag_html(score), unsafe_allow_html=True)
        
        with row_col5:
            if st.button("View Details", key=f"applicant_details_{i}", type="secondary"):
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
        
        if i < len(job_candidates) - 1:
            st.markdown("---")


# --- Main App Logic ---
try:
    if "role" not in st.session_state or st.session_state.role is None:
        render_sidebar()
        render_landing_page()
    else:
        render_sidebar()

        try:
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
                elif st.session_state.role == "candidate":
                    recruiter_dashboard_page()
            elif st.session_state.role == "candidate":
                if st.session_state.page == "dashboard":
                    candidate_dashboard_page()
                elif st.session_state.page == "job_postings":
                    candidate_job_postings_page()
                elif st.session_state.page == "help_support":
                    help_and_support_page()
                elif st.session_state.role == "candidate":
                    candidate_dashboard_page()
        except Exception as e:
            st.error(f"Error loading page content: {str(e)}")
            st.info("Please try refreshing the page or contact support if the issue persists.")
            st.markdown("### Welcome to AI Resume Analyzer")
            st.markdown("There was an error loading the page content. Please try:")
            st.markdown("- Refreshing the page")
            st.markdown("- Clearing your browser cache")
            st.markdown("- Using the navigation menu")

except Exception as e:
    st.error(f"Critical error in main app logic: {str(e)}")
    st.info("Please refresh the page to continue.")
    st.markdown("### AI Resume Analyzer")
    st.markdown("Please refresh the page to start using the application.")

    if st.session_state.get('show_application_feedback', False):
        backend_result = st.session_state.get('feedback_backend_result')
        
        if backend_result and not backend_result.get('error'):
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
        elif st.session_state.role == "candidate":
            feedback_app_data = {
                'job_title': st.session_state.get('feedback_job_title', 'Unknown'),
                'score': 82,
                'summary': 'A promising candidate with a good foundation in frontend technologies.',
                'focus_areas': ['Next.js', 'Storybook'],
                'suggestions': 'Your React skills are strong. To better match the role, gain some experience with server-side rendering using Next.js and documenting components with Storybook.'
            }
        
        st.session_state.show_application_feedback = False
        application_feedback_modal(feedback_app_data)