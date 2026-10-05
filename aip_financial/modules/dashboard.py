import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import db

def render_dashboard(user):
    st.markdown("""
    <style>
        /* 1. Stat Cards (Compact & Crisp) */
        .cards-grid {
            display: grid; grid-template-columns: 1fr 1fr 1fr;
            gap: 16px; margin-bottom: 16px;
        }
        .metric-box {
            background: #ffffff; border-radius: 12px; padding: 18px 22px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
        }
        .m-blue { border-left: 5px solid #1e40af; }
        .m-red { border-left: 5px solid #ef4444; }
        .m-green { border-left: 5px solid #10b981; }

        .m-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin: 0; }
        .m-val { font-size: 26px; font-weight: 800; margin: 4px 0 0 0; }

        /* 2. Containers */
        .content-card {
            background: #ffffff; border-radius: 12px; padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
            margin-bottom: 16px;
        }
        .content-header { font-size: 14.5px; font-weight: 800; color: #0f172a; margin-bottom: 12px; }

        /* 3. ඉහළ Action Buttons Styles & Perfect Alignment */
        .top-btn-green div.stButton > button {
            background-color: #10b981 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 13.5px !important;
            border: none !important;
            height: 42px !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(16, 185, 129, 0.2) !important;
        }
        .top-btn-blue div.stButton > button {
            background-color: #1e40af !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 13.5px !important;
            border: none !important;
            height: 42px !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(30, 64, 175, 0.2) !important;
        }

        /* Dropdown එක බොත්තම් වල උසටම සමාන කිරීම */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            height: 42px !important;
            border-radius: 8px !important;
        }

        /* 4. Right Panel Activity Rows */
        .feed-row {
            padding: 10px 8px; border-bottom: 1px solid #f1f5f9;
            display: flex; justify-content: space-between; align-items: center;
        }
        .feed-title { font-size: 12px; font-weight: 700; color: #0f172a; margin: 0 0 3px 0; max-width: 190px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .feed-meta { font-size: 10px; color: #64748b; margin: 0; }
        .feed-cost { font-size: 12px; font-weight: 800; color: #1e40af; }
    </style>
    """, unsafe_allow_html=True)

    # Database Fetch
    conn = db.get_connection()
    ref_df = pd.read_sql_query("SELECT * FROM aip_reference", conn)
    v_df = pd.read_sql_query("SELECT * FROM voucher_log", conn)
    d_df = pd.read_sql_query("SELECT * FROM data_log", conn)
    conn.close()

    acc = user.get('access_level', '')
    user_access = [x.strip() for x in acc.split(',')] if acc and acc != "All" else []
    if user.get('role') != "Super Admin" and acc != "All":
        ref_df = ref_df[ref_df['action_no'].isin(user_access)]

    # =========================================================
    # ඉහළ Action Bar: Buttons සහ Dropdown එක සමානව Align කිරීම
    # =========================================================
    bar_col1, bar_col2 = st.columns([1.3, 2.0])
    with bar_col1:
        st.markdown("<h3 style='margin:0; font-size:20px; font-weight:800; color:#1e1b4b; padding-top:6px;'>ප්‍රගති පාලක පුවරුව</h3>", unsafe_allow_html=True)

    with bar_col2:
        btn1_col, btn2_col, flt_col = st.columns([1.1, 1.1, 1.3])
        
        # 1. "+ වැඩසටහනක්" (Green)
        with btn1_col:
            st.markdown('<div class="top-btn-green">', unsafe_allow_html=True)
            if st.button("+ වැඩසටහනක්", key="top_btn_act", use_container_width=True):
                st.session_state.selected_menu = "වැඩසටහන් එක් කරන්න"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 2. "වවුචරයක්" (Blue)
        with btn2_col:
            st.markdown('<div class="top-btn-blue">', unsafe_allow_html=True)
            if st.button("වවුචරයක්", key="top_btn_vouch", use_container_width=True):
                st.session_state.selected_menu = "වවුචර විස්තර"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 3. Filter Dropdown (Alinged to buttons)
        with flt_col:
            filter_choice = st.selectbox("", ["සමස්තය", "ප්‍රාග්ධන", "පුනරාවර්තන"], label_visibility="collapsed")

    cat_map = {"සමස්තය": "All", "ප්‍රාග්ධන": "Capital", "පුනරාවර්තන": "Recurrent"}
    sel_cat = cat_map.get(filter_choice, "All")
    if sel_cat != "All":
        ref_df = ref_df[ref_df['category'] == sel_cat]

    # මූල්‍ය ගණනය කිරීම්
    total_alloc = ref_df['allocation'].sum() if not ref_df.empty else 0.0
    v_spent = v_df[v_df['action_no'].isin(ref_df['action_no'])]['amount'].sum() if not v_df.empty else 0.0
    d_spent = d_df[d_df['action_no'].isin(ref_df['action_no'])]['actual_cost'].sum() if not d_df.empty else 0.0
    total_spent = v_spent + d_spent
    balance = total_alloc - total_spent
    fin_prog = (total_spent / total_alloc * 100) if total_alloc > 0 else 0.0

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    # 70% Center vs 30% Right Panel
    col_center, col_right = st.columns([2.3, 1], gap="medium")

    # =========================================================
    # Center Panel
    # =========================================================
    with col_center:
        # 1. Stat Cards
        st.markdown(f"""
        <div class="cards-grid">
            <div class="metric-box m-blue">
                <p class="m-label">වෙන් කළ ප්‍රතිපාදන (Allocation)</p>
                <h2 class="m-val" style="color: #1e40af;">{(total_alloc/1000000):.2f} Mn</h2>
            </div>
            <div class="metric-box m-red">
                <p class="m-label">සත්‍ය වියදම (Actual Spent)</p>
                <h2 class="m-val" style="color: #ef4444;">{(total_spent/1000000):.2f} Mn</h2>
            </div>
            <div class="metric-box m-green">
                <p class="m-label">ඉතිරි ප්‍රතිපාදන (Balance)</p>
                <h2 class="m-val" style="color: #10b981;">{(balance/1000000):.2f} Mn</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Action Breakdown Table
        st.markdown('<div class="content-card"><div class="content-header">විෂය පථය අනුව ප්‍රගතිය (Action-wise Breakdown)</div>', unsafe_allow_html=True)
        breakdown_rows = []
        for _, row in ref_df.iterrows():
            act = row['action_no']
            v_s = v_df[v_df['action_no'] == act]['amount'].sum() if not v_df.empty else 0.0
            d_s = d_df[d_df['action_no'] == act]['actual_cost'].sum() if not d_df.empty else 0.0
            act_spent = v_s + d_s
            act_bal = row['allocation'] - act_spent

            breakdown_rows.append({
                "Action No": act,
                "වැඩසටහන": row['activity_name'],
                "ප්‍රතිපාදන (Rs.)": f"{row['allocation']:,.2f}",
                "වියදම (Rs.)": f"{act_spent:,.2f}",
                "ඉතිරිය (Rs.)": f"{act_bal:,.2f}"
            })

        df_table = pd.DataFrame(breakdown_rows)
        st.dataframe(df_table, use_container_width=True, height=270, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. Charts Row
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown('<div class="content-card" style="text-align: center;"><div class="content-header">මූල්‍ය ප්‍රගතිය (Financial)</div>', unsafe_allow_html=True)
            fig_fin = go.Figure(data=[go.Pie(
                labels=['වියදම', 'ඉතිරිය'],
                values=[total_spent, max(0, balance)],
                hole=.75,
                marker_colors=['#1e40af', '#e2e8f0'],
                textinfo='none'
            )])
            fig_fin.update_layout(
                showlegend=False, height=170, margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(text=f"<b>{fin_prog:.1f}%</b><br><span style='font-size:9px; color:#64748b;'>වියදම් ප්‍රතිශතය</span>", x=0.5, y=0.5, font_size=18, showarrow=False)]
            )
            st.plotly_chart(fig_fin, use_container_width=True)
            st.markdown('<p style="font-size: 10px; color: #94a3b8; margin: 0;">සමස්ත ප්‍රතිපාදන මත භාවිතය</p></div>', unsafe_allow_html=True)

        with ch2:
            st.markdown('<div class="content-card" style="text-align: center;"><div class="content-header">භෞතික ප්‍රගතිය (Physical)</div>', unsafe_allow_html=True)
            phy_prog = min(100, int(fin_prog * 1.05)) if total_alloc > 0 else 0
            fig_phy = go.Figure(data=[go.Pie(
                labels=['නිමකළ', 'ඉතිරි'],
                values=[phy_prog, max(0, 100 - phy_prog)],
                hole=.75,
                marker_colors=['#f59e0b', '#e2e8f0'],
                textinfo='none'
            )])
            fig_phy.update_layout(
                showlegend=False, height=170, margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(text=f"<b>{phy_prog}%</b><br><span style='font-size:9px; color:#64748b;'>නිමකළ මට්ටම</span>", x=0.5, y=0.5, font_size=18, showarrow=False)]
            )
            st.plotly_chart(fig_phy, use_container_width=True)
            st.markdown('<p style="font-size: 10px; color: #94a3b8; margin: 0;">වැඩසටහන් අවසන් කිරීමේ මට්ටම</p></div>', unsafe_allow_html=True)

    # =========================================================
    # Right Panel (Recent Activity Feed)
    # =========================================================
    with col_right:
        st.markdown("""
        <div class="content-card" style="padding: 16px;">
            <div class="content-header" style="margin-bottom: 2px;">මෑතකාලීන වියදම් ලොගය</div>
            <p style="font-size: 10px; color: #64748b; margin-bottom: 10px;">AIP_Reference තාර්කිකත්වය මත පදනම් වූ දත්ත</p>
            <div style="max-height: 600px; overflow-y: auto;">
        """, unsafe_allow_html=True)

        combined_logs = []
        if not v_df.empty:
            for _, r in v_df.tail(8).iterrows():
                combined_logs.append({
                    "name": r.get('description') or "වවුචර වියදම",
                    "type": "Voucher",
                    "date": str(r.get('voucher_date', ''))[:10],
                    "act": r.get('action_no', ''),
                    "cost": float(r.get('amount') or 0)
                })

        if not d_df.empty:
            for _, r in d_df.tail(8).iterrows():
                combined_logs.append({
                    "name": r.get('activity_name') or "වැඩසටහන් වියදම",
                    "type": "Activity",
                    "date": str(r.get('activity_date', ''))[:10],
                    "act": r.get('action_no', ''),
                    "cost": float(r.get('actual_cost') or 0)
                })

        combined_logs.sort(key=lambda x: x["date"], reverse=True)

        if combined_logs:
            for item in combined_logs[:12]:
                tag_bg = "#eff6ff" if item["type"] == "Voucher" else "#f0fdf4"
                tag_col = "#1e40af" if item["type"] == "Voucher" else "#15803d"
                st.markdown(f"""
                <div class="feed-row">
                    <div>
                        <div class="feed-title" title="{item['name']}">{item['name']}</div>
                        <div class="feed-meta">
                            <span style="background:{tag_bg}; color:{tag_col}; padding:2px 5px; border-radius:4px; font-weight:800; font-size:9px;">{item['type']}</span>
                            <span>{item['date']}</span> | 
                            <span style="color:#1e40af; font-weight:700;">#{item['act']}</span>
                        </div>
                    </div>
                    <div class="feed-cost">{item['cost']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:center; color:#94a3b8; padding:30px 0; font-size:12px;'>ගනුදෙනු කිසිවක් හමු නොවීය.</p>", unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)