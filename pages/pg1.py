import streamlit as st

st.markdown("<h1 style='text-align: center;'>TaxFlowLK</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Welcome to your tax filing journey!</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Create your annual tax return <br><b>Simply & Responsibly</b></p>", unsafe_allow_html=True)


if st.button("Start Now"):
    st.switch_page("pages/pg2.py")  # Redirect to the next page
