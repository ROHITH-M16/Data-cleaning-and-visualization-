"""
Data Cleaner Module
Provides individual and automated dataset cleaning transformations:
- Column standardization
- Whitespace stripping
- Missing value imputation & row/column dropping
- Duplicate record removal
- Data type casting
- Outlier detection & handling via IQR method
- Text casing & special character cleaning
- One-Click Auto-Clean pipeline
"""

import re
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional

def standardize_column_names(df: pd.DataFrame, case: str = "snake") -> Tuple[pd.DataFrame, str]:
    """
    Standardize column names.
    Options: 'snake' (lower_snake_case), 'upper' (UPPER_CASE), 'title' (Title Case), 'clean' (strip only)
    """
    df_clean = df.copy()
    original_cols = list(df_clean.columns)
    new_cols = []

    for col in original_cols:
        c = str(col).strip()
        if case == "snake":
            c = re.sub(r'[^\w\s]', '', c)
            c = re.sub(r'\s+', '_', c).lower()
        elif case == "upper":
            c = re.sub(r'[^\w\s]', '', c)
            c = re.sub(r'\s+', '_', c).upper()
        elif case == "title":
            c = c.title()
        elif case == "clean":
            c = re.sub(r'\s+', ' ', c)
        new_cols.append(c)

    # Ensure unique column names
    seen = {}
    unique_cols = []
    for c in new_cols:
        if c in seen:
            seen[c] += 1
            unique_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            unique_cols.append(c)

    df_clean.columns = unique_cols
    log = f"Standardized {len(original_cols)} column names (Format: {case})."
    return df_clean, log

def strip_whitespace(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Tuple[pd.DataFrame, str]:
    """Trim leading and trailing whitespace from string columns."""
    df_clean = df.copy()
    target_cols = columns if columns else df_clean.select_dtypes(include=['object', 'string']).columns.tolist()
    modified = 0

    for col in target_cols:
        if col in df_clean.columns and df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str).str.strip().replace({'nan': np.nan, 'None': np.nan, '': np.nan})
            modified += 1

    log = f"Trimmed whitespace in {modified} string column(s)."
    return df_clean, log

def handle_missing_values(
    df: pd.DataFrame,
    action: str = "impute",
    columns: Optional[List[str]] = None,
    numeric_strategy: str = "median",
    categorical_strategy: str = "mode",
    fill_value: Any = None,
    drop_threshold_pct: float = 50.0
) -> Tuple[pd.DataFrame, str]:
    """
    Handle missing values in dataset.
    Actions:
    - 'drop_rows': Drop rows with any missing values in specified columns.
    - 'drop_cols': Drop columns with missing percentage > drop_threshold_pct.
    - 'impute': Impute missing numeric and categorical values based on chosen strategies.
    """
    df_clean = df.copy()
    initial_missing = df_clean.isna().sum().sum()

    if initial_missing == 0:
        return df_clean, "No missing values detected."

    target_cols = columns if columns else df_clean.columns.tolist()

    if action == "drop_rows":
        before_rows = len(df_clean)
        df_clean = df_clean.dropna(subset=target_cols)
        dropped_rows = before_rows - len(df_clean)
        log = f"Dropped {dropped_rows} row(s) containing missing values in selected columns."

    elif action == "drop_cols":
        cols_to_drop = []
        for col in target_cols:
            missing_pct = df_clean[col].isna().mean() * 100
            if missing_pct >= drop_threshold_pct:
                cols_to_drop.append(col)
        df_clean = df_clean.drop(columns=cols_to_drop)
        log = f"Dropped {len(cols_to_drop)} column(s) with > {drop_threshold_pct}% missing values: {cols_to_drop}."

    elif action == "impute":
        imputed_count = 0
        for col in target_cols:
            if col not in df_clean.columns or df_clean[col].isna().sum() == 0:
                continue

            if pd.api.types.is_numeric_dtype(df_clean[col]):
                if numeric_strategy == "mean":
                    val = df_clean[col].mean()
                elif numeric_strategy == "median":
                    val = df_clean[col].median()
                elif numeric_strategy == "zero":
                    val = 0
                elif numeric_strategy == "constant":
                    val = fill_value if fill_value is not None else 0
                else:
                    val = df_clean[col].median()
                df_clean[col] = df_clean[col].fillna(val)
                imputed_count += 1
            else:
                if categorical_strategy == "mode":
                    mode_val = df_clean[col].mode()
                    val = mode_val[0] if not mode_val.empty else "Unknown"
                elif categorical_strategy == "unknown":
                    val = "Unknown"
                elif categorical_strategy == "constant":
                    val = fill_value if fill_value is not None else "Unknown"
                elif categorical_strategy == "ffill":
                    df_clean[col] = df_clean[col].ffill()
                    continue
                elif categorical_strategy == "bfill":
                    df_clean[col] = df_clean[col].bfill()
                    continue
                else:
                    val = "Unknown"
                df_clean[col] = df_clean[col].fillna(val)
                imputed_count += 1

        log = f"Imputed missing values across {imputed_count} column(s) (Numeric: {numeric_strategy}, Categorical: {categorical_strategy})."

    else:
        log = "No action performed on missing values."

    return df_clean, log

