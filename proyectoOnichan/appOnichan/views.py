import json
import re
from django.db import models # Ensure models is imported for Q objects
import random
import string
from django.core.paginator import Paginator
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.error.transbank_error import TransbankError
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect, get_object_or_404 # Added get_object_or_404
from django.http import Http404, HttpResponseForbidden, JsonResponse, HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum, Count, F, Max
from django.utils import timezone
from datetime import date as dt_date, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.utils.text import slugify
from datetime import date as dt_date

from .models import (
    Product,
    Customer,
    Order,
    OrderItem,
    Category,
    UserProfile,
    Coupon,
    ProductDetail,
    BulkOffer,
    ProductSize,
    PointReward,
    RedemptionHistory,
    UserCoupon
)
from .forms import CouponForm, BulkDiscountForm, CouponGenerationForm # Added Forms
from django.contrib import messages # Added messages
from .services import get_regional_stats, RewardService, StockService
from django.core.exceptions import ValidationError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF
from reportlab.lib.utils import simpleSplit

def index(request):
    return pagina1(request)

def pagina1(request):
    # Obtener parámetros de filtro y orden
    category_slug = request.GET.get("category", "")
    sort_by = request.GET.get("sort", "")
    query = request.GET.get("q", "").strip()
    try:
        items_per_page = int(request.GET.get("items", 8))
    except ValueError:
        items_per_page = 8

    # Base query
    productos = Product.objects.select_related('category', 'detail').prefetch_related('bulk_offers', 'sizes').all()

    # Filtrar por búsqueda
    if query:
        productos = productos.filter(name__icontains=query)

    # Filtrar por categoría
    if category_slug and category_slug != 'all':
        productos = productos.filter(category__slug=category_slug)

    # Ordenar
    if sort_by == "price_asc":
        productos = productos.order_by("price")
    elif sort_by == "price_desc":
        productos = productos.order_by("-price")
    elif sort_by == "newest":
        productos = productos.order_by("-id") # Asumiendo ID más alto es más nuevo
    else:
        productos = productos.order_by("id")

    categories = Category.objects.all()

    # Ofertas imperdibles (productos con descuento activo)
    ofertas_imperdibles = Product.objects.filter(bulk_offers__active=True).distinct().select_related('category', 'detail').prefetch_related('bulk_offers', 'sizes')

    # Paginación
    paginator = Paginator(productos, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "productos": page_obj,
        "ofertas_imperdibles": ofertas_imperdibles,
        "categories": categories,
        "current_category": category_slug,
        "current_sort": sort_by,
        "items_per_page": items_per_page
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "partials/product_list.html", context)

    return render(request, "pagina1.html", context)

def buscar_productos(request):
    # Obtener parámetros de filtro y orden
    category_slug = request.GET.get("category", "")
    sort_by = request.GET.get("sort", "")
    query = request.GET.get("q", "").strip()

    # Base query
    productos = Product.objects.select_related('category', 'detail').prefetch_related('bulk_offers').all()

    # Filtrar por búsqueda
    if query:
        productos = productos.filter(name__icontains=query)

    # Filtrar por categoría
    if category_slug:
        productos = productos.filter(category__slug=category_slug)

    # Ordenar
    if sort_by == "price_asc":
        productos = productos.order_by("price")
    elif sort_by == "price_desc":
        productos = productos.order_by("-price")
    elif sort_by == "newest":
        productos = productos.order_by("-id") # Asumiendo ID más alto es más nuevo
    else:
        productos = productos.order_by("id")

    categories = Category.objects.all()

    context = {
        "productos": productos,
        "categories": categories,
        "current_category": category_slug,
        "current_sort": sort_by,
        "query": query
    }
    return render(request, "buscar_productos.html", context)

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Decide redirección por rol
            if user.is_superuser or user.is_staff or user.groups.filter(name__iexact="admin").exists():
                return redirect("dashboardadmin")
            if user.groups.filter(name__iexact="trabajador").exists():
                return redirect("dashboardtrabajador")
            # default: cliente
            return redirect("pagina1")
        else:
            return render(request, "login.html", {"error": "Usuario o contraseña inválidos."})

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        
        # Profile fields
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        commune = request.POST.get("commune", "").strip()
        region = request.POST.get("region", "").strip()

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "El nombre de usuario ya existe."})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Create profile
        UserProfile.objects.create(
            user=user,
            phone=phone,
            address=address,
            commune=commune,
            region=region
        )

        login(request, user)
        return redirect("pagina1")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("pagina1")

@login_required
def stock(request):
    return render(request, "stock.html")

