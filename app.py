import streamlit as st


home_page = st.Page("pages/home_page.py", title="home")
signup_page = st.Page("pages/signup_page.py", title="Sign Up")
login_page = st.Page("pages/login_page.py", title="Login")
pg1 = st.Page("pages/pg1.py", title="Page 1")
pg2 = st.Page("pages/pg2.py", title="Page 2")
pg = st.navigation([ home_page, signup_page, login_page, pg1, pg2])
pg.run()


