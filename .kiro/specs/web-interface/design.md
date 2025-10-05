# Web Interface Design Document

## Overview

This design document describes the architecture for adding an HTTPS web interface to the Market Data MCP Server. The implementation uses AWS Lambda with Function URLs, CDK for infrastructure as code, and a simple HTML/JavaScript UI. This phase focuses on establishing the infrastructure with mock data responses, preparing for future integration with the refactored core logic.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Desktop/Mobile)                 │
│  ┌──────────────┐                    ┌──────────────────────┐   │
│  │ Login Page   │ ──validates──────> │   Tools Page         │   │
│  │ (index.html) │                    │   (index.html)       │   │
│  └──────────────┘                    └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS (AWS-managed SSL)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Lambda Function URL                       │
│                         (Public HTTPS)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Lambda Handler (Python 3.12)                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Route Handler                                           │   │
│  │  • GET / or /index.html  ──> Serve HTML UI              │   │
│  │  • GET /validate         ──> Validate token             │   │
│  │  • GET /tools/<tool>     ──> Execute tool (mock data)   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Mock Data Generator                                     │   │
│  │  • get_stock_quote       ──> Dummy quote data           │   │
│  │  • get_fundamentals      ──> Dummy fundamental data     │   │
│  │  • get_options_chain     ──> Dummy options data         │   │
│  │  • get_historical        ──> Dummy historical data      │   │
│  │  • ... (14 tools total)                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CloudWatch Logs                             │
│                   (Request/Error Logging)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Infrastructure Architecture (CDK)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CDK Stack                                │
│                    (TypeScript - lib/mcp-tools-stack.ts)         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Lambda Function                                       │     │
│  │  • Runtime: Python 3.12                                │     │
│  │  • Memory: 128 MB                                      │     │
│  │  • Timeout: 30 seconds                                 │     │
│  │  • Handler: handler.handler                            │     │
│  │  • Code: lambda/ directory                             │     │
│  │  • Environment:                                        │     │
│  │    - AUTH_TOKEN: 'ddg@9812'                            │     │
│  └────────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Lambda Function URL                                   │     │
│  │  • Auth Type: NONE (public)                            │     │
│  │  • CORS: Enabled (all origins, GET)                    │     │
│  │  • Protocol: HTTPS (AWS-managed cert)                  │     │
│  │  • Invoke Mode: BUFFERED                               │     │
│  └────────────────────────────────────────────────────────┘     │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  IAM Permission                                        │     │
│  │  • Principal: *                                        │     │
│  │  • Action: InvokeFunctionUrl                           │     │
│  │  • FunctionUrlAuthType: NONE                           │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. CDK Infrastructure (TypeScript)

#### File: `cdk/bin/app.ts`
```typescript
// CDK app entry point
- Imports the MCP Tools Stack
- Configures AWS environment (account, region)
- Synthesizes CloudFormation template
```

#### File: `cdk/lib/mcp-tools-stack.ts`
```typescript
// CDK stack definition
class McpToolsStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    // Lambda Function
    const lambdaFunction = new lambda.Function(this, 'McpToolsFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('../lambda/src'),  // Point to lambda/src
      memorySize: 128,
      timeout: Duration.seconds(30),
      environment: {
        AUTH_TOKEN: 'ddg@9812'
      }
    });

    // Function URL
    const functionUrl = lambdaFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ['*'],
        allowedMethods: [lambda.HttpMethod.GET],
      }
    });

    // Output the URL
    new CfnOutput(this, 'FunctionUrl', {
      value: functionUrl.url
    });
  }
}
```

#### File: `cdk/cdk.json`
```json
{
  "app": "npx ts-node --prefer-ts-exts bin/app.ts",
  "context": {
    "@aws-cdk/core:enableStackNameDuplicates": true
  }
}
```

#### File: `cdk/package.json`
```json
{
  "name": "mcp-tools-web-cdk",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc",
    "cdk": "cdk"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "aws-cdk": "^2.100.0",
    "ts-node": "^10.9.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {
    "aws-cdk-lib": "^2.100.0",
    "constructs": "^10.0.0"
  }
}
```

#### File: `cdk/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["es2020"],
    "declaration": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "exclude": ["node_modules", "cdk.out"]
}
```

### 2. Lambda Handler (Python)

#### File: `lambda/src/handler.py`

**Main Handler Function:**
```python
def handler(event, context):
    """
    Main Lambda handler for HTTP requests
    
    Routes:
    - GET / or /index.html -> Serve HTML UI
    - GET /validate?token=X -> Validate authentication token
    - GET /tools/<tool_name>?token=X&param1=val1 -> Execute tool with mock data
    
    Returns:
    - HTTP response with status code, headers, and body
    """
