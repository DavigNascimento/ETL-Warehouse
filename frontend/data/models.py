"""
Data models and schemas for the Data Warehouse Frontend.
Uses TypedDict for type hints without adding Pydantic dependencies.
"""

from typing import TypedDict, List, Optional
from datetime import date, datetime


# ============================================================================
# KPI AND SUMMARY METRICS
# ============================================================================
class KPISummary(TypedDict):
    """Executive summary KPI metrics."""
    total_transaction_value: float
    total_quantity_traded: float
    total_transactions: int
    average_ticket_size: float
    period_start: date
    period_end: date


# ============================================================================
# FINANCIAL TRENDS
# ============================================================================
class MonthlySummary(TypedDict):
    """Monthly aggregated transaction data."""
    period: str  # Format: "YYYY-MM"
    month_name: str
    total_value: float
    total_quantity: float
    transaction_count: int
    average_ticket: float


class QuarterlySummary(TypedDict):
    """Quarterly aggregated transaction data."""
    period: str  # Format: "YYYY-Q#"
    quarter: str
    year: int
    total_value: float
    total_quantity: float
    transaction_count: int


class YearlySummary(TypedDict):
    """Yearly aggregated transaction data."""
    year: int
    total_value: float
    total_quantity: float
    transaction_count: int


# ============================================================================
# GEOGRAPHIC ANALYSIS
# ============================================================================
class CountryPerformance(TypedDict):
    """Transaction metrics by country."""
    country_id: int
    country_name: str
    iso_code: str
    economic_bloc: str
    total_value: float
    total_quantity: float
    transaction_count: int
    average_ticket: float


# ============================================================================
# ECONOMIC BLOC ANALYSIS
# ============================================================================
class BlocPerformance(TypedDict):
    """Transaction metrics by economic bloc."""
    economic_bloc: str
    total_value: float
    total_quantity: float
    transaction_count: int
    average_ticket: float
    country_count: int


# ============================================================================
# PRODUCT ANALYSIS
# ============================================================================
class ProductPerformance(TypedDict):
    """Transaction metrics by product."""
    product_id: int
    product_name: str
    ncm_code: str
    category_id: int
    category_name: str
    total_value: float
    total_quantity: float
    transaction_count: int
    average_ticket: float


class CategoryPerformance(TypedDict):
    """Transaction metrics by product category."""
    category_id: int
    category_name: str
    total_value: float
    total_quantity: float
    transaction_count: int
    product_count: int


# ============================================================================
# EXCHANGE RATE ANALYSIS
# ============================================================================
class CurrencyPerformance(TypedDict):
    """Transaction metrics by currency."""
    currency_id: int
    currency_code: str
    currency_name: str
    total_value: float
    transaction_count: int
    average_exchange_rate: float
    exchange_rate_volatility: float


class CurrencyTrend(TypedDict):
    """Exchange rate trend data."""
    period: str  # Format: "YYYY-MM"
    currency_id: int
    currency_code: str
    average_exchange_rate: float
    min_exchange_rate: float
    max_exchange_rate: float


# ============================================================================
# TRANSACTION DETAILS (for tables and drill-downs)
# ============================================================================
class TransactionDetail(TypedDict):
    """Individual transaction detail (for tables)."""
    transaction_id: int
    transaction_date: date
    origin_country: str
    destination_country: str
    product_name: str
    category_name: str
    quantity: float
    transaction_value: float
    converted_value: float
    exchange_rate: float
    currency_code: str
    transaction_type: str
