import streamlit as st
import openai
import os
import fitz  # PyMuPDF
from docx import Document
from fpdf import FPDF
import pytesseract
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import base64
from io import BytesIO
from github import Github  # PyGithub

st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("AI Cover Letter & Resume Optimizer")

# Note for OpenAI API key
with st.expander("ℹ️ What is an OpenAI API Key?"):
    st.markdown("""
        **OpenAI API Key** ek unique password jaisa hota hai jo aapko OpenAI ki services (jaise GPT-3.5) use karne deta hai.  
        🔑 Aap apni API key yahan se generate kar sakte ho: [OpenAI API Keys](https://platform.openai.com/account/api-keys)  
        📌 Bas key ko copy karke upar ke box me daalo.  
        ⚠️ Apni key kisi ke saath share mat karna.
    """)

# API Key
user_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")
if not user_api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()
openai.api_key = user_api_key

# Resume Upload
st.subheader("📄 Upload Resume")
resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
resume_text_input = st.text_area("Or Paste Resume Text", height=200)

# JD Upload
st.subheader("🧾 Upload Job Description")
jd_file = st.file_uploader("Upload JD (PDF, DOCX, TXT, or Image)", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
jd_text_input = st.text_area("Or Paste JD Text", height=200)

# Extract text from file
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    _, ext = os.path.splitext(uploaded_file.name)
    if ext == ".pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            return " ".join([page.get_text() for page in doc])
    elif ext == ".docx":
        return "\n".join([para.text for para in Document(uploaded_file).paragraphs])
    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)
    elif ext == ".txt":
        return uploaded_file.read().decode("utf-8")
    return ""

resume_text = resume_text_input or extract_text_from_file(resume_file)
job_text = jd_text_input or extract_text_from_file(jd_file)

# Smart Dashboard function
def show_dashboard(improvements_dict):
    df = pd.DataFrame(list(improvements_dict.items()), columns=["Feature", "Improvement (%)"])
    st.subheader("📊 Smart Resume Improvement Dashboard")

    fig1, ax1 = plt.subplots()
    ax1.pie(df["Improvement (%)"], labels=df["Feature"], autopct="%1.1f%%", startangle=90)
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.bar(df["Feature"], df["Improvement (%)"], color='skyblue')
    ax2.set_ylabel("Improvement (%)")
    ax2.set_title("Resume Feature-Wise Improvement")
    st.pyplot(fig2)

    # Export Excel
    excel_path = "resume_improvement.xlsx"
    df.to_excel(excel_path, index=False)

    with open(excel_path, "rb") as f:
        st.download_button("⬇️ Download Excel", f, file_name="resume_improvement.xlsx")

    # Save charts as images
    def save_fig_as_image(fig, filename):
        buf = BytesIO()
        fig.savefig(buf, format="png")
        with open(filename, "wb") as f:
            f.write(buf.getbuffer())

    save_fig_as_image(fig1, "pie_chart.png")
    save_fig_as_image(fig2, "bar_chart.png")

    # Upload to GitHub
    github_token = st.secrets["github"]["token"]
    repo_name = "mdayanahmed/Cover-letter-generator"
    g = Github(github_token)
    repo = g.get_repo(repo_name)

    def upload_to_github(filepath):
        with open(filepath, "rb") as f:
            content = f.read()
        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{os.path.basename(filepath)}"
        repo.create_file(f"analytics/{filename}", f"Add {filename}", content)

    upload_to_github("pie_chart.png")
    upload_to_github("bar_chart.png")
    upload_to_github(excel_path)
    st.success("✅ Charts and Excel uploaded to GitHub!")

# If both resume and JD are available
if resume_text and job_text:

    # COVER LETTER
    if st.button("✉️ Generate Cover Letter"):
        with st.spinner("Generating..."):
            prompt = f"""Write a professional cover letter based on:
Resume:
{resume_text}

Job Description:
{job_text}
"""
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            cover_letter = response.choices[0].message.content
            st.success("Cover Letter Generated!")
            st.text_area("📄 Preview", cover_letter, height=300)

            doc = Document()
            doc.add_heading("Cover Letter", 0)
            doc.add_paragraph(cover_letter)
            doc.save("Cover_Letter.docx")
            with open("Cover_Letter.docx", "rb") as file:
                st.download_button("⬇️ Download Cover Letter", file, "Cover_Letter.docx")

    # RESUME SUGGESTIONS
    if st.button("🛠️ Suggest Resume Improvements"):
        with st.spinner("Analyzing..."):
            prompt = f"""
You are a resume expert. Based on the resume and job description, suggest area-wise improvement percentages in format:
Skill Match: 80%
Action Verbs: 60%
Achievements: 70%
ATS Keywords: 75%
Formatting: 65%
Also give text suggestions below.
Resume:
{resume_text}
Job:
{job_text}
"""
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            content = response.choices[0].message.content
            st.markdown("### 📈 Resume Suggestions")
            st.markdown(content)

            # Parse improvement % for dashboard
            improvements = {}
            for line in content.splitlines():
                if ":" in line and "%" in line:
                    key, val = line.split(":")
                    try:
                        improvements[key.strip()] = int(val.strip().replace("%", ""))
                    except:
                        pass
            if improvements:
                show_dashboard(improvements)

    # JOB ROLES
    if st.button("💼 Suggest Job Titles"):
        with st.spinner("Matching..."):
            prompt = f"Suggest 5 job titles based on this resume:\n{resume_text}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown("### 🔍 Suggested Job Roles")
            st.markdown(response.choices[0].message.content)

    # ATS MATCH
    if st.button("📊 Check ATS Match Score"):
        with st.spinner("Checking..."):
            prompt = f"""
Act as ATS engine. Compare resume and job description.
Return match % (0-100), matching & missing keywords, short feedback.
Resume:
{resume_text}

JD:
{job_text}
"""
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            st.markdown("### 📋 ATS Report")
            st.markdown(response.choices[0].message.content)

    # INTERVIEW QUESTIONS
    if st.button("🎤 Generate Interview Questions"):
        with st.spinner("Generating..."):
            prompt = f"Generate 5 interview questions from this JD:\n{job_text}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            st.markdown("### ❓ Likely Interview Questions")
            st.markdown(response.choices[0].message.content)

else:
    st.info("Please upload or paste both Resume and Job Description to begin.")
