import streamlit as st
import pandas as pd
import sqlite3

st.title("📥 Importar Produtos")

uploaded_file = st.file_uploader(
    "Selecionar Arquivo Excel",
    type=["xlsx"]
)

if uploaded_file:

    try:

        df = pd.read_excel(
    uploaded_file,
    sheet_name="Banco de Dados",
    header=1

        )

        st.subheader("Pré-visualização")

        st.dataframe(df.head())

        if st.button("Importar Produtos"):

            conn = sqlite3.connect("estoque.db")
            cursor = conn.cursor()

            imported = 0
            duplicates = 0

            for _, row in df.iterrows():

                try:

                    cursor.execute("""
                        INSERT INTO produtos
                        (
                            codigo,
                            descricao,
                            unidade,
                            posicao,
                            qtd_inicial
                        )

                        VALUES (?, ?, ?, ?, ?)

                    """, (

                        str(row["CÃ³digo"]).strip(),
                        str(row["DescriÃ§Ã£o"]).strip(),
                        str(row["Unidade"]).strip(),
                        str(row["PosiÃ§Ã£o"]).strip(),
                        float(row["Qtd Inicial"]) if pd.notna(row["Qtd Inicial"]) else 0

                    ))

                    imported += 1

                except sqlite3.IntegrityError:
                    duplicates += 1

                except:
                    pass

            conn.commit()
            conn.close()

            st.success(
                f"{imported} produtos importados com sucesso!"
            )

            if duplicates > 0:
                st.warning(
                    f"{duplicates} produtos duplicados ignorados."
                )

    except Exception as e:
        st.error(e)

