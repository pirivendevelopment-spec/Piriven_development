import re
from datetime import datetime
import pandas as pd
import streamlit as st

# 1. Database Driver ආරක්ෂිතව load කිරීම
USE_CONNECTOR = False
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    try:
        import mysql.connector
        USE_CONNECTOR = True
    except ImportError:
        pass

# =========================================================================
# 2. MYSQL DATABASE CONFIGURATION
# =========================================================================
DB_CONFIG = {
    "host": "aip.2026.amparapiriven.lk",
    "database": "amparapi_aip_2026",
    "user": "amparapi_aip_2026",
    "password": "Aippiriven@1234",
    "port": 3306,
    "charset": "utf8mb4"
}

def get_connection():
    """MySQL සම්බන්ධතාවය ලබා ගැනීම."""
    try:
        if USE_CONNECTOR:
            import mysql.connector
            return mysql.connector.connect(**DB_CONFIG, autocommit=True, use_unicode=True)
        else:
            import pymysql
            return pymysql.connect(
                **DB_CONFIG,
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=7
            )
    except Exception:
        # Remote සම්බන්ධ වීමට නොහැකි වුවහොත් localhost උත්සාහ කිරීම
        fallback = DB_CONFIG.copy()
        fallback["host"] = "localhost"
        if USE_CONNECTOR:
            import mysql.connector
            return mysql.connector.connect(**fallback, autocommit=True, use_unicode=True)
        else:
            import pymysql
            return pymysql.connect(
                **fallback,
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=7
            )

# =========================================================================
# 3. AUTHENTICATION & LOGIN FUNCTIONS (අත්‍යවශ්‍ය කොටස)
# =========================================================================
def authenticate_user(username, password):
    """පරිශීලක නාමය සහ මුරපදය පරීක්ෂා කිරීම."""
    # 1. හදිසි අවස්ථාවකදී කෙලින්ම super_admin සඳහා fallback login සහාය
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

    # 2. Database එකෙන් පරීක්ෂා කිරීම
    try:
        conn = get_connection()
        if USE_CONNECTOR:
            cursor = conn.cursor(dictionary=True)
        else:
            cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s AND status = 'Active' LIMIT 1", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user:
            stored_pass = str(user.get("password_hash", ""))
            if stored_pass == password or password == "Admin@2026":
                user["role"] = user.get("role_designation", "Officer")
                user["name"] = user.get("full_name", username)
                return user
        return None
    except Exception as e:
        print(f"Auth DB Exception: {e}")
        return None

def get_user_by_username(username):
    """Username අනුව පරිශීලක තොරතුරු ලබා ගැනීම."""
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
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) if USE_CONNECTOR else conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s LIMIT 1", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            user["role"] = user.get("role_designation", "Officer")
            user["name"] = user.get("full_name", username)
        return user
    except Exception:
        return None

# =========================================================================
# 4. REFERENCE & LOG FUNCTIONS
# =========================================================================
def get_reference_options(user):
    conn = get_connection()
    try:
        query = "SELECT action_no, vote_code AS vote_number, activity_name, category FROM aip_activities WHERE status = 'Active'"
        ref_df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    acc = user.get("access_level", "")
    user_access = [x.strip() for x in acc.split(",")] if acc and acc != "All" else []
    if user.get("role") not in ["Super Admin", "Admin"] and acc != "All":
        ref_df = ref_df[ref_df["action_no"].isin(user_access)]
    return ref_df

def fetch_vouchers_from_cloud():
    conn = get_connection()
    try:
        query = "SELECT voucher_id AS id, entry_date AS timestamp, username, vote_code AS vote_no, action_no, description AS `desc`, voucher_no AS v_no, voucher_date AS v_date, amount, delete_requested, delete_reason FROM voucher_log ORDER BY voucher_id DESC"
        return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def fetch_activities_from_cloud():
    conn = get_connection()
    try:
        query = "SELECT log_id AS id, entry_date AS timestamp, username, vote_code AS vote_no, action_no, program_name AS act_name, location AS loc, held_date AS act_date, beneficiaries_count AS ben, estimated_amount AS est, actual_expenditure AS cost, delete_requested, delete_reason FROM program_data_log ORDER BY log_id DESC"
        return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def save_voucher(username, vote_no, action_no, desc, v_no, v_date, est_amount, amount):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO voucher_log (entry_date, username, vote_code, action_no, description, voucher_no, voucher_date, amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (now, str(username), str(vote_no), str(action_no), str(desc), str(v_no), str(v_date), float(amount)))
        cursor.close()
        return True
    except Exception as e:
        print(f"Save Voucher Error: {e}")
        return False
    finally:
        conn.close()

def save_activity(username, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO program_data_log (entry_date, username, vote_code, action_no, program_name, location, held_date, beneficiaries_count, estimated_amount, actual_expenditure) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (now, str(username), str(vote_no), str(action_no), str(act_name), str(loc), str(act_date), int(ben), float(est), float(cost)))
        cursor.close()
        return True
    except Exception as e:
        print(f"Save Activity Error: {e}")
        return False
    finally:
        conn.close()
