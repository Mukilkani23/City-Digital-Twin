/**
 * MapCore - Initializes and manages the Mapbox GL map instance.
 */
const CITY_CENTERS = {
    mumbai: { lat: 19.076, lon: 72.8777, zoom: 13 },
    chennai: { lat: 13.0827, lon: 80.2707, zoom: 13 },
    kolkata: { lat: 22.5726, lon: 88.3639, zoom: 13 },
    delhi: { lat: 28.6139, lon: 77.2090, zoom: 13 },
    jakarta: { lat: -6.2088, lon: 106.8456, zoom: 13 },
};

let map = null;
let epicenterMarker = null;
let epicenterCoords = null;

function initMap() {
    mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw';

    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [78.9629, 20.5937],
        zoom: 5,
        pitch: 0,
        bearing: 0,
        antialias: true,
    });

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');

    map.on('click', function (e) {
        if (document.getElementById('earthquakeControls').style.display !== 'none') {
            setEpicenter(e.lngLat.lat, e.lngLat.lng);
        }
    });

    map.on('load', function () {
        console.log('Map loaded successfully');
    });
}

function flyToCity(cityKey) {
    const city = CITY_CENTERS[cityKey];
    if (city && map) {
        map.flyTo({
            center: [city.lon, city.lat],
            zoom: city.zoom,
            duration: 2000,
            essential: true,
        });
    }
}

function setEpicenter(lat, lng) {
    epicenterCoords = { lat, lon: lng };

    if (epicenterMarker) {
        epicenterMarker.remove();
    }

    const el = document.createElement('div');
    el.className = 'epicenter-marker';
    el.style.cssText = `
        width: 24px; height: 24px;
        background: rgba(239,68,68,0.8);
        border: 3px solid #ef4444;
        border-radius: 50%;
        cursor: move;
        box-shadow: 0 0 20px rgba(239,68,68,0.6);
        animation: pulse 1.5s ease-in-out infinite;
    `;

    epicenterMarker = new mapboxgl.Marker({ element: el, draggable: true })
        .setLngLat([lng, lat])
        .addTo(map);

    epicenterMarker.on('dragend', function () {
        const pos = epicenterMarker.getLngLat();
        epicenterCoords = { lat: pos.lat, lon: pos.lng };
    });

    addSeismicWaveAnimation(lat, lng);
}

function addSeismicWaveAnimation(lat, lng) {
    const waveId = 'seismic-wave';
    if (map.getLayer(waveId)) {
        map.removeLayer(waveId);
        map.removeSource(waveId);
    }
    const point = { type: 'Point', coordinates: [lng, lat] };
    map.addSource(waveId, { type: 'geojson', data: point });
    map.addLayer({
        id: waveId,
        type: 'circle',
        source: waveId,
        paint: {
            'circle-radius': 0,
            'circle-color': 'transparent',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ef4444',
            'circle-opacity': 0.8,
        }
    });

    let radius = 0;
    const animate = () => {
        radius += 2;
        if (radius > 100) radius = 0;
        map.setPaintProperty(waveId, 'circle-radius', radius);
        map.setPaintProperty(waveId, 'circle-opacity', Math.max(0, 1 - radius / 100));
        if (map.getLayer(waveId)) {
            requestAnimationFrame(animate);
        }
    };
    animate();
}

function clearAllLayers() {
    const layerIds = [
        'flood-zones', 'flood-zones-outline',
        'building-damage', 'building-damage-3d',
        'road-passable', 'road-blocked',
        'risk-heatmap', 'resource-markers', 'resource-radius',
        'seismic-wave', 'facility-markers',
    ];
    layerIds.forEach(id => {
        if (map.getLayer(id)) map.removeLayer(id);
        if (map.getSource(id)) map.removeSource(id);
    });
}
