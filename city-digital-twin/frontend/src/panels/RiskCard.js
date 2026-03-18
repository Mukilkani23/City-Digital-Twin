/**
 * RiskCard - Displays building risk information in map popups.
 */
const RiskCard = {
    showBuildingPopup(lngLat, properties, damageData) {
        const riskScore = damageData?.risk_score || properties.risk_score || 0;
        const riskLevel = this.getRiskLevel(riskScore);
        const riskColor = this.getRiskColor(riskScore);

        const factors = damageData?.risk_factors || [];
        const factorsHtml = factors.map(f =>
            `<div class="risk-factor">
                <span class="risk-factor-dot ${f.impact}"></span>
                <span>${f.factor}</span>
            </div>`
        ).join('');

        const html = `
            <div class="popup-title">🏢 ${properties.building_type || 'Building'}</div>
            <div class="popup-row"><span>ID</span><span>${properties.id || 'N/A'}</span></div>
            <div class="popup-row"><span>Year Built</span><span>${properties.construction_year || 'N/A'}</span></div>
            <div class="popup-row"><span>Floors</span><span>${properties.floors || 'N/A'}</span></div>
            <div class="popup-row"><span>Material</span><span>${properties.material || 'N/A'}</span></div>
            <div class="popup-row"><span>Flood Depth</span><span>${(damageData?.flood_depth || 0).toFixed(2)}m</span></div>
            <div class="popup-row"><span>Damage State</span><span style="color:${DAMAGE_COLORS[damageData?.damage_state || 'none']}">${(damageData?.damage_state || 'none').toUpperCase()}</span></div>
            ${damageData?.pga_g ? `<div class="popup-row"><span>PGA</span><span>${damageData.pga_g.toFixed(4)}g</span></div>` : ''}
            <div class="popup-row"><span>AI Risk Score</span><span style="color:${riskColor};font-weight:800">${riskScore}/100</span></div>
            <div class="popup-risk-bar">
                <div class="popup-risk-fill" style="width:${riskScore}%;background:linear-gradient(90deg,#22c55e,#eab308,#f97316,#ef4444);"></div>
            </div>
            ${factorsHtml ? '<div style="margin-top:8px;font-size:11px;color:#94a3b8">Risk Factors:</div>' + factorsHtml : ''}
        `;

        new mapboxgl.Popup({ maxWidth: '280px' })
            .setLngLat(lngLat)
            .setHTML(html)
            .addTo(map);
    },

    getRiskLevel(score) {
        if (score < 20) return 'low';
        if (score < 40) return 'moderate';
        if (score < 60) return 'high';
        if (score < 80) return 'very_high';
        return 'critical';
    },

    getRiskColor(score) {
        if (score < 20) return '#22c55e';
        if (score < 40) return '#eab308';
        if (score < 60) return '#f97316';
        return '#ef4444';
    },
};
