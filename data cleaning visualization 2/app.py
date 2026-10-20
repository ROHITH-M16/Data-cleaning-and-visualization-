"""
Data Cleaning & Visualization System
Streamlit Main Application
"""

import os
import io
import pandas as pd
import numpy as np
import streamlit as st

# Import configuration & UI helpers
from config import APP_TITLE, APP_SUBTITLE, APP_ICON, PAGE_CONFIG, COLOR_PALETTES
from utils.ui_components import inject_custom_css, render_header, render_metric_card
from utils.helpers import (
    init_session_state, df_to_csv_bytes, df_to_excel_bytes, reset_dataset
)

# Import custom modules
from modules.data_loader import load_dataset, get_dataset_metadata
from modules.data_cleaner import (
    standardize_column_names, strip_whitespace, handle_missing_values,
    remove_duplicates, convert_column_datatype, handle_outliers_iqr,
    clean_text_formatting, auto_clean_dataset
)
from modules.data_analyzer import (
    calculate_data_quality_score, get_data_health_matrix,
    get_descriptive_stats, get_correlation_matrix,
    get_before_after_comparison, get_column_type_classification
)
from modules.visualizer import (
    plot_quality_gauge, plot_bar_chart, plot_line_chart, plot_pie_chart,
    plot_histogram, plot_scatter, plot_box_plot, plot_correlation_heatmap,
    plot_missing_matrix
)
from modules.insights_generator import generate_automated_insights
from modules.report_generator import generate_html_report, export_summary_text

# Configure Streamlit page
st.set_page_config(**PAGE_CONFIG)
inject_custom_css()
init_session_state()

# Helper to load sample dataset
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_sample_file(sample_filename: str):
    file_path = os.path.join(SAMPLE_DATA_DIR, sample_filename)
    if os.path.exists(file_path):
        df, err = load_dataset(file_path, sample_filename)
        if df is not None:
            st.session_state["df_raw"] = df.copy()
            st.session_state["df_cleaned"] = df.copy()
            st.session_state["filename"] = sample_filename
            st.session_state["audit_log"] = [f"Loaded sample dataset: '{sample_filename}'"]
            st.success(f"Successfully loaded sample dataset: **{sample_filename}** ({len(df):,} rows)")
            st.rerun()
        else:
            st.error(err)
    else:
        st.error(f"Sample dataset file '{sample_filename}' not found at {file_path}")

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/data-configuration.png", width=70)
    st.title("Navigation")
    
    page = st.radio(
        "Select Module / Page:",
        [
            "📁 Dataset Upload & Overview",
            "🧹 Interactive Data Cleaning",
            "📊 Data Quality & Health Audit",
            "📈 Exploratory Data Analysis (EDA)",
            "🎨 Interactive Visualizations",
            "💡 Automated Data Insights",
            "⚡ One-Click Auto-Clean & Export"
        ],
        index=0
    )
    
    st.markdown("---")
    if st.session_state.get("df_cleaned") is not None:
        df_c = st.session_state["df_cleaned"]
        st.markdown("### 📌 Active Dataset")
        st.caption(f"**File:** `{st.session_state.get('filename', 'Dataset')}`")
        st.caption(f"**Shape:** {df_c.shape[0]:,} rows × {df_c.shape[1]} cols")
        q_score = calculate_data_quality_score(df_c)
        st.caption(f"**Quality Score:** `{q_score:.1f}%`")

        if st.button("🔄 Reset to Raw Dataset", use_container_width=True):
            reset_dataset()
            st.success("Reset dataset to original uploaded version!")
            st.rerun()

    st.markdown("---")
    st.markdown("**Data Cleaning & Visualization System**\n*M.Sc Computer Science / Data Science Project*")

# MAIN PAGE ROUTING

