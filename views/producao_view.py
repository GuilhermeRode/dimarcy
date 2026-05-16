"""
views/producao_view.py
Gerenciamento de ordens de produção (sem banco — dados em memória durante a sessão).
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from views.theme import *
from views.widgets import (Card, ScrollFrame, PrimaryBtn, SecondaryBtn,
                            DangerBtn, build_treeview)

TAMANHOS   = ["PP", "P", "M", "G", "GG", "XGG", "Único"]
_SZ_KEYS   = ["pp",  "p", "m", "g", "gg", "xgg", "unico"]
_PROD_STORE: list[dict] = []   # memória da sessão
_PROD_SEQ   = [0]              # contador


def _next_num() -> str:
    _PROD_SEQ[0] += 1
    return f"PROD-{_PROD_SEQ[0]:04d}"


class ProducaoView(tk.Frame):
    """Lista de ordens de produção + botão Nova Produção."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=CREME)
        self.app = app
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        hdr = tk.Frame(self, bg=CREME)
        hdr.pack(fill="x", padx=PAD_PAGE, pady=(PAD_PAGE, 0))
        tk.Label(hdr, text="Produção", font=FONT_TITLE,
                 fg=CINZA_900, bg=CREME).pack(side="left")
        tk.Label(hdr, text="Ordens de produção da sessão",
                 font=FONT_SMALL, fg=CINZA_500, bg=CREME).pack(
                 side="left", padx=(12, 0))
        PrimaryBtn(hdr, "＋  Nova produção",
                   command=self._nova_producao).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=PAD_PAGE, pady=(10, 0))

        # Info banner
        info = tk.Frame(self, bg="#FFF9E6",
                        highlightbackground="#F0C040", highlightthickness=1)
        info.pack(fill="x", padx=PAD_PAGE, pady=(10, 0))
        tk.Label(info,
                 text="ℹ️  As ordens de produção ficam na memória durante a sessão. "
                      "Gere o PDF para salvar permanentemente.",
                 font=FONT_SMALL, fg="#7A5A00", bg="#FFF9E6",
                 padx=14, pady=8).pack(anchor="w")

        # Treeview
        cols = [
            ("numero",    "Número",    100),
            ("data",      "Data",       90),
            ("total_refs","Refs",        50),
            ("total_pcs", "Peças",       70),
            ("obs",       "Obs.",       300),
        ]
        frame = tk.Frame(self, bg=CREME)
        frame.pack(fill="both", expand=True, padx=PAD_PAGE, pady=(10, 0))
        self._tree = build_treeview(frame, cols, height=18)
        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self._tree.bind("<Double-1>", lambda _: self._abrir())

        # Toolbar
        bar = tk.Frame(self, bg=CREME,
                       highlightbackground=CINZA_300, highlightthickness=1)
        bar.pack(fill="x", padx=PAD_PAGE, pady=(0, PAD_PAGE))
        SecondaryBtn(bar, "✎  Abrir / Editar", command=self._abrir).pack(
            side="left", padx=(8, 4), pady=8)
        SecondaryBtn(bar, "🖨  Gerar PDF", command=self._pdf).pack(
            side="left", padx=4, pady=8)
        DangerBtn(bar, "✕  Excluir", command=self._excluir).pack(
            side="left", padx=4, pady=8)

    def refresh(self):
        for r in self._tree.get_children():
            self._tree.delete(r)
        for p in _PROD_STORE:
            total_pcs = sum(
                sum(it.get(k, 0) for k in _SZ_KEYS)
                for it in p.get("itens", [])
            )
            self._tree.insert("", "end", iid=p["numero"], values=(
                p["numero"], p["data"],
                len(p.get("itens", [])),
                total_pcs,
                p.get("obs", "")[:60],
            ))

    def _nova_producao(self):
        ProducaoFormDialog(self, on_save=self._on_salvo)

    def _sel(self) -> dict | None:
        sel = self._tree.selection()
        if not sel:
            return None
        num = sel[0]
        return next((p for p in _PROD_STORE if p["numero"] == num), None)

    def _abrir(self):
        p = self._sel()
        if p:
            ProducaoFormDialog(self, producao=p, on_save=self._on_salvo)

    def _excluir(self):
        p = self._sel()
        if p and messagebox.askyesno("Confirmar",
                                      f"Excluir {p['numero']}? Esta ação é irreversível."):
            _PROD_STORE.remove(p)
            self.refresh()

    def _pdf(self):
        p = self._sel()
        if not p:
            return
        _exportar_pdf(p)

    def _on_salvo(self):
        self.refresh()


