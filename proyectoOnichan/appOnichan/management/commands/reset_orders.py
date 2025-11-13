from django.core.management.base import BaseCommand
from appOnichan.models import OrderItem, Order


class Command(BaseCommand):
    help = "Elimina todos los pedidos y sus ítems (reset). Útil para recomenzar y crear pedidos a mano."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="Confirmación para proceder sin prompt")

    def handle(self, *args, **options):
        if not options.get("yes"):
            self.stdout.write("Este comando eliminará TODOS los pedidos e ítems. Use --yes para confirmar.")
            return

        cnt_items, _ = OrderItem.objects.all().delete()
        cnt_orders, _ = Order.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Eliminados pedidos={cnt_orders}, items={cnt_items}"))
