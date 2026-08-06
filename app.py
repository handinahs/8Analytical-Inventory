import sqlite3

import pandas as pd
import streamlit as st

from database import criar_tabelas
from migrations import m001_add_status, m002_cancel_info
from utils.ui import format_and_translate_columns


st.set_page_config(
    page_title="8Analytical Inventory",
    page_icon="📦",
    layout="wide",
)

criar_tabelas()
m001_add_status.run()
m002_cancel_info.run()


def show_dashboard():
    st.image("assets/logo_8analytical_inventory.png", width=208)
    st.title("8Analytical Inventory")
    st.caption("Controle de estoque e almoxarifado")

    conn = sqlite3.connect("estoque.db")

    total_products = pd.read_sql(
        "SELECT COUNT(*) AS total FROM produtos WHERE ativo = 1", conn
    ).iloc[0]["total"]

    total_stock = pd.read_sql(
        """
        SELECT SUM(
            p.qtd_inicial
            + COALESCE((SELECT SUM(quantidade) FROM movimentacoes
                        WHERE codigo_produto = p.codigo AND tipo = 'IN' AND status = 1), 0)
            - COALESCE((SELECT SUM(quantidade) FROM movimentacoes
                        WHERE codigo_produto = p.codigo AND tipo = 'OUT' AND status = 1), 0)
        ) AS total_estoque
        FROM produtos p
        WHERE p.ativo = 1
        """,
        conn,
    ).iloc[0]["total_estoque"]

    zero_stock = pd.read_sql(
        """
        SELECT COUNT(*) AS total
        FROM (
            SELECT p.codigo,
                p.qtd_inicial
                + COALESCE((SELECT SUM(quantidade) FROM movimentacoes
                            WHERE codigo_produto = p.codigo AND tipo = 'IN' AND status = 1), 0)
                - COALESCE((SELECT SUM(quantidade) FROM movimentacoes
                            WHERE codigo_produto = p.codigo AND tipo = 'OUT' AND status = 1), 0) AS saldo
            FROM produtos p
            WHERE p.ativo = 1
        )
        WHERE saldo <= 0
        """,
        conn,
    ).iloc[0]["total"]

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Produtos", f"{total_products:,}")
    col2.metric("🏪 Estoque Total", f"{total_stock or 0:,.0f}")
    col3.metric("⚠️ Produtos Sem Estoque", f"{zero_stock:,}")

    st.divider()
    st.subheader("🕒 Últimas Movimentações")

    movements = pd.read_sql(
        """
        SELECT m.data_movimento AS Date, p.codigo AS Code, p.descricao AS Product,
               m.tipo AS Type, m.quantidade AS Quantity
        FROM movimentacoes m
        INNER JOIN produtos p ON p.codigo = m.codigo_produto
        WHERE m.status = 1 AND p.ativo = 1
        ORDER BY m.data_movimento DESC
        LIMIT 10
        """,
        conn,
    )
    conn.close()

    movements["Type"] = movements["Type"].map({"IN": "Entrada", "OUT": "Saída"})
    st.dataframe(format_and_translate_columns(movements), use_container_width=True, hide_index=True)


navigation = {
    "⌂ GERAL": [
        st.Page(show_dashboard, title="Dashboard", icon="🏠", default=True),
        st.Page("pages/4_Inventory.py", title="Estoque Atual", icon="📋"),
        st.Page("pages/13_Quick_Search.py", title="Busca Rápida", icon="🔎"),
    ],
    "↔ MOVIMENTAÇÕES": [
        st.Page("pages/2_Stock_In.py", title="Entrada de Estoque", icon="📥"),
        st.Page("pages/3_Stock_Out.py", title="Saída de Estoque", icon="📤"),
        st.Page("pages/7_Stock_Adjustment.py", title="Ajuste de Estoque", icon="⚖️"),
        st.Page("pages/8_All_Movements.py", title="Todas as Movimentações", icon="🧾"),
    ],
    "▣ CADASTROS E DOCUMENTOS": [
        st.Page("pages/1_Products.py", title="Produtos", icon="📦"),
        st.Page("pages/10_Position_Adjustment.py", title="Ajuste de Posição", icon="📍"),
        st.Page("pages/6_Import_Products.py", title="Importar Produtos", icon="📥"),
        st.Page("pages/9_Purchase_Request.py", title="Requisição de Compras", icon="🧾"),
        st.Page("pages/14_Material_List.py", title="LM - Lista de Materiais", icon="📄"),
        st.Page("pages/11_Stock_Report.py", title="Relatório de Estoque", icon="📑"),
    ],
    "▥ ANÁLISES": [
        st.Page("pages/5_Reports.py", title="Relatórios", icon="📊"),
    ],
    "⚙ SISTEMA": [
        st.Page("pages/12_Backup.py", title="Backup", icon="💾"),
    ],
}

selected_page = st.navigation(navigation)
selected_page.run()
