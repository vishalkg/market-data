# Implementation Plan

- [x] 1. Set up CDK project structure
  - Create `cdk/` directory with package.json, tsconfig.json, and cdk.json
  - Install CDK dependencies (aws-cdk-lib, constructs, typescript, ts-node)
  - Configure TypeScript compiler settings for CDK
  - _Requirements: 5.1, 5.2_

- [x] 2. Implement CDK infrastructure stack
  - [x] 2.1 Create CDK app entry point (`cdk/bin/app.ts`)
    - Import and instantiate the MCP Tools Stack
    - Configure AWS account and region from environment
    - _Requirements: 5.1, 5.2_
  
  - [x] 2.2 Create Lambda function stack (`cdk/lib/mcp-tools-stack.ts`)
    - Define Lambda function with Python 3.12 runtime
    - Configure memory (128MB), timeout (30s), and handler path
    - Set AUTH_TOKEN environment variable
    - Point code asset to `../lambda/src` directory
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 2.3 Add Lambda Function URL to stack
    - Configure Function URL with NONE auth type
    - Enable CORS for all origins and GET method
    - Add explicit InvokeFunctionUrl permission
    - Output Function URL in CloudFormation
    - _Requirements: 2.1, 2.2, 3.1, 3.2_

- [x] 3. Create Lambda handler with routing
  - [x] 3.1 Set up Lambda project structure
    - Create `lambda/src/` directory
    - Create `lambda/tests/` directory
    - Add `__init__.py` files if needed
    - _Requirements: 2.1_
  
  - [x] 3.2 Implement main handler function (`lambda/src/handler.py`)
    - Parse incoming HTTP event (path, query parameters, method)
    - Route to appropriate handler based on path
    - Return standardized HTTP response format
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 3.3 Implement HTML serving route
    - Read `index.html` file from same directory
    - Return HTML with 200 status and text/html content-type
    - Handle file not found errors gracefully
    - _Requirements: 3.1_
  
  - [x] 3.4 Implement token validation route
    - Extract token from query parameters
    - Compare with AUTH_TOKEN environment variable
    - Return JSON with success boolean (no 403 on failure)
    - _Requirements: 3.2, 3.3, 10.1_
  
  - [x] 3.5 Implement tool execution route
    - Extract tool name from URL path
    - Validate token (return 403 if invalid)
    - Parse tool parameters from query string
    - Route to appropriate mock data generator
    - Return JSON response with success/error format
    - _Requirements: 2.1, 2.2, 2.4, 4.2, 4.3_

- [x] 4. Create mock data generators
  - [x] 4.1 Create mock data module (`lambda/src/mock_data.py`)
    - Define all 14 mock data generator functions
    - Each function accepts params dict and returns data dict
    - Use realistic dummy data matching expected schemas
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 6.1_
  
  - [x] 4.2 Implement core stock tools mock data
    - `mock_get_stock_quote`: symbol, price, volume, market cap
    - `mock_get_multiple_quotes`: array of quote objects
    - `mock_get_fundamentals`: PE ratio, EPS, dividend yield
    - `mock_get_enhanced_fundamentals`: fundamentals + earnings + ratings
    - _Requirements: 1.2, 6.2, 6.3_
  
  - [x] 4.3 Implement historical data tools mock data
    - `mock_get_historical`: array of OHLCV data points
    - `mock_get_intraday`: array of intraday price data
    - Include timestamps and proper date formatting
    - _Requirements: 1.2, 6.1_
  
  - [x] 4.4 Implement options tools mock data
    - `mock_get_options_chain`: strikes, premiums, volume, OI
    - `mock_get_option_greeks`: detailed Greeks for specific option
    - Include both calls and puts with realistic ATM data
    - _Requirements: 1.4, 6.4_
  
  - [x] 4.5 Implement technical and utility tools mock data
    - `mock_get_indicators`: technical indicator values
    - `mock_get_supported_indicators`: list of available indicators
    - `mock_get_provider_status`: provider health status
    - `mock_search_symbols`: symbol search results
    - `mock_get_market_status`: market open/close status
    - `mock_get_earnings_calendar`: upcoming earnings dates
    - _Requirements: 1.2, 6.1_

- [x] 5. Build web UI with authentication
  - [x] 5.1 Create HTML structure (`lambda/src/index.html`)
    - Define login page section with secret input
    - Define tools page section (hidden by default)
    - Add viewport meta tag for mobile responsiveness
    - _Requirements: 3.1, 3.2, 9.1, 9.2_
  
  - [x] 5.2 Implement CSS styling
    - Responsive layout for desktop and mobile
    - Clean, modern design with good contrast
    - Form styling for inputs and buttons
    - JSON output formatting with monospace font
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [x] 5.3 Implement login functionality (JavaScript)
    - Get token from input field
    - Call `/validate` endpoint
    - Store token in sessionStorage on success
    - Show tools page and hide login page
    - Display error message on failure
    - _Requirements: 3.2, 3.3, 10.1, 10.2_
  
  - [x] 5.4 Implement logout functionality (JavaScript)
    - Clear sessionStorage
    - Hide tools page and show login page
    - Reset form inputs
    - _Requirements: 3.5, 10.2_
  
  - [x] 5.5 Implement session check on page load (JavaScript)
    - Check for token in sessionStorage
    - If exists, show tools page directly
    - If not, show login page
    - _Requirements: 3.4, 10.1_

