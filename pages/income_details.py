import streamlit as st
from db import save_primary, save_secondary, save_interest_income, save_solar, get_prior_cumulative_relief

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

if "income_flags" not in st.session_state:
    st.warning("Please complete the income source confirmation first.")
    st.stop()

flags = st.session_state.income_flags
tax_year = st.session_state.tax_year
user_id = st.session_state.user_id

st.markdown(f"<h2 style='text-align:center;'>Income details — {tax_year}</h2>", unsafe_allow_html=True)

# ---- Primary employment ----
if flags["primary"]:
    st.subheader("Primary employment")
    st.caption("It's best to have your T10 form on hand to answer this.")
    primary_employer = st.text_input("Employer / company name", key="primary_employer")
    primary_tin = st.text_input("TIN of the employer", key="primary_tin")
    primary_remuneration = st.number_input("Remuneration (Rs.)", min_value=0.0, step=1000.0, key="primary_remuneration")

    primary_has_exempt_income = st.radio("Do you have any exempt / excluded income from this employment?", ["No", "Yes"], key="primary_has_exempt_income")
    primary_exempt_amount = 0.0
    if primary_has_exempt_income == "Yes":
        primary_exempt_amount = st.number_input("Exempt / excluded income (Rs.)", min_value=0.0, step=1000.0, key="primary_exempt_amount")

# ---- Secondary employment ----
if flags["secondary"]:
    st.subheader("Secondary employment")
    secondary_employer = st.text_input("Employer / company name", key="secondary_employer")
    secondary_tin = st.text_input("TIN of the employer", key="secondary_tin")
    secondary_remuneration = st.number_input("Remuneration (Rs.)", min_value=0.0, step=1000.0, key="secondary_remuneration")

    secondary_has_exempt_income = st.radio("Do you have any exempt / excluded income from this employment?", ["No", "Yes"], key="secondary_has_exempt_income")
    secondary_exempt_amount = 0.0
    if secondary_has_exempt_income == "Yes":
        secondary_exempt_amount = st.number_input("Exempt / excluded income (Rs.)", min_value=0.0, step=1000.0, key="secondary_exempt_amount")

# ---- Interest income (dynamic list) ----
if flags["fixed_deposits"]:
    st.subheader("Interest income")
    st.caption("This will be entered as I-Interest on the return. Have your WHT certificate ready.")

    if "interest_rows" not in st.session_state:
        st.session_state.interest_rows = [{}]

    for i, row in enumerate(st.session_state.interest_rows):
        with st.container(border=True):
            st.markdown(f"**Interest income {i + 1}**")
            col1, col2 = st.columns(2)
            with col1:
                row["bank_name"] = st.text_input("Bank / financial institution", key=f"int_bank_{i}", value=row.get("bank_name", ""))
                row["institution_tin"] = st.text_input("TIN of the withholding agent", key=f"int_tin_{i}", value=row.get("institution_tin", ""))
                row["balance_as_at"] = st.number_input("Balance as at 31.03.2026 (Rs.)", min_value=0.0, step=1000.0, key=f"int_bal_{i}", value=row.get("balance_as_at", 0.0))
            with col2:
                row["interest"] = st.number_input("Net interest received (Rs.)", min_value=0.0, step=100.0, key=f"int_amt_{i}", value=row.get("interest", 0.0))
                row["wht_deducted"] = st.number_input("AIT/WHT deducted by the agent (Rs.)", min_value=0.0, step=100.0, key=f"int_wht_{i}", value=row.get("wht_deducted", 0.0))

            if len(st.session_state.interest_rows) > 1:
                if st.button("Remove this entry", key=f"int_remove_{i}"):
                    st.session_state.interest_rows.pop(i)
                    st.rerun()

    if st.button("Add another interest income entry"):
        st.session_state.interest_rows.append({})
        st.rerun()

# ---- Solar panel income ----
if flags["solar"]:
    st.subheader("Solar panel income")
    st.caption("Relief up to Rs. 600,000 per year, capped by total remaining expenditure not yet claimed.")

    solar_expenditure = st.number_input("Total expenditure on solar panel installation (Rs.)", min_value=0.0, step=1000.0, key="solar_expenditure")
    solar_income = st.number_input("Income from solar panel (Rs.)", min_value=0.0, step=1000.0, key="solar_income")

    prior_cumulative = get_prior_cumulative_relief(user_id, tax_year)
    remaining_expenditure = max(solar_expenditure - prior_cumulative, 0)
    relief_this_year = min(600_000, remaining_expenditure)
    new_cumulative = prior_cumulative + relief_this_year

    st.info(
        f"Already claimed in prior years: Rs. {prior_cumulative:,.2f}\n\n"
        f"Relief claimable this year: Rs. {relief_this_year:,.2f}\n\n"
        f"Remaining expenditure after this year: Rs. {max(solar_expenditure - new_cumulative, 0):,.2f}"
    )

# ---- Save everything ----
if st.button("Save and continue"):
    if flags["primary"]:
        save_primary(user_id, tax_year, primary_employer, primary_tin, primary_has_exempt_income, primary_exempt_amount, primary_remuneration)
    if flags["secondary"]:
        save_secondary(user_id, tax_year, secondary_employer, secondary_tin, secondary_has_exempt_income, secondary_exempt_amount, secondary_remuneration)
    if flags["fixed_deposits"]:
        save_interest_income(user_id, tax_year, st.session_state.interest_rows)
    if flags["solar"]:
        save_solar(user_id, tax_year, solar_expenditure, solar_income, relief_this_year, new_cumulative)

    st.success("Income details saved!")
    st.switch_page("pages/tax_summary.py")