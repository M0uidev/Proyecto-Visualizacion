# Documentación Técnica - Proyecto Visualización

Documentación técnica para el desarrollo y mantenimiento del proyecto. Guía sobre la funcionalidad y estructura del código.

---

## 1. pagina1.html - Página de Productos

### Descripción General
Página principal de catálogo de productos con carrusel de ofertas, filtrado dinámico y paginación AJAX.

### Archivos Asociados
- `css/dashboardtrabajador.css` - Estilos de dashboard base
- `css/pages/pagina1.css` - Estilos específicos de la página
- Script inline en `pagina1.html`

### Funcionalidad Principal

#### Sección Hero
```html
- Gradiente lineal como fondo
- CTA principal "Ver Ofertas" que navega a #ofertas
```

#### Carrusel de Ofertas (Horizontal)
```javascript
- ID: offersCarousel
- Botones: #prevOffer, #nextOffer
- Comportamiento: scroll horizontal suave con loop (vuelve al inicio/final automáticamente)
- Lógica:
  * nextBtn: Avanza cardWidth + gap (16px)
  * Detecta si llegó al final y vuelve al inicio
  * prevBtn: Lo mismo pero en reversa
```

#### Sistema de Filtrado AJAX
```javascript
- Chips de filtro por categoría (data-category)
- Preserva estado: categoría, sort, items_per_page en URL
- Actualización dinámica del contenedor #product-list-container
- Dos tipos de eventos:
  * Filtro de categoría: actualiza URL + fetch
  * Paginación: listener en .pagination .ajax-link
  * Items por página: listener en #items select
```

#### Funciones Clave
- `fetchProducts(url)`: Realiza fetch AJAX, actualiza DOM, maneja historia del navegador
- `attachPaginationListeners()`: Vincula clics de paginación a fetchProducts
- `moveModalsToBody(container)`: Resuelve conflicto z-index de modales Bootstrap en móvil
- `updateFormInputs(url)`: Sincroniza formularios con parámetros URL

#### Manejo de Modales
El script mueve modales dinámicos al body para evitar problemas de z-index y backdrop en contenedores con scroll. Marca modales del product-list-container con clase `list-modal` para limpiarlos antes de recargar.

---

## 2. cart.html - Carrito de Compras

### Descripción General
Carrito funcional con gestión de cantidades, cupones, cálculo de totales y formulario de checkout con Webpay.

### Archivos Asociados
- `js/cart.js` - Lógica del carrito
- `js/regions.js` - Selector dinámico de regiones/comunas

### Estructura Principal

#### Tabla de Productos
```html
- Columnas: Producto | Precio | Cantidad | Total | Eliminar
- Cantidad: input-group con botones +/- (deshabilita + si stock=qty)
- Descuentos: muestra precio tachado + precio con descuento
- Productos gratis: badge "GRATIS (Puntos)"
```

#### Sección de Cupones
```javascript
- Dos estados:
  1. Sin cupón aplicado: form #couponForm para ingresar código
  2. Con cupón: muestra resumen + botón para quitar cupón
  
- Modal #walletModal: lista cupones del usuario (wallet)
  * onclick="applyWalletCoupon(code)": llena input y envía form
```

#### Formulario de Checkout
```html
- Datos contacto: nombre, apellido, teléfono, email (precarga desde user)
- Entrega: Radio toggle Despacho/Retiro
- Despacho: selector dinámico región/comuna (chile-regiones-2025.json)
- CTA: Botón "Pagar con Webpay"
```

#### Funciones en cart.js

**applyWalletCoupon(code)**
- Llena input #couponCode con código
- Cierra modal #walletModal
- Dispara submit en #couponForm

**toggleDeliveryFields()**
- Si Despacho: muestra #shippingFields, marca required
- Si Retiro: oculta #shippingFields, quita required

**Manejo de Cupones (AJAX)**
- POST a `apply_coupon` con action=apply_coupon
- Respuesta JSON: `{success, code, discount_amount, new_total}`
- Actualiza UI: oculta form, muestra resumen descuento, actualiza total
- Errores: muestra en #couponError

#### Funciones en regions.js

**initRegionSelector(jsonUrl, userRegion, userCommune)**
- Carga JSON de regiones desde URL estática
- Puebla select #regionSelect con todas las regiones
- Al cambiar región: extrae comunas de provincias y puebla #communeSelect (ordenadas alfabéticamente)
- Preselecciona región/comuna del usuario si existen

---

## 3. login.html - Inicio de Sesión

### Descripción General
Formulario de login con validación cliente, toggle de visibilidad de contraseña y feedback visual.

### Archivos Asociados
- `js/login.js` - Lógica de validación y envío
- `css/auth.css` - Estilos de auth

### Estructura

#### Formulario
```html
- Inputs: usuario, contraseña (ambos required)
- Toggle contraseña: botón #togglePwd (ícono ojo)
- Envío: #submitBtn
- Alertas: #alertBox (oculto por defecto)
```

#### Validaciones en login.js

**setInvalid(input, message)**
- Agrega clase `is-invalid` al input
- Busca `.invalid-feedback` o siguiente elemento sibling
- Inserta mensaje de error

**clearInvalid(input)**
- Remueve clase `is-invalid`

**showAlert(type, text)**
- Asigna clase `alert alert-{type}` a #alertBox
- Inserta texto de alerta

#### Flujo de Envío
1. Previene default
2. Oculta alertas previas
3. Valida campos (usuario y contraseña no vacíos)
4. Si inválido: muestra errores
5. Si válido:
   - Deshabilita botón, muestra spinner
   - setTimeout 600ms simulando envío
   - Muestra "Ingreso exitoso"
   - Redirige a data-redirect-url si existe

#### Toggle Contraseña
- Cambia type entre password/text
- Intercambia ícono bi-eye / bi-eye-slash

#### Limpieza de Errores
- Event listener 'input' en form: llama clearInvalid() si es .form-control

---

## 4. stock.html - Administración de Stock

### Descripción General
Sistema de gestión de inventario con grilla de productos, filtrado, búsqueda, gráfico donut y modales para editar stock.