# ── Formulário de Produção ────────────────────────────────────────────────────

class ProducaoFormDialog(tk.Toplevel):
    """Janela para criar/editar uma ordem de produção."""

    def __init__(self, parent, producao: dict = None, on_save=None):
        super().__init__(parent)
        self._producao = producao
        self._on_save  = on_save
        self._item_rows: list[_ProdItemRow] = []

        titulo = "Editar produção" if producao else "Nova produção"
        self.title(titulo)
        self.geometry("900x680")
        self.minsize(800, 560)
        self.configure(bg=CREME)
        self.grab_set()
        self._build()
        self._center()

        if producao:
            self._load(producao)
        else:
            self._num_var.set(_next_num())
            self._data_var.set(date.today().strftime("%d/%m/%Y"))
            self._add_item()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build(self):
        # Top bar
        bar = tk.Frame(self, bg=CREME_CARD,
                       highlightbackground=CREME_ESCURO,
                       highlightthickness=1)
        bar.pack(fill="x")

        left = tk.Frame(bar, bg=CREME_CARD)
        left.pack(side="left", padx=16, pady=12)
        tk.Label(left, text="🏭  Ordem de Produção",
                 font=FONT_HEADING, fg=CINZA_900, bg=CREME_CARD).pack(side="left")
        self._num_lbl_bar = tk.Label(left, text="", font=FONT_BODY,
                                      fg=CINZA_500, bg=CREME_CARD)
        self._num_lbl_bar.pack(side="left", padx=(10, 0))

        right = tk.Frame(bar, bg=CREME_CARD)
        right.pack(side="right", padx=16, pady=10)
        tk.Button(right, text="Cancelar", command=self.destroy,
                  font=FONT_BODY, bg=CREME_CARD, fg=CINZA_700,
                  relief="flat", cursor="hand2",
                  highlightbackground=CINZA_300, highlightthickness=1,
                  padx=12, pady=5).pack(side="left", padx=(0, 8))
        tk.Button(right, text="🖨  PDF", command=self._pdf,
                  font=FONT_BODY, bg=CREME_CARD, fg=CINZA_700,
                  relief="flat", cursor="hand2",
                  highlightbackground=CINZA_300, highlightthickness=1,
                  padx=12, pady=5).pack(side="left", padx=(0, 8))
        tk.Button(right, text="💾  Salvar", command=self._salvar,
                  font=FONT_BODY, bg=AZUL, fg="white",
                  activebackground=AZUL_MED, activeforeground="white",
                  relief="flat", cursor="hand2",
                  padx=16, pady=5).pack(side="left")

        # Scroll
        sf = ScrollFrame(self, bg=CREME)
        sf.pack(fill="both", expand=True)
        body = sf.inner
        body.columnconfigure(0, weight=1)

        # Cabeçalho da ordem
        head_card = Card(body, title="📋  Dados da ordem", accent_left=True)
        head_card.pack(fill="x", padx=PAD_PAGE, pady=(14, 0))
        hb = head_card.body()

        hrow = tk.Frame(hb, bg=CREME_CARD)
        hrow.pack(fill="x")
        hrow.columnconfigure(0, weight=1)
        hrow.columnconfigure(1, weight=1)
        hrow.columnconfigure(2, weight=2)

        self._num_var  = tk.StringVar()
        self._data_var = tk.StringVar()
        self._obs_var  = tk.StringVar()

        for i, (lbl, var) in enumerate([
            ("Número da ordem", self._num_var),
            ("Data (dd/mm/aaaa)", self._data_var),
            ("Observações gerais", self._obs_var),
        ]):
            f = tk.Frame(hrow, bg=CREME_CARD)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, 8) if i < 2 else 0)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 2))
            ttk.Entry(f, textvariable=var, font=FONT_BODY).pack(fill="x")

        # Itens
        itens_card = Card(body, title="🧶  Itens de produção", accent_left=True)
        itens_card.pack(fill="x", padx=PAD_PAGE, pady=(14, 0))

        tot_bar = tk.Frame(itens_card, bg=CREME_CARD)
        tot_bar.pack(fill="x", padx=PAD_CARD, pady=(0, 6))
        self._tot_lbl = tk.Label(tot_bar, text="0 peças",
                                  font=FONT_SUBHEAD, fg=AZUL, bg=CREME_CARD)
        self._tot_lbl.pack(side="left")
        tk.Button(tot_bar, text="＋  Adicionar referência",
                  command=self._add_item,
                  font=FONT_SMALL, bg=CREME_CARD, fg=CINZA_700,
                  relief="flat", cursor="hand2",
                  highlightbackground=CINZA_300, highlightthickness=1,
                  padx=12, pady=4).pack(side="right")

        ttk.Separator(itens_card, orient="horizontal").pack(
            fill="x", padx=PAD_CARD)

        self._itens_frame = tk.Frame(itens_card, bg=CREME_CARD)
        self._itens_frame.pack(fill="x", padx=PAD_CARD, pady=(6, PAD_CARD))

        # Espaço final
        tk.Frame(body, bg=CREME, height=30).pack()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width() or 900
        h = self.winfo_height() or 680
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _add_item(self, item: dict = None):
        idx = len(self._item_rows) + 1
        row = _ProdItemRow(self._itens_frame, idx, item, self._remove_item, self._recalc)
        row.pack(fill="x", pady=(0, 8))
        self._item_rows.append(row)
        self._recalc()

    def _remove_item(self, row):
        self._item_rows.remove(row)
        row.destroy()
        self._recalc()

    def _recalc(self):
        total = sum(r.total_pcs() for r in self._item_rows)
        self._tot_lbl.config(text=f"{total} peças")

    def _load(self, p: dict):
        self._num_var.set(p.get("numero", ""))
        self._data_var.set(p.get("data", ""))
        self._obs_var.set(p.get("obs", ""))
        self._num_lbl_bar.config(text=p.get("numero", ""))
        for it in p.get("itens", []):
            self._add_item(it)

    def _collect(self) -> dict:
        return {
            "numero": self._num_var.get().strip() or _next_num(),
            "data":   self._data_var.get().strip(),
            "obs":    self._obs_var.get().strip(),
            "itens":  [r.to_dict() for r in self._item_rows],
        }

    def _salvar(self):
        p = self._collect()
        if not p["itens"]:
            messagebox.showerror("Sem itens",
                                  "Adicione pelo menos um item de produção.",
                                  parent=self)
            return
        # Atualiza ou insere
        for i, existing in enumerate(_PROD_STORE):
            if existing["numero"] == p["numero"]:
                _PROD_STORE[i] = p
                break
        else:
            _PROD_STORE.append(p)

        if self._on_save:
            self._on_save()
        messagebox.showinfo("Salvo",
                            f"Ordem {p['numero']} salva na sessão.", parent=self)
        self.destroy()

    def _pdf(self):
        p = self._collect()
        if not p["itens"]:
            messagebox.showerror("Sem itens", "Adicione itens antes de gerar o PDF.",
                                 parent=self)
            return
        _exportar_pdf(p, parent=self)


