#home page
import streamlit as st



st.html("""
    <div style="background-color: #f5f5f5; padding: 100px; border-radius: 20px; text-align: center;">
        <h2 style="color: #333;">Welcome</h2>
        <h3 style="color: #333;">to</h3>
        <h1 style="color: #8B0000;">TaxFlowLK</h1>
        <p style="color: #666;">Your one-stop solution for tax management and filing.</p>
        <style>
        .get-started {
            background-color: #000000;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px 20px;
            }
        .get-started:hover {
            background-color: #ffffff;
            color: #000000;
            }
        </style>,
        <button 
        class="get-started"
        onclick="window.location.href='/signup_page'">
        Get Started
        </button>
         
    </div>
""")
