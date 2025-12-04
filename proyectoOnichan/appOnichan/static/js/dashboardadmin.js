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
        chart: {
            style: {
                fontFamily: 'inherit',
                fontSize: '14px'
            }
        },
        exporting: {
            enabled: false
        },
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
        colors: ['#4f46e5', '#22c55e', '#f97316', '#0ea5e9', '#ec4899', '#f59e0b', '#8b5cf6', '#a01d8eff'],
        tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e5e7eb',
            borderRadius: 8,
            borderWidth: 1,
            shadow: {
                opacity: 0.15
            },
            style: {
                fontSize: '15px',
                color: '#1f2937',
                padding: '12px'
            },
            headerFormat: '<span style="font-size: 16px; font-weight: bold; color: #111827">{point.key}</span><br/>',
            useHTML: true
        },
        xAxis: {
            labels: {
                style: {
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: '#333333'
                }
            },
            title: {
                style: {
                    fontSize: '15px',
                    fontWeight: 'bold',
                    color: '#333333'
                }
            }
        },
        yAxis: {
            labels: {
                style: {
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: '#333333'
                }
            },
            title: {
                style: {
                    fontSize: '15px',
                    fontWeight: 'bold',
                    color: '#333333'
                }
            }
        },
        legend: {
            itemStyle: {
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#333333'
            }
        }
    });

    // Chart Instances
    let ordersChart, topProductsChart, revenueChart, salesTreemapChart, modalChart;
    let retentionChart, frequencyChart, ticketChart, topCustomersChart, dayOfWeekChart;
    let currentTopProductsData = initialData.topProducts;

    // Render Functions
    function createRetentionChart(data) {
        if (!data) return;
        if (!document.getElementById('retentionChart')) return;
        
        // Map data to include details
        const newData = data.new.map((val, i) => ({
            y: val,
            customDetails: data.newDetails ? data.newDetails[i] : []
        }));
        
        const returningData = data.returning.map((val, i) => ({
            y: val,
            customDetails: data.returningDetails ? data.returningDetails[i] : []
        }));

        retentionChart = Highcharts.chart('retentionChart', {
            chart: { type: 'column' },
            title: { text: null },
            xAxis: { categories: data.labels },
            yAxis: { 
                allowDecimals: false,
                min: 0,
                title: { text: 'Clientes' }, 
                stackLabels: { enabled: true } 
            },
            tooltip: {
                format: '<b>{key}</b><br/>{series.name}: {y}<br/>Total: {point.stackTotal}'
            },
            plotOptions: {
                column: {
                    stacking: 'normal',
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function () {
                                const details = this.customDetails;
                                const category = this.category;
                                const seriesName = this.series.name;
                                
                                if (details && details.length > 0) {
                                    // Use existing openModal but adapt it for list display
                                    // We can pass type='list' (custom handling) or just pass dummy values
                                    // Let's use a custom type 'list' and handle it in openModal
                                    openModal({
                                        title: `Clientes ${seriesName} - ${category}`,
                                        labels: details, // Pass names as labels
                                        values: details.map(() => 1), // Dummy values
                                        datasetLabel: 'Cliente',
                                        type: 'list', // Custom type
                                        isCurrency: false
                                    });
                                }
                            }
                        }
                    }
                }
            },
            series: [{
                name: 'Nuevos',
                data: newData,
                color: '#22c55e'
            }, {
                name: 'Recurrentes',
                data: returningData,
                color: '#4f46e5'
            }]
        });
    }

    function updateRetentionChart(data) {
        if (!data) return;
        if (!retentionChart) { createRetentionChart(data); return; }
        
        const newData = data.new.map((val, i) => ({
            y: val,
            customDetails: data.newDetails ? data.newDetails[i] : []
        }));
        
        const returningData = data.returning.map((val, i) => ({
            y: val,
            customDetails: data.returningDetails ? data.returningDetails[i] : []
        }));

        retentionChart.xAxis[0].setCategories(data.labels, false);
        retentionChart.series[0].setData(newData, false);
        retentionChart.series[1].setData(returningData, true);
    }

    function createFrequencyChart(data) {
        if (!data) return;
        if (!document.getElementById('frequencyChart')) return;
        frequencyChart = Highcharts.chart('frequencyChart', {
            chart: { type: 'column' },
            title: { text: null },
            xAxis: { categories: data.labels, title: { text: 'Pedidos realizados' } },
            yAxis: { title: { text: 'Cantidad de Clientes' } },
            series: [{
                name: 'Clientes',
                data: data.values,
                color: '#f59e0b'
            }]
        });
    }

    function updateFrequencyChart(data) {
        if (!data) return;
        if (!frequencyChart) { createFrequencyChart(data); return; }
        frequencyChart.xAxis[0].setCategories(data.labels, false);
        frequencyChart.series[0].setData(data.values, true);
    }

    function createTicketChart(data) {
        if (!data) return;
        if (!document.getElementById('ticketChart')) return;
        const seriesData = data.labels.map((l, i) => ({ 
            name: l, 
            y: data.values[i],
            customDetails: data.details ? data.details[i] : []
        }));
        ticketChart = Highcharts.chart('ticketChart', {
            chart: {
                type: 'pie',
                zooming: { type: 'xy' },
                panning: { enabled: true, type: 'xy' },
                panKey: 'shift'
            },
            title: { text: null },
            tooltip: { 
                pointFormat: '<b>{point.name}</b>: {point.y} pedidos' 
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    showInLegend: true,
                    dataLabels: {
                        enabled: false
                    },
                    point: {
                        events: {
                            click: function () {
                                const details = this.customDetails;
                                const label = this.name;
                                
                                if (details && details.length > 0) {
                                    openModal({
                                        title: `Pedidos en rango ${label}`,
                                        labels: details,
                                        values: [],
                                        datasetLabel: 'Pedidos',
                                        type: 'list'
                                    });
                                }
                            }
                        }
                    }
                }
            },
            series: [{
                name: 'Pedidos',
                colorByPoint: true,
                data: seriesData
            }]
        });
    }

    function updateTicketChart(data) {
        if (!data) return;
        if (!ticketChart) { createTicketChart(data); return; }
        const seriesData = data.labels.map((l, i) => ({ 
            name: l, 
            y: data.values[i],
            customDetails: data.details ? data.details[i] : []
        }));
        ticketChart.series[0].setData(seriesData, true);
    }

    function createTopCustomersChart(data) {
        if (!data) return;
        if (!document.getElementById('topCustomersChart')) return;
        topCustomersChart = Highcharts.chart('topCustomersChart', {
            chart: { type: 'bar' },
            title: { text: null },
            xAxis: { categories: data.labels },
            yAxis: { title: { text: 'Total Gastado' } },
            tooltip: { valuePrefix: '$' },
            series: [{
                name: 'Gasto Total',
                data: data.values,
                color: '#8b5cf6'
            }]
        });
    }

    function updateTopCustomersChart(data) {
        if (!data) return;
        if (!topCustomersChart) { createTopCustomersChart(data); return; }
        topCustomersChart.xAxis[0].setCategories(data.labels, false);
        topCustomersChart.series[0].setData(data.values, true);
    }

    function createDayOfWeekChart(data) {
        if (!data) return;
        if (!document.getElementById('dayOfWeekChart')) return;
        dayOfWeekChart = Highcharts.chart('dayOfWeekChart', {
            chart: { type: 'column' },
            title: { text: null },
            xAxis: { categories: data.labels },
            yAxis: { title: { text: 'Pedidos' } },
            series: [{
                name: 'Pedidos',
                data: data.values,
                color: '#ec4899'
            }]
        });
    }

    function updateDayOfWeekChart(data) {
        if (!data) return;
        if (!dayOfWeekChart) { createDayOfWeekChart(data); return; }
        dayOfWeekChart.xAxis[0].setCategories(data.labels, false);
        dayOfWeekChart.series[0].setData(data.values, true);
    }

    function createOrdersChart(lineData) {
        if (!lineData) return;
        if (!document.getElementById('ordersLineChart')) return;
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
                                        title: `Estados de Pedidos (${label})`,
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
        if (!document.getElementById('topProductsPieChart')) return;
        console.log('Creating Top Products Chart');
        currentTopProductsData = pieData;
        
        const limit = 10;

        // Slice data based on limit
        const labels = pieData.labels.slice(0, limit);
        const values = pieData.values.slice(0, limit);
        const revenues = pieData.revenues ? pieData.revenues.slice(0, limit) : values;

        // Calculate total for Z (percentage of displayed items)
        const totalUnits = values.reduce((a, b) => a + b, 0);

        const seriesData = labels.map((label, i) => ({
            name: label,
            y: values[i],
            z: totalUnits > 0 ? (values[i] / totalUnits) : 0,
            revenue: revenues[i]
        }));

        topProductsChart = Highcharts.chart('topProductsPieChart', {
            chart: {
                type: 'variablepie'
            },
            title: {
                text: null
            },
            tooltip: {
                headerFormat: '',
                pointFormat: '<span style="color:{point.color}">\u25CF</span> <b> {point.name}</b><br/>' +
                    'Unidades: <b>{point.y}</b><br/>' +
                    'Ingresos: <b>${point.revenue:,.0f}</b><br/>' +
                    'Porcentaje: <b>{point.percentage:.1f}%</b><br/>'
            },
            plotOptions: {
                variablepie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: { enabled: false },
                    showInLegend: false,
                    point: {
                        events: {
                            click: function (event) {
                                const label = this.name;
                                const detail = this.series.chart.customDetalles?.[label];
                                
                                // Prevent default slicing behavior initially
                                event.preventDefault(); 

                                if (detail) {
                                    // Check if product has sizes (more than just "Único" or empty)
                                    const keys = Object.keys(detail);
                                    if (keys.length === 1 && (keys[0] === 'Único' || keys[0] === '')) {
                                        return; // Do nothing if no sizes
                                    }

                                    // Manually slice the point since we prevented default
                                    this.slice(true);

                                    openModal({
                                        title: `Tallas de ${label}`,
                                        labels: Object.keys(detail),
                                        values: Object.values(detail),
                                        datasetLabel: 'Unidades',
                                        type: 'variablepie'
                                    });
                                }
                            }
                        }
                    }
                }
            },
            series: [{
                minPointSize: '10%',
                maxPointSize: '100%',
                innerSize: '20%',
                zMin: 0,
                name: 'Productos',
                borderRadius: 5,
                data: seriesData,
                colors: Highcharts.getOptions().colors
            }]
        });
        topProductsChart.customDetalles = pieData.detalles;
        
        // Custom Legend (if needed, but Highcharts has built-in legend)
        const legendContainer = document.getElementById('topProductsLegend');
        if (legendContainer) legendContainer.innerHTML = ''; 
    }

    function updateTopProductsChart(pieData) {
        if (!pieData) return;
        currentTopProductsData = pieData;
        
        if (!topProductsChart) {
            createTopProductsChart(pieData);
            return;
        }
        console.log('Updating Top Products Chart');
        
        const limit = 10;

        // Slice data based on limit
        const labels = pieData.labels.slice(0, limit);
        const values = pieData.values.slice(0, limit);
        const revenues = pieData.revenues ? pieData.revenues.slice(0, limit) : values;

        // Calculate total for Z (percentage of displayed items)
        const totalUnits = values.reduce((a, b) => a + b, 0);

        const seriesData = labels.map((label, i) => ({
            name: label,
            y: values[i],
            z: totalUnits > 0 ? (values[i] / totalUnits) : 0,
            revenue: revenues[i]
        }));
        
        topProductsChart.customDetalles = pieData.detalles;
        topProductsChart.series[0].setData(seriesData, true);
    }

    function createRevenueChart(barData) {
        if (!barData) return;
        if (!document.getElementById('categoryRevenueBarChart')) return;
        console.log('Creating Revenue Chart');
        
        // Map data to include names explicitly
        const seriesData = barData.labels.map((label, i) => ({
            name: label,
            y: barData.values[i]
        }));

        revenueChart = Highcharts.chart('categoryRevenueBarChart', {
            chart: { type: 'column' },
            title: { text: null },
            xAxis: { 
                type: 'category',
                categories: barData.labels 
            },
            yAxis: {
                title: { text: 'Productos Vendidos' },
                labels: {
                    formatter: function () { return this.value; }
                }
            },
            tooltip: {
                formatter: function () {
                    return `<b>${this.key}</b><br/>${this.series.name}: ${this.y}`;
                }
            },
            plotOptions: {
                column: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function () {
                                const label = this.name; // Now we can use this.name safely
                                const detail = this.series.chart.customDetalles?.[label];
                                if (detail) {
                                    openModal({
                                        title: `Productos en ${label}`,
                                        labels: Object.keys(detail),
                                        values: Object.values(detail),
                                        datasetLabel: 'Unidades',
                                        type: 'pie',
                                        isCurrency: false,
                                        detalles: this.series.chart.customSubDetalles
                                    });
                                }
                            }
                        }
                    }
                }
            },
            series: [{
                name: 'Productos Vendidos',
                data: seriesData,
                colorByPoint: true
            }]
        });
        revenueChart.customDetalles = barData.detalles;
        revenueChart.customSubDetalles = barData.subDetalles;
    }

    function updateRevenueChart(barData) {
        if (!barData) return;
        if (!revenueChart) {
            createRevenueChart(barData);
            return;
        }
        console.log('Updating Revenue Chart');
        
        const seriesData = barData.labels.map((label, i) => ({
            name: label,
            y: barData.values[i]
        }));

        revenueChart.customDetalles = barData.detalles;
        revenueChart.customSubDetalles = barData.subDetalles;
        revenueChart.xAxis[0].setCategories(barData.labels, false);
        revenueChart.series[0].setData(seriesData, true);
    }

    function createSalesTreemap(data) {
        if (!data) return;
        if (!document.getElementById('salesTreemapChart')) return;
        console.log('Creating Sales Treemap');
        
        // Separate categories (roots) and products (children)
        const categories = data.filter(d => !d.parent);
        const products = data.filter(d => d.parent);

        salesTreemapChart = Highcharts.chart('salesTreemapChart', {
            series: [{
                type: 'treemap',
                layoutAlgorithm: 'squarified',
                data: categories, // Only show categories initially
                colorByPoint: true,
                dataLabels: {
                    enabled: true,
                    style: {
                        fontSize: '15px',
                        fontWeight: 'bold'
                    }
                },
                tooltip: {
                    pointFormat: '<b>{point.name}</b>:<br>Ventas: {point.value:,.0f}'
                },
                events: {
                    click: function(event) {
                        const point = event.point;
                        // Find products for this category
                        const catProducts = products.filter(p => p.parent === point.id);
                        
                        if (catProducts.length > 0) {
                            openModal({
                                type: 'treemap',
                                title: `Productos en ${point.name}`,
                                data: catProducts,
                                datasetLabel: 'Ventas'
                            });
                        }
                    }
                }
            }],
            title: { text: null }
        });
        
        // Store full data for updates
        salesTreemapChart.fullData = data;
    }

    function updateSalesTreemap(data) {
        if (!data) return;
        if (!salesTreemapChart) {
            createSalesTreemap(data);
            return;
        }
        console.log('Updating Sales Treemap');
        
        const categories = data.filter(d => !d.parent);
        salesTreemapChart.series[0].setData(categories, true);
        salesTreemapChart.fullData = data;
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
            // Reset Modal Chart slicing (if it was a pie chart that opened another level)
            if (modalChart && modalChart.series && modalChart.series[0]) {
                modalChart.series[0].points.forEach(p => {
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
            modalChart = null;
        }

        // Clear modal body content (in case we added a list previously)
        const container = document.getElementById('dashModalChart');
        container.innerHTML = '';

        if (config.type === 'list') {
            // Render a simple list instead of a chart
            const ul = document.createElement('ul');
            ul.className = 'list-group list-group-flush';
            
            if (config.labels && config.labels.length > 0) {
                config.labels.forEach(label => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.textContent = label;
                    ul.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.className = 'list-group-item text-muted';
                li.textContent = 'No hay datos disponibles.';
                ul.appendChild(li);
            }
            container.appendChild(ul);
            bootstrapModal.show();
            return;
        }

        if (config.type === 'treemap') {
            modalChart = Highcharts.chart('dashModalChart', {
                series: [{
                    type: 'treemap',
                    layoutAlgorithm: 'squarified',
                    data: config.data,
                    colorByPoint: true,
                    dataLabels: {
                        enabled: true
                    },
                    tooltip: {
                        pointFormat: '<b>{point.name}</b>:<br>Ventas: {point.value:,.0f}'
                    }
                }],
                title: { text: null }
            });
            bootstrapModal.show();
            return;
        }

        // Render new chart
        let seriesData;
        if (config.type === 'variablepie') {
             const total = config.values.reduce((a, b) => a + b, 0);
             seriesData = config.labels.map((l, i) => ({
                name: l,
                y: config.values[i],
                z: total > 0 ? config.values[i] / total : 0
            }));
        } else {
            seriesData = config.labels.map((l, i) => ({
                name: l,
                y: config.values[i]
            }));
        }

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
            plotOptions: {
                column: {
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.y}</b>',
                        style: { textOutline: 'none' }
                    }
                },
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.y}'
                    },
                    point: {
                        events: {
                            click: function(event) {
                                // Check if we have next level details (Level 3: Channels)
                                const prodName = this.name;
                                const channels = config.detalles?.[prodName];
                                
                                event.preventDefault();

                                if (channels) {
                                    this.slice(true);
                                    // Open modal again (update it) with Channel data
                                    openModal({
                                        title: `Canales de venta: ${prodName}`,
                                        labels: Object.keys(channels),
                                        values: Object.values(channels),
                                        datasetLabel: 'Unidades',
                                        type: 'pie',
                                        isCurrency: false,
                                        detalles: null // No more levels
                                    });
                                }
                            }
                        }
                    }
                },
                variablepie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.y}'
                    }
                }
            },
            series: [{
                minPointSize: '10%',
                maxPointSize: '100%',
                zMin: 0,
                name: config.datasetLabel,
                data: seriesData,
                colorByPoint: true
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
        createSalesTreemap(initialData.treemapData);

        if (initialData.customerBehavior) {
            createRetentionChart(initialData.customerBehavior.newVsReturning);
            createFrequencyChart(initialData.customerBehavior.frequency);
            createTicketChart(initialData.customerBehavior.ticket);
            createTopCustomersChart(initialData.customerBehavior.topCustomers);
            createDayOfWeekChart(initialData.customerBehavior.dayOfWeek);
        }
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
                updateSalesTreemap(data.treemapData);

                if (data.customerBehavior) {
                    updateRetentionChart(data.customerBehavior.newVsReturning);
                    updateFrequencyChart(data.customerBehavior.frequency);
                    updateTicketChart(data.customerBehavior.ticket);
                    updateTopCustomersChart(data.customerBehavior.topCustomers);
                    updateDayOfWeekChart(data.customerBehavior.dayOfWeek);
                }
                
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
            // Ensure we are using the correct base URL for API calls
            // If href already contains the full path or starts with ?, handle accordingly
            let url;
            if (href.startsWith('?')) {
                url = `${apiDashboardUrl}${href}`;
            } else {
                // If href is a full URL or absolute path, use it directly (though typically it's just query params)
                url = href;
            }
            fetchDashboardData(url);
        }
    }

    if (btnPrev) btnPrev.addEventListener('click', handleNavClick);
    if (btnNext) btnNext.addEventListener('click', handleNavClick);

    // Handle Browser Back/Forward Buttons
    window.addEventListener('popstate', function() {
        const url = `${apiDashboardUrl}${window.location.search}`;
        fetchDashboardData(url, false);
    });

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
                updateSalesTreemap(data.treemapData);

                if (data.customerBehavior) {
                    updateRetentionChart(data.customerBehavior.newVsReturning);
                    updateFrequencyChart(data.customerBehavior.frequency);
                    updateTicketChart(data.customerBehavior.ticket);
                    updateTopCustomersChart(data.customerBehavior.topCustomers);
                    updateDayOfWeekChart(data.customerBehavior.dayOfWeek);
                }

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
