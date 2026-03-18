/**
 * Main Application Entry Point
 * Initializes the map, wires up event handlers, and manages the simulation workflow.
 */

let currentCityData = null;
let lastSimulationResult = null;
let isAnimating = false;

/* ---- Initialization ---- */
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    document.getElementById('citySelect').addEventListener('change', onCityChange);

    map.on('load', () => {
        const initialCity = document.getElementById('citySelect').value;
        loadCity(initialCity);
    });
});

/* ---- City Loading ---- */
async function loadCity(cityName) {
    showLoading('Loading city data...');
    try {
        currentCityData = await ApiClient.getCityInfrastructure(cityName);
        flyToCity(cityName);
        hideLoading();
        StatsPanel.hide();
        clearAllLayers();
        if (currentCityData.facilities) {
            ResourceLayer.addFacilityMarkers(currentCityData.facilities);
        }
    } catch (error) {
        hideLoading();
        showError('Failed to load city data: ' + error.message);
    }
}

function onCityChange() {
    const city = document.getElementById('citySelect').value;
    clearAllLayers();
    StatsPanel.hide();
    lastSimulationResult = null;
    loadCity(city);
}

/* ---- Tab & Mode Switching ---- */
function switchTab(tab) {
    ScenarioPanel.switchTab(tab);
}

function setFloodMode(mode) {
    ScenarioPanel.setFloodMode(mode);
}

/* ---- Slider Updates ---- */
function updateSliderValue(type, value) {
    switch (type) {
        case 'rainfall':
            document.getElementById('rainfallValue').textContent = value + 'mm';
            break;
        case 'duration':
            document.getElementById('durationValue').textContent = value + 'h';
            break;
        case 'curve':
            document.getElementById('curveValue').textContent = value;
            break;
        case 'waterLevel':
            document.getElementById('waterLevelValue').textContent = parseFloat(value).toFixed(1) + 'm';
            break;
        case 'magnitude':
            document.getElementById('magnitudeValue').textContent = value;
            const mag = parseFloat(value);
            const magEl = document.getElementById('magnitudeValue');
            magEl.className = 'slider-value ' + (mag < 5.5 ? 'magnitude-low' : mag < 7.0 ? 'magnitude-medium' : 'magnitude-high');
            break;
        case 'depth':
            document.getElementById('depthValue').textContent = value + 'km';
            break;
    }
}

/* ---- Flood Simulation ---- */
async function runFloodSimulation() {
    if (ScenarioPanel.floodMode === 'waterLevel') {
        return runBathtubFlood();
    }

    const params = ScenarioPanel.getFloodParams();
    showLoading('Running flood simulation...');
    TimelinePanel.addSimulationStart('Flood');

    try {
        updateLoadingMessage('Calculating surface runoff...');
        const result = await ApiClient.simulateFlood(params);
        lastSimulationResult = result;

        updateLoadingMessage('Rendering flood zones...');
        clearAllLayers();

        if (result.flood_zones) {
            FloodLayer.addFloodZones(result.flood_zones);
        }
        if (result.building_damage && currentCityData) {
            BuildingLayer.addBuildingDamage(result.building_damage, currentCityData.buildings);
        }
        if (result.road_damage) {
            RoadLayer.addRoads(result.road_damage);
        }
        if (result.risk_scores) {
            HeatmapLayer.addRiskHeatmap(result.risk_scores);
        }
        if (currentCityData?.facilities) {
            const isolated = result.isolated_facilities || [];
            const allFacilities = JSON.parse(JSON.stringify(currentCityData.facilities));
            const isolatedIds = new Set(isolated.map(f => f.properties?.name));
            allFacilities.features.forEach(f => {
                f.properties.isolated = isolatedIds.has(f.properties.name);
            });
            ResourceLayer.addFacilityMarkers(allFacilities);
        }

        StatsPanel.show(result.statistics, result.damage_summary);
        ComparePanel.setScenarioA(result);
        TimelinePanel.addSimulationComplete('Flood', result.statistics);
        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Flood simulation failed: ' + error.message);
    }
}

async function runBathtubFlood() {
    const params = ScenarioPanel.getBathtubParams();
    showLoading('Running bathtub flood...');

    try {
        const result = await ApiClient.simulateBathtubFlood(params);
        lastSimulationResult = result;
        clearAllLayers();

        if (result.flood_zones) {
            FloodLayer.addFloodZones(result.flood_zones);
        }
        if (result.building_damage && currentCityData) {
            BuildingLayer.addBuildingDamage(result.building_damage, currentCityData.buildings);
        }

        StatsPanel.show(result.statistics, result.damage_summary);
        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Bathtub simulation failed: ' + error.message);
    }
}

