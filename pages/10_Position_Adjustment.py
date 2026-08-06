import sqlite3

import pandas as pd
import streamlit as st

from utils.ui import enable_select_all_inputs, translate_columns, render_brand_header

render_brand_header("📍 Ajuste de Posição")

enable_select_all_inputs()

DB_PATH = "estoque.db"


def load_products():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        p.codigo AS Code,
        p.descricao AS Product,
        p.unidade AS Unit,
        COALESCE(p.posicao, '') AS Location,
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
    WHERE p.ativo = 1
    ORDER BY p.descricao
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


def update_location(code, new_location):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE produtos
        SET posicao = ?
        WHERE codigo = ?
        """,
        (new_location.strip().upper(), code),
    )

    conn.commit()
    conn.close()


products = load_products()

if products.empty:
    st.warning("Nenhum produto cadastrado.")
    st.stop()

options = {
    f"{row['Code']} - {row['Product']}": row
    for _, row in products.iterrows()
}

selected_product = st.selectbox(
    "Selecionar Produto",
    list(options.keys()),
)

product = options[selected_product]
current_location = str(product["Location"] or "").strip()
current_location_label = current_location if current_location else "Sem posição"

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Posição Atual", current_location_label)

with col2:
    st.metric("Estoque Atual", f"{product['Current_Stock']:,.0f}")

with col3:
    st.metric("Unidade", product["Unit"] or "-")

st.divider()

with st.form("position_adjustment_form"):
    new_location = st.text_input(
        "Nova Posição",
        value=current_location,
        placeholder="Exemplo: B.01.03",
    )

    submitted = st.form_submit_button("Atualizar Posição")

    if submitted:
        clean_location = new_location.strip().upper()

        if not clean_location:
            st.warning("Digite a nova posição.")
        elif clean_location == current_location.upper():
            st.info("Este produto já está nessa posição.")
        else:
            update_location(product["Code"], clean_location)
            st.success(
                f"Posição atualizada de '{current_location_label}' para '{clean_location}'."
            )
            st.rerun()

st.divider()

st.subheader("Produtos Sem Posição")

missing_location = products[
    products["Location"].fillna("").str.strip() == ""
][["Code", "Product", "Unit", "Current_Stock"]]

if missing_location.empty:
    st.info("Todos os produtos têm posição cadastrada.")
else:
    st.dataframe(
        translate_columns(missing_location),
        use_container_width=True,
        hide_index=True,
    )

