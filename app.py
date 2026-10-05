import streamlit as st
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

# Active Module කළමනාකරණය
if "active_module" not in st.session_state:
    st.session_state.active_module = None

# =========================================================================
# 1. ප්‍රධාන ඩෑෂ්බෝඩ් එක
# =========================================================================
if st.session_state.active_module is None:

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap');
        
        * {
            font-family: 'Noto Sans Sinhala', 'Segoe UI', sans-serif !important;
        }
        .stApp {
            background-color: #f8fafc !important;
        }
        [data-testid='stSidebar'] { display: none !important; }
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        
        .block-container {
            padding: 0 2rem 3rem 2rem !important;
            max-width: 1280px !important;
            margin: auto !important;
        }

        /* Banner Header */
        .portal-header {
            background: linear-gradient(135deg, #0f766e, #115e59);
            color: white;
            padding: 30px 15px;
            border-radius: 0 0 22px 22px;
            margin: 0 -2rem 35px -2rem;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            text-align: center;
        }
        .portal-header h2 {
            font-size: 26px;
            font-weight: 800;
            margin: 0;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .portal-header p {
            margin: 6px 0 0 0;
            color: #ccfbf1;
            font-size: 13.5px;
        }

        .section-heading {
            color: #475569;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 25px;
        }

        /* Card Unified Box */
        .custom-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 22px 20px 12px 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            min-height: 145px;
            margin-bottom: 8px;
        }
        .border-exam { border-top: 5px solid #2563eb !important; }
        .border-fin { border-top: 5px solid #10b981 !important; }
        .border-census { border-top: 5px solid #8b5cf6 !important; }
        .border-board { border-top: 5px solid #f59e0b !important; }
        .border-inv { border-top: 5px solid #ef4444 !important; }
        .border-peqi { border-top: 5px solid #06b6d4 !important; }

        .c-title {
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 8px;
        }
        .c-desc {
            font-size: 12.5px;
            color: #64748b;
            line-height: 1.5;
            min-height: 48px;
            margin: 0;
        }

        /* Streamlit Native Buttons Exact Colors Override */
        div.stButton > button {
            width: 100% !important;
            padding: 11px !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            border-radius: 10px !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button:hover {
            opacity: 0.9 !important;
            transform: translateY(-2px) !important;
        }

        /* Buttons Styling with Precise Classes */
        .btn-exam button { background: #2563eb !important; }
        .btn-fin button { background: #10b981 !important; }
        .btn-census button { background: #8b5cf6 !important; }
        .btn-board button { background: #f59e0b !important; }
        .btn-inv button { background: #ef4444 !important; }
        .btn-peqi button { background: #06b6d4 !important; }
    </style>

    <!-- Header Section -->
    <div class="portal-header">
        <h2>🏛️ පිරිවෙන් අංශයේ ප්‍රධාන කළමනාකරණ පෝටලය</h2>
        <p>අධ්‍යාපන අමාත්‍යාංශය - ශ්‍රී ලංකා | කේන්ද්‍රීය කළමනාකරණ මධ්‍යස්ථානය</p>
    </div>

    <div class="section-heading">🚀 පද්ධති මොඩියුල සහ කළමනාකරණ අංශ</div>
    """, unsafe_allow_html=True)

    # පේළිය 1 (මොඩියුල 1, 2, 3)
    col1, col2, col3 = st.columns(3, gap="large")

    # 1. විභාග විශ්ලේෂණය
    with col1:
        st.markdown("""
        <div class="custom-card border-exam">
            <div class="c-title" style="color: #2563eb;">📈 1. විභාග ප්‍රතිඵල විශ්ලේෂණය</div>
            <p class="c-desc">පිරිවෙන් සාමාන්‍ය පෙළ විභාග ප්‍රතිඵල, Quality Score (QS) සහ කලාපීය ප්‍රගති ප්‍රස්තාර.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-exam">', unsafe_allow_html=True)
        if st.button("විභාග විශ්ලේෂණයට පිවිසෙන්න", key="btn_exam", use_container_width=True):
            st.session_state.active_module = "exam"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. AIP මූල්‍ය පාලනය
    with col2:
        st.markdown("""
        <div class="custom-card border-fin">
            <div class="c-title" style="color: #10b981;">💰 2. AIP මූල්‍ය හා ප්‍රගති පාලනය</div>
            <p class="c-desc">ප්‍රාග්ධන සහ පුනරාවර්තන වැය ශීර්ෂ, වවුචර් ලොග් සහ මූල්‍ය ප්‍රගති වාර්තා.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-fin">', unsafe_allow_html=True)
        if st.button("මූල්‍ය පාලන පද්ධතියට පිවිසෙන්න", key="btn_aip", use_container_width=True):
            st.session_state.active_module = "aip"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. සංගණන දත්ත
    with col3:
        st.markdown("""
        <div class="custom-card border-census">
            <div class="c-title" style="color: #8b5cf6;">👥 3. පිරිවෙන් සංගණන දත්ත</div>
            <p class="c-desc">පිරිවෙන් ආයතන, ගුරු මණ්ඩලය, පැවිදි/ගිහි ශිෂ්‍ය සංචිතය සහ දිස්ත්‍රික් වාර්තා.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-census">', unsafe_allow_html=True)
        if st.button("සංගණන දත්ත වෙත පිවිසෙන්න", key="btn_census", use_container_width=True):
            st.session_state.active_module = "census"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # පේළිය 2 (මොඩියුල 4, 5, 6)
    col4, col5, col6 = st.columns(3, gap="large")

    # 4. ඩිජිටල් බෝඩ් මොනිටරින්
    with col4:
        st.markdown("""
        <div class="custom-card border-board">
            <div class="c-title" style="color: #f59e0b;">🖥️ 4. ඩිජිටල් බෝඩ් මොනිටරින්</div>
            <p class="c-desc">අමාත්‍යාංශ මට්ටමේ සජීවී සිතියම් ලුහුබැඳීම, විකාශන (Broadcast) සහ ටිකට් පද්ධතිය.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-board">', unsafe_allow_html=True)
        if st.button("අමාත්‍යාංශ මොනිටරින් වෙත පිවිසෙන්න", key="btn_board", use_container_width=True):
            st.session_state.active_module = "board"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. ඉන්වෙන්ට්‍රි පාලනය
    with col5:
        st.markdown("""
        <div class="custom-card border-inv">
            <div class="c-title" style="color: #ef4444;">📦 5. ඉන්වෙන්ට්‍රි සහ සම්පත් කළමනාකරණය</div>
            <p class="c-desc">මූල්‍ය ප්‍රතිපාදන, බඩු වට්ටෝරු (පොදු 44), තොග පොත් (පොදු 198) සහ නිකුත් කිරීම්.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-inv">', unsafe_allow_html=True)
        if st.button("ඉන්වෙන්ට්‍රි පද්ධතියට පිවිසෙන්න", key="btn_inv", use_container_width=True):
            st.session_state.active_module = "inventory"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 6. PEQI මොඩියුලය
    with col6:
        st.markdown("""
        <div class="custom-card border-peqi">
            <div class="c-title" style="color: #06b6d4;">☑️ 6. පිරිවෙන් ප්‍රමිති (PEQI) ලකුණු</div>
            <p class="c-desc">පිරිවෙන්වල ප්‍රමිති 10 සඳහා නව ලකුණු ඇතුළත් කිරීම, වාර 5 ලුහුබැඳීම සහ PDF වාර්තා.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-peqi">', unsafe_allow_html=True)
        if st.button("PEQI පද්ධතියට පිවිසෙන්න", key="btn_peqi", use_container_width=True):
            st.session_state.active_module = "peqi"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <footer style="text-align: center; margin-top: 45px; padding: 20px 0; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 13px;">
        © 2026 Piriven Development Branch | Ministry of Education - Sri Lanka
    </footer>
    """, unsafe_allow_html=True)

# =========================================================================
# 2. මොඩියුල පිටු
# =========================================================================
else:
    # ආපසු ප්‍රධාන Dashboard එකට යාමට Button එක
    st.sidebar.markdown("""
    <div style='padding-bottom: 8px;'>
        <h4 style='color: #0f766e; font-weight: 800; margin: 0;'>🏛️ පිරිවෙන් පෝටලය</h4>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("⬅️ ප්‍රධාන පෝටලයට ආපසු", use_container_width=True):
        st.session_state.active_module = None
        st.rerun()

    st.sidebar.markdown("<hr style='border: 0.5px solid rgba(0,0,0,0.1); margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

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
