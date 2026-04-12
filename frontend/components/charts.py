"""
Reusable Plotly chart functions for dashboard visualizations.
All charts return Plotly Figure objects for Streamlit integration.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional


# ============================================================================
# CHART STYLING & CONFIGURATION
# ============================================================================
CHART_THEME = "plotly_white"
COLOR_SCALE_MAIN = px.colors.sequential.Blues_r
COLOR_SCALE_ACCENT = px.colors.qualitative.Set2
DEFAULT_HEIGHT = 500


# ============================================================================
# TIME SERIES / TREND CHARTS
# ============================================================================

def plot_monthly_trends(df: pd.DataFrame, metric_column: str = "total_value") -> go.Figure:
    """
    Plot monthly trend line chart.
    
    Args:
        df: DataFrame with columns [year, month, month_name, total_value, total_quantity, etc.]
        metric_column: Column to plot (total_value, total_quantity, or transaction_count)
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    # Create a date-like label for better x-axis display
    df['period_label'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    
    fig = px.line(
        df,
        x='period_label',
        y=metric_column,
        title=f"Monthly {metric_column.replace('_', ' ').title()} Trends",
        labels={
            'period_label': 'Month',
            metric_column: metric_column.replace('_', ' ').title()
        },
        markers=True,
        template=CHART_THEME,
        height=DEFAULT_HEIGHT
    )
    
    fig.update_layout(
        hovermode='x unified',
        xaxis_title='Month',
        yaxis_title=metric_column.replace('_', ' ').title(),
    )
    
    return fig


def plot_quarterly_trends(df: pd.DataFrame, metric_column: str = "total_value") -> go.Figure:
    """
    Plot quarterly trend line chart.
    
    Args:
        df: DataFrame with columns [year, quarter, total_value, total_quantity, etc.]
        metric_column: Column to plot
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    df['period_label'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
    
    fig = px.line(
        df,
        x='period_label',
        y=metric_column,
        title=f"Quarterly {metric_column.replace('_', ' ').title()} Trends",
        labels={'period_label': 'Quarter', metric_column: metric_column.replace('_', ' ').title()},
        markers=True,
        template=CHART_THEME,
        height=DEFAULT_HEIGHT
    )
    
    fig.update_layout(hovermode='x unified')
    return fig


def plot_yearly_trends(df: pd.DataFrame, metric_column: str = "total_value") -> go.Figure:
    """
    Plot yearly trend bar chart.
    
    Args:
        df: DataFrame with columns [year, total_value, total_quantity, etc.]
        metric_column: Column to plot
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    fig = px.bar(
        df,
        x='year',
        y=metric_column,
        title=f"Yearly {metric_column.replace('_', ' ').title()} Trends",
        labels={'year': 'Year', metric_column: metric_column.replace('_', ' ').title()},
        template=CHART_THEME,
        height=DEFAULT_HEIGHT,
        color=metric_column,
        color_continuous_scale=COLOR_SCALE_MAIN
    )
    
    fig.update_layout(hovermode='x unified', showlegend=False)
    return fig


# ============================================================================
# GEOGRAPHIC CHARTS
# ============================================================================

def plot_top_countries_bar(
    df: pd.DataFrame,
    metric_column: str = "total_value",
    title: str = "Top Countries by",
    limit: int = 15
) -> go.Figure:
    """
    Plot top countries as horizontal bar chart.
    
    Args:
        df: DataFrame with columns [country_name, total_value, total_quantity, etc.]
        metric_column: Column to plot
        title: Chart title prefix
        limit: Limit to top N countries
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    df_sorted = df.nlargest(limit, metric_column)
    
    fig = px.barh(
        df_sorted.sort_values(metric_column),
        x=metric_column,
        y='country_name',
        title=f"{title} {metric_column.replace('_', ' ').title()}",
        labels={'country_name': 'Country', metric_column: metric_column.replace('_', ' ').title()},
        template=CHART_THEME,
        height=max(400, len(df_sorted) * 25),
        color=metric_column,
        color_continuous_scale=COLOR_SCALE_ACCENT
    )
    
    fig.update_layout(showlegend=False, hovermode='y')
    return fig


def plot_countries_scatter(
    df: pd.DataFrame,
    x_col: str = "transaction_count",
    y_col: str = "total_value",
    size_col: Optional[str] = "total_quantity"
) -> go.Figure:
    """
    Plot countries as scatter chart (x, y, bubble size).
    
    Args:
        df: DataFrame with country data
        x_col: Column for x-axis
        y_col: Column for y-axis
        size_col: Optional column for bubble size
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        hover_name='country_name',
        title=f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}",
        labels={
            x_col: x_col.replace('_', ' ').title(),
            y_col: y_col.replace('_', ' ').title(),
            size_col: size_col.replace('_', ' ').title() if size_col else ''
        },
        template=CHART_THEME,
        height=DEFAULT_HEIGHT,
        color='economic_bloc' if 'economic_bloc' in df.columns else None
    )
    
    return fig


# ============================================================================
# ECONOMIC BLOC CHARTS
# ============================================================================

