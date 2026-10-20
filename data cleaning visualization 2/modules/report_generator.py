"""
Report Generator Module
Produces comprehensive HTML and Text summary reports summarizing data cleaning operations,
before vs after data health metrics, and automated analytical insights.
"""

import pandas as pd
from typing import Dict, Any, List
from modules.data_analyzer import calculate_data_quality_score, get_descriptive_stats

def generate_html_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    audit_log: List[str],
    metrics_comp: Dict[str, Any],
    filename: str = "dataset"
) -> str:
    """
    Generate a styled, self-contained HTML Executive Report.
    """
    q_before = calculate_data_quality_score(df_before)
    q_after = calculate_data_quality_score(df_after)
    
    num_df, cat_df = get_descriptive_stats(df_after)

    log_items_html = "".join([f"<li>{item}</li>" for item in audit_log]) if audit_log else "<li>No cleaning operations logged.</li>"

    # Convert stats tables to HTML
    num_table_html = num_df.to_html(classes="report-table", index=False) if not num_df.empty else "<p>No numeric columns available.</p>"
    cat_table_html = cat_df.to_html(classes="report-table", index=False) if not cat_df.empty else "<p>No categorical columns available.</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Cleaning & Quality Audit Report - {filename}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1E293B;
            background-color: #F8FAFC;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #FFFFFF;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .header {{
            border-bottom: 3px solid #0EA5E9;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #0F172A;
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .header p {{
            color: #64748B;
            margin: 0;
            font-size: 14px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #F1F5F9;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .card .label {{
            font-size: 12px;
            color: #475569;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .card .val {{
            font-size: 22px;
            font-weight: 800;
            color: #0F172A;
            margin-top: 5px;
        }}
        h2 {{
            color: #0F172A;
            font-size: 20px;
            border-left: 4px solid #0EA5E9;
            padding-left: 10px;
            margin-top: 30px;
        }}
        ul.audit-log {{
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            border-radius: 8px;
            padding: 20px 20px 20px 40px;
            color: #065F46;
        }}
        ul.audit-log li {{
            margin-bottom: 8px;
        }}
        table.report-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 13px;
        }}
        table.report-table th, table.report-table td {{
            border: 1px solid #CBD5E1;
            padding: 8px 12px;
            text-align: left;
        }}
        table.report-table th {{
            background-color: #0F172A;
            color: #FFFFFF;
        }}
        table.report-table tr:nth-child(even) {{
            background-color: #F8FAFC;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #94A3B8;
            border-top: 1px solid #E2E8F0;
            padding-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Data Cleaning & Quality Audit Report</h1>
            <p>Dataset Name: <strong>{filename}</strong> | Report Generated: Automatically by Data Cleaning & Visualization System</p>
        </div>

        <div class="grid">
            <div class="card">
                <div class="label">Initial Quality Score</div>
                <div class="val" style="color: #DC2626;">{q_before:.1f}%</div>
            </div>
            <div class="card">
                <div class="label">Final Quality Score</div>
                <div class="val" style="color: #16A34A;">{q_after:.1f}%</div>
            </div>
            <div class="card">
                <div class="label">Total Records</div>
                <div class="val">{len(df_after):,}</div>
            </div>
            <div class="card">
                <div class="label">Total Columns</div>
                <div class="val">{len(df_after.columns)}</div>
            </div>
        </div>

        <h2>Data Cleaning Transformations Log</h2>
        <ul class="audit-log">
            {log_items_html}
        </ul>

        <h2>Descriptive Statistics - Numerical Features</h2>
        {num_table_html}

        <h2>Descriptive Statistics - Categorical Features</h2>
        {cat_table_html}

        <div class="footer">
            Generated by <strong>Data Cleaning & Visualization System</strong> | College Project Edition
        </div>
    </div>
</body>
</html>
"""
    return html_content

def export_summary_text(df: pd.DataFrame, audit_log: List[str], filename: str = "dataset") -> str:
    """Generate a clean plain text summary report."""
    q_score = calculate_data_quality_score(df)
    lines = [
        "===========================================================",
        "        DATA CLEANING & ANALYSIS SUMMARY REPORT            ",
        "===========================================================",
        f"Dataset Name     : {filename}",
        f"Quality Score    : {q_score:.1f}%",
        f"Total Records    : {len(df):,}",
        f"Total Columns    : {len(df.columns)}",
        f"Missing Cells    : {df.isna().sum().sum():,}",
        f"Duplicate Rows   : {df.duplicated().sum():,}",
        "-----------------------------------------------------------",
        "CLEANING OPERATIONS LOG:",
    ]
    if audit_log:
        for log in audit_log:
            lines.append(f" - {log}")
    else:
        lines.append(" - No cleaning operations recorded.")

    lines.append("-----------------------------------------------------------")
    lines.append("COLUMN BREAKDOWN:")
    for col in df.columns:
        lines.append(f" - {col:<25} | Type: {str(df[col].dtype):<10} | Nulls: {df[col].isna().sum():<5} | Unique: {df[col].nunique()}")

    lines.append("===========================================================")
    return "\n".join(lines)
