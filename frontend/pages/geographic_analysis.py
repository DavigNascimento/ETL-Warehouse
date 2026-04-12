"""
Geographic Analysis Page
Analyzes top countries and trade flows (origin/destination).
"""

import streamlit as st
from datetime import date
import sys
from pathlib import Path

frontend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(frontend_path.parent))

from frontend.components.filters import date_range_selector, refresh_button
from frontend.components.export import export_multi_sheet
from frontend.components.charts import plot_top_countries_bar, plot_countries_scatter
from frontend.data.repository import QueryRepository
from frontend.utils.cache import cache_with_ttl
from frontend.utils.logging import safe_execute

st.set_page_config(page_title="Geographic Analysis", page_icon="🌍", layout="wide")

st.title("🌍 Geographic Analysis")
st.markdown("Identify top countries by transaction activity and trade flows")
st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

date_from, date_to = date_range_selector()
refresh_button()

# Settings
col1, col2 = st.columns(2)
with col1:
    top_n = st.slider("Top N Countries", min_value=5, max_value=50, value=15)
with col2:
    metric = st.selectbox(
        "Metric",
        ["total_value", "transaction_count", "total_quantity"],
        format_func=lambda x: x.replace("_", " ").title()
    )

# ============================================================================
# DATA RETRIEVAL
# ============================================================================

@cache_with_ttl(ttl_seconds=180)
def get_origin_countries(date_from: date, date_to: date, limit: int):
    repo = QueryRepository()
    return repo.get_top_origin_countries(date_from, date_to, limit=limit)

@cache_with_ttl(ttl_seconds=180)
def get_destination_countries(date_from: date, date_to: date, limit: int):
    repo = QueryRepository()
    return repo.get_top_destination_countries(date_from, date_to, limit=limit)

# ============================================================================
# ORIGIN COUNTRIES
# ============================================================================

st.subheader("📤 Top Origin Countries")

with st.spinner("Loading origin countries..."):
    origin_df = safe_execute(
        get_origin_countries, date_from, date_to, top_n,
        fallback_value=None, error_message="Failed to load origin countries"
    )

if origin_df is not None and not origin_df.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = plot_top_countries_bar(origin_df, metric_column=metric, title="Top Origin Countries", limit=top_n)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Summary Stats**")
        st.metric("Countries", len(origin_df))
        st.metric("Total Value", f"${origin_df['total_value'].sum():,.0f}")
        st.metric("Avg Ticket", f"${origin_df['average_ticket'].mean():,.0f}")
    
    with st.expander("View Detailed Data"):
        st.dataframe(origin_df, use_container_width=True)
else:
    st.info("No origin country data available")

# ============================================================================
# DESTINATION COUNTRIES
# ============================================================================

st.markdown("---")
st.subheader("📥 Top Destination Countries")

with st.spinner("Loading destination countries..."):
    dest_df = safe_execute(
        get_destination_countries, date_from, date_to, top_n,
        fallback_value=None, error_message="Failed to load destination countries"
    )

if dest_df is not None and not dest_df.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = plot_top_countries_bar(dest_df, metric_column=metric, title="Top Destination Countries", limit=top_n)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Summary Stats**")
        st.metric("Countries", len(dest_df))
        st.metric("Total Value", f"${dest_df['total_value'].sum():,.0f}")
        st.metric("Avg Ticket", f"${dest_df['average_ticket'].mean():,.0f}")
    
    with st.expander("View Detailed Data"):
        st.dataframe(dest_df, use_container_width=True)
else:
    st.info("No destination country data available")

# ============================================================================
# COMPARISON
# ============================================================================

st.markdown("---")
st.subheader("🔄 Origin vs Destination Comparison")

if origin_df is not None and dest_df is not None and not origin_df.empty and not dest_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top 5 Origins by Value**")
        st.dataframe(
            origin_df.nlargest(5, 'total_value')[['country_name', 'economic_bloc', 'total_value']],
            use_container_width=True
        )
    
    with col2:
        st.write("**Top 5 Destinations by Value**")
        st.dataframe(
            dest_df.nlargest(5, 'total_value')[['country_name', 'economic_bloc', 'total_value']],
            use_container_width=True
        )

# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")

if origin_df is not None and not origin_df.empty and dest_df is not None and not dest_df.empty:
    export_multi_sheet(
        {
            "Origin Countries": origin_df,
            "Destination Countries": dest_df
        },
        title="Export Geographic Data",
        filename_base="geographic_analysis"
    )
