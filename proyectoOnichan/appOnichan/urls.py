from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='Index'),
    path('pagina2/', views.pagina2, name='Pagina2'),
    path('pagina3/', views.pagina3, name='Pagina3'),
    path('admin/', views.admin_dashboard, name='admin-dashboard'),
    path('worker/', views.worker_dashboard, name='worker-dashboard'),
]
