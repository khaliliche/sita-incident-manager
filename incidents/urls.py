from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('nouveau/', views.ticket_create, name='ticket_create'),
    path('dashboard/', views.dashboard_superviseur, name='dashboard'),
    path('dashboard/export/excel/', views.dashboard_export_excel, name='dashboard_export_excel'),
    path('dashboard/export/pdf/', views.dashboard_export_pdf, name='dashboard_export_pdf'),
    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('<int:pk>/resoudre/', views.ticket_resoudre, name='ticket_resoudre'),
    path('<int:pk>/escalader/', views.ticket_escalader, name='ticket_escalader'),
    path('<int:pk>/reaffecter/', views.ticket_reaffecter, name='ticket_reaffecter'),
    path('<int:pk>/cloturer/', views.ticket_cloturer, name='ticket_cloturer'),
]