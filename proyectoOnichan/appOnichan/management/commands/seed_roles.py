from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Crea grupos de roles (admin, trabajador, cliente) y usuarios de ejemplo"

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="admin")
        worker_group, _ = Group.objects.get_or_create(name="trabajador")
        client_group, _ = Group.objects.get_or_create(name="cliente")

        # Admin
        admin_user, created = User.objects.get_or_create(username="admin")
        if created:
            admin_user.set_password("admin123")
            admin_user.is_staff = True
            admin_user.save()
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS("Usuario admin creado: admin/admin123"))
        else:
            self.stdout.write("Usuario admin ya existe")

        # Trabajador
        worker_user, created = User.objects.get_or_create(username="trabajador")
        if created:
            worker_user.set_password("trabajador123")
            worker_user.save()
            worker_user.groups.add(worker_group)
            self.stdout.write(self.style.SUCCESS("Usuario trabajador creado: trabajador/trabajador123"))
        else:
            self.stdout.write("Usuario trabajador ya existe")

        # Cliente
        client_user, created = User.objects.get_or_create(username="cliente")
        if created:
            client_user.set_password("cliente123")
            client_user.save()
            client_user.groups.add(client_group)
            self.stdout.write(self.style.SUCCESS("Usuario cliente creado: cliente/cliente123"))
        else:
            self.stdout.write("Usuario cliente ya existe")
