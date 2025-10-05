#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { McpToolsStack } from '../lib/mcp-tools-stack';

const app = new cdk.App();

// Get AWS account and region from environment
// These will be automatically detected from AWS CLI configuration
const account = process.env.CDK_DEFAULT_ACCOUNT;
const region = process.env.CDK_DEFAULT_REGION || 'us-west-2';

new McpToolsStack(app, 'McpToolsWebStack', {
  env: {
    account: account,
    region: region,
  },
  description: 'MCP Tools Web Interface - Lambda Function with HTTPS endpoint',
});

app.synth();