# ==============================================================================
# PAGE 1: UPLOAD DATASET & OVERVIEW
# ==============================================================================
if page == "📁 Dataset Upload & Overview":
    render_header("Dataset Upload & Overview", "Upload your CSV or Excel dataset, inspect data shape, column types, and sample rows.")
    
    col_u1, col_u2 = st.columns([2, 1])
    
    with col_u1:
        st.subheader("📤 File Uploader")
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            df, err = load_dataset(uploaded_file, uploaded_file.name)
            if err:
                st.error(err)
            else:
                st.session_state["df_raw"] = df.copy()
                st.session_state["df_cleaned"] = df.copy()
                st.session_state["filename"] = uploaded_file.name
                st.session_state["audit_log"] = [f"Uploaded dataset '{uploaded_file.name}'"]
                st.success(f"Successfully uploaded dataset: **{uploaded_file.name}**")

    with col_u2:
        st.subheader("💡 Or Try Sample Datasets")
        st.caption("Click any sample dataset below to test the platform instantly:")
        if st.button("📦 Retail Sales Data (.csv)", use_container_width=True):
            load_sample_file("sample_sales_data.csv")
        if st.button("👥 Employee HR Data (.xlsx)", use_container_width=True):
            load_sample_file("sample_employee_data.xlsx")
        if st.button("🏥 Medical Patient Data (.csv)", use_container_width=True):
            load_sample_file("sample_medical_data.csv")

    st.markdown("---")

    if st.session_state.get("df_cleaned") is not None:
        df_curr = st.session_state["df_cleaned"]
        meta = get_dataset_metadata(df_curr)

        # Render KPI Cards
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            render_metric_card("Total Rows", f"{meta['total_rows']:,}", "Records", "#1E88E5")
        with k2:
            render_metric_card("Total Columns", f"{meta['total_cols']}", "Features", "#00ACC1")
        with k3:
            render_metric_card("Missing Values", f"{meta['total_missing']:,}", f"{meta['missing_pct']}% of cells", "#FF9800" if meta['total_missing'] > 0 else "#4CAF50")
        with k4:
            render_metric_card("Duplicate Rows", f"{meta['duplicate_rows']:,}", f"{meta['duplicate_pct']}% of rows", "#F44336" if meta['duplicate_rows'] > 0 else "#4CAF50")
        with k5:
            render_metric_card("Memory Size", f"{meta['memory_mb']} MB", "Deep Memory", "#7C4DFF")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("👀 Dataset Preview")
        tab_p1, tab_p2, tab_p3, tab_p4 = st.tabs(["First 10 Rows (Head)", "Last 5 Rows (Tail)", "Random Sample (10 Rows)", "Data Types Breakdown"])
        
        with tab_p1:
            st.dataframe(df_curr.head(10), use_container_width=True)
        with tab_p2:
            st.dataframe(df_curr.tail(5), use_container_width=True)
        with tab_p3:
            sample_n = min(10, len(df_curr))
            st.dataframe(df_curr.sample(sample_n, random_state=42), use_container_width=True)
        with tab_p4:
            dtype_df = pd.DataFrame([
                {"Column Name": col, "Data Type": str(dtype), "Non-Null Count": df_curr[col].count(), "Null Count": df_curr[col].isna().sum()}
                for col, dtype in df_curr.dtypes.items()
            ])
            st.dataframe(dtype_df, use_container_width=True)
    else:
        st.info("👈 Please upload a CSV or Excel dataset, or select one of the sample datasets to get started!")

