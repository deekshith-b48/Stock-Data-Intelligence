# Manual Testing Quick Start Guide

**Task 14.3:** Perform manual testing of the Stock Data Intelligence Dashboard

---

## Quick Setup (5 minutes)

### Step 1: Start the API Server

```bash
# Option A: Using uvicorn (development)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Option B: Using Docker
docker-compose up -d
```

### Step 2: Verify API is Running

```bash
# Check health
curl http://localhost:8000/health

# Expected: {"status":"healthy",...}
```

### Step 3: Ensure Data Exists

```bash
# Check companies
curl http://localhost:8000/companies

# If empty, initialize database and collect data:
python scripts/init_db.py
python scripts/collect_data.py
```

### Step 4: Open Dashboard

```bash
# Option A: Direct file access
# Open dashboard/index.html in your browser

# Option B: Local server
cd dashboard
python -m http.server 8080
# Then open: http://localhost:8080

# Option C: Docker (if using docker-compose)
# Open: http://localhost:8000/dashboard
```

---

## 5-Minute Smoke Test

This quick test verifies core functionality:

### 1. Page Load (30 seconds)
- [ ] Open dashboard
- [ ] Page loads without errors
- [ ] Company list appears
- [ ] Welcome message visible

### 2. Company Selection (1 minute)
- [ ] Click any company
- [ ] Chart appears within 3 seconds
- [ ] Chart shows data
- [ ] Summary statistics display

### 3. Filter Test (1 minute)
- [ ] Click "90 Days" button
- [ ] Chart updates
- [ ] Click "30 Days" button
- [ ] Chart updates back

### 4. Multiple Companies (1 minute)
- [ ] Click different company
- [ ] Chart updates
- [ ] Summary updates
- [ ] Previous company unhighlighted

### 5. Browser Console (30 seconds)
- [ ] Open DevTools (F12)
- [ ] Check Console tab
- [ ] No red errors

**Result:** [ ] PASS [ ] FAIL

---

## 15-Minute Core Test

Follow this sequence for comprehensive testing:

### Test Sequence

1. **Initial Load** (2 min)
   - Open dashboard
   - Verify all UI elements
   - Check company list loads

2. **Chart Rendering** (3 min)
   - Select company
   - Verify chart displays
   - Check axes and labels
   - Test tooltip hover

3. **Filters** (3 min)
   - Test 30-day filter
   - Test 90-day filter
   - Toggle between filters
   - Verify data updates

4. **Summary Statistics** (2 min)
   - Verify 52-week high
   - Verify 52-week low
   - Verify average close
   - Check formatting

5. **Multiple Companies** (3 min)
   - Select 3 different companies
   - Verify each updates correctly
   - Check highlighting works

6. **Error Checks** (2 min)
   - Check browser console
   - Verify no network errors
   - Test with invalid scenarios

**Use:** `DASHBOARD_TESTING_CHECKLIST.md` for detailed tracking

---

## Full Test Suite (60 minutes)

For complete validation, follow the comprehensive guide:

1. **Read:** `MANUAL_TESTING_GUIDE.md`
2. **Use:** `DASHBOARD_TESTING_CHECKLIST.md`
3. **Execute:** All 15 test cases
4. **Document:** Results and issues
5. **Report:** Using template in guide

---

## Common Issues & Quick Fixes

### Issue: Company list not loading

```bash
# Check API
curl http://localhost:8000/companies

# If empty, initialize:
python scripts/init_db.py

# Restart API server
```

### Issue: Chart not rendering

```bash
# Check stock data
curl http://localhost:8000/data/RELIANCE.NS

# If empty, collect data:
python scripts/collect_data.py

# Clear browser cache: Ctrl+Shift+R
```

### Issue: CORS errors

```bash
# Serve dashboard via HTTP server:
cd dashboard
python -m http.server 8080

# Or use Docker with proper CORS config
```

### Issue: Chart.js not loading

```bash
# Check internet connection
# Chart.js loads from CDN

# Or download Chart.js locally:
# Update dashboard/index.html to use local file
```

---

## Testing Checklist Summary

### Requirements Validation

**Requirement 11.1:** Dashboard displays company list
- [ ] Company list loads
- [ ] Alphabetically sorted
- [ ] Clickable items
- [ ] Loads within 2 seconds

**Requirement 12.1:** Chart renders correctly
- [ ] Line chart displays
- [ ] Dates on X-axis
- [ ] Prices on Y-axis
- [ ] Company name in title
- [ ] Renders within 3 seconds

