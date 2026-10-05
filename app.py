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
# 1. ප්‍රධාන ඩෑෂ්බෝඩ් එක (ඔබේ මුල් BOOTSTRAP DESIGN එක 100% ක්ම)
# =========================================================================
if st.session_state.active_module is None:

    # Bootstrap සහ මුල් CSS Styles
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        [data-testid='stSidebar'] { display: none !important; }
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            background-color: #f8fafc;
        }
        
        .header-section {
            background: linear-gradient(135deg, #0f766e, #115e59);
            color: white;
            padding: 30px 0;
            border-radius: 0 0 20px 20px;
            margin-bottom: 35px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }

        .card-custom {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            margin-bottom: 10px;
            min-height: 145px;
        }
        .card-exam { border-top: 5px solid #2563eb; }
        .card-fin { border-top: 5px solid #10b981; }
        .card-census { border-top: 5px solid #8b5cf6; }
        .card-board { border-top: 5px solid #f59e0b; }
        .card-inv { border-top: 5px solid #ef4444; }
        .card-peqi { border-top: 5px solid #06b6d4; }

        /* Streamlit Native Buttons Bootstrap විදියට හැඩගැන්වීම */
        div[data-testid="stButton"] > button {
            width: 100% !important;
            padding: 10px !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stButton"] > button:hover {
            opacity: 0.9 !important;
            transform: translateY(-2px) !important;
        }

        /* බොත්තම් සඳහා අදාළ පාට ලබා දීම */
        .btn-exam div[data-testid="stButton"] > button { background-color: #2563eb !important; }
        .btn-fin div[data-testid="stButton"] > button { background-color: #10b981 !important; }
        .btn-census div[data-testid="stButton"] > button { background-color: #8b5cf6 !important; }
        .btn-board div[data-testid="stButton"] > button { background-color: #f59e0b !important; }
        .btn-inv div[data-testid="stButton"] > button { background-color: #ef4444 !important; }
        .btn-peqi div[data-testid="stButton"] > button { background-color: #06b6d4 !important; }
    </style>

    <div class="header-section">
        <div class="container">
            <h2><i class="fa-solid fa-landmark"></i> පිරිවෙන් අංශයේ ප්‍රධාන කළමනාකරණ පෝටලය</h2>
            <p class="mb-0 text-light">අධ්‍යාපන අමාත්‍යාංශය - ශ්‍රී ලංකා | කේන්ද්‍රීය කළමනාකරණ මධ්‍යස්ථානය</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ප්‍රධාන Cards Container
    st.markdown('<div class="container"><h4 class="mb-4 text-secondary fw-bold">🚀 පද්ධති මොඩියුල සහ කළමනාකරණ අංශ</h4></div>', unsafe_allow_html=True)

    container = st.container()
    with container:
        # පේළිය 1
        col1, col2, col3 = st.columns(3, gap="medium")
        
        with col1:
            st.markdown("""
            <div class="card-custom card-exam">
                <h5><i class="fa-solid fa-chart-line text-primary"></i> 1. විභාග ප්‍රතිඵල විශ්ලේෂණය</h5>
                <p class="text-muted small mt-2">පිරිවෙන් සාමාන්‍ය පෙළ විභාග ප්‍රතිඵල, Quality Score (QS) සහ කලාපීය ප්‍රගති ප්‍රස්තාර.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="btn-exam">', unsafe_allow_html=True)
            if st.button("විභාග විශ්ලේෂණයට පිවිසෙන්න", key="btn_exam"):
                st.session_state.active_module = "exam"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="card-custom card-fin">
                <h5><i class="fa-solid fa-coins text-success"></i> 2. AIP මූල්‍ය හා ප්‍රගති පාලනය</h5>
                <p class="text-muted small mt-2">ප්‍රාග්ධන සහ පුනරාවර්තන වැය ශීර්ෂ, වවුචර් ලොග් සහ මූල්‍ය ප්‍රගති වාර්තා.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="btn-fin">', unsafe_allow_html=True)
            if st.button("මූල්‍ය පාලන පද්ධතියට පිවිසෙන්න", key="btn_aip"):
                st.session_state.active_module = "aip"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="card-custom card-census">
                <h5><i class="fa-solid fa-users-rectangle text-purple"></i> 3. පිරිවෙන් සංගණන දත්ත</h5>
                <p class="text-muted small mt-2">පිරිවෙන් ආයතන, ගුරු මණ්ඩලය, පැවිදි/ගිහි ශිෂ්‍ය සංචිතය සහ දිස්ත්‍රික් වාර්තා.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="btn-census">', unsafe_allow_html=True)
            if st.button("සංගණන දත්ත වෙත පිවිසෙන්න", key="btn_census"):
                st.session_state.active_module = "census"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

        # පේළිය 2
        col4, col5, col6 = st.columns(3, gap="medium")

        with col4:
            st.markdown("""
            <div class="card-custom card-board">
                <h5><i class="fa-solid fa-desktop text-warning"></i> 4. ඩිජිටල් බෝඩ් මොනිටරින්</h5>
                <p class="text-muted small mt-2">අමාත්‍යාංශ මට්ටමේ සජීවී සිතියම් ලුහුබැඳීම, විකාශන (Broadcast) සහ ටිකට් පද්ධතිය.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="btn-board">', unsafe_allow_html=True)
            if st.button("අමාත්‍යාංශ මොනිටරින් වෙත පිවිසෙන්න", key="btn_board"):
                st.session_state.active_module = "board"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col5:
            st.markdown("""
            <div class="card-custom card-inv">
                <h5><i class="fa-solid fa-boxes-stacked text-danger"></i> 5. ඉන්වෙන්ට්‍රි සහ සම්පත් කළමනාකරණය</h5>
                <p class="text-muted small mt-2">මූල්‍ය ප්‍රතිපාදන, බඩු වට්ටෝරු (පොදු 44), තොග පොත් (පොදු 198) සහ නිකුත් කිරීම්.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="btn-inv">', unsafe_allow_html=True)
            if st.button("ඉන්වෙන්ට්‍රි පද්ධතියට පිවිසෙන්න", key="btn_inv"):
                st.session_state.active_module = "inventory"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col6:
            st.markdown("""
            <div class="card-custom card-peqi">
                <h5><i class="fa-solid fa-clipboard-check text-info"></i> 6. පිරිවෙන් ප්‍රමිති (PEQI) ලකුණු</h5>
                <p class="text-muted small mt-2">පිරිවෙන්වල ප්‍රමිති 10 සඳහා නව ලකුණු ඇතුළත් කිරීම, වාර 5 ලුහුබැඳීම සහ PDF වාර්තා.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="btn-peqi">', unsafe_allow_html=True)
            if st.button("PEQI පද්ධතියට පිවිසෙන්න", key="btn_peqi"):
                st.session_state.active_module = "peqi"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <footer class="text-center mt-5 mb-4 text-muted small">
        <hr>
        <p>© 2026 Piriven Development Branch | Ministry of Education - Sri Lanka</p>
    </footer>
    """, unsafe_allow_html=True)

# =========================================================================
# 2. මොඩියුල පිටු (ක්ලික් කළ පසු ක්ෂණිකව විවෘත වන කොටස්)
# =========================================================================
else:
    # ආපසු ප්‍රධාන Dashboard එකට යාමට Button එක
    if st.sidebar.button("⬅️ ප්‍රධාන පෝටලයට ආපසු", use_container_width=True):
        st.session_state.active_module = None
        st.rerun()

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
