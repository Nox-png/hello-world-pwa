from django.urls import path
from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    path('documents/search/', views.document_search, name='document_search'),
    path('mentor/', views.mentor, name='mentor'),
    path("robots.txt", views.robotsTXT),
    path('security.txt', views.securityTXT, name='securityTXT'),
    path('health/', views.health_check, name='health_check'),
    path('offline/', views.offline, name='offline'),
    ]