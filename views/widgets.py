"""
views/widgets.py
Componentes reutilizáveis de UI.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from views.theme import *


# ── Helpers ──────────────────────────────────────────────────────────────────

def label(parent, text, font=FONT_SMALL, color=CINZA_500, **kw):
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
        super().__init__(parent, bg=bg, **kw)
        tk.Label(self, text=f"  {status}  ", font=FONT_SMALL,
                 fg=fg, bg=bg).pack()


# ── Card frame ────────────────────────────────────────────────────────────────

class Card(tk.Frame):
    """Frame com visual de card: fundo branco, borda suave, título opcional."""
    def __init__(self, parent, title: str = "", accent_left: bool = False, **kw):
        super().__init__(parent, bg=CREME_CARD,
                         highlightbackground=CREME_ESCURO,
                         highlightthickness=1, **kw)
        if title:
            hdr = tk.Frame(self, bg=CREME_CARD)
            hdr.pack(fill="x", padx=PAD_CARD, pady=(PAD_CARD, 4))
            if accent_left:
                accent = tk.Frame(hdr, bg=AZUL, width=3)
                accent.pack(side="left", fill="y", padx=(0, 8))
            tk.Label(hdr, text=title, font=FONT_SUBHEAD,
                     fg=AZUL, bg=CREME_CARD).pack(side="left", anchor="w")
            ttk.Separator(self, orient="horizontal").pack(fill="x",
                padx=PAD_CARD, pady=(0, PAD_CARD//2))

    def body(self) -> tk.Frame:
        f = tk.Frame(self, bg=CREME_CARD)
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
        self.inner = tk.Frame(self._canvas, bg=bg)
        self._win = self._canvas.create_window((0, 0), window=self.inner,
                                                anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_inner_configure(self, _):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self._canvas.itemconfig(self._win, width=e.width)

    def _on_mousewheel(self, e):
        # Windows: e.delta; Linux: e.num
        delta = -1 * (e.delta // 120) if e.delta else (-1 if e.num == 4 else 1)
        self._canvas.yview_scroll(delta, "units")


# ── Stat card (dashboard) ────────────────────────────────────────────────────

class StatCard(tk.Frame):
    def __init__(self, parent, title: str, value: str,
                 icon: str = "", accent: str = AZUL, **kw):
        bg = kw.pop("bg", CREME_CARD)
        super().__init__(parent, bg=bg,
                         highlightbackground=AZUL_ESCURO,
                         highlightthickness=1, **kw)
        top = tk.Frame(self, bg=bg)
        top.pack(fill="x", padx=16, pady=(14, 0))
        if icon:
            tk.Label(top, text=icon, font=(FONT_FAMILY, 18),
                     fg=accent, bg=bg).pack(side="left")
        tk.Label(top, text=title, font=FONT_LABEL,
                 fg=CINZA_500, bg=bg).pack(side="right", anchor="e")
        tk.Label(self, text=value, font=(FONT_FAMILY, 22, "bold"),
                 fg=accent, bg=bg).pack(anchor="w", padx=16, pady=(4, 14))


# ── Primary / secondary buttons ──────────────────────────────────────────────

class PrimaryBtn(tk.Button):
    def __init__(self, parent, text, command=None, **kw):
        super().__init__(
            parent, text=text, command=command,
            bg=AZUL, fg=DOURADO, activebackground=AZUL_MED,
            activeforeground=DOURADO, font=FONT_BODY,
            relief="flat", cursor="hand2",
            padx=16, pady=6, **kw)


class SecondaryBtn(tk.Button):
    def __init__(self, parent, text, command=None, **kw):
        super().__init__(
            parent, text=text, command=command,
            bg=CREME_CARD, fg=CINZA_700, activebackground=CINZA_100,
            activeforeground=CINZA_900, font=FONT_BODY,
            relief="flat", cursor="hand2",
            highlightbackground=CINZA_300, highlightthickness=1,
            padx=14, pady=5, **kw)


class DangerBtn(tk.Button):
    def __init__(self, parent, text, command=None, **kw):
        super().__init__(
            parent, text=text, command=command,
            bg="#FCEBEB", fg="#A32D2D", activebackground="#F7C1C1",
            activeforeground="#791F1F", font=FONT_BODY,
            relief="flat", cursor="hand2",
            highlightbackground="#F09595", highlightthickness=1,
            padx=14, pady=5, **kw)


# ── Table / Treeview wrapper ──────────────────────────────────────────────────

def build_treeview(parent, columns: list[tuple], height=18) -> ttk.Treeview:
    """columns = list of (id, header, width)"""
    style = ttk.Style()
    style.configure("Tricot.Treeview",
                    background=CREME_CARD, fieldbackground=CREME_CARD,
                    foreground=CINZA_700, rowheight=28,
                    font=FONT_BODY)
    style.configure("Tricot.Treeview.Heading",
                    background=CINZA_100, foreground=AZUL,
                    font=FONT_SMALL, relief="flat")
    style.map("Tricot.Treeview",
              background=[("selected", AZUL)],
              foreground=[("selected", DOURADO)])
    ids = [c[0] for c in columns]
    tv = ttk.Treeview(parent, columns=ids, show="headings",
                       style="Tricot.Treeview", height=height)
    for col_id, header, width in columns:
        tv.heading(col_id, text=header)
        tv.column(col_id, width=width, minwidth=40)
    return tv
