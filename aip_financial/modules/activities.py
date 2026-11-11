import streamlit as st
import pandas as pd
from datetime import datetime
import aip_db as db

def clean_str(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def clean_float(val):
    if pd.isna(val):
        return 0.0
    try:
        return float(val)
    except Exception:
        return 0.0

def render_activities(user):
    st.markdown("### 📋 වැඩසටහන් දත්ත ඇතුළත් කිරීම (Activity Entry)")
    st.markdown("<p style='color: #64748b; font-size: 14px;'>පිරිවෙන් ඒකකයේ වාර්ෂික සැලැස්මට අදාළව ක්‍රියාත්මක කළ වැඩසටහන් තොරතුරු සහ සත්‍ය වියදම් මෙහි ඇතුළත් කරන්න.</p>", unsafe_allow_html=True)
    st.markdown("---")

    is_super_admin = str(user.get("role", "")).lower() in ["super admin", "admin", "ප්‍රධාන පරිපාලක"]

    # =========================================================================
    # 0. EXCEL FILE UPLOAD SECTION (ADMIN ONLY - ඇඩ්මින්ට පමණි)
    # =========================================================================
    if is_super_admin:
        with st.expander("📤 Excel ගොනුවකින් සමස්ත දත්ත Host Database එකට Upload කිරීම (Admin Only)", expanded=False):
            st.markdown("""
                <div style='background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 4px solid #1e40af; margin-bottom: 12px;'>
                    <p style='margin: 0; font-size: 13px; color: #334155;'>
                        <b>AIP 2026.xlsx</b> ගොනුව මෙතැනට Upload කර එහි ඇති <b>Data_Log (වැඩසටහන් 69)</b> සහ <b>Voucher_Log (වවුචර් 15)</b> එකවර සජීවී MySQL දත්ත සමුදායට ඇතුළත් කරන්න.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader("AIP 2026 Excel ගොනුව තෝරන්න (.xlsx)", type=["xlsx"], key="admin_excel_upload")

            if uploaded_file is not None:
                try:
                    xls = pd.ExcelFile(uploaded_file)
                    st.info(f"📁 හඳුනාගත් ටැබ්: {', '.join(xls.sheet_names)}")

                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        sync_activities = st.checkbox("Data_Log (වැඩසටහන් දත්ත) ඇතුළත් කරන්න", value=True)
                    with col_u2:
                        sync_vouchers = st.checkbox("Voucher_Log (වවුචර් දත්ත) ඇතුළත් කරන්න", value=True)

                    if st.button("🚀 දත්ත Host Database එකට සුරකින්න (Start Import)", type="primary", use_container_width=True):
                        act_count = 0
                        vouch_count = 0

                        with st.spinner("දත්ත Database එක වෙත තැන්පත් වෙමින් පවතී..."):
                            # 1. Activities Import
                            if sync_activities and "Data_Log" in xls.sheet_names:
                                df_d = pd.read_excel(xls, "Data_Log")
                                for _, r in df_d.iterrows():
                                    cost = clean_float(r.get("වියදම"))
                                    act_name = clean_str(r.get("වැඩසටහන"))
                                    if act_name:
                                        u_name = clean_str(r.get("පරිශීලක")) or user.get("username", "super_admin")
                                        vote_no = clean_str(r.get("වැය ශීර්ෂය"))
                                        action_no = clean_str(r.get("Action No"))
                                        loc_val = clean_str(r.get("ස්ථානය"))
                                        act_date = str(r.get("දිනය.1") or r.get("දිනය") or "")[:10]
                                        ben_val = int(clean_float(r.get("ප්‍රතිලාභීන්")))
                                        est_val = clean_float(r.get("ඇස්තමේන්තුව"))

                                        if db.save_activity(u_name, vote_no, action_no, act_name, loc_val, act_date, ben_val, est_val, cost):
                                            act_count += 1

                            # 2. Vouchers Import
                            if sync_vouchers and "Voucher_Log" in xls.sheet_names:
                                df_v = pd.read_excel(xls, "Voucher_Log")
                                for _, r in df_v.iterrows():
                                    amt = clean_float(r.get("මුදල"))
                                    if amt > 0:
                                        u_name = clean_str(r.get("පරිශීලක")) or user.get("username", "super_admin")
                                        vote_no = clean_str(r.get("වැය ශීර්ෂය"))
                                        action_no = clean_str(r.get("Action No"))
                                        desc_val = clean_str(r.get("විස්තරය"))
                                        v_no = clean_str(r.get("වවුචර අංකය"))
                                        v_date = str(r.get("වවුචර දිනය") or "")[:10]

                                        if db.save_voucher(u_name, vote_no, action_no, desc_val, v_no, v_date, 0.0, amt):
                                            vouch_count += 1

                        st.success(f"✅ සාර්ථකයි! වැඩසටහන් {act_count} ක් සහ වවුචර් {vouch_count} ක් සාර්ථකව MySQL දත්ත සමුදායට එක් කරන ලදී.")
                        st.rerun()

                except Exception as e:
                    st.error(f"⚠️ Excel ගොනුව කියවීමේදී දෝෂයක් හටගත්තේය: {e}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 1. අවසර ලත් වැඩසටහන් ලබා ගැනීම
    # =========================================================================
    ref_df = db.get_reference_options(user)
    if ref_df.empty:
        st.error("⚠️ ඔබට අවසර ලත් වැඩසටහන් හෝ විෂයයන් හමු නොවීය.")
        return

    options = {
        f"#{r['action_no']} - {r['activity_name']} ({r.get('vote_number') or r.get('vote_code')})": (
            r['action_no'], r.get('vote_number') or r.get('vote_code')
        )
        for _, r in ref_df.iterrows()
    }

    # =========================================================================
    # 2. දත්ත ඇතුළත් කිරීමේ පෝරමය (Manual Entry Form)
    # =========================================================================
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

        act_name_val = row.get("act_name") or row.get("program_name") or row.get("activity_name") or "N/A"
        act_date_val = str(row.get("act_date") or row.get("held_date") or row.get("activity_date") or "N/A")[:10]
        vote_no_val = row.get("vote_no") or row.get("vote_number") or row.get("vote_code") or "N/A"
        loc_val = row.get("loc") or row.get("location") or "නොදක්වා ඇත"
        ben_val = row.get("ben") or row.get("beneficiaries_count") or 0
        cost_val = row.get("cost") or row.get("actual_expenditure") or row.get("actual_cost") or 0.0
        est_val = row.get("est") or row.get("estimated_amount") or row.get("estimated_cost") or 0.0

        card_html = (
            f'<div style="background-color: {bg_color}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">'
            f'<table style="width: 100%; border-collapse: collapse; border: none;">'
            f'<tr style="border: none;">'
            f'<td style="text-align: left; vertical-align: top; border: none;">'
            f'<strong style="color: #0f172a !important; font-size: 15px;">{act_name_val}</strong>'
            f'<span style="color: #64748b !important; font-size: 12px; margin-left: 8px;">({act_date_val})</span>'
            f'<div style="color: #334155 !important; font-size: 13px; margin-top: 4px;">'
            f'වැය ශීර්ෂය: <b>{vote_no_val}</b> | විෂය අංකය: <b>#{row.get("action_no", "N/A")}</b> | ස්ථානය: <b>{loc_val}</b> | ප්‍රතිලාභීන්: <b>{ben_val}</b>'
            f'</div>'
            + (f'<div style="color: #dc2626 !important; font-size: 12px; margin-top: 4px;"><b>⚠️ ඉවත් කිරීමට ඉල්ලුම් කර ඇත:</b> {row.get("delete_reason", "")}</div>' if is_del_pending else '') +
            f'</td>'
            f'<td style="text-align: right; vertical-align: top; border: none;">'
            f'<span style="font-size: 16px; font-weight: 800; color: #0f766e !important;">රු. {float(cost_val):,.2f}</span>'
            f'<div style="font-size: 11px; color: #64748b !important; margin-top: 2px;">ඇස්තමේන්තුව: රු. {float(est_val):,.2f}</div>'
            f'<div style="font-size: 11px; color: #94a3b8 !important;">ඇතුළත් කළේ: {row.get("username", "N/A")}</div>'
            f'</td>'
            f'</tr>'
            f'</table>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        col_btn1, col_btn2, col_btn3, _ = st.columns([1.2, 1.8, 1.8, 6])

        # 1. Edit Option (API Safe)
        with col_btn1:
            with st.popover("✏️ Edit"):
                with st.form(key=f"edit_act_{act_id}"):
                    st.write(f"**වැඩසටහන සංස්කරණය (#{row.get('action_no')})**")
                    e_name = st.text_input("වැඩසටහනේ නම", value=str(act_name_val))
                    e_loc = st.text_input("ස්ථානය", value=str(loc_val))
                    e_ben = st.number_input("ප්‍රතිලාභීන්", value=int(clean_float(ben_val)), step=1)
                    e_est = st.number_input("ඇස්තමේන්තුව (රු.)", value=float(clean_float(est_val)), step=500.0)
                    e_cost = st.number_input("සත්‍ය වියදම (රු.)", value=float(clean_float(cost_val)), step=500.0)
                    e_date = st.text_input("දිනය (YYYY-MM-DD)", value=str(act_date_val))

                    if st.form_submit_button("💾 සුරකින්න"):
                        try:
                            if hasattr(db, "update_activity"):
                                db.update_activity(act_id, e_name, e_loc, e_date, e_ben, e_est, e_cost)
                            st.toast("වැඩසටහන් විස්තර සාර්ථකව යාවත්කාලීන විය!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"යාවත්කාලීන කිරීමේ දෝෂයකි: {e}")

        # 2. Regular User - Delete Request
        if not is_super_admin:
            with col_btn2:
                if not is_del_pending:
                    with st.popover("⚠️ Delete Request"):
                        with st.form(key=f"del_act_form_{act_id}"):
                            reason = st.text_input("හේතුව", placeholder="වැරදි දත්තයක් ඇතුළත් විය")
                            if st.form_submit_button("ඉල්ලීම යවන්න"):
                                if reason.strip():
                                    try:
                                        if hasattr(db, "request_activity_delete"):
                                            db.request_activity_delete(act_id, reason.strip())
                                        st.toast("ඉල්ලීම Admin වෙත යොමු විය!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"ඉල්ලීම යැවීමේ දෝෂයකි: {e}")
                                else:
                                    st.error("කරුණාකර හේතුව දක්වන්න.")

        # 3. Super Admin - Approve / Reject Delete
        if is_super_admin and is_del_pending:
            with col_btn2:
                if st.button("🗑️ Approve Delete", key=f"app_d_act_{act_id}", type="primary"):
                    try:
                        if hasattr(db, "delete_activity_permanent"):
                            db.delete_activity_permanent(act_id)
                        st.toast("වැඩසටහන ස්ථිරවම මකා දමන ලදී!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"මැකීමේ දෝෂයකි: {e}")
            with col_btn3:
                if st.button("❌ Reject", key=f"rej_d_act_{act_id}"):
                    try:
                        if hasattr(db, "cancel_activity_delete_request"):
                            db.cancel_activity_delete_request(act_id)
                        st.toast("ඉල්ලීම ප්‍රතික්ෂේප විය.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"දෝෂයකි: {e}")

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
