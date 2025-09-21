import streamlit as st
from components.shared_components import render_score_circle, get_tag_html

def application_feedback_modal(app_data, current_tab):
    """Renders the 'Application Feedback' modal for a candidate."""
    if 'show_feedback_modal' not in st.session_state:
        st.session_state.show_feedback_modal = False

    if st.session_state.show_feedback_modal:
        st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
        st.markdown(f'<div class="modal-content" style="border-top: 4px solid {get_score_color(app_data["score"])};">', unsafe_allow_html=True)

        # Modal Header
        st.markdown(f"""
            <div class="modal-header" style="border-bottom-color: {get_score_color(app_data['score'])};">
                <div>
                    <h2 style="font-size:1.5rem; font-weight:700; color:#1E293B;">Application Feedback</h2>
                    <p style="color:#64748B;">For: {app_data['job_title']}</p>
                </div>
                <button onclick="window.parent.document.querySelector('.modal-overlay').remove();" style="font-size:1.5rem; color:#94A3B8; background:none; border:none; cursor:pointer;">&times;</button>
            </div>
        """, unsafe_allow_html=True)

        # Modal Tabs
        tab_buttons = st.columns(2)
        with tab_buttons[0]:
            if st.button("Overview", key="cand_tab_overview"):
                st.session_state.feedback_tab = "overview"
        with tab_buttons[1]:
            if st.button("Improvement Plan", key="cand_tab_improvement"):
                st.session_state.feedback_tab = "improvement"

        # Tab Content
        st.markdown('<div class="modal-body">', unsafe_allow_html=True)
        if st.session_state.feedback_tab == "overview":
            render_feedback_overview(app_data)
        else:
            render_improvement_plan(app_data)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)
        
def render_feedback_overview(app_data):
    col1, col2 = st.columns([1, 2])
    with col1:
        render_score_circle(app_data['score'])
        st.markdown(f'<p style="text-align: center; font-weight: 600; color:#475569;">{get_tag_html(app_data["score"])}</p>', unsafe_allow_html=True)
    with col2:
        st.markdown('<h3 style="font-weight: 600; color:#334155;">AI Summary</h3>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#475569;">{app_data["summary"]}</p>', unsafe_allow_html=True)

def render_improvement_plan(app_data):
    st.markdown('<h3 style="font-weight: 600; color:#334155;">Focus Areas for Your Resume</h3>', unsafe_allow_html=True)
    st.markdown('<ul style="list-style-type: none; padding-left: 0;">', unsafe_allow_html=True)
    for area in app_data.get("focus_areas", []):
        st.markdown(f'<li style="display: flex; align-items: center; gap: 8px; color: #EF4444;"><span style="font-size: 1.25em; line-height: 1; color: inherit;">&times;</span> {area}</li>', unsafe_allow_html=True)
    st.markdown('</ul>', unsafe_allow_html=True)
    
    st.markdown('<h3 style="font-weight: 600; color:#334155;">AI-Powered Suggestions</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#475569;">{app_data["suggestions"]}</p>', unsafe_allow_html=True)
    
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