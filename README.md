# Project Cerberus - Complete Marketing Attribution Platform

Project Cerberus is an automated performance marketing analysis tool designed to eliminate manual data aggregation and provide proactive campaign optimization insights for MY, PH, and TH markets.

## Overview

This project includes comprehensive API integrations that fetch yesterday's ad-level performance data from **Meta Marketing API**, **Google Ads API**, and **Salesforce**, creating a complete attribution chain from ad spend to business outcomes. The unified dataset supports Cerberus's core alert system:

- **Zero Performance Alert**: Identify ad sets spending >$50 with 0 conversions
- **Top Performer Alert**: Detect ad sets with CPL <50% of market average  
- **Funnel Mismatch Alert**: Find high CTR ads with low conversion rates

## Features

- ✅ **Complete Attribution Chain** - Meta + Google Ads + Salesforce integration
- ✅ **Ad-level granularity** for detailed performance analysis
- ✅ **Yesterday's data** with automatic date handling
- ✅ **GAQL queries** for Google Ads with advanced filtering
- ✅ **SOQL queries** for Salesforce with UTM attribution tracking
- ✅ **Unified output format** - all platforms return identical data structures
- ✅ **Attribution joining** - left join from ad data to Salesforce leads via UTM parameters
- ✅ **Conversion source of truth** - Salesforce leads override platform conversion data
- ✅ **CPL calculations** for performance benchmarking with actual lead data
- ✅ **Funnel metrics** (CTR, click-to-conversion rates) with attribution insights
- ✅ **Spreadsheet-ready output** as list of dictionaries with enriched attribution
- ✅ **CSV export** functionality for complete attributed datasets
- ✅ **Comprehensive testing** for all integrations
- ✅ **Error handling** and logging across all platforms
- ✅ **Multi-account support** ready

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zsaaad/Project-Cerberus.V1.git
   cd Project-Cerberus.V1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials:**
   ```bash
   cp env.example .env
   # Edit .env with your Meta and Google Ads API credentials
   ```

## Configuration

### Required Environment Variables

Create a `.env` file with your API credentials for all platforms:

```env
# Meta Marketing API
META_ACCESS_TOKEN=your_meta_access_token_here
META_AD_ACCOUNT_ID=act_1234567890  
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your_google_ads_developer_token_here
GOOGLE_ADS_CLIENT_ID=your_google_ads_client_id_here
GOOGLE_ADS_CLIENT_SECRET=your_google_ads_client_secret_here
GOOGLE_ADS_REFRESH_TOKEN=your_google_ads_refresh_token_here
GOOGLE_ADS_CUSTOMER_ID=1234567890

# Salesforce API
SALESFORCE_USERNAME=your_salesforce_username@company.com
SALESFORCE_PASSWORD=your_salesforce_password
SALESFORCE_SECURITY_TOKEN=your_salesforce_security_token
```

### Getting API Credentials

