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

STATUS_OPTS = ["Em produção","Pronto","Entregue","Cancelado"]
ENTREGAS    = ["Retirada na fábrica","Transportadora","Correios PAC",
               "Correios SEDEX","Entrega própria"]
FORMAS_PGTO = ["À vista — PIX","À vista — transferência","À vista — dinheiro",
               "Boleto","Cartão de crédito"]
PRAZOS_PGTO = ["Na entrega","30","30/60", "30/60/90", "30/60/90/120", "30/60/90/120/150", "quinzenal"]


class FormPedidoView(tk.Frame):
    def __init__(self, parent, controller, app):
        super().__init__(parent, bg=CREME)
        self.ctrl = controller
        self.app = app
        self._pedido: Pedido | None = None
        self._item_rows: list[_ItemRow] = []
        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build(self):
        # Top bar fixa
        self._bar = tk.Frame(self, bg=CREME_CARD,
                              highlightbackground=CREME_ESCURO,
                              highlightthickness=1)
        self._bar.pack(fill="x")
        self._build_topbar()

        # Corpo rolável
        self._scroll = ScrollFrame(self, bg=CREME)
        self._scroll.pack(fill="both", expand=True)
        body = self._scroll.inner
        body.columnconfigure(0, weight=1)

        self._build_cliente(body)
        self._build_datas(body)
        self._build_pagamento(body)
        self._build_itens(body)
        self._build_obs(body)

        # Padding final
        tk.Frame(body, bg=CREME, height=30).pack()

    def _build_topbar(self):
        left = tk.Frame(self._bar, bg=CREME_CARD)
        left.pack(side="left", padx=PAD_PAGE, pady=12)

        self._titulo_lbl = tk.Label(left, text="Novo pedido",
                                     font=FONT_HEADING, fg=CINZA_900,bg=CREME_CARD
                                     )
        self._titulo_lbl.pack(side="left")

        self._num_lbl = tk.Label(left, text="", font=FONT_BODY,
                                  fg=CINZA_500, bg=CREME_CARD)
        self._num_lbl.pack(side="left", padx=(10, 0))

        right = tk.Frame(self._bar, bg=CREME_CARD)
        right.pack(side="right", padx=PAD_PAGE, pady=10)

        tk.Label(right, text="Status:", font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME_CARD).pack(side="left", padx=(0,5))
        self._status_var = tk.StringVar(value="Rascunho")
        ttk.Combobox(right, textvariable=self._status_var, width=14,
                     values=STATUS_OPTS, state="readonly",
                     font=FONT_SMALL).pack(side="left", padx=(0, 16))

        SecondaryBtn(right, "🖨  PDF", command=self._pdf).pack(side="left", padx=4)
        SecondaryBtn(right, "Cancelar", command=self.app.show_lista).pack(side="left", padx=4)
        PrimaryBtn(right, "💾  Salvar pedido", command=self._salvar).pack(side="left", padx=(4,0))

    def _section(self, parent, title: str) -> tk.Frame:
        """Retorna o body frame de um Card section."""
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
                   combo_vals=None, width=None) -> ttk.Entry | ttk.Combobox:
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
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0,2))
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

        r1 = self._row_frame(body, 2)
        self._lbl_entry(r1[0], "Nome / razão social *", self._v["cli_nome"])
        self._lbl_entry(r1[1], "CPF / CNPJ", self._v["cli_doc"])

        r2 = self._row_frame(body, 2)
        self._lbl_entry(r2[0], "Telefone", self._v["cli_tel"])
        self._lbl_entry(r2[1], "E-mail", self._v["cli_email"])

        r3 = self._row_frame(body, 3)
        r3[0].grid_configure(padx=(0, PAD_ROW))
        tk.Label(r3[0], text="Endereço", font=FONT_LABEL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0,2))
        ttk.Entry(r3[0], textvariable=self._v["cli_end"],
                  font=FONT_BODY).pack(fill="x")
        # make endereço span 2 columns
        r3[0].grid_configure(columnspan=1)
        tk.Label(r3[1], text="Endereço", font=FONT_LABEL,
                 fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0,2))
        ttk.Entry(r3[1], textvariable=self._v["cli_end"],
                  font=FONT_BODY).pack(fill="x")

        # redo properly
        for w in body.winfo_children():
            if isinstance(w, tk.Frame) and w == r3[0].master:
                w.destroy()
                break

        r3b = tk.Frame(body, bg=CREME_CARD)
        r3b.pack(fill="x", pady=PAD_ROW)
        r3b.columnconfigure(0, weight=2)
        r3b.columnconfigure(1, weight=1)
        for i, (lbl, key) in enumerate([("Endereço","cli_end"),
                                          ("Cidade / UF","cli_cidade")]):
            f = tk.Frame(r3b, bg=CREME_CARD)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, PAD_ROW) if i == 0 else 0)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0,2))
            ttk.Entry(f, textvariable=self._v[key],
                      font=FONT_BODY).pack(fill="x")

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
                     fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0,2))
            kw = dict(textvariable=self._v[key], font=FONT_BODY)
            if opts:
                ttk.Combobox(f, values=opts, state="readonly", **kw).pack(fill="x")
            else:
                ttk.Entry(f, **kw).pack(fill="x")

        self._obs_entrega = self._lbl_text(body, "Observações de entrega")

    def _build_pagamento(self, parent):
        for k in ["forma_pgto","prazo_pgto","desconto"]:
            self._v[k] = tk.StringVar()
        body = self._section(parent, "💳  Pagamento")
        r = tk.Frame(body, bg=CREME_CARD)
        r.pack(fill="x", pady=PAD_ROW)
        fields = [
            ("Forma de pagamento", "forma_pgto", FORMAS_PGTO),
            ("Prazo de pagamento", "prazo_pgto", PRAZOS_PGTO),
            ("Desconto (%)", "desconto", None),
            
        ]
        for i, (lbl, key, opts) in enumerate(fields):
            f = tk.Frame(r, bg=CREME_CARD)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, PAD_ROW) if i < len(fields)-1 else 0)
            r.columnconfigure(i, weight=1)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CREME_CARD).pack(anchor="w", pady=(0,2))
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

        # totais bar
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
                       on_remove=self._remove_item,
                       on_change=self._recalc)
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

    def novo(self):
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
            "cli_nome":"cliente_nome","cli_doc":"cliente_doc",
            "cli_tel":"cliente_tel","cli_email":"cliente_email",
            "cli_end":"cliente_end","cli_cidade":"cliente_cidade",
            "dt_pedido":"dt_pedido","dt_entrega":"dt_entrega",
            "tipo_entrega":"tipo_entrega","forma_pgto":"forma_pgto",
            "prazo_pgto":"prazo_pgto",
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
        p.cliente_nome  = self._v["cli_nome"].get().strip()
        p.cliente_doc   = self._v["cli_doc"].get()
        p.cliente_tel   = self._v["cli_tel"].get()
        p.cliente_email = self._v["cli_email"].get()
        p.cliente_end   = self._v["cli_end"].get()
        p.cliente_cidade= self._v["cli_cidade"].get()
        p.dt_pedido     = self._v["dt_pedido"].get()
        p.dt_entrega    = self._v["dt_entrega"].get()
        p.tipo_entrega  = self._v["tipo_entrega"].get()
        p.obs_entrega   = self._obs_entrega.get("1.0","end-1c")
        p.forma_pgto    = self._v["forma_pgto"].get()
        p.prazo_pgto    = self._v["prazo_pgto"].get()
        p.obs_pgto      = self._obs_pgto.get("1.0","end-1c")
        p.obs_geral     = self._obs_geral.get("1.0","end-1c")
        p.status        = self._status_var.get()
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

