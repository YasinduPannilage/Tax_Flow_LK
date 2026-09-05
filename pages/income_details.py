import streamlit as st
import psycopg2
from psycopg2.extensions import new_type, register_type, DECIMAL

def get_connection():
    return psycopg2.connect(**st.secrets["postgres"])

def cast_numeric_to_float(value, cur):
    return float(value) if value is not None else None

DEC2FLOAT = new_type(DECIMAL.values, 'DEC2FLOAT', cast_numeric_to_float)
register_type(DEC2FLOAT)

def save_primary(user_id, tax_year, employer_name, employer_tin, remuneration):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO primary_employment (user_id, tax_year, employer_name, employer_tin, remuneration)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id, tax_year)
        DO UPDATE SET employer_name = EXCLUDED.employer_name,
                      employer_tin = EXCLUDED.employer_tin,
                      remuneration = EXCLUDED.remuneration
    """, (user_id, tax_year, employer_name, employer_tin, remuneration))
    conn.commit()
    c.close()
    conn.close()

def save_secondary(user_id, tax_year, employer_name, employer_tin, remuneration):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO secondary_employment (user_id, tax_year, employer_name, employer_tin, remuneration)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id, tax_year)
        DO UPDATE SET employer_name = EXCLUDED.employer_name,
                      employer_tin = EXCLUDED.employer_tin,
                      remuneration = EXCLUDED.remuneration
    """, (user_id, tax_year, employer_name, employer_tin, remuneration))
    conn.commit()
    c.close()
    conn.close()

def save_fixed_deposits(user_id, tax_year, deposits):
    conn = get_connection()
    c = conn.cursor()
    # replace all rows for this user/year to keep it simple and avoid orphaned rows
    c.execute("DELETE FROM fixed_deposits WHERE user_id = %s AND tax_year = %s", (user_id, tax_year))
    for d in deposits:
        c.execute("""
            INSERT INTO fixed_deposits (user_id, tax_year, bank_name, institution_tin, account_no, amount_invested, interest, balance_as_at, wht_deducted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, tax_year, d["bank_name"], d["institution_tin"], d["account_no"], d["amount_invested"], d["interest"], d["balance_as_at"], d["wht_deducted"]))
    conn.commit()
    c.close()
    conn.close()


def get_prior_cumulative_relief(user_id, tax_year):
    """Look up cumulative relief claimed as of the most recent prior tax_year on record."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT cumulative_relief_claimed FROM solar_panel_income
        WHERE user_id = %s AND tax_year != %s
        ORDER BY tax_year DESC LIMIT 1
    """, (user_id, tax_year))
    row = c.fetchone()
    c.close()
    conn.close()
    return row[0] if row else 0


def save_solar(user_id, tax_year, total_expenditure, brought_forward, income_from_solar, relief_claimed_this_year, relief_carried_forward, cumulative_relief_claimed=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO solar_panel_income
            (user_id, tax_year, total_expenditure, brought_forward_balance, income_from_solar, relief_claimed_this_year, relief_carried_forward, cumulative_relief_claimed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, tax_year)
        DO UPDATE SET total_expenditure = EXCLUDED.total_expenditure,
                      brought_forward_balance = EXCLUDED.brought_forward_balance,
                      income_from_solar = EXCLUDED.income_from_solar,
                      relief_claimed_this_year = EXCLUDED.relief_claimed_this_year,
                      relief_carried_forward = EXCLUDED.relief_carried_forward,
                      cumulative_relief_claimed = EXCLUDED.cumulative_relief_claimed
    """, (user_id, tax_year, total_expenditure, brought_forward, income_from_solar, relief_claimed_this_year, relief_carried_forward, cumulative_relief_claimed))
    conn.commit()
    c.close()
    conn.close()


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

# ---- Secondary employment ----
if flags["secondary"]:
    st.subheader("Secondary employment")
    secondary_employer = st.text_input("Employer / company name", key="secondary_employer")
    secondary_tin = st.text_input("TIN of the employer", key="secondary_tin")
    secondary_remuneration = st.number_input("Remuneration (Rs.)", min_value=0.0, step=1000.0, key="secondary_remuneration")

