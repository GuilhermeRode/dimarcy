"""
views/config_view.py
Configurações da empresa.
"""
import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import Card, PrimaryBtn


class ConfigView(tk.Frame):
    def __init__(self, parent, controller, app):
        super().__init__(parent, bg=CREME)
        self.ctrl = controller
        self.app = app
        self._vars: dict[str, tk.StringVar] = {}
        self._build()

    def _build(self):
        tk.Label(self, text="Configurações", font=FONT_TITLE,
                 fg=CINZA_900, bg=CREME).pack(
                 anchor="w", padx=PAD_PAGE, pady=(PAD_PAGE, 0))
        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=PAD_PAGE, pady=(10, 20))

        card = Card(self, title="🏭  Dados da empresa", accent_left=True)
        card.pack(fill="x", padx=PAD_PAGE)
        body = card.body()

        fields = [
            ("empresa_nome",  "Nome / razão social da empresa"),
            ("empresa_cnpj",  "CNPJ"),
            ("empresa_tel",   "Telefone"),
            ("empresa_email", "E-mail"),
            ("empresa_end",   "Endereço completo"),
        ]
        for key, label in fields:
            self._vars[key] = tk.StringVar()
            row = tk.Frame(body, bg=CREME_CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=FONT_LABEL,
                     fg=CINZA_500, bg=CREME_CARD, width=30,
                     anchor="w").pack(side="left")
            ttk.Entry(row, textvariable=self._vars[key],
                      font=FONT_BODY, width=40).pack(side="left", fill="x", expand=True)

        PrimaryBtn(self, "💾  Salvar configurações",
                   command=self._salvar).pack(anchor="w", padx=PAD_PAGE, pady=16)

        # Info box
        info = tk.Frame(self, bg="#E6F1FB",
                        highlightbackground="#B5D4F4",
                        highlightthickness=1)
        info.pack(fill="x", padx=PAD_PAGE)
        tk.Label(info, text="ℹ️  Os dados da empresa aparecem no cabeçalho e rodapé dos PDFs gerados.",
                 font=FONT_SMALL, fg="#185FA5", bg="#E6F1FB",
                 padx=14, pady=10).pack(anchor="w")

    def refresh(self):
        cfg = self.ctrl.get_all()
        for k, var in self._vars.items():
            var.set(cfg.get(k, ""))

    def _salvar(self):
        dados = {k: v.get() for k, v in self._vars.items()}
        self.ctrl.salvar(dados)
