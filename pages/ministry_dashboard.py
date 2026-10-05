import requests
import streamlit as st
import streamlit.components.v1 as components  # 💡 JS ඔරලෝසුව සජීවීව පණගැන්වීමට
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime
import base64
import os
from urllib.parse import urlparse, parse_qs

# ⚠️ Firebase API URL
FIREBASE_URL = "https://pirivensmartboardmonitoring-default-rtdb.asia-southeast1.firebasedatabase.app/"

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
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #111827; padding: 10px; border-radius: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1f2937; border-radius: 8px;
            padding: 10px 20px; font-weight: bold; color: #94a3b8;
            border: 1px solid #374151;
        }
        .stTabs [aria-selected="true"] { background-color: #0f766e !important; color: white !important; }
        
        /* Metrics Card Styling */
        div[data-testid="stMetric"] {
            background-color: #111827;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #374151;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        div[data-testid="stMetricValue"] { 
            color: #38bdf8 !important; 
            font-size: 28px; 
            font-weight: bold;
        }
        div[data-testid="stMetricLabel"] p {
            color: #94a3b8 !important;
            font-weight: 600;
        }
        
        /* Inputs & Buttons */
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background-color: #1f2937 !important;
            color: white !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
        }
        .stButton>button, div[data-testid="stFormSubmitButton"]>button { 
            width: 100% !important;
            border-radius: 8px !important;
            font-weight: bold !important; 
            background-color: #0f766e !important; 
            color: #ffffff !important; 
            border: none !important;
            padding: 10px 20px !important;
        }
        .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover { 
            background-color: #115e59 !important; 
            color: #ffffff !important; 
        }
    </style>
""", unsafe_allow_html=True)

# --- 🔐 Digital Board Module Login Gate ---
if "board_logged_in" not in st.session_state:
    st.session_state.board_logged_in = False
if "board_user" not in st.session_state:
    st.session_state.board_user = None

if not st.session_state.board_logged_in:
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.3, 1])
    with col_l2:
        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
        with st.form("board_login_form"):
            st.markdown("<h3 style='color: #38bdf8; text-align: center;'>💻 ඩිජිටල් බෝඩ් පාලක මැදිරිය</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 13px;'>අමාත්‍යාංශ ඩෑෂ්බෝඩ් එකට පිවිසීමට ඔබේ පරිශීලක නාමය සහ මුරපදය ලබා දෙන්න.</p>", unsafe_allow_html=True)
            
            u_name = st.text_input("👤 පරිශීලක නාමය (Username)")
            u_pass = st.text_input("🔑 මුරපදය (Password)", type="password")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            sub_login = st.form_submit_button("පද්ධතියට ඇතුල් වන්න 🔓", use_container_width=True)
            
            if sub_login:
                login_success = False
                user_details = {}
                
                excel_paths = ["users.xlsx", os.path.join("digital_boards", "users.xlsx"), os.path.join("..", "users.xlsx")]
                df_users = None
                
                for path in excel_paths:
                    if os.path.exists(path):
                        try:
                            df_users = pd.read_excel(path)
                            break
                        except: pass
                
                if df_users is not None:
                    df_users.columns = df_users.columns.str.strip()
                    u_col = next((c for c in df_users.columns if 'user' in c.lower()), 'Username')
                    p_col = next((c for c in df_users.columns if 'pass' in c.lower()), 'Password')
                    n_col = next((c for c in df_users.columns if 'name' in c.lower() and 'user' not in c.lower()), 'Name')
                    r_col = next((c for c in df_users.columns if 'role' in c.lower() or 'acc' in c.lower()), df_users.columns[3] if len(df_users.columns) > 3 else 'Role')
                    
                    for _, row in df_users.iterrows():
                        db_user = str(row.get(u_col, "")).strip()
                        db_pass = str(row.get(p_col, "")).strip()
                        
                        if db_user == u_name.strip() and db_pass == u_pass.strip():
                            login_success = True
                            user_details = {
                                "name": str(row.get(n_col, "Admin")),
                                "role": str(row.get(r_col, "Super Admin"))
                            }
                            break
                
                if login_success:
                    st.session_state.board_logged_in = True
                    st.session_state.board_user = user_details
                    st.success("✅ ප්‍රවේශය සාර්ථකයි!")
                    st.rerun()
                else:
                    st.error("⚠️ පරිශීලක නාමය හෝ මුරපදය වැරදියි!")
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 ප්‍රධාන මුල් පිටුවට (Home) ආපසු යන්න", key="home_btn_login", use_container_width=True):
            st.switch_page("app.py")
    st.stop()

# ලොග් වූ පසු සයිඩ්බාර් එක පෙන්වීම
with st.sidebar:
    if st.button("🏠 ප්‍රධාන මුල් පිටුවට", key="home_btn_sidebar", use_container_width=True):
        st.switch_page("app.py")
    
    if st.session_state.board_user:
        u_info = st.session_state.board_user
        st.markdown(f"""
            <div style="background: #1f2937; padding: 10px; border-radius: 8px; border-left: 4px solid #0f766e; margin-bottom: 15px;">
                <div style="font-size: 13px; font-weight: bold; color: #f3f4f6;">👤 {u_info['name']}</div>
                <div style="font-size: 11px; color: #38bdf8; margin-top: 3px;">තනතුර: <b>{u_info['role']}</b></div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.header("📁 Data Source Setup")
    uploaded_file = st.file_uploader("Upload Piriven Excel Registry (.xlsx)", type=["xlsx"])

