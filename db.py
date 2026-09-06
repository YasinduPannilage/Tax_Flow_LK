import streamlit as st
import psycopg2
import hashlib


def get_connection():
    return psycopg2.connect(**st.secrets["postgres"])


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS public.users (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nic_number TEXT,
            phone_number TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS public.income_sources (
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
        CREATE TABLE IF NOT EXISTS public.primary_employment (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            employer_name TEXT,
            employer_tin TEXT,
            has_exempt_income BOOLEAN DEFAULT FALSE,
            exempt_income_amount NUMERIC DEFAULT 0,
            remuneration NUMERIC DEFAULT 0,
            UNIQUE(user_id, tax_year)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS public.secondary_employment (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            employer_name TEXT,
            employer_tin TEXT,
            has_exempt_income BOOLEAN DEFAULT FALSE,
            exempt_income_amount NUMERIC DEFAULT 0,
            remuneration NUMERIC DEFAULT 0,
            UNIQUE(user_id, tax_year)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS public.interest_income (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            bank_name TEXT,
            institution_tin TEXT,
            interest NUMERIC DEFAULT 0,
            wht_deducted NUMERIC DEFAULT 0,
            balance_as_at NUMERIC DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS public.solar_panel_income (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            tax_year TEXT NOT NULL,
            total_expenditure NUMERIC DEFAULT 0,
            income_from_solar NUMERIC DEFAULT 0,
            relief_claimed_this_year NUMERIC DEFAULT 0,
            cumulative_relief_claimed NUMERIC DEFAULT 0,
            UNIQUE(user_id, tax_year)
        )
    """)

    conn.commit()
    c.close()
    conn.close()


# ---------- Users ----------

def add_user(full_name, email, password, nic_number, phone_number):
    conn = get_connection()
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute("""
            INSERT INTO users (full_name, email, password, nic_number, phone_number)
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, email, hashed_password, nic_number, phone_number))
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    finally:
        c.close()
        conn.close()


def get_user(email, password):
    conn = get_connection()
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, hashed_password))
    user = c.fetchone()
    c.close()
    conn.close()
    return user


# ---------- Income sources (confirmation flags) ----------

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


# ---------- Employment ----------

def save_primary(user_id, tax_year, employer_name, employer_tin, has_exempt_income, exempt_income_amount, remuneration):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO primary_employment
            (user_id, tax_year, employer_name, employer_tin, has_exempt_income, exempt_income_amount, remuneration)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, tax_year)
        DO UPDATE SET employer_name = EXCLUDED.employer_name,
                      employer_tin = EXCLUDED.employer_tin,
                      has_exempt_income = EXCLUDED.has_exempt_income,
                      exempt_income_amount = EXCLUDED.exempt_income_amount,
                      remuneration = EXCLUDED.remuneration
    """, (user_id, tax_year, employer_name, employer_tin, has_exempt_income == "Yes", exempt_income_amount, remuneration))
    conn.commit()
    c.close()
    conn.close()


def save_secondary(user_id, tax_year, employer_name, employer_tin, has_exempt_income, exempt_income_amount, remuneration):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO secondary_employment
            (user_id, tax_year, employer_name, employer_tin, has_exempt_income, exempt_income_amount, remuneration)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, tax_year)
        DO UPDATE SET employer_name = EXCLUDED.employer_name,
                      employer_tin = EXCLUDED.employer_tin,
                      has_exempt_income = EXCLUDED.has_exempt_income,
                      exempt_income_amount = EXCLUDED.exempt_income_amount,
                      remuneration = EXCLUDED.remuneration
    """, (user_id, tax_year, employer_name, employer_tin, has_exempt_income == "Yes", exempt_income_amount, remuneration))
    conn.commit()
    c.close()
    conn.close()


# ---------- Interest income ----------

