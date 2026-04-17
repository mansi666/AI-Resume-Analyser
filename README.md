# 🚀 AI Resume Analyzer & Neural Intelligence Dashboard

A high-performance, AI-powered recruitment tool that goes beyond simple keyword matching. Built using **Google Gemini 1.5 Flash**, this dashboard analyzes resumes against job descriptions to provide deep insights, career roadmaps, and interview preparation.

![Dashboard Preview](assets/Screenshot_211.png)

## 🌟 Key Features

* **Job Match & ATS Scoring**: Instant visualization of how well a candidate fits a role with high-impact "Hero Scores".
* **Neural Skill Matrix**: A 5-axis radar chart analyzing Technical Skills, Experience, Education, Certifications, and Soft Skills.
* **Job Fit Analysis**: Dual-bar charts comparing Skill Alignment and Experience Match levels (High/Moderate/Low).
* **30-Day Goal Roadmap**: Personalized, actionable learning paths to bridge the gap between current skills and job requirements.
* **AI Interview Prep**: Automatically generates customized interview questions based on the candidate's specific profile gaps.
* **Automated PDF Reports**: Generate and download a professional summary report of the entire analysis.

## 🛠️ Tech Stack

* **Frontend/App Framework**: [Streamlit](https://streamlit.io/)
* **AI Model**: [Google Gemini 1.5 Flash](https://ai.google.dev/) (Generative AI)
* **Data Visualization**: [Plotly](https://plotly.com/python/)
* **PDF Processing**: PyPDF2 & FPDF
* **Language**: Python 3.13

## 📊 Real-World Intelligence Example

During testing, the system correctly analyzed a student's resume focused on **AI/ML & Deep Learning** against a **Software Developer (Web)** role. It accurately identified:
* **Strengths**: Strong background in RAG systems, LLaMA, and Python.
* **Critical Gaps**: Missing experience in Javascript, React, and Node.js required by the JD.
* **Outcome**: It assigned a logical match score of 28% and provided a roadmap to learn Web Development fundamentals.

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mansi-chaudhary-ai/AI-Resume-Analyser

2. **Install dependencies:**
    pip install streamlit plotly PyPDF2 fpdf2 python-dotenv google-generativeai

3. **Set up Environment Variables:**
     GOOGLE_API_KEY=your_gemini_api_key_here
4. **Run the application:**
     streamlit run app.py

## 📜 License
Distributed under the MIT License. See LICENSE for more information.

   
