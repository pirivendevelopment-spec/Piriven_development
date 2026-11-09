import sys
import requests
import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime
import base64
import os
import smtplib
import hashlib
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from urllib.parse import urlparse, parse_qs

# ⚠️ Firebase API URL
FIREBASE_URL = "https://pirivensmartboardmonitor-8ee4f-default-rtdb.asia-southeast1.firebasedatabase.app/"

SRI_LANKA_DISTRICTS = [
    "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya", 
    "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar", 
    "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara", "Trincomalee", 
    "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla", 
    "Monaragala", "Ratnapura", "Kegalle"
]

# 💡 Helper functions
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def get_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

def check_admin_login(user, pwd):
    if user == "Admin" and pwd == "Admin@2022":
        st.session_state["user_role"] = "super_admin"
        return True
    try:
        res = requests.get(f"{FIREBASE_URL}system_admins/{user}.json", timeout=4)
        if res.status_code == 200 and res.json():
            if make_hashes(pwd) == res.json().get("password_hash"):
                st.session_state["user_role"] = "standard_admin"
                return True
    except: pass
    return False

# --- UI Setup ---
st.set_page_config(page_title="Ministry Admin Dashboard", layout="wide")
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

# --- Login Logic ---
if not st.session_state["logged_in"]:
    col_l1, col_l2, col_l3 = st.columns([1, 1.3, 1])
    with col_l2:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center; color: #38bdf8;'>🏛️ Ministry Admin Portal</h3>", unsafe_allow_html=True)
            u = st.text_input("👤 Username").strip()
            p = st.text_input("🔑 Password", type="password")
            if st.form_submit_button("පද්ධතියට ඇතුල් වන්න 🔓", use_container_width=True):
                if check_admin_login(u, p):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = u
                    st.success("✅ ප්‍රවේශය සාර්ථකයි!")
                    st.rerun()
                else:
                    st.error("⚠️ පරිශීලක නාමය හෝ මුරපදය වැරදියයි!")
    st.stop()

# --- Main Dashboard Header ---
st.title("🏛️ Ministry of Education - Piriven Division")
st.markdown("Central Control, Analytics & Monitoring Dashboard (Firebase)")
if st.button("🔒 LOGOUT"): 
    st.session_state["logged_in"] = False
    st.rerun()

st.write("---")

# Fetch Data from Firebase
reg_data = requests.get(f"{FIREBASE_URL}ministry_excel_registry.json").json() or []
df = pd.DataFrame(reg_data)

tabs = st.tabs(["🗺️ Live Map & Remote Control", "📊 Analytics & Usage Stats", "🛠️ Support Tickets & Live Chat"])

with tabs[1]:
    st.subheader("📊 Performance Analytics & Leaderboard")
    if not df.empty:
        if "Monthly Usage (Hours)" in df.columns:
            df["Usage (Minutes)"] = df.get("Monthly Usage (Hours)", 0) * 60
            df_top10 = df.sort_values(by="Usage (Minutes)", ascending=False).head(10)
            if "Piriven Name" in df.columns:
                st.bar_chart(df_top10.set_index("Piriven Name")["Usage (Minutes)"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Leaderboard (.xlsx)",
                data=get_excel_bytes(df),
                file_name="Piriven_Leaderboard.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col2:
            st.download_button(
                label="📥 Download Full Registry (.xlsx)",
                data=get_excel_bytes(df),
                file_name="Full_Registry.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Registry දත්ත හමු නොවීය.")

with tabs[0]:
    st.subheader("🗺️ Live Map Tracking")
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=8)
    st_folium(m, width=1000, height=550)

with tabs[2]:
    st.subheader("🛠️ Technical Support & Live Chat")
    try:
        res_t = requests.get(f"{FIREBASE_URL}support_tickets.json", timeout=4)
        if res_t.status_code == 200 and res_t.json():
            tickets = res_t.json()
            for tid, tinfo in tickets.items():
                if isinstance(tinfo, dict):
                    st.write(f"**Ticket ID:** {tid} | **Issue:** {tinfo.get('issue_type')} | **Status:** {tinfo.get('status')}")
        else:
            st.info("ගැටලු වාර්තා (Tickets) කිසිවක් නොමැත.")
    except:
        st.error("Support tickets ලබාගැනීමේ දෝෂයක් ඇති විය.")
