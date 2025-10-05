#!/bin/bash

# MCP Tools Web Interface - Deployment Script
# This script deploys the CDK stack to AWS

set -e  # Exit on error

# Configuration
AWS_PROFILE="personal"
AWS_REGION="us-west-2"

echo "========================================="
echo "MCP Tools Web Interface - Deployment"
echo "========================================="
echo ""
echo "Configuration:"
echo "  AWS Profile: $AWS_PROFILE"
echo "  AWS Region: $AWS_REGION"
echo ""

# Navigate to CDK directory
cd cdk

# Install Node.js dependencies
echo "📦 Installing CDK dependencies..."
npm install

# Build TypeScript
echo "🔨 Building CDK app..."
npm run build

# Check if CDK is bootstrapped
echo ""
echo "🚀 Checking CDK bootstrap status..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit --profile $AWS_PROFILE --region $AWS_REGION &> /dev/null; then
    echo "⚠️  CDK not bootstrapped. Bootstrapping now..."
    npx cdk bootstrap --profile $AWS_PROFILE --region $AWS_REGION
else
    echo "✅ CDK already bootstrapped"
fi

# Deploy the stack
echo ""
echo "🚀 Deploying stack..."
npx cdk deploy --profile $AWS_PROFILE --region $AWS_REGION --require-approval never

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Copy the Function URL from the output above"
echo "2. Open it in your browser"
echo "3. Login with token: ddg@9812"
echo ""
echo "To destroy the stack later:"
echo "  cd cdk"
echo "  npx cdk destroy --profile $AWS_PROFILE --region $AWS_REGION"
echo ""
echo "========================================="
