import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import re, os, time
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from fpdf import FPDF
import io

# --- 1. PREMIUM UI CONFIG ---
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f4f7f9; }
    
    /* Hero Score Styling */
    .hero-score-box {
        background: white; padding: 20px; border-radius: 12px;
        text-align: center; border: 1px solid #e1e4e8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .hero-val { font-size: 3.2rem; font-weight: 800; line-height: 1; }
    .hero-label { font-size: 0.9rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-top: 5px; }

    .stats-card {
        background: white; padding: 15px; border-radius: 8px;
        text-align: center; border: 1px solid #e1e4e8;
    }
    .stats-val { font-size: 1.5rem; font-weight: 700; color: #1e3a8a; }

    .dash-card {
        background: white; padding: 20px; border-radius: 10px;
        border: 1px solid #e1e4e8; margin-bottom: 20px;
    }
    .card-title { font-weight: 700; color: #1e3a8a; margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
    
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; margin: 3px; display: inline-block; }
    .kw-found { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    .kw-missing { background: #fff1f2; color: #9f1239; border: 1px solid #fecaca; }
    
    .strength-box { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .improve-box { background: #fff7ed; border-left: 4px solid #f97316; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    
    /* Roadmap Box Styling */
    .roadmap-box { background: #eff6ff; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    
    /* Interview Prep Styling (As per your previous choice) */
    .interview-q { background: #f8fafc; padding: 10px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 8px; font-style: italic; font-size: 0.85rem; }

    [data-testid="stHeader"] { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC ---
@st.cache_data(show_spinner=False)
def get_ai_analysis(resume_text, jd_text):
    try:
        model_names = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in model_names if "1.5-flash" in m), model_names[0])
        model = genai.GenerativeModel(target)
        prompt = f"""
        Act as an HR Expert. Format: MATCH: (num), ATS: (num), QUALITY: (num), FOUND_KW: (list), MISS_KW: (list), STRENGTHS: (Bullet points), AREAS: (Bullet points), RADAR: (5 nums), BARS: (6 nums), SUMMARY: (text), QUESTIONS: (3 separate points), ROADMAP: (3 separate points).
        Resume: {resume_text} | JD: {jd_text}
        """
        return model.generate_content(prompt).text
    except Exception as e: return f"ERROR: {str(e)}"

def generate_pdf_report(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(30, 58, 138); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20); pdf.cell(0, 20, "AI ANALYSIS REPORT", 0, 1, 'C')
    pdf.set_text_color(0, 0, 0); pdf.ln(25); pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Match Score: {data['m_score']}% | ATS score: {data['ats_score']}%", 0, 1)
    clean_summary = data['summary'].encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, clean_summary)
    return bytes(pdf.output())

# --- 3. HEADER & STATS ---
st.markdown("""<div style="background:#1e3a8a; padding:15px; color:white; border-radius:10px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
<h2 style='margin:0;'>AI Resume Analyzer</h2><div style='text-align:right;'>Welcome, <b>Mansi Chaudhary</b></div></div>""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
s1.markdown('<div class="stats-card"><div class="stats-val">1,256</div><div class="stats-label">Resumes Analyzed</div></div>', unsafe_allow_html=True)
s2.markdown('<div class="stats-card"><div class="stats-val">184</div><div class="stats-label">Shortlisted</div></div>', unsafe_allow_html=True)
s3.markdown('<div class="stats-card"><div class="stats-val">92%</div><div class="stats-label">Top Match</div></div>', unsafe_allow_html=True)
s4.markdown('<div class="stats-card"><div class="stats-val">78%</div><div class="stats-label">Avg. Rate</div></div>', unsafe_allow_html=True)

u1, u2 = st.columns(2)
with u1: res_file = st.file_uploader("Candidate Resume (PDF)", type="pdf")
with u2: jd_input = st.text_area("Job Description", height=80)

if st.button("🚀 INITIATE ANALYSIS", use_container_width=True):
    if res_file and jd_input:
        with st.spinner("Decoding DNA..."):
            reader = PdfReader(res_file)
            resume_text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
            raw = get_ai_analysis(resume_text, jd_input)
            
            if "ERROR" not in raw:
                def extract(tag):
                    match = re.search(f"{tag}:\\s*(.*?)(?=\\n[A-Z]+:|$)", raw, re.DOTALL | re.IGNORECASE)
                    return match.group(1).strip() if match else "N/A"

                m_score = int(re.search(r"MATCH:\s*(\d+)", raw).group(1))
                ats_score = int(re.search(r"ATS:\s*(\d+)", raw).group(1))
                radar_vals = [int(v) for v in re.findall(r"\d+", extract("RADAR"))[:5]]
                bar_vals = [int(v) for v in re.findall(r"\d+", extract("BARS"))[:6]]
                summary = extract("SUMMARY")

                def format_bullets(text):
                    pts = re.split(r'\*|\n-|\d+\.|\n\d+\.', text)
                    return "".join([f'<div style="display:flex; align-items:flex-start; margin-bottom:8px;"><span style="font-size:1.2rem; margin-right:10px; line-height:1;">•</span><span style="font-size:0.85rem; line-height:1.4;">{p.strip()}</span></div>' for p in pts if len(p.strip()) > 5])

                # --- LARGE HERO SCORES ---
                h1, h2 = st.columns(2)
                h1.markdown(f'<div class="hero-score-box"><div class="hero-val" style="color:#10b981;">{m_score}%</div><div class="hero-label">Job Match Score</div></div>', unsafe_allow_html=True)
                h2.markdown(f'<div class="hero-score-box"><div class="hero-val" style="color:#3b82f6;">{ats_score}%</div><div class="hero-label">ATS Compatibility</div></div>', unsafe_allow_html=True)

                # --- DASHBOARD LAYOUT ---
                col_l, col_m, col_r = st.columns([1.2, 1.5, 1.2])

                with col_l:
                    st.markdown('<div class="dash-card"><div class="card-title">Resume Overview</div>', unsafe_allow_html=True)
                    fig_r = go.Figure(data=go.Scatterpolar(r=radar_vals, theta=['Tech', 'Exp', 'Edu', 'Cert', 'Soft'], fill='toself'))
                    st.plotly_chart(fig_r.update_layout(height=250, margin=dict(t=20,b=20,l=20,r=20), polar=dict(radialaxis=dict(visible=False, range=[0, 10]))), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="dash-card"><h4>🚀 30-Day Goal Roadmap</h4>', unsafe_allow_html=True)
                    st.markdown(f'<div class="roadmap-box">{format_bullets(extract("ROADMAP"))}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_m:
                    st.markdown('<div class="dash-card"><div class="card-title">Job Fit Analysis</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="strength-box"><b>Strengths:</b><br>{format_bullets(extract("STRENGTHS"))}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="improve-box"><b>Improvements:</b><br>{format_bullets(extract("AREAS"))}</div>', unsafe_allow_html=True)
                    f1, f2 = st.columns(2)
                    with f1:
                        fig_fit = px.bar(x=['High', 'Mod', 'Low'], y=bar_vals[:3], title="Skill Alignment", color_discrete_sequence=['#1e3a8a'])
                        st.plotly_chart(fig_fit.update_layout(height=280, margin=dict(t=40,b=10,l=10,r=10), xaxis_title=""), use_container_width=True)
                    with f2:
                        fig_exp = px.bar(x=['Exc', 'Avg', 'Low'], y=bar_vals[3:], title="Exp Match", color_discrete_sequence=['#3b82f6'])
                        st.plotly_chart(fig_exp.update_layout(height=280, margin=dict(t=40,b=10,l=10,r=10), xaxis_title=""), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_r:
                    st.markdown('<div class="dash-card"><div class="card-title">Resume Insights</div>', unsafe_allow_html=True)
                    st.write("**Keywords:**")
                    st.markdown(" ".join([f'<span class="badge kw-found">{k.strip()}</span>' for k in extract("FOUND_KW").split(",")]), unsafe_allow_html=True)
                    st.write("<br>**Missing:**", unsafe_allow_html=True)
                    st.markdown(" ".join([f'<span class="badge kw-missing">{k.strip()}</span>' for k in extract("MISS_KW").split(",")]), unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # BACK TO BOXES FOR INTERVIEW PREP
                    st.markdown('<div class="dash-card"><h4>🎙️ Interview Prep</h4>', unsafe_allow_html=True)
                    for q in re.split(r'\*|\n-|\d+\.|\n\d+\.', extract("QUESTIONS")):
                        if len(q.strip()) > 5:
                            st.markdown(f'<div class="interview-q">{q.strip()}?</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                pdf_bytes = generate_pdf_report({'m_score': m_score, 'ats_score': ats_score, 'summary': summary})
                st.download_button(label="📥 DOWNLOAD FULL REPORT", data=pdf_bytes, file_name="Nexus_Report.pdf", mime="application/pdf", use_container_width=True)
            else: st.error(raw)