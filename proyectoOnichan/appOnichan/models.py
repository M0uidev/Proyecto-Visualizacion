from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(max_length=120, unique=True)

	class Meta:
		verbose_name_plural = "Categories"

	def __str__(self) -> str:  # pragma: no cover
		return self.name


class Product(models.Model):
	# Keep ids compatible with existing site URLs (101..110)
	id = models.PositiveIntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	price = models.PositiveIntegerField(help_text="Precio en CLP (entero)")
	image_url = models.CharField(max_length=300)
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")

	def __str__(self) -> str:  # pragma: no cover
		return f"{self.name} (${self.price})"


class ProductDetail(models.Model):
	product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="detail")
	rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
	rating_count = models.PositiveIntegerField(default=0)
	color = models.CharField(max_length=80, blank=True)
	descuento_pct = models.PositiveIntegerField(default=0)
	envio = models.CharField(max_length=120, blank=True)
	llega = models.CharField(max_length=120, blank=True)
	warranty = models.CharField(max_length=120, blank=True)
	capacity_l = models.PositiveIntegerField(null=True, blank=True)


class ProductSize(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
	label = models.CharField(max_length=20)

	class Meta:
		unique_together = ("product", "label")


class ProductSpec(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
	text = models.CharField(max_length=200)


class ProductCare(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="care")
	text = models.CharField(max_length=200)


class ProductBreadcrumb(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="breadcrumbs")
	position = models.PositiveSmallIntegerField(default=0)
	label = models.CharField(max_length=60)

	class Meta:
		ordering = ["position"]


class Customer(models.Model):
	name = models.CharField(max_length=150)

	def __str__(self) -> str:  # pragma: no cover
		return self.name


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

	code = models.CharField(max_length=20, unique=True)
	fecha = models.DateField()
	cliente = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
	total = models.PositiveIntegerField(default=0)
	estado = models.CharField(max_length=20, choices=STATUS_CHOICES)
	channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="Online")

	def __str__(self) -> str:  # pragma: no cover
		return self.code


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	cantidad = models.PositiveIntegerField(default=1)
	price = models.PositiveIntegerField(help_text="Precio unitario en CLP")
	size = models.CharField(max_length=20, blank=True)

	@property
	def subtotal(self) -> int:
		return self.cantidad * self.price

