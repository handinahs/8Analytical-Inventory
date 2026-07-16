import sqlite3
import pandas as pd


def get_all_movements(movement_type="ALL", search=""):

    conn = sqlite3.connect("estoque.db")

    query = """
    SELECT
        m.id,
        m.data_movimento AS Date,
        p.codigo AS Code,
        p.descricao AS Product,
        m.tipo AS Type,
        m.quantidade AS Quantity,
        m.status AS Status,
        m.observacao AS Observation

    FROM movimentacoes m

    INNER JOIN produtos p
        ON p.codigo = m.codigo_produto

    WHERE 1 = 1
    """

    if movement_type != "ALL":
        query += f"""
        AND m.tipo = '{movement_type}'
        """

    if search:
        query += f"""
        AND (
            p.codigo LIKE '%{search}%'
            OR p.descricao LIKE '%{search}%'
        )
        """

    query += """
    ORDER BY m.data_movimento DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


def cancel_movement(movement_id):

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE movimentacoes
        SET status = 0
        WHERE id = ?
        AND status = 1
    """, (movement_id,))

    conn.commit()
    conn.close()

