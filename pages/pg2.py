import streamlit as st
from db import save_income_sources

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

tax_year = st.session_state.get("tax_year", "2025/2026")
st.markdown(f"<h2 style='text-align:center;'>For the {tax_year} tax year</h2>", unsafe_allow_html=True)

primary = st.radio("Do you earn a salary from a primary employment?", ["Yes", "No"], key="q_primary")
secondary = st.radio("Do you earn a salary from a secondary employment?", ["Yes", "No"], key="q_secondary")
fixed_deposits = st.radio("Do you have any fixed deposits or savings account?", ["Yes", "No"], key="q_fd")
solar = st.radio("Do you have any income from resident solar panels?", ["Yes", "No"], key="q_solar")

st.caption("Sadly we are currently available only for these income sources.")

if st.button("Next"):
    flags = {
        "primary": primary == "Yes",
        "secondary": secondary == "Yes",
        "fixed_deposits": fixed_deposits == "Yes",
        "solar": solar == "Yes",
    }
    save_income_sources(st.session_state.user_id, tax_year, flags)

    st.session_state.income_flags = flags
    st.session_state.tax_year = tax_year

    st.switch_page("pages/income_details.py")
    