"""
views/lista_view.py
Listagem de pedidos com busca, filtros e ações rápidas.
"""
import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import (Card, PrimaryBtn, SecondaryBtn, DangerBtn,
                            build_treeview, StatusBadge)


STATUS_OPTS = ["Todos","Rascunho","Confirmado","Em produção","Pronto","Entregue","Cancelado"]


class ListaView(tk.Frame):
    def __init__(self, parent, controller, app):
        super().__init__(parent, bg=CREME)
        self.ctrl = controller
        self.app = app
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=CREME)
        hdr.pack(fill="x", padx=PAD_PAGE, pady=(PAD_PAGE, 0))
        tk.Label(hdr, text="Pedidos", font=FONT_TITLE,
                 fg=CINZA_900, bg=CREME).pack(side="left")
        PrimaryBtn(hdr, "＋  Novo pedido",
                   command=self.app.novo_pedido).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=PAD_PAGE, pady=(10, 0))

        # ── Filtros ──────────────────────────────────────────────────────────
        filt = tk.Frame(self, bg=CREME)
        filt.pack(fill="x", padx=PAD_PAGE, pady=(12, 0))

        tk.Label(filt, text="Buscar:", font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME).pack(side="left", padx=(0, 6))
        self._busca = tk.StringVar()
        self._busca.trace_add("write", lambda *_: self.refresh())
        e = ttk.Entry(filt, textvariable=self._busca, width=32, font=FONT_BODY)
        e.pack(side="left", padx=(0, 20))

        tk.Label(filt, text="Status:", font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME).pack(side="left", padx=(0, 6))
        self._status = tk.StringVar(value="Todos")
        cb = ttk.Combobox(filt, textvariable=self._status, width=15,
                          values=STATUS_OPTS, state="readonly", font=FONT_BODY)
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        self._count_lbl = tk.Label(filt, text="", font=FONT_SMALL,
                                    fg=CINZA_500, bg=CREME)
        self._count_lbl.pack(side="right")

        # ── Treeview ─────────────────────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=CREME)
        tree_frame.pack(fill="both", expand=True, padx=PAD_PAGE, pady=(10, 0))

        cols = [
            ("numero",      "Número",   100),
            ("cliente_nome","Cliente",  240),
            ("dt_pedido",   "Pedido",   95),
            ("dt_entrega",  "Entrega",  95),
            ("total_pecas", "Peças",    65),
            ("total_valor", "Total R$", 110),
            ("status",      "Status",   120),
        ]
        self._tree = build_treeview(tree_frame, cols, height=22)
        self._configure_columns()

        sb = ttk.Scrollbar(tree_frame, orient="vertical",
                           command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        # tags de cor por status
        for st, (bg, fg) in STATUS_COLORS.items():
            self._tree.tag_configure(st, foreground=fg)

        self._tree.bind("<Double-1>", lambda _: self._abrir())

        # ── Toolbar ──────────────────────────────────────────────────────────
        bar = tk.Frame(self, bg=CREME,
                       highlightbackground=CINZA_300, highlightthickness=1)
        bar.pack(fill="x", padx=PAD_PAGE, pady=(0, PAD_PAGE))

        SecondaryBtn(bar, "✎  Abrir", command=self._abrir).pack(
            side="left", padx=(8, 4), pady=8)
        SecondaryBtn(bar, "🖨  PDF", command=self._pdf).pack(
            side="left", padx=4, pady=8)
        DangerBtn(bar, "✕  Excluir", command=self._excluir).pack(
            side="left", padx=4, pady=8)

        # status rápido
        tk.Label(bar, text="Alterar status:", font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME).pack(side="right", padx=(0,8), pady=8)
        self._novo_status = tk.StringVar(value="Status")
        st_cb = ttk.Combobox(bar, textvariable=self._novo_status, width=14,
                              values=STATUS_OPTS[1:], state="readonly",
                              font=FONT_SMALL)
        st_cb.pack(side="right", pady=8, padx=4)
        st_cb.bind("<<ComboboxSelected>>", self._change_status)

    def _configure_columns(self):
        for c in ("numero","cliente_nome","dt_pedido","dt_entrega","total_pecas","total_valor","status"):
            self._tree.heading(c, anchor="center")
            self._tree.column(c, anchor="center")

    # ── Actions ──────────────────────────────────────────────────────────────

    def refresh(self):
        for r in self._tree.get_children():
            self._tree.delete(r)
        busca  = self._busca.get()
        status = self._status.get() if self._status.get() != "Todos" else ""
        rows = self.ctrl.listar(busca, status)
        for r in rows:
            valor = f"R$ {r['total_valor']:.2f}" if r["total_valor"] else "R$ 0,00"
            self._tree.insert("", "end", iid=str(r["id"]),
                values=(r["numero"], r["cliente_nome"],
                        r.get("dt_pedido","—"), r.get("dt_entrega","—"),
                        r["total_pecas"], valor, r["status"]),
                tags=(r["status"],))
        self._count_lbl.config(text=f"{len(rows)} pedido(s)")

    def _sel_id(self):
        sel = self._tree.selection()
        return int(sel[0]) if sel else None

    def _abrir(self):
        pid = self._sel_id()
        if pid:
            self.app.abrir_pedido(pid)

    def _excluir(self):
        pid = self._sel_id()
        if pid and self.ctrl.excluir(pid):
            self.refresh()

    def _pdf(self):
        pid = self._sel_id()
        if not pid:
            return
        pedido = self.ctrl.carregar(pid)
        if pedido:
            self.ctrl.exportar_pdf(pedido)

    def _change_status(self, _):
        pid = self._sel_id()
        novo = self._novo_status.get()
        if not pid or novo == "Status":
            return
        from models import pedido_model
        pedido = pedido_model.buscar(pid)
        if pedido:
            pedido.status = novo
            pedido_model.salvar(pedido)
            self.refresh()
        self._novo_status.set("Status")
