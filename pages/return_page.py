import streamlit as st
from db import get_connection, get_income_summary, calculate_tax

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state.user_id
tax_year = st.session_state.tax_year
summary = get_income_summary(user_id, tax_year)
result = calculate_tax(user_id, tax_year)

st.markdown("<h1 style='text-align:center;'>Filing Your Return — Step by Step</h1>", unsafe_allow_html=True)

st.divider()
st.subheader("Step 1: Log in")
st.image("pages/pictures/1st.png", width=600)
st.markdown("Select **Individual Taxpayer**, click 'Proceed to Login', then enter your TIN, IRD PIN, and the captcha text shown.")
st.image("pages/pictures/2nd.png")
st.divider()
st.subheader("Step 2: Open Individual Income Tax")
st.image("pages/pictures/3rd.png", width=600)
st.markdown("Click **Individual Income Tax (IIT)** in the left menu.")

st.divider()
st.subheader("Step 3: Select the year")
st.image("pages/pictures/4th.png", width=600)
st.info(f"Select tax year: **{tax_year}**, then click 'Proceed'.")

st.divider()
st.subheader("Step 4: Select your income sources")
st.image("pages/pictures/5th.png", width=600)
st.markdown("Tick the boxes matching what you told us earlier:")
flags = st.session_state.get("income_flags", {})
labels = {
    "primary": "1. Employment income (Primary employment)",
    "secondary": "2. Employment income (Secondary employment)",
    "solar": "3. Income from resident solar panel",
    "fixed_deposits": "4. Interest Income (AIT deducted by Bank & Finance Institutions)",
}
for key, label in labels.items():
    st.write(("✅ " if flags.get(key) else "⬜ ") + label)

st.divider()
st.subheader("Step 5: Employment income")
st.image("pages/pictures/7th.png", width=600)

if summary["primary"]:
    name, tin, rem, exempt = summary["primary"]
    st.success(f"**Primary employment**\n\n- Employer name: `{name}`\n- TIN of employer: `{tin}`\n- Remuneration: Rs. {rem:,.2f}" +
               (f"\n- Exempt/excluded income: Rs. {exempt:,.2f}" if exempt else ""))
if summary["secondary"]:
    name, tin, rem, exempt = summary["secondary"]
    st.success(f"**Secondary employment**\n\n- Employer name: `{name}`\n- TIN of employer: `{tin}`\n- Remuneration: Rs. {rem:,.2f}" +
               (f"\n- Exempt/excluded income: Rs. {exempt:,.2f}" if exempt else ""))
st.caption("Note: APIT already paid is filled in automatically by the IRD system — you don't need to enter it.")

st.divider()
st.subheader("Step 6: Interest income")
st.image("pages/pictures/10th.png", width=600)
if summary["interest_rows"]:
    for i, (bank, tin, interest, wht, balance) in enumerate(summary["interest_rows"], start=1):
        st.success(
            f"**Interest income {i}** ({bank})\n\n"
            f"- Source/type: `I-INTEREST`\n- TIN of withholding agent: `{tin}`\n"
            f"- Net interest received: Rs. {interest:,.2f}\n- AIT/WHT deducted: Rs. {wht:,.2f}"
        )
    st.caption("The certificate number, withholding agent's name, and date of payment come from your WHT certificate — enter those directly on the portal.")
else:
    st.write("No interest income recorded — skip this section.")

st.divider()
st.subheader("Step 7: Solar panel relief")
st.image("pages/pictures/13th.png", width=600)
if summary["solar_income"]:
    st.success(
        f"- Total expenditure / brought forward balance to enter: Rs. {summary['remaining_expenditure_to_enter']:,.2f}\n"
        f"- Income from solar panel: Rs. {summary['solar_income']:,.2f}"
    )
    st.caption("The portal will calculate your claimable relief automatically once you enter the figure above — you don't need to calculate it yourself.")
else:
    st.write("No solar panel income recorded — skip this section.")

st.divider()
st.subheader("Step 8: Check the summary")
st.image("pages/pictures/15th.png", width=600)
st.markdown("Compare the portal's auto-calculated summary against our estimate below. If they differ significantly, double check your entries before continuing.")
st.write(f"Our estimate — Taxable income: Rs. {result['taxable_income']:,.2f} | Tax payable: Rs. {result['gross_tax']:,.2f} | Credits: Rs. {result['wht_credit']:,.2f}")
if result["net_tax_payable"] > 0:
    st.error(f"Balance tax payable (estimate): Rs. {result['net_tax_payable']:,.2f}")
else:
    st.success(f"Refund due (estimate): Rs. {result['refund_due']:,.2f}")

st.divider()
st.subheader("Step 9: Statement of Assets & Liabilities")
st.image("pages/pictures/18th.png", width=600)
st.markdown(
    "This section is filled in directly on the portal, based on your own records — we don't collect most of this data in the app. "
    "You'll need: property and vehicle details (if any), shares/investments, cash in hand, loans given, "
    "jewellery value, and any liabilities (e.g. loans owed). Only fill in sections that apply to you."
)

if summary["interest_rows"]:
    st.markdown("**Bank balances (from your saved interest income entries) — enter these under 'ii. Bank balances including term deposits':**")
    st.image("pages/pictures/20tth.png", width=600)
    for bank, tin, interest, wht, balance in summary["interest_rows"]:
        st.success(
            f"**{bank}**\n\n"
            f"- Account No.: enter manually (not stored in the app)\n"
            f"- Amount invested: enter manually if applicable\n"
            f"- Interest (Rs.): {interest:,.2f}\n"
            f"- Balance (Rs.): {balance:,.2f}"
        )
else:
    st.write("No saved bank accounts to show here.")

st.divider()
st.subheader("Step 10: Declaration")
st.write("Dont forget to print before submit the return and uplod supporting documents")
st.image("pages/pictures/32nd.png", width=600)
conn = get_connection()
c = conn.cursor()
c.execute("SELECT full_name, email, nic_number, phone_number FROM users WHERE id=%s", (user_id,))
full_name, email, nic, phone = c.fetchone()
c.close()
conn.close()
st.markdown("Leave 'prepared by an approved accountant' as **No**, unless someone else is filing on your behalf. Fill Part B with your own details:")
st.success(
    f"- Full name: `{full_name}`\n- Email: `{email}`\n"
    f"- NIC/Passport number: `{nic or 'Not on file — enter manually'}`\n"
    f"- Phone: `{phone or 'Not on file — enter manually'}`\n"
    f"- Date: today's date"
)

st.divider()
st.subheader("Step 11: Submit")
st.markdown(
    "Choose whether to upload supporting documents now, later, or skip if not required. "
    "Then click **Submit** to file your return. Click **Print** afterward to save a copy for your records."
)

st.divider()
st.info("Filing deadline for this year of assessment: **30 November 2026**.")

st.markdown("<h1 style='text-align: center;'>Thank you for choosing us</h1>", unsafe_allow_html=True)