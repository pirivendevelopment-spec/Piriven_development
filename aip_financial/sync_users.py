import os
import pandas as pd
import requests

API_URL = "https://aip.2026.amparapiriven.lk/aip_2026.php"
API_KEY = "AIP_SECRET_2026_SECURE_TOKEN"

def clean_val(v):
    if pd.isna(v):
        return ""
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") else s

def sync_users_and_access():
    # 1. පවතින Excel ගොනුව ස්වයංක්‍රීයව හඳුනා ගැනීම
    excel_path = "AIP 2026.xlsx"
    if not os.path.exists(excel_path):
        for f in os.listdir("."):
            if f.endswith(".xlsx") and not f.startswith("~$"):
                excel_path = f
                break

    if not os.path.exists(excel_path):
        print("❌ කිසිදු Excel (.xlsx) ගොනුවක් හමු නොවීය!")
        return

    print(f"📖 Excel ගොනුව කියවීම: {excel_path}")
    xls = pd.ExcelFile(excel_path)
    
    if "Users" not in xls.sheet_names:
        print("❌ Excel ගොනුවේ 'Users' නමින් Sheet එකක් හමු නොවීය!")
        return

    df_u = pd.read_excel(xls, "Users")
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

    print(f"Users {len(df_u)} දෙනාගේ Access Levels Sync කිරීම අරඹයි...")
    success = 0
    failed = 0

    for idx, r in df_u.iterrows():
        uname = clean_val(r.get("Username"))
        pwd = clean_val(r.get("Password"))
        
        if uname:
            payload = {
                "action": "save_user",
                "username": uname,
                "password": pwd,
                "role_designation": clean_val(r.get("Role / Designation")),
                "access_level": clean_val(r.get("Access Level")),      # Column D (Access Limitation)
                "allocations": clean_val(r.get("Allocations")),        # Column E
                "vote_number": clean_val(r.get("Vote Number")),        # Column F
                "full_name": clean_val(r.get("name")) or uname,        # Column G
                "title": clean_val(r.get("title")),                    # Column H
                "phone": clean_val(r.get("phone"))                     # Column I
            }
            try:
                res = requests.post(f"{API_URL}?action=save_user", json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "success":
                        success += 1
                    else:
                        print(f"⚠️ {uname} සුරැකීම අසාර්ථකයි: {data.get('message')}")
                        failed += 1
                else:
                    print(f"⚠️ HTTP Error {res.status_code} for user: {uname}")
                    failed += 1
            except Exception as e:
                print(f"⚠️ Error connecting for user {uname}: {e}")
                failed += 1

    print("-" * 50)
    print(f"✅ Users {success} දෙනෙකුගේ Access Limitations සාර්ථකව MySQL එකට යාවත්කාලීන විය!")
    if failed > 0:
        print(f"❌ අසාර්ථක වූ ගණන: {failed}")

if __name__ == "__main__":
    sync_users_and_access()
