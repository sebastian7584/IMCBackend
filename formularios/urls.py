from django.urls import path
from .views import  adminFormView, openFormView


urlpatterns = [
    path('admin', adminFormView),
    path('open', openFormView),
  
]
