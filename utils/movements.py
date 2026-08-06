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
        m.observacao AS Observation,
        m.motivo_cancelamento AS Cancellation_Reason,
        m.data_cancelamento AS Cancellation_Date

    FROM movimentacoes m

    INNER JOIN produtos p
        ON p.codigo = m.codigo_produto

    WHERE 1 = 1
    """

    params = []

    if movement_type != "ALL":
        query += """
        AND m.tipo = ?
        """
        params.append(movement_type)

    if search:
        query += """
        AND (
            p.codigo LIKE ?
            OR p.descricao LIKE ?
        )
        """
        params.extend([f"%{search}%", f"%{search}%"])

    query += """
    ORDER BY m.data_movimento DESC
    """

    df = pd.read_sql(query, conn, params=params)

    conn.close()

    return df


def cancel_movement(movement_id, cancellation_reason):

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE movimentacoes
        SET
            status = 0,
            motivo_cancelamento = ?,
            data_cancelamento = CURRENT_TIMESTAMP
        WHERE id = ?
        AND status = 1
    """, (cancellation_reason.strip(), movement_id))

    rows_updated = cursor.rowcount

    conn.commit()
    conn.close()

    return rows_updated
