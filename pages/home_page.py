#home page
import streamlit as st



st.html("""
        <h2 style="color: #f5f5f5; text-align: center";>Welcome</h2>
        <h3 style="color: #f5f5f5; text-align: center";>to</h3>
        <h1 style="color: #8B0000; text-align: center";>TaxFlowLK</h1>
        <p style="color: #f5f5f5; text-align: center";>Your one-stop solution for tax management and filing.</p>   
""")

if st.button("Get Standard"):
    st.switch_page("pages/signup_page.py")

 #does not work the redirect to signup page
