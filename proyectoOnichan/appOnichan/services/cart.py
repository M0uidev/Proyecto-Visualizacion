"""
Servicio de Carrito - Lógica centralizada para gestión del carrito
"""
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from ..models import Product, Coupon


class CartService:
    """Servicio para gestionar el carrito de compras"""
    
    @staticmethod
    def get_cart_items(request):
        """
        Obtiene los items del carrito con información completa de productos.
        Retorna lista de diccionarios con: product, qty, size, key, subtotal, price_used, is_reward
        """
        cart = request.session.get("cart", {})
        rewards_cart = request.session.get("rewards_cart", {})
        items = []
        
        # Extraer IDs de productos del carrito normal
        pids = set()
        for key in list(cart.keys()) + list(rewards_cart.keys()):
            try:
                pids.add(int(key.split('_')[0]))
            except (ValueError, IndexError):
                continue
        
        if not pids:
            return items
        
        # Cargar productos de una vez
        products = Product.objects.filter(id__in=pids).select_related('category', 'detail').prefetch_related('sizes', 'bulk_offers')
        product_map = {str(p.id): p for p in products}
        
        # Procesar items del carrito normal
        for key, qty in cart.items():
            try:
                parts = key.split('_')
                pid = parts[0]
                size = parts[1] if len(parts) > 1 else None
            except (ValueError, IndexError):
                continue
            
            product = product_map.get(pid)
            if not product:
                continue
            
            # Calcular precio (con descuento si aplica)
            try:
                price_used = product.detail.discounted_price
            except:
                price_used = product.price
            
            items.append({
                'key': key,
                'product': product,
                'qty': qty,
                'size': size,
                'price_used': price_used,
                'subtotal': price_used * qty,
                'is_reward': False
            })
        
        # Procesar items de recompensas
        for key, qty in rewards_cart.items():
            try:
                parts = key.split('_')
                pid = parts[0]
                size = parts[1] if len(parts) > 1 else None
            except (ValueError, IndexError):
                continue
            
            product = product_map.get(pid)
            if not product:
                continue
            
            items.append({
                'key': key,
                'product': product,
                'qty': qty,
                'size': size,
                'price_used': 0,
                'subtotal': 0,
                'is_reward': True
            })
        
        return items
    
    @staticmethod
    def calculate_totals(cart_items, coupon=None):
        """
        Calcula totales del carrito.
        Retorna: (subtotal, discount_amount, final_total)
        """
        subtotal = sum(item['subtotal'] for item in cart_items)
        discount_amount = 0
        
        if coupon:
            discount_amount = int(subtotal * (coupon.discount_percentage / 100))
        
        final_total = subtotal - discount_amount
        return subtotal, discount_amount, final_total
    
    @staticmethod
    def validate_stock(product, quantity, cart):
        """
        Valida que haya suficiente stock disponible.
        Considera el stock ya en el carrito.
        """
        # Calcular cantidad total en carrito (todas las tallas)
        total_in_cart = 0
        for key, qty in cart.items():
            if key == str(product.id) or key.startswith(f"{product.id}_"):
                total_in_cart += qty
        
        # Verificar si al agregar esta cantidad excede el stock
        if total_in_cart + quantity > product.stock:
            return False, f"No puedes agregar más unidades de {product.name}. Stock máximo alcanzado."
        
        return True, None
    
    @staticmethod
    def add_to_cart(request, product_id, size=None):
        """
        Añade un producto al carrito.
        Retorna: (success, response) donde response puede ser JsonResponse o redirect
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            error_msg = "Producto no encontrado."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
                return False, JsonResponse({'status': 'error', 'message': error_msg}, status=404)
            messages.error(request, error_msg)
            return False, redirect(request.META.get('HTTP_REFERER', 'pagina1'))
        
        # Validar stock
        if product.stock <= 0:
            error_msg = "Este producto no tiene stock."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
                return False, JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return False, redirect(request.META.get('HTTP_REFERER', 'pagina1'))
        
        # Validar talla si es requerida
        if product.sizes.exists() and not size:
            error_msg = "Debe seleccionar una talla para este producto."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
                return False, JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return False, redirect(request.META.get('HTTP_REFERER', 'pagina1'))
        
        # Generar clave del carrito
        key = str(product_id)
        if size:
            key = f"{product_id}_{size}"
        
        cart = request.session.get("cart", {})
        
        # Validar stock disponible
        is_valid, error_msg = CartService.validate_stock(product, 1, cart)
        if not is_valid:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
                return False, JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return False, redirect(request.META.get('HTTP_REFERER', 'pagina1'))
        
        # Añadir al carrito
        cart[key] = cart.get(key, 0) + 1
        request.session["cart"] = cart
        
        # Respuesta AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
            total_items = sum(cart.values())
            return True, JsonResponse({'status': 'ok', 'cart_count': total_items})
        
        return True, redirect(request.META.get('HTTP_REFERER', 'pagina1'))
    
    @staticmethod
    def remove_from_cart(request, key):
        """Elimina un item del carrito"""
        from django.shortcuts import redirect
        from django.contrib import messages
        from ..models import PointReward
        from . import RewardService
        
        cart = request.session.get("cart", {})
        if key in cart:
            del cart[key]
            request.session["cart"] = cart
        
        # También verificar rewards_cart
        rewards_cart = request.session.get("rewards_cart", {})
        if key in rewards_cart:
            # Lógica de reembolso de puntos (si aplica)
            try:
                pid = int(key.split('_')[0])
                qty = rewards_cart[key]
                reward = PointReward.objects.filter(
                    product_id=pid, reward_type='PRODUCT'
                ).first()
                
                if reward and request.user.is_authenticated:
                    RewardService.restore_reward(request.user, reward.id, qty)
                    messages.success(request, "Producto eliminado. Se han reembolsado los puntos.")
            except Exception:
                pass
            
            del rewards_cart[key]
            request.session["rewards_cart"] = rewards_cart
        
        return redirect("cart_view")
    
    @staticmethod
    def update_quantity(request, key, action):
        """
        Actualiza la cantidad de un item en el carrito.
        action: 'increment' o 'decrement'
        """
        cart = request.session.get("cart", {})
        
        if key not in cart:
            messages.error(request, "Item no encontrado en el carrito.")
            return redirect("cart_view")
        
        try:
            pid = int(key.split('_')[0])
            product = Product.objects.get(id=pid)
        except (ValueError, Product.DoesNotExist):
            messages.error(request, "Producto no encontrado.")
            return redirect("cart_view")
        
        current_qty = cart[key]
        
        if action == 'increment':
            # Validar stock antes de incrementar
            is_valid, error_msg = CartService.validate_stock(product, 1, cart)
            if not is_valid:
                messages.warning(request, error_msg)
                return redirect("cart_view")
            cart[key] = current_qty + 1
        elif action == 'decrement':
            if current_qty > 1:
                cart[key] = current_qty - 1
            else:
                # Si es 1, eliminar del carrito
                return CartService.remove_from_cart(request, key)
        else:
            messages.error(request, "Acción inválida.")
            return redirect("cart_view")
        
        request.session["cart"] = cart
        return redirect("cart_view")

