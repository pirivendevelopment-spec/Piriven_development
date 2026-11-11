import os
import sqlite3
import requests
import pandas as pd
import streamlit as st

# =========================================================================
# API BRIDGE CONFIGURATION
# =========================================================================
API_URL = "https://aip.2026.amparapiriven.lk/aip_2026.php"
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
# 1. AUTHENTICATION & USERS
# =========================================================================
def authenticate_user(username, password):
    """පරිශීලකයා සත්‍යාපනය කිරීම (Login Authentication)"""
    # Emergency fallback login for super_admin
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
# 2. DATA RETRIEVAL
# =========================================================================
def get_reference_options(user):
    """AIP විෂයයන් සහ ප්‍රතිපාදන පරිශීලකයාගේ Access Level එකට අනුව ලබා ගැනීම."""
    res = call_api("get_reference")
    df = pd.DataFrame(res.get("data", [])) if res.get("status") == "success" else pd.DataFrame()

    if not df.empty and user:
        role = str(user.get("role", "")).lower()
        acc = str(user.get("access_level", "")).strip()

        if role not in ["super admin", "admin", "ප්‍රධාන පරිපාලක"] and acc not in ["All", "All Management", "0", ""]:
            allowed_actions = [x.strip().removesuffix(".0") for x in acc.split(",") if x.strip()]
            
            def is_allowed(act_val):
                act_str = str(act_val).strip().removesuffix(".0")
                for allowed in allowed_actions:
                    if act_str == allowed or act_str.startswith(allowed + "."):
                        return True
                return False

            df = df[df["action_no"].apply(is_allowed)]

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
    """වවුචරයක් සුරැකීම."""
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

def update_activity(log_id, act_name, loc, act_date, ben, est, cost):
    call_api("update_activity", {
        "log_id": log_id,
        "act_name": act_name,
        "loc": loc,
        "act_date": act_date,
        "ben": ben,
        "est": est,
        "cost": cost
    })

def request_activity_delete(log_id, reason):
    call_api("request_activity_delete", {"log_id": log_id, "reason": reason})

def delete_activity_permanent(log_id):
    call_api("delete_activity_permanent", {"log_id": log_id})

def cancel_activity_delete_request(log_id):
    call_api("cancel_activity_delete_request", {"log_id": log_id})
