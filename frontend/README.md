# 📊 Data Warehouse Frontend - Streamlit Dashboard

A modern, interactive dashboard for visualizing your Data Warehouse with Streamlit and Plotly. Real-time analysis of financial transactions, geographic patterns, and market trends.

## 🎯 Features

### Dashboard Pages

1. **🏠 Executive Dashboard**
   - Key Performance Indicators (KPIs)
   - Total transaction value, quantity traded, average ticket size
   - Monthly and yearly trend analysis
   - Quick overview of warehouse health

2. **📈 Financial Trends**
   - Monthly, quarterly, and yearly transaction trends
   - Identify seasonality and growth patterns
   - Multiple metric options (value, quantity, transaction count)
   - Selectable time periods and comparison views

3. **🌍 Geographic Analysis**
   - Top origin and destination countries
   - Trade flow analysis
   - Economic bloc distribution
   - Country performance metrics and rankings

4. **🌐 Economic Blocs**
   - Performance comparison by economic partnerships
   - Total value and transaction counts by bloc
   - Market share distribution (pie charts)
   - Bloc-level KPIs and statistics

5. **📦 Product Performance**
   - Top-performing products and categories
   - Quantity traded and monetary value per product
   - Product category analysis
   - Product vs. category comparisons

6. **💱 Exchange Rates**
   - Currency performance metrics
   - Exchange rate trends over time
   - Currency volatility analysis
   - Top currencies by transaction volume

### Global Features

- **🔄 Real-time Auto-Refresh**: Data updates every 1-5 minutes configurable
- **📅 Global Date Filtering**: Filter all dashboards by date range with quick presets
- **📥 CSV/Excel Export**: Download data from any dashboard in multiple formats
- **🎨 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Performance Optimized**: 3-minute cache TTL to balance freshness with speed
- **🔐 Error Resilient**: Graceful error handling with fallback displays

## 📋 Requirements

- Python 3.8+
- MySQL 8.0+ (Docker or cloud-hosted)
- See `requirements.txt` for dependencies

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

Or using your existing venv:

```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r frontend/requirements.txt
```

### 2. Environment Configuration

Ensure `.env` file is set up with key variables:

```bash
# DW target (Docker MySQL)
DW_DB_HOST=localhost
DW_DB_PORT=3306
DW_DB_USER=etl_user
DW_DB_PASSWORD=etl_password
DW_DB_NAME=comex_dw
```

### 3. Start Streamlit App

From the project root:

```bash
streamlit run frontend/main.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure

```
frontend/
├── main.py                              # App entry point (Streamlit home)
├── config.py                            # Configuration management
├── requirements.txt                     # Python dependencies
├── data/
│   ├── repository.py                   # Database query abstraction layer
│   └── models.py                        # TypedDict data schemas
├── components/
│   ├── charts.py                        # Reusable Plotly chart functions
│   ├── metrics.py                       # KPI cards and metric displays
│   ├── filters.py                       # Date range & filter widgets
│   └── export.py                        # CSV/Excel export functions
├── pages/
│   ├── executive_dashboard.py           # KPI & summary page
│   ├── financial_trends.py              # Time series analysis
│   ├── geographic_analysis.py           # Country-level analysis
│   ├── economic_blocs.py                # Bloc performance page
│   ├── product_performance.py           # Product & category analysis
│   └── exchange_rates.py                # Currency analysis
└── utils/
    ├── cache.py                         # Session state & caching
    └── logging.py                       # Error handling & logging
```

## 🏗 Architecture

### Data Flow

```
Database (MySQL)
    ↓
QueryRepository (data/repository.py)
    ↓ [Cached queries with 3-min TTL]
    ↓
Components (charts/, metrics/, etc.)
    ↓
Dashboard Pages (pages/)
    ↓
Streamlit UI + Plotly Visualizations
```

### Key Layers

1. **Repository Layer** (`data/repository.py`)
   - Centralized database query logic
   - Parameterized queries with date filtering
   - Error handling and fallback DataFrames

2. **Component Layer** (`components/`)
   - Reusable Plotly chart functions
   - Streamlit UI components (metrics, filters)
   - Export functionality

3. **Page Layer** (`pages/`)
   - Feature-specific dashboard pages
   - Composition of components
   - User interactions and filtering

4. **Utilities** (`utils/`)
   - Caching and session state management
   - Logging and error handling

## 🔧 Configuration

### Refresh Intervals

Edit `frontend/config.py` to adjust refresh behavior:

```python
REFRESH_INTERVALS = {
    "1_minute": 60,
    "3_minutes": 180,
    "5_minutes": 300,
}

