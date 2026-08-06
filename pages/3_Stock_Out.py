import streamlit as st
import sqlite3
import pandas as pd
from utils.ui import enable_select_all_inputs, format_and_translate_columns, render_brand_header

render_brand_header("📤 Saída de Estoque")

enable_select_all_inputs()

# -----------------
# LOAD PRODUCTS
# -----------------

conn = sqlite3.connect("estoque.db")

produtos = pd.read_sql("""
SELECT
    p.codigo,
    p.descricao,
    p.unidade,
    p.posicao,
    p.qtd_inicial
    + COALESCE((
        SELECT SUM(quantidade)
        FROM movimentacoes
        WHERE codigo_produto = p.codigo
        AND tipo = 'IN'
        AND status = 1
    ), 0)
    - COALESCE((
        SELECT SUM(quantidade)
        FROM movimentacoes
        WHERE codigo_produto = p.codigo
        AND tipo = 'OUT'
        AND status = 1
    ), 0) AS estoque_atual
FROM produtos p
WHERE p.ativo = 1
ORDER BY p.descricao
""", conn)

conn.close()

lista_produtos = [
    f"{row['codigo']} - {row['descricao']}"
    for _, row in produtos.iterrows()
]

produtos_por_opcao = {
    f"{row['codigo']} - {row['descricao']}": row
    for _, row in produtos.iterrows()
}

# -----------------
# SAVE STOCK OUT
# -----------------

def save_stock_out(produto, quantidade, observacao):

    codigo = produto.split(" - ")[0]

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movimentacoes
        (codigo_produto, tipo, quantidade, observacao)
        VALUES (?, ?, ?, ?)
    """, (codigo, "OUT", quantidade, observacao))

    conn.commit()
    conn.close()

    st.success("Saída de estoque salva com sucesso!")


# -----------------
# PRODUCT SELECTION
# -----------------

produto = st.selectbox(
    "Selecionar Produto",
    lista_produtos
)

produto_selecionado = produtos_por_opcao[produto]
estoque_atual = produto_selecionado["estoque_atual"] or 0
unidade = produto_selecionado["unidade"] or ""
posicao = produto_selecionado["posicao"] or "Sem posição"

st.info(
    f"Estoque atual: {estoque_atual:,.2f} {unidade} | Posição: {posicao}"
)

# -----------------
# FORM
# -----------------

with st.form("stock_out_form"):

    quantidade = st.number_input(
        "Quantidade",
        min_value=1.0,
        step=1.0
    )

    observacao = st.text_area(
        "Observação"
    )

    submitted = st.form_submit_button(
        "Salvar Saída"
    )

    if submitted:

        save_stock_out(
            produto,
            quantidade,
            observacao
        )

# -----------------
# HISTORY
# -----------------

st.divider()

st.header("Histórico de Saídas")

conn = sqlite3.connect("estoque.db")

df = pd.read_sql("""
SELECT
    m.data_movimento AS Date,
    p.codigo AS Code,
    p.descricao AS Product,
    m.quantidade AS Quantity,
    m.observacao AS Observation

FROM movimentacoes m

INNER JOIN produtos p
ON m.codigo_produto = p.codigo

WHERE m.tipo = 'OUT'

ORDER BY m.data_movimento DESC
""", conn)

conn.close()

st.dataframe(
    format_and_translate_columns(df),
    use_container_width=True
)








