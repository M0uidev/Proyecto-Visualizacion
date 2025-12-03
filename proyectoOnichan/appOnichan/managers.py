"""
Managers personalizados para modelos
"""
from django.db import models


class ProductManager(models.Manager):
    """Manager personalizado para Product con métodos de consulta útiles"""
    """Manager personalizado para Product"""
    
    def available(self):
        """Retorna productos con stock disponible"""
        return self.filter(stock__gt=0)
    
    def with_discounts(self):
        """Retorna productos que tienen descuentos activos"""
        return self.filter(bulk_offers__active=True).distinct()
    
    def by_category(self, category_slug):
        """Retorna productos filtrados por categoría"""
        return self.filter(category__slug=category_slug)


class OrderManager(models.Manager):
    """Manager personalizado para Order"""
    
    def pending(self):
        """Retorna pedidos pendientes"""
        return self.filter(estado="Pendiente")
    
    def by_period(self, start_date, end_date):
        """Retorna pedidos en un rango de fechas"""
        return self.filter(fecha__gte=start_date, fecha__lte=end_date)
    
    def by_region(self, region):
        """Retorna pedidos de una región específica"""
        return self.filter(shipping_region=region)

