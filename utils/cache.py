import sqlite3
import pandas as pd
import streamlit as st


@st.cache_data
def load_products():

    conn = sqlite3.connect("estoque.db")

    df = pd.read_sql("""

    SELECT
        codigo,
        descricao

    FROM produtos

    WHERE ativo = 1

    ORDER BY descricao

    """, conn)

    conn.close()

    return df
