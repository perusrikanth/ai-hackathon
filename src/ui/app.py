import streamlit as st
import requests


API = "http://localhost:8000"


st.title("🤖 Browser Automation AI Agent")


# Step 1: Flow Discovery
st.header("1. Discover Website Flow")
url = st.text_input("Enter website URL:")


if st.button("Discover Flow"):
    res = requests.post(f"{API}/discover-flow", json={"url": url})
    st.json(res.json())


# Step 2: Generate Script
st.header("2. Generate Automation Script")
flow = st.text_area("Paste flow description:")


if st.button("Generate Script"):
    res = requests.post(f"{API}/generate-script", json={"flow": flow})
    st.code(res.text)


# Step 3: Execute Script
st.header("3. Execute Script")
script = st.text_area("Paste script:")


if st.button("Run Script"):
    res = requests.post(f"{API}/execute-script", json={"script": script})
    st.json(res.json())


# Step 4: Error Diagnosis
st.header("4. Diagnose Errors")
stderr = st.text_area("Paste stderr:")


if st.button("Diagnose Error"):
    res = requests.post(f"{API}/diagnose", json={"stderr": stderr, "script": script})
    st.json(res.json())