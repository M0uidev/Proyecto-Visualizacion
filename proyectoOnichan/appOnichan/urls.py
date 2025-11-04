from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    path('iniciosesiontrabajador/', views.login_trabajador_view, name='iniciosesiontrabajador'),
    path('dashboardtrabajador/', views.dashboard_trabajador_view, name='dashboard_trabajador'),
    path('pagina3/', views.pagina3, name='pagina3'),
]
