"""
Test script for Phase 1: Foundation & Data Layer
Tests repository connection and sample queries.
Run with: python -m pytest test_phase1.py -v
Or: python test_phase1.py (for manual testing)
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add frontend to path
frontend_path = Path(__file__).resolve().parent / "frontend"
sys.path.insert(0, str(frontend_path.parent))

# Mock Streamlit for testing (since we're not running in Streamlit context)
class MockStreamlit:
    class SessionState(dict):
        def __setitem__(self, key, value):
            super().__setitem__(key, value)
        def __getitem__(self, key):
            return super().get(key)
        def __contains__(self, key):
            return super().__contains__(key)
    
    session_state = SessionState()
    
    @staticmethod
    def error(msg):
        print(f"❌ ERROR: {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"⚠️  WARNING: {msg}")
    
    @staticmethod
    def info(msg):
        print(f"ℹ️  INFO: {msg}")

sys.modules['streamlit'] = MockStreamlit()

# Now import our modules
from frontend.config import DW_CONFIG, validate_config
from frontend.data.repository import QueryRepository


def test_config():
    """Test 1: Validate configuration."""
    print("\n" + "="*70)
    print("TEST 1: Configuration Validation")
    print("="*70)
    
    try:
        validate_config()
        print("✅ Configuration validated successfully")
        print(f"   Database: {DW_CONFIG['database']}")
        print(f"   Host: {DW_CONFIG['host']}:{DW_CONFIG['port']}")
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def test_db_connection():
    """Test 2: Database connection."""
    print("\n" + "="*70)
    print("TEST 2: Database Connection")
    print("="*70)
    
    try:
        repo = QueryRepository()
        conn = repo._get_connection()
        if conn:
            print("✅ Database connection established")
            return True
        else:
            print("❌ Database connection returned None")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_kpi_query():
    """Test 3: KPI Summary Query."""
    print("\n" + "="*70)
    print("TEST 3: KPI Summary Query")
    print("="*70)
    
    try:
        repo = QueryRepository()
        
        # Get date range from warehouse
        date_range = repo.get_date_range()
        if date_range.get("min_date") is None:
            print("⚠️  No data found in warehouse. Skipping KPI test.")
            return True
        
        date_from = date_range["min_date"]
        date_to = date_range["max_date"]
        
        print(f"   Testing date range: {date_from} to {date_to}")
        
        kpi = repo.get_kpi_summary(date_from, date_to)
        print("✅ KPI query executed successfully")
        print(f"   Total Value: ${kpi['total_value']:,.2f}")
        print(f"   Total Quantity: {kpi['total_quantity']:,.2f}")
        print(f"   Total Transactions: {kpi['transaction_count']:,}")
        print(f"   Average Ticket: ${kpi['average_ticket']:,.2f}")
        return True
    except Exception as e:
        print(f"❌ KPI query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trends_query():
    """Test 4: Monthly Trends Query."""
    print("\n" + "="*70)
    print("TEST 4: Monthly Trends Query")
    print("="*70)
    
    try:
        repo = QueryRepository()
        
        date_range = repo.get_date_range()
        if date_range.get("min_date") is None:
            print("⚠️  No data found in warehouse. Skipping trends test.")
            return True
        
        date_from = date_range["min_date"]
        date_to = date_range["max_date"]
        
        df = repo.get_monthly_trends(date_from, date_to)
        
        if df.empty:
            print("⚠️  Trends query returned empty result")
            return True
        
        print(f"✅ Monthly trends query executed successfully")
        print(f"   Rows returned: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   Sample data:")
        print(df.head(3).to_string(index=False))
        return True
    except Exception as e:
        print(f"❌ Trends query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_geographic_query():
    """Test 5: Top Countries Query."""
    print("\n" + "="*70)
    print("TEST 5: Top Countries Query")
    print("="*70)
    
    try:
        repo = QueryRepository()
        
        date_range = repo.get_date_range()
        if date_range.get("min_date") is None:
            print("⚠️  No data found in warehouse. Skipping geographic test.")
            return True
        
        date_from = date_range["min_date"]
        date_to = date_range["max_date"]
        
        df = repo.get_top_origin_countries(date_from, date_to, limit=5)
        
        if df.empty:
            print("⚠️  Geographic query returned empty result")
            return True
        
        print(f"✅ Top countries query executed successfully")
        print(f"   Rows returned: {len(df)}")
        print(f"\n   Top 5 Origin Countries:")
        print(df[['country_name', 'economic_bloc', 'total_value', 'transaction_count']].to_string(index=False))
        return True
    except Exception as e:
        print(f"❌ Geographic query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "🧪" * 35)
    print("PHASE 1: FOUNDATION & DATA LAYER TESTS")
    print("🧪" * 35)
    
    results = {
        "Configuration": test_config(),
        "DB Connection": test_db_connection(),
        "KPI Query": test_kpi_query(),
        "Trends Query": test_trends_query(),
        "Geographic Query": test_geographic_query(),
    }
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 1 tests passed! Ready for Phase 2.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
