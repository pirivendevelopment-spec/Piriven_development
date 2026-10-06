import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

# Local import ආරක්ෂිතව තහවුරු කිරීම
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import db

st.set_page_config(page_title="AIP 2026 - පිරිවෙන් ඒකකය", layout="wide", initial_sidebar_state="expanded")

# --- Session State & Auto-Login පරීක්ෂාව ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "📊 පාලක පුවරුව"

# Refresh කළ විට නැවත ලොග් වීම (Remember Me)
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
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
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
            div[data-testid="stTextInput"] input {
                background-color: #f8fafc !important;
                border: 1.5px solid #e2e8f0 !important;
                border-radius: 10px !important;
                padding: 12px 14px !important;
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
                <h1 style='color: #ffffff; margin: 0; font-size: 28px; font-weight: 800;'>AIP 2026</h1>
                <p style='color: #94a3b8; font-size: 13.5px; margin-top: 4px; font-weight: 600;'>පිරිවෙන් ඒකක ප්‍රගති පාලන පද්ධතිය</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                u = st.text_input("පරිශීලක නාමය (Username)", placeholder="Username එක ඇතුළත් කරන්න")
                p = st.text_input("මුරපදය (Password)", type="password", placeholder="••••••••")
                remember_me = st.checkbox("මා මතක තබා ගන්න (Remember Login)", value=True)
                
                submitted = st.form_submit_button("පද්ධතියට පිවිසෙන්න")
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
    # 2. MAIN APPLICATION UI & SIDEBAR
    # =========================================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
        .stApp {
            background-color: #f8fafc !important;
            font-family: 'Inter', 'Noto Sans Sinhala', sans-serif !important;
        }
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
            justify-content: center !important;
            text-align: center !important;
            margin-top: 25px !important;
            width: 100% !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    u_name = user.get('name') or user.get('username') or "පරිශීලක"
    u_title = user.get('title') or "විෂය භාර නිලධාරී"
    u_role = user.get('role', 'Officer')
    is_super_admin = str(u_role).lower() in ["super admin", "admin", "ප්‍රධාන පරිපාලක"]

    # Sidebar Profile Card
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
    nav_buttons = [
        "📊 පාලක පුවරුව",
        "📑 වවුචර විස්තර",
        "📝 වැඩසටහන් එක් කරන්න",
        "🖨️ පද්ධති වාර්තා"
    ]

    for item in nav_buttons:
        if st.sidebar.button(item, key=f"side_{item}", use_container_width=True):
            st.session_state.selected_menu = item
            st.rerun()

    # Logout
    st.sidebar.markdown("<div class='logout-btn-container'>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 පද්ධතියෙන් ඉවත් වන්න", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        if "aip_auth" in st.query_params:
            del st.query_params["aip_auth"]
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # 3. TOP NAVIGATION (උඩින් ඇති බොත්තම් මඟින් මාරු වීම)
    # =========================================================================
    default_idx = nav_buttons.index(st.session_state.selected_menu) if st.session_state.selected_menu in nav_buttons else 0
    active_tab = st.radio("ප්‍රධාන මෙනුව", nav_buttons, index=default_idx, horizontal=True, label_visibility="collapsed")
    
    if active_tab != st.session_state.selected_menu:
        st.session_state.selected_menu = active_tab
        st.rerun()

    st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

    # =========================================================================
    # VIEW 1: 📊 පාලක පුවරුව (KPIs & Summary)
    # =========================================================================
    if active_tab == "📊 පාලක පුවරුව":
        st.markdown("### 📊 AIP 2026 ප්‍රධාන පාලක පුවරුව")
        
        conn = db.get_connection()
        v_df = pd.read_sql_query("SELECT * FROM voucher_log WHERE delete_requested = 0 OR delete_requested IS NULL", conn)
        a_df = pd.read_sql_query("SELECT * FROM data_log WHERE delete_requested = 0 OR delete_requested IS NULL", conn)
        conn.close()

        total_spent = v_df["amount"].sum() if not v_df.empty else 0.0
        total_activities = len(a_df) if not a_df.empty else 0
        total_estimate = a_df["estimate"].sum() if not a_df.empty else 0.0

        k1, k2, k3 = st.columns(3)
        k1.metric("මුළු වියදම (වවුචර)", f"රු. {total_spent:,.2f}")
        k2.metric("සම්පූර්ණ කළ වැඩසටහන්", f"{total_activities}")
        k3.metric("මුළු ඇස්තමේන්තුව", f"රු. {total_estimate:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1.5, 1])
        with col_c1:
            st.subheader("📈 වැය ශීර්ෂ අනුව වියදම්")
            if not v_df.empty:
                chart_df = v_df.groupby("vote_number")["amount"].sum().reset_index()
                fig = px.bar(chart_df, x="vote_number", y="amount", color="amount", 
                             color_continuous_scale="Teal", labels={"vote_number": "වැය ශීර්ෂය", "amount": "මුදල (රු.)"})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("වියදම් දත්ත නොමැත.")

        with col_c2:
            st.subheader("📝 මෑතකාලීන වැඩසටහන්")
            if not a_df.empty:
                st.dataframe(a_df[["activity_name", "location", "actual_cost"]].tail(5), use_container_width=True, hide_index=True)
            else:
                st.info("වැඩසටහන් දත්ත නොමැත.")

    # =========================================================================
    # VIEW 2: 📑 වවුචර විස්තර ඇතුළත් කිරීම (Voucher Form)
    # =========================================================================
    elif active_tab == "📑 වවුචර විස්තර":
        st.markdown("### 📑 නව වවුචරයක් ඇතුළත් කිරීම")
        ref_df = db.get_reference_options(user)

        with st.form("voucher_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                vote_opts = ref_df["vote_number"].dropna().unique().tolist()
                sel_vote = st.selectbox("වැය ශීර්ෂය (Vote Number)", vote_opts if vote_opts else ["N/A"])
                act_opts = ref_df[ref_df["vote_number"] == sel_vote]["action_no"].dropna().unique().tolist() if vote_opts else ["N/A"]
                sel_act = st.selectbox("ක්‍රියාකාරකම් අංකය (Action No)", act_opts)
                v_no = st.text_input("වවුචර අංකය (Voucher No)")

            with col2:
                v_date = st.date_input("වවුචර දිනය", value=datetime.today())
                amount = st.number_input("වියදම් මුදල (රු.)", min_value=0.0, step=100.0)
                desc = st.text_area("වියදම් විස්තරය (Description)")

            if st.form_submit_button("💾 වවුචරය සුරකින්න", use_container_width=True):
                if v_no and amount > 0:
                    db.save_voucher(user["username"], sel_vote, sel_act, desc, v_no, v_date, amount)
                    st.toast("✅ වවුචරය සාර්ථකව සුරකින ලදී!")
                    st.rerun()
                else:
                    st.error("කරුණාකර වවුචර අංකය සහ මුදල නිවැරදිව ඇතුළත් කරන්න.")

    # =========================================================================
    # VIEW 3: 📝 වැඩසටහන් එක් කරන්න (Activity Form)
    # =========================================================================
    elif active_tab == "📝 වැඩසටහන් එක් කරන්න":
        st.markdown("### 📝 නව වැඩසටහනක් ඇතුළත් කිරීම")
        ref_df = db.get_reference_options(user)

        with st.form("activity_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                vote_opts = ref_df["vote_number"].dropna().unique().tolist()
                a_vote = st.selectbox("වැය ශීර්ෂය", vote_opts if vote_opts else ["N/A"])
                act_opts = ref_df[ref_df["vote_number"] == a_vote]["action_no"].dropna().unique().tolist() if vote_opts else ["N/A"]
                a_act_no = st.selectbox("ක්‍රියාකාරකම් අංකය", act_opts)
                act_name = st.text_input("වැඩසටහනේ නම (Activity Name)")
                location = st.text_input("පැවැත්වූ ස්ථානය (Location)")

            with col2:
                act_date = st.date_input("පැවැත්වූ දිනය", value=datetime.today())
                beneficiaries = st.number_input("ප්‍රතිලාභීන් සංඛ්‍යාව", min_value=0, step=1)
                estimate = st.number_input("ඇස්තමේන්තු මුදල (රු.)", min_value=0.0, step=500.0)
                actual_cost = st.number_input("සැබෑ වියදම (රු.)", min_value=0.0, step=500.0)

            if st.form_submit_button("💾 වැඩසටහන සුරකින්න", use_container_width=True):
                if act_name:
                    db.save_activity(user["username"], a_vote, a_act_no, act_name, location, act_date, beneficiaries, estimate, actual_cost)
                    st.toast("✅ වැඩසටහන සාර්ථකව ඇතුළත් කරන ලදී!")
                    st.rerun()
                else:
                    st.error("කරුණාකර වැඩසටහනේ නම ඇතුළත් කරන්න.")

    # =========================================================================
    # VIEW 4: 🖨️ පද්ධති වාර්තා
    # =========================================================================
    elif active_tab == "🖨️ පද්ධති වාර්තා":
        st.markdown("### 🖨️ පද්ධති වාර්තා සහ සාරාංශ")
        conn = db.get_connection()
        rep_v = pd.read_sql_query("SELECT * FROM voucher_log WHERE delete_requested = 0 OR delete_requested IS NULL", conn)
        rep_a = pd.read_sql_query("SELECT * FROM data_log WHERE delete_requested = 0 OR delete_requested IS NULL", conn)
        conn.close()

        st.subheader("📑 සියලුම වවුචර වාර්තාව")
        st.dataframe(rep_v, use_container_width=True)

        st.subheader("📝 සියලුම වැඩසටහන් වාර්තාව")
        st.dataframe(rep_a, use_container_width=True)

    # =========================================================================
    # 4. මෑතකාලීන වියදම් ලොගය (EDIT / DELETE REQUEST / SUPER ADMIN APPROVE)
    # =========================================================================
    st.markdown("---")
    st.subheader("📋 මෑතකාලීන වියදම් ලොගය (Recent Expense Log)")

    conn = db.get_connection()
    vouchers_df = pd.read_sql_query("""
        SELECT rowid as id, timestamp, vote_number, action_no, description, 
               voucher_no, voucher_date, amount, delete_requested, delete_reason, username
        FROM voucher_log 
        ORDER BY rowid DESC LIMIT 10
    """, conn)
    conn.close()

    if vouchers_df.empty:
        st.info("මෑතකාලීන වියදම් කිසිවක් හමු නොවීය.")
    else:
        for _, row in vouchers_df.iterrows():
            v_id = row['id']
            is_del_pending = bool(row.get('delete_requested') == 1)
            border_color = "#ef4444" if is_del_pending else "#cbd5e1"
            bg_color = "#fef2f2" if is_del_pending else "#ffffff"

            with st.container():
                st.markdown(f"""
                <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #0f172a; font-size: 15px;">වවුචර අංකය: {row['voucher_no']}</strong> 
                            <span style="color: #64748b; font-size: 12px; margin-left: 10px;">({row['voucher_date']})</span>
                            <div style="color: #334155; font-size: 13.5px; margin-top: 4px;">
                                වැය ශීර්ෂය: <b>{row['vote_number']}</b> | විස්තරය: {row['description']}
                            </div>
                            {f"<div style='color: #dc2626; font-size: 12px; margin-top: 4px;'><b>⚠️ ඉවත් කිරීමට ඉල්ලුම් කර ඇත:</b> {row.get('delete_reason')}</div>" if is_del_pending else ""}
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 16px; font-weight: bold; color: #0f766e;">රු. {float(row['amount']):,.2f}</span>
                            <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">ඇතුළත් කළේ: {row.get('username', 'N/A')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_btn1, col_btn2, col_btn3, _ = st.columns([1.5, 1.8, 1.8, 5])
                
                # 1. Edit Button (Expander/Popover)
                with col_btn1:
                    with st.popover("✏️ Edit"):
                        with st.form(key=f"edit_v_{v_id}"):
                            st.write(f"**වවුචරය සංස්කරණය (#{row['voucher_no']})**")
                            e_vno = st.text_input("වවුචර අංකය", value=str(row['voucher_no']))
                            e_desc = st.text_input("විස්තරය", value=str(row['description']))
                            e_amount = st.number_input("මුදල (රු.)", value=float(row['amount']), step=500.0)
                            e_date = st.text_input("දිනය (YYYY-MM-DD)", value=str(row['voucher_date']))
                            
                            if st.form_submit_button("💾 සුරකින්න"):
                                db.update_voucher(v_id, row['vote_number'], row['action_no'], e_desc, e_vno, e_date, e_amount)
                                st.toast("වවුචරය සංස්කරණය කරන ලදී!")
                                st.rerun()

                # 2. Officer Delete Request
                if not is_super_admin:
                    with col_btn2:
                        if not is_del_pending:
                            with st.popover("⚠️ Delete"):
                                with st.form(key=f"del_v_form_{v_id}"):
                                    reason = st.text_input("හේතුව", placeholder="දත්ත වැරදීමක්")
                                    if st.form_submit_button("ඉල්ලීම යවන්න"):
                                        if reason.strip():
                                            db.request_voucher_delete(v_id, reason)
                                            st.toast("ඉල්ලීම Admin වෙත යොමු විය!")
                                            st.rerun()
                                        else:
                                            st.error("හේතුව දක්වන්න.")

                # 3. Super Admin Approve / Reject
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

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
