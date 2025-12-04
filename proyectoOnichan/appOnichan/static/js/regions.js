/**
 * Inicializa selectores de región y comuna.
 * @param {string} jsonUrl - URL para obtener el JSON de regiones.
 * @param {string} userRegion - Región guardada del usuario (opcional).
 * @param {string} userCommune - Comuna guardada del usuario (opcional).
 */
function initRegionSelector(jsonUrl, userRegion, userCommune) {
    const regionSelect = document.getElementById('regionSelect');
    const communeSelect = document.getElementById('communeSelect');
    
    if (!regionSelect || !communeSelect) return;

    let regionsData = [];
    let initialLoad = true;

    // Obtiene JSON de regiones
    fetch(jsonUrl)
        .then(response => response.json())
        .then(data => {
            regionsData = data;

            regionsData.forEach(region => {
                const option = document.createElement('option');
                option.value = region.nombre_region;
                option.textContent = region.nombre_region;
                if (userRegion && region.nombre_region === userRegion) {
                    option.selected = true;
                }
                regionSelect.appendChild(option);
            });
            
            // Dispara cambio si hay región preseleccionada
            if (userRegion) {
                regionSelect.dispatchEvent(new Event('change'));
            }
            initialLoad = false;
        })
        .catch(error => console.error('Error al cargar regiones:', error));

    // Maneja cambio de región
    regionSelect.addEventListener('change', function() {
        const selectedRegionName = this.value;
        communeSelect.innerHTML = '<option value="">Seleccione Comuna...</option>';
        communeSelect.disabled = true;

        if (selectedRegionName) {
            const region = regionsData.find(r => r.nombre_region === selectedRegionName);
            if (region && region.provincias) {
                const comunas = [];
                region.provincias.forEach(provincia => {
                    if (provincia.comunas) {
                        provincia.comunas.forEach(comuna => {
                            comunas.push(comuna.nombre_comuna);
                        });
                    }
                });
                
                // Ordena alfabéticamente
                comunas.sort();

                comunas.forEach(comunaName => {
                    const option = document.createElement('option');
                    option.value = comunaName;
                    option.textContent = comunaName;
                    // Preselecciona comuna solo en carga inicial
                    if (initialLoad && userCommune && comunaName === userCommune) {
                        option.selected = true;
                    }
                    communeSelect.appendChild(option);
                });
                communeSelect.disabled = false;
            }
        }
    });
}