@login_required
def dashboardadmin(request):
    # Solo administradores
    user = request.user
    if not (user.is_superuser or user.is_staff or user.groups.filter(name__iexact="admin").exists()):
        return HttpResponseForbidden("No autorizado")
    # Selección de periodo: semana (default), mes o año
    today = timezone.localdate()
    period = (request.GET.get("period", "week") or "week").lower()
    period = period if period in ("week", "month", "year") else "week"

    # Determinar rango de fechas
    period_title = "semana" if period == "week" else ("mes" if period == "month" else "año")
    if period == "week":
        ref_str = request.GET.get("week", "").strip()
        try:
            ref_date = dt_date.fromisoformat(ref_str) if ref_str else today
        except Exception:
            ref_date = today
        start_date = ref_date - timedelta(days=ref_date.weekday())
        end_date = start_date + timedelta(days=6)
        # navegación
        prev_ref_date = start_date - timedelta(days=1)
        next_ref_date = end_date + timedelta(days=1)
        prev_url = f"?period=week&week={prev_ref_date.isoformat()}"
        next_url = f"?period=week&week={next_ref_date.isoformat()}"
        ref_value = ref_date.isoformat()
        title_text = f"Pedidos por día ({start_date.isoformat()} al {end_date.isoformat()})"
        # Labels por día de la semana
        weekday_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        day_counts = {label: 0 for label in weekday_labels}
        delivered_counts = {label: 0 for label in weekday_labels}
        pending_counts = {label: 0 for label in weekday_labels}
        orders_period = Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date).exclude(estado="IniciandoPago")
        for o in orders_period:
            idx = o.fecha.weekday()
            label = weekday_labels[idx]
            day_counts[label] += 1
            if o.estado == "Entregado":
                delivered_counts[label] += 1
            elif o.estado == "Pendiente":
                pending_counts[label] += 1
        line_labels = weekday_labels
        line_values = [day_counts[l] for l in line_labels]
        line_detalles = {l: {"Entregados": delivered_counts[l], "Pendientes": pending_counts[l]} for l in line_labels}
    elif period == "month":
        # referencia YYYY-MM
        month_str = request.GET.get("month", "").strip()
        try:
            if month_str:
                y, m = month_str.split("-")
                year_i, month_i = int(y), int(m)
                ref_date = dt_date(year_i, month_i, 1)
            else:
                ref_date = dt_date(today.year, today.month, 1)
        except Exception:
            ref_date = dt_date(today.year, today.month, 1)
        start_date = ref_date
        # calcular fin de mes
        if ref_date.month == 12:
            next_month_start = dt_date(ref_date.year + 1, 1, 1)
        else:
            next_month_start = dt_date(ref_date.year, ref_date.month + 1, 1)
        end_date = next_month_start - timedelta(days=1)
        # navegación
        if ref_date.month == 1:
            prev_month = dt_date(ref_date.year - 1, 12, 1)
        else:
            prev_month = dt_date(ref_date.year, ref_date.month - 1, 1)
        next_month = next_month_start
        prev_url = f"?period=month&month={prev_month.strftime('%Y-%m')}"
        next_url = f"?period=month&month={next_month.strftime('%Y-%m')}"
        ref_value = ref_date.strftime('%Y-%m')
        title_text = f"Pedidos por día ({ref_date.strftime('%B %Y')})"
        # Labels por día del mes
        total_days = (end_date - start_date).days + 1
        day_labels = [str(d) for d in range(1, total_days + 1)]
        day_counts = {label: 0 for label in day_labels}
        delivered_counts = {label: 0 for label in day_labels}
        pending_counts = {label: 0 for label in day_labels}
        orders_period = Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date).exclude(estado="IniciandoPago")
        for o in orders_period:
            label = str(o.fecha.day)
            day_counts[label] += 1
            if o.estado == "Entregado":
                delivered_counts[label] += 1
            elif o.estado == "Pendiente":
                pending_counts[label] += 1
        line_labels = day_labels
        line_values = [day_counts[l] for l in line_labels]
        line_detalles = {l: {"Entregados": delivered_counts[l], "Pendientes": pending_counts[l]} for l in line_labels}
    else:  # year
        year_str = request.GET.get("year", "").strip()
        try:
            year_i = int(year_str) if year_str else today.year
        except Exception:
            year_i = today.year
        start_date = dt_date(year_i, 1, 1)
        end_date = dt_date(year_i, 12, 31)
        prev_url = f"?period=year&year={year_i - 1}"
        next_url = f"?period=year&year={year_i + 1}"
        ref_value = str(year_i)
        title_text = f"Pedidos por mes ({year_i})"
        month_labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        m_counts = {label: 0 for label in month_labels}
        delivered_counts = {label: 0 for label in month_labels}
        pending_counts = {label: 0 for label in month_labels}
        orders_period = Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date).exclude(estado="IniciandoPago")
        for o in orders_period:
            idx = o.fecha.month - 1
            label = month_labels[idx]
            m_counts[label] += 1
            if o.estado == "Entregado":
                delivered_counts[label] += 1
            elif o.estado == "Pendiente":
                pending_counts[label] += 1
        line_labels = month_labels
        line_values = [m_counts[l] for l in line_labels]
        line_detalles = {l: {"Entregados": delivered_counts[l], "Pendientes": pending_counts[l]} for l in line_labels}

    # KPIs
    pedidos_hoy = Order.objects.filter(fecha=today).exclude(estado="IniciandoPago").count()
    pendientes = Order.objects.filter(estado="Pendiente").count()
    ingresos_7d = (
        Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date)
        .exclude(estado="IniciandoPago")
        .aggregate(total=Sum("total"))
        .get("total")
        or 0
    )

    # Top products y revenue por categoría dentro del periodo seleccionado
    top = (
        OrderItem.objects.filter(order__fecha__gte=start_date, order__fecha__lte=end_date)
        .exclude(order__estado="IniciandoPago")
        .values("product__name")
        .annotate(units=Sum("cantidad"))
        .order_by("-units")[:4]
    )
    top_labels = [t["product__name"] for t in top]
    top_values = [t["units"] for t in top]
    detalles_top = {}
    for label in top_labels:
        qs = (
            OrderItem.objects.filter(order__fecha__gte=start_date, order__fecha__lte=end_date, product__name=label)
            .exclude(order__estado="IniciandoPago")
            .values("size")
            .annotate(units=Sum("cantidad"))
            .order_by("-units")
        )
        detalles_top[label] = {(r["size"] or "Único"): r["units"] for r in qs}

    cat_rows = (
        OrderItem.objects.filter(order__fecha__gte=start_date, order__fecha__lte=end_date)
        .exclude(order__estado="IniciandoPago")
        .values("product__category__name", "order__channel")
        .annotate(revenue=Sum(F("cantidad") * F("price")))
    )
    cat_totals = {}
    cat_details = {}
    for r in cat_rows:
        cat = r["product__category__name"] or "Otros"
        ch = r["order__channel"] or "Online"
        rev = r["revenue"] or 0
        cat_totals[cat] = cat_totals.get(cat, 0) + rev
        det = cat_details.get(cat, {})
        det[ch] = det.get(ch, 0) + rev
        cat_details[cat] = det

    cat_labels = list(cat_totals.keys())
    cat_values = [cat_totals[c] for c in cat_labels]

    # Multi Series Pie (categorías vs productos por unidades vendidas en el periodo)
    sales_rows = (
        OrderItem.objects.filter(order__fecha__gte=start_date, order__fecha__lte=end_date)
        .exclude(order__estado="IniciandoPago")
        .values("product__category__name", "product__name")
        .annotate(units=Sum("cantidad"))
        .order_by("product__category__name", "product__name")
    )
    category_units = {}
    product_units = []
    for r in sales_rows:
        cat_name = r["product__category__name"] or "Otros"
        prod_name = r["product__name"] or "(Sin nombre)"
        units = r["units"] or 0
        category_units[cat_name] = category_units.get(cat_name, 0) + units
        product_units.append((cat_name, prod_name, units))

    multi_categories = list(category_units.keys())
    multi_products = [p for (_, p, _) in product_units]
    # Labels combinadas: primero categorías luego productos
    multi_labels = multi_categories + multi_products
    # Dataset interno (categorías): valores en posiciones de categorías, cero en productos
    categories_data = [category_units[c] for c in multi_categories] + [0] * len(multi_products)
    # Dataset externo (productos): cero en categorías, valor en posición de cada producto
    products_data = [0] * len(multi_categories) + [u for (_, _, u) in product_units]
    # Mapa producto -> categoría (para color/leyenda)
    product_category_map = {p: c for (c, p, _) in product_units}

    # Mapa de Chile: Ventas por región
    region_sales_qs = (
        Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date)
        .exclude(estado="IniciandoPago")
        .exclude(shipping_region__isnull=True)
        .exclude(shipping_region="")
        .values("shipping_region")
        .annotate(total=Sum("total"))
    )
    map_data = {item["shipping_region"]: item["total"] for item in region_sales_qs}

    dashboard_data = {
        "kpis": {
            "pedidos_hoy": {"value": pedidos_hoy, "trend": ""},
            "pendientes": {"value": pendientes, "trend": ""},
            "ingresos_7d": {"value": ingresos_7d, "trend": "", "isCurrency": True},
        },
        "mapData": map_data,
        "lineChart": {
            "labels": line_labels,
            "values": line_values,
            "detalles": line_detalles,
        },
        "topProducts": {
            "labels": top_labels,
            "values": top_values,
            "detalles": detalles_top,
        },
        "categoryRevenue": {
            "labels": cat_labels,
            "values": cat_values,
            "detalles": cat_details,
        },
        "multiSeriesPie": {
            "labels": multi_labels,
            "datasets": {
                "categories": categories_data,
                "products": products_data,
            },
            "categories": multi_categories,
            "productCategoryMap": product_category_map,
        },
    }

    context = {
        "data_json": json.dumps(dashboard_data),
        "title_text": title_text,
        "period": period,
        "period_title": period_title,
        "ref_value": ref_value,
        "prev_url": prev_url,
        "next_url": next_url,
    }
    return render(request, "dashboardadmin.html", context)


@login_required
def dashboardtrabajador(request):
    """Dashboard para trabajador: gráfico de pie con ventas del día por producto."""
    user = request.user
    # Restringir a trabajadores y administradores (admin también puede ver)
    if not (
        user.groups.filter(name__iexact="trabajador").exists()
        or user.is_staff
        or user.is_superuser
        or user.groups.filter(name__iexact="admin").exists()
    ):
        return HttpResponseForbidden("No autorizado")

    today = timezone.localdate()
    period = (request.GET.get("period", "day") or "day").lower()
    period = period if period in ("day", "week", "month", "year") else "day"

    # Calcular rango de fechas según el periodo
    if period == "day":
        date_str = request.GET.get("date", "").strip()
        try:
            ref_date = dt_date.fromisoformat(date_str) if date_str else today
        except Exception:
            ref_date = today
        start_date = ref_date
        end_date = ref_date
        prev_ref = ref_date - timedelta(days=1)
        next_ref = ref_date + timedelta(days=1)
        prev_url = f"?period=day&date={prev_ref.isoformat()}"
        next_url = f"?period=day&date={next_ref.isoformat()}"
        ref_value = ref_date.isoformat()
        title_text = f"Ventas por producto ({ref_date.isoformat()})"
        period_title = "día"
    elif period == "week":
        week_str = request.GET.get("week", "").strip()
        try:
            ref_date = dt_date.fromisoformat(week_str) if week_str else today
        except Exception:
            ref_date = today
        start_date = ref_date - timedelta(days=ref_date.weekday())
        end_date = start_date + timedelta(days=6)
        prev_ref = start_date - timedelta(days=1)
        next_ref = end_date + timedelta(days=1)
        prev_url = f"?period=week&week={prev_ref.isoformat()}"
        next_url = f"?period=week&week={next_ref.isoformat()}"
        ref_value = ref_date.isoformat()
        title_text = f"Ventas por producto (semana {start_date.isoformat()} a {end_date.isoformat()})"
        period_title = "semana"
    elif period == "month":
        month_str = request.GET.get("month", "").strip()
        try:
            if month_str:
                y, m = month_str.split("-")
                ref_date = dt_date(int(y), int(m), 1)
            else:
                ref_date = dt_date(today.year, today.month, 1)
        except Exception:
            ref_date = dt_date(today.year, today.month, 1)
        start_date = ref_date
        if ref_date.month == 12:
            next_month_start = dt_date(ref_date.year + 1, 1, 1)
        else:
            next_month_start = dt_date(ref_date.year, ref_date.month + 1, 1)
        end_date = next_month_start - timedelta(days=1)
        prev_month = dt_date(ref_date.year - 1, 12, 1) if ref_date.month == 1 else dt_date(ref_date.year, ref_date.month - 1, 1)
        next_month = next_month_start
        prev_url = f"?period=month&month={prev_month.strftime('%Y-%m')}"
        next_url = f"?period=month&month={next_month.strftime('%Y-%m')}"
        ref_value = ref_date.strftime('%Y-%m')
        title_text = f"Ventas por producto ({ref_date.strftime('%Y-%m')})"
        period_title = "mes"
    else:  # year
        year_str = request.GET.get("year", "").strip()
        try:
            year_i = int(year_str) if year_str else today.year
        except Exception:
            year_i = today.year
        start_date = dt_date(year_i, 1, 1)
        end_date = dt_date(year_i, 12, 31)
        prev_url = f"?period=year&year={year_i - 1}"
        next_url = f"?period=year&year={year_i + 1}"
        ref_value = str(year_i)
        title_text = f"Ventas por producto ({year_i})"
        period_title = "año"

    rows = (
        OrderItem.objects.filter(order__fecha__gte=start_date, order__fecha__lte=end_date)
        .exclude(order__estado="IniciandoPago")
        .values("product__name")
        .annotate(units=Sum("cantidad"))
        .order_by("product__name")
    )
    labels = [r["product__name"] for r in rows]
    values = [r["units"] for r in rows]

    data = {"labels": labels, "values": values}
    context = {
        "data_json": json.dumps(data),
        "period": period,
        "period_title": period_title,
        "ref_value": ref_value,
        "prev_url": prev_url,
        "next_url": next_url,
        "title_text": title_text,
    }
    return render(request, "dashboardtrabajador.html", context)

