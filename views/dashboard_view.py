"""
views/dashboard_view.py — Página inicial com estatísticas e rankings
"""
import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import Card, StatCard, PrimaryBtn, build_treeview


class DashboardView(tk.Frame):
    def __init__(self, parent, controller, app):
        super().__init__(parent, bg=CREME)
        self.ctrl = controller
        self.app  = app
        self._counter_job = None
        self._build()

    def _build(self):
        # ── Page header ──────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=CREME)
        hdr.pack(fill="x", padx=PAD_PAGE, pady=(PAD_PAGE, 0))
        tk.Label(hdr, text="Dashboard", font=FONT_TITLE,
                 fg=CINZA_900, bg=CREME).pack(side="left")
        PrimaryBtn(hdr, "＋  Novo pedido",
                   command=self.app.novo_pedido).pack(side="right")
        tk.Label(hdr, text="Visão geral",
                 font=FONT_SMALL, fg=CINZA_500, bg=CREME).pack(
                 side="left", padx=(12, 0))
        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=PAD_PAGE, pady=(10, 0))

        # ── Stat cards ───────────────────────────────────────────────────────
        self._stats_frame = tk.Frame(self, bg=CREME)
        self._stats_frame.pack(fill="x", padx=PAD_PAGE, pady=(16, 0))

        # ── Bottom section: status breakdown + recentes ───────────────────
        bottom = tk.Frame(self, bg=CREME)
        bottom.pack(fill="both", expand=True, padx=PAD_PAGE, pady=16)
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=2)
        bottom.columnconfigure(2, weight=2)
        bottom.rowconfigure(0, weight=1)

        # Status breakdown card
        self._status_card = Card(bottom, title="Por status", accent_left=True)
        self._status_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._status_body = self._status_card.body()

        # Recentes card
        rec_card = Card(bottom, title="Pedidos recentes", accent_left=True)
        rec_card.grid(row=0, column=1, sticky="nsew")
        rec_card.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        rec_body = rec_card.body()

        rank_card = Card(bottom, title="Referências mais vendidas", accent_left=True)
        rank_card.grid(row=0, column=2, sticky="nsew")
        rank_body = rank_card.body()

        cols = [("numero","Número",90), ("cliente_nome","Cliente",180),
                ("total_valor","Valor",90), ("status","Status",110),
                ("dt_entrega","Entrega",90)]
        self._rec_tree = build_treeview(rec_body, cols, height=8)
        self._rec_tree.pack(fill="both", expand=True)
        self._rec_tree.bind("<Double-1>", self._abrir_recente)

        rank_cols = [("pos","#",40), ("referencia","Referência",110),
                     ("descricao","Descrição",170), ("total_pecas","Peças",70)]
        self._rank_tree = build_treeview(rank_body, rank_cols, height=8)
        self._rank_tree.pack(fill="both", expand=True)

        self._configure_tree_columns()
        self._rank_tree.tag_configure("top1", background="#FFF4DD", foreground="#7A4B00")
        self._rank_tree.tag_configure("top2", background="#F4F7FB", foreground="#465A70")
        self._rank_tree.tag_configure("top3", background="#FFF0E6", foreground="#8A4B2F")
        self._rank_tree.tag_configure("default", background=CREME_CARD, foreground=CINZA_700)


    def _configure_tree_columns(self):
        self._rec_tree.heading("numero", anchor="center")
        self._rec_tree.heading("cliente_nome", anchor="w")
        self._rec_tree.heading("total_valor", anchor="e")
        self._rec_tree.heading("status", anchor="center")
        self._rec_tree.heading("dt_entrega", anchor="center")
        self._rec_tree.column("numero", anchor="center")
        self._rec_tree.column("cliente_nome", anchor="w")
        self._rec_tree.column("total_valor", anchor="e")
        self._rec_tree.column("status", anchor="center")
        self._rec_tree.column("dt_entrega", anchor="center")

        self._rank_tree.heading("pos", anchor="center")
        self._rank_tree.heading("referencia", anchor="center")
        self._rank_tree.heading("descricao", anchor="w")
        self._rank_tree.heading("total_pecas", anchor="e")
        self._rank_tree.column("pos", anchor="center", width=42, minwidth=40)
        self._rank_tree.column("referencia", anchor="center")
        self._rank_tree.column("descricao", anchor="w")
        self._rank_tree.column("total_pecas", anchor="e")

    def refresh(self):
        stats = self.ctrl.dashboard()

        # Clear stat cards
        for w in self._stats_frame.winfo_children():
            w.destroy()

        cards_data = [
            ("Total de pedidos", str(stats["total"]), "📋", AZUL),
            ("Faturamento", f"R$ {stats['faturamento']:,.2f}", "💰", "#0F6E56"),
            ("Em produção", str(stats["em_producao"]), "🧶", "#854F0B"),
            ("A entregar", str(stats["a_entregar"]), "📦", "#185FA5"),
        ]
        for i, (title, value, icon, accent) in enumerate(cards_data):
            sc = StatCard(self._stats_frame, title=title, value=value,
                          icon=icon, accent=accent, bg=CREME_CARD)
            sc.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))
            self._stats_frame.columnconfigure(i, weight=1)

        # Status breakdown
        for w in self._status_body.winfo_children():
            w.destroy()
        for row in stats["por_status"]:
            st = row["status"]
            bg, fg = STATUS_COLORS.get(st, (CINZA_100, CINZA_700))
            fr = tk.Frame(self._status_body, bg=CREME_CARD)
            fr.pack(fill="x", pady=3)
            tk.Label(fr, text=f"  {st}", font=FONT_BODY, fg=fg,
                     bg=bg, anchor="w", width=18).pack(side="left")
            tk.Label(fr, text=str(row["qtd"]), font=(FONT_FAMILY, 11, "bold"),
                     fg=fg, bg=bg).pack(side="right", padx=8)

        # Recentes
        for r in self._rec_tree.get_children():
            self._rec_tree.delete(r)
        for rec in stats["recentes"]:
            self._rec_tree.insert("", "end",
                values=(rec["numero"], rec["cliente_nome"],
                        rec.get("vendedor", "—") or "—",
                        f"R$ {rec['total_valor']:.2f}",
                        rec["status"], rec.get("dt_entrega","—")))

        for r in self._rank_tree.get_children():
            self._rank_tree.delete(r)
        for i, row in enumerate(self.ctrl.ranking_referencias(10), start=1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"{i}º"))
            tag = "top1" if i == 1 else ("top2" if i == 2 else ("top3" if i == 3 else "default"))
            self._rank_tree.insert("", "end", values=(
                medal,
                row.get("referencia", ""),
                row.get("descricao", "") or "—",
                row.get("total_pecas", 0),
            ), tags=(tag,))

    def _abrir_recente(self, _):
        sel = self._rec_tree.selection()
        if not sel: return
        num = self._rec_tree.item(sel[0])["values"][0]
        rows = self.ctrl.listar(busca=str(num))
        if rows: self.app.abrir_pedido(rows[0]["id"])