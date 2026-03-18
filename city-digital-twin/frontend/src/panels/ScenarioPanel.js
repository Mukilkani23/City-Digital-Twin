/**
 * ScenarioPanel - Controls scenario configuration UI.
 */
const ScenarioPanel = {
    currentTab: 'flood',
    floodMode: 'rainfall',

    switchTab(tab) {
        this.currentTab = tab;
        const floodControls = document.getElementById('floodControls');
        const earthquakeControls = document.getElementById('earthquakeControls');
        const tabFlood = document.getElementById('tabFlood');
        const tabEarthquake = document.getElementById('tabEarthquake');

        if (tab === 'flood') {
            floodControls.style.display = 'block';
            earthquakeControls.style.display = 'none';
            tabFlood.className = 'tab-btn active';
            tabEarthquake.className = 'tab-btn';
        } else {
            floodControls.style.display = 'none';
            earthquakeControls.style.display = 'block';
            tabFlood.className = 'tab-btn';
            tabEarthquake.className = 'tab-btn active-eq active';
        }
    },

    setFloodMode(mode) {
        this.floodMode = mode;
        const rainfallControls = document.getElementById('rainfallControls');
        const waterLevelControls = document.getElementById('waterLevelControls');
        const modeRainfall = document.getElementById('modeRainfall');
        const modeWaterLevel = document.getElementById('modeWaterLevel');

        if (mode === 'rainfall') {
            rainfallControls.style.display = 'block';
            waterLevelControls.style.display = 'none';
            modeRainfall.className = 'mode-btn active';
            modeWaterLevel.className = 'mode-btn';
        } else {
            rainfallControls.style.display = 'none';
            waterLevelControls.style.display = 'block';
            modeRainfall.className = 'mode-btn';
            modeWaterLevel.className = 'mode-btn active';
        }
    },

    getFloodParams() {
        return {
            city_name: document.getElementById('citySelect').value,
            rainfall_mm: parseFloat(document.getElementById('rainfallSlider').value),
            duration_hours: parseFloat(document.getElementById('durationSlider').value),
            curve_number: parseFloat(document.getElementById('curveSlider').value),
        };
    },

    getBathtubParams() {
        return {
            city_name: document.getElementById('citySelect').value,
            water_level_m: parseFloat(document.getElementById('waterLevelSlider').value),
        };
    },

    getEarthquakeParams() {
        const params = {
            city_name: document.getElementById('citySelect').value,
            magnitude: parseFloat(document.getElementById('magnitudeSlider').value),
            depth_km: parseFloat(document.getElementById('depthSlider').value),
        };
        if (epicenterCoords) {
            params.epicenter_lat = epicenterCoords.lat;
            params.epicenter_lon = epicenterCoords.lon;
        }
        return params;
    },
};
