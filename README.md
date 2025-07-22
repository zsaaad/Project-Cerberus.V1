# Project Cerberus - Multi-Platform Marketing API Integration

Project Cerberus is an automated performance marketing analysis tool designed to eliminate manual data aggregation and provide proactive campaign optimization insights for MY, PH, and TH markets.

## Overview

This project includes comprehensive API integrations that fetch yesterday's ad-level performance data from both **Meta Marketing API** and **Google Ads API**, formatted for spreadsheet import and optimized to support Cerberus's core alert system:

- **Zero Performance Alert**: Identify ad sets spending >$50 with 0 conversions
- **Top Performer Alert**: Detect ad sets with CPL <50% of market average  
- **Funnel Mismatch Alert**: Find high CTR ads with low conversion rates

## Features

- ✅ **Dual Platform Support** - Meta Marketing API + Google Ads API
- ✅ **Ad-level granularity** for detailed performance analysis
- ✅ **Yesterday's data** with automatic date handling
- ✅ **GAQL queries** for Google Ads with advanced filtering
- ✅ **Unified output format** - both platforms return identical data structures
- ✅ **Conversion tracking** for all relevant action types (leads, registrations, etc.)
- ✅ **CPL calculations** for performance benchmarking
- ✅ **Funnel metrics** (CTR, click-to-conversion rates)
- ✅ **Spreadsheet-ready output** as list of dictionaries
- ✅ **CSV export** functionality
- ✅ **Comprehensive testing** for both integrations
- ✅ **Error handling** and logging
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

Create a `.env` file with your API credentials for both platforms:

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

### Command Line Usage

```bash
# Run Meta API fetcher
python3 meta_api_fetcher.py

# Run Google Ads API fetcher  
python3 google_api_fetcher.py

# Run tests
python3 test_meta_api.py
python3 test_google_api.py
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
- `total_conversions`, `lead_conversions`
- `cost_per_lead`, `cost_per_conversion`
- Individual conversion types (`conversions_lead`, `conversions_purchase`, etc.)

**Funnel Analysis:**
- `click_to_conversion_rate`
- Status and delivery information

## Data Output Format

The script returns a list of dictionaries, each representing one ad's performance:

```python
[
    {
        'campaign_name': 'Q1 Lead Gen Campaign',
        'adset_name': 'Malaysia - Tech Professionals', 
        'ad_name': 'Demo CTA Creative A',
        'spend': 45.67,
        'impressions': 12543,
        'clicks': 234,
        'ctr': 1.87,
        'lead_conversions': 8,
        'cost_per_lead': 5.71,
        'click_to_conversion_rate': 3.42,
        'date_start': '2025-01-20',
        # ... additional fields
    },
    # ... more ad records
]
```

## Integration with Cerberus Pipeline

This script serves as the Meta data source for the Cerberus alert system:

1. **Daily Execution**: Run automatically each morning to fetch yesterday's data
2. **Data Processing**: Feed output into Cerberus analysis engine  
3. **Alert Generation**: Powers Zero Performance, Top Performer, and Funnel Mismatch alerts
4. **Multi-Platform**: Designed to combine with Google Ads and Salesforce data

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