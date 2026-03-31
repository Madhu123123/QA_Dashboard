/**
 * API Client for QA Test Runner Dashboard
 * Handles all communication with the backend API
 */

class APIClient {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
    this.timeout = 30000;
  }

  /**
   * Make API request
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const defaultOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: this.timeout
    };

    const config = { ...defaultOptions, ...options };
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeout);

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ===============================================
  // DASHBOARD ENDPOINTS
  // ===============================================

  async getDashboardStats() {
    return this.request('/api/dashboard/stats');
  }

  // ===============================================
  // TEST RUN ENDPOINTS
  // ===============================================

  async getAllRuns(page = 1, perPage = 10) {
    return this.request(`/api/runs?page=${page}&per_page=${perPage}`);
  }

  async getRun(runId) {
    return this.request(`/api/runs/${runId}`);
  }

  async startTestRun(config) {
    return this.request('/api/runs', {
      method: 'POST',
      body: JSON.stringify(config)
    });
  }

  async getRunStatus(runId) {
    return this.request(`/api/runs/${runId}/status`);
  }

  async stopRun(runId) {
    return this.request(`/api/runs/${runId}/stop`, {
      method: 'POST'
    });
  }

  // ===============================================
  // TEST CASE ENDPOINTS
  // ===============================================

  async getTestCases(runId) {
    return this.request(`/api/runs/${runId}/test-cases`);
  }

  async retryTestCase(testId) {
    return this.request(`/api/test-cases/${testId}/retry`, {
      method: 'POST'
    });
  }

  // ===============================================
  // REPORT ENDPOINTS
  // ===============================================

  async exportHtmlReport(runId) {
    const url = `${this.baseURL}/api/reports/${runId}/html`;
    window.location.href = url;
  }

  async exportCsvReport(runId) {
    const url = `${this.baseURL}/api/reports/${runId}/csv`;
    window.location.href = url;
  }

  // ===============================================
  // CONFIGURATION ENDPOINTS
  // ===============================================

  async getModules() {
    return this.request('/api/config/modules');
  }

  async getEnvironments() {
    return this.request('/api/config/environments');
  }

  async getBrowsers() {
    return this.request('/api/config/browsers');
  }

  async getRunTypes() {
    return this.request('/api/config/run-types');
  }

  // ===============================================
  // HEALTH CHECK
  // ===============================================

  async healthCheck() {
    return this.request('/api/health');
  }
}

// Global API client instance
const api = new APIClient();
