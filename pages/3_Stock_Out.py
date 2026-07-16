import streamlit as st
import sqlite3
import pandas as pd
from utils.ui import enable_select_all_inputs, translate_columns

st.title("📤 Saída de Estoque")

enable_select_all_inputs()

# -----------------
# LOAD PRODUCTS
# -----------------

conn = sqlite3.connect("estoque.db")

produtos = pd.read_sql("""
SELECT codigo, descricao
FROM produtos
WHERE ativo = 1
ORDER BY descricao
""", conn)

conn.close()

lista_produtos = [
    f"{row['codigo']} - {row['descricao']}"
    for _, row in produtos.iterrows()
]

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
# FORM
# -----------------

with st.form("stock_out_form"):

    produto = st.selectbox(
        "Selecionar Produto",
        lista_produtos
    )

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
    translate_columns(df),
    use_container_width=True
)





