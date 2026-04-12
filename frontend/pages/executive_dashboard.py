"""
Executive Dashboard Page
Displays key KPIs and high-level summary metrics.
"""

import streamlit as st
from datetime import date
import sys
from pathlib import Path

# Add frontend to path
frontend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(frontend_path.parent))

from frontend.components.filters import date_range_selector, refresh_button
from frontend.components.metrics import kpi_summary_row, mini_chart_row
from frontend.components.export import export_section
from frontend.components.charts import plot_monthly_trends, plot_yearly_trends
from frontend.data.repository import QueryRepository
from frontend.utils.cache import cache_with_ttl
from frontend.utils.logging import safe_execute

st.set_page_config(page_title="Executive Dashboard", page_icon="🏠", layout="wide")

st.title("🏠 Executive Dashboard")
st.markdown("High-level summary of your data warehouse performance")
st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

date_from, date_to = date_range_selector()
refresh_button()

# ============================================================================
# KPI SUMMARY
# ============================================================================

@cache_with_ttl(ttl_seconds=180)
def get_kpi_data(date_from: date, date_to: date):
    """Cached KPI data retrieval."""
    repo = QueryRepository()
    return repo.get_kpi_summary(date_from, date_to)

@cache_with_ttl(ttl_seconds=180)
def get_trends_data(date_from: date, date_to: date):
    """Cached trends data retrieval."""
    repo = QueryRepository()
    return repo.get_monthly_trends(date_from, date_to)

@cache_with_ttl(ttl_seconds=180)
def get_yearly_data(date_from: date, date_to: date):
    """Cached yearly trends data retrieval."""
    repo = QueryRepository()
    return repo.get_yearly_trends(date_from, date_to)

# Get KPI data
with st.spinner("Loading KPI data..."):
    kpi_data = safe_execute(
        get_kpi_data,
        date_from, date_to,
        fallback_value={},
        error_message="Failed to load KPI data"
    )

# Display KPI cards
if kpi_data:
    st.subheader("📊 Key Performance Indicators")
    kpi_summary_row(kpi_data)
else:
    st.warning("No KPI data available for selected date range")

# ============================================================================
# TREND ANALYSIS
# ============================================================================

st.markdown("---")
st.subheader("📈 Trend Analysis")

col1, col2 = st.columns(2)

with col1:
    if st.toggle("Show Monthly Trends", value=True):
        trends_df = safe_execute(
            get_trends_data,
            date_from, date_to,
            fallback_value=None,
            error_message="Failed to load monthly trends"
        )
        if trends_df is not None and not trends_df.empty:
            fig_monthly = plot_monthly_trends(trends_df, metric_column="total_value")
            st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.info("No monthly trend data available")

with col2:
    if st.toggle("Show Yearly Trends", value=True):
        yearly_df = safe_execute(
            get_yearly_data,
            date_from, date_to,
            fallback_value=None,
            error_message="Failed to load yearly trends"
        )
        if yearly_df is not None and not yearly_df.empty:
            fig_yearly = plot_yearly_trends(yearly_df, metric_column="total_value")
            st.plotly_chart(fig_yearly, use_container_width=True)
        else:
            st.info("No yearly trend data available")

# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")

if trends_df is not None and not trends_df.empty:
    export_section(trends_df, title="Export Trends Data", filename_base="trends")
