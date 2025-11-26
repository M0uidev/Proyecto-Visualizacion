from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # Dashboards
    path('dashboardadmin/', views.dashboardadmin, name='dashboardadmin'),
    path('dashboardtrabajador/', views.dashboardtrabajador, name='dashboardtrabajador'),
    # Stock (renombrado)
    path('stock/', views.stock, name='stock'),
    # POS para trabajador
    path('pos/', views.pos_view, name='pos'),
    # Productos
    path("producto/<int:pid>/", views.producto_detalle, name="producto_detalle"),
    path("producto/<int:pid>/edit/", views.edit_product, name="edit_product"),
    # Carrito
    path('add_to_cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:pid>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_quantity/<int:pid>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout_webpay, name='checkout_webpay'),
    path('receipt/<str:order_code>/', views.download_receipt, name='download_receipt'),
    # API Análisis Regional
    path('regional-analysis-api/', views.regional_analysis_api, name='regional_analysis_api'),
]
