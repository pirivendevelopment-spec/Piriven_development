import streamlit as st
import pandas as pd
import os
import plotly.express as px
import io

st.set_page_config(page_title="පිරිවෙන් සංගණන දත්ත පද්ධතිය 2026", layout="wide")

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
        .kpi-card {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #374151;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- 📂 Excel දත්ත මූලාශ්‍ර පූරණය සහ නිවැරදි ගණනය කිරීම් ---
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_file_path = os.path.join(current_dir, "Piriven_Censes_Data_Sysytem.xlsx")
if not os.path.exists(excel_file_path):
    excel_file_path = os.path.join(os.path.dirname(current_dir), "Piriven_Censes_Data_Sysytem.xlsx")

@st.cache_data
def load_and_process_census_data():
    if not os.path.exists(excel_file_path):
        return None, None, None, None, {"error": "දත්ත ගොනුව හමු නොවීය."}
    
    try:
        xls = pd.ExcelFile(excel_file_path)
        st2_df = pd.read_excel(excel_file_path, sheet_name="ST2") if "ST2" in xls.sheet_names else pd.DataFrame()
        asp2_df = pd.read_excel(excel_file_path, sheet_name="AS-P2") if "AS-P2" in xls.sheet_names else pd.DataFrame()
        teacher_df = pd.read_excel(excel_file_path, sheet_name="Teacher_Registry") if "Teacher_Registry" in xls.sheet_names else pd.DataFrame()
        users_df = pd.read_excel(excel_file_path, sheet_name="Users") if "Users" in xls.sheet_names else pd.DataFrame()

        # 1. පිරිවෙන් වර්ගීකරණය ගණනය කිරීම (ST2 හි 8 වන තීරුව / Index 7)
        pTypes = {"මූලික": 0, "මහ": 0, "විද්‍යායතන": 0, "ද්විභාෂා": 0, "සීලමාතා": 0, "විශේෂ": 0}
        pKeys = list(pTypes.keys())
        
        if not st2_df.empty and len(st2_df.columns) > 7:
            for _, row in st2_df.iloc[1:].iterrows():
                try:
                    idx = int(row.iloc[7])
                    if 1 <= idx <= 6:
                        pTypes[pKeys[idx - 1]] += 1
                except:
                    pass

        # 2. ශිෂ්‍ය සංඛ්‍යා ගණනය කිරීම (AS-P2 ෂීට් එක හරහා පැවිදි / ගිහි)
        sStat = {"monk": 0, "lay": 0}
        if not asp2_df.empty:
            for _, row in asp2_df.iloc[1:].iterrows():
                for j in range(1, len(row), 3):
                    try:
                        if j + 2 < len(row):
                            sStat["monk"] += float(row.iloc[j + 1]) if pd.notna(row.iloc[j + 1]) else 0
                            sStat["lay"] += float(row.iloc[j + 2]) if pd.notna(row.iloc[j + 2]) else 0
                    except:
                        pass

        # 3. ගුරු සුදුසුකම් ගණනය කිරීම (Teacher_Registry හි 21 වන තීරුව / Index 20)
        teacherQuals = {"පුහුණු උපාධි": 0, "ප්‍රාචීන පණ්ඩිත": 0, "ත්‍රිපිටකවේදී": 0, "උපාධිධාරී": 0, "සහතිකලාභී": 0, "වෙනත්": 0}
        qKeys = list(teacherQuals.keys())
        
        if not teacher_df.empty and len(teacher_df.columns) > 20:
            for _, row in teacher_df.iloc[1:].iterrows():
                if pd.isna(row.iloc[0]): continue
                try:
                    q = int(row.iloc[20])
                    idx = (q - 1) if (1 <= q <= 5) else 5
                    teacherQuals[qKeys[idx]] += 1
                except:
                    teacherQuals["වෙනත්"] += 1

        dashboard_metrics = {
            "totalPiriven": len(st2_df) - 1 if not st2_df.empty else 0,
            "totalStudents": int(sStat["monk"] + sStat["lay"]),
            "totalTeachers": len(teacher_df) - 1 if not teacher_df.empty else 0,
            "pirivenChart": pTypes,
            "studentChart": sStat,
            "teacherChart": teacherQuals
        }

        return st2_df, asp2_df, teacher_df, users_df, dashboard_metrics

    except Exception as e:
        return None, None, None, None, {"error": str(e)}

st2_df, asp2_df, teacher_df, users_df, metrics = load_and_process_census_data()

# --- 🔐 Session State Setup ---
if "census_logged_in" not in st.session_state: st.session_state.census_logged_in = False
if "census_user_name" not in st.session_state: st.session_state.census_user_name = ""
if "census_role" not in st.session_state: st.session_state.census_role = ""

# --- 1. 🔐 LOGIN SCREEN ---
if not st.session_state.census_logged_in:
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    top_c1, top_c2 = st.columns([6, 1])
    with top_c2:
        if st.button("⬅️ මුල් පිටුවට"):
            st.markdown('<meta http-equiv="refresh" content="0;url=http://localhost:8500">', unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        with st.form("login_screen_form"):
            st.markdown("<h3 style='color: #38bdf8; text-align: center;'>📊 පිරිවෙන් සංගණන ද්වාරය</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 13px;'>පරිශීලක නාමය හෝ සංගණන අංකය ලබා දෙන්න.</p>", unsafe_allow_html=True)
            
            uid = st.text_input("👤 පරිශීලක නාමය / සංගණන අංකය:")
            upass = st.text_input("🔑 මුරපදය (Password):", type="password")
            
            sub = st.form_submit_button("පද්ධතියට ඇතුල් වන්න 🔓")
            if sub:
                success = False
                if users_df is not None and not users_df.empty:
                    df_check = users_df.copy()
                    df_check.columns = df_check.columns.str.strip().str.lower()
                    u_col = next((c for c in df_check.columns if 'user' in c), None)
                    p_col = next((c for c in df_check.columns if 'pass' in c), None)
                    n_col = next((c for c in df_check.columns if 'name' in c and 'user' not in c), None)
                    
                    if u_col and p_col:
                        for _, u in df_check.iterrows():
                            if str(u.get(u_col, "")).strip().lower() == uid.strip().lower() and str(u.get(p_col, "")).strip() == upass.strip():
                                st.session_state.census_logged_in = True
                                st.session_state.census_user_name = str(u.get(n_col, 'පරිපාලක')) if n_col else 'පරිපාලක'
                                st.session_state.census_role = "Admin"
                                success = True
                                break

                if success:
                    st.success("✅ ප්‍රවේශය සාර්ථකයි!")
                    st.rerun()
                else:
                    st.error("⚠️ වැරදි පරිශීලක නාමයක් හෝ මුරපදයක්!")
    st.stop()

# --- 2. 🖥️ MAIN DASHBOARD & MODULES ---
with st.sidebar:
    st.markdown(f"🏛️ **ආයතනය:**\n{st.session_state.census_user_name}")
    st.markdown(f"👤 **තනතුර:** {st.session_state.census_role}")
    st.markdown("---")
    
    menu = st.radio(
        "ප්‍රධාන මෙනුව", 
        ["Dashboard", "Search Piriven", "Teachers Details", "District Reports", "Request Reports / Excel"]
    )
    
    st.markdown("---")
    if st.button("🚪 ඉවත් වන්න (Logout)"):
        st.session_state.census_logged_in = False
        st.rerun()

# 1. Dashboard Module
if menu == "Dashboard":
    st.markdown("## 📈 පිරිවෙන් සංගණන පාලක පුවරුව (Dashboard)")
    st.markdown("<p style='color: #94a3b8; font-size: 14px;'>අධ්‍යාපන අමාත්‍යාංශය - පිරිවෙන් අධ්‍යාපන අංශය</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if "error" in metrics:
        st.error(f"⚠️ දත්ත දෝෂයකි: {metrics['error']}")
    else:
        # KPI Cards / Buttons for Summary Reports
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"🏛️ මුළු පිරිවෙන් සංඛ්‍යාව: {metrics['totalPiriven']}\n\n[දිස්ත්‍රික් වාර්තා බලන්න]"):
                st.session_state.selected_report = "piriven"
                st.rerun()
        with col2:
            if st.button(f"👨‍🏫 මුළු ගුරු සංඛ්‍යාව: {metrics['totalTeachers']}\n\n[ගුරු සුදුසුකම් වාර්තා බලන්න]"):
                st.session_state.selected_report = "teacher"
                st.rerun()
        with col3:
            if st.button(f"👥 මුළු ශිෂ්‍ය සංඛ්‍යාව: {metrics['totalStudents']}\n\n[ශිෂ්‍ය වාර්තා බලන්න]"):
                st.session_state.selected_report = "student"
                st.rerun()

        st.markdown("---")
        
        # Charts Row
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("පිරිවෙන් වර්ගීකරණය")
            df_p = pd.DataFrame(list(metrics["pirivenChart"].items()), columns=["Type", "Count"])
            fig1 = px.pie(df_p, names="Type", values="Count", hole=0.5, color_discrete_sequence=px.colors.sequential.Tealgrn)
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            st.subheader("ශිෂ්‍ය ව්‍යාප්තිය (පැවිදි/ගිහි)")
            df_s = pd.DataFrame([["පැවිදි", metrics["studentChart"]["monk"]], ["ගිහි", metrics["studentChart"]["lay"]]], columns=["Category", "Count"])
            fig2 = px.pie(df_s, names="Category", values="Count", hole=0.5, color_discrete_sequence=px.colors.sequential.Sunset)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
            st.plotly_chart(fig2, use_container_width=True)

        with c3:
            st.subheader("ගුරු සුදුසුකම් ව්‍යාප්තිය")
            df_t = pd.DataFrame(list(metrics["teacherChart"].items()), columns=["Qualification", "Count"])
            fig3 = px.bar(df_t, x="Qualification", y="Count", color="Qualification")
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=300, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

# 2. Search Piriven Module
elif menu == "Search Piriven":
    st.markdown("## 🏛️ පිරිවෙන් තොරතුරු සෙවීම")
    st.markdown("---")
    if st2_df is not None and not st2_df.empty:
        q = st.text_input("සංගණන අංකය හෝ පිරිවෙන් නම ඇතුළත් කරන්න:")
        if q:
            res = st2_df[st2_df.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
            if not res.empty:
                st.dataframe(res, use_container_width=True)
            else:
                st.warning("⚠️ අදාළ පිරිවෙන සොයාගත නොහැකි විය.")

# 3. Teachers Details Module
elif menu == "Teachers Details":
    st.markdown("## 👨‍🏫 ගුරු තොරතුරු සෙවීම")
    st.markdown("---")
    if teacher_df is not None and not teacher_df.empty:
        t_q = st.text_input("ගුරුවරයාගේ නම, NIC අංකය හෝ දුරකථන අංකය ඇතුළත් කරන්න:")
        if t_q:
            t_res = teacher_df[teacher_df.astype(str).apply(lambda row: row.str.contains(t_q, case=False).any(), axis=1)]
            if not t_res.empty:
                st.dataframe(t_res, use_container_width=True)
            else:
                st.warning("⚠️ ගුරුවරුන් හමු නොවීය.")

# 4. District Reports Module
elif menu == "District Reports" or "selected_report" in st.session_state:
    st.markdown("## 📊 දිස්ත්‍රික් සහ ප්‍රමිති වාර්තා")
    st.markdown("---")
    
    rep_type = st.session_state.pop("selected_report", "piriven")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("📋 පිරිවෙන් වර්ගීකරණ වාර්තාව"):
            rep_type = "piriven"
    with col_b2:
        if st.button("📜 ගුරු සුදුසුකම් වාර්තාව"):
            rep_type = "teacher"
    with col_b3:
        if st.button("🎓 ශිෂ්‍ය සංඛ්‍යා වාර්තාව"):
            rep_type = "student"
            
    st.markdown("---")
    if rep_type == "piriven":
        st.subheader("🏛️ පිරිවෙන් වර්ගීකරණය - දිස්ත්‍රික් වාර්තාව")
        if st2_df is not None and len(st2_df.columns) > 2:
            dist_col = st2_df.columns[2]
            type_col = st2_df.columns[7] if len(st2_df.columns) > 7 else st2_df.columns[1]
            summary_table = pd.crosstab(st2_df[dist_col], st2_df[type_col])
            st.dataframe(summary_table, use_container_width=True)
    elif rep_type == "teacher":
        st.subheader("📜 ගුරු සුදුසුකම් - දිස්ත්‍රික් වාර්තාව")
        if teacher_df is not None and not teacher_df.empty:
            st.info("දිස්ත්‍රික් මට්ටමින් ගුරු සුදුසුකම් සංඛ්‍යා ලේඛන පෙන්වීම සඳහා දත්ත සකස් කර ඇත.")
    elif rep_type == "student":
        st.subheader("🎓 ශිෂ්‍ය සංඛ්‍යාව - දිස්ත්‍රික් වාර්තාව")
        if asp2_df is not None and not asp2_df.empty:
            st.info("ශිෂ්‍ය සංඛ්‍යා ව්‍යාප්තිය දිස්ත්‍රික් මට්ටමින් පෙන්වීම සඳහා දත්ත සකස් කර ඇත.")

# 5. Request Reports / Excel Export Module
elif menu == "Request Reports / Excel":
    st.markdown("## 📥 දත්ත ඉල්ලීම් සහ Excel වාර්තා බාගත කිරීම")
    st.markdown("---")
    
    req_type = st.selectbox("වාර්තා වර්ගය තෝරන්න:", ["ගුරු ලැයිස්තු (Teacher_Registry)", "පිරිවෙන් ලැයිස්තු (ST2)", "ශිෂ්‍ය සංඛ්‍යා (AS-P2)"])
    
    if st.button("📊 දත්ත පෙන්වන්න"):
        target_df = teacher_df if "ගුරු" in req_type else (st2_df if "පිරිවෙන්" in req_type else asp2_df)
        if target_df is not None and not target_df.empty:
            st.dataframe(target_df.head(100), use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                target_df.to_excel(writer, index=False, sheet_name='Report')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Excel (XLSX) ලෙස වාර්තාව බාගන්න",
                data=excel_data,
                file_name=f"Piriven_Census_Report_{os.path.basename(excel_file_path)}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ අදාළ දත්ත ගොනුව හමු නොවීය.")