# ==============================================================================
# PAGE 2: INTERACTIVE DATA CLEANING
# ==============================================================================
elif page == "🧹 Interactive Data Cleaning":
    render_header("Interactive Data Cleaning", "Detect, configure, and resolve data quality issues step-by-step.")

    if st.session_state.get("df_cleaned") is None:
        st.warning("Please upload a dataset on the 'Dataset Upload & Overview' page first.")
    else:
        df_curr = st.session_state["df_cleaned"]

        col_c1, col_c2 = st.columns([3, 1])

        with col_c1:
            st.subheader("🛠️ Data Cleaning Operations")

            # 1. Standardize Column Names
            with st.expander("1. Standardize Column Names", expanded=False):
                col_sub1, col_sub2 = st.columns([2, 1])
                with col_sub1:
                    c_case = st.selectbox("Naming Convention:", ["snake", "upper", "title", "clean"], help="snake_case, UPPER_CASE, Title Case, clean spaces")
                with col_sub2:
                    if st.button("Apply Column Renaming", use_container_width=True):
                        df_new, log = standardize_column_names(df_curr, case=c_case)
                        st.session_state["df_cleaned"] = df_new
                        st.session_state["audit_log"].append(f"Standardized column names ({c_case})")
                        st.success(log)
                        st.rerun()

            # 2. Trim Whitespace
            with st.expander("2. Strip Extra Spaces from Text Columns", expanded=False):
                str_cols = df_curr.select_dtypes(include=['object', 'string']).columns.tolist()
                st.write(f"Detected **{len(str_cols)}** text column(s): `{', '.join(str_cols) if str_cols else 'None'}`")
                if st.button("Trim Whitespace in Text Fields", use_container_width=True):
                    df_new, log = strip_whitespace(df_curr)
                    st.session_state["df_cleaned"] = df_new
                    st.session_state["audit_log"].append("Trimmed leading/trailing whitespace")
                    st.success(log)
                    st.rerun()

            # 3. Handle Missing Values
            with st.expander("3. Handle Missing Values", expanded=False):
                total_missing = df_curr.isna().sum().sum()
                st.write(f"Total Missing Cells: **{total_missing:,}**")

                m_action = st.selectbox("Action:", ["impute", "drop_rows", "drop_cols"])
                if m_action == "impute":
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        num_strat = st.selectbox("Numeric Imputation Strategy:", ["median", "mean", "zero", "constant"])
                    with col_m2:
                        cat_strat = st.selectbox("Categorical Imputation Strategy:", ["mode", "unknown", "ffill", "bfill"])

                    fill_val = None
                    if num_strat == "constant":
                        fill_val = st.number_input("Constant Fill Value:", value=0.0)

                    if st.button("Impute Missing Values", use_container_width=True):
                        df_new, log = handle_missing_values(
                            df_curr, action="impute", numeric_strategy=num_strat,
                            categorical_strategy=cat_strat, fill_value=fill_val
                        )
                        st.session_state["df_cleaned"] = df_new
                        st.session_state["audit_log"].append(log)
                        st.success(log)
                        st.rerun()

                elif m_action == "drop_rows":
                    st.caption("Drop rows with missing values in selected columns.")
                    sel_cols = st.multiselect("Target Columns:", df_curr.columns.tolist(), default=df_curr.columns.tolist())
                    if st.button("Drop Missing Rows", use_container_width=True):
                        df_new, log = handle_missing_values(df_curr, action="drop_rows", columns=sel_cols)
                        st.session_state["df_cleaned"] = df_new
                        st.session_state["audit_log"].append(log)
                        st.success(log)
                        st.rerun()

                elif m_action == "drop_cols":
                    thresh = st.slider("Missing Threshold (%) for Dropping Column:", 10.0, 90.0, 50.0)
                    if st.button("Drop High-Missing Columns", use_container_width=True):
                        df_new, log = handle_missing_values(df_curr, action="drop_cols", drop_threshold_pct=thresh)
                        st.session_state["df_cleaned"] = df_new
                        st.session_state["audit_log"].append(log)
                        st.success(log)
                        st.rerun()

            # 4. Duplicate Records
            with st.expander("4. Remove Duplicate Records", expanded=False):
                dups_cnt = df_curr.duplicated().sum()
                st.write(f"Detected Exact Duplicate Rows: **{dups_cnt:,}**")
                dup_subset = st.multiselect("Subset Columns (Leave empty for all columns):", df_curr.columns.tolist())
                if st.button("Remove Duplicate Records", use_container_width=True):
                    df_new, log = remove_duplicates(df_curr, subset=dup_subset if dup_subset else None)
                    st.session_state["df_cleaned"] = df_new
                    st.session_state["audit_log"].append(log)
                    st.success(log)
                    st.rerun()

            # 5. Convert Data Types
            with st.expander("5. Convert Column Data Types", expanded=False):
                col_t1, col_t2, col_t3 = st.columns([2, 2, 1])
                with col_t1:
                    target_col = st.selectbox("Select Column to Convert:", df_curr.columns.tolist())
                with col_t2:
                    t_type = st.selectbox("Target Data Type:", ["integer", "float", "string", "categorical", "datetime", "boolean"])
                with col_t3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Convert Type", use_container_width=True):
                        df_new, log = convert_column_datatype(df_curr, target_col, t_type)
                        st.session_state["df_cleaned"] = df_new
                        st.session_state["audit_log"].append(log)
                        st.success(log)
                        st.rerun()

            # 6. Outlier Handling (IQR)
            with st.expander("6. Handle Outliers (IQR Method)", expanded=False):
                num_cols, _, _ = get_column_type_classification(df_curr)
                if num_cols:
                    col_o1, col_o2, col_o3 = st.columns([2, 1, 1])
                    with col_o1:
                        out_col = st.selectbox("Select Numerical Column:", num_cols)
                    with col_o2:
                        iqr_fact = st.number_input("IQR Factor:", value=1.5, step=0.1)
                    with col_o3:
                        out_act = st.selectbox("Action:", ["cap", "remove", "median"])

                    # Show outlier preview
                    _, preview_log, info = handle_outliers_iqr(df_curr, out_col, action="detect", factor=iqr_fact)
                    st.caption(f"**Detected Outliers:** `{info.get('outlier_count', 0)}` records (IQR Bounds: [{info.get('lower_bound', 0):.2f}, {info.get('upper_bound', 0):.2f}])")

                    if st.button("Handle Outliers", use_container_width=True):
                        df_new, log, _ = handle_outliers_iqr(df_curr, out_col, action=out_act, factor=iqr_fact)
                        st.session_state["df_cleaned"] = df_new
                        st.session_state["audit_log"].append(log)
                        st.success(log)
                        st.rerun()
                else:
                    st.info("No numerical columns found for outlier detection.")

            # 7. Text Formatting
            with st.expander("7. Text Casing & Special Character Cleanup", expanded=False):
                str_cols = df_curr.select_dtypes(include=['object', 'string']).columns.tolist()
                if str_cols:
                    col_tx1, col_tx2 = st.columns(2)
                    with col_tx1:
                        t_col = st.selectbox("Select Text Column:", str_cols, key="text_col_select")
                        t_casing = st.selectbox("Casing Format:", ["none", "lowercase", "uppercase", "titlecase"])
                    with col_tx2:
                        rem_spec = st.checkbox("Remove Special Characters", value=False)
                        rem_dig = st.checkbox("Remove Digits/Numbers", value=False)

                    if st.button("Clean Text Formatting", use_container_width=True):
                        df_new, log = clean_text_formatting(df_curr, t_col, casing=t_casing, remove_special=rem_spec, remove_digits=rem_dig)
                        st.session_state["df_cleaned"] = df_new
                        st.session_state["audit_log"].append(log)
                        st.success(log)
                        st.rerun()

        with col_c2:
            st.subheader("📋 Cleaning Audit Log")
            st.caption("Trail of all transformations applied:")
            logs = st.session_state.get("audit_log", [])
            if logs:
                for idx, item in enumerate(logs, 1):
                    st.markdown(f"**{idx}.** {item}")
            else:
                st.caption("No operations performed yet.")

