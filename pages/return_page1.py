import streamlit as st


st.html(

    "<h3 style='text-align:center;'>Lets file your own tax return by yourself!</h3>"
    "<h4 style='text-align:center;'>We will guide you through the process step by step.</h4>"
    "<p style ='text-align:center;'>By clicking the link below, you will be redirected to the official e-services portal of the Inland Revenue Department (IRD) of Sri Lanka. There, you can start the process of filing your tax return online.</p>"
    "<a style='display: block; text-align: center;' href='https://www.ird.gov.lk/en/eServices/SitePages/Access%20To%20e-Services.aspx?menuid=1803' target='_blank'>start the process</a>"
    "<p style='text-align:center;'>After clicking the link above, scroll down to the bottom of the page <br> then select 'individual tax payer' and click 'proceed to login'</p>"
)

st.image("pages/pictures/1st.png")
if st.button("next"):
    st.switch_page("pages/return_page2.py")

