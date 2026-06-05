from django.contrib import admin
from django.urls import include, path
from accounts.views import logoutView
from accounts.views import loginView
from accounts.views import profileView, profileImageView


app_name = 'accounts'
urlpatterns = [
    path('login', loginView, name='loginView'),
    path('logout', logoutView, name='logoutView'),
    path('profile', profileView, name="profile"),
    path('profile/image', profileImageView, name="profile_image")
    ]