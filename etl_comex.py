"""
ETL - StarComex | Laboratório de Banco de Dados
Extração do OLTP (MySQL/Aiven) → Transformação → Carga no DW (MySQL local)
"""

import re
import os
import unicodedata
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# =============================================================================
# CONFIGURAÇÕES DE CONEXÃO
# =============================================================================

load_dotenv()


def _get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ValueError(f"Variável de ambiente obrigatória ausente: {name}")
    return value


def _get_env_int(name, default=None, required=False):
    value = _get_env(name, default=default, required=required)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Variável {name} deve ser um inteiro válido. Valor atual: {value}") from exc

# --- Banco OLTP (fonte - Aiven) ---
OLTP_CONFIG = {
    "host":     _get_env("OLTP_DB_HOST", required=True),
    "port":     _get_env_int("OLTP_DB_PORT", default="3306", required=True),
    "user":     _get_env("OLTP_DB_USER", required=True),
    "password": _get_env("OLTP_DB_PASSWORD", required=True),
    "database": _get_env("OLTP_DB_NAME", required=True),
    "ssl_disabled": _get_env("OLTP_DB_SSL_DISABLED", default="false").lower() == "true",
}

DW_CONFIG = {
    "host":     _get_env("DW_DB_HOST", default="localhost", required=True),
    "port":     _get_env_int("DW_DB_PORT", default="3306", required=True),
    "user":     _get_env("DW_DB_USER", required=True),
    "password": _get_env("DW_DB_PASSWORD", required=True),
    "database": _get_env("DW_DB_NAME", required=True),
}

SCHEMA_SQL_PATH = Path(__file__).resolve().parent / "DWschema.sql"
# =============================================================================
# UTILITÁRIOS DE TRANSFORMAÇÃO
# =============================================================================

def normalizar_texto(valor):
    """
    Padroniza strings:
      - Strip de espaços nas bordas
      - Colapsa espaços duplos internos
      - Remove acentos (unicode → ASCII)
      - Converte para MAIÚSCULAS
      - Remove caracteres não-alfanuméricos exceto espaço, hífen e ponto
    Retorna None se o valor for nulo/vazio.
    """
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return None
    valor = str(valor).strip()
    valor = re.sub(r'\s+', ' ', valor)
    valor = unicodedata.normalize('NFKD', valor)
    valor = valor.encode('ascii', 'ignore').decode('ascii')
    valor = valor.upper()
    valor = re.sub(r'[^A-Z0-9 \-\.]', '', valor)
    return valor if valor != '' else None


def normalizar_df_textos(df):
    """Aplica normalizar_texto em todas as colunas object/string do DataFrame."""
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(normalizar_texto)
    return df


def deduplicar(df, subset_cols):
    """Remove duplicatas pelas colunas de negócio, mantendo a primeira ocorrência."""
    antes = len(df)
    df = df.drop_duplicates(subset=subset_cols, keep='first').reset_index(drop=True)
    depois = len(df)
    if antes != depois:
        print(f"  ⚠  Deduplicação em {subset_cols}: {antes - depois} linha(s) removida(s).")
    return df


def extrair_campos_data(df, col_data):
    """Extrai ANO, MES, DIA, TRIMESTRE, SEMESTRE, NOME_MES, DIA_DA_SEMANA de uma coluna de data."""
    df[col_data] = pd.to_datetime(df[col_data], errors='coerce')
    df['ano']           = df[col_data].dt.year
    df['mes']           = df[col_data].dt.month
    df['dia']           = df[col_data].dt.day
    df['trimestre']     = df[col_data].dt.quarter
    df['semestre']      = df[col_data].dt.month.apply(lambda m: 1 if m <= 6 else 2)
    df['nome_mes']      = df[col_data].dt.strftime('%B').str.upper().apply(
                            lambda v: unicodedata.normalize('NFKD', v)
                                      .encode('ascii', 'ignore').decode('ascii'))
    df['dia_da_semana'] = df[col_data].dt.strftime('%A').str.upper().apply(
                            lambda v: unicodedata.normalize('NFKD', v)
                                      .encode('ascii', 'ignore').decode('ascii'))
    return df

