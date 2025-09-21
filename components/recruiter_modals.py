import streamlit as st
import pandas as pd
from components.shared_components import render_score_circle, get_tag_html

def analyze_resume_modal():
    """Renders the 'Analyze New Resume' modal."""
    if 'show_analyze_modal' not in st.session_state:
        st.session_state.show_analyze_modal = False

    if st.session_state.show_analyze_modal:
        st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
        st.markdown('<div class="modal-content" style="max-width: 600px;">', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="modal-header" style="border-bottom: none;">
                <h2 style="font-size: 1.5rem; font-weight: bold; color: #1E293B; margin: 0;">Analyze New Resume</h2>
                <button onclick="window.parent.document.querySelector('.modal-overlay').remove();" style="font-size:1.5rem; color:#94A3B8; background:none; border:none; cursor:pointer;">&times;</button>
            </div>
            """, unsafe_allow_html=True)
        
        with st.form("analyze_form"):
            st.columns(2)[0].text_input("Candidate Name", placeholder="e.g., John Doe")
            st.columns(2)[1].text_input("Job Role", placeholder="e.g., Frontend Developer")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="file-upload-box">', unsafe_allow_html=True)
                st.markdown('<p style="font-size: 0.875rem; color:#64748B;">Job Description</p>', unsafe_allow_html=True)
                st.file_uploader("Upload a file or drag and drop", type=['txt', 'pdf', 'docx'], label_visibility="collapsed")
                st.markdown('<p style="font-size: 0.75rem; color:#64748B;">TXT, PDF, DOCX up to 10MB</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="file-upload-box">', unsafe_allow_html=True)
                st.markdown('<p style="font-size: 0.875rem; color:#64748B;">Candidate\'s Resume</p>', unsafe_allow_html=True)
                st.file_uploader("Upload a file or drag and drop", type=['txt', 'pdf', 'docx'], label_visibility="collapsed")
                st.markdown('<p style="font-size: 0.75rem; color:#64748B;">TXT, PDF, DOCX up to 10MB</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="text-align: right; margin-top: 20px;">', unsafe_allow_html=True)
            if st.form_submit_button("Cancel"):
                st.session_state.show_analyze_modal = False
            st.form_submit_button("Run Analysis", type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

def create_job_modal():
    """Renders the 'Create New Job Posting' modal."""
    if 'show_create_job_modal' not in st.session_state:
        st.session_state.show_create_job_modal = False
        
    if st.session_state.show_create_job_modal:
        st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
        st.markdown('<div class="modal-content" style="max-width: 600px;">', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="modal-header" style="border-bottom: none;">
                <h2 style="font-size: 1.5rem; font-weight: bold; color: #1E293B; margin: 0;">Create New Job Posting</h2>
                <button onclick="window.parent.document.querySelector('.modal-overlay').remove();" style="font-size:1.5rem; color:#94A3B8; background:none; border:none; cursor:pointer;">&times;</button>
            </div>
            """, unsafe_allow_html=True)
        
        with st.form("create_job_form"):
            col1, col2 = st.columns(2)
            col1.text_input("Job Title", placeholder="e.g., Frontend Developer")
            col2.text_input("Department", placeholder="e.g., Engineering")
            
            st.text_area("Job Description", placeholder="Provide a summary of the role...")
            st.text_area("Requirements", placeholder="List each requirement on a new line...")
            
            st.file_uploader("Upload a file or drag and drop", type=['txt', 'pdf', 'docx'])
            
            st.markdown('<div style="text-align: right; margin-top: 20px;">', unsafe_allow_html=True)
            if st.form_submit_button("Cancel"):
                st.session_state.show_create_job_modal = False
            st.form_submit_button("Create Job", type="primary")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div></div>', unsafe_allow_html=True)

