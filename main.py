import streamlit as st
from model import report_to_record
from pat_doc import mapping_patient_to_doctor

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Report to Record", "Mapping Patient to Doctor"])

if page == "Report to Record":
    report_to_record()
elif page == "Mapping Patient to Doctor":
    mapping_patient_to_doctor()
