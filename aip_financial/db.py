import re
from datetime import datetime
import pandas as pd
import os
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ප්‍රධාන ව්‍යාපෘති ෆෝල්ඩරයේ නියමිත ස්ථානය නිවැරදිව ලබා ගැනීම
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aip_2026.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# =========================================================================
# GSPREAD GOOGLE SHEETS CONNECTION SETUP
# =========================================================================
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # Streamlit secrets හරහා credentials ලබා ගැනීම (Cloud එක සඳහා)
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client
        
        # Local පරිගණකයේ වැඩ කරන විට credentials.json ፋයිල් එක පාවිච්චි කිරීමට
        creds_path = os.path.join(BASE_DIR, "credentials.json")
        if os.path.exists(creds_path):
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            client = gspread.authorize(creds)
            return client
            
    except Exception as e:
        print(f"Gspread Auth Error: {e}")
    return None

# =========================================================================
# 0. DATABASE SCHEMA AUTO-UPDATE (පරණ DB එක සඳහා)
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
# 2. VOUCHER & ACTIVITY OPERATIONS (GOOGLE SHEETS API INTEGRATION)
# =========================================================================

# වවුචර් දත්ත ලබා ගැනීම (ഡෑෂ්බෝඩ් සඳහා)
def fetch_vouchers_from_cloud():
    try:
        sheet = get_google_sheet("vouchers")
        if sheet:
            data = sheet.get_all_records()
            if data:
                return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        print(f"Gspread Fetch Vouchers Error: {e}")
        return pd.DataFrame()

# වැඩසටහන් දත්ත ලබා ගැනීම (ഡෑෂ්බෝඩ් සඳහා)
def fetch_activities_from_cloud():
    try:
        sheet = get_google_sheet("activities")
        if sheet:
            data = sheet.get_all_records()
            if data:
                return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        print(f"Gspread Fetch Activities Error: {e}")
        return pd.DataFrame()

# වවුචරයක් Google Sheet එකට ඇතුළත් කිරීම (Save Voucher)
def save_voucher(username, vote_no, action_no, desc, v_no, v_date, est_amount, amount):
    try:
        sheet = get_google_sheet("vouchers")
        if sheet:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(username),
                str(vote_no),
                str(action_no),
                str(desc),
                str(v_no),
                str(v_date),
                float(est_amount),
                float(amount)
            ]
            sheet.append_row(row)
            return True
        return False
    except Exception as e:
        print(f"Gspread Save Voucher Error: {e}")
        return False

# වැඩසටහන් (Activities) Google Sheet එකට ඇතුළත් කිරීම (Save Activity)
def save_activity(username, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    try:
        sheet = get_google_sheet("activities")
        if sheet:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(username),
                str(vote_no),
                str(action_no),
                str(act_name),
                str(loc),
                str(act_date),
                int(ben),
                float(est),
                float(cost),
                0,
                ""
            ]
            sheet.append_row(row)
            return True
        return False
    except Exception as e:
        print(f"Gspread Save Activity Error: {e}")
        return False
