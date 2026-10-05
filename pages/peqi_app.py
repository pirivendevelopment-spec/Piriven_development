import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
import matplotlib.pyplot as plt
import io
import base64

st.set_page_config(page_title="PEQI - පිරිවෙන් ගුණාත්මක දර්ශකය", layout="wide")

# --- Dark Modern Theme CSS ---
st.markdown("""
    <style>
        .main, .stApp {
            background-color: #0b0f19 !important;
            color: #f8fafc !important;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            color: #ffffff !important;
        }
        .stTextInput input, .stNumberInput input, .stSelectbox select {
            background-color: #1f2937 !important;
            color: white !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
        }
        
        /* සාමාන්‍ය බටන් සඳහා */
        .stButton>button { 
            width: 100% !important;
            border-radius: 8px !important;
            font-weight: bold !important; 
            background-color: #0f766e !important; 
            color: #ffffff !important; 
            border: none !important;
            padding: 10px 20px !important;
        }
        .stButton>button:hover { 
            background-color: #115e59 !important; 
        }

        /* 🔐 ලොගින් ෆෝම් එකේ සබ්මිට් බටන් එක සඳහා විශේෂ වර්ණ සැකසුම (පැහැදිලිව පෙනෙන පරිදි) */
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #0f766e !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: bold !important;
            width: 100% !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #115e59 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 📂 Excel සහ Database කළමනාකරණය ---
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_file_path = os.path.join(current_dir, "Piriven_name.xlsx")
if not os.path.exists(excel_file_path):
    excel_file_path = os.path.join(os.path.dirname(current_dir), "Piriven_name.xlsx")

DB_FILE = os.path.join(current_dir, "peqi_database.csv")
CRED_FILE = os.path.join(current_dir, "piriven_passwords.csv")

master_df = None
users_df = None
census_to_info = {}

if os.path.exists(excel_file_path):
    try:
        xls = pd.ExcelFile(excel_file_path)
        if "Pirivena_Master" in xls.sheet_names:
            master_df = pd.read_excel(excel_file_path, sheet_name="Pirivena_Master")
            master_df.columns = master_df.columns.str.strip()
            master_df["Census_No_Clean"] = master_df["Census_No"].fillna("").astype(str).str.strip().apply(lambda x: x.split('.')[0] if '.' in x else x)
            
            for _, r in master_df.iterrows():
                c_clean = str(r["Census_No_Clean"])
                p_name = str(r["NAME OF THE PIRIVENA"])
                census_to_info[c_clean] = {
                    "census": c_clean,
                    "name": p_name,
                    "district": str(r.get("DISTRICT", "")),
                    "zone": str(r.get("EDU ZONE", "")),
                    "division": str(r.get("EDU DIVISION", "")),
                    "type": str(r.get("PIRIVEN TYPE", "MULIKA"))
                }

        if "Users" in xls.sheet_names:
            users_df = pd.read_excel(excel_file_path, sheet_name="Users")
            users_df.columns = users_df.columns.str.strip()
    except Exception as e:
        st.error(f"⚠️ Excel ගොනු දෝෂයකි: {e}")

# --- 🔐 Login & State Setup ---
if "peqi_logged_in" not in st.session_state: st.session_state.peqi_logged_in = False
if "peqi_user_census" not in st.session_state: st.session_state.peqi_user_census = ""
if "peqi_user_name" not in st.session_state: st.session_state.peqi_user_name = ""
if "peqi_role" not in st.session_state: st.session_state.peqi_role = ""
if "force_password_change" not in st.session_state: st.session_state.force_password_change = False

pass_db = {}
if os.path.exists(CRED_FILE):
    df_pass = pd.read_csv(CRED_FILE)
    for _, row in df_pass.iterrows():
        pass_db[str(row["Census"]).strip()] = str(row["Password"]).strip()

# --- 1. 🔐 LOGIN SCREEN ---
if not st.session_state.peqi_logged_in:
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    # 🛠️ මුල් පිටුවට යාම සඳහා නිවැරදි HTML බටන් එක (Path error එක මඟහරවා ගැනීමට)
    st.markdown("""
    <div style="text-align: right; margin-bottom: 15px;">
        <a href="http://localhost:8000" target="_self" style="background-color: #1f2937; color: #38bdf8; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; border: 1px solid #374151; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            🏠 මුල් පිටුවට (Main Dashboard)
        </a>
    </div>
""", unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        with st.form("login_screen_form"):
            st.markdown("<h3 style='color: #38bdf8; text-align: center;'>🏛️ පිරිවෙන් PEQI ද්වාරය</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 13px;'>පිරිවෙන් සංගණන අංකය (Census No) හෝ පරිපාලක නාමය ලබා දෙන්න.</p>", unsafe_allow_html=True)
            
            uid = st.text_input("👤 සංගණන අංකය / පරිශීලක නාමය:")
            upass = st.text_input("🔑 මුරපදය (Password):", type="password")
            
            sub = st.form_submit_button("පද්ධතියට ඇතුල් වන්න 🔓")
            if sub:
                success = False
                if users_df is not None:
                    for _, u in users_df.iterrows():
                        if str(u.get('Username')).strip() == uid.strip() and str(u.get('Password')).strip() == upass.strip():
                            st.session_state.peqi_logged_in = True
                            st.session_state.peqi_user_census = "ADMIN"
                            st.session_state.peqi_user_name = str(u.get('Name', 'Admin'))
                            st.session_state.peqi_role = "Admin"
                            success = True
                            break
                
                if not success and uid.strip() in census_to_info:
                    default_pass = uid.strip()
                    actual_pass = pass_db.get(uid.strip(), default_pass)
                    
                    if upass.strip() == actual_pass:
                        st.session_state.peqi_logged_in = True
                        st.session_state.peqi_user_census = uid.strip()
                        st.session_state.peqi_user_name = census_to_info[uid.strip()]["name"]
                        st.session_state.peqi_role = "Pirivena"
                        if uid.strip() not in pass_db:
                            st.session_state.force_password_change = True
                        success = True
                
                if success:
                    st.success("✅ ප්‍රවේශය සාර්ථකයි!")
                    st.rerun()
                else:
                    st.error("⚠️ වැරදි පරිශීලක නාමයක් හෝ මුරපදයක්!")
    st.stop()

# --- 2. 🔑 පාස්වර්ඩ් වෙනස් කිරීම ---
if st.session_state.force_password_change:
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    c_p1, c_p2, c_p3 = st.columns([1, 1.5, 1])
    with c_p2:
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        st.warning("⚠️ ඔබ පළමු වතාවට පද්ධතියට පිවිස ඇත. ආරක්ෂාව සඳහා කරුණාකර ඔබේ නව මුරපදය සකසා ගන්න.")
        with st.form("change_pass_form"):
            new_p1 = st.text_input("නව මුරපදය (New Password):", type="password")
            new_p2 = st.text_input("නව මුරපදය තහවුරු කරන්න (Confirm Password):", type="password")
            ch_sub = st.form_submit_button("මුරපදය යාවත්කාලීන කරන්න 🔒")
            
            if ch_sub:
                if new_p1.strip() and new_p1 == new_p2:
                    c_num = st.session_state.peqi_user_census
                    new_row = {"Census": c_num, "Password": new_p1.strip()}
                    if os.path.exists(CRED_FILE):
                        df_c = pd.read_csv(CRED_FILE)
                        df_c = df_c[df_c["Census"].astype(str) != str(c_num)]
                        df_c = pd.concat([df_c, pd.DataFrame([new_row])], ignore_index=True)
                    else:
                        df_c = pd.DataFrame([new_row])
                    df_c.to_csv(CRED_FILE, index=False)
                    st.session_state.force_password_change = False
                    st.success("✅ මුරපදය සාර්ථකව වෙනස් කරන ලදී!")
                    st.rerun()
                else:
                    st.error("⚠️ මුරපද නොගැලපේ හෝ හිස්ව ඇත.")
    st.stop()

# --- 3. 🖥️ ප්‍රධාන ඩෑෂ්බෝඩ් තිරය ---
with st.sidebar:
    # සයිඩ්බාර් එකේ මුල් පිටුවට යාමට HTML ලින්ක් එකක් හෝ markdown භාවිත කළ හැක
    st.markdown("""
    <div style="text-align: right; margin-bottom: 15px;">
        <a href="http://localhost:8000" target="_self" style="background-color: #1f2937; color: #38bdf8; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; border: 1px solid #374151; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            🏠 මුල් පිටුවට (Main Dashboard)
        </a>
    </div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"🏛️ **ආයතනය / නම:**\n{st.session_state.peqi_user_name}")
    st.markdown(f"👤 **තනතුර:** {st.session_state.peqi_role}")
    st.markdown("---")
    if st.button("🚪 ඉවත් වන්න (Logout)"):
        st.session_state.peqi_logged_in = False
        st.session_state.peqi_user_census = ""
        st.rerun()

