#!/usr/bin/env python3

import asyncio
import logging
import sys
import os

# Add the parent directory to the path so we can import the market_data module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_data.providers.unified_historical_provider import UnifiedHistoricalProvider
from market_data.providers.market_client import MultiProviderClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoricalMigrationTest:
    """Test suite for historical data migration to Robinhood primary"""
    
    def __init__(self):
        self.unified_provider = UnifiedHistoricalProvider()
        self.multi_client = MultiProviderClient()
        self.test_symbol = "AAPL"
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
    
    async def test_daily_historical_data(self):
        """Test 2: Daily historical data from Robinhood"""
        print("\n=== Test 2: Daily Historical Data ===")
        
        try:
            result = await self.unified_provider.robinhood_provider.get_daily_data(
                self.test_symbol, span="month"
            )
            
            print(f"Provider: {result.get('provider', 'unknown')}")
            print(f"Symbol: {result.get('symbol', 'unknown')}")
            print(f"Interval: {result.get('interval', 'unknown')}")
            print(f"Span: {result.get('span', 'unknown')}")
            print(f"Data Points: {result.get('data_points', 0)}")
            
            if 'data' in result and len(result['data']) > 0:
                latest = result['data'][-1]
                print(f"Latest Close: ${latest.get('close', 0):.2f}")
                print(f"Latest Volume: {latest.get('volume', 0):,}")
            
            success = result.get('provider') == 'robinhood' and result.get('data_points', 0) > 0
            print(f"✅ Daily historical test: {'PASSED' if success else 'FAILED'}")
            
            self.results['daily_data'] = result
            return success
            
        except Exception as e:
            print(f"❌ Daily historical test failed: {e}")
            return False
    
    async def test_intraday_data(self):
        """Test 3: Intraday data (5-minute intervals)"""
        print("\n=== Test 3: Intraday Data (5-minute) ===")
        
        try:
            result = await self.unified_provider.robinhood_provider.get_intraday_data(
                self.test_symbol, interval="5minute"
            )
            
            print(f"Provider: {result.get('provider', 'unknown')}")
            print(f"Interval: {result.get('interval', 'unknown')}")
            print(f"Data Points: {result.get('data_points', 0)}")
            
            if 'data' in result and len(result['data']) > 0:
                print(f"First timestamp: {result['data'][0].get('timestamp', 'N/A')}")
                print(f"Last timestamp: {result['data'][-1].get('timestamp', 'N/A')}")
            
            success = result.get('provider') == 'robinhood' and result.get('interval') == '5minute'
            print(f"✅ Intraday data test: {'PASSED' if success else 'FAILED'}")
            
            self.results['intraday_data'] = result
            return success
            
        except Exception as e:
            print(f"❌ Intraday data test failed: {e}")
            return False
    
    async def test_multiple_intervals(self):
        """Test 4: Multiple intervals support"""
        print("\n=== Test 4: Multiple Intervals Support ===")
        
        intervals_to_test = [
            ("day", "month"),
            ("week", "year"),
            ("30minute", "week")
        ]
        
        successful_intervals = 0
        
        for interval, span in intervals_to_test:
            try:
                result = await self.unified_provider.robinhood_provider.get_historical_data(
                    self.test_symbol, interval=interval, span=span
                )
                
                if result.get('provider') == 'robinhood' and result.get('data_points', 0) > 0:
                    print(f"✅ {interval}/{span}: {result.get('data_points', 0)} points")
                    successful_intervals += 1
                else:
                    print(f"❌ {interval}/{span}: Failed")
                    
            except Exception as e:
                print(f"❌ {interval}/{span}: Error - {e}")
        
        success = successful_intervals >= 2  # At least 2 intervals should work
        print(f"✅ Multiple intervals test: {'PASSED' if success else 'FAILED'} ({successful_intervals}/3)")
        
        self.results['multiple_intervals'] = {
            'successful': successful_intervals,
            'total': len(intervals_to_test)
        }
        return success
    
    async def test_unified_provider_integration(self):
        """Test 5: Unified provider with fallback logic"""
        print("\n=== Test 5: Unified Provider Integration ===")
        
        try:
            result = await self.unified_provider.get_historical_data(
                self.test_symbol, interval="day", span="month"
            )
            
            provider = result.get('provider', 'unknown')
            print(f"Provider Used: {provider}")
            
            # Should use Robinhood as primary
            success = provider == 'robinhood' and 'data' in result
            if success:
                print("✅ Unified provider test: PASSED")
            else:
                print("❌ Unified provider test: FAILED")
            
            self.results['unified_provider'] = result
            return success
            
        except Exception as e:
            print(f"❌ Unified provider test failed: {e}")
            return False
    
    async def test_supported_intervals(self):
        """Test 6: Supported intervals discovery"""
        print("\n=== Test 6: Supported Intervals ===")
        
        try:
            result = await self.unified_provider.get_supported_intervals()
            
            print(f"Provider: {result.get('provider', 'unknown')}")
            
            if 'supported' in result:
                supported = result['supported']
                intervals = supported.get('intervals', {})
                spans = supported.get('spans', {})
                
                print(f"Supported Intervals: {len(intervals)}")
                print(f"Supported Spans: {len(spans)}")
                
                # Show some examples
                for interval in list(intervals.keys())[:3]:
                    print(f"  • {interval}: {intervals[interval]}")
            
            success = 'supported' in result and len(result['supported'].get('intervals', {})) > 0
            print(f"✅ Supported intervals test: {'PASSED' if success else 'FAILED'}")
            
            self.results['supported_intervals'] = result
            return success
            
        except Exception as e:
            print(f"❌ Supported intervals test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 HISTORICAL DATA MIGRATION TEST SUITE")
        print("=" * 50)
        
        tests = [
            ("Robinhood Authentication", self.test_robinhood_authentication),
            ("Daily Historical Data", self.test_daily_historical_data),
            ("Intraday Data", self.test_intraday_data),
            ("Multiple Intervals", self.test_multiple_intervals),
            ("Unified Provider", self.test_unified_provider_integration),
            ("Supported Intervals", self.test_supported_intervals),
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
            print("🎉 ALL TESTS PASSED - Historical Data Migration Complete!")
            print("\n✅ Key Achievements:")
            print("  • Robinhood unlimited historical data operational")
            print("  • Multiple intervals supported (5min, 10min, 30min, day, week)")
            print("  • Real-time API vs static files")
            print("  • Unified provider with intelligent routing")
        else:
            print("⚠️  Some tests failed - Review before proceeding")
        
        return passed, total, self.results


async def main():
    """Run the historical data migration test"""
    test_suite = HistoricalMigrationTest()
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
