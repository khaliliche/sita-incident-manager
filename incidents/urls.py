from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('nouveau/', views.ticket_create, name='ticket_create'),
    path('dashboard/', views.dashboard_superviseur, name='dashboard'),
    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('<int:pk>/resoudre/', views.ticket_resoudre, name='ticket_resoudre'),
    path('<int:pk>/escalader/', views.ticket_escalader, name='ticket_escalader'),
    path('<int:pk>/cloturer/', views.ticket_cloturer, name='ticket_cloturer'),
    path('<int:pk>/reaffecter/', views.ticket_reaffecter, name='ticket_reaffecter'),
]