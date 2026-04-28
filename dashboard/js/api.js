/**
 * API Client for Stock Data Intelligence Dashboard
 * Handles all communication with the backend REST API
 */

class APIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper with error handling
     * @param {string} endpoint - API endpoint path
     * @param {object} options - Fetch options
     * @returns {Promise<any>} - Parsed JSON response
     */
    async _fetch(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.message || 
                    `HTTP ${response.status}: ${response.statusText}`
                );
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * Get list of all available companies
     * @returns {Promise<Array>} - Array of company objects with symbol and name
     */
    async getCompanies() {
        return await this._fetch('/companies');
    }

    /**
     * Get stock data for a specific symbol
     * @param {string} symbol - Stock symbol (e.g., 'AAPL', 'RELIANCE')
     * @param {number} days - Number of days of data to retrieve (default: 30)
     * @returns {Promise<Array>} - Array of stock data records
     */
    async getStockData(symbol, days = 30) {
        if (!symbol) {
            throw new Error('Symbol is required');
        }
        return await this._fetch(`/data/${symbol}`);
    }

    /**
     * Get summary statistics for a specific symbol
     * @param {string} symbol - Stock symbol
     * @returns {Promise<object>} - Summary statistics object
     */
    async getSummary(symbol) {
        if (!symbol) {
            throw new Error('Symbol is required');
        }
        return await this._fetch(`/summary/${symbol}`);
    }

    /**
     * Compare two stocks side by side
     * @param {string} symbol1 - First stock symbol
     * @param {string} symbol2 - Second stock symbol
     * @returns {Promise<object>} - Comparison data for both stocks
     */
    async compareStocks(symbol1, symbol2) {
        if (!symbol1 || !symbol2) {
            throw new Error('Both symbols are required');
        }
        return await this._fetch(`/compare?symbol1=${symbol1}&symbol2=${symbol2}`);
    }

    /**
     * Health check endpoint
     * @returns {Promise<object>} - Health status
     */
    async healthCheck() {
        return await this._fetch('/health');
    }
}

// Create a global API client instance
const apiClient = new APIClient();
