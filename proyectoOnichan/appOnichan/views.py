import json

from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseForbidden
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

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
    # KPIs
    today = timezone.localdate()
    last7 = today - timezone.timedelta(days=6)

    pedidos_hoy = Order.objects.filter(fecha=today).count()
    pendientes = Order.objects.filter(estado="Pendiente").count()
    ingresos_7d = (
        Order.objects.filter(fecha__gte=last7, fecha__lte=today).aggregate(total=Sum("total")).get("total")
        or 0
    )

    # Line chart by weekday name (Mon-Sun in Spanish abbreviations)
    weekday_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    day_counts = {label: 0 for label in weekday_labels}
    delivered_counts = {label: 0 for label in weekday_labels}
    pending_counts = {label: 0 for label in weekday_labels}

    orders_7d = Order.objects.filter(fecha__gte=last7, fecha__lte=today)
    for o in orders_7d:
        # Python's weekday(): Monday=0 ... Sunday=6
        idx = o.fecha.weekday()
        label = weekday_labels[idx]
        day_counts[label] += 1
        if o.estado == "Entregado":
            delivered_counts[label] += 1
        elif o.estado == "Pendiente":
            pending_counts[label] += 1

    line_labels = weekday_labels
    line_values = [day_counts[l] for l in line_labels]
    line_detalles = {
        l: {"Entregados": delivered_counts[l], "Pendientes": pending_counts[l]} for l in line_labels
    }

    # Top products by units sold (last 30 days)
    last30 = today - timezone.timedelta(days=30)
    top = (
        OrderItem.objects.filter(order__fecha__gte=last30)
        .values("product__name")
        .annotate(units=Sum("cantidad"))
        .order_by("-units")[:4]
    )
    top_labels = [t["product__name"] for t in top]
    top_values = [t["units"] for t in top]
    detalles_top = {}
    # Breakdown by size/color (using size field) for each top product
    for label in top_labels:
        qs = (
            OrderItem.objects.filter(order__fecha__gte=last30, product__name=label)
            .values("size")
            .annotate(units=Sum("cantidad"))
            .order_by("-units")
        )
        detalles_top[label] = { (r["size"] or "Único"): r["units"] for r in qs }

    # Revenue by category (last 30 days) + online/tienda split
    cat_rows = (
        OrderItem.objects.filter(order__fecha__gte=last30)
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

    context = {"data_json": json.dumps(dashboard_data)}
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
    rows = (
        OrderItem.objects.filter(order__fecha=today)
        .values("product__name")
        .annotate(units=Sum("cantidad"))
        .order_by("product__name")
    )
    labels = [r["product__name"] for r in rows]
    values = [r["units"] for r in rows]

    data = {"labels": labels, "values": values, "date": today.isoformat()}
    return render(request, "dashboardtrabajador.html", {"data_json": json.dumps(data)})

@login_required
def pagina3(request):
    # Solo trabajadores y administradores
    user = request.user
    if not (
        user.groups.filter(name__iexact="trabajador").exists()
        or user.is_staff
        or user.is_superuser
        or user.groups.filter(name__iexact="admin").exists()
    ):
        return HttpResponseForbidden("No autorizado")
    # Obtener pedidos desde la BD y devolver la misma estructura JSON usada por el front
    orders = []
    for o in Order.objects.select_related("cliente").prefetch_related("items__product").order_by("-fecha", "code"):
        productos = [
            {"nombre": it.product.name, "cantidad": it.cantidad}
            for it in o.items.all()
        ]
        orders.append({
            "id": o.code,
            "fecha": o.fecha.isoformat(),
            "cliente": o.cliente.name,
            "total": o.total,
            "estado": o.estado,
            "productos": productos,
        })

    estadisticas = {
        "total_pedidos": len(orders),
        "pendientes": sum(1 for p in orders if p["estado"] == "Pendiente"),
        "despachados": sum(1 for p in orders if p["estado"] == "Despachado"),
        "entregados": sum(1 for p in orders if p["estado"] == "Entregado"),
        "cancelados": sum(1 for p in orders if p["estado"] == "Cancelado"),
        "total_ventas": sum(p["total"] for p in orders),
    }

    data = {"orders": orders, "estadisticas": estadisticas}
    return render(request, "pagina3.html", {"data": json.dumps(data)})

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

            today = timezone.localdate()
            # Cliente genérico de mostrador
            cliente, _ = Customer.objects.get_or_create(name="Mostrador")

            # Generar código único simple POSYYYYMMDD-XXXX
            base = today.strftime("POS%Y%m%d")
            seq = 1
            while True:
                code = f"{base}-{seq:04d}"
                if not Order.objects.filter(code=code).exists():
                    break
                seq += 1

            order = Order.objects.create(
                code=code,
                fecha=today,
                cliente=cliente,
                total=0,
                estado="Entregado",
                channel="Tienda",  # presencial
            )

            total = 0
            for pid, qty in cart.items():
                try:
                    p = Product.objects.get(pk=int(pid))
                except Product.DoesNotExist:
                    continue
                qty = int(qty)
                item = OrderItem.objects.create(
                    order=order,
                    product=p,
                    cantidad=qty,
                    price=p.price,
                    size="",
                )
                total += item.subtotal

            order.total = total
            order.save()

            # Vaciar carrito
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
        {"productos": productos, "cart_items": cart_items, "cart_total": cart_total},
    )
