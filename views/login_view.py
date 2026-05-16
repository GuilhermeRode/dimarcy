import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import *
from views.widgets import Card, PrimaryBtn


class LoginView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=CREME)
        self.app = app
        self._build()

    def _build(self):
        wrap = tk.Frame(self, bg=CREME)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        card = Card(wrap, title="🔐  Login", accent_left=True)
        card.pack(fill="x")
        body = card.body()

        tk.Label(body, text="Acesse o sistema de pedidos", font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 8))

        self._usuario = tk.StringVar()
        self._senha = tk.StringVar()

        tk.Label(body, text="Usuário", font=FONT_LABEL, fg=CINZA_500, bg=CREME_CARD).pack(anchor="w")
        ttk.Entry(body, textvariable=self._usuario, width=32).pack(fill="x", pady=(0, 8))

        tk.Label(body, text="Senha", font=FONT_LABEL, fg=CINZA_500, bg=CREME_CARD).pack(anchor="w")
        e = ttk.Entry(body, textvariable=self._senha, show="*", width=32)
        e.pack(fill="x", pady=(0, 12))
        e.bind("<Return>", lambda _: self._entrar())

        PrimaryBtn(body, "Entrar", command=self._entrar).pack(anchor="e")

    def _entrar(self):
        if self._usuario.get().strip() == "admin" and self._senha.get() == "1234":
            self.app.login_sucesso()
            return
        messagebox.showerror("Login inválido", "Usuário ou senha incorretos.")