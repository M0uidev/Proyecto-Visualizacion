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

  const productsPayload = dataset.products || [];
  const adminMeta = document.getElementById('stock-meta');
  window.IS_ADMIN = adminMeta ? adminMeta.getAttribute('data-admin') === 'true' : false;

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));
  const peso = (value) => value.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });

  const PRODUCTS = productsPayload.map(p => {
    const prod = {
      code: String(p.code),
      name: p.name,
      price: p.price,
      category: p.category || 'Otros',
      stock: p.stock || 0,
      image_url: p.image_url || '',
      description: p.description || '',
      status: 'Disponible',
      sizes: p.sizes || [],
      has_sizes: p.has_sizes || false
    };
    prod.status = updateStockStatus(prod);
    return prod;
  });

  const CATEGORIES = [...new Set(PRODUCTS.map((product) => product.category))];

  let currentCategory = 'all';
  let currentSort = 'name_asc';
  let searchQuery = '';

  // Populate Category Filter
  const categorySelect = document.getElementById('categoryFilter');
  if (categorySelect) {
      // Clear existing options except "all"
      categorySelect.innerHTML = '<option value="all">Todas las Categorías</option>';
      CATEGORIES.forEach(cat => {
          const option = document.createElement('option');
          option.value = cat;
          option.textContent = cat;
          categorySelect.appendChild(option);
      });
      
      categorySelect.addEventListener('change', (e) => {
          currentCategory = e.target.value;
          renderGrid();
      });
  }

  const sortSelect = document.getElementById('sortFilter');
  if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
          currentSort = e.target.value;
          renderGrid();
      });
  }
  
  const searchInput = document.getElementById('productSearch');
  if (searchInput) {
      searchInput.addEventListener('input', (e) => {
          searchQuery = e.target.value;
          renderGrid();
      });
  }

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
      // Category Filter
      if (currentCategory !== 'all') {
          if (product.category !== currentCategory) return false;
      }

      // Search Filter
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

          const sales = {}; // opcional: sin dataset de ventas aquí

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

  function renderGrid() {
    const gridContainer = document.getElementById('productsGrid');
    const emptyState = document.getElementById('emptyState');
    if (!gridContainer) return;

    gridContainer.innerHTML = '';
    
    const filtered = filterProducts(PRODUCTS);
    
    if (filtered.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        return;
    }
    if (emptyState) emptyState.style.display = 'none';

    // Sort logic
    const sorted = [...filtered].sort((a, b) => {
        switch(currentSort) {
            case 'stock_desc':
                return b.stock - a.stock;
            case 'stock_asc':
                return a.stock - b.stock;
            case 'recent':
                return parseInt(b.code) - parseInt(a.code);
            case 'name_asc':
            default:
                return a.name.localeCompare(b.name);
        }
    });

    sorted.forEach(product => {
        const statusText = product.status;
        const statusClass = getStatusClass(statusText);
        
        const card = document.createElement('div');
        card.className = 'card product-card shadow-sm';
        card.style.width = '220px';
        card.style.transition = 'transform 0.2s';
        
        // Hover effect
        card.onmouseenter = () => card.style.transform = 'translateY(-5px)';
        card.onmouseleave = () => card.style.transform = 'none';

        let actionsHtml = '';
        actionsHtml += `<button class="btn btn-sm btn-outline-primary me-1" data-action="edit" data-id="${product.code}" title="Editar"><i class="bi bi-pencil"></i></button>`;
        
        if (window.IS_ADMIN) {
            actionsHtml += `<button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${product.code}" title="Eliminar"><i class="bi bi-trash"></i></button>`;
        }

        card.innerHTML = `
            <div class="position-relative">
                <img src="${product.image_url}" class="card-img-top" alt="${product.name}" style="height: 150px; object-fit: cover;">
                <span class="position-absolute top-0 end-0 badge bg-${statusClass} m-2">${statusText}</span>
            </div>
            <div class="card-body p-3">
                <h6 class="card-title text-truncate mb-1" title="${product.name}">${product.name}</h6>
                <p class="card-text small text-muted mb-1">ID: ${product.code}</p>
                <p class="card-text small text-muted mb-2">${product.category}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="fw-bold text-primary">${peso(product.price)}</span>
                    <small class="text-muted">Stock: ${product.stock}</small>
                </div>
                <div class="mt-3 d-flex justify-content-end">
                    ${actionsHtml}
                </div>
            </div>
        `;
        
        gridContainer.appendChild(card);
    });

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

  $('#btnRefresh')?.addEventListener('click', () => window.location.reload());
  // btnAdd abre modal via data-bs-toggle (no JS extra)

  $('#productsGrid')?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (!button) {
      return;
    }

    const action = button.dataset.action;
    const productId = button.dataset.id;

    if (action === 'edit') {
      const product = PRODUCTS.find(p => p.code === productId);
      if (!product) return;
      
      if (window.IS_ADMIN) {
          // Populate Modal
          document.getElementById('editProductId').value = product.code;
          document.getElementById('editName').value = product.name;
          document.getElementById('editPrice').value = product.price;
          document.getElementById('editImageUrl').value = product.image_url;
          document.getElementById('editCategory').value = product.category;
          document.getElementById('editDescription').value = product.description;
          document.getElementById('editStock').value = product.stock;
          document.getElementById('editSizes').value = product.sizes.join(', ');
          
          // Show Modal
          const editModal = new bootstrap.Modal(document.getElementById('editProductModal'));
          editModal.show();
      } else {
          // Populate Worker Modal (Adjust Stock)
          document.getElementById('adjustStockId').value = product.code;
          document.getElementById('adjustStockName').textContent = product.name;
          document.getElementById('displayCurrentStock').textContent = product.stock;
          document.getElementById('currentStockValue').value = product.stock;
          document.getElementById('stockAdjustment').value = 0;
          document.getElementById('finalStockPreview').textContent = product.stock;
          
          const adjustModal = new bootstrap.Modal(document.getElementById('adjustStockModal'));
          adjustModal.show();
      }
    } else if (action === 'delete') {
      if (!window.IS_ADMIN) return;
      // Nota: eliminación no persistente en UI (opcionalmente implementar en backend)
      if(confirm('¿Estás seguro de eliminar este producto?')) {
          const idx = PRODUCTS.findIndex(p => p.code === productId);
          if (idx >= 0) { PRODUCTS.splice(idx, 1); renderGrid(); }
      }
    }
  });

  // Handle Edit Form Submission
  const editForm = document.getElementById('editProductForm');
  if (editForm) {
      editForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const formData = new FormData(editForm);
          const csrftoken = document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1];
          
          fetch(window.location.href, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': csrftoken || ''
              },
              body: formData
          })
          .then(r => r.json())
          .then(data => {
              if (data.ok) {
                  // Update local data
                  const pid = formData.get('product_id');
                  const product = PRODUCTS.find(p => p.code === pid);
                  if (product) {
                      product.name = formData.get('name');
                      product.price = parseInt(formData.get('price'));
                      product.image_url = formData.get('image_url');
                      product.category = formData.get('category');
                      product.description = formData.get('description');
                      product.stock = parseInt(formData.get('stock'));
                      const sizesStr = formData.get('sizes');
                      product.sizes = sizesStr ? sizesStr.split(',').map(s => s.trim()).filter(s => s) : [];
                      product.has_sizes = product.sizes.length > 0;
                      product.status = updateStockStatus(product);
                      renderGrid();
                  }
                  // Close modal
                  const modalEl = document.getElementById('editProductModal');
                  const modal = bootstrap.Modal.getInstance(modalEl);
                  modal.hide();
                  alert('Producto actualizado correctamente');
              } else {
                  alert('Error: ' + data.error);
              }
          })
          .catch(err => {
              console.error(err);
              alert('Error al actualizar el producto');
          });
      });
  }

  // Add Product Modal Logic
  const addHasSizes = document.getElementById('addHasSizes');
  const sizeScaleContainer = document.getElementById('sizeScaleContainer');
  const sizeScaleSelect = document.querySelector('select[name="size_scale"]');
  const customSizeInput = document.getElementById('customSizeInput');

  if (addHasSizes) {
      addHasSizes.addEventListener('change', (e) => {
          sizeScaleContainer.style.display = e.target.checked ? 'block' : 'none';
      });
  }

  if (sizeScaleSelect) {
      sizeScaleSelect.addEventListener('change', (e) => {
          customSizeInput.style.display = e.target.value === 'custom' ? 'block' : 'none';
      });
  }

  // Adjust Stock Logic (Worker)
  const adjustForm = document.getElementById('adjustStockForm');
  const btnIncrease = document.getElementById('btnIncrease');
  const btnDecrease = document.getElementById('btnDecrease');
  const stockAdjustment = document.getElementById('stockAdjustment');
  const currentStockValue = document.getElementById('currentStockValue');
  const finalStockPreview = document.getElementById('finalStockPreview');

  function updateFinalStock() {
      const current = parseInt(currentStockValue.value || 0);
      const adjustment = parseInt(stockAdjustment.value || 0);
      const final = Math.max(0, current + adjustment);
      finalStockPreview.textContent = final;
  }

  if (stockAdjustment) {
      stockAdjustment.addEventListener('input', updateFinalStock);
      btnIncrease.addEventListener('click', () => {
          stockAdjustment.value = parseInt(stockAdjustment.value || 0) + 1;
          updateFinalStock();
      });
      btnDecrease.addEventListener('click', () => {
          stockAdjustment.value = parseInt(stockAdjustment.value || 0) - 1;
          updateFinalStock();
      });
  }

  if (adjustForm) {
      adjustForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const current = parseInt(currentStockValue.value || 0);
          const adjustment = parseInt(stockAdjustment.value || 0);
          const finalStock = Math.max(0, current + adjustment);
          
          const formData = new FormData();
          formData.append('action', 'update_stock');
          formData.append('product_id', document.getElementById('adjustStockId').value);
          formData.append('stock', finalStock);
          
          const csrftoken = document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1];

          fetch(window.location.href, {
              method: 'POST',
              headers: { 'X-CSRFToken': csrftoken || '' },
              body: formData
          })
          .then(r => r.json())
          .then(data => {
              if (data.ok) {
                  const pid = formData.get('product_id');
                  const product = PRODUCTS.find(p => p.code === pid);
                  if (product) {
                      product.stock = parseInt(data.stock);
                      product.status = updateStockStatus(product);
                      renderGrid();
                  }
                  const modalEl = document.getElementById('adjustStockModal');
                  const modal = bootstrap.Modal.getInstance(modalEl);
                  modal.hide();
                  alert('Stock actualizado correctamente');
              } else {
                  alert('Error: ' + data.error);
              }
          })
          .catch(err => {
              console.error(err);
              alert('Error al actualizar stock');
          });
      });
  }

  renderGrid();
});