# 💡 වින්ඩෝස් පද්ධතියේ නියම වෙලාව පෙන්වන සජීවී ඔරලෝසු ව්‍යුහය
col_title, col_clock = st.columns([4, 1])
with col_title:
    st.markdown("<h2 style='color: #f8fafc; margin-top: -10px;'>🏛️ Ministry of Education - Piriven Division</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 14px; font-weight: bold; margin-top: -15px;'>Central Control, Analytics & Monitoring Dashboard</p>", unsafe_allow_html=True)
with col_clock:
    st.markdown("<p style='text-align:center; margin-bottom:0px; font-weight:bold; color:#cbd5e1; font-size:12px;'>💻 DEVICE TIME</p>", unsafe_allow_html=True)
    clock_html = """
    <div id="clock-span" style="background-color: #111827; color: #38bdf8; padding: 8px; border-radius: 8px; text-align: center; font-family: monospace; font-size: 14px; font-weight: bold; border: 1px solid #374151;">Loading...</div>
    <script>
        function updateClock() {
            var now = new Date();
            var year = now.getFullYear();
            var month = String(now.getMonth() + 1).padStart(2, '0');
            var day = String(now.getDate()).padStart(2, '0');
            var hours = String(now.getHours()).padStart(2, '0');
            var minutes = String(now.getMinutes()).padStart(2, '0');
            var seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock-span').innerText = year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """
    components.html(clock_html, height=60)

st.write("---")

live_boards_data, cloud_excel_data = {}, None
try:
    res1 = requests.get(f"{FIREBASE_URL}live_boards.json")
    if res1.status_code == 200: live_boards_data = res1.json() or {}
    res2 = requests.get(f"{FIREBASE_URL}ministry_excel_registry.json")
    if res2.status_code == 200: cloud_excel_data = res2.json()
except: pass

