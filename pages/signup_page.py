#Tax Flow LK
import psycopg2
import hashlib
import streamlit as st

def get_connection():
    return psycopg2.connect(**st.secrets["postgres"])

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    c.close()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(full_name, email, password):
    conn = get_connection()
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute(
            "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
            (full_name, email, hashed_password)
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    finally:
        c.close()
        conn.close()

st.markdown("<h1 style='text-align: center;'>Welcome <br> to <br> TaxFlowLK</h1>",
            unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>let's get started with your tax filing journey!</h3>",
            unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>create your account</p>", unsafe_allow_html=True)

full_name = st.text_input("Enter your full name", key="full_name")
email = st.text_input("Enter your email address", key="email")
password = st.text_input("Create your password", type="password", key="password")
confirm_password = st.text_input("Confirm your password", type="password", key="confirm_password")

if st.button("Create Account"):
    if not full_name or not email or not password or not confirm_password:
        st.error("Please fill in all fields.")
    elif password != confirm_password:
        st.error("Passwords do not match!")
    elif add_user(full_name, email, password):
        st.success("Account created successfully!")
        st.switch_page("pages/login_page.py")
    else:
        st.error("Error creating account. Email may already be in use.")

already_have_account = st.checkbox("Already have an account? Log in here.")
if already_have_account:
    st.switch_page("pages/login_page.py")