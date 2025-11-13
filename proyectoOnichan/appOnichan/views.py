import json

from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import date as dt_date, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.utils.text import slugify
from datetime import date as dt_date

from .models import (
    Product,
    ProductDetail,
    ProductSize,
    ProductSpec,
    ProductCare,
    ProductBreadcrumb,
    Customer,
    Order,
    OrderItem,
    Category,
)

def index(request):
    return pagina1(request)

def pagina1(request):
    productos = Product.objects.all().order_by("id")
    return render(request, "pagina1.html", {"productos": productos})

def login_view(request):
    """Login unificado para admin, trabajador y cliente.

    - Admin: redirige a dashboardadmin/
    - Trabajador: redirige a dashboardtrabajador/
    - Cliente: redirige a pagina1/
    """
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


def logout_view(request):
    logout(request)
    return redirect("pagina1")

@login_required
def pagina3(request):
    return render(request, "pagina3.html")

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

    # Determinar rango de fechas y metadata de navegación
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
        orders_period = Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date)
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
        orders_period = Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date)
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
        orders_period = Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date)
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
    pedidos_hoy = Order.objects.filter(fecha=today).count()
    pendientes = Order.objects.filter(estado="Pendiente").count()
    ingresos_7d = (
        Order.objects.filter(fecha__gte=start_date, fecha__lte=end_date)
        .aggregate(total=Sum("total"))
        .get("total")
        or 0
    )

    # Top products y revenue por categoría dentro del periodo seleccionado
    top = (
        OrderItem.objects.filter(order__fecha__gte=start_date, order__fecha__lte=end_date)
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
            .values("size")
            .annotate(units=Sum("cantidad"))
            .order_by("-units")
        )
        detalles_top[label] = {(r["size"] or "Único"): r["units"] for r in qs}

    cat_rows = (
        OrderItem.objects.filter(order__fecha__gte=start_date, order__fecha__lte=end_date)
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

    dashboard_data = {
        "kpis": {
            "pedidos_hoy": {"value": pedidos_hoy, "trend": ""},
            "pendientes": {"value": pendientes, "trend": ""},
            "ingresos_7d": {"value": ingresos_7d, "trend": "", "isCurrency": True},
        },
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
def pagina3(request):
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
            initial_stock = int(request.POST.get("initial_stock", "0") or 0)
            if not (name and price > 0 and image_url and category_name):
                return render(request, "pagina3.html", {"error": "Datos inválidos", "data": json.dumps(_products_payload())})

            cat, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": slugify(category_name)})
            # Generar nuevo id
            max_id = Product.objects.aggregate(mx=Max("id")).get("mx") or 100
            new_id = max_id + 1
            Product.objects.create(
                id=new_id,
                name=name,
                price=price,
                image_url=image_url,
                category=cat,
                stock=initial_stock,
            )
            return redirect("stock")

    # GET: construir dataset de productos para el front
    payload = _products_payload()
    return render(request, "pagina3.html", {"data": json.dumps(payload)})


from django.db.models import Max
def _products_payload():
    products = (
        Product.objects.select_related("category").order_by("id")
        .values("id", "name", "price", "image_url", "category__name", "stock")
    )
    out = []
    for p in products:
        out.append({
            "code": str(p["id"]),
            "name": p["name"],
            "price": p["price"],
            "category": p["category__name"] or "Otros",
            "stock": p["stock"] or 0,
            "image_url": p["image_url"],
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
        "descuento_pct": det.descuento_pct if det else 0,
        "envio": det.envio if det else "",
        "llega": det.llega if det else "",
        "warranty": det.warranty if det else "",
        "capacity_l": det.capacity_l if det else None,
    }

    descuento = d.get("descuento_pct", 0) or 0
    d["precio_original"] = round(p.price / (1 - descuento / 100)) if descuento else None

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