df_usage = None
if uploaded_file:
    try:
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip()
        
        df_raw["Census No"] = df_raw["Census No"].fillna("").astype(str).str.strip().apply(lambda x: x.split('.')[0] if '.' in x else x)
        df_raw["Piriven Name"] = df_raw["Piriven Name"].fillna("").astype(str).str.strip()
        df_raw["District"] = df_raw["District"].fillna("").astype(str).str.strip().str.title() 
        df_raw["Zone"] = df_raw["Zone"].fillna("").astype(str).str.strip().str.title() if "Zone" in df_raw.columns else df_raw["District"]
        df_raw["Latitude"] = df_raw["Latitude"].fillna(0.0)
        df_raw["Longitude"] = df_raw["Longitude"].fillna(0.0)
        df_raw["Monthly Usage (Hours)"] = df_raw["Monthly Usage (Hours)"].fillna(0)

        for index, row in df_raw.iterrows():
            lat, lon = float(row.get("Latitude", 0.0)), float(row.get("Longitude", 0.0))
            if lat > 70.0 and lon < 15.0:
                df_raw.at[index, "Latitude"], df_raw.at[index, "Longitude"] = lon, lat

        df_temp = pd.DataFrame()
        df_temp["Census No"], df_temp["Piriven Name"] = df_raw["Census No"], df_raw["Piriven Name"]
        df_temp["District"] = [([d for d in SRI_LANKA_DISTRICTS if d.lower() == x.lower()] + ["Other/Unclassified"])[0] for x in df_raw["District"]]
        df_temp["Zone"], df_temp["Latitude"], df_temp["Longitude"], df_temp["Monthly Usage (Hours)"] = df_raw["Zone"], df_raw["Latitude"], df_raw["Longitude"], df_raw["Monthly Usage (Hours)"]
        
        requests.put(f"{FIREBASE_URL}ministry_excel_registry.json", json=df_temp.to_dict(orient="records"))
        df_usage = df_temp.copy()
        st.sidebar.success("✅ Excel Saved to Cloud!")
    except Exception as e: st.sidebar.error(f"Error: {e}")

if df_usage is None and cloud_excel_data:
    df_usage = pd.DataFrame(cloud_excel_data)
    df_usage["Census No"] = df_usage["Census No"].astype(str).str.strip().apply(lambda x: x.split('.')[0] if '.' in x else x)
    df_usage["District"] = df_usage["District"].astype(str).str.strip().str.title()
    st.sidebar.info("☁️ Registry Loaded from Cloud")

if df_usage is None:
    df_usage = pd.DataFrame({"Census No": ["0542"], "Piriven Name": ["Sample Pirivena"], "District": ["Colombo"], "Zone": ["Central"], "Status": ["Offline"], "Latitude": [6.9271], "Longitude": [79.8612], "Monthly Usage (Hours)": [0]})

def is_device_actually_active(last_ping_str):
    try:
        if not last_ping_str: return False
        last_ping_time = datetime.datetime.strptime(last_ping_str, "%Y-%m-%d %H:%M:%S")
        srilanka_now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
        time_difference = (srilanka_now - last_ping_time).total_seconds()
        if 0 <= time_difference < 600: return True
    except: pass
    return False

live_census_list = []
for c_id, devices in live_boards_data.items():
    if isinstance(devices, dict):
        for d_id, d_info in devices.items():
            if d_id != "attendance" and isinstance(d_info, dict) and is_device_actually_active(d_info.get("last_ping")):
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