**Meta Marketing API:**
1. **Meta App**: Create an app at [Meta for Developers](https://developers.facebook.com/)
2. **Access Token**: Generate a long-lived access token with `ads_read` permissions
3. **Ad Account ID**: Find your account ID in Meta Ads Manager (format: `act_1234567890`)

**Google Ads API:**
1. **Developer Token**: Apply for API access at [Google Ads API](https://developers.google.com/google-ads/api)
2. **OAuth Credentials**: Create OAuth2 credentials in Google Cloud Console
3. **Refresh Token**: Generate using OAuth2 flow with `https://www.googleapis.com/auth/adwords` scope
4. **Customer ID**: Find in your Google Ads account (format: `1234567890`)

**Salesforce API:**
1. **Username/Password**: Your Salesforce login credentials
2. **Security Token**: Generate in Salesforce Setup → Personal Information → Reset Security Token
3. **Custom Fields**: Create UTM tracking fields (`utm_campaign_id__c`, `utm_adset_id__c`, `utm_ad_id__c`) in Lead object

## Usage

### Basic Usage

**Meta Marketing API:**
```python
from meta_api_fetcher import MetaAPIFetcher

# Initialize fetcher
fetcher = MetaAPIFetcher(
    access_token="your_token",
    ad_account_id="act_1234567890", 
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# Fetch yesterday's ad performance data
ad_data = fetcher.fetch_ad_performance_data()
print(f"Fetched {len(ad_data)} Meta ad records")
```

**Google Ads API:**
```python
from google_api_fetcher import GoogleAPIFetcher

# Initialize fetcher  
fetcher = GoogleAPIFetcher(
    developer_token="your_developer_token",
    client_id="your_client_id",
    client_secret="your_client_secret",
    refresh_token="your_refresh_token",
    customer_id="1234567890"
)

# Fetch yesterday's ad performance data
ad_data = fetcher.fetch_ad_performance_data()
print(f"Fetched {len(ad_data)} Google ad records")
```

**Salesforce API:**
```python
from salesforce_fetcher import SalesforceAPIFetcher

# Initialize fetcher
fetcher = SalesforceAPIFetcher(
    username="user@company.com",
    password="password",
    security_token="security_token"
)

# Fetch attribution data
attribution_data = fetcher.fetch_attribution_data()
print(f"Fetched {len(attribution_data['leads'])} leads")
```

**Complete Attribution Processing:**
```python
from data_merger import CerberusDataMerger

merger = CerberusDataMerger()
unified_data = merger.merge_platform_data(
    meta_data, google_data, salesforce_data
)
# Creates complete attribution: Ad Spend → Leads → Conversions
```

### Command Line Usage

```bash
# Run individual API fetchers
python3 meta_api_fetcher.py
python3 google_api_fetcher.py
python3 salesforce_fetcher.py

# Run complete attribution processing
python3 data_merger.py

# Run tests
python3 test_meta_api.py
python3 test_google_api.py
python3 test_salesforce_api.py
```

### Data Fields Included

The script fetches comprehensive ad-level data optimized for Cerberus alerts:

**Campaign Structure:**
- `campaign_id`, `campaign_name`
- `adset_id`, `adset_name`  
- `ad_id`, `ad_name`

**Performance Metrics:**
- `spend`, `impressions`, `clicks`, `reach`
- `ctr`, `cost_per_unique_click`
- `frequency`, `cost_per_1000_people_reached`

**Conversion Data:**
- `total_conversions`, `lead_conversions` (platform-reported)
- `sf_lead_count`, `sf_converted_count` (Salesforce source of truth)
- `cost_per_lead`, `cost_per_conversion` (calculated with actual leads)
- Individual conversion types (`conversions_lead`, `conversions_purchase`, etc.)

**Attribution Data:**
- `utm_campaign_id`, `utm_adset_id`, `utm_ad_id` (join keys)
- `sf_lead_statuses`, `sf_lead_sources` (Salesforce lead details)
- `has_salesforce_data` (attribution match flag)

**Funnel Analysis:**
- `click_to_conversion_rate` (with attributed conversions)
- Status and delivery information

## Data Output Format

The system returns a list of dictionaries, each representing one ad's complete attribution:

```python
[
    {
        'platform': 'Meta',
        'campaign_name': 'Q1 Lead Gen Campaign',
        'adset_name': 'Malaysia - Tech Professionals', 
        'ad_name': 'Demo CTA Creative A',
        'spend': 45.67,
        'impressions': 12543,
        'clicks': 234,
        'ctr': 1.87,
        
        # Platform-reported conversions
        'total_conversions': 8,
        'lead_conversions': 8,
        
        # Salesforce attribution (source of truth)
        'sf_lead_count': 2,
        'sf_converted_count': 1,
        'sf_lead_statuses': 'Qualified, New',
        'sf_first_lead_email': 'john.doe@company.com',
        'has_salesforce_data': True,
        
        # Updated metrics with attribution
        'cost_per_lead': 22.84,  # $45.67 / 2 actual leads
        'click_to_conversion_rate': 0.85,  # 2 leads / 234 clicks
        
        'date_start': '2025-01-20',
        # ... 35+ additional attribution fields
    },
    # ... more attributed ad records
]
```

## Integration with Cerberus Pipeline

This platform serves as the complete data source for the Cerberus alert system:

1. **Daily Execution**: Run automatically each morning to fetch yesterday's attributed data
2. **Attribution Processing**: Join ad spend data with actual Salesforce leads via UTM parameters
3. **Alert Generation**: Powers Zero Performance, Top Performer, and Funnel Mismatch alerts with source-of-truth conversion data
4. **End-to-End Attribution**: Complete chain from ad spend → clicks → leads → conversions

## Error Handling

The script includes comprehensive error handling:
- API authentication errors
- Rate limiting and retries
- Data validation
- Logging for troubleshooting

## Next Steps

This Meta API integration is the foundation for Project Cerberus V1. Next development phases include:

1. **Google Ads API integration**
2. **Salesforce API integration**  
3. **Cross-platform data joining logic**
4. **Alert engine implementation**
5. **Slack/Lark delivery mechanism**

## Support

For questions about Project Cerberus or this Meta API integration, contact the Product Team or review the full PRD documentation.

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Markets**: MY, PH, TH 