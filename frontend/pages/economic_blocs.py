"""
Economic Blocs Page
Analyzes performance by economic partnership blocs.
"""

import streamlit as st
from datetime import date
import sys
from pathlib import Path

frontend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(frontend_path.parent))

from frontend.components.filters import date_range_selector, refresh_button
from frontend.components.export import export_section
from frontend.components.charts import plot_bloc_performance_bar, plot_bloc_pie
from frontend.data.repository import QueryRepository
from frontend.utils.cache import cache_with_ttl
from frontend.utils.logging import safe_execute

st.set_page_config(page_title="Economic Blocs", page_icon="🌐", layout="wide")

st.title("🌐 Economic Blocs Performance")
st.markdown("Compare economic partnerships by transaction volume and value")
st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

date_from, date_to = date_range_selector()
refresh_button()

metric = st.selectbox(
    "Metric",
    ["total_value", "transaction_count", "total_quantity"],
    format_func=lambda x: x.replace("_", " ").title(),
    key="bloc_metric"
)

# ============================================================================
# DATA RETRIEVAL
# ============================================================================

@cache_with_ttl(ttl_seconds=180)
def get_bloc_performance(date_from: date, date_to: date):
    repo = QueryRepository()
    return repo.get_economic_bloc_performance(date_from, date_to)

with st.spinner("Loading economic bloc data..."):
    bloc_df = safe_execute(
        get_bloc_performance, date_from, date_to,
        fallback_value=None, error_message="Failed to load bloc data"
    )

# ============================================================================
# BAR CHART
# ============================================================================

st.subheader("📊 Bloc Performance Ranking")

if bloc_df is not None and not bloc_df.empty:
    fig_bar = plot_bloc_performance_bar(bloc_df, metric_column=metric)
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No bloc data available")

# ============================================================================
# PIE CHART
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🥧 Distribution by Value")
    if bloc_df is not None and not bloc_df.empty:
        fig_pie_value = plot_bloc_pie(bloc_df, metric_column="total_value")
        st.plotly_chart(fig_pie_value, use_container_width=True)
    else:
        st.info("No data available")

with col2:
    st.subheader("🥧 Distribution by Transactions")
    if bloc_df is not None and not bloc_df.empty:
        fig_pie_count = plot_bloc_pie(bloc_df, metric_column="transaction_count")
        st.plotly_chart(fig_pie_count, use_container_width=True)
    else:
        st.info("No data available")

# ============================================================================
# DETAILED TABLE
# ============================================================================

st.markdown("---")
st.subheader("📋 Detailed Bloc Statistics")

if bloc_df is not None and not bloc_df.empty:
    st.dataframe(
        bloc_df.sort_values("total_value", ascending=False),
        use_container_width=True
    )
    
    # Summary statistics
    st.write("**Aggregate Statistics**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Blocs", len(bloc_df))
    with col2:
        st.metric("Total Value", f"${bloc_df['total_value'].sum():,.0f}")
    with col3:
        st.metric("Total Transactions", f"{bloc_df['transaction_count'].sum():,}")
    with col4:
        st.metric("Avg Value/Bloc", f"${bloc_df['total_value'].mean():,.0f}")

# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")

if bloc_df is not None and not bloc_df.empty:
    export_section(
        bloc_df,
        title="Export Bloc Performance Data",
        filename_base="economic_blocs"
    )
