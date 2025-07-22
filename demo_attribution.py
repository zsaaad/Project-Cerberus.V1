#!/usr/bin/env python3
"""
Demonstration of Platform-Specific Attribution Logic
Shows Meta ID matching vs Google name matching with transparency flags.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock the data merger logic for demonstration
class AttributionDemo:
    """Demo of realistic attribution matching logic."""
    
    def __init__(self):
        self.platform_mapping = {
            'meta': 'Meta',
            'google': 'Google Ads'
        }
    
    def demo_attribution_scenarios(self):
        """Demonstrate different attribution scenarios."""
        print("🔗 Project Cerberus - Platform-Specific Attribution Demo")
        print("=" * 60)
        
        # Sample ad data from both platforms
        meta_ads = [
            {
                'platform': 'Meta',
                'platform_key': 'meta',
                'campaign_id': 'camp_meta_001',
                'campaign_name': 'Meta Lead Gen Q1',
                'adset_id': 'adset_meta_001',
                'ad_id': 'ad_meta_001',
                'ad_name': 'Demo CTA Creative A',
                'spend': 150.75,
                'clicks': 450,
                'total_conversions': 12  # Platform reported
            },
            {
                'platform': 'Meta',
                'platform_key': 'meta', 
                'campaign_id': 'camp_meta_002',
                'campaign_name': 'Meta Retargeting',
                'adset_id': 'adset_meta_002',
                'ad_id': 'ad_meta_002',
                'ad_name': 'Retargeting Creative B',
                'spend': 89.50,
                'clicks': 230,
                'total_conversions': 0  # Zero performance scenario
            }
        ]
        
        google_ads = [
            {
                'platform': 'Google Ads',
                'platform_key': 'google',
                'campaign_id': 'camp_google_001',
                'campaign_name': 'Google Search Q1',  # This will match by name
                'adset_id': 'adgroup_google_001', 
                'ad_id': 'ad_google_001',
                'ad_name': 'Search Text Ad',
                'spend': 245.30,
                'clicks': 380,
                'total_conversions': 18  # Platform reported
            },
            {
                'platform': 'Google Ads', 
                'platform_key': 'google',
                'campaign_id': 'camp_google_002',
                'campaign_name': 'Google Shopping Campaign',
                'adset_id': 'adgroup_google_002',
                'ad_id': 'ad_google_002', 
                'ad_name': 'Shopping Product Ad',
                'spend': 95.20,
                'clicks': 156,
                'total_conversions': 8  # Platform reported
            }
        ]
        
        # Realistic Salesforce lead data with actual field constraints
        salesforce_leads = [
            # Meta leads - Perfect ID matching available
            {
                'lead_id': 'lead_001',
                'lead_status': 'Qualified',
                'is_converted': True,
                'fb_campaign_id': 'camp_meta_001',  # Perfect match
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
                'email': 'john.doe@techcorp.com',
                'company': 'TechCorp Ltd'
            },
            {
                'lead_id': 'lead_002',
                'lead_status': 'New', 
                'is_converted': False,
                'fb_campaign_id': 'camp_meta_001',  # Same ad as lead_001
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
                'email': 'jane.smith@startup.io',
                'company': 'Startup Dynamics'
            },
            {
                'lead_id': 'lead_003',
                'lead_status': 'Qualified',
                'is_converted': True,
                'fb_campaign_id': 'camp_meta_001',  # Third lead from same ad
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
                'email': 'bob.wilson@enterprise.com',
                'company': 'Enterprise Solutions'
            },
            
            # Google leads - Only name-based matching available
            {
                'lead_id': 'lead_004',
                'lead_status': 'Qualified',
                'is_converted': False,
                'utm_campaign': 'Google Search Q1',  # Name match to Google campaign
                'utm_source': 'google',
                'utm_medium': 'cpc',
                'utm_term': 'saas software',
                'email': 'alice.johnson@growth.co',
                'company': 'Growth Co'
            },
            {
                'lead_id': 'lead_005',
                'lead_status': 'Converted',
                'is_converted': True,
                'utm_campaign': 'google search q1',  # Case-insensitive match
                'utm_source': 'google', 
                'utm_medium': 'cpc',
                'utm_term': 'marketing automation',
                'email': 'david.brown@scale.com',
                'company': 'Scale Inc'
            }
            # Note: No Salesforce leads for Google Shopping Campaign (no attribution)
        ]
        
        # Demonstrate attribution matching
        print("📊 PLATFORM-SPECIFIC ATTRIBUTION RESULTS")
        print()
        
        # Process Meta attribution (ID-based)
        print("🎯 Meta Attribution - ID-to-ID Matching (High Confidence)")
        print("-" * 55)
        
        for meta_ad in meta_ads:
            matching_leads = self._find_meta_leads(meta_ad, salesforce_leads)
            attribution_quality = 'ID_Matched' if matching_leads else 'No_Attribution'
            
            print(f"Ad: {meta_ad['ad_name']}")
            print(f"  Platform Conversions: {meta_ad['total_conversions']}")
            print(f"  Salesforce Leads: {len(matching_leads)}")
            print(f"  Attribution Quality: {attribution_quality}")
            if matching_leads:
                converted = sum(1 for lead in matching_leads if lead['is_converted'])
                updated_cpl = meta_ad['spend'] / len(matching_leads)
                print(f"  Lead Details: {len(matching_leads)} total, {converted} converted")
                print(f"  Updated CPL: ${updated_cpl:.2f} (vs platform estimate)")
                print(f"  Companies: {', '.join([lead['company'] for lead in matching_leads])}")
            print()
        
        # Process Google attribution (name-based)
        print("🔍 Google Attribution - Name-Based Matching (Best Effort)")
        print("-" * 58)
        
        for google_ad in google_ads:
            matching_leads = self._find_google_leads(google_ad, salesforce_leads)
            attribution_quality = 'Name_Matched_Best_Effort' if matching_leads else 'No_Attribution'
            
            print(f"Ad: {google_ad['ad_name']} (Campaign: {google_ad['campaign_name']})")
            print(f"  Platform Conversions: {google_ad['total_conversions']}")
            print(f"  Salesforce Leads: {len(matching_leads)}")
            print(f"  Attribution Quality: {attribution_quality}")
            if matching_leads:
                converted = sum(1 for lead in matching_leads if lead['is_converted'])
                updated_cpl = google_ad['spend'] / len(matching_leads)
                print(f"  Lead Details: {len(matching_leads)} total, {converted} converted")
                print(f"  Updated CPL: ${updated_cpl:.2f} (vs platform estimate)")
                print(f"  UTM Campaigns: {set([lead['utm_campaign'] for lead in matching_leads])}")
            else:
                print(f"  ⚠️  No name match found - relying on platform conversion data")
            print()
        
        # Attribution quality summary
        all_ads = meta_ads + google_ads
        all_leads_matched = []
        
        for ad in all_ads:
            if ad['platform_key'] == 'meta':
                leads = self._find_meta_leads(ad, salesforce_leads)
            else:
                leads = self._find_google_leads(ad, salesforce_leads)
            all_leads_matched.extend(leads)
        
        print("📈 ATTRIBUTION QUALITY SUMMARY")
        print("-" * 35)
        print(f"Total Ads Processed: {len(all_ads)}")
        print(f"Total Salesforce Leads: {len(salesforce_leads)}")
        print(f"Successfully Attributed Leads: {len(all_leads_matched)}")
        print()
        print("Attribution Quality Distribution:")
        print(f"  ID_Matched (Meta): {len([ad for ad in meta_ads if self._find_meta_leads(ad, salesforce_leads)])} ads")
        print(f"  Name_Matched_Best_Effort (Google): {len([ad for ad in google_ads if self._find_google_leads(ad, salesforce_leads)])} ads")
        print(f"  No_Attribution: {len([ad for ad in all_ads if not self._has_attribution(ad, salesforce_leads)])} ads")
        
        print("\n🎯 Business Impact:")
        print(f"  Platform Reported Conversions: {sum(ad['total_conversions'] for ad in all_ads)}")
        print(f"  Salesforce Actual Leads: {len(all_leads_matched)}")
        print(f"  Attribution Match Rate: {len(all_leads_matched)/len(salesforce_leads)*100:.1f}%")
        
        return True
    
    def _find_meta_leads(self, ad: Dict[str, Any], leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find Meta leads using perfect ID matching."""
        campaign_id = ad['campaign_id'] 
        adset_id = ad['adset_id']
        ad_id = ad['ad_id']
        
        matching_leads = []
        for lead in leads:
            if (lead.get('fb_campaign_id') == campaign_id and 
                lead.get('fb_adset_id') == adset_id and
                lead.get('fb_ad_id') == ad_id):
                matching_leads.append(lead)
        
        return matching_leads
    
    def _find_google_leads(self, ad: Dict[str, Any], leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find Google leads using name-based matching."""
        campaign_name = ad['campaign_name'].lower().strip()
        
        matching_leads = []
        for lead in leads:
            utm_campaign = lead.get('utm_campaign', '').lower().strip()
            if utm_campaign and utm_campaign == campaign_name:
                matching_leads.append(lead)
        
        return matching_leads
    
    def _has_attribution(self, ad: Dict[str, Any], leads: List[Dict[str, Any]]) -> bool:
        """Check if ad has any attribution."""
        if ad['platform_key'] == 'meta':
            return len(self._find_meta_leads(ad, leads)) > 0
        else:
            return len(self._find_google_leads(ad, leads)) > 0


def main():
    """Run the attribution demonstration."""
    demo = AttributionDemo()
    demo.demo_attribution_scenarios()
    
    print("\n✅ Attribution Demo Complete!")
    print("\nKey Insights:")
    print("• Meta: Perfect ID matching provides high-confidence attribution")
    print("• Google: Name-based matching provides best-effort attribution")
    print("• Attribution quality transparency helps assess data reliability")
    print("• Multiple leads per ad are properly aggregated")
    print("• Zero attribution scenarios are handled gracefully")
    
    print(f"\n🚀 Ready for Production:")
    print("• Update Salesforce with FB_Campaign_ID__c, FB_Adset_ID__c, FB_Ad_ID__c custom fields")
    print("• Ensure UTM_Campaign__c captures Google campaign names accurately")
    print("• Configure daily automated execution at 9:00 AM local time")
    print("• Connect to alert engine for proactive optimization insights")


if __name__ == "__main__":
    main() 