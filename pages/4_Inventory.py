import streamlit as st
import sqlite3
import pandas as pd
from utils.ui import enable_select_all_inputs, translate_columns

st.title("📋 Estoque Atual")

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

st.subheader("Buscar Produto")

search = st.text_input(
    "Buscar por Código ou Produto"
)

if search:
    df = df[
        df["Code"].str.contains(search, case=False)
        |
        df["Product"].str.contains(search, case=False)
    ]

st.dataframe(
    translate_columns(df),
    use_container_width=True
)






