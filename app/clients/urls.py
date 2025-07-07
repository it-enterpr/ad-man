from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_client, name='create_client'),
    path('client/<int:client_id>/manage/', views.manage_client, name='manage_client'),
    path('client/<int:client_id>/start/', views.start_client, name='start_client'),
    path('client/<int:client_id>/stop/', views.stop_client, name='stop_client'),
    path('client/<int:client_id>/delete/', views.delete_client, name='delete_client'),
    path('update/', views.update_system, name='update_system'),
]
