"""
views/login_view.py — Tela de login
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import *
from models.database import autenticar


class LoginView(tk.Toplevel):
    """Janela de login modal — bloqueia a app principal até autenticar."""

    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.title("Di Marcy — Acesso")
        self.resizable(False, False)
        self.grab_set()                    # modal
        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self._usuario_logado = None
        self._build()
        self._centralizar(master)

    def _centralizar(self, master):
        self.update_idletasks()
        mw, mh = master.winfo_width(), master.winfo_height()
        mx, my = master.winfo_x(), master.winfo_y()
        w, h   = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{mx+(mw-w)//2}+{my+(mh-h)//2}")

    def _build(self):
        self.configure(bg=AZUL_ESCURO)

        # ── Painel central ────────────────────────────────────────────────
        card = tk.Frame(self, bg=BRANCO_CARD,
                        highlightbackground=AZUL_BORDER, highlightthickness=1)
        card.pack(padx=0, pady=0)

        # Cabeçalho azul
        hdr = tk.Frame(card, bg=AZUL_ESCURO)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🧶", font=(FONT_FAMILY, 32),
                 fg=DOURADO, bg=AZUL_ESCURO).pack(pady=(28, 4))
        tk.Label(hdr, text="Di Marcy Tricot",
                 font=(FONT_FAMILY, 15, "bold"),
                 fg=DOURADO, bg=AZUL_ESCURO).pack()
        tk.Label(hdr, text="Faça login para continuar",
                 font=(FONT_FAMILY, 9),
                 fg="#8BBDE0", bg=AZUL_ESCURO).pack(pady=(2, 24))

        # Campos
        body = tk.Frame(card, bg=BRANCO_CARD)
        body.pack(padx=40, pady=28)

        # Usuário
        tk.Label(body, text="Usuário", font=FONT_LABEL,
                 fg=CINZA_500, bg=BRANCO_CARD).pack(anchor="w")
        self._u_var = tk.StringVar()
        u_entry = ttk.Entry(body, textvariable=self._u_var,
                            font=FONT_BODY, width=28)
        u_entry.pack(fill="x", pady=(2, 12))
        u_entry.focus_set()

        # Senha
        tk.Label(body, text="Senha", font=FONT_LABEL,
                 fg=CINZA_500, bg=BRANCO_CARD).pack(anchor="w")
        self._p_var = tk.StringVar()
        p_entry = ttk.Entry(body, textvariable=self._p_var,
                            font=FONT_BODY, width=28, show="●")
        p_entry.pack(fill="x", pady=(2, 4))
        p_entry.bind("<Return>", lambda _: self._login())

        # Erro
        self._err_lbl = tk.Label(body, text="", font=FONT_SMALL,
                                  fg="#B42318", bg=BRANCO_CARD)
        self._err_lbl.pack(pady=(0, 10))

        # Botão
        btn = tk.Button(body, text="Entrar", font=(FONT_FAMILY, 11, "bold"),
                        bg=AZUL, fg="white",
                        activebackground=AZUL_MED, activeforeground="white",
                        relief="flat", cursor="hand2",
                        padx=0, pady=10, width=24,
                        command=self._login)
        btn.pack(fill="x")

        # Dica
        tk.Label(body, text="Padrão: admin / admin123",
                 font=(FONT_FAMILY, 7), fg=CINZA_300,
                 bg=BRANCO_CARD).pack(pady=(12, 0))

    def _login(self):
        usuario = self._u_var.get().strip()
        senha   = self._p_var.get()
        if not usuario or not senha:
            self._err_lbl.config(text="Preencha usuário e senha.")
            return
        user = autenticar(usuario, senha)
        if user:
            self._usuario_logado = user
            self.grab_release()
            self.destroy()
            self.on_success(user)
        else:
            self._err_lbl.config(text="Usuário ou senha incorretos.")
            self._p_var.set("")

    def _fechar(self):
        # Fechar o login fecha a aplicação inteira
        self.master.destroy()