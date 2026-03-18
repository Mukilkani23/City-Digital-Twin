/**
 * API Client - Handles all communication with the backend.
 */
const API_BASE = window.location.origin;

const ApiClient = {
    async request(method, path, body = null) {
        const url = `${API_BASE}${path}`;
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail?.message || errorData.message || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error [${method} ${path}]:`, error);
            throw error;
        }
    },

    async getHealth() {
        return this.request('GET', '/health');
    },

    async getCityInfrastructure(cityName) {
        return this.request('GET', `/api/v1/city/${cityName}/infrastructure`);
    },

    async getCityRiskBaseline(cityName) {
        return this.request('GET', `/api/v1/city/${cityName}/risk-baseline`);
    },

    async simulateFlood(params) {
        return this.request('POST', '/api/v1/simulate/flood', params);
    },

    async simulateBathtubFlood(params) {
        return this.request('POST', '/api/v1/simulate/flood/bathtub', params);
    },

    async simulateEarthquake(params) {
        return this.request('POST', '/api/v1/simulate/earthquake', params);
    },

    async optimizeResources(params) {
        return this.request('POST', '/api/v1/optimize/resources', params);
    },

    async listCities() {
        return this.request('GET', '/api/v1/city/list');
    },

    async saveScenario(scenario) {
        return this.request('POST', '/api/v1/scenarios/save', scenario);
    },

    async compareScenarios(params) {
        return this.request('POST', '/api/v1/scenarios/compare', params);
    },
};
