import pandas as pd
import re
from database import get_pirivena_map

# =========================================================================
# 1. පිරිවෙන් ශ්‍රේණිගත කිරීම් සහ ප්‍රගති කලාප ගණනය (Rankings & Zones)
# =========================================================================
def calculate_piriven_rankings(results_df, master_df, year, user_role, user_access):
    p_map = get_pirivena_map(master_df)
    
    pass_grades = ["A", "B", "C", "S", "1", "2", "3"]
    weightage = {"A": 10.0, "B": 8.0, "C": 6.5, "S": 5.0, "W": 0.0, "1": 10.0, "2": 8.0, "3": 6.5}
    invalid_grades = ["-", "AB", "ABSENT", "+", "", "NONE", "NAN"]
    
    is_sub_director = "subject director" in user_role.lower() or "විෂය අධ්‍යක්ෂ" in user_role.lower()
    sub_num = None
    if is_sub_director:
        match = re.search(r'\d+', str(user_access))
        if match:
            sub_num = match.group()

    p_stats = {}
    for p_no, p_info in p_map.items():
        p_stats[str(p_no).strip()] = {
            **p_info, 
            "pNo": str(p_no).strip(), 
            "applied": 0, 
            "sat": 0, 
            "pass": 0, 
            "totalStudentAverages": 0.0
        }

    yr_df = results_df[results_df["Year"].astype(str) == str(year).strip()]
    
    for _, row in yr_df.iterrows():
        p_no = str(row.get("Pirivena_No", "")).strip()
        if not p_no:
            continue
            
        if p_no not in p_stats:
            p_stats[p_no] = {
                "province": "Unknown", "name": "Unknown", "district": "Unknown", "zone": "Unknown", "census_no": "",
                "pNo": p_no, "applied": 0, "sat": 0, "pass": 0, "totalStudentAverages": 0.0
            }
        
        p_stats[p_no]["applied"] += 1
        
        # විෂය අධ්‍යක්ෂවරයෙකු නම් අදාළ විෂය පමණක් ගණනය කිරීම
        if is_sub_director and sub_num:
            g = str(row.get("GRD" + sub_num, "")).upper().strip()
            if g and g not in invalid_grades and "#ERR" not in g:
                p_stats[p_no]["sat"] += 1
                p_stats[p_no]["totalStudentAverages"] += weightage.get(g, 0.0)
                if g in pass_grades:
                    p_stats[p_no]["pass"] += 1
        else:
            student_points = 0.0
            student_actual_sat = 0
            pass_count = 0
            tripitaka_passed = False
            sinhala_or_pali_passed = False
            
            for i in range(1, 13):
                g = str(row.get(f"GRD{i}", "")).upper().strip()
                s_raw = str(row.get(f"SUB{i}", "")).strip()
                if s_raw.endswith(".0"):
                    s_raw = s_raw[:-2]
                
                # AB හෝ Absent නොවී විභාගයට පෙනී සිටි විෂයන් පමණක් ගණනය
                if g and g not in invalid_grades and "#ERR" not in g:
                    student_actual_sat += 1
                    student_points += weightage.get(g, 0.0)
                    if g in pass_grades:
                        pass_count += 1
                        if s_raw == "3": 
                            tripitaka_passed = True
                        if s_raw in ["1", "2"]:
                            sinhala_or_pali_passed = True
            
            # සිසුවෙකු විෂයයන් 6ක් හෝ ඊට වැඩි ගණනකට පෙනී සිටි විට පමණක් විභාගයට පෙනී සිටි (Sat) ලෙස සැලකීම
            if student_actual_sat >= 6:
                p_stats[p_no]["sat"] += 1
                p_stats[p_no]["totalStudentAverages"] += (student_points / student_actual_sat)
                
                # පිරිවෙන් සා.පෙළ සමත් නීතිය: (ත්‍රිපිටකය + සිංහල/පාලි + විෂයයන් 6ක් සමත්)
                if tripitaka_passed and sinhala_or_pali_passed and pass_count >= 6:
                    p_stats[p_no]["pass"] += 1

    ranking_list = []
    for p_no, data in p_stats.items():
        sat = data["sat"]
        pass_cnt = data["pass"]
        pass_rate = round((pass_cnt / sat * 100), 1) if sat > 0 else 0.0
        avg_score = round((data["totalStudentAverages"] / sat), 2) if sat > 0 else 0.0
        
        # විභාග සමත්වීමේ ප්‍රතිශතය මත පදනම්ව ප්‍රගති කලාප (Zones) තීරණය කිරීම
        if sat == 0:
            zone_color = "Red"
        elif pass_rate >= 75.0: 
            zone_color = "Green"
        elif pass_rate >= 50.0: 
            zone_color = "Yellow"
        elif pass_rate >= 35.0: 
            zone_color = "Orange"
        else: 
            zone_color = "Red"
        
        ranking_list.append({
            "දිවයිනේ ස්ථානය": 0,
            "පළාත් ස්ථානය": 0,
            "දිස්ත්‍රික් ස්ථානය": 0,
            "සංගණන අංකය": data.get("census_no", ""),
            "පිරිවෙන් අංකය": p_no,
            "පිරිවෙනේ නම": data.get("name", "Unknown"),
            "දිස්ත්‍රික්කය": str(data.get("district", "Unknown")).strip(),
            "පළාත": str(data.get("province", "Unknown")).strip(),
            "කලාපය": str(data.get("zone", "Unknown")).strip(),
            "අයදුම් කළ": data["applied"],
            "පෙනී සිටි": sat,
            "සමත්": pass_cnt,
            "සමත් ප්‍රතිශතය (%)": pass_rate,
            "Quality Score (QS)": avg_score,
            "zoneColor": zone_color
        })

    # ශ්‍රේණිගත කිරීම: ප්‍රධාන වශයෙන් සමත් ප්‍රතිශතය (Pass %), දෙවනුව Quality Score (QS)
    sorted_ranking = sorted(ranking_list, key=lambda x: (x["සමත් ප්‍රතිශතය (%)"], x["Quality Score (QS)"]), reverse=True)
    for i, p in enumerate(sorted_ranking):
        p["දිවයිනේ ස්ථානය"] = i + 1

    # පළාත් සහ දිස්ත්‍රික් මට්ටමේ ශ්‍රේණිගත කිරීම
    df_temp = pd.DataFrame(sorted_ranking)
    if not df_temp.empty:
        df_temp["පළාත් ස්ථානය"] = df_temp.groupby("පළාත")["සමත් ප්‍රතිශතය (%)"].rank(ascending=False, method="min").astype(int)
        df_temp["දිස්ත්‍රික් ස්ථානය"] = df_temp.groupby("දිස්ත්‍රික්කය")["සමත් ප්‍රතිශතය (%)"].rank(ascending=False, method="min").astype(int)
        sorted_ranking = df_temp.to_dict(orient="records")

    filtered_ranking = []
    u_role_lower = user_role.lower()
    u_access_upper = str(user_access).upper().strip()

    for p in sorted_ranking:
        p_prov_upper = str(p.get("පළාත", "")).upper().strip()
        if "super admin" in u_role_lower or "admin" in u_role_lower or u_access_upper in ["ALL", "ALL SUMMARY VIEW", ""]:
            filtered_ranking.append(p)
        elif "province" in u_role_lower and p_prov_upper == u_access_upper:
            filtered_ranking.append(p)
        elif is_sub_director:
            filtered_ranking.append(p)
            
    return filtered_ranking


