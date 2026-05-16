"""
models/pedido_model.py — CRUD de pedidos, produtos e ranking
"""
from __future__ import annotations
from dataclasses import dataclass, field
import sqlite3
from typing import List, Optional
from .database import DB_PATH, get_connection

TAMANHOS = ["PP", "P", "M", "G", "GG", "XGG", "Único"]
_SZ_COLS  = ["qtd_pp","qtd_p","qtd_m","qtd_g","qtd_gg","qtd_xgg","qtd_unico"]

@dataclass
class ItemPedido:
    referencia: str = ""
    descricao: str = ""
    cor: str = ""
    preco_unitario: float = 0.0
    qtd_pp: int = 0
    qtd_p: int = 0
    qtd_m: int = 0
    qtd_g: int = 0
    qtd_gg: int = 0
    qtd_xgg: int = 0
    qtd_unico: int = 0
    id: Optional[int] = None
    pedido_id: Optional[int] = None

    @property
    def subtotal(self):
        return self.total_pcs * self.preco_unitario

    @property
    def total_pcs(self):
        return sum(getattr(self, col, 0) for col in _SZ_COLS)


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
    vendedor:       str  = ""
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


def listar(busca: str = "", status: str = "") -> list[dict]:
    con = get_connection()
    q = """SELECT id, numero, cliente_nome, dt_pedido, dt_entrega,
                  total_pecas, total_valor, vendedor, status
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
            "desconto","obs_pgto","obs_geral","vendedor","status")
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
        con.execute("""
            INSERT INTO itens_pedido (
                pedido_id, referencia, descricao, cor, preco_unitario,
                qtd_pp, qtd_p, qtd_m, qtd_g, qtd_gg, qtd_xgg, qtd_unico
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pid, it.referencia, it.descricao, it.cor, it.preco_unitario,
              it.qtd_pp, it.qtd_p, it.qtd_m, it.qtd_g, it.qtd_gg,
              it.qtd_xgg, it.qtd_unico))

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
    """Retorna clientes da tabela dedicada + histórico de pedidos."""
    con = get_connection()
    # Clientes cadastrados
    cadastrados = {r["nome"]: dict(r) for r in con.execute("SELECT * FROM clientes ORDER BY nome").fetchall()}
    # Histórico agregado por nome
    hist = {r["cliente_nome"]: dict(r) for r in con.execute("""
        SELECT cliente_nome, cliente_doc, cliente_tel, cliente_email, cliente_cidade,
               COUNT(*) as total_pedidos, SUM(total_valor) as total_gasto
        FROM pedidos GROUP BY cliente_nome ORDER BY cliente_nome
    """).fetchall()}
    con.close()

    resultado = []
    vistos = set()

    # Primeiro, clientes cadastrados (com dados completos)
    for nome, c in cadastrados.items():
        h = hist.get(nome, {})
        resultado.append({
            "cliente_nome": c["nome"],
            "cliente_doc":  c["doc"] or "",
            "cliente_tel":  c["tel"] or "",
            "cliente_email":c["email"] or "",
            "cliente_end":  c.get("endereco","") or "",
            "cliente_cidade":c["cidade"] or "",
            "total_pedidos": h.get("total_pedidos", 0),
            "total_gasto":   h.get("total_gasto", 0.0),
        })
        vistos.add(nome)

    # Depois, clientes que aparecem só em pedidos
    for nome, h in hist.items():
        if nome not in vistos:
            resultado.append({
                "cliente_nome": nome,
                "cliente_doc":  h.get("cliente_doc","") or "",
                "cliente_tel":  h.get("cliente_tel","") or "",
                "cliente_email":h.get("cliente_email","") or "",
                "cliente_end":  "",
                "cliente_cidade":h.get("cliente_cidade","") or "",
                "total_pedidos": h.get("total_pedidos", 0),
                "total_gasto":   h.get("total_gasto", 0.0),
            })

    return sorted(resultado, key=lambda x: x["cliente_nome"])


