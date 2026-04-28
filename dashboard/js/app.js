/**
 * Main Application Logic
 * Handles company list rendering, user interactions, and state management
 */

class StockDashboard {
    constructor() {
        this.companies = [];
        this.selectedSymbol = null;
        this.currentFilter = 30; // Default to 30 days
        
        // DOM elements
        this.companyListEl = document.getElementById('company-list');
        this.loadingCompaniesEl = document.getElementById('loading-companies');
        this.errorCompaniesEl = document.getElementById('error-companies');
        this.welcomeEl = document.getElementById('welcome-message');
        this.chartContainerEl = document.getElementById('chart-container');
        
        // Initialize
        this.init();
    }

    /**
     * Initialize the dashboard
     */
    async init() {
        try {
            await this.loadCompanies();
            this.setupEventListeners();
        } catch (error) {
            this.showError('Failed to initialize dashboard', error);
        }
    }

    /**
     * Load companies from API
     */
    async loadCompanies() {
        try {
            this.loadingCompaniesEl.style.display = 'block';
            this.errorCompaniesEl.style.display = 'none';
            
            this.companies = await apiClient.getCompanies();
            
            // Sort companies alphabetically by symbol
            this.companies.sort((a, b) => a.symbol.localeCompare(b.symbol));
            
            this.loadingCompaniesEl.style.display = 'none';
            
            if (this.companies.length === 0) {
                this.showCompaniesError('No companies available in the database');
            } else {
                this.renderCompanyList();
            }
        } catch (error) {
            this.loadingCompaniesEl.style.display = 'none';
            this.showCompaniesError('Failed to load companies. Please try again later.');
            console.error('Error loading companies:', error);
        }
    }

    /**
     * Render the company list
     */
    renderCompanyList() {
        this.companyListEl.innerHTML = '';
        
        this.companies.forEach(company => {
            const li = document.createElement('li');
            li.dataset.symbol = company.symbol;
            li.innerHTML = `
                <span class="company-symbol">${company.symbol}</span>
                <span class="company-name">${company.name}</span>
            `;
            
            li.addEventListener('click', () => this.selectCompany(company.symbol));
            this.companyListEl.appendChild(li);
        });
    }

    /**
     * Select a company and load its data
     * @param {string} symbol - Stock symbol
     */
    async selectCompany(symbol) {
        // Update UI to show selected company
        const allItems = this.companyListEl.querySelectorAll('li');
        allItems.forEach(item => item.classList.remove('active'));
        
        const selectedItem = this.companyListEl.querySelector(`[data-symbol="${symbol}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        this.selectedSymbol = symbol;
        
        // Hide welcome message and show chart container
        this.welcomeEl.style.display = 'none';
        this.chartContainerEl.style.display = 'block';
        
        // Load stock data and summary
        await this.loadStockData(symbol);
    }

    /**
     * Load stock data for selected symbol
     * @param {string} symbol - Stock symbol
     */
    async loadStockData(symbol) {
        try {
            // Show loading state
            const loadingEl = document.getElementById('loading-chart');
            const errorEl = document.getElementById('error-chart');
            loadingEl.style.display = 'block';
            errorEl.style.display = 'none';
            
            // Fetch data in parallel
            const [stockData, summary] = await Promise.all([
                apiClient.getStockData(symbol, this.currentFilter),
                apiClient.getSummary(symbol)
            ]);
            
            loadingEl.style.display = 'none';
            
            // Filter data based on current filter
            const filteredData = this.filterDataByDays(stockData, this.currentFilter);
            
            // Update chart
            const company = this.companies.find(c => c.symbol === symbol);
            chartManager.updateChart(filteredData, company);
            
            // Update summary
            this.updateSummary(summary);
            
        } catch (error) {
            document.getElementById('loading-chart').style.display = 'none';
            this.showChartError('Failed to load stock data. Please try again.');
            console.error('Error loading stock data:', error);
        }
    }

    /**
     * Filter stock data by number of days
     * @param {Array} data - Stock data array
     * @param {number} days - Number of days to include
     * @returns {Array} - Filtered data
     */
    filterDataByDays(data, days) {
        // Data is already sorted by date descending from API
        return data.slice(0, days);
    }

    /**
     * Update summary statistics display
     * @param {object} summary - Summary data from API
     */
    updateSummary(summary) {
        document.getElementById('summary-high').textContent = 
            summary.week_52_high ? `₹${summary.week_52_high.toFixed(2)}` : '-';
        document.getElementById('summary-low').textContent = 
            summary.week_52_low ? `₹${summary.week_52_low.toFixed(2)}` : '-';
        document.getElementById('summary-avg').textContent = 
            summary.avg_close ? `₹${summary.avg_close.toFixed(2)}` : '-';
    }

    /**
     * Setup event listeners for filter buttons
     */
    setupEventListeners() {
        const filter30Btn = document.getElementById('filter-30');
        const filter90Btn = document.getElementById('filter-90');
        
        filter30Btn.addEventListener('click', () => this.changeFilter(30, filter30Btn));
        filter90Btn.addEventListener('click', () => this.changeFilter(90, filter90Btn));
    }

    /**
     * Change time period filter
     * @param {number} days - Number of days
     * @param {HTMLElement} buttonEl - Button element that was clicked
     */
    async changeFilter(days, buttonEl) {
        // Update active button state
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        buttonEl.classList.add('active');
        
        this.currentFilter = days;
        
        // Reload data if a company is selected
        if (this.selectedSymbol) {
            await this.loadStockData(this.selectedSymbol);
        }
    }

    /**
     * Show error message for companies section
     * @param {string} message - Error message
     */
    showCompaniesError(message) {
        this.errorCompaniesEl.textContent = message;
        this.errorCompaniesEl.style.display = 'block';
    }

    /**
     * Show error message for chart section
     * @param {string} message - Error message
     */
    showChartError(message) {
        const errorEl = document.getElementById('error-chart');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }

    /**
     * Generic error handler
     * @param {string} context - Error context
     * @param {Error} error - Error object
     */
    showError(context, error) {
        console.error(`${context}:`, error);
        alert(`${context}: ${error.message}`);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new StockDashboard();
});
