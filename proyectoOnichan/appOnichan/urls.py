from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='Index'),
    path('pagina2/', views.pagina2, name='Pagina2'),
    path('pagina3/', views.pagina3, name='Pagina3'),
]
