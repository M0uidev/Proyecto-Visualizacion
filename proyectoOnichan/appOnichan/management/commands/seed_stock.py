from django.core.management.base import BaseCommand
from appOnichan.models import Product

class Command(BaseCommand):
    help = "Inicializa el stock de productos existentes si está en cero (por defecto 50)."

    def add_arguments(self, parser):
        parser.add_argument("--value", type=int, default=50, help="Valor de stock a asignar si está en 0")

    def handle(self, *args, **options):
        value = max(0, int(options.get("value", 50)))
        updated = 0
        for p in Product.objects.all():
            if (p.stock or 0) == 0:
                p.stock = value
                p.save(update_fields=["stock"])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Stock inicializado en {updated} productos (valor={value})."))
