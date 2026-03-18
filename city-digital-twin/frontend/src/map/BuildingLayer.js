/**
 * BuildingLayer - Renders building damage with 3D extrusion.
 */
const DAMAGE_COLORS = {
    none: '#22c55e',
    slight: '#84cc16',
    moderate: '#eab308',
    extensive: '#f97316',
    complete: '#ef4444',
};

const BuildingLayer = {
    addBuildingDamage(buildingDamage, buildingsGeoJSON) {
        if (!map || !buildingDamage) return;

        if (map.getLayer('building-damage-3d')) {
            map.removeLayer('building-damage-3d');
            map.removeSource('building-damage');
        }

        const damageMap = {};
        buildingDamage.forEach(b => { damageMap[b.id] = b; });

        const features = (buildingsGeoJSON?.features || []).map(f => {
            const id = f.properties.id;
            const damage = damageMap[id] || {};
            return {
                ...f,
                properties: {
                    ...f.properties,
                    damage_state: damage.damage_state || 'none',
                    flood_depth: damage.flood_depth || 0,
                    pga_g: damage.pga_g || 0,
                    risk_score: damage.risk_score || 0,
                    damage_color: DAMAGE_COLORS[damage.damage_state || 'none'],
                },
            };
        });

        const geojson = { type: 'FeatureCollection', features };

        map.addSource('building-damage', { type: 'geojson', data: geojson });

        map.addLayer({
            id: 'building-damage-3d',
            type: 'fill-extrusion',
            source: 'building-damage',
            paint: {
                'fill-extrusion-color': [
                    'match',
                    ['get', 'damage_state'],
                    'none', '#22c55e',
                    'slight', '#84cc16',
                    'moderate', '#eab308',
                    'extensive', '#f97316',
                    'complete', '#ef4444',
                    '#22c55e',
                ],
                'fill-extrusion-height': ['*', ['get', 'floors'], 3],
                'fill-extrusion-base': 0,
                'fill-extrusion-opacity': 0.85,
            },
        });

        map.on('click', 'building-damage-3d', (e) => {
            if (e.features.length > 0) {
                const props = e.features[0].properties;
                const damage = damageMap[props.id];
                RiskCard.showBuildingPopup(e.lngLat, props, damage);
            }
        });

        map.on('mouseenter', 'building-damage-3d', () => {
            map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', 'building-damage-3d', () => {
            map.getCanvas().style.cursor = '';
        });
    },

    setVisibility(visible) {
        if (map.getLayer('building-damage-3d')) {
            map.setLayoutProperty('building-damage-3d', 'visibility', visible ? 'visible' : 'none');
        }
    },
};
