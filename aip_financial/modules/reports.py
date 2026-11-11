import streamlit as st
import pandas as pd
from datetime import datetime
import aip_db as db

def render_reports(user):
    st.markdown("""
    <style>
        .report-header {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 16px 20px;
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .report-summary-box {
            background: #ffffff;
            border-radius: 10px;
            padding: 14px 18px;
            border: 1px solid #cbd5e1;
            text-align: center;
        }
        .sum-title { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin: 0; }
        .sum-value { font-size: 20px; font-weight: 800; margin-top: 4px; }
        
        @media print {
            body { -webkit-print-color-adjust: exact; }
            section[data-testid="stSidebar"], .stButton, div[data-testid="stSelectbox"] {
                display: none !important;
            }
            .block-container {
                padding: 0 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin:0; font-size:22px; font-weight:800; color:#1e1b4b;'>වාර්තා ප්‍රකාශන පුවරුව (A4 Landscape)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 13.5px; margin-top: 2px;'>ප්‍රධාන වැය ශීර්ෂයන්හි ඒකාබද්ධ ප්‍රගතිය, සාරාංශය සහ මුද්‍රණ පෙරදසුන</p>", unsafe_allow_html=True)

    # 1. API හරහා දත්ත ලබා ගැනීම (No SQL Connections)
    ref_df = db.get_reference_options(user)
    v_df = db.fetch_vouchers_from_cloud()
    d_df = db.fetch_activities_from_cloud()

    # 2. වාර්තා පෙරහන (Filter)
    filter_choice = st.selectbox(
        "වාර්තා පෙරහන තෝරන්න:",
        ["සමස්ත ප්‍රගතිය (Grand Total)", "ප්‍රාග්ධන (Capital)", "පුනරාවර්තන (Recurrent)"]
    )

    if ref_df.empty:
        st.info("ප්‍රදර්ශනය කිරීමට අදාළ විෂය දත්ත කිසිවක් හමු නොවීය.")
        return

    # Allocation තීරුව සංඛ්‍යාත්මක අගයක් බවට පත් කිරීම
    if 'allocation' not in ref_df.columns:
        if 'allocation_actual' in ref_df.columns:
            ref_df['allocation'] = ref_df['allocation_actual']
        else:
            ref_df['allocation'] = 0.0
    ref_df['allocation'] = pd.to_numeric(ref_df['allocation'], errors='coerce').fillna(0.0)

    # Filter කිරීම
    if filter_choice == "ප්‍රාග්ධන (Capital)" and 'category' in ref_df.columns:
        ref_df = ref_df[ref_df['category'] == "Capital"]
    elif filter_choice == "පුනරාවර්තන (Recurrent)" and 'category' in ref_df.columns:
        ref_df = ref_df[ref_df['category'] == "Recurrent"]

    # Delete requested නොවන වලංගු ලොග පමණක් ලබා ගැනීම
    v_valid = v_df[v_df.get('delete_requested', 0) != 1] if not v_df.empty and 'delete_requested' in v_df.columns else v_df
    d_valid = d_df[d_df.get('delete_requested', 0) != 1] if not d_df.empty and 'delete_requested' in d_df.columns else d_df

    if not v_valid.empty and 'action_no' in v_valid.columns:
        v_valid['clean_act'] = v_valid['action_no'].astype(str).str.strip().str.removesuffix('.0')
    if not d_valid.empty and 'action_no' in d_valid.columns:
        d_valid['clean_act'] = d_valid['action_no'].astype(str).str.strip().str.removesuffix('.0')

    # 3. විෂය සහ ක්‍රියාකාරකම් මට්ටමින් සාරාංශ වාර්තාව සකස් කිරීම
    report_rows = []
    tot_alloc_sum = 0.0
    tot_v_spent = 0.0
    tot_d_spent = 0.0

    for idx, row in ref_df.iterrows():
        act_raw = str(row.get('action_no', ''))
        clean_act = act_raw.strip().removesuffix('.0')
        vote_code = row.get('vote_number') or row.get('vote_code') or 'N/A'
        act_name = row.get('activity_name', 'N/A')
        alloc = float(pd.to_numeric(row.get('allocation', 0), errors='coerce') or 0.0)

        # Voucher වියදම
        v_spent = 0.0
        if not v_valid.empty and 'clean_act' in v_valid.columns:
            v_match = v_valid[v_valid['clean_act'] == clean_act]
            if not v_match.empty and 'amount' in v_match.columns:
                v_spent = float(pd.to_numeric(v_match['amount'], errors='coerce').fillna(0.0).sum())

        # Program වියදම
        d_spent = 0.0
        if not d_valid.empty and 'clean_act' in d_valid.columns:
            d_match = d_valid[d_valid['clean_act'] == clean_act]
            if not d_match.empty:
                cost_col = 'actual_expenditure' if 'actual_expenditure' in d_match.columns else ('cost' if 'cost' in d_match.columns else 'actual_cost')
                if cost_col in d_match.columns:
                    d_spent = float(pd.to_numeric(d_match[cost_col], errors='coerce').fillna(0.0).sum())

        total_spent = v_spent + d_spent
        balance = alloc - total_spent
        progress = (total_spent / alloc * 100) if alloc > 0 else 0.0

        tot_alloc_sum += alloc
        tot_v_spent += v_spent
        tot_d_spent += d_spent

        report_rows.append({
            "අනු අංකය": len(report_rows) + 1,
            "Action No": act_raw,
            "වැය ශීර්ෂය": vote_code,
            "විෂය / වැඩසටහන": act_name,
            "වෙන් කළ මුදල (රු.)": alloc,
            "වවුචර වියදම (රු.)": v_spent,
            "වැඩසටහන් වියදම (රු.)": d_spent,
            "සමස්ත වියදම (රු.)": total_spent,
            "ඉතිරි ප්‍රතිපාදන (රු.)": balance,
            "ප්‍රගතිය (%)": round(progress, 1)
        })

    rep_df = pd.DataFrame(report_rows)

    tot_overall_spent = tot_v_spent + tot_d_spent
    overall_balance = tot_alloc_sum - tot_overall_spent
    overall_progress = (tot_overall_spent / tot_alloc_sum * 100) if tot_alloc_sum > 0 else 0.0

    # 4. සාරාංශ කොටු (Summary Cards)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="report-summary-box" style="border-left: 4px solid #1e40af;">
            <p class="sum-title">වෙන් කළ සමස්තය</p>
            <div class="sum-value" style="color: #1e40af;">රු. {tot_alloc_sum:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="report-summary-box" style="border-left: 4px solid #ef4444;">
            <p class="sum-title">සමස්ත වියදම</p>
            <div class="sum-value" style="color: #ef4444;">රු. {tot_overall_spent:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="report-summary-box" style="border-left: 4px solid #10b981;">
            <p class="sum-title">ඉතිරි ශේෂය</p>
            <div class="sum-value" style="color: #10b981;">රු. {overall_balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="report-summary-box" style="border-left: 4px solid #f59e0b;">
            <p class="sum-title">සමස්ත ප්‍රගතිය</p>
            <div class="sum-value" style="color: #f59e0b;">{overall_progress:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 5. වාර්තා වගුව ප්‍රදර්ශනය කිරීම (Formatted Table)
    display_df = rep_df.copy()
    display_df["වෙන් කළ මුදල (රු.)"] = display_df["වෙන් කළ මුදල (රු.)"].apply(lambda x: f"{x:,.2f}")
    display_df["වවුචර වියදම (රු.)"] = display_df["වවුචර වියදම (රු.)"].apply(lambda x: f"{x:,.2f}")
    display_df["වැඩසටහන් වියදම (රු.)"] = display_df["වැඩසටහන් වියදම (රු.)"].apply(lambda x: f"{x:,.2f}")
    display_df["සමස්ත වියදම (රු.)"] = display_df["සමස්ත වියදම (රු.)"].apply(lambda x: f"{x:,.2f}")
    display_df["ඉතිරි ප්‍රතිපාදන (රු.)"] = display_df["ඉතිරි ප්‍රතිපාදන (රු.)"].apply(lambda x: f"{x:,.2f}")
    display_df["ප්‍රගතිය (%)"] = display_df["ප්‍රගතිය (%)"].apply(lambda x: f"{x}%")

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

    # 6. Export Options (CSV බාගත කිරීම)
    col_dl1, col_dl2 = st.columns([1.5, 4.5])
    with col_dl1:
        csv_data = rep_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 මෙම වාර්තාව Excel/CSV ලෙස බාගත කරන්න",
            data=csv_data,
            file_name=f"AIP_2026_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
