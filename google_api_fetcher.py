"""
Google Ads API Data Fetcher for Project Cerberus
Fetches yesterday's ad-level performance data for performance marketing analysis.

Author: Project Cerberus Team  
Version: 1.0
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GoogleAPIFetcher:
    """
    Fetches Google Ads API data for Project Cerberus performance analysis.
    Designed to support Zero Performance, Top Performer, and Funnel Mismatch alerts.
    """
    
    def __init__(self, developer_token: str, client_id: str, client_secret: str, 
                 refresh_token: str, customer_id: str, login_customer_id: str = None):
        """
        Initialize the Google Ads API fetcher.
        
        Args:
            developer_token: Google Ads API developer token
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            refresh_token: OAuth2 refresh token
            customer_id: Google Ads customer ID (without hyphens)
            login_customer_id: Optional login customer ID for MCC accounts
        """
        self.developer_token = developer_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.customer_id = customer_id.replace('-', '')  # Remove hyphens
        self.login_customer_id = login_customer_id.replace('-', '') if login_customer_id else None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Ads client
        self.client = self._initialize_client()
        
        # GAQL query optimized for Cerberus alert requirements
        self.base_query = """
            SELECT 
                campaign.id,
                campaign.name,
                ad_group.id, 
                ad_group.name,
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                ad_group_ad.status,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.conversions,
                metrics.conversions_value,
                metrics.cost_per_conversion,
                metrics.conversion_rate,
                metrics.average_cpc,
                metrics.average_cpm,
                segments.date
            FROM ad_group_ad 
            WHERE segments.date = '{date}'
            AND ad_group_ad.status = 'ENABLED'
            AND ad_group.status = 'ENABLED' 
            AND campaign.status = 'ENABLED'
            ORDER BY metrics.cost_micros DESC
        """
        
        # Conversion action types for lead generation (similar to Meta mapping)
        self.conversion_categories = {
            'lead_generation': ['SUBMIT_LEAD_FORM', 'CONTACT', 'GET_DIRECTIONS'],
            'signup': ['SIGN_UP', 'SUBSCRIBE'],
            'engagement': ['DOWNLOAD', 'VIEW_ITEM'],
            'purchase': ['PURCHASE', 'ADD_TO_CART']
        }
    
    def _initialize_client(self) -> GoogleAdsClient:
        """Initialize Google Ads API client with credentials."""
        try:
            # Create client configuration
            credentials = {
                "developer_token": self.developer_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "use_proto_plus": True
            }
            
            if self.login_customer_id:
                credentials["login_customer_id"] = self.login_customer_id
                
            client = GoogleAdsClient.load_from_dict(credentials)
            self.logger.info("Google Ads API client initialized successfully")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Ads client: {e}")
            raise
    
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
        Fetch ad-level performance data from Google Ads API using GAQL.
        
        Args:
            date_preset: Optional date preset. If None, uses yesterday's date
        
        Returns:
            List of dictionaries containing ad performance data
        """
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Set date range
            if date_preset:
                # For date presets, we'd need to calculate the actual date
                # For simplicity, defaulting to yesterday
                query_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                start_date, end_date = self.get_yesterday_date_range()
                query_date = start_date
            
            # Build GAQL query with date
            query = self.base_query.format(date=query_date)
            
            self.logger.info(f"Fetching ad insights for customer {self.customer_id}")
            self.logger.info(f"Date: {query_date}")
            self.logger.info(f"GAQL Query: {query}")
            
            # Execute query
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = self.customer_id
            search_request.query = query
            search_request.page_size = 10000  # Adjust based on account size
            
            response = ga_service.search(request=search_request)
            
            # Convert to list of dictionaries
            ad_data = []
            for row in response:
                ad_record = self._process_ad_row(row, query_date)
                ad_data.append(ad_record)
            
            self.logger.info(f"Successfully fetched {len(ad_data)} ad records")
            return ad_data
            
        except GoogleAdsException as ex:
            self.logger.error(f"Google Ads API error occurred: {ex}")
            for error in ex.failure.errors:
                self.logger.error(f"\t{error.error_code.error_code}: {error.message}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching data: {e}")
            raise
    
    def _process_ad_row(self, row, query_date: str) -> Dict[str, Any]:
        """
        Process a single Google Ads API row and format for spreadsheet output.
        Mirror the Meta API output format exactly.
        
        Args:
            row: Google Ads API response row
            query_date: Date string for the query
            
        Returns:
            Dictionary with processed ad data
        """
        # Extract data from row
        campaign = row.campaign
        ad_group = row.ad_group
        ad_group_ad = row.ad_group_ad
        metrics = row.metrics
        
        # Convert cost from micros to dollars (Google Ads uses micros)
        spend = float(metrics.cost_micros) / 1_000_000
        
        # Create processed record optimized for Cerberus analysis
        # Match Meta API output format exactly
        processed_record = {
            # Campaign Structure - matching Meta format
            'account_id': self.customer_id,
            'campaign_id': str(campaign.id),
            'campaign_name': campaign.name,
            'adset_id': str(ad_group.id),  # Ad Group = Ad Set in Meta terms
            'adset_name': ad_group.name,
            'ad_id': str(ad_group_ad.ad.id),
            'ad_name': ad_group_ad.ad.name or f"Ad {ad_group_ad.ad.id}",
            
            # Date Information
            'date_start': query_date,
            'date_stop': query_date,
            
            # Core Metrics
            'spend': spend,
            'impressions': int(metrics.impressions),
            'clicks': int(metrics.clicks),
            'unique_clicks': int(metrics.clicks),  # Google Ads doesn't distinguish unique clicks
            'reach': int(metrics.impressions),  # Approximation for reach
            'frequency': 1.0,  # Default for Google Ads
            
            # Calculated Metrics
            'ctr': float(metrics.ctr * 100),  # Convert to percentage to match Meta
            'cost_per_unique_click': float(metrics.average_cpc) / 1_000_000 if metrics.average_cpc else 0,
            'cost_per_1000_people_reached': float(metrics.average_cpm) / 1_000_000 if metrics.average_cpm else 0,
            
            # Status Information
            'status': ad_group_ad.status.name if ad_group_ad.status else 'UNKNOWN',
            'effective_status': ad_group_ad.status.name if ad_group_ad.status else 'UNKNOWN',
            
            # Conversion Metrics (for CPL calculations)
            'total_conversions': float(metrics.conversions),
            'total_conversion_value': float(metrics.conversions_value),
        }
        
        # Add conversion fields to match Meta format
        processed_record['conversions_lead'] = float(metrics.conversions)  # Simplified mapping
        processed_record['conversion_value_lead'] = float(metrics.conversions_value)
        processed_record['cost_per_lead'] = float(metrics.cost_per_conversion) / 1_000_000 if metrics.cost_per_conversion else 0
        
        # Calculate derived metrics for Cerberus alerts
        processed_record['cost_per_conversion'] = (
            processed_record['spend'] / processed_record['total_conversions'] 
            if processed_record['total_conversions'] > 0 else 0
        )
        
        # Lead-specific metrics (primary conversion type for B2B)
        lead_conversions = processed_record['total_conversions']  # Simplified for now
        processed_record['lead_conversions'] = lead_conversions
        processed_record['cost_per_lead'] = (
            processed_record['spend'] / lead_conversions if lead_conversions > 0 else 0
        )
        
        # Click-to-conversion rate (for Funnel Mismatch alerts)
        processed_record['click_to_conversion_rate'] = (
            float(metrics.conversion_rate * 100) if metrics.conversion_rate else 0
        )
        
        return processed_record
    
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
            filename = f'google_ad_performance_{yesterday}.csv'
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        self.logger.info(f"Data saved to {filename}")
        return filename


def main():
    """
    Main function to demonstrate usage of the Google Ads API fetcher.
    """
    # Load configuration from environment variables
    developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    client_id = os.getenv('GOOGLE_ADS_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
    customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
    login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
    
    # Validate required environment variables
    required_vars = {
        'GOOGLE_ADS_DEVELOPER_TOKEN': developer_token,
        'GOOGLE_ADS_CLIENT_ID': client_id,
        'GOOGLE_ADS_CLIENT_SECRET': client_secret,
        'GOOGLE_ADS_REFRESH_TOKEN': refresh_token,
        'GOOGLE_ADS_CUSTOMER_ID': customer_id
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return
    
    try:
        # Initialize fetcher
        fetcher = GoogleAPIFetcher(
            developer_token=developer_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            customer_id=customer_id,
            login_customer_id=login_customer_id
        )
        
        # Fetch yesterday's ad performance data
        print("Fetching yesterday's ad performance data from Google Ads API...")
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