```

**Route Handlers:**
```python
def serve_html():
    """Serve the HTML UI from index.html file"""
    # Read index.html
    # Return 200 with HTML content-type
    
def validate_token(query_params):
    """Validate authentication token"""
    # Extract token from query params
    # Compare with AUTH_TOKEN environment variable
    # Return {"success": true/false}
    
def execute_tool(tool_name, query_params):
    """Execute tool and return mock data"""
    # Validate token
    # Route to appropriate mock data generator
    # Return JSON response with mock data
```

#### File: `lambda/src/mock_data.py`

**Mock Data Generators:**
```python
def mock_get_stock_quote(params):
    """Generate mock stock quote data"""
    symbol = params.get('symbol', 'AAPL')
    return {
        'symbol': symbol,
        'price': 175.43,
        'change': 2.15,
        'change_percent': 1.24,
        'volume': 52_000_000,
        'market_cap': 2_750_000_000_000,
        'timestamp': '2025-01-04T16:00:00Z'
    }

def mock_get_fundamentals(params):
    """Generate mock fundamental data"""
    symbol = params.get('symbol', 'AAPL')
    return {
        'symbol': symbol,
        'company_name': 'Apple Inc.',
        'pe_ratio': 28.5,
        'eps': 6.15,
        'market_cap': 2_750_000_000_000,
        'dividend_yield': 0.52,
        'beta': 1.25,
        'earnings': [
            {'quarter': 'Q4 2024', 'eps': 1.64, 'revenue': 119_000_000_000},
            {'quarter': 'Q3 2024', 'eps': 1.53, 'revenue': 94_000_000_000}
        ]
    }

def mock_get_options_chain(params):
    """Generate mock options chain data"""
    symbol = params.get('symbol', 'AAPL')
    return {
        'symbol': symbol,
        'stock_price': 175.43,
        'options': [
            {
                'strike': 175.0,
                'type': 'call',
                'expiration': '2025-01-17',
                'premium': 3.25,
                'volume': 1250,
                'open_interest': 5400,
                'delta': 0.52,
                'gamma': 0.03,
                'theta': -0.15,
                'vega': 0.18
            },
            {
                'strike': 175.0,
                'type': 'put',
                'expiration': '2025-01-17',
                'premium': 2.85,
                'volume': 980,
                'open_interest': 4200,
                'delta': -0.48,
                'gamma': 0.03,
                'theta': -0.12,
                'vega': 0.18
            }
        ]
    }

