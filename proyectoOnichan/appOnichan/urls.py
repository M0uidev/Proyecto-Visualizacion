from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Dashboards
    path('dashboardadmin/', views.dashboardadmin, name='dashboardadmin'),
    path('dashboardtrabajador/', views.dashboardtrabajador, name='dashboardtrabajador'),
    # Stock (renombrado)
    path('stock/', views.pagina3, name='stock'),
    # POS para trabajador
    path('pos/', views.pos_view, name='pos'),
    # Productos
    path("producto/<int:pid>/", views.producto_detalle, name="producto_detalle"),
]
