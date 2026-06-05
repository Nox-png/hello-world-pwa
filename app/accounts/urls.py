from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login', views.loginView, name='loginView'),
    path('logout', views.logoutView, name='logoutView'),
    ]