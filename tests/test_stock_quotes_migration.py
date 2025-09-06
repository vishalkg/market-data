#!/usr/bin/env python3

import asyncio
import logging
import sys
import os
import aiohttp

# Add the parent directory to the path so we can import the market_data module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_data.providers.unified_stock_provider import UnifiedStockProvider
from market_data.providers.market_client import MultiProviderClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockQuotesMigrationTest:
    """Test suite for stock quotes migration to Robinhood primary"""
    
    def __init__(self):
        self.unified_provider = UnifiedStockProvider()
        self.multi_client = MultiProviderClient()
        self.test_symbols = ["AAPL", "TSLA", "MSFT"]
        self.results = {}
    
    async def test_robinhood_authentication(self):
        """Test 1: Robinhood authentication"""
        print("\n=== Test 1: Robinhood Authentication ===")
        
        try:
            await self.unified_provider.robinhood_provider.ensure_authenticated()
            print("✅ Robinhood authentication successful")
            self.results['auth'] = True
            return True
            
        except Exception as e:
            print(f"❌ Robinhood authentication failed: {e}")
            self.results['auth'] = False
            return False
    
    async def test_single_quote_robinhood(self):
        """Test 2: Single quote from Robinhood"""
        print("\n=== Test 2: Single Quote (Robinhood) ===")
        
        try:
            result = await self.unified_provider.robinhood_provider.get_stock_quote("AAPL")
            
            print(f"Provider: {result.get('provider', 'unknown')}")
            print(f"Symbol: {result.get('symbol', 'unknown')}")
            
            if 'data' in result:
                data = result['data']
                print(f"Current Price: ${data.get('c', 0):.2f}")
                print(f"Change: {data.get('dp', 0):+.2f}%")
                print(f"High: ${data.get('h', 0):.2f}")
                print(f"Low: ${data.get('l', 0):.2f}")
            
            success = result.get('provider') == 'robinhood' and 'data' in result
            print(f"✅ Single quote test: {'PASSED' if success else 'FAILED'}")
            
            self.results['single_quote'] = result
            return success
            
        except Exception as e:
            print(f"❌ Single quote test failed: {e}")
            return False
    
    async def test_batch_quotes(self):
        """Test 3: Batch quotes (Robinhood advantage)"""
        print("\n=== Test 3: Batch Quotes ===")
        
        try:
            result = await self.unified_provider.robinhood_provider.get_multiple_quotes(self.test_symbols)
            
            print(f"Provider: {result.get('provider', 'unknown')}")
            print(f"Batch Size: {result.get('batch_size', 0)}")
            
            if 'data' in result:
                print("Stock Prices:")
                for symbol, data in result['data'].items():
                    print(f"  {symbol}: ${data.get('c', 0):.2f} ({data.get('dp', 0):+.2f}%)")
            
            success = result.get('provider') == 'robinhood' and len(result.get('data', {})) > 0
            print(f"✅ Batch quotes test: {'PASSED' if success else 'FAILED'}")
            
            self.results['batch_quotes'] = result
            return success
            
        except Exception as e:
            print(f"❌ Batch quotes test failed: {e}")
            return False
    
    async def test_unified_provider_integration(self):
        """Test 4: Unified provider with fallback logic"""
        print("\n=== Test 4: Unified Provider Integration ===")
        
        try:
            async with aiohttp.ClientSession() as session:
                result = await self.unified_provider.get_stock_quote(session, "AAPL")
            
            provider = result.get('provider', 'unknown')
            print(f"Provider Used: {provider}")
            
            # Should use Robinhood as primary
            success = provider == 'robinhood' and 'data' in result
            if success:
                data = result['data']
                print(f"Price: ${data.get('c', 0):.2f}")
                print("✅ Unified provider test: PASSED")
            else:
                print("❌ Unified provider test: FAILED")
            
            self.results['unified_provider'] = result
            return success
            
        except Exception as e:
            print(f"❌ Unified provider test failed: {e}")
            return False
    
    async def test_mcp_integration(self):
        """Test 5: MCP tool integration"""
        print("\n=== Test 5: MCP Integration ===")
        
        try:
            async with aiohttp.ClientSession() as session:
                result = await self.multi_client.get_quote(session, "AAPL")
            
            provider = result.get('provider', 'unknown')
            print(f"MCP Provider: {provider}")
            
            success = provider == 'robinhood' and 'data' in result
            if success:
                print("✅ MCP integration test: PASSED")
            else:
                print("❌ MCP integration test: FAILED")
            
            self.results['mcp_integration'] = result
            return success
            
        except Exception as e:
            print(f"❌ MCP integration test failed: {e}")
            return False
    
    async def test_performance_comparison(self):
        """Test 6: Performance comparison"""
        print("\n=== Test 6: Performance Comparison ===")
        
        try:
            import time
            
            # Test single requests (old way)
            start_time = time.time()
            single_results = []
            for symbol in self.test_symbols:
                result = await self.unified_provider.robinhood_provider.get_stock_quote(symbol)
                single_results.append(result)
            single_time = time.time() - start_time
            
            # Test batch request (new way)
            start_time = time.time()
            batch_result = await self.unified_provider.robinhood_provider.get_multiple_quotes(self.test_symbols)
            batch_time = time.time() - start_time
            
            print(f"Individual Requests: {single_time:.2f}s for {len(self.test_symbols)} symbols")
            print(f"Batch Request: {batch_time:.2f}s for {len(self.test_symbols)} symbols")
            
            if batch_time < single_time:
                improvement = ((single_time - batch_time) / single_time) * 100
                print(f"✅ Performance improvement: {improvement:.1f}% faster with batch")
                success = True
            else:
                print("❌ Batch request not faster than individual requests")
                success = False
            
            self.results['performance'] = {
                'single_time': single_time,
                'batch_time': batch_time,
                'improvement': improvement if batch_time < single_time else 0
            }
            return success
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 STOCK QUOTES MIGRATION TEST SUITE")
        print("=" * 50)
        
        tests = [
            ("Robinhood Authentication", self.test_robinhood_authentication),
            ("Single Quote", self.test_single_quote_robinhood),
            ("Batch Quotes", self.test_batch_quotes),
            ("Unified Provider", self.test_unified_provider_integration),
            ("MCP Integration", self.test_mcp_integration),
            ("Performance Comparison", self.test_performance_comparison),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                success = await test_func()
                if success:
                    passed += 1
            except Exception as e:
                print(f"\n{test_name}: ❌ ERROR - {e}")
        
        print(f"\n{'='*50}")
        print(f"📊 TEST RESULTS: {passed}/{total} PASSED ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Stock Quotes Migration Complete!")
            print("\n✅ Key Achievements:")
            print("  • Robinhood unlimited stock quotes operational")
            print("  • Batch processing working (performance advantage)")
            print("  • MCP integration successful")
            print("  • Unified provider with intelligent routing")
        else:
            print("⚠️  Some tests failed - Review before proceeding")
        
        return passed, total, self.results


async def main():
    """Run the stock quotes migration test"""
    test_suite = StockQuotesMigrationTest()
    passed, total, results = await test_suite.run_all_tests()
    
    # Return results for tracking
    return {
        "passed": passed,
        "total": total,
        "success_rate": passed / total * 100,
        "results": results
    }


if __name__ == "__main__":
    asyncio.run(main())
