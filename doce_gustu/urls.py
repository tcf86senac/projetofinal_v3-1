"""
URL configuration for doce_gustu project.
"""
from django.contrib import admin
from django.urls import path, include

# Importe a view de login da sua aplicação
from doce_gustu_app.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('doce_gustu_app.urls')),
    
    # URL de login que usa a sua view personalizada
    path('login/', login_view, name='login'),
]