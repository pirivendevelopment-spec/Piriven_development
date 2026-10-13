import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    try:
        excel_path = os.path.join(BASE_DIR, "Piriven Ordinary Level Result.xlsx")
        if not os.path.exists(excel_path):
            excel_path = os.path.join(os.path.dirname(BASE_DIR), "Piriven Ordinary Level Result.xlsx")
            
        if not os.path.exists(excel_path):
            st.error("⚠️ 'Piriven Ordinary Level Result.xlsx' ගොනුව ප්‍රධාන ෆෝල්ඩරය තුළ හමු නොවීය.")
            return None, None, None

        xls = pd.ExcelFile(excel_path)
        
        users_df = pd.DataFrame()
        results_df = pd.DataFrame()
        master_df = pd.DataFrame()

        for sheet in xls.sheet_names:
            sheet_lower = sheet.strip().lower()
            temp_df = pd.read_excel(excel_path, sheet_name=sheet)
            temp_df.columns = temp_df.columns.str.strip()
            cols_lower = [str(c).lower() for c in temp_df.columns]
            
            if 'user' in sheet_lower or 'username' in cols_lower:
                users_df = temp_df
            elif 'result' in sheet_lower or 'exam' in sheet_lower or 'year' in cols_lower or 'sub1' in cols_lower:
                results_df = temp_df
            elif 'master' in sheet_lower or 'st2' in sheet_lower or 'pirivena_n' in cols_lower or 'census_no' in cols_lower or 'name of the pirivena' in cols_lower or 'district' in cols_lower:
                master_df = temp_df

        # Fallback (ස්වයංක්‍රීයව හඳුනාගත නොහැකි වුවහොත් ෂීට් අනුපිළිවෙළ අනුව ගැනීම)
        if master_df.empty and len(xls.sheet_names) > 0:
            master_df = pd.read_excel(excel_path, sheet_name=0)
            master_df.columns = master_df.columns.str.strip()
        if results_df.empty and len(xls.sheet_names) > 1:
            results_df = pd.read_excel(excel_path, sheet_name=1)
            results_df.columns = results_df.columns.str.strip()
        if users_df.empty and len(xls.sheet_names) > 2:
            users_df = pd.read_excel(excel_path, sheet_name=2)
            users_df.columns = users_df.columns.str.strip()

        return users_df, results_df, master_df

    except Exception as e:
        st.error(f"⚠️ Excel දත්ත පූරණය වීමේදී දෝෂයක් ඇති විය: {str(e)}")
        return None, None, None

def get_pirivena_map(master_df):
    p_map = {}
    if master_df is None or master_df.empty:
        return p_map
        
    master_df.columns = master_df.columns.str.strip()
    cols = {str(c).strip().lower(): c for c in master_df.columns}
    
    # 💡 කේත අංක තීරු (District N) මඟහැර, නියම පෙළ නම් ඇති DISTRICT සහ PROVINCE තීරු නිවැරදිව තෝරා ගැනීම
    p_no_key = next((cols[c] for c in cols if 'pirivena_n' in c or 'p_no' in c or 'pirivena no' in c), master_df.columns[1] if len(master_df.columns) > 1 else None)
    name_key = next((cols[c] for c in cols if 'name of the pirivena' in c or 'pirivena name' in c or 'name' in c), master_df.columns[2] if len(master_df.columns) > 2 else None)
    
    # මෙහි 'n' හෝ 'code' අඩංගු නොවන, අදාළ පෙළ (Text) තීරු සෙවීම සිදු කරයි
    dist_key = next((cols[c] for c in cols if c == 'district' or (('district' in c or 'දිස්ත්‍රික්' in c) and 'n' not in c and 'code' not in c)), None)
    prov_key = next((cols[c] for c in cols if c == 'province' or (('province' in c or 'පළාත්' in c) and 'n' not in c and 'code' not in c)), None)
    zone_key = next((cols[c] for c in cols if 'zone' in c or 'කලාප' in c or 'edu zone' in c), None)
    census_key = next((cols[c] for c in cols if 'census' in c or 'census_no' in c), master_df.columns[0] if len(master_df.columns) > 0 else None)

    for _, row in master_df.iterrows():
        raw_p_no = row.get(p_no_key, "")
        p_no = str(raw_p_no).strip()
        if p_no.endswith(".0"):
            p_no = p_no[:-2]
            
        if p_no and p_no != "nan":
            raw_prov = str(row.get(prov_key, "Unknown")).strip() if prov_key else "Unknown"
            if raw_prov.endswith(".0"): raw_prov = raw_prov[:-2]

            raw_dist = str(row.get(dist_key, "Unknown")).strip() if dist_key else "Unknown"
            if raw_dist.endswith(".0"): raw_dist = raw_dist[:-2]

            p_map[p_no] = {
                "census_no": str(row.get(census_key, "")) if census_key else "",
                "name": str(row.get(name_key, "Unknown")),
                "district": raw_dist.title(),
                "province": raw_prov.title(),
                "zone": str(row.get(zone_key, "Unknown")).strip().title() if zone_key else "Unknown"
            }
    return p_map
