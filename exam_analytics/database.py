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
    
    # සියලුම තීරු නම් Upper case කර සෙවීම
    cols_map = {str(c).strip().upper(): c for c in master_df.columns}
    
    p_no_col = cols_map.get('PIRIVENA_N', master_df.columns[1] if len(master_df.columns) > 1 else None)
    name_col = cols_map.get('NAME OF THE PIRIVENA', cols_map.get('PIRIVENA NAME', master_df.columns[2] if len(master_df.columns) > 2 else None))
    
    # 'DISTRICT N' හෝ 'CODE' වැනි සංඛ්‍යාත්මක තීරු මඟහැර නියම පෙළ ඇති DISTRICT සහ PROVINCE තීරු තෝරා ගැනීම
    dist_col = next((cols_map[c] for c in cols_map if c == 'DISTRICT' or (c.startswith('DISTRICT') and 'N' not in c and 'CODE' not in c)), master_df.columns[4] if len(master_df.columns) > 4 else None)
    prov_col = next((cols_map[c] for c in cols_map if c == 'PROVINCE' or (c.startswith('PROVINCE') and 'N' not in c and 'CODE' not in c)), master_df.columns[6] if len(master_df.columns) > 6 else None)
    census_col = next((cols_map[c] for c in cols_map if 'CENSUS' in c), master_df.columns[0] if len(master_df.columns) > 0 else None)
    zone_col = next((cols_map[c] for c in cols_map if 'ZONE' in c), master_df.columns[7] if len(master_df.columns) > 7 else None)

    for _, row in master_df.iterrows():
        raw_p_no = row.get(p_no_col, "") if p_no_col else ""
        p_no = str(raw_p_no).strip()
        if p_no.endswith(".0"):
            p_no = p_no[:-2]
            
        if p_no and p_no != "nan":
            raw_prov = str(row.get(prov_col, "Unknown")).strip() if prov_col else "Unknown"
            if raw_prov.endswith(".0"): raw_prov = raw_prov[:-2]

            raw_dist = str(row.get(dist_col, "Unknown")).strip() if dist_col else "Unknown"
            if raw_dist.endswith(".0"): raw_dist = raw_dist[:-2]

            p_map[p_no] = {
                "census_no": str(row.get(census_col, "")) if census_col else "",
                "name": str(row.get(name_col, "Unknown")) if name_col else "Unknown",
                "district": raw_dist.title() if raw_dist.lower() != 'nan' and raw_dist != '' else "Unknown",
                "province": raw_prov.title() if raw_prov.lower() != 'nan' and raw_prov != '' else "Unknown",
                "zone": str(row.get(zone_col, "Unknown")).strip().title() if zone_col else "Unknown"
            }
    return p_map