/* ---- Animate Water Rise ---- */
async function animateWaterRise() {
    if (isAnimating) return;
    isAnimating = true;

    const cityName = document.getElementById('citySelect').value;
    const maxLevel = 15;
    const steps = 12;

    showLoading('Animating water rise...');

    for (let i = 1; i <= steps; i++) {
        if (!isAnimating) break;
        const level = (maxLevel / steps) * i;
        updateLoadingMessage(`Water level: ${level.toFixed(1)}m`);

        try {
            const result = await ApiClient.simulateBathtubFlood({
                city_name: cityName,
                water_level_m: level,
            });
            if (result.flood_zones) {
                FloodLayer.addFloodZones(result.flood_zones);
            }
            StatsPanel.show(result.statistics, result.damage_summary);
            await new Promise(resolve => setTimeout(resolve, 300));
        } catch (e) {
            break;
        }
    }

    isAnimating = false;
    hideLoading();
}

/* ---- Earthquake Simulation ---- */
async function runEarthquakeSimulation() {
    const params = ScenarioPanel.getEarthquakeParams();
    showLoading('Running earthquake simulation...');
    TimelinePanel.addSimulationStart('Earthquake');

    try {
        updateLoadingMessage('Calculating ground acceleration...');
        const result = await ApiClient.simulateEarthquake(params);
        lastSimulationResult = result;

        updateLoadingMessage('Rendering damage...');
        clearAllLayers();

        if (result.building_damage && currentCityData) {
            BuildingLayer.addBuildingDamage(result.building_damage, currentCityData.buildings);
        }
        if (result.road_damage) {
            RoadLayer.addRoads(result.road_damage);
        }
        if (result.risk_scores) {
            HeatmapLayer.addRiskHeatmap(result.risk_scores);
        }
        if (currentCityData?.facilities) {
            const isolated = result.isolated_facilities || [];
            const allFacilities = JSON.parse(JSON.stringify(currentCityData.facilities));
            const isolatedIds = new Set(isolated.map(f => f.properties?.name));
            allFacilities.features.forEach(f => {
                f.properties.isolated = isolatedIds.has(f.properties.name);
            });
            ResourceLayer.addFacilityMarkers(allFacilities);
        }

        StatsPanel.show(result.statistics, result.damage_summary);
        ComparePanel.setScenarioA(result);
        TimelinePanel.addSimulationComplete('Earthquake', result.statistics);
        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Earthquake simulation failed: ' + error.message);
    }
}

/* ---- Resource Optimization ---- */
async function optimizeResources() {
    if (!lastSimulationResult?.building_damage) {
        showError('Run a simulation first');
        return;
    }

    showLoading('Optimizing resource placement...');

    try {
        const resourceType = ScenarioPanel.currentTab === 'flood' ? 'boat' : 'ambulance';
        const result = await ApiClient.optimizeResources({
            building_damage: lastSimulationResult.building_damage,
            num_resources: 5,
            coverage_radius_m: 1500,
            resource_type: resourceType,
        });

        if (result.placements) {
            ResourceLayer.addResourcePlacements(result.placements);
        }

        TimelinePanel.addResourceOptimization(result.coverage_percentage);
        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Resource optimization failed: ' + error.message);
    }
}

/* ---- Compare Scenarios ---- */
function toggleCompare() {
    ComparePanel.toggle();
}

/* ---- Layer Visibility ---- */
function toggleLayer(layerType) {
    const checkboxMap = {
        flood: 'toggleFloodZones',
        buildings: 'toggleBuildingDamage',
        roads: 'toggleRoadNetwork',
        heatmap: 'toggleHeatmap',
        resources: 'toggleResources',
    };

    const checkbox = document.getElementById(checkboxMap[layerType]);
    const visible = checkbox ? checkbox.checked : true;

    switch (layerType) {
        case 'flood': FloodLayer.setVisibility(visible); break;
        case 'buildings': BuildingLayer.setVisibility(visible); break;
        case 'roads': RoadLayer.setVisibility(visible); break;
        case 'heatmap': HeatmapLayer.setVisibility(visible); break;
        case 'resources': ResourceLayer.setVisibility(visible); break;
    }
}

/* ---- UI Helpers ---- */
function showLoading(message) {
    const overlay = document.getElementById('loadingOverlay');
    const msg = document.getElementById('loadingMessage');
    overlay.style.display = 'flex';
    msg.textContent = message;
}

function updateLoadingMessage(message) {
    document.getElementById('loadingMessage').textContent = message;
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showError(message) {
    console.error(message);
    const overlay = document.getElementById('loadingOverlay');
    const msg = document.getElementById('loadingMessage');
    overlay.style.display = 'flex';
    msg.textContent = '❌ ' + message;
    msg.style.color = '#ef4444';
    setTimeout(() => {
        hideLoading();
        msg.style.color = '';
    }, 3000);
}
