import sqlite3


def conectar():
    conn = sqlite3.connect("estoque.db")
    return conn


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # Tabela Produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descricao TEXT NOT NULL,
            unidade TEXT,
            posicao TEXT,
            qtd_inicial REAL DEFAULT 0,
            ativo INTEGER DEFAULT 1
        )
    """)

    # Tabela Movimentações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_movimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            codigo_produto TEXT NOT NULL,
            tipo TEXT NOT NULL,
            quantidade REAL NOT NULL,
            observacao TEXT,
            FOREIGN KEY (codigo_produto)
                REFERENCES produtos(codigo)
        )
    """)

    conn.commit()
    conn.close()