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

# Streamlit URL Query Parameters ලබා ගැනීම
try:
    module = st.query_params.get("module")
except Exception:
    params = st.experimental_get_query_params()
    module = params.get("module", [None])[0]

# =========================================================================
# 0. ප්‍රධාන ඩෑෂ්බෝඩ් එක (INDEX.HTML මුල් Bootstrap Design එකම පෙන්වීම)
# =========================================================================
if not module:
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
        components.html(html_content, height=950, scrolling=True)
    else:
        st.error("⚠️ index.html ගොනුව හමු නොවීය!")

# =========================================================================
# මොඩියුල පිටු (AIP ඇතුළු අනෙකුත් සියල්ල)
# =========================================================================
else:
    # ආපසු ප්‍රධාන Dashboard එකට යාමට Button එක
    st.sidebar.markdown("""
    <div style='padding-bottom: 12px; margin-bottom: 15px;'>
        <a href="?" target="_top" style="text-decoration: none;">
            <button style="
                background: linear-gradient(135deg, #0f766e, #115e59);
                color: white; border: none; padding: 11px 16px; border-radius: 8px;
                font-weight: 700; width: 100%; cursor: pointer; font-size: 14px;">
                ⬅️ ප්‍රධාන පෝටලයට ආපසු
            </button>
        </a>
    </div>
    <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 10px 0;">
    """, unsafe_allow_html=True)

    # 1. විභාග ප්‍රතිඵල විශ්ලේෂණය
    if module == "exam":
        exam_path = os.path.join(BASE_DIR, "result_app.py")
        if os.path.exists(exam_path):
            with open(exam_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.warning("result_app.py ගොනුව හමු නොවීය.")

    # 2. AIP මූල්‍ය හා ප්‍රගති පාලනය
    elif module == "aip":
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
    elif module == "census":
        st.title("👥 පිරිවෙන් සංගණන දත්ත පද්ධතිය")
        st.info("පද්ධතිය සූදානම් වෙමින් පවතී...")

    # 4. ඩිජිටල් බෝඩ්
    elif module == "board":
        b_path = os.path.join(BASE_DIR, "digital_boards", "app.py")
        if not os.path.exists(b_path):
            b_path = os.path.join(BASE_DIR, "digital_boards", "ministry_dashboard.py")
        if os.path.exists(b_path):
            with open(b_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.info("ඩිජිටල් බෝඩ් පද්ධතිය සූදානම් වෙමින් පවතී...")

    # 5. ඉන්වෙන්ට්‍රි
    elif module == "inventory":
        i_path = os.path.join(BASE_DIR, "inventory_management", "app.py")
        if not os.path.exists(i_path):
            i_path = os.path.join(BASE_DIR, "inventory_management", "inventory_app.py")
        if os.path.exists(i_path):
            with open(i_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.info("ඉන්වෙන්ට්‍රි පද්ධතිය සූදානම් වෙමින් පවතී...")

    # 6. PEQI
    elif module == "peqi":
        p_path = os.path.join(BASE_DIR, "peqi_module", "app.py")
        if not os.path.exists(p_path):
            p_path = os.path.join(BASE_DIR, "peqi_module", "peqi_app.py")
        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                exec(f.read(), {"__name__": "__main__"})
        else:
            st.info("PEQI පද්ධතිය සූදානම් වෙමින් පවතී...")