import streamlit as st
import streamlit.components.v1 as components 
import pandas as pd
import datetime
import base64
import os
from urllib.parse import urlparse, parse_qs
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 💡 Google Sheets සම්බන්ධතා සැකසීම
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
current_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(current_dir, "credentials.json")

def get_google_sheet():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        client = gspread.authorize(creds)
        return client.open("Piriven_Monitoring_DB")
    except Exception as e:
        return None

# 💡 Folium ආරක්ෂාකාරී ලෙස ඉම්පෝට් කිරීම
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# ලංකාවේ නිල දිස්ත්‍රික්ක 25
SRI_LANKA_DISTRICTS = [
    "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya", 
    "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar", 
    "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara", "Trincomalee", 
    "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla", 
    "Monaragala", "Ratnapura", "Kegalle"
]

def process_youtube_link(url_or_id):
    url_str = url_or_id.strip()
    if "youtube.com" not in url_str and "youtu.be" not in url_str: return {"type": "video", "value": url_str}
    try:
        parsed_url = urlparse(url_str)
        if "list=" in url_str: return {"type": "playlist", "value": url_str}
        if "/c/" in url_str or "/channel/" in url_str or "/@" in url_str or "user/" in url_str: return {"type": "channel", "value": url_str}
        if parsed_url.hostname == 'youtu.be': return {"type": "video", "value": parsed_url.path[1:]}
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                p = parse_qs(parsed_url.query)
                return {"type": "video", "value": p['v'][0]}
    except: pass
    return {"type": "custom", "value": url_str}

st.set_page_config(page_title="Ministry Admin Dashboard", layout="wide")

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
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #111827; padding: 10px; border-radius: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1f2937; border-radius: 8px;
            padding: 10px 20px; font-weight: bold; color: #94a3b8;
            border: 1px solid #374151;
        }
        .stTabs [aria-selected="true"] { background-color: #0f766e !important; color: white !important; }
        
        div[data-testid="stMetric"] {
            background-color: #111827; padding: 15px; border-radius: 12px; border: 1px solid #374151;
        }
        div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 28px; font-weight: bold; }
        
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background-color: #1f2937 !important; color: white !important; border: 1px solid #374151 !important; border-radius: 8px !important;
        }
        .stButton>button { 
            width: 100% !important; border-radius: 8px !important; font-weight: bold !important; 
            background-color: #0f766e !important; color: #ffffff !important; border: none !important; padding: 10px 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 🔐 Login Gate ---
if "board_logged_in" not in st.session_state: st.session_state.board_logged_in = False
if "board_user" not in st.session_state: st.session_state.board_user = None

if not st.session_state.board_logged_in:
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.3, 1])
    with col_l2:
        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
        with st.form("board_login_form"):
            st.markdown("<h3 style='color: #38bdf8; text-align: center;'>💻 ඩිජිටල් බෝඩ් පාලක මැදිරිය</h3>", unsafe_allow_html=True)
            u_name = st.text_input("👤 පරිශීලක නාමය (Username)")
            u_pass = st.text_input("🔑 මුරපදය (Password)", type="password")
            sub_login = st.form_submit_button("පද්ධතියට ඇතුල් වන්න 🔓", use_container_width=True)
            
            if sub_login:
                if u_name == "admin" and u_pass == "admin123":
                    st.session_state.board_logged_in = True
                    st.session_state.board_user = {"name": "Super Admin", "role": "Super Admin"}
                    st.success("✅ ප්‍රවේශය සාර්ථකයි!")
                    st.rerun()
                else:
                    st.error("⚠️ පරිශීලක නාමය හෝ මුරපදය වැරදියයි!")
    st.stop()

with st.sidebar:
    if st.button("🏠 ප්‍රධාන මුල් පිටුවට", key="home_btn_sidebar", use_container_width=True):
        st.switch_page("app.py")
    st.markdown("---")
    st.header("📁 Data Source Setup")
    uploaded_file = st.file_uploader("Upload Piriven Excel Registry (.xlsx)", type=["xlsx"])

st.markdown("<h2 style='color: #f8fafc;'>🏛️ Ministry of Education - Piriven Division</h2>", unsafe_allow_html=True)
st.write("---")

# Google Sheets මඟින් දත්ත ලබා ගැනීම
sheet = get_google_sheet()
live_boards_data = {}
cloud_excel_data = []

if sheet:
    try:
        live_ws = sheet.worksheet("Live_Boards")
        live_records = live_ws.get_all_records()
        for r in live_records:
            c_no = str(r.get("Census No", ""))
            ser = str(r.get("Device Serial", ""))
            if c_no not in live_boards_data: live_boards_data[c_no] = {}
            live_boards_data[c_no][ser] = {
                "device_type": r.get("Device Type", "Smart Board"),
                "live_lat": float(r.get("Latitude", 0)),
                "live_lon": float(r.get("Longitude", 0)),
                "status": r.get("Status", "Offline"),
                "last_ping": r.get("Last Ping", "")
            }
        
        # 💡 Pirivena_Master ටැබ් එකෙන් පිරිවෙන් දත්ත කියවා ගැනීම
        reg_ws = sheet.worksheet("Pirivena_Master")
        cloud_excel_data = reg_ws.get_all_records()
    except Exception as e:
        st.error(f"Sheet Read Error: {e}")