# =========================================================================
# 2. සමස්ත විෂය සාරාංශය (Overall Subject Summary)
# =========================================================================
def get_subject_summary(results_df, year):
    yr_df = results_df[results_df["Year"].astype(str) == str(year)]
    subject_names = {
        "1": "සිංහල", "2": "පාලි", "3": "ත්‍රිපිටක ධර්මය", "4": "සංස්කෘත",
        "5": "ගණිතය", "6": "ඉංග්‍රීසි", "7": "ඉතිහාසය", "8": "සමාජ විද්‍යාව",
        "9": "සෞඛ්‍ය විද්‍යාව", "10": "භූගෝල විද්‍යාව", "11": "සාමාන්‍ය විද්‍යාව", "12": "දෙමළ"
    }
    
    sub_stats = {k: {"විෂයය": v, "පෙනී සිටි සංඛ්‍යාව": 0, "සමත් (A-S/1-3) සංඛ්‍යාව": 0, "සමත් ප්‍රතිශතය (%)": 0.0} for k, v in subject_names.items()}
    pass_grades = ["A", "B", "C", "S", "1", "2", "3"]
    invalid_grades = ["-", "AB", "ABSENT", "+", "", "NONE", "NAN"]

    for _, row in yr_df.iterrows():
        for i in range(1, 13):
            g = str(row.get(f"GRD{i}", "")).upper().strip()
            s_raw = str(row.get(f"SUB{i}", "")).strip()
            if s_raw.endswith(".0"):
                s_raw = s_raw[:-2]
                
            if s_raw in sub_stats and g and g not in invalid_grades and "#ERR" not in g:
                sub_stats[s_raw]["පෙනී සිටි සංඛ්‍යාව"] += 1
                if g in pass_grades:
                    sub_stats[s_raw]["සමත් (A-S/1-3) සංඛ්‍යාව"] += 1

    for k in sub_stats:
        sat = sub_stats[k]["පෙනී සිටි සංඛ්‍යාව"]
        pas = sub_stats[k]["සමත් (A-S/1-3) සංඛ්‍යාව"]
        sub_stats[k]["සමත් ප්‍රතිශතය (%)"] = round((pas / sat * 100), 1) if sat > 0 else 0.0

    return pd.DataFrame(list(sub_stats.values()))