### Archivos Asociados
- `js/pagina3.js` - Lógica principal (603 líneas)
- `css/pages/pagina3.css` - Estilos
- `css/dashboardtrabajador.css` - Estilos base
- Datos: JSON en `#stock-data`

### Estructura de Datos

```javascript
// Cada producto tiene:
{
  code: String,
  name: String,
  price: Number,
  category: String,
  stock: Number,
  image_url: String,
  description: String,
  status: 'Disponible' | 'Stock Bajo' | 'Sin Stock',
  sizes: Array,
  has_sizes: Boolean
}

// Estados de stock:
- stock > 10: 'Disponible' (badge success)
- 0 < stock <= 10: 'Stock Bajo' (badge warning)
- stock <= 0: 'Sin Stock' (badge danger)
```

### Interfaz Principal

#### Filtros y Búsqueda
```html
- #productSearch: búsqueda por nombre, ID o categoría
- #categoryFilter: dropdown de categorías (poblado dinámicamente)
- #sortFilter: ordenamiento (nombre, stock desc/asc, reciente)
```

#### Grilla de Productos
```javascript
- #productsGrid: contenedor flex gap-3
- Cada producto es tarjeta:
  * Imagen (150px height, object-fit cover)
  * Badge estado en esquina (top-right)
  * Nombre (truncado, tooltip)
  * ID, Categoría
  * Precio, Stock
  * Botones: Editar (siempre), Eliminar (solo admin)
  
- Hover: translateY(-5px)
```

#### Gráficos
```javascript
- Chart.js: tipo donut
- Datos: stock total por categoría
- Colores: paleta de 7 colores rotativa
- onClick: muestra modal con detalle categoría (gráfico barras H)
```

### Modales (Solo Admin)

#### Modal Agregar Producto
```html
- Campos: nombre, precio, imagen (file), categoría, descripción, stock inicial
- Checkbox "¿Tiene Tallas?" muestra #sizeScaleContainer
- Select escala tallas (S-XL, números 36-44, custom)
- Si custom: textarea para tallas manuales
- Form method=post action={% url 'stock' %} con action=add_product
```

#### Modal Editar Producto
```html
- Prellenado con datos del producto
- Campos: nombre, precio, image_url (texto, no file), categoría, descripción, stock, tallas
- Envío AJAX: POST fetch con X-CSRFToken header
- Respuesta: {ok, error}
- Success: actualiza PRODUCTS[], rerenderiza, cierra modal
```

### Modal Ajustar Stock (Trabajadores)

```html
- Muestra: nombre producto, stock actual
- Input con botones +/- para ajuste
- Vista previa: "Stock Final Resultante: X"
- Input hidden guarda stock actual para cálculo

function updateFinalStock():
  - final = Math.max(0, current + adjustment)
  - actualiza #finalStockPreview
```

### Funciones Principales en pagina3.js

#### filterProducts(products)
- Filtra por categoría (currentCategory)
- Filtra por búsqueda (nombre, code, category)
- Retorna array filtrado

#### renderGrid()
- Obtiene productos filtrados
- Ordena según currentSort
- Genera HTML de tarjetas dinámicamente
- Actualiza #tableStats con conteo
- Llama updateChart()

#### updateStockStatus(product)
- Evalúa stock y retorna estado string
- Usado al cargar y actualizar productos

#### getStatusClass(status)
- Mapea estado a clase Bootstrap (success, warning, danger)

#### updateChart()
- Destruye gráfico anterior si existe
- Calcula datos por categoría
- Crea nueva instancia Chart.js tipo donut
- Vincula evento click para mostrar modal detalle

#### Manejo de Edición (Admin)
1. Click en botón editar → llena campos
2. Submit form → fetch POST con FormData
3. Respuesta JSON → actualiza PRODUCTS[] localmente
4. Cierra modal, rerenderiza

#### Manejo de Ajuste Stock (Worker)
1. Click editar (no admin) → abre modal ajustar
2. Botones +/- actualizan input y preview
3. Submit → fetch POST con nuevo stock
4. Respuesta: actualiza producto localmente

#### Event Listeners
- #categoryFilter change: renderGrid()
- #sortFilter change: renderGrid()
- #productSearch input: renderGrid()
- #chartModal hidden: destruye modalChartInstance
- #productsGrid click: maneja acciones edit/delete
- #editProductForm submit: AJAX actualizar
- #addHasSizes change: toggle #sizeScaleContainer
- #sizeScaleSelect change: toggle custom tallas input
- #adjustStockForm submit: AJAX actualizar stock
- btnIncrease/btnDecrease: incrementa/decrementa adjustment

---

## 5. register.html - Registro de Usuario

### Descripción General
Formulario de registro con validación HTML5, selector dinámico de región/comuna y prevención de doble envío.

### Archivos Asociados
- `js/regions.js` - Selector dinámico de regiones/comunas

### Estructura del Formulario

#### Campos del Registro
```html
- Usuario (text, required)
- Email (email, required)
- Contraseña (password, required)
- Nombre (text, required)
- Apellido (text, required)
- Teléfono (tel, required)
- Dirección (text, required)
- Región (select, required) - poblado dinámicamente
- Comuna (select, required, disabled) - se habilita al seleccionar región
```

#### Validación y Envío
```javascript
- Script inline en extra_js block
- Inicializa selector de regiones con JSON estático
- Listener en submit:
  * Si botón está disabled → previene envío (protege doble click)
  * De otro modo: deshabilita botón, muestra spinner loading "Registrando..."
  * Permite envío normal del formulario
```

#### Funcionalidad del Selector de Regiones
- `initRegionSelector()` carga `chile-regiones-2025.json`
- Al cargar página: puebla #regionSelect con todas las regiones
- Al cambiar región: extrae comunas de provincias, puebla #communeSelect alfabéticamente
- #communeSelect comienza disabled, se habilita cuando región tiene valor

#### Seguridad
- CSRF token incluido en formulario ({% csrf_token %})
- Validación requerida en HTML5 (required attributes)
- Doble envío prevenido via button.disabled + estado en submit

---

## 6. rewards.html - Catálogo de Recompensas

