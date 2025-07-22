"""
Meta Marketing API Data Fetcher for Project Cerberus
Fetches yesterday's ad-level performance data for performance marketing analysis.

Author: Project Cerberus Team  
Version: 1.0
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.exceptions import FacebookRequestError
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MetaAPIFetcher:
    """
    Fetches Meta Marketing API data for Project Cerberus performance analysis.
    Designed to support Zero Performance, Top Performer, and Funnel Mismatch alerts.
    """
    
    def __init__(self, access_token: str, ad_account_id: str, app_id: str, app_secret: str):
        """
        Initialize the Meta API fetcher.
        
        Args:
            access_token: Meta API access token
            ad_account_id: Meta Ad Account ID (format: act_1234567890)
            app_id: Meta App ID
            app_secret: Meta App Secret
        """
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.app_id = app_id
        self.app_secret = app_secret
        
        # Initialize Facebook API
        FacebookAdsApi.init(app_id, app_secret, access_token)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Fields optimized for Cerberus alert requirements
        self.fields = [
            # Identifiers & Structure
            'campaign_id',
            'campaign_name', 
            'adset_id',
            'adset_name',
            'ad_id',
            'ad_name',
            'account_id',
            
            # Core Performance Metrics (for Zero Performance & Top Performer alerts)
            'spend',
            'impressions',
            'clicks', 
            'ctr',
            'cost_per_unique_click',
            
            # Conversion Metrics (for CPL calculations)
            'actions',
            'action_values',
            'cost_per_action_type',
            'conversion_values',
            
            # Additional Engagement Metrics (for Funnel Mismatch analysis)
            'unique_clicks',
            'frequency',
            'reach',
            'cost_per_1000_people_reached',
            
            # Attribution & Tracking
            'attribution_setting',
            'date_start',
            'date_stop',
            
            # Status & Delivery
            'delivery_info',
            'status',
            'effective_status'
        ]
        
        # Conversion action types relevant to lead generation
        self.conversion_actions = [
            'lead',
            'complete_registration', 
            'submit_application',
            'schedule',
            'contact',
            'find_location',
            'customize_product',
            'add_to_cart',
            'initiate_checkout',
            'add_payment_info',
            'purchase'
        ]
    
    def get_yesterday_date_range(self) -> tuple:
        """
        Get yesterday's date range for API query.
        
        Returns:
            Tuple of (start_date, end_date) as strings in YYYY-MM-DD format
        """
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
        return date_str, date_str
    
    def fetch_ad_performance_data(self, date_preset: str = None) -> List[Dict[str, Any]]:
        """
        Fetch ad-level performance data from Meta Marketing API.
        
        Args:
            date_preset: Optional date preset ('yesterday', 'last_7d', etc.)
                        If None, uses yesterday's date range
        
        Returns:
            List of dictionaries containing ad performance data
        """
        try:
            # Get ad account
            ad_account = AdAccount(self.ad_account_id)
            
            # Set date range
            if date_preset:
                params = {
                    'fields': self.fields,
                    'date_preset': date_preset,
                    'level': 'ad',
                    'limit': 1000  # Adjust based on account size
                }
            else:
                start_date, end_date = self.get_yesterday_date_range()
                params = {
                    'fields': self.fields,
                    'time_range': {
                        'since': start_date,
                        'until': end_date
                    },
                    'level': 'ad',
                    'limit': 1000
                }
            
            self.logger.info(f"Fetching ad insights for account {self.ad_account_id}")
            self.logger.info(f"Date range: {params.get('time_range', date_preset)}")
            
            # Fetch insights
            insights = ad_account.get_insights(params=params)
            
            # Convert to list of dictionaries
            ad_data = []
            for insight in insights:
                ad_record = self._process_ad_insight(insight)
                ad_data.append(ad_record)
            
            self.logger.info(f"Successfully fetched {len(ad_data)} ad records")
            return ad_data
            
        except FacebookRequestError as e:
            self.logger.error(f"Facebook API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching data: {e}")
            raise
    
    def _process_ad_insight(self, insight) -> Dict[str, Any]:
        """
        Process a single ad insight record and format for spreadsheet output.
        
        Args:
            insight: Facebook Ads Insight object
            
        Returns:
            Dictionary with processed ad data
        """
        # Convert insight to dictionary
        data = dict(insight)
        
        # Process conversion actions into separate columns
        conversions = self._extract_conversions(data.get('actions', []))
        conversion_values = self._extract_conversion_values(data.get('action_values', []))
        cost_per_actions = self._extract_cost_per_actions(data.get('cost_per_action_type', []))
        
        # Create processed record optimized for Cerberus analysis
        processed_record = {
            # Campaign Structure
            'account_id': data.get('account_id', ''),
            'campaign_id': data.get('campaign_id', ''),
            'campaign_name': data.get('campaign_name', ''),
            'adset_id': data.get('adset_id', ''),
            'adset_name': data.get('adset_name', ''),
            'ad_id': data.get('ad_id', ''),
            'ad_name': data.get('ad_name', ''),
            
            # Date Information
            'date_start': data.get('date_start', ''),
            'date_stop': data.get('date_stop', ''),
            
            # Core Metrics
            'spend': float(data.get('spend', 0)),
            'impressions': int(data.get('impressions', 0)),
            'clicks': int(data.get('clicks', 0)),
            'unique_clicks': int(data.get('unique_clicks', 0)),
            'reach': int(data.get('reach', 0)),
            'frequency': float(data.get('frequency', 0)),
            
            # Calculated Metrics
            'ctr': float(data.get('ctr', 0)),
            'cost_per_unique_click': float(data.get('cost_per_unique_click', 0)),
            'cost_per_1000_people_reached': float(data.get('cost_per_1000_people_reached', 0)),
            
            # Status Information
            'status': data.get('status', ''),
            'effective_status': data.get('effective_status', ''),
            
            # Conversion Metrics (for CPL calculations)
            'total_conversions': sum(conversions.values()),
            'total_conversion_value': sum(conversion_values.values()),
        }
        
        # Add individual conversion types as columns
        for action_type, count in conversions.items():
            processed_record[f'conversions_{action_type}'] = count
            
        for action_type, value in conversion_values.items():
            processed_record[f'conversion_value_{action_type}'] = value
            
        for action_type, cost in cost_per_actions.items():
            processed_record[f'cost_per_{action_type}'] = cost
        
        # Calculate derived metrics for Cerberus alerts
        processed_record['cost_per_conversion'] = (
            processed_record['spend'] / processed_record['total_conversions'] 
            if processed_record['total_conversions'] > 0 else 0
        )
        
        # Lead-specific metrics (primary conversion type for B2B)
        lead_conversions = conversions.get('lead', 0)
        processed_record['lead_conversions'] = lead_conversions
        processed_record['cost_per_lead'] = (
            processed_record['spend'] / lead_conversions if lead_conversions > 0 else 0
        )
        
        # Click-to-conversion rate (for Funnel Mismatch alerts)
        processed_record['click_to_conversion_rate'] = (
            (processed_record['total_conversions'] / processed_record['clicks'] * 100) 
            if processed_record['clicks'] > 0 else 0
        )
        
        return processed_record
    
    def _extract_conversions(self, actions: List[Dict]) -> Dict[str, int]:
        """Extract conversion counts by action type."""
        conversions = {}
        for action in actions:
            action_type = action.get('action_type', '')
            if action_type in self.conversion_actions:
                conversions[action_type] = int(action.get('value', 0))
        return conversions
    
    def _extract_conversion_values(self, action_values: List[Dict]) -> Dict[str, float]:
        """Extract conversion values by action type."""
        values = {}
        for action_value in action_values:
            action_type = action_value.get('action_type', '')
            if action_type in self.conversion_actions:
                values[action_type] = float(action_value.get('value', 0))
        return values
    
    def _extract_cost_per_actions(self, cost_per_actions: List[Dict]) -> Dict[str, float]:
        """Extract cost per action by action type."""
        costs = {}
        for cost_action in cost_per_actions:
            action_type = cost_action.get('action_type', '')
            if action_type in self.conversion_actions:
                costs[action_type] = float(cost_action.get('value', 0))
        return costs
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save fetched data to CSV file for spreadsheet import.
        
        Args:
            data: List of ad performance dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved CSV file
        """
        import pandas as pd
        
        if not filename:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            filename = f'meta_ad_performance_{yesterday}.csv'
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        self.logger.info(f"Data saved to {filename}")
        return filename