with tab2:
    st.subheader("📊 Performance Analytics")
    c_left, c_middle, c_right = st.columns(3) 
    c_left.metric("Registered Boards", len(df_filtered))
    
    total_active_devices = 0
    total_live_students = 0
    filtered_census_nos = df_filtered["Census No"].astype(str).tolist()
    
    for c_no in filtered_census_nos:
        if c_no in live_boards_data and isinstance(live_boards_data[c_no], dict):
            for dev_id, dev_info in live_boards_data[c_no].items():
                if dev_id != "attendance" and isinstance(dev_info, dict) and is_device_actually_active(dev_info.get("last_ping")):
                    total_active_devices += 1
            if "attendance" in live_boards_data[c_no] and isinstance(live_boards_data[c_no]["attendance"], dict):
                att_info = live_boards_data[c_no]["attendance"]
                if is_device_actually_active(att_info.get("last_captured")):
                    total_live_students += int(att_info.get("live_student_count", 0))
            
    c_middle.metric("Total Active Devices Now", total_active_devices)
    c_right.metric("👨‍🎓 Total Live Students Learning Now", total_live_students) 
    st.write("---")
    
    app_hours_dict = {}
    try:
        res_apps = requests.get(f"{FIREBASE_URL}software_analytics.json")
        if res_apps.status_code == 200 and res_apps.json():
            apps_cloud_data = res_apps.json()
            for c_no in filtered_census_nos:
                if c_no in apps_cloud_data and isinstance(apps_cloud_data[c_no], dict):
                    for app_name, minutes in apps_cloud_data[c_no].items():
                        if app_name not in app_hours_dict: app_hours_dict[app_name] = 0.0
                        app_hours_dict[app_name] += round(minutes / 60.0, 2)
    except: pass
    if not app_hours_dict: app_hours_dict = {"No Software Tracked Yet": 0.0}
    software_chart_data = pd.DataFrame({"Software Application": list(app_hours_dict.keys()), "Total Active Execution (Hours)": list(app_hours_dict.values())})
    
    st.markdown("### ⏱️ Select Time Analytics View")
    time_view = st.selectbox(
        "Display Usage Data In:",
        ["Hours (පැය)", "Days (දවස්)", "Weeks (සති)", "Months (මාස)", "Years (අවුරුදු)"],
        key="time_view_filter"
    )
    
    conversion_factor = 1.0
    unit_label = "Hours"
    if "Days" in time_view: conversion_factor, unit_label = 24.0, "Days"
    elif "Weeks" in time_view: conversion_factor, unit_label = 168.0, "Weeks"
    elif "Months" in time_view: conversion_factor, unit_label = 730.0, "Months"
    elif "Years" in time_view: conversion_factor, unit_label = 8760.0, "Years"

    software_chart_data["Total Active Execution"] = (software_chart_data["Total Active Execution (Hours)"] / conversion_factor).round(2)
    software_chart_data_view = software_chart_data[["Software Application", "Total Active Execution"]].rename(
        columns={"Total Active Execution": f"Total Active Execution ({unit_label})"}
    )

    col_sw1, col_sw2 = st.columns(2)
    with col_sw1: 
        st.markdown(f"**Software Usage Comparison ({unit_label})**")
        st.bar_chart(software_chart_data_view.set_index("Software Application"))
    with col_sw2: 
        st.markdown(f"**Application Screen-Time Breakdown ({unit_label})**")
        st.dataframe(software_chart_data_view, use_container_width=True)
            
    st.write("---")
    df_filtered_time = df_filtered.copy()
    df_filtered_time[f"Usage ({unit_label})"] = (df_filtered_time["Monthly Usage (Hours)"] / conversion_factor).round(2)
    st.markdown(f"**Overall Board Runtime Log ({unit_label})**")
    st.bar_chart(df_filtered_time.set_index("Piriven Name")[f"Usage ({unit_label})"])
    
    st.write("---")
    st.markdown("### 📋 Device Registry & Quick Map Link")
    
    styled_df = df_filtered.drop(columns=["Latitude", "Longitude"], errors="ignore").style.map(
        lambda v: "background-color: #064e3b; color: #a7f3d0; font-weight: bold;" if v == "Active" else ("background-color: #7f1d1d; color: #fecaca; font-weight: bold;" if v == "Offline" else ""),
        subset=["Status"]
    )
    st.dataframe(styled_df, use_container_width=True)

map_center = [7.8731, 80.7718]
map_zoom = 8
if selected_piriven != "All Piriven" and not df_filtered.empty:
    first_row = df_filtered.iloc[0]
    if float(first_row.get("Latitude", 0.0)) != 0.0: 
        map_center = [float(first_row["Latitude"]), float(first_row["Longitude"])]
        map_zoom = 14

