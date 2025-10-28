import json
from datetime import timedelta
from random import randint

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET


STORES = {
    "A": "Tienda A",
    "B": "Tienda B",
    "C": "Tienda C",
}


def format_clp(amount: int) -> str:
    return f"$ {amount:,.0f}".replace(",", ".")


def index(request):
    return render(request, "pagina1.html")


def pagina2(request):
    return render(request, "pagina2.html")


def pagina3(request):
    return render(request, "pagina3.html")


def admin_dashboard(request):
    today = timezone.now().date()
    dates = [(today - timedelta(days=offset)).strftime("%d-%m-%Y") for offset in range(13, -1, -1)]
    sales_values = [
        245_500,
        258_300,
        249_800,
        262_900,
        271_400,
        275_600,
        289_900,
        301_200,
        297_800,
        312_500,
        326_400,
        331_900,
        344_200,
        352_100,
    ]

    kpis = [
        {"label": "Ventas Totales", "value": format_clp(sum(sales_values)), "delta": "+7,4% vs mes anterior"},
        {"label": "Ticket Promedio", "value": format_clp(58_900), "delta": "+2,1%"},
        {"label": "Clientes Nuevos", "value": "284", "delta": "+18 clientes"},
        {"label": "Órdenes Completadas", "value": "1.642", "delta": "+5,6%"},
    ]

    top_categories = {
        "categories": ["Electrónica", "Hogar", "Moda", "Juguetería", "Deportes"],
        "sales": [982_300, 756_400, 643_200, 521_800, 498_600],
    }

    purchase_values = [
        34_900,
        42_500,
        55_800,
        61_200,
        48_900,
        72_400,
        81_500,
        69_800,
        58_300,
        63_700,
        54_100,
        77_900,
        88_400,
        92_100,
        66_800,
        59_700,
        71_200,
        83_500,
        94_900,
        102_300,
    ]
    bin_size = 20_000
    min_value = 20_000
    bins = []
    for index in range(5):
        start = min_value + index * bin_size
        end = min_value + (index + 1) * bin_size
        count = sum(1 for value in purchase_values if start <= value < end)
        bins.append(
            {
                "start": start,
                "end": end,
                "size": bin_size,
                "count": count,
                "label": f"{format_clp(start)} - {format_clp(end)}",
            }
        )

    recent_orders = [
        {"id": "A-2081", "customer": "Valentina Ríos", "product": "Notebook 14\"", "total": format_clp(489_900), "date": "14-07-2024"},
        {"id": "B-2079", "customer": "Felipe Morales", "product": "Audífonos inalámbricos", "total": format_clp(89_990), "date": "13-07-2024"},
        {"id": "C-2078", "customer": "Claudia Peña", "product": "Silla ergonómica", "total": format_clp(179_500), "date": "13-07-2024"},
        {"id": "A-2077", "customer": "Ignacio Vera", "product": "Smartwatch deportivo", "total": format_clp(129_990), "date": "12-07-2024"},
        {"id": "B-2076", "customer": "Camila Torres", "product": "Cafetera premium", "total": format_clp(159_900), "date": "12-07-2024"},
    ]

    filters = {
        "date_range": f"{dates[0]} al {dates[-1]}",
        "last_updated": today.strftime("%d-%m-%Y 09:00"),
        "stores": [{"value": key, "label": label} for key, label in STORES.items()],
        "selected_store": "A",
        "selected_store_label": STORES["A"],
    }

    context = {
        "filters": filters,
        "kpis": kpis,
        "sales_daily": json.dumps({"dates": dates, "sales": sales_values}),
        "top_categories": json.dumps(top_categories),
        "purchase_distribution": json.dumps(
            {
                "labels": [bin_item["label"] for bin_item in bins],
                "counts": [bin_item["count"] for bin_item in bins],
                "bins": bins,
            }
        ),
        "recent_orders": recent_orders,
    }
    return render(request, "admin.html", context)