@login_required
def stock(request):
    # Solo trabajadores y administradores
    user = request.user
    is_worker = user.groups.filter(name__iexact="trabajador").exists()
    is_admin = user.is_staff or user.is_superuser or user.groups.filter(name__iexact="admin").exists()
    if not (is_worker or is_admin):
        return HttpResponseForbidden("No autorizado")

    # Acciones POST
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_stock":
            # Trabajador y admin pueden editar stock
            pid = request.POST.get("product_id")
            stock = request.POST.get("stock")
            try:
                p = Product.objects.get(pk=int(pid))
                new_stock = max(0, int(stock))
                p.stock = new_stock
                p.save(update_fields=["stock"])
                return JsonResponse({"ok": True, "stock": p.stock})
            except Exception as e:
                return JsonResponse({"ok": False, "error": str(e)}, status=400)

        if action == "add_product":
            # Solo admin
            if not is_admin:
                return HttpResponseForbidden("No autorizado")
            name = request.POST.get("name", "").strip()
            price = int(request.POST.get("price", "0") or 0)
            image_url = request.POST.get("image_url", "").strip()
            category_name = request.POST.get("category", "").strip()
            description = request.POST.get("description", "").strip()
            initial_stock = int(request.POST.get("initial_stock", "0") or 0)
            has_sizes = request.POST.get("has_sizes") == "on"
            size_scale = request.POST.get("size_scale")
            custom_sizes = request.POST.get("custom_sizes", "").strip()

            if not (name and price > 0 and image_url and category_name):
                return render(request, "stock.html", {"error": "Datos inválidos", "data": json.dumps(_products_payload())})

            cat, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": slugify(category_name)})
            # Generar nuevo id
            max_id = Product.objects.aggregate(mx=Max("id")).get("mx") or 100
            new_id = max_id + 1
            p = Product.objects.create(
                id=new_id,
                name=name,
                price=price,
                image_url=image_url,
                category=cat,
                description=description,
                stock=initial_stock,
                has_sizes=has_sizes
            )

            if has_sizes:
                sizes_to_create = []
                if size_scale == "s_xl":
                    sizes_to_create = ["S", "M", "L", "XL"]
                elif size_scale == "numbers":
                    sizes_to_create = [str(i) for i in range(36, 45)]
                elif size_scale == "custom" and custom_sizes:
                    sizes_to_create = [s.strip() for s in custom_sizes.split(",") if s.strip()]
                
                for label in sizes_to_create:
                    ProductSize.objects.create(product=p, label=label)

            return redirect("stock")

        if action == "update_product_details":
            if not is_admin:
                return HttpResponseForbidden("No autorizado")
            
            pid = request.POST.get("product_id")
            name = request.POST.get("name", "").strip()
            price = int(request.POST.get("price", "0") or 0)
            image_url = request.POST.get("image_url", "").strip()
            category_name = request.POST.get("category", "").strip()
            description = request.POST.get("description", "").strip()
            stock = int(request.POST.get("stock", "0") or 0)
            sizes_str = request.POST.get("sizes", "").strip()
            
            # Validation
            if not (name and price > 0 and category_name):
                 return JsonResponse({"ok": False, "error": "Datos inválidos"}, status=400)

            # Image URL Validation
            if image_url:
                if not (image_url.lower().endswith('.png') or image_url.lower().endswith('.jpg')):
                     return JsonResponse({"ok": False, "error": "La URL de la imagen debe terminar en .png o .jpg"}, status=400)
                if not image_url.startswith('/static/images/productos/'):
                     return JsonResponse({"ok": False, "error": "La imagen debe estar en /static/images/productos/"}, status=400)
            
            try:
                p = Product.objects.get(pk=int(pid))
                p.name = name
                p.price = price
                p.description = description
                p.image_url = image_url
                p.stock = stock
                
                cat, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": slugify(category_name)})
                p.category = cat
                
                # Update sizes
                if sizes_str:
                    p.has_sizes = True
                    new_labels = [s.strip() for s in sizes_str.split(",") if s.strip()]
                    p.sizes.all().delete()
                    for label in new_labels:
                        ProductSize.objects.create(product=p, label=label)
                else:
                    p.has_sizes = False
                    p.sizes.all().delete()

                p.save()
                return JsonResponse({"ok": True})
            except Exception as e:
                return JsonResponse({"ok": False, "error": str(e)}, status=400)

    # GET: construir dataset de productos para el front
    payload = _products_payload()
    return render(request, "stock.html", {"data": json.dumps(payload)})


def _products_payload():
    products = Product.objects.select_related("category").prefetch_related("sizes").order_by("id")
    out = []
    for p in products:
        out.append({
            "code": str(p.id),
            "name": p.name,
            "price": p.price,
            "category": p.category.name if p.category else "Otros",
            "stock": p.stock,
            "image_url": p.image_url,
            "description": p.description,
            "has_sizes": p.has_sizes,
            "sizes": [s.label for s in p.sizes.all()]
        })
    return {"products": out}

def producto_detalle(request, pid: int):
    try:
        p = Product.objects.get(pk=pid)
    except Product.DoesNotExist:
        raise Http404("Producto no encontrado")

    # Construir el diccionario de detalle desde las tablas normalizadas
    det = getattr(p, "detail", None)
    d = {
        "breadcrumbs": [b.label for b in p.breadcrumbs.all()],
        "rating": float(det.rating) if det else 4.5,
        "rating_count": det.rating_count if det else 0,
        "color": det.color if det else "",
        "sizes": [s.label for s in p.sizes.all()],
        "specs": [s.text for s in p.specs.all()],
        "care": [c.text for c in p.care.all()],
        "descuento_pct": det.discount_percentage if det else 0,
        "envio": det.envio if det else "",
        "llega": det.llega if det else "",
        "warranty": det.warranty if det else "",
        "capacity_l": det.capacity_l if det else None,
    }

    d["discounted_price"] = det.discounted_price if det else p.price

    return render(request, "producto_detalle.html", {"p": p, "d": d})