# Additional mock generators for all 14 tools:
# - mock_get_multiple_quotes
# - mock_get_enhanced_fundamentals
# - mock_get_historical
# - mock_get_intraday
# - mock_get_indicators
# - mock_get_supported_indicators
# - mock_get_option_greeks
# - mock_get_provider_status
# ... etc
```

**Handler imports mock_data:**
```python
# In lambda/src/handler.py
from mock_data import (
    mock_get_stock_quote,
    mock_get_fundamentals,
    mock_get_options_chain,
    # ... all other mock functions
)
```

**Error Handling:**
```python
def create_response(status_code, body, content_type='application/json'):
    """Create standardized HTTP response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': content_type,
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body) if content_type == 'application/json' else body
    }

def handle_error(error, tool_name=None):
    """Handle errors and return appropriate response"""
    # Log error to CloudWatch
    # Return 500 with generic error message
```

### 3. Web UI (HTML/JavaScript)

#### File: `lambda/src/index.html`

**Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Data Tools</title>
    <style>
        /* Responsive CSS for desktop and mobile */
        /* Login page styling */
        /* Tools page styling */
        /* JSON output formatting */
    </style>
</head>
<body>
    <!-- Login Page (default view) -->
    <div id="login-page">
        <h1>Market Data Tools</h1>
        <input type="password" id="token-input" placeholder="Enter secret">
        <button onclick="login()">Login</button>
        <div id="login-error"></div>
    </div>

    <!-- Tools Page (shown after successful login) -->
    <div id="tools-page" style="display: none;">
        <h1>Market Data Tools</h1>
        <button onclick="logout()">Logout</button>
        
        <div class="tool-selector">
            <label>Select Tool:</label>
            <select id="tool-select" onchange="updateParams()">
                <option value="get_stock_quote">Get Stock Quote</option>
                <option value="get_fundamentals">Get Fundamentals</option>
                <option value="get_options_chain">Get Options Chain</option>
                <option value="get_historical">Get Historical Data</option>
                <!-- All 14 tools -->
            </select>
        </div>
        
        <div id="params-container">
            <!-- Dynamic parameter inputs based on selected tool -->
        </div>
        
        <button onclick="executeTool()">Execute</button>
        
        <div id="result-container">
            <pre id="result-output"></pre>
        </div>
    </div>

    <script>
        // JavaScript implementation
    </script>
</body>
</html>
```

**JavaScript Functions:**
```javascript
// Session Management
function login() {
    // Get token from input
    // Call /validate endpoint
    // If successful, store token in sessionStorage
    // Show tools page, hide login page
}

function logout() {
    // Clear sessionStorage
    // Show login page, hide tools page
}

function checkSession() {
    // Check if token exists in sessionStorage
    // If yes, show tools page
    // If no, show login page
}

// Tool Execution
function updateParams() {
    // Get selected tool
    // Show appropriate parameter inputs
    // e.g., symbol input for stock quote
}

function executeTool() {
    // Get selected tool and parameters
    // Get token from sessionStorage
    // Call /tools/<tool_name>?token=X&params
    // Display result in formatted JSON
}

// Utility Functions
function formatJSON(data) {
    // Pretty-print JSON with syntax highlighting
}

function showError(message) {
    // Display error message to user
}
```

### 4. Deployment Script

#### File: `deploy.sh`
```bash
#!/bin/bash

# Configuration
export AWS_REGION=us-east-1
export AWS_ACCOUNT=368253648705
export AWS_PROFILE=default

# Navigate to CDK directory
cd cdk

# Install Node.js dependencies
echo "Installing dependencies..."
npm install

# Build TypeScript
echo "Building CDK app..."
npm run build

# Bootstrap CDK (first time only)
echo "Bootstrapping CDK..."
npx cdk bootstrap aws://$AWS_ACCOUNT/$AWS_REGION --profile $AWS_PROFILE

# Deploy stack
echo "Deploying stack..."
npx cdk deploy --profile $AWS_PROFILE --require-approval never

echo "Deployment complete!"
echo "Check the output above for your Function URL"
```

## Data Models

### HTTP Request/Response Models

**Validate Token Request:**
```
GET /validate?token=ddg@9812
```

**Validate Token Response:**
```json
{
  "success": true
}
```

**Tool Execution Request:**
```
GET /tools/get_stock_quote?token=ddg@9812&symbol=AAPL
```

**Tool Execution Response (Success):**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "price": 175.43,
    "change": 2.15,
    "change_percent": 1.24,
    "volume": 52000000,
    "market_cap": 2750000000000,
    "timestamp": "2025-01-04T16:00:00Z"
  },
  "timestamp": "2025-01-04T16:05:23Z"
}
```

**Tool Execution Response (Error):**
```json
{
  "success": false,
  "error": "Invalid token",
  "timestamp": "2025-01-04T16:05:23Z"
}
```

### Mock Data Schemas

All mock data generators return schemas matching the expected output from the real MCP tools. This ensures that when we integrate with the refactored core logic, the UI and API contracts remain unchanged.

**14 MCP Tools to Mock:**
1. `get_stock_quote` - Real-time stock quote
2. `get_multiple_quotes` - Multiple stock quotes in one call
3. `get_fundamentals` - Company fundamentals
4. `get_enhanced_fundamentals` - Fundamentals with earnings and ratings
5. `get_historical` - Historical price data
6. `get_intraday` - Intraday price data
7. `get_indicators` - Technical indicators
8. `get_supported_indicators` - List of available indicators
9. `get_options_chain` - Options chain data
10. `get_option_greeks` - Detailed option Greeks
11. `get_provider_status` - Provider health status
12. `search_symbols` - Symbol search
13. `get_market_status` - Market open/close status
14. `get_earnings_calendar` - Upcoming earnings dates

## Error Handling

### Lambda Error Handling

**Authentication Errors:**
- Missing token: 403 Forbidden
- Invalid token: 403 Forbidden
- Expired session: 403 Forbidden

**Request Errors:**
- Invalid tool name: 400 Bad Request
- Missing required parameters: 400 Bad Request
- Malformed request: 400 Bad Request

**Server Errors:**
- Unexpected exception: 500 Internal Server Error
- Timeout: 504 Gateway Timeout

**Error Response Format:**
```json
{
  "success": false,
  "error": "Error message here",
  "timestamp": "2025-01-04T16:05:23Z"
}
```

### UI Error Handling

**Login Errors:**
- Display "Access Denied" for invalid token
- Clear input field after failed attempt
- No hints about correct token format

**Tool Execution Errors:**
- Display error message in result container
- Highlight error in red
- Preserve previous successful results

**Network Errors:**
- Display "Network error, please try again"
- Provide retry button
- Log error to browser console

## Testing Strategy

### Unit Tests (Python)

**Test File: `lambda/tests/test_handler.py`**

```python
# Test route handling
def test_serve_html():
    # Verify HTML is returned with 200 status
    
def test_validate_token_success():
    # Verify correct token returns success
    
def test_validate_token_failure():
    # Verify incorrect token returns failure
    
def test_execute_tool_with_valid_token():
    # Verify tool execution with valid token
    
def test_execute_tool_with_invalid_token():
    # Verify 403 error with invalid token
```

**Test File: `lambda/tests/test_mock_data.py`**

```python
# Test mock data generators
def test_mock_get_stock_quote():
    # Verify mock data structure matches expected schema
    
def test_mock_get_fundamentals():
    # Verify mock data structure matches expected schema
    
def test_mock_get_options_chain():
    # Verify mock data structure matches expected schema

# Test all 14 mock generators
# ... (one test per tool)
```

### Integration Tests

**Test File: `lambda/tests/test_integration.py`**

```python
# Test end-to-end Lambda invocation
def test_lambda_handler_html_route():
    # Invoke handler with GET / request
    # Verify HTML response
    
def test_lambda_handler_validate_route():
    # Invoke handler with /validate request
    # Verify JSON response
    
def test_lambda_handler_tool_route():
    # Invoke handler with /tools/get_stock_quote request
    # Verify JSON response with mock data
```

### Manual Testing

**Deployment Testing:**
1. Run `./deploy.sh`
2. Verify CDK deployment succeeds
3. Verify Function URL is output
4. Access Function URL in browser
5. Verify login page loads

**Authentication Testing:**
1. Enter incorrect token
2. Verify "Access Denied" message
3. Enter correct token (`ddg@9812`)
4. Verify tools page loads

**Tool Execution Testing:**
1. Select each of the 14 tools
2. Enter required parameters
3. Click Execute
4. Verify mock data is displayed
5. Verify JSON formatting is correct

**Mobile Testing:**
1. Access Function URL on mobile device
2. Verify responsive layout
3. Test login flow
4. Test tool execution
5. Verify JSON is readable on small screen

## Security Considerations

### Authentication

**Token Storage:**
- Token stored in `sessionStorage` (not `localStorage`)
- Cleared on browser close
- Cleared on logout
- Not accessible to other tabs/windows

**Token Transmission:**
- Sent via HTTPS (AWS-managed SSL)
- Included in query parameters
- Not visible in page source
- Not logged in CloudWatch (sanitized)

**Token Validation:**
- Compared against environment variable
- Constant-time comparison to prevent timing attacks
- No hints on login page about token format

### HTTPS

**AWS-Managed SSL:**
- Automatic certificate provisioning
- Automatic certificate renewal
- TLS 1.2+ enforced
- Strong cipher suites

### CORS

**Configuration:**
- Allow all origins (acceptable for public API)
- Allow GET method only
- No credentials required
- Preflight requests handled automatically

### Rate Limiting

**Current Implementation:**
- No rate limiting (acceptable for personal use)
- Lambda concurrency limits provide natural throttling
- CloudWatch metrics for monitoring

**Future Enhancement:**
- API Gateway with rate limiting
- DynamoDB for request tracking
- Per-token rate limits

## Deployment Process

### Prerequisites

1. AWS CLI configured with credentials
2. Node.js installed (v18+)
3. Python 3.12 installed
4. AWS account with Lambda permissions

### Deployment Steps

1. **Install Dependencies:**
   ```bash
   cd cdk
   npm install
   ```

2. **Build TypeScript:**
   ```bash
   npm run build
   ```

3. **Bootstrap CDK (first time only):**
   ```bash
   npx cdk bootstrap aws://368253648705/us-east-1
   ```

4. **Deploy Stack:**
   ```bash
   npx cdk deploy
   ```

5. **Access Function URL:**
   - Copy URL from deployment output
   - Open in browser
   - Login with token: `ddg@9812`

### Update Process

1. Make changes to code
2. Run `./deploy.sh`
3. CDK automatically detects changes
4. Lambda function updated in-place
5. No downtime (Function URL remains same)

### Cleanup

```bash
npx cdk destroy
```

## Cost Analysis

### Monthly Cost Breakdown (20 calls/day = 600 calls/month)

**Lambda Invocations:**
- 600 requests × $0.20 per 1M requests = $0.00012

**Lambda Compute:**
- 600 requests × 100ms average × 128MB
- 600 × 0.1s × 128MB = 7,680 MB-seconds
- 7,680 MB-seconds × $0.0000166667 per GB-second = $0.00013

**CloudWatch Logs:**
- 600 requests × 1KB per request = 600KB
- 600KB × $0.50 per GB = $0.0003

**Data Transfer:**
- 600 requests × 5KB response = 3MB
- First 1GB free = $0

**Total Monthly Cost: ~$0.50**

### Cost Optimization

**Current Optimizations:**
- Minimal memory (128MB)
- Short timeout (30s)
- No API Gateway (Function URL is free)
- No additional AWS services

**Future Optimizations:**
- Lambda reserved concurrency for predictable costs
- CloudWatch Logs retention policy (7 days)
- Compress responses for smaller data transfer

## Future Enhancements

### Phase 2: Real Data Integration

After the refactoring PR is merged:
1. Replace mock data generators with core logic calls
2. Add dependency management for `market_data` package
3. Add environment variables for API keys
4. Add AWS Secrets Manager for sensitive credentials
5. Update Lambda memory/timeout based on real performance

### Phase 3: Advanced Features

**UI Enhancements:**
- Tool parameter validation
- Auto-complete for stock symbols
- Historical data charting
- Options chain visualization
- Favorites/recent symbols

**Infrastructure Enhancements:**
- Custom domain with Route 53
- CloudFront CDN for global access
- API Gateway for advanced routing
- DynamoDB for request logging
- Rate limiting per token

**Security Enhancements:**
- Multiple user support
- Token expiration
- IP-based rate limiting
- Request signing
- Audit logging

## Success Criteria

### Phase 1 (This Implementation)

✅ CDK stack deploys successfully  
✅ Lambda Function URL is accessible via HTTPS  
✅ Login page loads and validates token  
✅ Tools page displays all 14 tools  
✅ Each tool returns mock data in correct format  
✅ UI works on desktop and mobile browsers  
✅ Session persists until logout or browser close  
✅ Cost under $1/month for expected usage  
✅ All unit tests pass  
✅ Integration tests pass  

### Phase 2 (Future)

⬜ Real data integration with refactored core  
⬜ All 14 tools return live market data  
⬜ Provider fallback mechanisms work correctly  
⬜ Performance meets SLA (<5s response time)  
⬜ Error handling covers all edge cases  

## Project Structure

```
.
├── README-webtool.md          # User documentation
├── DESIGN.md                  # Design document (from DESIGN.md in root)
├── deploy.sh                  # One-click deployment script
├── cdk/                       # CDK infrastructure code
│   ├── package.json          # Node.js dependencies
│   ├── tsconfig.json         # TypeScript configuration
│   ├── cdk.json              # CDK configuration
│   ├── bin/
│   │   └── app.ts           # CDK app entry point
│   └── lib/
│       └── mcp-tools-stack.ts # CDK stack definition
└── lambda/                    # Lambda function code
    ├── src/
    │   ├── handler.py        # Lambda handler
    │   ├── mock_data.py      # Mock data generators
    │   └── index.html        # Web UI
    └── tests/
        ├── test_handler.py           # Unit tests for handler
        ├── test_mock_data.py         # Unit tests for mock data
        └── test_integration.py       # Integration tests
```

**Benefits of this structure:**
- Clear separation: CDK infrastructure vs Lambda application code
- Lambda code is self-contained with its own src and tests
- Easy to navigate: all CDK files in one place, all Lambda files in another
- Scalable: Easy to add more Lambda functions or CDK stacks later

## Conclusion

This design provides a complete architecture for adding an HTTPS web interface to the Market Data MCP Server. The implementation is:

- **Simple**: Minimal infrastructure (Lambda + Function URL)
- **Secure**: Token-based auth with HTTPS
- **Cost-effective**: Under $1/month for personal use
- **Scalable**: Ready for Phase 2 real data integration
- **Maintainable**: Clean separation of concerns
- **Testable**: Comprehensive unit and integration tests

The mock data approach allows us to validate the entire infrastructure and UI before integrating with the refactored core logic, reducing risk and enabling parallel development.