# =========================================================================
# 3. වසර 4ක ප්‍රතිඵල ඉතිහාසය (Four-Year History)
# =========================================================================
def get_four_year_history(results_df):
    years = ["2022", "2023", "2024", "2025"]
    history_data = []
    pass_grades = ["A", "B", "C", "S", "1", "2", "3"]
    invalid_grades = ["-", "AB", "ABSENT", "+", "", "NONE", "NAN"]
    
    for yr in years:
        yr_df = results_df[results_df["Year"].astype(str) == yr]
        applied = len(yr_df)
        sat = 0
        passed = 0
        
        for _, row in yr_df.iterrows():
            actual_sat = 0
            p_cnt = 0
            tripitaka_passed = False
            sinhala_or_pali_passed = False
            
            for i in range(1, 13):
                g = str(row.get(f"GRD{i}", "")).upper().strip()
                s_raw = str(row.get(f"SUB{i}", "")).strip()
                if s_raw.endswith(".0"):
                    s_raw = s_raw[:-2]
                    
                if g and g not in invalid_grades and "#ERR" not in g:
                    actual_sat += 1
                    if g in pass_grades:
                        p_cnt += 1
                        if s_raw == "3": 
                            tripitaka_passed = True
                        if s_raw in ["1", "2"]:
                            sinhala_or_pali_passed = True
                            
            if actual_sat >= 6:
                sat += 1
                if tripitaka_passed and sinhala_or_pali_passed and p_cnt >= 6:
                    passed += 1

        history_data.append({"වර්ෂය": yr, "අයදුම් කළ": applied, "පෙනී සිටි": sat, "සමත්": passed})
        
    return pd.DataFrame(history_data)


