"""
app.py — Entry point do Sistema de Pedidos Tricot (MVC)

Estrutura:
  models/      — dados e acesso ao SQLite
  views/       — interfaces gráficas (tkinter)
  controllers/ — lógica de negócio entre views e models
  app.py — Entry point do Sistema de Pedidos Tricot (MVC)

Estrutura:
  models/      — dados e acesso ao SQLite
  views/       — interfaces gráficas (tkinter)
  controllers/ — lógica de negócio entre views e models
  app.py       — janela principal e roteamento de páginas
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Garante que os imports relativos funcionem independente de onde o script é chamado
sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db
from models import config_model
from controllers.pedido_controller import PedidoController, ConfigController
from views.theme import *
from views.dashboard_view import DashboardView
from views.lista_view import ListaView
from views.form_pedido_view import FormPedidoView
from views.clientes_view import ClientesView
from views.config_view import ConfigView
from views.login_view import LoginView
from views.producao_view import ProducaoView

NAV_ITEMS = [
    ("dashboard", "📊", "Dashboard"),
    ("lista",     "📋", "Pedidos"),
    ("producao",  "🏭", "Produção"),
    ("clientes",  "👥", "Clientes"),
    ("config",    "⚙️", "Configurações"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pedidos - Di Marcy")
        self.geometry("1280x780")
        self.minsize(1000, 640)
        self.configure(bg="#1E3A5F")

        # ── TTK style global ─────────────────────────────────────────────────
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=FONT_BODY, background=CREME)
        style.configure("TEntry", fieldbackground=CREME_CARD,
                        foreground=CINZA_900, bordercolor=CINZA_300,
                        padding=(6, 4))
        style.map("TEntry", bordercolor=[("focus", AZUL_CLARO)])
        style.configure("TCombobox", fieldbackground=CREME_CARD,
                        foreground=CINZA_900, bordercolor=CINZA_300,
                        padding=(6, 4))
        style.configure("TSpinbox", fieldbackground=CREME_CARD,
                        foreground=CINZA_900)
        style.configure("TSeparator", background=CREME_ESCURO)
        style.configure("TScrollbar", background=CINZA_300,
                        troughcolor=CINZA_100, bordercolor=CINZA_100,
                        arrowcolor=CINZA_500)

        # ── Controllers ──────────────────────────────────────────────────────
        self._pedido_ctrl = PedidoController(self)
        self._config_ctrl = ConfigController()

        # ── Layout ───────────────────────────────────────────────────────────
        self._sidebar = self._build_sidebar()

        self._content = tk.Frame(self, bg=CREME)
        self._content.pack(side="left", fill="both", expand=True)
        self.container = self._content  # compatibilidade código legado

        # ── Pages ────────────────────────────────────────────────────────────
        self._pages: dict[str, tk.Frame] = {}
        self._pages["login"] = LoginView(self._content, self)
        self._pages["dashboard"] = DashboardView(self._content, self._pedido_ctrl, self)
        self._pages["lista"] = ListaView(self._content, self._pedido_ctrl, self)
        self._pages["form"] = FormPedidoView(self._content, self._pedido_ctrl, self)
        self._pages["clientes"] = ClientesView(self._content, self._pedido_ctrl, self)
        self._pages["producao"] = ProducaoView(self._content, self)
        self._pages["config"] = ConfigView(self._content, self._config_ctrl, self)

    
        self._current = None
        self.show_page("login")

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> tk.Frame:
        sb = tk.Frame(self, bg=AZUL_ESCURO, width=SIDEBAR_W)
        sb.pack_propagate(False)

        brand = tk.Frame(sb, bg=AZUL_ESCURO)
        brand.pack(fill="x", pady=(24, 8))
        tk.Label(brand, text="🧶", font=(FONT_FAMILY, 28),
                 fg=DOURADO, bg=AZUL_ESCURO).pack()
        tk.Label(brand, text="Di Marcy Tricot",
                 font=(FONT_FAMILY, 13, "bold"),
                 fg=DOURADO, bg=AZUL_ESCURO).pack(pady=(2, 0))
        self._empresa_lbl = tk.Label(
            brand, text="Since 2001",
            font=(FONT_FAMILY, 8),
            fg="#BDBDBD", bg=AZUL_ESCURO, wraplength=180
        )
        self._empresa_lbl.pack(pady=(2, 16))

        tk.Frame(sb, bg=AZUL_ESCURO, height=1).pack(fill="x", padx=20)

        self._nav_btns: dict[str, tk.Button] = {}
        for item in NAV_ITEMS:
            if len(item) == 3:
                key, icon, label = item
            elif len(item) == 2:
                key, label = item
                icon = "•"
            else:
                continue

            btn = tk.Button(
                sb,
                text=f"  {icon}  {label}",
                anchor="w",
                font=(FONT_FAMILY, 10),
                bg=AZUL_ESCURO, fg="#DCEEFF",
                activebackground="#2E6DA4",
                activeforeground=DOURADO,
                relief="flat", cursor="hand2",
                pady=11, padx=16,
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x")
            self._nav_btns[key] = btn

        tk.Frame(sb, bg=AZUL_ESCURO).pack(fill="both", expand=True)
        tk.Frame(sb, bg="#2E6DA4", height=1).pack(fill="x", padx=20)
        tk.Label(sb, text="v2.0 · MVC Edition",
                 font=(FONT_FAMILY, 8), fg="#5A4A3A",
                 bg=AZUL_ESCURO).pack(pady=(6, 16))

        return sb

    def _set_nav_active(self, key: str):
        map_key = key if key not in ("form", "login") else None
        for k, btn in self._nav_btns.items():
            if k == map_key:
                btn.config(bg="#2424B1", fg=DOURADO)
            else:
                btn.config(bg=AZUL_ESCURO, fg="#B8A898")

    # ── Page routing ──────────────────────────────────────────────────────────

    def show_page(self, key: str):
        # proteção para evitar KeyError: 'producao' (ou qualquer página ausente)
        if key not in self._pages:
            self.show_page("dashboard")
            return

        if self._current:
            self._current.pack_forget()

        page = self._pages[key]
        page.pack(fill="both", expand=True)
        self._current = page
        self._set_nav_active(key)

        if hasattr(page, "refresh"):
            page.refresh()

    def login_sucesso(self):
        if not self._sidebar.winfo_ismapped():
            self._sidebar.pack(side="left", fill="y", before=self._content)

        self.show_page("dashboard")

    def show_lista(self):
        self.show_page("lista")

    def novo_pedido(self, cliente: dict | None = None):
        self._pages["form"].novo()
        if cliente:
            self._pages["form"].prefill_cliente(cliente)
        self.show_page("form")
        self._set_nav_active("lista")

    def nova_producao(self):
        self.show_page("producao")

    def abrir_pedido(self, pedido_id: int):
        self._pages["form"].carregar(pedido_id)
        self.show_page("form")
        self._set_nav_active("lista")

    def refresh_lista(self):
        if hasattr(self._pages["lista"], "refresh"):
            self._pages["lista"].refresh()
        self._empresa_lbl.config(text=config_model.get("empresa_nome"))

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
