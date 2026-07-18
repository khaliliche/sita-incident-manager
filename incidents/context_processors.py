from .models import Ticket


def notifications_badge(request):
    if not request.user.is_authenticated:
        return {}

    role = getattr(request.user, 'role', None)
    count = 0

    if role == 'helpdesk':
        count = Ticket.objects.filter(statut='resolu').count() + Ticket.objects.filter(statut='escalade').count()
    elif role in ['technicien', 'ingenieur']:
        count = Ticket.objects.filter(assigne_a=request.user, statut='affecte').count()
    elif role == 'superviseur':
        count = Ticket.objects.filter(statut='escalade').count()

    return {'notif_count': count}