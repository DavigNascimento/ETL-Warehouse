"""
Configuration module for Data Warehouse Frontend.
Loads environment variables and provides app configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


def _get_env(name, default=None, required=False):
    """Get environment variable with optional default and requirement check."""
    value = os.getenv(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ValueError(f"Required environment variable missing: {name}")
    return value


def _get_env_int(name, default=None, required=False):
    """Get environment variable as integer."""
    value = _get_env(name, default=default, required=required)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Environment variable {name} must be a valid integer. Current value: {value}"
        ) from exc


# ============================================================================
# DATA WAREHOUSE (Docker MySQL - Target)
# ============================================================================
DW_CONFIG = {
    "host": _get_env("DW_DB_HOST", default="localhost"),
    "port": _get_env_int("DW_DB_PORT", default="3306"),
    "user": _get_env("DW_DB_USER", required=True),
    "password": _get_env("DW_DB_PASSWORD", required=True),
    "database": _get_env("DW_DB_NAME", required=True),
}

# ============================================================================
# STREAMLIT APP CONFIGURATION
# ============================================================================
STREAMLIT_CONFIG = {
    "page_title": "Data Warehouse Dashboard",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Auto-refresh intervals (in seconds)
REFRESH_INTERVALS = {
    "1_minute": 60,
    "3_minutes": 180,
    "5_minutes": 300,
}

DEFAULT_REFRESH_INTERVAL = 180  # 3 minutes

# ============================================================================
# DATABASE CONNECTION VALIDATION
# ============================================================================
def validate_config():
    """Validate that all required configuration values are present."""
    required_keys = ["host", "port", "user", "password", "database"]
    for key in required_keys:
        if key not in DW_CONFIG or DW_CONFIG[key] is None:
            raise ValueError(f"Missing DW configuration: {key}")
    return True
