document.addEventListener('DOMContentLoaded', () => {
    // Initial Data
    const dataElement = document.getElementById('dashboard-data');
    let initialData = {};
    try {
        initialData = JSON.parse(dataElement.textContent || '{}');
    } catch (error) {
        console.error('Error parsing dashboard data:', error);
    }

    const currencyFormatter = new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        maximumFractionDigits: 0,
    });

    // Highcharts Global Options
    Highcharts.setOptions({
        lang: {
            loading: 'Cargando...',
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            exportButtonTitle: "Exportar",
            printButtonTitle: "Importar",
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "Hasta",
            rangeSelectorZoom: "Período",
            downloadPNG: 'Descargar imagen PNG',
            downloadJPEG: 'Descargar imagen JPEG',
            downloadPDF: 'Descargar documento PDF',
            downloadSVG: 'Descargar imagen SVG',
            printChart: 'Imprimir gráfico',
            thousandsSep: ".",
            decimalPoint: ','
        },
        colors: ['#4f46e5', '#22c55e', '#f97316', '#0ea5e9', '#ec4899', '#f59e0b', '#8b5cf6']
    });

    // Chart Instances
    let ordersChart, topProductsChart, revenueChart, multiPieChart, modalChart;

    // Render Functions
    function createOrdersChart(lineData) {
        if (!lineData) return;
        console.log('Creating Orders Chart');
        ordersChart = Highcharts.chart('ordersLineChart', {
            chart: { type: 'area' },
            title: { text: null },
            xAxis: { categories: lineData.labels },
            yAxis: { title: { text: 'Pedidos' } },
            tooltip: { shared: true },
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: { radius: 4 },
                    lineWidth: 2,
                    states: { hover: { lineWidth: 3 } },
                    threshold: null
                },
                series: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function () {
                                const label = this.category;
                                const detail = this.series.chart.customDetalles?.[label];
                                if (detail) {
                                    openModal({
                                        title: `Pedidos ${label}`,
                                        labels: Object.keys(detail),
                                        values: Object.values(detail),
                                        datasetLabel: 'Pedidos',
                                        type: 'column'
                                    });
                                }
                            }
                        }
                    }
                }
            },
            series: [{
                name: 'Pedidos',
                data: lineData.values
            }]
        });
        ordersChart.customDetalles = lineData.detalles;
    }

    function updateOrdersChart(lineData) {
        if (!lineData) return;
        if (!ordersChart) {
            createOrdersChart(lineData);
            return;
        }
        console.log('Updating Orders Chart');
        ordersChart.customDetalles = lineData.detalles;
        ordersChart.xAxis[0].setCategories(lineData.labels, false);
        ordersChart.series[0].setData(lineData.values, true);
    }

    function createTopProductsChart(pieData) {
        if (!pieData) return;
        console.log('Creating Top Products Chart');
        const seriesData = pieData.labels.map((label, i) => ({
            name: label,
            y: pieData.values[i]
        }));

        topProductsChart = Highcharts.chart('topProductsPieChart', {
            chart: { type: 'pie' },
            title: { text: null },
            tooltip: { pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>' },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: { enabled: false },
                    showInLegend: true,
                    point: {
                        events: {
                            click: function () {
                                const label = this.name;
                                const detail = this.series.chart.customDetalles?.[label];
                                if (detail) {
                                    openModal({
                                        title: `Top productos · ${label}`,
                                        labels: Object.keys(detail),
                                        values: Object.values(detail),
                                        datasetLabel: 'Unidades',
                                        type: 'pie'
                                    });
                                }
                            }
                        }
                    }
                }
            },
            series: [{
                name: 'Unidades',
                colorByPoint: true,
                data: seriesData
            }]
        });
        topProductsChart.customDetalles = pieData.detalles;
        
        // Custom Legend (if needed, but Highcharts has built-in legend)
        const legendContainer = document.getElementById('topProductsLegend');
        if (legendContainer) legendContainer.innerHTML = ''; 
    }

    function updateTopProductsChart(pieData) {
        if (!pieData) return;
        if (!topProductsChart) {
            createTopProductsChart(pieData);
            return;
        }
        console.log('Updating Top Products Chart');
        const seriesData = pieData.labels.map((label, i) => ({
            name: label,
            y: pieData.values[i]
        }));
        topProductsChart.customDetalles = pieData.detalles;
        topProductsChart.series[0].setData(seriesData, true);
    }

    function createRevenueChart(barData) {
        if (!barData) return;
        console.log('Creating Revenue Chart');
        revenueChart = Highcharts.chart('categoryRevenueBarChart', {
            chart: { type: 'column' },
            title: { text: null },
            xAxis: { categories: barData.labels },
            yAxis: {
                title: { text: 'Ingresos' },
                labels: {
                    formatter: function () { return currencyFormatter.format(this.value); }
                }
            },
            tooltip: {
                formatter: function () {
                    return `<b>${this.x}</b><br/>${this.series.name}: ${currencyFormatter.format(this.y)}`;
                }
            },
            plotOptions: {
                column: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function () {
                                const label = this.category;
                                const detail = this.series.chart.customDetalles?.[label];
                                if (detail) {
                                    openModal({
                                        title: `Ingresos · ${label}`,
                                        labels: Object.keys(detail),
                                        values: Object.values(detail),
                                        datasetLabel: 'Ingresos',
                                        type: 'pie', // or column
                                        isCurrency: true
                                    });
                                }
                            }
                        }
                    }
                }
            },
            series: [{
                name: 'Ingresos',
                data: barData.values,
                colorByPoint: true
            }]
        });
        revenueChart.customDetalles = barData.detalles;
    }

    function updateRevenueChart(barData) {
        if (!barData) return;
        if (!revenueChart) {
            createRevenueChart(barData);
            return;
        }
        console.log('Updating Revenue Chart');
        revenueChart.customDetalles = barData.detalles;
        revenueChart.xAxis[0].setCategories(barData.labels, false);
        revenueChart.series[0].setData(barData.values, true);
    }

    function createMultiPieChart(multiData) {
        if (!multiData) return;
        console.log('Creating Multi Pie Chart');
        // Prepare data for Highcharts
        // Inner ring: Categories
        const categoriesData = multiData.categories.map((cat, i) => ({
            name: cat,
            y: multiData.datasets.categories[i],
            color: Highcharts.getOptions().colors[i % Highcharts.getOptions().colors.length]
        })).filter(p => p.y > 0);

        // Outer ring: Products
        const productNames = multiData.labels.slice(multiData.categories.length);
        const productValues = multiData.datasets.products.slice(multiData.categories.length);
        
        const productsSeries = productNames.map((name, i) => {
            const cat = multiData.productCategoryMap[name];
            const catIdx = multiData.categories.indexOf(cat);
            const color = Highcharts.color(Highcharts.getOptions().colors[catIdx % Highcharts.getOptions().colors.length]).brighten(0.1).get();
            return {
                name: name,
                y: productValues[i],
                color: color
            };
        }).filter(p => p.y > 0);

        multiPieChart = Highcharts.chart('multiSeriesPieChart', {
            chart: { type: 'pie' },
            title: { text: null },
            plotOptions: {
                pie: {
                    shadow: false,
                    center: ['50%', '50%']
                }
            },
            tooltip: {
                valueSuffix: ' unidades'
            },
            series: [{
                name: 'Categorías',
                data: categoriesData,
                size: '60%',
                dataLabels: {
                    formatter: function () {
                        return this.y > 5 ? this.point.name : null;
                    },
                    color: '#ffffff',
                    distance: -30
                }
            }, {
                name: 'Productos',
                data: productsSeries,
                size: '80%',
                innerSize: '60%',
                dataLabels: {
                    formatter: function () {
                        // display only if larger than 1
                        return this.y > 1 ? `<b>${this.point.name}:</b> ${this.y}` : null;
                    }
                },
                id: 'versions'
            }]
        });
        
        const multiLegend = document.getElementById('multiSeriesPieLegend');
        if (multiLegend) multiLegend.innerHTML = ''; // Clear custom legend
    }

    function updateMultiPieChart(multiData) {
        if (!multiData) return;
        if (!multiPieChart) {
            createMultiPieChart(multiData);
            return;
        }
        console.log('Updating Multi Pie Chart');
        // Prepare data for Highcharts
        // Inner ring: Categories
        const categoriesData = multiData.categories.map((cat, i) => ({
            name: cat,
            y: multiData.datasets.categories[i],
            color: Highcharts.getOptions().colors[i % Highcharts.getOptions().colors.length]
        })).filter(p => p.y > 0);

        // Outer ring: Products
        const productNames = multiData.labels.slice(multiData.categories.length);
        const productValues = multiData.datasets.products.slice(multiData.categories.length);
        
        const productsSeries = productNames.map((name, i) => {
            const cat = multiData.productCategoryMap[name];
            const catIdx = multiData.categories.indexOf(cat);
            const color = Highcharts.color(Highcharts.getOptions().colors[catIdx % Highcharts.getOptions().colors.length]).brighten(0.1).get();
            return {
                name: name,
                y: productValues[i],
                color: color
            };
        }).filter(p => p.y > 0);

        multiPieChart.series[0].setData(categoriesData, false);
        multiPieChart.series[1].setData(productsSeries, true);
    }

    function updateMetrics(kpis) {
        if (!kpis) return;
        Object.keys(kpis).forEach(key => {
            const metric = kpis[key];
            const valueEl = document.querySelector(`[data-kpi="${key}"]`);
            const trendEl = document.querySelector(`[data-kpi-trend="${key}"]`);
            
            if (valueEl) {
                let val = metric.value;
                if (metric.isCurrency || key === 'ingresos_7d') {
                    val = currencyFormatter.format(val);
                }
                valueEl.textContent = val;
            }
            if (trendEl) {
                trendEl.textContent = metric.trend || '';
            }
        });
    }

    // Modal Logic
    const modalEl = document.getElementById('dashModal');
    const modalTitle = document.getElementById('dashModalTitle');
    let bootstrapModal = modalEl ? new bootstrap.Modal(modalEl, { backdrop: true }) : null;

    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', () => {
            // Reset Top Products Pie Chart slicing
            if (topProductsChart && topProductsChart.series && topProductsChart.series[0]) {
                topProductsChart.series[0].points.forEach(p => {
                    if (p.sliced) p.slice(false);
                });
            }
        });
    }

    function openModal(config) {
        if (!bootstrapModal) return;
        
        modalTitle.textContent = config.title;
        
        // Destroy previous chart if exists
        if (modalChart) {
            modalChart.destroy();
        }

        // Render new chart
        const seriesData = config.labels.map((l, i) => ({
            name: l,
            y: config.values[i]
        }));

        modalChart = Highcharts.chart('dashModalChart', {
            chart: { type: config.type || 'column' },
            title: { text: null },
            xAxis: { categories: config.labels },
            yAxis: { 
                title: { text: config.datasetLabel },
                labels: {
                    formatter: function() {
                        return config.isCurrency ? currencyFormatter.format(this.value) : this.value;
                    }
                }
            },
            tooltip: {
                formatter: function() {
                    const val = config.isCurrency ? currencyFormatter.format(this.y) : this.y;
                    return `<b>${this.point.name || this.x}</b><br/>${this.series.name}: ${val}`;
                }
            },
            series: [{
                name: config.datasetLabel,
                data: config.type === 'pie' ? seriesData : config.values,
                colorByPoint: config.type === 'pie'
            }]
        });

        bootstrapModal.show();
    }

    // Initial Render
    if (initialData && Object.keys(initialData).length > 0) {
        updateMetrics(initialData.kpis);
        createOrdersChart(initialData.lineChart);
        createTopProductsChart(initialData.topProducts);
        createRevenueChart(initialData.categoryRevenue);
        createMultiPieChart(initialData.multiSeriesPie);
    } else {
        console.warn('No initial data found, waiting for WebSocket update...');
    }

    // Period Select Logic
    // Unified Data Fetcher
    function fetchDashboardData(url, pushToHistory = true) {
        // Show loading state
        const wrapper = document.querySelector('.dashboard-wrapper');
        if (wrapper) wrapper.style.opacity = '0.6';

        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                console.log('AJAX update received', data);
                updateMetrics(data.kpis);
                updateOrdersChart(data.lineChart);
                updateTopProductsChart(data.topProducts);
                updateRevenueChart(data.categoryRevenue);
                updateMultiPieChart(data.multiSeriesPie);
                
                // Update Navigation Buttons
                const btnPrev = document.getElementById('btnPrevPeriod');
                const btnNext = document.getElementById('btnNextPeriod');
                
                function updateNavButton(btn, url) {
                    if (!btn) return;
                    if (url) {
                        btn.setAttribute('href', url);
                        btn.classList.remove('disabled');
                        btn.style.pointerEvents = 'auto';
                        btn.style.opacity = '1';
                    } else {
                        btn.removeAttribute('href');
                        btn.classList.add('disabled');
                        btn.style.pointerEvents = 'none';
                        btn.style.opacity = '0.5';
                    }
                }

                updateNavButton(btnPrev, data.prev_url);
                updateNavButton(btnNext, data.next_url);

                // Update Title
                const titleEl = document.getElementById('chartLineTitle');
                if (titleEl && data.title_text) titleEl.textContent = data.title_text;

                // Update Input Value
                if (data.period && data.ref_value) {
                    const activeInputGroup = document.getElementById(`input-${data.period}`);
                    if (activeInputGroup) {
                        const input = activeInputGroup.querySelector('input');
                        if (input) input.value = data.ref_value;
                    }
                    // Also update radio button if needed (e.g. if changed via arrow navigation across years/months boundary? No, period stays same usually)
                    // But if backend forces a period change, we should update radio.
                    const radio = document.querySelector(`input[name="period"][value="${data.period}"]`);
                    if (radio && !radio.checked) {
                        radio.checked = true;
                        updateInputVisibility();
                    }
                }
                
                // Push History
                if (pushToHistory) {
                    const queryString = url.split('?')[1];
                    if (queryString) {
                        window.history.pushState({}, '', `?${queryString}`);
                    }
                }
                
                // Update dataElement attributes for WebSocket consistency
                if (dataElement) {
                    dataElement.dataset.period = data.period || 'week';
                    dataElement.dataset.refValue = data.ref_value || '';
                }
            })
            .catch(error => console.error('Error fetching dashboard data:', error))
            .finally(() => {
                if (wrapper) wrapper.style.opacity = '1';
            });
    }

    // Period Select & Input Logic
    const filterForm = document.getElementById('dashboardFilterForm');
    const periodRadios = document.querySelectorAll('input[name="period"]');
    const inputGroups = {
        'week': document.getElementById('input-week'),
        'month': document.getElementById('input-month'),
        'year': document.getElementById('input-year')
    };

    function updateInputVisibility() {
        const selectedRadio = document.querySelector('input[name="period"]:checked');
        const selected = selectedRadio ? selectedRadio.value : 'week';
        
        Object.keys(inputGroups).forEach(key => {
            if (inputGroups[key]) {
                inputGroups[key].style.display = (key === selected) ? '' : 'none';
                const input = inputGroups[key].querySelector('input');
                if (input) input.disabled = (key !== selected);
            }
        });
    }

    function handleFilterChange() {
        if (!filterForm) return;
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData);
        const url = `${apiDashboardUrl}?${params.toString()}`;
        fetchDashboardData(url);
    }

    // Attach listeners to Radio Buttons
    periodRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateInputVisibility();
            handleFilterChange();
        });
    });

    // Initial setup
    updateInputVisibility();

    // Attach change listeners to all date inputs
    Object.values(inputGroups).forEach(group => {
        if (group) {
            const input = group.querySelector('input');
            if (input) {
                input.addEventListener('change', handleFilterChange);
            }
        }
    });

    // Navigation Arrows Logic
    const btnPrev = document.getElementById('btnPrevPeriod');
    const btnNext = document.getElementById('btnNextPeriod');

    function handleNavClick(e) {
        e.preventDefault();
        const href = this.getAttribute('href'); 
        console.log('Navigating to:', href); // Debug log
        if (href) {
            const url = `${apiDashboardUrl}${href}`;
            fetchDashboardData(url);
        }
    }

    if (btnPrev) btnPrev.addEventListener('click', handleNavClick);
    if (btnNext) btnNext.addEventListener('click', handleNavClick);

    // Prevent form submit (if user hits enter)
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFilterChange();
        });
    }

    // Polling & WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // Construct WS URL using server-provided context to ensure consistency
    // Ensure dataElement is available and has attributes
    const currentPeriod = (dataElement && dataElement.dataset.period) ? dataElement.dataset.period : 'week';
    const currentRefValue = (dataElement && dataElement.dataset.refValue) ? dataElement.dataset.refValue : '';
    
    console.log('Dashboard Config:', { currentPeriod, currentRefValue });

    let wsQuery = `?period=${currentPeriod}`;
    if (currentPeriod === 'week' && currentRefValue) wsQuery += `&week=${currentRefValue}`;
    if (currentPeriod === 'month' && currentRefValue) wsQuery += `&month=${currentRefValue}`;
    if (currentPeriod === 'year' && currentRefValue) wsQuery += `&year=${currentRefValue}`;

    const wsUrl = `${protocol}//${window.location.host}/ws/dashboard/${wsQuery}`;
    let socket;

    function connectWebSocket() {
        console.log('Connecting to WebSocket:', wsUrl);
        socket = new WebSocket(wsUrl);

        socket.onopen = function() {
            console.log('WebSocket connected');
        };

        socket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                console.log('WebSocket update received', data);

                // Validate period matches current view to prevent overwriting with default data
                // Use the dataset period which is the source of truth for this page render
                const expectedPeriod = dataElement.dataset.period || 'week';
                
                if (data.period && data.period !== expectedPeriod) {
                    console.warn(`Ignoring update for period '${data.period}' (expected '${expectedPeriod}')`);
                    return;
                }
                
                // Update Charts
                updateOrdersChart(data.lineChart);
                updateTopProductsChart(data.topProducts);
                updateRevenueChart(data.categoryRevenue);
                updateMultiPieChart(data.multiSeriesPie);

                updateMetrics(data.kpis);
            } catch (err) {
                console.error('Error processing WebSocket message:', err);
            }
        };

        socket.onclose = function(e) {
            console.error('WebSocket closed unexpectedly. Reconnecting in 5s...');
            setTimeout(connectWebSocket, 5000);
        };
        
        socket.onerror = function(err) {
            console.error('WebSocket error:', err);
            socket.close();
        };
    }

    // Start WebSocket connection
    connectWebSocket();

    // Fallback Polling (optional, can be removed if WS is reliable)
    // setInterval(fetchDashboardData, 30000);

});