def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = 'first') -> Tuple[pd.DataFrame, str]:
    """Remove duplicate rows based on all or subset of columns."""
    df_clean = df.copy()
    before_rows = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=subset, keep=keep)
    removed = before_rows - len(df_clean)
    log = f"Removed {removed} duplicate record(s)."
    return df_clean, log

def convert_column_datatype(df: pd.DataFrame, column: str, target_type: str) -> Tuple[pd.DataFrame, str]:
    """
    Convert data type of a single column safely.
    target_type: 'integer', 'float', 'string', 'categorical', 'datetime', 'boolean'
    """
    df_clean = df.copy()
    if column not in df_clean.columns:
        return df_clean, f"Column '{column}' not found."

    try:
        if target_type == "integer":
            # Coerce numeric, then convert float to Int64 (nullable int)
            numeric_vals = pd.to_numeric(df_clean[column], errors='coerce')
            df_clean[column] = numeric_vals.astype('Int64')
        elif target_type == "float":
            df_clean[column] = pd.to_numeric(df_clean[column], errors='coerce').astype('float64')
        elif target_type == "string":
            df_clean[column] = df_clean[column].astype(str)
        elif target_type == "categorical":
            df_clean[column] = df_clean[column].astype('category')
        elif target_type == "datetime":
            df_clean[column] = pd.to_datetime(df_clean[column], errors='coerce')
        elif target_type == "boolean":
            df_clean[column] = df_clean[column].astype(bool)
        log = f"Converted column '{column}' to {target_type} type."
    except Exception as e:
        log = f"Failed to convert column '{column}' to {target_type}: {str(e)}"

    return df_clean, log

def handle_outliers_iqr(
    df: pd.DataFrame,
    column: str,
    action: str = "cap",
    factor: float = 1.5
) -> Tuple[pd.DataFrame, str, Dict[str, Any]]:
    """
    Detect and handle outliers using Interquartile Range (IQR) method.
    IQR = Q3 - Q1
    Lower Bound = Q1 - (factor * IQR)
    Upper Bound = Q3 + (factor * IQR)
    
    Actions: 'cap' (Winsorize), 'remove' (drop outlier rows), 'median' (replace with median)
    """
    df_clean = df.copy()
    info = {"outlier_count": 0, "lower_bound": None, "upper_bound": None}

    if column not in df_clean.columns or not pd.api.types.is_numeric_dtype(df_clean[column]):
        return df_clean, f"Column '{column}' is not numeric.", info

    series = df_clean[column].dropna()
    if len(series) < 4:
        return df_clean, f"Insufficient numeric records in '{column}' for outlier detection.", info

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return df_clean, f"IQR is 0 for column '{column}'. No outliers detected.", info

    lower_bound = q1 - (factor * iqr)
    upper_bound = q3 + (factor * iqr)

    outliers_mask = (df_clean[column] < lower_bound) | (df_clean[column] > upper_bound)
    outlier_count = int(outliers_mask.sum())

    info = {
        "outlier_count": outlier_count,
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound)
    }

    if outlier_count == 0:
        return df_clean, f"No outliers detected in '{column}' (Bounds: [{lower_bound:.2f}, {upper_bound:.2f}]).", info

    if action == "cap":
        df_clean[column] = df_clean[column].clip(lower=lower_bound, upper=upper_bound)
        log = f"Capped {outlier_count} outlier(s) in '{column}' to range [{lower_bound:.2f}, {upper_bound:.2f}]."
    elif action == "remove":
        df_clean = df_clean[~outliers_mask]
        log = f"Removed {outlier_count} row(s) containing outliers in '{column}'."
    elif action == "median":
        med_val = series.median()
        df_clean.loc[outliers_mask, column] = med_val
        log = f"Replaced {outlier_count} outlier(s) in '{column}' with median value ({med_val:.2f})."
    else:
        log = f"Detected {outlier_count} outlier(s) in '{column}'."

    return df_clean, log, info

