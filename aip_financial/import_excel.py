import os
import pandas as pd
import requests

API_URL = "https://aip.2026.amparapiriven.lk/aip_2026.php"
API_KEY = "AIP_SECRET_2026_SECURE_TOKEN"

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

def run_sync():
    # Excel ගොනුව තෝරාගැනීම
    excel_file = None
    for f in os.listdir("."):
        if f.endswith(".xlsx") and not f.startswith("~$"):
            excel_file = f
            break

    if not excel_file:
        print("❌ Excel ගොනුව හමු නොවීය! කරුණාකර Excel ගොනුව එකම folder එකේ තබන්න.")
        return

    print(f"📖 කියවීම අරඹයි: {excel_file}")
    xls = pd.ExcelFile(excel_file)
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

    # 1. Users 62 Sync
    if "Users" in xls.sheet_names:
        df_u = pd.read_excel(xls, "Users")
        u_count = 0
        for _, r in df_u.iterrows():
            uname = clean_str(r.get("Username"))
            pwd = clean_str(r.get("Password"))
            if uname:
                res = requests.post(f"{API_URL}?action=save_user", json={
                    "action": "save_user",
                    "username": uname,
                    "password": pwd,
                    "role_designation": clean_str(r.get("Role / Designation")) or "Officer",
                    "access_level": clean_str(r.get("Access Level")) or "All",
                    "full_name": clean_str(r.get("name")) or uname,
                    "title": clean_str(r.get("title")),
                    "phone": clean_str(r.get("phone"))
                }, headers=headers, timeout=10)
                if res.status_code == 200 and res.json().get("status") == "success":
                    u_count += 1
        print(f"✅ 1. Users {u_count} දෙනෙකු සාර්ථකව ඇතුළත් විය.")

    # 2. Activities 86 Sync (Sheet '12' හෝ 'AIP_Reference')
    sheet_ref = "12" if "12" in xls.sheet_names else ("AIP_Reference" if "AIP_Reference" in xls.sheet_names else None)
    if sheet_ref:
        df_act = pd.read_excel(xls, sheet_ref)
        act_col = "action No" if "action No" in df_act.columns else "Parent No"
        name_col = "Activity (C)" if "Activity (C)" in df_act.columns else "Activity Name"
        vote_col = "Vote Number " if "Vote Number " in df_act.columns else "Vote Code"
        alloc_col = "Allocation " if "Allocation " in df_act.columns else "Allocation (Rs. '000)"

        a_count = 0
        for _, r in df_act.iterrows():
            ano = clean_str(r.get(act_col))
            vcode = clean_str(r.get(vote_col))
            aname = clean_str(r.get(name_col))
            alloc = clean_float(r.get(alloc_col))
            if ano and vcode:
                res = requests.post(f"{API_URL}?action=save_activity_ref", json={
                    "action_no": ano,
                    "vote_code": vcode,
                    "activity_name": aname,
                    "category": "Capital" if ("2205" in vcode or "2509" in vcode) else "Recurrent",
                    "allocation": alloc
                }, headers=headers, timeout=10)
                if res.status_code == 200 and res.json().get("status") == "success":
                    a_count += 1
        print(f"✅ 2. ක්‍රියාකාරකම් හා ප්‍රතිපාදන {a_count} ක් සාර්ථකව ඇතුළත් විය.")

    # 3. Voucher Log Sync (වවුචර් 15)
    if "Voucher_Log" in xls.sheet_names:
        df_v = pd.read_excel(xls, "Voucher_Log")
        v_count = 0
        for _, r in df_v.iterrows():
            amt = clean_float(r.get("මුදල"))
            if amt > 0:
                res = requests.post(f"{API_URL}?action=save_voucher", json={
                    "username": clean_str(r.get("පරිශීලක")) or "super_admin",
                    "vote_no": clean_str(r.get("වැය ශීර්ෂය")),
                    "action_no": clean_str(r.get("Action No")),
                    "desc": clean_str(r.get("විස්තරය")),
                    "v_no": clean_str(r.get("වවුචර අංකය")),
                    "v_date": str(r.get("වවුචර දිනය") or "")[:10],
                    "amount": amt
                }, headers=headers, timeout=10)
                if res.status_code == 200 and res.json().get("status") == "success":
                    v_count += 1
        print(f"✅ 3. වවුචර් (Vouchers) {v_count} ක් සාර්ථකව ඇතුළත් විය.")

    # 4. Program Data Log Sync (වැඩසටහන් 69)
    if "Data_Log" in xls.sheet_names:
        df_d = pd.read_excel(xls, "Data_Log")
        d_count = 0
        for _, r in df_d.iterrows():
            cost = clean_float(r.get("වියදම"))
            act_name = clean_str(r.get("වැඩසටහන"))
            if act_name:
                res = requests.post(f"{API_URL}?action=save_activity", json={
                    "username": clean_str(r.get("පරිශීලක")) or "super_admin",
                    "vote_no": clean_str(r.get("වැය ශීර්ෂය")),
                    "action_no": clean_str(r.get("Action No")),
                    "act_name": act_name,
                    "loc": clean_str(r.get("ස්ථානය")),
                    "act_date": str(r.get("දිනය.1") or r.get("දිනය") or "")[:10],
                    "ben": int(clean_float(r.get("ප්‍රතිලාභීන්"))),
                    "est": clean_float(r.get("ඇස්තමේන්තුව")),
                    "cost": cost
                }, headers=headers, timeout=10)
                if res.status_code == 200 and res.json().get("status") == "success":
                    d_count += 1
        print(f"✅ 4. වැඩසටහන් ප්‍රගති දත්ත {d_count} ක් සාර්ථකව ඇතුළත් විය.")

    print("\n🎉 සියලුම දත්ත සාර්ථකව Database එකට Sync විය!")

if __name__ == "__main__":
    run_sync()
