"""
Repository layer for Data Warehouse queries.
Provides abstraction over direct SQL queries with reusable parameterized methods.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime
from typing import Optional, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from config import DW_CONFIG


class QueryRepository:
    """
    Centralized repository for all Data Warehouse queries.
    Handles database connection and provides typed query methods.
    """

    def __init__(self):
        """Initialize repository with DW configuration."""
        self.config = DW_CONFIG
        self._connection = None

    def _get_connection(self):
        """
        Get or create a database connection.
        Uses Streamlit session state to cache connection.
        """
        if "db_connection" not in st.session_state:
            try:
                conn = mysql.connector.connect(**self.config)
                st.session_state.db_connection = conn
            except Error as e:
                st.error(f"Database connection error: {e}")
                return None
        return st.session_state.db_connection

    def _execute_query(self, query: str, params: Optional[List] = None) -> Optional[pd.DataFrame]:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string (with ? placeholders for params)
            params: Optional list of parameters to bind to query
            
        Returns:
            DataFrame with query results, or empty DataFrame on error
        """
        try:
            conn = self._get_connection()
            if conn is None:
                return pd.DataFrame()
            
            if params:
                df = pd.read_sql(query, conn, params=params)
            else:
                df = pd.read_sql(query, conn)
            return df
        except Error as e:
            st.error(f"Query execution error: {e}")
            return pd.DataFrame()

    def close_connection(self):
        """Close the database connection."""
        if "db_connection" in st.session_state:
            try:
                st.session_state.db_connection.close()
                del st.session_state.db_connection
            except Error:
                pass

    # ========================================================================
    # KPI AND SUMMARY QUERIES
    # ========================================================================

    def get_kpi_summary(
        self, date_from: date, date_to: date
    ) -> dict:
        """
        Get executive summary KPIs for a date range.
        
        Returns:
            Dictionary with total_value, total_quantity, transaction_count, avg_ticket
        """
        query = """
        SELECT
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        WHERE dt.data >= %s AND dt.data <= %s
        """
        
        df = self._execute_query(query, [date_from, date_to])
        
        if df.empty:
            return {
                "total_value": 0.0,
                "total_quantity": 0.0,
                "transaction_count": 0,
                "average_ticket": 0.0,
            }
        
        row = df.iloc[0]
        return {
            "total_value": float(row["total_value"] or 0),
            "total_quantity": float(row["total_quantity"] or 0),
            "transaction_count": int(row["transaction_count"] or 0),
            "average_ticket": float(row["average_ticket"] or 0),
        }

    # ========================================================================
    # FINANCIAL TRENDS QUERIES
    # ========================================================================

    def get_monthly_trends(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame:
        """
        Get monthly aggregated transaction trends.
        
        Returns:
            DataFrame with year, month, month_name, total_value, total_quantity, transaction_count
        """
        query = """
        SELECT
            dt.ano as year,
            dt.mes as month,
            dt.nome_mes as month_name,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        WHERE dt.data >= %s AND dt.data <= %s
        GROUP BY dt.ano, dt.mes, dt.nome_mes
        ORDER BY dt.ano, dt.mes
        """
        return self._execute_query(query, [date_from, date_to])

    def get_quarterly_trends(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame:
        """
        Get quarterly aggregated transaction trends.
        
        Returns:
            DataFrame with year, quarter, total_value, total_quantity, transaction_count
        """
        query = """
        SELECT
            dt.ano as year,
            dt.trimestre as quarter,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        WHERE dt.data >= %s AND dt.data <= %s
        GROUP BY dt.ano, dt.trimestre
        ORDER BY dt.ano, dt.trimestre
        """
        return self._execute_query(query, [date_from, date_to])

    def get_yearly_trends(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame:
        """
        Get yearly aggregated transaction trends.
        
        Returns:
            DataFrame with year, total_value, total_quantity, transaction_count
        """
        query = """
        SELECT
            dt.ano as year,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        WHERE dt.data >= %s AND dt.data <= %s
        GROUP BY dt.ano
        ORDER BY dt.ano
        """
        return self._execute_query(query, [date_from, date_to])

    # ========================================================================
    # GEOGRAPHIC ANALYSIS QUERIES
    # ========================================================================

    def get_top_origin_countries(
        self, date_from: date, date_to: date, limit: int = 20
    ) -> pd.DataFrame:
        """
        Get top origin countries by transaction value.
        
        Args:
            date_from: Start date
            date_to: End date
            limit: Number of top countries to return
            
        Returns:
            DataFrame with country info and metrics
        """
        query = f"""
        SELECT
            dp.id_pais as country_id,
            dp.nome_pais as country_name,
            dp.codigo_iso as iso_code,
            dp.bloco_economico as economic_bloc,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        INNER JOIN dim_pais dp ON ft.sk_pais_origem = dp.sk_pais
        WHERE dt.data >= %s AND dt.data <= %s
        GROUP BY dp.sk_pais, dp.id_pais, dp.nome_pais, dp.codigo_iso, dp.bloco_economico
        ORDER BY total_value DESC
        LIMIT {limit}
        """
        return self._execute_query(query, [date_from, date_to])

    def get_top_destination_countries(
        self, date_from: date, date_to: date, limit: int = 20
    ) -> pd.DataFrame:
        """
        Get top destination countries by transaction value.
        
        Args:
            date_from: Start date
            date_to: End date
            limit: Number of top countries to return
            
        Returns:
            DataFrame with country info and metrics
        """
        query = f"""
        SELECT
            dp.id_pais as country_id,
            dp.nome_pais as country_name,
            dp.codigo_iso as iso_code,
            dp.bloco_economico as economic_bloc,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        INNER JOIN dim_pais dp ON ft.sk_pais_destino = dp.sk_pais
        WHERE dt.data >= %s AND dt.data <= %s
        GROUP BY dp.sk_pais, dp.id_pais, dp.nome_pais, dp.codigo_iso, dp.bloco_economico
        ORDER BY total_value DESC
        LIMIT {limit}
        """
        return self._execute_query(query, [date_from, date_to])

    # ========================================================================
    # ECONOMIC BLOC ANALYSIS QUERIES
    # ========================================================================

    def get_economic_bloc_performance(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame:
        """
        Get performance metrics aggregated by economic bloc.
        
        Returns:
            DataFrame with bloc name and aggregated metrics
        """
        query = """
        SELECT
            dp.bloco_economico as economic_bloc,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket,
            COUNT(DISTINCT dp.sk_pais) as country_count
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        INNER JOIN dim_pais dp ON ft.sk_pais_origem = dp.sk_pais
        WHERE dt.data >= %s AND dt.data <= %s
            AND dp.bloco_economico IS NOT NULL
        GROUP BY dp.bloco_economico
        ORDER BY total_value DESC
        """
        return self._execute_query(query, [date_from, date_to])

    # ========================================================================
    # PRODUCT ANALYSIS QUERIES
    # ========================================================================

    def get_top_products(
        self, date_from: date, date_to: date, limit: int = 20
    ) -> pd.DataFrame:
        """
        Get top products by transaction value.
        
        Args:
            date_from: Start date
            date_to: End date
            limit: Number of top products to return
            
        Returns:
            DataFrame with product info and metrics
        """
        query = f"""
        SELECT
            dp.id_produto as product_id,
            dp.descricao_produto as product_name,
            dp.codigo_ncm as ncm_code,
            dcp.id_categoria as category_id,
            dcp.descricao_categoria as category_name,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        INNER JOIN dim_produto dp ON ft.sk_produto = dp.sk_produto
        INNER JOIN dim_categoria_produto dcp ON ft.sk_categoria_produto = dcp.sk_categoria_produto
        WHERE dt.data >= %s AND dt.data <= %s
        GROUP BY dp.sk_produto, dp.id_produto, dp.descricao_produto, dp.codigo_ncm,
                 dcp.sk_categoria_produto, dcp.id_categoria, dcp.descricao_categoria
        ORDER BY total_value DESC
        LIMIT {limit}
        """
        return self._execute_query(query, [date_from, date_to])

    def get_product_category_performance(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame:
        """
        Get performance metrics aggregated by product category.
        
        Returns:
            DataFrame with category metrics
        """
        query = """
        SELECT
            dcp.id_categoria as category_id,
            dcp.descricao_categoria as category_name,
            SUM(ft.valor_convertido) as total_value,
            SUM(ft.quantidade_transacionada) as total_quantity,
            COUNT(*) as transaction_count,
            COUNT(DISTINCT dp.sk_produto) as product_count,
            AVG(ft.valor_convertido) as average_ticket
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        INNER JOIN dim_produto dp ON ft.sk_produto = dp.sk_produto
        INNER JOIN dim_categoria_produto dcp ON ft.sk_categoria_produto = dcp.sk_categoria_produto
        WHERE dt.data >= %s AND dt.data <= %s
        GROUP BY dcp.sk_categoria_produto, dcp.id_categoria, dcp.descricao_categoria
        ORDER BY total_value DESC
        """
        return self._execute_query(query, [date_from, date_to])

    # ========================================================================
    # EXCHANGE RATE ANALYSIS QUERIES
    # ========================================================================

    def get_currency_performance(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame:
        """
        Get currency performance metrics.
        
        Returns:
            DataFrame with currency info and transaction metrics
        """
        query = """
        SELECT
            dm.id_moeda as currency_id,
            dm.descricao_moeda as currency_name,
            SUM(ft.valor_convertido) as total_value,
            COUNT(*) as transaction_count,
            AVG(ft.taxa_cambio_aplicada) as average_exchange_rate,
            STDDEV(ft.taxa_cambio_aplicada) as exchange_rate_volatility
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        INNER JOIN dim_moeda dm ON ft.sk_moeda_origem = dm.sk_moeda
        WHERE dt.data >= %s AND dt.data <= %s
            AND ft.taxa_cambio_aplicada > 0
        GROUP BY dm.sk_moeda, dm.id_moeda, dm.descricao_moeda
        ORDER BY total_value DESC
        """
        return self._execute_query(query, [date_from, date_to])

    def get_exchange_rate_trends(
        self, date_from: date, date_to: date, currency_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get exchange rate trends over time.
        
        Args:
            date_from: Start date
            date_to: End date
            currency_id: Optional filter for specific currency
            
        Returns:
            DataFrame with date and exchange rate data
        """
        query = """
        SELECT
            DATE_FORMAT(dt.data, '%Y-%m') as period,
            dm.id_moeda as currency_id,
            dm.descricao_moeda as currency_name,
            AVG(ft.taxa_cambio_aplicada) as average_exchange_rate,
            MIN(ft.taxa_cambio_aplicada) as min_exchange_rate,
            MAX(ft.taxa_cambio_aplicada) as max_exchange_rate
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        INNER JOIN dim_moeda dm ON ft.sk_moeda_origem = dm.sk_moeda
        WHERE dt.data >= %s AND dt.data <= %s
            AND ft.taxa_cambio_aplicada > 0
        """
        
        params = [date_from, date_to]
        if currency_id:
            query += " AND dm.id_moeda = %s"
            params.append(currency_id)
        
        query += """
        GROUP BY DATE_FORMAT(dt.data, '%Y-%m'), dm.sk_moeda, dm.id_moeda, dm.descricao_moeda
        ORDER BY period
        """
        
        return self._execute_query(query, params)

    # ========================================================================
    # UTILITY QUERIES
    # ========================================================================

    def get_date_range(self) -> dict:
        """
        Get the minimum and maximum dates available in the warehouse.
        
        Returns:
            Dictionary with min_date and max_date
        """
        query = """
        SELECT
            MIN(dt.data) as min_date,
            MAX(dt.data) as max_date
        FROM fato_transacoes_internacionais ft
        INNER JOIN dim_tempo dt ON ft.sk_tempo = dt.sk_tempo
        """
        
        df = self._execute_query(query)
        
        if df.empty:
            return {
                "min_date": None,
                "max_date": None,
            }
        
        row = df.iloc[0]
        return {
            "min_date": row["min_date"],
            "max_date": row["max_date"],
        }
