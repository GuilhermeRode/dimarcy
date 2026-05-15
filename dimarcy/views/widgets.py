"""
views/widgets.py
Componentes reutilizáveis (widgets customizados).
"""
import tkinter as tk
from tkinter import ttk
from views.theme import *


def label(parent, text: str = "", font=FONT_BODY, color=CINZA_900, **kw):
    """Label com fonte e cor padrão."""
    return tk.Label(parent, text=text, font=font, fg=color,
                    bg=parent["bg"] if hasattr(parent, "keys") else CREME, **kw)


def entry(parent, textvariable=None, width=None, **kw):
    e = ttk.Entry(parent, textvariable=textvariable, font=FONT_BODY, **kw)
    if width:
        e.config(width=width)
    return e


# ── Status badge ─────────────────────────────────────────────────────────────

class StatusBadge(tk.Frame):
    def __init__(self, parent, status: str, **kw):
        bg, fg = STATUS_COLORS.get(status, (CINZA_100, CINZA_700))
        kw.pop("bg", None)  # Remove bg from kw if present
        super().__init__(parent, bg=bg, **kw)
        tk.Label(self, text=f"  {status}  ", font=FONT_SMALL,
                 fg=fg, bg=bg).pack()


# ── Card frame ────────────────────────────────────────────────────────────────

class Card(tk.Frame):
    """Frame com visual de card: fundo branco, borda suave, título opcional."""
    def __init__(self, parent, title: str = "", accent_left: bool = False, **kw):
        bg = kw.pop("bg", CREME_CARD)
        super().__init__(parent, bg=bg,
                         highlightbackground=CREME_ESCURO,
                         highlightthickness=1, **kw)
        if title:
            hdr = tk.Frame(self, bg=bg)
            hdr.pack(fill="x", padx=PAD_CARD, pady=(PAD_CARD, 4))
            if accent_left:
                accent = tk.Frame(hdr, bg=AZUL, width=3)
                accent.pack(side="left", fill="y", padx=(0, 8))
            tk.Label(hdr, text=title, font=FONT_SUBHEAD,
                     fg=AZUL, bg=bg).pack(side="left", anchor="w")
            ttk.Separator(self, orient="horizontal").pack(fill="x",
                padx=PAD_CARD, pady=(0, PAD_CARD//2))

    def body(self) -> tk.Frame:
        f = tk.Frame(self, bg=self["bg"])
        f.pack(fill="both", expand=True, padx=PAD_CARD, pady=(0, PAD_CARD))
        return f


# ── Field group (label + widget) ─────────────────────────────────────────────

class Field(tk.Frame):
    def __init__(self, parent, label_text: str, **kw):
        bg = kw.pop("bg", CREME_CARD)
        super().__init__(parent, bg=bg, **kw)
        tk.Label(self, text=label_text, font=FONT_LABEL,
                 fg=CINZA_500, bg=bg).pack(anchor="w", pady=(0, 2))

    def add(self, widget_cls, **kw):
        w = widget_cls(self, **kw)
        w.pack(fill="x")
        return w


# ── Scrollable frame ─────────────────────────────────────────────────────────

class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=CREME, **kw):
        super().__init__(parent, bg=bg, **kw)
        self._canvas = tk.Canvas(self, bg=bg, borderwidth=0,
                                  highlightthickness=0)
        self._vsb = ttk.Scrollbar(self, orient="vertical",
                                   command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._bind_mousewheel()

        self.update()
        region = self._canvas.bbox("all")
        self._canvas.configure(scrollregion=region or "0 0 1 1")

    def _bind_mousewheel(self):
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>", self._on_mousewheel)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self._canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self._canvas.yview_scroll(-1, "units")

    @property
    def inner(self) -> tk.Frame:
        """Retorna o frame interno para widgets."""
        if not hasattr(self, "_inner"):
            self._inner = tk.Frame(self._canvas, bg=self["bg"])
            self._canvas.create_window((0, 0), window=self._inner, anchor="nw")
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        return self._inner


# ── PrimaryBtn ────────────────────────────────────────────────────────────────

class PrimaryBtn(tk.Frame):
    def __init__(self, parent, text: str = "", command=None, **kw):
        super().__init__(parent, **kw)
        self._btn = tk.Button(self, text=text, command=command,
                              font=FONT_SMALL, bg=AZUL, fg="white",
                              activebackground=AZUL_ESCURO, activeforeground="white",
                              relief="flat", padx=14, pady=6)
        self._btn.pack()

    def pack(self, **kw):
        super().pack(kw, fill="x", expand=False) if kw else super().pack()


# ── SecondaryBtn ──────────────────────────────────────────────────────────────

class SecondaryBtn(tk.Frame):
    def __init__(self, parent, text: str = "", command=None, **kw):
        super().__init__(parent, **kw)
        self._btn = tk.Button(self, text=text, command=command,
                              font=FONT_SMALL, bg=CINZA_200, fg=CINZA_800,
                              activebackground=CINZA_300, activeforeground=CINZA_900,
                              relief="flat", padx=14, pady=6)
        self._btn.pack()


# ── DangerBtn ──────────────────────────────────────────────────────────────────

class DangerBtn(tk.Frame):
    def __init__(self, parent, text: str = "", command=None, **kw):
        super().__init__(parent, **kw)
        self._btn = tk.Button(self, text=text, command=command,
                              font=FONT_SMALL, bg="#D32F2F", fg="white",
                              activebackground="#B71C1C", activeforeground="white",
                              relief="flat", padx=14, pady=6)
        self._btn.pack()


# ── StatCard ──────────────────────────────────────────────────────────────────

class StatCard(tk.Frame):
    def __init__(self, parent, label: str = "", value: str = "", icon: str = "", icon_color: str = AZUL, **kw):
        kw.pop("bg", None)  # Remove bg from kw if present
        super().__init__(parent, bg=CREME_CARD,
                         highlightbackground=CREME_ESCURO,
                         highlightthickness=1, **kw)
        pad = 14
        tk.Label(self, text=icon, font=("Segoe UI", 32),
                 fg=icon_color, bg=CREME_CARD).pack(padx=pad, pady=(pad, 0), anchor="w")
        tk.Label(self, text=value, font=FONT_HEADING,
                 fg=CINZA_900, bg=CREME_CARD).pack(padx=pad, anchor="w", pady=(4, 0))
        tk.Label(self, text=label, font=FONT_SMALL,
                 fg=CINZA_500, bg=CREME_CARD).pack(padx=pad, pady=(0, pad), anchor="w")


# ── Treeview builder ──────────────────────────────────────────────────────────

def build_treeview(parent, cols: list[tuple], height: int = 12) -> ttk.Treeview:
    """Constrói um Treeview estilizado com colunas dinâmicas."""
    tree = ttk.Treeview(parent, columns=[c[0] for c in cols],
                        height=height, show="headings")
    for col_id, heading, width in cols:
        tree.column(col_id, width=width, anchor="w")
        tree.heading(col_id, text=heading)
    return tree
