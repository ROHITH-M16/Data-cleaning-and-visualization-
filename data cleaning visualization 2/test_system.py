"""
Verification Test Script for Data Cleaning & Visualization System
"""

import os
import pandas as pd
from modules.data_loader import load_dataset, get_dataset_metadata
from modules.data_cleaner import auto_clean_dataset
from modules.data_analyzer import calculate_data_quality_score, get_data_health_matrix, get_descriptive_stats
from modules.insights_generator import generate_automated_insights
from modules.report_generator import generate_html_report, export_summary_text

def run_tests():
    data_dir = r"d:\Data_Cleaning_Visualization_System\data"
    sample_files = ["sample_sales_data.csv", "sample_employee_data.xlsx", "sample_medical_data.csv"]

    for fname in sample_files:
        fpath = os.path.join(data_dir, fname)
        print(f"\n--- Testing Dataset: {fname} ---")
        df_raw, err = load_dataset(fpath, fname)
        assert err is None, f"Failed to load {fname}: {err}"
        print(f"Loaded raw shape: {df_raw.shape}")

        q_before = calculate_data_quality_score(df_raw)
        print(f"Raw Quality Score: {q_before:.1f}%")

        meta = get_dataset_metadata(df_raw)
        print(f"Metadata: missing={meta['total_missing']}, dups={meta['duplicate_rows']}")

        # Test Auto Clean
        df_cleaned, audit_log, metrics = auto_clean_dataset(df_raw)
        q_after = calculate_data_quality_score(df_cleaned)
        print(f"Cleaned shape: {df_cleaned.shape}")
        print(f"Cleaned Quality Score: {q_after:.1f}%")
        print(f"Audit log items: {len(audit_log)}")

        # Test Stats & Health Matrix
        health_df = get_data_health_matrix(df_cleaned)
        print(f"Health matrix rows: {len(health_df)}")

        num_df, cat_df = get_descriptive_stats(df_cleaned)
        print(f"Numeric stats cols: {len(num_df)}, Categorical stats cols: {len(cat_df)}")

        # Test Insights
        insights = generate_automated_insights(df_cleaned)
        print(f"Generated insights categories: {list(insights.keys())}")

        # Test Report HTML & Text
        html_report = generate_html_report(df_raw, df_cleaned, audit_log, metrics, filename=fname)
        txt_report = export_summary_text(df_cleaned, audit_log, filename=fname)
        assert len(html_report) > 500
        assert len(txt_report) > 100
        print("Reports generated successfully!")

    print("\n[SUCCESS] ALL SYSTEM VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
