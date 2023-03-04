from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/equipos/', include('equipos.urls')),
    path('api/formularios/', include('formularios.urls')),
    path('api/bases/', include('bases.urls')),
    path('api/aerolineas/', include('aerolineas.urls')),
]
