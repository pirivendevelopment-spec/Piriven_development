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
# 1. LOGIN SCREEN (ලොග් වී නැතිනම් පමණි)
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
# 2. MAIN LOGGED-IN VIEW (ලොග් වූ පසු සෘජුවම ක්‍රියාත්මක වේ)
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

    # VIEW 1: සාරාංශ පුවරුව (Summary)
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
            
            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f'<div class="kpi-card"><div class="kpi-title">අයදුම් කළ සංඛ්‍යාව</div><div class="kpi-value">{tot_applied:,}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card"><div class="kpi-title">පෙනී සිටි සංඛ්‍යාව</div><div class="kpi-value">{tot_sat:,}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card"><div class="kpi-title">සමත් සංඛ්‍යාව</div><div class="kpi-value">{tot_pass:,}</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="kpi-card" style="background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%); border-top: 5px solid #084298;"><div class="kpi-title" style="color: #fff;">සමත් ප්‍රතිශතය</div><div class="kpi-value" style="color: #fff;">{overall_rate}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            z1, z2, z3, z4 = st.columns(4)
            z1.markdown(f'<div class="zone-green"><div class="zone-title">🟢 GREEN ZONE (QS 7.5+)</div><div class="zone-count">{green_count}</div></div>', unsafe_allow_html=True)
            z2.markdown(f'<div class="zone-yellow"><div class="zone-title">🟡 YELLOW ZONE (QS 5.0+)</div><div class="zone-count">{yellow_count}</div></div>', unsafe_allow_html=True)
            z3.markdown(f'<div class="zone-orange"><div class="zone-title">🟠 ORANGE ZONE (QS 3.5+)</div><div class="zone-count">{orange_count}</div></div>', unsafe_allow_html=True)
            z4.markdown(f'<div class="zone-red"><div class="zone-title">🔴 RED ZONE (QS < 3.5)</div><div class="zone-count">{red_count}</div></div>', unsafe_allow_html=True)
            
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
                st.subheader("📍 දිස්ත්‍‍රික් ප්‍රගතිය")
                dist_df = pd.DataFrame(ranking_data)
                if not dist_df.empty:
                    dist_summary = dist_df.groupby("දිස්ත්‍රික්කය")["සමත් ප්‍රතිශතය (%)"].mean().reset_index()
                    dist_summary = dist_summary.sort_values(by="සමත් ප්‍රතිශතය (%)", ascending=False)
                    st.dataframe(dist_summary, use_container_width=True, height=350, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)
            formula_html = """
            <div style="background: white; padding: 25px; border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-left: 6px solid #198754; border: 1px solid #cbd5e1;">
                <h4 style="color: #1e293b; margin-top: 0; font-size: 18px;">📐 ශ්‍රේණිගත කිරීමේ විද්‍යාත්මක පදනම (Scientific Ranking Formula)</h4>
                <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                    මෙම පද්ධතියේ පිරිවෙන් ශ්‍රේණිගත කරනු ලබන්නේ එක් එක් සිසුවා ලබාගන්නා සාමාර්ථයන්හි ගුණාත්මක අගය (Quality Score) මත පදනම් වූ සාමාන්‍ය අගයෙනි. මෙහිදී භාවිත වන මූලික සමීකරණය පහත පරිදි වේ:
                </p>
                <div style="background: #f8fafc; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e2e8f0; margin: 15px 0;">
                    <span style="font-size: 20px; font-weight: bold; color: #0f766e;">Quality Score (QS) = Σ (G<sub>w</sub>) / N</span>
                    <div style="font-size: 13px; color: #64748b; margin-top: 5px;">මෙහි: G<sub>w</sub> = සාමාර්ථයට අදාළ බර තැබීම | N = පෙනී සිටි මුළු සිසුන් සංඛ්‍යාව</div>
                </div>
                <div style="display: flex; gap: 30px; margin-top: 20px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 250px;">
                        <strong style="color: #1e293b; font-size: 15px;">සාමාර්ථ බර තැබීම් (Weightage):</strong>
                        <ul style="color: #475569; font-size: 14px; margin-top: 8px; padding-left: 20px; line-height: 1.8;">
                            <li><strong>A (විශිෂ්ට):</strong> 10.0</li>
                            <li><strong>B (ඉතා හොඳ):</strong> 8.0</li>
                            <li><strong>C (හොඳ):</strong> 6.5</li>
                            <li><strong>S (සාමාන්‍ය):</strong> 5.0</li>
                            <li><strong>W (අසමත්):</strong> 0.0</li>
                        </ul>
                    </div>
                    <div style="flex: 2; min-width: 300px;">
                        <strong style="color: #1e293b; font-size: 15px;">විශේෂ සටහන:</strong>
                        <ul style="color: #475569; font-size: 14px; margin-top: 8px; padding-left: 20px; line-height: 1.8;">
                            <li>පිරිවෙනක ශිෂ්‍ය සංඛ්‍යාව කුඩා වුවත් විශාල වුවත්, සෑම ආයතනයක්ම එකම සාಧಾರණ මිනුම් දණ්ඩකින් (Scale 0-100) මෙහිදී මැනුම් ලබයි.</li>
                            <li>මෙහිදී පිරිවෙනක සමූහික ශාස්ත්‍රීය දක්ෂතාවය මෙන්ම එක් එක් සිසුවා කෙරෙහි දක්වන අවධානය මනාව නිරූපණය වේ.</li>
                            <li>සමත්විමේ ප්‍රතිශතය ගණනය කරනු ලබන්නේ පෙනී සිටි (Sat) සිසුන් සංඛ්‍යාව මත පමණි.</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
            st.markdown(formula_html, unsafe_allow_html=True)

    # VIEW 2: පළාත් හා ශ්‍රේණිගත කිරීම් (Rankings)
    elif menu == "පළාත් හා ශ්‍රේණිගත කිරීම් (Rankings)":
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown("### 🏆 පිරිවෙන් සාධන ශ්‍රේණිගත කිරීම් (Rankings)")
        with col_h2:
            components.html("""
                <div style="text-align: right; margin-top: 5px;">
                    <button onclick="parent.window.print()" style="background-color: #0f766e; color: white; padding: 10px 18px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: bold; font-family: 'Segoe UI', sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                        🖨️ ප්‍රින්ට් සෙටින්ග්ස් / PDF
                    </button>
                </div>
            """, height=50)
            
        st.markdown("---")
        
        ranking_data = calculate_piriven_rankings(results_df, master_df, selected_year, role, access)
        if not ranking_data:
            st.info("දත්ත නොමැත.")
        else:
            df_rank = pd.DataFrame(ranking_data)
            
            # දත්තවල ඇති හිස්තැන් ඉවත් කිරීම
            for col in ["පළාත", "දිස්ත්‍රික්කය", "zoneColor", "කලාපය"]:
                if col in df_rank.columns:
                    df_rank[col] = df_rank[col].astype(str).str.strip()

            ALL_PROV = "සියලුම පළාත්"
            ALL_DIST = "සියලුම දිස්ත්‍රික්ක"
            ALL_ZONE = "සියලුම කලාප"

            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            
            with f_col1:
                prov_list = sorted([p for p in df_rank["පළාත"].dropna().unique().tolist() if p and p.lower() != 'nan'])
                provinces = [ALL_PROV] + prov_list
                sel_prov = st.selectbox("පළාත අනුව පෙරන්න", provinces)
                
            with f_col2:
                if sel_prov != ALL_PROV:
                    available_districts = df_rank[df_rank["පළාත"] == sel_prov]["දිස්ත්‍රික්කය"].dropna().unique().tolist()
                else:
                    available_districts = df_rank["දිස්ත්‍රික්කය"].dropna().unique().tolist()
                
                dist_list = sorted([d for d in available_districts if d and d.lower() != 'nan'])
                districts = [ALL_DIST] + dist_list
                sel_dist = st.selectbox("දිස්ත්‍රික්කය අනුව පෙරන්න", districts)
                
            with f_col3:
                zones = [ALL_ZONE, "Green", "Yellow", "Orange", "Red"]
                sel_zone = st.selectbox("ප්‍රගති කලාපය (Zone)", zones)
                
            with f_col4:
                search_query = st.text_input("පිරිවෙන සෙවීම", placeholder="නම හෝ අංකය...")

            # පෙරීම් ක්‍රියාවලිය (Safe Filtering)
            filtered_df = df_rank.copy()
            if sel_prov != ALL_PROV:
                filtered_df = filtered_df[filtered_df["පළාත"] == sel_prov]
            if sel_dist != ALL_DIST:
                filtered_df = filtered_df[filtered_df["දිස්ත්‍රික්කය"] == sel_dist]
            if sel_zone != ALL_ZONE:
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
                    dist = row.get("දිස්ත්‍රික්කය", "")
                    prov = row.get("පළාත", "")
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
                    f'.rank-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 10px; }}'
                    f'.rank-header {{ background-color: #1a252f; color: white; padding: 14px; font-size: 15px; text-align: center; }}'
                    f'.rank-row {{ border-bottom: 1px solid #f0f2f5; }}'
                    f'.rank-cell {{ padding: 18px 14px; vertical-align: middle; font-size: 15px; color: #1e293b; }}'
                    f'.badge-rank {{ font-size: 20px; font-weight: bold; color: #0f766e; text-align: center; }}'
                    f'.badge-sub {{ font-size: 12px; color: #475569; text-align: center; }}'
                    f'.p-name {{ font-weight: bold; font-size: 16px; color: #0f172a; }}'
                    f'.p-meta {{ font-size: 13px; color: #475569; margin-top: 4px; }}'
                    f'.badge-tag {{ background: #f1f5f9; border: 1px solid #cbd5e1; padding: 3px 10px; border-radius: 6px; font-size: 13px; margin-right: 4px; display: inline-block; color: #1e293b; }}'
                    f'.badge-zone-Green {{ background-color: #d1e7dd; color: #0f5132; padding: 8px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; }}'
                    f'.badge-zone-Yellow {{ background-color: #fff3cd; color: #664d03; padding: 8px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; }}'
                    f'.badge-zone-Orange {{ background-color: #ffe5d0; color: #854d0e; padding: 8px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; }}'
                    f'.badge-zone-Red {{ background-color: #f8d7da; color: #842029; padding: 8px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; }}'
                    f'</style>'
                    f'<div class="printable-table-container">'
                    f'<table class="rank-table">'
                    f'<thead>'
                    f'<tr style="background-color: #1a252f; color: white;">'
                    f'<th class="rank-header">ස්ථානගතවීම</th>'
                    f'<th class="rank-header" style="text-align: left;">පිරිවෙන සහ අනන්‍යතාවය</th>'
                    f'<th class="rank-header" style="text-align: left;">ප්‍රදේශය</th>'
                    f'<th class="rank-header">පෙනී සිටි/සමත්</th>'
                    f'<th class="rank-header">QS සහ ප්‍රතිශතය</th>'
                    f'<th class="rank-header">ප්‍රගති කලාපය</th>'
                    f'</tr>'
                    f'</thead>'
                    f'<tbody>'
                    f'{all_rows_str}'
                    f'</tbody>'
                    f'</table>'
                    f'</div>'
                )

                st.markdown(table_component, unsafe_allow_html=True)
    # VIEW 3: විෂය සාරාංශය (Subjects)
    elif menu == "විෂය සාරාංශය (Subjects)":
        sub_h1, sub_h2 = st.columns([3, 1])
        with sub_h1:
            st.markdown("### 📚 විෂය මට්ටමේ ප්‍රතිඵල විශ්ලේෂණය")
        with sub_h2:
            components.html("""
                <div style="text-align: right; margin-top: 5px;">
                    <button onclick="parent.window.print()" style="background-color: #0f766e; color: white; padding: 10px 18px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: bold; font-family: 'Segoe UI', sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                        🖨️ ප්‍රින්ට් සෙටින්ග්ස් / PDF
                    </button>
                </div>
            """, height=50)

        st.markdown("---")
        
        sub_col1, sub_col2 = st.columns([2, 2])
        with sub_col1:
            sub_years = ["2025", "2024", "2023", "2022"]
            default_year_idx = sub_years.index(selected_year) if selected_year in sub_years else 0
            analysis_year = st.selectbox("විභාග වර්ෂය තෝරන්න", sub_years, index=default_year_idx, key="subj_year_picker")
            
        subjects_dict = {
            "සිංහල (SUB1)": "1", "පාලි (SUB2)": "2", "ත්‍රිපිටක ධර්මය (SUB3)": "3", "සංස්කෘත (SUB4)": "4",
            "ගණිතය (SUB5)": "5", "ඉංග්‍රීසි (SUB6)": "6", "ඉතිහාසය (SUB7)": "7", "සමාජ විද්‍යාව (SUB8)": "8",
            "සෞඛ්‍ය විද්‍යාව (SUB9)": "9", "භූගෝල විද්‍යාව (SUB10)": "10", "සාමාන්‍ය විද්‍යාව (SUB11)": "11", "දෙමළ (SUB12)": "12"
        }
        
        with sub_col2:
            selected_sub_name = st.selectbox("විෂය තෝරන්න", list(subjects_dict.keys()), key="subj_name_picker")
            sub_code = subjects_dict[selected_sub_name]
            
        st.markdown(f"<p style='color: #334155;'><b>{analysis_year}</b> වර්ෂයට අදාළ <b>{selected_sub_name}</b> විෂයෙහි ශ්‍රේණි ව්‍යාප්තිය සහ දිස්ත්‍රික් ප්‍රගතිය</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        grade_counts, df_dist = get_detailed_subject_analysis(results_df, master_df, analysis_year, sub_code)
        total_grades = sum(grade_counts.values())
        
        c_chart, c_table = st.columns([1.3, 1])
        
        with c_chart:
            st.markdown("##### ශ්‍රේණි ව්‍යාප්තිය (Grade Distribution)")
            df_pie = pd.DataFrame(list(grade_counts.items()), columns=["ශ්‍රේණිය", "ගණන"])
            fig = px.pie(
                df_pie, names="ශ්‍රේණිය", values="ගණන", hole=0.6,
                color="ශ්‍රේණිය",
                template="plotly_white",
                color_discrete_map={"A": "#198754", "B": "#20c997", "C": "#ffc107", "S": "#fd7e14", "W": "#dc3545"}
            )
            fig.update_layout(
                plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                margin=dict(l=10, r=10, t=10, b=10), showlegend=True,
                height=390
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with c_table:
            st.markdown("##### සාමාර්ථ සාරාංශය")
            summary_data = []
            for g, count in grade_counts.items():
                pct = (count / total_grades * 100) if total_grades > 0 else 0
                summary_data.append({
                    "ශ්‍රේණිය": f"{g} සාමාර්ථය",
                    "සංඛ්‍යාව": count,
                    "ප්‍රතිශතය": f"{pct:.1f}%"
                })
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True, height=230)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### දිස්ත්‍රික් මට්ටමින් විෂය සාමාර්ථයන්")
        
        if not df_dist.empty:
            st.dataframe(df_dist, use_container_width=True, height=450, hide_index=True)
        else:
            st.info("තෝරාගත් වර්ෂය සඳහා දත්ත නොමැත.")

    # VIEW 4: වාර්ෂික වාර්තාව (Yearly Report)
    elif menu == "වාර්ෂික වාර්තාව (Yearly Report)":
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown("### 📈 වාර්ෂික ප්‍රගති වාර්තාව (2022 - 2025)")
        with col_h2:
            components.html("""
                <div style="text-align: right; margin-top: 5px;">
                    <button onclick="parent.window.print()" style="background-color: #0f766e; color: white; padding: 10px 18px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: bold; font-family: 'Segoe UI', sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                        🖨️ ප්‍රින්ට් සෙටින්ග්ස් / PDF
                    </button>
                </div>
            """, height=50)
            
        st.markdown("---")

        yearly_df = get_yearly_report_data(results_df, master_df, selected_year, role, access)

        if not yearly_df.empty:
            f_c1, f_c2 = st.columns(2)
            with f_c1:
                provinces = ["සියලුම පළාත්"] + sorted(yearly_df["province"].dropna().unique().tolist())
                sel_rep_prov = st.selectbox("පළාත අනුව පෙරන්න", provinces, key="rep_prov_filter")
            with f_c2:
                if sel_rep_prov != "සියලුම පළාත්":
                    avail_dists = yearly_df[yearly_df["province"] == sel_rep_prov]["district"].dropna().unique().tolist()
                else:
                    avail_dists = yearly_df["district"].dropna().unique().tolist()
                districts = ["සියලුම දිස්ත්‍රික්ක"] + sorted(avail_dists)
                sel_rep_dist = st.selectbox("දිස්ත්‍රික්කය අනුව පෙරන්න", districts, key="rep_dist_filter")

            filtered_report_df = yearly_df.copy()
            if sel_rep_prov != "සියලුම පළාත්":
                filtered_report_df = filtered_report_df[filtered_report_df["province"] == sel_rep_prov]
            if sel_rep_dist != "සියලුම දිස්ත්‍රික්ක":
                filtered_report_df = filtered_report_df[filtered_report_df["district"] == sel_rep_dist]

            st.markdown(f"<p style='color: #0f766e;'><b>පෙන්වන ලද පිරිවෙන් සංඛ්‍යාව: {len(filtered_report_df)}</b></p>", unsafe_allow_html=True)

            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <style>
                body { font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; margin: 0; padding: 5px; }
                .yearly-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-size: 13px; }
                .yearly-table th, .yearly-table td { border: 1px solid #cbd5e1; padding: 8px 4px; text-align: center; vertical-align: middle; color: #1e293b; }
                .yearly-table th { background-color: #1a252f; color: white; font-weight: bold; }
                .p-cell { text-align: left !important; padding-left: 10px !important; font-weight: bold; width: 240px; }
                .zone-Green { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }
                .zone-Yellow { background-color: #fff3cd; color: #664d03; font-weight: bold; }
                .zone-Orange { background-color: #ffe5d0; color: #854d0e; font-weight: bold; }
                .zone-Red { background-color: #f8d7da; color: #842029; font-weight: bold; }
            </style>
            </head>
            <body>
            <table class="yearly-table">
                <thead>
                    <tr>
                        <th rowspan="2" class="p-cell">පිරිවෙනේ නම</th>
                        <th colspan="5">2022</th>
                        <th colspan="5">2023</th>
                        <th colspan="5">2024</th>
                        <th colspan="5">2025</th>
                        <th rowspan="2">සමත් %</th>
                        <th rowspan="2">අසමත් %</th>
                        <th rowspan="2">ප්‍රගති කලාපය</th>
                    </tr>
                    <tr>
                        <th>A</th><th>B</th><th>C</th><th>S</th><th>W</th>
                        <th>A</th><th>B</th><th>C</th><th>S</th><th>W</th>
                        <th>A</th><th>B</th><th>C</th><th>S</th><th>W</th>
                        <th>A</th><th>B</th><th>C</th><th>S</th><th>W</th>
                    </tr>
                </thead>
                <tbody>
            """

            for _, r in filtered_report_df.iterrows():
                z_class = f"zone-{r['zone']}"
                html_content += f"""
                    <tr>
                        <td class="p-cell">
                            <div style="font-size: 13px; color: #0f172a;">{r['name']}</div>
                            <div style="font-size: 11px; color: #64748b; font-weight: normal;">{r['p_no']} | {r['district']}</div>
                        </td>
                        <td>{r['2022_A']}</td><td>{r['2022_B']}</td><td>{r['2022_C']}</td><td>{r['2022_S']}</td><td>{r['2022_W']}</td>
                        <td>{r['2023_A']}</td><td>{r['2023_B']}</td><td>{r['2023_C']}</td><td>{r['2023_S']}</td><td>{r['2023_W']}</td>
                        <td>{r['2024_A']}</td><td>{r['2024_B']}</td><td>{r['2024_C']}</td><td>{r['2024_S']}</td><td>{r['2024_W']}</td>
                        <td>{r['2025_A']}</td><td>{r['2025_B']}</td><td>{r['2025_C']}</td><td>{r['2025_S']}</td><td>{r['2025_W']}</td>
                        <td><b>{r['pass_pct']}</b></td>
                        <td>{r['fail_pct']}</td>
                        <td class="{z_class}">{r['zone']} Zone</td>
                    </tr>
                """

            html_content += """
                </tbody>
            </table>
            </body>
            </html>
            """

            components.html(html_content, height=650, scrolling=True)
        else:
            st.info("වාර්තාගත දත්ත කිසිවක් හමු නොවීය.")

    # VIEW 5: පිරිවෙන් විශ්ලේෂණය (Single Pirivena Analysis)
    elif menu == "පිරිවෙන් විශ්ලේෂණය":
        st.markdown("### 🔍 තනි පිරිවෙන් දත්ත  විශ්ලේෂණය")
        st.markdown("<p style='color: #334155;'>පිරිවෙන් අංකය, සංගණන අංකය හෝ නම ඇතුළත් කර අදාළ ආයතනයේ විෂය ප්‍රගතිය පරීක්ෂා කරන්න</p>", unsafe_allow_html=True)
        st.markdown("---")

        col_srch1, col_srch2 = st.columns([4, 1])
        with col_srch1:
            search_input = st.text_input("සෙවුම් පදය", placeholder="උදා: 1109 හෝ මහා විසුද්ධාරම හෝ 416013...", label_visibility="collapsed")
        with col_srch2:
            search_clicked = st.button("🔍 සොයන්න", use_container_width=True, type="primary")

        if search_input or search_clicked:
            analysis_data, err_msg = get_single_pirivena_full_analysis(results_df, master_df, search_input, selected_year, role, access)
            
            if err_msg:
                st.error(err_msg)
            elif analysis_data:
                head_col1, head_col2, head_col3 = st.columns([6, 2, 1])
                with head_col1:
                    st.markdown(f"""
                        <div style="background: #ffffff; padding: 20px; border-radius: 12px; border-left: 6px solid #0f766e; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;">
                            <h3 style="color: #0f172a; margin: 0; font-size: 22px;">{analysis_data['name']}</h3>
                            <p style="color: #64748b; margin-top: 8px; font-size: 14px;">අංකය: <b>{analysis_data['p_no']}</b> | සංගණන: <b>{analysis_data['census_no']}</b> | දිස්ත්‍රික්කය: <b>{analysis_data['district']}</b> | පළාත: <b>{analysis_data['province']}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                with head_col2:
                    analysis_year = st.selectbox("විභාග වර්ෂය", ["2025", "2024", "2023", "2022"], key="single_ana_yr")
                    if analysis_year != selected_year:
                        analysis_data, err_msg = get_single_pirivena_full_analysis(results_df, master_df, search_input, analysis_year, role, access)
                with head_col3:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    components.html("""
                        <div style="text-align: right;">
                            <button onclick="parent.window.print()" style="background-color: #0f766e; color: white; padding: 8px 14px; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; font-weight: bold; font-family: 'Segoe UI', sans-serif;">
                                🖨️️ ප්‍රින්ට්
                            </button>
                        </div>
                    """, height=40)

                k1, k2, k3, k4 = st.columns(4)
                k1.markdown(f'<div class="kpi-card"><div class="kpi-title">බර තැබූ ලකුණු (QS)</div><div class="kpi-value">{analysis_data["qs"]:.2f}</div></div>', unsafe_allow_html=True)
                k2.markdown(f'<div class="kpi-card"><div class="kpi-title">දිවයිනේ ස්ථානය</div><div class="kpi-value" style="color: #0284c7;">#{analysis_data["island_rank"]}</div></div>', unsafe_allow_html=True)
                k3.markdown(f'<div class="kpi-card"><div class="kpi-title">පළාත් ස්ථානය</div><div class="kpi-value" style="color: #0d9488;">#{analysis_data["province_rank"]}</div></div>', unsafe_allow_html=True)
                k4.markdown(f'<div class="kpi-card"><div class="kpi-title">දිස්ත්‍රික් ස්ථානය</div><div class="kpi-value" style="color: #4f46e5;">#{analysis_data["district_rank"]}</div></div>', unsafe_allow_html=True)

                zone_colors = {"Green": "#198754", "Yellow": "#ffc107", "Orange": "#fd7e14", "Red": "#dc3545"}
                z_color = zone_colors.get(analysis_data["zone"], "#198754")
                
                zc1, zc2 = st.columns(2)
                zc1.markdown(f"""
                    <div style="background: #ffffff; padding: 20px; border-radius: 12px; border-left: 5px solid {z_color}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-top: 15px;">
                        <div style="font-size: 14px; font-weight: bold; color: #334155; text-transform: uppercase;">ප්‍රගති කලාපය ({analysis_year})</div>
                        <div style="font-size: 26px; font-weight: bold; color: {z_color}; margin-top: 8px;">{analysis_data['zone']} Zone</div>
                    </div>
                """, unsafe_allow_html=True)
                
                zc2.markdown(f"""
                    <div style="background: #ffffff; padding: 20px; border-radius: 12px; border-left: 5px solid #0f766e; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-top: 15px;">
                        <div style="font-size: 14px; font-weight: bold; color: #334155; text-transform: uppercase;">{analysis_year} සමත් වීමේ ප්‍රතිශතය</div>
                        <div style="font-size: 26px; font-weight: bold; color: #0f766e; margin-top: 8px;">{analysis_data['pass_rate']}</div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # සුදු පසුබිම සහිත Plots (Clean Light Layout)
                ch_col1, ch_col2 = st.columns(2)
                
                with ch_col1:
                    st.markdown("<h5 style='text-align: center;'>වර්ෂ 4ක සාධන ඉතිහාසය</h5>", unsafe_allow_html=True)
                    hist_df = pd.DataFrame(analysis_data["history"])
                    if not hist_df.empty:
                        fig_hist = px.bar(
                            hist_df, x="වර්ෂය", y=["පෙනී සිටි", "සමත්"], barmode="group",
                            template="plotly_white",
                            color_discrete_sequence=["#20b2aa", "#008b8b"], text_auto=True
                        )
                        fig_hist.update_traces(textposition="outside")
                        fig_hist.update_layout(
                            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                            margin=dict(t=20, b=20, l=20, r=20), height=300, legend_title=""
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)

                with ch_col2:
                    st.markdown(f"<h5 style='text-align: center;'>විෂය සාධනය ({analysis_year})</h5>", unsafe_allow_html=True)
                    subs_raw_df = pd.DataFrame(analysis_data["subjects"])
                    if not subs_raw_df.empty:
                        fig_sub = px.bar(
                            subs_raw_df, x="විෂය කේතය", y=["A", "B", "C", "S", "W"], barmode="stack",
                            template="plotly_white",
                            color_discrete_sequence=["#013220", "#00563b", "#20b2aa", "#7fffd4", "#dc3545"], text_auto=True
                        )
                        fig_sub.update_traces(textposition="inside")
                        fig_sub.update_layout(
                            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                            margin=dict(t=20, b=40, l=20, r=20), height=300, xaxis_tickangle=-30, legend_title=""
                        )
                        st.plotly_chart(fig_sub, use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 📚 විෂය මට්ටමේ සාමාර්ථ විශ්ලේෂණය")
                
                if not subs_raw_df.empty:
                    display_df = subs_raw_df[["විෂය කේතය", "A", "B", "C", "S", "W", "සමත් %"]]
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.info("මෙම පිරිවෙන සඳහා තෝරාගත් වර්ෂයේ විෂය දත්ත හමු නොවීය.")

    st.markdown("""
        <div class="print-footer-global">
            Copyright © සංවර්ධන ශාඛාව - පිරිවෙන් අධ්‍යාපන අංශය - විභාග දෙපාර්තමේන්තුව නිකුත් කළ පිරිවෙන් සාමාන්‍ය පෙළ විභාගය 2025 (2026) දත්ත පදනම් කරගත් විශ්ලේෂණ වාර්තාවකි.
        </div>
    """, unsafe_allow_html=True)
