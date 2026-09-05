import streamlit as st
import psycopg2
from psycopg2.extensions import new_type, register_type, DECIMAL

def get_connection():
    return psycopg2.connect(**st.secrets["postgres"])

def cast_numeric_to_float(value, cur):
    return float(value) if value is not None else None

DEC2FLOAT = new_type(DECIMAL.values, 'DEC2FLOAT', cast_numeric_to_float)
register_type(DEC2FLOAT)

def get_income_summary(user_id, tax_year):
    """Fetch all income data for a user/tax_year from the database."""
    conn = get_connection()
    c = conn.cursor()

    # Primary employment
    c.execute("SELECT remuneration FROM primary_employment WHERE user_id = %s AND tax_year = %s",
              (user_id, tax_year))
    row = c.fetchone()
    primary_remuneration = row[0] if row else 0

    # Secondary employment
    c.execute("SELECT remuneration FROM secondary_employment WHERE user_id = %s AND tax_year = %s",
              (user_id, tax_year))
    row = c.fetchone()
    secondary_remuneration = row[0] if row else 0

    # Fixed deposits — sum interest and actual WHT deducted across all accounts
    c.execute("""
        SELECT COALESCE(SUM(interest), 0), COALESCE(SUM(wht_deducted), 0)
        FROM fixed_deposits WHERE user_id = %s AND tax_year = %s
    """, (user_id, tax_year))
    fd_interest_total, fd_wht_total = c.fetchone()

    # Solar relief already calculated and stored when the form was saved
    c.execute("""
        SELECT income_from_solar, relief_claimed_this_year
        FROM solar_panel_income WHERE user_id = %s AND tax_year = %s
    """, (user_id, tax_year))
    row = c.fetchone()
    solar_income, solar_relief_this_year = row if row else (0, 0)

    c.close()
    conn.close()

    return {
        "primary_remuneration": primary_remuneration,
        "secondary_remuneration": secondary_remuneration,
        "fd_interest_total": fd_interest_total,
        "fd_wht_total": fd_wht_total,
        "solar_income": solar_income,
        "solar_relief_this_year": solar_relief_this_year,
    }


def calculate_tax(user_id, tax_year):
    PERSONAL_RELIEF = 1_800_000

    summary = get_income_summary(user_id, tax_year)

    # Assessable income: employment income + interest income
    # (solar income offset by the qualifying payment relief calculated earlier)
    assessable_income = (
        summary["primary_remuneration"]
        + summary["secondary_remuneration"]
        + summary["fd_interest_total"]
    )

    taxable_income = max(
        assessable_income - PERSONAL_RELIEF - summary["solar_relief_this_year"],
        0
    )

    bands = [
        (1_000_000, 0.06),
        (500_000, 0.18),
        (500_000, 0.24),
        (500_000, 0.30),
        (float("inf"), 0.36),
    ]

    gross_tax = 0
    remaining = taxable_income
    for band_amount, rate in bands:
        taxed_in_band = min(remaining, band_amount)
        gross_tax += float(taxed_in_band) * float(rate)
        remaining -= taxed_in_band
        if remaining <= 0:
            break

    # Use ACTUAL WHT deducted from certificates, not an estimated 10%
    wht_credit = float(summary["fd_wht_total"])

    net_tax_payable = max(gross_tax - wht_credit, 0)
    refund_due = max(wht_credit - gross_tax, 0)

    return {
        "assessable_income": assessable_income,
        "personal_relief": PERSONAL_RELIEF,
        "solar_relief_claimed": summary["solar_relief_this_year"],
        "taxable_income": taxable_income,
        "gross_tax": gross_tax,
        "wht_credit": wht_credit,
        "net_tax_payable": net_tax_payable,
        "refund_due": refund_due,
    }



def get_connection():
    return psycopg2.connect(**st.secrets["postgres"])

# ... paste get_income_summary() and calculate_tax() here, or import from a shared module ...

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state.user_id
tax_year = st.session_state.tax_year

result = calculate_tax(user_id, tax_year)

st.markdown(f"<h2 style='text-align:center;'>Tax Summary — {tax_year}</h2>", unsafe_allow_html=True)

st.write(f"**Assessable income:** Rs. {result['assessable_income']:,.2f}")
st.write(f"**Personal relief:** Rs. {result['personal_relief']:,.2f}")
st.write(f"**Solar relief claimed:** Rs. {result['solar_relief_claimed']:,.2f}")
st.write(f"**Taxable income:** Rs. {result['taxable_income']:,.2f}")
st.write(f"**Gross tax payable:** Rs. {result['gross_tax']:,.2f}")
st.write(f"**WHT already deducted (credit):** Rs. {result['wht_credit']:,.2f}")

if result["net_tax_payable"] > 0:
    st.error(f"**Balance tax payable:** Rs. {result['net_tax_payable']:,.2f}")
else:
    st.success(f"**Refund due:** Rs. {result['refund_due']:,.2f}")