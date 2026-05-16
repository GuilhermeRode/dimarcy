"""
views/clientes_view.py
Histórico + cadastro de clientes.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import *
from views.widgets import Card, PrimaryBtn, SecondaryBtn, DangerBtn, build_treeview
from models.cliente_model import Cliente


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
        tk.Label(hdr, text="Cadastro e histórico",
                 font=FONT_SMALL, fg=CINZA_500, bg=CREME).pack(
                 side="left", padx=(12, 0))

        PrimaryBtn(hdr, "＋  Novo cliente",
                   command=self._novo_cliente).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(
            fill="x", padx=PAD_PAGE, pady=(10, 0))

        # Busca
        filt = tk.Frame(self, bg=CREME)
        filt.pack(fill="x", padx=PAD_PAGE, pady=(10, 0))
        tk.Label(filt, text="Buscar:", font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME).pack(side="left", padx=(0, 6))
        self._busca = tk.StringVar()
        self._busca.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(filt, textvariable=self._busca, width=32,
                  font=FONT_BODY).pack(side="left")
        self._count_lbl = tk.Label(filt, text="", font=FONT_SMALL,
                                    fg=CINZA_500, bg=CREME)
        self._count_lbl.pack(side="right")

        # Treeview
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
        frame.pack(fill="both", expand=True, padx=PAD_PAGE, pady=(10, 0))
        self._tree = build_treeview(frame, cols, height=20)
        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self._tree.bind("<Double-1>", lambda _: self._editar_cliente())

        # Toolbar
        bar = tk.Frame(self, bg=CREME,
                       highlightbackground=CINZA_300, highlightthickness=1)
        bar.pack(fill="x", padx=PAD_PAGE, pady=(0, PAD_PAGE))
        SecondaryBtn(bar, "✎  Editar", command=self._editar_cliente).pack(
            side="left", padx=(8, 4), pady=8)
        SecondaryBtn(bar, "📋  Novo pedido para este cliente",
                     command=self._novo_pedido_cliente).pack(
            side="left", padx=4, pady=8)
        DangerBtn(bar, "✕  Excluir", command=self._excluir_cliente).pack(
            side="left", padx=4, pady=8)

    def refresh(self):
        for r in self._tree.get_children():
            self._tree.delete(r)
        clientes = self.ctrl.clientes()
        busca = self._busca.get().lower()
        if busca:
            clientes = [c for c in clientes
                        if busca in c.get("cliente_nome","").lower()
                        or busca in c.get("cliente_cidade","").lower()
                        or busca in c.get("cliente_doc","").lower()]
        for c in clientes:
            self._tree.insert("", "end",
                iid=str(c.get("id", c.get("cliente_nome",""))),
                values=(
                    c.get("cliente_nome", ""),
                    c.get("cliente_doc", ""),
                    c.get("cliente_tel", ""),
                    c.get("cliente_email", ""),
                    c.get("cliente_cidade", ""),
                    c.get("total_pedidos", 0),
                    f"R$ {c.get('total_gasto', 0.0):.2f}",
                ))
        self._count_lbl.config(text=f"{len(clientes)} cliente(s)")

    def _sel_cliente_dict(self) -> dict | None:
        sel = self._tree.selection()
        if not sel:
            return None
        vals = self._tree.item(sel[0])["values"]
        return {
            "cliente_nome":   vals[0],
            "cliente_doc":    vals[1],
            "cliente_tel":    vals[2],
            "cliente_email":  vals[3],
            "cliente_cidade": vals[4],
        }

    def _novo_cliente(self):
        ClienteFormDialog(self, on_save=self._on_cliente_salvo)

    def _editar_cliente(self):
        d = self._sel_cliente_dict()
        if not d:
            return
        # Tenta carregar por nome do banco
        from models import cliente_model
        rows = cliente_model.listar(d["cliente_nome"])
        c = None
        for row in rows:
            if row["nome"] == d["cliente_nome"]:
                c = cliente_model.buscar(row["id"])
                break
        if c is None:
            # Cria objeto a partir dos dados da treeview
            c = Cliente(
                nome=d["cliente_nome"],
                doc=d["cliente_doc"],
                tel=d["cliente_tel"],
                email=d["cliente_email"],
                cidade=d["cliente_cidade"],
            )
        ClienteFormDialog(self, cliente=c, on_save=self._on_cliente_salvo)

    def _excluir_cliente(self):
        sel = self._tree.selection()
        if not sel:
            return
        iid = sel[0]
        try:
            cid = int(iid)
            from models import cliente_model
            if messagebox.askyesno("Confirmar exclusão",
                                   "Deseja excluir este cliente do cadastro?\n"
                                   "O histórico de pedidos não será afetado."):
                cliente_model.excluir(cid)
                self.refresh()
        except ValueError:
            messagebox.showinfo("Aviso",
                "Este cliente veio apenas de pedidos e não está no cadastro.\n"
                "Para removê-lo, exclua seus pedidos.")

    def _on_cliente_salvo(self):
        self.refresh()
        messagebox.showinfo("Salvo", "Cliente salvo com sucesso!")

    def _novo_pedido_cliente(self):
        d = self._sel_cliente_dict()
        if d:
            self.app.novo_pedido(d)
        else:
            self.app.novo_pedido()


# ── Diálogo de formulário de cliente ─────────────────────────────────────────

class ClienteFormDialog(tk.Toplevel):
    """Janela modal para criar ou editar um cliente."""

    def __init__(self, parent, cliente: Cliente = None, on_save=None):
        super().__init__(parent)
        self._cliente = cliente
        self._on_save = on_save
        self._vars: dict[str, tk.StringVar] = {}

        self.title("Novo cliente" if not cliente else "Editar cliente")
        self.resizable(False, False)
        self.configure(bg=CREME)
        self.grab_set()  # modal

        self._build()
        self._center()

        if cliente:
            self._load(cliente)

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=AZUL)
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text="👤  " + ("Editar cliente" if self._cliente else "Novo cliente"),
                 font=(FONT_FAMILY, 12, "bold"),
                 fg=DOURADO, bg=AZUL).pack(side="left", padx=16, pady=12)

        # Corpo
        body = tk.Frame(self, bg=CREME)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        fields = [
            ("nome",     "Nome / Razão Social *",  True),
            ("doc",      "CPF / CNPJ",             False),
            ("tel",      "Telefone",               False),
            ("email",    "E-mail",                 False),
            ("endereco", "Endereço completo",       False),
            ("cidade",   "Cidade / UF",            False),
        ]

        for key, lbl_text, required in fields:
            self._vars[key] = tk.StringVar()
            f = tk.Frame(body, bg=CREME)
            f.pack(fill="x", pady=5)
            color = AZUL if required else CINZA_500
            tk.Label(f, text=lbl_text, font=FONT_LABEL,
                     fg=color, bg=CREME).pack(anchor="w", pady=(0, 2))
            e = ttk.Entry(f, textvariable=self._vars[key], font=FONT_BODY, width=44)
            e.pack(fill="x")
            if key == "nome":
                e.focus_set()

        # Botões
        bar = tk.Frame(self, bg=CREME)
        bar.pack(fill="x", padx=24, pady=(0, 20))

        tk.Button(bar, text="Cancelar", command=self.destroy,
                  font=FONT_BODY, bg=CREME_CARD, fg=CINZA_700,
                  relief="flat", cursor="hand2",
                  highlightbackground=CINZA_300, highlightthickness=1,
                  padx=14, pady=6).pack(side="right", padx=(8, 0))

        tk.Button(bar, text="💾  Salvar cliente", command=self._salvar,
                  font=FONT_BODY, bg=AZUL, fg="white",
                  activebackground=AZUL_MED, activeforeground="white",
                  relief="flat", cursor="hand2",
                  padx=16, pady=6).pack(side="right")

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    def _load(self, c: Cliente):
        self._vars["nome"].set(c.nome or "")
        self._vars["doc"].set(c.doc or "")
        self._vars["tel"].set(c.tel or "")
        self._vars["email"].set(c.email or "")
        self._vars["endereco"].set(c.endereco or "")
        self._vars["cidade"].set(c.cidade or "")

    def _salvar(self):
        from models import cliente_model
        c = self._cliente or Cliente()
        c.nome     = self._vars["nome"].get().strip()
        c.doc      = self._vars["doc"].get().strip()
        c.tel      = self._vars["tel"].get().strip()
        c.email    = self._vars["email"].get().strip()
        c.endereco = self._vars["endereco"].get().strip()
        c.cidade   = self._vars["cidade"].get().strip()

        if not c.nome:
            messagebox.showerror("Campo obrigatório", "Informe o nome do cliente.",
                                 parent=self)
            return

        cliente_model.salvar(c)
        if self._on_save:
            self._on_save()
        self.destroy()