"""
Data Analyzer Module
Provides statistical EDA and Data Quality Analysis:
- Data Quality Score calculation
- Data Health Audit matrix per column
- Numerical & Categorical descriptive statistics
- Correlation matrix
- Before vs After dataset comparison
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple

def get_column_type_classification(df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    """Identify numerical, categorical, and datetime columns."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    dt_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns.tolist()
    cat_cols = [c for c in df.columns if c not in num_cols and c not in dt_cols]
    return num_cols, cat_cols, dt_cols

def calculate_data_quality_score(df: pd.DataFrame) -> float:
    """
    Calculate an overall Data Quality Score (0 to 100%).
    Based on completeness, uniqueness, and column health.
    """
    if df.empty:
        return 0.0

    total_cells = df.size
    missing_cells = df.isna().sum().sum()
    completeness_score = (1 - (missing_cells / total_cells)) * 50.0

    total_rows = len(df)
    duplicate_rows = df.duplicated().sum()
    uniqueness_score = (1 - (duplicate_rows / total_rows)) * 30.0 if total_rows > 0 else 30.0

    # Type consistency score (20 pts)
    # Check if object columns have mixed data types
    mixed_count = 0
    obj_cols = df.select_dtypes(include=['object']).columns
    for c in obj_cols:
        sample = df[c].dropna()
        if not sample.empty:
            types = set(sample.apply(type))
            if len(types) > 1:
                mixed_count += 1

    type_score = max(0.0, 20.0 - (mixed_count * 5.0))

    final_score = round(completeness_score + uniqueness_score + type_score, 1)
    return min(100.0, max(0.0, final_score))

def get_data_health_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a granular column health diagnostic table.
    """
    health_data = []
    total_rows = len(df)

    for col in df.columns:
        s = df[col]
        dtype_str = str(s.dtype)
        missing_cnt = int(s.isna().sum())
        missing_pct = round((missing_cnt / total_rows * 100), 2) if total_rows > 0 else 0.0
        unique_cnt = int(s.nunique(dropna=True))
        unique_pct = round((unique_cnt / total_rows * 100), 2) if total_rows > 0 else 0.0

        outliers_cnt = 0
        skew_val = None
        min_val = None
        max_val = None
        mean_val = None

        if pd.api.types.is_numeric_dtype(s):
            num_s = s.dropna()
            if not num_s.empty:
                min_val = round(float(num_s.min()), 2)
                max_val = round(float(num_s.max()), 2)
                mean_val = round(float(num_s.mean()), 2)
                if len(num_s) > 2:
                    skew_val = round(float(num_s.skew()), 2)

                q1 = num_s.quantile(0.25)
                q3 = num_s.quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    outliers_cnt = int(((num_s < (q1 - 1.5 * iqr)) | (num_s > (q3 + 1.5 * iqr))).sum())

        sample_vals = ", ".join([str(v) for v in s.dropna().unique()[:3]])

        health_data.append({
            "Column Name": col,
            "Data Type": dtype_str,
            "Missing Count": missing_cnt,
            "Missing (%)": missing_pct,
            "Unique Count": unique_cnt,
            "Unique (%)": unique_pct,
            "Outliers (IQR)": outliers_cnt,
            "Min": min_val if min_val is not None else "-",
            "Mean": mean_val if mean_val is not None else "-",
            "Max": max_val if max_val is not None else "-",
            "Skewness": skew_val if skew_val is not None else "-",
            "Sample Values": sample_vals
        })

    return pd.DataFrame(health_data)

def get_descriptive_stats(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate thorough descriptive statistics for numerical and categorical features.
    Returns: (num_stats_df, cat_stats_df)
    """
    num_cols, cat_cols, _ = get_column_type_classification(df)

    # Numerical Summary
    num_summary_list = []
    for col in num_cols:
        s = df[col].dropna()
        if len(s) > 0:
            mode_series = s.mode()
            mode_val = mode_series.iloc[0] if not mode_series.empty else np.nan

            num_summary_list.append({
                "Column": col,
                "Count": len(s),
                "Mean": round(float(s.mean()), 3),
                "Median (50%)": round(float(s.median()), 3),
                "Mode": round(float(mode_val), 3) if pd.notna(mode_val) else "-",
                "Std Dev": round(float(s.std()), 3),
                "Variance": round(float(s.var()), 3),
                "Min": round(float(s.min()), 3),
                "25% Q1": round(float(s.quantile(0.25)), 3),
                "75% Q3": round(float(s.quantile(0.75)), 3),
                "Max": round(float(s.max()), 3),
                "Range": round(float(s.max() - s.min()), 3),
                "Skewness": round(float(s.skew()), 3) if len(s) > 2 else 0.0,
                "Kurtosis": round(float(s.kurtosis()), 3) if len(s) > 3 else 0.0
            })
    num_df = pd.DataFrame(num_summary_list)

    # Categorical Summary
    cat_summary_list = []
    for col in cat_cols:
        s = df[col].dropna()
        if len(s) > 0:
            val_counts = s.value_counts()
            top_cat = val_counts.index[0] if not val_counts.empty else "-"
            top_freq = int(val_counts.iloc[0]) if not val_counts.empty else 0
            top_pct = round((top_freq / len(s) * 100), 2) if len(s) > 0 else 0.0

            cat_summary_list.append({
                "Column": col,
                "Count": len(s),
                "Unique Values": s.nunique(),
                "Most Common (Mode)": str(top_cat),
                "Mode Frequency": top_freq,
                "Mode Share (%)": top_pct
            })
    cat_df = pd.DataFrame(cat_summary_list)

    return num_df, cat_df

