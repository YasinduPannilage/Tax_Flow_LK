import streamlit as st
import sqlite3  


st.markdown("<h1 style='text-align: center;'>Welcome Back<br> to <br> TaxFlowLK</h1>", 
            unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Please log in to your account</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Enter your credentials below</p>", unsafe_allow_html=True)

email = st.text_input("Enter your email address", key="email")
password = st.text_input("Enter your password", type="password", key="password")   
login_button = st.button("Log In")