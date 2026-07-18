from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.core_settings, name='settings'),
    path('zones/nouvelle/', views.zone_create, name='zone_create'),
    path('zones/<int:pk>/modifier/', views.zone_edit, name='zone_edit'),
    path('zones/<int:pk>/supprimer/', views.zone_delete, name='zone_delete'),
    path('equipements/nouveau/', views.equipement_create, name='equipement_create'),
    path('equipements/<int:pk>/modifier/', views.equipement_edit, name='equipement_edit'),
    path('equipements/<int:pk>/supprimer/', views.equipement_delete, name='equipement_delete'),
]