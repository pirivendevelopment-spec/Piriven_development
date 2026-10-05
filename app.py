import streamlit as st
import sys
import os
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

st.set_page_config(
    page_title="පිරිවෙන් අංශයේ ප්‍රධාන කළමනාකරණ පෝටලය",
    page_icon="🏛️️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sub-script එකක් ආරක්ෂිතව ධාවනය කිරීමේ function එක
def run_sub_module(file_path):
    if not os.path.exists(file_path):
        st.error(f"⚠️ ගොනුව හමු නොවීය: {os.path.basename(file_path)}")
        return

    module_dir = os.path.dirname(file_path)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    # Current working directory අදාළ module ෆෝල්ඩරයට තාවකාලිකව මාරු කිරීම
    original_cwd = os.getcwd()
    try:
        os.chdir(module_dir)
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        # අතුරු පිටු තුළ නැවත st.set_page_config තිබේ නම් එයින් එන දෝෂය වැළැක්වීම
        # (Streamlit allow කරන්නේ මුල් පිටුවේදී එක් වරක් පමණි)
        cleaned_code = ""
        for line in code_content.splitlines(keepends=True):
            if "st.set_page_config(" in line:
                cleaned_code += "# " + line  # Comment out secondary page config
            else:
                cleaned_code += line

        exec(cleaned_code, {"__name__": "__main__", "__file__": file_path})
    except Exception as e:
        st.error(f"⚠️ මොඩියුලය ධාවනය කිරීමේදී දෝෂයක් මතුවිය:")
        st.code(traceback.format_exc())
    finally:
        os.chdir(original_cwd)

# URL Query Parameters පරීක්ෂා කිරීම
query_params = st.query_params
active_module = query_params.get("module", None)

# =========================================================================
# 1. ප්‍රධාන ඩෑෂ්බෝඩ් එක (NO IFRAME - NATIVE BOOTSTRAP)
# =========================================================================
if not active_module:
    st.markdown("""
<style>
[data-testid='stSidebar'] { display: none !important; }
header { visibility: hidden !important; }
footer { visibility: hidden !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.stApp {
    background-color: #f8fafc !important;
}
</style>
""", unsafe_allow_html=True)

    dashboard_html = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
.portal-wrap {
    background-color: #f8fafc;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding-bottom: 40px;
}
.header-section {
    background: linear-gradient(135deg, #0f766e, #115e59);
    color: white;
    padding: 35px 0;
    border-radius: 0 0 20px 20px;
    margin-bottom: 35px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    text-align: center;
}
.header-section h2 {
    font-weight: 700;
    font-size: 26px;
    margin-bottom: 6px;
    color: #ffffff;
}
.card-custom {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    height: 100%;
    border: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.card-custom:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.card-exam { border-top: 5px solid #2563eb; }
.card-fin { border-top: 5px solid #10b981; }
.card-census { border-top: 5px solid #8b5cf6; }
.card-board { border-top: 5px solid #f59e0b; }
.card-inv { border-top: 5px solid #ef4444; }
.card-peqi { border-top: 5px solid #06b6d4; }

.btn-portal {
    width: 100%;
    padding: 10px;
    font-weight: 700;
    border-radius: 10px;
    border: none;
    color: white !important;
    transition: opacity 0.2s;
    text-decoration: none !important;
    display: inline-block;
    text-align: center;
    font-size: 14px;
}
.btn-portal:hover {
    opacity: 0.9;
    color: white !important;
}
</style>

<div class="portal-wrap">
<div class="header-section">
<div class="container">
<h2><i class="fa-solid fa-landmark"></i> පිරිවෙන් අංශයේ ප්‍රධාන කළමනාකරණ පෝටලය</h2>
<p class="mb-0 text-light">අධ්‍යාපන අමාත්‍යාංශය - ශ්‍රී ලංකා | කේන්ද්‍රීය කළමනාකරණ මධ්‍යස්ථානය</p>
</div>
</div>

<div class="container">
<h4 class="mb-4 text-secondary fw-bold">🚀 පද්ධති මොඩියුල සහ කළමනාකරණ අංශ</h4>

<div class="row g-4">
<!-- 1. විභාග විශ්ලේෂණය -->
<div class="col-md-6 col-lg-4">
<div class="card-custom card-exam">
<div>
<h5><i class="fa-solid fa-chart-line text-primary"></i> 1. විභාග ප්‍රතිඵල විශ්ලේෂණය</h5>
<p class="text-muted small mt-2">පිරිවෙන් සාමාන්‍ය පෙළ විභාග ප්‍රතිඵල, Quality Score (QS) සහ කලාපීය ප්‍රගති ප්‍රස්තාර.</p>
</div>
<a href="?module=exam" target="_self" class="btn-portal mt-3" style="background-color: #2563eb;">විභාග විශ්ලේෂණයට පිවිසෙන්න</a>
</div>
</div>

<!-- 2. AIP මූල්‍ය පාලනය -->
<div class="col-md-6 col-lg-4">
<div class="card-custom card-fin">
<div>
<h5><i class="fa-solid fa-coins text-success"></i> 2. AIP මූල්‍ය හා ප්‍රගති පාලනය</h5>
<p class="text-muted small mt-2">ප්‍රාග්ධන සහ පුනරාවර්තන වැය ශීර්ෂ, වවුචර් ලොග් සහ මූල්‍ය ප්‍රගති වාර්තා.</p>
</div>
<a href="?module=aip" target="_self" class="btn-portal mt-3" style="background-color: #10b981;">මූල්‍ය පාලන පද්ධතියට පිවිසෙන්න</a>
</div>
</div>

<!-- 3. සංගණන දත්ත -->
<div class="col-md-6 col-lg-4">
<div class="card-custom card-census">
<div>
<h5><i class="fa-solid fa-users-rectangle" style="color: #8b5cf6;"></i> 3. පිරිවෙන් සංගණන දත්ත</h5>
<p class="text-muted small mt-2">පිරිවෙන් ආයතන, ගුරු මණ්ඩලය, පැවිදි/ගිහි ශිෂ්‍ය සංචිතය සහ දිස්ත්‍රික් වාර්තා.</p>
</div>
<a href="?module=census" target="_self" class="btn-portal mt-3" style="background-color: #8b5cf6;">සංගණන දත්ත වෙත පිවිසෙන්න</a>
</div>
</div>

<!-- 4. ඩිජිටල් බෝඩ් මොනිටරින් -->
<div class="col-md-6 col-lg-4">
<div class="card-custom card-board">
<div>
<h5><i class="fa-solid fa-desktop text-warning"></i> 4. ඩිජිටල් බෝඩ් මොනිටරින්</h5>
<p class="text-muted small mt-2">අමාත්‍යාංශ මට්ටමේ සජීවී සිතියම් ලුහුබැඳීම, විකාශන (Broadcast) සහ ටිකට් පද්ධතිය.</p>
</div>
<a href="?module=board" target="_self" class="btn-portal mt-3" style="background-color: #f59e0b;">අමාත්‍යාංශ මොනිටරින් වෙත පිවිසෙන්න</a>
</div>
</div>

<!-- 5. ඉන්වෙන්ට්‍රි පාලනය -->
<div class="col-md-6 col-lg-4">
<div class="card-custom card-inv">
<div>
<h5><i class="fa-solid fa-boxes-stacked text-danger"></i> 5. ඉන්වෙන්ට්‍රි සහ සම්පත් කළමනාකරණය</h5>
<p class="text-muted small mt-2">මූල්‍ය ප්‍රතිපාදන, බඩු වට්ටෝරු (පොදු 44), තොග පොත් (පොදු 198) සහ නිකුත් කිරීම්.</p>
</div>
<a href="?module=inventory" target="_self" class="btn-portal mt-3" style="background-color: #ef4444;">ඉන්වෙන්ට්‍රි පද්ධතියට පිවිසෙන්න</a>
</div>
</div>

<!-- 6. PEQI මොඩියුලය -->
<div class="col-md-6 col-lg-4">
<div class="card-custom card-peqi">
<div>
<h5><i class="fa-solid fa-clipboard-check text-info"></i> 6. පිරිවෙන් ප්‍රමිති (PEQI) ලකුණු</h5>
<p class="text-muted small mt-2">පිරිවෙන්වල ප්‍රමිති 10 සඳහා නව ලකුණු ඇතුළත් කිරීම, වාර 5 ලුහුබැඳීම සහ PDF වාර්තා.</p>
</div>
<a href="?module=peqi" target="_self" class="btn-portal mt-3" style="background-color: #06b6d4;">PEQI පද්ධතියට පිවිසෙන්න</a>
</div>
</div>
</div>

<footer class="text-center mt-5 mb-4 text-muted small">
<hr>
<p>© 2026 Piriven Development Branch | Ministry of Education - Sri Lanka</p>
</footer>
</div>
</div>
"""
    st.markdown(dashboard_html, unsafe_allow_html=True)

# =========================================================================
# 2. මොඩියුල පිටු
# =========================================================================
else:
    # ආපසු ප්‍රධාන Dashboard එකට යාමට Sidebar එකේ Button එක
    st.sidebar.markdown("""
<div style='padding-bottom: 12px; margin-bottom: 15px;'>
<a href="?" target="_self" style="text-decoration: none;">
<button style="
background: linear-gradient(135deg, #0f766e, #115e59);
color: white; border: none; padding: 10px 16px; border-radius: 8px;
font-weight: 700; width: 100%; cursor: pointer;">
⬅️ ප්‍රධාන පෝටලයට ආපසු
</button>
</a>
</div>
<hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 10px 0;">
""", unsafe_allow_html=True)

    # 1. විභාග ප්‍රතිඵල විශ්ලේෂණය
    if active_module == "exam":
        run_sub_module(os.path.join(BASE_DIR, "result_app.py"))

    # 2. AIP මූල්‍ය හා ප්‍රගති පාලනය
    elif active_module == "aip":
        aip_path = os.path.join(BASE_DIR, "aip_financial")
        if aip_path not in sys.path:
            sys.path.insert(0, aip_path)
        try:
            from aip_financial.modules import dashboard
            from aip_financial import db
            db.init_db()
            user = st.session_state.get("user", {
                "name": "ප්‍රධාන පරිපාලක", "role": "Super Admin",
                "access_level": "All", "username": "admin"
            })
            dashboard.render_dashboard(user)
        except Exception:
            st.error("AIP පද්ධතිය ධාවනය කිරීමේ දෝෂයකි:")
            st.code(traceback.format_exc())

    # 3. සංගණන දත්ත
    elif active_module == "census":
        st.title("👥 පිරිවෙන් සංගණන දත්ත පද්ධතිය")
        st.info("පද්ධතිය සූදානම් වෙමින් පවතී...")

    # 4. ඩිජිටල් බෝඩ්
    elif active_module == "board":
        b_file = os.path.join(BASE_DIR, "digital_boards", "app.py")
        if not os.path.exists(b_file):
            b_file = os.path.join(BASE_DIR, "digital_boards", "ministry_dashboard.py")
        run_sub_module(b_file)

    # 5. ඉන්වෙන්ට්‍රි
    elif active_module == "inventory":
        inv_file = os.path.join(BASE_DIR, "inventory_management", "app.py")
        if not os.path.exists(inv_file):
            inv_file = os.path.join(BASE_DIR, "inventory_management", "inventory_app.py")
        run_sub_module(inv_file)

    # 6. PEQI
    elif active_module == "peqi":
        p_file = os.path.join(BASE_DIR, "peqi_module", "app.py")
        if not os.path.exists(p_file):
            p_file = os.path.join(BASE_DIR, "peqi_module", "peqi_app.py")
        run_sub_module(p_file)
