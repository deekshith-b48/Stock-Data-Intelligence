# Stock Data Intelligence Dashboard - Frontend

A responsive web dashboard for visualizing stock market data with interactive charts.

## Features

- **Company List**: Browse all available companies alphabetically
- **Interactive Charts**: View closing price trends with Chart.js
- **Time Period Filters**: Switch between 30-day and 90-day views
- **Summary Statistics**: Display 52-week high, low, and average closing price
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## File Structure

```
dashboard/
├── index.html          # Main HTML page
├── css/
│   └── styles.css      # Styling and responsive design
├── js/
│   ├── api.js          # API client for backend communication
│   ├── app.js          # Main application logic and company list
│   └── charts.js       # Chart.js integration and rendering
└── README.md           # This file
```

## Usage

### Running Locally

1. **Start the Backend API Server**:
   ```bash
   # From the project root
   uvicorn src.api.main:app --reload
   ```
   The API will be available at `http://localhost:8000`

2. **Serve the Dashboard**:
   
   **Option A: Using Python's built-in server**:
   ```bash
   cd dashboard
   python -m http.server 8080
   ```
   
   **Option B: Using Node.js http-server**:
   ```bash
   cd dashboard
   npx http-server -p 8080
   ```
   
   **Option C: Using VS Code Live Server extension**:
   - Open `dashboard/index.html` in VS Code
   - Right-click and select "Open with Live Server"

3. **Access the Dashboard**:
   Open your browser and navigate to `http://localhost:8080`

### Configuration

The API base URL is configured in `js/api.js`:

```javascript
const apiClient = new APIClient('http://localhost:8000');
```

To change the API endpoint (e.g., for production deployment), modify this line.

## Components

### APIClient (api.js)

Handles all HTTP communication with the backend REST API:
- `getCompanies()` - Fetch list of all companies
- `getStockData(symbol, days)` - Fetch stock data for a symbol
- `getSummary(symbol)` - Fetch summary statistics
- `compareStocks(symbol1, symbol2)` - Compare two stocks

### StockDashboard (app.js)

Main application controller:
- Loads and displays company list
- Handles company selection
- Manages time period filters (30-day, 90-day)
- Updates summary statistics
- Error handling and loading states

### ChartManager (charts.js)

Chart rendering and management:
- Creates interactive line charts with Chart.js
- Displays closing prices over time
- Shows tooltips with price and volume data
- Responsive chart sizing

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- **Chart.js 4.4.0**: Loaded via CDN for chart rendering
- No build process required - pure HTML/CSS/JavaScript

## API Requirements

The dashboard expects the following API endpoints:

- `GET /companies` - Returns array of `{symbol, name}`
- `GET /data/{symbol}` - Returns array of stock data records
- `GET /summary/{symbol}` - Returns summary statistics

See the API documentation at `http://localhost:8000/docs` for details.

## Customization

### Changing Colors

Edit `css/styles.css` to modify the color scheme. Main colors:
- Primary: `#667eea` (purple-blue)
- Secondary: `#764ba2` (purple)

### Adding More Filters

To add additional time period filters (e.g., 7 days, 180 days):

1. Add button in `index.html`:
   ```html
   <button id="filter-7" class="filter-btn" data-days="7">7 Days</button>
   ```

2. Add event listener in `app.js`:
   ```javascript
   const filter7Btn = document.getElementById('filter-7');
   filter7Btn.addEventListener('click', () => this.changeFilter(7, filter7Btn));
   ```

## Troubleshooting

### Dashboard shows "Failed to load companies"

- Ensure the backend API is running at `http://localhost:8000`
- Check browser console for CORS errors
- Verify the API endpoint is accessible

### Charts not displaying

- Check browser console for JavaScript errors
- Ensure Chart.js CDN is accessible
- Verify stock data is being returned from API

### CORS Issues

If you encounter CORS errors, ensure the backend API has CORS middleware configured:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```
