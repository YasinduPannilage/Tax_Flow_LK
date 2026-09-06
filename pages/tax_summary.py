import streamlit as st
from db import calculate_tax

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state.user_id
tax_year = st.session_state.tax_year

result = calculate_tax(user_id, tax_year)

st.markdown(f"<h2 style='text-align:center;'>Tax Summary — {tax_year}</h2>", unsafe_allow_html=True)

st.write(f"**Assessable income:** Rs. {result['assessable_income']:,.2f}")
st.write(f"**Personal relief:** Rs. {result['personal_relief']:,.2f}")
st.write(f"**Solar relief claimed:** Rs. {result['solar_relief_estimate']:,.2f}")
st.write(f"**Taxable income:** Rs. {result['taxable_income']:,.2f}")
st.write(f"**Gross tax payable:** Rs. {result['gross_tax']:,.2f}")
st.write(f"**WHT already deducted (credit):** Rs. {result['wht_credit']:,.2f}")

if result["net_tax_payable"] > 0:
    st.error(f"**Balance tax payable:** Rs. {result['net_tax_payable']:,.2f}")
else:
    st.success(f"**Refund due:** Rs. {result['refund_due']:,.2f}")

if st.button("File tax return"):
    st.switch_page("pages/return_page.py")