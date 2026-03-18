/**
 * StatsPanel - Manages the statistics display and damage chart.
 */
let damageChart = null;

const StatsPanel = {
    show(stats, damageSummary) {
        const section = document.getElementById('resultsSection');
        section.style.display = 'block';

        this.animateCounter('statArea', stats.affected_area_km2 || 0, 1);
        this.animateCounter('statBuildings', stats.buildings_at_risk || stats.buildings_damaged || 0, 0);
        this.animateCounter('statRoads', stats.roads_blocked_pct || 0, 1);
        this.animateCounter('statHospitals', stats.hospitals_isolated || 0, 0);

        this.updateDamageChart(damageSummary);
    },

    animateCounter(elementId, targetValue, decimals) {
        const el = document.getElementById(elementId);
        if (!el) return;

        const duration = 1200;
        const startTime = performance.now();
        const startValue = 0;

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (targetValue - startValue) * eased;
            el.textContent = decimals > 0 ? currentValue.toFixed(decimals) : Math.round(currentValue);
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };
        requestAnimationFrame(update);
    },

    updateDamageChart(damageSummary) {
        if (!damageSummary) return;

        const ctx = document.getElementById('damageChart');
        if (!ctx) return;

        if (damageChart) {
            damageChart.destroy();
        }

        damageChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['None', 'Slight', 'Moderate', 'Extensive', 'Complete'],
                datasets: [{
                    data: [
                        damageSummary.none || 0,
                        damageSummary.slight || 0,
                        damageSummary.moderate || 0,
                        damageSummary.extensive || 0,
                        damageSummary.complete || 0,
                    ],
                    backgroundColor: [
                        '#22c55e', '#84cc16', '#eab308', '#f97316', '#ef4444',
                    ],
                    borderColor: '#1e293b',
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            font: { family: 'Inter', size: 11 },
                            padding: 12,
                            usePointStyle: true,
                            pointStyleWidth: 10,
                        },
                    },
                },
                animation: { animateScale: true, duration: 800 },
            },
        });
    },

    hide() {
        document.getElementById('resultsSection').style.display = 'none';
    },
};
