import streamlit as st
from db import get_user

st.markdown("<h1 style='text-align: center;'>Welcome Back<br> to <br> TaxFlowLK</h1>",
            unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Please log in to your account</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Enter your credentials below</p>", unsafe_allow_html=True)

email = st.text_input("Enter your email address", key="email")
password = st.text_input("Enter your password", type="password", key="password")

if st.button("Log In"):
    email = st.session_state.email
    password = st.session_state.password

    user = get_user(email, password)

    if user:
        st.success("Login successful!")
        st.session_state.user_id = user[0]
        st.session_state.logged_in = True
        st.switch_page("pages/pg1.py")
    else:
        st.error("Invalid email or password. Please try again.")

not_registered = st.checkbox("Don't have an account? Sign up here.")
if not_registered:
    st.switch_page("pages/signup_page.py")