### Descripción General
Página de canje de puntos con catálogo de recompensas (productos y cupones) usando modales Bootstrap para selección de tallas o confirmación.

### Archivos Asociados
- Ningún archivo JS externo (todo está en Django template)
- `css/dashboardtrabajador.css` - Estilos base
- `css/pages/pagina1.css` - Estilos de página

### Estructura Principal

#### Hero Section
```html
- Gradiente oro-naranja
- Muestra saldo de puntos del usuario ({{ user_points }})
- Descripción del sistema de canje
```

#### Catálogo de Recompensas
```html
- Grid 3 columnas (responsive: 1 col móvil, 3 col desktop)
- Cada tarjeta muestra:
  * Imagen (ratio-16x9 object-fit-cover)
  * Nombre y descripción
  * Badge: tipo recompensa (PRODUCT, COUPON, DISCOUNT)
  * Badge: costo en puntos (amarillo)
  * Cantidad disponible (si aplica)
  * Botón "Canjear" (deshabilitado si puntos insuficientes)
```

#### Tipos de Modales

**Modal para Productos con Tallas**
```html
- ID: rewardModal-{reward.id}
- Contenido: grid de radio buttons para cada talla del producto
- Tallas vienen de reward.product.sizes.all (relación ManyToMany)
- Submit: POST a redeem_reward con talla seleccionada
- Solo aparece si reward.product.has_sizes == True
```

**Modal de Confirmación (para cupones/descuentos)**
```html
- ID: confirmModal-{reward.id}
- Contenido: pregunta confirmación "¿Canjear X puntos por Y?"
- Botones: Cancelar (dismiss), Confirmar (link a redeem_reward)
- Aparece para rewards sin tallas (COUPON, DISCOUNT)
```

#### Lógica de Visibilidad

```python
# Mostrar botón según condiciones:
if reward.reward_type == 'PRODUCT' and reward.product.has_sizes:
    # Mostrar Modal de Tallas
elif user_points >= reward.points_cost:
    # Mostrar Modal de Confirmación
else:
    # Botón "Puntos insuficientes" disabled
```

#### Datos Dinámicos del Servidor
```
- user_points: saldo de puntos del usuario
- rewards: QuerySet de reward objects con:
  * id, name, description
  * points_cost, reward_type (PRODUCT/COUPON/DISCOUNT)
  * available_quantity (None si ilimitado)
  * product (si reward_type == PRODUCT)
    - has_sizes (bool)
    - sizes (ManyToMany, cada uno con .label)
  * coupon (si reward_type == COUPON/DISCOUNT)
```

---

## 7. profile.html - Perfil de Usuario

### Descripción General
Panel de perfil completo con información de contacto, dirección, chequera de cupones e historial de pedidos con descarga de boletas.

### Archivos Asociados
- Ningún archivo JS externo (estructura estática)
- Redirecciona a edit_profile view para edición

### Estructura del Perfil

#### Encabezado
```html
- Avatar: inicial del nombre + apellido en círculo azul
- Nombre completo ({{ profile.user.get_full_name }})
- Username (@{{ profile.user.username }})
- Badge: puntos disponibles con ícono estrella
- Botón "Editar Perfil": link a edit_profile view
```

#### Información de Contacto
```html
- Email: con badge "Verificado" o "No Verificado"
  * Si no verificado: link "Reenviar correo"
- Teléfono: {{ profile.phone }}
```

#### Dirección de Envío
```html
- Dirección: {{ profile.address }}
- Comuna: {{ profile.commune }}
- Región: {{ profile.region }}
```

#### Mi Chequera (Wallet/Cupones)
```html
- Muestra lista de UserCoupon objects (wallet_coupons)
- Cada cupón es tarjeta con borde primario:
  * Código cupón ({{ uc.coupon.code }})
  * Descuento en grande ({{ uc.coupon.discount_percentage }}% OFF)
  * Fecha adquirido: {{ uc.acquired_at|date:"d/m/Y" }}
  * Fecha vencimiento: {{ uc.coupon.valid_to|date:"d/m/Y" }}
  
- Si vacío: muestra alerta "No tienes cupones disponibles"
```

#### Historial de Pedidos
```html
- Tabla responsive con filas: Código | Fecha | Total | Estado | Boleta
- Cada fila muestra:
  * Código: #{{ order.code }} (link visual en azul)
  * Fecha: {{ order.fecha|date:"d/m/Y" }}
  * Total: ${{ order.total }} (sin decimales)
  * Estado: badge con color:
    - Entregado: verde (bg-success)
    - Pendiente: amarillo (bg-warning)
    - Otros: gris (bg-secondary)
  * Boleta: botón "PDF" link a download_receipt

- Si vacío: muestra alerta con ícono bolsa vacía
```

#### Contexto del Servidor
```python
- profile: UserProfile object
  * user (FK a User)
  * phone, address, commune, region
  * points, is_verified
- orders: QuerySet de Order objects
  * code, fecha, total, estado
- wallet_coupons: QuerySet de UserCoupon objects
  * coupon (FK): code, discount_percentage, valid_to
  * acquired_at
```

---

## 8. buscar_productos.html - Búsqueda de Productos

### Descripción General
Página de búsqueda y filtrado de productos con formulario GET, grid responsivo y badges de stock/descuento.

### Archivos Asociados
- Ningún archivo JS externo (búsqueda server-side GET)
- Referencia a partials reutilizables:
  * `partials/buttons/action_button.html`
  * `partials/badges/stock_badge.html`
  * `partials/badges/discount_badge.html`

### Estructura de Búsqueda

#### Formulario de Filtros
```html
- Método: GET action="buscar_productos"
- Campos:
  1. q (text): término de búsqueda por nombre
  2. category (select): filtro por categoría
     * Opción vacía: "Todas las categorías"
     * Opciones: {% for cat in categories %} con slug como value
     * Preselecciona current_category si existe
  3. sort (select): ordenamiento
     * newest (default)
     * price_asc
     * price_desc
     * Preselecciona current_sort
  4. Botón submit: "Filtrar"
```