def get_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Calculate correlation matrix for numerical columns."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 2:
        return pd.DataFrame()
    return df[num_cols].corr(method=method).round(3)

def get_before_after_comparison(df_before: pd.DataFrame, df_after: pd.DataFrame) -> pd.DataFrame:
    """
    Generate side-by-side comparison matrix of key metrics before and after cleaning.
    """
    q_before = calculate_data_quality_score(df_before)
    q_after = calculate_data_quality_score(df_after)

    rows_b, cols_b = df_before.shape
    rows_a, cols_a = df_after.shape

    miss_b = int(df_before.isna().sum().sum())
    miss_a = int(df_after.isna().sum().sum())

    dup_b = int(df_before.duplicated().sum())
    dup_a = int(df_after.duplicated().sum())

    mem_b = round(df_before.memory_usage(deep=True).sum() / 1024, 1)
    mem_a = round(df_after.memory_usage(deep=True).sum() / 1024, 1)

    comp_data = [
        {"Metric": "Data Quality Score", "Before Cleaning": f"{q_before:.1f}%", "After Cleaning": f"{q_after:.1f}%", "Difference": f"{q_after - q_before:+.1f}%"},
        {"Metric": "Total Rows", "Before Cleaning": f"{rows_b:,}", "After Cleaning": f"{rows_a:,}", "Difference": f"{rows_a - rows_b:+,}"},
        {"Metric": "Total Columns", "Before Cleaning": f"{cols_b}", "After Cleaning": f"{cols_a}", "Difference": f"{cols_a - cols_b:+}"},
        {"Metric": "Missing Cells", "Before Cleaning": f"{miss_b:,}", "After Cleaning": f"{miss_a:,}", "Difference": f"{miss_a - miss_b:+,}"},
        {"Metric": "Duplicate Rows", "Before Cleaning": f"{dup_b:,}", "After Cleaning": f"{dup_a:,}", "Difference": f"{dup_a - dup_b:+,}"},
        {"Metric": "Memory Usage (KB)", "Before Cleaning": f"{mem_b:,}", "After Cleaning": f"{mem_a:,}", "Difference": f"{mem_a - mem_b:+.1f}"}
    ]

    return pd.DataFrame(comp_data)
