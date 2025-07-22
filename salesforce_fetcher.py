"""
Salesforce API Data Fetcher for Project Cerberus
Fetches yesterday's lead and opportunity data for attribution analysis.

Author: Project Cerberus Team  
Version: 1.0
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SalesforceAPIFetcher:
    """
    Fetches Salesforce API data for Project Cerberus attribution analysis.
    Designed to provide conversion data for Zero Performance, Top Performer, and Funnel Mismatch alerts.
    """
    
    def __init__(self, username: str, password: str, security_token: str, domain: str = 'login'):
        """
        Initialize the Salesforce API fetcher.
        
        Args:
            username: Salesforce username
            password: Salesforce password  
            security_token: Salesforce security token
            domain: Salesforce domain (default: 'login' for production, 'test' for sandbox)
        """
        self.username = username
        self.password = password
        self.security_token = security_token
        self.domain = domain
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Salesforce connection
        self.sf = self._initialize_connection()
        
        # Lead SOQL query for attribution data
        self.lead_query = """
            SELECT 
                Id, 
                Status, 
                CreatedDate, 
                IsConverted, 
                ConvertedOpportunityId,
                ConvertedContactId,
                ConvertedAccountId,
                FirstName,
                LastName, 
                Email,
                Company,
                LeadSource,
                utm_campaign_id__c,
                utm_adset_id__c, 
                utm_ad_id__c,
                utm_source__c,
                utm_medium__c,
                utm_campaign__c,
                utm_content__c,
                utm_term__c
            FROM Lead 
            WHERE CreatedDate >= {start_datetime}
            AND CreatedDate <= {end_datetime}
            ORDER BY CreatedDate DESC
        """
        
        # Opportunity SOQL query for converted leads
        self.opportunity_query = """
            SELECT 
                Id,
                Name,
                StageName,
                Amount,
                CloseDate,
                Probability,
                Type,
                LeadSource,
                CreatedDate,
                AccountId,
                ContactId
            FROM Opportunity 
            WHERE CreatedDate >= {start_datetime}
            AND CreatedDate <= {end_datetime}
            ORDER BY CreatedDate DESC
        """
    
    def _initialize_connection(self) -> Salesforce:
        """Initialize Salesforce API connection."""
        try:
            sf = Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                domain=self.domain
            )
            self.logger.info("Salesforce API connection established successfully")
            return sf
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Salesforce connection: {e}")
            raise
    
    def get_yesterday_date_range(self) -> tuple:
        """
        Get yesterday's date range for SOQL query.
        
        Returns:
            Tuple of (start_datetime, end_datetime) as strings in Salesforce datetime format
        """
        yesterday = datetime.now() - timedelta(days=1)
        start_datetime = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_datetime = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Format for Salesforce SOQL (ISO format)
        start_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        end_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        return start_str, end_str
    
    def fetch_lead_data(self, date_preset: str = None) -> List[Dict[str, Any]]:
        """
        Fetch lead data from Salesforce using SOQL.
        
        Args:
            date_preset: Optional date preset. If None, uses yesterday's date range
        
        Returns:
            List of dictionaries containing lead data
        """
        try:
            # Set date range
            if date_preset:
                # For simplicity, defaulting to yesterday for presets
                start_datetime, end_datetime = self.get_yesterday_date_range()
            else:
                start_datetime, end_datetime = self.get_yesterday_date_range()
            
            # Build SOQL query with date range
            query = self.lead_query.format(
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )
            
            self.logger.info(f"Fetching leads from {start_datetime} to {end_datetime}")
            self.logger.info(f"SOQL Query: {query}")
            
            # Execute SOQL query
            result = self.sf.query_all(query)
            leads = result['records']
            
            # Process leads into standard format
            lead_data = []
            for lead in leads:
                lead_record = self._process_lead_record(lead)
                lead_data.append(lead_record)
            
            self.logger.info(f"Successfully fetched {len(lead_data)} lead records")
            return lead_data
            
        except SalesforceError as e:
            self.logger.error(f"Salesforce API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching lead data: {e}")
            raise
    
    def fetch_opportunity_data(self, date_preset: str = None) -> List[Dict[str, Any]]:
        """
        Fetch opportunity data from Salesforce using SOQL.
        
        Args:
            date_preset: Optional date preset. If None, uses yesterday's date range
        
        Returns:
            List of dictionaries containing opportunity data
        """
        try:
            # Set date range
            if date_preset:
                start_datetime, end_datetime = self.get_yesterday_date_range()
            else:
                start_datetime, end_datetime = self.get_yesterday_date_range()
            
            # Build SOQL query with date range
            query = self.opportunity_query.format(
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )
            
            self.logger.info(f"Fetching opportunities from {start_datetime} to {end_datetime}")
            
            # Execute SOQL query
            result = self.sf.query_all(query)
            opportunities = result['records']
            
            # Process opportunities into standard format
            opp_data = []
            for opp in opportunities:
                opp_record = self._process_opportunity_record(opp)
                opp_data.append(opp_record)
            
            self.logger.info(f"Successfully fetched {len(opp_data)} opportunity records")
            return opp_data
            
        except SalesforceError as e:
            self.logger.error(f"Salesforce API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching opportunity data: {e}")
            raise
    
    def fetch_attribution_data(self, date_preset: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch both leads and opportunities for complete attribution analysis.
        
        Args:
            date_preset: Optional date preset. If None, uses yesterday's date range
        
        Returns:
            Dictionary containing both leads and opportunities data
        """
        try:
            self.logger.info("Fetching complete Salesforce attribution data")
            
            # Fetch both datasets
            leads = self.fetch_lead_data(date_preset)
            opportunities = self.fetch_opportunity_data(date_preset)
            
            attribution_data = {
                'leads': leads,
                'opportunities': opportunities,
                'summary': {
                    'total_leads': len(leads),
                    'total_opportunities': len(opportunities),
                    'converted_leads': len([lead for lead in leads if lead.get('is_converted', False)])
                }
            }
            
            self.logger.info(f"Attribution data summary: {attribution_data['summary']}")
            return attribution_data
            
        except Exception as e:
            self.logger.error(f"Error fetching attribution data: {e}")
            raise
    
    def _process_lead_record(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single lead record into standard format for Cerberus analysis.
        
        Args:
            lead: Salesforce lead record
            
        Returns:
            Processed lead data dictionary
        """
        # Remove Salesforce metadata
        lead_data = {key: value for key, value in lead.items() if key != 'attributes'}
        
        # Create processed record optimized for attribution
        processed_record = {
            # Lead Identification
            'lead_id': lead_data.get('Id', ''),
            'lead_status': lead_data.get('Status', ''),
            'created_date': lead_data.get('CreatedDate', ''),
            'is_converted': bool(lead_data.get('IsConverted', False)),
            'converted_opportunity_id': lead_data.get('ConvertedOpportunityId', ''),
            'converted_contact_id': lead_data.get('ConvertedContactId', ''),
            'converted_account_id': lead_data.get('ConvertedAccountId', ''),
            
            # Lead Details
            'first_name': lead_data.get('FirstName', ''),
            'last_name': lead_data.get('LastName', ''),
            'email': lead_data.get('Email', ''),
            'company': lead_data.get('Company', ''),
            'lead_source': lead_data.get('LeadSource', ''),
            
            # Meta Attribution Fields (Perfect ID matching)
            'fb_campaign_id': lead_data.get('FB_Campaign_ID__c', ''),
            'fb_adset_id': lead_data.get('FB_Adset_ID__c', ''),
            'fb_ad_id': lead_data.get('FB_Ad_ID__c', ''),
            
            # Google Attribution Fields (Name-based matching)
            'utm_campaign': lead_data.get('UTM_Campaign__c', ''),
            'utm_source': lead_data.get('UTM_Source__c', ''),
            'utm_medium': lead_data.get('UTM_Medium__c', ''),
            'utm_term': lead_data.get('UTM_Term__c', ''),
            'utm_content': lead_data.get('UTM_Content__c', ''),
            
            # Date Processing
            'date_start': lead_data.get('CreatedDate', '')[:10] if lead_data.get('CreatedDate') else '',  # YYYY-MM-DD format
            'date_stop': lead_data.get('CreatedDate', '')[:10] if lead_data.get('CreatedDate') else '',
            
            # Conversion Flags for Cerberus Analysis
            'lead_count': 1,  # Each record represents 1 lead
            'conversion_count': 1 if lead_data.get('IsConverted', False) else 0,
        }
        
        return processed_record
    
    def _process_opportunity_record(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single opportunity record into standard format.
        
        Args:
            opp: Salesforce opportunity record
            
        Returns:
            Processed opportunity data dictionary
        """
        # Remove Salesforce metadata
        opp_data = {key: value for key, value in opp.items() if key != 'attributes'}
        
        # Create processed record
        processed_record = {
            # Opportunity Identification
            'opportunity_id': opp_data.get('Id', ''),
            'opportunity_name': opp_data.get('Name', ''),
            'stage_name': opp_data.get('StageName', ''),
            'amount': float(opp_data.get('Amount', 0)) if opp_data.get('Amount') else 0,
            'close_date': opp_data.get('CloseDate', ''),
            'probability': float(opp_data.get('Probability', 0)) if opp_data.get('Probability') else 0,
            'type': opp_data.get('Type', ''),
            'lead_source': opp_data.get('LeadSource', ''),
            'created_date': opp_data.get('CreatedDate', ''),
            'account_id': opp_data.get('AccountId', ''),
            'contact_id': opp_data.get('ContactId', ''),
            
            # Date Processing
            'date_start': opp_data.get('CreatedDate', '')[:10] if opp_data.get('CreatedDate') else '',
            'date_stop': opp_data.get('CreatedDate', '')[:10] if opp_data.get('CreatedDate') else '',
        }
        
        return processed_record
    
    def save_to_csv(self, data: Dict[str, List[Dict[str, Any]]], filename_prefix: str = None) -> Dict[str, str]:
        """
        Save fetched attribution data to CSV files.
        
        Args:
            data: Attribution data dictionary with leads and opportunities
            filename_prefix: Optional custom filename prefix
            
        Returns:
            Dictionary with paths to saved CSV files
        """
        import pandas as pd
        
        if not filename_prefix:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            filename_prefix = f'salesforce_attribution_{yesterday}'
        
        saved_files = {}
        
        # Save leads data
        if data.get('leads'):
            leads_filename = f'{filename_prefix}_leads.csv'
            leads_df = pd.DataFrame(data['leads'])
            leads_df.to_csv(leads_filename, index=False)
            saved_files['leads'] = leads_filename
            self.logger.info(f"Leads data saved to {leads_filename}")
        
        # Save opportunities data
        if data.get('opportunities'):
            opps_filename = f'{filename_prefix}_opportunities.csv'
            opps_df = pd.DataFrame(data['opportunities'])
            opps_df.to_csv(opps_filename, index=False)
            saved_files['opportunities'] = opps_filename
            self.logger.info(f"Opportunities data saved to {opps_filename}")
        
        return saved_files


def main():
    """
    Main function to demonstrate usage of the Salesforce API fetcher.
    """
    # Load configuration from environment variables
    username = os.getenv('SALESFORCE_USERNAME')
    password = os.getenv('SALESFORCE_PASSWORD')
    security_token = os.getenv('SALESFORCE_SECURITY_TOKEN')
    domain = os.getenv('SALESFORCE_DOMAIN', 'login')  # Default to production
    
    # Validate required environment variables
    required_vars = {
        'SALESFORCE_USERNAME': username,
        'SALESFORCE_PASSWORD': password,
        'SALESFORCE_SECURITY_TOKEN': security_token
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return
    
    try:
        # Initialize fetcher
        fetcher = SalesforceAPIFetcher(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain
        )
        
        # Fetch complete attribution data
        print("Fetching yesterday's Salesforce attribution data...")
        attribution_data = fetcher.fetch_attribution_data()
        
        if attribution_data['leads'] or attribution_data['opportunities']:
            print(f"Successfully fetched Salesforce data:")
            print(f"  - Leads: {len(attribution_data['leads'])} records")
            print(f"  - Opportunities: {len(attribution_data['opportunities'])} records")
            print(f"  - Converted Leads: {attribution_data['summary']['converted_leads']}")
            
            # Display sample lead record
            if attribution_data['leads']:
                print("\nSample lead record structure:")
                sample = attribution_data['leads'][0]
                for key, value in list(sample.items())[:10]:  # Show first 10 fields
                    print(f"  {key}: {value}")
                print("  ...")
            
            # Save to CSV files
            saved_files = fetcher.save_to_csv(attribution_data)
            print(f"\nData saved to:")
            for data_type, filename in saved_files.items():
                print(f"  - {data_type.title()}: {filename}")
            
            print("Ready for integration with Cerberus data merger!")
            
        else:
            print("No Salesforce data found for yesterday")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Check your Salesforce credentials and custom field configuration")


if __name__ == "__main__":
    main() 