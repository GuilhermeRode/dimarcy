"""
views/clientes_view.py
Histórico de clientes extraído dos pedidos.
"""
import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import Card, build_treeview


class ClientesView(tk.Frame):
    def __init__(self, parent, controller, app):
        super().__init__(parent, bg=CREME)
        self.ctrl = controller
        self.app = app
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=CREME)
        hdr.pack(fill="x", padx=PAD_PAGE, pady=(PAD_PAGE, 0))
        tk.Label(hdr, text="Clientes", font=FONT_TITLE,
                 fg=CINZA_900, bg=CREME).pack(side="left")
        tk.Label(hdr, text="Histórico de clientes dos pedidos",
                 font=FONT_SMALL, fg=CINZA_500, bg=CREME).pack(
                 side="left", padx=(12,0))
        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=PAD_PAGE, pady=(10, 14))

        cols = [
            ("cliente_nome",  "Nome / razão social", 220),
            ("cliente_doc",   "CPF / CNPJ",          130),
            ("cliente_tel",   "Telefone",             120),
            ("cliente_email", "E-mail",               190),
            ("cliente_cidade","Cidade",               130),
            ("total_pedidos", "Pedidos",               70),
            ("total_gasto",   "Total gasto R$",       120),
        ]
        frame = tk.Frame(self, bg=CREME)
        frame.pack(fill="both", expand=True, padx=PAD_PAGE)
        self._tree = build_treeview(frame, cols, height=24)
        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

    def refresh(self):
        for r in self._tree.get_children():
            self._tree.delete(r)
        for c in self.ctrl.clientes():
            self._tree.insert("", "end", values=(
                c.get("cliente_nome",""),
                c.get("cliente_doc",""),
                c.get("cliente_tel",""),
                c.get("cliente_email",""),
                c.get("cliente_cidade",""),
                c.get("total_pedidos", 0),
                f"R$ {c.get('total_gasto',0):.2f}",
            ))