st.markdown("## 📊 පිරිවෙන් අධ්‍යාපන ගුණාත්මක දර්ශකය (PEQI)")
st.markdown("---")

tab_new, tab_search = st.tabs(["📝 නව ඇගයීමක් ඇතුළත් කිරීම", "🔍 ගබඩා කළ දත්ත සහ වාර්තා"])

standards_list = [
    "01. සිසු ආකල්ප සංවර්ධනය",
    "02. ගුණාත්මක පිරිවෙන් සිසු නිපුණතා",
    "03. ශිෂ්‍ය සාධනය හා ඵලදායිතා ප්‍රතිඵල",
    "04. ඉගෙනුම, ඉගැන්වීම, ඇගයීම සහ ගුරු වෘත්තීය කුසලතා සංවර්ධනය",
    "05. විධිමත් විෂයමාලා කළමනාකරණය",
    "06. විෂය සමගාමී කටයුතු",
    "07. ශිෂ්‍ය සුබසාධනය",
    "08. නායකත්වය හා කළමනාකරණය",
    "09. භෞතික සම්පත් කළමනාකරණය",
    "10. පිරිවෙන හා ප්‍රජාව"
]

def generate_matplotlib_donut(df_summary):
    fig, ax = plt.subplots(figsize=(5, 4))
    cmap = plt.get_cmap("YlGnBu")
    colors = [cmap(i / len(df_summary)) for i in range(len(df_summary))]
    
    wedges, texts, autotexts = ax.pie(
        df_summary["Percentage"], 
        labels=[s.split('.')[0] for s in df_summary["Standard"]], 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=colors, 
        wedgeprops=dict(width=0.4, edgecolor='w')
    )
    
    plt.setp(autotexts, size=7, weight="bold")
    plt.setp(texts, size=7)
    ax.set_title("PEQI Standards Performance", fontsize=10, weight="bold")
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight', dpi=150)
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    return f'<img src="data:image/png;base64,{img_b64}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />'

