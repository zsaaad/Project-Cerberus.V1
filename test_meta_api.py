#!/usr/bin/env python3
"""
Test script for Meta Marketing API integration
Validates the MetaAPIFetcher class structure and basic functionality.
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_date_handling():
    """Test yesterday date calculation"""
    print("Testing date handling...")
    
    # Import here to avoid API initialization
    from meta_api_fetcher import MetaAPIFetcher
    
    # Mock initialization (won't actually connect to API)
    try:
        fetcher = MetaAPIFetcher("test_token", "act_test", "test_app", "test_secret")
        start_date, end_date = fetcher.get_yesterday_date_range()
        
        # Validate date format
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        assert start_date == yesterday, f"Expected {yesterday}, got {start_date}"
        assert end_date == yesterday, f"Expected {yesterday}, got {end_date}"
        
        print(f"✅ Date handling works correctly: {start_date}")
        return True
        
    except Exception as e:
        print(f"❌ Date handling failed: {e}")
        return False

def test_field_configuration():
    """Test that required fields are properly configured"""
    print("Testing field configuration...")
    
    try:
        from meta_api_fetcher import MetaAPIFetcher
        fetcher = MetaAPIFetcher("test_token", "act_test", "test_app", "test_secret")
        
        # Check essential fields are present
        required_fields = [
            'campaign_id', 'campaign_name', 
            'adset_id', 'adset_name',
            'ad_id', 'ad_name',
            'spend', 'clicks', 'ctr',
            'actions', 'cost_per_action_type'
        ]
        
        missing_fields = [field for field in required_fields if field not in fetcher.fields]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"✅ All {len(fetcher.fields)} required fields configured properly")
        return True
        
    except Exception as e:
        print(f"❌ Field configuration test failed: {e}")
        return False

def test_data_processing():
    """Test data processing logic with mock data"""
    print("Testing data processing...")
    
    try:
        from meta_api_fetcher import MetaAPIFetcher
        fetcher = MetaAPIFetcher("test_token", "act_test", "test_app", "test_secret")
        
        # Mock insight data
        mock_insight = {
            'campaign_id': '123456789',
            'campaign_name': 'Test Campaign',
            'adset_id': '987654321', 
            'adset_name': 'Test AdSet',
            'ad_id': '555666777',
            'ad_name': 'Test Ad',
            'spend': '45.67',
            'impressions': '12543',
            'clicks': '234',
            'ctr': '1.87',
            'actions': [
                {'action_type': 'lead', 'value': '8'},
                {'action_type': 'link_click', 'value': '230'}
            ],
            'date_start': '2025-01-20',
            'date_stop': '2025-01-20'
        }
        
        # Test data processing
        processed = fetcher._process_ad_insight(mock_insight)
        
        # Validate key calculations
        assert processed['spend'] == 45.67, f"Spend processing failed: {processed['spend']}"
        assert processed['clicks'] == 234, f"Clicks processing failed: {processed['clicks']}" 
        assert processed['lead_conversions'] == 8, f"Lead conversion processing failed: {processed['lead_conversions']}"
        assert processed['cost_per_lead'] == 45.67/8, f"CPL calculation failed: {processed['cost_per_lead']}"
        
        print(f"✅ Data processing works correctly")
        print(f"   - Spend: ${processed['spend']}")
        print(f"   - Clicks: {processed['clicks']}")
        print(f"   - Lead Conversions: {processed['lead_conversions']}")
        print(f"   - Cost per Lead: ${processed['cost_per_lead']:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_environment_validation():
    """Test environment variable validation"""
    print("Testing environment variable validation...")
    
    # Check if env.example exists
    if os.path.exists('env.example'):
        print("✅ Configuration template (env.example) exists")
        
        with open('env.example', 'r') as f:
            content = f.read()
            
        required_vars = ['META_ACCESS_TOKEN', 'META_AD_ACCOUNT_ID', 'META_APP_ID', 'META_APP_SECRET']
        missing_vars = [var for var in required_vars if var not in content]
        
        if missing_vars:
            print(f"❌ Missing environment variables in template: {missing_vars}")
            return False
        else:
            print("✅ All required environment variables documented")
            return True
    else:
        print("❌ Configuration template not found")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Project Cerberus Meta API Tests")
    print("=" * 50)
    
    tests = [
        test_environment_validation,
        test_date_handling,
        test_field_configuration, 
        test_data_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("   Make sure dependencies are installed: pip install -r requirements.txt")
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Meta API integration is ready.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and add your real API credentials")
        print("2. Run: python meta_api_fetcher.py")
        print("3. Integrate with Cerberus pipeline for automated daily alerts")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 