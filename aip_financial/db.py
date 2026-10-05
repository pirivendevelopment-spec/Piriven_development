import sqlite3
import re
from datetime import datetime
import pandas as pd

DB_NAME = "aip_2026.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def extract_category(vote_str):
    matches = re.findall(r'(1\d{3}|2\d{3})', str(vote_str))
    if matches:
        code = int(matches[-1])
        if 1000 <= code < 2000:
            return "Recurrent"
        if 2000 <= code < 3000:
            return "Capital"
    return "Recurrent"

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_reference_options(user):
    conn = get_connection()
    ref_df = pd.read_sql_query("SELECT action_no, vote_number, activity_name, category FROM aip_reference", conn)
    conn.close()

    acc = user.get("access_level", "")
    user_access = [x.strip() for x in acc.split(',')] if acc and acc != "All" else []

    if user.get("role") != "Super Admin" and acc != "All":
        ref_df = ref_df[ref_df['action_no'].isin(user_access)]

    return ref_df

def save_voucher(username, vote_no, action_no, desc, v_no, v_date, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO voucher_log (timestamp, username, vote_number, action_no, description, voucher_no, voucher_date, amount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, vote_no, action_no, desc, v_no, str(v_date), float(amount)))
    conn.commit()
    conn.close()
    return True

def save_activity(username, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO data_log (timestamp, username, vote_number, action_no, activity_name, location, activity_date, beneficiaries, estimate, actual_cost)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, vote_no, action_no, act_name, loc, str(act_date), int(ben), float(est), float(cost)))
    conn.commit()
    conn.close()
    return True