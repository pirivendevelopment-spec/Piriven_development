import streamlit as st
import sys
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

st.set_page_config(
    page_title="පිරිවෙන් අංශයේ ප්‍රධාන කළමනාකරණ පෝටලය",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# URL Query Parameters පරීක්ෂා කිරීම
query_params = st.query_params
active_module = query_params.get("module", None)

# =========================================================================
# 1. ප්‍රධාන ඩෑෂ්බෝඩ් එක (NO IFRAME - 100% NATIVE BOOTSTRAP DESIGN)
# =========================================================================
if not active_module:
    # Sidebar සැඟවීම සහ Full-screen CSS
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

    # Markdown Code Block වැළැක්වීමට සෑම පේළියක්ම වම් කෙළවරෙන්ම (No Indentation) සකසා ඇත
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
<p class