df_usage = None
if uploaded_file:
    try:
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip()
        df_raw["Census No"] = df_raw["Census No"].fillna("").astype(str).str.strip().apply(lambda x: x.split('.')[0] if '.' in x else x)
        df_raw["Piriven Name"] = df_raw["Piriven Name"].fillna("").astype(str).str.strip()
        df_raw["District"] = df_raw["District"].fillna("").astype(str).str.strip().str.title() 
        df_raw["Zone"] = df_raw["Zone"].fillna("").astype(str).str.strip().str.title() if "Zone" in df_raw.columns else df_raw["District"]
        
        df_temp = pd.DataFrame()
        df_temp["Census No"], df_temp["Piriven Name"] = df_raw["Census No"], df_raw["Piriven Name"]
        df_temp["District"] = df_raw["District"]
        df_temp["Zone"], df_temp["Latitude"], df_temp["Longitude"] = df_raw["Zone"], df_raw.get("Latitude", 0), df_raw.get("Longitude", 0)
        
        # Google Sheet එකේ Pirivena_Master ටැබ් එකට සේව් කිරීම
        if sheet:
            reg_ws = sheet.worksheet("Pirivena_Master")
            reg_ws.clear()
            reg_ws.update([df_temp.columns.values.tolist()] + df_temp.values.tolist())
        
        df_usage = df_temp.copy()
        st.sidebar.success("✅ Excel Saved to Google Sheets!")
    except Exception as e: st.sidebar.error(f"Error: {e}")

if df_usage is None and cloud_excel_data:
    df_usage = pd.DataFrame(cloud_excel_data)
    if not df_usage.empty:
        df_usage["Census No"] = df_usage["Census No"].astype(str).str.strip().apply(lambda x: x.split('.')[0] if '.' in x else x)
        df_usage["District"] = df_usage["District"].astype(str).str.strip().str.title()

if df_usage is None or df_usage.empty:
    df_usage = pd.DataFrame({"Census No": ["0542"], "Piriven Name": ["Sample Pirivena"], "District": ["Colombo"], "Zone": ["Central"], "Status": ["Offline"], "Latitude": [6.9271], "Longitude": [79.8612]})

def is_device_actually_active(last_ping_str):
    try:
        if not last_ping_str: return False
        last_ping_time = datetime.datetime.strptime(last_ping_str, "%Y-%m-%d %H:%M:%S")
        srilanka_now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
        return 0 <= (srilanka_now - last_ping_time).total_seconds() < 600
    except: return False

live_census_list = []
for c_id, devices in live_boards_data.items():
    if isinstance(devices, dict):
        for d_id, d_info in devices.items():
            if is_device_actually_active(d_info.get("last_ping")):
                live_census_list.append(str(c_id).strip())
                break

df_usage["Status"] = ["Active" if str(row["Census No"]).strip() in live_census_list else "Offline" for i, row in df_usage.iterrows()]
census_to_name = dict(zip(df_usage["Census No"].astype(str), df_usage["Piriven Name"]))

# Filters
st.sidebar.write("---")
st.sidebar.header("🔍 Live Filters")
dist_list = ["All Island"] + sorted([d for d in df_usage["District"].unique().tolist() if d and d != "Nan"])
selected_district = st.sidebar.selectbox("Select District:", dist_list)
df_step1 = df_usage[df_usage["District"] == selected_district] if selected_district != "All Island" else df_usage.copy()

pir_list = ["All Piriven"] + sorted(df_step1["Piriven Name"].unique().tolist())
selected_piriven = st.sidebar.selectbox("Select Piriven Name:", pir_list)
df_filtered = df_step1[df_step1["Piriven Name"] == selected_piriven] if selected_piriven != "All Piriven" else df_step1.copy()

tab1, tab2, tab3 = st.tabs(["🗺️ Live Map & Remote Control", "📊 Analytics & Usage Stats", "🛠️ Support Tickets & Live Chat"])

with tab1:
    col_map, col_ctrl = st.columns([3, 2])
    with col_map:
        st.subheader("Live Board Tracking")
        if FOLIUM_AVAILABLE:
            m = folium.Map(location=[7.8731, 80.7718], zoom_start=8, tiles="OpenStreetMap")
            for _, r in df_filtered.iterrows():
                c_no = str(r["Census No"]).strip()
                lat, lon = float(r.get("Latitude", 0)), float(r.get("Longitude", 0))
                if lat != 0 and lon != 0:
                    status = r.get("Status", "Offline")
                    color = "green" if status == "Active" else "red"
                    folium.Marker([lat, lon], popup=f"🏛️ {r['Piriven Name']}<br>Status: {status}", icon=folium.Icon(color=color)).add_to(m)
            st_folium(m, width=700, height=600)

    with col_ctrl:
        st.subheader("📢 Command Center")
        yt_input = st.text_input("YouTube URL / ID:")
        if st.button("🚀 BROADCAST TO ALL BOARDS"):
            if yt_input and sheet:
                settings_ws = sheet.worksheet("Settings")
                settings_ws.update('A1', [[yt_input]])
                st.success("✅ Broadcast Successful via Google Sheets!")

with tab3:
    st.subheader("🛠️ Technical Support Tickets")
    if sheet:
        try:
            t_ws = sheet.worksheet("Support_Tickets")
            tickets = t_ws.get_all_records()
            for idx, t in enumerate(tickets, 1):
                st.markdown(f"**Ticket #{idx} | Census: {t.get('Census No')} | Issue: {t.get('Issue Type')}**")
                st.write(f"Description: {t.get('Description')}")
                st.caption(f"Status: {t.get('Status')} | Date: {t.get('Reported At')}")
                st.write("---")
        except Exception as e:
            st.info("No tickets found or worksheet missing.")