# ==============================================================================
# PAGE 3: DATA QUALITY & HEALTH AUDIT
# ==============================================================================
elif page == "📊 Data Quality & Health Audit":
    render_header("Data Quality & Health Audit", "Diagnostic scorecards, column health matrix, and before vs after cleaning metrics.")

    if st.session_state.get("df_cleaned") is None:
        st.warning("Please upload a dataset on the 'Dataset Upload & Overview' page first.")
    else:
        df_curr = st.session_state["df_cleaned"]
        df_raw = st.session_state.get("df_raw", df_curr)

        q_score = calculate_data_quality_score(df_curr)

        col_q1, col_q2 = st.columns([1, 2])

        with col_q1:
            st.plotly_chart(plot_quality_gauge(q_score), use_container_width=True)

        with col_q2:
            st.subheader("Data Health Scorecard")
            if q_score >= 85:
                st.success("🟢 **Excellent Data Quality**: Dataset is clean, complete, and structurally sound for advanced analysis.")
            elif q_score >= 65:
                st.warning("🟡 **Good Data Quality**: Dataset has minor missing values or outlier issues. Cleaning is recommended.")
            else:
                st.error("🔴 **Poor Data Quality**: Dataset contains significant missing values, duplicate rows, or type inconsistencies.")

            k1, k2, k3 = st.columns(3)
            with k1:
                render_metric_card("Total Cells", f"{df_curr.size:,}", "Grid Size", "#1E88E5")
            with k2:
                render_metric_card("Completeness", f"{100 - (df_curr.isna().sum().sum()/df_curr.size*100):.1f}%", "Non-null Ratio", "#4CAF50")
            with k3:
                render_metric_card("Uniqueness", f"{100 - (df_curr.duplicated().sum()/len(df_curr)*100):.1f}%", "Unique Rows", "#00ACC1")

        st.markdown("---")

        tab_d1, tab_d2 = st.tabs(["🔍 Column-by-Column Health Diagnostic Matrix", "🔄 Before vs After Cleaning Comparison"])

        with tab_d1:
            health_df = get_data_health_matrix(df_curr)
            st.dataframe(health_df, use_container_width=True)

        with tab_d2:
            st.subheader("Side-by-Side Dataset Metrics Comparison")
            comp_df = get_before_after_comparison(df_raw, df_curr)
            st.dataframe(comp_df, use_container_width=True)

