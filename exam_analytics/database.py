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
    dist_key = next((cols[c] for c in cols if 'district' in c or 'දිස්ත්‍රික්' in c), None)
    prov_key = next((cols[c] for c in cols if 'province' in c or 'පළාත්' in c), None)
    zone_key = next((cols[c] for c in cols if 'zone' in c or 'කලාප' in c or 'edu zone' in c), None)
    census_key = next((cols[c] for c in cols if 'census' in c or 'සංගණන' in c), master_df.columns[0] if len(master_df.columns) > 0 else None)

    for _, row in master_df.iterrows():
        raw_p_no = row.get(p_no_key, "")
        p_no = str(raw_p_no).strip()
        # දශමයක් සහිතව (උදා: 1117.0) තිබේ නම් .0 ඉවත් කර පිරිසිදු කරගැනීම
        if p_no.endswith(".0"):
            p_no = p_no[:-2]
            
        if p_no and p_no != "nan":
            p_map[p_no] = {
                "census_no": str(row.get(census_key, "")) if census_key else "",
                "name": str(row.get(name_key, "Unknown")),
                "district": str(row.get(dist_key, "Unknown")) if dist_key else "Unknown",
                "province": str(row.get(prov_key, "Unknown")) if prov_key else "Unknown",
                "zone": str(row.get(zone_key, "Unknown")) if zone_key else "Unknown"
            }
    return p_map