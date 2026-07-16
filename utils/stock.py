import sqlite3


def save_movement(produto, tipo, quantidade, observacao):

    codigo = produto.split(" - ")[0]

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movimentacoes
        (
            codigo_produto,
            tipo,
            quantidade,
            observacao
        )
        VALUES (?, ?, ?, ?)
    """, (
        codigo,
        tipo,
        quantidade,
        observacao
    ))

    conn.commit()
    conn.close()    