def dashboard_stats() -> dict:
    con = get_connection()
    total       = con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = con.execute(
        "SELECT COALESCE(SUM(total_valor),0) FROM pedidos WHERE status!='Cancelado'"
    ).fetchone()[0]
    em_prod    = con.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status='Em produção'").fetchone()[0]
    a_entregar = con.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status IN ('Pronto','Confirmado')"
    ).fetchone()[0]
    por_status = [dict(r) for r in con.execute(
        "SELECT status,COUNT(*) as qtd FROM pedidos GROUP BY status").fetchall()]
    recentes   = [dict(r) for r in con.execute(
        "SELECT numero,cliente_nome,total_valor,vendedor, status,dt_entrega "
        "FROM pedidos ORDER BY id DESC LIMIT 6").fetchall()]
    ranking_mais = [dict(r) for r in con.execute("""
        SELECT ip.referencia, ip.descricao,
               SUM(ip.total_pcs) as total_pcs,
               SUM(ip.total_pcs*ip.preco_unitario) as total_valor
        FROM itens_pedido ip JOIN pedidos p ON p.id=ip.pedido_id
        WHERE p.status!='Cancelado' AND ip.referencia!=''
        GROUP BY ip.referencia ORDER BY total_pcs DESC LIMIT 8
    """).fetchall()]
    con.close()
    return dict(total=total, faturamento=faturamento, em_producao=em_prod,
                a_entregar=a_entregar, por_status=por_status, recentes=recentes,
                ranking_mais=ranking_mais)


def referencias_mais_vendidas(limit=10) -> list[dict]:
    con = get_connection()
    rows = con.execute("""
        SELECT referencia, MAX(COALESCE(descricao,'')) as descricao,
               SUM(COALESCE(total_pcs,0)) as total_pecas
        FROM itens_pedido WHERE TRIM(COALESCE(referencia,''))!=''
        GROUP BY referencia ORDER BY total_pecas DESC, referencia ASC LIMIT ?
    """, (limit,)).fetchall()
    con.close()
    return [dict(r) for r in rows]


def buscar_produto(referencia: str) -> Optional[dict]:
    con = get_connection()
    try:
        row = con.execute(
            "SELECT * FROM produtos WHERE referencia=? AND ativo=1", (referencia,)).fetchone()
        if not row:
            con.close()
            return None
        p = dict(row)
        cores = con.execute(
            "SELECT nome_cor,hex_cor FROM produto_cores WHERE produto_id=?", (p["id"],)
        ).fetchall()
        p["cores"] = [dict(c) for c in cores]
        con.close()
        return p
    except Exception:
        con.close()
        return None


def listar_vendedores() -> list[str]:
    con = get_connection()
    try:
        rows = con.execute(
            "SELECT nome FROM vendedores WHERE ativo=1 ORDER BY nome").fetchall()
        con.close()
        return [r["nome"] for r in rows]
    except Exception:
        con.close()
        return []


def buscar_clientes_autocomplete(termo: str) -> list[dict]:
    """Busca clientes para autocomplete no form de pedido."""
    from .cliente_model import buscar_por_nome
    resultado = buscar_por_nome(termo)
    # Também busca nos pedidos existentes
    con = get_connection()
    rows = con.execute("""
        SELECT DISTINCT cliente_nome as nome, cliente_doc as doc,
               cliente_tel as tel, cliente_email as email,
               cliente_end as endereco, cliente_cidade as cidade
        FROM pedidos WHERE cliente_nome LIKE ? ORDER BY cliente_nome LIMIT 10
    """, (f"%{termo}%",)).fetchall()
    con.close()

    nomes_vistos = {r["nome"] for r in resultado}
    for r in rows:
        rd = dict(r)
        if rd["nome"] not in nomes_vistos:
            resultado.append(rd)
            nomes_vistos.add(rd["nome"])
    return resultado[:10]