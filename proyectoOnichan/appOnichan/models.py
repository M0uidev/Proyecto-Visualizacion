from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.CharField(max_length=120, unique=True, verbose_name="Slug")

    class Meta:
        db_table = 'apponichan_category'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150, verbose_name="Nombre")

    class Meta:
        db_table = 'apponichan_customer'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Modelo de Producto"""
    from .managers import ProductManager
    objects = ProductManager()
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=200, verbose_name="Nombre")
    price = models.PositiveIntegerField(verbose_name="Precio", help_text="Precio en CLP (entero)")
    image_url = models.CharField(max_length=300, verbose_name="URL Imagen")
    category = models.ForeignKey(
        Category, 
        models.PROTECT, 
        related_name="products",
        verbose_name="Categoría"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    has_sizes = models.BooleanField(default=False, verbose_name="Tiene Tallas")

    class Meta:
        db_table = 'apponichan_product'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} (${self.price})"
    
    def is_available(self):
        """Verifica si el producto está disponible (tiene stock)"""
        return self.stock > 0
    
    def get_final_price(self):
        """
        Obtiene el precio final del producto considerando descuentos activos.
        Usa el servicio de productos para calcular el precio con descuento.
        """
        try:
            return self.detail.discounted_price
        except:
            return self.price


class ProductDetail(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.OneToOneField(
        Product, 
        models.CASCADE, 
        related_name="detail",
        verbose_name="Producto"
    )
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5, verbose_name="Calificación")
    rating_count = models.PositiveIntegerField(default=0, verbose_name="Cantidad de Calificaciones")
    color = models.CharField(max_length=80, blank=True, verbose_name="Color")
    descuento_pct = models.PositiveIntegerField(default=0, verbose_name="Porcentaje Descuento")
    envio = models.CharField(max_length=120, blank=True, verbose_name="Envío")
    llega = models.CharField(max_length=120, blank=True, verbose_name="Llega")
    warranty = models.CharField(max_length=120, blank=True, verbose_name="Garantía")
    capacity_l = models.PositiveIntegerField(blank=True, null=True, verbose_name="Capacidad (L)")

    class Meta:
        db_table = 'apponichan_productdetail'
        verbose_name = "Detalle de Producto"
        verbose_name_plural = "Detalles de Productos"

    def __str__(self):
        return f"Detalle de {self.product.name}"

    @property
    def discount_percentage(self):
        # Calculate discount dynamically from active Bulk Offers
        # Ignoring self.descuento_pct as requested
        from django.db.models import Max
        active_offers = self.product.bulk_offers.filter(active=True)
        if active_offers.exists():
            return active_offers.aggregate(Max('discount_percentage'))['discount_percentage__max'] or 0
        return 0

    @property
    def discounted_price(self):
        pct = self.discount_percentage
        if pct > 0:
            return int(self.product.price * (1 - pct / 100))
        return self.product.price


class ProductSize(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        models.CASCADE, 
        related_name="sizes",
        verbose_name="Producto"
    )
    label = models.CharField(max_length=20, verbose_name="Etiqueta")

    class Meta:
        db_table = 'apponichan_productsize'
        unique_together = (('product', 'label'),)
        verbose_name = "Talla de Producto"
        verbose_name_plural = "Tallas de Productos"

    def __str__(self):
        return f"{self.product.name} - {self.label}"


class ProductSpec(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        models.CASCADE, 
        related_name="specs",
        verbose_name="Producto"
    )
    text = models.CharField(max_length=200, verbose_name="Especificación")

    class Meta:
        db_table = 'apponichan_productspec'
        verbose_name = "Especificación de Producto"
        verbose_name_plural = "Especificaciones de Productos"

    def __str__(self):
        return f"{self.product.name}: {self.text}"


class ProductCare(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        models.CASCADE, 
        related_name="care",
        verbose_name="Producto"
    )
    text = models.CharField(max_length=200, verbose_name="Cuidado")

    class Meta:
        db_table = 'apponichan_productcare'
        verbose_name = "Cuidado de Producto"
        verbose_name_plural = "Cuidados de Productos"

    def __str__(self):
        return f"{self.product.name}: {self.text}"


class ProductBreadcrumb(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        models.CASCADE, 
        related_name="breadcrumbs",
        verbose_name="Producto"
    )
    position = models.PositiveSmallIntegerField(default=0, verbose_name="Posición")
    label = models.CharField(max_length=60, verbose_name="Etiqueta")

    class Meta:
        db_table = 'apponichan_productbreadcrumb'
        ordering = ["position"]
        verbose_name = "Miga de Pan"
        verbose_name_plural = "Migas de Pan"

    def __str__(self):
        return f"{self.product.name} > {self.label}"


class Order(models.Model):
    """Modelo de Pedido/Orden"""
    from .managers import OrderManager
    objects = OrderManager()
    
    STATUS_CHOICES = [
        ("Pendiente", "Pendiente"),
        ("Procesado", "Procesado"),
        ("En camino", "En camino"),
        ("Despachado", "Despachado"),
        ("Entregado", "Entregado"),
        ("Fallido", "Fallido"),
        ("Cancelado", "Cancelado"),
    ]
    CHANNEL_CHOICES = [
        ("Online", "Online"),
        ("Tienda", "Tienda"),
    ]

    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=20, verbose_name="Código")
    fecha = models.DateField(verbose_name="Fecha")
    cliente = models.ForeignKey(
        Customer, 
        models.PROTECT, 
        related_name="orders",
        verbose_name="Cliente"
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario Registrado")
    total = models.PositiveIntegerField(default=0, verbose_name="Total")
    discount_amount = models.PositiveIntegerField(default=0, verbose_name="Descuento Aplicado")
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Estado")
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="Online", verbose_name="Canal")
    
    # Nuevos campos para despacho y contacto
    delivery_method = models.CharField(max_length=20, default="Despacho", verbose_name="Método de Entrega")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    contact_email = models.EmailField(blank=True, verbose_name="Email")
    recipient_name = models.CharField(max_length=150, blank=True, verbose_name="Nombre Destinatario")
    shipping_address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    shipping_commune = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    shipping_region = models.CharField(max_length=100, blank=True, verbose_name="Región")

    class Meta:
        db_table = 'apponichan_order'
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return self.code
    
    def calculate_total(self):
        """
        Calcula el total del pedido sumando todos los items.
        Retorna el total calculado (sin considerar descuentos del cupón, que ya están en self.total).
        """
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        models.CASCADE, 
        related_name="items",
        verbose_name="Pedido"
    )
    product = models.ForeignKey(
        Product, 
        models.PROTECT,
        related_name="order_items",
        verbose_name="Producto"
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    price = models.PositiveIntegerField(verbose_name="Precio Unitario", help_text="Precio unitario en CLP")
    size = models.CharField(max_length=20, blank=True, verbose_name="Talla")
    is_reward = models.BooleanField(default=False, verbose_name="Es Recompensa")

    class Meta:
        db_table = 'apponichan_orderitem'
        verbose_name = "Ítem de Pedido"
        verbose_name_plural = "Ítems de Pedidos"

    def __str__(self):
        return f"{self.cantidad}x {self.product.name} ({self.order.code})"

    @property
    def subtotal(self) -> int:
        return self.cantidad * self.price


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    commune = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    region = models.CharField(max_length=100, blank=True, verbose_name="Región")
    points = models.PositiveIntegerField(default=0, verbose_name="Puntos Acumulados")
    is_verified = models.BooleanField(default=False, verbose_name="Verificado")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    discount_percentage = models.PositiveIntegerField(verbose_name="Porcentaje de Descuento", help_text="Porcentaje entre 1 y 100")
    valid_from = models.DateTimeField(verbose_name="Válido Desde")
    valid_to = models.DateTimeField(verbose_name="Válido Hasta")
    active = models.BooleanField(default=True, verbose_name="Activo")
    usage_limit = models.PositiveIntegerField(default=0, verbose_name="Límite de Uso", help_text="0 para ilimitado")
    times_used = models.PositiveIntegerField(default=0, verbose_name="Veces Usado")
    batch_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lote / Grupo") # Added batch_name

    class Meta:
        verbose_name = "Cupón"
        verbose_name_plural = "Cupones"

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

    def is_valid(self):
        """Verifica si el cupón es válido (activo, en rango de fechas y con usos disponibles)"""
        now = timezone.now()
        if not self.active:
            return False
        if self.valid_from > now or self.valid_to < now:
            return False
        if self.usage_limit > 0 and self.times_used >= self.usage_limit:
            return False
        return True
    
    def can_be_used_by(self, user):
        """
        Verifica si un usuario puede usar este cupón.
        Valida que el cupón sea válido y que el usuario no lo haya usado ya.
        """
        if not self.is_valid():
            return False
        
        # Verificar si el usuario ya usó este cupón (si aplica)
        if user and user.is_authenticated:
            # Verificar UserCoupon solo si existe la relación
            try:
                user_coupon = self.user_coupons.filter(user=user, is_used=True).first()
                if user_coupon:
                    return False
            except:
                # Si no existe la relación, asumir que puede usarlo
                pass
        
        return True


class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_coupons', verbose_name="Usuario")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_coupons', verbose_name="Cupón")
    acquired_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Adquisición")
    is_used = models.BooleanField(default=False, verbose_name="Usado")

    class Meta:
        verbose_name = "Cupón de Usuario"
        verbose_name_plural = "Cupones de Usuarios"
        unique_together = ('user', 'coupon')

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"


class BulkOffer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de la Oferta")
    discount_percentage = models.PositiveIntegerField(verbose_name="Porcentaje")
    products = models.ManyToManyField(Product, related_name="bulk_offers", verbose_name="Productos Afectados")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Oferta Masiva"
        verbose_name_plural = "Ofertas Masivas"

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}%)"


class PointReward(models.Model):
    TYPE_CHOICES = [
        ('COUPON', 'Cupón de Descuento'),
        ('PRODUCT', 'Producto Gratis'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del Canje")
    description = models.TextField(blank=True, verbose_name="Descripción")
    points_cost = models.PositiveIntegerField(verbose_name="Costo en Puntos")
    reward_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PRODUCT', verbose_name="Tipo de Recompensa")
    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Producto a Canjear")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cupón Asociado")
    
    image_url = models.CharField(max_length=300, blank=True, verbose_name="URL Imagen (Opcional)")
    active = models.BooleanField(default=True, verbose_name="Activo")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="Válido Hasta")
    coupon_batch_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lote de Cupones")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    
    class Meta:
        verbose_name = "Recompensa por Puntos"
        verbose_name_plural = "Recompensas por Puntos"

    def __str__(self):
        return f"{self.name} ({self.points_cost} pts)"

    def get_image(self):
        if self.image_url:
            return self.image_url
        if self.product:
            return self.product.image_url
        return "https://via.placeholder.com/300?text=Recompensa"

    @property
    def available_quantity(self):
        if self.reward_type == 'PRODUCT':
            return self.stock
        elif self.reward_type == 'COUPON' and self.coupon_batch_name:
            # Calculate remaining coupons in batch
            # We need to import UserCoupon here if it wasn't defined before, but it is.
            # However, to be safe from circular dependency issues if moved:
            from django.apps import apps
            UserCoupon = apps.get_model('appOnichan', 'UserCoupon')
            Coupon = apps.get_model('appOnichan', 'Coupon')
            
            batch_coupons = Coupon.objects.filter(batch_name=self.coupon_batch_name, active=True)
            assigned_count = UserCoupon.objects.filter(coupon__in=batch_coupons).count()
            return batch_coupons.count() - assigned_count
        return None


class RedemptionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redemptions', verbose_name="Usuario")
    reward = models.ForeignKey(PointReward, on_delete=models.SET_NULL, null=True, verbose_name="Recompensa")
    points_spent = models.PositiveIntegerField(verbose_name="Puntos Gastados")
    redeemed_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Canje")
    
    class Meta:
        verbose_name = "Historial de Canje"
        verbose_name_plural = "Historial de Canjes"
        ordering = ['-redeemed_at']

    def __str__(self):
        return f"{self.user.username} - {self.reward.name if self.reward else 'Borrado'}"


# --- MODELOS DE MARKETING ---

class MarketingTemplate(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Template")
    subject = models.CharField(max_length=200, verbose_name="Asunto del Correo (Default)")
    
    # HTML listo para enviar
    content_html = models.TextField(verbose_name="Contenido HTML", blank=True)
    
    # JSON interno de GrapesJS para poder re-editar el diseño (posiciones, estilos, etc)
    design_json = models.JSONField(verbose_name="Diseño (JSON)", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MarketingCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('scheduled', 'Programada'),
        ('sent', 'Enviada'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre de Campaña")
    template = models.ForeignKey(MarketingTemplate, on_delete=models.PROTECT)
    subject = models.CharField(max_length=200, help_text="Si se deja vacío usa el del template", blank=True)
    
    # Configuración de Cupones
    include_coupon = models.BooleanField(default=False, verbose_name="¿Incluir Cupón Personalizado?")
    coupon_discount_percent = models.IntegerField(default=0, verbose_name="% Descuento", blank=True)
    coupon_valid_days = models.IntegerField(default=7, verbose_name="Días de validez")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Destinatarios (simplificado: todos los usuarios o lógica futura de segmentos)
    # En un sistema real, aquí iría una relación ManyToMany o un filtro JSON.
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

class CampaignLog(models.Model):
    """Registro de envío individual para trazabilidad"""
    campaign = models.ForeignKey(MarketingCampaign, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    opened = models.BooleanField(default=False) # Para tracking futuro (pixel)

    def __str__(self):
        return f"Log: {self.campaign.name} -> {self.user.username}"

