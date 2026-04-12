# ETL Warehouse

Pipeline ETL que extrai dados do OLTP (MySQL), transforma e carrega no DW (MySQL).

## 1) Configurar ambiente

1. Copie o arquivo de exemplo e ajuste credenciais:

```bash
cp .env.example .env
```

2. Edite `.env` com seus valores reais, principalmente:
- `OLTP_DB_*` para fonte OLTP
- `DW_DB_*` para destino DW

## 2) Subir o MySQL do DW via Docker Compose

```bash
docker compose up -d
```

O serviço `warehouse` usa MySQL 8 e monta o arquivo `DWschema.sql` da raiz em:
- `/docker-entrypoint-initdb.d/01-DWschema.sql`

Esse script roda automaticamente apenas na primeira inicializacao do volume de dados.

## 3) Instalar dependencias Python

```bash
pip install -r requirements.txt
```

## 4) Executar ETL

```bash
python etl_comex.py
```

O script le as configuracoes de conexao do arquivo `.env`.

## Observacoes importantes

- O arquivo `DWschema.sql` e a referencia unica do schema do DW.
- Se voce alterar `DWschema.sql` depois da primeira subida, precisa recriar o volume:

```bash
docker compose down -v
docker compose up -d
```

- Como o ETL roda no host, use `DW_DB_HOST=localhost` e `DW_DB_PORT` igual a porta publicada no compose.
