from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_client, name='create_client'),
    path('client/<str:client_name>/', views.client_detail, name='client_detail'),
    path('client/<str:client_name>/start/', views.start_client, name='start_client'),
    path('client/<str:client_name>/stop/', views.stop_client, name='stop_client'),
    path('client/<str:client_name>/delete/', views.delete_client, name='delete_client'),
]
