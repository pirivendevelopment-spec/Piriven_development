import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import db

def render_reports(user):
    # Super Admin පරීක්ෂාව
    if user.get("role") != "Super Admin":
        st.error("මෙම පද්ධති වාර්තා බැලීමට 'Super Admin' බලතල අවශ්‍ය වේ.")
        return

    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h3 style="margin: 0; color: #1e1b4b; font-weight: 800; font-size: 20px;">පද්ධති ප්‍රගති වාර්තා (A4 Landscape)</h3>
        <p style="margin: 4px 0 0; color: #64748b; font-size: 12px;">ප්‍රධාන වැය ශීර්ෂයන්හි ඒකාබද්ධ ප්‍රගතිය, සාරාංශය සහ මුද්‍රණ පෙරදසුන</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. පාලක පැනලය (Filter & Actions)
    f_col1, f_col2 = st.columns([1.5, 2])
    with f_col1:
        filter_option = st.selectbox(
            "වාර්තා පෙරහන තෝරන්න:",
            ["සමස්ත ප්‍රගතිය (Grand Total)", "පුනරාවර්තන (Recurrent)", "ප්‍රාග්ධන (Capital)"],
            index=0
        )
    
    cat_map = {
        "සමස්ත ප්‍රගතිය (Grand Total)": "All",
        "පුනරාවර්තන (Recurrent)": "Recurrent",
        "ප්‍රාග්ධන (Capital)": "Capital"
    }
    sel_filter = cat_map[filter_option]

    # 2. Database වෙතින් දත්ත කියවීම
    conn = db.get_connection()
    ref_df = pd.read_sql_query("SELECT * FROM aip_reference", conn)
    v_df = pd.read_sql_query("SELECT * FROM voucher_log", conn)
    d_df = pd.read_sql_query("SELECT * FROM data_log", conn)
    conn.close()

    if ref_df.empty:
        st.warning("AIP Reference දත්ත හමු නොවීය.")
        return

    # Filter යෙදීම
    if sel_filter != "All":
        ref_df = ref_df[ref_df['category'] == sel_filter]

    # ගණනය කිරීම්
    t_alloc = 0.0
    t_spent = 0.0
    total_weighted_physical = 0.0
    table_rows_html = ""
    export_rows = []

    for _, row in ref_df.iterrows():
        act = row['action_no']
        vote = row['vote_number']
        name = row['activity_name']
        alloc = float(row['allocation'] or 0.0)

        # වියදම් එකතුව
        v_s = v_df[v_df['action_no'] == act]['amount'].sum() if not v_df.empty else 0.0
        d_s = d_df[d_df['action_no'] == act]['actual_cost'].sum() if not d_df.empty else 0.0
        spent = v_s + d_s

        t_alloc += alloc
        t_spent += spent

        fin_prog = (spent / alloc * 100) if alloc > 0 else 0.0
        phy_prog = min(100, int(fin_prog * 1.1)) if alloc > 0 else (100 if spent > 0 else 0)

        total_weighted_physical += (alloc * phy_prog)

        alloc_mn = f"{(alloc / 1000000):.2f}"
        spent_mn = f"{(spent / 1000000):.2f}"
        fin_str = f"{fin_prog:.1f}%"
        phy_str = f"{phy_prog}%"

        table_rows_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #000; text-align: center;">{act}</td>
            <td style="padding: 8px; border: 1px solid #000; text-align: center;">{vote}</td>
            <td style="padding: 8px; border: 1px solid #000;">{name}</td>
            <td style="padding: 8px; border: 1px solid #000; text-align: right; padding-right: 8px;">{alloc_mn}</td>
            <td style="padding: 8px; border: 1px solid #000; text-align: right; padding-right: 8px;">{spent_mn}</td>
            <td style="padding: 8px; border: 1px solid #000; text-align: center; font-weight: bold;">{fin_str}</td>
            <td style="padding: 8px; border: 1px solid #000; text-align: center;">{phy_str}</td>
        </tr>
        """

        export_rows.append({
            "Action No": act,
            "Vote Number": vote,
            "Main Activity Description": name,
            "Allocation (Mn)": alloc_mn,
            "Expenditure (Mn)": spent_mn,
            "Fin.%": fin_str,
            "Phy.%": phy_str
        })

    # සමස්ත ප්‍රතිශතයන්
    fin_prog_total = f"{(t_spent / t_alloc * 100):.1f}%" if t_alloc > 0 else "0.0%"
    phy_prog_total = f"{(total_weighted_physical / t_alloc):.0f}%" if t_alloc > 0 else "0%"
    t_alloc_mn = f"{(t_alloc / 1000000):.2f} Mn"
    t_spent_mn = f"{(t_spent / 1000000):.2f} Mn"
    current_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # Excel Export බොත්තම ඉහළට දැමීම
    with f_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        exp_df = pd.DataFrame(export_rows)
        st.download_button(
            label="📥 Excel (.csv) ලෙස බාගත කරන්න",
            data=exp_df.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"AIP_2026_Report_{sel_filter}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 3. කලින් සාදන ලද සම්පූර්ණ A4 Landscape HTML ආකෘතිය සහ Print Engine එක
    report_complete_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap" rel="stylesheet">
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
      <style>
        * {{ font-family: 'Inter', 'Noto Sans Sinhala', sans-serif; box-sizing: border-box; }}
        body {{ margin: 0; padding: 10px; background: transparent; color: black; }}
        
        .print-btn-bar {{
            display: flex; justify-content: flex-end; margin-bottom: 15px;
        }}
        .btn-print {{
            background: #1e40af; color: white; border: none; padding: 12px 24px;
            border-radius: 8px; cursor: pointer; font-weight: 700; font-size: 14px;
            display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(30,64,175,0.25);
            transition: 0.2s;
        }}
        .btn-print:hover {{ background: #1e3a8a; transform: translateY(-1px); }}

        /* මුද්‍රණය වන කඩදාසි පත්‍රිකාව (Exact CSS) */
        .printable-sheet {{
            background: white; width: 100%; padding: 25px;
            border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            border: 1px solid #e2e8f0;
        }}
        .report-header {{ text-align: center; margin-bottom: 25px; border-bottom: 2px solid #0f172a; padding-bottom: 12px; }}
        .report-header h1 {{ margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 0.5px; }}
        .report-header h2 {{ margin: 6px 0; font-size: 16px; font-weight: 700; color: #334155; }}
        .report-header h3 {{ margin: 12px 0 6px; font-size: 14px; font-weight: 800; text-decoration: underline; text-underline-offset: 4px; }}
        .report-header p {{ font-size: 11px; color: #475569; margin: 4px 0 0; }}

        .summary-grid {{ display: flex; justify-content: space-between; background: #f8fafc; border: 1.5px solid #0f172a; border-radius: 8px; margin-bottom: 20px; }}
        .sum-box {{ flex: 1; border-right: 1.5px solid #0f172a; padding: 10px; display: flex; flex-direction: column; align-items: center; gap: 4px; }}
        .sum-box.last {{ border-right: none; }}
        .sum-label {{ font-size: 11.5px; font-weight: 700; color: #475569; }}
        .sum-val {{ font-size: 18px; font-weight: 800; }}
        .sum-val.blue {{ color: #1e40af; }}
        .sum-val.red {{ color: #b91c1c; }}
        .sum-val.green {{ color: #15803d; }}

        .report-table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; background: white; }}
        .report-table th {{ background: #f1f5f9; color: #0f172a; padding: 9px 6px; border: 1px solid #0f172a; font-size: 12px; font-weight: 800; text-align: center; }}
        .report-table td {{ padding: 8px 6px; border: 1px solid #000; font-size: 11.5px; vertical-align: middle; color: #0f172a; }}
        .report-table tbody tr:nth-child(even) {{ background: #f8fafc; }}
        .total-row td {{ font-weight: 800; background: #f1f5f9; border: 1.5px solid #0f172a !important; padding: 10px 6px; }}

        .signature-section {{ display: flex; justify-content: space-between; margin-top: 50px; page-break-inside: avoid; }}
        .sig-col {{ text-align: center; width: 28%; }}
        .dots {{ margin-bottom: 30px; color: #64748b; }}
        .label-si {{ font-size: 12.5px; font-weight: 700; margin: 0; color: #0f172a; }}
        .label-en {{ font-size: 11px; margin: 2px 0 0; color: #475569; }}
      </style>
    </head>
    <body>
      <div class="print-btn-bar">
        <button onclick="printReportOnly()" class="btn-print">
            <i class="fas fa-print"></i> මුද්‍රණය කරන්න (A4 Landscape Print)
        </button>
      </div>

      <div id="landscape-report-sheet" class="printable-sheet">
        <div class="report-header">
            <h1>MINISTRY OF EDUCATION</h1>
            <h2>Pirivena Education Division - AIP 2026</h2>
            <h3>Consolidated Physical & Financial Progress Summary Report</h3>
            <p>Generated on: <span>{current_date}</span> | Category: <span>{filter_option}</span></p>
        </div>

        <div class="summary-grid">
            <div class="sum-box">
                <span class="sum-label">සමස්ත ප්‍රතිපාදන</span>
                <span class="sum-val blue">{t_alloc_mn}</span>
            </div>
            <div class="sum-box">
                <span class="sum-label">සමස්ත වියදම</span>
                <span class="sum-val red">{t_spent_mn}</span>
            </div>
            <div class="sum-box">
                <span class="sum-label">මූල්‍ය ප්‍රගතිය</span>
                <span class="sum-val green">{fin_prog_total}</span>
            </div>
            <div class="sum-box last">
                <span class="sum-label">භෞතික ප්‍රගතිය</span>
                <span class="sum-val green">{phy_prog_total}</span>
            </div>
        </div>

        <table class="report-table">
            <thead>
                <tr>
                    <th style="width: 8%;">Action No</th>
                    <th style="width: 15%;">Vote Number</th>
                    <th style="width: 41%; text-align: left; padding-left: 12px;">Main Activity Description</th>
                    <th style="width: 13%; text-align: right; padding-right: 12px;">Allocation (Mn)</th>
                    <th style="width: 13%; text-align: right; padding-right: 12px;">Expenditure (Mn)</th>
                    <th style="width: 5%;">Fin.%</th>
                    <th style="width: 5%;">Phy.%</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
            <tfoot>
                <tr class="total-row">
                    <td colspan="3" style="text-align: right; padding-right: 15px;">Grand Total (සමස්ත එකතුව):</td>
                    <td style="text-align: right; padding-right: 12px;">{t_alloc_mn}</td>
                    <td style="text-align: right; padding-right: 12px;">{t_spent_mn}</td>
                    <td colspan="2" style="background: #f8fafc;"></td>
                </tr>
            </tfoot>
        </table>

        <div class="signature-section">
            <div class="sig-col">
                <p class="dots">.........................................</p>
                <p class="label-si">සකස් කළේ</p>
                <p class="label-en">Subject Officer</p>
            </div>
            <div class="sig-col">
                <p class="dots">.........................................</p>
                <p class="label-si">නිර්දේශය</p>
                <p class="label-en">Director (Development)</p>
            </div>
            <div class="sig-col">
                <p class="dots">.........................................</p>
                <p class="label-si">අනුමත කිරීම</p>
                <p class="label-en">Addl. Secretary (Pirivena)</p>
            </div>
        </div>
      </div>

      <script>
        function printReportOnly() {{
            const content = document.getElementById("landscape-report-sheet").outerHTML;
            const win = window.open('', '', 'width=1200,height=850');
            win.document.write(`
                <html>
                <head>
                    <title>AIP 2026 - Progress Report Print</title>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+Sinhala:wght@400;600;700;800&display=swap" rel="stylesheet">
                    <style>
                        @page {{
                            size: A4 landscape;
                            margin: 10mm;
                        }}
                        body {{
                            font-family: 'Inter', 'Noto Sans Sinhala', sans-serif;
                            margin: 0; padding: 0; background: white; color: black;
                        }}
                        .printable-sheet {{ width: 100%; background: white; }}
                        .report-header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #0f172a; padding-bottom: 10px; }}
                        .report-header h1 {{ margin: 0; font-size: 20px; font-weight: 800; }}
                        .report-header h2 {{ margin: 4px 0; font-size: 15px; font-weight: 700; color: #334155; }}
                        .report-header h3 {{ margin: 8px 0 4px; font-size: 13px; font-weight: 800; text-decoration: underline; }}
                        .report-header p {{ font-size: 10px; color: #475569; margin: 2px 0 0; }}

                        .summary-grid {{ display: flex; justify-content: space-between; border: 1.5px solid #0f172a; border-radius: 6px; margin-bottom: 16px; background: #f8fafc; }}
                        .sum-box {{ flex: 1; border-right: 1.5px solid #0f172a; padding: 8px; display: flex; flex-direction: column; align-items: center; }}
                        .sum-box.last {{ border-right: none; }}
                        .sum-label {{ font-size: 11px; font-weight: 700; color: #475569; }}
                        .sum-val {{ font-size: 16px; font-weight: 800; }}
                        
                        .report-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                        .report-table th, .report-table td {{ border: 1px solid black !important; padding: 6px 4px; font-size: 11px; }}
                        .report-table th {{ background: #f1f5f9; font-weight: 800; }}
                        .report-table thead {{ display: table-header-group; }}
                        .report-table tr {{ page-break-inside: avoid !important; }}
                        .total-row td {{ font-weight: 800; background: #f1f5f9; border: 1.5px solid black !important; }}

                        .signature-section {{ display: flex; justify-content: space-between; margin-top: 35px; page-break-inside: avoid; }}
                        .sig-col {{ text-align: center; width: 28%; }}
                        .dots {{ margin-bottom: 25px; }}
                        .label-si {{ font-size: 12px; font-weight: 700; margin: 0; }}
                        .label-en {{ font-size: 10px; margin: 2px 0 0; color: #475569; }}
                    </style>
                </head>
                <body>
                    ${{content}}
                </body>
                </html>
            `);
            win.document.close();
            win.focus();
            setTimeout(() => {{
                win.print();
                win.close();
            }}, 600);
        }}
      </script>
    </body>
    </html>
    """

    # Streamlit Component එකක් ලෙස සෘජුවම Embed කිරීම (Full Width & Scrollable Preview)
    components.html(report_complete_html, height=850, scrolling=True)