from django.core.management.base import BaseCommand
from django.utils import timezone
import random

from appOnichan.models import Customer, Order, OrderItem, Product


class Command(BaseCommand):
    help = "Genera pedidos de demostración (20) a partir de los productos existentes"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20, help="Cantidad de pedidos a generar")

    def handle(self, *args, **options):
        count = options["count"]
        estados = ["Pendiente", "Despachado", "Entregado", "Cancelado"]
        canales = ["Online", "Tienda"]
        nombres = [
            "Juan Pérez", "María González", "Carlos Rodríguez", "Ana Silva", "Luis Torres",
            "Carmen Ruiz", "Diego Muñoz", "Patricia Lagos", "Roberto Vera", "Isabel Ortiz",
        ]

        productos = list(Product.objects.all())
        if not productos:
            self.stdout.write(self.style.WARNING("No hay productos. Ejecute primero: python manage.py seed_products"))
            return

        # Crear o tomar clientes
        clientes = {n: Customer.objects.get_or_create(name=n)[0] for n in nombres}

        today = timezone.localdate()
        created = 0

        for i in range(1, count + 1):
            dias_atras = random.randint(0, 7)
            fecha = today - timezone.timedelta(days=dias_atras)
            cliente = random.choice(list(clientes.values()))
            estado = random.choice(estados)
            channel = random.choice(canales)

            code = f"PED-{i:03d}"
            if Order.objects.filter(code=code).exists():
                continue

            order = Order.objects.create(
                code=code,
                fecha=fecha,
                cliente=cliente,
                total=0,
                estado=estado,
                channel=channel,
            )

            # Items: 1 a 3 productos
            for prod in random.sample(productos, k=random.randint(1, min(3, len(productos)))):
                cantidad = random.randint(1, 3)
                # Seleccionar una talla si existe
                sizes = list(prod.sizes.values_list("label", flat=True))
                size = random.choice(sizes) if sizes else ""
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    cantidad=cantidad,
                    price=prod.price,
                    size=size,
                )

            # Recalcular total
            total = sum(it.cantidad * it.price for it in order.items.all())
            order.total = total
            order.save(update_fields=["total"])
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Pedidos de demostración generados: {created}"))
