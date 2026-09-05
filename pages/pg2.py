import streamlit as st
import psycopg2
from psycopg2.extensions import new_type, register_type, DECIMAL

def get_connection():
    return psycopg2.connect(**st.secrets["postgres"])


def cast_numeric_to_float(value, cur):
    return float(value) if value is not None else None

DEC2FLOAT = new_type(DECIMAL.values, 'DEC2FLOAT', cast_numeric_to_float)
register_type(DEC2FLOAT)

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

    c.execute("""
        CREATE TABLE IF NOT EXISTS income_sources (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            has_primary_employment BOOLEAN DEFAULT FALSE,
            has_secondary_employment BOOLEAN DEFAULT FALSE,
            has_fixed_deposits BOOLEAN DEFAULT FALSE,
            has_solar_panel BOOLEAN DEFAULT FALSE,
            UNIQUE(user_id, tax_year)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS primary_employment (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            employer_name TEXT,
            employer_tin TEXT,
            remuneration NUMERIC DEFAULT 0,
            UNIQUE(user_id, tax_year)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS secondary_employment (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            employer_name TEXT,
            employer_tin TEXT,
            remuneration NUMERIC DEFAULT 0,
            UNIQUE(user_id, tax_year)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS fixed_deposits (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            bank_name TEXT,
            institution_tin TEXT,
            account_no TEXT,
            amount_invested NUMERIC DEFAULT 0,
            interest NUMERIC DEFAULT 0,
            balance_as_at NUMERIC DEFAULT 0,
            wht_deducted NUMERIC DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS solar_panel_income (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year VARCHAR(9) NOT NULL,              
            total_expenditure NUMERIC DEFAULT 0,
            brought_forward_balance NUMERIC DEFAULT 0,
            income_from_solar NUMERIC DEFAULT 0,
            relief_claimed_this_year NUMERIC DEFAULT 0,
            relief_carried_forward NUMERIC DEFAULT 0,
            cumulative_relief_claimed NUMERIC DEFAULT 0,
            UNIQUE (user_id, tax_year)
            )
    """)

    conn.commit()
    c.close()
    conn.close()

init_db()


def save_income_sources(user_id, tax_year, flags):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO income_sources
            (user_id, tax_year, has_primary_employment, has_secondary_employment,
             has_fixed_deposits, has_solar_panel)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, tax_year)
        DO UPDATE SET
            has_primary_employment = EXCLUDED.has_primary_employment,
            has_secondary_employment = EXCLUDED.has_secondary_employment,
            has_fixed_deposits = EXCLUDED.has_fixed_deposits,
            has_solar_panel = EXCLUDED.has_solar_panel
    """, (
        user_id, tax_year,
        flags["primary"], flags["secondary"], flags["fixed_deposits"], flags["solar"]
    ))
    conn.commit()
    c.close()
    conn.close()

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

tax_year = st.session_state.get("tax_year", "2025/2026")
st.markdown(f"<h2 style='text-align:center;'>For the {tax_year} tax year</h2>", unsafe_allow_html=True)

primary = st.radio("Do you earn a salary from a primary employment?", ["Yes", "No"], key="q_primary")
secondary = st.radio("Do you earn a salary from a secondary employment?", ["Yes", "No"], key="q_secondary")
fixed_deposits = st.radio("Do you have any fixed deposits or savings account?", ["Yes", "No"], key="q_fd")
solar = st.radio("Do you have any income from resident solar panels?", ["Yes", "No"], key="q_solar")

st.caption("Sadly we are currently available only for these income sources.")

if st.button("Next"):
    flags = {
        "primary": primary == "Yes",
        "secondary": secondary == "Yes",
        "fixed_deposits": fixed_deposits == "Yes",
        "solar": solar == "Yes",
    }
    save_income_sources(st.session_state.user_id, tax_year, flags)

    # carry flags forward to the next page
    st.session_state.income_flags = flags
    st.session_state.tax_year = tax_year

    st.switch_page("pages/income_details.py")

