"""
Global filter components (date range selector, etc.).
Stores state in Streamlit session state for consistency across pages.
"""

import streamlit as st
from datetime import date, timedelta
from typing import Tuple


def initialize_session_state() -> None:
    """Initialize session state for filters if not already done."""
    if "date_from" not in st.session_state:
        st.session_state.date_from = date(2023, 1, 1)
    if "date_to" not in st.session_state:
        st.session_state.date_to = date.today()


def date_range_selector(
    label: str = "Select Date Range",
    min_date: date = date(2023, 1, 1),
    max_date: date = None
) -> Tuple[date, date]:
    """
    Display a date range selector in the sidebar.
    
    Args:
        label: Selector label
        min_date: Minimum allowed date
        max_date: Maximum allowed date (defaults to today)
    
    Returns:
        Tuple of (date_from, date_to)
    """
    if max_date is None:
        max_date = date.today()
    
    initialize_session_state()
    
    with st.sidebar:
        st.subheader(label)
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_from = st.date_input(
                "From",
                value=st.session_state.date_from,
                min_value=min_date,
                max_value=max_date,
                key="date_from_input"
            )
        
        with col2:
            date_to = st.date_input(
                "To",
                value=st.session_state.date_to,
                min_value=min_date,
                max_value=max_date,
                key="date_to_input"
            )
        
        # Update session state
        st.session_state.date_from = date_from
        st.session_state.date_to = date_to
        
        # Validation
        if date_from > date_to:
            st.error("Start date must be before end date")
            return st.session_state.date_from, st.session_state.date_to
    
    return date_from, date_to


def quick_date_filters() -> None:
    """
    Display quick filter buttons (Last 30 days, Last 90 days, YTD, All time).
    Modifies st.session_state.date_from and date_to.
    """
    initialize_session_state()
    
    with st.sidebar:
        st.markdown("### Quick Filters")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Last 30 days", use_container_width=True):
                st.session_state.date_to = date.today()
                st.session_state.date_from = date.today() - timedelta(days=30)
        
        with col2:
            if st.button("Last 90 days", use_container_width=True):
                st.session_state.date_to = date.today()
                st.session_state.date_from = date.today() - timedelta(days=90)
        
        with col3:
            if st.button("Last Year", use_container_width=True):
                st.session_state.date_to = date.today()
                st.session_state.date_from = date.today() - timedelta(days=365)
        
        with col4:
            if st.button("All Time", use_container_width=True):
                st.session_state.date_from = date(2023, 1, 1)
                st.session_state.date_to = date.today()


def country_multiselect(available_countries: list) -> list:
    """
    Display a multi-select widget for country filtering.
    
    Args:
        available_countries: List of country names
    
    Returns:
        List of selected countries
    """
    if "selected_countries" not in st.session_state:
        st.session_state.selected_countries = available_countries
    
    with st.sidebar:
        selected = st.multiselect(
            "Filter by Country",
            options=available_countries,
            default=st.session_state.selected_countries,
            key="country_multiselect"
        )
        st.session_state.selected_countries = selected
    
    return selected


def bloc_multiselect(available_blocs: list) -> list:
    """
    Display a multi-select widget for economic bloc filtering.
    
    Args:
        available_blocs: List of economic bloc names
    
    Returns:
        List of selected blocs
    """
    if "selected_blocs" not in st.session_state:
        st.session_state.selected_blocs = available_blocs
    
    with st.sidebar:
        selected = st.multiselect(
            "Filter by Economic Bloc",
            options=available_blocs,
            default=st.session_state.selected_blocs,
            key="bloc_multiselect"
        )
        st.session_state.selected_blocs = selected
    
    return selected


def refresh_button() -> bool:
    """
    Display a refresh button in the sidebar.
    Used to trigger data re-fetch (clears cache).
    
    Returns:
        True if button was clicked
    """
    with st.sidebar:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        return False