# =========================================================================
# 4. විෂය සහ දිස්ත්‍රික් මට්ටමේ විස්තරාත්මක විශ්ලේෂණය
# =========================================================================
def get_detailed_subject_analysis(results_df, master_df, year, selected_subject_code):
    p_map = get_pirivena_map(master_df)
    yr_df = results_df[results_df["Year"].astype(str) == str(year)]
    
    grade_counts = {"A": 0, "B": 0, "C": 0, "S": 0, "W": 0}
    district_data = {}
    invalid_grades = ["-", "AB", "ABSENT", "+", "", "NONE", "NAN"]
    
    sel_code_str = str(selected_subject_code).strip()
    if sel_code_str.endswith(".0"):
        sel_code_str = sel_code_str[:-2]
    
    for _, row in yr_df.iterrows():
        p_no = str(row.get("Pirivena_No", "")).strip()
        p_info = p_map.get(p_no, {"district": "Unknown", "province": "Unknown"})
        dist = str(p_info.get("district", "Unknown")).strip()
        
        if dist not in district_data:
            district_data[dist] = {"A": 0, "B": 0, "C": 0, "S": 0, "W": 0, "sat": 0, "pass": 0}
            
        for i in range(1, 13):
            s_raw = str(row.get(f"SUB{i}", "")).strip()
            if s_raw.endswith(".0"):
                s_raw = s_raw[:-2]
                
            if s_raw == sel_code_str:
                g = str(row.get(f"GRD{i}", "")).upper().strip()
                
                # AB හෝ Absent අය විභාගයට පෙනී සිටි ලෙස නොගැනීම
                if not g or g in invalid_grades or "#ERR" in g:
                    continue
                    
                grade_key = None
                if g in ["A", "1"]: grade_key = "A"
                elif g in ["B", "2"]: grade_key = "B"
                elif g in ["C", "3"]: grade_key = "C"
                elif g in ["S"]: grade_key = "S"
                elif g in ["W", "F"]: grade_key = "W"
                
                if grade_key:
                    grade_counts[grade_key] += 1
                    district_data[dist][grade_key] += 1
                    district_data[dist]["sat"] += 1
                    if grade_key in ["A", "B", "C", "S"]:
                        district_data[dist]["pass"] += 1

    dist_list = []
    for dist, d in district_data.items():
        sat = d["sat"]
        if sat == 0:
            continue
        pas = d["pass"]
        rate = (pas / sat * 100) if sat > 0 else 0.0
        dist_list.append({
            "දිස්ත්‍රික්කය": dist,
            "A": d["A"],
            "B": d["B"],
            "C": d["C"],
            "S": d["S"],
            "W": d["W"],
            "පෙනී සිටි": sat,
            "සමත්": pas,
            "සමත් ප්‍රතිශතය (%)": round(rate, 1)
        })
        
    df_dist = pd.DataFrame(dist_list)
    if not df_dist.empty:
        df_dist = df_dist.sort_values(by="සමත් ප්‍රතිශතය (%)", ascending=False)
        
    return grade_counts, df_dist


# =========================================================================
# 5. වාර්ෂික වාර්තා දත්ත (Yearly Report Data)
# =========================================================================
def get_yearly_report_data(results_df, master_df, year, user_role, user_access):
    p_map = get_pirivena_map(master_df)
    
    is_sub_director = "subject director" in user_role.lower() or "විෂය අධ්‍යක්ෂ" in user_role.lower()
    sub_num = None
    if is_sub_director:
        match = re.search(r'\d+', str(user_access))
        if match:
            sub_num = match.group()

    years = ["2022", "2023", "2024", "2025"]
    pirivena_records = {}

    for p_no, p_info in p_map.items():
        p_no_str = str(p_no).strip()
        init_row = {
            "p_no": p_no_str,
            "name": p_info.get('name', 'Unknown'),
            "district": p_info.get('district', 'Unknown').upper(),
            "province": p_info.get('province', 'Unknown'),
            "zone": "Red"
        }
        for y in years:
            for g in ["A", "B", "C", "S", "W"]:
                init_row[f"{y}_{g}"] = 0
        init_row["pass_pct"] = 0.0
        init_row["fail_pct"] = 0.0
        init_row["zone"] = "Red"
        pirivena_records[p_no_str] = init_row

    for _, row in results_df.iterrows():
        yr = str(row.get("Year", "")).strip()
        if yr not in years:
            continue
            
        p_no = str(row.get("Pirivena_No", "")).strip()
        if not p_no or p_no not in pirivena_records:
            continue
            
        p_info = p_map.get(p_no, {})
        u_access_upper = str(user_access).upper()
        if "province" in user_role.lower() and str(p_info.get("province", "")).upper() != u_access_upper:
            if not ("super admin" in user_role.lower() or "admin" in user_role.lower() or u_access_upper in ["ALL", "ALL SUMMARY VIEW"]):
                continue

        if is_sub_director and sub_num:
            g = str(row.get("GRD" + sub_num, "")).upper().strip()
            if g in ["1", "A"]: g_key = "A"
            elif g in ["2", "B"]: g_key = "B"
            elif g in ["3", "C"]: g_key = "C"
            elif g == "S": g_key = "S"
            elif g in ["W", "F"]: g_key = "W"
            else: g_key = None
            
            if g_key:
                pirivena_records[p_no][f"{yr}_{g_key}"] += 1
        else:
            for i in range(1, 13):
                g = str(row.get(f"GRD{i}", "")).upper().strip()
                if g in ["1", "A"]: g_key = "A"
                elif g in ["2", "B"]: g_key = "B"
                elif g in ["3", "C"]: g_key = "C"
                elif g == "S": g_key = "S"
                elif g in ["W", "F"]: g_key = "W"
                else: g_key = None
                
                if g_key:
                    pirivena_records[p_no][f"{yr}_{g_key}"] += 1

    final_rows = []
    for p_no, d in pirivena_records.items():
        total_sat_2025 = sum([d[f"2025_{g}"] for g in ["A", "B", "C", "S", "W"]])
        total_pass_2025 = sum([d[f"2025_{g}"] for g in ["A", "B", "C", "S"]])
        
        pass_pct = (total_pass_2025 / total_sat_2025 * 100) if total_sat_2025 > 0 else 0.0
        fail_pct = (d["2025_W"] / total_sat_2025 * 100) if total_sat_2025 > 0 else 0.0
        
        if total_sat_2025 == 0:
            zone = "Red"
        elif pass_pct >= 75.0: zone = "Green"
        elif pass_pct >= 50.0: zone = "Yellow"
        elif pass_pct >= 35.0: zone = "Orange"
        else: zone = "Red"
        
        d["pass_pct"] = f"{pass_pct:.1f}%"
        d["fail_pct"] = f"{fail_pct:.1f}%"
        d["zone"] = zone
        
        final_rows.append(d)

    return pd.DataFrame(final_rows)


