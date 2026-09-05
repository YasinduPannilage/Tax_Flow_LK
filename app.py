import streamlit as st


home_page = st.Page("pages/home_page.py", title="home")
signup_page = st.Page("pages/signup_page.py", title="Sign Up")
login_page = st.Page("pages/login_page.py", title="Login")
pg1 = st.Page("pages/pg1.py", title="Page 1")
pg2 = st.Page("pages/pg2.py", title="Page 2")
income_details_page = st.Page("pages/income_details.py", title="Income Details")
tax_summary_page = st.Page("pages/tax_summary.py", title="Tax Summary")
tax_return_page1 = st.Page("pages/return_page1.py", title="Tax Return1")
tax_return_page2 = st.Page("pages/return_page2.py", title="Tax Return2")
tax_return_page3 = st.Page("pages/return_page3.py", title="Tax Return3")

pg = st.navigation([ home_page, signup_page, login_page, pg1, pg2, income_details_page, tax_summary_page, tax_return_page1, tax_return_page2, tax_return_page3])



pg.run()


