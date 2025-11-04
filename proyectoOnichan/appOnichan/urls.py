from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    path('pagina2/', views.pagina2, name='pagina2'),
    path('pagina3/', views.pagina3, name='pagina3'),
]
