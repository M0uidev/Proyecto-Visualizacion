from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='Index'),
    path('pagina2/', views.pagina2, name='Pagina2'),
    path('pagina3/', views.pagina3, name='Pagina3'),
    path('admin/', views.admin_dashboard, name='admin-dashboard'),
    path('worker/', views.worker_dashboard, name='worker-dashboard'),
    path('api/drill/orders', views.drill_orders, name='api_drill_orders'),
    path('api/drill/category', views.drill_category, name='api_drill_category'),
    path('api/drill/purchase_bin', views.drill_purchase_bin, name='api_drill_purchase_bin'),
    path('api/drill/metric', views.drill_metric, name='api_drill_metric'),
    path('api/drill/shift', views.drill_shift, name='api_drill_shift'),
]
