import streamlit as st
import pandas as pd
from datetime import datetime
# පැරණි import db වෙනුවට:
import aip_db as db

def render_activities(user):
    st.markdown("### 📋 වැඩසටහන් දත්ත ඇතුළත් කිරීම (Activity Entry)")
    st.markdown("<p style='color: #64748b; font-size: 14px;'>පිරිවෙන් ඒකකයේ වාර්ෂික සැලැස්මට අදාළව ක්‍රියාත්මක කළ වැඩසටහන් තොරතුරු සහ සත්‍ය වියදම් මෙහි ඇතුළත් කරන්න.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 1. අවසර ලත් වැඩසටහන් ලබා ගැනීම
    ref_df = db.get_reference_options(user)
    if ref_df.empty:
        st.error("⚠️ ඔබට අවසර ලත් වැඩසටහන් හෝ විෂයයන් හමු නොවීය.")
        return

    options = {
        f"#{r['action_no']} - {r['activity_name']} ({r['vote_number']})": (r['action_no'], r['vote_number']) 
        for _, r in ref_df.iterrows()
    }

    # 2. දත්ත ඇතුළත් කිරීමේ පෝරමය
    with st.form("act_form", clear_on_submit=True):
        sel_display = st.selectbox("වැඩසටහන හෝ විෂය තෝරන්න (Action / Vote)", list(options.keys()))
        name = st.text_input("ක්‍රියාත්මක කළ නිශ්චිත වැඩසටහනේ නම", placeholder="උදා: ත්‍රිපිටක ධර්මය ගුරු පුහුණු වැඩමුළුව")
        
        c1, c2 = st.columns(2)
        loc = c1.text_input("ස්ථානය (Location)", placeholder="උදා: මීතිරිගල නිස්සරණ වනය")
        date = c2.date_input("පැවැත්වූ දිනය (Date)", value=datetime.today())
        
        c3, c4, c5 = st.columns(3)
        ben = c3.number_input("ප්‍රතිලාභීන් සංඛ්‍යාව", min_value=0, step=1, value=0)
        est = c4.number_input("ඇස්තමේන්තුව (රු.)", min_value=0.0, step=100.0, value=0.0)
        cost = c5.number_input("සත්‍ය වියදම (Actual Cost - රු.)", min_value=0.0, step=100.0, value=0.0)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 දත්ත සුරකින්න (Save Activity)", use_container_width=True, type="primary")
        
        if submitted:
            if not name.strip():
                st.error("⚠️ කරුණාකර වැඩසටහනේ නම ඇතුළත් කරන්න.")
            else:
                action_no, vote_no = options[sel_display]
                try:
                    success = db.save_activity(
                        user['username'], 
                        vote_no, 
                        action_no, 
                        name.strip(), 
                        loc.strip(), 
                        str(date), 
                        int(ben), 
                        float(est), 
                        float(cost)
                    )
                    if success:
                        st.success(f"✅ වැඩසටහන් දත්ත සාර්ථකව MySQL දත්ත සමුදායේ තැන්පත් විය! (Action No: {action_no})")
                        st.rerun()
                    else:
                        st.error("⚠️ දත්ත සුරැකීමේදී දෝෂයක් ඇති විය. කරුණාකර නැවත උත්සාහ කරන්න.")
                except Exception as e:
                    st.error(f"⚠️ දත්ත සමුදා දෝෂයකි: {e}")

    # =========================================================================
    # 3. මෑතකාලීන වැඩසටහන් දත්ත ලැයිස්තුව හා කළමනාකරණය (Recent Activities Log)
    # =========================================================================
    st.markdown("<br><hr style='border-color: #cbd5e1;'>", unsafe_allow_html=True)
    st.markdown("#### 📜 මෑතකාලීන වැඩසටහන් වාර්තා (Recent Activity Records)")

    activities_df = db.fetch_activities_from_cloud()
    
    if activities_df.empty:
        st.info("තවමත් කිසිදු වැඩසටහනක් ඇතුළත් කර නොමැත.")
        return

    # පරිශීලක ප්‍රවේශ සීමාව අනුව පෙරීම
    is_super_admin = str(user.get("role", "")).lower() in ["super admin", "admin", "ප්‍රධාන පරිපාලක"]
    acc = user.get("access_level", "")
    user_access = [x.strip() for x in acc.split(',')] if acc and acc != "All" else []

    if not is_super_admin and acc != "All":
        if user_access:
            activities_df = activities_df[
                activities_df['action_no'].astype(str).isin(user_access) | 
                (activities_df['username'] == user.get('username'))
            ]
        else:
            activities_df = activities_df[activities_df['username'] == user.get('username')]

    if activities_df.empty:
        st.info("ඔබගේ විෂයට අදාළ මෑතකාලීන වැඩසටහන් කිසිවක් හමු නොවීය.")
        return

    # මුල් වාර්තා 15 ප්‍රදර්ශනය කිරීම
    for _, row in activities_df.head(15).iterrows():
        act_id = row['id']
        is_del_pending = bool(row.get('delete_requested', 0) == 1)
        border_color = "#ef4444" if is_del_pending else "#cbd5e1"
        bg_color = "#fef2f2" if is_del_pending else "#ffffff"

        card_html = (
            f'<div style="background-color: {bg_color}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">'
            f'<table style="width: 100%; border-collapse: collapse; border: none;">'
            f'<tr style="border: none;">'
            f'<td style="text-align: left; vertical-align: top; border: none;">'
            f'<strong style="color: #0f172a !important; font-size: 15px;">{row.get("act_name", "N/A")}</strong>'
            f'<span style="color: #64748b !important; font-size: 12px; margin-left: 8px;">({str(row.get("act_date", "N/A"))[:10]})</span>'
            f'<div style="color: #334155 !important; font-size: 13px; margin-top: 4px;">'
            f'වැය ශීර්ෂය: <b>{row.get("vote_no", "N/A")}</b> | විෂය අංකය: <b>#{row.get("action_no", "N/A")}</b> | ස්ථානය: <b>{row.get("loc", "නොදක්වා ඇත")}</b> | ප්‍රතිලාභීන්: <b>{row.get("ben", 0)}</b>'
            f'</div>'
            + (f'<div style="color: #dc2626 !important; font-size: 12px; margin-top: 4px;"><b>⚠️ ඉවත් කිරීමට ඉල්ලුම් කර ඇත:</b> {row.get("delete_reason", "")}</div>' if is_del_pending else '') +
            f'</td>'
            f'<td style="text-align: right; vertical-align: top; border: none;">'
            f'<span style="font-size: 16px; font-weight: 800; color: #0f766e !important;">රු. {float(row.get("cost", 0)):,.2f}</span>'
            f'<div style="font-size: 11px; color: #64748b !important; margin-top: 2px;">ඇස්තමේන්තුව: රු. {float(row.get("est", 0)):,.2f}</div>'
            f'<div style="font-size: 11px; color: #94a3b8 !important;">ඇතුළත් කළේ: {row.get("username", "N/A")}</div>'
            f'</td>'
            f'</tr>'
            f'</table>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        col_btn1, col_btn2, col_btn3, _ = st.columns([1.2, 1.8, 1.8, 6])

        # 1. Edit Option
        with col_btn1:
            with st.popover("✏️ Edit"):
                with st.form(key=f"edit_act_{act_id}"):
                    st.write(f"**වැඩසටහන සංස්කරණය (#{row.get('action_no')})**")
                    e_name = st.text_input("වැඩසටහනේ නම", value=str(row.get('act_name', '')))
                    e_loc = st.text_input("ස්ථානය", value=str(row.get('loc', '')))
                    e_ben = st.number_input("ප්‍රතිලාභීන්", value=int(row.get('ben', 0)), step=1)
                    e_est = st.number_input("ඇස්තමේන්තුව (රු.)", value=float(row.get('est', 0)), step=500.0)
                    e_cost = st.number_input("සත්‍ය වියදම (රු.)", value=float(row.get('cost', 0)), step=500.0)
                    e_date = st.text_input("දිනය (YYYY-MM-DD)", value=str(row.get('act_date', ''))[:10])

                    if st.form_submit_button("💾 සුරකින්න"):
                        conn = db.get_connection()
                        cur = conn.cursor()
                        try:
                            cur.execute("""
                                UPDATE program_data_log 
                                SET program_name = %s, location = %s, held_date = %s, 
                                    beneficiaries_count = %s, estimated_amount = %s, actual_expenditure = %s 
                                WHERE log_id = %s
                            """, (e_name, e_loc, e_date, e_ben, e_est, e_cost, act_id))
                            conn.commit()
                            st.toast("වැඩසටහන් විස්තර සාර්ථකව යාවත්කාලීන විය!")
                            st.rerun()
                        finally:
                            cur.close()
                            conn.close()

        # 2. Regular User - Delete Request
        if not is_super_admin:
            with col_btn2:
                if not is_del_pending:
                    with st.popover("⚠️ Delete Request"):
                        with st.form(key=f"del_act_form_{act_id}"):
                            reason = st.text_input("හේතුව", placeholder="වැරදි දත්තයක් ඇතුළත් විය")
                            if st.form_submit_button("ඉල්ලීම යවන්න"):
                                if reason.strip():
                                    conn = db.get_connection()
                                    cur = conn.cursor()
                                    try:
                                        cur.execute("UPDATE program_data_log SET delete_requested = 1, delete_reason = %s WHERE log_id = %s", (reason.strip(), act_id))
                                        conn.commit()
                                        st.toast("ඉල්ලීම Admin වෙත යොමු විය!")
                                        st.rerun()
                                    finally:
                                        cur.close()
                                        conn.close()
                                else:
                                    st.error("කරුණාකර හේතුව දක්වන්න.")

        # 3. Super Admin - Approve / Reject Delete
        if is_super_admin and is_del_pending:
            with col_btn2:
                if st.button("🗑️ Approve Delete", key=f"app_d_act_{act_id}", type="primary"):
                    conn = db.get_