@login_required
def pos_view(request):
    """Caja (POS) para trabajador: construir pedido y finalizar venta presencial."""
    user = request.user
    if not (
        user.groups.filter(name__iexact="trabajador").exists()
        or user.is_staff
        or user.is_superuser
        or user.groups.filter(name__iexact="admin").exists()
    ):
        return HttpResponseForbidden("No autorizado")

    # Carrito en sesión: {product_id: cantidad}
    cart = request.session.get("pos_cart", {})

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            pid = request.POST.get("product_id")
            qty = int(request.POST.get("qty", 1) or 1)
            if pid and Product.objects.filter(pk=pid).exists():
                cart[str(pid)] = cart.get(str(pid), 0) + max(qty, 1)
                request.session["pos_cart"] = cart
            return redirect("pos")

        if action == "remove":
            pid = request.POST.get("product_id")
            if pid and str(pid) in cart:
                cart.pop(str(pid), None)
                request.session["pos_cart"] = cart
            return redirect("pos")

        if action == "clear":
            request.session["pos_cart"] = {}
            return redirect("pos")

        if action == "finalize":
            if not cart:
                return redirect("pos")

            # Validar stock suficiente antes de crear el pedido
            pids = [int(pid) for pid in cart.keys()]
            productos_db = {p.id: p for p in Product.objects.filter(id__in=pids)}
            insuficientes = []
            for pid, qty in cart.items():
                qty = int(qty)
                p = productos_db.get(int(pid))
                if not p or p.stock < qty:
                    insuficientes.append({
                        "id": pid,
                        "name": p.name if p else f"Producto {pid}",
                        "requested": qty,
                        "available": (p.stock if p else 0),
                    })

            if insuficientes:
                # Preparar contexto y mostrar error en la misma página POS
                productos = Product.objects.all().order_by("id")
                cart_items = []
                cart_total = 0
                for pid, qty in cart.items():
                    p = productos_db.get(int(pid))
                    if not p:
                        continue
                    subtotal = p.price * int(qty)
                    cart_total += subtotal
                    cart_items.append({
                        "id": p.id,
                        "name": p.name,
                        "price": p.price,
                        "qty": int(qty),
                        "subtotal": subtotal,
                    })
                return render(
                    request,
                    "pos.html",
                    {
                        "productos": productos,
                        "cart_items": cart_items,
                        "cart_total": cart_total,
                        "pos_errors": insuficientes,
                    },
                )

            # Stock suficiente: crear pedido y descontar
            # Determinar fecha del pedido (permitir seleccionar manualmente)
            date_str = request.POST.get("order_date", "").strip()
            try:
                selected_date = dt_date.fromisoformat(date_str) if date_str else timezone.localdate()
            except Exception:
                selected_date = timezone.localdate()
            cliente, _ = Customer.objects.get_or_create(name="Mostrador")

            base = selected_date.strftime("POS%Y%m%d")
            seq = 1
            while True:
                code = f"{base}-{seq:04d}"
                if not Order.objects.filter(code=code).exists():
                    break
                seq += 1

            order = Order.objects.create(
                code=code,
                fecha=selected_date,
                cliente=cliente,
                total=0,
                estado="Entregado",
                channel="Tienda",
            )

            total = 0
            for pid, qty in cart.items():
                p = productos_db.get(int(pid))
                qty = int(qty)
                item = OrderItem.objects.create(
                    order=order,
                    product=p,
                    cantidad=qty,
                    price=p.price,
                    size="",
                )
                total += item.subtotal
                p.stock = p.stock - qty
                p.save(update_fields=["stock"])

            order.total = total
            order.save()

            request.session["pos_cart"] = {}

            return redirect("dashboardtrabajador")

    # Preparar datos de vista
    productos = Product.objects.all().order_by("id")
    cart_items = []
    cart_total = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            continue
        subtotal = p.price * int(qty)
        cart_total += subtotal
        cart_items.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "qty": int(qty),
            "subtotal": subtotal,
        })

    return render(
        request,
        "pos.html",
        {"productos": productos, "cart_items": cart_items, "cart_total": cart_total, "today": timezone.localdate().isoformat()},
    )

def add_to_cart(request, pid):
    product = get_object_or_404(Product, id=pid)
    
    # Check if product is out of stock
    if product.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
            return JsonResponse({'status': 'error', 'message': 'Producto sin stock'}, status=400)
        messages.error(request, "Este producto no tiene stock.")
        return redirect(request.META.get('HTTP_REFERER', 'pagina1'))

    size = request.GET.get('size') or request.POST.get('size')
    
    # Validate size selection if product has sizes
    if product.sizes.exists() and not size:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
             return JsonResponse({'status': 'error', 'message': 'Debe seleccionar una talla'}, status=400)
        messages.error(request, "Debe seleccionar una talla para este producto.")
        return redirect(request.META.get('HTTP_REFERER', 'pagina1'))

    key = str(pid)
    if size:
        key = f"{pid}_{size}"

    cart = request.session.get("cart", {})
    
    # Calculate total quantity of this product currently in cart (across all sizes)
    total_in_cart = 0
    for k, v in cart.items():
        if k == str(pid) or k.startswith(f"{pid}_"):
            total_in_cart += v
            
    if total_in_cart + 1 > product.stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
            return JsonResponse({'status': 'error', 'message': 'No hay suficiente stock disponible'}, status=400)
        messages.error(request, f"No puedes agregar más unidades de {product.name}. Stock máximo alcanzado.")
        return redirect(request.META.get('HTTP_REFERER', 'pagina1'))

    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    
    # Check for AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        total_items = sum(cart.values())
        return JsonResponse({'status': 'ok', 'cart_count': total_items})
        
    return redirect(request.META.get('HTTP_REFERER', 'pagina1'))

def remove_from_cart(request, key):
    cart = request.session.get("cart", {})
    if key in cart:
        del cart[key]
        request.session["cart"] = cart
        return redirect("cart_view")

    rewards_cart = request.session.get("rewards_cart", {})
    if key in rewards_cart:
        # Refund logic
        try:
            pid = int(key.split('_')[0])
            qty = rewards_cart[key]
            
            # Find the reward
            reward = PointReward.objects.filter(product_id=pid, reward_type='PRODUCT').first()
            
            if reward and request.user.is_authenticated:
                RewardService.restore_reward(request.user, reward.id, qty)
                messages.success(request, f"Producto eliminado. Se han reembolsado los puntos.")
        except Exception as e:
            pass
            
        del rewards_cart[key]
        request.session["rewards_cart"] = rewards_cart
        
    return redirect("cart_view")

def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0
    
    # Extract product IDs from keys (which might be "ID" or "ID_SIZE")
    pids = set()
    for key in cart.keys():
        try:
            pids.add(int(key.split('_')[0]))
        except ValueError:
            continue
            
    products = Product.objects.filter(id__in=pids)
    product_map = {str(p.id): p for p in products}
    
    for key, qty in cart.items():
        try:
            parts = key.split('_')
            pid = parts[0]
            size = parts[1] if len(parts) > 1 else None
        except ValueError:
            continue

        product = product_map.get(pid)
        if product:
            # Calculate price with product discount if any
            price = product.price
            try:
                price = product.detail.discounted_price
            except ProductDetail.DoesNotExist:
                pass
                
            subtotal = price * qty
            total += subtotal
            items.append({
                "product": product,
                "qty": qty,
                "subtotal": subtotal,
                "price_used": price,
                "size": size,
                "key": key
            })

    # Rewards Logic
    rewards_cart = request.session.get("rewards_cart", {})
    reward_pids = set()
    for key in rewards_cart.keys():
        try:
            reward_pids.add(int(key.split('_')[0]))
        except ValueError:
            continue
            
    if reward_pids:
        reward_products = Product.objects.filter(id__in=reward_pids)
        reward_product_map = {str(p.id): p for p in reward_products}
        
        for key, qty in rewards_cart.items():
            try:
                parts = key.split('_')
                pid = parts[0]
                size = parts[1] if len(parts) > 1 else None
            except ValueError:
                continue

            product = reward_product_map.get(pid)
            if product:
                items.append({
                    "product": product,
                    "qty": qty,
                    "subtotal": 0,
                    "price_used": 0,
                    "size": size,
                    "key": key,
                    "is_reward": True
                })
            
    # Coupon Logic
    coupon_id = request.session.get('coupon_id')
    discount_amount = 0
    coupon = None
    
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.is_valid():
                discount_amount = int(total * (coupon.discount_percentage / 100))
            else:
                # Remove invalid coupon
                del request.session['coupon_id']
                coupon = None
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
            
    final_total = total - discount_amount

    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            pass

    # Fetch wallet coupons
    wallet_coupons = []
    if request.user.is_authenticated:
        wallet_coupons = UserCoupon.objects.filter(user=request.user, is_used=False).select_related('coupon')

    return render(request, "cart.html", {
        "items": items, 
        "total": total, 
        "discount_amount": discount_amount,
        "final_total": final_total,
        "coupon": coupon,
        "user_profile": user_profile,
        "wallet_coupons": wallet_coupons
    })

