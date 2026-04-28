# Manual Testing Guide - Stock Data Intelligence Dashboard

## Overview

This guide provides comprehensive instructions for manually testing the Stock Data Intelligence Dashboard. It covers all user-facing features, expected behaviors, and verification steps to ensure the dashboard functions correctly.

**Task Reference:** Task 14.3 - Perform manual testing  
**Requirements Validated:** 11.1, 12.1, 13.1  
**Date Created:** 2024-01-15

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Test Environment Setup](#test-environment-setup)
3. [Testing Checklist](#testing-checklist)
4. [Detailed Test Cases](#detailed-test-cases)
5. [Expected Behaviors](#expected-behaviors)
6. [Known Limitations](#known-limitations)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Components

- ✅ Backend API server running on `http://localhost:8000`
- ✅ Database initialized with sample company data
- ✅ Stock data collected for at least one company
- ✅ Modern web browser (Chrome, Firefox, Safari, or Edge)
- ✅ Internet connection (for Chart.js CDN)

### Verification Steps

Before starting manual testing, verify the environment is ready:

```bash
# 1. Check API server is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected","timestamp":"..."}

# 2. Verify companies exist
curl http://localhost:8000/companies

# Expected response: Array of companies with symbol and name

# 3. Verify stock data exists
curl http://localhost:8000/data/RELIANCE.NS

# Expected response: Array of stock data records
```

---

## Test Environment Setup

### Option 1: Local Development Server

```bash
# Start API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Serve dashboard (in a new terminal)
cd dashboard
python -m http.server 8080

# Access dashboard at: http://localhost:8080
```

### Option 2: Docker Deployment

```bash
# Start all services
docker-compose up -d

# Access dashboard at: http://localhost:8000/dashboard
# Or open dashboard/index.html directly in browser
```

### Option 3: Direct File Access

```bash
# Open dashboard/index.html directly in browser
# Note: Update API base URL in dashboard/js/api.js if needed
```

---

## Testing Checklist

Use this checklist to track your testing progress:

### Initial Load Tests
- [ ] Dashboard loads without errors
- [ ] Page title displays correctly
- [ ] Header and subtitle are visible
- [ ] Company list section is visible
- [ ] Chart section shows welcome message
- [ ] Footer displays correctly
- [ ] No console errors in browser DevTools

### Company List Tests (Requirement 11.1)
- [ ] Company list loads within 2 seconds
- [ ] Companies are displayed alphabetically by symbol
- [ ] Each company shows symbol and name
- [ ] Loading indicator appears during fetch
- [ ] Error message displays if API fails
- [ ] Empty state message shows if no companies exist
- [ ] Company items are clickable

### Chart Rendering Tests (Requirement 12.1)
- [ ] Chart displays when company is selected
- [ ] Welcome message hides when chart appears
- [ ] Chart title shows company name and symbol
- [ ] X-axis displays dates correctly
- [ ] Y-axis displays prices with ₹ symbol
- [ ] Line chart renders with proper styling
- [ ] Chart renders within 3 seconds
- [ ] Loading indicator appears during data fetch
- [ ] Error message displays if data fetch fails

### Time Period Filter Tests (Requirement 13.1)
- [ ] 30-day filter button is active by default
- [ ] 90-day filter button is available
- [ ] Clicking 30-day button updates chart
- [ ] Clicking 90-day button updates chart
- [ ] Active filter button has visual indication
- [ ] Chart updates within 1 second of filter change
- [ ] Chart data matches selected time period

### Summary Statistics Tests
- [ ] Summary section displays below chart
- [ ] 52-week high displays correctly
- [ ] 52-week low displays correctly
- [ ] Average close displays correctly
- [ ] Values are formatted with ₹ symbol
- [ ] Values show 2 decimal places
- [ ] Summary updates when company changes

### Interaction Tests
- [ ] Clicking different companies updates chart
- [ ] Selected company is highlighted in list
- [ ] Hovering over chart shows tooltip
- [ ] Tooltip displays date, price, and volume
- [ ] Chart is responsive to window resize
- [ ] Scrolling works properly in company list

### Error Handling Tests
- [ ] Invalid API responses show error messages
- [ ] Network errors are handled gracefully
- [ ] Missing data shows appropriate message
- [ ] Console logs errors for debugging

### Browser Compatibility Tests
- [ ] Dashboard works in Chrome
- [ ] Dashboard works in Firefox
- [ ] Dashboard works in Safari
- [ ] Dashboard works in Edge
- [ ] Dashboard is responsive on mobile devices

---

## Detailed Test Cases

### Test Case 1: Initial Page Load

**Objective:** Verify the dashboard loads correctly with all UI elements visible.

**Steps:**
1. Open browser and navigate to dashboard URL
2. Wait for page to fully load
3. Observe the page layout and elements

**Expected Results:**
- ✅ Page title: "Stock Data Intelligence Dashboard"
- ✅ Subtitle: "Real-time stock market analysis and visualization"
- ✅ Left sidebar shows "Companies" heading
- ✅ Main area shows welcome message: "Welcome to Stock Dashboard"
- ✅ Welcome text: "Select a company from the list to view its stock performance"
- ✅ Footer shows copyright notice
- ✅ No JavaScript errors in console

**Validation:** Requirement 11.1 (Dashboard display)

---

### Test Case 2: Company List Loading

**Objective:** Verify companies load and display correctly in alphabetical order.

**Steps:**
1. Open dashboard
2. Observe the company list section
3. Note the loading indicator
4. Wait for companies to load
5. Verify the list content

**Expected Results:**
- ✅ Loading indicator appears: "Loading companies..."
- ✅ Loading indicator disappears after data loads
- ✅ Companies are listed alphabetically by symbol
- ✅ Each item shows: `SYMBOL - Company Name`
- ✅ List loads within 2 seconds
- ✅ All configured companies are visible

**Example Display:**
```
HDFCBANK.NS - HDFC Bank Ltd
INFY.NS - Infosys Ltd
RELIANCE.NS - Reliance Industries Ltd
TCS.NS - Tata Consultancy Services Ltd
```

**Validation:** Requirement 11.1, 11.3, 11.4

---

### Test Case 3: Company Selection

**Objective:** Verify selecting a company displays its stock chart.

**Steps:**
1. Open dashboard and wait for companies to load
2. Click on any company in the list
3. Observe the chart section
4. Note the loading indicator
5. Wait for chart to render

**Expected Results:**
- ✅ Welcome message disappears
- ✅ Chart container becomes visible
- ✅ Loading indicator appears: "Loading chart data..."
- ✅ Selected company is highlighted in the list
- ✅ Chart renders within 3 seconds
- ✅ Chart title shows: "Company Name (SYMBOL)"
- ✅ Chart displays closing prices over time

**Validation:** Requirement 11.2, 12.1, 12.4, 12.5

---

### Test Case 4: Chart Visualization

**Objective:** Verify the chart displays stock data correctly with proper formatting.

**Steps:**
1. Select a company from the list
2. Wait for chart to render
3. Examine the chart elements
4. Verify axes and labels
5. Check data visualization

**Expected Results:**

**Chart Title:**
- ✅ Format: "Company Name (SYMBOL)"
- ✅ Example: "Reliance Industries Ltd (RELIANCE.NS)"

**X-Axis (Dates):**
- ✅ Label: "Date"
- ✅ Format: "MMM DD" (e.g., "Jan 15")
- ✅ Dates are in chronological order
- ✅ Labels are rotated 45 degrees for readability

**Y-Axis (Prices):**
- ✅ Label: "Price (₹)"
- ✅ Format: "₹XXX.XX" (e.g., "₹2,465.75")
- ✅ Scale is appropriate for data range
- ✅ Grid lines are visible

**Chart Line:**
- ✅ Color: Blue/purple (#667eea)
- ✅ Line is smooth (tension: 0.4)
- ✅ Area under line is filled with light color
- ✅ Data points are visible
- ✅ Line connects all data points

**Validation:** Requirement 12.1, 12.2, 12.3, 12.4

---

### Test Case 5: Chart Tooltip Interaction

**Objective:** Verify hovering over the chart displays detailed information.

**Steps:**
1. Select a company and wait for chart to render
2. Move mouse cursor over the chart line
3. Hover over different data points
4. Observe the tooltip content

**Expected Results:**
- ✅ Tooltip appears when hovering over data points
- ✅ Tooltip follows mouse cursor
- ✅ Tooltip displays:
  - Date (e.g., "Jan 15")
  - Closing Price: "₹XXX.XX"
  - Volume: "X,XXX,XXX"
- ✅ Tooltip has dark background with white text
- ✅ Tooltip disappears when mouse moves away

**Example Tooltip:**
```
Jan 15
Closing Price (₹): ₹2,465.75
Volume: 5,234,567
```

**Validation:** Requirement 12.1 (Interactive visualization)

---

### Test Case 6: 30-Day Filter

**Objective:** Verify the 30-day filter displays the correct time period.

**Steps:**
1. Select a company from the list
2. Wait for chart to render (default is 30 days)
3. Observe the filter buttons
4. Verify the chart data range
5. Count the number of data points

**Expected Results:**
- ✅ "30 Days" button is highlighted/active by default
- ✅ "90 Days" button is not highlighted
- ✅ Chart displays up to 30 days of data
- ✅ Most recent date is today or last trading day
- ✅ Oldest date is approximately 30 days ago
- ✅ Data points represent trading days only (no weekends)

**Validation:** Requirement 13.1, 13.3

---

### Test Case 7: 90-Day Filter

**Objective:** Verify the 90-day filter updates the chart correctly.

**Steps:**
1. Select a company and wait for chart to render
2. Click the "90 Days" filter button
3. Observe the chart update
4. Verify the data range
5. Note the update speed

**Expected Results:**
- ✅ "90 Days" button becomes highlighted/active
- ✅ "30 Days" button is no longer highlighted
- ✅ Chart updates within 1 second
- ✅ Chart displays up to 90 days of data
- ✅ X-axis adjusts to show more dates
- ✅ Y-axis scale adjusts if needed
- ✅ Chart remains smooth and readable

**Validation:** Requirement 13.1, 13.2, 13.4, 13.5

---

### Test Case 8: Filter Toggle

**Objective:** Verify switching between filters works correctly.

**Steps:**
1. Select a company
2. Click "90 Days" button
3. Wait for chart to update
4. Click "30 Days" button
5. Wait for chart to update
6. Repeat several times

**Expected Results:**
- ✅ Each click updates the chart
- ✅ Active button is always visually indicated
- ✅ Chart updates smoothly without flickering
- ✅ No errors in console
- ✅ Data is fetched correctly for each period
- ✅ Chart maintains proper formatting

**Validation:** Requirement 13.1, 13.4

---

### Test Case 9: Summary Statistics Display

**Objective:** Verify summary statistics are displayed correctly.

**Steps:**
1. Select a company from the list
2. Wait for chart and summary to load
3. Locate the "Summary Statistics" section
4. Verify all metrics are displayed

**Expected Results:**

**Summary Section:**
- ✅ Heading: "Summary Statistics"
- ✅ Three metrics displayed in a grid layout

**52-Week High:**
- ✅ Label: "52-Week High"
- ✅ Value format: "₹X,XXX.XX"
- ✅ Value is the highest price in 52 weeks

**52-Week Low:**
- ✅ Label: "52-Week Low"
- ✅ Value format: "₹X,XXX.XX"
- ✅ Value is the lowest price in 52 weeks

**Average Close:**
- ✅ Label: "Average Close"
- ✅ Value format: "₹X,XXX.XX"
- ✅ Value is the average closing price

**Validation:** Requirement 12.1 (Summary display)

---

### Test Case 10: Multiple Company Selection

**Objective:** Verify switching between companies updates all data correctly.

**Steps:**
1. Select first company (e.g., RELIANCE.NS)
2. Wait for chart and summary to load
3. Note the displayed data
4. Select second company (e.g., TCS.NS)
5. Wait for chart and summary to update
6. Compare the data

**Expected Results:**
- ✅ First company is highlighted in list
- ✅ Chart displays first company's data
- ✅ Summary shows first company's statistics
- ✅ Clicking second company highlights it
- ✅ First company is no longer highlighted
- ✅ Chart updates to show second company's data
- ✅ Chart title changes to second company
- ✅ Summary updates to second company's statistics
- ✅ Filter selection is maintained (30 or 90 days)

**Validation:** Requirement 11.2, 12.1

---

### Test Case 11: Error Handling - No Companies

**Objective:** Verify appropriate message when no companies exist.

**Steps:**
1. Ensure database has no companies (or mock empty response)
2. Open dashboard
3. Observe the company list section

**Expected Results:**
- ✅ Loading indicator appears briefly
- ✅ Error or empty state message displays
- ✅ Message: "No companies available in the database"
- ✅ Welcome message remains in chart section
- ✅ No JavaScript errors in console

**Validation:** Requirement 11.5

---

### Test Case 12: Error Handling - API Failure

**Objective:** Verify error handling when API is unavailable.

**Steps:**
1. Stop the API server
2. Open dashboard
3. Observe the behavior

**Expected Results:**
- ✅ Loading indicator appears
- ✅ Error message displays after timeout
- ✅ Message: "Failed to load companies. Please try again later."
- ✅ Error is logged to console
- ✅ Dashboard remains functional (no crash)

**Validation:** Requirement 11.3 (Error handling)

---

### Test Case 13: Error Handling - No Stock Data

**Objective:** Verify appropriate message when company has no data.

**Steps:**
1. Select a company with no stock data
2. Wait for chart section to respond

**Expected Results:**
- ✅ Loading indicator appears
- ✅ Error message displays
- ✅ Message: "No data available for the selected time period"
- ✅ Chart canvas is empty
- ✅ Summary shows "-" for all values

**Validation:** Requirement 12.5 (Error handling)

---

### Test Case 14: Responsive Design

**Objective:** Verify dashboard is responsive to different screen sizes.

**Steps:**
1. Open dashboard in full-screen browser
2. Resize browser window to various widths
3. Test on mobile device or use browser DevTools device emulation

**Expected Results:**

**Desktop (>1024px):**
- ✅ Two-column layout (company list + chart)
- ✅ Company list is fixed width sidebar
- ✅ Chart takes remaining space
- ✅ All elements are visible

**Tablet (768px - 1024px):**
- ✅ Layout adjusts appropriately
- ✅ Chart remains readable
- ✅ Buttons are accessible

**Mobile (<768px):**
- ✅ Single-column layout (stacked)
- ✅ Company list appears above chart
- ✅ Chart is full width
- ✅ Touch interactions work
- ✅ Text is readable

**Validation:** Requirement 12.1 (Responsive visualization)

---

### Test Case 15: Performance Testing

**Objective:** Verify dashboard meets performance requirements.

**Steps:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Reload dashboard
4. Measure load times
5. Select different companies
6. Measure chart render times

**Expected Results:**

**Initial Load:**
- ✅ Page loads within 2 seconds
- ✅ Company list loads within 2 seconds
- ✅ Total page weight < 1 MB

**Company Selection:**
- ✅ Chart renders within 3 seconds
- ✅ API response time < 500ms
- ✅ Chart animation is smooth (60fps)

**Filter Changes:**
- ✅ Chart updates within 1 second
- ✅ No visible lag or stuttering

**Validation:** Requirements 11.3, 12.5, 13.4

---

## Expected Behaviors

### Normal Operation Flow

1. **Page Load:**
   - Dashboard loads with welcome message
   - Company list fetches and displays companies
   - No chart is shown initially

2. **Company Selection:**
   - User clicks a company
   - Company is highlighted
   - Welcome message hides
   - Chart section shows loading indicator
   - Chart renders with 30-day data (default)
   - Summary statistics display

3. **Filter Interaction:**
   - User clicks 30-day or 90-day button
   - Active button is highlighted
   - Chart updates with new data range
   - Summary remains unchanged

4. **Company Switching:**
   - User clicks different company
   - Previous company is unhighlighted
   - New company is highlighted
   - Chart updates with new company's data
   - Summary updates with new company's statistics
   - Filter selection is maintained

### Visual Indicators

**Loading States:**
- "Loading companies..." - While fetching company list
- "Loading chart data..." - While fetching stock data
- Spinner or text indicator

**Active States:**
- Selected company: Background color change, bold text
- Active filter button: Different background color, border

**Error States:**
- Red text for error messages
- Error icon (optional)
- Descriptive error message

### Data Formatting

**Dates:**
- Format: "MMM DD" (e.g., "Jan 15", "Dec 31")
- Chronological order (oldest to newest)

**Prices:**
- Format: "₹X,XXX.XX" (e.g., "₹2,465.75")
- Two decimal places
- Comma separators for thousands

**Volume:**
- Format: "X,XXX,XXX" (e.g., "5,234,567")
- Comma separators for thousands

---

## Known Limitations

### Data Limitations

1. **Trading Days Only:**
   - Charts show only trading days (no weekends/holidays)
   - 30-day filter may show fewer than 30 data points
   - 90-day filter may show fewer than 90 data points

2. **Data Availability:**
   - Stock data depends on external API availability
   - Historical data may be limited for some symbols
   - Real-time data may have delays

3. **Symbol Format:**
   - Indian stocks require ".NS" suffix (e.g., "RELIANCE.NS")
   - Symbol format must match yfinance requirements

### UI Limitations

1. **Browser Compatibility:**
   - Requires modern browser with ES6 support
   - Chart.js requires JavaScript enabled
   - Internet connection needed for Chart.js CDN

2. **Mobile Experience:**
   - Chart interactions may be limited on small screens
   - Tooltip may be difficult to trigger on touch devices
   - Horizontal scrolling may be needed for long date ranges

3. **Performance:**
   - Large datasets (>365 days) may slow chart rendering
   - Multiple rapid filter changes may cause lag
   - Browser memory usage increases with chart complexity

### Feature Limitations

1. **No Real-Time Updates:**
   - Data is not automatically refreshed
   - User must reload page for latest data

2. **No Data Export:**
   - Cannot download chart as image
   - Cannot export data to CSV

3. **No Comparison View:**
   - Cannot view multiple stocks simultaneously
   - Must switch between companies manually

4. **No Customization:**
   - Cannot change chart colors
   - Cannot adjust time ranges beyond 30/90 days
   - Cannot toggle metrics on/off

---

## Troubleshooting

### Issue: Company List Not Loading

**Symptoms:**
- Loading indicator stays visible
- Error message appears
- Empty list

**Possible Causes:**
1. API server is not running
2. Database has no companies
3. Network connectivity issue
4. CORS policy blocking request

**Solutions:**
```bash
# Check API server
curl http://localhost:8000/health

# Check companies endpoint
curl http://localhost:8000/companies

# Verify database has data
python scripts/init_db.py

# Check browser console for errors
# Open DevTools (F12) > Console tab
```

---

### Issue: Chart Not Rendering

**Symptoms:**
- Chart section remains empty
- Loading indicator disappears but no chart
- Error message appears

**Possible Causes:**
1. No stock data for selected company
2. Chart.js CDN not loading
3. JavaScript error in chart rendering
4. Invalid data format from API

**Solutions:**
```bash
# Check stock data exists
curl http://localhost:8000/data/RELIANCE.NS

# Collect data if missing
python scripts/collect_data.py

# Check browser console for errors
# Look for Chart.js errors or network failures

# Verify Chart.js CDN is accessible
# Check Network tab in DevTools
```

---

### Issue: Chart Displays Incorrectly

**Symptoms:**
- Chart is distorted or misaligned
- Axes are not visible
- Data points are missing
- Colors are wrong

**Possible Causes:**
1. CSS styling conflicts
2. Chart.js version mismatch
3. Invalid data values
4. Browser rendering issue

**Solutions:**
```bash
# Clear browser cache
# Hard reload: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

# Check CSS is loading
# DevTools > Network tab > Filter by CSS

# Verify Chart.js version
# Check dashboard/index.html for CDN link

# Test in different browser
# Try Chrome, Firefox, or Edge
```

---

### Issue: Filters Not Working

**Symptoms:**
- Clicking filter buttons does nothing
- Chart doesn't update
- Active state doesn't change

**Possible Causes:**
1. JavaScript error preventing event handling
2. API not returning data for requested period
3. Event listeners not attached

**Solutions:**
```bash
# Check browser console for errors
# Look for JavaScript exceptions

# Verify API returns data for both periods
curl "http://localhost:8000/data/RELIANCE.NS?days=30"
curl "http://localhost:8000/data/RELIANCE.NS?days=90"

# Check event listeners are attached
# DevTools > Elements tab > Event Listeners
```

---

### Issue: Summary Statistics Not Displaying

**Symptoms:**
- Summary section shows "-" for all values
- Summary doesn't update when company changes
- Summary section is missing

**Possible Causes:**
1. API not returning summary data
2. Insufficient historical data (< 52 weeks)
3. JavaScript error in summary update

**Solutions:**
```bash
# Check summary endpoint
curl http://localhost:8000/summary/RELIANCE.NS

# Verify data exists
# Summary requires at least some historical data

# Check browser console for errors
# Look for API call failures
```

---

### Issue: Performance Problems

**Symptoms:**
- Dashboard is slow to load
- Chart rendering takes >3 seconds
- Browser becomes unresponsive
- High CPU/memory usage

**Possible Causes:**
1. Large dataset (>365 days)
2. Too many data points
3. Browser resource constraints
4. Network latency

**Solutions:**
```bash
# Limit data range
# Use 30-day or 90-day filters only

# Check API response time
curl -w "@curl-format.txt" http://localhost:8000/data/RELIANCE.NS

# Close other browser tabs
# Free up system resources

# Check database query performance
# Review API server logs
```

---

## Testing Report Template

Use this template to document your testing results:

```markdown
# Manual Testing Report

**Date:** YYYY-MM-DD
**Tester:** [Your Name]
**Environment:** [Local/Docker/Production]
**Browser:** [Chrome/Firefox/Safari/Edge] [Version]

## Test Summary

- Total Test Cases: 15
- Passed: X
- Failed: X
- Blocked: X
- Not Tested: X

## Test Results

### Test Case 1: Initial Page Load
- Status: [PASS/FAIL]
- Notes: [Any observations]

### Test Case 2: Company List Loading
- Status: [PASS/FAIL]
- Notes: [Any observations]

[Continue for all test cases...]

## Issues Found

### Issue 1: [Title]
- Severity: [Critical/High/Medium/Low]
- Description: [Detailed description]
- Steps to Reproduce: [Steps]
- Expected: [Expected behavior]
- Actual: [Actual behavior]
- Screenshot: [If applicable]

## Recommendations

[Any suggestions for improvements]

## Sign-off

Tested by: [Name]
Date: [Date]
Approved: [Yes/No]
```

---

## Conclusion

This manual testing guide provides comprehensive coverage of the Stock Data Intelligence Dashboard's user-facing features. By following these test cases and using the checklist, you can verify that:

1. ✅ Dashboard displays correctly (Requirement 11.1)
2. ✅ Charts render properly (Requirement 12.1)
3. ✅ Time period filters work (Requirement 13.1)
4. ✅ All interactions function as expected
5. ✅ Error handling is appropriate
6. ✅ Performance meets requirements

**Next Steps:**
1. Execute all test cases systematically
2. Document results using the report template
3. Report any issues found
4. Verify fixes and retest
5. Obtain sign-off for production deployment

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**Maintained By:** Development Team
