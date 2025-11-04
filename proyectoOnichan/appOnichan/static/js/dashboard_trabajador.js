(function () {
  function parseData(id) {
    const element = document.getElementById(id);
    if (!element) {
      return null;
    }
    try {
      return JSON.parse(element.textContent);
    } catch (error) {
      console.error('No se pudo parsear', id, error);
      return null;
    }
  }

  function formatearNumero(valor) {
    return Number(valor || 0).toLocaleString('es-CL');
  }

  function formatearMoneda(valor) {
    return '$' + Number(valor || 0).toLocaleString('es-CL');
  }

  function inicializarGraficos() {
    if (typeof Chart === 'undefined') {
      return;
    }

    const labels = parseData('labels-meses');
    const clientes = parseData('clientes-por-mes');
    const ventas = parseData('ventas-por-mes');
    const porcentajes = parseData('porcentaje-comision');
    const comisiones = parseData('comision-por-mes');

    if (!labels || !clientes || !ventas || !comisiones) {
      return;
    }

    const ctxClientes = document.getElementById('graficoClientes');
    if (ctxClientes) {
      new Chart(ctxClientes, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Clientes atendidos',
              data: clientes,
              borderColor: '#0d6efd',
              backgroundColor: 'rgba(13, 110, 253, 0.15)',
              borderWidth: 2,
              tension: 0.3,
              fill: true,
              pointRadius: 4,
              pointBackgroundColor: '#0d6efd',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: (value) => formatearNumero(value),
              },
            },
          },
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: (context) => `${context.dataset.label}: ${formatearNumero(context.parsed.y)}`,
              },
            },
          },
        },
      });
    }

    const ctxVentas = document.getElementById('graficoVentas');
    if (ctxVentas) {
      new Chart(ctxVentas, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: 'Ventas',
              data: ventas,
              backgroundColor: 'rgba(25, 135, 84, 0.25)',
              borderColor: '#198754',
              borderWidth: 1,
              stack: 'ventas',
            },
            {
              label: 'Comisión',
              data: comisiones,
              backgroundColor: 'rgba(255, 193, 7, 0.6)',
              borderColor: '#ffc107',
              borderWidth: 1,
              stack: 'ventas',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: true,
            },
            y: {
              stacked: true,
              beginAtZero: true,
              ticks: {
                callback: (value) => formatearMoneda(value),
              },
            },
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (context) => {
                  const etiqueta = context.dataset.label || '';
                  const valor = formatearMoneda(context.parsed.y);
                  if (context.dataset.label === 'Comisión' && Array.isArray(porcentajes)) {
                    const porcentaje = Number(porcentajes[context.dataIndex] || 0) * 100;
                    return `${etiqueta}: ${valor} (${porcentaje.toFixed(1)}%)`;
                  }
                  return `${etiqueta}: ${valor}`;
                },
              },
            },
          },
        },
      });
    }
  }

  function inicializarCalendario() {
    const contenedor = document.getElementById('calendarioTurnos');
    const eventos = parseData('eventos-turnos') || [];

    if (!contenedor) {
      return;
    }

    const fechaReferencia = contenedor.dataset.fechaReferencia || '';
    const baseDate = fechaReferencia ? new Date(fechaReferencia) : new Date();
    const year = baseDate.getFullYear();
    const month = baseDate.getMonth();

    const eventosPorDia = eventos.reduce((acc, evento) => {
      if (!evento || !evento.start) {
        return acc;
      }
      const fecha = evento.start.split('T')[0];
      if (!acc[fecha]) {
        acc[fecha] = [];
      }
      acc[fecha].push(evento);
      return acc;
    }, {});

    const nombresDias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
    const tabla = document.createElement('table');
    tabla.className = 'table table-sm calendario-tabla';

    const thead = document.createElement('thead');
    const filaCabecera = document.createElement('tr');
    nombresDias.forEach((nombre) => {
      const th = document.createElement('th');
      th.textContent = nombre;
      filaCabecera.appendChild(th);
    });
    thead.appendChild(filaCabecera);
    tabla.appendChild(thead);

    const tbody = document.createElement('tbody');
    const primerDiaMes = new Date(year, month, 1);
    const desplazamiento = (primerDiaMes.getDay() + 6) % 7;
    const fechaCursor = new Date(year, month, 1);
    fechaCursor.setDate(fechaCursor.getDate() - desplazamiento);

    for (let semana = 0; semana < 6; semana += 1) {
      const fila = document.createElement('tr');
      for (let dia = 0; dia < 7; dia += 1) {
        const celda = document.createElement('td');
        if (fechaCursor.getMonth() !== month) {
          celda.classList.add('mes-otro');
        }
        const fechaISO = fechaCursor.toISOString().split('T')[0];

        const numero = document.createElement('span');
        numero.className = 'dia-numero';
        numero.textContent = String(fechaCursor.getDate());
        celda.appendChild(numero);

        const eventosDia = eventosPorDia[fechaISO] || [];
        eventosDia.forEach((evento) => {
          const etiqueta = document.createElement('span');
          const tipo = evento.tipo || 'trabajo';
          etiqueta.className = `etiqueta-turno etiqueta-${tipo}`;
          etiqueta.textContent = tipo.charAt(0).toUpperCase() + tipo.slice(1);

          const horaInicio = evento.start?.split('T')[1]?.slice(0, 5) || '';
          const horaFin = evento.end?.split('T')[1]?.slice(0, 5) || '';
          let detalleTexto = '';
          if (tipo === 'libre') {
            detalleTexto = 'Día completo';
          } else if (horaInicio && horaFin) {
            detalleTexto = `${horaInicio} - ${horaFin}`;
          }

          const contenedorEtiqueta = document.createElement('div');
          contenedorEtiqueta.className = 'mb-2';
          contenedorEtiqueta.appendChild(etiqueta);
          if (detalleTexto) {
            const textoDetalle = document.createElement('div');
            textoDetalle.className = 'small text-muted mt-1';
            textoDetalle.textContent = detalleTexto;
            contenedorEtiqueta.appendChild(textoDetalle);
          }
          celda.appendChild(contenedorEtiqueta);
        });

        fila.appendChild(celda);
        fechaCursor.setDate(fechaCursor.getDate() + 1);
      }
      tbody.appendChild(fila);
    }

    tabla.appendChild(tbody);
    contenedor.innerHTML = '';
    contenedor.appendChild(tabla);
  }

  document.addEventListener('DOMContentLoaded', function () {
    inicializarGraficos();
    inicializarCalendario();
  });
})();