def checkout_webpay(request):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        rewards_cart = request.session.get("rewards_cart", {})
        if not cart and not rewards_cart:
            return redirect("cart_view")
            
        # Obtener datos del formulario
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        delivery_method = request.POST.get("delivery_method", "Despacho")
        
        shipping_address = ""
        shipping_commune = ""
        shipping_region = ""
        
        if delivery_method == "Despacho":
            shipping_address = request.POST.get("address", "").strip()
            shipping_commune = request.POST.get("commune", "").strip()
            shipping_region = request.POST.get("region", "").strip()
            
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = "Cliente Web"

        # Crear o actualizar cliente (simple logic)
        if request.user.is_authenticated:
            customer = Customer.objects.filter(name=request.user.username).first()
            if not customer:
                customer = Customer.objects.create(name=request.user.username)
        else:
            customer, _ = Customer.objects.get_or_create(name=full_name)
        
        today = timezone.localdate()
        base = today.strftime("WEB%Y%m%d")
        
        # Generar código único
        last_order = Order.objects.filter(code__startswith=base).order_by('code').last()
        if last_order:
            try:
                last_seq = int(last_order.code.split('-')[-1])
                seq = last_seq + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
            
        code = f"{base}-{seq:04d}"
        
        try:
            with transaction.atomic():
                # Calculate total again to be safe
                total_order = 0
                
                # Extract product IDs from keys
                pids = set()
                for key in cart.keys():
                    try:
                        pids.add(int(key.split('_')[0]))
                    except ValueError:
                        continue
                        
                products_in_cart = Product.objects.filter(id__in=pids)
                product_map = {str(p.id): p for p in products_in_cart}
                
                for key, qty in cart.items():
                    try:
                        parts = key.split('_')
                        pid = parts[0]
                    except ValueError:
                        continue

                    p = product_map.get(pid)
                    if p:
                        price = p.price
                        try:
                            price = p.detail.discounted_price
                        except ProductDetail.DoesNotExist:
                            pass
                        total_order += price * qty
                        
                # Apply Coupon
                coupon_id = request.session.get('coupon_id')
                discount = 0
                if coupon_id:
                    try:
                        coupon = Coupon.objects.select_for_update().get(id=coupon_id)
                        if coupon.is_valid():
                            discount = int(total_order * (coupon.discount_percentage / 100))
                            total_order -= discount
                            
                            # Increment usage
                            coupon.times_used += 1
                            coupon.save()

                            # Mark UserCoupon as used if it exists for this user
                            if request.user.is_authenticated:
                                try:
                                    user_coupon = UserCoupon.objects.get(user=request.user, coupon=coupon, is_used=False)
                                    user_coupon.is_used = True
                                    user_coupon.save()
                                except UserCoupon.DoesNotExist:
                                    pass
                    except Coupon.DoesNotExist:
                        pass
                
                order = Order.objects.create(
                    code=code,
                    fecha=today,
                    cliente=customer,
                    user=request.user if request.user.is_authenticated else None,
                    total=total_order,
                    discount_amount=discount,
                    estado="IniciandoPago",
                    channel="Online",
                    delivery_method=delivery_method,
                    contact_phone=phone,
                    contact_email=email,
                    recipient_name=full_name,
                    shipping_address=shipping_address,
                    shipping_commune=shipping_commune,
                    shipping_region=shipping_region
                )
                
                for key, qty in cart.items():
                    try:
                        parts = key.split('_')
                        pid = parts[0]
                        size = parts[1] if len(parts) > 1 else ""
                    except ValueError:
                        continue

                    product = product_map.get(pid)
                    if product:
                        # Use discounted price for OrderItem
                        price = product.price
                        try:
                            price = product.detail.discounted_price
                        except ProductDetail.DoesNotExist:
                            pass

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            cantidad=qty,
                            price=price,
                            size=size,
                            is_reward=False
                        )

                # Process Rewards Cart
                if rewards_cart:
                    reward_pids = set()
                    for key in rewards_cart.keys():
                        try:
                            reward_pids.add(int(key.split('_')[0]))
                        except ValueError:
                            continue
                    
                    reward_products = Product.objects.filter(id__in=reward_pids)
                    reward_product_map = {str(p.id): p for p in reward_products}
                    
                    for key, qty in rewards_cart.items():
                        try:
                            parts = key.split('_')
                            pid = parts[0]
                            size = parts[1] if len(parts) > 1 else ""
                        except ValueError:
                            continue

                        product = reward_product_map.get(pid)
                        if product:
                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                cantidad=qty,
                                price=0, # Free
                                size=size,
                                is_reward=True
                            )
                
                # Reserve Stock for Normal Items
                StockService.reserve_stock_for_order(order)

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("cart_view")
        except Exception as e:
            messages.error(request, "Error al procesar el pedido: " + str(e))
            return redirect("cart_view")
                
        # Start Webpay Transaction
        buy_order = order.code
        session_id = request.session.session_key or "session"
        amount = order.total
        return_url = request.build_absolute_uri('/webpay/commit/') 

        try:
            tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
            response = tx.create(buy_order, session_id, amount, return_url)
            
            return render(request, 'webpay_redirect.html', {'url': response['url'], 'token': response['token']})
        except TransbankError as e:
             # Restore stock if transaction creation fails
            StockService.release_stock_for_order(order)
            order.estado = 'Fallido'
            order.save()
            return render(request, 'payment_failed.html', {'message': str(e)})
        
    return redirect("cart_view")

@csrf_exempt
def webpay_commit(request):
    token = request.GET.get("token_ws") or request.POST.get("token_ws")
    
    if not token:
        return render(request, 'payment_failed.html', {'message': 'Transacción cancelada o inválida'})

    try:
        tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
        response = tx.commit(token)
        
        status = response.get('status')
        buy_order = response.get('buy_order')
        
        order = get_object_or_404(Order, code=buy_order)
        
        if status == 'AUTHORIZED':
            order.estado = 'Pendiente'
            order.save()
            
            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                    points_earned = int(order.total / 100)
                    profile.points += points_earned
                    profile.save()
                except:
                    pass
            
            request.session["cart"] = {}
            if "rewards_cart" in request.session:
                del request.session["rewards_cart"]
            if "coupon_id" in request.session:
                del request.session["coupon_id"]
                
            return render(request, "checkout_success.html", {"order": order})
        else:
            order.estado = 'Rechazado'
            order.save()
            
            StockService.release_stock_for_order(order)
                
            return render(request, 'payment_failed.html', {'message': 'El pago fue rechazado por el banco.'})
            
    except TransbankError as e:
        return render(request, 'payment_failed.html', {'message': str(e)})

def download_receipt(request, order_code):
    try:
        order = Order.objects.get(code=order_code)
    except Order.DoesNotExist:
        raise Http404("Pedido no encontrado")
        
    items = OrderItem.objects.filter(order=order)
    
    template_path = 'receipt_pdf.html'
    context = {'order': order, 'items': items}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleta_{order_code}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
       
    if pisa_status.err:
       return HttpResponse('Error al generar PDF <pre>' + html + '</pre>')
    return response

def update_cart_quantity(request, key, action):
    cart = request.session.get("cart", {})
    
    if key in cart:
        if action == "increment":
            # Validate stock before incrementing
            try:
                pid = key.split('_')[0]
                product = Product.objects.get(id=pid)
                
                # Calculate total quantity of this product currently in cart (across all sizes)
                total_in_cart = 0
                for k, v in cart.items():
                    if k == str(pid) or k.startswith(f"{pid}_"):
                        total_in_cart += v
                
                if total_in_cart < product.stock:
                    cart[key] += 1
                else:
                    messages.error(request, f"No puedes agregar más unidades de {product.name}. Stock máximo alcanzado.")
            except Product.DoesNotExist:
                pass
        elif action == "decrement":
            cart[key] -= 1
            if cart[key] <= 0:
                del cart[key]
        
        request.session["cart"] = cart
        
    return redirect("cart_view")

