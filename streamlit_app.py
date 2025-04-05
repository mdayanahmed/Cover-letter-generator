# Full code bhai yahaan se start hota hai
import streamlit as st
import openai
import os
import fitz
import pytesseract
import pandas as pd
from PIL import Image
from docx import Document
import matplotlib.pyplot as plt
from io import BytesIO
from github import Github
from datetime import datetime

# ---------- Streamlit Config ----------
st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("AI Career Assistant: Cover Letter & Resume Optimizer")

# ---------- API Key ----------
user_api_key = st.text_input("Enter your OpenAI API Key", type="password")
if not user_api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()
openai.api_key = user_api_key

# ---------- Upload Resume & JD ----------
st.subheader("Upload Resume")
resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
resume_text_input = st.text_area("Or Paste Resume Text", height=200)

st.subheader("Upload Job Description")
jd_file = st.file_uploader("Upload Job Description (PDF, DOCX, TXT, or Image)", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
jd_text_input = st.text_area("Or Paste Job Description Text", height=200)

# ---------- Extractor Function ----------
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
    else:
        return ""

# ---------- Resume/JD Final Text ----------
resume_text = resume_text_input or extract_text_from_file(resume_file)
job_text = jd_text_input or extract_text_from_file(jd_file)

# ---------- Generate Outputs ----------
if resume_text and job_text:

    # ------------------- COVER LETTER -------------------
    if st.button("Generate Cover Letter"):
        with st.spinner("Generating Cover Letter..."):
            prompt = f"""
            Write a professional and enthusiastic cover letter based on the resume and job description below.
            Resume: {resume_text}
            Job Description: {job_text}
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            cover_letter = response.choices[0].message.content
            st.success("✅ Cover Letter Generated")
            st.text_area("Cover Letter Preview", cover_letter, height=300)

    # ------------------- RESUME SUGGESTIONS -------------------
    if st.button("Suggest Resume Improvements"):
        with st.spinner("Analyzing resume..."):
            prompt = f"""
            You're a resume coach. Based on the resume and job description below, suggest specific improvements to tailor the resume for the job.
            Resume: {resume_text}
            Job Description: {job_text}
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            suggestions = response.choices[0].message.content
            st.markdown("### Resume Optimization Suggestions")
            st.markdown(suggestions)

            # ----- SMART DASHBOARD -----
            st.subheader("📊 Smart Resume Improvement Dashboard")

            improvements = {
                "Skills": 20,
                "Experience": 15,
                "Education": 10,
                "Keywords Added": 25,
                "Achievements": 10,
                "Formatting": 20,
            }

            df = pd.DataFrame(list(improvements.items()), columns=["Area", "Improvement (%)"])
            fig1, ax1 = plt.subplots()
            ax1.pie(df["Improvement (%)"], labels=df["Area"], autopct="%1.1f%%", startangle=90)
            ax1.axis("equal")
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots()
            ax2.bar(df["Area"], df["Improvement (%)"], color='skyblue')
            plt.xticks(rotation=30)
            st.pyplot(fig2)

            st.download_button("⬇️ Download Data as Excel", data=df.to_csv(index=False), file_name="resume_dashboard.csv")

            # -------- GitHub Upload (optional) --------
            if st.checkbox("Upload visuals + Excel to GitHub"):
                github_token = st.text_input("Enter GitHub Access Token", type="password")
                if github_token:
                    g = Github(github_token)
                    repo = g.get_repo("mdayanahmed/Cover-letter-generator")
                    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                    # Excel Upload
                    excel_bytes = BytesIO()
                    df.to_excel(excel_bytes, index=False)
                    repo.create_file(f"dashboard/dashboard_{now}.xlsx", "upload dashboard", excel_bytes.getvalue())

                    # Pie Chart Upload
                    pie_img = BytesIO()
                    fig1.savefig(pie_img, format='png')
                    repo.create_file(f"dashboard/pie_{now}.png", "upload pie", pie_img.getvalue())

                    # Bar Chart Upload
                    bar_img = BytesIO()
                    fig2.savefig(bar_img, format='png')
                    repo.create_file(f"dashboard/bar_{now}.png", "upload bar", bar_img.getvalue())

                    st.success("✅ Uploaded to GitHub")

    # ------------------- JOB TITLES -------------------
    if st.button("Suggest Job Titles"):
        with st.spinner("Finding matching roles..."):
            prompt = f"""
            Based on the resume below, suggest 3–5 suitable job titles or roles.
            Resume: {resume_text}
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            st.markdown("### Suggested Job Roles")
            st.markdown(response.choices[0].message.content)

    # ------------------- ATS SCORE -------------------
    if st.button("Check ATS Match Score"):
        with st.spinner("Calculating ATS match..."):
            prompt = f"""
            You are an ATS engine. Compare this resume and job description:
            - Give a match percentage (0-100%)
            - List of matching & missing keywords
            - Short feedback
            Resume: {resume_text}
            Job Description: {job_text}
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            st.markdown("### ATS Compatibility Report")
            st.markdown(response.choices[0].message.content)

    # ------------------- INTERVIEW QUESTIONS -------------------
    if st.button("Generate Interview Questions"):
        with st.spinner("Preparing questions..."):
            prompt = f"""
            You are an interview coach. Based on the job description, generate 5 likely interview questions.
            Job Description: {job_text}
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            st.markdown("### Potential Interview Questions")
            st.markdown(response.choices[0].message.content)

else:
    st.info("Please upload or paste both Resume and Job Description.")