with tab1:
    col_map, col_ctrl = st.columns([3, 2])
    with col_map:
        st.subheader("Live Board Tracking")
        m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="CartoDB dark_matter")
        
        for i, r in df_filtered.iterrows():
            c_no = str(r["Census No"]).strip()
            is_any_device_live = False
            
            if c_no in live_boards_data and isinstance(live_boards_data[c_no], dict):
                live_stu_popup = 0
                if "attendance" in live_boards_data[c_no] and isinstance(live_boards_data[c_no]["attendance"], dict):
                    att_info = live_boards_data[c_no]["attendance"]
                    if is_device_actually_active(att_info.get("last_captured")):
                        live_stu_popup = att_info.get("live_student_count", 0)

                for dev_id, dev_info in live_boards_data[c_no].items():
                    if dev_id == "attendance" or not isinstance(dev_info, dict): continue
                    
                    if is_device_actually_active(dev_info.get("last_ping")):
                        is_any_device_live = True
                        d_type = dev_info.get("device_type", "Smart Board")
                        l_lat = dev_info.get("live_lat", r["Latitude"])
                        l_lon = dev_info.get("live_lon", r["Longitude"])
                        
                        if c_no == "430001" or l_lat == 7.8731 or l_lat == 0.0:
                            l_lat, l_lon = r["Latitude"], r["Longitude"]
                        
                        if d_type == "Smart Board": icon_color = "green"
                        elif d_type == "Laptop": icon_color = "blue"
                        else: icon_color = "orange"
                        
                        adv_spec = dev_info.get("spec_advanced", {})
                        popup_html = f"""
                        <div style='font-family: sans-serif; font-size: 12px; line-height: 1.5; min-width: 270px; background-color: #1e293b; color: white; padding: 10px; border-radius: 8px;'>
                            <h3 style='margin: 0 0 5px 0; color: #38bdf8;'>🏛️ {r['Piriven Name']}</h3>
                            <span style='background-color: #064e3b; color: #a7f3d0; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>🟢 Active Now</span><br>
                            <p style='margin: 8px 0 4px 0;'>📟 <b>Device Type:</b> {d_type} (Serial: {dev_id})</p>
                            <p style='margin: 0 0 8px 0;'>👨‍🎓 <b>Active Students Now:</b> <span style='color: #60a5fa; font-weight: bold;'>{live_stu_popup}</span></p>
                        </div>
                        """
                        if l_lat != 0.0 and l_lon != 0.0:
                            folium.Marker(
                                [l_lat, l_lon], popup=popup_html,
                                icon=folium.Icon(color=icon_color, icon="desktop" if d_type != "Laptop" else "laptop")
                            ).add_to(m)
            
            if not is_any_device_live and r["Latitude"] != 0:
                folium.Marker(
                    [r["Latitude"], r["Longitude"]], popup=f"🏛️ {r['Piriven Name']}<br>🔴 Status: Offline", 
                    icon=folium.Icon(color="red", icon="remove-sign")
                ).add_to(m)
                                    
        st_folium(m, width=700, height=600, key=f"map_{selected_district}_{selected_piriven}")

    with col_ctrl:
        st.subheader("📢 Command Center")
        yt_input = st.text_input("YouTube URL:")
        if st.button("🚀 BROADCAST TO ALL BOARDS", key="broadcast_btn"):
            if yt_input:
                requests.put(f"{FIREBASE_URL}current_lesson.json", json=process_youtube_link(yt_input))
                st.success("✅ Broadcast Successful!")
                        
        st.write("---")
        ann_t = st.text_input("Announcement Title:")
        ann_b = st.text_area("Message Body:")
        if st.button("📢 PUSH LIVE NOTIFICATION", key="push_notif_btn"):
            if ann_t and ann_b: 
                requests.put(f"{FIREBASE_URL}latest_announcement.json", json={"title": ann_t, "body": ann_b})
                st.success("✅ Message Pushed Successfully!")

