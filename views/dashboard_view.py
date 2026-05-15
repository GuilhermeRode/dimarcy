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
        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=CREME)
        hdr.pack(fill="x", padx=PAD_PAGE, pady=(PAD_PAGE, 0))
        tk.Label(hdr, text="Dashboard", font=FONT_TITLE,
                 fg=CINZA_900, bg=CREME).pack(side="left")
        PrimaryBtn(hdr, "＋  Novo pedido",
                   command=self.app.novo_pedido).pack(side="right")
        self._saudacao = tk.Label(hdr, text="", font=FONT_SMALL,
                                   fg=CINZA_500, bg=CREME)
        self._saudacao.pack(side="left", padx=(12, 0))
        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=PAD_PAGE, pady=(10, 0))

        # ── Stat cards ───────────────────────────────────────────────────────
        self._stats_frame = tk.Frame(self, bg=CREME)
        self._stats_frame.pack(fill="x", padx=PAD_PAGE, pady=(16, 0))

        # ── Linha inferior ────────────────────────────────────────────────
        bottom = tk.Frame(self, bg=CREME)
        bottom.pack(fill="both", expand=True, padx=PAD_PAGE, pady=12)
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=2)
        bottom.columnconfigure(2, weight=2)
        bottom.rowconfigure(0, weight=1)

        # Status
        sc = Card(bottom, title="Por status", accent_left=True)
        sc.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._status_body = sc.body()

        # Recentes
        rc = Card(bottom, title="Pedidos recentes", accent_left=True)
        rc.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        rb = rc.body()
        cols_rec = [("numero","Número",88),("cliente_nome","Cliente",160),
                    ("total_valor","Valor R$",88),("status","Status",100),
                    ("dt_entrega","Entrega",84)]
        self._rec_tree = build_treeview(rb, cols_rec, height=7)
        self._rec_tree.pack(fill="both", expand=True)
        self._rec_tree.bind("<Double-1>", self._abrir_recente)

        # Rankings
        rank_card = Card(bottom, title="Ranking de referências", accent_left=True)
        rank_card.grid(row=0, column=2, sticky="nsew")
        rank_body = rank_card.body()

        # Tabs dentro do card
        nb = ttk.Notebook(rank_body)
        nb.pack(fill="both", expand=True)

        tab_mais  = tk.Frame(nb, bg=BRANCO_CARD)
        tab_menos = tk.Frame(nb, bg=BRANCO_CARD)
        nb.add(tab_mais,  text="🏆 Mais vendidas")
        nb.add(tab_menos, text="📉 Menos vendidas")

        cols_rank = [("pos","#",36),("referencia","Ref.",80),
                     ("descricao","Descrição",160),("total_pcs","Peças",60)]
        self._mais_tree  = build_treeview(tab_mais,  cols_rank, height=7)
        self._menos_tree = build_treeview(tab_menos, cols_rank, height=7)
        self._mais_tree.pack(fill="both", expand=True)
        self._menos_tree.pack(fill="both", expand=True)

        # Tags de destaque
        for tree in (self._mais_tree, self._menos_tree):
            tree.tag_configure("gold",   background="#FFF8E1", foreground="#7A4B00")
            tree.tag_configure("silver", background="#F5F7FA", foreground="#4A5560")
            tree.tag_configure("bronze", background="#FFF3ED", foreground="#7A3510")
            tree.tag_configure("normal", background=BRANCO_CARD, foreground=CINZA_700)

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self):
        stats = self.ctrl.dashboard()
        self._atualizar_saudacao()
        self._atualizar_stat_cards(stats)
        self._atualizar_status(stats)
        self._atualizar_recentes(stats)
        self._atualizar_rankings(stats)
        self._iniciar_contador()

    def _atualizar_saudacao(self):
        from datetime import datetime
        h = datetime.now().hour
        s = "Bom dia" if h < 12 else ("Boa tarde" if h < 18 else "Boa noite")
        nome = getattr(self.app, "_usuario_nome", "")
        self._saudacao.config(text=f"{s}{', ' + nome if nome else ''}  —  Visão geral")

    def _atualizar_stat_cards(self, stats):
        for w in self._stats_frame.winfo_children():
            w.destroy()
        data = [
            ("Total de pedidos",  str(stats["total"]),                   "📋", AZUL),
            ("Faturamento",       f"R$ {stats['faturamento']:,.2f}",     "💰", "#0F6E56"),
            ("Em produção",       str(stats["em_producao"]),             "🧶", "#854F0B"),
            ("A entregar",        str(stats["a_entregar"]),              "📦", "#185FA5"),
        ]
        for i, (title, value, icon, accent) in enumerate(data):
            sc = StatCard(self._stats_frame, title=title, value=value,
                          icon=icon, accent=accent)
            sc.grid(row=0, column=i, sticky="ew",
                    padx=(0 if i == 0 else 8, 0))
            self._stats_frame.columnconfigure(i, weight=1)

    def _atualizar_status(self, stats):
        for w in self._status_body.winfo_children():
            w.destroy()
        total = sum(r["qtd"] for r in stats["por_status"]) or 1
        for row in stats["por_status"]:
            st  = row["status"]
            qtd = row["qtd"]
            bg, fg = STATUS_COLORS.get(st, (CINZA_100, CINZA_700))
            fr = tk.Frame(self._status_body, bg=BRANCO_CARD)
            fr.pack(fill="x", pady=2)
            tk.Label(fr, text=f"  {st}", font=FONT_BODY, fg=fg,
                     bg=bg, anchor="w", width=16).pack(side="left")
            # barra de progresso proporcional
            pct = int((qtd / total) * 80)
            bar_frame = tk.Frame(fr, bg=CINZA_100, height=18)
            bar_frame.pack(side="left", fill="x", expand=True, padx=6)
            tk.Frame(bar_frame, bg=fg, height=18, width=max(pct, 4)).place(x=0,y=0)
            tk.Label(fr, text=str(qtd), font=(FONT_FAMILY, 9, "bold"),
                     fg=fg, bg=BRANCO_CARD, width=3).pack(side="right", padx=6)

    def _atualizar_recentes(self, stats):
        for r in self._rec_tree.get_children():
            self._rec_tree.delete(r)
        for rec in stats["recentes"]:
            self._rec_tree.insert("", "end",
                values=(rec["numero"], rec["cliente_nome"],
                        f"R$ {rec['total_valor']:.2f}",
                        rec["status"], rec.get("dt_entrega","—")))

    def _atualizar_rankings(self, stats):
        def _preencher(tree, rows):
            for r in tree.get_children(): tree.delete(r)
            tags = ["gold","silver","bronze"] + ["normal"]*100
            for i, row in enumerate(rows):
                medal = ("🥇","🥈","🥉")[i] if i < 3 else f"{i+1}º"
                tree.insert("", "end", values=(
                    medal, row.get("referencia",""),
                    row.get("descricao","") or "—",
                    row.get("total_pcs", 0),
                ), tags=(tags[i],))

        _preencher(self._mais_tree,  stats.get("ranking_mais", []))
        _preencher(self._menos_tree, stats.get("ranking_menos",[]))

    # ── Contador em tempo real ────────────────────────────────────────────────

    def _iniciar_contador(self):
        if self._counter_job:
            self.after_cancel(self._counter_job)
        self._tick()

    def _tick(self):
        from datetime import datetime
        agora = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        try:
            self._saudacao.config(
                text=self._saudacao.cget("text").split("  |")[0] + f"  |  {agora}")
        except Exception:
            pass
        self._counter_job = self.after(1000, self._tick)

    def _abrir_recente(self, _):
        sel = self._rec_tree.selection()
        if not sel: return
        num = self._rec_tree.item(sel[0])["values"][0]
        rows = self.ctrl.listar(busca=str(num))
        if rows: self.app.abrir_pedido(rows[0]["id"])