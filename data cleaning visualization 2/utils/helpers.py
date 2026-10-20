"""
Helper utilities for Session State management and Export/Download operations.
"""

import io
import pandas as pd
import streamlit as st

def init_session_state():
    """Initialize Streamlit session state variables if not present."""
    if "df_raw" not in st.session_state:
        st.session_state["df_raw"] = None
    if "df_cleaned" not in st.session_state:
        st.session_state["df_cleaned"] = None
    if "filename" not in st.session_state:
        st.session_state["filename"] = "dataset"
    if "audit_log" not in st.session_state:
        st.session_state["audit_log"] = []
    if "cleaning_history" not in st.session_state:
        st.session_state["cleaning_history"] = []

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert pandas DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode('utf-8')

def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convert pandas DataFrame to Excel (.xlsx) bytes for download."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cleaned Data')
    return output.getvalue()

def reset_dataset():
    """Reset session state dataset to original uploaded dataset."""
    if st.session_state.get("df_raw") is not None:
        st.session_state["df_cleaned"] = st.session_state["df_raw"].copy()
        st.session_state["audit_log"] = ["Reset dataset to raw uploaded version."]
