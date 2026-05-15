"""
models/pedido_model.py
CRUD completo de pedidos e itens.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import date as _date
from .database import get_connection

TAMANHOS = ["PP", "P", "M", "G", "GG", "XGG", "Único"]
_SZ_COLS  = ["qtd_pp","qtd_p","qtd_m","qtd_g","qtd_gg","qtd_xgg","qtd_unico"]


# ── Data classes ────────────────────────────────────────────────────────────────

@dataclass
class ItemPedido:
    referencia:     str  = ""
    descricao:      str  = ""
    cor:            str  = ""
    preco_unitario: float = 0.0
    qtd_pp:    int = 0
    qtd_p:     int = 0
    qtd_m:     int = 0
    qtd_g:     int = 0
    qtd_gg:    int = 0
    qtd_xgg:   int = 0
    qtd_unico: int = 0
    id: Optional[int] = None
    pedido_id: Optional[int] = None

    @property
    def total_pcs(self) -> int:
        return sum(getattr(self, c) for c in _SZ_COLS)

    @property
    def subtotal(self) -> float:
        return self.total_pcs * self.preco_unitario

    def qtds_dict(self) -> dict:
        return {s: getattr(self, c) for s, c in zip(TAMANHOS, _SZ_COLS)}


@dataclass
class Pedido:
    cliente_nome:   str  = ""
    cliente_doc:    str  = ""
    cliente_tel:    str  = ""
    cliente_email:  str  = ""
    cliente_end:    str  = ""
    cliente_cidade: str  = ""
    dt_pedido:      str  = ""
    dt_entrega:     str  = ""
    tipo_entrega:   str  = "Retirada na fábrica"
    obs_entrega:    str  = ""
    forma_pgto:     str  = "À vista — PIX"
    prazo_pgto:     str  = "No ato"
    desconto:       float = 0.0
    obs_pgto:       str  = ""
    obs_geral:      str  = ""
    status:         str  = "Rascunho"
    numero:         str  = ""
    id: Optional[int]    = None
    itens: List[ItemPedido] = field(default_factory=list)

    @property
    def total_pecas(self) -> int:
        return sum(i.total_pcs for i in self.itens)

    @property
    def valor_bruto(self) -> float:
        return sum(i.subtotal for i in self.itens)

    @property
    def valor_liquido(self) -> float:
        return self.valor_bruto * (1 - self.desconto / 100)



# ── Repository ──────────────────────────────────────────────────────────────────

def _row_to_pedido(row) -> Pedido:
    d = dict(row)
    itens_raw = d.pop("itens", [])
    p = Pedido(**{k: v for k, v in d.items()
                  if k in Pedido.__dataclass_fields__})
    return p


def listar(busca: str = "", status: str = "") -> list[dict]:
    con = get_connection()
    q = """SELECT id, numero, cliente_nome, dt_pedido, dt_entrega,
                  total_pecas, total_valor, status
           FROM pedidos"""
    params = []
    wheres = []
    if status:
        wheres.append("status = ?")
        params.append(status)
    if busca:
        wheres.append("(numero LIKE ? OR cliente_nome LIKE ? OR status LIKE ?)")
        b = f"%{busca}%"
        params += [b, b, b]
    if wheres:
        q += " WHERE " + " AND ".join(wheres)
    q += " ORDER BY id DESC"
    rows = [dict(r) for r in con.execute(q, params).fetchall()]
    con.close()
    return rows


def buscar(pedido_id: int) -> Optional[Pedido]:
    con = get_connection()
    row = con.execute("SELECT * FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if not row:
        con.close()
        return None
    p = Pedido(**{k: row[k] for k in Pedido.__dataclass_fields__
                  if k not in ("itens",) and k in row.keys()})
    irows = con.execute(
        "SELECT * FROM itens_pedido WHERE pedido_id=?", (pedido_id,)).fetchall()
    p.itens = [ItemPedido(**{k: r[k] for k in ItemPedido.__dataclass_fields__
                              if k in r.keys()}) for r in irows]
    con.close()
    return p


def salvar(p: Pedido) -> int:
    con = get_connection()
    campos = ("cliente_nome","cliente_doc","cliente_tel","cliente_email",
              "cliente_end","cliente_cidade","dt_pedido","dt_entrega",
              "tipo_entrega","obs_entrega","forma_pgto","prazo_pgto",
              "desconto","obs_pgto","obs_geral","status")
    vals = tuple(getattr(p, c) for c in campos)
    total_pcs = p.total_pecas
    total_val = p.valor_liquido

    if p.id:
        sets = ", ".join(f"{c}=?" for c in campos)
        con.execute(
            f"UPDATE pedidos SET {sets}, total_pecas=?, total_valor=? WHERE id=?",
            vals + (total_pcs, total_val, p.id))
        con.execute("DELETE FROM itens_pedido WHERE pedido_id=?", (p.id,))
        pid = p.id
    else:
        from .config_model import novo_numero
        from datetime import datetime
        p.numero = novo_numero()
        cols = ("numero",) + campos + ("total_pecas","total_valor","criado_em")
        placeholders = ",".join("?" for _ in cols)
        con.execute(
            f"INSERT INTO pedidos ({','.join(cols)}) VALUES ({placeholders})",
            (p.numero,) + vals + (total_pcs, total_val,
                                   datetime.now().strftime("%d/%m/%Y %H:%M")))
        pid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        p.id = pid

    for it in p.itens:
        con.execute("""INSERT INTO itens_pedido
            (pedido_id,referencia,descricao,cor,preco_unitario,
             qtd_pp,qtd_p,qtd_m,qtd_g,qtd_gg,qtd_xgg,qtd_unico,total_pcs)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (pid, it.referencia, it.descricao, it.cor,
             it.preco_unitario, it.qtd_pp, it.qtd_p, it.qtd_m,
             it.qtd_g, it.qtd_gg, it.qtd_xgg, it.qtd_unico, it.total_pcs))
    con.commit()
    con.close()
    return pid


