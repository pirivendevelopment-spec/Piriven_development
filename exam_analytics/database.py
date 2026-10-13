import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    try:
        users_path = os.path.join(BASE_DIR, "users.csv")
        results_path = os.path.join(BASE_DIR, "exam_results.csv")
        master_path = os.path.join(BASE_DIR, "pirivena_master.csv")
        
        users_df = pd.read_csv(users_path, encoding="utf-8-sig", sep=None, engine='python')
        results_df = pd.read_csv(results_path, encoding="utf-8-sig", sep=None, engine='python')
        master_df = pd.read_csv(master_path, encoding="utf-8-sig", sep=None, engine='python')
        
        return users_df, results_df, master_df
    except Exception as e:
        st.error(f"⚠️ දත්ත ගොනු පූරණය වීමේදී දෝෂයක් ඇති විය: {str(e)}")
        return None, None, None

def get_pirivena_map(master_df):
    p_map = {}
    cols = {str(c).strip().lower(): c for c in master_df.columns}
    
    p_no_key = next((cols[c] for c in cols if 'pirivena_no' in c or 'p_no' in c), master_df.columns[1] if len(master_df.columns) > 1 else None)
    name_key = next((cols[c] for c in cols if 'name' in c and 'pirivena' in c), next((cols[c] for c in cols if 'name' in c), master_df.columns[2] if len(master_df.columns) > 2 else None))
    dist_key = next((cols[c] for c in cols if 'district' in c or 'දිස්ත්‍රික්' in c or 'dist' in c), None)
    prov_key = next((cols[c] for c in cols if 'province' in c or 'පළාත්' in c or 'prov' in c), None)
    zone_key = next((cols[c] for c in cols if 'zone' in c or 'කලාප' in c or 'edu zone' in c), None)
    census_key = next((cols[c] for c in cols if 'census' in c or 'සංගණන' in c), master_df.columns[0] if len(master_df.columns) > 0 else None)

    # 💡 පළාත් සහ දිස්ත්‍රික්කවල අංක (Codes) වෙනුවට නිවැරදි නම් ලබා දීම සඳහා Mapping (ඔබේ දත්තවල ඇති අංක අනුව මෙහි නම් වෙනස් කරගත හැක)
    province_mapping = {
        "1": "Western", "2": "Central", "3": "Southern", "4": "Northern",
        "5": "Eastern", "6": "North Western", "7": "North Central", "8": "Uva", "9": "Sabaragamuwa"
    }
    
    district_mapping = {
        "1": "Colombo", "2": "Gampaha", "3": "Kalutara", "4": "Kandy", "5": "Matale", "6": "Nuwara Eliya",
        "7": "Galle", "8": "Matara", "9": "Hambantota", "10": "Jaffna", "11": "Kilinochchi", "12": "Mannar",
        "13": "Vavuniya", "14": "Mullaitivu", "15": "Batticaloa", "16": "Ampara", "17": "Trincomalee",
        "18": "Kurunegala", "19": "Puttalam", "20": "Anuradhapura", "21": "Polonnaruwa", "22": "Badulla",
        "23": "Monaragala", "24": "Ratnapura", "25": "Kegalle"
    }

    for _, row in master_df.iterrows():
        raw_p_no = row.get(p_no_key, "")
        p_no = str(raw_p_no).strip()
        if p_no.endswith(".0"):
            p_no = p_no[:-2]
            
        if p_no and p_no != "nan":
            raw_prov = str(row.get(prov_key, "Unknown")).strip() if prov_key else "Unknown"
            raw_dist = str(row.get(dist_key, "Unknown")).strip() if dist_key else "Unknown"

            # අංක ලෙස ඇත්නම් ඒවා නම් වලට හැරවීම (නැතහොත් මුල් නමම තබා ගැනීම)
            prov_name = province_mapping.get(raw_prov, raw_prov)
            dist_name = district_mapping.get(raw_dist, raw_dist)

            p_map[p_no] = {
                "census_no": str(row.get(census_key, "")) if census_key else "",
                "name": str(row.get(name_key, "Unknown")),
                "district": dist_name,
                "province": prov_name,
                "zone": str(row.get(zone_key, "Unknown")) if zone_key else "Unknown"
            }
    return p_map
