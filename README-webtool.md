# MCP Tools HTTP Endpoint

Expose MCP tools via HTTPS with a web interface. Access from any device with token-based authentication.

## Quick Start

**Prepare for deployment:**
```bash
./deploy.sh
```

This will:
- Prompt for your AWS profile and region
- Install CDK dependencies
- Build the TypeScript code
- Show you the next steps for deployment

**Deploy to AWS:**
```bash
cd cdk

# First time only - bootstrap CDK
npx cdk bootstrap --profile YOUR_PROFILE

# Deploy the stack
npx cdk deploy --profile YOUR_PROFILE
```

**Access:**
1. Copy the Function URL from deployment output
2. Open it in your browser
3. Enter secret: `ddg@9812`
4. Use the tools interface

## Features

- ✅ HTTPS endpoint (AWS-managed SSL)
- ✅ Two-page gated UI (login + tools)
- ✅ Token-based authentication
- ✅ Works on desktop and mobile
- ✅ No IP restrictions
- ✅ ~$0.50/month cost

## Architecture

```
Browser → Lambda Function URL → Lambda (Python) → Tool Execution
                              ↓
                           HTML UI
```

## Configuration

**Change token:**
Edit `cdk/lib/mcp-tools-stack.ts`:
```typescript
environment: {
  AUTH_TOKEN: 'your-new-token',
}
```

Then rebuild and redeploy:
```bash
cd cdk
npm run build
npx cdk deploy --profile YOUR_PROFILE
```

## Project Structure

```
.
├── deploy.sh              # Deployment preparation script
├── DESIGN.md              # Full design document
├── cdk/                   # CDK infrastructure code
│   ├── bin/app.ts        # CDK entry point
│   ├── lib/mcp-tools-stack.ts # Infrastructure definition
│   ├── package.json      # Node.js dependencies
│   └── tsconfig.json     # TypeScript config
└── lambda/                # Lambda application code
    ├── src/
    │   ├── handler.py    # Lambda function
    │   ├── mock_data.py  # Mock data generators
    │   └── index.html    # Web UI
    └── tests/            # Test files
```

## Usage

### Desktop
1. Open Function URL
2. Enter secret
3. Enter object and property
4. Click Execute

### Mobile
1. Bookmark Function URL
2. Same workflow as desktop

## Adding Your MCP Tools

Edit `lambda/handler.py` in the `execute_tool()` function:

```python
def execute_tool(obj, prop, params):
    if obj == 'myobject' and prop == 'myproperty':
        # Your tool logic here
        return {'result': 'your data'}
    
    return {'result': f'Executed {obj}.{prop}'}
```

Redeploy: `./deploy.sh`

## API Endpoints

- `GET /` - HTML UI
- `GET /validate?token=SECRET` - Validate token
- `GET /<object>/<property>?token=SECRET` - Execute tool

## Cleanup

```bash
npx cdk destroy
```

## Cost

~$0.50/month for 400 requests/month (20/day)

## Requirements

- AWS CLI configured
- Node.js (for CDK)
- AWS account

## Security

- HTTPS by default
- Token-based auth
- Session-based access
- No hints on login page

See [DESIGN.md](DESIGN.md) for full details.