# =============================================================================
# EXTRAÇÃO
# =============================================================================

def conectar(config, nome='banco'):
    try:
        conn = mysql.connector.connect(**config)
        print(f"  ✔  Conectado ao {nome}.")
        return conn
    except Error as e:
        print(f"  ✘  Erro ao conectar ao {nome}: {e}")
        raise


def extrair_tabela(conn, tabela):
    print(f"  → Extraindo: {tabela}")
    df = pd.read_sql(f"SELECT * FROM {tabela}", conn)
    print(f"     {len(df)} registros extraídos.")
    return df


def extrair_dados_oltp():
    print("\n[EXTRAÇÃO] Lendo tabelas do OLTP...")
    conn = conectar(OLTP_CONFIG, 'OLTP')
    tabelas = [
        'transacoes', 'cambios', 'produtos', 'categoria_produtos',
        'paises', 'blocos_economicos', 'moedas',
        'transportes', 'tipos_transacoes',
    ]
    dados = {t: extrair_tabela(conn, t) for t in tabelas}
    conn.close()
    return dados

# =============================================================================
# TRANSFORMAÇÃO
# =============================================================================

def transformar(dados):
    print("\n[TRANSFORMAÇÃO] Iniciando pipeline de qualidade...")

    # ------------------------------------------------------------------
    # 1. BLOCOS ECONÔMICOS
    # ------------------------------------------------------------------
    print("\n  [blocos_economicos]")
    bl = dados['blocos_economicos'].copy()
    bl = normalizar_df_textos(bl)
    bl = deduplicar(bl, ['nome'])

    # ------------------------------------------------------------------
    # 2. PAÍSES
    # ------------------------------------------------------------------
    print("\n  [paises]")
    pa = dados['paises'].copy()
    pa = normalizar_df_textos(pa)
    pa = pa.merge(bl[['id', 'nome']].rename(columns={'id': 'bloco_id', 'nome': 'bloco_economico'}),
                  on='bloco_id', how='left')
    pa = deduplicar(pa, ['nome', 'codigo_iso'])

    # ------------------------------------------------------------------
    # 3. MOEDAS
    # ------------------------------------------------------------------
    print("\n  [moedas]")
    mo = dados['moedas'].copy()
    mo = normalizar_df_textos(mo)
    mo = deduplicar(mo, ['descricao', 'pais'])

    # ------------------------------------------------------------------
    # 4. CATEGORIAS DE PRODUTO
    # ------------------------------------------------------------------
    print("\n  [categoria_produtos]")
    cat = dados['categoria_produtos'].copy()
    cat = normalizar_df_textos(cat)
    cat = deduplicar(cat, ['descricao'])

    # ------------------------------------------------------------------
    # 5. PRODUTOS
    # ------------------------------------------------------------------
    print("\n  [produtos]")
    pr = dados['produtos'].copy()
    pr = normalizar_df_textos(pr)
    pr = deduplicar(pr, ['descricao', 'codigo_ncm'])
    ids_cat_validos = set(cat['id'])
    invalidos_cat = ~pr['categoria_id'].isin(ids_cat_validos)
    if invalidos_cat.any():
        print(f"  ⚠  {invalidos_cat.sum()} produto(s) com categoria_id inválida — serão nullificados.")
        pr.loc[invalidos_cat, 'categoria_id'] = None

    # ------------------------------------------------------------------
    # 6. TRANSPORTES
    # ------------------------------------------------------------------
    print("\n  [transportes]")
    tr = dados['transportes'].copy()
    tr = normalizar_df_textos(tr)
    tr = deduplicar(tr, ['descricao'])

    # ------------------------------------------------------------------
    # 7. TIPOS DE TRANSAÇÃO
    # ------------------------------------------------------------------
    print("\n  [tipos_transacoes]")
    tt = dados['tipos_transacoes'].copy()
    tt = normalizar_df_textos(tt)
    tt = deduplicar(tt, ['descricao'])

    # ------------------------------------------------------------------
    # 8. CÂMBIOS → dim_tempo também é derivada daqui
    # ------------------------------------------------------------------
    print("\n  [cambios]")
    ca = dados['cambios'].copy()
    ca = extrair_campos_data(ca, 'data')
    ca['taxa_cambio'] = pd.to_numeric(ca['taxa_cambio'], errors='coerce')
    invalidos_taxa = ca['taxa_cambio'] <= 0
    if invalidos_taxa.any():
        print(f"  ⚠  {invalidos_taxa.sum()} câmbio(s) com taxa inválida (≤0) removidos.")
        ca = ca[~invalidos_taxa]
    for col in ['nome_mes', 'dia_da_semana']:
        if col in ca.columns:
            ca[col] = ca[col].apply(normalizar_texto)

    # ------------------------------------------------------------------
    # 9. TRANSAÇÕES → tabela fato
    # ------------------------------------------------------------------
    print("\n  [transacoes]")
    tx = dados['transacoes'].copy()

    # Valor monetário não pode ser negativo
    tx['valor_monetario'] = pd.to_numeric(tx['valor_monetario'], errors='coerce')
    invalidos_val = tx['valor_monetario'] < 0
    if invalidos_val.any():
        print(f"  ⚠  {invalidos_val.sum()} transação(ões) com valor negativo removidas.")
        tx = tx[~invalidos_val]

    # País origem ≠ país destino
    mesmo_pais = tx['pais_origem'] == tx['pais_destino']
    if mesmo_pais.any():
        print(f"  ⚠  {mesmo_pais.sum()} transação(ões) com origem = destino removidas.")
        tx = tx[~mesmo_pais]

    # Valida FK câmbio
    ids_cambio_validos = set(ca['id'])
    invalidos_cambio = ~tx['cambio_id'].isin(ids_cambio_validos)
    if invalidos_cambio.any():
        print(f"  ⚠  {invalidos_cambio.sum()} transação(ões) com cambio_id inválido removidas.")
        tx = tx[~invalidos_cambio]

    # Valida FK produto
    ids_prod_validos = set(pr['id'])
    invalidos_prod = ~tx['produto_id'].isin(ids_prod_validos)
    if invalidos_prod.any():
        print(f"  ⚠  {invalidos_prod.sum()} transação(ões) com produto_id inválido removidas.")
        tx = tx[~invalidos_prod]

    # Valida FK transporte
    ids_transp_validos = set(tr['id'])
    invalidos_transp = ~tx['transporte_id'].isin(ids_transp_validos)
    if invalidos_transp.any():
        print(f"  ⚠  {invalidos_transp.sum()} transação(ões) com transporte_id inválido removidas.")
        tx = tx[~invalidos_transp]

    # Outlier: z-score > 3 por produto
    tx['z_score'] = tx.groupby('produto_id')['valor_monetario'].transform(
        lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
    )
    outliers = tx['z_score'].abs() > 3
    if outliers.any():
        print(f"  ⚠  {outliers.sum()} transação(ões) com valor muito discrepante (z>3) sinalizadas.")
    tx['flag_outlier'] = outliers.astype(int)
    tx = tx.drop(columns=['z_score'])

    # Enriquece com dados de câmbio
    tx = tx.merge(
        ca[['id', 'data', 'taxa_cambio', 'ano', 'mes', 'dia', 'trimestre']].rename(
            columns={'id': 'cambio_id'}),
        on='cambio_id', how='left'
    )
    tx['quantidade'] = pd.to_numeric(tx['quantidade'], errors='coerce').fillna(0)
    tx['valor_convertido'] = tx['valor_monetario'] * tx['taxa_cambio']

    # custo_transporte — coluna opcional no OLTP
    if 'custo_transporte' in tx.columns:
        tx['custo_transporte'] = pd.to_numeric(tx['custo_transporte'], errors='coerce').fillna(0)
    else:
        tx['custo_transporte'] = 0.0

    print(f"\n  ✔  Transações válidas para carga: {len(tx)}")

    return {
        'blocos_economicos':  bl,
        'paises':             pa,
        'moedas':             mo,
        'categoria_produtos': cat,
        'produtos':           pr,
        'transportes':        tr,
        'tipos_transacoes':   tt,
        'cambios':            ca,
        'transacoes':         tx,
    }