@login_required
def regional_analysis_api(request):
    user = request.user
    if not (user.is_superuser or user.is_staff or user.groups.filter(name__iexact="admin").exists()):
        return HttpResponseForbidden("No autorizado")

    today = timezone.localdate()
    period = (request.GET.get("period", "week") or "week").lower()
    period = period if period in ("week", "month", "year") else "week"

    if period == "week":
        ref_str = request.GET.get("week", "").strip()
        try:
            ref_date = dt_date.fromisoformat(ref_str) if ref_str else today
        except Exception:
            ref_date = today
        start_date = ref_date - timedelta(days=ref_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        month_str = request.GET.get("month", "").strip()
        try:
            if month_str:
                y, m = month_str.split("-")
                ref_date = dt_date(int(y), int(m), 1)
            else:
                ref_date = dt_date(today.year, today.month, 1)
        except Exception:
            ref_date = dt_date(today.year, today.month, 1)
        start_date = ref_date
        if ref_date.month == 12:
            next_month_start = dt_date(ref_date.year + 1, 1, 1)
        else:
            next_month_start = dt_date(ref_date.year, ref_date.month + 1, 1)
        end_date = next_month_start - timedelta(days=1)
    else:  # year
        year_str = request.GET.get("year", "").strip()
        try:
            year_i = int(year_str) if year_str else today.year
        except Exception:
            year_i = today.year
        start_date = dt_date(year_i, 1, 1)
        end_date = dt_date(year_i, 12, 31)

    data = get_regional_stats(start_date, end_date)
    return JsonResponse(data)

@login_required
def profile(request):
    user = request.user
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Fetch orders
    # Assuming Customer.name matches User.username as per checkout logic
    customer = Customer.objects.filter(name=user.username).first()
    orders = []
    if customer:
        orders = Order.objects.filter(cliente=customer).exclude(estado="IniciandoPago").order_by('-fecha', '-id')
    
    # Fetch wallet coupons
    wallet_coupons = UserCoupon.objects.filter(user=user, is_used=False).select_related('coupon')
    
    return render(request, "profile.html", {
        "profile": profile, 
        "orders": orders, 
        "wallet_coupons": wallet_coupons
    })

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.email = request.POST.get("email", "").strip()
        user.save()

        profile.phone = request.POST.get("phone", "").strip()
        profile.address = request.POST.get("address", "").strip()
        profile.commune = request.POST.get("commune", "").strip()
        profile.region = request.POST.get("region", "").strip()
        profile.save()

        return redirect("profile")

    return render(request, "edit_profile.html", {"profile": profile})

@login_required
def edit_product(request, pid):
    user = request.user
    if not (user.is_staff or user.is_superuser or user.groups.filter(name__iexact="admin").exists()):
        return HttpResponseForbidden("No autorizado")
    
    try:
        product = Product.objects.get(pk=pid)
    except Product.DoesNotExist:
        raise Http404("Producto no encontrado")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = int(request.POST.get("price", "0") or 0)
        description = request.POST.get("description", "").strip()
        category_name = request.POST.get("category", "").strip()

        if name and price > 0:
            product.name = name
            product.price = price
            product.description = description
            
            if category_name:
                cat, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": slugify(category_name)})
                product.category = cat
            
            product.save()
            return redirect("producto_detalle", pid=product.id)
    
    return render(request, "edit_product.html", {"product": product})

@login_required
def marketing_dashboard(request):
    # Check permissions (admin or staff)
    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__iexact="admin").exists()):
        return redirect("pagina1")

    # Group coupons by batch
    coupon_batches = Coupon.objects.exclude(batch_name__isnull=True).exclude(batch_name="").values('batch_name').annotate(
        total_count=Count('id'),
        used_count=Sum('times_used'),
        active_count=Count('id', filter=models.Q(active=True))
    ).order_by('-batch_name')
    
    # Get Bulk Offers History
    bulk_offers = BulkOffer.objects.all().order_by('-created_at')
    
    # Prepare products data for the grid selector
    products_qs = Product.objects.select_related('category').prefetch_related(
        models.Prefetch('bulk_offers', queryset=BulkOffer.objects.filter(active=True), to_attr='active_offers')
    ).all().order_by('id')
    
    products_data = []
    for p in products_qs:
        active_offer = p.active_offers[0].name if p.active_offers else None
        products_data.append({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'image_url': p.image_url,
            'category': p.category.name if p.category else "Sin Categoría",
            'active_offer': active_offer
        })
        
    categories = Category.objects.all().order_by('name')
    
    # Forms
    bulk_form = BulkDiscountForm()
    gen_form = CouponGenerationForm()

    if request.method == "POST":
        if "bulk_discount" in request.POST:
            bulk_form = BulkDiscountForm(request.POST)
            if bulk_form.is_valid():
                products = bulk_form.cleaned_data['products']
                discount = bulk_form.cleaned_data['discount_percentage']
                action = bulk_form.cleaned_data['action']
                name = bulk_form.cleaned_data.get('name')
                
                if action == 'apply':
                    # Create BulkOffer record
                    offer_name = name if name else f"Oferta Masiva {timezone.now().strftime('%d/%m/%Y %H:%M')}"
                    bulk_offer = BulkOffer.objects.create(
                        name=offer_name,
                        discount_percentage=discount,
                        active=True
                    )
                    bulk_offer.products.set(products)
                    
                    count = 0
                    for product in products:
                        detail, created = ProductDetail.objects.get_or_create(product=product)
                        detail.descuento_pct = discount
                        detail.save()
                        count += 1
                    
                    messages.success(request, f"Oferta '{offer_name}' aplicada a {count} productos.")
                
                elif action == 'remove':
                    # Just remove discount from selected products (manual cleanup)
                    count = 0
                    for product in products:
                        detail, created = ProductDetail.objects.get_or_create(product=product)
                        detail.descuento_pct = 0
                        detail.save()
                        count += 1
                    messages.success(request, f"Descuentos removidos de {count} productos.")
                
                return redirect("marketing_dashboard")
        
        elif "generate_coupons" in request.POST:
            gen_form = CouponGenerationForm(request.POST)
            if gen_form.is_valid():
                # Pass batch name logic inside form or handle here?
                # Let's handle it here by modifying the form method or just doing it manually
                # Ideally we update the form class, but for now let's just use the form data
                quantity = gen_form.cleaned_data['quantity']
                discount = gen_form.cleaned_data['discount_percentage']
                days = gen_form.cleaned_data['valid_days']
                limit = gen_form.cleaned_data['usage_limit']
                prefix = gen_form.cleaned_data['prefix'] or "GEN"
                custom_batch_name = gen_form.cleaned_data.get('batch_name')
                
                batch_name = custom_batch_name if custom_batch_name else f"Lote {prefix} - {timezone.now().strftime('%d/%m %H:%M')}"
                
                created_count = 0
                now = timezone.now()
                valid_to = now + timezone.timedelta(days=days)
                
                for _ in range(quantity):
                    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    code = f"{prefix}-{random_str}"
                    while Coupon.objects.filter(code=code).exists():
                        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                        code = f"{prefix}-{random_str}"
                    
                    Coupon.objects.create(
                        code=code,
                        discount_percentage=discount,
                        valid_from=now,
                        valid_to=valid_to,
                        usage_limit=limit,
                        active=True,
                        batch_name=batch_name
                    )
                    created_count += 1

                messages.success(request, f"Se han generado {created_count} cupones en el lote '{batch_name}'.")
                return redirect("marketing_dashboard")

    # Rewards Data
    rewards = PointReward.objects.all().order_by('-active', 'points_cost')
    all_products = Product.objects.filter(stock__gt=0)
    all_coupons = Coupon.objects.filter(active=True)

    context = {
        "coupon_batches": coupon_batches,
        "bulk_offers": bulk_offers,
        "bulk_form": bulk_form,
        "gen_form": gen_form,
        "products_json": json.dumps(products_data),
        "categories": categories,
        "rewards": rewards,
        "all_products": all_products,
        "all_coupons": all_coupons,
        "active_tab": request.GET.get('tab', 'coupons')
    }
    return render(request, "marketing_dashboard.html", context)

