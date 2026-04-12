"""
Streamlit session state management utilities for caching and state persistence.
"""

import streamlit as st
from typing import Callable, Any
import functools


def cache_with_ttl(ttl_seconds: int = 300):
    """
    Decorator for caching function results with TTL (time-to-live) in Streamlit.
    Falls back to built-in st.cache_data when available.
    
    Args:
        ttl_seconds: Cache lifetime in seconds (default: 5 minutes)
    """
    return st.cache_data(ttl=ttl_seconds, show_spinner=True)


def get_or_create_session_value(key: str, default_value: Any) -> Any:
    """
    Get or create a value in Streamlit session state.
    
    Args:
        key: Session state key
        default_value: Default value if key doesn't exist
    
    Returns:
        Current or newly created value
    """
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]


def update_session_value(key: str, value: Any) -> None:
    """
    Update a value in Streamlit session state.
    
    Args:
        key: Session state key
        value: New value
    """
    st.session_state[key] = value


def clear_session_cache(pattern: str = "") -> None:
    """
    Clear session state entries matching a pattern.
    
    Args:
        pattern: String pattern to match (empty = clear all)
    """
    if not pattern:
        st.session_state.clear()
    else:
        keys_to_delete = [k for k in st.session_state if pattern in k]
        for k in keys_to_delete:
            del st.session_state[k]