def executar_ddl(conn_dw):
    if not SCHEMA_SQL_PATH.exists():
        raise FileNotFoundError(f"Arquivo de schema não encontrado: {SCHEMA_SQL_PATH}")

    ddl_content = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    cursor = conn_dw.cursor()
    for stmt in ddl_content.strip().split(';'):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)
    conn_dw.commit()
    cursor.close()
    print(f"  ✔  Schema do DW criado/verificado com {SCHEMA_SQL_PATH.name}.")


def upsert_dim(conn_dw, tabela, df, cols_insert):
    cursor = conn_dw.cursor()
    placeholders = ', '.join(['%s'] * len(cols_insert))
    colunas = ', '.join(cols_insert)
    sql = f"INSERT IGNORE INTO {tabela} ({colunas}) VALUES ({placeholders})"
    dados = [tuple(None if (isinstance(v, float) and np.isnan(v)) else v
                   for v in row)
             for row in df[cols_insert].itertuples(index=False)]
    cursor.executemany(sql, dados)
    conn_dw.commit()
    inseridos = cursor.rowcount
    cursor.close()
    print(f"  ✔  {tabela}: {inseridos} registro(s) inserido(s).")


def carregar_dim_tempo(conn_dw, ca_df):
    print("\n  [dim_tempo]")
    datas = ca_df[['data', 'dia', 'mes', 'nome_mes', 'trimestre', 'semestre', 'ano', 'dia_da_semana']]\
                 .drop_duplicates(subset=['data'])
    upsert_dim(conn_dw, 'dim_tempo',
               datas,
               ['data', 'dia', 'mes', 'nome_mes', 'trimestre', 'semestre', 'ano', 'dia_da_semana'])


