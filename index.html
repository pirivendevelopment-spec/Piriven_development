import streamlit as st
import streamlit.components.v1 as components
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

st.set_page_config(
    page_title="පිරිවෙන් අංශයේ ප්‍රධාන කළමනාකරණ පෝටලය",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Active Module State එක කළමනාකරණය
if "active_module" not in st.session_state:
    st.session_state.active_module = None

# URL Query Parameter එකක් පැමිණ ඇත්නම් එයට මුල්තැන දීම
try:
    param_module = st.query_params.get("module")
except Exception:
    params = st.experimental_get_query_params()
    param_module = params.get("module", [None])[0]

if param_module and st.session_state.active_module is None:
    st.session_state.active_module = param_module

# =========================================================================
# 0. ප්‍රධාන ඩෑෂ්බෝඩ් එක (INDEX.HTML)
# =========================================================================
if not st.session_state.active_module:
    st.markdown("""
    <style>
        [data-testid='stSidebar'] { display: none !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
    </style>
    """, unsafe_allow_html=True)

    html_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # HTML Component එකෙන් User Click කළ Module එක ලබාගැනීම
        clicked_module = components.html(html_content, height=1000, scrolling=True)

        if clicked_module and clicked_module != st.session_state.active_module:
            st.session_state.active_module = clicked_module
            st.rerun()
    else:
        st.error("⚠️ index.html ගොනුව හමු නොවීය!")

# =========================================================================
# මොඩියුල පිටු (AIP ඇතුළු අනෙකුත් සියල්ල)
# =========================================================================
else:
    # ආපසු ප්‍රධාන Dashboard එකට යාමට Native Streamlit Button
    if st.sidebar.button("⬅️ ප්‍රධාන පෝටලයට ආපසු", use_container_width=True):
        st.session_state.active_module = None
        try:
            st.query_params.clear()
        except Exception:
            st.experimental_set_query_params()
        st.rerun()

    st.sidebar.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 10px 0;'>", unsafe_allow_html=True)

    # 1. විභාග ප්‍රතිඵල විශ්ලේෂණය
    if st.session_state.active_module == "exam":
        exam_path = os.path.join(BASE_DIR, "result_app.py")
        if os.path.exists(exam_path):
            with open(exam_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.warning("result_app.py ගොනුව හමු නොවීය.")

    # 2. AIP මූල්‍ය හා ප්‍රගති පාලනය
    elif st.session_state.active_module == "aip":
        aip_path = os.path.join(BASE_DIR, "aip_financial")
        if aip_path not in sys.path:
            sys.path.append(aip_path)
        try:
            from aip_financial.modules import dashboard
            from aip_financial import db
            db.init_db()
            user = st.session_state.get("user", {
                "name": "ප්‍රධාන පරිපාලක", "role": "Super Admin",
                "access_level": "All", "username": "admin"
            })
            dashboard.render_dashboard(user)
        except Exception as e:
            st.error(f"AIP මූල්‍ය පද්ධතිය පූරණය කිරීමේ දෝෂයකි: {e}")

    # 3. සංගණන දත්ත
    elif st.session_state.active_module == "census":
        st.title("👥 පිරිවෙන් සංගණන දත්ත පද්ධතිය")
        st.info("පද්ධතිය සූදානම් වෙමින් පවතී...")

    # 4. ඩිජිටල් බෝඩ්
    elif st.session_state.active_module == "board":
        b_path = os.path.join(BASE_DIR, "digital_boards", "app.py")
        if not os.path.exists(b_path):
            b_path = os.path.join(BASE_DIR, "digital_boards", "ministry_dashboard.py")
        if os.path.exists(b_path):
            with open(b_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.info("ඩිජිටල් බෝඩ් පද්ධතිය සූදානම් වෙමින් පවතී...")

    # 5. ඉන්වෙන්ට්‍රි
    elif st.session_state.active_module == "inventory":
        i_path = os.path.join(BASE_DIR, "inventory_management", "app.py")
        if not os.path.exists(i_path):
            i_path = os.path.join(BASE_DIR, "inventory_management", "inventory_app.py")
        if os.path.exists(i_path):
            with open(i_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.info("ඉන්වෙන්ට්‍රි පද්ධතිය සූදානම් වෙමින් පවතී...")

    # 6. PEQI
    elif st.session_state.active_module == "peqi":
        p_path = os.path.join(BASE_DIR, "peqi_module", "app.py")
        if not os.path.exists(p_path):
            p_path = os.path.join(BASE_DIR, "peqi_module", "peqi_app.py")
        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.info("PEQI පද්ධතිය සූදානම් වෙමින් පවතී...")