#### Grid de Productos
```html
- Responsive columns:
  * Móvil: 1 columna
  * Tablet pequeño: 2 columnas
  * Tablet: 3 columnas
  * Desktop: 4 columnas
- Gap: 4 (Bootstrap spacing)
```

#### Tarjeta de Producto

**Imagen y Badges**
```html
- Ratio 1x1 (square image, object-fit-cover)
- Badges en top-left:
  1. Stock Badge: importa desde partial (muestra si disponible/bajo)
  2. Discount Badge: importa desde partial (muestra % si tiene descuento)
- Overlay "Sin Stock": si producto.stock <= 0
  * Positioned: centro absoluto
  * Badge rojo con texto blanco
```

**Contenido**
```html
- Nombre: truncado a 1 línea con tooltip (title attribute)
- Categoría: gray text pequeño
- Precio:
  * Si tiene descuento:
    - Precio con descuento en rojo y bold
    - Precio original tachado en gris
  * Sin descuento:
    - Solo precio en azul bold
- Botón "Ver Detalles": link a producto_detalle
```

#### Estado Vacío
```html
- Si no hay productos:
  * Heading "No se encontraron productos"
  * Texto sugerencia
  * Botón "Limpiar filtros" link a buscar_productos (sin parámetros)
```

#### Contexto del Servidor
```python
- productos: QuerySet de Product objects (paginado/filtrado)
  * name, image_url, stock, category
  * detail (FK o relación): discount_percentage, discounted_price
- categories: QuerySet de categorías con slug, name
- query: string de búsqueda actual
- current_category: slug de categoría seleccionada
- current_sort: opción de ordenamiento actual
```

#### Flujo de Búsqueda
1. Usuario llena form (q, category, sort)
2. Submit GET a buscar_productos
3. Backend filtra queryset por q + category + order
4. Renderiza template con productos filtrados
5. Si usuario modifica filtros, repite desde paso 2

---

## 9. orders_list.html - Listado de Pedidos

### Descripción General
Página de administración de pedidos online con búsqueda, filtrado por fecha y modal detalle de pedidos cargado vía AJAX.

### Archivos Asociados
- Ningún archivo JS/CSS externo (todo inline en template)
- WebSocket listener desde base.html para actualizaciones en tiempo real

### Estructura Principal

#### Formulario de Búsqueda y Filtros
```html
- Búsqueda: por cliente, producto, código pedido o código de barras (formato P#-S#)
- Filtro por fecha: input type="date"
- Botones: Filtrar, Limpiar
```

#### Tabla de Pedidos
```html
- Cargada dinámicamente vía partial: 'partials/orders_rows.html'
- Contenedor: #orders-wrapper
- Soporta paginación AJAX con .ajax-link
```

#### Modal Detalle Pedido
```html
- ID: #orderDetailModal (Bootstrap fade modal)
- Contenido: cargado vía AJAX desde /orders/{orderId}/detail/
- Spinner durante carga: .spinner-border text-primary
```

#### Funciones JavaScript

**loadOrderDetail(orderId)**
- Fetch GET a `/orders/{orderId}/detail/`
- Muestra spinner mientras carga
- Rellena #order-detail-content con HTML respuesta
- Error: muestra mensaje en rojo

**Event Listeners**
- `newOrderDetected` (custom event desde WebSocket en base.html):
  * Obtiene filas actualizadas vía AJAX
  * POST a window.location.href con header 'X-Requested-With'
  * Actualiza #orders-wrapper con nuevo HTML
  
- Click en .ajax-link (paginación):
  * Previene default
  * Fetch GET a href del link
  * Actualiza #orders-wrapper
  * `history.pushState` para cambiar URL sin recargar

---

## 10. receipt_pdf.html - Boleta de Compra (PDF)

### Descripción General
Plantilla PDF de comprobante de pago generada en servidor con estilos impresos y estructura de boleta formal.

### Archivos Asociados
- Ninguno (es template standalone para generación PDF con weasyprint/similar)

### Estructura del PDF

#### Encabezado
```html
- Datos empresa: MultiTienda, dirección, contacto
- Número pedido: {{ order.code }}
- Fecha: {{ order.fecha|date:"d/m/Y" }}
- Título: "COMPROBANTE DE PAGO"
```

#### Columnas de Información
```html
- Izquierda: Datos del cliente
  * Nombre completo
  * Email
  * Teléfono
  
- Derecha: Método de entrega
  * Si Despacho: dirección, comuna, región
  * Si Retiro: "Retiro en Tienda"
```

#### Tabla de Productos
```html
- Columnas: Producto | Cant. | Precio | Total
- Producto: nombre + talla (si aplica)
- Cantidad: cantidad pedida
- Precio: precio unitario
- Total: subtotal por línea
```

#### Totales
```html
- Subtotal: si hay descuento, muestra subtotal original tachado
- Descuento: línea roja si discount_amount > 0
- Total a Pagar: destacado en azul (color primario)
```

#### Pie de Página
```html
- Agradecimiento: "¡Gracias por tu compra en MultiTienda!"
- Instrucciones: "Para dudas o consultas, contáctanos indicando tu número de pedido."
```

#### Estilos de Impresión
```css
- @page: letter size, 2cm margins
- Colores: azul (#0dcaf0) para títulos y bordes
- Tablas: bordes y padding consistentes
- Encabezados: fondo gris ligero (#f8f9fa)
```

#### Contexto del Servidor
```python
- order: Order object
  * code, fecha, total, discount_amount
  * cliente.name, contact_email, contact_phone
  * delivery_method, shipping_address, shipping_commune, shipping_region
  
- items: QuerySet de OrderItem objects
  * product.name, size, cantidad, price, subtotal
```

---

## 11. barcode_tool.html - Generador de Códigos de Barras

### Descripción General
Herramienta para gestionar cola de impresión de etiquetas con códigos de barras. Permite seleccionar productos/tallas y generar PDF con múltiples códigos.

### Archivos Asociados
- Ningún archivo JS/CSS externo (todo inline)
- Usa localStorage para persistencia de cola
- Genera PDF via /print_barcodes endpoint

### Estructura Principal

