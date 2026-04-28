# Stock Data Intelligence Dashboard - Usage Guide

## Quick Start

### 1. Start the API Server
```bash
venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open the Dashboard
Open `dashboard/index.html` in your web browser or navigate to:
```
file:///Users/deekshi484/Downloads/Stock%20Data%20Intelligence%20Dashboard/dashboard/index.html
```

## Features Overview

### 🏢 Company List
- **Auto-filtered**: Only shows companies with available stock data
- **Search**: Type to filter companies by symbol or name
- **Click to view**: Select any company to see its stock performance

### 📊 Stock Charts
- **Interactive charts**: Hover over data points for details
- **Time filters**: 
  - 7D: Last 7 days
  - 30D: Last 30 days (default)
  - 90D: Last 90 days
- **Price indicators**: Current price with change percentage
- **Color-coded**: Green for gains, red for losses

### 📈 Summary Statistics
- **52-Week High**: Highest price in the last year
- **52-Week Low**: Lowest price in the last year
- **Average Close**: Average closing price
- **Volatility**: Price volatility score

### 🔄 Compare Stocks
1. Click the "Compare" button
2. Select two stocks from the dropdowns
3. Click "Compare" to see side-by-side statistics
4. View key metrics comparison

**Note**: Only stocks with `.NS` suffix have data (e.g., RELIANCE.NS, TCS.NS, INFY.NS)

### 🌙 Dark Mode
- Click the moon/sun icon in the header
- Preference is saved automatically
- Reduces eye strain in low-light conditions

### 🔍 Search
- Real-time filtering of company list
- Search by symbol (e.g., "RELIANCE.NS")
- Search by name (e.g., "Reliance")

### 🔄 Refresh
- Click the refresh icon to reload all data
- Updates company list and current chart
- Animated feedback during refresh

## Available Stocks

The following stocks have data available:

| Symbol | Company Name |
|--------|-------------|
| RELIANCE.NS | Reliance Industries |
| TCS.NS | Tata Consultancy Services |
| INFY.NS | Infosys |
| HDFCBANK.NS | HDFC Bank |
| ICICIBANK.NS | ICICI Bank |
| HINDUNILVR.NS | Hindustan Unilever |
| ITC.NS | ITC Limited |
| SBIN.NS | State Bank of India |
| BHARTIARTL.NS | Bharti Airtel |
| KOTAKBANK.NS | Kotak Mahindra Bank |

## Troubleshooting

### "No companies with stock data available"
- The database may be empty
- Run the data collection script:
  ```bash
  python scripts/collect_data.py
  ```

### "Failed to load companies"
- Check if the API server is running
- Verify the API is accessible at http://localhost:8000
- Check the browser console for errors

### "Failed to compare stocks"
- Ensure both selected stocks have data
- Only stocks with `.NS` suffix have data
- Check the API server logs for errors

### Chart not displaying
- Ensure the stock has data for the selected time period
- Try a different time filter (7D, 30D, 90D)
- Check browser console for JavaScript errors

## API Endpoints

The dashboard uses the following API endpoints:

- `GET /companies` - List all companies
- `GET /data/{symbol}?days={days}` - Get stock data
- `GET /summary/{symbol}` - Get summary statistics
- `GET /compare?symbol1={symbol1}&symbol2={symbol2}` - Compare stocks
- `GET /health` - API health check

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Keyboard Shortcuts

- **Tab**: Navigate between elements
- **Enter**: Select company or submit form
- **Esc**: Close modal (when implemented)
- **Ctrl/Cmd + F**: Browser search (works in company list)

## Performance Tips

1. **Use time filters**: Shorter time periods load faster
2. **Clear browser cache**: If experiencing issues
3. **Close unused tabs**: Reduces memory usage
4. **Use dark mode**: Reduces screen brightness and power usage

## Data Update Frequency

- **Real-time**: Dashboard updates when you select a stock
- **Manual refresh**: Click the refresh button
- **API data**: Updated when data collection script runs

## Mobile Usage

The dashboard is fully responsive:
- **Portrait mode**: Single column layout
- **Landscape mode**: Optimized for wider screens
- **Touch-friendly**: Large buttons and tap targets
- **Swipe**: Scroll through company list

## Advanced Features

### Custom Time Ranges
Currently supports 7D, 30D, and 90D. To add custom ranges:
1. Modify `dashboard/js/app.js`
2. Add new filter button in `dashboard/index.html`
3. Update the `changeFilter` method

### Export Data
To export chart data:
1. Open browser developer tools (F12)
2. Go to Console tab
3. Type: `chartManager.chart.data`
4. Copy the data object

### API Integration
To integrate with other tools:
```javascript
// Example: Fetch stock data
fetch('http://localhost:8000/data/RELIANCE.NS?days=30')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Support

For issues or questions:
1. Check the browser console for errors
2. Review API server logs
3. Verify database has data
4. Check network connectivity

## Version Information

- **Dashboard Version**: 2.0.0
- **API Version**: 1.0.0
- **Last Updated**: 2024-04-28

---

**Enjoy analyzing stock data! 📈**