def save_interest_income(user_id, tax_year, rows):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM interest_income WHERE user_id = %s AND tax_year = %s", (user_id, tax_year))
    for r in rows:
        c.execute("""
            INSERT INTO interest_income (user_id, tax_year, bank_name, institution_tin, interest, wht_deducted, balance_as_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, tax_year, r["bank_name"], r["institution_tin"], r["interest"], r["wht_deducted"], r["balance_as_at"]))
    conn.commit()
    c.close()
    conn.close()


# ---------- Solar panel ----------

def get_prior_cumulative_relief(user_id, tax_year):
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


def save_solar(user_id, tax_year, total_expenditure, income_from_solar,
               relief_claimed_this_year, cumulative_relief_claimed):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO solar_panel_income
            (user_id, tax_year, total_expenditure, income_from_solar,
             relief_claimed_this_year, cumulative_relief_claimed)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, tax_year)
        DO UPDATE SET total_expenditure = EXCLUDED.total_expenditure,
                      income_from_solar = EXCLUDED.income_from_solar,
                      relief_claimed_this_year = EXCLUDED.relief_claimed_this_year,
                      cumulative_relief_claimed = EXCLUDED.cumulative_relief_claimed
    """, (user_id, tax_year, total_expenditure, income_from_solar,
          relief_claimed_this_year, cumulative_relief_claimed))
    conn.commit()
    c.close()
    conn.close()


# ---------- Summary + tax calculation ----------

def get_income_summary(user_id, tax_year):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT employer_name, employer_tin, remuneration, exempt_income_amount FROM primary_employment WHERE user_id=%s AND tax_year=%s", (user_id, tax_year))
    primary = c.fetchone()

    c.execute("SELECT employer_name, employer_tin, remuneration, exempt_income_amount FROM secondary_employment WHERE user_id=%s AND tax_year=%s", (user_id, tax_year))
    secondary = c.fetchone()

    c.execute("SELECT bank_name, institution_tin, interest, wht_deducted, balance_as_at FROM interest_income WHERE user_id=%s AND tax_year=%s", (user_id, tax_year))
    interest_rows = c.fetchall()

    c.execute("SELECT total_expenditure, income_from_solar, cumulative_relief_claimed FROM solar_panel_income WHERE user_id=%s AND tax_year=%s", (user_id, tax_year))
    solar = c.fetchone()

    c.close()
    conn.close()

    # Convert Decimal → float right here, so nothing downstream has to worry about it
    def to_float(val):
        return float(val) if val is not None else 0.0

    primary_remuneration = to_float(primary[2]) if primary else 0.0
    secondary_remuneration = to_float(secondary[2]) if secondary else 0.0
    fd_interest_total = sum(to_float(r[2]) for r in interest_rows) if interest_rows else 0.0
    fd_wht_total = sum(to_float(r[3]) for r in interest_rows) if interest_rows else 0.0
    solar_income = to_float(solar[1]) if solar else 0.0

    prior_cumulative = to_float(solar[2]) if solar else 0.0
    total_expenditure = to_float(solar[0]) if solar else 0.0
    remaining_expenditure = max(total_expenditure, prior_cumulative, 0.0)
    estimated_solar_relief = min(600_000.0, remaining_expenditure)

    return {
        "primary": primary, "secondary": secondary,
        "primary_remuneration": primary_remuneration,
        "secondary_remuneration": secondary_remuneration,
        "interest_rows": interest_rows,
        "fd_interest_total": fd_interest_total,
        "fd_wht_total": fd_wht_total,
        "solar_income": solar_income,
        "estimated_solar_relief": estimated_solar_relief,
        "remaining_expenditure_to_enter": remaining_expenditure,
    }

def calculate_tax(user_id, tax_year):
    PERSONAL_RELIEF = 1_800_000
    summary = get_income_summary(user_id, tax_year)

    assessable_income = (
        summary["primary_remuneration"] + summary["secondary_remuneration"] + summary["fd_interest_total"]
    )
    taxable_income = max(assessable_income - PERSONAL_RELIEF - summary["estimated_solar_relief"], 0)

    bands = [(1_000_000, 0.06), (500_000, 0.18), (500_000, 0.24), (500_000, 0.30), (float("inf"), 0.36)]
    gross_tax, remaining = 0, taxable_income
    for band_amount, rate in bands:
        taxed = min(remaining, band_amount)
        gross_tax += taxed * rate
        remaining -= taxed
        if remaining <= 0:
            break

    wht_credit = summary["fd_wht_total"]
    net_tax_payable = max(gross_tax - wht_credit, 0)
    refund_due = max(wht_credit - gross_tax, 0)

    return {
        "assessable_income": assessable_income, "personal_relief": PERSONAL_RELIEF,
        "solar_relief_estimate": summary["estimated_solar_relief"],
        "taxable_income": taxable_income, "gross_tax": gross_tax,
        "wht_credit": wht_credit, "net_tax_payable": net_tax_payable, "refund_due": refund_due,
    }