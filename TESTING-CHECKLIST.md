# Web Interface Testing Checklist

This checklist should be completed after deploying the web interface to AWS.

## Pre-Deployment Verification

- [ ] All files are in correct locations:
  - [ ] `cdk/bin/app.ts` exists
  - [ ] `cdk/lib/mcp-tools-stack.ts` exists
  - [ ] `cdk/package.json` exists
  - [ ] `lambda/src/handler.py` exists
  - [ ] `lambda/src/mock_data.py` exists
  - [ ] `lambda/src/index.html` exists
  - [ ] `deploy.sh` exists and is executable

- [ ] CDK configuration is correct:
  - [ ] AWS profile configured
  - [ ] AWS region set (default: us-east-1)
  - [ ] Lambda code points to `../lambda/src`

## Deployment Testing

### 1. Build and Deploy

- [ ] Run `./deploy.sh` successfully
- [ ] CDK dependencies installed without errors
- [ ] TypeScript builds without errors
- [ ] Bootstrap CDK (first time): `npx cdk bootstrap --profile YOUR_PROFILE`
- [ ] Deploy stack: `npx cdk deploy --profile YOUR_PROFILE`
- [ ] Function URL is output after deployment
- [ ] Copy Function URL for testing

### 2. Login Flow Testing

- [ ] Open Function URL in browser
- [ ] Login page loads correctly
- [ ] Page shows "Market Data Tools" title
- [ ] Secret input field is visible
- [ ] Login button is visible

**Test Invalid Token:**
- [ ] Enter incorrect token (e.g., "wrong")
- [ ] Click Login
- [ ] "Access Denied" message appears
- [ ] Input field is cleared
- [ ] Still on login page

**Test Valid Token:**
- [ ] Enter correct token: `ddg@9812`
- [ ] Click Login
- [ ] Tools page loads
- [ ] Login page is hidden
- [ ] Tools page is visible

### 3. Tools Interface Testing

**UI Elements:**
- [ ] "Market Data Tools" title visible
- [ ] Logout button visible in top right
- [ ] Tool selector dropdown visible
- [ ] All 14 tools listed in dropdown:
  - [ ] Get Stock Quote
  - [ ] Get Multiple Quotes
  - [ ] Get Fundamentals
  - [ ] Get Enhanced Fundamentals
  - [ ] Get Historical Data
  - [ ] Get Intraday Data
  - [ ] Get Technical Indicators
  - [ ] Get Supported Indicators
  - [ ] Get Options Chain
  - [ ] Get Option Greeks
  - [ ] Get Provider Status
  - [ ] Search Symbols
  - [ ] Get Market Status
  - [ ] Get Earnings Calendar

**Parameter Inputs:**
- [ ] Select "Get Stock Quote"
- [ ] Symbol input field appears
- [ ] Default value is "AAPL"
- [ ] Select "Get Multiple Quotes"
- [ ] Symbols input field appears
- [ ] Default value is "AAPL,GOOGL,MSFT"
- [ ] Select "Get Supported Indicators"
- [ ] No parameter inputs shown (correct)

### 4. Tool Execution Testing

Test each tool with default parameters:

**Stock Tools:**
- [ ] Get Stock Quote (AAPL)
  - [ ] Returns mock quote data
  - [ ] Includes price, volume, market cap
  - [ ] JSON is properly formatted
  
- [ ] Get Multiple Quotes (AAPL,GOOGL,MSFT)
  - [ ] Returns array of quotes
  - [ ] All 3 symbols present
  
- [ ] Get Fundamentals (AAPL)
  - [ ] Returns PE ratio, EPS, etc.
  
- [ ] Get Enhanced Fundamentals (AAPL)
  - [ ] Returns fundamentals + earnings + ratings

**Historical Tools:**
- [ ] Get Historical Data (AAPL)
  - [ ] Returns array of OHLCV data
  - [ ] 22 data points present
  
- [ ] Get Intraday Data (AAPL)
  - [ ] Returns intraday bars
  - [ ] 78 data points present

**Technical Tools:**
- [ ] Get Technical Indicators (AAPL, SMA)
  - [ ] Returns indicator values
  
- [ ] Get Supported Indicators
  - [ ] Returns list of indicators
  - [ ] Includes SMA, EMA, RSI, MACD, etc.

