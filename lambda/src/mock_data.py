"""
Mock data generators for all 14 MCP tools
Returns realistic dummy data matching expected schemas
"""

from typing import Dict, Any, Optional

def get_mock_data(tool_name: str, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Route to appropriate mock data generator based on tool name
    
    Args:
        tool_name: Name of the tool to execute
        params: Query parameters (excluding token)
    
    Returns:
        Mock data dict or None if tool not found
    """
    # Map tool names to generator functions
    tool_map = {
        'get_stock_quote': mock_get_stock_quote,
        'get_multiple_quotes': mock_get_multiple_quotes,
        'get_fundamentals': mock_get_fundamentals,
        'get_enhanced_fundamentals': mock_get_enhanced_fundamentals,
        'get_historical': mock_get_historical,
        'get_intraday': mock_get_intraday,
        'get_indicators': mock_get_indicators,
        'get_supported_indicators': mock_get_supported_indicators,
        'get_options_chain': mock_get_options_chain,
        'get_option_greeks': mock_get_option_greeks,
        'get_provider_status': mock_get_provider_status,
        'search_symbols': mock_search_symbols,
        'get_market_status': mock_get_market_status,
        'get_earnings_calendar': mock_get_earnings_calendar,
    }
    
    generator = tool_map.get(tool_name)
    if generator:
        return generator(params)
    return None

# Stock quote tools

def mock_get_stock_quote(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock stock quote data"""
    symbol = params.get('symbol', 'AAPL')
    return {
        'symbol': symbol,
        'price': 175.43,
        'change': 2.15,
        'change_percent': 1.24,
        'volume': 52_000_000,
        'market_cap': 2_750_000_000_000,
        'high': 176.82,
        'low': 173.25,
        'open': 174.10,
        'previous_close': 173.28,
        'timestamp': '2025-01-04T16:00:00Z'
    }

def mock_get_multiple_quotes(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock data for multiple stock quotes"""
    symbols = params.get('symbols', 'AAPL,GOOGL,MSFT').split(',')
    quotes = []
    
    mock_data = {
        'AAPL': {'price': 175.43, 'change': 2.15, 'change_percent': 1.24},
        'GOOGL': {'price': 142.67, 'change': -1.23, 'change_percent': -0.85},
        'MSFT': {'price': 378.91, 'change': 3.45, 'change_percent': 0.92},
    }
    
    for symbol in symbols[:3]:  # Limit to 3 symbols
        symbol = symbol.strip().upper()
        data = mock_data.get(symbol, {'price': 100.00, 'change': 0.00, 'change_percent': 0.00})
        quotes.append({
            'symbol': symbol,
            'price': data['price'],
            'change': data['change'],
            'change_percent': data['change_percent'],
            'volume': 25_000_000,
            'timestamp': '2025-01-04T16:00:00Z'
        })
    
    return {'quotes': quotes}

# Fundamentals tools

def mock_get_fundamentals(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock fundamental data"""
    symbol = params.get('symbol', 'AAPL')
    return {
        'symbol': symbol,
        'company_name': 'Apple Inc.',
        'pe_ratio': 28.5,
        'eps': 6.15,
        'market_cap': 2_750_000_000_000,
        'dividend_yield': 0.52,
        'beta': 1.25,
        'fifty_two_week_high': 199.62,
        'fifty_two_week_low': 164.08,
        'average_volume': 58_000_000,
        'shares_outstanding': 15_700_000_000
    }

def mock_get_enhanced_fundamentals(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock enhanced fundamental data with earnings and ratings"""
    symbol = params.get('symbol', 'AAPL')
    base_fundamentals = mock_get_fundamentals(params)
    
    base_fundamentals['earnings'] = [
        {'quarter': 'Q4 2024', 'eps': 1.64, 'revenue': 119_580_000_000, 'date': '2024-11-01'},
        {'quarter': 'Q3 2024', 'eps': 1.53, 'revenue': 94_930_000_000, 'date': '2024-08-01'},
        {'quarter': 'Q2 2024', 'eps': 1.52, 'revenue': 90_753_000_000, 'date': '2024-05-02'},
        {'quarter': 'Q1 2024', 'eps': 1.46, 'revenue': 85_778_000_000, 'date': '2024-02-01'},
    ]
    
    base_fundamentals['analyst_ratings'] = {
        'buy': 18,
        'hold': 8,
        'sell': 2,
        'average_target': 195.50,
        'high_target': 250.00,
        'low_target': 150.00
    }
    
    return base_fundamentals

# Historical data tools

def mock_get_historical(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock historical price data"""
    symbol = params.get('symbol', 'AAPL')
    interval = params.get('interval', 'day')
    
    # Generate 22 trading days of data
    data_points = []
    base_price = 175.00
    
    for i in range(22):
        day_offset = 21 - i
        price_variation = (i % 5 - 2) * 2.5
        data_points.append({
            'date': f'2024-12-{str(10 + i).zfill(2)}',
            'open': round(base_price + price_variation, 2),
            'high': round(base_price + price_variation + 2.5, 2),
            'low': round(base_price + price_variation - 2.0, 2),
            'close': round(base_price + price_variation + 1.0, 2),
            'volume': 50_000_000 + (i * 1_000_000)
        })
    
    return {
        'symbol': symbol,
        'interval': interval,
        'data': data_points
    }

def mock_get_intraday(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock intraday price data"""
    symbol = params.get('symbol', 'AAPL')
    interval = params.get('interval', '5min')
    
    # Generate 78 intraday bars (6.5 hours of trading)
    data_points = []
    base_price = 175.00
    
    for i in range(78):
        hour = 9 + (i * 5) // 60
        minute = (i * 5) % 60
        price_variation = (i % 10 - 5) * 0.5
        
        data_points.append({
            'timestamp': f'2025-01-04T{str(hour).zfill(2)}:{str(minute).zfill(2)}:00Z',
            'open': round(base_price + price_variation, 2),
            'high': round(base_price + price_variation + 0.5, 2),
            'low': round(base_price + price_variation - 0.3, 2),
            'close': round(base_price + price_variation + 0.2, 2),
            'volume': 500_000 + (i * 10_000)
        })
    
    return {
        'symbol': symbol,
        'interval': interval,
        'data': data_points
    }

# Technical indicators tools

def mock_get_indicators(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock technical indicator data"""
    symbol = params.get('symbol', 'AAPL')
    indicator = params.get('indicator', 'SMA')
    
    return {
        'symbol': symbol,
        'indicator': indicator,
        'values': [
            {'date': '2025-01-04', 'value': 175.43},
            {'date': '2025-01-03', 'value': 174.28},
            {'date': '2025-01-02', 'value': 173.15},
            {'date': '2024-12-31', 'value': 172.89},
            {'date': '2024-12-30', 'value': 171.56},
        ],
        'parameters': {
            'period': 20,
            'time_period': 20
        }
    }

def mock_get_supported_indicators(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate list of supported technical indicators"""
    return {
        'indicators': [
            {'name': 'SMA', 'description': 'Simple Moving Average'},
            {'name': 'EMA', 'description': 'Exponential Moving Average'},
            {'name': 'RSI', 'description': 'Relative Strength Index'},
            {'name': 'MACD', 'description': 'Moving Average Convergence Divergence'},
            {'name': 'BBANDS', 'description': 'Bollinger Bands'},
            {'name': 'STOCH', 'description': 'Stochastic Oscillator'},
            {'name': 'ADX', 'description': 'Average Directional Index'},
            {'name': 'ATR', 'description': 'Average True Range'},
        ]
    }

# Options tools

def mock_get_options_chain(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock options chain data"""
    symbol = params.get('symbol', 'AAPL')
    
    return {
        'symbol': symbol,
        'stock_price': 175.43,
        'expiration_dates': ['2025-01-17', '2025-01-24', '2025-01-31'],
        'options': [
            {
                'strike': 170.0,
                'type': 'call',
                'expiration': '2025-01-17',
                'premium': 6.25,
                'bid': 6.20,
                'ask': 6.30,
                'volume': 2150,
                'open_interest': 8400,
                'implied_volatility': 0.28,
                'delta': 0.72,
                'gamma': 0.04,
                'theta': -0.18,
                'vega': 0.22
            },
            {
                'strike': 175.0,
                'type': 'call',
                'expiration': '2025-01-17',
                'premium': 3.25,
                'bid': 3.20,
                'ask': 3.30,
                'volume': 3250,
                'open_interest': 12400,
                'implied_volatility': 0.26,
                'delta': 0.52,
                'gamma': 0.05,
                'theta': -0.15,
                'vega': 0.24
            },
            {
                'strike': 180.0,
                'type': 'call',
                'expiration': '2025-01-17',
                'premium': 1.45,
                'bid': 1.40,
                'ask': 1.50,
                'volume': 1850,
                'open_interest': 6200,
                'implied_volatility': 0.25,
                'delta': 0.28,
                'gamma': 0.04,
                'theta': -0.12,
                'vega': 0.20
            },
            {
                'strike': 170.0,
                'type': 'put',
                'expiration': '2025-01-17',
                'premium': 0.95,
                'bid': 0.90,
                'ask': 1.00,
                'volume': 1250,
                'open_interest': 4800,
                'implied_volatility': 0.27,
                'delta': -0.28,
                'gamma': 0.04,
                'theta': -0.10,
                'vega': 0.22
            },
            {
                'strike': 175.0,
                'type': 'put',
                'expiration': '2025-01-17',
                'premium': 2.85,
                'bid': 2.80,
                'ask': 2.90,
                'volume': 2980,
                'open_interest': 10200,
                'implied_volatility': 0.26,
                'delta': -0.48,
                'gamma': 0.05,
                'theta': -0.12,
                'vega': 0.24
            },
            {
                'strike': 180.0,
                'type': 'put',
                'expiration': '2025-01-17',
                'premium': 5.75,
                'bid': 5.70,
                'ask': 5.80,
                'volume': 1650,
                'open_interest': 7400,
                'implied_volatility': 0.28,
                'delta': -0.72,
                'gamma': 0.04,
                'theta': -0.16,
                'vega': 0.20
            },
        ]
    }

def mock_get_option_greeks(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock detailed option Greeks"""
    symbol = params.get('symbol', 'AAPL')
    strike = float(params.get('strike', '175.0'))
    option_type = params.get('type', 'call')
    
    return {
        'symbol': symbol,
        'strike': strike,
        'type': option_type,
        'expiration': '2025-01-17',
        'stock_price': 175.43,
        'premium': 3.25,
        'greeks': {
            'delta': 0.52,
            'gamma': 0.05,
            'theta': -0.15,
            'vega': 0.24,
            'rho': 0.08
        },
        'implied_volatility': 0.26,
        'intrinsic_value': 0.43 if option_type == 'call' else 0.00,
        'time_value': 2.82 if option_type == 'call' else 3.25,
        'days_to_expiration': 13
    }

# Utility tools

def mock_get_provider_status(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock provider health status"""
    return {
        'providers': [
            {
                'name': 'Robinhood',
                'status': 'healthy',
                'last_check': '2025-01-04T16:00:00Z',
                'response_time_ms': 245,
                'success_rate': 99.8
            },
            {
                'name': 'Finnhub',
                'status': 'healthy',
                'last_check': '2025-01-04T16:00:00Z',
                'response_time_ms': 180,
                'success_rate': 99.5
            },
            {
                'name': 'FMP',
                'status': 'healthy',
                'last_check': '2025-01-04T16:00:00Z',
                'response_time_ms': 320,
                'success_rate': 98.9
            },
            {
                'name': 'Alpha Vantage',
                'status': 'healthy',
                'last_check': '2025-01-04T16:00:00Z',
                'response_time_ms': 410,
                'success_rate': 97.2
            },
        ]
    }

def mock_search_symbols(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock symbol search results"""
    query = params.get('query', 'APP')
    
    return {
        'query': query,
        'results': [
            {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'type': 'Common Stock',
                'exchange': 'NASDAQ'
            },
            {
                'symbol': 'APP',
                'name': 'AppLovin Corporation',
                'type': 'Common Stock',
                'exchange': 'NASDAQ'
            },
            {
                'symbol': 'APPN',
                'name': 'Appian Corporation',
                'type': 'Common Stock',
                'exchange': 'NASDAQ'
            },
        ]
    }

def mock_get_market_status(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock market status"""
    return {
        'market': 'US',
        'status': 'closed',
        'current_time': '2025-01-04T20:00:00Z',
        'next_open': '2025-01-06T14:30:00Z',
        'next_close': '2025-01-06T21:00:00Z',
        'is_holiday': False,
        'trading_hours': {
            'regular': {
                'start': '09:30',
                'end': '16:00',
                'timezone': 'America/New_York'
            },
            'extended': {
                'pre_market_start': '04:00',
                'after_hours_end': '20:00'
            }
        }
    }

def mock_get_earnings_calendar(params: Dict[str, str]) -> Dict[str, Any]:
    """Generate mock earnings calendar"""
    return {
        'upcoming_earnings': [
            {
                'symbol': 'AAPL',
                'company_name': 'Apple Inc.',
                'earnings_date': '2025-01-30',
                'estimate_eps': 1.55,
                'fiscal_quarter': 'Q1 2025'
            },
            {
                'symbol': 'MSFT',
                'company_name': 'Microsoft Corporation',
                'earnings_date': '2025-01-23',
                'estimate_eps': 2.78,
                'fiscal_quarter': 'Q2 2025'
            },
            {
                'symbol': 'GOOGL',
                'company_name': 'Alphabet Inc.',
                'earnings_date': '2025-02-04',
                'estimate_eps': 1.62,
                'fiscal_quarter': 'Q4 2024'
            },
            {
                'symbol': 'AMZN',
                'company_name': 'Amazon.com Inc.',
                'earnings_date': '2025-02-01',
                'estimate_eps': 1.12,
                'fiscal_quarter': 'Q4 2024'
            },
        ]
    }
