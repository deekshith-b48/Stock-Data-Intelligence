/**
 * Main Application Logic
 * Enhanced with search, dark mode, compare, and refresh features
 */

class StockDashboard {
    constructor() {
        this.companies = [];
        this.selectedSymbol = null;
        this.currentFilter = 30; // Default to 30 days
        this.darkMode = localStorage.getItem('darkMode') === 'true';
        
        // DOM elements
        this.companyListEl = document.getElementById('company-list');
        this.loadingCompaniesEl = document.getElementById('loading-companies');
        this.errorCompaniesEl = document.getElementById('error-companies');
        this.welcomeEl = document.getElementById('welcome-message');
        this.chartContainerEl = document.getElementById('chart-container');
        this.searchInput = document.getElementById('company-search');
        this.themeToggle = document.getElementById('theme-toggle');
        this.refreshBtn = document.getElementById('refresh-btn');
        this.compareBtn = document.getElementById('compare-btn');
        this.compareModal = document.getElementById('compare-modal');
        
        // Initialize
        this.init();
    }

    /**
     * Initialize the dashboard
     */
    async init() {
        try {
            // Apply saved theme
            if (this.darkMode) {
                document.body.classList.add('dark-mode');
                this.themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            }
            
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
            this.loadingCompaniesEl.style.display = 'flex';
            this.errorCompaniesEl.style.display = 'none';
            
            const allCompanies = await apiClient.getCompanies();
            
            // Filter companies to only show those with stock data
            // Check if each company has data by testing the data endpoint
            const companiesWithData = [];
            for (const company of allCompanies) {
                try {
                    const data = await apiClient.getStockData(company.symbol, 1);
                    if (data && data.length > 0) {
                        companiesWithData.push(company);
                    }
                } catch (error) {
                    // Skip companies without data
                    console.log(`Skipping ${company.symbol} - no data available`);
                }
            }
            
            this.companies = companiesWithData;
            
            // Sort companies alphabetically by symbol
            this.companies.sort((a, b) => a.symbol.localeCompare(b.symbol));
            
            this.loadingCompaniesEl.style.display = 'none';
            
            if (this.companies.length === 0) {
                this.showCompaniesError('No companies with stock data available');
            } else {
                this.renderCompanyList();
                // Update total companies count
                document.getElementById('total-companies').textContent = this.companies.length;
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
    renderCompanyList(filter = '') {
        this.companyListEl.innerHTML = '';
        
        const filteredCompanies = filter 
            ? this.companies.filter(c => 
                c.symbol.toLowerCase().includes(filter.toLowerCase()) ||
                c.name.toLowerCase().includes(filter.toLowerCase())
              )
            : this.companies;
        
        if (filteredCompanies.length === 0) {
            this.companyListEl.innerHTML = '<li style="text-align: center; color: var(--text-secondary);">No companies found</li>';
            return;
        }
        
        filteredCompanies.forEach(company => {
            const li = document.createElement('li');
            li.dataset.symbol = company.symbol;
            li.innerHTML = `
                <span class="company-symbol">${company.symbol}</span>
                <span class="company-name">${company.name}</span>
            `;
            
            if (this.selectedSymbol === company.symbol) {
                li.classList.add('active');
            }
            
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
            loadingEl.style.display = 'flex';
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
            
            // Update price indicator
            this.updatePriceIndicator(filteredData);
            
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
     * Update price indicator with current price and change
     * @param {Array} data - Stock data array
     */
    updatePriceIndicator(data) {
        if (!data || data.length < 2) return;
        
        const currentPrice = data[0].close;
        const previousPrice = data[1].close;
        const change = currentPrice - previousPrice;
        const changePercent = (change / previousPrice) * 100;
        
        const priceEl = document.getElementById('current-price');
        const changeEl = document.getElementById('price-change');
        
        priceEl.textContent = `₹${currentPrice.toFixed(2)}`;
        
        const changeText = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent.toFixed(2)}%)`;
        changeEl.textContent = changeText;
        changeEl.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
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
        document.getElementById('summary-volatility').textContent = 
            summary.volatility_score ? `${summary.volatility_score.toFixed(2)}%` : '-';
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Filter buttons
        document.getElementById('filter-7').addEventListener('click', (e) => 
            this.changeFilter(7, e.currentTarget));
        document.getElementById('filter-30').addEventListener('click', (e) => 
            this.changeFilter(30, e.currentTarget));
        document.getElementById('filter-90').addEventListener('click', (e) => 
            this.changeFilter(90, e.currentTarget));
        
        // Search
        this.searchInput.addEventListener('input', (e) => {
            this.renderCompanyList(e.target.value);
        });
        
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Refresh button
        this.refreshBtn.addEventListener('click', () => this.refresh());
        
        // Compare button
        this.compareBtn.addEventListener('click', () => this.openCompareModal());
        
        // Modal close
        document.getElementById('modal-close').addEventListener('click', () => 
            this.closeCompareModal());
        
        // Click outside modal to close
        this.compareModal.addEventListener('click', (e) => {
            if (e.target === this.compareModal) {
                this.closeCompareModal();
            }
        });
        
        // Compare submit
        document.getElementById('compare-submit').addEventListener('click', () => 
            this.compareStocks());
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
     * Toggle dark mode
     */
    toggleTheme() {
        this.darkMode = !this.darkMode;
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', this.darkMode);
        
        this.themeToggle.innerHTML = this.darkMode 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }

    /**
     * Refresh data
     */
    async refresh() {
        this.refreshBtn.style.animation = 'spin 0.5s ease';
        setTimeout(() => {
            this.refreshBtn.style.animation = '';
        }, 500);
        
        await this.loadCompanies();
        
        if (this.selectedSymbol) {
            await this.loadStockData(this.selectedSymbol);
        }
    }

    /**
     * Open compare modal
     */
    openCompareModal() {
        // Populate select options
        const select1 = document.getElementById('compare-stock1');
        const select2 = document.getElementById('compare-stock2');
        
        select1.innerHTML = '<option value="">Select stock...</option>';
        select2.innerHTML = '<option value="">Select stock...</option>';
        
        this.companies.forEach(company => {
            select1.innerHTML += `<option value="${company.symbol}">${company.symbol} - ${company.name}</option>`;
            select2.innerHTML += `<option value="${company.symbol}">${company.symbol} - ${company.name}</option>`;
        });
        
        // Pre-select current stock if available
        if (this.selectedSymbol) {
            select1.value = this.selectedSymbol;
        }
        
        this.compareModal.style.display = 'flex';
    }

    /**
     * Close compare modal
     */
    closeCompareModal() {
        this.compareModal.style.display = 'none';
        document.getElementById('compare-result').style.display = 'none';
    }

    /**
     * Compare two stocks
     */
    async compareStocks() {
        const symbol1 = document.getElementById('compare-stock1').value;
        const symbol2 = document.getElementById('compare-stock2').value;
        
        if (!symbol1 || !symbol2) {
            alert('Please select both stocks to compare');
            return;
        }
        
        if (symbol1 === symbol2) {
            alert('Please select different stocks to compare');
            return;
        }
        
        try {
            // Show loading state
            const submitBtn = document.getElementById('compare-submit');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Comparing...';
            submitBtn.disabled = true;
            
            const comparison = await apiClient.compareStocks(symbol1, symbol2);
            this.displayComparison(comparison);
            
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        } catch (error) {
            const submitBtn = document.getElementById('compare-submit');
            submitBtn.innerHTML = '<i class="fas fa-chart-line"></i> Compare';
            submitBtn.disabled = false;
            
            // Better error message
            let errorMessage = 'Failed to compare stocks';
            if (error.message.includes('404')) {
                errorMessage = 'One or both stocks do not have data available. Please select different stocks.';
            } else if (error.message.includes('SYMBOL_NOT_FOUND')) {
                errorMessage = 'One or both stocks were not found in the database.';
            } else {
                errorMessage = 'Failed to compare stocks: ' + error.message;
            }
            
            alert(errorMessage);
            console.error('Compare error:', error);
        }
    }

    /**
     * Display comparison results
     * @param {object} comparison - Comparison data
     */
    displayComparison(comparison) {
        const resultEl = document.getElementById('compare-result');
        const { stock1, stock2 } = comparison;
        
        resultEl.innerHTML = `
            <h3 style="margin-bottom: 20px; color: var(--primary-color);">
                <i class="fas fa-chart-bar"></i> Comparison Results
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="background: var(--bg-light); padding: 20px; border-radius: 12px;">
                    <h4 style="color: var(--primary-color); margin-bottom: 15px;">${stock1.symbol}</h4>
                    <p><strong>Name:</strong> ${stock1.name}</p>
                    <p><strong>52-Week High:</strong> ₹${stock1.week_52_high.toFixed(2)}</p>
                    <p><strong>52-Week Low:</strong> ₹${stock1.week_52_low.toFixed(2)}</p>
                    <p><strong>Average Close:</strong> ₹${stock1.avg_close.toFixed(2)}</p>
                </div>
                <div style="background: var(--bg-light); padding: 20px; border-radius: 12px;">
                    <h4 style="color: var(--secondary-color); margin-bottom: 15px;">${stock2.symbol}</h4>
                    <p><strong>Name:</strong> ${stock2.name}</p>
                    <p><strong>52-Week High:</strong> ₹${stock2.week_52_high.toFixed(2)}</p>
                    <p><strong>52-Week Low:</strong> ₹${stock2.week_52_low.toFixed(2)}</p>
                    <p><strong>Average Close:</strong> ₹${stock2.avg_close.toFixed(2)}</p>
                </div>
            </div>
        `;
        
        resultEl.style.display = 'block';
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
