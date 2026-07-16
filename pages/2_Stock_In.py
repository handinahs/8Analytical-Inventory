import streamlit as st
import sqlite3
import pandas as pd
from utils.ui import enable_select_all_inputs, translate_columns

from utils.cache import load_products
from utils.stock import save_movement

st.title("📥 Entrada de Estoque")

enable_select_all_inputs()

# -----------------
# CARREGAR PRODUTOS
# -----------------

produtos = load_products()

lista_produtos = [
    f"{row['codigo']} - {row['descricao']}"
    for _, row in produtos.iterrows()
]

# -----------------
# FORMULÃRIO
# -----------------

with st.form("stock_in_form"):

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
        "Salvar Entrada"
    )

    if submitted:

        save_movement(
    produto,
    "IN",
    quantidade,
    observacao
)

        st.success(
            "Entrada de estoque salva com sucesso!"
        )

# -----------------
# HISTÃ“RICO DE ENTRADAS
# -----------------

st.divider()

st.header("Histórico de Entradas")

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

WHERE m.tipo = 'IN'

ORDER BY m.data_movimento DESC
""", conn)

conn.close()

st.dataframe(
    translate_columns(df),
    use_container_width=True
)




