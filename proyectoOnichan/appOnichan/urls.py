from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pagina1/', views.pagina1, name='pagina1'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification_email'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # Dashboards
    path('dashboardadmin/', views.dashboardadmin, name='dashboardadmin'),
    path('api/dashboard-data/', views.api_dashboard_data, name='api_dashboard_data'),
    path('dashboardtrabajador/', views.dashboardtrabajador, name='dashboardtrabajador'),
    path('api/worker-dashboard-data/', views.api_worker_dashboard_data, name='api_worker_dashboard_data'),
    path('api/check_orders/', views.check_new_orders, name='check_new_orders'),
    # Fulfillment Game
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/detail/', views.order_detail_partial, name='order_detail_partial'),
    path('orders/<int:order_id>/print_label/', views.print_shipping_label, name='print_shipping_label'),
    path('fulfillment/', views.fulfillment_game, name='fulfillment_game'),
    path('fulfillment/complete/<int:order_id>/', views.complete_fulfillment, name='complete_fulfillment'),
    # Stock (renombrado)
    path('stock/', views.stock, name='stock'),
    # POS para trabajador
    path('pos/', views.pos_view, name='pos'),
    # Productos
    path("producto/<int:pid>/", views.producto_detalle, name="producto_detalle"),
    path("producto/<int:pid>/edit/", views.edit_product, name="edit_product"),
    # Carrito
    path('add_to_cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_quantity/<str:key>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout_webpay, name='checkout_webpay'),
    path('webpay/commit/', views.webpay_commit, name='webpay_commit'),
    path('receipt/<str:order_code>/', views.download_receipt, name='download_receipt'),
    # Marketing & Cupones
    path('marketing/', views.marketing_dashboard, name='marketing_dashboard'),
    path('marketing/coupon/create/', views.coupon_create, name='coupon_create'),
    path('marketing/coupon/edit/<int:cid>/', views.coupon_edit, name='coupon_edit'),
    path('marketing/coupon/delete/<int:cid>/', views.coupon_delete, name='coupon_delete'),
    path('marketing/coupon/delete-batch/', views.delete_coupon_batch, name='delete_coupon_batch'),
    path('marketing/bulk/revert/<int:oid>/', views.revert_bulk_offer, name='revert_bulk_offer'),
    path('marketing/bulk/detail/<int:oid>/', views.bulk_offer_detail, name='bulk_offer_detail'),
    path('cart/apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/remove_coupon/', views.remove_coupon, name='remove_coupon'),
    # API Análisis Regional
    path('regional-analysis-api/', views.regional_analysis_api, name='regional_analysis_api'),
    path('marketing/coupon/get-batch/', views.get_coupon_batch, name='get_coupon_batch'),
    # Barcode Tool
    path('barcode-tool/', views.barcode_tool, name='barcode_tool'),
    path('barcode-tool/print/', views.print_barcodes, name='print_barcodes'),
    # Rewards
    path('rewards/', views.rewards_catalog, name='rewards_catalog'),
    path('rewards/redeem/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
    path('marketing/reward/create/', views.create_reward, name='create_reward'),
    path('marketing/reward/toggle/<int:rid>/', views.toggle_reward_status, name='toggle_reward_status'),
    path('marketing/reward/delete/<int:rid>/', views.delete_reward, name='delete_reward'),
    
    # Marketing Editor
    path('marketing/editor/<int:template_id>/', views.marketing_editor, name='marketing_editor'),
    path('marketing/save/<int:template_id>/', views.save_marketing_template, name='save_marketing_template'),
    path('marketing/campaign/create/', views.create_campaign, name='create_campaign'),
]
