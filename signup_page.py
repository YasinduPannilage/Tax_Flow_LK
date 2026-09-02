#Tax Flow LK

import sqlite3
import hashlib
import streamlit as st



def init_db():
    # Connects to your database file
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Create the table with the exact columns your INSERT statement expects
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()




init_db()  # Initialize the database when the module is imported

 #hash password for security

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


 #insert user data into the database
def add_user(full_name, email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
              (full_name, email, hashed_password))
    conn.commit()
    conn.close()
    return True

  

#signup page

st.set_page_config(
    page_title="TaxFlowLK",
    layout="wide"
)
st.markdown("<h1 style='text-align: center;'>Welcome <br> to <br> TaxFlowLK</h1>", 
            unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>let's get started with your tax filing journey!</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>create your account</p>", unsafe_allow_html=True)

full_name = st.text_input("Enter your full name", key="full_name")
email = st.text_input("Enter your email address", key="email")
password = st.text_input("Create your password", type="password", key="password")
confirm_password = st.text_input("Confirm your password", type="password", key="confirm_password")

if st.button("Create Account"):
    full_name = st.session_state.full_name
    email = st.session_state.email
    password = st.session_state.password
    confirm_password = st.session_state.confirm_password

    if password != confirm_password:
        st.error("Passwords do not match!")
    else:
        if add_user(full_name, email, password):
            st.success("Account created successfully!")
        else:
            st.error("Error creating account.")
