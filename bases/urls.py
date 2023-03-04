from django.urls import path
from .views import  adminBaseView


urlpatterns = [
    path('admin', adminBaseView),
  
]
