from django.shortcuts import render
from django.http import Http404

PRODUCTOS = [
    {"id": 101, "name": "Polera Oversized Negra",    "price": 14990, "image_url": "/static/images/productos/polera_negra.png",     "is_new": True},
    {"id": 102, "name": "Zapatillas Urban Classic",   "price": 39990, "image_url": "/static/images/productos/zapatillas_urban.png", "is_new": False},
    {"id": 103, "name": "Pantalón Cargo Verde",       "price": 29990, "image_url": "/static/images/productos/pantalon_cargo.png",   "is_new": True},
    {"id": 104, "name": "Chaqueta Denim Azul",        "price": 34990, "image_url": "/static/images/productos/chaqueta_denim.png",   "is_new": False},
    {"id": 105, "name": "Gorro Beanie Gris",          "price": 9990, "image_url": "/static/images/productos/gorro_gris.png",       "is_new": True},
    {"id": 106, "name": "Polerón Essential Blanco",   "price": 25990, "image_url": "/static/images/productos/poleron_blanco.png",   "is_new": False},
    {"id": 107, "name": "Mochila Explorer Negra",     "price": 27990, "image_url": "/static/images/productos/mochila_negra.png",    "is_new": False},
    {"id": 108, "name": "Botines Urbanos Cuero",      "price": 49990, "image_url": "/static/images/productos/botines_cuero.png",    "is_new": True},
    {"id": 109, "name": "Cinturón Minimal",           "price": 12990, "image_url": "/static/images/productos/cinturon.png",         "is_new": False},
    {"id": 110, "name": "Reloj Vintage Metal",        "price": 55990, "image_url": "/static/images/productos/reloj_metal.png",      "is_new": True},
]

# Detalle con sentido por producto (puedes tunear lo que quieras)
PRODUCT_DETAILS = {
    101: {  # Polera
        "breadcrumbs": ["Home", "Moda", "Poleras"],
        "rating": 4.6, "rating_count": 384,
        "color": "Negro",
        "sizes": ["S", "M", "L", "XL"],
        "specs": ["Algodón 100% peinado 220 GSM", "Fit oversized unisex", "Cuello reforzado", "No destiñe"],
        "care": ["Lavar a 30°C", "No cloro", "Planchar tibio del revés"],
        "descuento_pct": 15, "envio": "Envío gratis", "llega": "Mañana",
    },
    102: {  # Zapatillas
        "breadcrumbs": ["Home", "Calzado", "Zapatillas"],
        "rating": 4.8, "rating_count": 1207,
        "color": "Blanco/Negro",
        "sizes": ["38","39","40","41","42","43","44"],
        "specs": ["Suela EVA antideslizante", "Plantilla memory foam", "Capellada respirable"],
        "descuento_pct": 25, "envio": "Retiro hoy en tienda B", "llega": "Jueves",
    },
    103: {  # Pantalón cargo
        "breadcrumbs": ["Home", "Moda", "Pantalones"],
        "rating": 4.5, "rating_count": 228,
        "color": "Verde oliva",
        "sizes": ["28","30","32","34","36"],
        "specs": ["Tela ripstop stretch", "6 bolsillos funcionales", "Cintura ajustable"],
        "descuento_pct": 20, "envio": "Envío gratis", "llega": "Mañana",
    },
    104: {  # Chaqueta
        "breadcrumbs": ["Home", "Moda", "Chaquetas"],
        "rating": 4.7, "rating_count": 312,
        "color": "Azul índigo",
        "sizes": ["S","M","L","XL"],
        "specs": ["Denim 12 oz", "Costuras reforzadas", "Botones metálicos"],
        "descuento_pct": 10, "envio": "Despacho programado", "llega": "Viernes",
    },
    105: {  # Beanie
        "breadcrumbs": ["Home", "Accesorios", "Gorros"],
        "rating": 4.4, "rating_count": 97,
        "color": "Gris",
        "specs": ["Tejido acrílico hipoalergénico", "Unisex", "Talla única"],
        "descuento_pct": 0, "envio": "Retiro hoy en tienda A", "llega": "Mañana",
    },
    106: {  # Polerón
        "breadcrumbs": ["Home", "Moda", "Polerones"],
        "rating": 4.6, "rating_count": 541,
        "color": "Blanco",
        "sizes": ["S","M","L","XL"],
        "specs": ["French terry 300 GSM", "Capucha forrada", "Bolsillo canguro"],
        "descuento_pct": 18, "envio": "Envío gratis", "llega": "Mañana",
    },
    107: {  # Mochila
        "breadcrumbs": ["Home", "Accesorios", "Mochilas"],
        "rating": 4.7, "rating_count": 660,
        "color": "Negro",
        "capacity_l": 22,
        "specs": ["Compartimento laptop 15.6\"", "Tela repelente al agua", "Bolsillo oculto"],
        "descuento_pct": 12, "envio": "Envío a domicilio", "llega": "Jueves",
    },
    108: {  # Botines
        "breadcrumbs": ["Home", "Calzado", "Botines"],
        "rating": 4.9, "rating_count": 188,
        "color": "Cuero café",
        "sizes": ["39","40","41","42","43"],
        "specs": ["Cuero legítimo", "Suela antideslizante", "Forro respirable"],
        "descuento_pct": 30, "envio": "Envío gratis", "llega": "Mañana",
    },
    109: {  # Cinturón
        "breadcrumbs": ["Home", "Accesorios", "Cinturones"],
        "rating": 4.3, "rating_count": 75,
        "color": "Negro",
        "sizes": ["S (80-90)","M (90-100)","L (100-110)"],
        "specs": ["Cuero sintético premium", "Hebilla metálica mate"],
        "descuento_pct": 5, "envio": "Retiro en tienda C", "llega": "Viernes",
    },
    110: {  # Reloj
        "breadcrumbs": ["Home", "Accesorios", "Relojes"],
        "rating": 4.8, "rating_count": 420,
        "color": "Acero",
        "specs": ["Cuarzo japonés", "Resistencia al agua 5 ATM", "Malla de acero"],
        "warranty": "12 meses",
        "descuento_pct": 22, "envio": "Envío asegurado", "llega": "Miércoles",
    },
}

def index(request):
    return pagina1(request)

def pagina1(request):
    return render(request, "pagina1.html", {"productos": PRODUCTOS})

def iniciosesiontrabajador(request):
    return render(request, "iniciosesiontrabajador.html")

def pagina3(request):
    return render(request, "pagina3.html")

def dashboardtrabajador(request):
    return render(request, "dashboardtrabajador.html")

def producto_detalle(request, pid: int):
    producto = next((p for p in PRODUCTOS if p["id"] == pid), None)
    if not producto:
        raise Http404("Producto no encontrado")

    # Detalle específico si existe, si no, uno base.
    d = PRODUCT_DETAILS.get(pid, {
        "breadcrumbs": ["Home", "Productos"],
        "rating": 4.5, "rating_count": 100,
        "color": "Único",
        "specs": ["Producto de alta calidad"],
        "descuento_pct": 0, "envio": "Envío a todo Chile", "llega": "Próxima semana",
    })

    # Precio original si hay descuento
    precio = producto["price"]
    descuento = d.get("descuento_pct", 0)
    d["precio_original"] = round(precio / (1 - descuento/100)) if descuento else None

    return render(request, "producto_detalle.html", {"p": producto, "d": d})
