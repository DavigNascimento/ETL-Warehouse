"""
Export functions for downloading dashboard data as CSV or Excel.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from typing import Optional


def export_csv(df: pd.DataFrame, filename: str = "export") -> None:
    """
    Display a download button for CSV export.
    
    Args:
        df: DataFrame to export
        filename: Base name for the file (timestamp will be appended)
    """
    if df.empty:
        st.warning("No data to export")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"{filename}_{timestamp}.csv",
        mime="text/csv",
        use_container_width=True
    )


def export_excel(
    dataframes: dict,
    filename: str = "export"
) -> None:
    """
    Display a download button for Excel export with multiple sheets.
    
    Args:
        dataframes: Dictionary mapping sheet names to DataFrames
        filename: Base name for the file (timestamp will be appended)
    """
    if not dataframes or all(df.empty for df in dataframes.values()):
        st.warning("No data to export")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create Excel file in memory
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    excel_bytes = output.getvalue()
    
    st.download_button(
        label="📥 Download as Excel",
        data=excel_bytes,
        file_name=f"{filename}_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


def export_section(
    df: pd.DataFrame,
    title: str = "Export Data",
    filename_base: str = "export"
) -> None:
    """
    Display a complete export section with CSV and Excel buttons.
    
    Args:
        df: DataFrame to export
        title: Section title
        filename_base: Base name for export files
    """
    with st.expander(f"📊 {title}"):
        col1, col2 = st.columns(2)
        
        with col1:
            export_csv(df, filename=filename_base)
        
        with col2:
            export_excel(
                {title: df},
                filename=filename_base
            )


def export_multi_sheet(
    dataframes_dict: dict,
    title: str = "Export All Data",
    filename_base: str = "export"
) -> None:
    """
    Display export section for multiple DataFrames as Excel sheets.
    
    Args:
        dataframes_dict: Dictionary of {sheet_name: DataFrame}
        title: Section title
        filename_base: Base name for export file
    """
    with st.expander(f"📊 {title}"):
        # Show summary of what will be exported
        st.write("Sheets to export:")
        for sheet_name, df in dataframes_dict.items():
            st.write(f"  • {sheet_name}: {len(df)} rows")
        
        export_excel(dataframes_dict, filename=filename_base)
