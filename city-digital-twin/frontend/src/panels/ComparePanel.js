/**
 * ComparePanel - Handles scenario comparison display.
 */
const ComparePanel = {
    visible: false,
    scenarioA: null,
    scenarioB: null,

    toggle() {
        this.visible = !this.visible;
        const panel = document.getElementById('comparePanel');
        panel.style.display = this.visible ? 'flex' : 'none';
    },

    setScenarioA(result) {
        this.scenarioA = result;
        this.updateDisplay();
    },

    setScenarioB(result) {
        this.scenarioB = result;
        this.updateDisplay();
    },

    updateDisplay() {
        const content = document.getElementById('compareContent');
        if (!this.scenarioA) {
            content.innerHTML = '<p class="compare-placeholder">Run a simulation first, then compare with a different scenario.</p>';
            return;
        }

        let html = this.renderScenarioColumn('Current Scenario', this.scenarioA);

        if (this.scenarioB) {
            html += this.renderScenarioColumn('Alternate Scenario', this.scenarioB);
            html += this.renderDifferences();
        } else {
            html += '<p class="compare-placeholder">Run a second simulation to compare.</p>';
        }

        content.innerHTML = html;
    },

    renderScenarioColumn(title, data) {
        const stats = data.statistics || {};
        const damage = data.damage_summary || {};
        return `
            <div class="compare-column">
                <h4>${title}</h4>
                <div class="compare-stat-row"><span class="label">Affected Area</span><span class="value">${(stats.affected_area_km2 || 0).toFixed(2)} km²</span></div>
                <div class="compare-stat-row"><span class="label">Buildings at Risk</span><span class="value">${stats.buildings_at_risk || stats.buildings_damaged || 0}</span></div>
                <div class="compare-stat-row"><span class="label">Roads Blocked</span><span class="value">${(stats.roads_blocked_pct || 0).toFixed(1)}%</span></div>
                <div class="compare-stat-row"><span class="label">None</span><span class="value">${damage.none || 0}</span></div>
                <div class="compare-stat-row"><span class="label">Slight</span><span class="value">${damage.slight || 0}</span></div>
                <div class="compare-stat-row"><span class="label">Moderate</span><span class="value">${damage.moderate || 0}</span></div>
                <div class="compare-stat-row"><span class="label">Extensive</span><span class="value">${damage.extensive || 0}</span></div>
                <div class="compare-stat-row"><span class="label">Complete</span><span class="value">${damage.complete || 0}</span></div>
            </div>
        `;
    },

    renderDifferences() {
        if (!this.scenarioA || !this.scenarioB) return '';
        const sa = this.scenarioA.statistics || {};
        const sb = this.scenarioB.statistics || {};

        const diffs = [
            { label: 'Affected Area', a: sa.affected_area_km2 || 0, b: sb.affected_area_km2 || 0, unit: 'km²' },
            { label: 'Buildings at Risk', a: sa.buildings_at_risk || 0, b: sb.buildings_at_risk || 0, unit: '' },
            { label: 'Roads Blocked', a: sa.roads_blocked_pct || 0, b: sb.roads_blocked_pct || 0, unit: '%' },
        ];

        let html = '<div class="compare-column"><h4>Differences</h4>';
        diffs.forEach(d => {
            const diff = d.b - d.a;
            const cls = diff > 0 ? 'change-positive' : 'change-negative';
            const sign = diff > 0 ? '+' : '';
            html += `<div class="compare-stat-row">
                <span class="label">${d.label}</span>
                <span class="${cls}">${sign}${diff.toFixed(1)}${d.unit}</span>
            </div>`;
        });
        html += '</div>';
        return html;
    },
};
