import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import * as path from 'path';

export class McpToolsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda Function
    const mcpToolsFunction = new lambda.Function(this, 'McpToolsFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda/src')),
      memorySize: 128,
      timeout: cdk.Duration.seconds(30),
      environment: {
        AUTH_TOKEN: 'ddg@9812',
      },
      description: 'MCP Tools Web Interface - Serves UI and executes market data tools',
    });

    // Function URL with public access
    const functionUrl = mcpToolsFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ['*'],
        allowedMethods: [lambda.HttpMethod.GET],
        allowedHeaders: ['*'],
        maxAge: cdk.Duration.hours(1),
      },
    });

    // Output the Function URL
    new cdk.CfnOutput(this, 'FunctionUrl', {
      value: functionUrl.url,
      description: 'Lambda Function URL for MCP Tools Web Interface',
      exportName: 'McpToolsFunctionUrl',
    });

    // Output the Function ARN
    new cdk.CfnOutput(this, 'FunctionArn', {
      value: mcpToolsFunction.functionArn,
      description: 'Lambda Function ARN',
    });
  }
}
