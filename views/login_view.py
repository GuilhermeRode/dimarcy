"""
views/login_view.py — Tela de login
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import *
from views.widgets import Card, PrimaryBtn
from models.database import autenticar


class LoginView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=AZUL_ESCURO)
        self.app = app
        self._build()

    def _build(self):
        # Fundo gradiente simulado
        tk.Frame(self, bg=AZUL_ESCURO).pack(fill="both", expand=True)

        wrap = tk.Frame(self, bg=AZUL_ESCURO)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / marca
        tk.Label(wrap, text="🧶", font=(FONT_FAMILY, 48),
                 fg=DOURADO, bg=AZUL_ESCURO).pack(pady=(0, 4))
        tk.Label(wrap, text="Di Marcy Tricot",
                 font=(FONT_FAMILY, 20, "bold"),
                 fg=DOURADO, bg=AZUL_ESCURO).pack()
        tk.Label(wrap, text="Sistema de Pedidos",
                 font=(FONT_FAMILY, 10),
                 fg="#7AABCF", bg=AZUL_ESCURO).pack(pady=(2, 24))

        # Card de login
        card = tk.Frame(wrap, bg=CREME_CARD,
                        highlightbackground=AZUL_BORDER,
                        highlightthickness=1)
        card.pack(fill="x", ipadx=8, ipady=8)

        inner = tk.Frame(card, bg=CREME_CARD)
        inner.pack(padx=32, pady=24, fill="x")

        tk.Label(inner, text="Acesse sua conta", font=(FONT_FAMILY, 13, "bold"),
                 fg=AZUL, bg=CREME_CARD).pack(anchor="w", pady=(0, 16))

        # Usuário
        tk.Label(inner, text="Usuário", font=FONT_LABEL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w")
        self._usuario = tk.StringVar()
        u_entry = ttk.Entry(inner, textvariable=self._usuario,
                            font=FONT_BODY, width=30)
        u_entry.pack(fill="x", pady=(2, 12))

        # Senha
        tk.Label(inner, text="Senha", font=FONT_LABEL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w")
        self._senha = tk.StringVar()
        s_entry = ttk.Entry(inner, textvariable=self._senha,
                            show="*", font=FONT_BODY, width=30)
        s_entry.pack(fill="x", pady=(2, 20))
        s_entry.bind("<Return>", lambda _: self._entrar())

        # Botão
        btn = tk.Button(inner, text="  Entrar  →",
                        command=self._entrar,
                        font=(FONT_FAMILY, 11, "bold"),
                        bg=AZUL, fg="white",
                        activebackground=AZUL_MED, activeforeground="white",
                        relief="flat", cursor="hand2",
                        padx=24, pady=10)
        btn.pack(fill="x")

        self._erro_lbl = tk.Label(inner, text="", font=FONT_SMALL,
                                   fg="#B42318", bg=CREME_CARD)
        self._erro_lbl.pack(pady=(8, 0))

        # Focus inicial
        u_entry.focus_set()

    def _entrar(self):
        usuario = self._usuario.get().strip()
        senha   = self._senha.get()

        if not usuario or not senha:
            self._erro_lbl.config(text="Preencha usuário e senha.")
            return

        # Login via banco (ou legado admin/1234)
        user = autenticar(usuario, senha)
        ok = user is not None or (usuario == "admin" and senha == "1234")

        if ok:
            self._erro_lbl.config(text="")
            self.app.login_sucesso()
        else:
            self._erro_lbl.config(text="Usuário ou senha incorretos.")
            self._senha.set("")