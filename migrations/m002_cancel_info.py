import sqlite3


def run():

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(movimentacoes)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    if "motivo_cancelamento" not in colunas:
        cursor.execute("""
            ALTER TABLE movimentacoes
            ADD COLUMN motivo_cancelamento TEXT
        """)

    if "data_cancelamento" not in colunas:
        cursor.execute("""
            ALTER TABLE movimentacoes
            ADD COLUMN data_cancelamento TIMESTAMP
        """)

    conn.commit()
    conn.close()
