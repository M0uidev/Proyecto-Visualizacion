/**
 * Initializes the region and commune selectors.
 * @param {string} jsonUrl - The URL to fetch the regions JSON from.
 * @param {string} userRegion - The user's saved region (optional).
 * @param {string} userCommune - The user's saved commune (optional).
 */
function initRegionSelector(jsonUrl, userRegion, userCommune) {
    const regionSelect = document.getElementById('regionSelect');
    const communeSelect = document.getElementById('communeSelect');
    
    if (!regionSelect || !communeSelect) return;

    let regionsData = [];
    let initialLoad = true;

    // Fetch regions JSON
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
            
            // Trigger change if we have a pre-selected region
            if (userRegion) {
                regionSelect.dispatchEvent(new Event('change'));
            }
            initialLoad = false;
        })
        .catch(error => console.error('Error loading regions:', error));

    // Handle region change
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
                
                // Sort alphabetically
                comunas.sort();

                comunas.forEach(comunaName => {
                    const option = document.createElement('option');
                    option.value = comunaName;
                    option.textContent = comunaName;
                    // Pre-select commune only on initial load
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
