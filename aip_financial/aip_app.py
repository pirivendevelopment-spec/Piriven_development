import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import db

st.set_page_config(page_title="AIP 2026 - පිරිවෙන් ඒකකය", layout="wide", initial_sidebar_state="expanded")

# --- Session State & Auto-Login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "පාලක පුවරුව"

if not st.session_state.logged_in:
    saved_user = st.query_params.get("aip_auth")
    if saved_user:
        user_data = db.get_user_by_username(saved_user)
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user = dict(user_data)

def main():
    # =========================================================================
    # 1. PREMIUM LOGIN SCREEN (තද නිල් + Glass Card Styling)
    # =========================================================================
    if not st.session_state.logged_in:
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
            
            .stApp {
                background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 100%) !important;
                font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
            }
            
            section[data-testid="stSidebar"] {
                display: none !important;
            }

            div[data-testid="stForm"] {
                background: #ffffff !important;
                border-radius: 20px !important;
                padding: 35px 30px !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
            }

            div[data-testid="stTextInput"] input {
                background-color: #f8fafc !important;
                border: 1.5px solid #e2e8f0 !important;
                border-radius: 10px !important;
                color: #0f172a !important;
                font-size: 14px !important;
                padding: 12px 14px !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #1e40af !important;
                box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.15) !important;
            }

            div[data-testid="stTextInput"] label p {
                color: #475569 !important;
                font-weight: 700 !important;
                font-size: 12.5px !important;
            }

            div[data-testid="stFormSubmitButton"] > button {
                background: #1e40af !important;
                color: #ffffff !important;
                border: none !important;
                padding: 13px !important;
                border-radius: 10px !important;
                font-weight: 800 !important;
                font-size: 15px !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 4px 15px rgba(30, 64, 175, 0.35) !important;
                margin-top: 10px !important;
                width: 100% !important;
            }
            div[data-testid="stFormSubmitButton"] > button:hover {
                background: #1e3a8a !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(30, 64, 175, 0.45) !important;
            }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1.2, 1.6, 1.2])
        with col2:
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style='text-align: center; margin-bottom: 25px;'>
                <div style='background: #1e40af; width: 60px; height: 60px; border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 12px; box-shadow: 0 10px 20px rgba(30,64,175,0.4);'>
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>
                </div>
                <h1 style='color: #ffffff; margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;'>AIP 2026</h1>
                <p style='color: #94a3b8; font-size: 13.5px; margin-top: 4px; font-weight: 600;'>පිරිවෙන් ඒකක ප්‍රගති පාලන පද්ධතිය</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                u = st.text_input("පරිශීලක නාමය (Username)", placeholder="ඔබේ username එක ඇතුළත් කරන්න")
                p = st.text_input("මුරපදය (Password)", type="password", placeholder="••••••••")
                remember_me = st.checkbox("මා මතක තබා ගන්න (Remember Login)", value=True)
                
                submitted = st.form_submit_button("පද්ධතියට පිවිසෙන්න")
                if submitted:
                    user = db.authenticate_user(u, p)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = dict(user)
                        st.session_state.selected_menu = "පාලක පුවරුව"
                        if remember_me:
                            st.query_params["aip_auth"] = user["username"]
                        st.rerun()
                    else:
                        st.error("පරිශීලක නාමය හෝ මුරපදය වැරදියි!")
        return

    # =========================================================================
    # 2. MAIN DASHBOARD SHELL & ORIGINAL SIDEBAR THEME
    # =========================================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
        
        .stApp {
            background-color: #f1f5f9 !important;
            font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
        }

        /* Dark Navy Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #1e1b4b !important;
            padding-top: 1rem !important;
        }
        section[data-testid="stSidebar"] * {
            font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
        }

        /* Sidebar Navigation Buttons */
        div[data-testid="stSidebar"] div.stButton > button {
            background-color: #272757 !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 12px 18px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 14.5px !important;
            transition: all 0.25s ease !important;
            margin-bottom: 8px !important;
            width: 100% !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        }
        
        div[data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #1e40af !important;
            color: #ffffff !important;
            border-color: #3b82f6 !important;
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4) !important;
        }

        /* Active Navigation Button */
        div[data-testid="stSidebar"] div.active-nav > div.stButton > button {
            background-color: #1e40af !important;
            border-color: #60a5fa !important;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.5) !important;
        }

        /* Logout Button */
        div[data-testid="stSidebar"] div.logout-btn-container > div.stButton > button {
            background-color: #b91c1c !important;
            color: #ffffff !important;
            border: 1px solid #ef4444 !important;
            font-weight: 800 !important;
            font-size: 14px !important;
            justify-content: center !important;
            text-align: center !important;
            margin-top: 25px !important;
        }
        div[data-testid="stSidebar"] div.logout-btn-container > div.stButton > button:hover {
            background-color: #dc2626 !important;
            color: #ffffff !important;
            transform: none !important;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.5) !important;
        }

        .block-container {
            padding-top: 1.2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    u_name = user.get('name') or user.get('username') or "පරිශීලක"
    u_title = user.get('title') or "විෂය භාර නිලධාරී"
    u_role = user.get('role', 'Officer')
    is_super_admin = str(u_role).lower() in ["super admin", "admin", "ප්‍රධාන පරිපාලක"]
    u_initial = u_name.strip()[0].upper() if u_name.strip() else "U"

    # Sidebar Header & User Profile Card
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);'>
        <h2 style='color: #fbbf24; margin: 0; font-size: 22px; font-weight: 800;'>AIP 2026</h2>
        <p style='font-size: 10px; color: #94a3b8; margin: 2px 0 0; text-transform: uppercase; letter-spacing: 1px;'>ප්‍රගති පාලන පද්ධතිය</p>
    </div>

    <div style='display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.06); padding: 12px; border-radius: 12px; margin: 15px 0; border: 1px solid rgba(255,255,255,0.08);'>
        <div style='background: #1e40af; color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; flex-shrink: 0;'>
            {u_initial}
        </div>
        <div style='overflow: hidden;'>
            <div style='color: white; font-size: 13.5px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{u_name}'>{u_name}</div>
            <div style='color: #94a3b8; font-size: 11px; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{u_title}</div>
            <span style='background: #10b98125; color: #34d399; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top: 4px;'>{u_role}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation Buttons
    nav_items = [
        ("📊 පාලක පුවරුව", "පාලක පුවරුව"),
        ("📑 වවුචර විස්තර", "වවුචර විස්තර"),
        ("📝 වැඩසටහන් එක් කරන්න", "වැඩසටහන් එක් කරන්න"),
        ("🖨️ පද්ධති වාර්තා", "පද්ධති වාර්තා")
    ]

    for label, key in nav_items:
        wrap_class = "active-nav" if st.session_state.selected_menu == key else "normal-nav"
        st.sidebar.markdown(f"<div class='{wrap_class}'>", unsafe_allow_html=True)
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.selected_menu = key
            st.rerun()
        st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # Logout Button
    st.sidebar.markdown("<div class='logout-btn-container'>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 පද්ධතියෙන් ඉවත් වන්න", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.selected_menu = "පාලක පුවරුව"
        if "aip_auth" in st.query_params:
            del st.query_params["aip_auth"]
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # 3. VIEWS HANDLING (පෙර පරිදිම අලංකාර Forms සහ Dashboard Views)
    # =========================================================================
    selected = st.session_state.selected_menu

    # VIEW 1: පාලක පුවරුව
    if selected == "පාලක පුවරුව":
        st.markdown("<h2 style='color: #0f172a; font-weight: 800; margin-bottom: 20px;'>📊 AIP 2026 ප්‍රධාන පාලක පුවරුව</h2>", unsafe_allow_html=True)
        
        conn = db.get_connection()
        v_df = pd.read_sql_query("SELECT * FROM voucher_log WHERE delete_requested = 0 OR delete_requested IS NULL", conn)
        a_df = pd.read_sql_query("SELECT * FROM data_log WHERE delete_requested = 0 OR delete_requested IS NULL", conn)
        conn.close()

        total_spent = v_df["amount"].sum() if not v_df.empty else 0.0
        total_activities = len(a_df) if not a_df.empty else 0
        total_estimate = a_df["estimate"].sum() if not a_df.empty else 0.0

        # KPI Metrics
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"""
        <div style='background: white; border-radius: 14px; padding: 20px; border-left: 5px solid #1e40af; box-shadow: 0 4px 15px rgba(0,0,0,0.04);'>
            <div style='color: #64748b; font-size: 13px; font-weight: 700;'>මුළු වියදම (වවුචර)</div>
            <div style='color: #1e40af; font-size: 26px; font-weight: 800; margin-top: 5px;'>රු. {total_spent:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        m2.markdown(f"""
        <div style='background: white; border-radius: 14px; padding: 20px; border-left: 5px solid #059669; box-shadow: 0 4px 15px rgba(0,0,0,0.04);'>
            <div style='color: #64748b; font-size: 13px; font-weight: 700;'>සම්පූර්ණ කළ වැඩසටහන්</div>
            <div style='color: #059669; font-size: 26px; font-weight: 800; margin-top: 5px;'>{total_activities}</div>
        </div>
        """, unsafe_allow_html=True)

        m3.markdown(f"""
        <div style='background: white; border-radius: 14px; padding: 20px; border-left: 5px solid #d97706; box-shadow: 0 4px 15px rgba(0,0,0,0.04);'>
            <div style='color: #64748b; font-size: 13px; font-weight: 700;'>මුළු ඇස්තමේන්තුව</div>
            <div style='color: #d97706; font-size: 26px; font-weight: 800; margin-top: 5px;'>රු. {total_estimate:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1.6, 1])
        with col_c1:
            st.markdown("#### 📈 වැය ශීර්ෂ අනුව වියදම් විශ්ලේෂණය")