def carregar_dim_pais(conn_dw, pa_df):
    print("\n  [dim_pais]")
    pa_sel = pa_df[['id', 'nome', 'codigo_iso', 'bloco_economico']].rename(
        columns={'id': 'id_pais', 'nome': 'nome_pais'})
    upsert_dim(conn_dw, 'dim_pais',
               pa_sel,
               ['id_pais', 'nome_pais', 'codigo_iso', 'bloco_economico'])


def carregar_dim_moeda(conn_dw, mo_df):
    print("\n  [dim_moeda]")
    mo_sel = mo_df[['id', 'descricao', 'pais']].rename(
        columns={'id': 'id_moeda', 'descricao': 'descricao_moeda', 'pais': 'pais_moeda'})
    upsert_dim(conn_dw, 'dim_moeda',
               mo_sel,
               ['id_moeda', 'descricao_moeda', 'pais_moeda'])


def carregar_dim_tipo_transacao(conn_dw, tt_df):
    print("\n  [dim_tipo_transacao]")
    tt_sel = tt_df[['id', 'descricao']].rename(
        columns={'id': 'id_tipo_transacao', 'descricao': 'descricao_tipo_transacao'})
    upsert_dim(conn_dw, 'dim_tipo_transacao',
               tt_sel,
               ['id_tipo_transacao', 'descricao_tipo_transacao'])


def carregar_dim_produto(conn_dw, pr_df):
    print("\n  [dim_produto]")
    pr_sel = pr_df[['id', 'descricao', 'codigo_ncm']].rename(
        columns={'id': 'id_produto', 'descricao': 'descricao_produto'})
    upsert_dim(conn_dw, 'dim_produto',
               pr_sel,
               ['id_produto', 'descricao_produto', 'codigo_ncm'])