def render_report_html(p_name, census_no, district, zone, term, overall_peqi, results_summary, internal_notes, external_notes, recommendations, is_admin_user):
    df_sum = pd.DataFrame(results_summary)
    donut_img_tag = generate_matplotlib_donut(df_sum)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>PEQI Report - {p_name}</title>
        <style>
            body {{ background-color: #ffffff; color: #000000; font-family: 'Segoe UI', Tahoma, sans-serif; padding: 20px; }}
            .report-container {{ max-width: 800px; margin: 0 auto; padding: 30px; border: 1px solid #d1d5db; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <h2 style="color: #0f766e; border-bottom: 2px solid #0f766e; padding-bottom: 8px; margin-top: 0; font-size: 18px;">PIRIVEN EDUCATION QUALITY INDEX (PEQI) - OFFICIAL REPORT</h2>
            <p style="font-size: 13px; margin: 5px 0;"><b>පිරිවෙනේ නම / Pirivena:</b> {p_name} | <b>සංගණන අංකය / Census No:</b> {census_no}</p>
            <p style="font-size: 13px; margin: 5px 0;"><b>දිස්ත්‍රික්කය / District:</b> {district} | <b>කලාපය / Zone:</b> {zone} | <b>අධීක්ෂණ වාරය / Term:</b> {term}</p>
            <p style="font-size: 15px; margin: 10px 0; color: #047857;"><b>සමස්ත PEQI අගය / Overall PEQI Score: {overall_peqi:.2f}%</b></p>
            
            <hr style="border: 0; border-top: 1px solid #d1d5db; margin: 15px 0;">
            
            <h3 style="color: #1f2937; font-size: 15px; text-align: center;">ප්‍රමිතිකානුකූල කාර්යසාධන ඩෝනට් ප්‍රස්තාරය</h3>
            <div style="text-align: center; margin: 10px 0;">
                {donut_img_tag}
            </div>
            
            <h3 style="color: #1f2937; font-size: 15px; margin-top: 20px;">ප්‍රමිති සාරාංශය (Standards Summary):</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 8px;">
                <tr style="background-color: #f3f4f6; text-align: left;">
                    <th style="padding: 6px; border: 1px solid #d1d5db; font-size: 12px;">ප්‍රමිතිය (Standard)</th>
                    <th style="padding: 6px; border: 1px solid #d1d5db; font-size: 12px; text-align: center;">ලබාගත් / උපරිම</th>
                    <th style="padding: 6px; border: 1px solid #d1d5db; font-size: 12px; text-align: center;">ප්‍රතිශතය (%)</th>
                </tr>
    """
    for item in results_summary:
        html += f"""
                <tr>
                    <td style="padding: 6px; border: 1px solid #d1d5db; font-size: 12px;">{item['Standard']}</td>
                    <td style="padding: 6px; border: 1px solid #d1d5db; font-size: 12px; text-align: center;">{item['Obtained']} / {item['Maximum']}</td>
                    <td style="padding: 6px; border: 1px solid #d1d5db; font-size: 12px; text-align: center; font-weight: bold; color: #0f766e;">{item['Percentage']}%</td>
                </tr>
        """
    
    html += f"""
            </table>
            
            <h3 style="color: #1f2937; font-size: 15px; margin-top: 20px;">අභ්‍යන්තර අධීක්ෂණ සටහන් (පිරිවෙනේ සටහන):</h3>
            <p style="background-color: #f9fafb; padding: 10px; border-radius: 6px; border: 1px solid #e5e7eb; font-size: 12px;">{internal_notes if internal_notes else 'අභ්‍යන්තර සටහන් කිසිවක් ඇතුළත් කර නැත.'}</p>
    """
    
    if is_admin_user:
        html += f"""
            <h3 style="color: #1f2937; font-size: 15px; margin-top: 20px;">බාහිර අධීක්ෂණ සටහන් (අධීක්ෂණ නිලධාරීන්ගේ සටහන):</h3>
            <p style="background-color: #ecfdf5; padding: 10px; border-radius: 6px; border: 1px solid #a7f3d0; font-size: 12px;">{external_notes if external_notes else 'බාහිර අධීක්ෂණ සටහන් කිසිවක් ඇතුළත් කර නැත.'}</p>
        """
        
    html += f"""
            <h3 style="color: #1f2937; font-size: 15px; margin-top: 20px;">සංවර්ධන යෝජනා සහ ක්‍රියාමාර්ග:</h3>
            <ul style="padding-left: 20px; font-size: 12px;">
    """
    for rec in recommendations:
        html += f"<li style='margin-bottom: 5px;'>{rec}</li>"
        
    html += f"""
            </ul>
            
            <div style="margin-top: 40px; display: flex; justify-content: space-between;">
                <div style="width: 45%; border-top: 1px solid #000000; padding-top: 6px; text-align: center;">
                    <p style="margin: 0; font-size: 12px;">......................................................</p>
                    <p style="margin: 2px 0; font-size: 12px; font-weight: bold;">පරිවේණාධිපති / ආයතනාධිපති අත්සන</p>
                    <p style="margin: 0; font-size: 10px;">දිනය: .......................... නිල මුද්‍රාව</p>
                </div>
                <div style="width: 45%; border-top: 1px solid #000000; padding-top: 6px; text-align: center;">
                    <p style="margin: 0; font-size: 12px;">......................................................</p>
                    <p style="margin: 2px 0; font-size: 12px; font-weight: bold;">බාහිර අධීක්ෂණ නිලධාරී අත්සන</p>
                    <p style="margin: 0; font-size: 10px;">නම / තනතුර: .................................</p>
                    <p style="margin: 0; font-size: 10px;">දිනය: ..........................</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

with tab_new:
    is_admin = (st.session_state.peqi_role == "Admin")
    default_census = st.session_state.peqi_user_census if not is_admin else ""
    
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c1:
        if is_admin:
            input_census = st.text_input("🔢 සංගණන අංකය (Census No):", placeholder="උදා: 416013")
        else:
            input_census = st.text_input("🔢 සංගණන අංකය (Census No):", value=default_census, disabled=True)
    
    matched_data = {"census": "", "name": "", "district": "-", "zone": "-", "division": "-", "type": "MULIKA"}
    target_census = input_census if is_admin else default_census
    
    if target_census.strip():
        c_clean = target_census.strip().split('.')[0]
        if c_clean in census_to_info:
            matched_data = census_to_info[c_clean]

    with col_c2:
        piriven_display_name = st.text_input("🏛️ පිරිවෙනේ නම:", value=matched_data["name"], disabled=not is_admin)
    with col_c3:
        evaluation_term = st.selectbox("📅 අධීක්ෂණ වාරය:", [
            "1 වන අධීක්ෂණ වාරය", 
            "2 වන අධීක්ෂණ වාරය", 
            "3 වන අධීක්ෂණ වාරය", 
            "4 වන අධීක්ෂණ වාරය", 
            "5 වන අධීක්ෂණ වාරය"
        ])

    st.markdown(f"📍 **දිස්ත්‍රික්කය:** {matched_data['district']} | **කලාපය:** {matched_data['zone']} | **පිරිවෙන් වර්ගය:** `{matched_data['type']}`")
    st.markdown("---")

    st.markdown("### 📝 ප්‍රමිති 10 සඳහා මුළු ලකුණු ඇතුළත් කිරීම")

    results_summary = []
    total_obtained_all = 0
    total_maximum_all = 0

    col_s1, col_s2 = st.columns(2)
    
    for i, std in enumerate(standards_list):
        col_target = col_s1 if i < 5 else col_s2
        with col_target:
            with st.expander(f"📌 {std}", expanded=False):
                obt = st.number_input(f"ලබාගත් ලකුණු", min_value=0, max_value=1000, value=20, step=1, format="%d", key=f"obt_sum_{i}")
                max_m = st.number_input(f"උපරිම ලකුණු", min_value=1, max_value=1000, value=60, step=1, format="%d", key=f"max_sum_{i}")
                
                pct = (obt / max_m * 100) if max_m > 0 else 0.0
                st.caption(f"ප්‍රතිශතය: **{pct:.2f}%**")
                
                total_obtained_all += obt
                total_maximum_all += max_m
                
                results_summary.append({
                    "Standard": std,
                    "Obtained": int(obt),
                    "Maximum": int(max_m),
                    "Percentage": round(pct, 2)
                })

    st.markdown("---")
    st.markdown("### 📋 අධීක්ෂණ සටහන් (Monitoring Notes)")
    
    internal_notes = st.text_area("🏛️ අභ්‍යන්තර අධීක්ෂණ සටහන් (Internal Monitoring Notes - පිරිවෙන මඟින්):", placeholder="පිරිවෙනේ අභ්‍යන්තර ඇගයීම් කමිටුව මඟින් ලබා දුන් නිරීක්ෂණ සටහන් මෙහි ලියන්න...")

    external_notes = ""
    if is_admin:
        external_notes = st.text_area("🔍 බාහිර අධීක්ෂණ සටහන් (External Monitoring Notes - අධීක්ෂණ නිලධාරීන්ගේ සටහන):", placeholder="බාහිර අධීක්ෂණයට පැමිණි මාණ්ඩලික / කලාපීය නිලධාරීන්ගේ නිරීක්ෂණ හා උපදෙස් මෙහි ලියන්න...")

    if st.button("🧮 සමස්ත PEQI අගය ගණනය කර වාර්තාව සේව් කරන්න"):
        cur_census_val = target_census.strip()
        if not piriven_display_name.strip() or not cur_census_val:
            st.warning("⚠️ කරුණාකර නිවැරදි සංගණන අංකයක් සහ පිරිවෙන් නමක් ඇතුළත් කරන්න.")
        else:
            overall_peqi = (total_obtained_all / total_maximum_all * 100) if total_maximum_all > 0 else 0.0
            
            st.success(f"🎉 **{piriven_display_name}** සඳහා ගණනය කරන ලද **සමස්ත පිරිවෙන් අධ්‍යාපන ගුණාත්මක දර්ශකය (PEQI): {overall_peqi:.2f}%**")
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_records = []
            for item in results_summary:
                new_records.append({
                    "Timestamp": timestamp,
                    "Census No": cur_census_val,
                    "Piriven Name": piriven_display_name,
                    "District": matched_data["district"],
                    "Zone": matched_data["zone"],
                    "Piriven Type": matched_data["type"],
                    "Term": evaluation_term,
                    "Standard": item["Standard"],
                    "Obtained Marks": item["Obtained"],
                    "Max Marks": item["Maximum"],
                    "Percentage": item["Percentage"],
                    "Overall PEQI": round(overall_peqi, 2),
                    "Internal Notes": internal_notes,
                    "External Notes": external_notes
                })
            
            df_new = pd.DataFrame(new_records)
            if os.path.exists(DB_FILE):
                df_existing = pd.read_csv(DB_FILE)
                df_existing = df_existing[~((df_existing["Census No"].astype(str) == str(cur_census_val)) & (df_existing["Term"] == evaluation_term))]
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new
            
            df_combined.to_csv(DB_FILE, index=False)
            st.toast("✅ දත්ත පද්ධතියේ සාර්ථකව සුරකින ලදී!", icon="💾")

            st.markdown("### 📊 ප්‍රමිති අනුව කාර්යසාධන Donut Chart එක")
            df_chart = pd.DataFrame(results_summary)
            fig = px.pie(df_chart, names="Standard", values="Percentage", hole=0.5, 
                         color_discrete_sequence=px.colors.sequential.Tealgrn)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=450)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 🤖 සංවර්ධනය විය යුතු ක්ෂේත්‍ර සහ සවිස්තරාත්මක යෝජනා (Action Plan)")
            lowest_standards = df_chart.sort_values(by="Percentage", ascending=True).head(3)
            
            recommendations_list = []
            for _, row_s in lowest_standards.iterrows():
                std_name = row_s['Standard']
                std_pct = row_s['Percentage']
                rec_msg = f"අඩු ප්‍රතිශතයක් පෙන්වන '{std_name}' ({std_pct}%) ප්‍රමිතිය ඉහළ නංවා ගැනීමට විශේෂ වැඩපිළිවෙළක් ක්‍රියාත්මක කිරීම."
                recommendations_list.append(rec_msg)
                st.info(f"👉 {rec_msg}")

            st.markdown("---")
            st.markdown("### 📄 නිල වාර්තාව (PDF ලෙස ඩවුන්ලෝඩ් කරගැනීම)")
            st.success("💡 වාර්තාව සාර්ථකව සකසා ඇත. මොබයිල් හෝ පරිගණකය මඟින් PDF ලෙස ඩවුන්ලෝඩ් කරගැනීමට පහත බොත්තම ඔබන්න.")

            report_html_output = render_report_html(piriven_display_name, cur_census_val, matched_data["district"], matched_data["zone"], evaluation_term, overall_peqi, results_summary, internal_notes, external_notes, recommendations_list, is_admin)
            
            b64_html = base64.b64encode(report_html_output.encode('utf-8')).decode('utf-8')
            href = f'<a href="data:text/html;base64,{b64_html}" download="PEQI_Report_{cur_census_val}_{evaluation_term.replace(" ", "_")}.html" style="background-color: #0f766e; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 15px;">📥 නිල වාර්තාව PDF ලෙස Download කරගන්න</a>'
            st.markdown(href, unsafe_allow_html=True)

with tab_search:
    st.markdown("### 🔍 ගබඩා කළ දත්ත සහ වාර්තා සෙවීම")
    search_q = st.text_input("පිරිවෙන් නම හෝ සංගණන අංකය ඇතුළත් කරන්න:", placeholder="උදා: Subodhi")
    
    if os.path.exists(DB_FILE):
        df_db = pd.read_csv(DB_FILE)
        is_admin_user = (st.session_state.peqi_role == "Admin")
        
        if not is_admin_user:
            filtered = df_db[df_db["Census No"].astype(str) == str(st.session_state.peqi_user_census)]
        elif search_q.strip():
            q = search_q.strip().lower()
            filtered = df_db[df_db["Census No"].astype(str).str.lower().str.contains(q) | df_db["Piriven Name"].astype(str).str.lower().str.contains(q)]
        else:
            filtered = df_db
            
        if not filtered.empty:
            uniques = filtered[["Census No", "Piriven Name", "District", "Term", "Overall PEQI"]].drop_duplicates()
            st.dataframe(uniques, use_container_width=True)
            
            sel_p = st.selectbox("පිරිවෙන තෝරන්න:", uniques["Piriven Name"].unique())
            sel_t = st.selectbox("අධීක්ෂණ වාරය තෝරන්න:", uniques["Term"].unique(), key="search_term_sel")
            
            if st.button("📊 වාර්තාව සහ ප්‍රස්තාරය පෙන්වන්න"):
                row_sel = filtered[(filtered["Piriven Name"].astype(str) == str(sel_p)) & (filtered["Term"] == sel_t)]
                if not row_sel.empty:
                    p_name = row_sel.iloc[0]["Piriven Name"]
                    p_census = row_sel.iloc[0]["Census No"]
                    p_dist = row_sel.iloc[0]["District"]
                    p_zone = row_sel.iloc[0]["Zone"]
                    p_peqi = row_sel.iloc[0]["Overall PEQI"]
                    p_notes = row_sel.iloc[0].get("Internal Notes", "N/A")
                    p_ext_notes = row_sel.iloc[0].get("External Notes", "N/A")
                    
                    st.markdown(f"### 🏛️ {p_name} ({sel_t})")
                    st.success(f"⭐ **සමස්ත PEQI අගය:** `{p_peqi}%`")
                    st.info(f"📝 **අභ්‍යන්තර සටහන්:** {p_notes}")
                    if is_admin_user:
                        st.warning(f"🔍 **බාහිර අධීක්ෂණ සටහන්:** {p_ext_notes}")
                    
                    fig2 = px.pie(row_sel, names="Standard", values="Percentage", hole=0.5, 
                                 color_discrete_sequence=px.colors.sequential.Tealgrn)
                    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=450)
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    s_summary = []
                    for _, r in row_sel.iterrows():
                        s_summary.append({"Standard": r["Standard"], "Percentage": r["Percentage"], "Obtained": r["Obtained Marks"], "Maximum": r["Max Marks"]})
                    
                    s_low = row_sel.sort_values(by="Percentage", ascending=True).head(3)
                    s_recs = [f"'{r['Standard']}' ({r['Percentage']}%): සංවර්ධනය විය යුතුය." for _, r in s_low.iterrows()]
                    
                    saved_html_output = render_report_html(p_name, p_census, p_dist, p_zone, sel_t, p_peqi, s_summary, p_notes, p_ext_notes, s_recs, is_admin_user)
                    
                    b64_saved = base64.b64encode(saved_html_output.encode('utf-8')).decode('utf-8')
                    href_saved = f'<a href="data:text/html;base64,{b64_saved}" download="PEQI_Report_{p_census}_{sel_t.replace(" ", "_")}.html" style="background-color: #0f766e; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-top: 15px;">📥 මෙම වාර්තාව Download කරගන්න</a>'
                    st.markdown(href_saved, unsafe_allow_html=True)
        else:
            st.info("⚠️ ගැලපෙන දත්ත හමු නොවීය.")
    else:
        st.info("📂 තවම දත්ත ගබඩා කර නැත.")