#### Columna Izquierda: Selección de Productos

**Búsqueda/Filtro**
```html
- Search: input text por nombre de producto
- Categoria: select con opciones dinámicas
- Botón Filtrar: GET a barcode_tool con parámetros
```

**Grilla de Productos**
```html
- Responsive: 2-6 columnas según tamaño
- Cada card:
  * Imagen: aspect-ratio 1:1, object-fit cover
  * Badge precio: top-right absoluto
  * Nombre: truncado
  * Categoría: small text
  * Botón Agregar:
    - Si tiene tallas: select dropdown + botón
    - Si no: botón directo "Agregar"
```

**Estado Vacío**
```html
- Ícono búsqueda grandes
- Texto: "No se encontraron productos"
- Sugerencia: "Intenta con otros términos de búsqueda"
```

#### Columna Derecha: Cola de Impresión (Sidebar)

**Encabezado**
```html
- Título: "Cola de Impresión"
- Badge: contador de items
```

**Cuerpo**
```html
- Estado vacío: ícono UPC, "La cola está vacía"
- Items dinámicos: inyectados vía JS
  * Cada item muestra:
    - Nombre producto/talla
    - Precio
    - Input cantidad con botones +/-
    - Botón eliminar X
```

**Pie de Página (Footer)**
```html
- Form POST a /print_barcodes con token CSRF
- Hidden inputs: qty_product_{id} o qty_size_{id}
- Botón "Imprimir Etiquetas": disabled si cola vacía
- Botón "Limpiar Todo": borra localStorage y UI
```

#### Estado y Persistencia (JavaScript)

**Estructura datos**
```javascript
queue = {
  "p_ProductID": {name, type: 'product', id, qty, price},
  "s_SizeID": {name, type: 'size', id, qty, price}
}
```

**Funciones principales**
- `addToQueue(productId, productName, hasSizes, price)`: 
  * Si tallas: crea key s_{sizeId} con label
  * Si no: crea key p_{productId}
  * Incrementa qty si existe, crea nuevo objeto si no
  * Guarda en localStorage
  
- `removeFromQueue(key)`: borra item y guarda

- `updateQty(key, delta)`: suma/resta cantidad

- `updateQtyInput(key, val)`: actualiza desde input numérico

- `clearQueue()`: vacía todo y localStorage

- `renderQueue()`: regenera UI desde estado
  * Crea divs para cada item
  * Genera hidden inputs para form
  * Actualiza badge contador
  * Habilita/deshabilita botón print

**LocalStorage**
- Key: 'barcodeQueue'
- Value: JSON stringified queue object
- Se carga al init (DOMContentLoaded)
- Se guarda después cada cambio

#### Flujo de Usuario
1. Busca/filtra productos en grilla
2. Selecciona producto o (talla + producto)
3. Click botón "Agregar" → addToQueue → renderQueue
4. Ajusta cantidad en sidebar (botones +/- o input)
5. Click "Imprimir" → POST form a /print_barcodes
6. Backend genera PDF con códigos de barras
7. Click "Limpiar" → vacía cola y localStorage

---

## 12. base.html - Plantilla Base del Proyecto

### Descripción General
Plantilla base (layout principal) de todo el proyecto que contiene navbar, footer, notificaciones en tiempo real vía WebSocket, gestión de modales Bootstrap y manejo de carrrito de compras.

### Funcionalidades Principales

#### Conexión WebSocket
```javascript
- Endpoint: /ws/orders/
- Protocolo: ws:// o wss:// según protocolo actual
- Mensajes escuchados: type='order_new'
- Acciones al recibir:
  * Actualiza badge contador de nuevos pedidos (#worker-orders-badge)
  * Muestra toast de notificación (#newOrderToast)
  * Dispara evento personalizado 'newOrderDetected' para que otras páginas escuchen
```

#### Gestión de Modales Bootstrap
```javascript
- Problema: z-index duplicados en modales con zoom/dispositivos móviles
- Solución:
  1. cleanupBackdrops(): elimina backdrops duplicados
  2. adjustBackdrop(): ajusta posición y tamaño del backdrop único
  3. Eventos capturados: show.bs.modal, shown.bs.modal, hide.bs.modal
  4. Diferencia entre modales Bootstrap (.fade) y custom
```

#### Carrito de Compras (AJAX)
```javascript
- Evento: click en .add-to-cart-btn
- Flujo:
  1. Obtiene URL del botón
  2. Agrega parámetro ajax=1
  3. Fetch GET con header 'X-Requested-With': 'XMLHttpRequest'
  4. Si respuesta redirige: window.location.href
  5. Si JSON ok: actualiza badge, muestra toast
  6. Error: fallback a navegación normal
```

#### Toasts (Notificaciones)
```html
- #newOrderToast: desde WebSocket
- .message-toast: mensajes Django (delay 5s auto-hide)
- Todos usan Bootstrap.Toast()
```

#### Componentes Globales
```html
- Navbar (extends navbar_right.html)
- Main content ({% block content %})
- Footer
- Toast Container (bottom-right)
- Worker Notification Toast (WebSocket)
- Modals ({% block modals %})
- Scripts: Bootstrap 5 bundle + custom JS
```

---

## 13. dashboardtrabajador.html - Dashboard de Trabajador

### Descripción General
Dashboard analytics para trabajadores con KPIs y gráficos de ventas usando Highcharts.

### Estructura

#### KPIs (Siempre visibles)
```html
- Tarjetas de estadísticas: Pedidos, Ingresos, Ticket Promedio, etc
- Filtros por período (mes/año)
```

#### Filtros de Período
```html
- Input month para período específico
- Apply/Reset buttons
- Variables CSS: .period-input (ancho fijo 240px)
```

#### Tabs de Contenido

**Pestaña Ventas**
```html
- Row 1: Gráfico líneas (ordersLineChart) + Treemap (salesTreemapChart)
- Ambos con height: 400px
- Chart wrapper responsivos
```

#### Scripts
```html
- Highcharts JS bundle
- Módulos: variable-pie, treemap, exporting, export-data, accessibility
- dashboardtrabajador.js (JS file)
```

---

