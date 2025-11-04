from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    path('iniciosesiontrabajador/', views.iniciosesiontrabajador, name='iniciosesiontrabajador'),
    path('dashboardtrabajador/', views.dashboardtrabajador, name='dashboardtrabajador'),
    path('pagina3/', views.pagina3, name='pagina3'),
]
