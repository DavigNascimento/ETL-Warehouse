"""
Product Performance Page
Analyzes top products and product categories.
"""

import streamlit as st
from datetime import date
import sys
from pathlib import Path

frontend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(frontend_path.parent))

from frontend.components.filters import date_range_selector, refresh_button
from frontend.components.export import export_multi_sheet
from frontend.components.charts import plot_top_products_bar, plot_category_performance_pie
from frontend.data.repository import QueryRepository
from frontend.utils.cache import cache_with_ttl
from frontend.utils.logging import safe_execute

st.set_page_config(page_title="Product Performance", page_icon="📦", layout="wide")

st.title("📦 Product Performance")
st.markdown("Analyze top-performing products and categories")
st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

date_from, date_to = date_range_selector()
refresh_button()

col1, col2 = st.columns(2)
with col1:
    top_products = st.slider("Top N Products", min_value=5, max_value=50, value=15)
with col2:
    metric = st.selectbox(
        "Metric",
        ["total_value", "total_quantity", "transaction_count"],
        format_func=lambda x: x.replace("_", " ").title(),
        key="product_metric"
    )

# ============================================================================
# DATA RETRIEVAL
# ============================================================================

@cache_with_ttl(ttl_seconds=180)
def get_top_products(date_from: date, date_to: date, limit: int):
    repo = QueryRepository()
    return repo.get_top_products(date_from, date_to, limit=limit)

@cache_with_ttl(ttl_seconds=180)
def get_category_performance(date_from: date, date_to: date):
    repo = QueryRepository()
    return repo.get_product_category_performance(date_from, date_to)

# ============================================================================
# TOP PRODUCTS
# ============================================================================

st.subheader("🏆 Top Products by Transaction Value")

with st.spinner("Loading product data..."):
    products_df = safe_execute(
        get_top_products, date_from, date_to, top_products,
        fallback_value=None, error_message="Failed to load product data"
    )

if products_df is not None and not products_df.empty:
    fig = plot_top_products_bar(products_df, metric_column=metric, limit=top_products)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Detailed Product Data"):
        st.dataframe(products_df, use_container_width=True)
else:
    st.info("No product data available")

# ============================================================================
# PRODUCT CATEGORIES
# ============================================================================

st.markdown("---")
st.subheader("📂 Product Categories Performance")

with st.spinner("Loading category data..."):
    category_df = safe_execute(
        get_category_performance, date_from, date_to,
        fallback_value=None, error_message="Failed to load category data"
    )

if category_df is not None and not category_df.empty:
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        fig_pie = plot_category_performance_pie(category_df, metric_column="total_value")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.write("**Category Summary**")
        st.metric("Total Categories", len(category_df))
        st.metric("Total Value", f"${category_df['total_value'].sum():,.0f}")
        
        # Top category
        if not category_df.empty:
            top_cat = category_df.nlargest(1, 'total_value').iloc[0]
            st.write(f"**Top Category**: {top_cat['category_name']}")
            st.write(f"Value: ${top_cat['total_value']:,.0f}")
    
    with st.expander("View Category Data"):
        st.dataframe(
            category_df.sort_values("total_value", ascending=False),
            use_container_width=True
        )
else:
    st.info("No category data available")

# ============================================================================
# PRODUCT VS CATEGORY COMPARISON
# ============================================================================

st.markdown("---")
st.subheader("📊 Product vs Category Analysis")

if products_df is not None and not products_df.empty and category_df is not None and not category_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Products by Category**")
        products_by_cat = products_df.groupby('category_name').size().sort_values(ascending=False)
        st.bar_chart(products_by_cat)
    
    with col2:
        st.write("**Category Performance**")
        st.bar_chart(category_df.set_index('category_name')['total_value'])

# ============================================================================
# EXPORT
# ============================================================================

st.markdown("---")

if products_df is not None and not products_df.empty and category_df is not None and not category_df.empty:
    export_multi_sheet(
        {
            "Top Products": products_df,
            "Categories": category_df
        },
        title="Export Product Data",
        filename_base="product_performance"
    )
