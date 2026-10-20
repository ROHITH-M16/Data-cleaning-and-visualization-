"""
Insights Generator Module
Automated Data Storytelling Engine:
Generates natural language data insights, correlation discoveries, missingness warnings,
skewness alerts, and data quality recommendations.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List

def generate_automated_insights(df: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
    """
    Scans the DataFrame and outputs structured insights categorized by domain.
    Returns dict of insight cards with fields: 'type' ('info', 'success', 'warning', 'danger'), 'title', 'detail'.
    """
    insights = {
        "health": [],
        "categorical": [],
        "numerical": [],
        "correlations": [],
        "outliers": [],
        "recommendations": []
    }

    if df.empty:
        insights["health"].append({"type": "warning", "title": "Empty Dataset", "detail": "No records available for analysis."})
        return insights

    total_rows, total_cols = df.shape
    total_cells = total_rows * total_cols
    missing_cells = int(df.isna().sum().sum())
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    duplicate_rows = int(df.duplicated().sum())

    # --- 1. HEALTH & COMPLEATNESS INSIGHTS ---
    if missing_cells == 0:
        insights["health"].append({
            "type": "success",
            "title": "Complete Dataset",
            "detail": "Zero missing values detected across all columns. Dataset completeness is 100%."
        })
    else:
        insights["health"].append({
            "type": "warning" if missing_pct < 15 else "danger",
            "title": "Missing Values Alert",
            "detail": f"Dataset contains {missing_cells:,} missing cell(s) ({missing_pct:.2f}% of total data)."
        })

    if duplicate_rows > 0:
        insights["health"].append({
            "type": "warning",
            "title": "Duplicate Records Detected",
            "detail": f"Found {duplicate_rows:,} exact duplicate row(s) ({duplicate_rows/total_rows*100:.1f}% of total rows)."
        })
    else:
        insights["health"].append({
            "type": "success",
            "title": "No Duplicate Rows",
            "detail": "All records in the dataset are unique."
        })

    # High missingness columns
    high_miss_cols = [c for c in df.columns if (df[c].isna().mean() * 100) > 20.0]
    if high_miss_cols:
        insights["health"].append({
            "type": "danger",
            "title": "High Missingness Columns",
            "detail": f"The following column(s) have > 20% missing data: {', '.join(high_miss_cols)}. Consider dropping or imputing."
        })

    # --- 2. CATEGORICAL INSIGHTS ---
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    for col in cat_cols[:4]: # Top 4 categorical columns
        s = df[col].dropna()
        if not s.empty:
            vc = s.value_counts()
            top_name = vc.index[0]
            top_cnt = vc.iloc[0]
            share = (top_cnt / len(s)) * 100
            n_unique = s.nunique()

            insights["categorical"].append({
                "type": "info",
                "title": f"Dominant Category in '{col}'",
                "detail": f"'{top_name}' is the most frequent category with {top_cnt:,} occurrence(s) ({share:.1f}% share) across {n_unique} unique categories."
            })

    # --- 3. NUMERICAL METRICS & EXTREMES ---
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in num_cols[:4]: # Top 4 numeric columns
        s = df[col].dropna()
        if len(s) > 2:
            mean_v = s.mean()
            med_v = s.median()
            min_v = s.min()
            max_v = s.max()
            skew_v = s.skew()

            detail_msg = f"Ranges from {min_v:,.2f} to {max_v:,.2f} (Mean: {mean_v:,.2f}, Median: {med_v:,.2f})."
            if abs(skew_v) > 1.0:
                direction = "right (positive)" if skew_v > 0 else "left (negative)"
                detail_msg += f" Displayed substantial {direction} skewness ({skew_v:.2f})."

            insights["numerical"].append({
                "type": "info" if abs(skew_v) <= 1.0 else "warning",
                "title": f"Summary Distribution: '{col}'",
                "detail": detail_msg
            })

    # --- 4. CORRELATION INSIGHTS ---
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        strong_corrs = []
        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                c1, c2 = num_cols[i], num_cols[j]
                val = corr.loc[c1, c2]
                if abs(val) >= 0.5 and not np.isnan(val):
                    rel = "strong positive" if val > 0 else "strong negative"
                    strong_corrs.append((c1, c2, val, rel))

        for c1, c2, val, rel in strong_corrs[:5]:
            insights["correlations"].append({
                "type": "success" if val > 0 else "info",
                "title": f"Correlation: {c1} & {c2}",
                "detail": f"Identified a {rel} linear relationship (r = {val:+.2f})."
            })

        if not strong_corrs:
            insights["correlations"].append({
                "type": "info",
                "title": "Low Linear Correlation",
                "detail": "No numeric column pairs exhibited strong correlation (|r| ≥ 0.5)."
            })

    # --- 5. OUTLIER INSIGHTS ---
    for col in num_cols:
        s = df[col].dropna()
        if len(s) > 4:
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                out_cnt = int(((s < lower) | (s > upper)).sum())
                if out_cnt > 0:
                    pct = (out_cnt / len(s)) * 100
                    insights["outliers"].append({
                        "type": "warning" if pct < 10 else "danger",
                        "title": f"Outliers in '{col}'",
                        "detail": f"Detected {out_cnt:,} outlier value(s) ({pct:.1f}% of column values) outside IQR bounds [{lower:.2f}, {upper:.2f}]."
                    })

    # --- 6. ACTIONABLE RECOMMENDATIONS ---
    if missing_cells > 0:
        insights["recommendations"].append({
            "type": "info",
            "title": "Impute or Drop Missing Values",
            "detail": "Use the Data Cleaning tab to fill missing numerical values with median and categorical values with mode."
        })
    if duplicate_rows > 0:
        insights["recommendations"].append({
            "type": "info",
            "title": "Remove Duplicate Rows",
            "detail": "Deduplicate your dataset before statistical modeling to prevent biased coefficient estimation."
        })
    if len(insights["outliers"]) > 0:
        insights["recommendations"].append({
            "type": "info",
            "title": "Cap Extreme Outliers",
            "detail": "Apply IQR capping to numerical variables to prevent extreme values from distorting line charts and mean statistics."
        })

    return insights
