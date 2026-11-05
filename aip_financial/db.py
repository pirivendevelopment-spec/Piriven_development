import re
from datetime import datetime
import pandas as pd
import os
import sqlite3
import requests

# ප්‍රධාන ව්‍යාපෘති ෆෝල්ඩරයේ නියමිත ස්ථානය නිවැරදිව ලබා ගැනීම
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aip_2026.db")

# 💡 1. ඩෑෂ්බෝඩ් එක සහ අනෙකුත් මොඩියුල සඳහා අවශ්‍ය get_connection() ශ්‍රිතය නැවත එකතු කිරීම
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ඔබ ලබාදුන් Google Apps Script Web App URL එක
GOOGLE_SHEET_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwuPKHcBMswJbn5UWSJNlXEGJb61Fnov1HyIMfag5paG6-SVOrHpq95O7D7BPZ7aonSWA/exec"

# 1. Google Sheet එකෙන් දත්ත නැවත ඩෑෂ්බෝඩ් එකට ලබා ගැනීම (Fetch)
def fetch_vouchers_from_cloud():
    try:
        # ඔබේ Google Sheet එකේ CSV Export લින්ක් එක (gid අංකය ඔබේ ෂීට් එකට අනුව වෙනස් විය හැක)
        sheet_id = "1TKxr2dL1xZYnflJ9RSa6m9YXdufqMCb1OJLiuY8-YFg"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=231977232"
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        print(f"Error fetching from cloud: {e}")
        return pd.DataFrame()

# 2. වවුචරයක් ඇතුළත් කළ විට ගූගල් ෂීට් එකට යැවීම (Save)
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
