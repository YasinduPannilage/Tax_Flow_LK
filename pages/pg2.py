import streamlit as st

st.markdown("<h1 style='text-align: center;'>" "For the <b>2025/2026</b> tax year</h1>", unsafe_allow_html=True)

primary_employment = st.radio("Do you have an income from primary employment?", ["Yes", "No"], key="primary_employment")
secondary_employment = st.radio("Do you have an income from Secondary employment?",["Yes","No"], key="secondary_employment")
solar_panel_income = st.radio("Do you have an income from resident solar panel?", ["Yes", "No"], key="solar_panel_income")
fixed_savings_income = st.radio("Do you have an income from fixed deposits or savings accounts??", ["Yes", "No"], key="fixed/savings_income")

if primary_employment == "yes":
    st.switch_page("pages/income/primary_employment.py")  