def plot_bloc_performance_bar(df: pd.DataFrame, metric_column: str = "total_value") -> go.Figure:
    """
    Plot economic blocs as bar chart.
    
    Args:
        df: DataFrame with columns [economic_bloc, total_value, total_quantity, etc.]
        metric_column: Column to plot
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    df_sorted = df.sort_values(metric_column, ascending=True)
    
    fig = px.barh(
        df_sorted,
        x=metric_column,
        y='economic_bloc',
        title=f"Economic Blocs by {metric_column.replace('_', ' ').title()}",
        labels={'economic_bloc': 'Bloc', metric_column: metric_column.replace('_', ' ').title()},
        template=CHART_THEME,
        height=max(400, len(df_sorted) * 40),
        color=metric_column,
        color_continuous_scale=COLOR_SCALE_MAIN
    )
    
    fig.update_layout(showlegend=False)
    return fig


def plot_bloc_pie(df: pd.DataFrame, metric_column: str = "total_value") -> go.Figure:
    """
    Plot economic bloc distribution as pie chart.
    
    Args:
        df: DataFrame with columns [economic_bloc, total_value, etc.]
        metric_column: Column for pie slices
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    fig = px.pie(
        df,
        labels='economic_bloc',
        values=metric_column,
        title=f"World Trade by Economic Bloc ({metric_column.replace('_', ' ').title()})",
        template=CHART_THEME,
        height=DEFAULT_HEIGHT
    )
    
    return fig


# ============================================================================
# PRODUCT CHARTS
# ============================================================================

def plot_top_products_bar(
    df: pd.DataFrame,
    metric_column: str = "total_value",
    limit: int = 15
) -> go.Figure:
    """
    Plot top products as horizontal bar chart.
    
    Args:
        df: DataFrame with columns [product_name, total_value, etc.]
        metric_column: Column to plot
        limit: Limit to top N products
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    df_sorted = df.nlargest(limit, metric_column).sort_values(metric_column)
    
    fig = px.barh(
        df_sorted,
        x=metric_column,
        y='product_name',
        title=f"Top {limit} Products by {metric_column.replace('_', ' ').title()}",
        labels={'product_name': 'Product', metric_column: metric_column.replace('_', ' ').title()},
        template=CHART_THEME,
        height=max(400, min(len(df_sorted) * 25, 600)),
        color=metric_column,
        color_continuous_scale=COLOR_SCALE_ACCENT
    )
    
    fig.update_layout(showlegend=False)
    return fig


def plot_category_performance_pie(df: pd.DataFrame, metric_column: str = "total_value") -> go.Figure:
    """
    Plot product categories as pie chart.
    
    Args:
        df: DataFrame with columns [category_name, total_value, etc.]
        metric_column: Column for pie slices
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    fig = px.pie(
        df,
        labels='category_name',
        values=metric_column,
        title=f"Trade by Product Category ({metric_column.replace('_', ' ').title()})",
        template=CHART_THEME,
        height=DEFAULT_HEIGHT
    )
    
    return fig


# ============================================================================
# EXCHANGE RATE / CURRENCY CHARTS
# ============================================================================

def plot_currency_performance_bar(df: pd.DataFrame, metric_column: str = "total_value", limit: int = 10) -> go.Figure:
    """
    Plot top currencies as bar chart.
    
    Args:
        df: DataFrame with currency data
        metric_column: Column to plot
        limit: Limit to top N currencies
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    df_sorted = df.nlargest(limit, metric_column).sort_values(metric_column)
    
    fig = px.barh(
        df_sorted,
        x=metric_column,
        y='currency_name',
        title=f"Top {limit} Currencies by {metric_column.replace('_', ' ').title()}",
        labels={'currency_name': 'Currency', metric_column: metric_column.replace('_', ' ').title()},
        template=CHART_THEME,
        height=max(300, len(df_sorted) * 30),
        color=metric_column,
        color_continuous_scale=COLOR_SCALE_ACCENT
    )
    
    fig.update_layout(showlegend=False)
    return fig


def plot_exchange_rate_trend(df: pd.DataFrame) -> go.Figure:
    """
    Plot exchange rate trends over time.
    
    Args:
        df: DataFrame with columns [period, currency_name, average_exchange_rate, min_, max_]
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    
    fig = px.line(
        df,
        x='period',
        y='average_exchange_rate',
        color='currency_name',
        title='Exchange Rate Trends Over Time',
        labels={'period': 'Month', 'average_exchange_rate': 'Average Exchange Rate'},
        template=CHART_THEME,
        height=DEFAULT_HEIGHT,
        markers=True
    )
    
    fig.update_layout(
        hovermode='x unified',
        legend=dict(x=0, y=1, xanchor='left', yanchor='top')
    )
    
    return fig


# ============================================================================
# COMPARATIVE CHARTS
# ============================================================================

def plot_metric_comparison(
    data_dict: dict,
    chart_type: str = "bar",
    title: str = "Metric Comparison"
) -> go.Figure:
    """
    Plot comparison chart from a dict of {label: value} pairs.
    
    Args:
        data_dict: Dictionary mapping labels to values
        chart_type: 'bar', 'pie', or 'scatter'
        title: Chart title
    
    Returns:
        Plotly Figure object
    """
    if not data_dict:
        return go.Figure().add_annotation(text="No data available")
    
    df = pd.DataFrame(list(data_dict.items()), columns=['label', 'value'])
    
    if chart_type == "pie":
        fig = px.pie(df, labels='label', values='value', title=title, template=CHART_THEME)
    elif chart_type == "bar":
        fig = px.bar(
            df,
            x='label',
            y='value',
            title=title,
            template=CHART_THEME,
            height=DEFAULT_HEIGHT,
            color='value',
            color_continuous_scale=COLOR_SCALE_MAIN
        )
        fig.update_layout(showlegend=False)
    else:
        fig = go.Figure()
    
    return fig
