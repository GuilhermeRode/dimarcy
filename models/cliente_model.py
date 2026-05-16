"""
models/cliente_model.py — CRUD de clientes cadastrados
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .database import get_connection


@dataclass
class Cliente:
    nome:      str = ""
    doc:       str = ""
    tel:       str = ""
    email:     str = ""
    endereco:  str = ""
    cidade:    str = ""
    id: Optional[int] = None


def listar(busca: str = "") -> list[dict]:
    con = get_connection()
    q = "SELECT * FROM clientes"
    params = []
    if busca:
        q += " WHERE nome LIKE ? OR doc LIKE ? OR cidade LIKE ?"
        b = f"%{busca}%"
        params = [b, b, b]
    q += " ORDER BY nome"
    rows = [dict(r) for r in con.execute(q, params).fetchall()]
    con.close()
    return rows


def buscar(cliente_id: int) -> Optional[Cliente]:
    con = get_connection()
    row = con.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone()
    con.close()
    if not row:
        return None
    return Cliente(**{k: row[k] for k in Cliente.__dataclass_fields__ if k in row.keys()})


def salvar(c: Cliente) -> int:
    con = get_connection()
    campos = ("nome", "doc", "tel", "email", "endereco", "cidade")
    vals = tuple(getattr(c, f) for f in campos)
    if c.id:
        sets = ", ".join(f"{f}=?" for f in campos)
        con.execute(f"UPDATE clientes SET {sets} WHERE id=?", vals + (c.id,))
        cid = c.id
    else:
        placeholders = ",".join("?" * len(campos))
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        con.execute(
            f"INSERT INTO clientes ({','.join(campos)}, criado_em) VALUES ({placeholders},?)",
            vals + (now,)
        )
        cid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        c.id = cid
    con.commit()
    con.close()
    return cid


def excluir(cliente_id: int):
    con = get_connection()
    con.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    con.commit()
    con.close()


def buscar_por_nome(termo: str) -> list[dict]:
    """Autocomplete: retorna clientes cujo nome contém o termo."""
    con = get_connection()
    rows = con.execute(
        "SELECT * FROM clientes WHERE nome LIKE ? ORDER BY nome LIMIT 10",
        (f"%{termo}%",)
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]