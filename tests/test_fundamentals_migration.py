#!/usr/bin/env python3

import asyncio
import logging
import sys
import os
import aiohttp

# Add the parent directory to the path so we can import the market_data module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_data.providers.unified_fundamentals_provider import UnifiedFundamentalsProvider
from market_data.providers.market_client import MultiProviderClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundamentalsMigrationTest:
    """Test suite for fundamentals migration to Robinhood primary"""
    
    def __init__(self):
        self.unified_provider = UnifiedFundamentalsProvider()
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
    
    async def test_basic_fundamentals(self):
        """Test 2: Basic fundamentals from Robinhood"""
        print("\n=== Test 2: Basic Fundamentals (Robinhood) ===")
        
        try:
            result = await self.unified_provider.robinhood_provider.get_fundamentals(self.test_symbol)
            
            print(f"Provider: {result.get('provider', 'unknown')}")
            print(f"Symbol: {result.get('symbol', 'unknown')}")
            
            if 'data' in result and 'fundamentals' in result['data']:
                data = result['data']['fundamentals']
                print(f"Market Cap: {data.get('market_cap', 'N/A')}")
                print(f"P/E Ratio: {data.get('pe_ratio', 'N/A')}")
                print(f"Sector: {data.get('sector', 'N/A')}")
                print(f"Description: {data.get('description', 'N/A')[:100]}...")
            
            success = result.get('provider') == 'robinhood' and 'data' in result
            print(f"✅ Basic fundamentals test: {'PASSED' if success else 'FAILED'}")
            
            self.results['basic_fundamentals'] = result
            return success
            
        except Exception as e:
            print(f"❌ Basic fundamentals test failed: {e}")
            return False
    
    async def test_enhanced_fundamentals(self):
        """Test 3: Enhanced fundamentals with earnings and ratings"""
        print("\n=== Test 3: Enhanced Fundamentals ===")
        
        try:
            result = await self.unified_provider.get_enhanced_fundamentals(
                self.test_symbol, include_earnings=True, include_ratings=True
            )
            
            print(f"Provider: {result.get('provider', 'unknown')}")
            print(f"Enhanced: {result.get('enhanced', False)}")
            
            if 'data' in result:
                data = result['data']
                
                # Check earnings data
                if 'earnings' in data:
                    earnings_count = data['earnings'].get('total_quarters', 0)
                    print(f"Earnings Quarters: {earnings_count}")
                
                # Check ratings data
                if 'analyst_ratings' in data:
                    ratings_count = data['analyst_ratings'].get('ratings_count', 0)
                    print(f"Analyst Ratings: {ratings_count}")
                
                # Check detailed data
                if 'detailed_earnings' in data:
                    print(f"Detailed Earnings: {len(data['detailed_earnings'])} quarters")
                
                if 'detailed_ratings' in data:
                    print(f"Detailed Ratings: Available")
            
            success = result.get('provider') == 'robinhood' and result.get('enhanced', False)
            print(f"✅ Enhanced fundamentals test: {'PASSED' if success else 'FAILED'}")
            
            self.results['enhanced_fundamentals'] = result
            return success
            
        except Exception as e:
            print(f"❌ Enhanced fundamentals test failed: {e}")
            return False
    
    async def test_unified_provider_integration(self):
        """Test 4: Unified provider with fallback logic"""
        print("\n=== Test 4: Unified Provider Integration ===")
        
        try:
            async with aiohttp.ClientSession() as session:
                result = await self.unified_provider.get_fundamentals(session, self.test_symbol)
            
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
    
    async def test_mcp_integration(self):
        """Test 5: MCP tool integration"""
        print("\n=== Test 5: MCP Integration ===")
        
        try:
            async with aiohttp.ClientSession() as session:
                result = await self.multi_client.get_fundamentals(session, self.test_symbol)
            
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
    
    async def test_data_quality_comparison(self):
        """Test 6: Data quality comparison"""
        print("\n=== Test 6: Data Quality Comparison ===")
        
        try:
            # Get Robinhood data
            rh_result = await self.unified_provider.robinhood_provider.get_fundamentals(self.test_symbol)
            
            # Get enhanced data
            enhanced_result = await self.unified_provider.get_enhanced_fundamentals(
                self.test_symbol, include_earnings=True, include_ratings=True
            )
            
            # Compare data richness
            rh_fields = len(rh_result.get('data', {}).get('fundamentals', {}))
            enhanced_fields = len(enhanced_result.get('data', {}))
            
            print(f"Basic Fundamentals Fields: {rh_fields}")
            print(f"Enhanced Data Sections: {enhanced_fields}")
            
            # Check for additional data
            has_earnings = 'earnings' in enhanced_result.get('data', {})
            has_ratings = 'analyst_ratings' in enhanced_result.get('data', {})
            
            print(f"Has Earnings Data: {has_earnings}")
            print(f"Has Ratings Data: {has_ratings}")
            
            success = enhanced_fields > rh_fields and (has_earnings or has_ratings)
            print(f"✅ Data quality test: {'PASSED' if success else 'FAILED'}")
            
            self.results['data_quality'] = {
                'basic_fields': rh_fields,
                'enhanced_fields': enhanced_fields,
                'has_earnings': has_earnings,
                'has_ratings': has_ratings
            }
            return success
            
        except Exception as e:
            print(f"❌ Data quality test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 FUNDAMENTALS MIGRATION TEST SUITE")
        print("=" * 50)
        
        tests = [
            ("Robinhood Authentication", self.test_robinhood_authentication),
            ("Basic Fundamentals", self.test_basic_fundamentals),
            ("Enhanced Fundamentals", self.test_enhanced_fundamentals),
            ("Unified Provider", self.test_unified_provider_integration),
            ("MCP Integration", self.test_mcp_integration),
            ("Data Quality Comparison", self.test_data_quality_comparison),
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
            print("🎉 ALL TESTS PASSED - Fundamentals Migration Complete!")
            print("\n✅ Key Achievements:")
            print("  • Robinhood unlimited fundamentals operational")
            print("  • Enhanced data with earnings and analyst ratings")
            print("  • MCP integration successful")
            print("  • Unified provider with intelligent routing")
        else:
            print("⚠️  Some tests failed - Review before proceeding")
        
        return passed, total, self.results


async def main():
    """Run the fundamentals migration test"""
    test_suite = FundamentalsMigrationTest()
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
