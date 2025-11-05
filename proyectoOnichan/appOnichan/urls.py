from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    path('iniciosesionadmin/', views.iniciosesionadmin, name='iniciosesionadmin'),
    path('adminstock/', views.pagina3, name='pagina3'),
    path('dashboardadmin/', views.dashboardadmin, name='dashboardadmin'),
    path("producto/<int:pid>/", views.producto_detalle, name="producto_detalle"),
]
