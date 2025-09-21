# File: pages/5_Recruiter_Reports.py
import streamlit as st
from backend_api_service import BackendAPIService

def get_api_service():
    return BackendAPIService()

# Placeholder for the render_header function, which would be in your main app.
def render_header(title, subtitle, analyze_button, avatar_url):
    st.title(title)
    st.subheader(subtitle)
    # The real implementation of this function is more complex but this works for running the page.

def recruiter_reports_page():
    render_header("Reports", "Recruiter View", False, "https://i.pravatar.cc/40?u=recruiter")
    
    # Get data from backend
    api_service = get_api_service()
    backend_candidates = api_service.get_candidates()
    backend_jobs = api_service.get_jobs()
    
    if "error" in backend_candidates or "error" in backend_jobs:
        st.error("Could not load reports data. Please check your backend connection.")
        return
    
    # Process candidates data
    candidates = backend_candidates if isinstance(backend_candidates, list) else backend_candidates.get("candidates", [])
    jobs = backend_jobs if isinstance(backend_jobs, list) else backend_jobs.get("jobs", [])
    
    # Transform candidates to consistent format
    processed_candidates = []
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
        
        processed_candidates.append({
            'name': candidate_name,
            'job_role': job_role,
            'score': app.get('relevance_score', 0),
            'verdict': app.get('verdict', 'Medium'),
            'id': app.get('id')
        })
    
    # Calculate metrics
    total_candidates = len(processed_candidates)
    avg_score = int(sum(c['score'] for c in processed_candidates) / len(processed_candidates)) if processed_candidates else 0
    high_fit_candidates = len([c for c in processed_candidates if c['verdict'] == 'High'])
    
    # Verdict distribution
    verdict_counts = {}
    for candidate in processed_candidates:
        verdict = candidate['verdict']
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
    
    # Job score analysis
    job_scores = {}
    for candidate in processed_candidates:
        job_role = candidate['job_role']
        if job_role not in job_scores:
            job_scores[job_role] = []
        job_scores[job_role].append(candidate['score'])
    
    job_avg_scores = {job: int(sum(scores) / len(scores)) for job, scores in job_scores.items() if scores}
    
    # Summary Metrics
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">Total Candidates Analyzed</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{total_candidates}</p></div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">Average Score</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{avg_score}</p></div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="summary-card"><div><p style="color:#64748B;">High-Fit Candidates</p><p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{high_fit_candidates}</p></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-grid" style="grid-template-columns: 2fr 1fr;">', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="table-container" style="margin-top: 24px;">', unsafe_allow_html=True)
        st.markdown('<h3>Candidate Verdict Distribution</h3>', unsafe_allow_html=True)
        
        if total_candidates > 0:
            for verdict, count in verdict_counts.items():
                percentage = count / total_candidates
                st.progress(percentage, f"{verdict} Fit ({count} candidates)")
        else:
            st.info("No candidates data available for analysis.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="table-container" style="margin-top: 24px;">', unsafe_allow_html=True)
        st.markdown('<h3>Average Score by Job</h3>', unsafe_allow_html=True)
        
        if job_avg_scores:
            for job_role, avg_score in job_avg_scores.items():
                st.markdown(f'<p>{job_role}: {avg_score}</p>', unsafe_allow_html=True)
        else:
            st.info("No job scores data available for analysis.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Run the page function
if __name__ == "__main__":
    recruiter_reports_page()