# ---- Fixed deposits / savings (dynamic list) ----
if flags["fixed_deposits"]:
    st.subheader("Fixed deposits / savings accounts")
    st.caption("It's best to have the WHT certificate from your bank — it shows balance, interest, and WHT deducted.")

    if "fd_rows" not in st.session_state:
        st.session_state.fd_rows = [{}]  # start with one blank row

    for i, row in enumerate(st.session_state.fd_rows):
        with st.container(border=True):
            st.markdown(f"**Account {i + 1}**")
            col1, col2 = st.columns(2)
            with col1:
                row["bank_name"] = st.text_input("Bank / financial institution", key=f"fd_bank_{i}", value=row.get("bank_name", ""))
                row["institution_tin"] = st.text_input("TIN of the financial institution", key=f"fd_tin_{i}", value=row.get("institution_tin", ""))
                row["amount_invested"] = st.number_input("Amount invested", min_value=0.0, step=1000.0, key=f"fd_amt_{i}", value=row.get("amount_invested", 0.0))
            with col2:
                row["account_no"] = st.text_input("Account number", key=f"fd_acc_{i}", value=row.get("account_no", ""))
                row["interest"] = st.number_input("Interest earned", min_value=0.0, step=100.0, key=f"fd_int_{i}", value=row.get("interest", 0.0))
                row["wht_deducted"] = st.number_input("WHT deducted", min_value=0.0, step=100.0, key=f"fd_wht_{i}", value=row.get("wht_deducted", 0.0))
            row["balance_as_at"] = st.number_input("Balance as at 31.03.2026", min_value=0.0, step=1000.0, key=f"fd_bal_{i}", value=row.get("balance_as_at", 0.0))

            if len(st.session_state.fd_rows) > 1:
                if st.button("Remove this account", key=f"fd_remove_{i}"):
                    st.session_state.fd_rows.pop(i)
                    st.rerun()

    if st.button("Add another account"):
        st.session_state.fd_rows.append({})
        st.rerun()

# ---- Solar panel income (claimable deduction) ----
if flags["solar"]:

    st.subheader("Solar panel income")
    st.caption("Relief up to Rs. 600,000 per year. Unused relief carries forward; already-claimed relief in a prior year reduces what's available now.")

    solar_expenditure = st.number_input("Total expenditure / brought forward balance on acquisition of solar panel", min_value=0.0, step=1000.0, key="solar_expenditure")
    solar_income = st.number_input("Income from solar panel (Rs.)", min_value=0.0, step=1000.0, key="solar_income")

    # relief calc: capped at 600,000 or the income itself, whichever is lower, limited by remaining expenditure balance
    prior_cumulative = get_prior_cumulative_relief(user_id, tax_year)
    relief_claimed = min(solar_income, solar_expenditure, 600_000)
    relief_carried_forward = max(solar_expenditure - relief_claimed, 0)
    cumulative_relief_claimed = prior_cumulative + relief_claimed
    st.info(f"Already claimed in prior years: Rs. {prior_cumulative:,.2f}\n\n"
        f"Relief claimable this year: Rs. {relief_claimed:,.2f}\n"
        f"Carried forward: Rs. {relief_carried_forward:,.2f}")

# ---- Save everything ----
if st.button("Save and continue"):
    if flags["primary"]:
        save_primary(user_id, tax_year, primary_employer, primary_tin, primary_remuneration)
    if flags["secondary"]:
        save_secondary(user_id, tax_year, secondary_employer, secondary_tin, secondary_remuneration)
    if flags["fixed_deposits"]:
        save_fixed_deposits(user_id, tax_year, st.session_state.fd_rows)
    if flags["solar"]:
        save_solar(user_id, tax_year, solar_expenditure, 0, solar_income, relief_claimed, relief_carried_forward, cumulative_relief_claimed)

    st.success("Income details saved!")
    st.switch_page("pages/tax_summary.py")  # or wherever your calculation/output page lives