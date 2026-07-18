from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Zone, Equipement
from .forms import ZoneForm, EquipementForm


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
def core_settings(request):
    zones = Zone.objects.all().order_by('nom')
    equipements = Equipement.objects.all().order_by('nom')
    return render(request, 'core/settings.html', {'zones': zones, 'equipements': equipements})


@login_required
@superviseur_required
def zone_create(request):
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Zone ajoutée.")
            return redirect('core:settings')
    else:
        form = ZoneForm()
    return render(request, 'core/simple_form.html', {'form': form, 'titre': 'Ajouter une zone'})


@login_required
@superviseur_required
def zone_edit(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    if request.method == 'POST':
        form = ZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save()
            messages.success(request, "Zone modifiée.")
            return redirect('core:settings')
    else:
        form = ZoneForm(instance=zone)
    return render(request, 'core/simple_form.html', {'form': form, 'titre': f'Modifier {zone.nom}'})


@login_required
@superviseur_required
def zone_delete(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    if request.method == 'POST':
        zone.delete()
        messages.success(request, "Zone supprimée.")
        return redirect('core:settings')
    return render(request, 'core/confirm_delete.html', {'objet': zone})


@login_required
@superviseur_required
def equipement_create(request):
    if request.method == 'POST':
        form = EquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipement ajouté.")
            return redirect('core:settings')
    else:
        form = EquipementForm()
    return render(request, 'core/simple_form.html', {'form': form, 'titre': 'Ajouter un équipement'})


@login_required
@superviseur_required
def equipement_edit(request, pk):
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        form = EquipementForm(request.POST, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipement modifié.")
            return redirect('core:settings')
    else:
        form = EquipementForm(instance=equipement)
    return render(request, 'core/simple_form.html', {'form': form, 'titre': f'Modifier {equipement.nom}'})


@login_required
@superviseur_required
def equipement_delete(request, pk):
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        equipement.delete()
        messages.success(request, "Équipement supprimé.")
        return redirect('core:settings')
    return render(request, 'core/confirm_delete.html', {'objet': equipement})