**Options Tools:**
- [ ] Get Options Chain (AAPL)
  - [ ] Returns options data
  - [ ] Includes calls and puts
  - [ ] Greeks present
  
- [ ] Get Option Greeks (AAPL, 175.0, call)
  - [ ] Returns detailed Greeks
  - [ ] Delta, Gamma, Theta, Vega present

**Utility Tools:**
- [ ] Get Provider Status
  - [ ] Returns provider health data
  - [ ] Robinhood, Finnhub, FMP, Alpha Vantage listed
  
- [ ] Search Symbols (APP)
  - [ ] Returns search results
  - [ ] AAPL, APP, APPN present
  
- [ ] Get Market Status
  - [ ] Returns market status
  - [ ] Trading hours present
  
- [ ] Get Earnings Calendar
  - [ ] Returns upcoming earnings
  - [ ] Multiple companies listed

### 5. Session Management Testing

- [ ] Refresh page while logged in
- [ ] Tools page still visible (session persists)
- [ ] Click Logout button
- [ ] Login page appears
- [ ] Session cleared
- [ ] Close browser tab
- [ ] Open Function URL in new tab
- [ ] Login page appears (session cleared)

### 6. Mobile Responsiveness Testing

**On Mobile Device:**
- [ ] Open Function URL on mobile
- [ ] Login page is responsive
- [ ] Input fields are appropriately sized
- [ ] Login button is touch-friendly
- [ ] Login with token: `ddg@9812`
- [ ] Tools page is responsive
- [ ] Dropdown is usable
- [ ] Parameter inputs are touch-friendly
- [ ] Execute button works
- [ ] JSON output is readable
- [ ] Can scroll through results
- [ ] Logout button accessible

### 7. Error Handling Testing

**Network Errors:**
- [ ] Disconnect internet
- [ ] Try to execute tool
- [ ] "Network error" message appears

**Invalid Tool:**
- [ ] Manually navigate to `/tools/invalid_tool?token=ddg@9812`
- [ ] Error response returned
- [ ] "Unknown tool" message present

**Missing Token:**
- [ ] Manually navigate to `/tools/get_stock_quote` (no token)
- [ ] 403 Forbidden response
- [ ] "Unauthorized" message present

### 8. Security Verification

- [ ] Confirm HTTPS is used (check browser URL bar)
- [ ] Lock icon visible in browser
- [ ] View page source
- [ ] Token is NOT visible in HTML source
- [ ] Token is stored in sessionStorage (check DevTools)
- [ ] Token is NOT in localStorage
- [ ] Token is NOT in cookies

### 9. AWS Console Verification

**Lambda Function:**
- [ ] Open AWS Lambda console
- [ ] Find "McpToolsWebStack-McpToolsFunction" function
- [ ] Verify configuration:
  - [ ] Runtime: Python 3.12
  - [ ] Memory: 128 MB
  - [ ] Timeout: 30 seconds
  - [ ] Environment variable AUTH_TOKEN present

**CloudWatch Logs:**
- [ ] Open CloudWatch Logs
- [ ] Find log group for Lambda function
- [ ] Execute a tool from web interface
- [ ] Verify log entry appears
- [ ] Verify token is NOT logged
- [ ] Verify request parameters are logged

**Cost Monitoring:**
- [ ] Check AWS Cost Explorer
- [ ] Verify Lambda invocations count
- [ ] Verify costs are minimal (~$0.50/month)

### 10. Performance Testing

- [ ] Execute Get Stock Quote
- [ ] Note response time (should be <2s)
- [ ] Execute Get Options Chain
- [ ] Note response time (should be <3s)
- [ ] Execute 10 tools in succession
- [ ] All complete successfully
- [ ] No timeouts or errors

## Post-Testing

- [ ] All tests passed
- [ ] Document any issues found
- [ ] Function URL bookmarked
- [ ] Token documented securely
- [ ] Deployment considered successful

## Cleanup (Optional)

If you want to remove the deployment:

```bash
cd cdk
npx cdk destroy --profile YOUR_PROFILE
```

- [ ] Stack destroyed successfully
- [ ] Lambda function removed
- [ ] Function URL no longer accessible
- [ ] CloudWatch logs retained (optional cleanup)

---

**Testing Date:** _________________

**Tester:** _________________

**Function URL:** _________________

**Notes:**
