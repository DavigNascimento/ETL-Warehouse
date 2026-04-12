CREATE TABLE IF NOT EXISTS dim_tempo (
    sk_tempo      INT AUTO_INCREMENT PRIMARY KEY,
    data          DATE NOT NULL,
    dia           INT,
    mes           INT,
    nome_mes      VARCHAR(20),
    trimestre     INT,
    semestre      INT,
    ano           INT,
    dia_da_semana VARCHAR(20),
    UNIQUE KEY uq_data (data)
);

CREATE TABLE IF NOT EXISTS dim_pais (
    sk_pais         INT AUTO_INCREMENT PRIMARY KEY,
    id_pais         INT,
    nome_pais       VARCHAR(100),
    codigo_iso      VARCHAR(10),
    bloco_economico VARCHAR(100),
    UNIQUE KEY uq_pais (id_pais)
);

CREATE TABLE IF NOT EXISTS dim_moeda (
    sk_moeda        INT AUTO_INCREMENT PRIMARY KEY,
    id_moeda        INT,
    descricao_moeda VARCHAR(100),
    pais_moeda      VARCHAR(100),
    UNIQUE KEY uq_moeda (id_moeda)
);

CREATE TABLE IF NOT EXISTS dim_tipo_transacao (
    sk_tipo_trasacao         INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo_transacao        INT,
    descricao_tipo_transacao VARCHAR(100),
    UNIQUE KEY uq_tipo (id_tipo_transacao)
);

CREATE TABLE IF NOT EXISTS dim_produto (
    sk_produto        INT AUTO_INCREMENT PRIMARY KEY,
    id_produto        INT,
    descricao_produto VARCHAR(200),
    codigo_ncm        VARCHAR(20),
    UNIQUE KEY uq_produto (id_produto)
);

CREATE TABLE IF NOT EXISTS dim_categoria_produto (
    sk_categoria_produto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria         INT,
    descricao_categoria  VARCHAR(100),
    UNIQUE KEY uq_cat (id_categoria)
);

CREATE TABLE IF NOT EXISTS dim_transporte (
    sk_transporte        INT AUTO_INCREMENT PRIMARY KEY,
    id_transporte        INT,
    descricao_transporte VARCHAR(100),
    UNIQUE KEY uq_transp (id_transporte)
);

CREATE TABLE IF NOT EXISTS fato_transacoes_internacionais (
    id_fato                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    sk_tempo                 INT,
    sk_pais_origem           INT,
    sk_pais_destino          INT,
    sk_moeda_origem          INT,
    sk_moeda_destino         INT,
    sk_tipo_transacao        INT,
    sk_produto               INT,
    sk_categoria_produto     INT,
    sk_transporte            INT,
    quantidade_transacionada DECIMAL(18,4),
    valor_trasacao           DECIMAL(18,4),
    valor_convertido         DECIMAL(18,4),
    taxa_cambio_aplicada     DECIMAL(18,6),
    custo_transporte         DECIMAL(18,4),
    flag_outlier             TINYINT DEFAULT 0,
    FOREIGN KEY (sk_tempo)             REFERENCES dim_tempo(sk_tempo),
    FOREIGN KEY (sk_pais_origem)       REFERENCES dim_pais(sk_pais),
    FOREIGN KEY (sk_pais_destino)      REFERENCES dim_pais(sk_pais),
    FOREIGN KEY (sk_moeda_origem)      REFERENCES dim_moeda(sk_moeda),
    FOREIGN KEY (sk_moeda_destino)     REFERENCES dim_moeda(sk_moeda),
    FOREIGN KEY (sk_tipo_transacao)    REFERENCES dim_tipo_transacao(sk_tipo_trasacao),
    FOREIGN KEY (sk_produto)           REFERENCES dim_produto(sk_produto),
    FOREIGN KEY (sk_categoria_produto) REFERENCES dim_categoria_produto(sk_categoria_produto),
    FOREIGN KEY (sk_transporte)        REFERENCES dim_transporte(sk_transporte)
);
