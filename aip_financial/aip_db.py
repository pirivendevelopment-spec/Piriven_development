import os
import sqlite3
import requests
import pandas as pd
import streamlit as st

# =========================================================================
# API BRIDGE CONFIGURATION
# =========================================================================
API_URL = "https://aip.2026.amparapiriven.lk/aip_db_setup.php"
API_KEY = "AIP_SECRET_2026_SECURE_TOKEN"

# Streamlit Cloud හි පවතින SQLite ගොනු මාර්ගය (පැරණි දත්ත සඳහා)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in locals() else os.getcwd()
SQLITE_PATH = os.path.join(BASE_DIR, "aip_2026.db")

def call_api(action, payload=None):
    """PHP API එක අමතා JSON ප්‍රතිචාරය ලබා ගැනීම."""
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    data = payload or {}
    data["action"] = action
    try:
        response = requests.post(f"{API_URL}?action={action}", json=data, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# =========================================================================
# 1. AUTHENTICATION & USERS
# =========================================================================
def authenticate_user(username, password):
    if username == "super_admin" and password == "Admin@2026":
        return {
            "username": "super_admin",
            "full_name": "කහගල චන්දාලෝක හිමි",
            "name": "කහගල චන්දාලෝක හිමි",
            "title": "සහකාර අධ්‍යක්ෂ",
            "role": "Super Admin",
            "role_designation": "Super Admin",
            "access_level": "All Management"
        }

    res = call_api("authenticate", {"username": username, "password": password})
    if res.get("status") == "success":
        return res.get("data")
    return None

def get_user_by_username(username):
    if username == "super_admin":
        return {
            "username": "super_admin",
            "full_name": "කහගල චන්දාලෝක හිමි",
            "name": "කහගල චන්දාලෝක හිමි",
            "title": "සහකාර අධ්‍යක්ෂ",
            "role": "Super Admin",
            "role_designation": "Super Admin",
            "access_level": "All Management"
        }
    res = call_api("get_user", {"username": username})
    if res.get("status") == "success":
        return res.get("data")
    return None

# =========================================================================
# 2. DATA RETRIEVAL (API මුලින් පරීක්ෂා කර, හිස් නම් SQLite වෙතින් ගැනීම)
# =========================================================================
def get_reference_options(user):
    """AIP විෂයයන් ලබා ගැනීම (හොස්ට් එකේ නැතිනම් local SQLite එකෙන් ගනී)."""
    res = call_api("get_reference")
    df = pd.DataFrame(res.get("data", [])) if res.get("status") == "success" else pd.DataFrame()

    # හොස්ට් එකේ දත්ත නැතිනම් SQLite එකෙන් කියවීම
    if df.empty and os.path.exists(SQLITE_PATH):
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            df = pd.read_sql_query("SELECT action_no, vote_number, activity_name, category, allocation FROM aip_reference", conn)
            conn.close()
        except Exception:
            pass

    if not df.empty:
        acc = user.get("access_level", "")
        user_access = [x.strip() for x in acc.split(",")] if acc and acc != "All" else []
        if user.get("role") not in ["Super Admin", "Admin", "ප්‍රධාන පරිපාලක"] and acc != "All":
            df = df[df["action_no"].isin(user_access)]
    return df

def fetch_vouchers_from_cloud():
    """වවුචර් දත්ත API එකෙන් ගැනීම (නැතිනම් local SQLite එකෙන් ගනී)."""
    res = call_api("fetch_vouchers")
    df = pd.DataFrame(res.get("data", [])) if res.get("status") == "success" else pd.DataFrame()

    if df.empty and os.path.exists(SQLITE_PATH):
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            df = pd.read_sql_query("SELECT rowid AS id, timestamp, username, vote_number, action_no, description, voucher_no, voucher_date, amount, delete_requested, delete_reason FROM voucher_log ORDER BY rowid DESC", conn)
            conn.close()
        except Exception:
            pass
    return df

def fetch_activities_from_cloud():
    """වැඩසටහන් දත්ත API එකෙන් ගැනීම (නැතිනම් local SQLite එකෙන් ගනී)."""
    res = call_api("fetch_activities")
    df = pd.DataFrame(res.get("data", [])) if res.get("status") == "success" else pd.DataFrame()

    if df.empty and os.path.exists(SQLITE_PATH):
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            df = pd.read_sql_query("SELECT rowid AS id, timestamp, username, vote_number, action_no, activity_name, location, activity_date, beneficiaries_count, estimated_cost, actual_cost, delete_requested, delete_reason FROM data_log ORDER BY rowid DESC", conn)
            conn.close()
        except Exception:
            pass
    return df

# =========================================================================
# 3. SAVE ACTIONS (අලුතින් ඇතුළත් කරන සියල්ල කෙළින්ම HOST එකට SAVE වේ)
# =========================================================================
def save_voucher(username, vote_no, action_no, desc, v_no, v_date, est_amount, amount):
    payload = {
        "username": username,
        "vote_no": vote_no,
        "action_no": action_no,
        "desc": desc,
        "v_no": v_no,
        "v_date": v_date,
        "amount": amount
    }
    # 1. Host MySQL එකට API මඟින් Save කිරීම
    res = call_api("save_voucher", payload)
    
    # 2. Local Backup සඳහා SQLite වෙතද සුරැකීම
    if os.path.exists(SQLITE_PATH):
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO voucher_log (username, vote_number, action_no, description, voucher_no, voucher_date, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, vote_no, action_no, desc, v_no, v_date, amount))
            conn.commit()
            conn.close()
        except Exception:
            pass
            
    return res.get("status") == "success"

def save_activity(username, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    payload = {
        "username": username,
        "vote_no": vote_no,
        "action_no": action_no,
        "act_name": act_name,
        "loc": loc,
        "act_date": act_date,
        "ben": ben,
        "est": est,
        "cost": cost
    }
    res = call_api("save_activity", payload)
    
    if os.path.exists(SQLITE_PATH):
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO data_log (username, vote_number, action_no, activity_name, location, activity_date, beneficiaries_count, estimated_cost, actual_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, vote_no, action_no, act_name, loc, act_date, ben, est, cost))
            conn.commit()
            conn.close()
        except Exception:
            pass

    return res.get("status") == "success"

def update_voucher(voucher_id, vote_number, action_no, description, voucher_no, voucher_date, amount):
    call_api("update_voucher", {
        "voucher_id": voucher_id,
        "vote_number": vote_number,
        "action_no": action_no,
        "description": description,
        "voucher_no": voucher_no,
        "voucher_date": voucher_date,
        "amount": amount
    })

def request_voucher_delete(voucher_id, reason):
    call_api("request_voucher_delete", {"voucher_id": voucher_id, "reason": reason})

def delete_voucher_permanent(voucher_id):
    call_api("delete_voucher_permanent", {"voucher_id": voucher_id})

def cancel_voucher_delete_request(voucher_id):
    call_api("cancel_voucher_delete_request", {"voucher_id": voucher_id})
