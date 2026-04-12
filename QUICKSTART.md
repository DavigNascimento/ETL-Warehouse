# 🚀 QUICKSTART GUIDE

## Get Your Dashboard Running in 3 Steps

### Step 1: Install Dependencies

```bash
cd ETL-Warehouse
pip install -r frontend/requirements.txt --break-system-packages
```

**Already have Streamlit?** Skip this step and go to Step 2.

### Step 2: Ensure Docker is Running

Verify your Data Warehouse container is up:

```bash
docker compose ps
```

Should show `mysql` container as `Up`. If not:

```bash
docker compose up -d
```

### Step 3: Launch Dashboard

**Option A - Direct Command:**
```bash
streamlit run frontend/main.py
```

**Option B - Using Launch Script:**
```bash
bash launch-dashboard.sh
```

---

## 🎯 Dashboard Overview

Once launched at `http://localhost:8501`:

| Page | What It Shows | Key Features |
|------|--|--|
| 🏠 **Executive Dashboard** | KPIs & Summary | 4 main metrics + trends |
| 📈 **Financial Trends** | Monthly/Quarterly/Yearly | Seasonality & growth |
| 🌍 **Geographic Analysis** | Top Countries | Origin & destination flows |
| 🌐 **Economic Blocs** | Bloc Performance | Market share distribution |
| 📦 **Product Performance** | Top Products & Categories | Quantity & value per product |
| 💱 **Exchange Rates** | Currency Trends | Exchange rate impact |

---

## 🎮 How to Use

### Global Filters (Sidebar)
1. **Date Range**: Select start/end dates
2. **Quick Filters**: "Last 30 days", "Last 90 days", etc.
3. **Refresh Button**: Force data reload

### On Each Page
1. **View Charts**: Plotly interactive charts (hover, zoom, pan)
2. **Expand Sections**: Click to see underlying data tables
3. **Download Data**: Export as CSV or Excel

### Tips
- Date filter applies to **all pages**
- Charts auto-refresh every 3 minutes
- Expand "Detailed Data" sections to see full datasets
- Use export buttons to save data for reports

---

## 📊 Sample KPI Values

From your Data Warehouse:

```
Date Range: 2023-01-01 to 2025-12-31

📊 Key Metrics:
   Total Transaction Value: $709.9 Million
   Total Quantity Traded: 13.1 Million units
   Total Transactions: 13,152
   Average Ticket Size: $53,975

📈 Top Origin Country: FRANCE (€17.9M)
🌐 Top Economic Bloc: EU
📦 Top Product Category: Various
💱 Primary Currencies: USD, EUR, BRL
```

---

## 🔧 Troubleshooting

### Q: "Streamlit not found"
**A**: Install it: `pip install streamlit`

### Q: "Connection refused"
**A**: Start Docker: `docker compose up -d`

### Q: "Unknown column" error
**A**: Database schema mismatch. Verify `DWschema.sql` matches queries in `frontend/data/repository.py`

### Q: "No data available"
**A**: Try expanding date range or check if database has data loaded

### Q: Slow page loads
**A**: Reduce date range or wait (cache refreshes every 3 min)

---

## 💡 Customization Examples

### Change Auto-Refresh Interval
Edit `frontend/config.py`:
```python
DEFAULT_REFRESH_INTERVAL = 300  # Change from 180 to 300 (5 min)
```

### Add New Chart to Existing Page
In any page file, add:
```python
@cache_with_ttl(ttl_seconds=180)
def get_new_data():
    repo = QueryRepository()
    return repo.get_top_products(date_from, date_to)

df = get_new_data()
fig = plot_top_products_bar(df)
st.plotly_chart(fig, use_container_width=True)
```

### Add New Dashboard Page
1. Create `frontend/pages/new_page.py`
2. Copy template from existing page
3. Add your queries and charts
4. Streamlit auto-detects the file

---

## 📁 Project Structure

```
ETL-Warehouse/
├── frontend/                 # New Streamlit dashboard
│   ├── main.py              # Entry point
│   ├── config.py            # Settings
│   ├── requirements.txt      # Dependencies
│   ├── README.md            # Full docs
│   ├── data/
│   │   ├── repository.py    # Database queries
│   │   └── models.py        # Data schemas
│   ├── components/
│   │   ├── charts.py        # Plotly charts
│   │   ├── metrics.py       # KPI cards
│   │   ├── filters.py       # Date pickers
│   │   └── export.py        # CSV/Excel
│   ├── pages/
│   │   ├── executive_dashboard.py
│   │   ├── financial_trends.py
│   │   ├── geographic_analysis.py
│   │   ├── economic_blocs.py
│   │   ├── product_performance.py
│   │   └── exchange_rates.py
│   └── utils/
│       ├── cache.py         # Session state
│       └── logging.py       # Error handling
├── test_phase1.py           # Repository tests
├── test_integration.py      # Full integration tests
└── launch-dashboard.sh      # Launch script
```

---

## 🎯 Next Steps

1. ✅ **Get dashboard running** → `streamlit run frontend/main.py`
2. 🎨 **Explore all pages** → Try each dashboard
3. 🔍 **Filter data** → Test date range filters
4. 📥 **Export reports** → Download as CSV/Excel
5. 🚀 **Customize** → Add your own charts/pages
6. 📚 **Read docs** → `frontend/README.md` for deep dive

---

## 📞 Need Help?

**Check these files:**
- `frontend/README.md` - Comprehensive documentation
- `frontend/config.py` - Configuration options
- `frontend/data/repository.py` - Available queries
- `test_phase1.py` - Verify database connection
- `test_integration.py` - Verify all components

---

## ⚡ Performance Notes

**For optimal performance:**
- Data refresh: **Every 3 minutes** (configurable)
- Cache TTL: **180 seconds**
- Supported date ranges: **12-24 months recommended**
- Browser: **Modern Chrome, Firefox, Safari, Edge**

**If slow:**
1. Reduce date range to 3-6 months
2. Check DB indexes (run: `docker exec comex-dw mysql ... SHOW INDEXES`)
3. Increase cache TTL in `config.py`

---

## 🎉 You're Ready!

Your Data Warehouse Dashboard is fully configured and ready to use.

```bash
streamlit run frontend/main.py
```

**Happy visualizing!** 📊✨
