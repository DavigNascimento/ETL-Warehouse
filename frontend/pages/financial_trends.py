"""
Financial Trends Page
Analyzes monthly, quarterly, and yearly transaction trends.
"""

import streamlit as st
from datetime import date
import sys
from pathlib import Path

frontend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(frontend_path.parent))

from frontend.components.filters import date_range_selector, refresh_button
from frontend.components.export import export_section
from frontend.components.charts import (
    plot_monthly_trends, plot_quarterly_trends, plot_yearly_trends
)
from frontend.data.repository import QueryRepository
from frontend.utils.cache import cache_with_ttl
from frontend.utils.logging import safe_execute

st.set_page_config(page_title="Financial Trends", page_icon="📈", layout="wide")

st.title("📈 Financial Trends")
st.markdown("Analyze transaction patterns over time to identify seasonality and growth")
st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

date_from, date_to = date_range_selector()
refresh_button()

# Metric selection
metric_col, _ = st.columns([1, 3])
with metric_col:
    metric = st.selectbox(
        "Select Metric",
        ["total_value", "total_quantity", "transaction_count"],
        format_func=lambda x: x.replace("_", " ").title()
    )

# ============================================================================
# DATA RETRIEVAL
# ============================================================================

@cache_with_ttl(ttl_seconds=180)
def get_monthly_trends(date_from: date, date_to: date):
    repo = QueryRepository()
    return repo.get_monthly_trends(date_from, date_to)

@cache_with_ttl(ttl_seconds=180)
def get_quarterly_trends(date_from: date, date_to: date):
    repo = QueryRepository()
    return repo.get_quarterly_trends(date_from, date_to)

@cache_with_ttl(ttl_seconds=180)
def get_yearly_trends(date_from: date, date_to: date):
    repo = QueryRepository()
    return repo.get_yearly_trends(date_from, date_to)

# ============================================================================
# MONTHLY TRENDS
# ============================================================================

st.subheader("📅 Monthly Trends")

with st.spinner("Loading monthly trends..."):
    monthly_df = safe_execute(
        get_monthly_trends, date_from, date_to,
        fallback_value=None, error_message="Failed to load monthly trends"
    )

if monthly_df is not None and not monthly_df.empty:
    fig = plot_monthly_trends(monthly_df, metric_column=metric)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Data"):
        st.dataframe(monthly_df, use_container_width=True)
else:
    st.info("No monthly trend data available")

# ============================================================================
# QUARTERLY TRENDS
# ============================================================================

st.subheader("📊 Quarterly Trends")

with st.spinner("Loading quarterly trends..."):
    quarterly_df = safe_execute(
        get_quarterly_trends, date_from, date_to,
        fallback_value=None, error_message="Failed to load quarterly trends"
    )

if quarterly_df is not None and not quarterly_df.empty:
    fig = plot_quarterly_trends(quarterly_df, metric_column=metric)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Data"):
        st.dataframe(quarterly_df, use_container_width=True)
else:
    st.info("No quarterly trend data available")

# ============================================================================
# YEARLY TRENDS
# ============================================================================

st.subheader("📈 Yearly Trends")

with st.spinner("Loading yearly trends..."):
    yearly_df = safe_execute(
        get_yearly_trends, date_from, date_to,
        fallback_value=None, error_message="Failed to load yearly trends"
    )

if yearly_df is not None and not yearly_df.empty:
    fig = plot_yearly_trends(yearly_df, metric_column=metric)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    with st.expander("View Data & Statistics"):
        st.dataframe(yearly_df, use_container_width=True)
        
        if metric in yearly_df.columns:
            st.write(f"**{metric.title()} Statistics:**")
            st.write(yearly_df[metric].describe())
else:
    st.info("No yearly trend data available")

# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")

if monthly_df is not None and not monthly_df.empty:
    export_section(
        monthly_df,
        title="Export Trends Data",
        filename_base="financial_trends"
    )
