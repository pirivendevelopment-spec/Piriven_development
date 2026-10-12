import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# Sub-folder path නිවැරදිව ලබාගැනීම
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import load_data
from logic import (
    calculate_piriven_rankings, 
    get_four_year_history, 
    get_detailed_subject_analysis, 
    get_yearly_report_data, 
    get_single_pirivena_full_analysis
)

st.set_page_config(page_title="Piriven Analytics System - 2026", layout="wide")

# --- Custom CSS (Clean Light Theme) ---
st.markdown("""
    <style>
        .main, .stApp {
            background-color: #f4f7f6 !important;
            color: #1e293b !important;
            font-family: 'Segoe UI', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #1e293b !important;
        }

        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] .stButton button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 15px !important;
            transition: all 0.3s ease;
        }

        [data-testid="stSidebar"] .stButton button[kind="secondary"] {
            background-color: #1f2937 !important;
            color: #94a3b8 !important;
            border: 1px solid #374151 !important;
        }
        [data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
            background-color: #374151 !important;
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] .stButton button[kind="primary"] {
            background-color: #0f766e !important;
            color: #ffffff !important;
            border: none !important;
        }

        .logout-btn button {
            background-color: #dc3545 !important;
            color: white !important;
            border: none !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 15px !important;
        }
        .logout-btn button:hover {
            background-color: #b02a37 !important;
            color: white !important;
        }

        .kpi-card {
            background: #ffffff;
            padding: 20px; border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            text-align: center; border-top: 5px solid #0f766e;
            margin-bottom: 15px;
            border: 1px solid #cbd5e1;
        }
        .kpi-title { font-size: 15px; color: #334155; font-weight: bold; text-transform: uppercase; }
        .kpi-value { font-size: 30px; color: #0f766e; font-weight: bold; margin-top: 5px; }
        
        .zone-green { background: #d1e7dd; border-top: 5px solid #198754; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.04); }
        .zone-yellow { background: #fff3cd; border-top: 5px solid #ffc107; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.04); }
        .zone-orange { background: #ffe5d0; border-top: 5px solid #fd7e14; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.04); }
        .zone-red { background: #f8d7da; border-top: 5px solid #dc3545; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.04); }
        
        .zone-title { font-size: 13px; font-weight: bold; color: #1e293b; text-transform: uppercase; }
        .zone-count { font-size: 26px; font-weight: bold; margin-top: 5px; color: #0f172a; }

        @media print {
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            body, .main, .stApp { 
                background-color: #ffffff !important; 
                color: #000000 !important; 
            }
            [data-testid="stSidebar"], header, footer, .stButton { 
                display: none !important; 
            }
            table {
                background-color: #ffffff !important; 
                color: #000000 !important; 
                border: 1px solid #94a3b8 !important;
                box-shadow: none !important;
            }
            th {
                background-color: #1a252f !important;
                color: #ffffff !important;
            }
            td {
                background-color: #ffffff !important; 
                color: #000000 !important; 
            }
            .print-footer-global {
                display: block !important;
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                text-align: center;
                font-size: 10px;
                color: #444;
                border-top: 1px solid #bbb;
                padding-top: 5px;
                font-family: 'Segoe UI', sans-serif;
                background: white;
            }
        }
        .print-footer-global { display: none; }
    </style>
""", unsafe_allow_html=True)

# දත්ත පූරණය
load_result = load_data()
if isinstance(load_result, (list, tuple)):
    users_df = load_result[0] if len(load_result) > 0 else None
    results_df = load_result[1] if len(load_result) > 1 else None
    master_df = load_result[2] if len(load_result) > 2 else None
else:
    users_df, results_df, master_df = None, None, None

if users_df is None or results_df is None or master_df is None:
    st.error("⚠️ දත්ත සමුදාය (Database) සාර්ථකව පූරණය කළ නොහැක.")
    st.stop()

# Session State & Persistent Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