# =========================================================================
# 6. තනි පිරිවෙන් විශ්ලේෂණය (Single Pirivena Full Analysis)
# =========================================================================
def get_single_pirivena_full_analysis(results_df, master_df, pirivena_key, year, user_role, user_access):
    p_map = get_pirivena_map(master_df)
    
    target_p_no = None
    k_clean = str(pirivena_key).strip().lower()
    
    for p_no, p_info in p_map.items():
        p_no_s = str(p_no).strip().lower()
        p_name = str(p_info.get("name", "")).strip().lower()
        p_census = str(p_info.get("census_no", "")).strip().lower()
        
        if k_clean in p_no_s or k_clean in p_census or k_clean in p_name:
            target_p_no = str(p_no).strip()
            break
            
    if not target_p_no or target_p_no not in p_map:
        return None, "පිරිවෙන හමු නොවීය. කරුණාකර නිවැරදි අංකයක් හෝ නමක් ඇතුළත් කරන්න."
        
    p_info = p_map[target_p_no]
    
    rankings = calculate_piriven_rankings(results_df, master_df, year, user_role, user_access)
    pirivena_rank_data = None
    for r in rankings:
        if str(r["පිරිවෙන් අංකය"]) == target_p_no:
            pirivena_rank_data = r
            break
            
    if not pirivena_rank_data:
        pirivena_rank_data = {
            "දිවයිනේ ස්ථානය": "-",
            "පළාත් ස්ථානය": "-",
            "දිස්ත්‍රික් ස්ථානය": "-",
            "Quality Score (QS)": 0.0,
            "සමත් ප්‍රතිශතය (%)": 0.0,
            "zoneColor": "Red"
        }

    is_sub_director = "subject director" in user_role.lower() or "විෂය අධ්‍යක්ෂ" in user_role.lower()
    sub_num = None
    if is_sub_director:
        match = re.search(r'\d+', str(user_access))
        if match:
            sub_num = match.group()

    # වර්ෂ 4ක ඉතිහාසය (2022 - 2025)
    years = ["2022", "2023", "2024", "2025"]
    history_rows = []
    pass_grades = ["A", "B", "C", "S", "1", "2", "3"]
    invalid_grades = ["-", "AB", "ABSENT", "+", "", "NONE", "NAN"]
    
    for yr in years:
        yr_df = results_df[(results_df["Pirivena_No"].astype(str).str.strip() == target_p_no) & 
                           (results_df["Year"].astype(str) == yr)]
        sat_cnt = 0
        pass_cnt = 0
        for _, row in yr_df.iterrows():
            if is_sub_director and sub_num:
                g = str(row.get("GRD" + sub_num, "")).upper().strip()
                if g and g not in invalid_grades and "#ERR" not in g:
                    sat_cnt += 1
                    if g in pass_grades:
                        pass_cnt += 1
            else:
                actual_sat = 0
                p_c = 0
                trip_p = False
                sin_p = False
                for i in range(1, 13):
                    g = str(row.get(f"GRD{i}", "")).upper().strip()
                    s_raw = str(row.get(f"SUB{i}", "")).strip()
                    if s_raw.endswith(".0"): s_raw = s_raw[:-2]
                    if g and g not in invalid_grades and "#ERR" not in g:
                        actual_sat += 1
                        if g in pass_grades:
                            p_c += 1
                            if s_raw == "3": trip_p = True
                            if s_raw in ["1", "2"]: sin_p = True
                if actual_sat >= 6:
                    sat_cnt += 1
                    if trip_p and sin_p and p_c >= 6:
                        pass_cnt += 1
        history_rows.append({"වර්ෂය": yr, "පෙනී සිටි": sat_cnt, "සමත්": pass_cnt})

    current_yr_df = results_df[(results_df["Pirivena_No"].astype(str).str.strip() == target_p_no) & 
                               (results_df["Year"].astype(str) == str(year))]
    
    subject_names = {
        "1": "සිංහල", "2": "පාලි", "3": "ත්‍රිපිටක ධර්මය", "4": "සංස්කෘත",
        "5": "ගණිතය", "6": "ඉංග්‍රීසි", "7": "ඉතිහාසය", "8": "සමාජ විද්‍යාව",
        "9": "සෞඛ්‍ය විද්‍යාව", "10": "භූගෝල විද්‍යාව", "11": "සාමාන්‍ය විද්‍යාව", "12": "දෙමළ"
    }
    
    sub_stats = {}
    for s_code, s_name in subject_names.items():
        if is_sub_director and sub_num and s_code != sub_num:
            continue
        sub_stats[s_code] = {"code": s_code, "name": s_name, "A": 0, "B": 0, "C": 0, "S": 0, "W": 0, "sat": 0, "pass": 0}

    for _, row in current_yr_df.iterrows():
        for i in range(1, 13):
            s_raw = str(row.get(f"SUB{i}", "")).strip()
            if s_raw.endswith(".0"): s_raw = s_raw[:-2]
            if s_raw in sub_stats:
                g = str(row.get(f"GRD{i}", "")).upper().strip()
                if not g or g in invalid_grades or "#ERR" in g:
                    continue

                gk = None
                if g in ["A", "1"]: gk = "A"
                elif g in ["B", "2"]: gk = "B"
                elif g in ["C", "3"]: gk = "C"
                elif g == "S": gk = "S"
                elif g in ["W", "F"]: gk = "W"
                
                if gk:
                    sub_stats[s_raw][gk] += 1
                    sub_stats[s_raw]["sat"] += 1
                    if gk in ["A", "B", "C", "S"]:
                        sub_stats[s_raw]["pass"] += 1

    subject_rows = []
    for s_code, d in sub_stats.items():
        sat = d["sat"]
        if sat == 0:
            continue
            
        pas = d["pass"]
        rate = (pas / sat * 100) if sat > 0 else 0.0
        subject_rows.append({
            "විෂය කේතය": f"SUB{s_code} - {d['name']}",
            "A": d["A"], "B": d["B"], "C": d["C"], "S": d["S"], "W": d["W"],
            "පෙනී සිටි": sat,
            "සමත්": pas,
            "සමත් %": f"{rate:.1f}%"
        })

    qs_val = pirivena_rank_data.get("Quality Score (QS)", 0.0)
    zone = pirivena_rank_data.get("zoneColor", "Red")

    result_data = {
        "p_no": target_p_no,
        "name": p_info.get("name", "Unknown"),
        "census_no": p_info.get("census_no", ""),
        "district": p_info.get("district", "Unknown"),
        "province": p_info.get("province", "Unknown"),
        "zone": zone,
        "qs": qs_val,
        "island_rank": pirivena_rank_data.get("දිවයිනේ ස්ථානය", "-"),
        "province_rank": pirivena_rank_data.get("පළාත් ස්ථානය", "-"),
        "district_rank": pirivena_rank_data.get("දිස්ත්‍රික් ස්ථානය", "-"),
        "pass_rate": f"{pirivena_rank_data.get('සමත් ප්‍රතිශතය (%)', 0.0)}%",
        "history": history_rows,
        "subjects": subject_rows
    }
    
    return result_data, None
