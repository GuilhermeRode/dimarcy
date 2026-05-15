"""
views/theme.py
Tema azul moderno
"""

# ── Paleta principal ─────────────────────────────────────────────────────────
AZUL_ESCURO   = "#16324F"   # sidebar
AZUL          = "#1F4E79"   # primária
AZUL_MED      = "#2E6DA4"   # hover
AZUL_CLARO    = "#DCEEFF"   # acentos leves
AZUL_SOFT     = "#EDF5FC"   # fundo cards
AZUL_BORDER   = "#C7DCEF"   # bordas suaves

BRANCO_GELO   = "#F8FBFF"   # background geral
BRANCO_CARD   = "#FFFFFF"   # cards
ROW_BG        = "#F4F9FF"   # zebra rows

CINZA_900     = "#1E2933"
CINZA_700     = "#4A5560"
CINZA_500     = "#7A8793"
CINZA_300     = "#D6DEE6"
CINZA_100     = "#EEF3F8"

# Compatibilidade com nomes antigos
AZUL_ESCURO = AZUL_ESCURO
AZUL         = AZUL
AZUL_MED     = AZUL_MED
AZUL_CLARO       = AZUL_CLARO
DOURADO        = "#A7D3FF"

CREME_ESCURO   = AZUL_BORDER
CREME          = BRANCO_GELO
CREME_CARD     = BRANCO_CARD
CREME_ROW      = ROW_BG

# ── Status colors ───────────────────────────────────────────────────────────
STATUS_COLORS = {
    "Rascunho":     ("#EEF3F8", "#4A5560"),
    "Confirmado":   ("#DCEEFF", "#1F4E79"),
    "Em produção":  ("#E8F4FF", "#2E6DA4"),
    "Pronto":       ("#E3F7ED", "#237A4B"),
    "Entregue":     ("#DFF7F2", "#0E7490"),
    "Cancelado":    ("#FDECEC", "#B42318"),
}

# ── Tipografia ──────────────────────────────────────────────────────────────
FONT_FAMILY    = "Segoe UI"

FONT_TITLE     = (FONT_FAMILY, 22, "bold")
FONT_HEADING   = (FONT_FAMILY, 14, "bold")
FONT_SUBHEAD   = (FONT_FAMILY, 11, "bold")
FONT_BODY      = (FONT_FAMILY, 10)
FONT_SMALL     = (FONT_FAMILY, 9)
FONT_LABEL     = (FONT_FAMILY, 8)

# ── Espaçamentos ────────────────────────────────────────────────────────────
PAD_PAGE   = 28
PAD_CARD   = 16
PAD_ROW    = 6
PAD_FIELD  = 4

# ── Dimensões ───────────────────────────────────────────────────────────────
SIDEBAR_W  = 230
RADIUS     = 10
INPUT_H    = 34
BTN_H      = 36