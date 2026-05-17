"""
views/form_pedido_view.py
Formulário completo de criação e edição de pedidos.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import (Card, ScrollFrame, PrimaryBtn, SecondaryBtn,
                            DangerBtn, Field)
from models.pedido_model import Pedido, ItemPedido, TAMANHOS, _SZ_COLS

STATUS_OPTS = ["Rascunho", "Confirmado", "Em produção", "Pronto", "Entregue", "Cancelado"]
ENTREGAS    = ["Retirada na fábrica","Transportadora","Correios PAC",
               "Correios SEDEX","Entrega própria"]
FORMAS_PGTO = ["À vista — PIX","À vista — transferência","À vista — dinheiro",
               "Boleto","Cartão de crédito"]
PRAZOS_PGTO = ["No ato","Na entrega","30","30/60","30/60/90",
               "30/60/90/120","30/60/90/120/150","quinzenal"]
VENDEDORES  = ["Márcia","Edson","Ivanio","Vinicius"]


class FormPedidoView(tk.Frame):
    def __init__(self, parent, controller, app):
        super().__init__(parent, bg=CREME)
        self.ctrl = controller
        self.app = app
        self._pedido: Pedido | None = None
        self._item_rows: list[_ItemRow] = []
        self._autocomplete_win: tk.Toplevel | None = None
        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build(self):
        self._bar = tk.Frame(self, bg=CREME_CARD,
                              highlightbackground=CREME_ESCURO,
                              highlightthickness=1)
        self._bar.pack(fill="x")
        self._build_topbar()

        self._scroll = ScrollFrame(self, bg=CREME)
        self._scroll.pack(fill="both", expand=True)
        body = self._scroll.inner
        body.columnconfigure(0, weight=1)

        self._build_cliente(body)
        self._build_datas(body)
        self._build_pagamento(body)
        self._build_itens(body)
        self._build_obs(body)

        tk.Frame(body, bg=CREME, height=30).pack()

    def _build_topbar(self):
        left = tk.Frame(self._bar, bg=CREME_CARD)
        left.pack(side="left", padx=PAD_PAGE, pady=12)
        self._titulo_lbl = tk.Label(left, text="Novo pedido",
                                     font=FONT_HEADING, fg=CINZA_900, bg=CREME_CARD)
        self._titulo_lbl.pack(side="left")
        self._num_lbl = tk.Label(left, text="", font=FONT_BODY,
                                  fg=CINZA_500, bg=CREME_CARD)
        self._num_lbl.pack(side="left", padx=(10, 0))

        right = tk.Frame(self._bar, bg=CREME_CARD)
        right.pack(side="right", padx=PAD_PAGE, pady=10)

        tk.Label(right, text="Status:", font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME_CARD).pack(side="left", padx=(0, 5))
        self._status_var = tk.StringVar(value="Rascunho")
        ttk.Combobox(right, textvariable=self._status_var, width=14,
                     values=STATUS_OPTS, state="readonly",
                     font=FONT_SMALL).pack(side="left", padx=(0, 16))

        SecondaryBtn(right, "🖨  PDF", command=self._pdf).pack(side="left", padx=4)
        SecondaryBtn(right, "Cancelar", command=self.app.show_lista).pack(side="left", padx=4)
        PrimaryBtn(right, "💾  Salvar pedido", command=self._salvar).pack(side="left", padx=(4, 0))

    def _section(self, parent, title: str) -> tk.Frame:
        card = Card(parent, title=title, accent_left=True)
        card.pack(fill="x", padx=PAD_PAGE, pady=(14, 0))
        return card.body()

    def _row_frame(self, parent, cols=2) -> list[tk.Frame]:
        fr = tk.Frame(parent, bg=CREME_CARD)
        fr.pack(fill="x", pady=PAD_ROW)
        frames = []
        for i in range(cols):
            f = tk.Frame(fr, bg=CREME_CARD)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, PAD_ROW) if i < cols - 1 else 0)
            fr.columnconfigure(i, weight=1)
            frames.append(f)
        return frames

    def _lbl_entry(self, parent, label: str, var: tk.StringVar,
                   combo_vals=None, width=None):
        tk.Label(parent, text=label, font=FONT_LABEL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 2))
        kw = dict(textvariable=var, font=FONT_BODY)
        if width:
            kw["width"] = width
        if combo_vals is not None:
            w = ttk.Combobox(parent, values=combo_vals, state="readonly", **kw)
        else:
            w = ttk.Entry(parent, **kw)
        w.pack(fill="x")
        return w

    def _lbl_text(self, parent, label: str, height=2) -> tk.Text:
        tk.Label(parent, text=label, font=FONT_LABEL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 2))
        t = tk.Text(parent, height=height, font=FONT_BODY,
                    bg=CREME_CARD, fg=CINZA_700,
                    relief="solid", borderwidth=1)
        t.pack(fill="x")
        return t

    # ── Seções do formulário ──────────────────────────────────────────────────

    def _build_cliente(self, parent):
        self._v = {}
        body = self._section(parent, "👤  Dados do cliente")
        for k in ["cli_nome","cli_doc","cli_tel","cli_email","cli_end","cli_cidade"]:
            self._v[k] = tk.StringVar()

        # Nome com autocomplete
        r1 = self._row_frame(body, 2)
        tk.Label(r1[0], text="Nome / razão social *", font=FONT_LABEL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 2))
        self._nome_entry = ttk.Entry(r1[0], textvariable=self._v["cli_nome"],
                                      font=FONT_BODY)
        self._nome_entry.pack(fill="x")
        self._nome_entry.bind("<KeyRelease>", self._on_nome_key)
        self._nome_entry.bind("<FocusOut>", self._hide_autocomplete)
        self._nome_entry.bind("<Down>", self._ac_down)
        self._nome_entry.bind("<Escape>", lambda _: self._hide_autocomplete())

        self._lbl_entry(r1[1], "CPF / CNPJ", self._v["cli_doc"])

        r2 = self._row_frame(body, 2)
        self._lbl_entry(r2[0], "Telefone", self._v["cli_tel"])
        self._lbl_entry(r2[1], "E-mail", self._v["cli_email"])

        r3b = tk.Frame(body, bg=CREME_CARD)
        r3b.pack(fill="x", pady=PAD_ROW)
        r3b.columnconfigure(0, weight=2)
        r3b.columnconfigure(1, weight=1)
        for i, (lbl, key) in enumerate([("Endereço", "cli_end"),
                                          ("Cidade / UF", "cli_cidade")]):
            f = tk.Frame(r3b, bg=CREME_CARD)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, PAD_ROW) if i == 0 else 0)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 2))
            ttk.Entry(f, textvariable=self._v[key],
                      font=FONT_BODY).pack(fill="x")

    # ── Autocomplete de cliente ───────────────────────────────────────────────

    def _on_nome_key(self, event):
        # Navegação não deve disparar busca
        if event.keysym in ("Down", "Up", "Return", "Escape", "Tab"):
            return
        termo = self._v["cli_nome"].get().strip()
        if len(termo) < 2:
            self._hide_autocomplete()
            return
        resultados = self.ctrl.buscar_clientes_autocomplete(termo)
        if resultados:
            self._show_autocomplete(resultados)
        else:
            self._hide_autocomplete()

    def _show_autocomplete(self, clientes: list[dict]):
        self._hide_autocomplete(destroy=True)

        win = tk.Toplevel(self)
        win.wm_overrideredirect(True)
        win.configure(bg=CREME_CARD)
        self._autocomplete_win = win

        # Posiciona abaixo do campo de nome
        self._nome_entry.update_idletasks()
        x = self._nome_entry.winfo_rootx()
        y = self._nome_entry.winfo_rooty() + self._nome_entry.winfo_height() + 2
        w = max(self._nome_entry.winfo_width(), 320)
        win.geometry(f"{w}x{min(len(clientes)*36+4, 200)}+{x}+{y}")
        win.lift()

        # Frame com borda
        outer = tk.Frame(win, bg=AZUL_BORDER, highlightthickness=0)
        outer.pack(fill="both", expand=True, padx=1, pady=1)

        self._ac_listbox = tk.Listbox(
            outer, font=FONT_BODY,
            bg=CREME_CARD, fg=CINZA_900,
            selectbackground=AZUL, selectforeground="white",
            relief="flat", borderwidth=0, activestyle="none",
            height=min(len(clientes), 6)
        )
        self._ac_listbox.pack(fill="both", expand=True)
        self._ac_data = clientes

        for c in clientes:
            cidade = f" — {c['cidade']}" if c.get("cidade") else ""
            self._ac_listbox.insert("end", f"{c['nome']}{cidade}")

        self._ac_listbox.bind("<<ListboxSelect>>", self._ac_select)
        self._ac_listbox.bind("<Return>", self._ac_select)
        self._ac_listbox.bind("<FocusOut>", self._hide_autocomplete)

    def _hide_autocomplete(self, event=None, destroy=False):
        if self._autocomplete_win and self._autocomplete_win.winfo_exists():
            self._autocomplete_win.destroy()
        self._autocomplete_win = None

    def _ac_down(self, event):
        if self._autocomplete_win and hasattr(self, "_ac_listbox"):
            self._ac_listbox.focus_set()
            if self._ac_listbox.size() > 0:
                self._ac_listbox.selection_set(0)

    def _ac_select(self, event=None):
        if not hasattr(self, "_ac_listbox"):
            return
        sel = self._ac_listbox.curselection()
        if not sel:
            return
        c = self._ac_data[sel[0]]
        self._preencher_cliente(c)
        self._hide_autocomplete()
        # Foco retorna ao campo de nome
        self._nome_entry.focus_set()

    def _preencher_cliente(self, c: dict):
        """Preenche os campos do cliente a partir de um dict de autocomplete."""
        self._v["cli_nome"].set(c.get("nome", "") or c.get("cliente_nome", ""))
        self._v["cli_doc"].set(c.get("doc", "") or c.get("cliente_doc", ""))
        self._v["cli_tel"].set(c.get("tel", "") or c.get("cliente_tel", ""))
        self._v["cli_email"].set(c.get("email", "") or c.get("cliente_email", ""))
        self._v["cli_end"].set(c.get("endereco", "") or c.get("cliente_end", ""))
        self._v["cli_cidade"].set(c.get("cidade", "") or c.get("cliente_cidade", ""))

    def prefill_cliente(self, cliente: dict):
        """Pré-preenche campos de cliente (chamado de ClientesView)."""
        self._preencher_cliente(cliente)

    def _build_datas(self, parent):
        for k in ["dt_pedido","dt_entrega","tipo_entrega"]:
            self._v[k] = tk.StringVar()
        body = self._section(parent, "📅  Datas e entrega")
        r = tk.Frame(body, bg=CREME_CARD)
        r.pack(fill="x", pady=PAD_ROW)
        for i, (lbl, key, opts) in enumerate([
            ("Data do pedido (dd/mm/aaaa)", "dt_pedido", None),
            ("Previsão de entrega (dd/mm/aaaa)", "dt_entrega", None),
            ("Tipo de entrega", "tipo_entrega", ENTREGAS),
        ]):
            f = tk.Frame(r, bg=CREME_CARD)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, PAD_ROW) if i < 2 else 0)
            r.columnconfigure(i, weight=1)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 2))
            kw = dict(textvariable=self._v[key], font=FONT_BODY)
            if opts:
                ttk.Combobox(f, values=opts, state="readonly", **kw).pack(fill="x")
            else:
                ttk.Entry(f, **kw).pack(fill="x")
        self._obs_entrega = self._lbl_text(body, "Observações de entrega")

    def _build_pagamento(self, parent):
        for k in ["forma_pgto","prazo_pgto","desconto","vendedor"]:
            self._v[k] = tk.StringVar()
        body = self._section(parent, "💳  Pagamento e Vendedor")
        r = tk.Frame(body, bg=CREME_CARD)
        r.pack(fill="x", pady=PAD_ROW)
        fields = [
            ("Forma de pagamento", "forma_pgto", FORMAS_PGTO),
            ("Prazo de pagamento", "prazo_pgto", PRAZOS_PGTO),
            ("Vendedor", "vendedor", VENDEDORES),
            ("Desconto (%)", "desconto", None),
        ]
        for i, (lbl, key, opts) in enumerate(fields):
            f = tk.Frame(r, bg=CREME_CARD)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, PAD_ROW) if i < len(fields)-1 else 0)
            r.columnconfigure(i, weight=1)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0, 2))
            kw = dict(textvariable=self._v[key], font=FONT_BODY)
            if opts:
                ttk.Combobox(f, values=opts, state="readonly", **kw).pack(fill="x")
            else:
                e = ttk.Entry(f, **kw)
                e.pack(fill="x")
                e.bind("<KeyRelease>", lambda _: self._recalc())
        self._obs_pgto = self._lbl_text(body, "Observações de pagamento")

    def _build_itens(self, parent):
        card = Card(parent, title="🧶  Itens do pedido", accent_left=True)
        card.pack(fill="x", padx=PAD_PAGE, pady=(14, 0))

        tot_bar = tk.Frame(card, bg=CREME_CARD)
        tot_bar.pack(fill="x", padx=PAD_CARD, pady=(0, 6))
        self._tot_pcs_lbl = tk.Label(tot_bar, text="0 peças",
                                      font=FONT_SUBHEAD, fg=AZUL, bg=CREME_CARD)
        self._tot_pcs_lbl.pack(side="left")
        self._tot_val_lbl = tk.Label(tot_bar, text="  R$ 0,00",
                                      font=FONT_SUBHEAD, fg=AZUL, bg=CREME_CARD)
        self._tot_val_lbl.pack(side="left")
        SecondaryBtn(tot_bar, "＋  Adicionar referência",
                     command=self._add_item).pack(side="right")

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=PAD_CARD)
        self._itens_frame = tk.Frame(card, bg=CREME_CARD)
        self._itens_frame.pack(fill="x", padx=PAD_CARD, pady=(6, PAD_CARD))

    def _build_obs(self, parent):
        body = self._section(parent, "📝  Observações gerais")
        self._obs_geral = self._lbl_text(body, "Informações adicionais, embalagem, etc.", height=3)

    # ── Itens ─────────────────────────────────────────────────────────────────

    def _add_item(self, item: ItemPedido | None = None):
        idx = len(self._item_rows) + 1
        row = _ItemRow(self._itens_frame, idx, item,
                       on_remove=self._remove_item, on_change=self._recalc)
        row.pack(fill="x", pady=(0, 8))
        self._item_rows.append(row)
        self._recalc()

    def _remove_item(self, row: "_ItemRow"):
        self._item_rows.remove(row)
        row.destroy()
        self._recalc()

    def _recalc(self, *_):
        total_pcs = 0
        total_val = 0.0
        for row in self._item_rows:
            pcs, val = row.totals()
            total_pcs += pcs
            total_val += val
        try:
            desc = float(self._v["desconto"].get() or 0)
        except ValueError:
            desc = 0
        liq = total_val * (1 - desc / 100)
        self._tot_pcs_lbl.config(text=f"{total_pcs} peças")
        self._tot_val_lbl.config(text=f"  R$ {liq:,.2f}")

    # ── Load / Save ───────────────────────────────────────────────────────────

    def novo(self, cliente: dict = None):
        self._pedido = self.ctrl.novo()
        self._titulo_lbl.config(text="Novo pedido")
        self._num_lbl.config(text="")
        self._status_var.set("Rascunho")
        for k, var in self._v.items():
            var.set("")
        self._v["dt_pedido"].set(self._pedido.dt_pedido)
        self._obs_entrega.delete("1.0", "end")
        self._obs_pgto.delete("1.0", "end")
        self._obs_geral.delete("1.0", "end")
        for r in self._item_rows:
            r.destroy()
        self._item_rows.clear()
        self._recalc()
        # Preenche dados do cliente se fornecido
        if cliente:
            self.prefill_cliente(cliente)

    def carregar(self, pedido_id: int):
        self.novo()
        p = self.ctrl.carregar(pedido_id)
        if not p:
            return
        self._pedido = p
        self._titulo_lbl.config(text="Editar pedido")
        self._num_lbl.config(text=p.numero)
        self._status_var.set(p.status)
        mapa = {
            "cli_nome":    "cliente_nome",
            "cli_doc":     "cliente_doc",
            "cli_tel":     "cliente_tel",
            "cli_email":   "cliente_email",
            "cli_end":     "cliente_end",
            "cli_cidade":  "cliente_cidade",
            "dt_pedido":   "dt_pedido",
            "dt_entrega":  "dt_entrega",
            "tipo_entrega":"tipo_entrega",
            "forma_pgto":  "forma_pgto",
            "prazo_pgto":  "prazo_pgto",
            "vendedor":    "vendedor",
        }
        for vk, pk in mapa.items():
            self._v[vk].set(str(getattr(p, pk) or ""))
        self._v["desconto"].set(str(p.desconto or ""))
        self._obs_entrega.insert("1.0", p.obs_entrega or "")
        self._obs_pgto.insert("1.0", p.obs_pgto or "")
        self._obs_geral.insert("1.0", p.obs_geral or "")
        for item in p.itens:
            self._add_item(item)

    def _collect(self) -> Pedido:
        p = self._pedido or Pedido()
        p.cliente_nome   = self._v["cli_nome"].get().strip()
        p.cliente_doc    = self._v["cli_doc"].get()
        p.cliente_tel    = self._v["cli_tel"].get()
        p.cliente_email  = self._v["cli_email"].get()
        p.cliente_end    = self._v["cli_end"].get()
        p.cliente_cidade = self._v["cli_cidade"].get()
        p.dt_pedido      = self._v["dt_pedido"].get()
        p.dt_entrega     = self._v["dt_entrega"].get()
        p.tipo_entrega   = self._v["tipo_entrega"].get()
        p.obs_entrega    = self._obs_entrega.get("1.0", "end-1c")
        p.forma_pgto     = self._v["forma_pgto"].get()
        p.prazo_pgto     = self._v["prazo_pgto"].get()
        p.obs_pgto       = self._obs_pgto.get("1.0", "end-1c")
        p.obs_geral      = self._obs_geral.get("1.0", "end-1c")
        p.vendedor       = self._v["vendedor"].get()
        p.status         = self._status_var.get()
        try:
            p.desconto = float(self._v["desconto"].get() or 0)
        except ValueError:
            p.desconto = 0
        p.itens = [r.to_item() for r in self._item_rows]
        return p

    def _salvar(self):
        p = self._collect()
        if self.ctrl.salvar(p):
            self._pedido = p
            self._num_lbl.config(text=p.numero)
            self._titulo_lbl.config(text="Editar pedido")
            self.app.refresh_lista()
            from tkinter import messagebox
            messagebox.showinfo("Salvo", f"Pedido {p.numero} salvo com sucesso!")

    def _pdf(self):
        p = self._collect()
        if not p.numero:
            from tkinter import messagebox
            messagebox.showinfo("PDF", "Salve o pedido antes de gerar o PDF.")
            return
        self.ctrl.exportar_pdf(p)


# ── Item row widget ───────────────────────────────────────────────────────────

PRODUTOS_MOCK = {
    "1130": {"descricao": "Calça fusô", "preco": 109.8,
             "cores": ["preto","marinho","vinho","ninive"]},
    "1163": {"descricao": "Calça sweet friso", "preco": 139.80,
             "cores": ["preto","bege","vinho"]},
    "1003": {"descricao": "Blusa sweet friso", "preco": 139.80,
             "cores": ["rosa","preto","branco"]},
    "2001": {"descricao": "Blusa térmica feminina", "preco": 39.8,
             "cores": ["branco","preto","vermelho","verde"]},
}

COR_HEX = {
    "preto":"#1F1F1F","branco":"#F5F5F5","azul":"#355CDE",
    "marinho":"#1D2951","vermelho":"#C62828","verde":"#2E7D32",
    "rosa":"#E88CB2","bege":"#D7B899","cinza":"#9E9E9E",
    "vinho":"#7B1E3F","offwhite":"#F4F1EA","caramelo":"#B56A3C",
    "ninive":"#E3DBC9",
}


class _ItemRow(tk.Frame):
    def __init__(self, parent, idx: int, item: ItemPedido | None,
                 on_remove, on_change):
        super().__init__(parent, bg=CINZA_100,
                         highlightbackground=CREME_ESCURO,
                         highlightthickness=1)
        self._on_remove = on_remove
        self._on_change = on_change
        self._vs: dict[str, tk.StringVar] = {}
        self._sz: dict[str, tk.StringVar] = {}
        self._color_tip: tk.Toplevel | None = None
        self._build(idx)
        if item:
            self._load(item)

    def _build(self, idx: int):
        hdr = tk.Frame(self, bg=AZUL)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  Referência {idx}",
                 font=(FONT_FAMILY, 9, "bold"), fg=DOURADO,
                 bg=AZUL).pack(side="left", pady=5)
        tk.Button(hdr, text="✕ remover", font=FONT_LABEL,
                  fg="#F09595", bg=AZUL, relief="flat", cursor="hand2",
                  activebackground=AZUL_MED, activeforeground="white",
                  command=lambda: self._on_remove(self)).pack(
                  side="right", padx=8, pady=4)

        body = tk.Frame(self, bg=CINZA_100)
        body.pack(fill="x", padx=10, pady=8)

        r1 = tk.Frame(body, bg=CINZA_100)
        r1.pack(fill="x", pady=(0, 6))
        fields = [
            ("Referência / código", "referencia", 2),
            ("Descrição",           "descricao",  3),
            ("Cor",                 "cor",        2),
            ("Preço unitário R$",   "preco",      1),
        ]
        for i, (lbl, key, weight) in enumerate(fields):
            self._vs[key] = tk.StringVar()
            f = tk.Frame(r1, bg=CINZA_100)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, 8) if i < len(fields)-1 else 0)
            r1.columnconfigure(i, weight=weight)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CINZA_100).pack(anchor="w", pady=(0, 2))
            e = ttk.Entry(f, textvariable=self._vs[key], font=FONT_BODY)
            e.pack(fill="x")
            if key == "referencia":
                e.bind("<KeyRelease>", self._buscar_produto)
            else:
                e.bind("<KeyRelease>", lambda _: self._on_change())

        # Paleta de cores
        self._cores_paleta = tk.Frame(body, bg="#F7F1EA",
                                       highlightbackground="#E6DACB",
                                       highlightthickness=1)
        self._cores_paleta.pack(fill="x", pady=(0, 8))
        tk.Label(self._cores_paleta, text="Cores disponíveis",
                 font=(FONT_FAMILY, 9, "bold"), fg="#7A5A3A",
                 bg="#F7F1EA").pack(side="left", padx=(8, 8), pady=6)
        self._cores_dots = tk.Frame(self._cores_paleta, bg="#F7F1EA")
        self._cores_dots.pack(side="left", pady=4)

        # Tamanhos
        r2 = tk.Frame(body, bg=CINZA_100)
        r2.pack(fill="x")
        tk.Label(r2, text="Qtd. por tamanho →",
                 font=FONT_LABEL, fg=CINZA_500, bg=CINZA_100).grid(
                 row=0, column=0, sticky="w", padx=(0, 12))
        self._tot_lbl = tk.Label(r2, text="0 pçs",
                                  font=(FONT_FAMILY, 9, "bold"),
                                  fg=AZUL, bg=CINZA_100)
        for i, size in enumerate(TAMANHOS):
            self._sz[size] = tk.StringVar(value="0")
            f = tk.Frame(r2, bg=CINZA_100)
            f.grid(row=0, column=i+1, padx=3)
            tk.Label(f, text=size, font=FONT_LABEL,
                     fg=CINZA_500, bg=CINZA_100).pack()
            sp = ttk.Spinbox(f, textvariable=self._sz[size],
                             from_=0, to=9999, width=5, font=FONT_BODY,
                             command=self._on_change)
            sp.pack()
            sp.bind("<KeyRelease>", lambda _: self._on_change())
        self._tot_lbl.grid(row=0, column=len(TAMANHOS)+1, padx=(12, 0))

    def _load(self, item: ItemPedido):
        self._vs["referencia"].set(item.referencia)
        self._vs["descricao"].set(item.descricao)
        self._vs["cor"].set(item.cor)
        self._vs["preco"].set(str(item.preco_unitario) if item.preco_unitario else "")
        for size, col in zip(TAMANHOS, _SZ_COLS):
            self._sz[size].set(str(getattr(item, col, 0)))
        self._render_cores([c.strip() for c in str(item.cor or "").split(",") if c.strip()])

    def _buscar_produto(self, event=None):
        ref = self._vs["referencia"].get().strip()
        produto = PRODUTOS_MOCK.get(ref)
        if not produto:
            return
        self._vs["descricao"].set(produto["descricao"])
        self._vs["preco"].set(f'{produto["preco"]:.2f}')
        self._render_cores(produto.get("cores", []))
        self._on_change()

    def _render_cores(self, cores: list[str]):
        for w in self._cores_dots.winfo_children():
            w.destroy()
        if not cores:
            return
        for nome_cor in cores:
            cor_hex = COR_HEX.get(nome_cor.lower(), "#607D8B")
            cv = tk.Canvas(self._cores_dots, width=22, height=22,
                           bg="#F7F1EA", highlightthickness=0, cursor="hand2")
            cv.pack(side="left", padx=3)
            cv.create_oval(3, 3, 19, 19, fill=cor_hex, outline="#888888", width=1)
            cv.bind("<Enter>", lambda e, n=nome_cor: self._show_tip(e, n))
            cv.bind("<Leave>", self._hide_tip)
            cv.bind("<Button-1>", lambda e, n=nome_cor: self._vs["cor"].set(n))

    def _show_tip(self, event, nome: str):
        self._hide_tip()
        tip = tk.Toplevel(self)
        tip.wm_overrideredirect(True)
        tip.configure(bg="#2B2B2B")
        tip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        tk.Label(tip, text=nome.capitalize(), font=(FONT_FAMILY, 8),
                 fg="white", bg="#2B2B2B", padx=6, pady=2).pack()
        self._color_tip = tip

    def _hide_tip(self, _=None):
        tip = getattr(self, "_color_tip", None)
        if tip and tip.winfo_exists():
            tip.destroy()
        self._color_tip = None

    def totals(self) -> tuple[int, float]:
        pcs = sum(int(v.get() or 0) for v in self._sz.values())
        try:
            preco = float(self._vs["preco"].get() or 0)
        except ValueError:
            preco = 0.0
        self._tot_lbl.config(text=f"{pcs} pçs")
        return pcs, pcs * preco

    def to_item(self) -> ItemPedido:
        item = ItemPedido()
        item.referencia = self._vs["referencia"].get()
        item.descricao  = self._vs["descricao"].get()
        item.cor        = self._vs["cor"].get()
        try:
            item.preco_unitario = float(self._vs["preco"].get() or 0)
        except ValueError:
            item.preco_unitario = 0
        for size, col in zip(TAMANHOS, _SZ_COLS):
            try:
                setattr(item, col, int(self._sz[size].get() or 0))
            except ValueError:
                setattr(item, col, 0)
        return item