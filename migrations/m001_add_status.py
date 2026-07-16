import sqlite3


def run():

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    # Verifica as colunas existentes
    cursor.execute("PRAGMA table_info(movimentacoes)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    if "status" not in colunas:

        cursor.execute("""
            ALTER TABLE movimentacoes
            ADD COLUMN status INTEGER DEFAULT 1
        """)

        print("Migration 001 executed successfully.")

    conn.commit()
    conn.close()