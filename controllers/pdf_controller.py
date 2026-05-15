"""
controllers/pdf_controller.py — Geração de PDF profissional
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table,
                                 TableStyle, Spacer, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from models.pedido_model import Pedido, TAMANHOS, _SZ_COLS
from models import config_model

_AZUL      = colors.HexColor("#1F4E79")
_AZUL_ESC  = colors.HexColor("#16324F")
_CINZA     = colors.HexColor("#888780")
_CINZA_CLR = colors.HexColor("#D6DEE6")
_BRANCO    = colors.white

def _ps(name, **kw): return ParagraphStyle(name, **kw)


def gerar(pedido: Pedido, path: str):
    cfg     = config_model.get_all()
    empresa = cfg.get("empresa_nome","Empresa")
    doc     = SimpleDocTemplate(path, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm,
                                title=f"Pedido {pedido.numero}", author=empresa)
    s_sec    = _ps("sec", fontName="Helvetica-Bold", fontSize=10,
                   textColor=_AZUL, spaceBefore=14, spaceAfter=5)
    s_normal = _ps("n",   fontName="Helvetica", fontSize=8, leading=14)
    s_footer = _ps("f",   fontName="Helvetica", fontSize=7.5,
                   textColor=_CINZA, alignment=TA_CENTER)
    story = []

    # Cabeçalho
    hd = Table([[
        Paragraph(f"<b>{empresa}</b>",
                  _ps("h", fontName="Helvetica-Bold", fontSize=14, textColor=_AZUL)),
        Paragraph(f"<font color='#888780'>Pedido</font> <b>{pedido.numero}</b><br/>"
                  f"<font color='#888780'>Emitido: {pedido.dt_pedido or '—'}</font>"
                  f"{'<br/><font color=\"#888780\">Vendedor: </font>' + pedido.vendedor if pedido.vendedor else ''}",
                  _ps("hr", fontName="Helvetica", fontSize=9,
                      textColor=_AZUL_ESC, alignment=TA_RIGHT)),
    ]], colWidths=[10*cm,7*cm])
    hd.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                             ("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    story.append(hd)

    sc = {"Rascunho":"#888780","Confirmado":"#185FA5","Em produção":"#854F0B",
          "Pronto":"#3B6D11","Entregue":"#0F6E56","Cancelado":"#A32D2D"}
    story.append(Paragraph(
        f'<font color="{sc.get(pedido.status,"#888780")}">● {pedido.status}</font>',
        _ps("st", fontName="Helvetica-Bold", fontSize=9, spaceAfter=4)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_AZUL, spaceAfter=12))

    # Cliente
    story.append(Paragraph("DADOS DO CLIENTE", s_sec))
    ct = Table([
        ["Nome / Razão Social", pedido.cliente_nome or "—",
         "Cidade / UF", pedido.cliente_cidade or "—"],
        ["Telefone", pedido.cliente_tel or "—",
         "E-mail", pedido.cliente_email or "—"],
    ], colWidths=[3.5*cm,6*cm,2.8*cm,5.2*cm])
    ct.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
        ("FONTNAME",(1,0),(1,-1),"Helvetica"),
        ("FONTNAME",(3,0),(3,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#EDF5FC"),_BRANCO]),
        ("GRID",(0,0),(-1,-1),0.4,_CINZA_CLR),("PADDING",(0,0),(-1,-1),6),
    ]))
    story.append(ct)

    # Itens
    story.append(Paragraph("ITENS DO PEDIDO", s_sec))
    rows = [["Ref.","Descrição","Cor"]+TAMANHOS+["Total","Unit.","Subtotal"]]
    for it in pedido.itens:
        qtds = [getattr(it,c) for c in _SZ_COLS]
        rows.append([it.referencia,it.descricao,it.cor,
                     *[str(q) if q else "·" for q in qtds],
                     str(it.total_pcs),f"R${it.preco_unitario:.2f}",f"R${it.subtotal:.2f}"])
    col_w = [1.2*cm,3.5*cm,2.8*cm]+[0.8*cm]*7+[1.1*cm,1.4*cm,1.6*cm]
    it_t = Table(rows, colWidths=col_w, repeatRows=1)
    it_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),_AZUL),("TEXTCOLOR",(0,0),(-1,0),_BRANCO),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),7),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[_BRANCO,colors.HexColor("#EDF5FC")]),
        ("GRID",(0,0),(-1,-1),0.3,_CINZA_CLR),("ALIGN",(3,0),(-1,-1),"CENTER"),
        ("PADDING",(0,0),(-1,-1),4),
        ("FONTNAME",(-1,1),(-1,-1),"Helvetica-Bold"),
        ("TEXTCOLOR",(-1,1),(-1,-1),_AZUL),
    ]))
    story.append(it_t)

    # Totais + Pagamento
    story.append(Spacer(1,0.4*cm))
    story.append(Paragraph("DADOS DO PEDIDO E PAGAMENTO", s_sec))
    tot = Table([
        ["Total de peças",str(pedido.total_pecas),"Valor bruto",f"R$ {pedido.valor_bruto:.2f}",
         "Forma de pagamento",pedido.forma_pgto or "—"],
        [f"Desconto",f"{pedido.desconto:.1f}%","Valor líquido",f"R$ {pedido.valor_liquido:.2f}",
         "Prazo",pedido.prazo_pgto or "—"],
        ["OBS:",str(pedido.obs_geral or ""),"","","",""],
    ], colWidths=[3*cm,2.2*cm,2.8*cm,2.2*cm,3.5*cm,3.8*cm])
    tot.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
        ("FONTNAME",(4,0),(4,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("GRID",(0,0),(-1,-1),0.4,_CINZA_CLR),
        ("PADDING",(0,0),(-1,-1),6),
        ("SPAN",(1,2),(5,2)),
    ]))
    story.append(tot)

    # Entrega
    story.append(Paragraph("ENTREGA", s_sec))
    pg = [["Tipo de entrega",pedido.tipo_entrega or "—","Prev. entrega",pedido.dt_entrega or "—"]]
    if pedido.obs_entrega:
        pg.append(["Obs. entrega",pedido.obs_entrega,"",""])
    pgt = Table(pg, colWidths=[3.5*cm,5*cm,3*cm,5*cm])
    pgt.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#EDF5FC"),_BRANCO]),
        ("GRID",(0,0),(-1,-1),0.4,_CINZA_CLR),("PADDING",(0,0),(-1,-1),6),
    ]))
    story.append(pgt)

    story.append(Spacer(1,1.2*cm))
    story.append(HRFlowable(width="100%",thickness=0.5,color=_CINZA_CLR))
    story.append(Spacer(1,0.3*cm))
    from datetime import datetime
    story.append(Paragraph(
        f"{empresa}  ·  {cfg.get('empresa_tel','')}  ·  {cfg.get('empresa_email','')}",
        s_footer))
    story.append(Paragraph(
        f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        s_footer))
    doc.build(story)