def carregar_dim_categoria(conn_dw, cat_df):
    print("\n  [dim_categoria_produto]")
    cat_sel = cat_df[['id', 'descricao']].rename(
        columns={'id': 'id_categoria', 'descricao': 'descricao_categoria'})
    upsert_dim(conn_dw, 'dim_categoria_produto',
               cat_sel,
               ['id_categoria', 'descricao_categoria'])


def carregar_dim_transporte(conn_dw, tr_df):
    print("\n  [dim_transporte]")
    tr_sel = tr_df[['id', 'descricao']].rename(
        columns={'id': 'id_transporte', 'descricao': 'descricao_transporte'})
    upsert_dim(conn_dw, 'dim_transporte',
               tr_sel,
               ['id_transporte', 'descricao_transporte'])


def carregar_fato(conn_dw, tx_df, dados_oltp):
    print("\n  [fato_transacoes_internacionais]")
    cursor = conn_dw.cursor()

    def mapa_sk(tabela, col_sk, col_id):
        cursor.execute(f"SELECT {col_id}, {col_sk} FROM {tabela}")
        return dict(cursor.fetchall())

    sk_tempo  = mapa_sk('dim_tempo',            'sk_tempo',             'data')
    sk_pais   = mapa_sk('dim_pais',             'sk_pais',              'id_pais')
    sk_moeda  = mapa_sk('dim_moeda',            'sk_moeda',             'id_moeda')
    sk_tipo   = mapa_sk('dim_tipo_transacao',   'sk_tipo_trasacao',     'id_tipo_transacao')
    sk_prod   = mapa_sk('dim_produto',          'sk_produto',           'id_produto')
    sk_cat    = mapa_sk('dim_categoria_produto','sk_categoria_produto', 'id_categoria')
    sk_transp = mapa_sk('dim_transporte',       'sk_transporte',        'id_transporte')

    prod_cat    = dict(zip(dados_oltp['produtos']['id'],
                           dados_oltp['produtos']['categoria_id']))
    cambio_info = dados_oltp['cambios'].set_index('id')[
        ['moeda_origem', 'moeda_destino', 'data', 'taxa_cambio']].to_dict('index')

    sql_fato = """
        INSERT INTO fato_transacoes_internacionais (
            sk_tempo, sk_pais_origem, sk_pais_destino,
            sk_moeda_origem, sk_moeda_destino,
            sk_tipo_transacao, sk_produto, sk_categoria_produto,
            sk_transporte,
            quantidade_transacionada, valor_trasacao, valor_convertido,
            taxa_cambio_aplicada, custo_transporte, flag_outlier
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    batch = []
    erros = 0

    for _, row in tx_df.iterrows():
        try:
            cambio = cambio_info[row['cambio_id']]
            data_tx = cambio['data']
            if isinstance(data_tx, str):
                data_tx = datetime.strptime(data_tx[:10], '%Y-%m-%d').date()
            elif hasattr(data_tx, 'date'):
                data_tx = data_tx.date()

            cat_id = prod_cat.get(row['produto_id'])

            linha = (
                sk_tempo.get(data_tx),
                sk_pais.get(row['pais_origem']),
                sk_pais.get(row['pais_destino']),
                sk_moeda.get(cambio['moeda_origem']),
                sk_moeda.get(cambio['moeda_destino']),
                sk_tipo.get(row['tipo_id']),
                sk_prod.get(row['produto_id']),
                sk_cat.get(cat_id),
                sk_transp.get(row['transporte_id']),
                float(row['quantidade']),
                float(row['valor_monetario']),
                float(row['valor_convertido']),
                float(cambio['taxa_cambio']),
                float(row['custo_transporte']),
                int(row['flag_outlier']),
            )

            if any(v is None for v in linha[:9]):
                erros += 1
                continue

            batch.append(linha)

            if len(batch) >= 1000:
                cursor.executemany(sql_fato, batch)
                conn_dw.commit()
                batch = []

        except Exception as e:
            erros += 1
            print(f"  ⚠  Erro na linha id={row.get('id', '?')}: {e}")

    if batch:
        cursor.executemany(sql_fato, batch)
        conn_dw.commit()

    cursor.close()
    print(f"  ✔  Fato: {len(tx_df) - erros} registro(s) inserido(s). Erros: {erros}.")

def verificar_carga(conn_dw):
    cursor = conn_dw.cursor()
    tabelas = [
        'dim_tempo', 'dim_pais', 'dim_moeda',
        'dim_produto', 'dim_categoria_produto',
        'dim_transporte', 'dim_tipo_transacao',
        'fato_transacoes_internacionais'
    ]

    print("\n[VERIFICAÇÃO] Contagem de registros por tabela:")
    print("-" * 45)
    for tabela in tabelas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        total = cursor.fetchone()[0]
        print(f"  {tabela:<40} {total:>6} registros")
    print("-" * 45)

    print("\n[VERIFICAÇÃO] Amostra — dim_pais:")
    cursor.execute("SELECT * FROM dim_pais LIMIT 5")
    colunas = [desc[0] for desc in cursor.description]
    print(pd.DataFrame(cursor.fetchall(), columns=colunas).to_string(index=False))

    print("\n[VERIFICAÇÃO] Amostra — dim_produto:")
    cursor.execute("SELECT * FROM dim_produto LIMIT 5")
    colunas = [desc[0] for desc in cursor.description]
    print(pd.DataFrame(cursor.fetchall(), columns=colunas).to_string(index=False))

    print("\n[VERIFICAÇÃO] Amostra — dim_tempo:")
    cursor.execute("SELECT * FROM dim_tempo LIMIT 5")
    colunas = [desc[0] for desc in cursor.description]
    print(pd.DataFrame(cursor.fetchall(), columns=colunas).to_string(index=False))

    print("\n[VERIFICAÇÃO] Amostra — fato (5 registros):")
    cursor.execute("SELECT * FROM fato_transacoes_internacionais LIMIT 5")
    colunas = [desc[0] for desc in cursor.description]
    print(pd.DataFrame(cursor.fetchall(), columns=colunas).to_string(index=False))

    print("\n[VERIFICAÇÃO] Outliers sinalizados:")
    cursor.execute("SELECT COUNT(*) FROM fato_transacoes_internacionais WHERE flag_outlier = 1")
    print(f"  {cursor.fetchone()[0]} transações com flag_outlier = 1")

    cursor.close()

# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def main():
    inicio = datetime.now()
    print("=" * 60)
    print("  ETL StarComex — início:", inicio.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)

    # 1. EXTRAÇÃO
    dados_brutos = extrair_dados_oltp()

    # 2. TRANSFORMAÇÃO
    dados_tratados = transformar(dados_brutos)

    # 3. CARGA
    print("\n[CARGA] Conectando ao DW...")
    conn_dw = conectar(DW_CONFIG, 'DW')

    print("\n[CARGA] Criando schema...")
    executar_ddl(conn_dw)

    print("\n[CARGA] Carregando dimensões...")
    carregar_dim_tempo(conn_dw,          dados_tratados['cambios'])
    carregar_dim_pais(conn_dw,           dados_tratados['paises'])
    carregar_dim_moeda(conn_dw,          dados_tratados['moedas'])
    carregar_dim_tipo_transacao(conn_dw, dados_tratados['tipos_transacoes'])
    carregar_dim_produto(conn_dw,        dados_tratados['produtos'])
    carregar_dim_categoria(conn_dw,      dados_tratados['categoria_produtos'])
    carregar_dim_transporte(conn_dw,     dados_tratados['transportes'])

    print("\n[CARGA] Carregando tabela fato...")
    carregar_fato(conn_dw, dados_tratados['transacoes'], dados_brutos)

    #verificar_carga(conn_dw)
    conn_dw.close()

    fim = datetime.now()
    print("\n" + "=" * 60)
    print(f"  ETL concluído em {(fim - inicio).seconds}s — {fim.strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == '__main__':
    main()