- [x] 6. Build tool execution interface
  - [x] 6.1 Create tool selector dropdown
    - Add all 14 tools as options
    - Display user-friendly tool names
    - Trigger parameter update on selection change
    - _Requirements: 4.1, 6.1_
  
  - [x] 6.2 Implement dynamic parameter inputs
    - Show/hide parameter inputs based on selected tool
    - Common parameters: symbol (text input)
    - Historical parameters: interval, start_date, end_date
    - Options parameters: expiration_date
    - _Requirements: 4.2, 4.5_
  
  - [x] 6.3 Implement tool execution function (JavaScript)
    - Get selected tool and parameter values
    - Get token from sessionStorage
    - Build query string with token and parameters
    - Call `/tools/<tool_name>` endpoint
    - Display response in result container
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [x] 6.4 Implement JSON response formatting
    - Pretty-print JSON with indentation
    - Add syntax highlighting (optional)
    - Handle both success and error responses
    - Scroll to result after execution
    - _Requirements: 4.3, 4.4_

- [x] 7. Add error handling and logging
  - [x] 7.1 Implement Lambda error handling
    - Wrap handler in try-except block
    - Log errors to CloudWatch with context
    - Return 500 error with generic message
    - Sanitize token from logs
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 7.2 Implement request logging
    - Log tool name and parameters (without token)
    - Log execution time
    - Log response status code
    - _Requirements: 7.4_
  
  - [x] 7.3 Implement UI error handling
    - Display error messages in result container
    - Style errors differently from success responses
    - Handle network errors gracefully
    - Provide clear error messages to users
    - _Requirements: 4.4, 7.2_

- [x] 8. Create deployment configuration
  - [x] 8.1 Create deploy.sh script
    - Prompt user for AWS profile name
    - Prompt user for AWS region (default: us-east-1)
    - Navigate to cdk/ directory
    - Install npm dependencies
    - Build TypeScript
    - Show instructions for bootstrap and deploy commands
    - DO NOT automatically deploy
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 8.2 Make deploy.sh executable and create README
    - Set execute permissions (chmod +x)
    - Create deployment instructions in README-webtool.md
    - Document manual bootstrap and deploy steps
    - _Requirements: 5.1_

- [ ]* 9. Write unit tests for Lambda handler
  - [ ]* 9.1 Create test file (`lambda/tests/test_handler.py`)
    - Test HTML serving route returns 200 with HTML content
    - Test validate route with correct token returns success
    - Test validate route with incorrect token returns failure
    - Test tool execution with valid token returns mock data
    - Test tool execution with invalid token returns 403
    - _Requirements: 2.1, 2.2, 2.4, 2.5_
  
  - [ ]* 9.2 Create test file for mock data (`lambda/tests/test_mock_data.py`)
    - Test each mock generator returns expected schema
    - Test mock generators handle missing parameters gracefully
    - Test mock generators use default values appropriately
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 10. Write integration tests
  - [ ]* 10.1 Create integration test file (`lambda/tests/test_integration.py`)
    - Test full Lambda invocation for HTML route
    - Test full Lambda invocation for validate route
    - Test full Lambda invocation for tool execution route
    - Test error scenarios (missing token, invalid tool, etc.)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 11. Manual testing and validation
  - [x] 11.1 Prepare for deployment testing
    - Review deploy.sh script
    - Verify all files are in correct locations
    - Document deployment steps for user
    - Note: Actual AWS deployment will be done by user
    - _Requirements: 3.1, 3.2, 3.3, 5.1, 5.2_
  
  - [x] 11.2 Create testing checklist for user
    - Document how to test all 14 tools via web interface
    - Document mobile responsiveness testing steps
    - Document session management testing steps
    - Document security verification steps
    - Note: These tests will be performed by user after deployment
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.3, 6.4, 9.1, 9.2, 9.3, 9.4, 10.1, 10.2_

- [x] 12. Documentation and cleanup
  - [x] 12.1 Update README-webtool.md
    - Document deployment process
    - Document usage instructions
    - Add troubleshooting section
    - _Requirements: 5.1, 5.2_
  
  - [x] 12.2 Verify project structure matches design
    - Confirm all files are in correct locations
    - Verify cdk/ and lambda/ separation
    - Check that all required files exist
    - _Requirements: 5.1_
