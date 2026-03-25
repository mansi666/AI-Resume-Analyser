import plotly.graph_objects as go
import re
import streamlit as st
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Nexus AI Resume Analyser", layout="wide", page_icon="🛡️")

# Custom CSS for a Modern Dashboard Look
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #f4f7f6; }
    
    /* Title Gradient */
    .title-text {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 40px;
    }

    /* Cards Styling */
    .st-emotion-cache-1r6slb0 {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        font-weight: 600;
        height: 3rem;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(42, 82, 152, 0.3);
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Result Box Styling */
    .result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #1e3c72;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ API Key nahi mili!")

# --- 2. FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PdfReader(uploaded_file)
        full_text = " ".join([page.extract_text() or "" for page in pdf_reader.pages])
        return " ".join(full_text.split())
    except Exception as e:
        return None

def get_ai_analysis(resume_text, jd_text):
    # Prompt define kar lete hain pehle
    prompt = f"""
    Analyze the Resume against the JD as a Senior ATS Expert. 
    Output format:
    1. **ATS Match Score**: [Score]%
    2. **Missing Keywords**: [List]
    3. **Skill Gap Analysis**: [Details]
    4. **Roadmap**: [Steps]
    5. **Final Verdict**: [Yes/No]

    Resume: {resume_text}
    JD: {jd_text}
    """
    
    try:
        # Option 1: Try Gemini 1.5 Flash (Direct Name)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        try:
            # Option 2: Agar 404 aata hai, toh check karo available models kaunse hain
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Preference order: Flash (with prefix) -> Pro -> Pehla jo mile
            if 'models/gemini-1.5-flash' in available_models:
                model_to_use = 'models/gemini-1.5-flash'
            elif 'models/gemini-pro' in available_models:
                model_to_use = 'models/gemini-pro'
            else:
                model_to_use = available_models[0]
            
            st.info(f"Using Model: {model_to_use}")
            model = genai.GenerativeModel(model_to_use)
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e2:
            if "429" in str(e2):
                return "QUOTA_ERROR"
            return f"Model Error: {str(e2)}"
def create_gauge_chart(score):
    color = "#28a745" if score > 75 else "#ffa500" if score > 50 else "#ff4b4b"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "#2a5298"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'steps': [
                {'range': [0, 50], 'color': "#fce4e4"},
                {'range': [50, 80], 'color': "#fff4e6"},
                {'range': [80, 100], 'color': "#e6f4ea"}
            ],
        }
    ))
    fig.update_layout(height=280, margin=dict(l=30, r=30, t=50, b=30), paper_bgcolor='rgba(0,0,0,0)')
    return fig

# --- 3. UI DASHBOARD ---
# Main Header
st.markdown('<p class="title-text">🛡️ Nexus AI: Strategy Tool</p>', unsafe_allow_html=True)
st.markdown(f"**Operator:** Mansi Chaudhary | **Focus:** ML & AI Engineering")

# Sidebar Status
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.header("Project Roadmap")
    st.markdown("✅ **Phase 1:** Core Logic")
    st.markdown("✅ **Phase 2:** Visualization")
    st.markdown("🚀 **Phase 3:** UI Transformation")
    st.divider()
    st.caption("Using Gemini 1.5 Flash Engine")

# Two Column Layout for Input
col_input1, col_input2 = st.columns([1, 1], gap="large")

with col_input1:
    st.markdown("### 📤 Upload Resume")
    uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"], label_visibility="collapsed")

with col_input2:
    st.markdown("### 🎯 Job Description")
    jd_text = st.text_area("Paste the target JD", height=120, label_visibility="collapsed")

st.write(" ") # Spacer

# Execution
if st.button("🚀 Analyze with Nexus AI", use_container_width=True):
    if uploaded_file and jd_text:
        with st.spinner("Nexus AI is scanning your profile..."):
            resume_content = extract_text_from_pdf(uploaded_file)
            analysis_report = get_ai_analysis(resume_content, jd_text)
            
            if "QUOTA_ERROR" in analysis_report:
                st.error("⚠️ Server busy! Please retry in 10s.")
            else:
                match = re.search(r"(\d+)%", analysis_report)
                score = int(match.group(1)) if match else 50
                
                # Results Section
                st.divider()
                res_col1, res_col2 = st.columns([1, 2], gap="medium")
                
                with res_col1:
                    st.plotly_chart(create_gauge_chart(score), use_container_width=True)
                
                with res_col2:
                    st.markdown("### 🛠️ Strategic Insights")
                    
                    # Skill Gap Box
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown("**🎯 Skill Gap Analysis**")
                    gap_data = analysis_report.split("Missing Keywords**:")[1].split("3.")[0] if "Missing Keywords" in analysis_report else "N/A"
                    st.write(gap_data)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Roadmap Box
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown("**🚀 Career Roadmap**")
                    roadmap_data = analysis_report.split("Roadmap**:")[1].split("5.")[0] if "Roadmap" in analysis_report else "N/A"
                    st.write(roadmap_data)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with st.expander("🔍 View Detailed ATS Report"):
                    st.markdown(analysis_report)
    else:
        st.warning("Please upload a file and provide a JD.")