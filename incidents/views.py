from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, TicketHistorique
from .forms import TicketForm, ReaffectationForm
from accounts.models import Utilisateur
from core.models import Zone


@login_required
def ticket_list(request):
    user = request.user
    if user.role == 'helpdesk':
        tickets = Ticket.objects.all().order_by('-date_creation')
    elif user.role in ['technicien', 'ingenieur']:
        tickets = Ticket.objects.filter(assigne_a=user).order_by('-date_creation')
    elif user.role == 'superviseur':
        tickets = Ticket.objects.all().order_by('-date_creation')
    else:
        tickets = Ticket.objects.none()

    statut = request.GET.get('statut', '')
    priorite = request.GET.get('priorite', '')
    zone_id = request.GET.get('zone', '')
    q = request.GET.get('q', '').strip()

    if statut:
        tickets = tickets.filter(statut=statut)
    if priorite:
        tickets = tickets.filter(priorite=priorite)
    if zone_id:
        tickets = tickets.filter(zone_id=zone_id)
    if q:
        from django.db.models import Q
        tickets = tickets.filter(
            Q(numero_vol__icontains=q) | Q(compagnie_aerienne__icontains=q)
        )

    context = {
        'tickets': tickets,
        'zones': Zone.objects.all().order_by('nom'),
        'statut_choices': Ticket.STATUT_CHOICES,
        'priorite_choices': Ticket.PRIORITE_CHOICES,
        'filtre_statut': statut,
        'filtre_priorite': priorite,
        'filtre_zone': zone_id,
        'filtre_q': q,
    }
    return render(request, 'incidents/ticket_list.html', context)


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    historique = ticket.historique.all() if request.user.role == 'superviseur' else None
    return render(request, 'incidents/ticket_detail.html', {
        'ticket': ticket,
        'historique': historique,
    })


def affecter_agent(ticket):
    """Trouve un agent disponible dans la zone du ticket, selon la priorité."""
    if ticket.priorite in ['P1', 'P2']:
        role_cible = 'ingenieur'
    else:
        role_cible = 'technicien'

    agent = Utilisateur.objects.filter(
        role=role_cible,
        zone=ticket.zone,
        disponibilite='disponible'
    ).first()

    if agent:
        agent.disponibilite = 'occupe'
        agent.save()

    return agent