def view_details_modal(candidate_data, job_data, current_tab):
    """Renders the 'View Details' modal for a specific candidate."""
    if 'show_details_modal' not in st.session_state:
        st.session_state.show_details_modal = False

    if st.session_state.show_details_modal:
        st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
        st.markdown(f'<div class="modal-content" style="border-top: 4px solid {get_score_color(candidate_data["score"])};">', unsafe_allow_html=True)

        # Modal Header
        st.markdown(f"""
            <div class="modal-header" style="border-bottom-color: {get_score_color(candidate_data['score'])};">
                <div>
                    <h2 style="font-size:1.5rem; font-weight:700; color:#1E293B;">{candidate_data['name']}</h2>
                    <p style="color:#64748B;">{candidate_data['job_role']}</p>
                    <span class="tag-{get_fit_class(candidate_data['score'])}">
                        {get_fit_text(candidate_data['score'])} Fit
                    </span>
                </div>
                <button onclick="window.parent.document.querySelector('.modal-overlay').remove();" style="font-size:1.5rem; color:#94A3B8; background:none; border:none; cursor:pointer;">&times;</button>
            </div>
        """, unsafe_allow_html=True)

        # Modal Tabs
        tab_buttons = st.columns(3)
        with tab_buttons[0]:
            if st.button("Overview", key="tab_overview"):
                st.session_state.details_tab = "overview"
        with tab_buttons[1]:
            if st.button("AI Feedback", key="tab_feedback"):
                st.session_state.details_tab = "ai_feedback"
        with tab_buttons[2]:
            if st.button("Comparison", key="tab_comparison"):
                st.session_state.details_tab = "comparison"

        # Tab Content
        st.markdown('<div class="modal-body">', unsafe_allow_html=True)
        if st.session_state.details_tab == "overview":
            render_details_overview(candidate_data)
        elif st.session_state.details_tab == "ai_feedback":
            render_ai_feedback(candidate_data)
        else:
            render_comparison(candidate_data, job_data)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)
        
def render_details_overview(candidate_data):
    col1, col2 = st.columns([1, 2])
    with col1:
        render_score_circle(candidate_data['score'])
        st.markdown('<p style="text-align: center; font-weight: 600; color:#475569;">Relevance Score</p>', unsafe_allow_html=True)
    with col2:
        st.markdown('<h3 style="font-weight: 600; color:#334155;">AI Summary</h3>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#475569;">{candidate_data["summary"]}</p>', unsafe_allow_html=True)

def render_ai_feedback(candidate_data):
    st.markdown('<h3 style="font-weight: 600; color:#334155;">Highlighted Gaps</h3>', unsafe_allow_html=True)
    st.markdown('<ul style="list-style-type: none; padding-left: 0;">', unsafe_allow_html=True)
    for gap in candidate_data.get("gaps", []):
        st.markdown(f'<li style="display: flex; align-items: center; gap: 8px; color: #EF4444;"><span style="font-size: 1.25em; line-height: 1; color: inherit;">&times;</span> {gap}</li>', unsafe_allow_html=True)
    st.markdown('</ul>', unsafe_allow_html=True)
    
    st.markdown('<h3 style="font-weight: 600; color:#334155;">AI-Powered Suggestions</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#475569;">{candidate_data["suggestions"]}</p>', unsafe_allow_html=True)

def render_comparison(candidate_data, job_data):
    st.markdown('<h3 style="font-weight: 600; color:#334155;">Score Comparison</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#64748B; font-size: 0.875rem;">This chart compares {candidate_data["name"]}\'s relevance score to the average score of all candidates who applied for the {candidate_data["job_role"]} position.</p>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
    st.markdown(f'<p style="font-weight: 600; color: #1E293B;">Candidate Score</p>', unsafe_allow_html=True)
    st.progress(candidate_data['score'] / 100)
    st.markdown(f'<p style="text-align: right; margin-top: -24px; color: #1E293B;">{candidate_data["score"]}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
    st.markdown(f'<p style="font-weight: 600; color: #1E293B;">Average for Role</p>', unsafe_allow_html=True)
    avg_score = job_data.get('avg_score', 0)
    st.progress(avg_score / 100)
    st.markdown(f'<p style="text-align: right; margin-top: -24px; color: #1E293B;">{avg_score}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def get_score_color(score):
    if score >= 80:
        return "rgb(16, 185, 129)"
    elif score >= 60:
        return "rgb(245, 158, 11)"
    else:
        return "rgb(239, 68, 68)"

def get_fit_class(score):
    if score >= 80:
        return "high"
    elif score >= 60:
        return "medium"
    else:
        return "low"

def get_fit_text(score):
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    else:
        return "Low"