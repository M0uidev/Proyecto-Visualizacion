import os
import django
import random
import sys

# Add the project directory to the sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectoOnichan.settings')
django.setup()

from appOnichan.models import Product, Category, ProductDetail

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
        {"id": 101, "name": "Smartphone Galaxy S24", "price": 899990, "cat": "electronica", "img": "galaxy_s24.jpg", "desc": "El último smartphone de Samsung con pantalla AMOLED y cámara de alta resolución."},
        {"id": 102, "name": "Laptop ProBook 15", "price": 750000, "cat": "electronica", "img": "laptop_probook.jpg", "desc": "Laptop potente para trabajo y estudio, con procesador i7 y 16GB de RAM."},
        {"id": 103, "name": "Audífonos NoiseCancelling", "price": 120000, "cat": "electronica", "img": "headphones_nc.jpg", "desc": "Audífonos inalámbricos con cancelación de ruido activa para una experiencia inmersiva."},
        {"id": 104, "name": "Smartwatch Fit 3", "price": 85000, "cat": "electronica", "img": "smartwatch_fit3.jpg", "desc": "Reloj inteligente con monitoreo de salud, GPS y notificaciones."},
        {"id": 105, "name": "Tablet Tab S9", "price": 450000, "cat": "electronica", "img": "tablet_s9.jpg", "desc": "Tablet versátil con S Pen incluido, ideal para creatividad y productividad."},
        
        # Ropa
        {"id": 201, "name": "Polera Básica Algodón", "price": 12990, "cat": "ropa", "img": "tshirt_basic.jpg", "desc": "Polera 100% algodón, cómoda y duradera, disponible en varios colores."},
        {"id": 202, "name": "Jeans Slim Fit", "price": 29990, "cat": "ropa", "img": "jeans_slim.jpg", "desc": "Jeans de corte ajustado, modernos y con tela elástica para mayor comodidad."},
        {"id": 203, "name": "Chaqueta Impermeable", "price": 59990, "cat": "ropa", "img": "jacket_rain.jpg", "desc": "Chaqueta ligera y resistente al agua, perfecta para días lluviosos."},
        {"id": 204, "name": "Zapatillas Running", "price": 45990, "cat": "ropa", "img": "sneakers_run.jpg", "desc": "Zapatillas diseñadas para correr, con amortiguación y soporte superior."},
        {"id": 205, "name": "Polerón con Capucha", "price": 24990, "cat": "ropa", "img": "hoodie.jpg", "desc": "Polerón abrigado con capucha y bolsillo canguro, estilo casual."},

        # Hogar
        {"id": 301, "name": "Juego de Sábanas 2 Plazas", "price": 35000, "cat": "hogar", "img": "bedsheets.jpg", "desc": "Juego de sábanas suaves de 300 hilos, incluye sábana bajera, encimera y fundas."},
        {"id": 302, "name": "Lámpara de Escritorio LED", "price": 18990, "cat": "hogar", "img": "lamp_desk.jpg", "desc": "Lámpara moderna con luz LED regulable y puerto USB de carga."},
        {"id": 303, "name": "Set de Ollas Antiadherentes", "price": 65000, "cat": "hogar", "img": "cookware_set.jpg", "desc": "Set de 5 piezas con recubrimiento antiadherente de alta calidad."},
        {"id": 304, "name": "Cafetera Programable", "price": 42990, "cat": "hogar", "img": "coffee_maker.jpg", "desc": "Cafetera de goteo programable para tener tu café listo al despertar."},
        {"id": 305, "name": "Toallas de Baño Premium", "price": 15990, "cat": "hogar", "img": "towels.jpg", "desc": "Toallas de algodón egipcio, ultra absorbentes y suaves al tacto."},

        # Juguetes
        {"id": 401, "name": "Set de Bloques de Construcción", "price": 25990, "cat": "juguetes", "img": "blocks_set.jpg", "desc": "Set de 500 piezas para construir y desarrollar la creatividad."},
        {"id": 402, "name": "Muñeca Articulada", "price": 19990, "cat": "juguetes", "img": "doll.jpg", "desc": "Muñeca con múltiples articulaciones y accesorios de moda."},
        {"id": 403, "name": "Auto a Control Remoto", "price": 32990, "cat": "juguetes", "img": "rc_car.jpg", "desc": "Auto todo terreno a control remoto, alta velocidad y resistencia."},
        {"id": 404, "name": "Juego de Mesa Familiar", "price": 22990, "cat": "juguetes", "img": "board_game.jpg", "desc": "Divertido juego de estrategia para disfrutar en familia."},
        {"id": 405, "name": "Peluche Oso Gigante", "price": 28990, "cat": "juguetes", "img": "teddy_bear.jpg", "desc": "Oso de peluche gigante, suave y abrazable, el regalo perfecto."},

        # Deportes
        {"id": 501, "name": "Balón de Fútbol Profesional", "price": 18990, "cat": "deportes", "img": "soccer_ball.jpg", "desc": "Balón oficial tamaño 5, cosido a mano y resistente."},
        {"id": 502, "name": "Mat de Yoga Antideslizante", "price": 14990, "cat": "deportes", "img": "yoga_mat.jpg", "desc": "Mat de yoga ecológico con superficie antideslizante para mayor estabilidad."},
        {"id": 503, "name": "Mancuernas 5kg (Par)", "price": 21990, "cat": "deportes", "img": "dumbbells.jpg", "desc": "Par de mancuernas de vinilo, ideales para entrenamiento en casa."},
        {"id": 504, "name": "Botella de Agua Deportiva", "price": 8990, "cat": "deportes", "img": "water_bottle.jpg", "desc": "Botella libre de BPA, resistente a golpes y con tapa antiderrame."},
        {"id": 505, "name": "Raqueta de Tenis", "price": 55000, "cat": "deportes", "img": "tennis_racket.jpg", "desc": "Raqueta ligera de grafito, ideal para principiantes e intermedios."},
    ]

    for p_data in products_data:
        # Use static path for images
        img_url = f"/static/images/productos/{p_data['img']}"
        
        product, created = Product.objects.update_or_create(
            id=p_data["id"],
            defaults={
                "name": p_data["name"],
                "price": p_data["price"],
                "image_url": img_url,
                "category": categories[p_data["cat"]],
                "description": p_data.get("desc", ""),
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
