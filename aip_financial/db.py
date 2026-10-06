import sqlite3
import re
from datetime import datetime
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aip_2026.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# =========================================================================
# 0. DATABASE SCHEMA AUTO-UPDATE (අලුත් තීරු ස්වයංක්‍රීයව එක් කිරීම)
# =========================================================================
def check_and_update_schema():
    """පවතින table වලට delete request සඳහා අවශ්‍ය columns නොමැති නම් එක් කරයි."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # voucher_log සඳහා delete_requested සහ delete_reason තීරු
    try:
        cursor.execute("ALTER TABLE voucher_log ADD COLUMN delete_requested INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE voucher_log ADD COLUMN delete_reason TEXT")
    except sqlite3.OperationalError:
        pass

    # data_log (වැඩසටහන්) සඳහා delete_requested සහ delete_reason තීරු
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

# App එක load වන විටම Schema එක තහවුරු කරගැනීම
check_and_update_schema()

# =========================================================================
# 1. AUTHENTICATION & SESSION
# =========================================================================
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_username(username):
    """පිටුව refresh වූ විට auto-login වීම සඳහා පරිශීලකයා ලබා ගැනීම."""
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
# 2. VOUCHER OPERATIONS (INSERT / EDIT / DELETE REQUEST / ADMIN DELETE)
# =========================================================================
def save_voucher(username, vote_no, action_no, desc, v_no, v_date, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO voucher_log (timestamp, username, vote_number, action_no, description, voucher_no, voucher_date, amount, delete_requested, delete_reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, vote_no, action_no, desc, v_no, str(v_date), float(amount)))
    conn.commit()
    conn.close()
    return True

def update_voucher(voucher_id, vote_no, action_no, desc, v_no, v_date, amount):
    """දත්ත ඇතුළත් කළ නිලධාරියාට හෝ Admin ට වවුචරයක් edit කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE voucher_log
    SET vote_number = ?, action_no = ?, description = ?, voucher_no = ?, voucher_date = ?, amount = ?
    WHERE rowid = ? OR id = ?
    """, (vote_no, action_no, desc, v_no, str(v_date), float(amount), voucher_id, voucher_id))
    conn.commit()
    conn.close()
    return True

def request_voucher_delete(voucher_id, reason):
    """නිලධාරියා වැරදුණු විට Delete කරන්න කියා Request එකක් යැවීම."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE voucher_log
    SET delete_requested = 1, delete_reason = ?
    WHERE rowid = ? OR id = ?
    """, (reason, voucher_id, voucher_id))
    conn.commit()
    conn.close()
    return True

def cancel_voucher_delete_request(voucher_id):
    """Super Admin ඉල්ලීම ප්‍රතික්ෂේප කළ විට නැවත Active කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE voucher_log
    SET delete_requested = 0, delete_reason = NULL
    WHERE rowid = ? OR id = ?
    """, (voucher_id, voucher_id))
    conn.commit()
    conn.close()
    return True

def delete_voucher_permanent(voucher_id):
    """Super Admin විසින් ස්ථිරවම Delete කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM voucher_log WHERE rowid = ? OR id = ?", (voucher_id, voucher_id))
    conn.commit()
    conn.close()
    return True

def get_pending_delete_vouchers():
    """Super Admin ට පෙන්වීම සඳහා Delete Request කර ඇති වවුචර ලබා ගැනීම."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT rowid as id, * FROM voucher_log WHERE delete_requested = 1", conn)
    conn.close()
    return df

# =========================================================================
# 3. ACTIVITY OPERATIONS (INSERT / EDIT / DELETE REQUEST / ADMIN DELETE)
# =========================================================================
def save_activity(username, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO data_log (timestamp, username, vote_number, action_no, activity_name, location, activity_date, beneficiaries, estimate, actual_cost, delete_requested, delete_reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, vote_no, action_no, act_name, loc, str(act_date), int(ben), float(est), float(cost)))
    conn.commit()
    conn.close()
    return True

def update_activity(activity_id, vote_no, action_no, act_name, loc, act_date, ben, est, cost):
    """වැඩසටහන් විස්තර edit කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE data_log
    SET vote_number = ?, action_no = ?, activity_name = ?, location = ?, activity_date = ?, beneficiaries = ?, estimate = ?, actual_cost = ?
    WHERE rowid = ? OR id = ?
    """, (vote_no, action_no, act_name, loc, str(act_date), int(ben), float(est), float(cost), activity_id, activity_id))
    conn.commit()
    conn.close()
    return True

def request_activity_delete(activity_id, reason):
    """වැඩසටහනක් ඉවත් කිරීමට නිලධාරියා ඉල්ලීම."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE data_log
    SET delete_requested = 1, delete_reason = ?
    WHERE rowid = ? OR id = ?
    """, (reason, activity_id, activity_id))
    conn.commit()
    conn.close()
    return True

def cancel_activity_delete_request(activity_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE data_log
    SET delete_requested = 0, delete_reason = NULL
    WHERE rowid = ? OR id = ?
    """, (activity_id, activity_id))
    conn.commit()
    conn.close()
    return True

def delete_activity_permanent(activity_id):
    """Super Admin විසින් වැඩසටහන ස්ථිරවම Delete කිරීම."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM data_log WHERE rowid = ? OR id = ?", (activity_id, activity_id))
    conn.commit()
    conn.close()
    return True

def get_pending_delete_activities():
    conn = get_connection()
    df = pd.read_sql_query("SELECT rowid as id, * FROM data_log WHERE delete_requested = 1", conn)
    conn.close()
    return df
