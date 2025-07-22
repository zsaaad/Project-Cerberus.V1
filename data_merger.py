"""
Unified Data Merger for Project Cerberus
Combines Meta Marketing API and Google Ads API data into a single dataset.

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
    Combines data from Meta and Google Ads APIs into a unified dataset
    optimized for Project Cerberus alert processing.
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
                          google_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge Meta and Google Ads data into unified format.
        
        Args:
            meta_data: List of Meta ad performance dictionaries
            google_data: List of Google Ads performance dictionaries
            
        Returns:
            Unified list of ad performance data with platform identification
        """
        try:
            self.logger.info(f"Merging {len(meta_data)} Meta records with {len(google_data)} Google records")
            
            unified_data = []
            
            # Process Meta data
            for record in meta_data:
                unified_record = self._standardize_record(record, 'meta')
                unified_data.append(unified_record)
            
            # Process Google data  
            for record in google_data:
                unified_record = self._standardize_record(record, 'google')
                unified_data.append(unified_record)
            
            self.logger.info(f"Created unified dataset with {len(unified_data)} total records")
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
        record['zero_performance_flag'] = (
            record['spend'] > 50.0 and record['total_conversions'] == 0
        )
        
        # Funnel Mismatch Alert (high CTR, low conversion rate)
        record['funnel_mismatch_flag'] = (
            record['ctr'] > 2.0 and record['click_to_conversion_rate'] < 1.0
        )
        
        # Top Performer flag requires market benchmarking (done in alert engine)
        # For now, flag high-converting, low-cost ads
        record['top_performer_flag'] = (
            record['total_conversions'] > 5 and record['cost_per_lead'] > 0 and record['cost_per_lead'] < 10.0
        )
        
        return record
    
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
    Demonstration of unified data processing for Project Cerberus.
    """
    print("🔄 Project Cerberus - Unified Data Processing")
    print("=" * 50)
    
    try:
        # Import the API fetchers
        from meta_api_fetcher import MetaAPIFetcher
        from google_api_fetcher import GoogleAPIFetcher
        
        # Initialize merger
        merger = CerberusDataMerger()
        
        # For demo purposes, we'll create sample data
        # In production, this would fetch from actual APIs
        
        print("📊 Creating sample unified dataset...")
        
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
                'total_conversions': 8,
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
                'total_conversions': 12,
                'lead_conversions': 12,
                'cost_per_lead': 5.66,
                'click_to_conversion_rate': 8.28
            }
        ]
        
        # Merge data
        unified_data = merger.merge_platform_data(meta_sample, google_sample)
        
        # Generate summary
        summary = merger.generate_alert_summary(unified_data)
        
        print("\n📈 Unified Dataset Summary:")
        print(f"   Total Records: {summary['total_records']}")
        print(f"   Total Spend: ${summary['total_spend']:.2f}")
        print(f"   Total Conversions: {summary['total_conversions']}")
        print(f"   Platforms: {summary['platforms']}")
        print(f"   Zero Performance Alerts: {summary['zero_performance_alerts']}")
        print(f"   Funnel Mismatch Alerts: {summary['funnel_mismatch_alerts']}")
        print(f"   Top Performer Alerts: {summary['top_performer_alerts']}")
        
        # Save unified data
        csv_file = merger.save_unified_data(unified_data)
        print(f"\n💾 Unified dataset saved to: {csv_file}")
        print("✅ Ready for Cerberus alert processing!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure both meta_api_fetcher.py and google_api_fetcher.py exist")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 