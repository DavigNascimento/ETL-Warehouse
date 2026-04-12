"""
Reusable KPI cards and metrics components for dashboard summaries.
"""

import streamlit as st
from typing import Dict, Any


def metric_card(
    title: str,
    value: Any,
    format_spec: str = "",
    delta: Any = None,
    delta_format: str = "+",
    icon: str = "📊"
) -> None:
    """
    Display a single metric card with optional delta.
    
    Args:
        title: Metric title
        value: Metric value
        format_spec: Python format specifier (e.g., ".2f", ",")
        delta: Optional delta value for comparison
        delta_format: Delta format ("+", "%", "abs")
        icon: Icon emoji for card
    """
    if format_spec:
        if "%f" in format_spec or ".f" in format_spec:
            formatted_value = f"{value:{format_spec}}"
        else:
            formatted_value = f"{value:{format_spec}}"
    else:
        formatted_value = str(value)
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"## {icon}")
        with col2:
            st.markdown(f"**{title}**")
            st.markdown(f"### {formatted_value}")
            
            if delta is not None:
                if delta_format == "%":
                    delta_text = f"{delta:+.1f}%"
                elif delta_format == "+":
                    delta_text = f"{delta:+.0f}"
                else:
                    delta_text = f"{abs(delta):.0f}"
                
                delta_color = "green" if delta >= 0 else "red"
                st.markdown(f":{delta_color}[{delta_text}]")


def kpi_summary_row(kpi_data: Dict[str, Any]) -> None:
    """
    Display a row of 4 KPI cards (executive summary).
    
    Args:
        kpi_data: Dictionary with keys:
            - total_value: float
            - average_ticket: float
            - total_transactions: int
            - total_quantity: float
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            "Total Value",
            kpi_data.get("total_value", 0),
            format_spec=",.0f",
            icon="💰"
        )
    
    with col2:
        metric_card(
            "Avg. Ticket",
            kpi_data.get("average_ticket", 0),
            format_spec=",.0f",
            icon="🎟️"
        )
    
    with col3:
        metric_card(
            "Transactions",
            kpi_data.get("total_transactions", 0),
            format_spec=",",
            icon="📈"
        )
    
    with col4:
        metric_card(
            "Qty. Traded",
            kpi_data.get("total_quantity", 0),
            format_spec=",.0f",
            icon="📦"
        )


def stats_table(data: Dict[str, Any], columns: int = 2) -> None:
    """
    Display statistics in a compact tabular layout.
    
    Args:
        data: Dictionary of {label: value} pairs
        columns: Number of columns to display
    """
    cols = st.columns(columns)
    for idx, (label, value) in enumerate(data.items()):
        col = cols[idx % columns]
        with col:
            st.metric(label, value)


def mini_chart_row(charts: Dict[str, Any], title: str = "") -> None:
    """
    Display multiple small charts in a row.
    
    Args:
        charts: Dictionary of {chart_title: plotly_figure}
        title: Optional section title
    """
    if title:
        st.subheader(title)
    
    cols = st.columns(len(charts))
    for col, (chart_title, fig) in zip(cols, charts.items()):
        with col:
            st.plotly_chart(fig, use_container_width=True, height=300)