def worker_dashboard(request):
    now = timezone.localtime()
    profile = {
        "name": "Constanza Araya",
        "role": "Especialista de Atención",
        "city": "Santiago",
        "timestamp": now.strftime("%d-%m-%Y · %H:%M"),
    }

    stats = [
        {"label": "Puntualidad", "value": 94},
        {"label": "Órdenes Atendidas", "value": 88},
        {"label": "Velocidad", "value": 82},
        {"label": "Precisión", "value": 91},
        {"label": "Satisfacción", "value": 96},
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

    attendance_labels = [
        (now - timedelta(days=offset)).strftime("%d-%m") for offset in range(13, -1, -1)
    ]
    attendance_dates = [
        (now - timedelta(days=offset)).strftime("%d-%m-%Y") for offset in range(13, -1, -1)
    ]
    attendance_values = [1, 1, 1, 0.75, 1, 1, 1, 0.85, 1, 1, 0.9, 1, 1, 1]

    notes = [
        "Revisar feedback de clientes premium antes de las 12:00.",
        "Confirmar stock de accesorios en Tienda B.",
        "Coordinar capacitación de nuevos ingresos para el viernes.",
    ]

    context = {
        "profile": profile,
        "worker_id": "W-204",
        "stats": stats,
        "stats_chart": json.dumps({
            "labels": [metric["label"] for metric in stats],
            "values": [metric["value"] for metric in stats],
        }),
        "attendance": json.dumps({
            "labels": attendance_labels,
            "dates": attendance_dates,
            "values": attendance_values,
        }),
        "schedule": schedule,
        "notes": notes,
    }
    return render(request, "worker.html", context)


@require_GET
def drill_orders(request):
    date = request.GET.get("date") or timezone.now().strftime("%d-%m-%Y")
    store = request.GET.get("store", "A").upper()
    store_label = STORES.get(store, STORES["A"])

    sample_amounts = [randint(58_000, 142_000) for _ in range(5)]
    rows = [
        {
            "ID": f"{store}-{date.replace('-', '')}-{index+1}",
            "Cliente": f"Cliente {index + 1}",
            "Total": format_clp(amount),
            "Fecha": date,
        }
        for index, amount in enumerate(sample_amounts)
    ]

    chart = {
        "type": "bar",
        "data": {
            "labels": [row["ID"] for row in rows],
            "datasets": [
                {
                    "label": f"Órdenes · {store_label}",
                    "data": sample_amounts,
                    "backgroundColor": "#2563eb",
                    "borderRadius": 8,
                    "maxBarThickness": 48,
                }
            ],
        },
        "options": {
            "scales": {
                "y": {"beginAtZero": True},
            },
        },
    }
    return JsonResponse({"chart": chart, "rows": rows})


@require_GET
def drill_category(request):
    category = request.GET.get("name", "Categoría")
    store = request.GET.get("store", "A").upper()
    store_label = STORES.get(store, STORES["A"])
    base_details = {
        "Electrónica": [
            ("Accesorios", 382_000),
            ("Gadgets", 275_300),
            ("Computación", 325_400),
        ],
        "Hogar": [
            ("Decoración", 189_400),
            ("Cocina", 231_500),
            ("Electrodomésticos", 255_000),
        ],
        "Moda": [
            ("Calzado", 173_800),
            ("Ropa", 214_600),
            ("Accesorios", 128_700),
        ],
        "Juguetería": [
            ("Educativos", 142_800),
            ("Coleccionables", 121_500),
            ("Creativos", 118_400),
        ],
        "Deportes": [
            ("Fitness", 165_900),
            ("Outdoor", 152_300),
            ("Accesorios", 134_200),
        ],
    }

    details = base_details.get(category, [("General", 198_000), ("Otros", 154_000)])
    rows = [
        {"Subcategoría": name, "Venta": format_clp(amount), "Tienda": store_label}
        for name, amount in details
    ]

    chart = {
        "type": "bar",
        "data": {
            "labels": [name for name, _ in details],
            "datasets": [
                {
                    "label": f"Detalle · {store_label}",
                    "data": [amount for _, amount in details],
                    "backgroundColor": "#10b981",
                    "borderRadius": 8,
                    "maxBarThickness": 42,
                }
            ],
        },
        "options": {
            "indexAxis": "y",
            "scales": {"x": {"beginAtZero": True}},
        },
    }
    return JsonResponse({"chart": chart, "rows": rows})


@require_GET
def drill_purchase_bin(request):
    store = request.GET.get("store", "A").upper()
    store_label = STORES.get(store, STORES["A"])
    try:
        start = int(float(request.GET.get("bin_start", 0)))
    except (TypeError, ValueError):
        start = 0
    try:
        end = int(float(request.GET.get("bin_end", start + 20_000)))
    except (TypeError, ValueError):
        end = start + 20_000

    tickets = [start + randint(1_500, 18_000) for _ in range(6)]
    ordered_amounts = sorted(tickets, reverse=True)
    rows = [
        {
            "Ticket": f"{store}-{index+1}",
            "Monto": format_clp(amount),
            "Fecha": (timezone.now() - timedelta(days=index)).strftime("%d-%m-%Y"),
        }
        for index, amount in enumerate(ordered_amounts)
    ]

    chart = {
        "type": "bar",
        "data": {
            "labels": [row["Ticket"] for row in rows],
            "datasets": [
                {
                    "label": f"Tickets · {store_label}",
                    "data": ordered_amounts,
                    "backgroundColor": "#f97316",
                    "borderRadius": 8,
                    "maxBarThickness": 48,
                }
            ],
        },
        "options": {
            "scales": {
                "y": {"beginAtZero": True},
            },
        },
    }
    return JsonResponse({"chart": chart, "rows": rows})


@require_GET
def drill_metric(request):
    metric = request.GET.get("name", "Métrica")
    base_value = {
        "Puntualidad": 94,
        "Órdenes Atendidas": 88,
        "Velocidad": 82,
        "Precisión": 91,
        "Satisfacción": 96,
    }.get(metric, 85)

    today = timezone.now().date()
    dates = [(today - timedelta(days=offset)).strftime("%d-%m") for offset in range(29, -1, -1)]
    values = [max(60, min(100, base_value + randint(-6, 6))) for _ in dates]
    rows = [
        {"Fecha": date, "Índice": f"{value}%"}
        for date, value in list(zip(dates, values))[-7:]
    ]

    chart = {
        "type": "line",
        "data": {
            "labels": dates,
            "datasets": [
                {
                    "label": f"{metric}",
                    "data": values,
                    "borderColor": "#8b5cf6",
                    "backgroundColor": "rgba(139, 92, 246, 0.16)",
                    "tension": 0.35,
                    "fill": True,
                }
            ],
        },
        "options": {
            "scales": {"y": {"suggestedMin": 50, "suggestedMax": 105}},
        },
    }
    return JsonResponse({"chart": chart, "rows": rows})


@require_GET
def drill_shift(request):
    date = request.GET.get("date") or timezone.now().strftime("%d-%m-%Y")
    rows = [
        {"Fecha": date, "Entrada": "09:00", "Salida": "17:00", "Observación": "Turno completado"},
        {"Fecha": date, "Entrada": "17:10", "Salida": "17:40", "Observación": "Cierre de incidencias"},
    ]

    chart = {
        "type": "bar",
        "data": {
            "labels": ["Horas trabajadas"],
            "datasets": [
                {
                    "label": f"Turno · {date}",
                    "data": [7.5],
                    "backgroundColor": "#2563eb",
                    "borderRadius": 8,
                    "maxBarThickness": 72,
                }
            ],
        },
        "options": {"scales": {"y": {"suggestedMax": 9, "beginAtZero": True}}},
    }
    return JsonResponse({"chart": chart, "rows": rows})
