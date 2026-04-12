"""
Exchange Rates Page
Analyzes currency trends and exchange rate impacts.
"""

import streamlit as st
from datetime import date
import sys
from pathlib import Path

frontend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(frontend_path.parent))

from frontend.components.filters import date_range_selector, refresh_button
from frontend.components.export import export_multi_sheet
from frontend.components.charts import plot_currency_performance_bar, plot_exchange_rate_trend
from frontend.data.repository import QueryRepository
from frontend.utils.cache import cache_with_ttl
from frontend.utils.logging import safe_execute

st.set_page_config(page_title="Exchange Rates", page_icon="💱", layout="wide")

st.title("💱 Exchange Rate Analysis")
st.markdown("Monitor currency trends and exchange rate impacts on transactions")
st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

date_from, date_to = date_range_selector()
refresh_button()

top_currencies = st.slider("Top N Currencies", min_value=5, max_value=20, value=10, key="top_currencies")

# ============================================================================
# DATA RETRIEVAL
# ============================================================================

@cache_with_ttl(ttl_seconds=180)
def get_currency_performance(date_from: date, date_to: date):
    repo = QueryRepository()
    return repo.get_currency_performance(date_from, date_to)

@cache_with_ttl(ttl_seconds=180)
def get_exchange_trends(date_from: date, date_to: date):
    repo = QueryRepository()
    return repo.get_exchange_rate_trends(date_from, date_to)

# ============================================================================
# CURRENCY PERFORMANCE
# ============================================================================

st.subheader("💰 Top Currencies by Transaction Volume")

with st.spinner("Loading currency data..."):
    currency_df = safe_execute(
        get_currency_performance, date_from, date_to,
        fallback_value=None, error_message="Failed to load currency data"
    )

if currency_df is not None and not currency_df.empty:
    fig = plot_currency_performance_bar(currency_df, metric_column="total_value", limit=top_currencies)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Currency Details"):
        st.dataframe(currency_df, use_container_width=True)
else:
    st.info("No currency data available")

# ============================================================================
# EXCHANGE RATE TRENDS
# ============================================================================

st.markdown("---")
st.subheader("📈 Exchange Rate Trends Over Time")

with st.spinner("Loading exchange rate trends..."):
    trends_df = safe_execute(
        get_exchange_trends, date_from, date_to,
        fallback_value=None, error_message="Failed to load exchange trends"
    )

if trends_df is not None and not trends_df.empty:
    fig_trend = plot_exchange_rate_trend(trends_df)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    with st.expander("View Trend Data"):
        st.dataframe(trends_df, use_container_width=True)
else:
    st.info("No exchange rate trend data available")

# ============================================================================
# CURRENCY STATISTICS
# ============================================================================

st.markdown("---")
st.subheader("📊 Currency Statistics")

if currency_df is not None and not currency_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Currencies Tracked", len(currency_df))
    with col2:
        st.metric("Total Transactions", f"{currency_df['transaction_count'].sum():,}")
    with col3:
        std_dev = currency_df['exchange_rate_volatility'].mean()
        st.metric("Avg Exchange Rate Volatility", f"{std_dev:.4f}" if std_dev else "N/A")
    with col4:
        st.metric("Avg Exchange Rate", f"{currency_df['average_exchange_rate'].mean():.4f}")
    
    st.write("**Top 10 Currencies by Value**")
    st.dataframe(
        currency_df.nlargest(10, 'total_value')[['currency_name', 'total_value', 'transaction_count', 'average_exchange_rate']],
        use_container_width=True
    )

# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")

if currency_df is not None and not currency_df.empty and trends_df is not None and not trends_df.empty:
    export_multi_sheet(
        {
            "Currency Performance": currency_df,
            "Exchange Rate Trends": trends_df
        },
        title="Export Exchange Rate Data",
        filename_base="exchange_rates"
    )