@login_required
def ticket_create(request):
    if request.user.role != 'helpdesk':
        messages.error(request, "Seul un agent Helpdesk peut créer un ticket.")
        return redirect('incidents:ticket_list')

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.cree_par = request.user

            agent = affecter_agent(ticket)
            if agent:
                ticket.assigne_a = agent
                ticket.statut = 'affecte'
            else:
                ticket.statut = 'ouvert'

            ticket.save()

            TicketHistorique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action='Création du ticket',
                ancien_statut='',
                nouveau_statut=ticket.statut,
                commentaire=f"Affecté à {agent}" if agent else "Aucun agent disponible dans la zone"
            )

            if agent:
                messages.success(request, f"Ticket créé et affecté à {agent}.")
            else:
                messages.warning(request, "Ticket créé mais aucun agent disponible dans cette zone.")

            return redirect('incidents:ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()

    return render(request, 'incidents/ticket_form.html', {'form': form})


@login_required
def ticket_resoudre(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.assigne_a != request.user:
        messages.error(request, "Ce ticket ne vous est pas assigné.")
        return redirect('incidents:ticket_list')

    ancien_statut = ticket.statut
    ticket.statut = 'resolu'
    ticket.save()

    request.user.disponibilite = 'disponible'
    request.user.save()

    TicketHistorique.objects.create(
        ticket=ticket,
        utilisateur=request.user,
        action='Résolution',
        ancien_statut=ancien_statut,
        nouveau_statut='resolu',
        commentaire='Marqué comme résolu par ' + str(request.user)
    )
    messages.success(request, "Ticket marqué comme résolu.")
    return redirect('incidents:ticket_detail', pk=ticket.pk)


@login_required
def ticket_escalader(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.assigne_a != request.user or request.user.role != 'technicien':
        messages.error(request, "Action non autorisée.")
        return redirect('incidents:ticket_list')

    ancien_statut = ticket.statut

    request.user.disponibilite = 'disponible'
    request.user.save()

    ticket.statut = 'escalade'
    ticket.assigne_a = None
    ticket.save()

    TicketHistorique.objects.create(
        ticket=ticket,
        utilisateur=request.user,
        action='Escalade',
        ancien_statut=ancien_statut,
        nouveau_statut='escalade',
        commentaire=f"Signalé par {request.user} — en attente de réaffectation par le Helpdesk"
    )
    messages.warning(request, "Ticket escaladé. En attente de réaffectation par le Helpdesk.")
    return redirect('incidents:ticket_detail', pk=ticket.pk)


@login_required
def ticket_reaffecter(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.role != 'helpdesk':
        messages.error(request, "Seul le Helpdesk peut réaffecter un ticket.")
        return redirect('incidents:ticket_list')

    if ticket.statut != 'escalade':
        messages.error(request, "Ce ticket n'est pas en attente de réaffectation.")
        return redirect('incidents:ticket_detail', pk=ticket.pk)

    if request.method == 'POST':
        form = ReaffectationForm(request.POST, zone=ticket.zone)
        if form.is_valid():
            ingenieur = form.cleaned_data['ingenieur']
            ancien_statut = ticket.statut

            ticket.assigne_a = ingenieur
            ticket.statut = 'affecte'
            ticket.save()

            ingenieur.disponibilite = 'occupe'
            ingenieur.save()

            TicketHistorique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action='Réaffectation',
                ancien_statut=ancien_statut,
                nouveau_statut='affecte',
                commentaire=f"Réaffecté par {request.user} vers {ingenieur}"
            )
            messages.success(request, f"Ticket réaffecté à {ingenieur}.")
            return redirect('incidents:ticket_detail', pk=ticket.pk)
    else:
        form = ReaffectationForm(zone=ticket.zone)

    return render(request, 'incidents/ticket_reaffecter.html', {'form': form, 'ticket': ticket})


@login_required
def ticket_cloturer(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.role != 'helpdesk':
        messages.error(request, "Seul le Helpdesk peut clôturer un ticket.")
        return redirect('incidents:ticket_list')

    if request.method == 'POST':
        commentaire = request.POST.get('commentaire', '')
        ancien_statut = ticket.statut
        ticket.statut = 'cloture'
        ticket.commentaire_cloture = commentaire
        from django.utils import timezone
        ticket.date_cloture = timezone.now()
        ticket.save()

        TicketHistorique.objects.create(
            ticket=ticket,
            utilisateur=request.user,
            action='Clôture',
            ancien_statut=ancien_statut,
            nouveau_statut='cloture',
            commentaire=commentaire
        )
        messages.success(request, "Ticket clôturé.")
        return redirect('incidents:ticket_detail', pk=ticket.pk)

    return render(request, 'incidents/ticket_cloture_form.html', {'ticket': ticket})


from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField


@login_required
def dashboard_superviseur(request):
    if request.user.role != 'superviseur':
        messages.error(request, "Accès réservé au superviseur.")
        return redirect('incidents:ticket_list')

    tickets = Ticket.objects.all()

    total = tickets.count()
    par_statut = tickets.values('statut').annotate(total=Count('id'))
    par_zone = tickets.values('zone__nom').annotate(total=Count('id'))
    par_priorite = tickets.values('priorite').annotate(total=Count('id'))

    tickets_resolus = tickets.filter(statut='cloture', date_cloture__isnull=False)
    duree_moyenne = tickets_resolus.annotate(
        duree=ExpressionWrapper(F('date_cloture') - F('date_creation'), output_field=DurationField())
    ).aggregate(moyenne=Avg('duree'))['moyenne']

    return render(request, 'incidents/dashboard.html', {
        'total': total,
        'par_statut': par_statut,
        'par_zone': par_zone,
        'par_priorite': par_priorite,
        'duree_moyenne': duree_moyenne,
        'tickets_recents': tickets.order_by('-date_creation')[:10],
    })
from django.http import HttpResponse


@login_required
def dashboard_export_excel(request):
    if request.user.role != 'superviseur':
        messages.error(request, "Accès réservé au superviseur.")
        return redirect('incidents:ticket_list')

    import openpyxl
    from openpyxl.styles import Font, PatternFill

    tickets = Ticket.objects.all()
    par_statut = tickets.values('statut').annotate(total=Count('id'))
    par_zone = tickets.values('zone__nom').annotate(total=Count('id'))
    par_priorite = tickets.values('priorite').annotate(total=Count('id'))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rapport ITmanager"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")

    ws.append(["Rapport superviseur - ITmanager"])
    ws.append([f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}"])
    ws.append([])
    ws.append([f"Total tickets : {tickets.count()}"])
    ws.append([])

    ws.append(["Par statut"])
    ws.append(["Statut", "Total"])
    for row in ws.iter_rows(min_row=ws.max_row, max_row=ws.max_row):
        for cell in row:
            cell.font = header_font
            cell.fill = header_fill
    for s in par_statut:
        ws.append([s['statut'], s['total']])

    ws.append([])
    ws.append(["Par zone"])
    ws.append(["Zone", "Total"])
    for row in ws.iter_rows(min_row=ws.max_row, max_row=ws.max_row):
        for cell in row:
            cell.font = header_font
            cell.fill = header_fill
    for z in par_zone:
        ws.append([z['zone__nom'] or '-', z['total']])

    ws.append([])
    ws.append(["Par priorité"])
    ws.append(["Priorité", "Total"])
    for row in ws.iter_rows(min_row=ws.max_row, max_row=ws.max_row):
        for cell in row:
            cell.font = header_font
            cell.fill = header_fill
    for p in par_priorite:
        ws.append([p['priorite'], p['total']])

    for col in ws.columns:
        max_len = max(len(str(c.value)) for c in col if c.value) if any(c.value for c in col) else 10
        ws.column_dimensions[col[0].column_letter].width = max_len + 4

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="rapport_itmanager_{timezone.now().strftime("%Y%m%d")}.xlsx"'
    wb.save(response)
    return response


@login_required
def dashboard_export_pdf(request):
    if request.user.role != 'superviseur':
        messages.error(request, "Accès réservé au superviseur.")
        return redirect('incidents:ticket_list')

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import io

    tickets = Ticket.objects.all()
    par_statut = tickets.values('statut').annotate(total=Count('id'))
    par_zone = tickets.values('zone__nom').annotate(total=Count('id'))
    par_priorite = tickets.values('priorite').annotate(total=Count('id'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Rapport superviseur - ITmanager", styles['Title']))
    elements.append(Paragraph(f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"<b>Total tickets :</b> {tickets.count()}", styles['Normal']))
    elements.append(Spacer(1, 0.7*cm))

    def make_table(title, rows, headers):
        elements.append(Paragraph(title, styles['Heading2']))
        data = [headers] + rows
        t = Table(data, colWidths=[9*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E5EA')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F8FA')]),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.6*cm))

    make_table("Par statut", [[s['statut'], str(s['total'])] for s in par_statut], ["Statut", "Total"])
    make_table("Par zone", [[z['zone__nom'] or '-', str(z['total'])] for z in par_zone], ["Zone", "Total"])
    make_table("Par priorité", [[p['priorite'], str(p['total'])] for p in par_priorite], ["Priorité", "Total"])

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_itmanager_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response