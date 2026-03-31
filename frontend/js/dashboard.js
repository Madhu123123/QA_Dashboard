/**
 * QA Test Runner Dashboard - Main Application Script
 * Handles UI interactions and API integration
 */

class Dashboard {
  constructor() {
    this.selectedRunType = 'functionality';
    this.selectedBrowsers = ['Chrome', 'Firefox'];
    this.activeRun = null;
    this.statusUpdateInterval = null;
    this.init();
  }

  async init() {
    console.log('Initializing Dashboard...');

    try {
      // Check API health
      await api.healthCheck();
      console.log('API connection established');

      // Load configuration
      await this.loadConfiguration();

      // Load initial data
      await this.loadDashboardStats();
      await this.loadRuns();

      // Setup event listeners
      this.setupEventListeners();

      // Show success message
      this.showAlert('Dashboard loaded successfully', 'success');
    } catch (error) {
      console.error('Failed to initialize dashboard:', error);
      this.showAlert('Failed to connect to backend API', 'error');
    }
  }

  // ===============================================
  // CONFIGURATION LOADING
  // ===============================================

  async loadConfiguration() {
    try {
      const [runTypes, modules, envs, browsers] = await Promise.all([
        api.getRunTypes(),
        api.getModules(),
        api.getEnvironments(),
        api.getBrowsers()
      ]);

      // Populate run type cards
      this.populateRunTypes(runTypes.run_types);

      // Populate module select
      const moduleSelect = document.querySelector('select')[0]; // First select
      if (moduleSelect) {
        modules.modules.forEach(module => {
          const option = document.createElement('option');
          option.value = module;
          option.textContent = module;
          moduleSelect.appendChild(option);
        });
      }

      // Populate environment select
      const envSelect = document.querySelector('.env-sel');
      if (envSelect) {
        envs.environments.forEach(env => {
          const option = document.createElement('option');
          option.value = env;
          option.textContent = env;
          const icon = this.getEnvIcon(env);
          option.textContent = `${icon} ${env}`;
          envSelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error('Error loading configuration:', error);
    }
  }

  getEnvIcon(env) {
    const icons = {
      'Staging': '🔵',
      'Production': '🟢',
      'QA': '🟠',
      'Local': '⚪'
    };
    return icons[env] || '🔵';
  }

  populateRunTypes(runTypes) {
    const runGrid = document.querySelector('.run-grid');
    if (!runGrid) return;

    runGrid.innerHTML = '';

    runTypes.forEach(runType => {
      const card = document.createElement('div');
      card.className = 'run-card';
      if (runType.id === this.selectedRunType) card.classList.add('selected');

      card.innerHTML = `
        <div class="rc-icon">${runType.icon}</div>
        <div class="rc-title">${runType.title}</div>
        <div class="rc-desc">${runType.description}</div>
      `;

      card.addEventListener('click', () => this.selectRunType(card, runType.id));
      runGrid.appendChild(card);
    });
  }

  selectRunType(element, typeId) {
    document.querySelectorAll('.run-card').forEach(c => c.classList.remove('selected'));
    element.classList.add('selected');
    this.selectedRunType = typeId;
  }

  // ===============================================
  // DASHBOARD STATS
  // ===============================================

  async loadDashboardStats() {
    try {
      const stats = await api.getDashboardStats();

      // Update metric displays
      const metrics = document.querySelectorAll('.metric');
      if (metrics.length >= 4) {
        metrics[0].querySelector('.metric-val').textContent = stats.total_tests;
        metrics[1].querySelector('.metric-val').textContent = stats.total_passed;
        metrics[2].querySelector('.metric-val').textContent = stats.total_failed;

        metrics[1].querySelector('.metric-val').classList.add('green');
        metrics[2].querySelector('.metric-val').classList.add('red');

        const trendTwo = metrics[1].querySelector('.metric-trend');
        if (trendTwo) trendTwo.textContent = stats.pass_rate;
      }
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  }

  // ===============================================
  // TEST RUNS
  // ===============================================

  async loadRuns() {
    try {
      const data = await api.getAllRuns();
      this.populateReports(data.runs);
    } catch (error) {
      console.error('Error loading runs:', error);
      this.showAlert('Error loading test runs', 'error');
    }
  }

  populateReports(runs) {
    const reportContainer = document.querySelector('.report-row')?.parentElement;
    if (!reportContainer) return;

    // Clear existing rows (keep header)
    const rows = reportContainer.querySelectorAll('.report-row');
    rows.forEach(row => row.remove());

    // Add new rows
    runs.forEach(run => {
      const row = document.createElement('div');
      row.className = 'report-row';
      row.innerHTML = `
        <div class="report-name">${run.run_type} — ${run.environment}</div>
        <div class="report-date">${this.formatDate(run.started_at)}</div>
        <div class="cnt-pass">${run.passed_tests}</div>
        <div class="cnt-fail">${run.failed_tests}</div>
        <div class="cnt-time">${run.duration_seconds ? this.formatDuration(run.duration_seconds) : '—'}</div>
        <div class="row-btns">
          <button class="icon-btn" onclick="dashboard.viewRun('${run.run_id}')">View</button>
          <button class="icon-btn" onclick="dashboard.exportReport('${run.run_id}', 'html')">↓</button>
        </div>
      `;
      reportContainer.appendChild(row);
    });
  }

  async startTestRun() {
    try {
      const config = this.getRunConfig();

      // Validate config
      if (!config.browsers || config.browsers.length === 0) {
        this.showAlert('Please select at least one browser', 'error');
        return;
      }

      const runBtn = document.querySelector('.btn-green');
      runBtn.disabled = true;
      runBtn.textContent = '▶ Starting...';

      const response = await api.startTestRun(config);

      this.activeRun = response.run_id;
      this.showAlert(`Test run started: ${response.run_id}`, 'success');

      // Start polling for status
      this.startStatusPolling(response.run_id);

      // Reload runs after completion
      setTimeout(() => this.loadRuns(), 5000);

      runBtn.disabled = false;
      runBtn.textContent = '▶ Run now';
    } catch (error) {
      console.error('Error starting test run:', error);
      this.showAlert('Failed to start test run', 'error');

      const runBtn = document.querySelector('.btn-green');
      runBtn.disabled = false;
      runBtn.textContent = '▶ Run now';
    }
  }

  getRunConfig() {
    const moduleSelect = document.querySelector('select');
    const envSelect = document.querySelector('.env-sel');

    return {
      run_type: this.selectedRunType,
      module: moduleSelect?.value || 'All modules',
      environment: envSelect?.value?.split(' ').pop() || 'Staging',
      execution_mode: document.querySelectorAll('select')[1]?.value || 'Parallel',
      browsers: this.selectedBrowsers,
      max_retries: parseInt(document.querySelectorAll('select')[3]?.value || '0')
    };
  }

  startStatusPolling(runId) {
    if (this.statusUpdateInterval) {
      clearInterval(this.statusUpdateInterval);
    }

    this.statusUpdateInterval = setInterval(() => {
      this.updateRunStatus(runId);
    }, 2000); // Poll every 2 seconds
  }

  async updateRunStatus(runId) {
    try {
      const status = await api.getRunStatus(runId);

      // Update live status table
      this.updateLiveStatusTable(status);

      // Stop polling if run is completed
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(this.statusUpdateInterval);
        this.showAlert(`Test run ${status.status}`, status.status === 'completed' ? 'success' : 'error');
        this.loadRuns();
      }
    } catch (error) {
      console.error('Error updating run status:', error);
    }
  }

  updateLiveStatusTable(status) {
    // This would update the live status table rows
    const table = document.querySelector('.status-table tbody');
    if (!table) return;

    const progress = status.progress;
    const percentage = progress.percentage || 0;

    // Update progress information (you can enhance this to show individual test statuses)
    const runningTag = document.querySelector('.tag.running');
    if (runningTag) {
      runningTag.textContent = `▶ ${progress.completed} completed`;
    }
  }

  async viewRun(runId) {
    try {
      const data = await api.getRun(runId);
      console.log('Run details:', data);
      // You can implement a modal to show detailed test results here
      this.showAlert(`Viewing run: ${runId}`, 'info');
    } catch (error) {
      this.showAlert('Error loading run details', 'error');
    }
  }

  async exportReport(runId, format) {
    try {
      if (format === 'html') {
        await api.exportHtmlReport(runId);
      } else if (format === 'csv') {
        await api.exportCsvReport(runId);
      }
      this.showAlert(`Report exported as ${format.toUpperCase()}`, 'success');
    } catch (error) {
      this.showAlert('Error exporting report', 'error');
    }
  }

  // ===============================================
  // BROWSER SELECTION
  // ===============================================

  toggleBrowserChip(element) {
    const browserName = element.textContent.trim().split(' ')[1];

    element.classList.toggle('on');

    if (element.classList.contains('on')) {
      if (!this.selectedBrowsers.includes(browserName)) {
        this.selectedBrowsers.push(browserName);
      }
    } else {
      this.selectedBrowsers = this.selectedBrowsers.filter(b => b !== browserName);
    }

    console.log('Selected browsers:', this.selectedBrowsers);
  }

  // ===============================================
  // UI UTILITIES
  // ===============================================

  showAlert(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);

    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.textContent = message;

    const content = document.querySelector('.content');
    content?.insertBefore(alert, content.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return `Today ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      const daysAgo = Math.floor((today - date) / (1000 * 60 * 60 * 24));
      return `${daysAgo} days ago`;
    }
  }

  formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m`;
  }

  // ===============================================
  // EVENT LISTENERS
  // ===============================================

  setupEventListeners() {
    // Run now button
    const runNowBtn = document.querySelector('.btn-green');
    if (runNowBtn) {
      runNowBtn.addEventListener('click', () => this.startTestRun());
    }

    // Browser chips
    document.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', function() {
        dashboard.toggleBrowserChip(this);
      });
    });

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', function() {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
      });
    });

    // Stop all button
    const stopBtn = document.querySelector('.btn-red');
    if (stopBtn) {
      stopBtn.addEventListener('click', () => {
        if (this.activeRun) {
          this.stopRun(this.activeRun);
        }
      });
    }

    // Export buttons
    const panel = document.querySelector('.panel:last-child');
    if (panel) {
      const buttons = panel.querySelectorAll('.btn');
      buttons.forEach(btn => {
        if (btn.textContent.includes('Email')) {
          btn.addEventListener('click', () => this.showAlert('Email feature coming soon', 'info'));
        }
      });
    }
  }

  async stopRun(runId) {
    try {
      await api.stopRun(runId);
      clearInterval(this.statusUpdateInterval);
      this.showAlert('Test run stopped', 'success');
      this.loadRuns();
    } catch (error) {
      this.showAlert('Error stopping test run', 'error');
    }
  }
}

// Initialize dashboard when DOM is ready
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
  dashboard = new Dashboard();
});
