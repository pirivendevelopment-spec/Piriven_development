import streamlit as st
import db

def render_activities(user):
    st.markdown("### 📋 වැඩසටහන් දත්ත ඇතුළත් කිරීම (Activity Entry)")

    ref_df = db.get_reference_options(user)
    if ref_df.empty:
        st.error("ඔබට අවසර ලත් වැඩසටහන් හමු නොවීය.")
        return

    options = {f"{r['activity_name']} ({r['vote_number']})": (r['action_no'], r['vote_number']) for _, r in ref_df.iterrows()}

    with st.form("act_form", clear_on_submit=True):
        sel_display = st.selectbox("වැඩසටහන හෝ විෂය (Action / Vote)", list(options.keys()))
        name = st.text_input("ක්‍රියාත්මක කළ නිශ්චිත වැඩසටහනේ නම")
        c1, c2 = st.columns(2)
        loc = c1.text_input("ස්ථානය")
        date = c2.date_input("පැවැත්වූ දිනය")
        c3, c4 = st.columns(2)
        ben = c3.number_input("ප්‍රතිලාභීන් සංඛ්‍යාව", min_value=0, step=1)
        est = c4.number_input("ඇස්තමේන්තුව (රු.)", min_value=0.0, step=0.01)
        cost = st.number_input("සත්‍ය වියදම (Actual Cost - රු.)", min_value=0.0, step=0.01)

        submitted = st.form_submit_button("දත්ත සුරකින්න", use_container_width=True)
        if submitted:
            if not name:
                st.error("කරුණාකර වැඩසටහනේ නම ඇතුළත් කරන්න.")
                return

            action_no, vote_no = options[sel_display]
            db.save_activity(user['username'], vote_no, action_no, name, loc, date, ben, est, cost)
            st.success(f"වැඩසටහන් දත්ත සාර්ථකව සුරකින ලදී! (Action No: {action_no})")