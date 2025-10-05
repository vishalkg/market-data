#!/usr/bin/env node
"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
require("source-map-support/register");
const cdk = __importStar(require("aws-cdk-lib"));
const mcp_tools_stack_1 = require("../lib/mcp-tools-stack");
const app = new cdk.App();
// Get AWS account and region from environment
// These will be automatically detected from AWS CLI configuration
const account = process.env.CDK_DEFAULT_ACCOUNT;
const region = process.env.CDK_DEFAULT_REGION || 'us-west-2';
new mcp_tools_stack_1.McpToolsStack(app, 'McpToolsWebStack', {
    env: {
        account: account,
        region: region,
    },
    description: 'MCP Tools Web Interface - Lambda Function with HTTPS endpoint',
});
app.synth();
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiYXBwLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiYXBwLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQUNBLHVDQUFxQztBQUNyQyxpREFBbUM7QUFDbkMsNERBQXVEO0FBRXZELE1BQU0sR0FBRyxHQUFHLElBQUksR0FBRyxDQUFDLEdBQUcsRUFBRSxDQUFDO0FBRTFCLDhDQUE4QztBQUM5QyxrRUFBa0U7QUFDbEUsTUFBTSxPQUFPLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxtQkFBbUIsQ0FBQztBQUNoRCxNQUFNLE1BQU0sR0FBRyxPQUFPLENBQUMsR0FBRyxDQUFDLGtCQUFrQixJQUFJLFdBQVcsQ0FBQztBQUU3RCxJQUFJLCtCQUFhLENBQUMsR0FBRyxFQUFFLGtCQUFrQixFQUFFO0lBQ3pDLEdBQUcsRUFBRTtRQUNILE9BQU8sRUFBRSxPQUFPO1FBQ2hCLE1BQU0sRUFBRSxNQUFNO0tBQ2Y7SUFDRCxXQUFXLEVBQUUsK0RBQStEO0NBQzdFLENBQUMsQ0FBQztBQUVILEdBQUcsQ0FBQyxLQUFLLEVBQUUsQ0FBQyIsInNvdXJjZXNDb250ZW50IjpbIiMhL3Vzci9iaW4vZW52IG5vZGVcbmltcG9ydCAnc291cmNlLW1hcC1zdXBwb3J0L3JlZ2lzdGVyJztcbmltcG9ydCAqIGFzIGNkayBmcm9tICdhd3MtY2RrLWxpYic7XG5pbXBvcnQgeyBNY3BUb29sc1N0YWNrIH0gZnJvbSAnLi4vbGliL21jcC10b29scy1zdGFjayc7XG5cbmNvbnN0IGFwcCA9IG5ldyBjZGsuQXBwKCk7XG5cbi8vIEdldCBBV1MgYWNjb3VudCBhbmQgcmVnaW9uIGZyb20gZW52aXJvbm1lbnRcbi8vIFRoZXNlIHdpbGwgYmUgYXV0b21hdGljYWxseSBkZXRlY3RlZCBmcm9tIEFXUyBDTEkgY29uZmlndXJhdGlvblxuY29uc3QgYWNjb3VudCA9IHByb2Nlc3MuZW52LkNES19ERUZBVUxUX0FDQ09VTlQ7XG5jb25zdCByZWdpb24gPSBwcm9jZXNzLmVudi5DREtfREVGQVVMVF9SRUdJT04gfHwgJ3VzLXdlc3QtMic7XG5cbm5ldyBNY3BUb29sc1N0YWNrKGFwcCwgJ01jcFRvb2xzV2ViU3RhY2snLCB7XG4gIGVudjoge1xuICAgIGFjY291bnQ6IGFjY291bnQsXG4gICAgcmVnaW9uOiByZWdpb24sXG4gIH0sXG4gIGRlc2NyaXB0aW9uOiAnTUNQIFRvb2xzIFdlYiBJbnRlcmZhY2UgLSBMYW1iZGEgRnVuY3Rpb24gd2l0aCBIVFRQUyBlbmRwb2ludCcsXG59KTtcblxuYXBwLnN5bnRoKCk7XG4iXX0=