#!/bin/bash

# MCP Tools Web Interface - Deployment Script
# This script prepares the CDK project for deployment

set -e  # Exit on error

echo "========================================="
echo "MCP Tools Web Interface - Deployment"
echo "========================================="
echo ""

# Prompt for AWS profile
read -p "Enter your AWS profile name (default: personal): " AWS_PROFILE
AWS_PROFILE=${AWS_PROFILE:-personal}

# Prompt for AWS region
read -p "Enter your AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

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

echo ""
echo "✅ Build complete!"
echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "1. Bootstrap CDK (first time only):"
echo "   cd cdk"
echo "   npx cdk bootstrap --profile $AWS_PROFILE"
echo ""
echo "2. Deploy the stack:"
echo "   npx cdk deploy --profile $AWS_PROFILE"
echo ""
echo "3. After deployment, you'll receive a Function URL"
echo "   Open it in your browser and login with:"
echo "   Token: ddg@9812"
echo ""
echo "4. To destroy the stack later:"
echo "   npx cdk destroy --profile $AWS_PROFILE"
echo ""
echo "========================================="
