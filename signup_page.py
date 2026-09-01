#Tax Flow LK
import streamlit as st
#logging page

st.set_page_config(
    page_title="TaxFlowLK",
    layout="wide"
)
st.markdown("<h1 style='text-align: center;'>Welcome <br> to <br> TaxFlowLK</h1>", 
            unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>let's get started with your tax filing journey!</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>create your account</p>", unsafe_allow_html=True)

st.text_input("Enter your full name", key="full_name")
st.text_input("Enter your email address", key="email")
st.text_input("Create your password", type="password", key="password")
st.text_input("Confirm your password", type="password", key="confirm_password")

st.button("Create Account")

