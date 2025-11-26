import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectoOnichan.settings')
django.setup()

from appOnichan.models import Product, Category, ProductDetail, ProductSize

def populate():
    # Categories
    categories_data = [
        {"name": "Electrónica", "slug": "electronica"},
        {"name": "Ropa", "slug": "ropa"},
        {"name": "Hogar", "slug": "hogar"},
        {"name": "Juguetes", "slug": "juguetes"},
        {"name": "Deportes", "slug": "deportes"},
    ]

    categories = {}
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            slug=cat_data["slug"],
            defaults={"name": cat_data["name"]}
        )
        categories[cat.slug] = cat
        print(f"Category: {cat.name}")

    # Products
    products_data = [
        # Electrónica
        {"id": 101, "name": "Smartphone Galaxy S24", "price": 899990, "cat": "electronica", "img": "galaxy_s24.jpg"},
        {"id": 102, "name": "Laptop ProBook 15", "price": 750000, "cat": "electronica", "img": "laptop_probook.jpg"},
        {"id": 103, "name": "Audífonos NoiseCancelling", "price": 120000, "cat": "electronica", "img": "headphones_nc.jpg"},
        {"id": 104, "name": "Smartwatch Fit 3", "price": 85000, "cat": "electronica", "img": "smartwatch_fit3.jpg"},
        {"id": 105, "name": "Tablet Tab S9", "price": 450000, "cat": "electronica", "img": "tablet_s9.jpg"},
        
        # Ropa
        {"id": 201, "name": "Polera Básica Algodón", "price": 12990, "cat": "ropa", "img": "tshirt_basic.jpg"},
        {"id": 202, "name": "Jeans Slim Fit", "price": 29990, "cat": "ropa", "img": "jeans_slim.jpg"},
        {"id": 203, "name": "Chaqueta Impermeable", "price": 59990, "cat": "ropa", "img": "jacket_rain.jpg"},
        {"id": 204, "name": "Zapatillas Running", "price": 45990, "cat": "ropa", "img": "sneakers_run.jpg"},
        {"id": 205, "name": "Polerón con Capucha", "price": 24990, "cat": "ropa", "img": "hoodie.jpg"},

        # Hogar
        {"id": 301, "name": "Juego de Sábanas 2 Plazas", "price": 35000, "cat": "hogar", "img": "bedsheets.jpg"},
        {"id": 302, "name": "Lámpara de Escritorio LED", "price": 18990, "cat": "hogar", "img": "lamp_desk.jpg"},
        {"id": 303, "name": "Set de Ollas Antiadherentes", "price": 65000, "cat": "hogar", "img": "cookware_set.jpg"},
        {"id": 304, "name": "Cafetera Programable", "price": 42990, "cat": "hogar", "img": "coffee_maker.jpg"},
        {"id": 305, "name": "Toallas de Baño Premium", "price": 15990, "cat": "hogar", "img": "towels.jpg"},

        # Juguetes
        {"id": 401, "name": "Set de Bloques de Construcción", "price": 25990, "cat": "juguetes", "img": "blocks_set.jpg"},
        {"id": 402, "name": "Muñeca Articulada", "price": 19990, "cat": "juguetes", "img": "doll.jpg"},
        {"id": 403, "name": "Auto a Control Remoto", "price": 32990, "cat": "juguetes", "img": "rc_car.jpg"},
        {"id": 404, "name": "Juego de Mesa Familiar", "price": 22990, "cat": "juguetes", "img": "board_game.jpg"},
        {"id": 405, "name": "Peluche Oso Gigante", "price": 28990, "cat": "juguetes", "img": "teddy_bear.jpg"},

        # Deportes
        {"id": 501, "name": "Balón de Fútbol Profesional", "price": 18990, "cat": "deportes", "img": "soccer_ball.jpg"},
        {"id": 502, "name": "Mat de Yoga Antideslizante", "price": 14990, "cat": "deportes", "img": "yoga_mat.jpg"},
        {"id": 503, "name": "Mancuernas 5kg (Par)", "price": 21990, "cat": "deportes", "img": "dumbbells.jpg"},
        {"id": 504, "name": "Botella de Agua Deportiva", "price": 8990, "cat": "deportes", "img": "water_bottle.jpg"},
        {"id": 505, "name": "Raqueta de Tenis", "price": 55000, "cat": "deportes", "img": "tennis_racket.jpg"},
    ]

    for p_data in products_data:
        # Use static path for images
        img_url = f"/static/img/products/{p_data['img']}"
        
        product, created = Product.objects.update_or_create(
            id=p_data["id"],
            defaults={
                "name": p_data["name"],
                "price": p_data["price"],
                "image_url": img_url,
                "category": categories[p_data["cat"]],
                "stock": random.randint(10, 100)
            }
        )
        
        # Create detail if not exists
        ProductDetail.objects.get_or_create(
            product=product,
            defaults={
                "rating": round(random.uniform(3.5, 5.0), 1),
                "rating_count": random.randint(5, 50),
                "color": random.choice(["Negro", "Blanco", "Azul", "Rojo", "Verde"]),
                "envio": "Gratis",
                "llega": "Mañana",
                "warranty": "6 meses"
            }
        )
        
        print(f"Product: {product.name}")

if __name__ == '__main__':
    populate()
