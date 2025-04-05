import streamlit as st
import openai
from docx import Document

# OpenAI API Key (Isko deploy karne ke baad Streamlit Secrets me daalna)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-api-key-here")

st.title("AI Cover Letter Generator")
st.write("Generate a personalized cover letter using your resume and job description.")

# User inputs
resume_text = st.text_area("Paste Your Resume", height=200)
job_description = st.text_area("Paste Job Description", height=200)

if st.button("Generate Cover Letter"):
    with st.spinner("Generating your cover letter..."):

        prompt = f"""
        You are an expert career assistant. Write a personalized cover letter based on the following resume and job description.

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        The tone should be professional and enthusiastic.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        cover_letter = response.choices[0].message.content

        # Save as Word file
        doc = Document()
        doc.add_heading('Cover Letter', 0)
        doc.add_paragraph(cover_letter)
        doc.save("Cover_Letter.docx")

        # Show and download
        st.success("Cover Letter Generated!")
        st.text_area("Preview:", cover_letter, height=300)

        with open("Cover_Letter.docx", "rb") as file:
            st.download_button(
                label="Download Cover Letter (.docx)",
                data=file,
                file_name="Cover_Letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
