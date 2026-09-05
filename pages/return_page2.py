import streamlit as st

st.html("<h4 style='text-align:center;'>After that Fill your Taxpayer Identification Number(TIN) and IRD pin in the respective fields and enter the captcha code as shown below </h4>")
st.image("pages/pictures/2nd.png")
st.html("<h4 style='text-align:center;'>Then click on the 'login' button to proceed to the next step</h4>")
if st.button("next"):
    st.switch_page("pages/return_page3.py")
    