def _exportar_pdf(p: dict, parent=None):
    path = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
        initialfile=f"Producao_{p['numero']}.pdf",
        parent=parent
    )
    if not path:
        return
    try:
        from controllers.pdf_controller import gerar_producao
        gerar_producao(p, path)
        if messagebox.askyesno("PDF gerado!", f"Salvo em:\n{path}\n\nAbrir agora?",
                               parent=parent):
            import os, subprocess, sys
            if sys.platform == "win32": os.startfile(path)
            elif sys.platform == "darwin": subprocess.call(["open", path])
            else: subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Erro ao gerar PDF", str(e), parent=parent)


# ── Item Row de Produção ──────────────────────────────────────────────────────

class _ProdItemRow(tk.Frame):
    def __init__(self, parent, idx, item: dict, on_remove, on_change):
        super().__init__(parent, bg=CINZA_100,
                         highlightbackground=CREME_ESCURO,
                         highlightthickness=1)
        self._on_remove = on_remove
        self._on_change = on_change
        self._vs: dict[str, tk.StringVar] = {}
        self._sz: dict[str, tk.StringVar] = {}
        self._build(idx)
        if item:
            self._load(item)

    def _build(self, idx: int):
        # Header
        hdr = tk.Frame(self, bg="#237A4B")
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  Item {idx}",
                 font=(FONT_FAMILY, 9, "bold"), fg="white",
                 bg="#237A4B").pack(side="left", pady=5)
        tk.Button(hdr, text="✕ remover", font=FONT_LABEL,
                  fg="#A8F0C0", bg="#237A4B", relief="flat", cursor="hand2",
                  command=lambda: self._on_remove(self)).pack(
                  side="right", padx=8, pady=4)

        body = tk.Frame(self, bg=CINZA_100)
        body.pack(fill="x", padx=10, pady=8)

        # Linha 1: Ref, NPK, Cor
        r1 = tk.Frame(body, bg=CINZA_100)
        r1.pack(fill="x", pady=(0, 6))
        for i, (lbl, key, weight) in enumerate([
            ("Referência / código", "referencia", 2),
            ("NPK",                 "npk",        1),
            ("Cor",                 "cor",        2),
        ]):
            self._vs[key] = tk.StringVar()
            f = tk.Frame(r1, bg=CINZA_100)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, 8) if i < 2 else 0)
            r1.columnconfigure(i, weight=weight)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CINZA_100).pack(anchor="w", pady=(0, 2))
            e = ttk.Entry(f, textvariable=self._vs[key], font=FONT_BODY)
            e.pack(fill="x")
            e.bind("<KeyRelease>", lambda _: self._on_change())

        # Linha 2: tamanhos
        r2 = tk.Frame(body, bg=CINZA_100)
        r2.pack(fill="x")
        tk.Label(r2, text="Qtd. por tamanho →",
                 font=FONT_LABEL, fg=CINZA_500, bg=CINZA_100).grid(
                 row=0, column=0, sticky="w", padx=(0, 12))

        self._tot_lbl = tk.Label(r2, text="0 pçs",
                                  font=(FONT_FAMILY, 9, "bold"),
                                  fg="#237A4B", bg=CINZA_100)

        for i, (sz, key) in enumerate(zip(TAMANHOS, _SZ_KEYS)):
            self._sz[key] = tk.StringVar(value="0")
            f = tk.Frame(r2, bg=CINZA_100)
            f.grid(row=0, column=i+1, padx=3)
            tk.Label(f, text=sz, font=FONT_LABEL,
                     fg=CINZA_500, bg=CINZA_100).pack()
            sp = ttk.Spinbox(f, textvariable=self._sz[key],
                             from_=0, to=99999, width=6, font=FONT_BODY,
                             command=self._on_change)
            sp.pack()
            sp.bind("<KeyRelease>", lambda _: self._on_change())

        self._tot_lbl.grid(row=0, column=len(TAMANHOS)+1, padx=(12, 0))

    def _load(self, item: dict):
        self._vs["referencia"].set(item.get("referencia", ""))
        self._vs["npk"].set(item.get("npk", ""))
        self._vs["cor"].set(item.get("cor", ""))
        for key in _SZ_KEYS:
            self._sz[key].set(str(item.get(key, 0)))

    def total_pcs(self) -> int:
        total = sum(int(self._sz[k].get() or 0) for k in _SZ_KEYS)
        self._tot_lbl.config(text=f"{total} pçs")
        return total

    def to_dict(self) -> dict:
        d = {k: self._vs[k].get() for k in ("referencia", "npk", "cor")}
        for key in _SZ_KEYS:
            try:
                d[key] = int(self._sz[key].get() or 0)
            except ValueError:
                d[key] = 0
        return d