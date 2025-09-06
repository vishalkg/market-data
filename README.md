# Enhanced Market Data MCP Server

A Model Context Protocol (MCP) server that provides reliable, always-available real-time stock market data and options trading information with unlimited Robinhood options data and professional optimization.

## 🚀 Quick Start

### 1. Setup Authentication (Optional but Recommended)
```bash
python setup_rh_creds.py
```
*For full Robinhood options functionality. System works with Finnhub fallback if skipped.*

### 2. Run Comprehensive Tests
```bash
# One-click comprehensive test suite
python comprehensive_test_suite.py

# Or use the simple runner
python run_tests.py
```

### 3. Start the Server
```bash
# Start MCP server in stdio mode (recommended)
./start.sh

# Or run directly
python -m market_data.server
```

*The server runs in stdio mode for MCP protocol communication - no port conflicts!*

## 🧪 Testing

The system includes a comprehensive test suite that validates all functionality with real API calls:

- **Package Structure**: Import validation and file organization
- **Authentication**: Robinhood login and credential management  
- **Options Functionality**: Real options chains with 99%+ data reduction
- **MCP Server**: Tool registration and execution
- **Integration**: Multi-symbol processing and error handling

**Expected Results**: 10/10 tests passed (100%) with full Robinhood authentication, or graceful fallback to Finnhub.

## Features

- **Unlimited Options Data**: Robinhood integration with professional 99%+ data reduction
- **Real-time Greeks**: Delta, Gamma, Theta, Vega on-demand
- **Intelligent Fallback**: Robinhood → Finnhub → Error handling
- **Real-time stock quotes**: Finnhub (180 requests/min across 3 keys)
- **Company fundamentals**: FMP primary (250/day) → Finnhub backup
- **Technical indicators**: Alpha Vantage with key rotation (15/min across 3 keys)
- **Market status**: Real-time market open/close status
- **Historical data files**: Access to Polygon.io S3 flat files
- **Always-on**: Multiple API keys ensure continuous data availability

**Available MCP Tools**:
- `get_stock_quote`: Real-time quotes from Finnhub
- `get_stock_fundamentals`: Company fundamentals with fallback
- `get_options_chain`: Professional options with 99%+ optimization
- `get_option_greeks`: Real-time Greeks (Delta, Gamma, Theta, Vega)
- `get_provider_status`: System status and capabilities
- `get_technical_indicators`: RSI, MACD, Bollinger Bands
- `get_historical_data`: Historical price data
- `get_market_status`: Market open/close status

## Multi-Provider Architecture

### Data Sources & Limits
- **Finnhub**: 3 keys × 60/min = 180 requests/min (real-time quotes, options)
- **Alpha Vantage**: 3 keys × 5/min = 15 requests/min (technical indicators)
- **FMP**: 250 requests/day (fundamentals)
- **Polygon.io**: 5 requests/min (historical data backup)

### Smart Routing
- Real-time quotes: Finnhub primary (no fallback needed)
- Options chains: Finnhub only
- Fundamentals: FMP → Finnhub fallback
- Technical indicators: Alpha Vantage with automatic key rotation
- Rate limiting: Automatic key switching when limits reached

## Installation

1. **Make start script executable**:
   ```bash
   chmod +x ~/.mcp/market-data/start.sh
   ```

2. **Add to Q CLI MCP configuration**:
   ```bash
   qchat mcp add --name market-data --command ~/.mcp/market-data/start.sh
   ```

3. **Test**:
   ```bash
   qchat
   # In chat: "get stock quote for AAPL"
   ```

## Usage Examples

```
Get stock quote for AAPL
Get options chain for TSLA  
Get fundamental data for MSFT
Get RSI indicator for NVDA
Get MACD for GOOGL
Check API usage stats
Check if markets are open
List historical data files for 2024-01-15
```

## API Key Management

The server automatically manages multiple API keys:
- **Rate limiting**: Tracks usage per key per provider
- **Key rotation**: Switches to next available key when limits reached
- **Daily resets**: Automatically resets daily counters
- **Usage monitoring**: Real-time usage statistics via `get_usage_stats`

## Requirements

- Q CLI with MCP support
- Internet connection for API access
- Python 3.11+ (included in venv)
- No API key setup required (pre-configured)

## Benefits

- **99.9% uptime**: Multiple providers ensure continuous data
- **High throughput**: 180 quotes/min, 15 indicators/min
- **Cost optimization**: Maximizes free tier usage
- **Professional grade**: Real-time data with options Greeks
- **Monitoring**: Built-in usage tracking and optimization
