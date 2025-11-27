from .models import Order

def pending_orders_count(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.groups.filter(name__in=['admin', 'trabajador']).exists()):
        count = Order.objects.filter(estado='Pendiente').count()
        return {'pending_orders_count': count}
    return {}
