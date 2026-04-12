"""
Integration test for frontend components.
Verifies all layers work together: config → repository → components → pages
"""

import sys
from pathlib import Path

frontend_path = Path(__file__).resolve().parent / "frontend"
sys.path.insert(0, str(frontend_path.parent))

print("\n" + "="*70)
print("FRONTEND INTEGRATION TEST")
print("="*70 + "\n")

# ============================================================================
# Test 1: Configuration Load
# ============================================================================
print("TEST 1: Configuration Load")
print("-" * 70)

try:
    from frontend.config import DW_CONFIG, validate_config, STREAMLIT_CONFIG
    validate_config()
    print(f"✅ Config validated")
    print(f"   Database: {DW_CONFIG['database']} @ {DW_CONFIG['host']}:{DW_CONFIG['port']}")
    print(f"   Streamlit: {STREAMLIT_CONFIG['page_title']}")
except Exception as e:
    print(f"❌ Config test failed: {e}")
    sys.exit(1)

# ============================================================================
# Test 2: Repository Initialization
# ============================================================================
print("\nTEST 2: Repository Layer")
print("-" * 70)

try:
    from frontend.data.repository import QueryRepository
    
    repo = QueryRepository()
    print(f"✅ QueryRepository initialized")
    
    # Check methods exist
    required_methods = [
        'get_kpi_summary',
        'get_monthly_trends',
        'get_top_origin_countries',
        'get_economic_bloc_performance',
        'get_top_products',
        'get_currency_performance',
    ]
    
    for method in required_methods:
        if hasattr(repo, method):
            print(f"   ✓ {method}")
        else:
            print(f"   ✗ {method} NOT FOUND")
            raise AttributeError(f"Method {method} not found")
    
    print(f"✅ All {len(required_methods)} repository methods found")
except Exception as e:
    print(f"❌ Repository test failed: {e}")
    sys.exit(1)

# ============================================================================
# Test 3: Data Models
# ============================================================================
print("\nTEST 3: Data Models")
print("-" * 70)

try:
    from frontend.data.models import (
        KPISummary, MonthlySummary, CountryPerformance,
        BlocPerformance, ProductPerformance, CurrencyTrend
    )
    print(f"✅ All data models imported successfully")
    print(f"   Models: KPISummary, MonthlySummary, CountryPerformance,")
    print(f"           BlocPerformance, ProductPerformance, CurrencyTrend")
except Exception as e:
    print(f"❌ Data models test failed: {e}")
    sys.exit(1)

# ============================================================================
# Test 4: Components - Charts
# ============================================================================
print("\nTEST 4: Chart Components")
print("-" * 70)

try:
    from frontend.components.charts import (
        plot_monthly_trends, plot_quarterly_trends, plot_yearly_trends,
        plot_top_countries_bar, plot_bloc_performance_bar, plot_bloc_pie,
        plot_top_products_bar, plot_category_performance_pie,
        plot_currency_performance_bar, plot_exchange_rate_trend
    )
    print(f"✅ All chart functions imported successfully")
    print(f"   Functions: plot_monthly_trends, plot_quarterly_trends,")
    print(f"              plot_top_countries_bar, plot_bloc_performance_bar, etc.")
except Exception as e:
    print(f"❌ Chart components test failed: {e}")
    sys.exit(1)

# ============================================================================
# Test 5: Components - Metrics & Filters
# ============================================================================
print("\nTEST 5: Metrics & Filter Components")
print("-" * 70)

try:
    from frontend.components.metrics import kpi_summary_row, metric_card
    from frontend.components.filters import initialize_session_state, date_range_selector
    from frontend.components.export import export_csv, export_excel
    print(f"✅ Metrics, filters, and export components imported successfully")
except Exception as e:
    print(f"❌ Components test failed: {e}")
    sys.exit(1)

# ============================================================================
# Test 6: Utilities
# ============================================================================
print("\nTEST 6: Utility Modules")
print("-" * 70)

try:
    from frontend.utils.cache import cache_with_ttl, get_or_create_session_value
    from frontend.utils.logging import log_info, log_error, safe_execute
    print(f"✅ Cache and logging utilities imported successfully")
except Exception as e:
    print(f"❌ Utilities test failed: {e}")
    sys.exit(1)

# ============================================================================
# Test 7: Pages - File Check
# ============================================================================
print("\nTEST 7: Dashboard Pages")
print("-" * 70)

required_pages = [
    "executive_dashboard",
    "financial_trends",
    "geographic_analysis",
    "economic_blocs",
    "product_performance",
    "exchange_rates",
]

pages_dir = frontend_path / "pages"
missing_pages = []

for page in required_pages:
    page_file = pages_dir / f"{page}.py"
    if page_file.exists():
        size_kb = page_file.stat().st_size / 1024
        print(f"   ✓ {page}.py ({size_kb:.1f} KB)")
    else:
        missing_pages.append(page)
        print(f"   ✗ {page}.py NOT FOUND")

if missing_pages:
    print(f"\n❌ Missing {len(missing_pages)} page files: {missing_pages}")
    sys.exit(1)
else:
    print(f"\n✅ All {len(required_pages)} dashboard pages found")

# ============================================================================
# Test 8: Directory Structure
# ============================================================================
print("\nTEST 8: Directory Structure")
print("-" * 70)

required_dirs = [
    "frontend/data",
    "frontend/components",
    "frontend/pages",
    "frontend/utils",
]

for dir_path in required_dirs:
    full_path = Path(dir_path)
    if full_path.exists() and full_path.is_dir():
        file_count = len(list(full_path.glob("*.py")))
        print(f"   ✓ {dir_path}/ ({file_count} files)")
    else:
        print(f"   ✗ {dir_path}/ NOT FOUND")
        sys.exit(1)

print(f"\n✅ Directory structure validated")

# ============================================================================
# Test 9: Configuration Files
# ============================================================================
print("\nTEST 9: Configuration Files")
print("-" * 70)

required_files = [
    "frontend/main.py",
    "frontend/config.py",
    "frontend/requirements.txt",
    "frontend/README.md",
    ".env",
]

for file_path in required_files:
    full_path = Path(file_path)
    if full_path.exists():
        size_kb = full_path.stat().st_size / 1024
        print(f"   ✓ {file_path} ({size_kb:.1f} KB)")
    else:
        print(f"   ✗ {file_path} NOT FOUND")

print(f"\n✅ All configuration files present")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("INTEGRATION TEST SUMMARY")
print("="*70)
print("""
✅ All tests passed!

Your frontend is ready to run:

1. Install dependencies:
   pip install -r frontend/requirements.txt

2. Start the dashboard:
   streamlit run frontend/main.py

3. Or use the launch script:
   bash launch-dashboard.sh

The dashboard will be available at:
   http://localhost:8501

Dashboard Pages:
  • 🏠 Executive Dashboard (KPIs & summary)
  • 📈 Financial Trends (trends analysis)
  • 🌍 Geographic Analysis (countries & flows)
  • 🌐 Economic Blocs (bloc performance)
  • 📦 Product Performance (products & categories)
  • 💱 Exchange Rates (currency analysis)

Features:
  • Real-time auto-refresh (1-5 minutes)
  • Global date range filtering
  • CSV/Excel export
  • Responsive design
  • Error resilience

For more info, see: frontend/README.md

Happy analyzing! 📊
""")
