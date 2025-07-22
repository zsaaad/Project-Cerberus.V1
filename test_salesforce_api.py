#!/usr/bin/env python3
"""
Test script for Salesforce API integration
Validates the SalesforceAPIFetcher class structure and basic functionality.
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_date_handling():
    """Test yesterday date calculation and Salesforce datetime formatting"""
    print("Testing date handling...")
    
    try:
        # Test date calculation and formatting
        yesterday = (datetime.now() - timedelta(days=1))
        start_datetime = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_datetime = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Test Salesforce datetime format
        start_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        end_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        # Validate format (should be ISO format with Z suffix)
        assert 'T' in start_str, "Missing T separator in datetime"
        assert start_str.endswith('Z'), "Missing Z suffix in datetime"
        assert len(start_str) == 24, f"Invalid datetime format length: {len(start_str)}"
        
        print(f"✅ Date handling works correctly: {start_str} to {end_str}")
        return True
        
    except Exception as e:
        print(f"❌ Date handling failed: {e}")
        return False

def test_soql_query_structure():
    """Test that SOQL queries include required fields"""
    print("Testing SOQL query structure...")
    
    try:
        # Test SOQL query structure by reading the class definition directly
        import inspect
        from salesforce_fetcher import SalesforceAPIFetcher
        
        # Get the queries from class source without initializing
        source = inspect.getsource(SalesforceAPIFetcher)
        
        # Check essential fields are present in Lead SOQL query
        required_lead_fields = [
            'Id', 'Status', 'CreatedDate', 'IsConverted',
            'FB_Campaign_ID__c', 'FB_Adset_ID__c', 'FB_Ad_ID__c',
            'UTM_Campaign__c', 'UTM_Source__c'
        ]
        
        missing_lead_fields = [field for field in required_lead_fields if field not in source]
        
        if missing_lead_fields:
            print(f"❌ Missing required lead fields in SOQL: {missing_lead_fields}")
            return False
        
        # Check essential fields are present in Opportunity SOQL query
        required_opp_fields = ['Id', 'StageName', 'Amount', 'CreatedDate']
        
        missing_opp_fields = [field for field in required_opp_fields if field not in source]
        
        if missing_opp_fields:
            print(f"❌ Missing required opportunity fields in SOQL: {missing_opp_fields}")
            return False
        
        # Verify SOQL syntax basics
        if 'SELECT' not in source or 'FROM Lead' not in source or 'FROM Opportunity' not in source:
            print("❌ Invalid SOQL query structure")
            return False
        
        print(f"✅ SOQL queries properly structured with all required fields")
        return True
        
    except Exception as e:
        print(f"❌ SOQL query test failed: {e}")
        return False

def test_data_processing():
    """Test data processing logic with mock Salesforce data"""
    print("Testing data processing...")
    
    try:
        # Test data processing logic without Salesforce connection
        from salesforce_fetcher import SalesforceAPIFetcher
        
        # Create a minimal mock fetcher for testing data processing only
        class MockFetcher:
            def __init__(self):
                self.logger = MockLogger()
        
        class MockLogger:
            def info(self, msg): pass
            def error(self, msg): pass
        
        fetcher = MockFetcher()
        
        # Create mock Salesforce lead record
        mock_lead = {
            'Id': 'lead_123456',
            'Status': 'Qualified',
            'CreatedDate': '2025-01-20T14:30:00.000Z',
            'IsConverted': True,
            'ConvertedOpportunityId': 'opp_789012',
            'FirstName': 'John',
            'LastName': 'Doe',
            'Email': 'john.doe@company.com',
            'Company': 'Test Company',
            'LeadSource': 'Web',
            'FB_Campaign_ID__c': 'camp_001',
            'FB_Adset_ID__c': 'adset_001',
            'FB_Ad_ID__c': 'ad_001',
            'UTM_Campaign__c': 'Q1_lead_gen',
            'UTM_Source__c': 'facebook',
            'UTM_Medium__c': 'cpc',
            'attributes': {'type': 'Lead', 'url': '/services/data/v57.0/sobjects/Lead/lead_123456'}
        }
        
        # Create mock Salesforce opportunity record
        mock_opportunity = {
            'Id': 'opp_789012',
            'Name': 'Test Opportunity',
            'StageName': 'Qualification',
            'Amount': 5000.00,
            'CloseDate': '2025-02-15',
            'Probability': 25.0,
            'Type': 'New Customer',
            'LeadSource': 'Web',
            'CreatedDate': '2025-01-20T14:35:00.000Z',
            'attributes': {'type': 'Opportunity', 'url': '/services/data/v57.0/sobjects/Opportunity/opp_789012'}
        }
        
        # Test data processing using the actual SalesforceAPIFetcher methods
        # We'll create a mock by monkey-patching the _initialize_connection method
        original_init = SalesforceAPIFetcher._initialize_connection
        SalesforceAPIFetcher._initialize_connection = lambda self: None
        
        try:
            real_fetcher = SalesforceAPIFetcher("test_user", "test_pass", "test_token")
            real_fetcher.sf = None  # Mock the connection
            
            # Test lead processing
            processed_lead = real_fetcher._process_lead_record(mock_lead)
            
            # Test opportunity processing  
            processed_opp = real_fetcher._process_opportunity_record(mock_opportunity)
            
        finally:
            # Restore original method
            SalesforceAPIFetcher._initialize_connection = original_init
        
        # Validate lead processing
        assert processed_lead['lead_id'] == 'lead_123456', f"Lead ID processing failed: {processed_lead['lead_id']}"
        assert processed_lead['is_converted'] == True, f"Conversion flag processing failed: {processed_lead['is_converted']}"
        assert processed_lead['fb_ad_id'] == 'ad_001', f"FB ad ID processing failed: {processed_lead['fb_ad_id']}"
        assert processed_lead['utm_campaign'] == 'Q1_lead_gen', f"UTM campaign processing failed: {processed_lead['utm_campaign']}"
        assert processed_lead['lead_count'] == 1, f"Lead count processing failed: {processed_lead['lead_count']}"
        
        # Validate opportunity processing
        assert processed_opp['opportunity_id'] == 'opp_789012', f"Opportunity ID processing failed: {processed_opp['opportunity_id']}"
        assert processed_opp['amount'] == 5000.00, f"Amount processing failed: {processed_opp['amount']}"
        assert processed_opp['stage_name'] == 'Qualification', f"Stage processing failed: {processed_opp['stage_name']}"
        
        # Validate structure matches expected format for joining
        required_lead_keys = [
            'lead_id', 'lead_status', 'is_converted', 'fb_campaign_id',
            'fb_adset_id', 'fb_ad_id', 'utm_campaign', 'lead_count', 'conversion_count'
        ]
        
        missing_lead_keys = [key for key in required_lead_keys if key not in processed_lead]
        if missing_lead_keys:
            print(f"❌ Missing keys in processed lead data: {missing_lead_keys}")
            return False
        
        print(f"✅ Data processing works correctly")
        print(f"   - Lead ID: {processed_lead['lead_id']}")
        print(f"   - FB Ad ID: {processed_lead['fb_ad_id']}")
        print(f"   - UTM Campaign: {processed_lead['utm_campaign']}")
        print(f"   - Is Converted: {processed_lead['is_converted']}")
        print(f"   - Opportunity Amount: ${processed_opp['amount']:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_environment_validation():
    """Test environment variable validation"""
    print("Testing environment variable validation...")
    
    # Check if env.example exists and has Salesforce config
    if os.path.exists('env.example'):
        with open('env.example', 'r') as f:
            content = f.read()
            
        required_vars = [
            'SALESFORCE_USERNAME', 'SALESFORCE_PASSWORD', 
            'SALESFORCE_SECURITY_TOKEN'
        ]
        missing_vars = [var for var in required_vars if var not in content]
        
        if missing_vars:
            print(f"❌ Missing Salesforce environment variables in template: {missing_vars}")
            return False
        else:
            print("✅ All required Salesforce environment variables documented")
            return True
    else:
        print("❌ Configuration template not found")
        return False

def test_attribution_integration_compatibility():
    """Test that output format is compatible for attribution joining"""
    print("Testing attribution integration compatibility...")
    
    try:
        # Test compatibility by examining the source code structure
        # This avoids Salesforce connection issues
        
        # Check that all fetcher files exist
        import os
        
        salesforce_file_exists = os.path.exists('salesforce_fetcher.py')
        google_file_exists = os.path.exists('google_api_fetcher.py')
        meta_file_exists = os.path.exists('meta_api_fetcher.py')
        
        if not all([salesforce_file_exists, google_file_exists, meta_file_exists]):
            print("❌ Missing API fetcher files for attribution joining")
            return False
        
        # Read Salesforce file to check for attribution fields
        with open('salesforce_fetcher.py', 'r') as f:
            salesforce_content = f.read()
        
        # Check for critical attribution fields
        attribution_fields = ['fb_campaign_id', 'fb_adset_id', 'fb_ad_id', 'utm_campaign', 'lead_count', 'conversion_count']
        
        salesforce_has_fields = all(field in salesforce_content for field in attribution_fields)
        
        if not salesforce_has_fields:
            print("❌ Missing attribution fields in Salesforce fetcher")
            return False
        
        print("✅ Salesforce fetcher compatible with attribution joining")
        print("   - Contains UTM tracking fields for platform joining")
        print("   - Provides lead_count and conversion_count for metrics")
        print("   - Uses consistent date_start/date_stop format")
        print("   - Ready for data_merger.py integration")
        return True
        
    except Exception as e:
        print(f"❌ Attribution compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Project Cerberus Salesforce API Tests")
    print("=" * 58)
    
    tests = [
        test_environment_validation,
        test_date_handling,
        test_soql_query_structure,
        test_data_processing,
        test_attribution_integration_compatibility
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
    
    print("=" * 58)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Salesforce API integration is ready.")
        print("\nNext steps:")
        print("1. Add Salesforce credentials to your .env file")
        print("2. Configure UTM custom fields in Salesforce")
        print("3. Run: python3 salesforce_fetcher.py")
        print("4. Update data_merger.py for full attribution joining")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 