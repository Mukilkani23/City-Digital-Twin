/**
 * FloodLayer - Renders flood zone polygons on the map.
 */
const FloodLayer = {
    addFloodZones(floodGeoJSON) {
        if (!map || !floodGeoJSON) return;

        if (map.getLayer('flood-zones')) {
            map.removeLayer('flood-zones');
            map.removeLayer('flood-zones-outline');
            map.removeSource('flood-zones');
        }

        map.addSource('flood-zones', {
            type: 'geojson',
            data: floodGeoJSON,
        });

        map.addLayer({
            id: 'flood-zones',
            type: 'fill',
            source: 'flood-zones',
            paint: {
                'fill-color': [
                    'match',
                    ['get', 'depth_category'],
                    'shallow', 'rgba(135, 206, 250, 0.4)',
                    'moderate', 'rgba(65, 105, 225, 0.5)',
                    'deep', 'rgba(25, 25, 112, 0.6)',
                    'very_deep', 'rgba(10, 10, 60, 0.75)',
                    'rgba(100, 149, 237, 0.3)'
                ],
                'fill-opacity': 0,
            },
        });

        map.addLayer({
            id: 'flood-zones-outline',
            type: 'line',
            source: 'flood-zones',
            paint: {
                'line-color': 'rgba(59, 130, 246, 0.3)',
                'line-width': 0.5,
            },
        });

        let opacity = 0;
        const fadeIn = () => {
            opacity += 0.05;
            if (opacity <= 0.8) {
                map.setPaintProperty('flood-zones', 'fill-opacity', opacity * 0.8);
                requestAnimationFrame(fadeIn);
            }
        };
        fadeIn();
    },

    removeFloodZones() {
        if (map.getLayer('flood-zones')) {
            map.removeLayer('flood-zones');
            map.removeLayer('flood-zones-outline');
            map.removeSource('flood-zones');
        }
    },

    setVisibility(visible) {
        if (map.getLayer('flood-zones')) {
            map.setLayoutProperty('flood-zones', 'visibility', visible ? 'visible' : 'none');
            map.setLayoutProperty('flood-zones-outline', 'visibility', visible ? 'visible' : 'none');
        }
    },
};
