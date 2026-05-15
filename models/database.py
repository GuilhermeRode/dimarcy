"""
models/database.py — Conexão SQLite e inicialização do banco de dados
"""
import sqlite3, os, hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dimarcy.db")


def get_connection() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def _hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def init_db():
    con = get_connection()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS config (
        chave TEXT PRIMARY KEY, valor TEXT
    );
    INSERT OR IGNORE INTO config VALUES ('empresa_nome', 'Di Marcy');
    INSERT OR IGNORE INTO config VALUES ('empresa_cnpj', '');
    INSERT OR IGNORE INTO config VALUES ('empresa_tel',  '');
    INSERT OR IGNORE INTO config VALUES ('empresa_email','');
    INSERT OR IGNORE INTO config VALUES ('empresa_end',  '');
    INSERT OR IGNORE INTO config VALUES ('ultimo_numero','0');

    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL, perfil TEXT DEFAULT 'vendedor',
        ativo INTEGER DEFAULT 1, criado_em TEXT
    );

    CREATE TABLE IF NOT EXISTS vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE, ativo INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referencia TEXT NOT NULL UNIQUE, descricao TEXT NOT NULL,
        preco REAL DEFAULT 0, ativo INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS produto_cores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL, nome_cor TEXT NOT NULL,
        hex_cor TEXT NOT NULL DEFAULT '#888888',
        FOREIGN KEY(produto_id) REFERENCES produtos(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE NOT NULL, vendedor TEXT DEFAULT '',
        cliente_nome TEXT NOT NULL, cliente_doc TEXT, cliente_tel TEXT,
        cliente_email TEXT, cliente_end TEXT, cliente_cidade TEXT,
        dt_pedido TEXT, dt_entrega TEXT, tipo_entrega TEXT,
        obs_entrega TEXT, forma_pgto TEXT, prazo_pgto TEXT,
        desconto REAL DEFAULT 0, obs_pgto TEXT, obs_geral TEXT,
        status TEXT DEFAULT 'Rascunho',
        total_pecas INTEGER DEFAULT 0, total_valor REAL DEFAULT 0, criado_em TEXT
    );

    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL, referencia TEXT, descricao TEXT,
        cor TEXT, hex_cor TEXT DEFAULT '#888888',
        preco_unitario REAL DEFAULT 0,
        qtd_pp INTEGER DEFAULT 0, qtd_p INTEGER DEFAULT 0,
        qtd_m INTEGER DEFAULT 0, qtd_g INTEGER DEFAULT 0,
        qtd_gg INTEGER DEFAULT 0, qtd_xgg INTEGER DEFAULT 0,
        qtd_unico INTEGER DEFAULT 0, total_pcs INTEGER DEFAULT 0,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
    );
    """)

    if not cur.execute("SELECT id FROM usuarios WHERE usuario='admin'").fetchone():
        cur.execute(
            "INSERT INTO usuarios (nome,usuario,senha,perfil,criado_em) VALUES (?,?,?,?,?)",
            ("Administrador","admin",_hash("admin123"),"admin",
             datetime.now().strftime("%d/%m/%Y %H:%M")))

    if cur.execute("SELECT COUNT(*) FROM vendedores").fetchone()[0] == 0:
        for v in ["Ana Paula","Carlos Mendes","Fernanda Lima","Equipe interna"]:
            cur.execute("INSERT OR IGNORE INTO vendedores (nome) VALUES (?)",(v,))

    if cur.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
        demo = [
            ("1130","Calça fusô",109.80,[
                ("Preto","#1A1A1A"),("Marinho","#1B2A4A"),("Cinza","#777777")]),
            ("1163","Calça sweet friso",139.80,[
                ("Preto","#1A1A1A"),("Rosa","#E8557A"),("Verde","#3A7D44")]),
            ("1164","Blusa sweet friso",139.80,[
                ("Off-white","#F5F0E8"),("Azul","#2E6DA4"),("Caramelo","#C8813A")]),
            ("2001","Blusa térmica feminina",39.80,[
                ("Preto","#1A1A1A"),("Branco","#F5F5F5"),("Bordô","#7B1A2E")]),
            ("3010","Cardigan clássico",85.00,[
                ("Creme","#F5EDD6"),("Caramelo","#C8813A"),("Cinza mescla","#9E9E9E")]),
            ("3021","Conjunto tricot",195.00,[
                ("Azul marinho","#1B2A4A"),("Rosa antigo","#C47E8A"),("Areia","#C8B89A")]),
        ]
        for ref,desc,preco,cores in demo:
            cur.execute(
                "INSERT OR IGNORE INTO produtos (referencia,descricao,preco) VALUES (?,?,?)",
                (ref,desc,preco))
            pid=cur.execute("SELECT id FROM produtos WHERE referencia=?",(ref,)).fetchone()[0]
            for nome_cor,hex_cor in cores:
                cur.execute(
                    "INSERT INTO produto_cores (produto_id,nome_cor,hex_cor) VALUES (?,?,?)",
                    (pid,nome_cor,hex_cor))

    # migrações
    cols_p = [r[1] for r in cur.execute("PRAGMA table_info(pedidos)").fetchall()]
    if "vendedor" not in cols_p:
        cur.execute("ALTER TABLE pedidos ADD COLUMN vendedor TEXT DEFAULT ''")
    cols_i = [r[1] for r in cur.execute("PRAGMA table_info(itens_pedido)").fetchall()]
    if "hex_cor" not in cols_i:
        cur.execute("ALTER TABLE itens_pedido ADD COLUMN hex_cor TEXT DEFAULT '#888888'")

    con.commit()
    con.close()


def autenticar(usuario: str, senha: str) -> dict | None:
    con = get_connection()
    row = con.execute(
        "SELECT * FROM usuarios WHERE usuario=? AND senha=? AND ativo=1",
        (usuario, _hash(senha))).fetchone()
    con.close()
    return dict(row) if row else None