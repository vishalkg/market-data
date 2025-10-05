# MCP Tools HTTP Endpoint - Design Document

## Overview
Expose MCP (Model Context Protocol) server tools as HTTPS endpoints accessible from any device (desktop/mobile) via a web interface. Enables tool execution when MCP integration is unavailable.

## Architecture

```
Browser → Lambda Function URL (HTTPS) → Lambda Handler → Tool Execution
                                      ↓
                                   HTML UI (served from Lambda)
```

**Components:**
- **Lambda Function**: Python 3.12 runtime
- **Lambda Function URL**: Public HTTPS endpoint (AWS-managed SSL)
- **HTML UI**: Single-page app with login gate, served from Lambda
- **CDK**: Infrastructure as Code (TypeScript)

## Security Model

### Two-Page Gating
1. **Login Page**: Secret input only, no hints or branding
2. **Tools Page**: Object/property inputs, requires valid session

### Token-Based Authentication
- Secret token stored in Lambda environment variable
- Validated via `/validate` endpoint on login
- Stored in browser sessionStorage (cleared on logout/close)
- All API calls include token in query parameter

### Access Control
- Login page: Public (no auth)
- `/validate` endpoint: Returns success/failure (no 403)
- Tool endpoints: 403 if invalid/missing token
- Auto-logout on token expiration

## API Routes

### `GET /`
Returns HTML UI (login page)

### `GET /validate?token=SECRET`
Validates token for login
- Response: `{"success": true/false}`

### `GET /<object>/<property>?token=SECRET`
Executes MCP tool
- Success: `{"success": true, "data": {...}, "timestamp": "..."}`
- Failure: `{"success": false, "error": "..."}`

## Implementation Details

### Lambda Handler (`lambda/handler.py`)
```python
- Serves HTML on `/` and `/index.html`
- Validates token on `/validate`
- Routes tool requests to execute_tool()
- Token stored in AUTH_TOKEN environment variable
```

### HTML UI (`lambda/index.html`)
```
- Login page: Secret input → validates via /validate
- Tools page: Object/property inputs → calls /<obj>/<prop>
- Client-side routing with sessionStorage
- Logout clears session and returns to login
```

### CDK Stack (`lib/mcp-tools-stack.ts`)
```typescript
- Lambda Function with Python 3.12
- Function URL with NONE auth type
- Explicit InvokeFunctionUrl permission
- CORS enabled for browser access
- AUTH_TOKEN hardcoded in environment
```

### Deployment (`deploy.sh`)
```bash
- Installs dependencies
- Builds TypeScript
- Bootstraps CDK (first time)
- Deploys stack
```

## Project Structure

```
.
├── DESIGN.md                    # This file
├── README.md                    # Usage instructions
├── deploy.sh                    # One-click deployment
├── bin/
│   └── app.ts                  # CDK app entry point
├── lib/
│   └── mcp-tools-stack.ts      # CDK stack definition
├── lambda/
│   ├── handler.py              # Lambda function code
│   └── index.html              # HTML UI template
├── package.json
├── tsconfig.json
└── cdk.json
```

## Configuration

### Token
Hardcoded in `lib/mcp-tools-stack.ts`:
```typescript
environment: {
  AUTH_TOKEN: 'ddg@9812',
}
```

To change: Edit stack file and redeploy.

### AWS Settings
In `deploy.sh`:
- AWS_REGION: us-east-1
- AWS_ACCOUNT: 368253648705
- AWS_PROFILE: default

## Deployment

### First Time
```bash
./deploy.sh
```

### Updates
```bash
./deploy.sh
```

### Cleanup
```bash
npx cdk destroy
```

## Usage

### Desktop
1. Open Function URL in browser
2. Enter secret: `ddg@9812`
3. Enter object and property
4. Click Execute
5. View JSON response

### Mobile
1. Bookmark Function URL
2. Same workflow as desktop
3. Works on any network (WiFi, cellular, etc.)

## Cost Estimation

**Monthly cost (20 calls/day = ~400 calls/month):**
- Lambda invocations: $0.0001
- Lambda compute: $0.0001
- CloudWatch Logs: $0.50
- **Total: ~$0.50/month**

## Technical Specifications

### Lambda Configuration
- Runtime: Python 3.12
- Memory: 128 MB
- Timeout: 30 seconds
- Handler: handler.handler

### Function URL
- Auth Type: NONE (public)
- CORS: Enabled (all origins, GET method)
- Protocol: HTTPS (AWS-managed certificate)
- Invoke Mode: BUFFERED

### Browser Requirements
- Modern browser (Chrome, Safari, Firefox, Edge)
- JavaScript enabled
- sessionStorage support

## Security Considerations

**Strengths:**
- HTTPS by default (AWS-managed SSL)
- Token-based authentication
- No hints on login page
- Session-based (cleared on logout)
- Token not visible in page source

**Limitations:**
- Token in URL query parameters (mitigated by HTTPS)
- No rate limiting (acceptable for personal use)
- sessionStorage cleared on browser close (by design)

**Acceptable for:**
- Personal/side projects
- Low traffic (~20 calls/day)
- Trusted devices

## Adding MCP Tools

Edit `lambda/handler.py` in the `execute_tool()` function:

```python
def execute_tool(obj, prop, params):
    """Execute MCP tool logic"""
    
    # Add your tool implementations here
    if obj == 'myobject' and prop == 'myproperty':
        # Your logic here
        return {'result': 'your data'}
    
    # Default response
    return {
        'tool': f'{obj}/{prop}',
        'params': {k: v for k, v in params.items() if k != 'token'},
        'result': f'Executed {obj}.{prop}'
    }
```

Redeploy: `./deploy.sh`

## Troubleshooting

### 403 Forbidden Error
- Check Lambda resource policy has `InvokeFunctionUrl` permission
- Verify Function URL auth type is NONE
- CDK stack includes explicit permission grant

### Token Not Working
- Verify AUTH_TOKEN in Lambda environment matches your secret
- Check token is URL-encoded in requests
- Confirm no extra spaces in token

### HTML Not Loading
- Check Function URL is accessible
- Verify Lambda has correct handler path
- Ensure index.html is in lambda/ directory

## Success Criteria

✅ Lambda Function URL accessible via HTTPS  
✅ Login page shows only secret input  
✅ Invalid secret shows "Access Denied"  
✅ Valid secret grants access to tools page  
✅ Tool execution returns JSON response  
✅ Works on desktop and mobile browsers  
✅ Session persists until logout or browser close  
✅ Cost under $1/month for expected usage  

## Future Enhancements

**If needed:**
- API Gateway for custom domain
- CloudFront for global CDN
- DynamoDB for request logging
- Rate limiting per IP/token
- Multiple user support
- Query parameter inputs in UI

**Current implementation is sufficient for:**
- Personal use
- 20 calls/day
- Single user
- Simple tool execution
