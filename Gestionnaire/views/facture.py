import io

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Demande.models import DCL
from Client.decorators import role_required
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Informations légales de l'émetteur — voir templates/layouts/base_site.html pour les coordonnées publiques
EMETTEUR = {
    'nom': 'Mon Livreur Pro',
    'adresse': "Cité AGD, Modeste, Grand-Bassam, Côte d'Ivoire",
    'telephone': '+225 01 50 20 05 09',
    'email': 'infos@mon-livreur-pro.com',
    'rccm': 'CI-ABJ-03-2023-B12-06135',
    'cc': '2304865G',
}


def _build_facture_pdf(demande):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    PRIMARY = colors.HexColor('#000080')
    LIGHT_GREY = colors.HexColor('#F8FAFC')
    MID_GREY = colors.HexColor('#64748B')
    DARK = colors.HexColor('#1E293B')
    SUCCESS = colors.HexColor('#16A34A')

    style_label = ParagraphStyle('label', fontSize=8, fontName='Helvetica', textColor=MID_GREY)
    style_value = ParagraphStyle('value', fontSize=10, fontName='Helvetica-Bold', textColor=DARK)
    style_small = ParagraphStyle('small', fontSize=8, fontName='Helvetica', textColor=MID_GREY)
    style_center = ParagraphStyle('center', fontSize=8, fontName='Helvetica', textColor=MID_GREY, alignment=TA_CENTER)
    style_section = ParagraphStyle('section', fontSize=11, fontName='Helvetica-Bold', textColor=PRIMARY, spaceBefore=8, spaceAfter=4)

    story = []

    # ─── Header ──────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            f"<b>{EMETTEUR['nom']}</b><br/><font size=8>{EMETTEUR['adresse']}</font>"
            f"<br/><font size=8>Tél: {EMETTEUR['telephone']} · {EMETTEUR['email']}</font>",
            ParagraphStyle('logo', fontSize=15, fontName='Helvetica-Bold', textColor=colors.white, leading=13),
        ),
        Paragraph(
            f"FACTURE<br/><font size=11>{demande.numero_facture}</font>",
            ParagraphStyle('rh', fontSize=16, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_RIGHT),
        ),
    ]]
    header_table = Table(header_data, colWidths=['62%', '38%'])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 3 * mm))

    # ─── Mentions légales de l'émetteur ─────────────────────────────────────
    story.append(Paragraph(
        f"RCCM : {EMETTEUR['rccm']} · Compte Contribuable (CC) : {EMETTEUR['cc']}",
        style_small,
    ))
    story.append(Spacer(1, 5 * mm))

    # ─── Facture / Référence / Date ─────────────────────────────────────────
    date_facture = demande.date_facture.strftime('%d/%m/%Y à %H:%M') if demande.date_facture else '–'
    info_data = [
        [Paragraph('N° de facture', style_label), Paragraph('Date de facturation', style_label), Paragraph('Référence course', style_label)],
        [Paragraph(demande.numero_facture, style_value), Paragraph(date_facture, style_value), Paragraph(demande.ref, style_value)],
    ]
    info_table = Table(info_data, colWidths=['33%', '34%', '33%'])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEAFTER', (1, 0), (1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 5 * mm))

    # ─── Facturé à ───────────────────────────────────────────────────────────
    if demande.client:
        client_name = f"{demande.client.first_name} {demande.client.last_name}".strip() or demande.client.username
        client_phone = demande.client.Contact
        client_email = demande.client.email
    elif demande.client_invite:
        client_name = f"{demande.client_invite.prenom} {demande.client_invite.nom}"
        client_phone = demande.client_invite.telephone
        client_email = demande.client_invite.email or '–'
    else:
        client_name, client_phone, client_email = 'Inconnu', '–', '–'

    story.append(Paragraph('Facturé à', style_section))
    client_data = [
        [Paragraph('Nom', style_label), Paragraph(client_name, style_value)],
        [Paragraph('Téléphone', style_label), Paragraph(client_phone or '–', style_value)],
        [Paragraph('Email', style_label), Paragraph(client_email or '–', style_value)],
    ]
    client_table = Table(client_data, colWidths=['30%', '70%'])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 6 * mm))

    # ─── Prestation ──────────────────────────────────────────────────────────
    story.append(Paragraph('Détail de la prestation', style_section))
    montant = demande.cout_livraison or 0
    designation = (
        f"Prestation de livraison — {demande.get_type_course_display()} — "
        f"{demande.adresse_depart} → {demande.adresse_destination}"
    )
    presta_header = ['Désignation', 'Qté', 'Prix unitaire', 'Montant']
    presta_row = [Paragraph(designation, style_small), '1', f"{montant} FCFA", f"{montant} FCFA"]
    presta_table = Table(
        [presta_header, presta_row],
        colWidths=['52%', '10%', '19%', '19%'],
    )
    presta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(presta_table)
    story.append(Spacer(1, 5 * mm))

    # ─── Total ───────────────────────────────────────────────────────────────
    total_data = [
        [Paragraph('Total HT', style_label), Paragraph(f"{montant} FCFA", style_value)],
        [Paragraph('TVA', style_label), Paragraph('Non applicable', style_value)],
        [
            Paragraph('Total TTC', ParagraphStyle('ttcl', fontSize=11, fontName='Helvetica-Bold', textColor=PRIMARY)),
            Paragraph(f"{montant} FCFA", ParagraphStyle('ttcv', fontSize=13, fontName='Helvetica-Bold', textColor=SUCCESS, alignment=TA_RIGHT)),
        ],
    ]
    total_table = Table(total_data, colWidths=['70%', '30%'])
    total_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('LINEABOVE', (0, 2), (-1, 2), 0.75, PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 6 * mm))

    # ─── Footer légal ────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#E2E8F0')))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f"{EMETTEUR['nom']} · RCCM {EMETTEUR['rccm']} · CC {EMETTEUR['cc']} · TVA non applicable",
        style_center,
    ))
    generated_at = timezone.now().strftime('%d/%m/%Y à %H:%M')
    story.append(Paragraph(
        f"Facture définitive n° {demande.numero_facture} — générée le {generated_at}",
        style_center,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


@login_required
@role_required("gestionnaire")
def facture_pdf(request, pk):
    """Génère (une seule fois) et retourne la facture PDF définitive dès que le montant est connu."""
    demande = get_object_or_404(DCL, id=pk)

    if demande.cout_livraison is None:
        raise Http404("La facture n'est disponible qu'une fois le montant de la livraison défini.")

    demande.get_or_create_numero_facture()

    buffer = _build_facture_pdf(demande)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{demande.numero_facture}.pdf"'
    return response
