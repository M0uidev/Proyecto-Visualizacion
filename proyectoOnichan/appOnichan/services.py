from django.db.models import Sum, Count, Avg
from .models import Order, OrderItem

def get_regional_stats(start_date, end_date):
    # 1. General metrics by region
    base_qs = Order.objects.filter(
        fecha__gte=start_date, 
        fecha__lte=end_date
    ).exclude(shipping_region__isnull=True).exclude(shipping_region="")

    metrics = base_qs.values('shipping_region').annotate(
        ventas_totales=Sum('total'),
        pedidos_unicos=Count('id'),
        ticket_promedio=Avg('total')
    )

    # 2. Distinct products by region
    prod_distinct = OrderItem.objects.filter(
        order__fecha__gte=start_date, 
        order__fecha__lte=end_date
    ).exclude(order__shipping_region__isnull=True).exclude(order__shipping_region="").values('order__shipping_region').annotate(
        productos_distintos=Count('product', distinct=True)
    )
    prod_map = {x['order__shipping_region']: x['productos_distintos'] for x in prod_distinct}

    # 3. Top Category (Calculation in Python)
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

    # 4. Unify data
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
