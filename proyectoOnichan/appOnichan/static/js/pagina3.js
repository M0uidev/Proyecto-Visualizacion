document.addEventListener('DOMContentLoaded', () => {
  const dataElement = document.getElementById('stock-data');
  if (!dataElement) {
    return;
  }

  let dataset;
  try {
    dataset = JSON.parse(dataElement.textContent || '{}');
  } catch (error) {
    console.error('No se pudo parsear la información de stock.', error);
    dataset = {};
  }

  const orders = dataset.orders || [];
  const stats = dataset.estadisticas || {};

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));
  const peso = (value) => value.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });

  const PRODUCTS = [];
  const seenProducts = new Set();

  orders.forEach((order) => {
    order.productos.forEach((product) => {
      const key = product.nombre;
      if (seenProducts.has(key)) {
        return;
      }

      seenProducts.add(key);
      const units = order.productos.reduce((acc, current) => acc + current.cantidad, 0);
      const price = units ? order.total / units : 0;

      PRODUCTS.push({
        code: key.toLowerCase().replace(/\s+/g, '-'),
        name: product.nombre,
        price: Math.round(price),
        category: product.nombre.includes('Polera') || product.nombre.includes('Pantalón') || product.nombre.includes('Chaqueta') || product.nombre.includes('Polerón')
          ? 'Ropa'
          : product.nombre.includes('Zapatillas') || product.nombre.includes('Botines')
            ? 'Calzado'
            : 'Accesorios',
        stock: Math.floor(Math.random() * 100),
        status: 'Disponible',
      });
    });
  });

  const CATEGORIES = [...new Set(PRODUCTS.map((product) => product.category))];

  let currentCategory = 'all';
  let currentSort = { field: 'name', direction: 'asc' };
  let searchQuery = '';

  let modalChartInstance = null;

  function getStatusClass(status) {
    return {
      Disponible: 'success',
      'Stock Bajo': 'warning',
      'Sin Stock': 'danger',
    }[status] || 'secondary';
  }

  function updateStockStatus(product) {
    if (product.stock <= 0) {
      return 'Sin Stock';
    }
    if (product.stock <= 10) {
      return 'Stock Bajo';
    }
    return 'Disponible';
  }

  function filterProducts(products) {
    return products.filter((product) => {
      if (currentCategory !== 'all') {
        if (currentCategory === 'stock:bajo' && product.stock > 10) {
          return false;
        }
        if (currentCategory.startsWith('category:')) {
          const [, category] = currentCategory.split(':');
          if (product.category !== category) {
            return false;
          }
        }
      }

      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          product.name.toLowerCase().includes(query)
          || product.code.toLowerCase().includes(query)
          || product.category.toLowerCase().includes(query)
        );
      }

      return true;
    });
  }

  function updateChart() {
    const chartCanvas = $('#stockByCategory');
    if (!chartCanvas) {
      return;
    }

    const ctx = chartCanvas.getContext('2d');
    const productsByCategory = CATEGORIES.map((category) => ({
      category,
      count: PRODUCTS.filter((product) => product.category === category).length,
      totalStock: PRODUCTS.filter((product) => product.category === category).reduce((sum, product) => sum + product.stock, 0),
    }));

    if (window.stockChart) {
      window.stockChart.destroy();
    }

    const colorPalette = ['#4f46e5', '#22c55e', '#f97316', '#0ea5e9', '#ec4899', '#f59e0b', '#8b5cf6'];

    window.stockChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: productsByCategory.map((item) => item.category),
        datasets: [
          {
            data: productsByCategory.map((item) => item.totalStock),
            backgroundColor: productsByCategory.map((_, index) => colorPalette[index % colorPalette.length]),
            borderWidth: 0,
            hoverOffset: 10,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            top: 20,
            bottom: 20,
          },
        },
        plugins: {
          legend: {
            position: 'right',
            labels: {
              font: { size: 14 },
              padding: 20,
              usePointStyle: true,
              boxWidth: 10,
              boxHeight: 10,
            },
          },
          tooltip: {
            titleFont: { size: 16 },
            bodyFont: { size: 14 },
            padding: 12,
            callbacks: {
              label: (context) => {
                const totalItems = context.dataset.data[context.dataIndex];
                const totalProducts = PRODUCTS.filter((product) => product.category === context.label).length;
                return [
                  `Stock Total: ${totalItems} unidades`,
                  `${totalProducts} productos diferentes`,
                ];
              },
            },
          },
        },
        onClick: (event, elements) => {
          if (!elements.length) {
            return;
          }

          const index = elements[0].index;
          const category = productsByCategory[index].category;
          const productsInCategory = PRODUCTS.filter((product) => product.category === category).sort((a, b) => b.stock - a.stock);

          const sales = {};
          orders.forEach((order) => {
            order.productos.forEach((product) => {
              if (productsInCategory.find((item) => item.name === product.nombre)) {
                sales[product.nombre] = (sales[product.nombre] || 0) + product.cantidad;
              }
            });
          });

          if (modalChartInstance) {
            modalChartInstance.destroy();
          }

          const modalCanvas = document.getElementById('modalChart');
          const modal = document.getElementById('chartModal');
          const modalTitle = modal.querySelector('.modal-title');
          modalTitle.textContent = `Detalle de ${category}`;

          modalChartInstance = new Chart(modalCanvas.getContext('2d'), {
            type: 'bar',
            data: {
              labels: productsInCategory.map((product) => product.name),
              datasets: [
                {
                  label: 'Stock',
                  data: productsInCategory.map((product) => product.stock),
                  backgroundColor: `${colorPalette[index % colorPalette.length]}80`,
                  borderWidth: 1,
                  order: 2,
                },
                {
                  label: 'Ventas',
                  data: productsInCategory.map((product) => sales[product.name] || 0),
                  backgroundColor: `${colorPalette[(index + 1) % colorPalette.length]}80`,
                  borderWidth: 1,
                  order: 1,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              indexAxis: 'y',
              plugins: {
                title: {
                  display: true,
                  text: 'Stock y Ventas por Producto',
                  font: {
                    size: 20,
                    weight: 'bold',
                  },
                  padding: 20,
                },
                legend: {
                  display: true,
                  position: 'top',
                  labels: {
                    font: { size: 16 },
                    usePointStyle: true,
                    padding: 20,
                  },
                },
                tooltip: {
                  titleFont: { size: 16 },
                  bodyFont: { size: 15 },
                  padding: 12,
                  callbacks: {
                    label: (context) => {
                      const product = productsInCategory[context.dataIndex];
                      if (context.dataset.label === 'Stock') {
                        return `Stock: ${product.stock} unidades · Precio: ${peso(product.price)}`;
                      }
                      return `Ventas: ${sales[product.name] || 0} unidades`;
                    },
                  },
                },
              },
              scales: {
                x: {
                  stacked: false,
                  grid: {
                    display: false,
                  },
                  ticks: {
                    font: { size: 14 },
                    callback: (value) => `${value} unidades`,
                  },
                  title: {
                    display: true,
                    text: 'Cantidad',
                    font: {
                      size: 16,
                      weight: 'bold',
                    },
                    padding: { top: 20, bottom: 10 },
                  },
                },
                y: {
                  stacked: false,
                  grid: {
                    display: true,
                    drawBorder: false,
                  },
                  ticks: {
                    font: { size: 15 },
                    padding: 10,
                  },
                  title: {
                    display: true,
                    text: 'Productos',
                    font: {
                      size: 16,
                      weight: 'bold',
                    },
                    padding: { top: 20, bottom: 10 },
                  },
                },
              },
            },
          });

          const bootstrapModal = new bootstrap.Modal(modal);
          modal.addEventListener('shown.bs.modal', () => {
            modalCanvas.style.height = '400px';
            modalChartInstance.resize();
          }, { once: true });
          bootstrapModal.show();
        },
      },
    });
  }

  function renderTable() {
    const tbody = $('#stockTable tbody');
    if (!tbody) {
      return;
    }

    const filtered = filterProducts(PRODUCTS);
    const sorted = [...filtered].sort((a, b) => {
      const factor = currentSort.direction === 'asc' ? 1 : -1;
      return a[currentSort.field] > b[currentSort.field] ? factor : -factor;
    });

    tbody.innerHTML = sorted.map((product) => {
      const statusText = product.status;
      const statusClass = getStatusClass(statusText);

      const actions = [
        `<button class="btn btn-sm btn-outline-primary" data-action="edit" data-id="${product.code}">
              <i class="bi bi-pencil"></i>
            </button>`
      ];
      if (window.IS_ADMIN) {
        actions.push(`
            <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${product.code}">
              <i class="bi bi-trash"></i>
            </button>`);
      }

      return (
      `<tr>
        <td>${product.code}</td>
        <td>${product.name}</td>
        <td>${product.category}</td>
        <td>${product.stock}</td>
        <td>${peso(product.price)}</td>
        <td><span class="badge bg-${statusClass}">${statusText}</span></td>
        <td>
          <div class="btn-group">
            ${actions.join('')}
          </div>
        </td>
      </tr>`
      );
    }).join('');

    const statsElement = document.getElementById('tableStats');
    if (statsElement) {
      statsElement.textContent = `${filtered.length} productos`;
    }

    updateChart();
  }

  document.getElementById('chartModal')?.addEventListener('hidden.bs.modal', () => {
    if (modalChartInstance) {
      modalChartInstance.destroy();
      modalChartInstance = null;
    }
  });

  $$('.chip').forEach((button) => {
    button.addEventListener('click', (event) => {
      $$('.chip').forEach((chip) => chip.classList.remove('active'));
      event.currentTarget.classList.add('active');
      currentCategory = event.currentTarget.dataset.filter;
      renderTable();
    });
  });

  $('#btnRefresh')?.addEventListener('click', () => window.location.reload());
  $('#btnAdd')?.addEventListener('click', () => {
    alert('Funcionalidad de agregar producto pendiente');
  });

  $('#stockTable')?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (!button) {
      return;
    }

    const action = button.dataset.action;
    const productId = button.dataset.id;

    if (action === 'edit') {
      const product = PRODUCTS.find(p => p.code === productId);
      if (!product) return;
      const newVal = prompt(`Nueva cantidad para ${product.name}`, String(product.stock));
      if (newVal === null) return;
      const parsed = parseInt(newVal, 10);
      if (!Number.isFinite(parsed) || parsed < 0) {
        alert('Cantidad inválida');
        return;
      }
      product.stock = parsed;
      product.status = updateStockStatus(product);
      renderTable();
    } else if (action === 'delete') {
      if (!window.IS_ADMIN) return;
      const idx = PRODUCTS.findIndex(p => p.code === productId);
      if (idx >= 0) {
        PRODUCTS.splice(idx, 1);
        renderTable();
      }
    }
  });

  renderTable();
});
