#!/usr/bin/env python3
"""
Updated test script for Data Merger with platform-specific attribution logic
Tests Meta ID-based matching and Google name-based matching with attribution quality flags.
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_meta_id_matching():
    """Test Meta perfect ID matching logic"""
    print("Testing Meta ID-based attribution matching...")
    
    try:
        from data_merger import CerberusDataMerger
        
        merger = CerberusDataMerger()
        
        # Mock Meta ad data
        meta_data = [{
            'platform': 'Meta',
            'platform_key': 'meta', 
            'campaign_id': 'camp_meta_001',
            'campaign_name': 'Meta Lead Gen Q1',
            'adset_id': 'adset_meta_001',
            'adset_name': 'Malaysia Tech Pros',
            'ad_id': 'ad_meta_001',
            'ad_name': 'Demo CTA Creative',
            'spend': 45.67,
            'clicks': 234,
            'total_conversions': 8,
        }]
        
        # Mock Salesforce lead with matching Meta IDs
        salesforce_data = [{
            'lead_id': 'lead_001',
            'lead_status': 'Qualified',
            'is_converted': True,
            'fb_campaign_id': 'camp_meta_001',  # Perfect match
            'fb_adset_id': 'adset_meta_001',    # Perfect match
            'fb_ad_id': 'ad_meta_001',          # Perfect match
            'email': 'john.doe@company.com',
            'company': 'ABC Corp',
            'lead_source': 'Facebook'
        }]
        
        # Test Meta attribution
        unified_data = merger.merge_platform_data(meta_data, [], salesforce_data)
        
        # Validate Meta matching
        meta_record = unified_data[0]
        assert meta_record['attribution_quality'] == 'ID_Matched', f"Expected ID_Matched, got {meta_record['attribution_quality']}"
        assert meta_record['sf_lead_count'] == 1, f"Expected 1 lead, got {meta_record['sf_lead_count']}"
        assert meta_record['has_salesforce_data'] == True, "Expected Salesforce data"
        
        print("✅ Meta ID matching works correctly")
        print(f"   - Attribution Quality: {meta_record['attribution_quality']}")
        print(f"   - Salesforce Leads Matched: {meta_record['sf_lead_count']}")
        return True
        
    except Exception as e:
        print(f"❌ Meta ID matching test failed: {e}")
        return False

def test_google_name_matching():
    """Test Google name-based matching logic"""
    print("Testing Google name-based attribution matching...")
    
    try:
        from data_merger import CerberusDataMerger
        
        merger = CerberusDataMerger()
        
        # Mock Google ad data
        google_data = [{
            'platform': 'Google Ads',
            'platform_key': 'google',
            'campaign_id': 'camp_google_001', 
            'campaign_name': 'Google Search Q1',  # This will match UTM_Campaign
            'adset_id': 'adgroup_google_001',
            'adset_name': 'Tech Keywords',
            'ad_id': 'ad_google_001',
            'ad_name': 'Search Ad Text',
            'spend': 67.89,
            'clicks': 145,
            'total_conversions': 12,
        }]
        
        # Mock Salesforce lead with matching campaign name
        salesforce_data = [{
            'lead_id': 'lead_003',
            'lead_status': 'Qualified',
            'is_converted': False,
            'utm_campaign': 'Google Search Q1',  # Name match
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'email': 'bob.wilson@startup.com',
            'company': 'Startup LLC',
            'lead_source': 'Google'
        }]
        
        # Test Google attribution
        unified_data = merger.merge_platform_data([], google_data, salesforce_data)
        
        # Validate Google matching
        google_record = unified_data[0]
        assert google_record['attribution_quality'] == 'Name_Matched_Best_Effort', f"Expected Name_Matched_Best_Effort, got {google_record['attribution_quality']}"
        assert google_record['sf_lead_count'] == 1, f"Expected 1 lead, got {google_record['sf_lead_count']}"
        assert google_record['has_salesforce_data'] == True, "Expected Salesforce data"
        
        print("✅ Google name matching works correctly")
        print(f"   - Attribution Quality: {google_record['attribution_quality']}")
        print(f"   - Salesforce Leads Matched: {google_record['sf_lead_count']}")
        return True
        
    except Exception as e:
        print(f"❌ Google name matching test failed: {e}")
        return False

def test_no_attribution_scenario():
    """Test scenarios with no attribution matches"""
    print("Testing no attribution scenarios...")
    
    try:
        from data_merger import CerberusDataMerger
        
        merger = CerberusDataMerger()
        
        # Mock ad data with no matching Salesforce data
        meta_data = [{
            'platform': 'Meta',
            'platform_key': 'meta',
            'campaign_id': 'camp_meta_999',  # Won't match
            'adset_id': 'adset_meta_999',
            'ad_id': 'ad_meta_999',
            'spend': 25.50,
            'total_conversions': 3,
        }]
        
        # Mock Salesforce data that won't match
        salesforce_data = [{
            'lead_id': 'lead_999',
            'fb_campaign_id': 'different_campaign',  # Won't match
            'fb_adset_id': 'different_adset',
            'fb_ad_id': 'different_ad',
        }]
        
        # Test no attribution
        unified_data = merger.merge_platform_data(meta_data, [], salesforce_data)
        
        # Validate no attribution
        record = unified_data[0]
        assert record['attribution_quality'] == 'No_Attribution', f"Expected No_Attribution, got {record['attribution_quality']}"
        assert record['sf_lead_count'] == 0, f"Expected 0 leads, got {record['sf_lead_count']}"
        assert record['has_salesforce_data'] == False, "Expected no Salesforce data"
        
        print("✅ No attribution scenario works correctly")
        print(f"   - Attribution Quality: {record['attribution_quality']}")
        print(f"   - Salesforce Leads: {record['sf_lead_count']}")
        return True
        
    except Exception as e:
        print(f"❌ No attribution test failed: {e}")
        return False

def test_attribution_quality_column():
    """Test that attribution quality column is properly included in output"""
    print("Testing attribution quality column inclusion...")
    
    try:
        from data_merger import CerberusDataMerger
        
        merger = CerberusDataMerger()
        
        # Mixed data with different attribution qualities
        meta_data = [{
            'platform_key': 'meta',
            'campaign_id': 'camp_meta_001',
            'adset_id': 'adset_meta_001', 
            'ad_id': 'ad_meta_001',
        }]
        
        google_data = [{
            'platform_key': 'google',
            'campaign_name': 'Google Search Q1',
        }]
        
        salesforce_data = [
            {
                'lead_id': 'lead_001',
                'fb_campaign_id': 'camp_meta_001',
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
            },
            {
                'lead_id': 'lead_002', 
                'utm_campaign': 'Google Search Q1',
            }
        ]
        
        # Test complete attribution
        unified_data = merger.merge_platform_data(meta_data, google_data, salesforce_data)
        
        # Validate attribution quality columns exist
        attribution_qualities = []
        for record in unified_data:
            assert 'attribution_quality' in record, "attribution_quality column missing"
            attribution_qualities.append(record['attribution_quality'])
        
        # Should have both types of attribution
        assert 'ID_Matched' in attribution_qualities, "Missing ID_Matched attribution"
        assert 'Name_Matched_Best_Effort' in attribution_qualities, "Missing Name_Matched_Best_Effort attribution"
        
        print("✅ Attribution quality column works correctly")
        print(f"   - Attribution qualities found: {set(attribution_qualities)}")
        return True
        
    except Exception as e:
        print(f"❌ Attribution quality column test failed: {e}")
        return False

def test_multiple_leads_per_ad():
    """Test handling multiple leads for the same ad"""
    print("Testing multiple leads per ad aggregation...")
    
    try:
        from data_merger import CerberusDataMerger
        
        merger = CerberusDataMerger()
        
        # Single Meta ad
        meta_data = [{
            'platform_key': 'meta',
            'campaign_id': 'camp_meta_001',
            'adset_id': 'adset_meta_001',
            'ad_id': 'ad_meta_001',
            'spend': 100.0,
            'total_conversions': 5,  # Platform reported
        }]
        
        # Multiple Salesforce leads for same ad
        salesforce_data = [
            {
                'lead_id': 'lead_001',
                'lead_status': 'Qualified',
                'is_converted': True,
                'fb_campaign_id': 'camp_meta_001',
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
            },
            {
                'lead_id': 'lead_002', 
                'lead_status': 'New',
                'is_converted': False,
                'fb_campaign_id': 'camp_meta_001',
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
            },
            {
                'lead_id': 'lead_003',
                'lead_status': 'Qualified', 
                'is_converted': True,
                'fb_campaign_id': 'camp_meta_001',
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
            }
        ]
        
        # Test aggregation
        unified_data = merger.merge_platform_data(meta_data, [], salesforce_data)
        
        # Validate aggregation
        record = unified_data[0]
        assert record['sf_lead_count'] == 3, f"Expected 3 leads, got {record['sf_lead_count']}"
        assert record['sf_converted_count'] == 2, f"Expected 2 conversions, got {record['sf_converted_count']}"
        assert record['total_conversions'] == 3, f"Expected total_conversions to be updated to 3, got {record['total_conversions']}"
        assert abs(record['cost_per_lead'] - 33.33) < 0.01, f"Expected CPL ~33.33, got {record['cost_per_lead']}"
        
        print("✅ Multiple leads per ad aggregation works correctly")
        print(f"   - Leads: {record['sf_lead_count']}, Conversions: {record['sf_converted_count']}")
        print(f"   - Cost per Lead: ${record['cost_per_lead']:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Multiple leads aggregation test failed: {e}")
        return False

def main():
    """Run all updated attribution tests"""
    print("🧪 Running Project Cerberus Updated Data Merger Tests")
    print("=" * 65)
    
    tests = [
        test_meta_id_matching,
        test_google_name_matching,
        test_no_attribution_scenario,
        test_attribution_quality_column,
        test_multiple_leads_per_ad
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
            print("   Make sure data_merger.py exists and dependencies are installed")
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            print()
    
    print("=" * 65)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All attribution tests passed!")
        print("\nNew attribution features verified:")
        print("✅ Meta ID-to-ID matching (high confidence)")
        print("✅ Google name-based matching (best effort)")
        print("✅ Attribution quality transparency")
        print("✅ Multiple leads per ad aggregation")
        print("✅ No attribution fallback handling")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 