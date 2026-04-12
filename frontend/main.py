"""
Main Streamlit application entry point.
Configures multi-page dashboard with global navigation.
"""

import streamlit as st
from pathlib import Path
import sys

# Add frontend to path
frontend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(frontend_path.parent))

from config import STREAMLIT_CONFIG, validate_config
from frontend.components.filters import date_range_selector, quick_date_filters, refresh_button
from frontend.utils.logging import log_info

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

# Validate config on startup
try:
    validate_config()
except ValueError as e:
    st.error(f"Configuration error: {e}")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
)

# ============================================================================
# STYLES & THEME
# ============================================================================

st.markdown("""
<style>
    [data-testid="stMetricDeltaContainer"] {
        font-size: 1rem !important;
    }
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION & FILTERS
# ============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Data+Warehouse", width="stretch")
    st.title("Navigation")

# Global filters
date_from, date_to = date_range_selector(
    label="📅 Date Range",
    min_date=None,
    max_date=None
)

quick_date_filters()
refresh_button()

# ============================================================================
# PAGE REGISTRY
# ============================================================================

pages = {
    "🏠 Executive Dashboard": "pages/executive_dashboard",
    "📈 Financial Trends": "pages/financial_trends",
    "🌍 Geographic Analysis": "pages/geographic_analysis",
    "🌐 Economic Blocs": "pages/economic_blocs",
    "📦 Product Performance": "pages/product_performance",
    "💱 Exchange Rates": "pages/exchange_rates",
}

# ============================================================================
# MAIN APP
# ============================================================================

st.title("📊 Data Warehouse Dashboard")
st.markdown("---")

# Display page selection (Streamlit multi-page routing)
page_names_values = list(pages.keys())

# For Streamlit's file-based page routing, ensure pages exist as files
# Users will use sidebar to navigate to different pages

st.info("""
Welcome to the Data Warehouse Dashboard. Use the sidebar to navigate to different analysis pages:
- **Executive Dashboard**: High-level KPIs and trends
- **Financial Trends**: Monthly, quarterly, and yearly analysis
- **Geographic Analysis**: Top countries and trade origins/destinations
- **Economic Blocs**: Performance by economic partnership
- **Product Performance**: Top products and categories
- **Exchange Rates**: Currency trends and impact analysis

Use the date range selector to filter all data across pages.
""")

# Log app startup
log_info(f"Dashboard accessed. Date range: {date_from} to {date_to}")
