"""
models/database.py
Responsável pela conexão e inicialização do banco de dados SQLite.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pedidos.db")


def get_connection() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    con = get_connection()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS config (
        chave TEXT PRIMARY KEY,
        valor TEXT
    );
    INSERT OR IGNORE INTO config VALUES ('empresa_nome', 'Minha Empresa de Tricot');
    INSERT OR IGNORE INTO config VALUES ('empresa_cnpj', '');
    INSERT OR IGNORE INTO config VALUES ('empresa_tel', '');
    INSERT OR IGNORE INTO config VALUES ('empresa_email', '');
    INSERT OR IGNORE INTO config VALUES ('empresa_end', '');
    INSERT OR IGNORE INTO config VALUES ('ultimo_numero', '0');

    CREATE TABLE IF NOT EXISTS pedidos (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        numero      TEXT UNIQUE NOT NULL,
        cliente_nome  TEXT NOT NULL,
        cliente_doc   TEXT,
        cliente_tel   TEXT,
        cliente_email TEXT,
        cliente_end   TEXT,
        cliente_cidade TEXT,
        dt_pedido     TEXT,
        dt_entrega    TEXT,
        tipo_entrega  TEXT,
        obs_entrega   TEXT,
        forma_pgto    TEXT,
        prazo_pgto    TEXT,
        desconto      REAL DEFAULT 0,
        entrada       REAL DEFAULT 0,
        obs_pgto      TEXT,
        obs_geral     TEXT,
        status        TEXT DEFAULT 'Rascunho',
        total_pecas   INTEGER DEFAULT 0,
        total_valor   REAL DEFAULT 0,
        criado_em     TEXT
    );

    CREATE TABLE IF NOT EXISTS itens_pedido (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id       INTEGER NOT NULL,
        referencia      TEXT,
        descricao       TEXT,
        cor             TEXT,
        material        TEXT,
        preco_unitario  REAL DEFAULT 0,
        qtd_pp          INTEGER DEFAULT 0,
        qtd_p           INTEGER DEFAULT 0,
        qtd_m           INTEGER DEFAULT 0,
        qtd_g           INTEGER DEFAULT 0,
        qtd_gg          INTEGER DEFAULT 0,
        qtd_xgg         INTEGER DEFAULT 0,
        qtd_unico       INTEGER DEFAULT 0,
        total_pcs       INTEGER DEFAULT 0,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
    );
    """)
    con.commit()
    con.close()
