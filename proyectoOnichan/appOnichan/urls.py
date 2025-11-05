from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    path('iniciosesiontrabajador/', views.iniciosesiontrabajador, name='iniciosesiontrabajador'),
    path('pagina3/', views.pagina3, name='pagina3'),
    path('dashboardtrabajador/', views.dashboardtrabajador, name='dashboardtrabajador'),
    path("producto/<int:pid>/", views.producto_detalle, name="producto_detalle"),
]
