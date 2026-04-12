"""
Logging and error handling utilities for the dashboard.
"""

import streamlit as st
import logging
from typing import Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_info(message: str) -> None:
    """Log an info message and optionally display in app."""
    logger.info(message)


def log_error(message: str, display_to_user: bool = False) -> None:
    """
    Log an error message.
    
    Args:
        message: Error message
        display_to_user: Whether to display error in Streamlit UI
    """
    logger.error(message)
    if display_to_user:
        st.error(f"⚠️ Error: {message}")


def log_warning(message: str, display_to_user: bool = False) -> None:
    """
    Log a warning message.
    
    Args:
        message: Warning message
        display_to_user: Whether to display warning in Streamlit UI
    """
    logger.warning(message)
    if display_to_user:
        st.warning(f"⚠️ {message}")


def safe_execute(
    func: callable,
    *args,
    fallback_value: any = None,
    error_message: str = "Operation failed",
    **kwargs
):
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        fallback_value: Value to return on error
        error_message: Error message to log
        *args, **kwargs: Arguments for func
    
    Returns:
        Function result or fallback_value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_error(f"{error_message}: {str(e)}", display_to_user=True)
        return fallback_value