def main():
    """
    Main function to demonstrate usage of the Meta API fetcher.
    """
    # Load configuration from environment variables
    access_token = os.getenv('META_ACCESS_TOKEN')
    ad_account_id = os.getenv('META_AD_ACCOUNT_ID')  # Format: act_1234567890
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    
    # Validate required environment variables
    required_vars = {
        'META_ACCESS_TOKEN': access_token,
        'META_AD_ACCOUNT_ID': ad_account_id,
        'META_APP_ID': app_id,
        'META_APP_SECRET': app_secret
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return
    
    try:
        # Initialize fetcher
        fetcher = MetaAPIFetcher(
            access_token=access_token,
            ad_account_id=ad_account_id, 
            app_id=app_id,
            app_secret=app_secret
        )
        
        # Fetch yesterday's ad performance data
        print("Fetching yesterday's ad performance data from Meta Marketing API...")
        ad_data = fetcher.fetch_ad_performance_data()
        
        if ad_data:
            print(f"Successfully fetched {len(ad_data)} ad records")
            
            # Display sample record
            print("\nSample record structure:")
            sample = ad_data[0] if ad_data else {}
            for key, value in list(sample.items())[:10]:  # Show first 10 fields
                print(f"  {key}: {value}")
            print("  ...")
            
            # Save to CSV
            csv_file = fetcher.save_to_csv(ad_data)
            print(f"\nData saved to: {csv_file}")
            print("Ready for spreadsheet import or further processing by Cerberus pipeline")
            
        else:
            print("No ad data found for yesterday")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Check your API credentials and account access")


if __name__ == "__main__":
    main() 