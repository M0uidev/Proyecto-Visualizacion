import json

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

def iniciosesionadmin(request):
    return render(request, "iniciosesionadmin.html")

def pagina3(request):
    return render(request, "pagina3.html")

def dashboardadmin(request):
    dashboard_data = {
        "kpis": {
            "pedidos_hoy": {"value": 28, "trend": "+4 vs. ayer"},
            "pendientes": {"value": 12, "trend": "-2 respecto a la semana pasada"},
            "ingresos_7d": {"value": 1987500, "trend": "+6% semana previa", "isCurrency": True},
        },
        "lineChart": {
            "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
            "values": [20, 24, 21, 27, 32, 34, 26],
            "detalles": {
                "Lun": {"Entregados": 16, "Pendientes": 4},
                "Mar": {"Entregados": 19, "Pendientes": 5},
                "Mié": {"Entregados": 17, "Pendientes": 4},
                "Jue": {"Entregados": 22, "Pendientes": 5},
                "Vie": {"Entregados": 26, "Pendientes": 6},
                "Sáb": {"Entregados": 28, "Pendientes": 6},
                "Dom": {"Entregados": 21, "Pendientes": 5},
            },
        },
        "topProducts": {
            "labels": ["Polera Oversized", "Zapatillas Urban", "Chaqueta Azul", "Mochila Explorer"],
            "values": [48, 39, 31, 24],
            "detalles": {
                "Polera Oversized": {"Negro / M": 16, "Negro / L": 14, "Blanco / M": 10, "Blanco / L": 8},
                "Zapatillas Urban": {"41": 13, "42": 11, "43": 9, "44": 6},
                "Chaqueta Azul": {"S": 8, "M": 10, "L": 7, "XL": 6},
                "Mochila Explorer": {"Negro": 11, "Gris": 7, "Arena": 6},
            },
        },
        "categoryRevenue": {
            "labels": ["Ropa", "Calzado", "Accesorios", "Equipaje"],
            "values": [580000, 436500, 208000, 160500],
            "detalles": {
                "Ropa": {"Online": 350000, "Tienda": 230000},
                "Calzado": {"Online": 260000, "Tienda": 176500},
                "Accesorios": {"Online": 125000, "Tienda": 83000},
                "Equipaje": {"Online": 90500, "Tienda": 70000},
            },
        },
    }

    context = {
        "data_json": json.dumps(dashboard_data),
    }

    return render(request, "dashboardadmin.html", context)

def pagina3(request):
    orders_data = {
        "orders": [
            {
                "id": "PED-001",
                "fecha": "2025-11-03",
                "cliente": "Juan Pérez",
                "total": 54990,
                "estado": "Pendiente",
                "productos": [
                    {"nombre": "Polera Oversized Negra", "cantidad": 2},
                    {"nombre": "Gorro Beanie Gris", "cantidad": 1}
                ]
            },
            {
                "id": "PED-002",
                "fecha": "2025-11-03",
                "cliente": "María González",
                "total": 89980,
                "estado": "Despachado",
                "productos": [
                    {"nombre": "Zapatillas Urban Classic", "cantidad": 1},
                    {"nombre": "Cinturón Minimal", "cantidad": 2}
                ]
            },
            {
                "id": "PED-003",
                "fecha": "2025-11-02",
                "cliente": "Carlos Rodríguez",
                "total": 34990,
                "estado": "Entregado",
                "productos": [
                    {"nombre": "Chaqueta Denim Azul", "cantidad": 1}
                ]
            }
        ],
        "estadisticas": {
            "total_pedidos": 3,
            "pendientes": 1,
            "despachados": 1,
            "entregados": 1,
            "cancelados": 0
        }
    }
    
    return render(request, "pagina3.html", {"data": json.dumps(orders_data)})

def pagina3(request):
    # Generar 20 pedidos de ejemplo
    pedidos = []
    estados = ["Pendiente", "Despachado", "Entregado", "Cancelado"]
    nombres = ["Juan Pérez", "María González", "Carlos Rodríguez", "Ana Silva", "Luis Torres", 
              "Carmen Ruiz", "Diego Muñoz", "Patricia Lagos", "Roberto Vera", "Isabel Ortiz"]
    productos = [
        {"nombre": "Polera Oversized Negra", "precio": 14990},
        {"nombre": "Zapatillas Urban Classic", "precio": 39990},
        {"nombre": "Pantalón Cargo Verde", "precio": 29990},
        {"nombre": "Chaqueta Denim Azul", "precio": 34990},
        {"nombre": "Gorro Beanie Gris", "precio": 9990},
        {"nombre": "Polerón Essential Blanco", "precio": 25990},
        {"nombre": "Mochila Explorer Negra", "precio": 27990},
        {"nombre": "Botines Urbanos Cuero", "precio": 49990},
    ]
    
    import random
    from datetime import datetime, timedelta

    for i in range(1, 21):
        # Generar fecha aleatoria en los últimos 7 días
        dias_atras = random.randint(0, 7)
        fecha = datetime.now() - timedelta(days=dias_atras)
        
        # Seleccionar productos aleatorios para el pedido
        productos_pedido = []
        num_productos = random.randint(1, 3)
        productos_seleccionados = random.sample(productos, num_productos)
        total = 0
        
        for producto in productos_seleccionados:
            cantidad = random.randint(1, 3)
            productos_pedido.append({
                "nombre": producto["nombre"],
                "cantidad": cantidad
            })
            total += producto["precio"] * cantidad

        pedido = {
            "id": f"PED-{i:03d}",
            "fecha": fecha.strftime("%Y-%m-%d"),
            "cliente": random.choice(nombres),
            "total": total,
            "estado": random.choice(estados),
            "productos": productos_pedido
        }
        pedidos.append(pedido)
    
    # Ordenar por fecha más reciente primero
    pedidos.sort(key=lambda x: x["fecha"], reverse=True)
    
    # Calcular estadísticas
    estadisticas = {
        "total_pedidos": len(pedidos),
        "pendientes": sum(1 for p in pedidos if p["estado"] == "Pendiente"),
        "despachados": sum(1 for p in pedidos if p["estado"] == "Despachado"),
        "entregados": sum(1 for p in pedidos if p["estado"] == "Entregado"),
        "cancelados": sum(1 for p in pedidos if p["estado"] == "Cancelado"),
        "total_ventas": sum(p["total"] for p in pedidos)
    }
    
    orders_data = {
        "orders": pedidos,
        "estadisticas": estadisticas
    }
    
    return render(request, "pagina3.html", {"data": json.dumps(orders_data)})

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
