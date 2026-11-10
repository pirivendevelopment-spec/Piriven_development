import streamlit as st
import pandas as pd
from datetime import datetime
# පැරණි import db වෙනුවට:
import aip_db as db

def render_vouchers(user):
    st.markdown("### 📝 වවුචර විස්තර ඇතුළත් කිරීම (Voucher Entry)")
    st.markdown("<p style='color: #64748b; font-size: 14px;'>අදාළ වැය ශීර්ෂය සහ ක්‍රියාකාරකම තෝරා නිකුත් කරන ලද ගෙවීම් වවුචර තොරතුරු මෙහි ඇතුළත් කරන්න.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 1. අවසර ලත් වැඩසටහන්/විෂයයන් ලබා ගැනීම
    ref_df = db.get_reference_options(user)
    if ref_df.empty:
        st.error("⚠️ ඔබට අවසර ලත් වැඩසටහන් හෝ වැය ශීර්ෂ හමු නොවීය.")
        return

    options = {
        f"#{r['action_no']} - {r['activity_name']} ({r['vote_number']})": (r['action_no'], r['vote_number']) 
        for _, r in ref_df.iterrows()
    }

    # 2. වවුචරය ඇතුළත් කිරීමේ පෝරමය
    with st.form("voucher_form", clear_on_submit=True):
        sel_display = st.selectbox("වැඩසටහන හෝ විෂය තෝරන්න (Action / Vote)", list(options.keys()))
        desc = st.text_input("වැය විස්තරය (Description)", placeholder="උදා: ගුරු දීමනා ගෙවීම් / ලිපිද්‍රව්‍ය මිලදී ගැනීම")
        
        c1, c2 = st.columns(2)
        v_no = c1.text_input("වවුචර අංකය (Voucher No)", placeholder="උදා: V/2026/045")
        v_date = c2.date_input("වවුචර දිනය (Voucher Date)", value=datetime.today())
        
        amount = st.number_input("මුදල (රු. Amount)", min_value=0.01, step=100.0, format="%.2f")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 වවුචරය සුරකින්න (Save Voucher)", use_container_width=True, type="primary")
        
        if submitted:
            if not v_no.strip():
                st.error("⚠️ කරුණාකර වවුචර අංකය ඇතුළත් කරන්න.")
            elif amount <= 0:
                st.error("⚠️ කරුණාකර වලංගු මුදලක් ඇතුළත් කරන්න.")
            else:
                action_no, vote_no = options[sel_display]
                try:
                    success = db.save_voucher(
                        user['username'], 
                        vote_no, 
                        action_no, 
                        desc.strip(), 
                        v_no.strip(), 
                        str(v_date), 
                        amount, # est_amount
                        amount  # actual amount
                    )
                    if success:
                        st.success(f"✅ වවුචරය සාර්ථකව MySQL දත්ත සමුදායේ තැන්පත් විය! (Action No: {action_no})")
                        st.rerun()
                    else:
                        st.error("⚠️ වවුචරය සුරැකීමේදී දෝෂයක් ඇති විය. කරුණාකර නැවත උත්සාහ කරන්න.")
                except Exception as e:
                    st.error(f"⚠️ දත්ත සමුදා දෝෂයකි: {e}")

    # =========================================================================
    # 3. මෑතකාලීන වවුචර ලැයිස්තුව හා කළමනාකරණය (Recent Vouchers Log)
    # =========================================================================
    st.markdown("<br><hr style='border-color: #cbd5e1;'>", unsafe_allow_html=True)
    st.markdown("#### 📜 මෑතකාලීන වවුචර ලැයිස්තුව (Recent Voucher Records)")

    vouchers_df = db.fetch_vouchers_from_cloud()
    
    if vouchers_df.empty:
        st.info("තවමත් කිසිදු වවුචරයක් ඇතුළත් කර නොමැත.")
        return

    # පරිශීලක අවසර අනුව පෙරීම
    is_super_admin = str(user.get("role", "")).lower() in ["super admin", "admin", "ප්‍රධාන පරිපාලක"]
    acc = user.get("access_level", "")
    user_access = [x.strip() for x in acc.split(',')] if acc and acc != "All" else []

    if not is_super_admin and acc != "All":
        if user_access:
            vouchers_df = vouchers_df[
                vouchers_df['action_no'].astype(str).isin(user_access) | 
                (vouchers_df['username'] == user.get('username'))
            ]
        else:
            vouchers_df = vouchers_df[vouchers_df['username'] == user.get('username')]

    if vouchers_df.empty:
        st.info("ඔබගේ විෂයට අදාළ මෑතකාලීන වවුචර කිසිවක් හමු නොවීය.")
        return

    # මෑතකාලීන වවුචර 15 ක් ප්‍රදර්ශනය කිරීම
    for _, row in vouchers_df.head(15).iterrows():
        v_id = row['id']
        is_del_pending = bool(row.get('delete_requested', 0) == 1)
        border_color = "#ef4444" if is_del_pending else "#cbd5e1"
        bg_color = "#fef2f2" if is_del_pending else "#ffffff"

        card_html = (
            f'<div style="background-color: {bg_color}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">'
            f'<table style="width: 100%; border-collapse: collapse; border: none;">'
            f'<tr style="border: none;">'
            f'<td style="text-align: left; vertical-align: top; border: none;">'
            f'<strong style="color: #0f172a !important; font-size: 15px;">වවුචර අංකය: {row.get("v_no", "N/A")}</strong>'
            f'<span style="color: #64748b !important; font-size: 12px; margin-left: 8px;">({str(row.get("v_date", "N/A"))[:10]})</span>'
            f'<div style="color: #334155 !important; font-size: 13.5px; margin-top: 4px;">'
            f'වැය ශීර්ෂය: <b>{row.get("vote_no", "N/A")}</b> | විෂය අංකය: <b>#{row.get("action_no", "N/A")}</b> | විස්තරය: {row.get("desc", "")}'
            f'</div>'
            + (f'<div style="color: #dc2626 !important; font-size: 12px; margin-top: 4px;"><b>⚠️ ඉවත් කිරීමට ඉල්ලුම් කර ඇත:</b> {row.get("delete_reason", "")}</div>' if is_del_pending else '') +
            f'</td>'
            f'<td style="text-align: right; vertical-align: top; border: none;">'
            f'<span style="font-size: 17px; font-weight: 800; color: #0f766e !important;">රු. {float(row.get("amount", 0)):,.2f}</span>'
            f'<div style="font-size: 11px; color: #94a3b8 !important; margin-top: 2px;">ඇතුළත් කළේ: {row.get("username", "N/A")}</div>'
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
                with st.form(key=f"edit_vouch_{v_id}"):
                    st.write(f"**වවුචරය සංස්කරණය (#{row.get('v_no')})**")
                    e_vno = st.text_input("වවුචර අංකය", value=str(row.get('v_no', '')))
                    e_desc = st.text_input("විස්තරය", value=str(row.get('desc', '')))
                    e_amount = st.number_input("මුදල (රු.)", value=float(row.get('amount', 0)), step=500.0)
                    e_date = st.text_input("දිනය (YYYY-MM-DD)", value=str(row.get('v_date', ''))[:10])

                    if st.form_submit_button("💾 සුරකින්න"):
                        db.update_voucher(v_id, row.get('vote_no'), row.get('action_no'), e_desc, e_vno, e_date, e_amount)
                        st.toast("වවුචරය සාර්ථකව සංස්කරණය කරන ලදී!")
                        st.rerun()

        # 2. Regular User - Delete Request
        if not is_super_admin:
            with col_btn2:
                if not is_del_pending:
                    with st.popover("⚠️ Delete Request"):
                        with st.form(key=f"del_vouch_form_{v_id}"):
                            reason = st.text_input("හේතුව", placeholder="දත්ත වැරදීමක් සිදුවිය")
                            if st.form_submit_button("ඉල්ලීම යවන්න"):
                                if reason.strip():
                                    db.request_voucher_delete(v_id, reason.strip())
                                    st.toast("ඉල්ලීම Admin වෙත යොමු විය!")
                                    st.rerun()
                                else:
                                    st.error("කරුණාකර හේතුව දක්වන්න.")

        # 3. Super Admin - Approve / Reject Delete
        if is_super_admin and is_del_pending:
            with col_btn2:
                if st.button("🗑️ Approve Delete", key=f"app_d_vouch_{v_id}", type="primary"):
                    db.delete_voucher_permanent(v_id)
                    st.toast("වවුචරය ස්ථිරවම මකා දමන ලදී!")
                    st.rerun()

            with col_btn3:
                if st.button("❌ Reject", key=f"rej_d_vouch_{v_id}"):
                    db.cancel_voucher_delete_request(v_id)
                    st.toast("ඉල්ලීම ප්‍රතික්ෂේප විය.")
                    st.rerun()

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
