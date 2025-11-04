from django.shortcuts import render


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


def iniciosesiontrabajador(request):
    return render(request, "iniciosesiontrabajador.html")


def pagina3(request):
    return render(request, "pagina3.html")
