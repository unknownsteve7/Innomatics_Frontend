import streamlit as st
from streamlit.components.v1 import html

# Inject custom CSS
with open('styles/main.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Main content for the landing page
st.markdown('<div style="text-align:center; padding-top: 50px;">', unsafe_allow_html=True)
st.image("https://i.imgur.com/v8tT79t.png", width=150) # Replace with your logo if you have one
st.markdown('<h1 style="font-size: 2.5em; font-weight: 600; color: #333;">Welcome to the AI Resume Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Please select your role to get started.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Role selection cards
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="card-container-landing">', unsafe_allow_html=True)
    
    # Recruiter Card (using a button to simulate a link)
    with st.container(height=300):
        st.markdown(f"""
            <div class="card-landing">
                <img src="https://i.imgur.com/W6y4o0b.png" alt="Recruiter Icon" class="card-landing-icon">
                <div class="card-landing-title">I am a Recruiter</div>
                <div class="card-landing-description">Analyze resumes, manage candidates, and streamline your hiring process.</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Go to Recruiter Dashboard", key="recruiter_btn", use_container_width=True):
            st.session_state.role = "recruiter"
            st.experimental_set_query_params(page="recruiter_dashboard")
            st.rerun()

    # Student Card (using a button to simulate a link)
    with st.container(height=300):
        st.markdown(f"""
            <div class="card-landing">
                <img src="https://i.imgur.com/S78uYm4.png" alt="Student Icon" class="card-landing-icon">
                <div class="card-landing-title">I am a Student</div>
                <div class="card-landing-description">Get instant feedback on your resume and improve your job applications.</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Go to Student Dashboard", key="student_btn", use_container_width=True):
            st.session_state.role = "student"
            st.experimental_set_query_params(page="candidate_dashboard")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)