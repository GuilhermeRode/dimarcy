"""
views/theme.py
Tokens de design centralizados — cores, fontes, espaçamentos.
Altere aqui para mudar a aparência de toda a aplicação.
"""

# ── Paleta principal ─────────────────────────────────────────────────────────
MARROM_ESCURO  = "#2A1005"   # sidebar, cabeçalhos escuros
MARROM         = "#4A1B0C"   # cor primária (botões, destaques)
MARROM_MED     = "#712B13"   # hover primário
CARAMELO       = "#C8813A"   # acento quente
DOURADO        = "#FAC775"   # texto sidebar / badges
CREME_ESCURO   = "#EDE0CE"   # border cards
CREME          = "#FDF6EE"   # background geral
CREME_CARD     = "#FFFFFF"   # cards
CREME_ROW      = "#F9F4EE"   # zebra rows

CINZA_900      = "#1C1C1A"   # texto escuro
CINZA_700      = "#444441"   # texto normal
CINZA_500      = "#888780"   # texto muted / labels
CINZA_300      = "#D3D1C7"   # borders suaves
CINZA_100      = "#F1EFE8"   # backgrounds secundários

# Status colors
STATUS_COLORS = {
    "Rascunho":     ("#F1EFE8", "#444441"),   # (bg, fg)
    "Confirmado":   ("#E6F1FB", "#185FA5"),
    "Em produção":  ("#FAEEDA", "#854F0B"),
    "Pronto":       ("#EAF3DE", "#3B6D11"),
    "Entregue":     ("#E1F5EE", "#0F6E56"),
    "Cancelado":    ("#FCEBEB", "#A32D2D"),
}

# ── Tipografia ────────────────────────────────────────────────────────────────
FONT_FAMILY    = "Helvetica"
FONT_TITLE     = (FONT_FAMILY, 22, "bold")
FONT_HEADING   = (FONT_FAMILY, 14, "bold")
FONT_SUBHEAD   = (FONT_FAMILY, 11, "bold")
FONT_BODY      = (FONT_FAMILY, 10)
FONT_SMALL     = (FONT_FAMILY, 9)
FONT_LABEL     = (FONT_FAMILY, 8)

# ── Espaçamentos ──────────────────────────────────────────────────────────────
PAD_PAGE   = 28    # margem externa
PAD_CARD   = 16    # padding interno dos cards
PAD_ROW    = 6     # gap entre campos numa linha
PAD_FIELD  = 4     # gap label→input

# ── Dimensões ─────────────────────────────────────────────────────────────────
SIDEBAR_W  = 230
RADIUS     = 8
INPUT_H    = 32
BTN_H      = 34
