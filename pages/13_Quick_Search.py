import sqlite3

import pandas as pd
import streamlit as st

from utils.ui import enable_select_all_inputs, format_and_translate_columns, render_brand_header

render_brand_header("🔎 Busca Rápida")

enable_select_all_inputs()

DB_PATH = "estoque.db"

MOVEMENT_LABELS = {
    "IN": "Entrada",
    "OUT": "Saída",
}

STATUS_LABELS = {
    1: "🟢 Ativa",
    0: "🔴 Cancelada",
}


def load_products(search=""):
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        p.codigo AS Code,
        p.descricao AS Product,
        p.unidade AS Unit,
        COALESCE(p.posicao, '') AS Location,
        p.ativo AS Active,
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
        ), 0) AS Current_Stock
    FROM produtos p
    WHERE 1 = 1
    """

    params = []

    if search:
        query += """
        AND (
            p.codigo LIKE ?
            OR p.descricao LIKE ?
            OR p.posicao LIKE ?
        )
        """
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += """
    ORDER BY p.ativo DESC, p.descricao
    LIMIT 100
    """

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


def load_product_movements(code):
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        m.data_movimento AS Date,
        m.tipo AS Type,
        m.quantidade AS Quantity,
        m.observacao AS Observation,
        m.status AS Status,
        m.motivo_cancelamento AS Cancellation_Reason,
        m.data_cancelamento AS Cancellation_Date
    FROM movimentacoes m
    WHERE m.codigo_produto = ?
    ORDER BY m.data_movimento DESC
    LIMIT 50
    """

    df = pd.read_sql(query, conn, params=[code])
    conn.close()
    return df


search = st.text_input(
    "Buscar por código, descrição ou posição",
    placeholder="Exemplo: mouse, 18.1801, B.01.03"
)

products = load_products(search)

if products.empty:
    st.warning("Nenhum produto encontrado.")
    st.stop()

product_options = {
    f"{row['Code']} - {row['Product']}": row
    for _, row in products.iterrows()
}

selected_product = st.selectbox(
    "Selecionar Produto",
    list(product_options.keys())
)

product = product_options[selected_product]
status_label = "Ativo" if product["Active"] == 1 else "Inativo"
location_label = product["Location"] if str(product["Location"]).strip() else "Sem posição"

st.divider()

st.subheader("Resumo do Produto")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Estoque Atual", f"{product['Current_Stock']:,.0f}")

with col2:
    st.metric("Posição", location_label)

with col3:
    st.metric("Unidade", product["Unit"] or "-")

with col4:
    st.metric("Status", status_label)

st.write(f"**Código:** {product['Code']}")
st.write(f"**Descrição:** {product['Product']}")

st.divider()

st.subheader("Últimas Movimentações do Produto")

movements = load_product_movements(product["Code"])

if movements.empty:
    st.info("Este produto ainda não possui movimentações.")
else:
    display_movements = movements.copy()
    display_movements["Type"] = display_movements["Type"].map(MOVEMENT_LABELS).fillna(display_movements["Type"])
    display_movements["Status"] = display_movements["Status"].map(STATUS_LABELS).fillna(display_movements["Status"])
    display_movements = display_movements.rename(columns={
        "Cancellation_Reason": "Motivo do Cancelamento",
        "Cancellation_Date": "Data do Cancelamento",
    })

    st.dataframe(
        format_and_translate_columns(display_movements),
        use_container_width=True,
        hide_index=True,
    )

    active_movements = movements[movements["Status"] == 1]
    total_in = active_movements[active_movements["Type"] == "IN"]["Quantity"].sum()
    total_out = active_movements[active_movements["Type"] == "OUT"]["Quantity"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Entradas", f"{total_in:,.0f}")

    with col2:
        st.metric("Total de Saídas", f"{total_out:,.0f}")

    with col3:
        st.metric("Movimentações", len(movements))


