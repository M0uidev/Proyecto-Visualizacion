from django.core.management.base import BaseCommand
from django.utils.text import slugify

from appOnichan.models import (
    Category,
    Product,
    ProductDetail,
    ProductSize,
    ProductSpec,
    ProductCare,
    ProductBreadcrumb,
)


PRODUCTS = [
    {"id": 101, "name": "Polera Oversized Negra",    "price": 14990, "image_url": "/static/images/productos/polera_negra.png",     "category": "Ropa"},
    {"id": 102, "name": "Zapatillas Urban Classic",   "price": 39990, "image_url": "/static/images/productos/zapatillas_urban.png", "category": "Calzado"},
    {"id": 103, "name": "Pantalón Cargo Verde",       "price": 29990, "image_url": "/static/images/productos/pantalon_cargo.png",   "category": "Ropa"},
    {"id": 104, "name": "Chaqueta Denim Azul",        "price": 34990, "image_url": "/static/images/productos/chaqueta_denim.png",   "category": "Ropa"},
    {"id": 105, "name": "Gorro Beanie Gris",          "price": 9990,  "image_url": "/static/images/productos/gorro_gris.png",       "category": "Accesorios"},
    {"id": 106, "name": "Polerón Essential Blanco",   "price": 25990, "image_url": "/static/images/productos/poleron_blanco.png",   "category": "Ropa"},
    {"id": 107, "name": "Mochila Explorer Negra",     "price": 27990, "image_url": "/static/images/productos/mochila_negra.png",    "category": "Equipaje"},
    {"id": 108, "name": "Botines Urbanos Cuero",      "price": 49990, "image_url": "/static/images/productos/botines_cuero.png",    "category": "Calzado"},
    {"id": 109, "name": "Cinturón Minimal",           "price": 12990, "image_url": "/static/images/productos/cinturon.png",         "category": "Accesorios"},
    {"id": 110, "name": "Reloj Vintage Metal",        "price": 55990, "image_url": "/static/images/productos/reloj_metal.png",      "category": "Accesorios"},
]


PRODUCT_DETAILS = {
    101: {
        "breadcrumbs": ["Home", "Moda", "Poleras"],
        "rating": 4.6, "rating_count": 384,
        "color": "Negro",
        "sizes": ["S", "M", "L", "XL"],
        "specs": ["Algodón 100% peinado 220 GSM", "Fit oversized unisex", "Cuello reforzado", "No destiñe"],
        "care": ["Lavar a 30°C", "No cloro", "Planchar tibio del revés"],
        "descuento_pct": 15, "envio": "Envío gratis", "llega": "Mañana",
    },
    102: {
        "breadcrumbs": ["Home", "Calzado", "Zapatillas"],
        "rating": 4.8, "rating_count": 1207,
        "color": "Blanco/Negro",
        "sizes": ["38","39","40","41","42","43","44"],
        "specs": ["Suela EVA antideslizante", "Plantilla memory foam", "Capellada respirable"],
        "descuento_pct": 25, "envio": "Retiro hoy en tienda B", "llega": "Jueves",
    },
    103: {
        "breadcrumbs": ["Home", "Moda", "Pantalones"],
        "rating": 4.5, "rating_count": 228,
        "color": "Verde oliva",
        "sizes": ["28","30","32","34","36"],
        "specs": ["Tela ripstop stretch", "6 bolsillos funcionales", "Cintura ajustable"],
        "descuento_pct": 20, "envio": "Envío gratis", "llega": "Mañana",
    },
    104: {
        "breadcrumbs": ["Home", "Moda", "Chaquetas"],
        "rating": 4.7, "rating_count": 312,
        "color": "Azul índigo",
        "sizes": ["S","M","L","XL"],
        "specs": ["Denim 12 oz", "Costuras reforzadas", "Botones metálicos"],
        "descuento_pct": 10, "envio": "Despacho programado", "llega": "Viernes",
    },
    105: {
        "breadcrumbs": ["Home", "Accesorios", "Gorros"],
        "rating": 4.4, "rating_count": 97,
        "color": "Gris",
        "specs": ["Tejido acrílico hipoalergénico", "Unisex", "Talla única"],
        "descuento_pct": 0, "envio": "Retiro hoy en tienda A", "llega": "Mañana",
    },
    106: {
        "breadcrumbs": ["Home", "Moda", "Polerones"],
        "rating": 4.6, "rating_count": 541,
        "color": "Blanco",
        "sizes": ["S","M","L","XL"],
        "specs": ["French terry 300 GSM", "Capucha forrada", "Bolsillo canguro"],
        "descuento_pct": 18, "envio": "Envío gratis", "llega": "Mañana",
    },
    107: {
        "breadcrumbs": ["Home", "Accesorios", "Mochilas"],
        "rating": 4.7, "rating_count": 660,
        "color": "Negro",
        "capacity_l": 22,
        "specs": ["Compartimento laptop 15.6\"", "Tela repelente al agua", "Bolsillo oculto"],
        "descuento_pct": 12, "envio": "Envío a domicilio", "llega": "Jueves",
    },
    108: {
        "breadcrumbs": ["Home", "Calzado", "Botines"],
        "rating": 4.9, "rating_count": 188,
        "color": "Cuero café",
        "sizes": ["39","40","41","42","43"],
        "specs": ["Cuero legítimo", "Suela antideslizante", "Forro respirable"],
        "descuento_pct": 30, "envio": "Envío gratis", "llega": "Mañana",
    },
    109: {
        "breadcrumbs": ["Home", "Accesorios", "Cinturones"],
        "rating": 4.3, "rating_count": 75,
        "color": "Negro",
        "sizes": ["S (80-90)","M (90-100)","L (100-110)"],
        "specs": ["Cuero sintético premium", "Hebilla metálica mate"],
        "descuento_pct": 5, "envio": "Retiro en tienda C", "llega": "Viernes",
    },
    110: {
        "breadcrumbs": ["Home", "Accesorios", "Relojes"],
        "rating": 4.8, "rating_count": 420,
        "color": "Acero",
        "specs": ["Cuarzo japonés", "Resistencia al agua 5 ATM", "Malla de acero"],
        "warranty": "12 meses",
        "descuento_pct": 22, "envio": "Envío asegurado", "llega": "Miércoles",
    },
}


