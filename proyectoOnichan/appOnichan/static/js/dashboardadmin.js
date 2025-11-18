document.addEventListener('DOMContentLoaded', () => {
  const dataElement = document.getElementById('dashboard-data');
  if (!dataElement) {
    return;
  }

  let parsedData = {};
  try {
    parsedData = JSON.parse(dataElement.textContent || '{}');
  } catch (error) {
    console.error('No se pudo parsear la información del dashboard.', error);
  }

  const fallback = {
    kpis: {
      pedidos_hoy: { value: 26, trend: '+3 vs. ayer' },
      pendientes: { value: 14, trend: 'En línea con promedio' },
      ingresos_7d: { value: 1825000, trend: '+5% semana previa', isCurrency: true },
    },
    lineChart: {
      labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
      values: [18, 22, 19, 25, 28, 31, 24],
      detalles: {
        Lun: { Entregados: 15, Pendientes: 3 },
        Mar: { Entregados: 19, Pendientes: 3 },
        Mié: { Entregados: 15, Pendientes: 4 },
        Jue: { Entregados: 21, Pendientes: 4 },
        Vie: { Entregados: 24, Pendientes: 4 },
        Sáb: { Entregados: 27, Pendientes: 4 },
        Dom: { Entregados: 20, Pendientes: 4 },
      },
    },
    topProducts: {
      labels: ['Polera Oversized', 'Zapatillas Urban', 'Chaqueta Azul', 'Mochila Explorer'],
      values: [42, 35, 28, 22],
      detalles: {
        'Polera Oversized': { 'Negro / M': 14, 'Negro / L': 11, 'Blanco / M': 9, 'Blanco / L': 8 },
        'Zapatillas Urban': { '41': 12, '42': 10, '43': 8, '44': 5 },
        'Chaqueta Azul': { S: 7, M: 9, L: 7, XL: 5 },
        'Mochila Explorer': { Negro: 10, Gris: 7, Arena: 5 },
      },
    },
    categoryRevenue: {
      labels: ['Ropa', 'Calzado', 'Accesorios', 'Equipaje'],
      values: [520000, 410000, 195000, 132000],
      detalles: {
        Ropa: { Online: 320000, Tienda: 200000 },
        Calzado: { Online: 240000, Tienda: 170000 },
        Accesorios: { Online: 115000, Tienda: 80000 },
        Equipaje: { Online: 72000, Tienda: 60000 },
      },
    },
  };

  const data = parsedData && Object.keys(parsedData).length ? parsedData : fallback;
  const currencyFormatter = new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    maximumFractionDigits: 0,
  });

  const modal = document.getElementById('dashModal');
  const modalTitle = document.getElementById('dashModalTitle');
  const modalClose = document.getElementById('dashModalClose');
  const modalCanvas = document.getElementById('dashModalChart');
  let modalChartInstance = null;

  const palette = ['#4f46e5', '#22c55e', '#f97316', '#0ea5e9', '#ec4899', '#f59e0b', '#8b5cf6'];

  function setMetrics() {
    const metricKeys = ['pedidos_hoy', 'pendientes', 'ingresos_7d'];
    metricKeys.forEach((key) => {
      const metric = data.kpis?.[key] ?? fallback.kpis[key];
      const valueTarget = document.querySelector(`[data-kpi="${key}"]`);
      const trendTarget = document.querySelector(`[data-kpi-trend="${key}"]`);
      if (!valueTarget) {
        return;
      }
      const isCurrency = metric?.isCurrency || key === 'ingresos_7d';
      const formattedValue = isCurrency && metric?.value !== undefined
        ? currencyFormatter.format(metric.value)
        : (metric?.value ?? '--');
      valueTarget.textContent = formattedValue;
      if (trendTarget) {
        trendTarget.textContent = metric?.trend || '';
      }
    });
  }

  function closeModal() {
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
    if (modalChartInstance) {
      modalChartInstance.destroy();
      modalChartInstance = null;
    }
  }

  function openModal(config) {
    const { title, labels, values, datasetLabel = 'Detalle', type = 'bar' } = config;
    modalTitle.textContent = title;
    const ctx = modalCanvas.getContext('2d');
    if (modalChartInstance) {
      modalChartInstance.destroy();
    }
    modalChartInstance = new Chart(ctx, {
      type,
      data: {
        labels,
        datasets: [
          {
            label: datasetLabel,
            data: values,
            backgroundColor: labels.map((_, index) => palette[index % palette.length]),
            borderColor: labels.map((_, index) => palette[index % palette.length]),
            borderWidth: type === 'line' ? 2 : 1,
            tension: 0.35,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: type !== 'bar' || labels.length > 1,
            labels: {
              font: { size: 14 },
              padding: 15,
            },
          },
          tooltip: {
            titleFont: { size: 16 },
            bodyFont: { size: 14 },
            padding: 12,
            callbacks: {
              label: (context) => {
                const value = context.parsed.y ?? context.parsed;
                if (datasetLabel.toLowerCase().includes('ingreso')) {
                  return `${context.dataset.label}: ${currencyFormatter.format(value)}`;
                }
                return `${context.dataset.label}: ${value}`;
              },
            },
          },
        },
        scales: type === 'pie' || type === 'doughnut'
          ? {}
          : {
            y: {
              beginAtZero: true,
              ticks: {
                font: { size: 13 },
                ...(datasetLabel.toLowerCase().includes('ingreso')
                  ? {
                      callback: (val) => currencyFormatter.format(val),
                    }
                  : {}),
              },
            },
            x: {
              ticks: {
                font: { size: 13 },
              },
            },
          },
      },
    });

    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
  }

  modalClose?.addEventListener('click', closeModal);
  modal.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal.classList.contains('show')) {
      closeModal();
    }
  });

  setMetrics();

  Chart.defaults.color = '#1f2937';
  Chart.defaults.font.family = 'Inter, "Segoe UI", sans-serif';

  const lineCtx = document.getElementById('ordersLineChart');
  const pieCtx = document.getElementById('topProductsPieChart');
  const barCtx = document.getElementById('categoryRevenueBarChart');
  const multiPieCtx = document.getElementById('multiSeriesPieChart');

  if (!lineCtx || !pieCtx || !barCtx) {
    return;
  }

  const lineData = data.lineChart ?? fallback.lineChart;
  const pieData = data.topProducts ?? fallback.topProducts;
  const barData = data.categoryRevenue ?? fallback.categoryRevenue;
  const multiPieData = data.multiSeriesPie; // no fallback; se muestra sólo si existe
  console.log('[Dashboard] multiSeriesPie data:', multiPieData);

  const ordersLineChart = new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: lineData.labels,
      datasets: [
        {
          label: 'Pedidos',
          data: lineData.values,
          borderColor: '#4f46e5',
          backgroundColor: 'rgba(79, 70, 229, 0.18)',
          tension: 0.35,
          fill: true,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      interaction: { mode: 'nearest', intersect: false },
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0,
            font: { size: 14 },
          },
        },
        x: {
          ticks: {
            font: { size: 14, weight: '500' },
          },
        },
      },
      onClick: (event, elements) => {
        if (!elements.length) {
          return;
        }
        const index = elements[0].index;
        const label = lineData.labels[index];
        const detail = lineData.detalles?.[label];
        const detailLabels = detail ? Object.keys(detail) : ['Sin datos'];
        const detailValues = detail ? detailLabels.map((key) => detail[key]) : [0];
        openModal({
          title: `Pedidos ${label}`,
          labels: detailLabels,
          values: detailValues,
          datasetLabel: 'Pedidos',
        });
      },
    },
  });

  const pieColors = pieData.labels.map((_, index) => palette[index % palette.length]);
  const topProductsPieChart = new Chart(pieCtx, {
    type: 'pie',
    data: {
      labels: pieData.labels,
      datasets: [
        {
          data: pieData.values,
          backgroundColor: pieColors,
          hoverOffset: 10,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          titleFont: { size: 14 },
          bodyFont: { size: 14 },
        },
      },
      onClick: (event, elements) => {
        if (!elements.length) {
          return;
        }
        const index = elements[0].index;
        const label = pieData.labels[index];
        const detail = pieData.detalles?.[label];
        const detailLabels = detail ? Object.keys(detail) : ['Sin datos'];
        const detailValues = detail ? detailLabels.map((key) => detail[key]) : [0];
        openModal({
          title: `Top productos · ${label}`,
          labels: detailLabels,
          values: detailValues,
          datasetLabel: 'Unidades',
        });
      },
    },
  });

  const legendContainer = document.getElementById('topProductsLegend');
  if (legendContainer) {
    legendContainer.innerHTML = '';
    pieData.labels.forEach((label, index) => {
      const item = document.createElement('span');
      const marker = document.createElement('i');
      marker.style.backgroundColor = pieColors[index];
      const text = document.createElement('span');
      text.textContent = label;
      item.appendChild(marker);
      item.appendChild(text);
      legendContainer.appendChild(item);
    });
  }

  const categoryRevenueBarChart = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: barData.labels,
      datasets: [
        {
          label: 'Ingresos',
          data: barData.values,
          backgroundColor: barData.labels.map((_, index) => palette[index % palette.length]),
          borderRadius: 8,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.parsed.y;
              return `${context.dataset.label}: ${currencyFormatter.format(value)}`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => currencyFormatter.format(value),
            font: { size: 14 },
          },
        },
        x: {
          ticks: {
            font: { size: 14, weight: '500' },
          },
        },
      },
      onClick: (event, elements) => {
        if (!elements.length) {
          return;
        }
        const index = elements[0].index;
        const label = barData.labels[index];
        const detail = barData.detalles?.[label];
        const detailLabels = detail ? Object.keys(detail) : ['Sin datos'];
        const detailValues = detail ? detailLabels.map((key) => detail[key]) : [0];
        openModal({
          title: `Ingresos · ${label}`,
          labels: detailLabels,
          values: detailValues,
          datasetLabel: 'Ingresos',
        });
      },
    },
  });

  if (multiPieCtx && multiPieData && multiPieData.labels && multiPieData.datasets) {
    const labels = multiPieData.labels;
    const categoriesData = multiPieData.datasets.categories;
    const productsData = multiPieData.datasets.products;
    const categories = multiPieData.categories || [];
    const productCategoryMap = multiPieData.productCategoryMap || {};

    // Colores base para categorías
    const baseColors = ['#2563eb', '#16a34a', '#dc2626', '#9333ea', '#f59e0b', '#0d9488', '#6d28d9', '#ea580c'];
    const categoryColorMap = {};
    categories.forEach((c, i) => { categoryColorMap[c] = baseColors[i % baseColors.length]; });

    function tint(hex, factor = 0.3) {
      const h = hex.replace('#', '');
      const r = parseInt(h.substring(0, 2), 16);
      const g = parseInt(h.substring(2, 4), 16);
      const b = parseInt(h.substring(4, 6), 16);
      const nr = Math.min(255, Math.round(r + (255 - r) * factor));
      const ng = Math.min(255, Math.round(g + (255 - g) * factor));
      const nb = Math.min(255, Math.round(b + (255 - b) * factor));
      return `rgb(${nr},${ng},${nb})`;
    }

    const categoryBackground = labels.map((lbl, idx) => {
      if (idx < categories.length) {
        return categoryColorMap[lbl] || '#9ca3af';
      }
      return 'rgba(0,0,0,0)';
    });
    const productBackground = labels.map((lbl, idx) => {
      if (idx >= categories.length) {
        const cat = productCategoryMap[lbl];
        const base = categoryColorMap[cat] || '#6b7280';
        return tint(base, 0.45);
      }
      return 'rgba(0,0,0,0)';
    });

    const multiSeriesPieChart = new Chart(multiPieCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [
          {
            label: 'Categorías',
            data: categoriesData,
            backgroundColor: categoryBackground,
            borderWidth: 1,
            spacing: 2,
            weight: 0.6,
          },
          {
            label: 'Productos',
            data: productsData,
            backgroundColor: productBackground,
            borderWidth: 1,
            spacing: 1,
            weight: 1.2,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        cutout: '40%',
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.parsed;
                if (ctx.dataset.label === 'Categorías') {
                  return `${ctx.label}: ${val} u.`;
                }
                if (ctx.dataset.label === 'Productos') {
                  const cat = productCategoryMap[ctx.label] || '—';
                  return `${ctx.label} (${cat}): ${val} u.`;
                }
                return `${ctx.label}: ${val}`;
              },
            },
          },
          legend: { display: false },
        },
        onClick: (evt, els) => {
          if (!els.length) return;
          const el = els[0];
          const idx = el.index;
          const dsLabel = el.dataset.label;
          if (dsLabel === 'Categorías' && idx < categories.length) {
            const cat = labels[idx];
            // Drill-down: productos de esa categoría
            const productLabels = Object.keys(productCategoryMap).filter(p => productCategoryMap[p] === cat);
            const productValues = productLabels.map(p => {
              const pIndex = labels.indexOf(p);
              return pIndex >= 0 ? productsData[pIndex] : 0;
            });
            openModal({ title: `Productos · ${cat}`, labels: productLabels, values: productValues, datasetLabel: 'Unidades', type: 'bar' });
          } else if (dsLabel === 'Productos' && idx >= categories.length) {
            const prod = labels[idx];
            const cat = productCategoryMap[prod] || '—';
            openModal({ title: `${prod} · ${cat}`, labels: [prod], values: [productsData[idx]], datasetLabel: 'Unidades', type: 'bar' });
          }
        },
      },
    });

    // Leyenda manual (categorías y conteo)
    const multiLegend = document.getElementById('multiSeriesPieLegend');
    if (multiLegend) {
      multiLegend.innerHTML = '';
      categories.forEach(cat => {
        const span = document.createElement('span');
        const marker = document.createElement('i');
        marker.style.backgroundColor = categoryColorMap[cat];
        const text = document.createElement('span');
        text.textContent = cat;
        span.appendChild(marker);
        span.appendChild(text);
        multiLegend.appendChild(span);
      });
    }
  } else if (multiPieCtx) {
    // Fallback visual cuando no hay datos para el gráfico multi series
    const wrapper = multiPieCtx.parentElement;
    if (wrapper) {
      const msg = document.createElement('div');
      msg.style.padding = '1rem';
      msg.style.fontSize = '0.9rem';
      msg.style.color = '#6b7280';
      msg.textContent = 'Sin datos para multi-series (multiSeriesPie no presente).';
      wrapper.appendChild(msg);
    }
    console.warn('[Dashboard] multiSeriesPie no disponible o vacío.');
  }
});
