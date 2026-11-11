import os
import pandas as pd
import requests

API_URL = "https://aip.2026.amparapiriven.lk/aip_db_setup.php"
API_KEY = "AIP_SECRET_2026_SECURE_TOKEN"

# Excel ගොනුවේ නම
EXCEL_PATH = "AIP 2026.xlsx"

def clean_str(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def clean_float(val):
    if pd.isna(val):
        return 0.0
    try:
        return float(val)
    except Exception:
        return 0.0

def run_import():
    if not os.path.exists(EXCEL_PATH):
        # වෙනත් නමකින් තිබේ නම්
        for f in os.listdir("."):
            if f.endswith(".xlsx") and not f.startswith("~$"):
                excel_file = f
                break
    else:
        excel_file = EXCEL_PATH

    print(f"Excel ගොනුව කියවීම අරඹයි: {excel_file}")
    xls = pd.ExcelFile(excel_file)
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

    # 1. Activities Import (Sheet '12')
    if "12" in xls.sheet_names:
        df_12 = pd.read_excel(xls, "12")
        print(f"ක්‍රියාකාරකම් {len(df_12)} ක් හමුවිය...")
        # API මඟින් activities සෘජුවම ලබාගැනීමට හෝ සකස් කිරීමට සහාය වේ

    # 2. Vouchers Import (Sheet 'Voucher_Log')
    if "Voucher_Log" in xls.sheet_names:
        df_v = pd.read_excel(xls, "Voucher_Log")
        v_count = 0
        for _, r in df_v.iterrows():
            amt = clean_float(r.get("මුදල"))
            if amt > 0:
                payload = {
                    "username": clean_str(r.get("පරිශීලක")) or "super_admin",
                    "vote_no": clean_str(r.get("වැය ශීර්ෂය")),
                    "action_no": clean_str(r.get("Action No")),
                    "desc": clean_str(r.get("විස්තරය")),
                    "v_no": clean_str(r.get("වවුචර අංකය")),
                    "v_date": str(r.get("වවුචර දිනය"))[:10],
                    "amount": amt
                }
                res = requests.post(f"{API_URL}?action=save_voucher", json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    v_count += 1
        print(f"වවුචර {v_count} ක් සාර්ථකව Host Database එකට ඇතුළත් කරන ලදී!")

    # 3. Programs Data Log Import (Sheet 'Data_Log')
    if "Data_Log" in xls.sheet_names:
        df_d = pd.read_excel(xls, "Data_Log")
        d_count = 0
        for _, r in df_d.iterrows():
            cost = clean_float(r.get("වියදම"))
            act_name = clean_str(r.get("වැඩසටහන"))
            if act_name:
                payload = {
                    "username": clean_str(r.get("පරිශීලක")) or "super_admin",
                    "vote_no": clean_str(r.get("වැය ශීර්ෂය")),
                    "action_no": clean_str(r.get("Action No")),
                    "act_name": act_name,
                    "loc": clean_str(r.get("ස්ථානය")),
                    "act_date": str(r.get("දිනය.1"))[:10],
                    "ben": int(clean_float(r.get("ප්‍රතිලාභීන්"))),
                    "est": clean_float(r.get("ඇස්තමේන්තුව")),
                    "cost": cost
                }
                res = requests.post(f"{API_URL}?action=save_activity", json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    d_count += 1
        print(f"වැඩසටහන් ප්‍රගති දත්ත {d_count} ක් සාර්ථකව Host Database එකට ඇතුළත් කරන ලදී!")

if __name__ == "__main__":
    run_import()
