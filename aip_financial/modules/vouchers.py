import streamlit as st
import db

def render_vouchers(user):
    st.markdown("### 📝 වවුචර විස්තර ඇතුළත් කිරීම (Voucher Entry)")

    ref_df = db.get_reference_options(user)
    if ref_df.empty:
        st.error("ඔබට අවසර ලත් වැඩසටහන් හමු නොවීය.")
        return

    options = {f"{r['activity_name']} ({r['vote_number']})": (r['action_no'], r['vote_number']) for _, r in ref_df.iterrows()}

    with st.form("voucher_form", clear_on_submit=True):
        sel_display = st.selectbox("වැඩසටහන හෝ විෂය (Action / Vote)", list(options.keys()))
        desc = st.text_input("වැය විස්තරය")
        c1, c2 = st.columns(2)
        v_no = c1.text_input("වවුචර අංකය")
        v_date = c2.date_input("වවුචර දිනය")
        amount = st.number_input("මුදල (රු.)", min_value=0.01, step=0.01)

        submitted = st.form_submit_button("වවුචරය සුරකින්න", use_container_width=True)
        if submitted:
            if not v_no:
                st.error("කරුණාකර වවුචර අංකය ඇතුළත් කරන්න.")
                return

            action_no, vote_no = options[sel_display]
            db.save_voucher(user['username'], vote_no, action_no, desc, v_no, v_date, amount)
            st.success(f"වවුචරය සාර්ථකව සුරකින ලදී! (Action No: {action_no})")