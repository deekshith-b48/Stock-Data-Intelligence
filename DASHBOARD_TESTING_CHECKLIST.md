# Dashboard Testing Checklist - Quick Reference

**Task:** 14.3 Perform manual testing  
**Requirements:** 11.1, 12.1, 13.1  
**Date:** _______________  
**Tester:** _______________

---

## Pre-Testing Setup

- [ ] API server running on http://localhost:8000
- [ ] Database initialized with companies
- [ ] Stock data collected for test companies
- [ ] Browser DevTools open (F12)
- [ ] Dashboard URL: _______________

**Quick Verification:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/companies
```

---

## 1. Initial Load (Requirement 11.1)

- [ ] Page loads without errors
- [ ] Title: "Stock Data Intelligence Dashboard"
- [ ] Company list section visible
- [ ] Welcome message visible
- [ ] No console errors
- [ ] Load time < 2 seconds

**Notes:** _______________________________________________

---

## 2. Company List (Requirement 11.1)

- [ ] Loading indicator appears
- [ ] Companies load within 2 seconds
- [ ] Alphabetically sorted by symbol
- [ ] Each item shows symbol + name
- [ ] All companies visible
- [ ] Items are clickable
- [ ] Empty state handled (if applicable)

**Company Count:** _______  
**Notes:** _______________________________________________

---

## 3. Company Selection (Requirement 11.2, 12.1)

**Test Company:** _______________

- [ ] Click company in list
- [ ] Company highlighted
- [ ] Welcome message hides
- [ ] Chart container appears
- [ ] Loading indicator shows
- [ ] Chart renders within 3 seconds
- [ ] Chart title correct: "Name (SYMBOL)"

**Notes:** _______________________________________________

---

## 4. Chart Visualization (Requirement 12.1, 12.2, 12.3, 12.4)

- [ ] Line chart displays
- [ ] X-axis: Dates (MMM DD format)
- [ ] Y-axis: Prices (₹ symbol)
- [ ] Chart title includes company name
- [ ] Line is smooth and styled
- [ ] Data points visible
- [ ] Grid lines visible
- [ ] Legend displays

**Data Points Count:** _______  
**Date Range:** _______ to _______  
**Notes:** _______________________________________________

---

## 5. Chart Tooltip (Requirement 12.1)

- [ ] Hover over chart line
- [ ] Tooltip appears
- [ ] Shows date
- [ ] Shows closing price (₹)
- [ ] Shows volume
- [ ] Tooltip follows cursor
- [ ] Tooltip disappears on mouse out

**Notes:** _______________________________________________

---

## 6. 30-Day Filter (Requirement 13.1, 13.3)

- [ ] "30 Days" button active by default
- [ ] Button visually highlighted
- [ ] Chart shows ~30 days of data
- [ ] Most recent date is current/last trading day
- [ ] Data range is correct

**Actual Data Points:** _______  
**Date Range:** _______ to _______  
**Notes:** _______________________________________________

---

## 7. 90-Day Filter (Requirement 13.1, 13.2, 13.4, 13.5)

- [ ] Click "90 Days" button
- [ ] Button becomes active/highlighted
- [ ] "30 Days" button deactivated
- [ ] Chart updates within 1 second
- [ ] Chart shows ~90 days of data
- [ ] X-axis adjusts appropriately
- [ ] Y-axis adjusts if needed

**Actual Data Points:** _______  
**Date Range:** _______ to _______  
**Update Time:** _______ seconds  
**Notes:** _______________________________________________

---

## 8. Filter Toggle (Requirement 13.1, 13.4)

- [ ] Switch from 90-day to 30-day
- [ ] Chart updates correctly
- [ ] Switch from 30-day to 90-day
- [ ] Chart updates correctly
- [ ] Active button always indicated
- [ ] No flickering or errors
- [ ] Smooth transitions

**Notes:** _______________________________________________

---

## 9. Summary Statistics (Requirement 12.1)

- [ ] Summary section visible below chart
- [ ] "Summary Statistics" heading
- [ ] 52-Week High displayed
- [ ] 52-Week Low displayed
- [ ] Average Close displayed
- [ ] Values formatted: ₹X,XXX.XX
- [ ] Values have 2 decimal places

**52-Week High:** ₹_______  
**52-Week Low:** ₹_______  
**Average Close:** ₹_______  
**Notes:** _______________________________________________

---

## 10. Multiple Company Selection (Requirement 11.2, 12.1)

**Company 1:** _______________
- [ ] Select company 1
- [ ] Chart displays correctly
- [ ] Note chart title and data

**Company 2:** _______________
- [ ] Select company 2
- [ ] Company 1 unhighlighted
- [ ] Company 2 highlighted
- [ ] Chart updates to company 2
- [ ] Chart title changes
- [ ] Summary updates
- [ ] Filter selection maintained

**Notes:** _______________________________________________

---

## 11. Error Handling - No Companies (Requirement 11.5)

**Skip if not applicable**

- [ ] Empty database scenario
- [ ] Loading indicator appears
- [ ] Error/empty message displays
- [ ] Message: "No companies available..."
- [ ] No JavaScript errors
- [ ] Dashboard remains functional

**Notes:** _______________________________________________

---

## 12. Error Handling - API Failure (Requirement 11.3)

**Skip if not applicable**

- [ ] Stop API server
- [ ] Reload dashboard
- [ ] Loading indicator appears
- [ ] Error message displays
- [ ] Message: "Failed to load companies..."
- [ ] Error logged to console
- [ ] Dashboard doesn't crash

**Notes:** _______________________________________________

---

## 13. Error Handling - No Stock Data (Requirement 12.5)

**Skip if not applicable**

- [ ] Select company with no data
- [ ] Loading indicator appears
- [ ] Error message displays
- [ ] Message: "No data available..."
- [ ] Chart canvas empty
- [ ] Summary shows "-" values

**Notes:** _______________________________________________

---

## 14. Responsive Design

### Desktop (>1024px)
- [ ] Two-column layout
- [ ] Company list sidebar
- [ ] Chart takes remaining space
- [ ] All elements visible

### Tablet (768px - 1024px)
- [ ] Layout adjusts appropriately
- [ ] Chart readable
- [ ] Buttons accessible

### Mobile (<768px)
- [ ] Single-column layout
- [ ] Company list above chart
- [ ] Chart full width
- [ ] Touch interactions work
- [ ] Text readable

**Tested Devices/Sizes:** _______________________________________________

---

## 15. Performance (Requirements 11.3, 12.5, 13.4)

### Initial Load
- [ ] Page loads < 2 seconds
- [ ] Company list loads < 2 seconds
- [ ] Total page weight < 1 MB

**Actual Load Time:** _______ seconds  
**Page Weight:** _______ KB

### Company Selection
- [ ] Chart renders < 3 seconds
- [ ] API response < 500ms
- [ ] Smooth animation (60fps)

**Actual Render Time:** _______ seconds  
**API Response Time:** _______ ms

### Filter Changes
- [ ] Chart updates < 1 second
- [ ] No lag or stuttering

**Actual Update Time:** _______ seconds

**Notes:** _______________________________________________

---

## Browser Compatibility

### Chrome
- [ ] Version: _______
- [ ] All features work
- [ ] No errors

### Firefox
- [ ] Version: _______
- [ ] All features work
- [ ] No errors

### Safari
- [ ] Version: _______
- [ ] All features work
- [ ] No errors

### Edge
- [ ] Version: _______
- [ ] All features work
- [ ] No errors

**Notes:** _______________________________________________

---

## Console Errors

**Any JavaScript errors?** [ ] Yes [ ] No

**Error Details:**
```
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## Network Issues