## 14. dashboardadmin.html - Dashboard Administrativo

### Descripción General
Dashboard completo para administradores con análisis de ventas, mapa regional de Chile y comportamiento de clientes.

### Estructura de Pestañas

**Pestaña Ventas**
```html
- Row 1: Gráfico líneas + Treemap distribución
- Misma estructura que dashboardtrabajador
```

**Pestaña Análisis Regional**
```html
- Columna izquierda: Mapa interactivo de Chile (#chileMap)
  * Highcharts Map API
  * Coloreado por cantidad de pedidos
  * Hover muestra tooltip con datos regionales
  
- Columna derecha: Tabla detalle (#regionSalesTable)
  * Región | Ventas (sorted por cantidad)
  * Población dinámica vía JS
```

**Pestaña Comportamiento de Cliente**
```html
- Fila 1: Retención/Adquisición (retentionChart)
- Fila 2: Frecuencia + Ticket (frequencyChart + ticketChart)
- Fila 3: Top 10 Clientes + Día de Semana (topCustomersChart + dayOfWeekChart)
```

#### Lógica del Mapa Regional (JavaScript)

```javascript
- regionKeyMap: mapea ID región (1-16) a key Highcharts (cl-ta, cl-an, etc)
- Promise.all():
  1. Carga chile-regiones-2025.json (metadata)
  2. Carga GeoJSON de Highcharts (mapdata)
  3. Carga datos de venta: /regional_analysis_api
  
- forEach región:
  * Busca datos de ventas por nombre
  * Crea objeto con hcKey, value (orders para color), sales, topCategory, etc
  
- Highcharts.mapChart('chileMap'):
  * Series: bubble map con data
  * ColorAxis: min=0, basado en cantidad de órdenes
  * Tooltip: fondo oscuro, muestra región, pedidos, ventas, ticket promedio
```

#### Tabla Regional
```javascript
- Iteración sobre datos
- Crea rows dinámicamente
- Columns: Región (+ Top Category) | Ventas
```

---

## 15. iniciosesionadmin.html - Login Administrador

### Descripción General
Página de inicio de sesión para admin/trabajadores (heredada, similar a login.html pero puede tener otros estilos).

### Estructura
```html
- Si authenticated: muestra "Ya estás conectado"
- Si no: formulario login (form method=post)
- CSRF token incluido
```

---

## 16. pos.html - Terminal Punto de Venta

### Descripción General
Terminal de punto de venta (POS) para transacciones en caja rápida. Permite búsqueda de productos, cantidad y cobro inmediato sin carrito persistente.

### Archivos Asociados
- `base.html` - Hereda estructura y notificaciones WebSocket
- CSS inline + Bootstrap 5
- Script inline para lógica POS

### Funcionalidad Principal

#### Estructura de Interfaz
```html
- Header: Título, usuario actual
- Contenedor principal:
  * Searchbar para productos
  * Grilla de productos rápidos/recientes
  * Carrito flotante/modal (items actuales)
  * Panel de pago
```

#### Búsqueda y Adición de Productos
```javascript
- Input con evento input/change
- Fetch AJAX a endpoint de búsqueda de productos
- Resultados muestran producto con imagen, nombre, precio
- Click en producto: agrega a carrito
- Validación: verifica stock disponible
```

#### Carrito Temporal
```javascript
- Estructura: { productId: {name, price, qty, total} }
- No persiste en localStorage, solo en sesión memoria
- Actualización en tiempo real de total y cantidad de items
- Botón remover para cada item
```

#### Toasts de Notificación
```javascript
- Inicializa solo toasts de mensajes (no de órdenes WebSocket)
- Mensajes: "Producto agregado", "Stock insuficiente", "Producto removido"
- CSS: oculta notificaciones duplicadas de base.html (que aparecen abajo-derecha)
- Position: top-right local a POS
```

#### Transacción y Pago
```javascript
- Selecciona método pago: Webpay, Efectivo, Tarjeta
- Si Webpay: redirige a proceso de pago
- Si Efectivo/Tarjeta: genera boleta y completa transacción
- Confirmación y reset del carrito
```

### Funciones Clave
- `searchProduct(query)`: Fetch asincrónico a búsqueda, popula resultados
- `addToCart(productId)`: Agrega o incrementa qty del carrito
- `removeFromCart(itemId)`: Elimina item del carrito
- `updateTotal()`: Recalcula suma de subtotales
- `initializeToasts()`: Solo carga toasts de mensajes (no de órdenes)

### Patrones Especiales
- **Oculta Notificaciones Duplicadas**: CSS `display: none` para toasts de órdenes que vienen de base.html
- **Sin Persistencia**: A diferencia de cart.html, no guarda estado entre sesiones
- **Validación de Stock**: Chequea disponibilidad antes de agregar

---

## 17. marketing_dashboard.html - Dashboard de Marketing

### Descripción General
Dashboard administrativo para gestión de campañas de marketing, ofertas, cupones y productos de recompensa. Interfaz compleja con múltiples secciones de filtrado y gestión.

### Archivos Asociados
- `base.html` - Hereda estructura y notificaciones
- CSS Bootstrap 5 + inline personalizado
- `marketing_dashboard.js` (si está separado) o script inline extenso

### Funcionalidad Principal

#### Secciones Principales (Tabs)
```html
1. Campañas - Listado y creación de campañas
2. Ofertas - Gestión de ofertas por producto
3. Cupones - Creación y distribución de códigos
4. Productos Recompensa - Catálogo de recompensas por puntos
```

#### Control de Validación de Stock
```javascript
- Buttons globales: "Habilita validación de stock" / "Deshabilita validación de stock"
- Afecta a todos los productos en el formulario
- Toggle: stockValidationEnabled boolean
- Si habilitado: previene agregar productos sin stock
- Si deshabilitado: permite agregar productos incluso sin disponibilidad
```

