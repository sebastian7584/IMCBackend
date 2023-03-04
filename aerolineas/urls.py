from django.urls import path
from .views import  adminAerolineaView


urlpatterns = [
    path('admin', adminAerolineaView),
  
]
