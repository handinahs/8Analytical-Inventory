import streamlit as st
import sqlite3
import pandas as pd
from database import criar_tabelas
from migrations import m001_add_status
from utils.ui import translate_columns

# Inicializa banco
criar_tabelas()
m001_add_status.run()
# Inicializa banco


st.set_page_config(
    page_title="8Analytical Inventory",
    page_icon="📦",
    layout="wide"
)

st.image("assets/logo_8analytical_inventory.png", width=208)

st.title("8Analytical Inventory")
st.caption("Controle de estoque e almoxarifado")

conn = sqlite3.connect("estoque.db")

# -------------------
# KPIs
# -------------------

total_produtos = pd.read_sql("""
SELECT COUNT(*) AS total
FROM produtos
WHERE ativo = 1
""", conn).iloc[0]["total"]

estoque_total = pd.read_sql("""
SELECT SUM(

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

) AS total_estoque

FROM produtos p
WHERE p.ativo = 1
""", conn).iloc[0]["total_estoque"]

sem_estoque = pd.read_sql("""
SELECT COUNT(*) AS total

FROM (

SELECT

p.codigo,

p.qtd_inicial

+ COALESCE((
    SELECT SUM(quantidade)
    FROM movimentacoes
    WHERE codigo_produto = p.codigo
    AND tipo='IN'
    AND status = 1
),0)

- COALESCE((
    SELECT SUM(quantidade)
    FROM movimentacoes
    WHERE codigo_produto = p.codigo
    AND tipo='OUT'
    AND status = 1
),0)

AS saldo

FROM produtos p
WHERE p.ativo = 1

)

WHERE saldo <= 0
""", conn).iloc[0]["total"]

# -------------------
# CARDS
# -------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📦 Produtos",
        f"{total_produtos:,}"
    )

with col2:
    st.metric(
        "🏪 Estoque Total",
        f"{estoque_total or 0:,.0f}"
    )

with col3:
    st.metric(
        "⚠️ Produtos Sem Estoque",
        f"{sem_estoque:,}"
    )

st.divider()

# -------------------
# LAST MOVEMENTS
# -------------------

st.subheader("🕒 Últimas Movimentações")

mov = pd.read_sql("""
SELECT

m.data_movimento AS Date,
p.codigo AS Code,
p.descricao AS Product,
m.tipo AS Type,
m.quantidade AS Quantity

FROM movimentacoes m

INNER JOIN produtos p
ON p.codigo = m.codigo_produto

WHERE m.status = 1
AND p.ativo = 1

ORDER BY m.data_movimento DESC

LIMIT 10
""", conn)

conn.close()

st.dataframe(
    translate_columns(mov),
    use_container_width=True
)









