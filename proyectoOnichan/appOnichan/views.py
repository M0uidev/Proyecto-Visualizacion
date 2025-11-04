import random
import unicodedata
from datetime import date, timedelta

from django.shortcuts import redirect, render


def index(request):
    return pagina1(request)


def pagina1(request):
    # Lista de 10 productos hardcodeados
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

DAY_LABELS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

WORKER_PROFILES = {
    "ana perez": {"seed": 101, "commission": 0.11},
    "carlos silva": {"seed": 202, "commission": 0.09},
    "maria gomez": {"seed": 303, "commission": 0.13},
    "default": {"seed": 999, "commission": 0.1},
}


def _normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value or "")
    without_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return without_accents.strip().lower()


def _get_worker_profile(nombre: str):
    normalized = _normalize_name(nombre)
    profile = WORKER_PROFILES.get(normalized, WORKER_PROFILES["default"])
    seed = profile["seed"]
    if profile is WORKER_PROFILES["default"] and normalized and normalized != "default":
        seed = abs(hash(normalized)) % 10000 + profile["seed"]
    return {"seed": seed, "commission": profile["commission"]}


def _build_worker_stats(nombre: str):
    profile = _get_worker_profile(nombre)
    rng = random.Random(profile["seed"])
    clients = [rng.randint(25, 110) for _ in range(12)]
    sales = []
    for count in clients:
        base_ticket = rng.uniform(35000, 95000)
        modifier = rng.uniform(0.85, 1.25)
        sales.append(int(count * base_ticket * modifier))
    commission_rate = profile["commission"]
    commissions = [int(sale * commission_rate) for sale in sales]
    return {
        "clients": clients,
        "sales": sales,
        "commissions": commissions,
        "commission_rate": commission_rate,
    }


def _generate_schedule(nombre: str):
    profile = _get_worker_profile(nombre)
    rng = random.Random(profile["seed"] + 500)
    today = date.today()
    start = today - timedelta(days=today.weekday())
    days = [start + timedelta(days=i) for i in range(7)]
    statuses = []
    for _ in days:
        statuses.append(rng.choices(["Trabajando", "Libre", "No trabaja"], weights=[6, 3, 1])[0])
    if statuses.count("Trabajando") == 0:
        statuses[rng.randrange(len(statuses))] = "Trabajando"
    if statuses.count("Libre") == 0:
        libre_idx = (rng.randrange(len(statuses)) + 1) % len(statuses)
        statuses[libre_idx] = "Libre"
    if statuses.count("No trabaja") == len(statuses):
        statuses[0] = "Trabajando"
    schedule = []
    for idx, day in enumerate(days):
        label_index = (day.weekday()) % 7
        schedule.append(
            {
                "day": DAY_LABELS[label_index],
                "date": day.strftime("%d/%m"),
                "status": statuses[idx],
            }
        )
    end = days[-1]
    period_label = f"Semana del {start.strftime('%d/%m/%Y')} al {end.strftime('%d/%m/%Y')}"
    return schedule, period_label


def iniciosesiontrabajador(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        if not nombre:
            return render(
                request,
                "iniciosesiontrabajador.html",
                {"error": "Ingresa un nombre", "nombre": nombre},
            )
        request.session["worker_name"] = nombre
        return redirect("dashboardtrabajador")
    return render(request, "iniciosesiontrabajador.html", {"nombre": ""})


def dashboardtrabajador(request):
    nombre = request.session.get("worker_name")
    if not nombre:
        return redirect("iniciosesiontrabajador")
    stats = _build_worker_stats(nombre)
    schedule, period_label = _generate_schedule(nombre)
    context = {
        "worker_name": nombre,
        "month_labels": MONTH_LABELS,
        "clients_data": stats["clients"],
        "commissions_data": stats["commissions"],
        "sales_data": stats["sales"],
        "commission_rate_percent": round(stats["commission_rate"] * 100, 1),
        "turnos": schedule,
        "turnos_period_label": period_label,
    }
    return render(request, "dashboardtrabajador.html", context)


def pagina3(request):
    return render(request, "pagina3.html")