def excluir(pedido_id: int):
    con = get_connection()
    con.execute("DELETE FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
    con.execute("DELETE FROM pedidos WHERE id=?", (pedido_id,))
    con.commit()
    con.close()


def clientes_unicos() -> list[dict]:
    con = get_connection()
    rows = con.execute("""
        SELECT DISTINCT cliente_nome, cliente_doc, cliente_tel,
               cliente_email, cliente_cidade,
               COUNT(*) as total_pedidos,
               SUM(total_valor) as total_gasto
        FROM pedidos
        GROUP BY cliente_nome, cliente_doc
        ORDER BY cliente_nome
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]


def dashboard_stats() -> dict:
    con = get_connection()
    total  = con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = con.execute(
        "SELECT COALESCE(SUM(total_valor),0) FROM pedidos WHERE status != 'Cancelado'"
    ).fetchone()[0]
    em_prod = con.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status='Em produção'"
    ).fetchone()[0]
    a_entregar = con.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status IN ('Pronto','Confirmado')"
    ).fetchone()[0]
    por_status = con.execute("""
        SELECT status, COUNT(*) as qtd FROM pedidos GROUP BY status
    """).fetchall()
    recentes = con.execute("""
        SELECT numero, cliente_nome, total_valor, status, dt_entrega
        FROM pedidos ORDER BY id DESC LIMIT 5
    """).fetchall()
    con.close()
    return {
        "total": total,
        "faturamento": faturamento,
        "em_producao": em_prod,
        "a_entregar": a_entregar,
        "por_status": [dict(r) for r in por_status],
        "recentes": [dict(r) for r in recentes],
    }

def referencias_mais_vendidas(limit: int = 10) -> list[dict]:
    con = get_connection()
    rows = con.execute("""
        SELECT referencia,
               MAX(COALESCE(descricao, '')) as descricao,
               SUM(COALESCE(total_pcs, 0)) as total_pecas
        FROM itens_pedido
        WHERE TRIM(COALESCE(referencia, '')) != ''
        GROUP BY referencia
        ORDER BY total_pecas DESC, referencia ASC
        LIMIT ?
    """, (limit,)).fetchall()
    con.close()
    return [dict(r) for r in rows]

