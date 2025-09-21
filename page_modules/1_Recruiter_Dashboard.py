import streamlit as st
import pandas as pd
from components.shared_components import render_sidebar, render_header, render_metric_card, get_metric_svg, render_score_circle, get_tag_html
from components.recruiter_modals import analyze_resume_modal, view_details_modal
from backend_api_service import BackendAPIService

st.set_page_config(layout="wide", page_title="Recruiter Dashboard")

def get_api_service():
    return BackendAPIService()

def recruiter_dashboard_page():
    if 'selected_candidate' not in st.session_state:
        st.session_state.selected_candidate = None
    if 'details_tab' not in st.session_state:
        st.session_state.details_tab = "overview"

    # --- Page Rendering ---
    col_sidebar, col_content = st.columns([1, 4])

    with col_sidebar:
        render_sidebar("recruiter_dashboard", "recruiter")

    with col_content:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        render_header("Dashboard", "Recruiter View", analyze_button=True, avatar_url="https://i.pravatar.cc/40?u=recruiter")

        st.markdown('<main style="padding: 24px;">', unsafe_allow_html=True)
        
        # Get data from backend
        api_service = get_api_service()
        backend_candidates = api_service.get_candidates()
        backend_jobs = api_service.get_jobs()
        
        if "error" in backend_candidates or "error" in backend_jobs:
            st.error("Could not load dashboard data. Please check your backend connection.")
            st.markdown('</main></div>', unsafe_allow_html=True)
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
        
        # Transform jobs to consistent format
        processed_jobs = []
        for job in jobs:
            # Count applicants for this job
            job_applicants = [c for c in candidates if c.get('job', {}).get('job_title') == job.get('job_title', '')]
            avg_score = sum(c.get('relevance_score', 0) for c in job_applicants) / len(job_applicants) if job_applicants else 0
            
            processed_jobs.append({
                'title': job.get('job_title', 'Unknown Position'),
                'department': job.get('department', 'Unknown Department'),
                'applicants': len(job_applicants),
                'avg_score': int(avg_score)
            })
        
        # Calculate metrics
        metrics_data = {
            "Total Candidates": len(processed_candidates),
            "Open Positions": len(processed_jobs),
            "High-Fit Candidates": len([c for c in processed_candidates if c['verdict'] == 'High']),
            "Avg. Score": int(sum(c['score'] for c in processed_candidates) / len(processed_candidates)) if processed_candidates else 0
        }
        
        # Summary Cards
        st.markdown('<div class="card-grid">', unsafe_allow_html=True)
        for title, value in metrics_data.items():
            render_metric_card(title, value, get_metric_svg(title))
        st.markdown('</div>', unsafe_allow_html=True)

        # Dashboard Content
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown('<div class="table-container" style="margin-top: 24px;">', unsafe_allow_html=True)
            st.markdown('<h2 style="font-size:1.25rem; font-weight:700; color:#1E293B; margin-bottom:16px;">Recent Analyses</h2>', unsafe_allow_html=True)
            st.markdown('<div class="table-responsive">', unsafe_allow_html=True)
            st.markdown('<table class="table"><thead><tr><th>Candidate</th><th>Job Role</th><th style="text-align: center;">Score</th><th>Verdict</th><th>Action</th></tr></thead><tbody>', unsafe_allow_html=True)
            
            for cand in processed_candidates:
                st.markdown('<tr>', unsafe_allow_html=True)
                st.markdown(f'<td style="font-weight:600;">{cand["name"]}</td>', unsafe_allow_html=True)
                st.markdown(f'<td style="color:#475569;">{cand["job_role"]}</td>', unsafe_allow_html=True)
                st.markdown('<td>', unsafe_allow_html=True)
                render_score_circle(cand["score"])
                st.markdown('</td>', unsafe_allow_html=True)
                st.markdown(f'<td>{get_tag_html(cand["score"])}</td>', unsafe_allow_html=True)
                st.markdown(f'<td><a href="javascript:void(0);" onclick="window.parent.document.querySelector(\'#details-modal\').style.display=\'flex\';" style="color:#4338CA; font-weight:600;">View Details</a></td>', unsafe_allow_html=True)
                st.markdown('</tr>', unsafe_allow_html=True)
            
            st.markdown('</tbody></table></div></div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="job-posting-card" style="margin-top: 24px;">', unsafe_allow_html=True)
            st.markdown('<h2 style="font-size:1.25rem; font-weight:700; color:#1E293B; margin-bottom:16px;">Active Job Postings</h2>', unsafe_allow_html=True)
            for job in processed_jobs:
                st.markdown(f"""
                    <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 12px; margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="font-weight:600; color:#1E293B; margin:0;">{job['title']}</p>
                                <p style="font-size: 0.875rem; color: #64748B; margin:0;">{job['department']}</p>
                            </div>
                            <div style="text-align: right;">
                                <p style="font-weight:700; font-size: 1.125rem; color:#4338CA; margin:0;">{job['applicants']}</p>
                                <p style="font-size:0.75rem; color:#64748B; margin:0;">Applicants</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("""
                <button style="width:100%; text-align:center; background-color:#F1F5F9; color:#475569; font-weight:600; padding:8px; border-radius:8px; margin-top:16px; border:none; cursor:pointer;">
                    <a href="?page=recruiter_job_postings" style="text-decoration:none; color:inherit; display:block;">View All Jobs</a>
                </button>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</main></div>', unsafe_allow_html=True)
        
        # Modals (hidden by default)
        analyze_resume_modal()
        # The view details modal needs to be linked to the table.
        # In a real app, you would use st.session_state to manage which modal is shown and with what data.

# Call the function to render the page
recruiter_dashboard_page()