# ==============================================================================
# PAGE 4: EXPLORATORY DATA ANALYSIS (EDA)
# ==============================================================================
elif page == "📈 Exploratory Data Analysis (EDA)":
    render_header("Exploratory Data Analysis (EDA)", "Automatic classification, descriptive statistics, and feature correlation matrices.")

    if st.session_state.get("df_cleaned") is None:
        st.warning("Please upload a dataset on the 'Dataset Upload & Overview' page first.")
    else:
        df_curr = st.session_state["df_cleaned"]
        num_cols, cat_cols, dt_cols = get_column_type_classification(df_curr)

        st.info(f"📊 Feature Breakdown: **{len(num_cols)}** Numerical, **{len(cat_cols)}** Categorical, **{len(dt_cols)}** Datetime column(s).")

        num_df, cat_df = get_descriptive_stats(df_curr)

        tab_e1, tab_e2, tab_e3 = st.tabs(["🔢 Numerical Descriptive Statistics", "🔤 Categorical Descriptive Statistics", "🔥 Correlation Matrix"])

        with tab_e1:
            st.subheader("Numerical Features Summary")
            if not num_df.empty:
                st.dataframe(num_df, use_container_width=True)
            else:
                st.caption("No numerical features found in dataset.")

        with tab_e2:
            st.subheader("Categorical Features Summary")
            if not cat_df.empty:
                st.dataframe(cat_df, use_container_width=True)
            else:
                st.caption("No categorical features found in dataset.")

        with tab_e3:
            st.subheader("Correlation Analysis")
            if len(num_cols) >= 2:
                corr_method = st.radio("Correlation Method:", ["pearson", "spearman"], horizontal=True)
                corr_df = get_correlation_matrix(df_curr, method=corr_method)

                col_cm1, col_cm2 = st.columns([1, 1])
                with col_cm1:
                    st.dataframe(corr_df, use_container_width=True)
                with col_cm2:
                    st.plotly_chart(plot_correlation_heatmap(corr_df), use_container_width=True)
            else:
                st.warning("At least 2 numerical columns are required for correlation matrix.")

