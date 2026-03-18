/**
 * HeatmapLayer - Renders a risk heatmap overlay on the map.
 */
const HeatmapLayer = {
    addRiskHeatmap(riskScores) {
        if (!map || !riskScores || riskScores.length === 0) return;

        this.removeHeatmap();

        const features = riskScores
            .filter(b => b.lat && b.lon && b.risk_score > 0)
            .map(b => ({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [b.lon, b.lat] },
                properties: { risk_score: b.risk_score || 0, weight: (b.risk_score || 0) / 100 },
            }));

        map.addSource('risk-heatmap', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features },
        });

        map.addLayer({
            id: 'risk-heatmap',
            type: 'heatmap',
            source: 'risk-heatmap',
            paint: {
                'heatmap-weight': ['get', 'weight'],
                'heatmap-intensity': 1.5,
                'heatmap-radius': 30,
                'heatmap-color': [
                    'interpolate', ['linear'], ['heatmap-density'],
                    0, 'rgba(0,0,0,0)',
                    0.2, 'rgba(34,197,94,0.4)',
                    0.4, 'rgba(234,179,8,0.5)',
                    0.6, 'rgba(249,115,22,0.6)',
                    0.8, 'rgba(239,68,68,0.7)',
                    1.0, 'rgba(239,68,68,0.9)',
                ],
                'heatmap-opacity': 0.7,
            },
            layout: {
                visibility: 'none',
            },
        });
    },

    removeHeatmap() {
        if (map.getLayer('risk-heatmap')) {
            map.removeLayer('risk-heatmap');
            map.removeSource('risk-heatmap');
        }
    },

    setVisibility(visible) {
        if (map.getLayer('risk-heatmap')) {
            map.setLayoutProperty('risk-heatmap', 'visibility', visible ? 'visible' : 'none');
        }
    },
};
