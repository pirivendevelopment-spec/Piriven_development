import re
from datetime import datetime
import pandas as pd
import os
import sqlite3
import requests

# ප්‍රධාන ව්‍යාපෘති ෆෝල්ඩරයේ නියමිත ස්ථානය නිවැරදිව ලබා ගැනීම
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aip_2026.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Google Apps Script Web App URL එක
GOOGLE_SHEET_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwuPKHcBMswJbn5UWSJNlXEGJb61Fnov1HyIMfag5paG6-SVOrHpq95O7D7BPZ7aonSWA/exec"

# =========================================================================
# 0. DATABASE SCHEMA AUTO-UPDATE
# =========================================================================
def check_and_update_schema():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE voucher_log ADD COLUMN delete_requested INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE voucher_log ADD COLUMN delete_reason TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE data_log ADD COLUMN delete_requested INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE data_log ADD COLUMN delete_reason TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

check_and_update_schema()

# =========================================================================
# 1. AUTHENTICATION & SESSION & REFERENCE OPTIONS
# =========================================================================
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def extract_category(vote_str):
    matches = re.findall(r'(1\d{3}|2\d{3})', str(vote_str))
    if matches:
        code = int(matches[-1])
        if 1000 <= code < 2000:
            return "Recurrent"
        if 2000 <= code < 3000:
            return "Capital"
    return "Recurrent"

# 💡 වවුචර සහ ඇක්ටිවිටි ෆෝම් සඳහා අත්‍යවශ්‍ය get_reference_options ශ්‍රිතය
def get_reference_options(user):
    conn = get_connection()
    ref_df = pd.read_sql_query("SELECT action_no, vote_number, activity_name, category FROM aip_reference", conn)
    conn.close()

    acc = user.get("access_level", "")
    user_access = [x.strip() for x in acc.split(',')] if acc and acc != "All" else []

    if user.get("role") != "Super Admin" and acc != "All":
        ref_df = ref_df[ref_df['action_no'].isin(user_access)]

    return ref_df

# =========================================================================
# 2. VOUCHER OPERATIONS (GOOGLE SHEETS INTEGRATION)
# =========================================================================
def fetch_vouchers_from_cloud():
    try:
        sheet_id = "1TKxr2dL1xZYnflJ9RSa6m9YXdufqMCb1OJLiuY8-YFg"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=231977232"
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        print(f"Error fetching from cloud: {e}")
        return pd.DataFrame()

def save_voucher(username, vote_no, action_no, desc, v_no, v_date, est_amount, amount):
    payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "vote_number": vote_no,
        "action_no": action_no,
        "description": desc,
        "voucher_no": v_no,
        "voucher_date": str(v_date),
        "estimated_amount": float(est_amount),
        "amount": float(amount)
    }
    try:
        response = requests.post(GOOGLE_SHEET_WEB_APP_URL, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Cloud Save Error: {e}")
        return False
