from datetime import date, timedelta
import sqlite3

import pandas as pd
import streamlit as st

from utils.ui import format_and_translate_columns, render_brand_header, translate_columns


DB_PATH = "estoque.db"


def load_stock_summary():
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


def load_period_movements(start_date, end_date):
    conn = sqlite3.connect(DB_PATH)
    next_day = end_date + timedelta(days=1)

    query = """
    SELECT
        m.data_movimento AS Date,
        m.tipo AS Type,
        m.quantidade AS Quantity,
        m.status AS Status,
        p.codigo AS Code,
        p.descricao AS Product,
        p.unidade AS Unit
    FROM movimentacoes m
    INNER JOIN produtos p ON p.codigo = m.codigo_produto
    WHERE m.data_movimento >= ?
      AND m.data_movimento < ?
    ORDER BY m.data_movimento DESC
    """

    df = pd.read_sql(query, conn, params=(start_date.isoformat(), next_day.isoformat()))
    conn.close()
    return df


def get_period_dates(period):
    today = date.today()

    if period == "Hoje":
        return today, today
    if period == "Últimos 7 dias":
        return today - timedelta(days=6), today
    if period == "Mês anterior":
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        return last_month_end.replace(day=1), last_month_end

    return today.replace(day=1), today


render_brand_header("📊 Relatórios")

period_options = ["Hoje", "Últimos 7 dias", "Este mês", "Mês anterior", "Personalizado"]
period = st.selectbox("Período", period_options, index=2)

if period == "Personalizado":
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("Data inicial", value=date.today().replace(day=1))
    with date_col2:
        end_date = st.date_input("Data final", value=date.today())

    if start_date > end_date:
        st.error("A data inicial não pode ser posterior à data final.")
        st.stop()
else:
    start_date, end_date = get_period_dates(period)

stock_df = load_stock_summary()
movements_df = load_period_movements(start_date, end_date)

total_products = len(stock_df)
total_stock = stock_df["Current_Stock"].sum() if not stock_df.empty else 0
zero_stock = len(stock_df[stock_df["Current_Stock"] == 0])
negative_stock = len(stock_df[stock_df["Current_Stock"] < 0])

st.caption(f"Dados de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Produtos ativos", f"{total_products:,}".replace(",", "."))
metric2.metric("Estoque total", f"{total_stock:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
metric3.metric("Itens sem estoque", f"{zero_stock:,}".replace(",", "."))
metric4.metric("Saldo negativo", f"{negative_stock:,}".replace(",", "."))

st.divider()
st.subheader("Movimentações do Período")

valid_movements = movements_df[movements_df["Status"] == 1].copy()
cancelled_movements = movements_df[movements_df["Status"] == 0].copy()

entries = valid_movements.loc[valid_movements["Type"] == "IN", "Quantity"].sum()
outputs = valid_movements.loc[valid_movements["Type"] == "OUT", "Quantity"].sum()

movement_metric1, movement_metric2, movement_metric3 = st.columns(3)
movement_metric1.metric("Entradas", f"{entries:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
movement_metric2.metric("Saídas", f"{outputs:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
movement_metric3.metric("Movimentações canceladas", len(cancelled_movements))

if valid_movements.empty:
    st.info("Não há movimentações válidas no período selecionado.")
else:
    chart_df = valid_movements.copy()
    chart_df["Dia"] = pd.to_datetime(chart_df["Date"]).dt.strftime("%d/%m")
    chart_df["Tipo"] = chart_df["Type"].map({"IN": "Entradas", "OUT": "Saídas"})
    chart_df = chart_df.groupby(["Dia", "Tipo"])["Quantity"].sum().unstack(fill_value=0)
    st.bar_chart(chart_df, use_container_width=True)

st.divider()
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Itens que Precisam de Atenção")
    attention_df = stock_df[stock_df["Current_Stock"] <= 0].copy()

    if attention_df.empty:
        st.success("Nenhum item está sem estoque ou com saldo negativo.")
    else:
        attention_df["Situation"] = attention_df["Current_Stock"].apply(
            lambda stock: "Saldo negativo" if stock < 0 else "Sem estoque"
        )
        attention_df = attention_df.sort_values("Current_Stock")
        display_attention = attention_df[["Code", "Product", "Unit", "Location", "Current_Stock", "Situation"]]
        display_attention = display_attention.rename(columns={"Situation": "Situação"})
        st.dataframe(translate_columns(display_attention), use_container_width=True, hide_index=True)

with right_column:
    st.subheader("Produtos Mais Movimentados")

    if valid_movements.empty:
        st.info("Ainda não há dados de movimentação para este período.")
    else:
        top_products = (
            valid_movements.groupby(["Code", "Product", "Unit"], as_index=False)["Quantity"]
            .sum()
            .sort_values("Quantity", ascending=False)
            .head(10)
        )
        top_products = top_products.rename(columns={"Quantity": "Movimentado"})
        st.dataframe(translate_columns(top_products), use_container_width=True, hide_index=True)

st.divider()
st.subheader("Últimas Movimentações do Período")

if movements_df.empty:
    st.info("Nenhuma movimentação encontrada no período selecionado.")
else:
    recent_df = movements_df.copy()
    recent_df["Type"] = recent_df["Type"].map({"IN": "Entrada", "OUT": "Saída"})
    recent_df["Status"] = recent_df["Status"].map({1: "🟢 Ativa", 0: "🔴 Cancelada"})
    recent_df = recent_df[["Date", "Code", "Product", "Type", "Quantity", "Status"]].head(10)
    st.dataframe(format_and_translate_columns(recent_df), use_container_width=True, hide_index=True)
