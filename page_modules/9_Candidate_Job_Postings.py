# File: pages/9_Candidate_Job_Postings.py

import streamlit as st
import sys
import os

# Add the parent directory to the path to import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.api_service import get_api_service
except ImportError:
    # Fallback if running standalone
    def get_api_service():
        class MockAPIService:
            def get_jobs(self):
                return {"error": "API service not available in standalone mode"}
        return MockAPIService()

# Placeholder for the render_header function, which would be in your main app.
def render_header(title, subtitle, analyze_button, avatar_url):
    st.title(title)
    st.subheader(subtitle)
    # The real implementation of this function is more complex but this works for running the page.

def candidate_job_postings_page():
    render_header("Job Postings", "Student View", False, "https://i.pravatar.cc/40?u=candidate")
    
    # Get jobs from backend
    api_service = get_api_service()
    backend_jobs = api_service.get_jobs()
    
    if "error" in backend_jobs:
        st.error(f"Could not load job postings: {backend_jobs.get('error', 'Unknown error')}")
        st.info("Please check your backend connection in the main application.")
        return
    
    # Process jobs data
    jobs = backend_jobs if isinstance(backend_jobs, list) else backend_jobs.get("jobs", [])
    
    if not jobs:
        st.info("No job postings available at the moment.")
        return
    
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    for job in jobs:
        job_title = job.get('job_title', 'Unknown Job')
        department = job.get('department', 'Unknown Department')
        description = job.get('description', 'No description available.')
        
        # Get job stats if available
        applicants_count = job.get('applicants', 0)
        avg_score = job.get('avg_score', 0)
        
        st.markdown(f"""
            <div class="job-posting-card">
                <h3 style="font-weight:600; color:#1E293B; margin-top:0;">{job_title}</h3>
                <p style="font-size:0.875rem; color:#64748B; margin:0 0 16px;">{department}</p>
                <p>{description}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px;">
                    <div style="font-size: 0.75rem; color: #64748B;">
                        {applicants_count} applicants • Avg Score: {avg_score}
                    </div>
                    <a href="#" style="color: #4338CA; font-weight: 600;">View & Apply →</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Call the page function to render the content.
candidate_job_postings_page()