# Proyecto Onichan - Documentación de la Plataforma de E-commerce

## Descripción General del Proyecto
"Onichan" es una plataforma de comercio electrónico moderna diseñada para proporcionar una experiencia de compra fluida. Cuenta con un catálogo de productos robusto, gestión de cuentas de usuario, un carrito de compras dinámico y un sistema de billetera para la fidelización de clientes.

## Arquitectura
El proyecto está construido utilizando el framework web **Django** (Python) y utiliza **Bootstrap 5** para la interfaz frontend, asegurando capacidad de respuesta y una estética moderna.

*   **Backend**: Django 4.x
*   **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
*   **Base de Datos**: SQLite (por defecto para desarrollo)
*   **Fuentes**: Inter (Google Fonts)

## Sistemas Clave

### Regiones Dinámicas
Para optimizar el rendimiento y la experiencia del usuario, la plataforma maneja las regiones y comunas de Chile dinámicamente en el lado del cliente.
*   **Implementación**: `static/js/regions.js`
*   **Fuente de Datos**: `chile-regiones-2025.json`
*   **Beneficio**: Carga datos de regiones y comunas sin consultas adicionales a la base de datos, proporcionando retroalimentación instantánea al usuario durante el registro y la edición del perfil.

### Carrito y Pago (Checkout)
El sistema de carrito de compras está diseñado para ser flexible y fácil de usar.
*   **Lógica**: `cart.js` maneja las interacciones del frontend.
*   **Características**:
    *   Actualizaciones dinámicas de campos de entrega.
    *   Aplicación de cupones basada en AJAX.
    *   Cálculo del total en tiempo real.

### Sistema de Billetera (Wallet)
Un programa de fidelización integrado directamente en el perfil del usuario.
*   **Funcionalidad**: Los usuarios ganan puntos y cupones basados en su actividad.
*   **Uso**: Los puntos pueden ser canjeados por descuentos en futuras compras.

## Modelos

*   **Product**: Representa los artículos disponibles para la venta. Incluye campos para nombre, descripción, precio, stock e imagen.
*   **Order**: Rastrea las compras de los clientes, incluyendo estado, monto total y detalles de entrega.
*   **UserProfile**: Extiende el modelo de Usuario estándar de Django para almacenar información adicional como número de teléfono, dirección, región y saldo de la billetera.
*   **Coupon**: Gestiona los códigos de descuento que se pueden aplicar a los pedidos.

## Configuración

Para configurar el proyecto localmente, sigue estos pasos:

1.  **Instalar Dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Aplicar Migraciones**:
    ```bash
    python manage.py migrate
    ```

3.  **Ejecutar el Servidor**:
    ```bash
    python manage.py runserver
    ```

## Estructura de Carpetas

*   `proyectoOnichan/`: Directorio principal de configuración del proyecto.
*   `appOnichan/`: La aplicación central que contiene modelos, vistas y lógica.
    *   `static/`: Archivos estáticos (CSS, JS, Imágenes).
        *   `js/`: Módulos JavaScript personalizados (`regions.js`, `cart.js`).
        *   `css/`: Estilos personalizados (`base.css`).
    *   `templates/`: Plantillas HTML para la aplicación.
        *   `partials/`: Componentes de plantilla reutilizables (`navbar_right.html`, `product_card.html`).
    *   `migrations/`: Archivos de migración de base de datos.
*   `manage.py`: Utilidad de línea de comandos de Django.
