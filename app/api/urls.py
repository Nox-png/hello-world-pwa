from django.urls import path
from . import views

from api.modules.status import statusViews

app_name = 'api'
# Basis Pattern
urlpatterns = [
    path('',views.getRoutes, name="getRoutes"),
]

# Pattern für Status
urlpatterns += [
    path('showStatus/',statusViews.showStatus, name="showStatus"),
]