with tab3:
    st.subheader("🛠️ Technical Support & Ticket Interactive Chat Panel")
    
    def resolve_ticket(ticket_id):
        try:
            res = requests.patch(f"{FIREBASE_URL}support_tickets/{ticket_id}.json", json={"status": "Solved"}, timeout=4)
            if res.status_code == 200: 
                st.toast("🟢 ටිකට් එක සාර්ථකව යාවත්කාලීන වුණා!", icon="✅")
                st.rerun()
        except: st.sidebar.error("❌ Connection Error.")

    try:
        res_t = requests.get(f"{FIREBASE_URL}support_tickets.json", timeout=4)
        if res_t.status_code == 200 and res_t.json():
            t_data = res_t.json()
            ticket_index = 1
            
            for tid, det in t_data.items():
                c_no = str(det.get("census_no", "")).strip()
                p_name = census_to_name.get(c_no, f"Unknown ({c_no})")
                if selected_piriven != "All Piriven" and p_name != selected_piriven: continue
                
                status_label = "🔴 Pending" if det.get('status') == "Pending" else "🟢 Solved"
                
                with st.expander(f"🎫 TICKET #{ticket_index} | 🏛️ {p_name} - [{det.get('issue_type')}] (⏱️ {det.get('reported_at', 'N/A')}) - Status: {status_label}"):
                    st.markdown(f"**📝 Issue Description:** {det.get('description')}")
                    st.caption(f"Device Serial: {det.get('device_serial', 'N/A')} | DB Reference ID: {tid}")
                    
                    st.write("---")
                    st.markdown("💬 **Live Discussion / අමාත්‍යාංශ පිළිතුරු:**")
                    chats = det.get("chats", {})
                    if chats:
                        for cid, cmsg in chats.items():
                            sender = "🏛️ Ministry" if cmsg.get("sender") == "ministry" else "🏫 Piriven"
                            st.markdown(f"**{sender}:** {cmsg.get('msg')}  *<small>({cmsg.get('time')[11:16]})</small>*", unsafe_allow_html=True)
                    
                    if det.get('status') == "Pending":
                        chat_input = st.text_input("Type your response here / පිළිතුර සටහන් කරන්න:", key=f"chat_in_{tid}")
                        if st.button("↩️ Send Message", key=f"send_btn_{tid}"):
                            if chat_input:
                                new_chat_node = {
                                    "sender": "ministry",
                                    "msg": chat_input,
                                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                requests.post(f"{FIREBASE_URL}support_tickets/{tid}/chats.json", json=new_chat_node)
                                st.rerun()
                        
                        st.write("---")
                        st.button("Mark as Solved ✅", key=f"sol_{tid}", on_click=resolve_ticket, args=(tid,))
                    else:
                        st.info("🔒 This ticket has been marked as solved. Chat is locked.")
                
                ticket_index += 1
        else: st.info("No reported tickets found.")
    except Exception as e: st.error(f"Error loading tickets: {e}")

# Footer Section
st.write("---")
cur_year = datetime.datetime.now().year

def get_base64_image(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as image_file: return f"data:image/png;base64,{base64.b64encode(image_file.read()).decode()}"
    return ""

state_img_base64 = get_base64_image("statelogo.png")
piriven_img_base64 = get_base64_image("pirivenlogo.png")

footer_html = f"""
<div style="background-color: #111827; padding: 25px; border-radius: 12px; text-align: center; color: white; margin-top: 40px; font-family: sans-serif; border: 1px solid #374151;">
    <table style="width: 100%; border-collapse: collapse; border: none; background-color: transparent; margin: 0 auto;">
        <tr style="border: none; background-color: transparent;">
            <td style="width: 20%; text-align: right; border: none; background-color: transparent; padding: 10px; vertical-align: middle;">
                {"<img src='" + state_img_base64 + "' style='height: 60px; max-width: 100%; object-fit: contain;'>" if state_img_base64 else ""}
            </td>
            <td style="width: 60%; text-align: center; border-top: none; border-bottom: none; border-left: 2px solid #374151; border-right: 2px solid #374151; background-color: transparent; padding: 10px 20px; vertical-align: middle;">
                <p style="margin: 0; font-size: 16px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px;">Piriven Development Branch</p>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #94a3b8;">📧 Email: <a href="mailto:info.pirivendevelopment@gmail.com" style="color: #38bdf8; text-decoration: none; font-weight: bold;">info.pirivendevelopment@gmail.com</a></p>
            </td>
            <td style="width: 20%; text-align: left; border: none; background-color: transparent; padding: 10px; vertical-align: middle;">
                {"<img src='" + piriven_img_base64 + "' style='height: 60px; max-width: 100%; object-fit: contain;'>" if piriven_img_base64 else ""}
            </td>
        </tr>
    </table>
    <div style="font-size: 11px; color: #94a3b8; margin-top: 20px; padding-top: 15px; border-top: 1px solid #374151; line-height: 1.5;">
        © {cur_year} | All Rights Reserved | Development Branch, Piriven Division, Ministry of Education, Higher Education and Vocational Education.
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)