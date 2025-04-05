# dashboard.py

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import requests
import base64
import io
import os

# ------------------- Sample Improvement Data (replace with real later) -------------------
def get_sample_improvement_data():
    return {
        "Skills": 20,
        "Experience": 30,
        "Summary": 25,
        "Keywords": 25
    }

# ------------------- Plot Pie Chart -------------------
def generate_pie_chart(data):
    fig, ax = plt.subplots()
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title("Resume Improvement Areas")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf

# ------------------- Plot Bar Chart -------------------
def generate_bar_chart(data):
    fig, ax = plt.subplots()
    ax.bar(data.keys(), data.values(), color='skyblue')
    plt.ylabel("Improvement (%)")
    plt.title("Resume Improvement Breakdown")
    plt.xticks(rotation=45)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf

# ------------------- Export Excel -------------------
def export_to_excel(data_dict):
    df = pd.DataFrame(data_dict.items(), columns=["Area", "Improvement (%)"])
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Improvements")
    excel_buf.seek(0)
    return excel_buf

# ------------------- Upload File to GitHub -------------------
def upload_to_github(filename, file_content):
    github_token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    folder = st.secrets["UPLOAD_FOLDER"]

    api_url = f"https://api.github.com/repos/{repo}/contents/{folder}/{filename}"
    encoded_content = base64.b64encode(file_content.read()).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "message": f"Add {filename}",
        "content": encoded_content
    }

    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 201:
        st.success(f"Uploaded {filename} to GitHub ✅")
    else:
        st.error(f"Failed to upload {filename} ❌: {response.text}")

# ------------------- Main Function to Call -------------------
def run_dashboard():
    st.header("📈 Smart Resume Improvement Dashboard")

    data = get_sample_improvement_data()  # Replace with actual improvement data
    st.write("### 📊 Improvement Data:")
    st.json(data)

    pie_chart = generate_pie_chart(data)
    bar_chart = generate_bar_chart(data)
    excel_file = export_to_excel(data)

    st.image(pie_chart, caption="Pie Chart", use_column_width=True)
    st.image(bar_chart, caption="Bar Chart", use_column_width=True)

    st.download_button("⬇️ Download Excel", data=excel_file, file_name="Resume_Improvement.xlsx")

    # Upload to GitHub
    upload_to_github("resume_pie_chart.png", pie_chart)
    upload_to_github("resume_bar_chart.png", bar_chart)
    upload_to_github("resume_improvement.xlsx", excel_file)
