"""
Servicios de la aplicación - Lógica de negocio centralizada
"""
from django.db.models import Sum, Count, Avg
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Order, OrderItem, Product, PointReward, UserProfile, RedemptionHistory, UserCoupon, Coupon
from .emails import EmailService
from .cart import CartService
from .products import ProductService
from .coupons import CouponService

def get_regional_stats(start_date, end_date):
    """
    Obtiene estadísticas de ventas agrupadas por región.
    Retorna diccionario con métricas: ventas totales, pedidos únicos, ticket promedio, etc.
    """
    base_qs = Order.objects.filter(
        fecha__gte=start_date, 
        fecha__lte=end_date
    ).exclude(shipping_region__isnull=True).exclude(shipping_region="")

    # Métricas generales por región
    metrics = base_qs.values('shipping_region').annotate(
        ventas_totales=Sum('total'),
        pedidos_unicos=Count('id'),
        ticket_promedio=Avg('total')
    )

    # Productos distintos por región
    prod_distinct = OrderItem.objects.filter(
        order__fecha__gte=start_date, 
        order__fecha__lte=end_date
    ).exclude(order__shipping_region__isnull=True).exclude(order__shipping_region="").values('order__shipping_region').annotate(
        productos_distintos=Count('product', distinct=True)
    )
    prod_map = {x['order__shipping_region']: x['productos_distintos'] for x in prod_distinct}

    # Categoría más vendida por región (cálculo en Python)
    cat_qs = OrderItem.objects.filter(
        order__fecha__gte=start_date, 
        order__fecha__lte=end_date
    ).exclude(order__shipping_region__isnull=True).exclude(order__shipping_region="").values('order__shipping_region', 'product__category__name').annotate(
        qty=Sum('cantidad')
    ).order_by('order__shipping_region', '-qty')

    top_cat_map = {}
    for item in cat_qs:
        reg = item['order__shipping_region']
        if reg not in top_cat_map:
            top_cat_map[reg] = item['product__category__name']

    # Unificar datos en un solo diccionario
    results = {}
    for m in metrics:
        reg = m['shipping_region']
        results[reg] = {
            "nombre": reg,
            "ventas_totales": m['ventas_totales'] or 0,
            "pedidos_unicos": m['pedidos_unicos'] or 0,
            "ticket_promedio": round(m['ticket_promedio'] or 0, 2),
            "productos_distintos": prod_map.get(reg, 0),
            "categoria_top": top_cat_map.get(reg, "N/A"),
        }
    return results


class RewardService:
    """Servicio para gestionar canjes de recompensas por puntos"""
    
    @staticmethod
    @transaction.atomic
    def redeem_reward(user, reward_id, size=None):
        """
        Canjea una recompensa por puntos del usuario.
        Maneja productos y cupones, actualiza stock y puntos.
        """
        try:
            reward = PointReward.objects.select_for_update().get(id=reward_id, active=True)
        except PointReward.DoesNotExist:
            raise ValidationError("La recompensa no existe o no está activa.")

        profile = UserProfile.objects.select_for_update().get(user=user)

        if profile.points < reward.points_cost:
            raise ValidationError("No tienes suficientes puntos para este canje.")

        # Validar stock para recompensas de producto
        if reward.reward_type == 'PRODUCT':
            if reward.stock <= 0:
                raise ValidationError("Lo sentimos, este producto de recompensa se ha agotado.")
            
            reward.stock -= 1
            if reward.stock <= 0:
                reward.active = False
            reward.save()
        
        # Manejar cupones
        elif reward.reward_type == 'COUPON':
            if reward.coupon_batch_name:
                batch_coupons = Coupon.objects.filter(batch_name=reward.coupon_batch_name, active=True)
                assigned_ids = UserCoupon.objects.filter(coupon__in=batch_coupons).values_list('coupon_id', flat=True)
                
                # Buscar cupón disponible en el lote
                available_coupon = batch_coupons.exclude(id__in=assigned_ids).select_for_update().first()
                
                if not available_coupon:
                     raise ValidationError("Lo sentimos, se han agotado los cupones de esta recompensa.")
                
                UserCoupon.objects.create(user=user, coupon=available_coupon)
                
                # Desactivar recompensa si se agotaron los cupones
                remaining = batch_coupons.exclude(id__in=assigned_ids).count() - 1
                if remaining <= 0:
                    reward.active = False
                    reward.save()
                    
            elif reward.coupon:
                if UserCoupon.objects.filter(user=user, coupon=reward.coupon).exists():
                     raise ValidationError("Ya tienes este cupón.")
                UserCoupon.objects.create(user=user, coupon=reward.coupon)

        # Descontar puntos
        profile.points -= reward.points_cost
        profile.save()

        # Registrar en historial
        RedemptionHistory.objects.create(
            user=user,
            reward=reward,
            points_spent=reward.points_cost
        )
        
        return reward

    @staticmethod
    @transaction.atomic
    def restore_reward(user, reward_id, quantity=1):
        try:
            reward = PointReward.objects.select_for_update().get(id=reward_id)
        except PointReward.DoesNotExist:
            return

        if user:
            try:
                profile = UserProfile.objects.select_for_update().get(user=user)
                points_to_restore = reward.points_cost * quantity
                profile.points += points_to_restore
                profile.save()
            except UserProfile.DoesNotExist:
                pass
        
        if reward.reward_type == 'PRODUCT':
            reward.stock += quantity
            if reward.stock > 0 and not reward.active:
                reward.active = True
            reward.save()

class StockService:
    """Servicio para gestionar stock de productos"""
    
    @staticmethod
    @transaction.atomic
    def reserve_stock_for_order(order):
        """
        Reserva stock para un pedido (reduce stock disponible).
        Lanza ValidationError si no hay suficiente stock.
        """
        for item in order.items.all():
            if not item.is_reward:
                try:
                    product = Product.objects.select_for_update().get(id=item.product.id)
                except Product.DoesNotExist:
                    raise ValidationError(f"El producto {item.product.name} ya no existe.")
                
                if product.stock < item.cantidad:
                    raise ValidationError(f"No hay suficiente stock para {product.name}. Disponible: {product.stock}")
                
                product.stock -= item.cantidad
                product.save()

    @staticmethod
    @transaction.atomic
    def release_stock_for_order(order):
        """
        Libera stock de un pedido (aumenta stock disponible).
        Maneja reembolsos de recompensas si aplica.
        """
        for item in order.items.all():
            if item.is_reward:
                reward = PointReward.objects.filter(product=item.product, reward_type='PRODUCT').first()
                if reward and order.user:
                    RewardService.restore_reward(order.user, reward.id, item.cantidad)
            else:
                try:
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    product.stock += item.cantidad
                    product.save()
                except Product.DoesNotExist:
                    pass