#### Gestión de Productos de Recompensa
```javascript
- Grilla de productos filtrable:
  * Por término de búsqueda (search input)
  * Por categoría (chips de categorías)
  * Por tipo (product vs coupon)

- Lógica de filtrado para productos de recompensa:
  * Si searchTerm: incluye solo si nombre coincide (case-insensitive)
  * Si categoryFilter: incluye solo si pertenece a categoría
  * Si typeFilter: incluye si es producto o cupón según selección

- Renderiza cards de productos:
  * Imagen, nombre, puntos necesarios
  * Badge de estado: "Activo", "Inactivo", "Sin stock"
  * Si product está deshabilitado (tiene oferta activa): muestra badge "Ya tiene oferta"
  * Click en card: togglea selección (Set con IDs)
  * Estilo visual: border + background cuando seleccionado
```

#### Sistema de Selección Persistente
```javascript
- selectedIds: Set que mantiene IDs de productos seleccionados
- Sincronización con widget de formulario Django oculto:
  * Hidden input: name="selected_products" (MultipleChoiceField)
  * Antes de submit: convierte selectedIds a array, asigna a hidden input
  * Backend recibe lista de IDs en POST

- Funciones:
  * toggleProductSelection(id): agrega/quita de Set
  * updateHiddenField(): sincroniza Set -> hidden input
  * renderGrid(): recrea cards basado en filtros y selectedIds
```

#### Gestión de Cupones
```javascript
- Sección de cupón (separada o en modal):
  * Input: código
  * Input: descuento (%)
  * Input: cantidad disponible
  * Botón: "Agregar cupón a campaña"

- Evento: reinicia sección de cupón después de agregar
```

#### Cargas y Estados UI
```javascript
- Estado "cargando": muestra spinner/loader
- Deshabilita botones durante operación
- Habilita nuevamente al completar
- Manejo de errores: toast de error si falla fetch
```

#### Event Listeners
```javascript
- Search input: refiltra grid en tiempo real
- Category chips: togglean filtro, retrigger render
- Product cards: click para seleccionar/deseleccionar
- Tipo select: cambia entre productos y cupones
- Form submit: valida selección, sincroniza hidden input, envía POST
```

#### Inicialización
```javascript
- Al cargar documento:
  * Inicializa selectedIds desde estado previo del formulario
  * Si formulario tiene datos guardados: restaura selección
  * Renderiza grid inicial
```

### Funciones Clave
- `renderGrid()`: Genera cards basado en filtros actuales y selectedIds
- `toggleProductSelection(id)`: Agrega/quita producto de Set
- `updateHiddenField()`: Sincroniza selectedIds con hidden Django form widget
- `applyFilters()`: Aplica search, category, type filters
- `handleProductCardClick(id)`: Click handler para cards (delegated)
- `resetCouponSection()`: Limpia campos de cupón tras agregar

