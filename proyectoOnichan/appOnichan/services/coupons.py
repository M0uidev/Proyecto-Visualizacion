"""
Servicio de Cupones - Lógica centralizada para cupones
"""
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from ..models import Coupon


class CouponService:
    """Servicio para gestionar cupones"""
    
    @staticmethod
    def validate_and_apply(request, coupon_code, cart_total=None):
        """
        Valida y aplica un cupón al carrito.
        Si cart_total es None, lo calcula desde el carrito actual.
        Retorna: (success, response_data)
        """
        from .cart import CartService
        
        code = coupon_code.strip()
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if not code:
            error_msg = "Debe ingresar un código de cupón."
            if is_ajax:
                return False, JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return False, None
        
        # Calcular total del carrito si no se proporciona
        if cart_total is None:
            items, _ = CartService.get_cart_items(request)
            cart_total, _, _ = CartService.calculate_totals(items, None)
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            error_msg = "El cupón no existe."
            if is_ajax:
                return False, JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return False, None
        
        # Validar cupón
        if not coupon.is_valid():
            error_msg = "Cupón no válido o expirado"
            if is_ajax:
                return False, JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return False, None
        
        # Aplicar cupón
        request.session['coupon_id'] = coupon.id
        
        # Calcular descuento
        discount_amount = CouponService.calculate_discount(coupon, cart_total)
        final_total = cart_total - discount_amount
        
        success_msg = f"Cupón {code} aplicado: {coupon.discount_percentage}% de descuento."
        
        if is_ajax:
            return True, JsonResponse({
                'success': True,
                'message': success_msg,
                'discount_percentage': coupon.discount_percentage,
                'discount_amount': discount_amount,
                'new_total': final_total,
                'code': coupon.code
            })
        
        messages.success(request, success_msg)
        return True, None
    
    @staticmethod
    def calculate_discount(coupon, total):
        """
        Calcula el monto del descuento basado en el cupón y el total.
        """
        if not coupon or not coupon.is_valid():
            return 0
        return int(total * (coupon.discount_percentage / 100))
    
    @staticmethod
    def remove_coupon(request):
        """Remueve el cupón del carrito"""
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
            messages.info(request, "Cupón removido.")
        return redirect("cart_view")
    
    @staticmethod
    def get_active_coupon(request):
        """
        Obtiene el cupón activo en la sesión si existe y es válido.
        """
        coupon_id = request.session.get('coupon_id')
        if not coupon_id:
            return None
        
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.is_valid():
                return coupon
            else:
                # Cupón inválido, remover de sesión
                del request.session['coupon_id']
                return None
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
            return None

