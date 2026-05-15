from .database import get_connection

def get(chave: str, default: str = "") -> str:
    con = get_connection()
    row = con.execute("SELECT valor FROM config WHERE chave=?", (chave,)).fetchone()
    con.close()
    return row["valor"] if row else default

def set_value(chave: str, valor: str):
    con = get_connection()
    con.execute("INSERT OR REPLACE INTO config VALUES (?,?)", (chave, valor))
    con.commit(); con.close()

def get_all() -> dict:
    con = get_connection()
    rows = con.execute("SELECT chave, valor FROM config").fetchall()
    con.close()
    return {r["chave"]: r["valor"] for r in rows}

def novo_numero() -> str:
    n = int(get("ultimo_numero","0")) + 1
    set_value("ultimo_numero", str(n))
    return f"PED-{n:05d}"