**Any failed requests?** [ ] Yes [ ] No

**Failed Requests:**
```
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## Issues Found

### Issue 1
- **Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
- **Description:** _______________________________________________
- **Steps to Reproduce:** _______________________________________________
- **Expected:** _______________________________________________
- **Actual:** _______________________________________________

### Issue 2
- **Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
- **Description:** _______________________________________________
- **Steps to Reproduce:** _______________________________________________
- **Expected:** _______________________________________________
- **Actual:** _______________________________________________

### Issue 3
- **Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
- **Description:** _______________________________________________
- **Steps to Reproduce:** _______________________________________________
- **Expected:** _______________________________________________
- **Actual:** _______________________________________________

---

## Test Summary

**Total Checks:** _______  
**Passed:** _______  
**Failed:** _______  
**Blocked:** _______  
**Not Tested:** _______

**Pass Rate:** _______% 

---

## Overall Assessment

**Dashboard Status:** [ ] Ready for Production [ ] Needs Fixes [ ] Major Issues

**Comments:**
```
_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## Recommendations

```
_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## Sign-off

**Tested By:** _______________________________________________  
**Date:** _______________________________________________  
**Time Spent:** _______ minutes  
**Approved:** [ ] Yes [ ] No  
**Approver:** _______________________________________________

---

## Additional Notes

```
_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________
```

---

**Document Version:** 1.0  
**Task Reference:** 14.3 Perform manual testing  
**Requirements Validated:** 11.1, 12.1, 13.1
