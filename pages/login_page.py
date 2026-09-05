import streamlit as st
import psycopg2 
import hashlib
from psycopg2.extensions import new_type, register_type, DECIMAL

def get_connection():
    return psycopg2.connect(**st.secrets["postgres"])

def cast_numeric_to_float(value, cur):
    return float(value) if value is not None else None

DEC2FLOAT = new_type(DECIMAL.values, 'DEC2FLOAT', cast_numeric_to_float)
register_type(DEC2FLOAT)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(email, password):
    conn = get_connection()
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, hashed_password))
    user = c.fetchone()
    c.close()
    conn.close()
    return user


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
        st.session_state.user_id = user[0]  # Store user ID in session state
        st.session_state.logged_in = True  # Set logged_in flag to True
        st.switch_page("pages/pg1.py")  # Redirect to the next page
    else:
        st.error("Invalid email or password. Please try again.")

not_registered = st.checkbox("Don't have an account? Sign up here.")
if not_registered:
    st.switch_page("pages/signup_page.py")