/**
 * ResourceLayer - Renders emergency resource placements and coverage areas.
 */
const ResourceLayer = {
    addResourcePlacements(placements) {
        if (!map || !placements || placements.length === 0) return;

        this.removeResources();

        const markerFeatures = placements.map((p, i) => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
            properties: {
                id: p.id,
                resource_type: p.resource_type,
                buildings_covered: p.buildings_covered,
                index: i,
            },
        }));

        map.addSource('resource-markers', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: markerFeatures },
        });

        map.addLayer({
            id: 'resource-markers',
            type: 'circle',
            source: 'resource-markers',
            paint: {
                'circle-radius': 10,
                'circle-color': '#22c55e',
                'circle-stroke-width': 3,
                'circle-stroke-color': '#ffffff',
                'circle-opacity': 0.9,
            },
        });

        const radiusFeatures = placements.map(p => {
            const radiusDeg = (p.coverage_radius_m || 1500) / 111320;
            const coords = [];
            for (let angle = 0; angle <= 360; angle += 10) {
                const rad = (angle * Math.PI) / 180;
                coords.push([
                    p.lon + radiusDeg * Math.cos(rad) / Math.cos(p.lat * Math.PI / 180),
                    p.lat + radiusDeg * Math.sin(rad),
                ]);
            }
            coords.push(coords[0]);
            return {
                type: 'Feature',
                geometry: { type: 'Polygon', coordinates: [coords] },
                properties: { id: p.id },
            };
        });

        map.addSource('resource-radius', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: radiusFeatures },
        });

        map.addLayer({
            id: 'resource-radius',
            type: 'fill',
            source: 'resource-radius',
            paint: {
                'fill-color': 'rgba(34, 197, 94, 0.15)',
                'fill-outline-color': 'rgba(34, 197, 94, 0.5)',
            },
        });

        map.on('click', 'resource-markers', (e) => {
            if (e.features.length > 0) {
                const props = e.features[0].properties;
                const icon = props.resource_type === 'boat' ? '🚤' : '🚑';
                new mapboxgl.Popup({ className: 'dark-popup' })
                    .setLngLat(e.lngLat)
                    .setHTML(`
                        <div class="popup-title">${icon} ${props.resource_type}</div>
                        <div class="popup-row"><span>ID</span><span>${props.id}</span></div>
                        <div class="popup-row"><span>Buildings Covered</span><span>${props.buildings_covered}</span></div>
                    `)
                    .addTo(map);
            }
        });
    },

    removeResources() {
        ['resource-markers', 'resource-radius'].forEach(id => {
            if (map.getLayer(id)) map.removeLayer(id);
            if (map.getSource(id)) map.removeSource(id);
        });
    },

    setVisibility(visible) {
        ['resource-markers', 'resource-radius'].forEach(id => {
            if (map.getLayer(id)) {
                map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none');
            }
        });
    },

    addFacilityMarkers(facilities) {
        if (!map || !facilities) return;

        if (map.getLayer('facility-markers')) {
            map.removeLayer('facility-markers');
            map.removeSource('facility-markers');
        }

        const features = (facilities.features || []).map(f => ({
            ...f,
            properties: {
                ...f.properties,
                icon_text: f.properties.type === 'hospital' ? '🏥' :
                           f.properties.type === 'fire_station' ? '🚒' : '🛡️',
                isolated: f.properties.isolated || false,
            },
        }));

        map.addSource('facility-markers', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features },
        });

        map.addLayer({
            id: 'facility-markers',
            type: 'circle',
            source: 'facility-markers',
            paint: {
                'circle-radius': 8,
                'circle-color': [
                    'match', ['get', 'type'],
                    'hospital', '#ef4444',
                    'fire_station', '#f97316',
                    'shelter', '#3b82f6',
                    '#94a3b8',
                ],
                'circle-stroke-width': [
                    'case', ['get', 'isolated'], 3, 2,
                ],
                'circle-stroke-color': [
                    'case', ['get', 'isolated'], '#ef4444', '#ffffff',
                ],
            },
        });
    },
};
