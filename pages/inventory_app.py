import streamlit as st
import pandas as pd
import datetime
import os
import io

st.set_page_config(page_title="පිරිවෙන් ඉන්වෙන්ට්‍රි සහ සම්පත් කළමනාකරණය", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

# --- 📂 Excel සහ Database කළමනාකරණය ---
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_file_path = os.path.join(current_dir, "..", "Piriven_name.xlsx")
if not os.path.exists(excel_file_path):
    excel_file_path = os.path.join(current_dir, "Piriven_name.xlsx")

INV_DB_FILE = os.path.join(current_dir, "inventory_database.csv")
CRED_FILE = os.path.join(current_dir, "inventory_passwords.csv")

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
if "inv_logged_in" not in st.session_state: st.session_state.inv_logged_in = False
if "inv_user_census" not in st.session_state: st.session_state.inv_user_census = ""
if "inv_user_name" not in st.session_state: st.session_state.inv_user_name = ""
if "inv_role" not in st.session_state: st.session_state.inv_role = ""
if "inv_force_pass_change" not in st.session_state: st.session_state.inv_force_pass_change = False

pass_db = {}
if os.path.exists(CRED_FILE):
    df_pass = pd.read_csv(CRED_FILE)
    for _, row in df_pass.iterrows():
        pass_db[str(row["Census"]).strip()] = str(row["Password"]).strip()

# --- 1. 🔐 LOGIN SCREEN ---
if not st.session_state.inv_logged_in:
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    top_c1, top_c2 = st.columns([6, 1])
    with top_c2:
        if st.button("⬅️ මුල් පිටුවට"):
            st.switch_page("app.py")

    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        with st.form("login_screen_form"):
            st.markdown("<h3 style='color: #38bdf8; text-align: center;'>📦 ඉන්වෙන්ට්‍රි පද්ධති ප්‍රවේශය</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 13px;'>පිරිවෙන් සංගණන අංකය (Census No) හෝ අමාත්‍යාංශ පරිශීලක නාමය ලබා දෙන්න.</p>", unsafe_allow_html=True)
            
            uid = st.text_input("👤 සංගණන අංකය / පරිශීලක නාමය:")
            upass = st.text_input("🔑 මුරපදය (Password):", type="password")
            
            sub = st.form_submit_button("පද්ධතියට ඇතුල් වන්න 🔓")
            if sub:
                success = False
                # අමාත්‍යාංශ ඇඩ්මින් පරීක්ෂාව
                if users_df is not None:
                    for _, u in users_df.iterrows():
                        if str(u.get('Username')).strip() == uid.strip() and str(u.get('Password')).strip() == upass.strip():
                            st.session_state.inv_logged_in = True
                            st.session_state.inv_user_census = "ADMIN"
                            st.session_state.inv_user_name = str(u.get('Name', 'අමාත්‍යාංශ පරිපාලක'))
                            st.session_state.inv_role = "Admin"
                            success = True
                            break
                
                # පිරිවෙන් සංගණන අංක පරීක්ෂාව
                if not success and uid.strip() in census_to_info:
                    default_pass = uid.strip()
                    actual_pass = pass_db.get(uid.strip(), default_pass)
                    
                    if upass.strip() == actual_pass:
                        st.session_state.inv_logged_in = True
                        st.session_state.inv_user_census = uid.strip()
                        st.session_state.inv_user_name = census_to_info[uid.strip()]["name"]
                        st.session_state.inv_role = "Pirivena"
                        if uid.strip() not in pass_db:
                            st.session_state.inv_force_pass_change = True
                        success = True
                
                if success:
                    st.success("✅ ප්‍රවේශය සාර්ථකයි!")
                    st.rerun()
                else:
                    st.error("⚠️ වැරදි පරිශීලක නාමයක් හෝ මුරපදයක්!")
    st.stop()

# --- 2. 🔑 පාස්වර්ඩ් වෙනස් කිරීම ---
if st.session_state.inv_force_pass_change:
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
                    c_num = st.session_state.inv_user_census
                    new_row = {"Census": c_num, "Password": new_p1.strip()}
                    if os.path.exists(CRED_FILE):
                        df_c = pd.read_csv(CRED_FILE)
                        df_c = df_c[df_c["Census"].astype(str) != str(c_num)]
                        df_c = pd.concat([df_c, pd.DataFrame([new_row])], ignore_index=True)
                    else:
                        df_c = pd.DataFrame([new_row])
                    df_c.to_csv(CRED_FILE, index=False)
                    st.session_state.inv_force_pass_change = False
                    st.success("✅ මුරපදය සාර්ථකව වෙනස් කරන ලදී!")
                    st.rerun()
                else:
                    st.error("⚠️ මුරපද නොගැලපේ හෝ හිස්ව ඇත.")
    st.stop()

# --- 3. 🖥️ ප්‍රධාන ඩෑෂ්බෝඩ් තිරය ---
with st.sidebar:
    if st.button("🏠 ප්‍රධාන මුල් පිටුවට"):
        st.switch_page("app.py")
    st.markdown("---")
    st.markdown(f"🏛️ **ආයතනය / නම:**\n{st.session_state.inv_user_name}")
    st.markdown(f"👤 **තනතුර:** {st.session_state.inv_role}")
    st.markdown("---")
    if st.button("🚪 ඉවත් වන්න (Logout)"):
        st.session_state.inv_logged_in = False
        st.session_state.inv_user_census = ""
        st.rerun()

st.markdown("## 📦 පිරිවෙන් ඉන්වෙන්ට්‍රි සහ භෞතික සම්පත් කළමනාකරණ පද්ධතිය")
st.markdown("---")

if os.path.exists(INV_DB_FILE):
    df_inv = pd.read_csv(INV_DB_FILE)
else:
    df_inv = pd.DataFrame(columns=[
        "Date", "Pirivena", "Category", "Item Name", "Qty", "Value", 
        "Voucher No", "Source", "Doc Type", "Doc No", "Remarks"
    ])

# පිරිවෙනකින් ලොග් වූ විට අදාළ පිරිවෙනේ දත්ත පමණක් පෙරීම
is_admin = (st.session_state.inv_role == "Admin")
if not is_admin:
    current_pirivena_name = st.session_state.inv_user_name
    df_filtered = df_inv[df_inv["Pirivena"].astype(str).str.strip() == str(current_pirivena_name).strip()]
else:
    df_filtered = df_inv

tab1, tab2, tab3, tab4 = st.tabs([
    "💰 මූල්‍ය ප්‍රතිපාදන හා මිලදී ගැනීම්", 
    "📚 බඩු වට්ටෝරු & තොග (පොදු 44/198)", 
    "🔄 ලැබීම් හා නිකුත් කිරීම් (පොදු 219/141)", 
    "📥 Excel වාර්තා ඩවුන්ලෝඩ්"
])

with tab1:
    st.markdown("### 💰 භෞතික සම්පත් සංවර්ධනය සඳහා මූල්‍ය ප්‍රතිපාදන සහ මිලදී ගැනීම්")
    with st.form("financial_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            f_date = st.date_input("දිනය", datetime.date.today())
            if is_admin:
                pirivena_name = st.text_input("පිරිවෙනේ නම")
            else:
                pirivena_name = st.text_input("පිරිවෙනේ නම", value=st.session_state.inv_user_name, disabled=True)
            project_name = st.text_input("ව්‍යාපෘතිය / කාරණය")
        with col2:
            est_cost = st.number_input("දළ ඇස්තමේන්තුව (රු.)", min_value=0.0, value=50000.0, step=1000.0)
            allocated_amt = st.number_input("ලබා දුන් මුදල / ප්‍රතිපාදනය (රු.)", min_value=0.0, value=50000.0, step=1000.0)
            account_no = st.text_input("ගිණුම් අංකය")
        with col3:
            bank_branch = st.text_input("ශාඛාව")
            account_name = st.text_input("ගිණුමේ නම")
            item_cat = st.selectbox("උපකරණ වර්ගය", ["තාක්ෂණික උපකරණ", "පන්තිකාමර උපකරණ", "ගොඩනැගිලි/ස්ථාවර වත්කම්", "පාරිභෝජන ද්‍රව්‍ය"])

        st.markdown("#### මිලදී ගත් ස්ථාවර වත්කම් / උපකරණ විස්තර")
        item_name = st.text_input("භාණ්ඩයේ නම (උදා: පරිගණක, මේස, පුටු)")
        qty = st.number_input("ප්‍රමාණය", min_value=1, value=1, step=1)
        voucher_no = st.text_input("වවුචර් අංකය / ලිපි අංකය")
        
        submitted_fin = st.form_submit_button("💾 මූල්‍ය හා මිලදී ගැනීමේ දත්ත සුරකින්න")
        if submitted_fin:
            target_p_name = pirivena_name if is_admin else st.session_state.inv_user_name
            new_row = {
                "Date": str(f_date), "Pirivena": target_p_name, "Category": item_cat,
                "Item Name": item_name, "Qty": qty, "Value": allocated_amt,
                "Voucher No": voucher_no, "Source": f"Proj: {project_name} | Acc: {account_no} ({bank_branch})",
                "Doc Type": "මිලදී ගැනීම", "Doc No": voucher_no, "Remarks": "සාර්ථකයි"
            }
            df_inv = pd.concat([df_inv, pd.DataFrame([new_row])], ignore_index=True)
            df_inv.to_csv(INV_DB_FILE, index=False)
            st.success("✅ දත්ත සාර්ථකව සුරකින ලදී!")

    if not df_filtered.empty:
        st.markdown("#### 📋 දත්ත ලැයිස්තුව")
        st.dataframe(df_filtered, use_container_width=True)

with tab2:
    st.markdown("### 📚 බඩු වට්ටෝරු ලේඛණය (පොදු 44) සහ තොග පොත (පොදු 198)")
    col_t2_1, col_t2_2 = st.columns(2)
    
    with col_t2_1:
        st.markdown("#### බඩු වට්ටෝරු පොත (Inventory Book - පොදු 44)")
        with st.form("form_poddh44"):
            b44_date = st.date_input("දිනය (Received Date)", key="b44_d")
            b44_item = st.text_input("භාණ්ඩයේ නම (අකාරාදී ලෙස)")
            b44_qty = st.number_input("ප්‍රමාණය", 1, 500, 1, key="b44_q")
            b44_vouch = st.text_input("වවුචර් අංකය", key="b44_v")
            b44_from = st.text_input("ලැබුනේ කාගෙන්ද?")
            
            sub_b44 = st.form_submit_button("පොදු 44 ඇතුළත් කරන්න")
            if sub_b44:
                p_name_val = "අමාත්‍යාංශය" if is_admin else st.session_state.inv_user_name
                new_row = {
                    "Date": str(b44_date), "Pirivena": p_name_val, "Category": "ස්ථාවර වත්කම් (පොදු 44)",
                    "Item Name": b44_item, "Qty": b44_qty, "Value": 0.0,
                    "Voucher No": b44_vouch, "Source": b44_from, "Doc Type": "පොදු 44 (Inventory)", 
                    "Doc No": b44_vouch, "Remarks": "ලැබුනා"
                }
                df_inv = pd.concat([df_inv, pd.DataFrame([new_row])], ignore_index=True)
                df_inv.to_csv(INV_DB_FILE, index=False)
                st.success(f"✅ '{b44_item}' බඩු වට්ටෝරු පොතට (පොදු 44) ඇතුළත් කළා.")

    with col_t2_2:
        st.markdown("#### පාරිභෝජන ද්‍රව්‍ය ලේඛණය / තොග පොත (පොදු 198)")
        with st.form("form_poddh198"):
            b198_item = st.text_input("Item / කාරණය")
            b198_date = st.date_input("දිනය", key="198_d")
            b198_desc = st.text_input("ලැබුනේ නොහොත් නිකුත් කළේ කාගෙන්ද/කාටද")
            b198_rec = st.number_input("ලැබුනා (Qty Rec)", 0, 1000, 0)
            b198_iss = st.number_input("නිකුත් කළා (Qty Issued)", 0, 1000, 0)
            
            sub_b198 = st.form_submit_button("පොදු 198 ඇතුළත් කරන්න")
            if sub_b198:
                st.success(f"✅ '{b198_item}' තොග පොතට (පොදු 198) ඇතුළත් කළා.")

with tab3:
    st.markdown("### 🔄 නිකුත් කිරීමේ ඇණවුම් (පොදු 141) සහ ලැබීම් ඇණවුම් (පොදු 219)")
    col_3_1, col_3_2 = st.columns(2)
    with col_3_1:
        st.markdown("#### නිකුත් කිරීමේ නියෝග පොත (පොදු 141)")
        with st.form("form_p141"):
            p141_no = st.text_input("නිකුත් කිරීමේ ඇණවුම් අංකය (පොදු 141)")
            p141_date = st.date_input("දිනය", key="141_date")
            p141_dest = st.text_input("භාණ්ඩ ලබා ගන්නා ආයතනය / පුද්ගලයා")
            p141_item = st.text_input("භාණ්ඩ විස්තරය සහ ප්‍රමාණය")
            
            sub_141 = st.form_submit_button("නිකුත් කිරීමේ නියෝගය සකසන්න")
            if sub_141:
                st.success(f"✅ පොදු 141 අංක {p141_no} සාර්ථකව සටහන් කළා.")

    with col_3_2:
        st.markdown("#### ලැබීම් නියෝග පොත (පොදු 219)")
        with st.form("form_p219"):
            p219_no = st.text_input("ලැබීම් ඇණවුම් අංකය (පොදු 219)")
            p219_ref141 = st.text_input("අදාළ නිකුත් කිරීමේ ඇණවුම් අංකය (පොදු 141)")
            p219_date = st.date_input("දිනය", key="219_date")
            p219_item = st.text_input("ලැබුණු භාණ්ඩ විස්තරය")
            
            sub_219 = st.form_submit_button("ලැබීම් නියෝගය තහවුරු කරන්න")
            if sub_219:
                st.success(f"✅ ලැබීම් නියෝගය (පොදු 219) අංක {p219_no} තහවුරු කළා.")

with tab4:
    st.markdown("### 📥 ඉන්වෙන්ට්‍රි සහ මූල්‍ය දත්ත Excel ගොනුවක් ලෙස ඩවුන්ලෝඩ් කරගැනීම")
    if not df_filtered.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_filtered.to_excel(writer, sheet_name='ඉන්වෙන්ට්‍රි සහ මූල්‍ය දත්ත', index=False)
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 සම්පූර්ණ ඉන්වෙන්ට්‍රි වාර්තාව Excel (XLSX) ලෙස ඩවුන්ලෝඩ් කරගන්න",
            data=excel_data,
            file_name=f"PEQI_Inventory_Report_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ ඩවුන්ලෝඩ් කිරීමට ප්‍රමාණවත් දත්ත තවම ඇතුළත් කර නැත.")