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
exports.McpToolsStack = void 0;
const cdk = __importStar(require("aws-cdk-lib"));
const lambda = __importStar(require("aws-cdk-lib/aws-lambda"));
const path = __importStar(require("path"));
class McpToolsStack extends cdk.Stack {
    constructor(scope, id, props) {
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
exports.McpToolsStack = McpToolsStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoibWNwLXRvb2xzLXN0YWNrLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsibWNwLXRvb2xzLXN0YWNrLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQUFBLGlEQUFtQztBQUNuQywrREFBaUQ7QUFFakQsMkNBQTZCO0FBRTdCLE1BQWEsYUFBYyxTQUFRLEdBQUcsQ0FBQyxLQUFLO0lBQzFDLFlBQVksS0FBZ0IsRUFBRSxFQUFVLEVBQUUsS0FBc0I7UUFDOUQsS0FBSyxDQUFDLEtBQUssRUFBRSxFQUFFLEVBQUUsS0FBSyxDQUFDLENBQUM7UUFFeEIsa0JBQWtCO1FBQ2xCLE1BQU0sZ0JBQWdCLEdBQUcsSUFBSSxNQUFNLENBQUMsUUFBUSxDQUFDLElBQUksRUFBRSxrQkFBa0IsRUFBRTtZQUNyRSxPQUFPLEVBQUUsTUFBTSxDQUFDLE9BQU8sQ0FBQyxXQUFXO1lBQ25DLE9BQU8sRUFBRSxpQkFBaUI7WUFDMUIsSUFBSSxFQUFFLE1BQU0sQ0FBQyxJQUFJLENBQUMsU0FBUyxDQUFDLElBQUksQ0FBQyxJQUFJLENBQUMsU0FBUyxFQUFFLGtCQUFrQixDQUFDLENBQUM7WUFDckUsVUFBVSxFQUFFLEdBQUc7WUFDZixPQUFPLEVBQUUsR0FBRyxDQUFDLFFBQVEsQ0FBQyxPQUFPLENBQUMsRUFBRSxDQUFDO1lBQ2pDLFdBQVcsRUFBRTtnQkFDWCxVQUFVLEVBQUUsVUFBVTthQUN2QjtZQUNELFdBQVcsRUFBRSxvRUFBb0U7U0FDbEYsQ0FBQyxDQUFDO1FBRUgsa0NBQWtDO1FBQ2xDLE1BQU0sV0FBVyxHQUFHLGdCQUFnQixDQUFDLGNBQWMsQ0FBQztZQUNsRCxRQUFRLEVBQUUsTUFBTSxDQUFDLG1CQUFtQixDQUFDLElBQUk7WUFDekMsSUFBSSxFQUFFO2dCQUNKLGNBQWMsRUFBRSxDQUFDLEdBQUcsQ0FBQztnQkFDckIsY0FBYyxFQUFFLENBQUMsTUFBTSxDQUFDLFVBQVUsQ0FBQyxHQUFHLENBQUM7Z0JBQ3ZDLGNBQWMsRUFBRSxDQUFDLEdBQUcsQ0FBQztnQkFDckIsTUFBTSxFQUFFLEdBQUcsQ0FBQyxRQUFRLENBQUMsS0FBSyxDQUFDLENBQUMsQ0FBQzthQUM5QjtTQUNGLENBQUMsQ0FBQztRQUVILDBCQUEwQjtRQUMxQixJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLGFBQWEsRUFBRTtZQUNyQyxLQUFLLEVBQUUsV0FBVyxDQUFDLEdBQUc7WUFDdEIsV0FBVyxFQUFFLGlEQUFpRDtZQUM5RCxVQUFVLEVBQUUscUJBQXFCO1NBQ2xDLENBQUMsQ0FBQztRQUVILDBCQUEwQjtRQUMxQixJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLGFBQWEsRUFBRTtZQUNyQyxLQUFLLEVBQUUsZ0JBQWdCLENBQUMsV0FBVztZQUNuQyxXQUFXLEVBQUUscUJBQXFCO1NBQ25DLENBQUMsQ0FBQztJQUNMLENBQUM7Q0FDRjtBQXpDRCxzQ0F5Q0MiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgKiBhcyBjZGsgZnJvbSAnYXdzLWNkay1saWInO1xuaW1wb3J0ICogYXMgbGFtYmRhIGZyb20gJ2F3cy1jZGstbGliL2F3cy1sYW1iZGEnO1xuaW1wb3J0IHsgQ29uc3RydWN0IH0gZnJvbSAnY29uc3RydWN0cyc7XG5pbXBvcnQgKiBhcyBwYXRoIGZyb20gJ3BhdGgnO1xuXG5leHBvcnQgY2xhc3MgTWNwVG9vbHNTdGFjayBleHRlbmRzIGNkay5TdGFjayB7XG4gIGNvbnN0cnVjdG9yKHNjb3BlOiBDb25zdHJ1Y3QsIGlkOiBzdHJpbmcsIHByb3BzPzogY2RrLlN0YWNrUHJvcHMpIHtcbiAgICBzdXBlcihzY29wZSwgaWQsIHByb3BzKTtcblxuICAgIC8vIExhbWJkYSBGdW5jdGlvblxuICAgIGNvbnN0IG1jcFRvb2xzRnVuY3Rpb24gPSBuZXcgbGFtYmRhLkZ1bmN0aW9uKHRoaXMsICdNY3BUb29sc0Z1bmN0aW9uJywge1xuICAgICAgcnVudGltZTogbGFtYmRhLlJ1bnRpbWUuUFlUSE9OXzNfMTIsXG4gICAgICBoYW5kbGVyOiAnaGFuZGxlci5oYW5kbGVyJyxcbiAgICAgIGNvZGU6IGxhbWJkYS5Db2RlLmZyb21Bc3NldChwYXRoLmpvaW4oX19kaXJuYW1lLCAnLi4vLi4vbGFtYmRhL3NyYycpKSxcbiAgICAgIG1lbW9yeVNpemU6IDEyOCxcbiAgICAgIHRpbWVvdXQ6IGNkay5EdXJhdGlvbi5zZWNvbmRzKDMwKSxcbiAgICAgIGVudmlyb25tZW50OiB7XG4gICAgICAgIEFVVEhfVE9LRU46ICdkZGdAOTgxMicsXG4gICAgICB9LFxuICAgICAgZGVzY3JpcHRpb246ICdNQ1AgVG9vbHMgV2ViIEludGVyZmFjZSAtIFNlcnZlcyBVSSBhbmQgZXhlY3V0ZXMgbWFya2V0IGRhdGEgdG9vbHMnLFxuICAgIH0pO1xuXG4gICAgLy8gRnVuY3Rpb24gVVJMIHdpdGggcHVibGljIGFjY2Vzc1xuICAgIGNvbnN0IGZ1bmN0aW9uVXJsID0gbWNwVG9vbHNGdW5jdGlvbi5hZGRGdW5jdGlvblVybCh7XG4gICAgICBhdXRoVHlwZTogbGFtYmRhLkZ1bmN0aW9uVXJsQXV0aFR5cGUuTk9ORSxcbiAgICAgIGNvcnM6IHtcbiAgICAgICAgYWxsb3dlZE9yaWdpbnM6IFsnKiddLFxuICAgICAgICBhbGxvd2VkTWV0aG9kczogW2xhbWJkYS5IdHRwTWV0aG9kLkdFVF0sXG4gICAgICAgIGFsbG93ZWRIZWFkZXJzOiBbJyonXSxcbiAgICAgICAgbWF4QWdlOiBjZGsuRHVyYXRpb24uaG91cnMoMSksXG4gICAgICB9LFxuICAgIH0pO1xuXG4gICAgLy8gT3V0cHV0IHRoZSBGdW5jdGlvbiBVUkxcbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnRnVuY3Rpb25VcmwnLCB7XG4gICAgICB2YWx1ZTogZnVuY3Rpb25VcmwudXJsLFxuICAgICAgZGVzY3JpcHRpb246ICdMYW1iZGEgRnVuY3Rpb24gVVJMIGZvciBNQ1AgVG9vbHMgV2ViIEludGVyZmFjZScsXG4gICAgICBleHBvcnROYW1lOiAnTWNwVG9vbHNGdW5jdGlvblVybCcsXG4gICAgfSk7XG5cbiAgICAvLyBPdXRwdXQgdGhlIEZ1bmN0aW9uIEFSTlxuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdGdW5jdGlvbkFybicsIHtcbiAgICAgIHZhbHVlOiBtY3BUb29sc0Z1bmN0aW9uLmZ1bmN0aW9uQXJuLFxuICAgICAgZGVzY3JpcHRpb246ICdMYW1iZGEgRnVuY3Rpb24gQVJOJyxcbiAgICB9KTtcbiAgfVxufVxuIl19