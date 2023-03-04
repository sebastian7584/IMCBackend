from django.urls import path
from .views import  adminUserView, loginView, userView, logoutView, resetPasswordView, newPasswordView


urlpatterns = [
    path('admin', adminUserView),
    path('login', loginView),
    path('check', userView),
    path('logout', logoutView),
    path('reset', resetPasswordView),
    path('changePassword', newPasswordView),
]
