"""
Servicio de Productos - Lógica centralizada para productos
"""
from django.db.models import Q
from ..models import Product, Category


class ProductService:
    """Servicio para gestionar productos y búsquedas"""
    
    @staticmethod
    def filter_and_sort_products(query_params):
        """
        Filtra y ordena productos según parámetros de consulta.
        query_params: dict con keys: category, sort, q (query), items_per_page
        
        Retorna: (queryset, categories, context_dict)
        """
        category_slug = query_params.get("category", "")
        sort_by = query_params.get("sort", "")
        query = query_params.get("q", "").strip()
        
        try:
            items_per_page = int(query_params.get("items", 8))
        except (ValueError, TypeError):
            items_per_page = 8
        
        # Query base con optimizaciones
        productos = Product.objects.select_related('category', 'detail').prefetch_related(
            'bulk_offers', 'sizes'
        ).all()
        
        # Filtrar por búsqueda
        if query:
            productos = productos.filter(name__icontains=query)
        
        # Filtrar por categoría
        if category_slug and category_slug != 'all':
            productos = productos.filter(category__slug=category_slug)
        
        # Ordenar
        if sort_by == "price_asc":
            productos = productos.order_by("price")
        elif sort_by == "price_desc":
            productos = productos.order_by("-price")
        elif sort_by == "newest":
            productos = productos.order_by("-id")
        else:
            productos = productos.order_by("id")
        
        categories = Category.objects.all()
        
        context = {
            "productos": productos,
            "categories": categories,
            "current_category": category_slug,
            "current_sort": sort_by,
            "items_per_page": items_per_page,
            "query": query
        }
        
        return productos, categories, context
    
    @staticmethod
    def get_discounted_price(product):
        """
        Obtiene el precio con descuento aplicado.
        Considera ofertas masivas activas.
        """
        try:
            return product.detail.discounted_price
        except:
            return product.price
    
    @staticmethod
    def get_offers_imperdibles():
        """
        Obtiene productos con ofertas activas (ofertas imperdibles).
        """
        return Product.objects.filter(
            bulk_offers__active=True
        ).distinct().select_related('category', 'detail').prefetch_related(
            'bulk_offers', 'sizes'
        )