@login_required
def create_reward(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
        
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        points_cost = int(request.POST.get("points_cost"))
        reward_type = request.POST.get("reward_type")
        image_url = request.POST.get("image_url", "")
        
        product_id = request.POST.get("product_id")
        
        # Coupon Generator Params
        gen_quantity = request.POST.get("gen_quantity")
        gen_discount = request.POST.get("gen_discount")
        gen_days = request.POST.get("gen_days")
        gen_prefix = request.POST.get("gen_prefix", "REWARD")

        valid_until_str = request.POST.get("valid_until")
        
        valid_until = None
        if valid_until_str:
            valid_until = valid_until_str 
            
        # Stock for Product Rewards
        stock = 0
        if reward_type == 'PRODUCT':
            try:
                stock = int(request.POST.get("stock", 0))
            except (ValueError, TypeError):
                stock = 0

        reward = PointReward(
            name=name,
            description=description,
            points_cost=points_cost,
            reward_type=reward_type,
            image_url=image_url,
            valid_until=valid_until,
            stock=stock
        )
        
        if reward_type == 'PRODUCT' and product_id:
            reward.product_id = product_id
            # Auto-fill name/image if empty
            if not name:
                p = Product.objects.get(id=product_id)
                reward.name = p.name
            if not image_url:
                p = Product.objects.get(id=product_id)
                reward.image_url = p.image_url
                
        elif reward_type == 'COUPON':
            # Generate Batch
            try:
                qty = int(gen_quantity)
                discount = int(gen_discount)
                days = int(gen_days)
                
                batch_name = f"REWARD-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                reward.coupon_batch_name = batch_name
                
                # Set default name/image if empty
                if not name:
                    reward.name = f"Cupón {discount}% Descuento"
                if not image_url:
                    reward.image_url = "https://cdn-icons-png.flaticon.com/512/726/726476.png" # Generic coupon icon

                # Generate Coupons
                now = timezone.now()
                valid_to = now + timezone.timedelta(days=days)
                
                for _ in range(qty):
                    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    code = f"{gen_prefix}-{random_str}"
                    while Coupon.objects.filter(code=code).exists():
                        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                        code = f"{gen_prefix}-{random_str}"
                    
                    Coupon.objects.create(
                        code=code,
                        discount_percentage=discount,
                        valid_from=now,
                        valid_to=valid_to,
                        usage_limit=1, # Single use per coupon
                        active=True,
                        batch_name=batch_name
                    )
            except (ValueError, TypeError):
                messages.error(request, "Error en los parámetros del generador de cupones.")
                return redirect("/marketing/?tab=rewards")
            
        reward.save()
        messages.success(request, "Recompensa creada exitosamente.")
        
    return redirect("/marketing/?tab=rewards")

@login_required
def toggle_reward_status(request, rid):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
    
    reward = get_object_or_404(PointReward, id=rid)
    reward.active = not reward.active
    reward.save()
    messages.success(request, f"Recompensa '{reward.name}' {'activada' if reward.active else 'desactivada'}.")
    return redirect("/marketing/?tab=rewards")

@login_required
def delete_reward(request, rid):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
    
    reward = get_object_or_404(PointReward, id=rid)
    reward.delete()
    messages.success(request, "Recompensa eliminada.")
    return redirect("/marketing/?tab=rewards")

@login_required
def revert_bulk_offer(request, oid):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
        
    try:
        offer = BulkOffer.objects.get(id=oid)
        if offer.active:
            count = 0
            for product in offer.products.all():
                # Reset discount to 0
                # Note: This might overwrite other overlapping offers. 
                # For a simple system, this is acceptable behavior.
                if hasattr(product, 'detail'):
                    product.detail.descuento_pct = 0
                    product.detail.save()
                    count += 1
            
            offer.active = False
            offer.save()
            messages.success(request, f"Oferta '{offer.name}' revertida. {count} productos actualizados.")
        else:
            messages.warning(request, "Esta oferta ya fue revertida o está inactiva.")
    except BulkOffer.DoesNotExist:
        messages.error(request, "Oferta no encontrada.")
        
    return redirect("marketing_dashboard")

@login_required
def delete_coupon_batch(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
        
    batch_name = request.GET.get('batch_name')
    if batch_name:
        count, _ = Coupon.objects.filter(batch_name=batch_name).delete()
        messages.success(request, f"Se eliminaron {count} cupones del lote '{batch_name}'.")
    
    return redirect("marketing_dashboard")


@login_required
def coupon_create(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
        
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cupón creado exitosamente.")
            return redirect("marketing_dashboard")
    else:
        form = CouponForm()
    
    return render(request, "coupon_form.html", {"form": form, "title": "Crear Cupón"})

@login_required
def coupon_edit(request, cid):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
        
    coupon = Coupon.objects.get(id=cid)
    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Cupón actualizado exitosamente.")
            return redirect("marketing_dashboard")
    else:
        form = CouponForm(instance=coupon)
    
    return render(request, "coupon_form.html", {"form": form, "title": "Editar Cupón"})

@login_required
def coupon_delete(request, cid):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
        
    coupon = Coupon.objects.get(id=cid)
    coupon.delete()
    messages.success(request, "Cupón eliminado.")
    return redirect("marketing_dashboard")

def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                request.session['coupon_id'] = coupon.id
                
                # Calculate totals for AJAX response
                if is_ajax:
                    cart = request.session.get("cart", {})
                    total = 0
                    products = Product.objects.filter(id__in=cart.keys())
                    product_map = {str(p.id): p for p in products}
                    
                    for pid, qty in cart.items():
                        p = product_map.get(pid)
                        if p:
                            price = p.price
                            try:
                                price = p.detail.discounted_price
                            except ProductDetail.DoesNotExist:
                                pass
                            total += price * qty
                    
                    discount_amount = int(total * (coupon.discount_percentage / 100))
                    final_total = total - discount_amount
                    
                    return JsonResponse({
                        'success': True,
                        'message': f"Cupón aplicado: {coupon.discount_percentage}% de descuento",
                        'discount_percentage': coupon.discount_percentage,
                        'discount_amount': discount_amount,
                        'new_total': final_total,
                        'code': coupon.code
                    })

                messages.success(request, f"Cupón {code} aplicado: {coupon.discount_percentage}% de descuento.")
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'message': "Cupón no válido o expirado"})
                messages.error(request, "El cupón no es válido o ha expirado.")
        except Coupon.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'message': "Cupón no válido"})
            messages.error(request, "El cupón no existe.")
            
    return redirect("cart_view")

def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.info(request, "Cupón removido.")
    return redirect("cart_view")

@login_required
def bulk_offer_detail(request, oid):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("pagina1")
    
    offer = get_object_or_404(BulkOffer, id=oid)
    products = offer.products.all()
    
    # Pre-calculate discounted prices for display
    for p in products:
        p.calculated_discounted_price = int(p.price * (1 - offer.discount_percentage / 100))

    return render(request, "bulk_offer_detail.html", {
        "offer": offer,
        "products": products
    })

@login_required
def get_coupon_batch(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    batch_name = request.GET.get('batch_name')
    if not batch_name:
        return JsonResponse({'error': 'Nombre de lote requerido'}, status=400)
        
    coupons = Coupon.objects.filter(batch_name=batch_name).values_list('code', flat=True)
    return JsonResponse({'coupons': list(coupons)})

@login_required
def barcode_tool(request):
    # Check permissions (trabajador or admin)
    is_worker = request.user.groups.filter(name='trabajador').exists()
    is_admin = request.user.is_staff or request.user.is_superuser or request.user.groups.filter(name='admin').exists()
    
    if not (is_worker or is_admin):
        return HttpResponseForbidden("No tienes permiso para acceder a esta herramienta.")

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    
    products = Product.objects.select_related('category').prefetch_related('sizes').all().order_by('id')
    
    if query:
        products = products.filter(name__icontains=query)
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    categories = Category.objects.all()
    
    context = {
        "products": products,
        "categories": categories,
        "current_category": category_slug,
        "query": query
    }
    return render(request, "barcode_tool.html", context)

@login_required
def print_barcodes(request):
    # Check permissions
    is_worker = request.user.groups.filter(name='trabajador').exists()
    is_admin = request.user.is_staff or request.user.is_superuser or request.user.groups.filter(name='admin').exists()
    
    if not (is_worker or is_admin):
        return HttpResponseForbidden("No tienes permiso para acceder a esta herramienta.")
        
    if request.method == "POST":
        items_to_print = []
        
        # Iterate over POST data to find quantities
        for key, value in request.POST.items():
            try:
                qty = int(value)
                if qty <= 0:
                    continue
            except ValueError:
                continue
                
            if key.startswith("qty_product_"):
                # Handle product without sizes
                try:
                    pid = int(key.replace("qty_product_", ""))
                    product = Product.objects.get(id=pid)
                    code = f"P{product.id}"
                    for _ in range(qty):
                        items_to_print.append({
                            "name": product.name,
                            "code": code,
                            "price": product.price
                        })
                except (ValueError, Product.DoesNotExist):
                    continue
                    
            elif key.startswith("qty_size_"):
                # Handle product size
                try:
                    sid = int(key.replace("qty_size_", ""))
                    size = ProductSize.objects.select_related('product').get(id=sid)
                    code = f"P{size.product.id}-S{size.id}"
                    for _ in range(qty):
                        items_to_print.append({
                            "name": f"{size.product.name} - {size.label}",
                            "code": code,
                            "price": size.product.price
                        })
                except (ValueError, ProductSize.DoesNotExist):
                    continue
        
        return render(request, "print_barcodes.html", {"items": items_to_print})
    
    return redirect('barcode_tool')

@login_required
def rewards_catalog(request):
    rewards = PointReward.objects.filter(active=True)
    user_points = request.user.profile.points
    
    context = {
        'rewards': rewards,
        'user_points': user_points,
    }
    return render(request, 'rewards.html', context)

@login_required
def redeem_reward(request, reward_id):
    reward = get_object_or_404(PointReward, id=reward_id, active=True)
    
    size = None
    if reward.reward_type == 'PRODUCT' and reward.product and reward.product.has_sizes:
        if request.method == 'POST':
            size = request.POST.get('size')
        
        if not size:
             messages.error(request, "Debes seleccionar una talla para canjear este producto.")
             return redirect('rewards_catalog')

    try:
        reward = RewardService.redeem_reward(request.user, reward_id, size)
        
        if reward.reward_type == 'PRODUCT':
            rewards_cart = request.session.get('rewards_cart', {})
            product_id = str(reward.product.id)
            
            key = product_id
            if size:
                key = f"{product_id}_{size}"
                
            rewards_cart[key] = rewards_cart.get(key, 0) + 1
            request.session['rewards_cart'] = rewards_cart
            messages.success(request, f"¡Canje exitoso! El producto {reward.product.name} ha sido agregado a tu carrito.")
        else:
            messages.success(request, "¡Canje exitoso! El cupón ha sido guardado en tu chequera.")

    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, "Ocurrió un error inesperado al procesar el canje.")
        
    return redirect('rewards_catalog')