# ==============================================================================
# PAGE 5: INTERACTIVE VISUALIZATIONS
# ==============================================================================
elif page == "🎨 Interactive Visualizations":
    render_header("Interactive Data Visualizations", "Build customized Plotly charts dynamically by selecting features and parameters.")

    if st.session_state.get("df_cleaned") is None:
        st.warning("Please upload a dataset on the 'Dataset Upload & Overview' page first.")
    else:
        df_curr = st.session_state["df_cleaned"]
        num_cols, cat_cols, dt_cols = get_column_type_classification(df_curr)
        all_cols = df_curr.columns.tolist()

        col_v1, col_v2 = st.columns([1, 3])

        with col_v1:
            st.subheader("Chart Builder")
            chart_type = st.selectbox(
                "Select Chart Type:",
                ["Bar Chart", "Line Chart", "Pie / Donut Chart", "Histogram", "Scatter Plot", "Box Plot", "Missing Values Map"]
            )

            color_theme = st.selectbox("Color Palette:", COLOR_PALETTES)

            # Dynamic parameters based on chart type
            x_col = None
            y_col = None
            color_col = None
            agg_func = "count"
            nbins = 30
            trend = False
            barmode = "group"

            if chart_type == "Bar Chart":
                x_col = st.selectbox("X-Axis (Category/Feature):", all_cols)
                y_col = st.selectbox("Y-Axis (Value Column - Optional):", [None] + num_cols)
                color_col = st.selectbox("Group / Color By (Optional):", [None] + cat_cols)
                if y_col:
                    agg_func = st.selectbox("Aggregation Function:", ["sum", "mean", "median", "count"])
                barmode = st.selectbox("Bar Mode:", ["group", "stack"])

            elif chart_type == "Line Chart":
                x_col = st.selectbox("X-Axis (Time/Continuous):", dt_cols + num_cols + cat_cols)
                y_col = st.selectbox("Y-Axis (Value):", num_cols)
                color_col = st.selectbox("Color By (Optional):", [None] + cat_cols)

            elif chart_type == "Pie / Donut Chart":
                x_col = st.selectbox("Category Column (Names):", cat_cols + num_cols)
                y_col = st.selectbox("Values Column (Optional):", [None] + num_cols)

            elif chart_type == "Histogram":
                x_col = st.selectbox("Feature Column:", num_cols + cat_cols)
                color_col = st.selectbox("Color By (Optional):", [None] + cat_cols)
                nbins = st.slider("Number of Bins:", 5, 100, 30)

            elif chart_type == "Scatter Plot":
                x_col = st.selectbox("X-Axis Feature:", num_cols)
                y_col = st.selectbox("Y-Axis Feature:", [c for c in num_cols if c != x_col] if len(num_cols) > 1 else num_cols)
                color_col = st.selectbox("Color By (Optional):", [None] + cat_cols + num_cols)
                trend = st.checkbox("Add OLS Trendline", value=False)

            elif chart_type == "Box Plot":
                y_col = st.selectbox("Value Column (Y-Axis):", num_cols)
                x_col = st.selectbox("Group By Category (Optional):", [None] + cat_cols)

        with col_v2:
            st.subheader(f"📊 {chart_type} Output")

            if chart_type == "Bar Chart" and x_col:
                fig = plot_bar_chart(df_curr, x_col=x_col, y_col=y_col, color_col=color_col, aggregation=agg_func, barmode=barmode, color_scale=color_theme)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Line Chart" and x_col and y_col:
                fig = plot_line_chart(df_curr, x_col=x_col, y_col=y_col, color_col=color_col)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Pie / Donut Chart" and x_col:
                fig = plot_pie_chart(df_curr, names_col=x_col, values_col=y_col)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Histogram" and x_col:
                fig = plot_histogram(df_curr, x_col=x_col, color_col=color_col, nbins=nbins, color_scale=color_theme)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Scatter Plot" and x_col and y_col:
                fig = plot_scatter(df_curr, x_col=x_col, y_col=y_col, color_col=color_col, add_trendline=trend)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Box Plot" and y_col:
                fig = plot_box_plot(df_curr, y_col=y_col, x_col=x_col)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Missing Values Map":
                fig = plot_missing_matrix(df_curr)
                st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# PAGE 6: AUTOMATED DATA INSIGHTS
