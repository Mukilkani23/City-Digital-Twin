/**
 * TimelinePanel - Displays simulation event timeline.
 */
const TimelinePanel = {
    events: [],

    addEvent(text, active = true) {
        this.events.push({
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            text,
            active,
        });
        this.render();
    },

    clear() {
        this.events = [];
        this.render();
    },

    render() {
        const container = document.getElementById('timelineContainer');
        if (!container) return;

        if (this.events.length === 0) {
            container.innerHTML = '<p style="color:var(--text-muted);font-size:12px;">No simulation events yet.</p>';
            return;
        }

        container.innerHTML = this.events.map(e =>
            `<div class="timeline-entry ${e.active ? 'active' : ''}">
                <span class="timeline-time">${e.time}</span>
                <span class="timeline-text">${e.text}</span>
            </div>`
        ).join('');
    },

    addSimulationStart(type) {
        this.clear();
        this.addEvent(`${type} simulation started`);
    },

    addDataLoaded(cityName) {
        this.addEvent(`City data loaded for ${cityName}`);
    },

    addSimulationComplete(type, stats) {
        const buildings = stats.buildings_at_risk || stats.buildings_damaged || 0;
        this.addEvent(`${type} simulation complete: ${buildings} buildings affected`);
    },

    addResourceOptimization(coverage) {
        this.addEvent(`Resource optimization: ${coverage}% coverage achieved`);
    },
};