def is_worker(user):
    return user.groups.filter(name='trabajador').exists() or user.is_superuser

@login_required
@user_passes_test(is_worker)
def fulfillment_game(request):
    # Find the oldest pending order
    order = Order.objects.filter(estado='Pendiente').order_by('fecha', 'id').first()
    
    if not order:
        return render(request, 'fulfillment_empty.html')
    
    # Get items
    items = OrderItem.objects.filter(order=order).select_related('product')
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'fulfillment_game.html', context)

@login_required
@user_passes_test(is_worker)
def complete_fulfillment(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        if order.estado == 'Pendiente':
            order.estado = 'Procesado'
            order.save()
            messages.success(request, f"Pedido {order.code} procesado correctamente.")
        return redirect('fulfillment_game')
    return redirect('fulfillment_game')

def is_staff_or_worker(user):
    return user.is_staff or user.is_superuser or user.groups.filter(name__in=['admin', 'trabajador']).exists()

@login_required
@user_passes_test(is_staff_or_worker)
def order_list(request):
    search_query = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')

    orders = Order.objects.filter(channel='Online').exclude(estado="IniciandoPago").order_by('-id')

    if search_query:
        # Check for barcode patterns
        barcode_size_match = re.match(r'^P(\d+)-S(\d+)$', search_query, re.IGNORECASE)
        barcode_product_match = re.match(r'^P(\d+)$', search_query, re.IGNORECASE)

        if barcode_size_match:
            pid = barcode_size_match.group(1)
            sid = barcode_size_match.group(2)
            try:
                size_obj = ProductSize.objects.get(id=sid)
                orders = orders.filter(
                    items__product__id=pid,
                    items__size=size_obj.label
                ).distinct()
            except ProductSize.DoesNotExist:
                orders = orders.none()
        elif barcode_product_match:
            pid = barcode_product_match.group(1)
            orders = orders.filter(items__product__id=pid).distinct()
        else:
            orders = orders.filter(
                models.Q(cliente__name__icontains=search_query) |
                models.Q(items__product__name__icontains=search_query) |
                models.Q(items__product__id__icontains=search_query) |
                models.Q(code__icontains=search_query)
            ).distinct()

    if date_filter:
        orders = orders.filter(fecha=date_filter)

    paginator = Paginator(orders, 10) # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/orders_rows.html', {'orders': page_obj})
    
    return render(request, 'orders_list.html', {
        'orders': page_obj,
        'search_query': search_query,
        'date_filter': date_filter
    })

@login_required
def check_new_orders(request):
    user = request.user
    if not (user.groups.filter(name__iexact="trabajador").exists() or user.is_staff or user.is_superuser):
        return JsonResponse({"count": 0, "latest_id": 0})
    
    qs = Order.objects.filter(estado="Pendiente").exclude(estado="IniciandoPago").order_by('-id')
    count = qs.count()
    latest_id = qs.first().id if count > 0 else 0
    
    return JsonResponse({"count": count, "latest_id": latest_id})

@login_required
def print_shipping_label(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Only allow for orders with delivery_method='Despacho'
    if order.delivery_method != 'Despacho':
        return HttpResponseForbidden("Este pedido no es para despacho.")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="label_{order.code}.pdf"'

    # Create PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Label dimensions (100mm x 150mm standard shipping label)
    label_w = 100 * mm
    label_h = 150 * mm
    
    # Position label on top-left of A4 with some margin
    x_start = 10 * mm
    y_start = height - label_h - 10 * mm
    
    # Draw border
    p.rect(x_start, y_start, label_w, label_h)
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(x_start + 5*mm, y_start + label_h - 15*mm, "ETIQUETA DE ENVÍO")
    
    p.setFont("Helvetica", 10)
    p.drawString(x_start + 5*mm, y_start + label_h - 25*mm, f"Fecha: {order.fecha.strftime('%d/%m/%Y')}")
    
    # Sender Info (Store)
    p.line(x_start, y_start + label_h - 30*mm, x_start + label_w, y_start + label_h - 30*mm)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x_start + 5*mm, y_start + label_h - 38*mm, "REMITENTE:")
    p.setFont("Helvetica", 10)
    p.drawString(x_start + 5*mm, y_start + label_h - 43*mm, "MultiTienda")
    p.drawString(x_start + 5*mm, y_start + label_h - 48*mm, "Av. Principal 123")
    p.drawString(x_start + 5*mm, y_start + label_h - 53*mm, "Santiago, RM")
    
    # Recipient Info
    p.line(x_start, y_start + label_h - 60*mm, x_start + label_w, y_start + label_h - 60*mm)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x_start + 5*mm, y_start + label_h - 70*mm, "DESTINATARIO:")
    
    p.setFont("Helvetica-Bold", 14)
    recipient = order.recipient_name if order.recipient_name else order.cliente.name
    p.drawString(x_start + 10*mm, y_start + label_h - 80*mm, f"{recipient}")
    
    p.setFont("Helvetica", 12)
    # Handle address fields safely
    address = order.shipping_address or "Dirección no especificada"
    commune = order.shipping_commune or ""
    region = order.shipping_region or ""
    
    # Define text area
    text_width = label_w - 20*mm
    current_y = y_start + label_h - 90*mm
    
    # Address wrapping
    address_lines = simpleSplit(address, "Helvetica", 12, text_width)
    for line in address_lines:
        p.drawString(x_start + 10*mm, current_y, line)
        current_y -= 5*mm
        
    # Commune/Region wrapping
    location_str = f"{commune}, {region}"
    location_lines = simpleSplit(location_str, "Helvetica", 12, text_width)
    for line in location_lines:
        p.drawString(x_start + 10*mm, current_y, line)
        current_y -= 5*mm
    
    if order.contact_phone:
        p.drawString(x_start + 10*mm, current_y, f"Tel: {order.contact_phone}")
        
    # Barcode
    p.line(x_start, y_start + 40*mm, x_start + label_w, y_start + 40*mm)
    
    barcode_value = order.code
    barcode = code128.Code128(barcode_value, barHeight=20*mm, barWidth=0.5*mm)
    
    # Center barcode
    barcode_width = barcode.width
    barcode_x = x_start + (label_w - barcode_width) / 2
    barcode_y = y_start + 15*mm
    
    barcode.drawOn(p, barcode_x, barcode_y)
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(x_start + label_w/2, y_start + 10*mm, f"Pedido: {order.code}")
    
    p.showPage()
    p.save()
    return response

@login_required
@user_passes_test(is_staff_or_worker)
def order_detail_partial(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'partials/order_detail_modal_content.html', {'order': order})