queryParams = st.query_params
if not st.session_state.logged_in and "auth_user" in queryParams:
    saved_user = queryParams["auth_user"]
    for _, row in users_df.iterrows():
        db_user = str(row.get("Username", row.get("username", ""))).strip().lower()
        if db_user == saved_user.lower():
            st.session_state.logged_in = True
            st.session_state.user = {
                "username": db_user,
                "name": row.get("Name", "පරිශීලකයා"),
                "role": str(row.get("Role", "Guest")).strip(),
                "access": str(row.get("Access", "")).strip()
            }
            break

# -------------------------------------------------------------
# 1. LOGIN SCREEN
# -------------------------------------------------------------
if not st.session_state.logged_in or not st.session_state.user:
    st.markdown("""
        <style>
            .stApp {
                background-color: #eef2f5 !important;
            }
            [data-testid="stSidebar"] {
                display: none !important;
            }
            header { visibility: hidden !important; }
            div[data-testid="stForm"] {
                background-color: #ffffff !important;
                padding: 40px 30px !important;
                border-radius: 18px !important;
                border: 1px solid #cbd5e1 !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    left_gap, center_col, right_gap = st.columns([1, 1.3, 1])
    
    with center_col:
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            logo_path = os.path.join(CURRENT_DIR, "logo.png")
            if os.path.exists(logo_path):
                import base64
                with open(logo_path, "rb") as f:
                    b64_logo = base64.b64encode(f.read()).decode("utf-8")
                st.markdown(f'<img src="data:image/png;base64,{b64_logo}" width="80" style="display:block; margin: 0 auto 15px auto; border-radius: 6px;">', unsafe_allow_html=True)

            st.markdown("<h3 style='text-align: center; color: #0f766e; margin-bottom: 0px;'>පිරිවෙන් අධ්‍යාපන අංශය</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; margin-bottom: 25px;'>විභාග ප්‍රතිඵල විශ්ලේෂණ පද්ධතිය - 2026</p>", unsafe_allow_html=True)

            username = st.text_input("👤 පරිශීලක නාමය (Username)")
            password = st.text_input("🔑 මුරපදය (Password)", type="password")
            remember_me = st.checkbox("🔄 දින 3ක් පුරා මා මතක තබා ගන්න (Remember Me)")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("පද්ධතියට ඇතුල් වන්න", use_container_width=True)

            if submit_btn:
                u_clean = username.strip().lower()
                p_clean = password.strip()
                matched_user = None
                for _, row in users_df.iterrows():
                    db_user = str(row.get("Username", row.get("username", ""))).strip().lower()
                    db_pass = str(row.get("Password", row.get("password", ""))).strip()
                    if db_user == u_clean and db_pass == p_clean:
                        matched_user = row.to_dict()
                        break

                if matched_user:
                    st.session_state.logged_in = True
                    st.session_state.user = {
                        "username": u_clean,
                        "name": matched_user.get("Name", "පරිශීලකයා"),
                        "role": str(matched_user.get("Role", "Guest")).strip(),
                        "access": str(matched_user.get("Access", "")).strip()
                    }
                    if remember_me:
                        st.query_params["auth_user"] = u_clean
                    st.rerun()
                else:
                    st.error("⚠️ පරිශීලක නාමය හෝ මුරපදය වැරදියි!")

# -------------------------------------------------------------
# 2. MAIN LOGGED-IN VIEW
# -------------------------------------------------------------
else:
    user = st.session_state.user
    role = user.get("role", "Guest")
    access = user.get("access", "")

    # Sidebar
    with st.sidebar:
        logo_path = os.path.join(CURRENT_DIR, "logo.png")
        if os.path.exists(logo_path):
            import base64
            with open(logo_path, "rb") as f:
                encoded_sidebar_logo = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 5px;">
                    <img src="data:image/png;base64,{encoded_sidebar_logo}" width="75" style="display: block; margin: 0 auto; border-radius: 8px;">
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center; padding: 2px 0;">
                <h3 style="color: #f8fafc; margin-bottom: 2px; font-size: 15px;">පිරිවෙන් අධ්‍යාපන අංශය</h3>
                <p style="color: #94a3b8; font-size: 10px; margin-top: 0;">විභාග ප්‍රතිඵල විශ්ලේෂණ පද්ධතිය</p>
            </div>
            <hr style="border-color: #374151; margin: 8px 0 12px 0;">
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background: #1f2937; padding: 12px 15px; border-radius: 10px; border-left: 4px solid #0f766e; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                <div style="font-size: 14px; font-weight: bold; color: #f3f4f6;">👤 {user.get('name', 'පරිශීලකයා')}</div>
                <div style="font-size: 12px; color: #38bdf8; margin-top: 4px;">තනතුර: <b>{role}</b></div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">අනුමැතිය: {access}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 13px; color: #94a3b8; font-weight: bold; margin-bottom: 8px;'>ප්‍රධාන මෙනුව</p>", unsafe_allow_html=True)

        if 'menu_selection' not in st.session_state:
            st.session_state.menu_selection = "සාරාංශ පුවරුව (Summary)"

        menu_options = [
            ("📊 සාරාංශ පුවරුව (Summary)", "සාරාංශ පුවරුව (Summary)"),
            ("📚 විෂය සාරාංශය", "විෂය සාරාංශය (Subjects)"),
            ("📈 වාර්ෂික වාර්තාව", "වාර්ෂික වාර්තාව (Yearly Report)"),
            ("🏆 පළාත් හා ශ්‍රේණිගත කිරීම්", "පළාත් හා ශ්‍රේණිගත කිරීම් (Rankings)"),
            ("🔍 පිරිවෙන් විශ්ලේෂණය", "පිරිවෙන් විශ්ලේෂණය")
        ]

        for label, val in menu_options:
            is_selected = st.session_state.menu_selection == val
            btn_type = "primary" if is_selected else "secondary"
            if st.sidebar.button(label, key=f"menu_btn_{val}", use_container_width=True, type=btn_type):
                st.session_state.menu_selection = val
                st.rerun()

        menu = st.session_state.menu_selection

        st.markdown("<br>", unsafe_allow_html=True)
        selected_year = st.sidebar.selectbox("විභාග වර්ෂය තෝරන්න", ["2025", "2024", "2023", "2022"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.sidebar.button("🚪 පද්ධතියෙන් ඉවත් වන්න", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            if "auth_user" in st.query_params:
                del st.query_params["auth_user"]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # VIEW 1: සාරාංශ පුවරුව (Summary)
    # =========================================================================
    if menu == "සාරාංශ පුවරුව (Summary)":
        st.markdown("### 📊 සාරාංශ පුවරුව")
        st.markdown(f"<p style='color: #334155; font-size: 16px;'>පිරිවෙන් සාමාන්‍ය පෙළ විභාග ප්‍රතිඵල විශ්ලේෂණය - <b>{selected_year}</b></p>", unsafe_allow_html=True)
        st.markdown("---")
        
        ranking_data = calculate_piriven_rankings(results_df, master_df, selected_year, role, access)
        
        if not ranking_data:
            st.warning("දත්ත හමු නොවීය.")
        else:
            tot_applied = sum(d["අයදුම් කළ"] for d in ranking_data)
            tot_sat = sum(d["පෙනී සිටි"] for d in ranking_data)
            tot_pass = sum(d["සමත්"] for d in ranking_data)
            overall_rate = f"{(tot_pass / tot_sat * 100):.1f}%" if tot_sat > 0 else "0%"
            
            green_count = sum(1 for d in ranking_data if d["zoneColor"] == "Green")
            yellow_count = sum(1 for d in ranking_data if d["zoneColor"] == "Yellow")
            orange_count = sum(1 for d in ranking_data if d["zoneColor"] == "Orange")
            red_count = sum(1 for d in ranking_data if d["zoneColor"] == "Red")
            
            green_passed_students = sum(d["සමත්"] for d in ranking_data if d["zoneColor"] == "Green")
            yellow_passed_students = sum(d["සමත්"] for d in ranking_data if d["zoneColor"] == "Yellow")
            orange_passed_students = sum(d["සමත්"] for d in ranking_data if d["zoneColor"] == "Orange")
            red_passed_students = sum(d["සමත්"] for d in ranking_data if d["zoneColor"] == "Red")

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f'<div class="kpi-card"><div class="kpi-title">අයදුම් කළ සංඛ්‍යාව</div><div class="kpi-value">{tot_applied:,}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card"><div class="kpi-title">පෙනී සිටි සංඛ්‍යාව</div><div class="kpi-value">{tot_sat:,}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card"><div class="kpi-title">සමත් සංඛ්‍යාව</div><div class="kpi-value">{tot_pass:,}</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="kpi-card" style="background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%); border-top: 5px solid #084298;"><div class="kpi-title" style="color: #fff;">සමත් ප්‍රතිශතය</div><div class="kpi-value" style="color: #fff;">{overall_rate}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            z1, z2, z3, z4 = st.columns(4)
            z1.markdown(f'''
                <div class="zone-green">
                    <div class="zone-title">🟢 GREEN ZONE (75%+)</div>
                    <div class="zone-count">{green_count} <span style="font-size: 13px; font-weight: normal; color: #1e293b;">පිරිවෙන්</span></div>
                    <div style="font-size: 11.5px; color: #15803d; margin-top: 4px; font-weight: 600;">සමත් සිසුන්: {green_passed_students:,}</div>
                </div>
            ''', unsafe_allow_html=True)

            z2.markdown(f'''
                <div class="zone-yellow">
                    <div class="zone-title">🟡 YELLOW ZONE (50%+)</div>
                    <div class="zone-count">{yellow_count} <span style="font-size: 13px; font-weight: normal; color: #1e293b;">පිරිවෙන්</span></div>
                    <div style="font-size: 11.5px; color: #b45309; margin-top: 4px; font-weight: 600;">සමත් සිසුන්: {yellow_passed_students:,}</div>
                </div>
            ''', unsafe_allow_html=True)

            z3.markdown(f'''
                <div class="zone-orange">
                    <div class="zone-title">🟠 ORANGE ZONE (35%+)</div>
                    <div class="zone-count">{orange_count} <span style="font-size: 13px; font-weight: normal; color: #1e293b;">පිරිවෙන්</span></div>
                    <div style="font-size: 11.5px; color: #c2410c; margin-top: 4px; font-weight: 600;">සමත් සිසුන්: {orange_passed_students:,}</div>
                </div>
            ''', unsafe_allow_html=True)

            z4.markdown(f'''
                <div class="zone-red">
                    <div class="zone-title">🔴 RED ZONE (< 35%)</div>
                    <div class="zone-count">{red_count} <span style="font-size: 13px; font-weight: normal; color: #1e293b;">පිරිවෙන්</span></div>
                    <div style="font-size: 11.5px; color: #b91c1c; margin-top: 4px; font-weight: 600;">සමත් සිසුන්: {red_passed_students:,}</div>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown("---")
            col_chart, col_dist = st.columns([2, 1])
            
            with col_chart:
                st.subheader("📈 වසර 4ක ප්‍රතිඵල ප්‍රගතිය (2022 - 2025)")
                hist_df = get_four_year_history(results_df)
                fig = px.bar(
                    hist_df, x="වර්ෂය", y=["අයදුම් කළ", "පෙනී සිටි", "සමත්"],
                    barmode="group",
                    template="plotly_white",
                    color_discrete_map={"අයදුම් කළ": "#94a3b8", "පෙනී සිටි": "#0f766e", "සමත්": "#042f2e"}
                )
                fig.update_layout(
                    plot_bgcolor="#ffffff", 
                    paper_bgcolor="#ffffff", 
                    margin=dict(l=20, r=20, t=20, b=20),
                    bargap=0.25,     
                    bargroupgap=0.1    
                )
                fig.update_traces(marker=dict(cornerradius=6))
                st.plotly_chart(fig, use_container_width=True)
                
            with col_dist:
                st.subheader("📍 දිස්ත්‍රික් ප්‍රගතිය")
                dist_df = pd.DataFrame(ranking_data)
                if not dist_df.empty:
                    dist_summary = dist_df.groupby("දිස්ත්‍රික්කය")["සමත් ප්‍රතිශතය (%)"].mean().reset_index()
                    dist_summary = dist_summary.sort_values(by="සමත් ප්‍රතිශතය (%)", ascending=False)
                    st.dataframe(dist_summary, use_container_width=True, height=350, hide_index=True)

    # =========================================================================
    # VIEW 2: පළාත් හා ශ්‍රේණිගත කිරීම් (Rankings - Fixed District & Provincial Ranks)
    # =========================================================================
    elif menu == "පළාත් හා ශ්‍රේණිගත කිරීම් (Rankings)":
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown("### 🏆 පිරිවෙන් සාධන ශ්‍රේණිගත කිරීම් (Rankings)")
        with col_h2:
            components.html("""
                <div style="text-align: right; margin-top: 5px;">
                    <button onclick="parent.window.print()" style="background-color: #0f766e; color: white; padding: 10px 18px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: bold; font-family: 'Segoe UI', sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                        🖨 ප්‍රින්ට් සෙටින්ග්ස් / PDF
                    </button>
                </div>
            """, height=50)
            
        st.markdown("---")
        
        ranking_data = calculate_piriven_rankings(results_df, master_df, selected_year, role, access)
        if not ranking_data:
            st.info("දත්ත නොමැත.")
        else:
            df_rank = pd.DataFrame(ranking_data)
            df_rank.columns = df_rank.columns.str.strip()

            # Dynamic column identification for Province and District to avoid any KeyError
            prov_col = next((c for c in df_rank.columns if 'පළාත' in c or 'province' in c.lower()), 'පළාත')
            dist_col = next((c for c in df_rank.columns if 'දිස්ත්‍රික්' in c or 'district' in c.lower()), 'දිස්ත්‍රික්කය')

            # String trimming to prevent formatting issues
            for col in [prov_col, dist_col, "zoneColor", "කලාපය"]:
                if col in df_rank.columns:
                    df_rank[col] = df_rank[col].astype(str).str.strip()

            # Numeric columns type conversion for accurate sorting
            df_rank["Quality Score (QS)"] = pd.to_numeric(df_rank["Quality Score (QS)"], errors='coerce').fillna(0.0)
            df_rank["සමත් ප්‍රතිශතය (%)"] = pd.to_numeric(df_rank["සමත් ප්‍රතිශතය (%)"], errors='coerce').fillna(0.0)

            # Global, Provincial & District dynamic ranking calculation
            df_rank = df_rank.sort_values(by=["Quality Score (QS)", "සමත් ප්‍රතිශතය (%)"], ascending=[False, False]).reset_index(drop=True)
            df_rank["දිවයිනේ ස්ථානය"] = df_rank.index + 1
            df_rank["පළාත් ස්ථානය"] = df_rank.groupby(prov_col, observed=False).cumcount() + 1
            df_rank["දිස්ත්‍රික් ස්ථානය"] = df_rank.groupby(dist_col, observed=False).cumcount() + 1

            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            
            with f_col1:
                prov_list = sorted([p for p in df_rank[prov_col].unique().tolist() if p and p.lower() != 'nan' and p.strip() != ''])
                provinces = ["සියලුම පළාත්"] + prov_list
                sel_prov = st.selectbox("පළාත අනුව පෙරන්න", provinces)
                
            with f_col2:
                is_all_prov = (sel_prov == "සියලුම පළාත්") or sel_prov.startswith("සියලුම")
                if not is_all_prov:
                    avail_raw = df_rank[df_rank[prov_col] == sel_prov][dist_col].unique().tolist()
                else:
                    avail_raw = df_rank[dist_col].unique().tolist()
                
                dist_list = sorted([d for d in avail_raw if d and d.lower() != 'nan' and d.strip() != ''])
                districts = ["සියලුම දිස්ත්‍රික්ක"] + dist_list
                sel_dist = st.selectbox("දිස්ත්‍රික්කය අනුව පෙරන්න", districts)
                
            with f_col3:
                zones = ["සියලුම කලාප", "Green", "Yellow", "Orange", "Red"]
                sel_zone = st.selectbox("ප්‍රගති කලාපය (Zone)", zones)
                
            with f_col4:
                search_query = st.text_input("පිරිවෙන සෙවීම", placeholder="නම හෝ අංකය...")

            filtered_df = df_rank.copy()
            
            if not is_all_prov:
                filtered_df = filtered_df[filtered_df[prov_col] == sel_prov]
            
            is_all_dist = (sel_dist == "සියලුම දිස්ත්‍රික්ක") or sel_dist.startswith("සියලුම")
            if not is_all_dist:
                filtered_df = filtered_df[filtered_df[dist_col] == sel_dist]
                
            is_all_zone = (sel_zone == "සියලුම කලාප") or sel_zone.startswith("සියලුම")
            if not is_all_zone:
                filtered_df = filtered_df[filtered_df["zoneColor"] == sel_zone]
                
            if search_query:
                query = search_query.lower().strip()
                filtered_df = filtered_df[
                    filtered_df["පිරිවෙනේ නම"].astype(str).str.lower().str.contains(query, na=False) |
                    filtered_df["පිරිවෙන් අංකය"].astype(str).str.contains(query, na=False)
                ]

            st.markdown(f"<p style='color: #334155; font-size: 15px;'>පෙන්වන ලද ආයතන සංඛ්‍යාව: <b>{len(filtered_df)}</b></p>", unsafe_allow_html=True)

            if filtered_df.empty:
                st.warning("තෝරාගත් කොන්දේසිවලට අදාළ පිරිවෙන් කිසිවක් හමු නොවීය.")
            else:
                table_rows = []
                for idx, row in filtered_df.reset_index(drop=True).iterrows():
                    island_rank = row.get("දිවයිනේ ස්ථානය", "-")
                    prov_rank = row.get("පළාත් ස්ථානය", "-")
                    dist_rank = row.get("දිස්ත්‍රික් ස්ථානය", "-")
                    name = row.get("පිරිවෙනේ නම", "")
                    p_no = row.get("පිරිවෙන් අංකය", "")
                    dist = row.get(dist_col, "")
                    prov = row.get(prov_col, "")
                    zone = row.get("කලාපය", "")
                    sat = row.get("පෙනී සිටි", 0)
                    pas = row.get("සමත්", 0)
                    rate = row.get("සමත් ප්‍රතිශතය (%)", 0)
                    qs = float(row.get("Quality Score (QS)", 0))
                    z_color = str(row.get("zoneColor", "Green"))

                    row_html = (
                        f'<tr class="rank-row">'
                        f'<td class="rank-cell" style="text-align: center;">'
                        f'<div class="badge-rank">#{island_rank}</div>'
                        f'<div class="badge-sub">දිවයින: #{island_rank} | පළාත: #{prov_rank} | දිස්ත්‍රික්: #{dist_rank}</div>'
                        f'</td>'
                        f'<td class="rank-cell">'
                        f'<div class="p-name">{name}</div>'
                        f'<div class="p-meta">'
                        f'<span class="badge-tag">අංකය: {p_no}</span>'
                        f'<span class="badge-tag">කලාපය: {zone}</span>'
                        f'</div>'
                        f'</td>'
                        f'<td class="rank-cell">'
                        f'<div style="font-weight: bold; color: #1e293b; font-size: 16px;">{prov}</div>'
                        f'<div class="p-meta">{dist}</div>'
                        f'</td>'
                        f'<td class="rank-cell" style="text-align: center;">'
                        f'<div style="font-weight: bold; font-size: 16px;">{sat} / <span style="color: #198754;">{pas}</span></div>'
                        f'<div class="badge-sub">පෙනී සිටි/සමත්</div>'
                        f'</td>'
                        f'<td class="rank-cell" style="text-align: center;">'
                        f'<div style="font-size: 20px; font-weight: bold; color: #0f766e;">{qs:.2f}</div>'
                        f'<div style="font-size: 13px; color: #0f172a; font-weight: bold;">{rate}% (සමත්)</div>'
                        f'</td>'
                        f'<td class="rank-cell" style="text-align: center;">'
                        f'<span class="badge-zone-{z_color}">{z_color} Zone</span>'
                        f'</td>'
                        f'</tr>'
                    )
                    table_rows.append(row_html)

                all_rows_str = "".join(table_rows)

                table_component = (
                    f'<style>'
                    f'.rank-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 1
