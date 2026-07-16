import streamlit as st
import sqlite3
import pandas as pd
from utils.ui import enable_select_all_inputs

st.title("📦 Ajuste de Estoque")

enable_select_all_inputs()

conn = sqlite3.connect("estoque.db")

# -------------------
# LOAD PRODUCTS
# -------------------

produtos = pd.read_sql("""
SELECT codigo, descricao
FROM produtos
WHERE ativo = 1
ORDER BY descricao
""", conn)

lista_produtos = [
    f"{row['codigo']} - {row['descricao']}"
    for _, row in produtos.iterrows()
]

produto = st.selectbox(
    "Selecionar Produto",
    lista_produtos
)

codigo = produto.split(" - ")[0]

# -------------------
# CURRENT STOCK
# -------------------

estoque_atual = pd.read_sql(f"""

SELECT

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
AND p.codigo = '{codigo}'

""", conn).iloc[0]["saldo"]

st.metric(
    "Estoque Atual",
    estoque_atual
)

# -------------------
# ADJUST STOCK
# -------------------

novo_estoque = st.number_input(
    "Quantidade Real em Estoque",
    min_value=0.0,
    step=1.0
)

if st.button("Ajustar Estoque"):

    diferenca = novo_estoque - estoque_atual

    if diferenca > 0:

        tipo = "IN"
        quantidade = diferenca

    elif diferenca < 0:

        tipo = "OUT"
        quantidade = abs(diferenca)

    else:
        st.info("O estoque já está correto.")
        st.stop()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movimentacoes
        (
            codigo_produto,
            tipo,
            quantidade,
            observacao
        )

        VALUES (?, ?, ?, ?)

    """, (

        codigo,
        tipo,
        quantidade,
        "Ajuste de Estoque"

    ))

    conn.commit()

    st.success(
        "Estoque ajustado com sucesso!"
    )

conn.close()



