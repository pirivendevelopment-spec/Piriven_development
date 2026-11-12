import streamlit as st
import sys
import os
import pandas as pd
import importlib

# 1. aip_financial folder එක sys.path හි මුල්ම ස්ථානයට එක් කිරීම
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# 2. පවතින cache එක ඉවත් කර aip_financial/aip_db.py නැවුම්ව import කිරීම
if "aip_db" in sys.modules:
    del sys.modules["aip_db"]

import aip_db as db
importlib.reload(db)

from modules import dashboard, vouchers, activities, reports

st.set_page_config(page_title="AIP 2026 - පිරිවෙන් ඒකකය", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "පාලක පුවරුව"

# --- Remember Login (Auto-Login via Query Param) ---
if not st.session_state.logged_in:
    saved_user = st.query_params.get("aip_auth")
    if saved_user:
        user_data = db.get_user_by_username(saved_user)
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user = dict(user_data)

# =========================================================================
# පරිශීලකයාගේ Access Level අනුව දත්ත Filter කරන උපකාරක ශ්‍රිතය
# =========================================================================
def filter_by_user_access(df, user):
    if df.empty:
        return df
    role = str(user.get("role", "")).lower()
    acc = str(user.get("access_level", "")).strip()
    if role in ["super admin", "admin", "executive", "ප්‍රධාන පරිපාලක"] or acc in ["All", "All Management", "0", ""]:
        return df

    allowed_actions = [x.strip().removesuffix(".0") for x in acc.split(",") if x.strip()]
    uname = user.get("username", "")

    def is_allowed(row):
        if str(row.get("username", "")) == uname:
            return True
        act_str = str(row.get("action_no", "")).strip().removesuffix(".0")
        for allowed in allowed_actions:
            if act_str == allowed or act_str.startswith(allowed + "."):
                return True
        return False

    return df[df.apply(is_allowed, axis=1)]

# =========================================================================
# ආරක්ෂිත සංඛ්‍යා පරිවර්තන ශ්‍රිත (NaN Safe Helpers)
# =========================================================================
def safe_int(val, default=0):
    num = pd.to_numeric(val, errors="coerce")
    return int(num) if pd.notna(num) else default

def safe_float(val, default=0.0):
    num = pd.to_numeric(val, errors="coerce")
    return float(num) if pd.notna(num) else default

# =========================================================================
# මෑතකාලීන වියදම් ලොගය සඳහා Edit / Delete Actions Render කරන ශ්‍රිතය
# =========================================================================
def render_inline_expense_actions(user):
    st.markdown("<br><hr style='border-color: #cbd5e1;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #0f172a !important; font-weight: 800; margin-bottom: 10px;'>📋 මෑතකාලීන වියදම් කළමනාකරණය (Edit & Delete Requests)</h4>", unsafe_allow_html=True)

    is_super_admin = str(user.get("role", "")).lower() in ["super admin", "admin", "ප්‍රධාන පරිපාලක"]

    tab_act, tab_vouch = st.tabs(["📝 වැඩසටහන් වියදම් (Program Activities)", "📑 වවුචර වියදම් (Vouchers)"])

    # ---------------------------------------------------------------------
    # 1. වැඩසටහන් වියදම් (Program Activities Edit & Delete Request)
    # ---------------------------------------------------------------------
    with tab_act:
        try:
            act_df = db.fetch_activities_from_cloud()
            act_df = filter_by_user_access(act_df, user).head(15)
        except Exception:
            act_df = pd.DataFrame()

        if act_df.empty:
            st.info("ඔබගේ විෂයට අදාළ වැඩසටහන් වියදම් කිසිවක් හමු නොවීය.")
        else:
            for _, row in act_df.iterrows():
                l_id = row['id']
                is_del_pending = bool(safe_int(row.get('delete_requested', 0)) == 1)
                border_color = "#ef4444" if is_del_pending else "#cbd5e1"
                bg_color = "#fef2f2" if is_del_pending else "#ffffff"

                pname = row.get("program_name") or row.get("act_name") or "වැඩසටහන"
                loc = row.get("location") or row.get("loc") or ""
                hdate = str(row.get("held_date") or row.get("act_date") or "N/A")[:10]
                
                ben = safe_int(row.get("ben") if pd.notna(row.get("ben")) else row.get("beneficiaries_count"))
                est = safe_float(row.get("est") if pd.notna(row.get("est")) else row.get("estimated_amount"))
                cost = safe_float(row.get("cost") if pd.notna(row.get("cost")) else row.get("actual_expenditure"))

                card_html = (
                    f'<div style="background-color: {bg_color}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">'
                    f'<table style="width: 100%; border-collapse: collapse; border: none;">'
                    f'<tr style="border: none;">'
                    f'<td style="text-align: left; vertical-align: top; border: none;">'
                    f'<strong style="color: #0f172a !important; font-size: 14.5px;">{pname}</strong>'
                    f'<span style="color: #64748b !important; font-size: 12px; margin-left: 8px;">({hdate} | {loc})</span>'
                    f'<div style="color: #334155 !important; font-size: 13px; margin-top: 4px;">'
                    f'Action No: <b>#{row.get("action_no", "N/A")}</b> | ප්‍රතිලාභීන්: <b>{ben}</b> | ඇස්තමේන්තුව: <b>රු. {est:,.2f}</b>'
                    f'</div>'
                    + (f'<div style="color: #dc2626 !important; font-size: 12px; margin-top: 4px;"><b>⚠️ ඉවත් කිරීමට ඉල්ලුම් කර ඇත:</b> {row.get("delete_reason", "")}</div>' if is_del_pending else '') +
                    f'</td>'
                    f'<td style="text-align: right; vertical-align: top; border: none;">'
                    f'<span style="font-size: 16.5px; font-weight: 800; color: #15803d !important;">රු. {cost:,.2f}</span>'
                    f'<div style="font-size: 11px; color: #64748b !important; margin-top: 2px;">ඇතුළත් කළේ: {row.get("username", "N/A")}</div>'
                    f'</td>'
                    f'</tr>'
                    f'</table>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                c1, c2, c3, _ = st.columns([1.2, 1.8, 1.8, 6])
                with c1:
                    with st.popover("✏️ Edit"):
                        with st.form(key=f"edit_act_{l_id}"):
                            st.write("**වැඩසටහන සංස්කරණය**")
                            e_pname = st.text_input("වැඩසටහනේ නම", value=str(pname))
                            e_loc = st.text_input("ස්ථානය", value=str(loc))
                            e_hdate = st.text_input("පැවැත්වූ දිනය (YYYY-MM-DD)", value=str(hdate))
                            e_ben = st.number_input("ප්‍රතිලාභීන්", value=ben, step=1)
                            e_est = st.number_input("ඇස්තමේන්තුව (රු.)", value=est, step=500.0)
                            e_cost = st.number_input("සත්‍ය වියදම (රු.)", value=cost, step=500.0)
                            if st.form_submit_button("💾 සුරකින්න"):
                                db.update_activity(l_id, e_pname, e_loc, e_hdate, e_ben, e_est, e_cost)
                                st.toast("වැඩසටහන සාර්ථකව සංස්කරණය කරන ලදී!")
                                st.rerun()

                if not is_super_admin:
                    with c2:
                        if not is_del_pending:
                            with st.popover("⚠️ Delete Request"):
                                with st.form(key=f"del_act_form_{l_id}"):
                                    reason = st.text_input("හේතුව", placeholder="දත්ත වැරදීමක් / අවලංගු වීම")
                                    if st.form_submit_button("ඉල්ලීම යවන්න"):
                                        if reason.strip():
                                            db.request_activity_delete(l_id, reason.strip())
                                            st.toast("ඉල්ලීම Admin වෙත යොමු විය!")
                                            st.rerun()
                                        else:
                                            st.error("හේතුව දක්වන්න.")

                if is_super_admin and is_del_pending:
                    with c2:
                        if st.button("🗑️ Approve Delete", key=f"app_act_{l_id}", type="primary"):
                            db.delete_activity_permanent(l_id)
                            st.toast("වැඩසටහන ස්ථිරවම මකා දමන ලදී!")
                            st.rerun()
                    with c3:
                        if st.button("❌ Reject", key=f"rej_act_{l_id}"):
                            db.cancel_activity_delete_request(l_id)
                            st.toast("ඉල්ලීම ප්‍රතික්ෂේප විය.")
                            st.rerun()

    # ---------------------------------------------------------------------
    # 2. වවුචර වියදම් (Vouchers Edit & Delete Request)
    # ---------------------------------------------------------------------
    with tab_vouch:
        try:
            vouchers_df = db.fetch_vouchers_from_cloud()
            vouchers_df = filter_by_user_access(vouchers_df, user).head(15)
        except Exception:
            vouchers_df = pd.DataFrame()

        if vouchers_df.empty:
            st.info("ඔබගේ විෂයට අදාළ වවුචර වියදම් කිසිවක් හමු නොවීය.")
        else:
            for _, row in vouchers_df.iterrows():
                v_id = row['id']
                is_del_pending = bool(safe_int(row.get('delete_requested', 0)) == 1)
                border_color = "#ef4444" if is_del_pending else "#cbd5e1"
                bg_color = "#fef2f2" if is_del_pending else "#ffffff"

                v_no_val = row.get("voucher_no") or row.get("v_no") or "N/A"
                v_date_val = str(row.get("voucher_date") or row.get("v_date") or "N/A")[:10]
                desc_val = row.get("description") or row.get("desc") or ""
                vote_val = row.get("vote_number") or row.get("vote_no") or "N/A"
                amt_val = safe_float(row.get("amount"))

                card_html = (
                    f'<div style="background-color: {bg_color}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">'
                    f'<table style="width: 100%; border-collapse: collapse; border: none;">'
                    f'<tr style="border: none;">'
                    f'<td style="text-align: left; vertical-align: top; border: none;">'
                    f'<strong style="color: #0f172a !important; font-size: 14.5px;">වවුචර අංකය: {v_no_val}</strong>'
                    f'<span style="color: #64748b !important; font-size: 12px; margin-left: 8px;">({v_date_val})</span>'
                    f'<div style="color: #334155 !important; font-size: 13px; margin-top: 4px;">'
                    f'වැය ශීර්ෂය: <b>{vote_val}</b> | Action No: <b>#{row.get("action_no", "N/A")}</b> | විස්තරය: {desc_val}'
                    f'</div>'
                    + (f'<div style="color: #dc2626 !important; font-size: 12px; margin-top: 4px;"><b>⚠️ ඉවත් කිරීමට ඉල්ලුම් කර ඇත:</b> {row.get("delete_reason", "")}</div>' if is_del_pending else '') +
                    f'</td>'
                    f'<td style="text-align: right; vertical-align: top; border: none;">'
                    f'<span style="font-size: 16.5px; font-weight: 800; color: #0f766e !important;">රු. {amt_val:,.2f}</span>'
                    f'<div style="font-size: 11px; color: #64748b !important; margin-top: 2px;">ඇතුළත් කළේ: {row.get("username", "N/A")}</div>'
                    f'</td>'
                    f'</tr>'
                    f'</table>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                col_btn1, col_btn2, col_btn3, _ = st.columns([1.2, 1.8, 1.8, 6])
                with col_btn1:
                    with st.popover("✏️ Edit"):
                        with st.form(key=f"edit_v_{v_id}"):
                            st.write(f"**වවුචරය සංස්කරණය (#{v_no_val})**")
                            e_vno = st.text_input("වවුචර අංකය", value=str(v_no_val))
                            e_desc = st.text_input("විස්තරය", value=str(desc_val))
                            e_amount = st.number_input("මුදල (රු.)", value=amt_val, step=500.0)
                            e_date = st.text_input("දිනය (YYYY-MM-DD)", value=str(v_date_val))
                            if st.form_submit_button("💾 සුරකින්න"):
                                db.update_voucher(v_id, vote_val, row.get('action_no'), e_desc, e_vno, e_date, e_amount)
                                st.toast("වවුචරය සාර්ථකව සංස්කරණය කරන ලදී!")
                                st.rerun()

                if not is_super_admin:
                    with col_btn2:
                        if not is_del_pending:
                            with st.popover("⚠️ Delete Request"):
                                with st.form(key=f"del_v_form_{v_id}"):
                                    reason = st.text_input("හේතුව", placeholder="දත්ත වැරදීමක්")
                                    if st.form_submit_button("ඉල්ලීම යවන්න"):
                                        if reason.strip():
                                            db.request_voucher_delete(v_id, reason.strip())
                                            st.toast("ඉල්ලීම Admin වෙත යොමු විය!")
                                            st.rerun()
                                        else:
                                            st.error("හේතුව දක්වන්න.")

                if is_super_admin and is_del_pending:
                    with col_btn2:
                        if st.button("🗑️ Approve Delete", key=f"app_d_{v_id}", type="primary"):
                            db.delete_voucher_permanent(v_id)
                            st.toast("වවුචරය ස්ථිරවම මකා දමන ලදී!")
                            st.rerun()
                    with col_btn3:
                        if st.button("❌ Reject", key=f"rej_d_{v_id}"):
                            db.cancel_voucher_delete_request(v_id)
                            st.toast("ඉල්ලීම ප්‍රතික්ෂේප විය.")
                            st.rerun()


def main():
    # =========================================================================
    # 1. LOGIN SCREEN
    # =========================================================================
    if not st.session_state.logged_in:
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
            
            .stApp {
                background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 100%) !important;
                font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
            }
            
            section[data-testid="stSidebar"] { display: none !important; }

            div[data-testid="stForm"] {
                background: #ffffff !important;
                border-radius: 20px !important;
                padding: 35px 30px !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45) !important;
            }

            div[data-testid="stForm"] label, div[data-testid="stForm"] p, div[data-testid="stForm"] span {
                color: #1e293b !important;
            }

            div[data-testid="stTextInput"] input {
                background-color: #f8fafc !important;
                border: 1.5px solid #cbd5e1 !important;
                border-radius: 10px !important;
                color: #0f172a !important;
            }

            div[data-testid="stFormSubmitButton"] > button {
                background: #1e40af !important;
                color: #ffffff !important;
                border: none !important;
                padding: 13px !important;
                border-radius: 10px !important;
                font-weight: 800 !important;
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
                <h1 style='color: #ffffff !important; margin: 0; font-size: 28px; font-weight: 800;'>AIP 2026</h1>
                <p style='color: #cbd5e1 !important; font-size: 13.5px; margin-top: 4px; font-weight: 600;'>පිරිවෙන් ඒකක ප්‍රගති පාලන පද්ධතිය</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                u = st.text_input("පරිශීලක නාමය (Username)", placeholder="ඔබේ username එක ඇතුළත් කරන්න")
                p = st.text_input("මුරපදය (Password)", type="password", placeholder="••••••••")
                remember_me = st.checkbox("මා මතක තබා ගන්න (Remember Login)", value=True)
                
                submitted = st.form_submit_button("පද්ධතියට පිවිසෙන්න")
                if submitted:
                    user = db.authenticate_user(u.strip(), p.strip())
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = dict(user)
                        st.session_state.selected_menu = "පාලක පුවරුව"
                        if remember_me:
                            st.query_params["aip_auth"] = user["username"]
                        st.rerun()
                    else:
                        st.error("පරිශීලක නාමය හෝ මුරපදය වැරදියයි!")
        return

    # =========================================================================
    # 2. MAIN DASHBOARD SHELL (LIGHT THEME ENFORCED + HIGH CONTRAST SIDEBAR)
    # =========================================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');

        /* ප්‍රධාන පසුබිම Light Mode ලෙස ස්ථාවර කිරීම */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #f1f5f9 !important;
            color: #0f172a !important;
            font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
        }

        /* ප්‍රධාන තිරයේ සියලුම පෙළ, Labels සහ Inputs තද පැහැයෙන් පෙන්වීම */
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
        .main p, .main label, .main span, .main div {
            color: #0f172a;
        }

        .main input, .main textarea, .main select,
        .main div[data-baseweb="select"] > div,
        .main div[data-baseweb="input"] > div {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }

        /* Popover සහ Form ඇතුළත පැහැදිලි බව */
        div[data-testid="stPopoverBody"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        div[data-testid="stPopoverBody"] * {
            color: #0f172a !important;
        }

        /* Sidebar පසුබිම සහ අකුරු වර්ණ */
        section[data-testid="stSidebar"] {
            background-color: #1e1b4b !important;
        }
        
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div.stButton > button {
            background-color: rgba(255, 255, 255, 0.08) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            text-align: left !important;
            justify-content: flex-start !important;
            width: 100% !important;
            margin-bottom: 6px !important;
            transition: all 0.2s ease !important;
        }

        section[data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #312e81 !important;
            border-color: #818cf8 !important;
            transform: translateX(3px);
        }

        .logout-btn-container div.stButton > button {
            background-color: rgba(239, 68, 68, 0.2) !important;
            border-color: rgba(239, 68, 68, 0.45) !important;
            margin-top: 15px !important;
        }
        .logout-btn-container div.stButton > button:hover {
            background-color: #dc2626 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    u_name = user.get('name') or user.get('full_name') or user.get('username') or "පරිශීලක"
    u_title = user.get('title') or "විෂය භාර නිලධාරී"
    u_role = user.get('role') or user.get('role_designation') or "Officer"
    u_initial = u_name.strip()[0].upper() if u_name.strip() else "U"

    # Sidebar Header & User Profile Card
    st.sidebar.markdown(
        "<div style='text-align: center; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.15);'>"
        "<h2 style='color: #fbbf24 !important; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 1px;'>AIP 2026</h2>"
        "<p style='font-size: 11px; color: #e2e8f0 !important; margin: 4px 0 0; letter-spacing: 0.5px;'>ප්‍රගති පාලන පද්ධතිය</p>"
        "</div>"
        "<div style='display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.1); padding: 14px; border-radius: 12px; margin: 16px 0; border: 1px solid rgba(255,255,255,0.2);'>"
        f"<div style='background: #2563eb; color: #ffffff !important; width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; flex-shrink: 0;'>{u_initial}</div>"
        "<div style='overflow: hidden;'>"
        f"<div style='color: #ffffff !important; font-size: 14px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{u_name}'>{u_name}</div>"
        f"<div style='color: #cbd5e1 !important; font-size: 11.5px; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{u_title}</div>"
        f"<span style='background: #0f766e; color: #ffffff !important; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 5px; display: inline-block; margin-top: 5px;'>{u_role}</span>"
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # Sidebar Navigation Buttons
    nav_items = [
        ("📊 පාලක පුවරුව", "පාලක පුවරුව"),
        ("📑 වවුචර විස්තර", "වවුචර විස්තර"),
        ("📝 වැඩසටහන් එක් කරන්න", "වැඩසටහන් එක් කරන්න"),
        ("🖨️ පද්ධති වාර්තා", "පද්ධති වාර්තා")
    ]

    for label, key in nav_items:
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.selected_menu = key
            st.rerun()

    st.sidebar.markdown("<div class='logout-btn-container'>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 පද්ධතියෙන් ඉවත් වන්න", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.selected_menu = "පාලක පුවරුව"
        if "aip_auth" in st.query_params:
            del st.query_params["aip_auth"]
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    modules_map = {
        "පාලක පුවරුව": dashboard.render_dashboard,
        "වවුචර විස්තර": vouchers.render_vouchers,
        "වැඩසටහන් එක් කරන්න": activities.render_activities,
        "පද්ධති වාර්තා": reports.render_reports
    }

    # තෝරාගත් මොඩියුලය ධාවනය කිරීම
    modules_map[st.session_state.selected_menu](user)

    # ප්‍රධාන පාලක පුවරුවේදී පමණක් මෑතකාලීන වියදම් වලට Edit / Delete Controls පහළින් එක් කිරීම
    if st.session_state.selected_menu == "පාලක පුවරුව":
        render_inline_expense_actions(user)

if __name__ == "__main__":
    main()
