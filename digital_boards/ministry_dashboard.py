import streamlit as st
import streamlit.components.v1 as components 
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime
import base64
import os
import requests
import io
from urllib.parse import urlparse, parse_qs

# ⚠️ නිවැරදි Firebase API URL එක
FIREBASE_URL = "https://pirivensmartboardmonitor-8ee4f-default-rtdb.asia-southeast1.firebasedatabase.app/"

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

# --- ස්ථාවර Dark Modern Theme CSS ---
st.markdown("""
    <style>
        .main, .stApp {
            background-color: #0b0f19 !important;
            color: #f8fafc !important;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
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
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background-color: #1f2937 !important;
            color: #ffffff !important;
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

# --- 🔐 Login Gate ---
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
            
            sub_login = st.form_submit_button("පද්ධතියට ඇතුල් වන්න 🔓", use_container_width=True)
            
            if sub_login:
                if u_name.strip() == "Admin" and u_pass.strip() == "Admin@2022":
                    st.session_state.board_logged_in = True
                    st.session_state.board_user = {"name": "K Chandaloka", "role": "Super Admin"}
                    st.success("✅ ප්‍රවේශය සාර්ථකයි!")
                    st.rerun()
                else:
                    st.error("⚠️ පරිශීලක නාමය හෝ මුරපදය වැරදියයි!")
    st.stop()

with st.sidebar:
    if st.session_state.board_user:
        u_info = st.session_state.board_user
        st.markdown(f"""
            <div style="background: #1f2937; padding: 10px; border-radius: 8px; border-left: 4px solid #0f766e; margin-bottom: 15px;">
                <div style="font-size: 13px; font-weight: bold; color: #f3f4f6;">👤 {u_info['name']}</div>
                <div style="font-size: 11px; color: #38bdf8; margin-top: 3px;">තනතුර: <b>{u_info['role']}</b></div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.header("📁 Data Source Status")
    st.success("☁️ Firebase Realtime Database Active")

col_title, col_clock = st.columns([4, 1])
with col_title:
    st.markdown("<h2 style='color: #f8fafc; margin-top: -10px;'>🏛️ Ministry of Education - Piriven Division</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 14px; font-weight: bold; margin-top: -15px;'>Central Control, Analytics & Monitoring Dashboard (Firebase)</p>", unsafe_allow_html=True)
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

# --- Firebase දත්ත ලබා ගැනීම ---
live_boards_data = {}
try:
    res_live = requests.get(f"{FIREBASE_URL}live_boards.json", timeout=4)
    if res_live.status_code == 200 and res_live.json():
        live_boards_data = res_live.json()
except Exception as e:
    st.error(f"Firebase Live Boards Read Error: {e}")

df_usage = None
try:
    res_reg = requests.get(f"{FIREBASE_URL}ministry_excel_registry.json", timeout=4)
    if res_reg.status_code == 200 and res_reg.json():
        df_usage = pd.DataFrame(res_reg.json())
except: pass

if df_usage is None or df_usage.empty:
    csv_path = "piriven_registry.csv"
    if os.path.exists(csv_path):
        df_usage = pd.read_csv(csv_path)

if df_usage is not None and not df_usage.empty:
    df_usage.columns = df_usage.columns.str.strip()
    df_usage["Census No"] = df_usage["Census No"].fillna("").astype(str).str.strip().apply(lambda x: x.split('.')[0] if '.' in x else x)
    df_usage["Piriven Name"] = df_usage["Piriven Name"].fillna("").astype(str).str.strip()
    df_usage["District"] = df_usage["District"].fillna("").astype(str).str.strip().str.title()
    df_usage["Latitude"] = pd.to_numeric(df_usage.get("Latitude", 0), errors='coerce').fillna(0.0)
    df_usage["Longitude"] = pd.to_numeric(df_usage.get("Longitude", 0), errors='coerce').fillna(0.0)
else:
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
    piriven_total_hours = 0.0
    try:
        res_sw = requests.get(f"{FIREBASE_URL}software_analytics.json", timeout=4)
        if res_sw.status_code == 200 and res_sw.json():
            sw_data = res_sw.json()
            for c_no in filtered_census_nos:
                if c_no in sw_data and isinstance(sw_data[c_no], dict):
                    for date_str, apps in sw_data[c_no].items():
                        if isinstance(apps, dict):
                            for app_name, mins in apps.items():
                                hrs = round(float(mins) / 60.0, 2)
                                app_hours_dict[app_name] = app_hours_dict.get(app_name, 0.0) + hrs
                                piriven_total_hours += hrs
    except: pass

    if selected_piriven != "All Piriven":
        st.info(f"🏛️ **{selected_piriven}** සඳහා තෝරාගත් කාල සීමාව තුළ සමස්ත භාවිත පැය ගණන (Total Runtime): **{piriven_total_hours:.2f} Hours**")

    if not app_hours_dict: app_hours_dict = {"No Software Tracked Yet": 0.0}
    software_chart_data = pd.DataFrame({"Software Application": list(app_hours_dict.keys()), "Total Active Execution (Hours)": list(app_hours_dict.values())})
    
    st.markdown("### ⏱️ Select Time Analytics View & Excel Export")
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        time_view = st.selectbox("Display Usage Data In:", ["Hours (පැය)", "Days (දවස්)", "Weeks (සති)", "Months (මාස)", "Years (අවුරුදු)"], key="time_view_filter")
    
    conversion_factor = 1.0
    unit_label = "Hours"
    if "Days" in time_view: conversion_factor, unit_label = 24.0, "Days"
    elif "Weeks" in time_view: conversion_factor, unit_label = 168.0, "Weeks"
    elif "Months" in time_view: conversion_factor, unit_label = 730.0, "Months"
    elif "Years" in time_view: conversion_factor, unit_label = 8760.0, "Years"

    software_chart_data["Total Active Execution"] = (software_chart_data["Total Active Execution (Hours)"] / conversion_factor).round(2)
    software_chart_data_view = software_chart_data[["Software Application", "Total Active Execution"]].rename(columns={"Total Active Execution": f"Total Active Execution ({unit_label})"})

    with col_v2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            software_chart_data_view.to_excel(writer, index=False, sheet_name=f"Usage_{unit_label}")
        excel_bytes = excel_buffer.getvalue()
        st.download_button(
            label=f"📥 Download Usage ({unit_label}) .xlsx",
            data=excel_bytes,
            file_name=f"Piriven_Usage_Report_{unit_label}_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    col_sw1, col_sw2 = st.columns(2)
    with col_sw1: st.bar_chart(software_chart_data_view.set_index("Software Application"))
    with col_sw2: st.dataframe(software_chart_data_view, use_container_width=True)

map_center = [7.8731, 80.7718]
map_zoom = 8
if selected_piriven != "All Piriven" and not df_filtered.empty:
    first_row = df_filtered.iloc[0]
    if float(first_row.get("Latitude", 0.0)) != 0.0: 
        map_center = [float(first_row["Latitude"]), float(first_row["Longitude"])]
        map_zoom = 14

with tab1:
    col_map, col_ctrl = st.columns([2.5, 1.2])
    with col_map:
        st.subheader("Live Board Tracking (Multi-Device & OPS Status Map)")
        m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="OpenStreetMap")
        
        for _, r in df_usage.iterrows():
            try:
                c_no = str(r.get("Census No", "")).strip()
                p_name = r.get("Piriven Name", "Unknown")
                lat = float(r.get("Latitude", 0.0))
                lon = float(r.get("Longitude", 0.0))
                
                if lat != 0.0 and lon != 0.0:
                    if c_no in live_boards_data and isinstance(live_boards_data[c_no], dict):
                        device_idx = 0
                        for d_id, d_info in live_boards_data[c_no].items():
                            if d_id != "attendance" and isinstance(d_info, dict):
                                is_online = is_device_actually_active(d_info.get("last_ping"))
                                dtype = d_info.get("device_type", "Smart Board")
                                serial_txt = d_id
                                
                                # 💡 ඩිවයිස් එක ඔන්ලයින් නම් වින්ඩෝස් පින්, ඕෆ්ලයින් (OPS/Android) නම් වෙනස් පින් වර්ණයක්
                                if is_online:
                                    pin_color = "lightgreen" if dtype == "Smart Board" else "blue"
                                    status_label = "● Active Online (Windows/OPS Mode)"
                                    status_bg = "#064e3b"
                                    status_color = "#a7f3d0"
                                else:
                                    pin_color = "orange" # OPS/Android මෝඩ් එකට මාරු වී ඇති බව හැඟවීමට
                                    status_label = "● Switched to Android/OPS (Windows Paused)"
                                    status_bg = "#78350f"
                                    status_color = "#fde68a"
                                
                                offset_lat = lat + (device_idx * 0.00015)
                                offset_lon = lon + (device_idx * 0.00015)
                                device_idx += 1

                                popup_html = f"""
                                <div style='font-family: sans-serif; font-size: 12px; line-height: 1.5; min-width: 240px; background-color: #1e293b; color: white; padding: 10px; border-radius: 8px;'>
                                    <h3 style='margin: 0 0 5px 0; color: #38bdf8;'>🏛️ {p_name}</h3>
                                    <p style='margin: 4px 0;'><b>Device Type:</b> {dtype}</p>
                                    <p style='margin: 4px 0;'><b>Serial:</b> {serial_txt}</p>
                                    <span style='background-color: {status_bg}; color: {status_color}; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{status_label}</span>
                                </div>
                                """
                                folium.Marker(
                                    location=[offset_lat, offset_lon],
                                    popup=popup_html,
                                    icon=folium.Icon(color=pin_color, icon="laptop" if dtype=="Laptop" else ("desktop" if dtype=="Smart Board" else "info-sign"), prefix="fa")
                                ).add_to(m)
                    else:
                        popup_html = f"""
                        <div style='font-family: sans-serif; font-size: 12px; line-height: 1.5; min-width: 220px; background-color: #1e293b; color: white; padding: 10px; border-radius: 8px;'>
                            <h3 style='margin: 0 0 5px 0; color: #38bdf8;'>🏛️ {p_name}</h3>
                            <p style='margin: 4px 0;'><b>Status:</b> Fully Offline / Powered Off</p>
                        </div>
                        """
                        folium.Marker(
                            location=[lat, lon],
                            popup=popup_html,
                            icon=folium.Icon(color="red", icon="remove-sign", prefix="fa")
                        ).add_to(m)
            except: pass

        st_folium(m, width=None, height=650, key="main_map_display")

    with col_ctrl:
        st.subheader("📢 Command Center")
        yt_input = st.text_input("YouTube URL:")
        if st.button("🚀 BROADCAST TO ALL BOARDS", key="broadcast_btn"):
            if yt_input:
                link_data = process_youtube_link(yt_input)
                requests.put(f"{FIREBASE_URL}current_lesson.json", json=link_data)
                st.success("✅ Broadcast Successful!")
                        
        st.write("---")
        ann_t = st.text_input("Announcement Title:")
        ann_b = st.text_area("Message Body:")
        if st.button("📢 PUSH LIVE NOTIFICATION", key="push_notif_btn"):
            if ann_t and ann_b:
                ann_data = {"title": ann_t, "body": ann_b, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                requests.put(f"{FIREBASE_URL}latest_announcement.json", json=ann_data)
                st.success("✅ Message Pushed Successfully!")

with tab3:
    st.subheader("🛠️ Technical Support & Live Chat Panel (Device-Serial Specific)")
    
    filter_serial = st.text_input("🔍 Filter by Device Serial Number (Optional):", placeholder="Enter serial to filter...")

    try:
        res_t = requests.get(f"{FIREBASE_URL}support_tickets.json", timeout=4)
        if res_t.status_code == 200 and res_t.json():
            tickets = res_t.json()
            
            ticket_rows = []
            for tid, tinfo in tickets.items():
                if isinstance(tinfo, dict):
                    c_no = str(tinfo.get("census_no", "")).strip()
                    p_name = census_to_name.get(c_no, f"Unknown ({c_no})")
                    d_serial = tinfo.get("device_serial", "N/A")
                    
                    if filter_serial and filter_serial.strip().lower() not in d_serial.lower():
                        continue

                    ticket_rows.append({
                        "Ticket ID": tid,
                        "Piriven Name": p_name,
                        "Census No": c_no,
                        "Device Type": tinfo.get("device_type", "N/A"),
                        "Device Serial": d_serial,
                        "Issue Category": tinfo.get("issue_type", "N/A"),
                        "Description": tinfo.get("description", "N/A"),
                        "Status": tinfo.get("status", "Pending"),
                        "Reported At": tinfo.get("reported_at", "N/A")
                    })
            
            if ticket_rows:
                df_tickets = pd.DataFrame(ticket_rows)
                ticket_excel_buffer = io.BytesIO()
                with pd.ExcelWriter(ticket_excel_buffer, engine='openpyxl') as writer:
                    df_tickets.to_excel(writer, index=False, sheet_name="Support Tickets")
                ticket_excel_bytes = ticket_excel_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download All Support Tickets for Supplier (.xlsx)",
                    data=ticket_excel_bytes,
                    file_name=f"Piriven_Support_Tickets_Supplier_Report_{datetime.date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.write("---")

            for tid, t in tickets.items():
                if isinstance(t, dict):
                    c_no = str(t.get("census_no", "")).strip()
                    p_name = census_to_name.get(c_no, f"Unknown ({c_no})")
                    dev_serial = t.get("device_serial", "N/A")
                    dev_type = t.get("device_type", "N/A")
                    current_status = t.get("status", "Pending")
                    
                    if selected_piriven != "All Piriven" and p_name != selected_piriven: continue
                    if filter_serial and filter_serial.strip().lower() not in dev_serial.lower(): continue
                    
                    status_badge = "🔴 Pending" if current_status == "Pending" else "🟢 Solved"
                    
                    with st.expander(f"🎫 TICKET: {tid} | 🏛️ {p_name} | 💻 [{dev_type} - {dev_serial}] - {t.get('issue_type')} ({status_badge})"):
                        st.markdown(f"**📝 Issue Description:** {t.get('description')}")
                        st.caption(f"Device Serial: {dev_serial} | Reported At: {t.get('reported_at', 'N/A')}")
                        
                        st.write("---")
                        st.markdown("💬 **Live Discussion / අමාත්‍යාංශ සංවාදය:**")
                        chats = t.get("chats", {})
                        if chats:
                            for cid, cmsg in chats.items():
                                sender_label = "🏛️ Ministry" if cmsg.get("sender") == "ministry" else f"🏫 Device ({dev_serial})"
                                st.markdown(f"**{sender_label}:** {cmsg.get('msg')}  *<small>({cmsg.get('time')})</small>*", unsafe_allow_html=True)
                        else:
                            st.info("No chat messages yet.")

                        if current_status == "Pending":
                            reply_msg = st.text_input("Type ministry reply / පිළිතුර ලියන්න:", key=f"reply_{tid}")
                            col_send, col_sol = st.columns([2, 1])
                            with col_send:
                                if st.button("↩️ Send Reply", key=f"send_{tid}"):
                                    if reply_msg:
                                        new_chat = {
                                            "sender": "ministry",
                                            "msg": reply_msg,
                                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                        requests.post(f"{FIREBASE_URL}support_tickets/{tid}/chats.json", json=new_chat)
                                        st.success("පිළිතුර යවන ලදී!")
                                        st.rerun()
                            with col_sol:
                                if st.button("✅ Mark as Solved", key=f"resolve_{tid}"):
                                    requests.patch(f"{FIREBASE_URL}support_tickets/{tid}.json", json={"status": "Solved"})
                                    st.success("ටිකට් එක Solved ලෙස යාවත්කාලීන විය!")
                                    st.rerun()
                        else:
                            st.info("🔒 මෙම ගැටලුව විසඳා ඇති බැවින් (Solved) චැට් එක වසා ඇත.")
        else:
            st.info("No reported tickets found.")
    except Exception as e:
        st.error(f"Error loading tickets: {e}")
