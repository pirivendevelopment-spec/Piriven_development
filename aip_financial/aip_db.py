import requests
import pandas as pd
import streamlit as st

# =========================================================================
# API BRIDGE CONFIGURATION
# =========================================================================
# ඔබගේ හොස්ට් එකෙහි ඇති PHP Setup / API ගොනුවේ වෙබ් ලිපිනය
API_URL = "https://aip.2026.amparapiriven.lk/aip_db_setup.php"
API_KEY = "AIP_SECRET_2026_SECURE_TOKEN"

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
# 1. AUTHENTICATION & USER MANAGEMENT
# =========================================================================
def authenticate_user(username, password):
    """පරිශීලකයා සත්‍යාපනය කිරීම."""
    # Emergency fallback login
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
    """පරිශීලක තොරතුරු ලබා ගැනීම."""
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
# 2. REFERENCES & DATA RETRIEVAL
# =========================================================================
def get_reference_options(user):
    """AIP විෂයයන් සහ ක්‍රියාකාරකම් ලබා ගැනීම."""
    res = call_api("get_reference")
    if res.get("status") == "success":
        df = pd.DataFrame(res.get("data", []))
    else:
        df = pd.DataFrame()

    if not df.empty:
        acc = user.get("access_level", "")
        user_access = [x.strip() for x in acc.split(",")] if acc and acc != "All" else []
        if user.get("role") not in ["Super Admin", "Admin", "ප්‍රධාන පරිපාලක"] and acc != "All":
            df = df[df["action_no"].isin(user_access)]
    return df

def fetch_vouchers_from_cloud():
    """වවුචර් දත්ත API එකෙන් කියවීම."""
    res = call_api("fetch_vouchers")
    if res.get("status") == "success":
        return pd.DataFrame(res.get("data", []))
    return pd.DataFrame()

def fetch_activities_from_cloud():
    """වැඩසටහන් දත්ත API එකෙන් කියවීම."""
    res = call_api("fetch_activities")
    if res.get("status") == "success":
        return pd.DataFrame(res.get("data", []))
    return pd.DataFrame()

# =========================================================================
# 3. SAVE ACTIONS
# =========================================================================
def save_voucher(username, vote_no, action_no, desc, v_no, v_date, est_amount, amount):
    """වවුචරය සුරැකීම."""
    payload = {
        "username": username,
        "vote_no": vote_no,
        "action_no": action_no,
        "desc": desc,
        "v_no": v_no,
        "v_date": v_date,
        "amount": amount
    }
    res = call_api("save_voucher", payload)
    return res.get("status") == "success"

def save_activity(username, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    """වැඩසටහන් දත්ත සුරැකීම."""
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
    return res.get("status") == "success"

# =========================================================================
# 4. EDIT & DELETE ACTIONS
# =========================================================================
def update_voucher(voucher_id, vote_number, action_no, description, voucher_no, voucher_date, amount):
    """වවුචරය සංස්කරණය කිරීම."""
    payload = {
        "voucher_id": voucher_id,
        "vote_number": vote_number,
        "action_no": action_no,
        "description": description,
        "voucher_no": voucher_no,
        "voucher_date": voucher_date,
        "amount": amount
    }
    call_api("update_voucher", payload)

def request_voucher_delete(voucher_id, reason):
    """වවුචරය ඉවත් කිරීමේ ඉල්ලීමක් යැවීම."""
    call_api("request_voucher_delete", {"voucher_id": voucher_id, "reason": reason})

def delete_voucher_permanent(voucher_id):
    """වවුචරය ස්ථිරවම මකා දැමීම."""
    call_api("delete_voucher_permanent", {"voucher_id": voucher_id})

def cancel_voucher_delete_request(voucher_id):
    """මැකීමේ ඉල්ලීම අවලංගු කිරීම."""
    call_api("cancel_voucher_delete_request", {"voucher_id": voucher_id})
