(function () {
  const workerWrapper = document.getElementById('workerDashboard');
  if (!workerWrapper) return;

  const workerId = workerWrapper.dataset.workerId || '';
  const drillModalEl = document.getElementById('drillModal');
  const drillTitleEl = document.getElementById('drillTitle');
  const drillCanvas = document.getElementById('drillChartCanvas');
  const drillTableEl = document.getElementById('drillTable');
  let drillChartInstance = null;

  const percentFormatter = new Intl.NumberFormat('es-CL', {
    style: 'percent',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
  const numberFormatter = new Intl.NumberFormat('es-CL', {
    maximumFractionDigits: 1,
  });

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

  function prepareDrillConfig(source, mode = 'number') {
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
        if (mode === 'percent100') {
          return `${datasetLabel}${Math.round(value)}%`;
        }
        if (mode === 'percent1') {
          return `${datasetLabel}${percentFormatter.format(value)}`;
        }
        if (mode === 'hours') {
          return `${datasetLabel}${numberFormatter.format(value)} h`;
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
    if (mode === 'percent100') {
      targetScale.ticks.callback = (value) => `${Math.round(value)}%`;
    } else if (mode === 'percent1') {
      targetScale.ticks.callback = (value) => percentFormatter.format(value);
    } else if (mode === 'hours') {
      targetScale.ticks.callback = (value) => `${numberFormatter.format(value)} h`;
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

  async function handleDrill(url, title, mode = 'number') {
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

  const radarCanvas = document.getElementById('workerStatsRadar');
  if (radarCanvas) {
    const radarData = JSON.parse(radarCanvas.dataset.chart || '{}');
    const ctx = radarCanvas.getContext('2d');
    new Chart(ctx, {
      type: 'radar',
      data: {
        labels: radarData.labels || [],
        datasets: [
          {
            label: 'Desempeño',
            data: radarData.values || [],
            backgroundColor: 'rgba(168, 85, 247, 0.18)',
            borderColor: '#a855f7',
            pointBackgroundColor: '#f59e0b',
            borderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        responsive: true,
        scales: {
          r: {
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: {
              display: true,
              backdropColor: 'transparent',
              callback: (value) => `${value}%`,
            },
            angleLines: { color: 'rgba(148, 163, 184, 0.3)' },
            grid: { color: 'rgba(148, 163, 184, 0.2)' },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `${context.label}: ${Math.round(context.parsed.r)}%`,
            },
          },
        },
        onClick: async (_event, elements) => {
          if (!elements?.length) return;
          const index = elements[0].index;
          const metric = (radarData.labels || [])[index];
          if (!metric) return;
          const title = `Tendencia de ${metric}`;
          const params = new URLSearchParams({ name: metric, worker_id: workerId });
          await handleDrill(`/api/drill/metric?${params.toString()}`, title, 'percent100');
        },
      },
    });
  }

  const attendanceCanvas = document.getElementById('workerAttendanceChart');
  if (attendanceCanvas) {
    const attendanceData = JSON.parse(attendanceCanvas.dataset.chart || '{}');
    const ctx = attendanceCanvas.getContext('2d');
    const attendanceValues = (attendanceData.values || []).map((value) => Math.round(value * 100));
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: attendanceData.labels || [],
        datasets: [
          {
            label: 'Asistencia',
            data: attendanceValues,
            backgroundColor: '#2563eb',
            borderRadius: 6,
            maxBarThickness: 48,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        responsive: true,
        scales: {
          y: {
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: {
              callback: (value) => `${Math.round(value)}%`,
            },
          },
          x: {
            ticks: { maxRotation: 30, minRotation: 0 },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `${Math.round(context.parsed.y)}%`,
            },
          },
        },
        onClick: async (_event, elements) => {
          if (!elements?.length) return;
          const index = elements[0].index;
          const date = (attendanceData.dates || [])[index];
          if (!date) return;
          const title = `Detalle de turno · ${date}`;
          const params = new URLSearchParams({ date, worker_id: workerId });
          await handleDrill(`/api/drill/shift?${params.toString()}`, title, 'hours');
        },
      },
    });
  }
})();