# ==============================================================================
elif page == "💡 Automated Data Insights":
    render_header("Automated Data Insights", "Natural language storytelling engine revealing health alerts, distribution trends, and correlations.")

    if st.session_state.get("df_cleaned") is None:
        st.warning("Please upload a dataset on the 'Dataset Upload & Overview' page first.")
    else:
        df_curr = st.session_state["df_cleaned"]
        insights = generate_automated_insights(df_curr)

        st.subheader("🏥 1. Data Health & Completeness Findings")
        for item in insights["health"]:
            st.markdown(f"""
            <div class="insight-card-{item['type']}">
                <strong>{item['title']}</strong><br>
                <span>{item['detail']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col_in1, col_in2 = st.columns(2)

        with col_in1:
            st.subheader("🔤 2. Categorical Distribution Insights")
            if insights["categorical"]:
                for item in insights["categorical"]:
                    st.markdown(f"""
                    <div class="insight-card">
                        <strong>{item['title']}</strong><br>
                        <span>{item['detail']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No categorical insights detected.")

            st.subheader("🔗 4. Feature Correlations")
            if insights["correlations"]:
                for item in insights["correlations"]:
                    st.markdown(f"""
                    <div class="insight-card-success">
                        <strong>{item['title']}</strong><br>
                        <span>{item['detail']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No strong correlations detected.")

        with col_in2:
            st.subheader("🔢 3. Numerical Metrics & Skewness")
            if insights["numerical"]:
                for item in insights["numerical"]:
                    st.markdown(f"""
                    <div class="insight-card">
                        <strong>{item['title']}</strong><br>
                        <span>{item['detail']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No numerical insights detected.")

            st.subheader("⚠️ 5. Outlier Detection Alerts")
            if insights["outliers"]:
                for item in insights["outliers"]:
                    st.markdown(f"""
                    <div class="insight-card-warning">
                        <strong>{item['title']}</strong><br>
                        <span>{item['detail']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No severe outliers detected.")

        st.markdown("---")
        st.subheader("💡 6. Recommended Action Items")
        for item in insights["recommendations"]:
            st.markdown(f"• **{item['title']}**: {item['detail']}")

# ==============================================================================
# PAGE 7: ONE-CLICK AUTO-CLEAN & EXPORT
# ==============================================================================
elif page == "⚡ One-Click Auto-Clean & Export":
    render_header("One-Click Auto-Clean & Export", "Automatically fix missing values, duplicate rows, spaces, and outliers in 1 click, then download cleaned datasets & summary reports.")

    if st.session_state.get("df_cleaned") is None:
        st.warning("Please upload a dataset on the 'Dataset Upload & Overview' page first.")
    else:
        df_curr = st.session_state["df_cleaned"]
        df_raw = st.session_state.get("df_raw", df_curr)

        st.subheader("⚡ 1-Click Automated Cleaning Pipeline")
        st.markdown("Clicking **Auto Clean Dataset** below will execute a full standard automated cleaning sequence:")
        st.markdown("""
        - 🔹 Standardize column names to `lower_snake_case`
        - 🔹 Strip whitespace from text fields
        - 🔹 Remove 100% empty rows & columns
        - 🔹 Remove exact duplicate records
        - 🔹 Impute numeric missing values using Median & categorical using Mode
        - 🔹 Cap extreme outliers using IQR method (1.5 × IQR)
        """)

        if st.button("🚀 Auto Clean Dataset Now", type="primary", use_container_width=True):
            df_cleaned_auto, audit_log_auto, metrics_comp = auto_clean_dataset(df_raw)
            st.session_state["df_cleaned"] = df_cleaned_auto
            st.session_state["audit_log"] = audit_log_auto
            st.success("✅ Dataset successfully auto-cleaned!")
            st.rerun()

        st.markdown("---")

        # Before vs After Metrics
        comp_df = get_before_after_comparison(df_raw, df_curr)
        st.subheader("📊 Before vs After Cleaning Summary")
        st.dataframe(comp_df, use_container_width=True)

        st.markdown("---")

        # Auto Recommended Visualizations
        st.subheader("📈 Auto-Generated Recommended Visualizations")
        num_cols, cat_cols, _ = get_column_type_classification(df_curr)

        rv1, rv2 = st.columns(2)
        with rv1:
            if cat_cols:
                st.caption(f"Category Distribution: `{cat_cols[0]}`")
                fig1 = plot_bar_chart(df_curr, x_col=cat_cols[0], title=f"Records per {cat_cols[0]}")
                st.plotly_chart(fig1, use_container_width=True)
            elif num_cols:
                fig1 = plot_histogram(df_curr, x_col=num_cols[0])
                st.plotly_chart(fig1, use_container_width=True)

        with rv2:
            if len(num_cols) >= 2:
                st.caption(f"Relationship: `{num_cols[0]}` vs `{num_cols[1]}`")
                fig2 = plot_scatter(df_curr, x_col=num_cols[0], y_col=num_cols[1], add_trendline=True)
                st.plotly_chart(fig2, use_container_width=True)
            elif num_cols:
                fig2 = plot_box_plot(df_curr, y_col=num_cols[0])
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # EXPORT SECTION
        st.subheader("💾 Export & Downloads")
        st.caption("Download your cleaned dataset and summary executive reports:")

        fname = st.session_state.get("filename", "dataset").split(".")[0]

        d1, d2, d3, d4 = st.columns(4)

        with d1:
            csv_bytes = df_to_csv_bytes(df_curr)
            st.download_button(
                label="📄 Download Cleaned CSV",
                data=csv_bytes,
                file_name=f"{fname}_cleaned.csv",
                mime="text/csv",
                use_container_width=True
            )

        with d2:
            excel_bytes = df_to_excel_bytes(df_curr)
            st.download_button(
                label="📊 Download Cleaned Excel",
                data=excel_bytes,
                file_name=f"{fname}_cleaned.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with d3:
            html_report = generate_html_report(df_raw, df_curr, st.session_state.get("audit_log", []), {}, filename=fname)
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_report,
                file_name=f"{fname}_quality_report.html",
                mime="text/html",
                use_container_width=True
            )

        with d4:
            txt_report = export_summary_text(df_curr, st.session_state.get("audit_log", []), filename=fname)
            st.download_button(
                label="📝 Download Summary Text Report",
                data=txt_report,
                file_name=f"{fname}_summary_report.txt",
                mime="text/plain",
                use_container_width=True
            )
