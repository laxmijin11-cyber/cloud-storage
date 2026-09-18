import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Cloud Storage")
st.title("☁️ Cloud Storage with Versioning")

# Login
if "token" not in st.session_state:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        res = requests.post(f"{API_URL}/login", params={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.session_state.user = username
            st.rerun()
    st.stop()

# Upload
st.subheader("📤 Upload File")
file = st.file_uploader("Choose a file")
if file and st.button("Upload"):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    res = requests.post(f"{API_URL}/upload", files={"file": file}, headers=headers)
    st.success(f"Uploaded! Version: {res.json()['version']}")

# List versions
st.subheader("📂 File Versions")
filename = st.text_input("Enter filename to view versions")
if filename and st.button("List Versions"):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    res = requests.get(f"{API_URL}/versions/{filename}", headers=headers)
    for v in res.json():
        st.write(v)
        if st.button(f"Download {v}", key=v):
            dl = requests.get(f"{API_URL}/download/{v}", headers=headers)
            st.download_button("Download", dl.json()["content"], file_name=v.split("/")[-1])