from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utilisateur
from .forms import UtilisateurCreateForm, UtilisateurEditForm


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