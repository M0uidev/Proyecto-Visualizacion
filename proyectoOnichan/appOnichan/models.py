from django.db import models

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
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")

    class Meta:
        db_table = 'apponichan_product'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} (${self.price})"


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
    STATUS_CHOICES = [
        ("Pendiente", "Pendiente"),
        ("Despachado", "Despachado"),
        ("Entregado", "Entregado"),
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
    total = models.PositiveIntegerField(default=0, verbose_name="Total")
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Estado")
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="Online", verbose_name="Canal")

    class Meta:
        db_table = 'apponichan_order'
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return self.code


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

    class Meta:
        db_table = 'apponichan_orderitem'
        verbose_name = "Ítem de Pedido"
        verbose_name_plural = "Ítems de Pedidos"

    def __str__(self):
        return f"{self.cantidad}x {self.product.name} ({self.order.code})"

    @property
    def subtotal(self) -> int:
        return self.cantidad * self.price

