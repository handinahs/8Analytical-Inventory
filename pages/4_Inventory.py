import sqlite3
from io import BytesIO

import pandas as pd
import streamlit as st

from utils.ui import enable_select_all_inputs, render_brand_header, translate_columns

render_brand_header("📋 Estoque Atual")

enable_select_all_inputs()

conn = sqlite3.connect("estoque.db")

query = """
SELECT

    p.codigo AS Code,
    p.descricao AS Product,
    p.unidade AS Unit,
    p.posicao AS Location,

    p.qtd_inicial
    + COALESCE((
        SELECT SUM(quantidade)
        FROM movimentacoes
        WHERE codigo_produto = p.codigo
        AND tipo = 'IN'
        AND status = 1
    ),0)

    - COALESCE((
        SELECT SUM(quantidade)
        FROM movimentacoes
        WHERE codigo_produto = p.codigo
        AND tipo = 'OUT'
        AND status = 1
    ),0)

    AS Current_Stock

FROM produtos p

WHERE p.ativo = 1

ORDER BY p.descricao
"""

df = pd.read_sql(query, conn)

conn.close()

st.subheader("Filtros")

col_search, col_balance, col_location = st.columns([2, 1.4, 1.6])

with col_search:
    search = st.text_input(
        "Buscar por Código ou Produto"
    )

balance_options = [
    "Com saldo positivo",
    "Saldo zerado",
    "Saldo negativo",
]

with col_balance:
    balance_filters = st.multiselect(
        "Filtro de Saldo",
        balance_options,
        placeholder="Todos os saldos"
    )

location_values = df["Location"].fillna("").astype(str).str.strip()
location_options = sorted(location_values[location_values != ""].unique())
location_options.append("Sem posição")

with col_location:
    location_filters = st.multiselect(
        "Posição",
        location_options,
        placeholder="Todas as posições"
    )

if search:
    df = df[
        df["Code"].fillna("").str.contains(search, case=False)
        |
        df["Product"].fillna("").str.contains(search, case=False)
    ]

if balance_filters:
    balance_mask = pd.Series(False, index=df.index)

    if "Com saldo positivo" in balance_filters:
        balance_mask = balance_mask | (df["Current_Stock"] > 0)

    if "Saldo zerado" in balance_filters:
        balance_mask = balance_mask | (df["Current_Stock"] == 0)

    if "Saldo negativo" in balance_filters:
        balance_mask = balance_mask | (df["Current_Stock"] < 0)

    df = df[balance_mask]

if location_filters:
    clean_locations = df["Location"].fillna("").astype(str).str.strip()
    selected_locations = [location for location in location_filters if location != "Sem posição"]

    location_mask = pd.Series(False, index=df.index)

    if selected_locations:
        location_mask = location_mask | clean_locations.isin(selected_locations)

    if "Sem posição" in location_filters:
        location_mask = location_mask | (clean_locations == "")

    df = df[location_mask]

display_df = translate_columns(df)

st.info(f"Total de itens encontrados: {len(df)}")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    display_df.to_excel(writer, index=False, sheet_name="Estoque")

st.download_button(
    "Baixar Excel",
    data=excel_buffer.getvalue(),
    file_name="estoque_filtrado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    disabled=df.empty,
)
