from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utilisateur
from .forms import UtilisateurCreateForm, UtilisateurEditForm
from django.contrib.auth.decorators import login_required as login_required_profil
from incidents.models import Ticket
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField

def superviseur_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'superviseur':
            messages.error(request, "Accès réservé au superviseur.")
            return redirect('incidents:ticket_list')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@superviseur_required
def user_list(request):
    utilisateurs = Utilisateur.objects.all().order_by('role', 'username')
    return render(request, 'accounts/user_list.html', {'utilisateurs': utilisateurs})


@login_required
@superviseur_required
def user_create(request):
    if request.method == 'POST':
        form = UtilisateurCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur créé.")
            return redirect('accounts:user_list')
    else:
        form = UtilisateurCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'mode': 'creation'})


@login_required
@superviseur_required
def user_edit(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = UtilisateurEditForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur modifié.")
            return redirect('accounts:user_list')
    else:
        form = UtilisateurEditForm(instance=utilisateur)
    return render(request, 'accounts/user_form.html', {'form': form, 'mode': 'edition', 'utilisateur': utilisateur})



@login_required_profil
def profil(request):
    user = request.user
    context = {'utilisateur': user}

    if user.role == 'helpdesk':
        tickets_crees = Ticket.objects.filter(cree_par=user)
        context['nb_crees'] = tickets_crees.count()
        context['nb_clotures'] = tickets_crees.filter(statut='cloture').count()

    elif user.role in ['technicien', 'ingenieur']:
        tickets_traites = Ticket.objects.filter(assigne_a=user)
        tickets_resolus = tickets_traites.filter(statut__in=['resolu', 'cloture'])
        context['nb_assignes'] = tickets_traites.count()
        context['nb_resolus'] = tickets_resolus.count()

        duree_moyenne = tickets_traites.filter(
            statut='cloture', date_cloture__isnull=False
        ).annotate(
            duree=ExpressionWrapper(F('date_cloture') - F('date_creation'), output_field=DurationField())
        ).aggregate(moyenne=Avg('duree'))['moyenne']

        if duree_moyenne:
            total_seconds = int(duree_moyenne.total_seconds())
            h, reste = divmod(total_seconds, 3600)
            m, _ = divmod(reste, 60)
            context['duree_moyenne'] = f"{h}h {m}min" if h else f"{m}min"
        else:
            context['duree_moyenne'] = None

    return render(request, 'accounts/profil.html', context)