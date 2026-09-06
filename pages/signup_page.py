import streamlit as st
from db import add_user, init_db

init_db()

st.markdown("<h1 style='text-align: center;'>Welcome <br> to <br> TaxFlowLK</h1>",
            unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>let's get started with your tax filing journey!</h3>",
            unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>create your account</p>", unsafe_allow_html=True)

full_name = st.text_input("Enter your full name", key="full_name")
email = st.text_input("Enter your email address", key="email")
nic_number = st.text_input("Enter your National Identity Card number", key="nic_number")
phone_number = st.text_input("Enter your phone number", key="phone_number")
password = st.text_input("Create your password", type="password", key="password")
confirm_password = st.text_input("Confirm your password", type="password", key="confirm_password")

if st.button("Create Account"):
    if not full_name or not email or not password or not confirm_password or not nic_number or not phone_number:
        st.error("Please fill in all fields.")
    elif password != confirm_password:
        st.error("Passwords do not match!")
    elif add_user(full_name, email, password, nic_number, phone_number):
        st.success("Account created successfully!")
        st.switch_page("pages/login_page.py")
    else:
        st.error("Error creating account. Email may already be in use.")

already_have_account = st.checkbox("Already have an account? Log in here.")
if already_have_account:
    st.switch_page("pages/login_page.py")