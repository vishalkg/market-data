import json
import os
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def create_response(status_code: int, body: Any, content_type: str = 'application/json') -> Dict[str, Any]:
    """Create standardized HTTP response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': content_type,
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': '*',
        },
        'body': json.dumps(body) if content_type == 'application/json' else body
    }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for HTTP requests
    
    Routes:
    - GET / or /index.html -> Serve HTML UI
    - GET /validate?token=X -> Validate authentication token
    - GET /tools/<tool_name>?token=X&params -> Execute tool with mock data
    """
    try:
        # Extract request information
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        raw_path = event.get('rawPath', '/')
        query_params = event.get('queryStringParameters') or {}
        
        # Log request (sanitize token)
        safe_params = {k: v for k, v in query_params.items() if k != 'token'}
        logger.info(f"Request: {http_method} {raw_path} params={safe_params}")
        
        # Route based on path
        if raw_path == '/' or raw_path == '/index.html':
            return serve_html()
        elif raw_path == '/validate':
            return validate_token(query_params)
        elif raw_path.startswith('/tools/'):
            tool_name = raw_path.split('/tools/')[-1]
            return execute_tool(tool_name, query_params)
        else:
            return create_response(404, {
                'success': False,
                'error': 'Not found',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return create_response(500, {
            'success': False,
            'error': 'Internal server error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

def serve_html() -> Dict[str, Any]:
    """Serve the HTML UI from index.html file"""
    try:
        # Read index.html from the same directory
        html_path = os.path.join(os.path.dirname(__file__), 'index.html')
        with open(html_path, 'r') as f:
            html_content = f.read()
        
        return create_response(200, html_content, content_type='text/html')
    except FileNotFoundError:
        logger.error("index.html not found")
        return create_response(500, {
            'success': False,
            'error': 'UI file not found',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    except Exception as e:
        logger.error(f"Error serving HTML: {str(e)}")
        return create_response(500, {
            'success': False,
            'error': 'Error loading UI',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

def validate_token(query_params: Dict[str, str]) -> Dict[str, Any]:
    """Validate authentication token"""
    try:
        provided_token = query_params.get('token', '')
        expected_token = os.environ.get('AUTH_TOKEN', 'ddg@9812')
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = provided_token == expected_token
        
        # Log validation attempt (without exposing token)
        logger.info(f"Token validation: {'success' if is_valid else 'failure'}")
        
        return create_response(200, {
            'success': is_valid
        })
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return create_response(200, {
            'success': False
        })

def execute_tool(tool_name: str, query_params: Dict[str, str]) -> Dict[str, Any]:
    """Execute tool and return mock data"""
    try:
        # Validate token first
        provided_token = query_params.get('token', '')
        expected_token = os.environ.get('AUTH_TOKEN', 'ddg@9812')
        
        if provided_token != expected_token:
            logger.warning(f"Unauthorized tool execution attempt: {tool_name}")
            return create_response(403, {
                'success': False,
                'error': 'Unauthorized',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        # Import mock data generators
        from mock_data import get_mock_data
        
        # Get mock data for the tool
        mock_data = get_mock_data(tool_name, query_params)
        
        if mock_data is None:
            return create_response(400, {
                'success': False,
                'error': f'Unknown tool: {tool_name}',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        # Log successful execution
        safe_params = {k: v for k, v in query_params.items() if k != 'token'}
        logger.info(f"Tool executed: {tool_name} params={safe_params}")
        
        return create_response(200, {
            'success': True,
            'data': mock_data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
        return create_response(500, {
            'success': False,
            'error': 'Tool execution failed',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
