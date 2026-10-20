"""
Data Loader Module
Handles reading CSV and Excel files, validating dataset structure, and retrieving metadata.
"""

import io
import pandas as pd
from typing import Tuple, Dict, Any, List, Optional

def load_dataset(file_buffer_or_path, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load dataset from CSV or Excel buffer/file path.
    
    Returns:
        (DataFrame, error_message)
    """
    try:
        filename_lower = filename.lower()
        if filename_lower.endswith('.csv'):
            # Try reading UTF-8 first, fallback to latin1 or cp1252
            try:
                df = pd.read_csv(file_buffer_or_path, encoding='utf-8')
            except UnicodeDecodeError:
                if isinstance(file_buffer_or_path, io.BytesIO):
                    file_buffer_or_path.seek(0)
                try:
                    df = pd.read_csv(file_buffer_or_path, encoding='latin1')
                except Exception:
                    if isinstance(file_buffer_or_path, io.BytesIO):
                        file_buffer_or_path.seek(0)
                    df = pd.read_csv(file_buffer_or_path, encoding='cp1252')
        elif filename_lower.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_buffer_or_path, engine='openpyxl')
        else:
            return None, "Unsupported file format! Please upload a valid CSV (.csv) or Excel (.xls, .xlsx) file."
        
        if df.empty:
            return None, "The uploaded dataset is empty (0 rows or 0 columns)."
            
        return df, None
    except Exception as e:
        return None, f"Failed to load dataset: {str(e)}"

def get_dataset_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract comprehensive summary metadata of dataset.
    """
    total_rows, total_cols = df.shape
    total_cells = total_rows * total_cols
    total_missing = int(df.isna().sum().sum())
    missing_pct = round((total_missing / total_cells * 100), 2) if total_cells > 0 else 0.0
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_rows / total_rows * 100), 2) if total_rows > 0 else 0.0
    memory_usage_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)

    col_dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "total_cells": total_cells,
        "total_missing": total_missing,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": duplicate_pct,
        "memory_mb": memory_usage_mb,
        "col_dtypes": col_dtypes
    }
