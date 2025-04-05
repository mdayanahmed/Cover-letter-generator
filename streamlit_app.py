import streamlit as st
import openai
import os
import fitz  # PyMuPDF
from docx import Document
from fpdf import FPDF
import pytesseract
from PIL import Image

st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("AI Cover Letter & Resume Optimizer")

st.markdown("Upload your resume & job description (text/pdf/docx/image) to generate:")
st.markdown("- Personalized **Cover Letter**")
st.markdown("- Tailored **Resume Suggestions**")
st.markdown("- Matching **Job Roles**")
st.markdown("- **ATS Compatibility Score**")
st.markdown("- Likely **Interview Questions**")

# API Key
user_api_key = st.text_input("Enter your OpenAI API Key", type="password")
if not user_api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

openai.api_key = user_api_key

# File/Text Upload for Resume
st.subheader("Upload Resume")
resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
resume_text_input = st.text_area("Or Paste Resume Text", height=200)

# File/Text Upload for Job Description
st.subheader("Upload Job Description")
jd_file = st.file_uploader("Upload Job Description (PDF, DOCX, TXT, or Image)", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
jd_text_input = st.text_area("Or Paste Job Description Text", height=200)

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

resume_text = resume_text_input or extract_text_from_file(resume_file)
job_text = jd_text_input or extract_text_from_file(jd_file)

if resume_text and job_text:
    # COVER LETTER
    if st.button("Generate Cover Letter"):
        with st.spinner("Generating your cover letter..."):
            prompt = f"""
            Write a professional and enthusiastic cover letter based on the resume and job description below.

            Resume:
            {resume_text}

            Job Description:
            {job_text}
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                cover_letter = response.choices[0].message.content
                st.success("Cover Letter Generated!")
                st.text_area("Preview", cover_letter, height=300)

                doc = Document()
                doc.add_heading("Cover Letter", 0)
                doc.add_paragraph(cover_letter)
                doc.save("Cover_Letter.docx")

                with open("Cover_Letter.docx", "rb") as file:
                    st.download_button("Download Cover Letter (.docx)", file, "Cover_Letter.docx")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # RESUME SUGGESTIONS
    if st.button("Suggest Resume Improvements"):
        with st.spinner("Optimizing resume..."):
            prompt = f"""
            You're a resume coach. Based on the resume and job description below, suggest specific improvements to tailor the resume for the job.

            Resume:
            {resume_text}

            Job Description:
            {job_text}
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6
                )
                suggestions = response.choices[0].message.content
                st.markdown("### Resume Optimization Suggestions")
                st.markdown(suggestions)
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # JOB TITLES
    if st.button("Suggest Job Titles"):
        with st.spinner("Finding best-matching roles..."):
            prompt = f"""
            Based on the resume below, suggest 3–5 suitable job titles or roles.

            Resume:
            {resume_text}
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                jobs = response.choices[0].message.content
                st.markdown("### Suggested Job Roles")
                st.markdown(jobs)
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # ATS MATCH
    if st.button("Check ATS Match Score"):
        with st.spinner("Analyzing ATS compatibility..."):
            prompt = f"""
            You are an ATS engine. Compare this resume and job description:
            - Give a match percentage (0-100%)
            - List of matching & missing keywords
            - Short feedback

            Resume:
            {resume_text}

            Job Description:
            {job_text}
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
                ats = response.choices[0].message.content
                st.markdown("### ATS Compatibility Report")
                st.markdown(ats)
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # INTERVIEW QUESTIONS
    if st.button("Generate Interview Questions"):
        with st.spinner("Preparing likely interview questions..."):
            prompt = f"""
            You are an interview coach. Based on the job description, generate 5 likely interview questions.

            Job Description:
            {job_text}
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6
                )
                questions = response.choices[0].message.content
                st.markdown("### Potential Interview Questions")
                st.markdown(questions)
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info("Please upload or paste both resume and job description to enable features.")