class Command(BaseCommand):
    help = "Crea categorías, productos y detalles utilizando los datos del proyecto"

    def handle(self, *args, **options):
        # Crear categorías
        cats = {}
        for c in sorted({p["category"] for p in PRODUCTS}):
            cat, _ = Category.objects.get_or_create(name=c, defaults={"slug": slugify(c)})
            cats[c] = cat
        self.stdout.write(self.style.SUCCESS(f"Categorías listas: {', '.join(cats.keys())}"))

        # Crear/actualizar productos y detalles
        for p in PRODUCTS:
            cat = cats[p["category"]]
            prod, created = Product.objects.update_or_create(
                id=p["id"],
                defaults={
                    "name": p["name"],
                    "price": p["price"],
                    "image_url": p["image_url"],
                    "category": cat,
                },
            )
            action = "Creado" if created else "Actualizado"
            self.stdout.write(f"{action} producto {prod.id} - {prod.name}")

            # Detalles por producto
            d = PRODUCT_DETAILS.get(prod.id, {})
            det, _ = ProductDetail.objects.update_or_create(
                product=prod,
                defaults={
                    "rating": d.get("rating", 4.5),
                    "rating_count": d.get("rating_count", 0),
                    "color": d.get("color", ""),
                    "descuento_pct": d.get("descuento_pct", 0),
                    "envio": d.get("envio", ""),
                    "llega": d.get("llega", ""),
                    "warranty": d.get("warranty", ""),
                    "capacity_l": d.get("capacity_l"),
                },
            )

            # Limpieza y carga de colecciones relacionadas
            ProductSize.objects.filter(product=prod).delete()
            for s in d.get("sizes", []):
                ProductSize.objects.create(product=prod, label=s)

            ProductSpec.objects.filter(product=prod).delete()
            for s in d.get("specs", []):
                ProductSpec.objects.create(product=prod, text=s)

            ProductCare.objects.filter(product=prod).delete()
            for s in d.get("care", []):
                ProductCare.objects.create(product=prod, text=s)

            ProductBreadcrumb.objects.filter(product=prod).delete()
            for idx, label in enumerate(d.get("breadcrumbs", ["Home", "Productos"])):
                ProductBreadcrumb.objects.create(product=prod, position=idx, label=label)

        self.stdout.write(self.style.SUCCESS("Productos y detalles cargados correctamente"))
