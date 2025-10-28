(function () {
  const currencyFormatter = new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    maximumFractionDigits: 0,
  });
  const numberFormatter = new Intl.NumberFormat('es-CL');

  const storeSelect = document.getElementById('storeSelect');
  const drillModalEl = document.getElementById('drillModal');
  const drillTitleEl = document.getElementById('drillTitle');
  const drillCanvas = document.getElementById('drillChartCanvas');
  const drillTableEl = document.getElementById('drillTable');
  let drillChartInstance = null;

  function getStoreValue() {
    return storeSelect?.value || 'A';
  }

  function getStoreLabel() {
    return storeSelect?.selectedOptions?.[0]?.textContent?.trim() || 'Tienda A';
  }

  function openDrill(title) {
    if (drillTitleEl) {
      drillTitleEl.textContent = title || 'Detalle';
    }
    if (!drillModalEl) return;
    const modal = new bootstrap.Modal(drillModalEl);
    modal.show();
  }

  async function fetchJSON(url) {
    const response = await fetch(url, { headers: { Accept: 'application/json' } });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  }

  function renderTable(rows) {
    if (!drillTableEl) return;
    if (!rows || !rows.length) {
      drillTableEl.innerHTML = '<tbody><tr><td class="text-muted">Sin datos</td></tr></tbody>';
      return;
    }
    const headers = Object.keys(rows[0] || {});
    const thead = `<thead class="text-muted"><tr>${headers
      .map((header) => `<th>${header}</th>`)
      .join('')}</tr></thead>`;
    const tbody = `<tbody>${rows
      .map((row) => `<tr>${headers.map((header) => `<td>${row[header]}</td>`).join('')}</tr>`)
      .join('')}</tbody>`;
    drillTableEl.innerHTML = thead + tbody;
  }

  function prepareDrillConfig(source, mode) {
    if (!source || !drillCanvas) {
      return null;
    }
    const config = JSON.parse(JSON.stringify(source));
    config.type = config.type || 'bar';
    config.options = config.options || {};
    config.options.responsive = true;
    config.options.maintainAspectRatio = false;
    config.options.interaction = config.options.interaction || { mode: 'nearest', intersect: true };

    const plugins = config.options.plugins || {};
    const tooltip = plugins.tooltip || {};
    tooltip.callbacks = tooltip.callbacks || {};
    if (!tooltip.callbacks.label) {
      tooltip.callbacks.label = (context) => {
        const datasetLabel = context.dataset?.label ? `${context.dataset.label}: ` : '';
        const value = context.parsed.y ?? context.parsed;
        if (mode === 'currency') {
          return `${datasetLabel}${currencyFormatter.format(value)}`;
        }
        if (mode === 'percent') {
          return `${datasetLabel}${value.toFixed ? value.toFixed(0) : value}%`;
        }
        return `${datasetLabel}${numberFormatter.format(value)}`;
      };
    }
    plugins.tooltip = tooltip;
    if (plugins.legend === undefined) {
      plugins.legend = { display: (config.data?.datasets?.length || 0) > 1 };
    }
    config.options.plugins = plugins;

    if (!config.options.scales) {
      config.options.scales = {};
    }
    const axisKey = config.options.indexAxis === 'y' ? 'x' : 'y';
    config.options.scales[axisKey] = config.options.scales[axisKey] || {};
    const targetScale = config.options.scales[axisKey];
    targetScale.ticks = targetScale.ticks || {};
    if (mode === 'currency') {
      targetScale.ticks.callback = (value) => currencyFormatter.format(value);
    } else if (mode === 'percent') {
      targetScale.ticks.callback = (value) => `${value}%`;
    }

    return config;
  }

  function renderDrillChart(config) {
    if (!config || !drillCanvas) return;
    const ctx = drillCanvas.getContext('2d');
    if (drillChartInstance) {
      drillChartInstance.destroy();
    }
    drillChartInstance = new Chart(ctx, config);
  }

  async function handleDrill(url, title, mode = 'currency') {
    try {
      openDrill(title);
      const data = await fetchJSON(url);
      const config = prepareDrillConfig(data.chart, mode);
      renderDrillChart(config);
      renderTable(data.rows || []);
    } catch (error) {
      console.error(error);
    }
  }

  const salesCanvas = document.getElementById('chartSalesByDay');
  if (salesCanvas) {
    const salesData = JSON.parse(salesCanvas.dataset.chart || '{}');
    const ctx = salesCanvas.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: salesData.dates || [],
        datasets: [
          {
            label: 'Ventas diarias',
            data: salesData.sales || [],
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.18)',
            tension: 0.35,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: {
            ticks: { maxRotation: 45, minRotation: 0 },
            grid: { display: false },
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => currencyFormatter.format(value),
            },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: (context) => currencyFormatter.format(context.parsed.y),
            },
          },
        },
        onClick: async (_event, elements) => {
          if (!elements?.length) return;
          const index = elements[0].index;
          const date = (salesData.dates || [])[index];
          if (!date) return;
          const title = `Órdenes del ${date} · ${getStoreLabel()}`;
          const url = `/api/drill/orders?date=${encodeURIComponent(date)}&store=${getStoreValue()}`;
          await handleDrill(url, title, 'currency');
        },
      },
    });
  }

  const categoriesCanvas = document.getElementById('chartTopCategories');
  if (categoriesCanvas) {
    const categoriesData = JSON.parse(categoriesCanvas.dataset.chart || '{}');
    const ctx = categoriesCanvas.getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: categoriesData.categories || [],
        datasets: [
          {
            label: 'Ventas por categoría',
            data: categoriesData.sales || [],
            backgroundColor: '#10b981',
            borderRadius: 8,
            maxBarThickness: 48,
          },
        ],
      },
      options: {
        indexAxis: 'y',
        maintainAspectRatio: false,
        responsive: true,
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              callback: (value) => currencyFormatter.format(value),
            },
          },
          y: {
            ticks: { autoSkip: false },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => currencyFormatter.format(context.parsed.x),
            },
          },
        },
        onClick: async (_event, elements) => {
          if (!elements?.length) return;
          const index = elements[0].index;
          const category = (categoriesData.categories || [])[index];
          if (!category) return;
          const title = `Detalle de ${category} · ${getStoreLabel()}`;
          const params = new URLSearchParams({ name: category, store: getStoreValue() });
          await handleDrill(`/api/drill/category?${params.toString()}`, title, 'currency');
        },
      },
    });
  }

  const distributionCanvas = document.getElementById('chartPurchaseDistribution');
  if (distributionCanvas) {
    const distributionData = JSON.parse(distributionCanvas.dataset.chart || '{}');
    const bins = distributionData.bins || [];
    const ctx = distributionCanvas.getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: distributionData.labels || [],
        datasets: [
          {
            label: 'Frecuencia de tickets',
            data: distributionData.counts || [],
            backgroundColor: '#f97316',
            borderRadius: 6,
            maxBarThickness: 56,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: {
            ticks: { autoSkip: false },
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => numberFormatter.format(value),
            },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => {
                const count = context.parsed.y;
                const binLabel = (distributionData.labels || [])[context.dataIndex] || '';
                return `${numberFormatter.format(count)} tickets · ${binLabel}`;
              },
            },
          },
        },
        onClick: async (_event, elements) => {
          if (!elements?.length) return;
          const index = elements[0].index;
          const bin = bins[index] || {};
          const label = bin.label || (distributionData.labels || [])[index] || '';
          const params = new URLSearchParams({ store: getStoreValue() });
          if (bin.start !== undefined) {
            params.set('bin_start', bin.start);
          }
          if (bin.end !== undefined) {
            params.set('bin_end', bin.end);
          }
          const title = `Tickets entre ${label} · ${getStoreLabel()}`;
          await handleDrill(`/api/drill/purchase_bin?${params.toString()}`, title, 'currency');
        },
      },
    });
  }
})();
