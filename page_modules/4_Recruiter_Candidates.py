# File: pages/4_Recruiter_Candidates.py
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
            def get_candidates(self):
                return {"error": "API service not available in standalone mode"}
        return MockAPIService()


# Placeholder for the render_header function, which would be in your main app.
def render_header(title, subtitle, analyze_button, avatar_url):
    st.title(title)
    st.subheader(subtitle)
    # The real implementation of this function is more complex but this works for running the page.

def get_tag_html(score):
    if score >= 80: return '<span class="tag-high">High Fit</span>'
    if score >= 60: return '<span class="tag-medium">Medium Fit</span>'
    return '<span class="tag-low">Low Fit</span>'

def render_score_circle(score, color=None):
    if color is None: color = '#3498db'
    st.write(f"Score: {score}") # Placeholder for the visual circle

def recruiter_candidates_page():
    render_header("Candidates", "Recruiter View", True, "https://i.pravatar.cc/40?u=recruiter")
    
    # Get candidates from backend
    api_service = get_api_service()
    backend_candidates = api_service.get_candidates()
    
    if "error" in backend_candidates:
        st.error(f"Could not load candidates: {backend_candidates.get('error', 'Unknown error')}")
        st.info("Please check your backend connection in the main application.")
        return
    
    # Process candidates data
    candidates = backend_candidates if isinstance(backend_candidates, list) else backend_candidates.get("candidates", [])
    
    # Transform to consistent format
    processed_candidates = []
    job_roles = set()
    for app in candidates:
        # Extract candidate name from resume filename
        resume_filename = app.get('resume_filename', '')
        if resume_filename:
            candidate_name = resume_filename.replace('_resume.pdf', '').replace('_', ' ').replace('.pdf', '').title()
            if not candidate_name or candidate_name == '.Pdf':
                candidate_name = f"Candidate {app.get('id', 'Unknown')}"
        else:
            candidate_name = f"Candidate {app.get('id', 'Unknown')}"
        
        job_role = app.get('job', {}).get('job_title', 'Unknown Position')
        job_roles.add(job_role)
        
        processed_candidates.append({
            'name': candidate_name,
            'job_role': job_role,
            'score': app.get('relevance_score', 0),
            'verdict': app.get('verdict', 'Medium'),
            'id': app.get('id')
        })
    
    st.markdown('<div class="table-container" style="margin-top: 24px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size:1.25rem; font-weight:700; color:#1E293B; margin-bottom:16px;">All Candidates</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    search_term = col1.text_input("Search by name...", label_visibility="collapsed")
    job_role_filter = col2.selectbox("Job Role", ["All Job Roles"] + sorted(list(job_roles)))
    verdict_filter = col3.selectbox("Verdict", ["All Verdicts", "High", "Medium", "Low"])
    
    # Apply filters
    filtered_candidates = processed_candidates.copy()
    
    if search_term and search_term.strip():
        filtered_candidates = [c for c in filtered_candidates if search_term.lower() in c['name'].lower()]
    
    if job_role_filter and job_role_filter != "All Job Roles":
        filtered_candidates = [c for c in filtered_candidates if c['job_role'] == job_role_filter]
    
    if verdict_filter and verdict_filter != "All Verdicts":
        filtered_candidates = [c for c in filtered_candidates if c['verdict'] == verdict_filter]
    
    if not filtered_candidates:
        st.info("No candidates found matching the selected filters.")
        return
    
    st.markdown('<div style="overflow-x:auto;">', unsafe_allow_html=True)
    st.markdown('<table class="table"><thead><tr><th>Candidate</th><th>Job Role</th><th style="text-align: center;">Score</th><th>Verdict</th><th>Action</th></tr></thead><tbody>', unsafe_allow_html=True)
    
    for cand in filtered_candidates:
        st.markdown('<tr>', unsafe_allow_html=True)
        st.markdown(f'<td style="font-weight:600;">{cand["name"]}</td>', unsafe_allow_html=True)
        st.markdown(f'<td style="color:#475569;">{cand["job_role"]}</td>', unsafe_allow_html=True)
        st.markdown('<td>', unsafe_allow_html=True)
        render_score_circle(cand["score"])
        st.markdown('</td>', unsafe_allow_html=True)
        st.markdown(f'<td>{get_tag_html(cand["score"])}</td>', unsafe_allow_html=True)
        st.markdown(f'<td><button class="st-button" style="color:#4338CA; font-weight:600;" onclick="parent.postMessage(\'trigger-modal-recruiter\', \'*\');">View Details</button></td>', unsafe_allow_html=True)
        st.markdown('</tr>', unsafe_allow_html=True)
    
    st.markdown('</tbody></table></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Run the page function
if __name__ == "__main__":
    recruiter_candidates_page()