"""
controllers/pdf_controller.py
Geração de PDF profissional via ReportLab.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table,
                                 TableStyle, Spacer, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from models.pedido_model import Pedido, TAMANHOS, _SZ_COLS
from models import config_model

# Paleta
AZUL    = colors.HexColor("#1F4E79")
AZUL_CLARO  = colors.HexColor("#DCEEFF")
CREME     = colors.white
AZUL_ESCURO   = "#16324F"   # sidebar
CINZA_MED = colors.HexColor("#888780")
CINZA_CLR = colors.HexColor("#E8E5DF")
BRANCO    = colors.white

AZUL_ESCURO   = "#16324F"   # sidebar
AZUL          = "#1F4E79"   # primária
AZUL_MED      = "#2E6DA4"   # hover
AZUL_CLARO    = "#DCEEFF"   # acentos leves
AZUL_SOFT     = "#EDF5FC"   # fundo cards
AZUL_BORDER   = "#C7DCEF"   # bordas suaves
def _ps(name, **kw) -> ParagraphStyle:
    return ParagraphStyle(name, **kw)


def gerar(pedido: Pedido, path: str):
    cfg = config_model.get_all()
    empresa = cfg.get("empresa_nome", "Empresa")

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Pedido {pedido.numero}",
        author=empresa,
    )

    s_title  = _ps("t", fontName="Helvetica-Bold", fontSize=22,
                   textColor=AZUL, spaceAfter=2)
    s_sub    = _ps("s", fontName="Helvetica", fontSize=9,
                   textColor=CINZA_MED, spaceAfter=6)
    s_sec    = _ps("sec", fontName="Helvetica-Bold", fontSize=10,
                   textColor=AZUL, spaceBefore=14, spaceAfter=5)
    s_normal = _ps("n", fontName="Helvetica", fontSize=9, leading=14)
    s_footer = _ps("f", fontName="Helvetica", fontSize=7.5,
                   textColor=CINZA_MED, alignment=TA_CENTER)

    story = []

    # ── Cabeçalho ────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(f"<b>{empresa} , "Pedidos"</b>", _ps("h", fontName="Helvetica-Bold",
                  fontSize=14, textColor=AZUL)),
        Paragraph(
            f"<font color='#888780'>Pedido</font> <b>{pedido.numero}</b><br/>"
            f"<font color='#888780'>Emitido: {pedido.dt_pedido or '—'}</font>",
            _ps("hr", fontName="Helvetica", fontSize=9,
                textColor=AZUL_ESCURO, alignment=TA_RIGHT)),
    ]]
    ht = Table(header_data, colWidths=[10*cm, 7*cm])
    ht.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(ht)

    # Badge de status
    status_color = {
        "Rascunho": "#888780", "Confirmado": "#185FA5",
        "Em produção": "#854F0B", "Pronto": "#3B6D11",
        "Entregue": "#0F6E56", "Cancelado": "#A32D2D",
    }.get(pedido.status, "#888780")
    story.append(Paragraph(
        f'<font color="{status_color}">● {pedido.status}</font>',
        _ps("st", fontName="Helvetica-Bold", fontSize=9, spaceAfter=4)))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=AZUL, spaceAfter=12))

    # ── Cliente ───────────────────────────────────────────────────────────────
    story.append(Paragraph("DADOS DO CLIENTE", s_sec))
    cli_data = [
        ["Nome / Razão Social", pedido.cliente_nome or "—",
         "Cidade / UF", pedido.cliente_cidade or "—"],
    ]
    ct = Table(cli_data, colWidths=[3.2
    *cm, 6.5*cm, 2.8*cm, 4.7*cm])
    ct.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("TEXTCOLOR",   (0,0), (0,-1), CINZA_MED),
        ("TEXTCOLOR",   (2,0), (2,-1), CINZA_MED),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [CREME, BRANCO]),
        ("GRID",        (0,0), (-1,-1), 0.4, CINZA_CLR),
        ("PADDING",     (0,0), (-1,-1), 6),
    ]))
    story.append(ct)

    # ── Itens ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("ITENS DO PEDIDO", s_sec))
    col_hdrs = ["Ref.", "Descrição", "Cor"] + TAMANHOS + ["Total", "Unit.", "Subtotal"]
    rows = [col_hdrs]
    for it in pedido.itens:
        qtds = [getattr(it, c) for c in _SZ_COLS]
        rows.append([
            it.referencia, it.descricao, it.cor, it.material,
            *[str(q) if q else "·" for q in qtds],
            str(it.total_pcs),
            f"R${it.preco_unitario:.2f}",
            f"R${it.subtotal:.2f}",
        ])
    col_w = [1.8*cm, 3*cm, 1.8*cm, 1.8*cm] + [0.8*cm]*7 + [1.1*cm, 1.4*cm, 1.6*cm]
    it_t = Table(rows, colWidths=col_w, repeatRows=1)
    it_t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), AZUL),
        ("TEXTCOLOR",   (0,0), (-1,0), BRANCO),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 7),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [BRANCO, CREME]),
        ("GRID",        (0,0), (-1,-1), 0.3, CINZA_CLR),
        ("ALIGN",       (4,0), (-1,-1), "CENTER"),
        ("PADDING",     (0,0), (-1,-1), 4),
        ("FONTNAME",    (-1,1), (-1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (-1,1), (-1,-1), AZUL),
    ]))
    story.append(it_t)

    # ── Totais ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    tot_data = [
        ["Total de peças", str(pedido.total_pecas), "Valor bruto", f"R$ {pedido.valor_bruto:.2f}", "Valor líquido", f"R$ {pedido.valor_liquido:.2f}"],
        [f"Desconto ({pedido.desconto:.1f}%)", f"- R$ {pedido.valor_bruto - pedido.valor_liquido:.2f}", "Entrada paga", f"R$ {pedido.entrada:.2f}", "Saldo a pagar", f"R$ {pedido.saldo:.2f}"],
    ]
    tt = Table(tot_data, colWidths=[3*cm, 2.8*cm, 3*cm, 2.8*cm, 3*cm, 2.8*cm])
    tt.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",   (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("BACKGROUND", (0,0), (-1,-1), BRANCO),
        ("GRID",       (0,0), (-1,-1), 0.4, CINZA_CLR),
        ("PADDING",    (0,0), (-1,-1), 6),
        ("FONTNAME",   (3,2), (3,2), "Helvetica-Bold"),
        ("TEXTCOLOR",  (3,2), (3,2), AZUL),
        ("FONTSIZE",   (3,2), (3,2), 10),
    ]))
    story.append(tt)

    # ── Pagamento / Entrega ───────────────────────────────────────────────────
    story.append(Paragraph("PAGAMENTO E ENTREGA", s_sec))
    pg_data = [
        ["Forma de pagamento", pedido.forma_pgto or "—",
         "Prazo", pedido.prazo_pgto or "—"],
        ["Tipo de entrega", pedido.tipo_entrega or "—",
         "Prev. entrega", pedido.dt_entrega or "—"],
    ]
    if pedido.obs_entrega or pedido.obs_pgto:
        pg_data.append(["Obs. entrega", pedido.obs_entrega or "—",
                         "Obs. pgto", pedido.obs_pgto or "—"])
    pgt = Table(pg_data, colWidths=[3.2*cm, 6*cm, 2.8*cm, 5.2*cm])
    pgt.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",   (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("TEXTCOLOR",  (0,0), (0,-1), CINZA_MED),
        ("TEXTCOLOR",  (2,0), (2,-1), CINZA_MED),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [CREME, BRANCO]),
        ("GRID",       (0,0), (-1,-1), 0.4, CINZA_CLR),
        ("PADDING",    (0,0), (-1,-1), 6),
    ]))
    story.append(pgt)

    if pedido.obs_geral:
        story.append(Paragraph("OBSERVAÇÕES GERAIS", s_sec))
        story.append(Paragraph(pedido.obs_geral, s_normal))

    # ── Rodapé ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.2*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CINZA_CLR))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"{empresa}  ·  {cfg.get('empresa_tel','')}  ·  {cfg.get('empresa_email','')}",
        s_footer))
    from datetime import datetime
    story.append(Paragraph(
        f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        s_footer))

    doc.build(story)