DEFAULT_REFRESH_INTERVAL = 180  # 3 minutes
```

### Streamlit Settings

Customize appearance in `frontend/config.py`:

```python
STREAMLIT_CONFIG = {
    "page_title": "Data Warehouse Dashboard",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
```

### Environment Variables

All configuration is loaded from `.env` in the project root:

```env
DW_DB_HOST=localhost
DW_DB_PORT=3306
DW_DB_USER=etl_user
DW_DB_PASSWORD=etl_password
DW_DB_NAME=comex_dw
```

## 💻 Usage Guide

### Navigating the Dashboard

1. **Launch App**: `streamlit run frontend/main.py`
2. **Select Page**: Use sidebar navigation to switch between dashboards
3. **Filter by Date**: Adjust date range in sidebar (applies to all pages)
4. **Quick Filters**: Use "Last 30 days", "Last 90 days", etc. buttons
5. **View Details**: Expand sections to see underlying data tables
6. **Export Data**: Use download buttons to export as CSV or Excel

### Customizing Queries

Modify `frontend/data/repository.py` to add new queries:

```python
def get_custom_metric(self, date_from: date, date_to: date) -> pd.DataFrame:
    """Your custom query."""
    query = """
    SELECT ... FROM ... WHERE ...
    """
    return self._execute_query(query, [date_from, date_to])
```

Then use in pages with caching:

```python
@cache_with_ttl(ttl_seconds=180)
def get_data(date_from, date_to):
    repo = QueryRepository()
    return repo.get_custom_metric(date_from, date_to)
```

## 🧪 Testing

Run Phase 1 tests to validate the repository layer:

```bash
python test_phase1.py
```

Expected output:
```
✅ Configuration validated successfully
✅ Database connection established
✅ KPI query executed successfully
✅ Monthly trends query executed successfully
✅ Top countries query executed successfully
```

## 🔍 Troubleshooting

### Issue: "Connection refused"
- **Cause**: Docker database not running
- **Solution**: `docker compose up -d` from project root

### Issue: "Unknown column" errors
- **Cause**: Repository queries don't match actual schema
- **Solution**: Verify actual column names in `DWschema.sql`

### Issue: Slow page loads
- **Cause**: Large date ranges or no indexes on foreign keys
- **Solution**: 
  1. Reduce date range
  2. Add indexes: `CREATE INDEX idx_fk_tempo ON fato_transacoes_internacionais(sk_tempo);`
  3. Profile query execution time

### Issue: Charts not displaying
- **Cause**: Empty DataFrames or data type mismatches
- **Solution**: Check Streamlit logs, verify data with export feature

## 📊 Data Sources

The dashboard queries your Data Warehouse (`comex_dw`) which contains:

- **Fact Table**: `fato_transacoes_internacionais` (13K+ transactions)
- **Dimensions**: 
  - `dim_tempo` (date/time breakdown)
  - `dim_pais` (countries with economic blocs)
  - `dim_moeda` (currencies)
  - `dim_produto` (products with NCM codes)
  - `dim_categoria_produto` (product categories)
  - `dim_tipo_transacao` (transaction types)
  - `dim_transporte` (transport modes)

## 🚀 Performance Tips

1. **Date Range Filtering**: Limit to 12 months max for faster queries
2. **Pre-aggregation**: Consider creating materialized monthly summary tables
3. **Indexing**: Ensure foreign keys have indexes (auto-created by default)
4. **Cache TTL**: Increase from 3 to 5+ minutes if DB queries take >10 seconds

## 📚 API Reference

### QueryRepository Methods

```python
repo = QueryRepository()

# KPI data
kpi = repo.get_kpi_summary(date_from, date_to)

# Trends
monthly = repo.get_monthly_trends(date_from, date_to)
quarterly = repo.get_quarterly_trends(date_from, date_to)
yearly = repo.get_yearly_trends(date_from, date_to)

# Geography
origins = repo.get_top_origin_countries(date_from, date_to, limit=20)
destinations = repo.get_top_destination_countries(date_from, date_to, limit=20)

# Blocs
blocs = repo.get_economic_bloc_performance(date_from, date_to)

# Products
products = repo.get_top_products(date_from, date_to, limit=20)
categories = repo.get_product_category_performance(date_from, date_to)

# Currencies
currencies = repo.get_currency_performance(date_from, date_to)
trends = repo.get_exchange_rate_trends(date_from, date_to)

# Utility
range_info = repo.get_date_range()
```

## 🎨 Customization

### Adding New Charts

1. Add function to `frontend/components/charts.py`
2. Use Plotly Express or Graph Objects
3. Return `go.Figure` object
4. Import and use in page

Example:

```python
def plot_custom_chart(df) -> go.Figure:
    fig = px.bar(df, x='col1', y='col2')
    return fig
```

### Adding New Pages

1. Create `frontend/pages/new_page.py`
2. Use existing pages as template
3. Import components and repository
4. Add to Streamlit sidebar navigation

## 📝 License

Internal Use Only - Data Warehouse Project

## 👥 Support

For issues or feature requests, refer to the project documentation or contact the data engineering team.

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Status**: Production Ready
