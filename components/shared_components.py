import streamlit as st

def render_sidebar(current_page, role):
    """Renders the sidebar based on the current page and user role."""
    
    if 'page' not in st.session_state:
        st.session_state.page = current_page
        
    st.markdown('<div class="sidebar">', unsafe_allow_html=True)
    
    # Logo
    st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; padding:16px; border-bottom:1px solid #334155;">
            <img src="https://www.innomatics.in/wp-content/uploads/2023/01/logo-1.png" alt="Innomatics Logo" style="height:32px;" />
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<nav style="margin-top:32px; flex-grow:1;"><ul>', unsafe_allow_html=True)
    
    if role == "recruiter":
        nav_items = [
            ("Dashboard", "recruiter_dashboard", "M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"),
            ("Job Postings", "recruiter_job_postings", "M20.25 14.15v4.07a2.25 2.25 0 01-2.25 2.25H5.92a2.25 2.25 0 01-2.25-2.25v-4.07a2.25 2.25 0 01.92-1.75l.22-.16a2.25 2.25 0 00-1.1-4.32l-.22-.16a2.25 2.25 0 01-.92-1.75V5.5a2.25 2.25 0 012.25-2.25h12.38a2.25 2.25 0 012.25 2.25v1.27a2.25 2.25 0 01-.92 1.75l-.22.16a2.25 2.25 0 00-1.1 4.32l.22.16a2.25 2.25 0 01.92 1.75z"),
            ("Candidates", "recruiter_candidates", "M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m-7.5-2.962c.57-1.023.99-2.13.99-3.284v-1.598a3 3 0 00-3-3H6.556a3 3 0 00-3 3v1.598c0 1.153.42 2.26.99 3.284m7.5-2.962V5.625a3 3 0 00-3-3H6.556a3 3 0 00-3 3v3.472c0 1.153.42 2.26.99 3.284m7.5-2.962h3.846a3 3 0 012.962 2.592M12 10.5h3.846a3 3 0 002.962-2.592M12 10.5V5.625a3 3 0 00-3-3H6.556a3 3 0 00-3 3v3.472m0 0a3 3 0 002.962 2.592h3.846m-3.846 0V18a3 3 0 003 3h3.846a3 3 0 002.962-2.592"),
            ("Reports", "recruiter_reports", "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"),
        ]
    else: # candidate
        nav_items = [
            ("Dashboard", "candidate_dashboard", "M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"),
            ("Job Postings", "candidate_job_postings", "M20.25 14.15v4.07a2.25 2.25 0 01-2.25 2.25H5.92a2.25 2.25 0 01-2.25-2.25v-4.07a2.25 2.25 0 01.92-1.75l.22-.16a2.25 2.25 0 00-1.1-4.32l-.22-.16a2.25 2.25 0 01-.92-1.75V5.5a2.25 2.25 0 012.25-2.25h12.38a2.25 2.25 0 012.25 2.25v1.27a2.25 2.25 0 01-.92 1.75l-.22.16a2.25 2.25 0 00-1.1 4.32l.22.16a2.25 2.25 0 01.92 1.75z"),
        ]
        
    for name, page, d_path in nav_items:
        is_active = "active" if current_page == page else ""
        st.markdown(f"""
            <li class="sidebar-nav-item {is_active}">
                <a href="?page={page}" style="display:flex; align-items:center; gap:12px; color:inherit; text-decoration:none;">
                    <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="{d_path}" />
                    </svg>
                    <span>{name}</span>
                </a>
            </li>
        """, unsafe_allow_html=True)
        
    st.markdown('</ul></nav>', unsafe_allow_html=True)
    
    # Help & Support always at the bottom
    is_active = "active" if current_page == "help_support" else ""
    st.markdown(f"""
        <div style="margin-top:auto;">
            <ul>
                <li class="sidebar-nav-item {is_active}">
                    <a href="?page=help_support" style="display:flex; align-items:center; gap:12px; color:inherit; text-decoration:none;">
                        <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z" />
                        </svg>
                        <span>Help & Support</span>
                    </a>
                </li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def render_header(title, subtitle, analyze_button=True, avatar_url="https://i.pravatar.cc/40?u=user"):
    """Renders the main content header."""
    st.markdown('<div class="header">', unsafe_allow_html=True)
    
    # Title and Subtitle
    st.markdown(f"""
        <div>
            <h1 style="font-size: 1.5rem; font-weight: 700; color: #1E293B; margin: 0;">{title}</h1>
            <p style="color: #64748B; margin: 0; text-transform: capitalize;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Actions and Avatar
    st.markdown('<div style="display:flex; align-items:center; gap:16px;">', unsafe_allow_html=True)
    
    if analyze_button:
        if st.button("Analyze Resume", key="analyze_button", type="secondary"):
            st.session_state.show_analyze_modal = True

    st.image(avatar_url, width=40)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_metric_card(title, value, icon_svg):
    """Renders a single summary metric card."""
    st.markdown(f"""
        <div class="summary-card">
            <div>
                <p style="color: #64748B;">{title}</p>
                <p style="font-size: 3rem; font-weight: 700; color: #1E293B;">{value}</p>
            </div>
            <div style="background-color:#F1F5F9; padding:12px; border-radius:9999px;">
                <svg class="h-6 w-6 text-slate-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="{icon_svg}" />
                </svg>
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_metric_svg(name):
    """Returns SVG path for a given metric name."""
    icons = {
        "Total Candidates": "M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m-7.5-2.962c.57-1.023.99-2.13.99-3.284v-1.598a3 3 0 00-3-3H6.556a3 3 0 00-3 3v1.598c0 1.153.42 2.26.99 3.284m7.5-2.962V5.625a3 3 0 00-3-3H6.556a3 3 0 00-3 3v3.472c0 1.153.42 2.26.99 3.284m7.5-2.962h3.846a3 3 0 012.962 2.592M12 10.5h3.846a3 3 0 002.962-2.592M12 10.5V5.625a3 3 0 00-3-3H6.556a3 3 0 00-3 3v3.472m0 0a3 3 0 002.962 2.592h3.846m-3.846 0V18a3 3 0 003 3h3.846a3 3 0 002.962-2.592",
        "Open Positions": "M20.25 14.15v4.07a2.25 2.25 0 01-2.25 2.25H5.92a2.25 2.25 0 01-2.25-2.25v-4.07a2.25 2.25 0 01.92-1.75l.22-.16a2.25 2.25 0 00-1.1-4.32l-.22-.16a2.25 2.25 0 01-.92-1.75V5.5a2.25 2.25 0 012.25-2.25h12.38a2.25 2.25 0 012.25 2.25v1.27a2.25 2.25 0 01-.92 1.75l-.22.16a2.25 2.25 0 00-1.1 4.32l.22.16a2.25 2.25 0 01.92 1.75z",
        "High-Fit Candidates": "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z",
        "Avg. Score": "M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z",
        "create_job": "M12 4.5v15m7.5-7.5h-15",
        "job_posting_briefcase": "M20.25 14.15v4.07a2.25 2.25 0 01-2.25 2.25H5.92a2.25 2.25 0 01-2.25-2.25v-4.07a2.25 2.25 0 01.92-1.75l.22-.16a2.25 2.25 0 00-1.1-4.32l-.22-.16a2.25 2.25 0 01-.92-1.75V5.5a2.25 2.25 0 012.25-2.25h12.38a2.25 2.25 0 012.25 2.25v1.27a2.25 2.25 0 01-.92 1.75l-.22.16a2.25 2.25 0 00-1.1 4.32l.22.16a2.25 2.25 0 01.92 1.75z"
    }
    return icons.get(name, "")

def render_score_circle(score):
    """Renders a circular progress bar for a score."""
    score_color = ""
    if score >= 80:
        score_color = "rgb(16, 185, 129)"
    elif score >= 60:
        score_color = "rgb(245, 158, 11)"
    else:
        score_color = "rgb(239, 68, 68)"

    stroke_offset = 314.159 * (1 - score / 100)

    st.markdown(f"""
        <div class="metric-score">
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                <circle class="metric-circle-bg" stroke="currentColor"></circle>
                <circle class="metric-circle-fill" stroke-dashoffset="{stroke_offset}" stroke="{score_color}"></circle>
            </svg>
            <span class="metric-number" style="color: {score_color};">{score}</span>
        </div>
    """, unsafe_allow_html=True)
    
def get_tag_html(score):
    if score >= 80:
        return '<span class="tag-high">High</span>'
    elif score >= 60:
        return '<span class="tag-medium">Medium</span>'
    else:
        return '<span class="tag-low">Low</span>'