def clean_text_formatting(
    df: pd.DataFrame,
    column: str,
    casing: str = "none",
    remove_special: bool = False,
    remove_digits: bool = False
) -> Tuple[pd.DataFrame, str]:
    """Clean text column formatting: casing, special characters, digits."""
    df_clean = df.copy()
    if column not in df_clean.columns:
        return df_clean, f"Column '{column}' not found."

    s = df_clean[column].astype(str).str.strip()

    if casing == "lowercase":
        s = s.str.lower()
    elif casing == "uppercase":
        s = s.str.upper()
    elif casing == "titlecase":
        s = s.str.title()

    if remove_special:
        s = s.apply(lambda val: re.sub(r'[^\w\s]', '', val) if pd.notna(val) else val)

    if remove_digits:
        s = s.apply(lambda val: re.sub(r'\d+', '', val) if pd.notna(val) else val)

    s = s.replace({'nan': np.nan, 'None': np.nan, '': np.nan})
    df_clean[column] = s
    log = f"Cleaned text formatting in '{column}' (Casing: {casing}, Remove special: {remove_special}, Remove digits: {remove_digits})."
    return df_clean, log

def auto_clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
    """
    Advanced Feature: One-Click Auto-Clean Dataset.
    Executes a complete standard data cleaning pipeline:
    1. Standardize column names (snake_case)
    2. Strip whitespace from text fields
    3. Remove duplicate rows
    4. Handle 100% empty rows & columns
    5. Impute numeric missing values (median) & categorical (mode)
    6. Cap numeric outliers using IQR method
    7. Generate comprehensive audit log & metrics comparison
    """
    df_curr = df.copy()
    audit_log = []

    initial_rows, initial_cols = df_curr.shape
    initial_missing = int(df_curr.isna().sum().sum())
    initial_dups = int(df_curr.duplicated().sum())

    # 1. Standardize Column Names
    df_curr, log1 = standardize_column_names(df_curr, case="snake")
    audit_log.append(f"✓ {log1}")

    # 2. Strip Whitespace
    df_curr, log2 = strip_whitespace(df_curr)
    audit_log.append(f"✓ {log2}")

    # 3. Drop completely empty rows and columns
    before_r, before_c = df_curr.shape
    df_curr = df_curr.dropna(how='all', axis=0).dropna(how='all', axis=1)
    dropped_empty_r = before_r - df_curr.shape[0]
    dropped_empty_c = before_c - df_curr.shape[1]
    if dropped_empty_r > 0 or dropped_empty_c > 0:
        audit_log.append(f"✓ Dropped {dropped_empty_r} fully empty row(s) and {dropped_empty_c} fully empty column(s).")

    # 4. Remove Duplicate Rows
    df_curr, log4 = remove_duplicates(df_curr)
    audit_log.append(f"✓ {log4}")

    # 5. Impute Missing Values
    df_curr, log5 = handle_missing_values(df_curr, action="impute", numeric_strategy="median", categorical_strategy="mode")
    audit_log.append(f"✓ {log5}")

    # 6. Outlier Handling (Cap IQR for numeric columns)
    num_cols = df_curr.select_dtypes(include=[np.number]).columns.tolist()
    total_outliers_capped = 0
    for col in num_cols:
        df_curr, log6, info = handle_outliers_iqr(df_curr, col, action="cap", factor=1.5)
        total_outliers_capped += info.get("outlier_count", 0)

    if total_outliers_capped > 0:
        audit_log.append(f"✓ Capped {total_outliers_capped} extreme outlier(s) across {len(num_cols)} numeric column(s) using IQR method.")

    final_rows, final_cols = df_curr.shape
    final_missing = int(df_curr.isna().sum().sum())
    final_dups = int(df_curr.duplicated().sum())

    metrics_comparison = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "rows_removed": initial_rows - final_rows,
        "initial_cols": initial_cols,
        "final_cols": final_cols,
        "initial_missing": initial_missing,
        "final_missing": final_missing,
        "missing_fixed": initial_missing - final_missing,
        "initial_dups": initial_dups,
        "final_dups": final_dups,
        "dups_removed": initial_dups - final_dups,
        "outliers_capped": total_outliers_capped
    }

    return df_curr, audit_log, metrics_comparison
