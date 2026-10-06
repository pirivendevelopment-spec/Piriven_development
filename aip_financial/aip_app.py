import streamlit as st
import sys
import os

# Sub-folder import නිවැරදි කිරීම
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import db
from modules import dashboard

st.set_page_config(page_title="AIP 2026 - පිරිවෙන් ඒකකය", layout="wide", initial_sidebar_state="expanded")

# --- Session State & Auto-Login පරීක්ෂාව ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# Browser එක Refresh කළ විට පෙර ලොග් වූ තොරතුරු ස්වයංක්‍රීයව පූරණය කිරීම
if not st.session_state.logged_in:
    saved_user = st.query_params.get("aip_auth")
    if saved_user:
        user_data = db.get_user_by_username(saved_user)
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user = dict(user_data)

def main():
    # =========================================================================
    # 1. PREMIUM LOGIN SCREEN
    # =========================================================================
    if not st.session_state.logged_in:
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
            .stApp {
                background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 100%) !important;
                font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
            }
            /* Login අවස්ථාවේදී පමණක් Sidebar සැඟවීම */
            section[data-testid="stSidebar"] { display: none !important; }
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
            div[data-testid="stFormSubmitButton"] > button {
                background: #1e40af !important;
                color: #ffffff !important;
                border: none !important;
                padding: 13px !important;
                border-radius: 10px !important;
                font-weight: 800 !important;
                font-size: 15px !important;
                width: 100% !important;
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
                <h1 style='color: #ffffff; margin: 0; font-size: 28px; font-weight: 800;'>AIP 2026</h1>
                <p style='color: #94a3b8; font-size: 13.5px; margin-top: 4px; font-weight: 600;'>පිරිවෙන් ඒකක ප්‍රගති පාලන පද්ධතිය</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                u = st.text_input("පරිශීලක නාමය (Username)", placeholder="ඔබේ username එක ඇතුළත් කරන්න")
                p = st.text_input("මුරපදය (Password)", type="password", placeholder="••••••••")
                remember_me = st.checkbox("මා මතක තබා ගන්න (Remember Login)", value=True)
                
                submitted = st.form_submit_button("පද්ධතියට පිවිසෙන්න", use_container_width=True)
                if submitted:
                    user = db.authenticate_user(u, p)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = dict(user)
                        if remember_me:
                            st.query_params["aip_auth"] = user["username"]
                        st.rerun()
                    else:
                        st.error("පරිශීලක නාමය හෝ මුරපදය වැරදියි!")
        return

    # =========================================================================
    # 2. MAIN DASHBOARD SHELL & SIDEBAR THEME
    # =========================================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
        .stApp {
            background-color: #f1f5f9 !important;
            font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
        }
        /* Sidebar එක පැහැදිලිව දර්ශනය කරවීම */
        section[data-testid="stSidebar"] {
            display: block !important;
            background-color: #1e1b4b !important;
            padding-top: 1rem !important;
        }
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
            margin-bottom: 8px !important;
            width: 100% !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        }
        div[data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #1e40af !important;
            transform: translateX(4px);
        }
        .logout-btn-container button {
            background-color: #b91c1c !important;
            color: #ffffff !important;
            border: 1px solid #ef4444 !important;
            font-weight: 800 !important;
            font-size: 14px !important;
            justify-content: center !important;
            text-align: center !important;
            margin-top: 25px !important;
            width: 100% !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
        .logout-btn-container button:hover {
            background-color: #dc2626 !important;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.5) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    u_name = user.get('name') or user.get('username') or "පරිශීලක"
    u_title = user.get('title') or "විෂය භාර නිලධාරී"
    u_role = user.get('role', 'Officer')

    # Sidebar Header & User Card
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);'>
        <h2 style='color: #fbbf24; margin: 0; font-size: 22px; font-weight: 800;'>AIP 2026</h2>
        <p style='font-size: 10px; color: #94a3b8; margin: 2px 0 0; text-transform: uppercase;'>ප්‍රගති පාලන පද්ධතිය</p>
    </div>

    <div style='display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.06); padding: 12px; border-radius: 12px; margin: 15px 0;'>
        <div style='background: #1e40af; color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px;'>
            {u_name.strip()[0].upper()}
        </div>
        <div style='overflow: hidden;'>
            <div style='color: white; font-size: 13.5px; font-weight: 700;'>{u_name}</div>
            <div style='color: #94a3b8; font-size: 11px;'>{u_title}</div>
            <span style='background: #10b98125; color: #34d399; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;'>{u_role}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation Buttons
    st.sidebar.markdown("<p style='color: #94a3b8; font-size: 12px; font-weight: bold; margin-bottom: 8px;'>ප්‍රධාන අංශ</p>", unsafe_allow_html=True)
    if st.sidebar.button("📊 ප්‍රධාන පාලක පුවරුව", key="btn_dash", use_container_width=True):
        st.rerun()

    # Logout Button
    st.sidebar.markdown("<div class='logout-btn-container'>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 පද්ධතියෙන් ඉවත් වන්න", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        if "aip_auth" in st.query_params:
            del st.query_params["aip_auth"]
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # ප්‍රධාන Dashboard එක පූරණය කිරීම (සියලුම Forms සහ Recent Log ඇත්තේ මෙහිය)
    dashboard.render_dashboard(user)

if __name__ == "__main__":
    main()
