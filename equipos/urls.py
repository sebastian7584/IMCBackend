from django.urls import path
from .views import adminEquipoView

urlpatterns = [
    path('admin', adminEquipoView)
    
]