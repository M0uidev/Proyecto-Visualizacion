import json
from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone


def index(request):
    return render(request, 'pagina1.html')


def pagina2(request):
    return render(request, 'pagina2.html')


def pagina3(request):
    return render(request, 'pagina3.html')


def admin_dashboard(request):
    today = timezone.now().date()
    kpis = [
        {
            "label": "Ventas Totales",
            "value": "$125,430",
            "delta": "+8.2% vs. mes anterior",
        },
        {
            "label": "# Órdenes",
            "value": "1,248",
            "delta": "+5.1% intermensual",
        },
        {
            "label": "Ticket Promedio",
            "value": "$100.60",
            "delta": "+2.3%",
        },
        {
            "label": "% Clientes Nuevos",
            "value": "27%",
            "delta": "+3.4 pts",
        },
    ]

    sales_daily = {
        "dates": [
            today.replace(day=day).strftime("%Y-%m-%d")
            for day in range(1, 8)
        ],
        "sales": [21500, 19800, 22340, 24510, 23870, 25630, 27320],
    }

    top_categories = {
        "categories": [
            "Electrónica",
            "Hogar",
            "Moda",
            "Alimentos",
            "Deportes",
        ],
        "sales": [45210, 31890, 27500, 22340, 18970],
    }

    purchase_distribution = {
        "values": [
            85,
            91,
            95,
            102,
            87,
            115,
            98,
            134,
            122,
            110,
            97,
            142,
            131,
            118,
            108,
            95,
        ]
    }

    recent_orders = [
        {"id": "A-1045", "customer": "Laura Vega", "product": "Smartwatch", "total": "$320", "date": "2024-06-17"},
        {"id": "A-1044", "customer": "Carlos Ruiz", "product": "Laptop 14''", "total": "$980", "date": "2024-06-17"},
        {"id": "A-1043", "customer": "Ana López", "product": "Silla ergonómica", "total": "$210", "date": "2024-06-16"},
        {"id": "A-1042", "customer": "Miguel Torres", "product": "Auriculares", "total": "$150", "date": "2024-06-16"},
        {"id": "A-1041", "customer": "Daniela Pérez", "product": "Cafetera", "total": "$120", "date": "2024-06-16"},
    ]

    context = {
        "filters": {
            "date_range": "01 - 17 Jun 2024",
            "cities": ["Todas", "CDMX", "Monterrey", "Guadalajara", "Puebla"],
            "selected_city": "Todas",
        },
        "kpis": kpis,
        "sales_daily": json.dumps(sales_daily),
        "top_categories": json.dumps(top_categories),
        "purchase_distribution": json.dumps(purchase_distribution),
        "recent_orders": recent_orders,
    }
    return render(request, "admin.html", context)


def worker_dashboard(request):
    now = timezone.localtime()
    profile = {
        "name": "María González",
        "role": "Especialista de Atención",
        "city": "CDMX",
        "timestamp": now.strftime("%d %b %Y • %H:%M"),
    }

    stats = [
        {"label": "Puntualidad", "value": 92},
        {"label": "Órdenes atendidas", "value": 88},
        {"label": "Satisfacción", "value": 95},
        {"label": "Velocidad", "value": 82},
        {"label": "Precisión", "value": 90},
    ]

    schedule = [
        {"day": "Lunes", "shift": "09:00 - 17:00", "status": "Completado"},
        {"day": "Martes", "shift": "09:00 - 17:00", "status": "Completado"},
        {"day": "Miércoles", "shift": "11:00 - 19:00", "status": "Próximo"},
        {"day": "Jueves", "shift": "11:00 - 19:00", "status": "Próximo"},
        {"day": "Viernes", "shift": "09:00 - 17:00", "status": "Próximo"},
        {"day": "Sábado", "shift": "Descanso", "status": "Libre"},
        {"day": "Domingo", "shift": "Descanso", "status": "Libre"},
    ]

    attendance = {
        "days": [
            (now - timedelta(days=idx)).strftime("%d %b")
            for idx in range(13, -1, -1)
        ],
        "values": [1, 1, 1, 0.5, 1, 1, 1, 1, 0.8, 1, 1, 1, 1, 0.9],
    }

    notes = [
        "Recordar seguimiento VIP a cliente 3256.",
        "Confirmar inventario de repuestos antes del viernes.",
        "Revisar feedback del turno nocturno.",
    ]

    context = {
        "profile": profile,
        "stats": stats,
        "stats_chart": json.dumps({
            "labels": [metric["label"] for metric in stats],
            "values": [metric["value"] for metric in stats],
        }),
        "attendance": json.dumps(attendance),
        "schedule": schedule,
        "notes": notes,
    }
    return render(request, "worker.html", context)
