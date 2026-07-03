import io
import base64
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Demande.models import DCL
from Client.decorators import role_required
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def _build_pdf(demande):
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
    ORANGE = colors.HexColor('#FF6B00')
    LIGHT_GREY = colors.HexColor('#F8FAFC')
    MID_GREY = colors.HexColor('#64748B')
    DARK = colors.HexColor('#1E293B')
    SUCCESS = colors.HexColor('#16A34A')

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle('title', fontSize=22, fontName='Helvetica-Bold', textColor=PRIMARY, spaceAfter=2)
    style_subtitle = ParagraphStyle('subtitle', fontSize=10, fontName='Helvetica', textColor=MID_GREY, spaceAfter=0)
    style_section = ParagraphStyle('section', fontSize=11, fontName='Helvetica-Bold', textColor=PRIMARY, spaceBefore=8, spaceAfter=4)
    style_label = ParagraphStyle('label', fontSize=8, fontName='Helvetica', textColor=MID_GREY)
    style_value = ParagraphStyle('value', fontSize=10, fontName='Helvetica-Bold', textColor=DARK)
    style_small = ParagraphStyle('small', fontSize=8, fontName='Helvetica', textColor=MID_GREY)
    style_center = ParagraphStyle('center', fontSize=9, fontName='Helvetica', textColor=MID_GREY, alignment=TA_CENTER)
    style_ref = ParagraphStyle('ref', fontSize=14, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
    style_amount = ParagraphStyle('amount', fontSize=20, fontName='Helvetica-Bold', textColor=SUCCESS, alignment=TA_CENTER)

    story = []

    # ─── Header ──────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph('<b>MonLivreurPro</b>', ParagraphStyle('logo', fontSize=18, fontName='Helvetica-Bold', textColor=colors.white)),
        Paragraph(f'Reçu de livraison<br/><font size="9">{demande.ref}</font>', ParagraphStyle('rh', fontSize=12, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_RIGHT)),
    ]]
    header_table = Table(header_data, colWidths=['60%', '40%'])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [PRIMARY]),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6 * mm))

    # ─── Status pill ─────────────────────────────────────────────────────────
    status_data = [[
        Paragraph('✓ LIVRAISON CONFIRMÉE', ParagraphStyle('sp', fontSize=11, fontName='Helvetica-Bold', textColor=SUCCESS, alignment=TA_CENTER)),
    ]]
    status_table = Table(status_data, colWidths=['100%'])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0FDF4')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#22C55E')),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 5 * mm))

    # ─── Dates ───────────────────────────────────────────────────────────────
    date_liv = demande.date_livraison.strftime('%d/%m/%Y à %H:%M') if demande.date_livraison else '–'
    date_dem = demande.date_demande.strftime('%d/%m/%Y à %H:%M')
    dates_data = [
        [Paragraph('Date de la demande', style_label), Paragraph('Date de livraison')],
        [Paragraph(date_dem, style_value), Paragraph(date_liv, ParagraphStyle('dv', fontSize=10, fontName='Helvetica-Bold', textColor=SUCCESS))],
    ]
    dates_table = Table(dates_data, colWidths=['50%', '50%'])
    dates_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(dates_table)
    story.append(Spacer(1, 5 * mm))

    def section_table(title, rows):
        """rows: list of (label, value) tuples"""
        story.append(Paragraph(title, style_section))
        tdata = [[Paragraph(lbl, style_label), Paragraph(str(val) if val else '–', style_value)] for lbl, val in rows]
        t = Table(tdata, colWidths=['35%', '65%'])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GREY),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        story.append(t)

    # ─── Client ──────────────────────────────────────────────────────────────
    if demande.client:
        client_name = f"{demande.client.first_name} {demande.client.last_name}".strip() or demande.client.username
        client_phone = demande.client.Contact
        client_email = demande.client.email
    elif demande.client_invite:
        client_name = f"{demande.client_invite.prenom} {demande.client_invite.nom}"
        client_phone = demande.client_invite.telephone
        client_email = demande.client_invite.email or '–'
    else:
        client_name = 'Inconnu'
        client_phone = '–'
        client_email = '–'

    section_table('Client expéditeur', [
        ('Nom complet', client_name),
        ('Téléphone', client_phone),
        ('Email', client_email),
    ])
    story.append(Spacer(1, 3 * mm))

    # ─── Destinataire ────────────────────────────────────────────────────────
    section_table('Destinataire', [
        ('Contact', demande.Contact_destinateur or '–'),
        ('Adresse de livraison', demande.adresse_destination),
    ])
    story.append(Spacer(1, 3 * mm))

    # ─── Itinéraire ──────────────────────────────────────────────────────────
    section_table('Itinéraire', [
        ('Adresse de départ', demande.adresse_depart),
        ('Adresse de destination', demande.adresse_destination),
        ('Distance', f"{demande.distance} km" if demande.distance else '–'),
    ])
    story.append(Spacer(1, 3 * mm))

    # ─── Livreur ─────────────────────────────────────────────────────────────
    if demande.coursier:
        livreur_name = f"{demande.coursier.first_name} {demande.coursier.last_name}".strip() or demande.coursier.username
        section_table('Livreur', [
            ('Nom complet', livreur_name),
            ('Téléphone', demande.coursier.Contact),
        ])
        story.append(Spacer(1, 3 * mm))

    # ─── Colis ───────────────────────────────────────────────────────────────
    section_table('Colis', [
        ('Description', demande.description_colis),
        ('Poids', f"{demande.poids_colis} {demande.unite_poids}"),
        ('Type de course', demande.get_type_course_display()),
        ('Date de récupération', demande.date_recuperation.strftime('%d/%m/%Y à %H:%M')),
    ])
    story.append(Spacer(1, 3 * mm))

    # ─── Montant ─────────────────────────────────────────────────────────────
    if demande.cout_livraison:
        story.append(Paragraph('Montant de la livraison', style_section))
        amount_data = [[Paragraph(f'{demande.cout_livraison} FCFA', style_amount)]]
        amount_table = Table(amount_data, colWidths=['100%'])
        amount_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0FDF4')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#22C55E')),
        ]))
        story.append(amount_table)
        story.append(Spacer(1, 4 * mm))

    # ─── Signature ───────────────────────────────────────────────────────────
    if demande.signature_destinataire:
        story.append(Paragraph('Signature du destinataire', style_section))
        try:
            sig_data = demande.signature_destinataire
            if ',' in sig_data:
                sig_data = sig_data.split(',', 1)[1]
            sig_bytes = base64.b64decode(sig_data)
            sig_buf = io.BytesIO(sig_bytes)
            sig_img = RLImage(sig_buf, width=100 * mm, height=35 * mm)
            sig_table = Table([[sig_img]], colWidths=['100%'])
            sig_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#C4B5FD')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(sig_table)
        except Exception:
            story.append(Paragraph('Signature enregistrée électroniquement.', style_small))
        story.append(Spacer(1, 3 * mm))

    # ─── Footer ──────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#E2E8F0')))
    story.append(Spacer(1, 3 * mm))
    generated_at = timezone.now().strftime('%d/%m/%Y à %H:%M')
    story.append(Paragraph(
        f'Reçu généré automatiquement le {generated_at} · MonLivreurPro',
        style_center,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


@login_required
@role_required("client")
def recu_pdf(request, pk):
    """Génère et retourne le reçu PDF d'une livraison terminée."""
    demande = get_object_or_404(DCL, id=pk, client=request.user)

    if demande.statut != 'TERMINEE':
        raise Http404("Le reçu n'est disponible qu'après la livraison.")

    buffer = _build_pdf(demande)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recu-{demande.ref}.pdf"'
    return response