class _ItemRow(tk.Frame):
    """Uma linha de item de pedido com campos de referência e grade de tamanhos."""
    def __init__(self, parent, idx: int, item: ItemPedido | None,
                 on_remove, on_change):
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

        # Row 1: ref, descrição, cor, preço
        r1 = tk.Frame(body, bg=CINZA_100)
        r1.pack(fill="x", pady=(0, 6))
        fields = [
            ("Referência / código", "referencia", 2),
            ("Descrição", "descricao", 3),
            ("Cor", "cor", 2),
            ("Preço unitário R$", "preco", 1),
        ]
        for i, (lbl, key, weight) in enumerate(fields):
            self._vs[key] = tk.StringVar()
            f = tk.Frame(r1, bg=CINZA_100)
            f.grid(row=0, column=i, sticky="ew",
                   padx=(0, 8) if i < len(fields)-1 else 0)
            r1.columnconfigure(i, weight=weight)
            tk.Label(f, text=lbl, font=FONT_LABEL,
                     fg=CINZA_500, bg=CINZA_100).pack(anchor="w", pady=(0,2))
            e = ttk.Entry(f, textvariable=self._vs[key], font=FONT_BODY)
            e.pack(fill="x")

            # referência busca automaticamente
            if key == "referencia":
                e.bind("<KeyRelease>", self._buscar_produto_mock)
            else:
                e.bind("<KeyRelease>", lambda _: self._on_change())

        # Row 2: tamanhos
        r2 = tk.Frame(body, bg=CINZA_100)
        r2.pack(fill="x")
        tk.Label(r2, text="Qtd. por tamanho →",
                 font=FONT_LABEL, fg=CINZA_500, bg=CINZA_100).grid(
                 row=0, column=0, sticky="w", padx=(0,12))

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

        self._tot_lbl.grid(row=0, column=len(TAMANHOS)+1, padx=(12,0))

    def _load(self, item: ItemPedido):
        self._vs["referencia"].set(item.referencia)
        self._vs["descricao"].set(item.descricao)
        self._vs["cor"].set(item.cor)
        self._vs["preco"].set(str(item.preco_unitario) if item.preco_unitario else "")
        for size, col in zip(TAMANHOS, _SZ_COLS):
            self._sz[size].set(str(getattr(item, col, 0)))

    def _buscar_produto_mock(self, event=None):
        ref = self._vs["referencia"].get().strip()

        produto = PRODUTOS_MOCK.get(ref)

        if not produto:
            return

        self._vs["descricao"].set(produto["descricao"])
        self._vs["preco"].set(f'{produto["preco"]:.2f}')

        self._on_change()

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

PRODUTOS_MOCK = {
    "1130": {
        "descricao": "Calça fusô",
        "preco": 109.8
        },

    "1163": {
        "descricao": "Calça sweet friso",
        "preco": 139.80
    },

    "1164": {
        "descricao": "Blusa sweet friso",
        "preco": 139.80
    },

    "2001": {
        "descricao": "Blusa térmica feminina",
        "preco": 39.8

    }
}