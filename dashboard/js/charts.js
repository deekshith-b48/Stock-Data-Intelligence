/**
 * Chart Manager
 * Handles Chart.js integration and chart rendering
 */

class ChartManager {
    constructor() {
        this.chart = null;
        this.canvas = document.getElementById('stock-chart');
        this.ctx = this.canvas.getContext('2d');
    }

    /**
     * Update or create chart with new data
     * @param {Array} stockData - Array of stock data records
     * @param {object} company - Company information
     */
    updateChart(stockData, company) {
        if (!stockData || stockData.length === 0) {
            this.showNoDataMessage();
            return;
        }

        // Sort data by date ascending for proper chart display
        const sortedData = [...stockData].sort((a, b) => 
            new Date(a.date) - new Date(b.date)
        );

        // Extract dates and closing prices
        const dates = sortedData.map(record => this.formatDate(record.date));
        const closePrices = sortedData.map(record => record.close);
        const volumes = sortedData.map(record => record.volume);

        // Update chart title
        document.getElementById('chart-title').textContent = 
            `${company.name} (${company.symbol})`;

        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }

        // Create new chart
        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Closing Price (₹)',
                        data: closePrices,
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        pointBackgroundColor: 'rgb(102, 126, 234)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                weight: '600'
                            },
                            color: '#333',
                            padding: 15
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgb(102, 126, 234)',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                return `${label}: ₹${value.toFixed(2)}`;
                            },
                            afterLabel: function(context) {
                                const index = context.dataIndex;
                                const volume = volumes[index];
                                return `Volume: ${volume.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Date',
                            font: {
                                size: 14,
                                weight: '600'
                            },
                            color: '#667eea'
                        },
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                            font: {
                                size: 11
                            },
                            color: '#666'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Price (₹)',
                            font: {
                                size: 14,
                                weight: '600'
                            },
                            color: '#667eea'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toFixed(2);
                            },
                            font: {
                                size: 11
                            },
                            color: '#666'
                        }
                    }
                }
            }
        });
    }

    /**
     * Format date string for display
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const options = { month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }

    /**
     * Show message when no data is available
     */
    showNoDataMessage() {
        if (this.chart) {
            this.chart.destroy();
        }
        
        const errorEl = document.getElementById('error-chart');
        errorEl.textContent = 'No data available for the selected time period';
        errorEl.style.display = 'block';
    }

    /**
     * Destroy the chart instance
     */
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Create a global chart manager instance
const chartManager = new ChartManager();