### Patrones Especiales
- **Sincronización Formulario Django**: selectedIds (JS Set) ↔ hidden input (Django MultipleChoiceField)
- **Delegación de Eventos**: Click handler padre en grid, busca target más cercano con [data-product-id]
- **Estilo Visual de Selección**: Border + background (#e3f2fd o similar) cuando seleccionado
- **Persistencia entre Tab Switches**: selectedIds persiste aunque cambies de tab

---

## 18. print_barcodes.html - Generador de Etiquetas de Códigos de Barras

### Descripción General
Generador de vista previa e impresión de etiquetas de códigos de barras para productos. Optimizado para impresoras térmicas estándar (60x40mm).

### Archivos Asociados
- `jsbarcode.js` - Librería CDN para generar códigos de barras CODE128
- CSS print optimizado para A4
- Script inline para inicialización

### Funcionalidad Principal

#### Variables CSS (Dimensiones)
```css
--label-width: 60mm;     /* Ancho estándar */
--label-height: 40mm;    /* Alto estándar */
--label-gap: 4mm;        /* Espacio entre etiquetas */
```

#### Layout de Pantalla (Screen)
```html
- Contenedor .controls:
  * Título "Vista Previa de Impresión"
  * Instrucciones: cantidad de etiquetas, configuración recomendada A4 100%
  * Botones: Imprimir, Cerrar

- Contenedor #sheet:
  * Simula hoja A4 (210mm × 297mm)
  * Cuadrilla de etiquetas 3 columnas × N filas
  * Espaciado: 4mm entre items
  * Box-shadow para visualización en pantalla
```

#### Estructura de Etiqueta Individual
```html
<div class="label">
  <div class="label-content">
    <div class="product-name">Nombre del Producto</div>
    <div class="product-meta">Código (SKU)</div>
    <svg class="barcode" data-code="XXXXX"></svg>
    <div class="product-price">$9.990</div>
  </div>
</div>
```

#### Renderizado de Códigos de Barras
```javascript
- JsBarcode (librería CDN)
- Iteración sobre todos los SVG.barcode
- Configuración:
  * format: CODE128 (estándar retail)
  * width: 1.8 (grosor de barras)
  * height: 40 (altura en pixels)
  * displayValue: false (no muestra número debajo)
  * margin: 0 (sin márgenes)
  * background: transparent (fondo transparente)

- Error handling: try/catch por código, logs en consola
```

#### Estilos de Impresión (@media print)
```css
- Body: sin background, márgenes 0
- .controls: oculto (display: none)
- #sheet:
  * Ancho 100% (ajusta a página)
  * Sin box-shadow
  * Padding 5mm (respeta márgenes de impresora)
  * page-break-after: always (nueva página si hay más etiquetas)

- .label:
  * Border: 1px dashed (guía de corte)
  * break-inside: avoid (no parte etiqueta entre páginas)
  * Tamaño exacto: 60×40mm

- Cuadrilla de impresión: 3 columnas × N filas
  * gap: 5mm (espacio cortable entre etiquetas)
```

#### Flujo de Uso
```
1. Backend genera items = [{"name": "...", "code": "...", "price": "..."}]
2. Template renderiza {% for item in items %}
3. JavaScript (DOMContentLoaded):
   - Genera códigos de barras con JsBarcode
4. Usuario click "Imprimir Etiquetas"
5. Navegador abre print dialog con media print styles
6. Impresora: A4, escala 100%, márgenes mínimos
7. Resultado: 3 columnas × N filas de etiquetas 60×40mm
```

### Funciones Clave
- `document.addEventListener('DOMContentLoaded', ...)`: Inicializa todos los códigos
- `JsBarcode(svg, code, config)`: Genera barcode en SVG

### Patrones Especiales
- **Print Styles Optimizados**: Media queries separan layout pantalla vs impresión
- **Guía de Corte Dashed**: Border dashed en impresión indica líneas de corte
- **Responsive Units**: mm para impresión, coordina con A4
- **Fallback de Error**: try/catch mantiene proceso incluso si un código falla
- **Sin JavaScript de Lógica**: Solo renderizado, nada dinámico (datos vienen del backend)

### Notas de Configuración
- Impresora recomendada: térmica de rollo (58-80mm) o láser A4
- Escala: siempre 100% (importante para conservar tamaños)
- Márgenes: 0mm si es impresora térmica, 5mm si es A4
- Datos: backend proporciona items via Django template context

---

## 19. producto_detalle.html - Página de Detalle de Producto

### Descripción General
Página de visualización detallada de un producto individual. Muestra imagen, especificaciones, precio, opiniones, productos relacionados y permite agregar al carrito o recompensas.

### Archivos Asociados
- `basecliente.html` - Hereda estructura y navegación
- `CSS base + inline` - Estilos receptivos
- `partials/add_to_cart_button.html` - Botón reutilizable de carrito

### Funcionalidad Principal

#### Estructura de Página
```html
- Breadcrumb: Inicio > Categoría > Producto
- Container principal: 2 columnas (desktop), 1 (mobile)
  * Columna izquierda: Imagen del producto
  * Columna derecha: Detalles del producto
```

#### Sección de Imagen
```html
- Background blanco con esquinas redondeadas
- Imagen responsive (img-fluid, object-fit-cover)
- Galería dinámicamente si hay múltiples imágenes (opcional)
```

#### Sección de Detalles
```html
- Encabezado: Nombre + ID de admin (si es staff/admin)
  * Botón "Editar" (solo admin/staff)
  * Badge de ID de producto
  
- Calificación: Stars (si existe sistema de reviews)
- Stock: Badge de disponibilidad
- Precio: Grande y destacado
- Descuento: Si aplica, muestra porcentaje y precio original tachado

- Selector de atributos (si aplica):
  * Color: Radio buttons o select
  * Talla: Select dinámico (cascada)
  * Cantidad: Input numérico con validación

- Botones de acción:
  * "Agregar al carrito"
  * "Agregar a favoritos" (corazón)
  * "Compartir" (social)

- Descripción: Texto largo con formateo
- Especificaciones: Tabla con detalles técnicos
```

#### Información Adicional
```html
- Envío y devoluciones: Iconos + información
- Política de retorno: Link a página de políticas
- Productos relacionados: Carrusel horizontal
- Reviews/Opiniones: Sistema de valoración
```

### Patrones Especiales
- **Herencia de Template**: Extiende `basecliente.html` (estructura compartida)
- **Breadcrumb Dinámico**: Se genera desde context variable `d.breadcrumbs`
- **Roles de Usuario**: Solo muestra opciones de edición si `user.is_staff or user.is_superuser`
- **No persiste CSS antiguo**: Comentario indica que se removieron links CSS heredados

### Data Context Esperado
```python
{
  'p': ProductObject,           # Objeto del producto
  'd': {
    'breadcrumbs': ['Categoría', 'Subcategoría', ...],
    'related_products': [...]    # Productos relacionados
  }
}
```

---

## 20. Archivos Parciales de Componentes Reutilizables

### partials/product_card.html
Componente de tarjeta de producto usado en múltiples páginas (catálogo, búsqueda, carrusel).

**Estructura**:
- Imagen con badges (descuento, stock)
- Nombre del producto truncado
- Precio + precio original (si hay descuento)
- Botón "Ver detalles" o añadir al carrito

**Insignias**:
- Descuento %: Badge rojo
- Stock bajo: Badge amarillo
- Nuevo: Badge azul

### partials/product_list.html
Contenedor de una lista de productos con paginación.

**Secciones**:
- Grilla responsive (3-4 columnas desktop, 1-2 mobile)
- Paginación AJAX al final
- Mensaje "Sin productos" si está vacío

### partials/orders_rows.html
Filas de tabla de órdenes para el historial de pedidos.

**Columnas**:
- Número de orden
- Fecha
- Estado
- Total
- Acciones (Ver detalle, descargar boleta)

### partials/buttons/add_to_cart_button.html
Botón reutilizable para agregar al carrito con modal de atributos si es necesario.

**Comportamiento**:
- Si producto tiene tallas/colores: abre modal de selección
- Si no: agrega directamente
- Valida stock antes de agregar

### partials/badges/
Componentes de insignias para estado de producto:
- `stock_badge.html`: Muestra disponibilidad
- `discount_badge.html`: Muestra descuento %

---

## Patrones Generales

### AJAX Forms
Múltiples formularios usan fetch con CSRF token:
```javascript
const csrftoken = document.cookie.split('; ')
  .find(r => r.startsWith('csrftoken='))?.split('=')[1];

fetch(url, {
  method: 'POST',
  headers: { 'X-CSRFToken': csrftoken || '' },
  body: formData
})
```

### Event Delegation
Se usa querySelector + closest para capturar eventos en elementos dinámicos:
```javascript
document.addEventListener('click', (e) => {
  const button = e.target.closest('[data-action]');
  if (button) { /* procesar */ }
});
```

### Modal Manejo Bootstrap
```javascript
const modal = new bootstrap.Modal(element);
modal.show();
modal.hide();
bootstrap.Modal.getInstance(element).hide();
```

---

## Notas de Desarrollo

- **LocalStorage**: No se usa persistencia local, todo es servidor (Django)
- **Estado**: Mantenido en variables globales (PRODUCTS, currentCategory, currentSort, searchQuery)
- **Actualizaciones**: Siempre se actualiza PRODUCTS[] localmente antes de rerenderizar
- **Validaciones**: Cliente (HTML5 required, JS custom) + Server
- **Seguridad**: CSRF token en todos los POST, atributos required en inputs
