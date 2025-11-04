import calendar
import random
from datetime import date

from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone


MONTH_LABELS = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

WEEKDAY_LABELS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

WORKER_PROFILES = {
    "Ana Rojas": {
        "commission_rate": 0.12,
        "clients_range": (35, 58),
        "avg_ticket": 78000,
        "seed": "ana_rojas",
    },
    "Luis Fernández": {
        "commission_rate": 0.09,
        "clients_range": (28, 52),
        "avg_ticket": 69000,
        "seed": "luis_fernandez",
    },
    "Sofía Ramírez": {
        "commission_rate": 0.15,
        "clients_range": (42, 65),
        "avg_ticket": 82000,
        "seed": "sofia_ramirez",
    },
    "Default": {
        "commission_rate": 0.1,
        "clients_range": (30, 50),
        "avg_ticket": 72000,
        "seed": "default_worker",
    },
}


def index(request):
    return pagina1(request)


def pagina1(request):
    productos = [
        {
            "name": "Polera Oversized Negra",
            "price": 14990,
            "image_url": "/static/images/productos/polera_negra.png",
            "is_new": True,
            "detail_url": "#",
        },
        {
            "name": "Zapatillas Urban Classic",
            "price": 39990,
            "image_url": "/static/images/productos/zapatillas_urban.png",
            "is_new": False,
            "detail_url": "#",
        },
        {
            "name": "Pantalón Cargo Verde",
            "price": 29990,
            "image_url": "/static/images/productos/pantalon_cargo.png",
            "is_new": True,
            "detail_url": "#",
        },
        {
            "name": "Chaqueta Denim Azul",
            "price": 34990,
            "image_url": "/static/images/productos/chaqueta_denim.png",
            "is_new": False,
            "detail_url": "#",
        },
        {
            "name": "Gorro Beanie Gris",
            "price": 9990,
            "image_url": "/static/images/productos/gorro_gris.png",
            "is_new": True,
            "detail_url": "#",
        },
        {
            "name": "Polerón Essential Blanco",
            "price": 25990,
            "image_url": "/static/images/productos/poleron_blanco.png",
            "is_new": False,
            "detail_url": "#",
        },
        {
            "name": "Mochila Explorer Negra",
            "price": 27990,
            "image_url": "/static/images/productos/mochila_negra.png",
            "is_new": False,
            "detail_url": "#",
        },
        {
            "name": "Botines Urbanos Cuero",
            "price": 49990,
            "image_url": "/static/images/productos/botines_cuero.png",
            "is_new": True,
            "detail_url": "#",
        },
        {
            "name": "Cinturón Minimal",
            "price": 12990,
            "image_url": "/static/images/productos/cinturon.png",
            "is_new": False,
            "detail_url": "#",
        },
        {
            "name": "Reloj Vintage Metal",
            "price": 55990,
            "image_url": "/static/images/productos/reloj_metal.png",
            "is_new": True,
            "detail_url": "#",
        },
    ]

    return render(request, "pagina1.html", {"productos": productos})


def _resolve_worker_profile(name: str):
    normalized = (name or "").strip()
    canonical = next(
        (key for key in WORKER_PROFILES.keys() if normalized.lower() == key.lower()),
        None,
    )
    profile_key = canonical or "Default"
    profile = WORKER_PROFILES[profile_key].copy()
    seed = profile.get("seed", profile_key)
    return profile, profile_key, canonical, normalized


def _build_worker_stats(display_name: str):
    profile, profile_key, canonical, normalized = _resolve_worker_profile(display_name)
    seed = profile.get("seed", profile_key)
    rng = random.Random(seed)

    clients_data = []
    sales_data = []
    for _ in MONTH_LABELS:
        base_clients = rng.randint(*profile["clients_range"])
        variation = 0.9 + rng.random() * 0.25
        clients = max(5, round(base_clients * variation))
        clients_data.append(clients)

        avg_ticket = profile["avg_ticket"] * (0.85 + rng.random() * 0.3)
        sales = round(clients * avg_ticket)
        sales_data.append(sales)

    commission_rate = profile["commission_rate"]
    commissions = [round(sale * commission_rate) for sale in sales_data]

    today = timezone.localdate()
    year, month = today.year, today.month
    turno_rng = random.Random(f"{seed}-{year}-{month}")
    total_days = calendar.monthrange(year, month)[1]
    day_statuses = {}
    status_counts = {"Trabajando": 0, "Libre": 0, "No trabaja": 0}

    for day in range(1, total_days + 1):
        current = date(year, month, day)
        if current.weekday() >= 5:
            status = turno_rng.choice(["Libre", "No trabaja"])
        else:
            status = turno_rng.choices(
                ["Trabajando", "Libre", "No trabaja"],
                weights=[0.65, 0.25, 0.1],
            )[0]
        day_statuses[day] = status
        status_counts[status] += 1

    if status_counts["Trabajando"] == 0:
        first_weekday = next(
            (d for d in range(1, total_days + 1) if date(year, month, d).weekday() < 5),
            1,
        )
        day_statuses[first_weekday] = "Trabajando"
    if status_counts["Libre"] == 0:
        weekend_day = next(
            (d for d in range(1, total_days + 1) if date(year, month, d).weekday() >= 5),
            total_days,
        )
        day_statuses[weekend_day] = "Libre"
    if status_counts["No trabaja"] == 0:
        fallback_day = next(
            (d for d in range(1, total_days + 1) if date(year, month, d).weekday() >= 5),
            total_days,
        )
        day_statuses[fallback_day] = "No trabaja"

    calendar_builder = calendar.Calendar()
    weeks = []
    for week in calendar_builder.monthdayscalendar(year, month):
        week_cells = []
        for day in week:
            if day == 0:
                week_cells.append({"day": "", "status": ""})
            else:
                week_cells.append({"day": day, "status": day_statuses[day]})
        weeks.append(week_cells)

    month_label = f"{MONTH_LABELS[month - 1]} {year}"

    return {
        "display_name": normalized or display_name,
        "profile_key": profile_key,
        "clients": clients_data,
        "sales": sales_data,
        "commissions": commissions,
        "commission_rate": commission_rate,
        "turno_weeks": weeks,
        "current_month_label": month_label,
    }


def iniciosesiontrabajador(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        if not nombre:
            return render(
                request,
                "iniciosesiontrabajador.html",
                {"error": "Ingresa tu nombre.", "nombre": nombre},
            )
        request.session["worker_name"] = nombre
        return redirect(reverse("dashboardtrabajador"))

    nombre_inicial = request.session.get("worker_name", "")
    return render(request, "iniciosesiontrabajador.html", {"nombre": nombre_inicial})


def dashboardtrabajador(request):
    nombre = request.session.get("worker_name")
    if not nombre:
        return redirect(reverse("iniciosesiontrabajador"))

    stats = _build_worker_stats(nombre)
    display_name = nombre

    status_classes = {
        "Trabajando": "badge bg-primary",
        "Libre": "badge bg-success",
        "No trabaja": "badge bg-secondary",
        "": "",
    }

    context = {
        "nombre": display_name,
        "months": MONTH_LABELS,
        "clients_data": stats["clients"],
        "commissions_data": stats["commissions"],
        "commission_percentage": stats["commission_rate"] * 100,
        "turno_weeks": stats["turno_weeks"],
        "current_month_label": stats["current_month_label"],
        "week_labels": WEEKDAY_LABELS,
        "status_classes": status_classes,
    }

    return render(request, "dashboardtrabajador.html", context)


def pagina3(request):
    return render(request, "pagina3.html")
