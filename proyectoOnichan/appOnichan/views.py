import random
from calendar import monthrange
from datetime import date, datetime, time

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone


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


def login_trabajador_view(request):
    nombre = ""
    error_nombre = ""

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        if not nombre:
            error_nombre = "Ingresa tu nombre."
            messages.error(request, "Completa los campos marcados en rojo.", extra_tags="danger")
        else:
            request.session["nombre_trabajador"] = nombre
            return redirect("dashboard_trabajador")

    context = {"nombre_inicial": nombre, "error_nombre": error_nombre}
    return render(request, "iniciosesiontrabajador.html", context)


def dashboard_trabajador_view(request):
    nombre = request.session.get("nombre_trabajador")
    if not nombre:
        messages.info(request, "Inicia sesión para acceder al panel.")
        return redirect("iniciosesiontrabajador")

    labels_meses = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    ]

    clientes_por_mes = [random.randint(0, 120) for _ in labels_meses]
    ticket_promedio = [random.randint(15000, 35000) for _ in labels_meses]
    ventas_por_mes = [clientes_por_mes[i] * ticket_promedio[i] for i in range(len(labels_meses))]
    porcentaje_comision_por_mes = [round(random.uniform(0.08, 0.18), 3) for _ in labels_meses]
    comision_por_mes = [round(ventas_por_mes[i] * porcentaje_comision_por_mes[i], 2) for i in range(len(labels_meses))]

    fecha_base = timezone.localdate()
    fecha_referencia = date(fecha_base.year, fecha_base.month, 1)
    nombre_mes = [
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
    ][fecha_base.month - 1]

    eventos_turnos = _generar_eventos_turnos(fecha_referencia)

    contexto = {
        "nombre_trabajador": nombre,
        "labels_meses": labels_meses,
        "clientes_por_mes": clientes_por_mes,
        "ventas_por_mes": ventas_por_mes,
        "porcentaje_comision_por_mes": porcentaje_comision_por_mes,
        "comision_por_mes": comision_por_mes,
        "fecha_referencia": fecha_referencia.isoformat(),
        "titulo_calendario": f"{nombre_mes} {fecha_base.year}",
        "eventos_turnos": eventos_turnos,
    }

    return render(request, "dashboardtrabajador.html", contexto)


def _generar_eventos_turnos(fecha_referencia: date):
    eventos = []
    anio = fecha_referencia.year
    mes = fecha_referencia.month
    total_dias = monthrange(anio, mes)[1]

    for dia in range(1, total_dias + 1):
        fecha_actual = date(anio, mes, dia)
        es_fin_de_semana = fecha_actual.weekday() >= 5

        if es_fin_de_semana:
            tipo = random.choices(["libre", "trabajo", "descanso"], weights=[6, 2, 1])[0]
        else:
            tipo = random.choices(["trabajo", "descanso", "libre"], weights=[7, 2, 1])[0]

        if tipo == "trabajo":
            inicio = datetime.combine(fecha_actual, time(9, 0)).isoformat()
            fin = datetime.combine(fecha_actual, time(17, 0)).isoformat()
        elif tipo == "descanso":
            inicio = datetime.combine(fecha_actual, time(12, 30)).isoformat()
            fin = datetime.combine(fecha_actual, time(14, 0)).isoformat()
        else:
            inicio = datetime.combine(fecha_actual, time(0, 0)).isoformat()
            fin = datetime.combine(fecha_actual, time(23, 59)).isoformat()

        eventos.append({"start": inicio, "end": fin, "tipo": tipo})

    return eventos


def pagina3(request):
    return render(request, "pagina3.html")
