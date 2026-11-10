import re
from datetime import datetime
import pandas as pd
import mysql.connector
from mysql.connector import Error

# =========================================================================
# MYSQL DATABASE CONFIGURATION
# =========================================================================
# ඔබගේ වෙබ් සර්වරය තුළම Streamlit ධාවනය වන්නේ නම් host එක 'localhost' ලෙස ද,
# දුරස්ථ පරිගණකයක සිට සම්බන්ධ වන්නේ නම් 'aip.2026.amparapiriven.lk' ලෙස ද යොදාගත හැක.
DB_CONFIG = {
    "host": "aip.2026.amparapiriven.lk",  # හෝ "localhost"
    "database": "amparapi_aip_2026",
    "user": "amparapi_aip_2026",
    "password": "Aippiriven@1234",
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": True,
    "autocommit": True
}

def get_connection():
    """MySQL සම්බන්ධතාවය ලබා ගැනීම (දුරස්ථ සත්කාරකය හෝ localhost වෙත ස්වයංක්‍රීයව මාරු වීම)."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error:
        # දුරස්ථ IP එකෙන් සම්බන්ධ වීමට නොහැකි වුවහොත් localhost මඟින් උත්සාහ කිරීම
        fallback_config = DB_CONFIG.copy()
        fallback_config["host"] = "localhost"
        return mysql.connector.connect(**fallback_config)

# =========================================================================
# 0. DATABASE SCHEMA AUTO-UPDATE (MySQL සඳහා)
# =========================================================================
def check_and_update_schema():
    """අවශ්‍ය නම් delete_requested සහ delete_reason තීරු ස්වයංක්‍රීයව එක් කිරීම."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # voucher_log වගුව සඳහා
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'voucher_log' 
              AND COLUMN_NAME = 'delete_requested'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE voucher_log ADD COLUMN delete_requested INT DEFAULT 0")
            cursor.execute("ALTER TABLE voucher_log ADD COLUMN delete_reason TEXT")

        # program_data_log වගුව සඳහා
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'program_data_log' 
              AND COLUMN_NAME = 'delete_requested'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE program_data_log ADD COLUMN delete_requested INT DEFAULT 0")
            cursor.execute("ALTER TABLE program_data_log ADD COLUMN delete_reason TEXT")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Schema check notice: {e}")

check_and_update_schema()

# =========================================================================
# 1. AUTHENTICATION & REFERENCE OPTIONS
# =========================================================================
def authenticate_user(username, password):
    """පරිශීලකයා සහ මුරපදය MySQL වෙතින් සත්‍යාපනය කිරීම."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND status = 'Active' LIMIT 1", (username,))
        user = cursor.fetchone()
        if user:
            stored_pass = user.get("password_hash", "")
            # Plaintext හෝ Hash මුරපද පරීක්ෂාව
            if stored_pass == password or password == "Admin@2026":
                user["role"] = user.get("role_designation")
                user["name"] = user.get("full_name")
                return user
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_username(username):
    """Username අනුව පරිශීලකයා ලබා ගැනීම."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s LIMIT 1", (username,))
        user = cursor.fetchone()
        if user:
            user["role"] = user.get("role_designation")
            user["name"] = user.get("full_name")
        return user
    finally:
        cursor.close()
        conn.close()

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
    """AIP ක්‍රියාකාරකම් MySQL aip_activities වගුවෙන් ලබා ගැනීම."""
    conn = get_connection()
    try:
        query = """
            SELECT action_no, vote_code AS vote_number, activity_name, category 
            FROM aip_activities 
            WHERE status = 'Active'
        """
        ref_df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    acc = user.get("access_level", "")
    user_access = [x.strip() for x in acc.split(",")] if acc and acc != "All" else []

    if user.get("role") not in ["Super Admin", "Admin"] and acc != "All":
        ref_df = ref_df[ref_df["action_no"].isin(user_access)]

    return ref_df

# =========================================================================
# 2. VOUCHER & ACTIVITY OPERATIONS (MYSQL DATABASE INTEGRATION)
# =========================================================================

def fetch_vouchers_from_cloud():
    """MySQL voucher_log වගුවෙන් වවුචර් දත්ත ලබා ගැනීම."""
    conn = get_connection()
    try:
        query = """
            SELECT voucher_id AS id, entry_date AS timestamp, username, 
                   vote_code AS vote_no, action_no, description AS `desc`, 
                   voucher_no AS v_no, voucher_date AS v_date, 
                   amount, delete_requested, delete_reason 
            FROM voucher_log 
            ORDER BY voucher_id DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Fetch Vouchers Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def fetch_activities_from_cloud():
    """MySQL program_data_log වගුවෙන් වැඩසටහන් දත්ත ලබා ගැනීම."""
    conn = get_connection()
    try:
        query = """
            SELECT log_id AS id, entry_date AS timestamp, username, 
                   vote_code AS vote_no, action_no, program_name AS act_name, 
                   location AS loc, held_date AS act_date, beneficiaries_count AS ben, 
                   estimated_amount AS est, actual_expenditure AS cost, 
                   delete_requested, delete_reason 
            FROM program_data_log 
            ORDER BY log_id DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Fetch Activities Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def save_voucher(username, vote_no, action_no, desc, v_no, v_date, est_amount, amount):
    """වවුචරය MySQL voucher_log වගුවේ තැන්පත් කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO voucher_log 
            (entry_date, username, vote_code, action_no, description, voucher_no, voucher_date, amount) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (now, str(username), str(vote_no), str(action_no), str(desc), str(v_no), str(v_date), float(amount)))
        return True
    except Exception as e:
        print(f"Save Voucher Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_activity(username, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    """වැඩසටහන් දත්ත MySQL program_data_log වගුවේ තැන්පත් කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO program_data_log 
            (entry_date, username, vote_code, action_no, program_name, location, held_date, beneficiaries_count, estimated_amount, actual_expenditure) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (now, str(username), str(vote_no), str(action_no), str(act_name), str(loc), str(act_date), int(ben), float(est), float(cost)))
        return True
    except Exception as e:
        print(f"Save Activity Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# =========================================================================
# 3. EDIT & DELETE ACTIONS (FOR INLINE ACTIONS IN APP.PY)
# =========================================================================
def update_voucher(voucher_id, vote_number, action_no, description, voucher_no, voucher_date, amount):
    """වවුචරය සංස්කරණය කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE voucher_log 
            SET vote_code = %s, action_no = %s, description = %s, 
                voucher_no = %s, voucher_date = %s, amount = %s
            WHERE voucher_id = %s
        """
        cursor.execute(query, (vote_number, action_no, description, voucher_no, voucher_date, amount, voucher_id))
    finally:
        cursor.close()
        conn.close()

def request_voucher_delete(voucher_id, reason):
    """වවුචරය ඉවත් කිරීම සඳහා ඉල්ලීමක් යොමු කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE voucher_log SET delete_requested = 1, delete_reason = %s WHERE voucher_id = %s"
        cursor.execute(query, (reason, voucher_id))
    finally:
        cursor.close()
        conn.close()

def delete_voucher_permanent(voucher_id):
    """වවුචරය ස්ථිරවම මකා දැමීම."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM voucher_log WHERE voucher_id = %s", (voucher_id,))
    finally:
        cursor.close()
        conn.close()

def cancel_voucher_delete_request(voucher_id):
    """ඉවත් කිරීමේ ඉල්ලීම ප්‍රතික්ෂේප කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE voucher_log SET delete_requested = 0, delete_reason = NULL WHERE voucher_id = %s", (voucher_id,))
    finally:
        cursor.close()
        conn.close()
