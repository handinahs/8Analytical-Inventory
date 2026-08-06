import streamlit as st
import sqlite3
import pandas as pd
from utils.ui import enable_select_all_inputs, translate_columns, render_brand_header

render_brand_header("📦 Produtos")

enable_select_all_inputs()

DB_PATH = "estoque.db"


# -----------------
# DATABASE HELPERS
# -----------------

def save_product(codigo, descricao, unidade, posicao, qtd_inicial):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO produtos
            (codigo, descricao, unidade, posicao, qtd_inicial)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo, descricao, unidade, posicao, qtd_inicial))

        conn.commit()
        st.success("Produto cadastrado com sucesso!")

    except sqlite3.IntegrityError:
        st.error("Este código de produto já existe!")

    conn.close()


def update_product_info(codigo, descricao, unidade, posicao):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE produtos
        SET
            descricao = ?,
            unidade = ?,
            posicao = ?
        WHERE codigo = ?
    """, (
        descricao.strip(),
        unidade.strip(),
        posicao.strip().upper(),
        codigo,
    ))

    conn.commit()
    conn.close()
    st.cache_data.clear()


def set_product_status(codigo, ativo):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE produtos
        SET ativo = ?
        WHERE codigo = ?
    """, (ativo, codigo))

    conn.commit()
    conn.close()
    st.cache_data.clear()


def load_products(search="", ativo=1):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        codigo AS Code,
        descricao AS Descrição,
        unidade AS Unidade,
        posicao AS Posição,
        qtd_inicial AS Quantity
    FROM produtos
    WHERE ativo = ?
    """

    params = [ativo]

    if search:
        query += """
        AND (
            codigo LIKE ?
            OR descricao LIKE ?
        )
        """
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY descricao"

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    return df


# -----------------
# PRODUCT FORM
# -----------------

st.header("Cadastrar Produto")

with st.form("product_form"):

    codigo = st.text_input("Código do Produto")
    descricao = st.text_input("Descrição")

    col1, col2 = st.columns(2)

    with col1:
        unidade = st.text_input("Unidade")

    with col2:
        posicao = st.text_input("Posição")

    qtd_inicial = st.number_input(
        "Quantidade Inicial",
        min_value=0.0,
        step=1.0
    )

    submitted = st.form_submit_button("Salvar Produto")

    if submitted:

        if codigo and descricao:
            save_product(
                codigo.strip(),
                descricao.strip(),
                unidade.strip(),
                posicao.strip().upper(),
                qtd_inicial
            )
        else:
            st.warning("Preencha Código e Descrição.")

# -----------------
# PRODUCT LIST
# -----------------

st.divider()

st.header("Produtos Cadastrados")

search = st.text_input(
    "Buscar por Código ou Descrição"
)

df = load_products(search=search, ativo=1)

st.dataframe(translate_columns(df), use_container_width=True, hide_index=True)

# -----------------
# EDIT PRODUCT
# -----------------

st.divider()

st.header("Editar Produto")

if df.empty:
    st.info("Nenhum produto ativo encontrado para editar.")
else:
    edit_options = {
        f"{row['Code']} - {row['Descrição']}": row
        for _, row in df.iterrows()
    }

    selected_edit = st.selectbox(
        "Produto para Editar",
        list(edit_options.keys())
    )

    product_to_edit = edit_options[selected_edit]

    with st.form("edit_product_form"):
        st.text_input(
            "Código do Produto",
            value=product_to_edit["Code"],
            disabled=True
        )

        edited_description = st.text_input(
            "Descrição",
            value=product_to_edit["Descrição"] or ""
        )

        col1, col2 = st.columns(2)

        with col1:
            edited_unit = st.text_input(
                "Unidade",
                value=product_to_edit["Unidade"] or ""
            )

        with col2:
            edited_location = st.text_input(
                "Posição",
                value=product_to_edit["Posição"] or ""
            )

        submitted_edit = st.form_submit_button("Salvar Alterações")

        if submitted_edit:
            if not edited_description.strip():
                st.warning("A descrição não pode ficar vazia.")
            else:
                update_product_info(
                    product_to_edit["Code"],
                    edited_description,
                    edited_unit,
                    edited_location,
                )
                st.success("Produto atualizado com sucesso!")
                st.rerun()

# -----------------
# DEACTIVATE PRODUCT
# -----------------

st.divider()

st.header("Desativar Produto")

if df.empty:
    st.info("Nenhum produto ativo encontrado.")
else:
    product_options = {
        f"{row['Code']} - {row['Descrição']}": row["Code"]
        for _, row in df.iterrows()
    }

    selected_product = st.selectbox(
        "Produto para Desativar",
        list(product_options.keys())
    )

    st.warning(
        "O produto será ocultado do estoque, entradas, saídas, ajustes e requisições de compra. O histórico de movimentações existente será preservado."
    )

    if st.button("Desativar Produto", type="primary"):
        set_product_status(product_options[selected_product], 0)
        st.success("Produto desativado com sucesso!")
        st.rerun()

# -----------------
# INACTIVE PRODUCTS
# -----------------

st.divider()

st.header("Produtos Inativos")

inactive_df = load_products(ativo=0)

if inactive_df.empty:
    st.info("Nenhum produto inativo.")
else:
    st.dataframe(translate_columns(inactive_df), use_container_width=True, hide_index=True)

    inactive_options = {
        f"{row['Code']} - {row['Descrição']}": row["Code"]
        for _, row in inactive_df.iterrows()
    }

    selected_inactive = st.selectbox(
        "Produto para Reativar",
        list(inactive_options.keys())
    )

    if st.button("Reativar Produto"):
        set_product_status(inactive_options[selected_inactive], 1)
        st.success("Produto reativado com sucesso!")
        st.rerun()

