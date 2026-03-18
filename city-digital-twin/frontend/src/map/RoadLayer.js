/**
 * RoadLayer - Renders passable and blocked roads on the map.
 */
const RoadLayer = {
    addRoads(roadDamage, roadsGeoJSON) {
        if (!map) return;

        this.removeRoads();

        const passableFeatures = [];
        const blockedFeatures = [];

        if (roadDamage && roadDamage.length > 0) {
            roadDamage.forEach(road => {
                const feature = {
                    type: 'Feature',
                    geometry: road.geometry,
                    properties: {
                        id: road.id,
                        name: road.name,
                        blocked: road.blocked,
                        flood_depth: road.flood_depth || 0,
                    },
                };
                if (road.blocked) {
                    blockedFeatures.push(feature);
                } else {
                    passableFeatures.push(feature);
                }
            });
        } else if (roadsGeoJSON) {
            roadsGeoJSON.features.forEach(f => {
                passableFeatures.push(f);
            });
        }

        if (passableFeatures.length > 0) {
            map.addSource('road-passable', {
                type: 'geojson',
                data: { type: 'FeatureCollection', features: passableFeatures },
            });
            map.addLayer({
                id: 'road-passable',
                type: 'line',
                source: 'road-passable',
                paint: {
                    'line-color': 'rgba(255, 255, 255, 0.4)',
                    'line-width': 1.5,
                },
            });
        }

        if (blockedFeatures.length > 0) {
            map.addSource('road-blocked', {
                type: 'geojson',
                data: { type: 'FeatureCollection', features: blockedFeatures },
            });
            map.addLayer({
                id: 'road-blocked',
                type: 'line',
                source: 'road-blocked',
                paint: {
                    'line-color': '#ef4444',
                    'line-width': 2.5,
                    'line-dasharray': [3, 2],
                },
            });
        }
    },

    removeRoads() {
        ['road-passable', 'road-blocked'].forEach(id => {
            if (map.getLayer(id)) map.removeLayer(id);
            if (map.getSource(id)) map.removeSource(id);
        });
    },

    setVisibility(visible) {
        ['road-passable', 'road-blocked'].forEach(id => {
            if (map.getLayer(id)) {
                map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none');
            }
        });
    },
};
