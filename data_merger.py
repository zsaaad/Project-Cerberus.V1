"""
Unified Data Merger for Project Cerberus
Combines Meta Marketing API, Google Ads API, and Salesforce data into a single attribution dataset.

Author: Project Cerberus Team  
Version: 1.0
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class CerberusDataMerger:
    """
    Combines data from Meta Marketing API, Google Ads API, and Salesforce
    into a fully attributed dataset optimized for Project Cerberus alert processing.
    """
    
    def __init__(self):
        """Initialize the data merger."""
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Platform mapping for unified analysis
        self.platform_mapping = {
            'meta': 'Meta',
            'google': 'Google Ads'
        }
    
    def merge_platform_data(self, meta_data: List[Dict[str, Any]], 
                          google_data: List[Dict[str, Any]], 
                          salesforce_data: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Merge Meta, Google Ads, and Salesforce data into unified attribution format.
        
        Args:
            meta_data: List of Meta ad performance dictionaries
            google_data: List of Google Ads performance dictionaries
            salesforce_data: Optional list of Salesforce lead dictionaries for attribution
            
        Returns:
            Unified list of ad performance data with attribution and platform identification
        """
        try:
            salesforce_count = len(salesforce_data) if salesforce_data else 0
            self.logger.info(f"Merging {len(meta_data)} Meta records with {len(google_data)} Google records and {salesforce_count} Salesforce leads")
            
            unified_data = []
            
            # Process Meta data
            for record in meta_data:
                unified_record = self._standardize_record(record, 'meta')
                unified_data.append(unified_record)
            
            # Process Google data  
            for record in google_data:
                unified_record = self._standardize_record(record, 'google')
                unified_data.append(unified_record)
            
            # Perform attribution join with Salesforce data
            if salesforce_data:
                unified_data = self._join_salesforce_attribution(unified_data, salesforce_data)
            
            self.logger.info(f"Created unified attributed dataset with {len(unified_data)} total records")
            return unified_data
            
        except Exception as e:
            self.logger.error(f"Error merging platform data: {e}")
            raise
    
    def _standardize_record(self, record: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Standardize a single record with platform identification and unified metrics.
        
        Args:
            record: Original platform record
            platform: Platform identifier ('meta' or 'google')
            
        Returns:
            Standardized record for Cerberus analysis
        """
        # Create base unified record
        unified_record = {
            # Platform Identification
            'platform': self.platform_mapping[platform],
            'platform_key': platform,
            
            # Unified Campaign Structure
            'account_id': record.get('account_id', ''),
            'campaign_id': record.get('campaign_id', ''),
            'campaign_name': record.get('campaign_name', ''),
            'adset_id': record.get('adset_id', ''),
            'adset_name': record.get('adset_name', ''),
            'ad_id': record.get('ad_id', ''),
            'ad_name': record.get('ad_name', ''),
            
            # Date Information
            'date_start': record.get('date_start', ''),
            'date_stop': record.get('date_stop', ''),
            
            # Core Performance Metrics
            'spend': float(record.get('spend', 0)),
            'impressions': int(record.get('impressions', 0)),
            'clicks': int(record.get('clicks', 0)),
            'unique_clicks': int(record.get('unique_clicks', 0)),
            'reach': int(record.get('reach', 0)),
            'frequency': float(record.get('frequency', 0)),
            
            # Calculated Metrics
            'ctr': float(record.get('ctr', 0)),
            'cost_per_unique_click': float(record.get('cost_per_unique_click', 0)),
            'cost_per_1000_people_reached': float(record.get('cost_per_1000_people_reached', 0)),
            
            # Conversion Metrics (Critical for Cerberus Alerts)
            'total_conversions': float(record.get('total_conversions', 0)),
            'lead_conversions': float(record.get('lead_conversions', 0)),
            'total_conversion_value': float(record.get('total_conversion_value', 0)),
            
            # Derived Metrics for Alerts
            'cost_per_conversion': float(record.get('cost_per_conversion', 0)),
            'cost_per_lead': float(record.get('cost_per_lead', 0)),
            'click_to_conversion_rate': float(record.get('click_to_conversion_rate', 0)),
            
            # Status Information
            'status': record.get('status', ''),
            'effective_status': record.get('effective_status', ''),
            
            # Cerberus Alert Flags (calculated)
            'zero_performance_flag': False,
            'top_performer_flag': False, 
            'funnel_mismatch_flag': False,
        }
        
        # Calculate Cerberus alert flags
        unified_record = self._calculate_alert_flags(unified_record)
        
        # Create unique identifier for cross-platform tracking
        unified_record['unified_id'] = f"{platform}_{unified_record['campaign_id']}_{unified_record['adset_id']}_{unified_record['ad_id']}"
        
        return unified_record
    
    def _calculate_alert_flags(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate preliminary alert flags for Cerberus analysis.
        
        Args:
            record: Unified record
            
        Returns:
            Record with alert flags calculated
        """
        # Zero Performance Alert (spend > $50, conversions = 0)
        # Use Salesforce data if available, otherwise use platform data
        conversion_count = record.get('sf_lead_count', record.get('total_conversions', 0))
        record['zero_performance_flag'] = (
            record['spend'] > 50.0 and conversion_count == 0
        )
        
        # Funnel Mismatch Alert (high CTR, low conversion rate)
        record['funnel_mismatch_flag'] = (
            record['ctr'] > 2.0 and record['click_to_conversion_rate'] < 1.0
        )
        
        # Top Performer flag requires market benchmarking (done in alert engine)
        # For now, flag high-converting, low-cost ads using Salesforce data when available
        lead_count = record.get('sf_lead_count', record.get('total_conversions', 0))
        cost_per_lead = record.get('cost_per_lead', 0)
        record['top_performer_flag'] = (
            lead_count > 5 and cost_per_lead > 0 and cost_per_lead < 10.0
        )
        
        return record
    
    def _join_salesforce_attribution(self, unified_data: List[Dict[str, Any]], 
                                   salesforce_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform platform-specific attribution joins with Salesforce lead data.
        - Meta: ID-to-ID matching (high confidence)
        - Google: Name-based matching (best effort)
        
        Args:
            unified_data: Unified ad performance data from Meta and Google
            salesforce_leads: Salesforce lead data with platform-specific attribution fields
            
        Returns:
            Enriched unified data with platform-specific attribution
        """
        try:
            self.logger.info("Performing platform-specific attribution joins with Salesforce data")
            
            # Create platform-specific lookup dictionaries
            meta_lookup, google_lookup = self._create_attribution_lookups(salesforce_leads)
            
            self.logger.info(f"Created Meta ID lookup with {len(meta_lookup)} keys")
            self.logger.info(f"Created Google name lookup with {len(google_lookup)} keys")
            
            # Enrich each ad record with platform-specific attribution
            enriched_data = []
            meta_matches = 0
            google_matches = 0
            
            for ad_record in unified_data:
                platform = ad_record.get('platform_key', '')
                
                if platform == 'meta':
                    matching_leads, attribution_quality = self._find_meta_matches(ad_record, meta_lookup)
                    meta_matches += len(matching_leads)
                elif platform == 'google':
                    matching_leads, attribution_quality = self._find_google_matches(ad_record, google_lookup)
                    google_matches += len(matching_leads)
                else:
                    matching_leads, attribution_quality = [], 'No_Attribution'
                
                # Aggregate Salesforce metrics for this ad
                sf_metrics = self._aggregate_salesforce_metrics(matching_leads)
                
                # Add attribution quality flag
                sf_metrics['attribution_quality'] = attribution_quality
                
                # Enrich the ad record with Salesforce data
                enriched_record = {**ad_record, **sf_metrics}
                
                # Update conversion metrics with Salesforce truth
                if sf_metrics['sf_lead_count'] > 0:
                    enriched_record['total_conversions'] = sf_metrics['sf_lead_count']
                    enriched_record['lead_conversions'] = sf_metrics['sf_lead_count']
                    enriched_record['cost_per_lead'] = (
                        enriched_record['spend'] / sf_metrics['sf_lead_count'] 
                        if sf_metrics['sf_lead_count'] > 0 else 0
                    )
                
                # Recalculate Cerberus alert flags with Salesforce data
                enriched_record = self._calculate_alert_flags(enriched_record)
                
                enriched_data.append(enriched_record)
            
            self.logger.info(f"Attribution join complete: {meta_matches} Meta ID matches, {google_matches} Google name matches")
            return enriched_data
            
        except Exception as e:
            self.logger.error(f"Error in Salesforce attribution join: {e}")
            raise
    
    def _create_attribution_lookups(self, salesforce_leads: List[Dict[str, Any]]) -> tuple:
        """
        Create platform-specific lookup dictionaries for attribution joining.
        
        Args:
            salesforce_leads: Salesforce lead data
            
        Returns:
            Tuple of (meta_lookup, google_lookup) dictionaries
        """
        meta_lookup = {}  # Key: composite Meta ID key, Value: list of leads
        google_lookup = {}  # Key: campaign name, Value: list of leads
        
        for lead in salesforce_leads:
            # Meta ID-based lookup (perfect matching)
            fb_campaign_id = lead.get('fb_campaign_id', '')
            fb_adset_id = lead.get('fb_adset_id', '')
            fb_ad_id = lead.get('fb_ad_id', '')
            
            if fb_campaign_id and fb_adset_id and fb_ad_id:
                # Create composite key for exact matching
                meta_key = f"{fb_campaign_id}|{fb_adset_id}|{fb_ad_id}"
                if meta_key not in meta_lookup:
                    meta_lookup[meta_key] = []
                meta_lookup[meta_key].append(lead)
            
            # Google name-based lookup (best effort matching)
            utm_campaign = lead.get('utm_campaign', '').strip()
            if utm_campaign:
                # Use campaign name as key (case-insensitive)
                google_key = utm_campaign.lower()
                if google_key not in google_lookup:
                    google_lookup[google_key] = []
                google_lookup[google_key].append(lead)
        
        return meta_lookup, google_lookup
    
    def _find_meta_matches(self, ad_record: Dict[str, Any], meta_lookup: Dict[str, List[Dict[str, Any]]]) -> tuple:
        """
        Find Meta leads using perfect ID matching.
        
        Args:
            ad_record: Meta ad performance record
            meta_lookup: Meta ID lookup dictionary
            
        Returns:
            Tuple of (matching_leads, attribution_quality)
        """
        campaign_id = ad_record.get('campaign_id', '')
        adset_id = ad_record.get('adset_id', '')
        ad_id = ad_record.get('ad_id', '')
        
        if campaign_id and adset_id and ad_id:
            composite_key = f"{campaign_id}|{adset_id}|{ad_id}"
            matching_leads = meta_lookup.get(composite_key, [])
            
            if matching_leads:
                return matching_leads, 'ID_Matched'
        
        return [], 'No_Attribution'
    
    def _find_google_matches(self, ad_record: Dict[str, Any], google_lookup: Dict[str, List[Dict[str, Any]]]) -> tuple:
        """
        Find Google leads using best-effort name matching.
        
        Args:
            ad_record: Google ad performance record  
            google_lookup: Google campaign name lookup dictionary
            
        Returns:
            Tuple of (matching_leads, attribution_quality)
        """
        campaign_name = ad_record.get('campaign_name', '').strip().lower()
        
        if campaign_name:
            # Direct name match
            matching_leads = google_lookup.get(campaign_name, [])
            
            if matching_leads:
                return matching_leads, 'Name_Matched_Best_Effort'
            
            # Fallback: partial name matching (for V1, could be enhanced later)
            for lookup_name, leads in google_lookup.items():
                if campaign_name in lookup_name or lookup_name in campaign_name:
                    self.logger.warning(f"Partial name match: '{campaign_name}' matched with '{lookup_name}'")
                    return leads, 'Name_Matched_Best_Effort'
        
        return [], 'No_Attribution'
    
    def _aggregate_salesforce_metrics(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate Salesforce metrics for a single ad.
        
        Args:
            leads: List of Salesforce leads for this ad
            
        Returns:
            Aggregated Salesforce metrics dictionary
        """
        if not leads:
            return {
                'sf_lead_count': 0,
                'sf_converted_count': 0,
                'sf_conversion_rate': 0,
                'sf_total_opportunity_value': 0,
                'sf_lead_statuses': '',
                'sf_lead_sources': '',
                'sf_first_lead_date': '',
                'sf_last_lead_date': '',
                'has_salesforce_data': False,
                'attribution_quality': 'No_Attribution'
            }
        
        # Aggregate metrics
        lead_count = len(leads)
        converted_count = sum(1 for lead in leads if lead.get('is_converted', False))
        conversion_rate = (converted_count / lead_count * 100) if lead_count > 0 else 0
        
        # Get unique statuses and sources
        statuses = list(set([lead.get('lead_status', '') for lead in leads if lead.get('lead_status')]))
        sources = list(set([lead.get('lead_source', '') for lead in leads if lead.get('lead_source')]))
        
        # Date range
        lead_dates = [lead.get('created_date', '') for lead in leads if lead.get('created_date')]
        lead_dates.sort()
        first_date = lead_dates[0][:10] if lead_dates else ''
        last_date = lead_dates[-1][:10] if lead_dates else ''
        
        return {
            'sf_lead_count': lead_count,
            'sf_converted_count': converted_count,
            'sf_conversion_rate': conversion_rate,
            'sf_total_opportunity_value': 0,  # Would need opportunity joining for this
            'sf_lead_statuses': ', '.join(statuses),
            'sf_lead_sources': ', '.join(sources),
            'sf_first_lead_date': first_date,
            'sf_last_lead_date': last_date,
            'has_salesforce_data': True,
            
            # Individual lead details (first lead for reference)
            'sf_first_lead_id': leads[0].get('lead_id', ''),
            'sf_first_lead_email': leads[0].get('email', ''),
            'sf_first_lead_company': leads[0].get('company', ''),
        }
    
    def generate_alert_summary(self, unified_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for alert processing.
        
        Args:
            unified_data: Unified dataset
            
        Returns:
            Alert summary statistics
        """
        if not unified_data:
            return {}
        
        df = pd.DataFrame(unified_data)
        
        summary = {
            # Overall Stats
            'total_records': len(unified_data),
            'total_spend': df['spend'].sum(),
            'total_conversions': df['total_conversions'].sum(),
            'platforms': df['platform'].value_counts().to_dict(),
            
            # Alert Counts
            'zero_performance_alerts': df['zero_performance_flag'].sum(),
            'funnel_mismatch_alerts': df['funnel_mismatch_flag'].sum(), 
            'top_performer_alerts': df['top_performer_flag'].sum(),
            
            # Performance Metrics
            'avg_ctr': df['ctr'].mean(),
            'avg_cost_per_lead': df[df['cost_per_lead'] > 0]['cost_per_lead'].mean() if len(df[df['cost_per_lead'] > 0]) > 0 else 0,
            'avg_conversion_rate': df['click_to_conversion_rate'].mean(),
            
            # Date Range
            'date_start': df['date_start'].iloc[0] if len(df) > 0 else '',
            'date_stop': df['date_stop'].iloc[0] if len(df) > 0 else '',
        }
        
        return summary
    
    def save_unified_data(self, unified_data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save unified data to CSV for Cerberus pipeline processing.
        
        Args:
            unified_data: Unified dataset
            filename: Optional custom filename
            
        Returns:
            Path to saved CSV file
        """
        if not filename:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            filename = f'cerberus_unified_data_{yesterday}.csv'
        
        df = pd.DataFrame(unified_data)
        df.to_csv(filename, index=False)
        
        self.logger.info(f"Unified data saved to {filename}")
        return filename


def main():
    """
    Demonstration of complete attribution data processing for Project Cerberus.
    """
    print("🔄 Project Cerberus - Complete Attribution Data Processing")
    print("=" * 60)
    
    try:
        # Import all API fetchers
        from meta_api_fetcher import MetaAPIFetcher
        from google_api_fetcher import GoogleAPIFetcher
        from salesforce_fetcher import SalesforceAPIFetcher
        
        # Initialize merger
        merger = CerberusDataMerger()
        
        # For demo purposes, we'll create sample data
        # In production, this would fetch from actual APIs
        
        print("📊 Creating sample attribution dataset...")
        
        # Sample Meta data
        meta_sample = [
            {
                'account_id': 'act_123456789',
                'campaign_id': 'camp_meta_001',
                'campaign_name': 'Meta Lead Gen Q1',
                'adset_id': 'adset_meta_001', 
                'adset_name': 'Malaysia Tech Pros',
                'ad_id': 'ad_meta_001',
                'ad_name': 'Demo CTA Creative',
                'date_start': '2025-01-20',
                'date_stop': '2025-01-20',
                'spend': 45.67,
                'impressions': 12543,
                'clicks': 234,
                'ctr': 1.87,
                'total_conversions': 8,  # Platform reported
                'lead_conversions': 8,
                'cost_per_lead': 5.71,
                'click_to_conversion_rate': 3.42
            }
        ]
        
        # Sample Google data  
        google_sample = [
            {
                'account_id': '9876543210',
                'campaign_id': 'camp_google_001',
                'campaign_name': 'Google Search Q1',
                'adset_id': 'adgroup_google_001',
                'adset_name': 'Tech Keywords',
                'ad_id': 'ad_google_001', 
                'ad_name': 'Search Ad Text',
                'date_start': '2025-01-20',
                'date_stop': '2025-01-20',
                'spend': 67.89,
                'impressions': 8765,
                'clicks': 145,
                'ctr': 1.65,
                'total_conversions': 12,  # Platform reported
                'lead_conversions': 12,
                'cost_per_lead': 5.66,
                'click_to_conversion_rate': 8.28
            }
        ]
        
        # Sample Salesforce data with realistic field mapping
        salesforce_sample = [
            {
                'lead_id': 'lead_001',
                'lead_status': 'Qualified',
                'is_converted': True,
                # Meta attribution - Perfect ID matching
                'fb_campaign_id': 'camp_meta_001',
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
                'email': 'john.doe@company.com',
                'company': 'ABC Corp',
                'lead_source': 'Facebook',
                'created_date': '2025-01-20T10:30:00.000Z',
                'lead_count': 1,
                'conversion_count': 1
            },
            {
                'lead_id': 'lead_002',
                'lead_status': 'New',
                'is_converted': False,
                # Meta attribution - Same ad as lead_001
                'fb_campaign_id': 'camp_meta_001',
                'fb_adset_id': 'adset_meta_001',
                'fb_ad_id': 'ad_meta_001',
                'email': 'jane.smith@company.com',
                'company': 'XYZ Inc',
                'lead_source': 'Facebook',
                'created_date': '2025-01-20T14:15:00.000Z',
                'lead_count': 1,
                'conversion_count': 0
            },
            {
                'lead_id': 'lead_003',
                'lead_status': 'Qualified',
                'is_converted': False,
                # Google attribution - Name-based matching only
                'utm_campaign': 'Google Search Q1',  # Matches campaign_name from Google data
                'utm_source': 'google',
                'utm_medium': 'cpc',
                'utm_term': 'tech keywords',
                'email': 'bob.wilson@startup.com',
                'company': 'Startup LLC',
                'lead_source': 'Google',
                'created_date': '2025-01-20T16:45:00.000Z',
                'lead_count': 1,
                'conversion_count': 0
            }
        ]
        
        # Merge data with Salesforce attribution
        print("🔗 Performing attribution join with Salesforce data...")
        unified_data = merger.merge_platform_data(meta_sample, google_sample, salesforce_sample)
        
        # Generate summary
        summary = merger.generate_alert_summary(unified_data)
        
        print("\n📈 Complete Attribution Summary:")
        print(f"   Total Records: {summary['total_records']}")
        print(f"   Total Spend: ${summary['total_spend']:.2f}")
        print(f"   Platform Reported Conversions: {meta_sample[0]['total_conversions'] + google_sample[0]['total_conversions']}")
        print(f"   Salesforce Actual Leads: {len(salesforce_sample)}")
        print(f"   Platforms: {summary['platforms']}")
        
        # Show attribution details for each platform
        if unified_data:
            print(f"\n🔍 Platform-Specific Attribution Results:")
            for i, record in enumerate(unified_data):
                platform = record.get('platform', 'Unknown')
                attribution_quality = record.get('attribution_quality', 'Unknown')
                sf_lead_count = record.get('sf_lead_count', 0)
                
                print(f"   {i+1}. {platform} - {record['ad_name']}:")
                print(f"      Attribution Quality: {attribution_quality}")
                print(f"      Platform Conversions: {record.get('total_conversions', 0)} → Salesforce Leads: {sf_lead_count}")
                print(f"      Cost per Lead: ${record.get('cost_per_lead', 0):.2f}")
        
        print(f"\n🚨 Alert Flags:")
        print(f"   Zero Performance Alerts: {summary['zero_performance_alerts']}")
        print(f"   Funnel Mismatch Alerts: {summary['funnel_mismatch_alerts']}")
        print(f"   Top Performer Alerts: {summary['top_performer_alerts']}")
        
        # Show attribution quality distribution
        attribution_quality_counts = {}
        for record in unified_data:
            quality = record.get('attribution_quality', 'Unknown')
            attribution_quality_counts[quality] = attribution_quality_counts.get(quality, 0) + 1
        
        print(f"\n📊 Attribution Quality Distribution:")
        for quality, count in attribution_quality_counts.items():
            print(f"   {quality}: {count} records")
        
        # Save unified data
        csv_file = merger.save_unified_data(unified_data)
        print(f"\n💾 Complete attribution dataset saved to: {csv_file}")
        print("✅ Ready for Cerberus alert engine!")
        print("🎯 End-to-end attribution chain complete: Ad Spend → Leads → Conversions")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all API fetchers (meta, google, salesforce) exist")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 