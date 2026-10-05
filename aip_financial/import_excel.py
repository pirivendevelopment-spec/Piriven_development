import sqlite3
import pandas as pd
import re
import os

EXCEL_FILE = "AIP 2026.xlsx"
DB_NAME = "aip_2026.db"

def extract_category(vote_str):
    matches = re.findall(r'(1\d{3}|2\d{3})', str(vote_str))
    if matches:
        code = int(matches[-1])
        if 1000 <= code < 2000:
            return "Recurrent"
        if 2000 <= code < 3000:
            return "Capital"
    return "Recurrent"

def build_database():
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ '{EXCEL_FILE}' ගොනුව මෙම Folder එක තුළ හමු නොවීය. කරුණාකර නම නිවැරදිදැයි බලන්න.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. වගු නිර්මාණය (Tables Setup)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aip_reference (
        action_no TEXT PRIMARY KEY,
        vote_number TEXT,
        activity_name TEXT,
        unit TEXT,
        allocation REAL DEFAULT 0.0,
        category TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        access_level TEXT,
        vote TEXT,
        name TEXT,
        title TEXT,
        phone TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voucher_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        username TEXT,
        vote_number TEXT,
        action_no TEXT,
        description TEXT,
        voucher_no TEXT,
        voucher_date TEXT,
        amount REAL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        username TEXT,
        vote_number TEXT,
        action_no TEXT,
        activity_name TEXT,
        location TEXT,
        activity_date TEXT,
        beneficiaries INTEGER,
        estimate REAL,
        actual_cost REAL
    )""")

    print("🔄 Excel ගොනුව පූරණය වෙමින් පවතී...")
    xls = pd.ExcelFile(EXCEL_FILE)

    # -------------------------------------------------------------
    # A. 'Users' පත්‍රිකාව Import කිරීම
    # -------------------------------------------------------------
    if "Users" in xls.sheet_names:
        df_users = pd.read_excel(xls, sheet_name="Users")
        cursor.execute("DELETE FROM users")
        for _, r in df_users.iterrows():
            u = str(r.iloc[0]).strip() if pd.notna(r.iloc[0]) else ""
            p = str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else ""
            role = str(r.iloc[2]).strip() if pd.notna(r.iloc[2]) else ""
            acc = str(r.iloc[3]).strip() if len(r) > 3 and pd.notna(r.iloc[3]) else "All"
            vote = str(r.iloc[4]).strip() if len(r) > 4 and pd.notna(r.iloc[4]) else ""
            name = str(r.iloc[5]).strip() if len(r) > 5 and pd.notna(r.iloc[5]) else ""
            title = str(r.iloc[6]).strip() if len(r) > 6 and pd.notna(r.iloc[6]) else ""
            phone = str(r.iloc[7]).strip() if len(r) > 7 and pd.notna(r.iloc[7]) else ""

            if u:
                cursor.execute("""
                INSERT OR REPLACE INTO users (username, password, role, access_level, vote, name, title, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (u, p, role, acc, vote, name, title, phone))
        print("✅ Users පත්‍රිකාවේ දත්ත SQLite වෙත සාර්ථකව එක් විය.")

    # -------------------------------------------------------------
    # B. 'AIP_Reference' පත්‍රිකාව Import කිරීම
    # -------------------------------------------------------------
    if "AIP_Reference" in xls.sheet_names:
        df_ref = pd.read_excel(xls, sheet_name="AIP_Reference")
        cursor.execute("DELETE FROM aip_reference")
        for _, r in df_ref.iterrows():
            act = str(r.iloc[0]).strip() if pd.notna(r.iloc[0]) else ""
            vote = str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else ""
            name = str(r.iloc[2]).strip() if pd.notna(r.iloc[2]) else ""
            unit = str(r.iloc[3]).strip() if len(r) > 3 and pd.notna(r.iloc[3]) else ""
            
            raw_alloc = str(r.iloc[4]).replace(',', '').strip() if len(r) > 4 and pd.notna(r.iloc[4]) else "0"
            try:
                # ප්‍රතිපාදනය (Rs. Mn / '000 ගැලපීම)
                alloc = float(raw_alloc) * 1000
            except ValueError:
                alloc = 0.0

            cat = extract_category(vote)

            if act and act.lower() != "action no":
                cursor.execute("""
                INSERT OR REPLACE INTO aip_reference (action_no, vote_number, activity_name, unit, allocation, category)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (act, vote, name, unit, alloc, cat))
        print("✅ AIP_Reference පත්‍රිකාවේ දත්ත SQLite වෙත සාර්ථකව එක් විය.")

    # -------------------------------------------------------------
    # C. පැරණි Logs තිබේ නම් ඒවාද Import කිරීම (Optional)
    # -------------------------------------------------------------
    if "Voucher_Log" in xls.sheet_names:
        df_v = pd.read_excel(xls, sheet_name="Voucher_Log")
        cursor.execute("DELETE FROM voucher_log")
        for _, r in df_v.iterrows():
            if len(r) >= 8 and pd.notna(r.iloc[2]):
                cursor.execute("""
                INSERT INTO voucher_log (timestamp, username, vote_number, action_no, description, voucher_no, voucher_date, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(r.iloc[0]), str(r.iloc[1]), str(r.iloc[2]), str(r.iloc[3]), str(r.iloc[4]), str(r.iloc[5]), str(r.iloc[6]), float(r.iloc[7] or 0)))
        print("✅ Voucher_Log පැරණි දත්ත සාර්ථකව එක් විය.")

    if "Data_Log" in xls.sheet_names:
        df_d = pd.read_excel(xls, sheet_name="Data_Log")
        cursor.execute("DELETE FROM data_log")
        for _, r in df_d.iterrows():
            if len(r) >= 10 and pd.notna(r.iloc[2]):
                cursor.execute("""
                INSERT INTO data_log (timestamp, username, vote_number, action_no, activity_name, location, activity_date, beneficiaries, estimate, actual_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(r.iloc[0]), str(r.iloc[1]), str(r.iloc[2]), str(r.iloc[3]), str(r.iloc[4]), str(r.iloc[5]), str(r.iloc[6]), int(r.iloc[7] or 0), float(r.iloc[8] or 0), float(r.iloc[9] or 0)))
        print("✅ Data_Log පැරණි දත්ත සාර්ථකව එක් විය.")

    conn.commit()
    conn.close()
    print("\n🎉 සියලු දත්ත සාර්ථකව 'aip_2026.db' ගොනුවට Import කර අවසන්!")

if __name__ == "__main__":
    build_database()