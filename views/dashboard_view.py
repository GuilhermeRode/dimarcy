"""
views/dashboard_view.py
Página inicial com estatísticas e pedidos recentes.
"""
import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import Card, StatCard, PrimaryBtn, build_treeview, StatusBadge


class DashboardView(tk.Frame):
    def __init__(self, parent, controller, app):
        super().__init__(parent, bg=CREME)
        self.ctrl = controller
        self.app = app
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
        bottom.rowconfigure(0, weight=1)

        # Status breakdown card
        self._status_card = Card(bottom, title="Por status", accent_left=True)
        self._status_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._status_body = self._status_card.body()

        # Recentes card
        rec_card = Card(bottom, title="Pedidos recentes", accent_left=True)
        rec_card.grid(row=0, column=1, sticky="nsew")
        rec_body = rec_card.body()

        cols = [("numero","Número",90), ("cliente_nome","Cliente",180),
                ("total_valor","Valor",90), ("status","Status",110),
                ("dt_entrega","Entrega",90)]
        self._rec_tree = build_treeview(rec_body, cols, height=8)
        self._rec_tree.pack(fill="both", expand=True)
        self._rec_tree.bind("<Double-1>", self._abrir_recente)

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
                        f"R$ {rec['total_valor']:.2f}",
                        rec["status"], rec.get("dt_entrega","—")))

    def _abrir_recente(self, _):
        sel = self._rec_tree.selection()
        if not sel:
            return
        num = self._rec_tree.item(sel[0])["values"][0]
        # find id by numero
        rows = self.ctrl.listar(busca=num)
        if rows:
            self.app.abrir_pedido(rows[0]["id"])