**Requirement 13.1:** Time period filters work
- [ ] 30-day filter available
- [ ] 90-day filter available
- [ ] Default is 30 days
- [ ] Updates within 1 second
- [ ] Visual indication of active filter

---

## Test Data Recommendations

### Minimum Test Data

For effective testing, ensure you have:

- **At least 5 companies** in the database
- **At least 90 days** of stock data per company
- **Mix of data patterns:**
  - Stable stocks (low volatility)
  - Volatile stocks (high volatility)
  - Trending up stocks
  - Trending down stocks

### Sample Companies (Indian Stocks)

```python
# Good test companies:
RELIANCE.NS  # Large cap, stable
TCS.NS       # IT sector, moderate volatility
INFY.NS      # IT sector, similar to TCS
HDFCBANK.NS  # Banking sector
TATAMOTORS.NS # Auto sector, more volatile
```

### Collecting Test Data

```bash
# Collect data for specific symbols
python scripts/collect_data.py --symbols RELIANCE.NS TCS.NS INFY.NS HDFCBANK.NS TATAMOTORS.NS

# Collect data for date range
python scripts/collect_data.py --start-date 2023-10-01 --end-date 2024-01-15
```

---

## Browser Testing Matrix

### Priority Browsers

1. **Chrome** (Latest) - Primary
2. **Firefox** (Latest) - Secondary
3. **Safari** (Latest) - macOS/iOS
4. **Edge** (Latest) - Windows

### Testing Approach

**Desktop:**
- Test all features in Chrome first
- Spot-check in Firefox and Edge
- Full test in Safari if macOS available

**Mobile:**
- Test responsive design in Chrome DevTools
- Spot-check on actual mobile device if available

---

## Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Page Load | < 1s | < 2s | > 2s |
| Company List Load | < 1s | < 2s | > 2s |
| Chart Render | < 2s | < 3s | > 3s |
| Filter Update | < 0.5s | < 1s | > 1s |
| API Response | < 200ms | < 500ms | > 500ms |

### Measuring Performance

**Using Browser DevTools:**

1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Check "Load" time at bottom
5. Click company, check API response time
6. Use Performance tab for detailed analysis

---

## Reporting Results

### Quick Report Format

```markdown
## Test Results - [Date]

**Tester:** [Name]
**Duration:** [X] minutes
**Browser:** [Browser] [Version]

### Summary
- Total Tests: X
- Passed: X
- Failed: X

### Critical Issues
1. [Issue description]
2. [Issue description]

### Recommendation
[ ] Ready for production
[ ] Minor fixes needed
[ ] Major issues found
```

### Detailed Report

Use the template in `MANUAL_TESTING_GUIDE.md` for comprehensive reporting.

---

## Next Steps After Testing

### If All Tests Pass ✅

1. Document test results
2. Get sign-off from stakeholder
3. Proceed to deployment
4. Monitor production

### If Tests Fail ❌

1. Document all issues with details
2. Prioritize by severity
3. Create bug tickets
4. Fix issues
5. Retest affected areas
6. Full regression test

---

## Useful Commands Reference

```bash
# Start API server
uvicorn src.api.main:app --reload

# Start dashboard server
python -m http.server 8080 --directory dashboard

# Check API health
curl http://localhost:8000/health

# List companies
curl http://localhost:8000/companies

# Get stock data
curl http://localhost:8000/data/RELIANCE.NS

# Get summary
curl http://localhost:8000/summary/RELIANCE.NS

# Initialize database
python scripts/init_db.py

# Collect data
python scripts/collect_data.py

# Run with Docker
docker-compose up -d
docker-compose logs -f api
docker-compose down

# Check logs
tail -f app.log
```

---

## Contact & Support

**For Issues:**
- Check `MANUAL_TESTING_GUIDE.md` troubleshooting section
- Review browser console errors
- Check API server logs
- Verify database has data

**Documentation:**
- `MANUAL_TESTING_GUIDE.md` - Comprehensive guide
- `DASHBOARD_TESTING_CHECKLIST.md` - Printable checklist
- `README.md` - Project documentation

---

## Checklist Before Starting

- [ ] API server is running
- [ ] Database is initialized
- [ ] Stock data is collected
- [ ] Browser DevTools ready
- [ ] Testing checklist printed/open
- [ ] Time allocated (15-60 minutes)
- [ ] Test environment documented

**Ready to test?** Open `DASHBOARD_TESTING_CHECKLIST.md` and begin! 🚀

---

**Document Version:** 1.0  
**Task:** 14.3 Perform manual testing  
**Requirements:** 11.1, 12.1, 13.1
