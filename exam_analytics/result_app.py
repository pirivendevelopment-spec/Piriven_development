import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# Sub-folder path සැකසීම (app.py හරහා ධාවනය වන විට imports සහ ගොනු සොයා ගැනීමට)
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

# --- Custom CSS (Default Settings for Toolbars & Clean UI) ---
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

        /* Sidebar Theme (Dark Modern) */
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }

        /* Sidebar Buttons Styling */
        [data-testid="stSidebar"] .stButton button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 15px !important;
            transition: all 0.3s ease;
        }

        /* Secondary (Unselected) buttons */
        [data-testid="stSidebar"] .stButton button[kind="secondary"] {
            background-color: #1f2937 !important;
            color: #94a3b8 !important;
            border: 1px solid #374151 !important;
        }
        [data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
            background-color: #374151 !important;
            color: #ffffff !important;
        }

        /* Primary (Selected) button style */
        [data-testid="stSidebar"] .stButton button[kind="primary"] {
            background-color: #0f766e !important;
            color: #ffffff !important;
            border: none !important;
        }

        /* Logout button style */
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

        /* KPI Cards Styling */
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
        
        /* Progress Zones */
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

# දත්ත පූරණය කිරීම
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

# --- Session State & Persistent Login ---
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

# --- Login Screen ---
if not st.session_state.logged_in:
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

    st.stop()

# --- Main App Execution (Logged In User) ---
user = st.session_state.user
role = user.get("role", "Guest")
access = user.get("access", "")

# --- Sidebar Menu with Logo ---
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
            <div style="font-size: 14px; font-weight: bold; color: #f3f4f6;">👤 {user['name']}</div>
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

# --- 1. සාරාංශ පුවරුව (Summary) ---
if menu == "සාරාංශ පුවරුව (Summary)":
    st.markdown("### 📊 සාරාංශ පුවරුව")
    st.markdown(f"<p style='color: #334155; font-size: 16px;'>පිරිවෙන් සාමාන්‍ය පෙළ විභාග ප්‍රතිඵල විශ්ලේෂණය - <b>{selected_
