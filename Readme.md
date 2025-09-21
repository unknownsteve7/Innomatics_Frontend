# Automated Resume Relevance Check System  

## Overview  
The **Automated Resume Relevance Check System** is an AI-powered platform designed to transform the recruitment workflow at Innomatics Research Labs. It automates resume evaluation, generates a Relevance Score (0–100), provides fit verdicts, and offers personalized feedback to students — while centralizing results for the placement team.  

This system addresses the bottleneck of manual, inconsistent, and time-consuming resume reviews, ensuring a scalable, consistent, and data-driven solution.  

---

## The Problem  
- Placement team manages 18–20 job requirements weekly across 4 cities.  
- Each posting attracts thousands of applications.  
- Manual evaluation is slow, inconsistent, and prevents staff from focusing on high-value activities like student guidance and interview preparation.  
- Need for scalable, fast, and consistent resume screening.  

---

## Our Solution  
The system delivers a two-sided value proposition:  

### For Placement Team  
- Automates resume-job matching at scale.  
- Provides Relevance Score (0–100) and verdict (High / Medium / Low).  
- Highlights missing skills, certifications, or projects.  
- Centralized results in a web-based dashboard.  
- Integrated Social Media Campaign Manager to publish job posts on LinkedIn, Naukri, etc.  

### For Students  
- Access to a personalized student dashboard.  
- Instant Relevance Score and Gap Analysis.  
- Actionable AI-powered resume feedback (skills, action verbs, STAR method).  
- Helps improve resume quality and boosts placement chances.  

---

## Workflow  
1. **Job & Resume Upload** – Placement team uploads job descriptions, students upload resumes (PDF/DOCX).  
2. **Parsing** – Extracts and standardizes text from documents (skills, education, job title).  
3. **Relevance Analysis** –  
   - Hard Match → Rule-based keyword/skill/education matching.  
   - Semantic Match → LLMs and embeddings for contextual understanding.  
4. **Final Output** – Weighted formula → Relevance Score + verdict + missing items + improvement suggestions.  

---

## Tech Stack  
- **Frontend**: Streamlit  
- **Backend**: Python (FastAPI/Flask embedded in Streamlit)  
- **AI/NLP**: spaCy, NLTK, Transformers, OpenAI/Gemini APIs  
- **Database**: SQLite / PostgreSQL  
- **File Handling**: PyMuPDF, python-docx  

---

## Installation  

```bash
# Clone the repository
git clone https://github.com/unknownsteve7/Innomatics_Frontend.git
cd Innomatics_Frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage  

Run the Streamlit application:  

```bash
streamlit run app.py
```

### For Students  
- Upload resume and select job description.  
- Get Relevance Score, missing skills, and personalized improvement suggestions instantly.  

### For Placement Team  
- Upload job descriptions.  
- Receive auto-evaluated resumes.  
- Use filters (score, role, location) to shortlist candidates quickly.  
- Create and publish job posts directly to social platforms.  

---

## Learnings  
- Hybrid AI is Key → Combining rule-based and semantic AI ensures accuracy and speed.  
- Dual-Purpose Design → Helping students improve resumes boosts overall placement quality.  
- Strategic Prioritization → Focused on core MVP while showcasing advanced features in roadmap.  

---

## Team  
- Anand – Backend & AI Model  
- Naga Mohan – Database & Frontend  
- Leeladhar – Documentation, Integration & Deployment  

---

## Project Source  
Developed as part of Code4EdTech Hackathon ’25 by Innomatics Research Labs.  
