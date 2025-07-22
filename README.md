# Project Cerberus - Meta Marketing API Integration

Project Cerberus is an automated performance marketing analysis tool designed to eliminate manual data aggregation and provide proactive campaign optimization insights for MY, PH, and TH markets.

## Overview

This script fetches yesterday's ad-level performance data from Meta Marketing API, formatted for spreadsheet import and optimized to support Cerberus's core alert system:

- **Zero Performance Alert**: Identify ad sets spending >$50 with 0 conversions
- **Top Performer Alert**: Detect ad sets with CPL <50% of market average  
- **Funnel Mismatch Alert**: Find high CTR ads with low conversion rates

## Features

- ✅ **Ad-level granularity** for detailed performance analysis
- ✅ **Yesterday's data** with automatic date handling
- ✅ **Conversion tracking** for all relevant action types (leads, registrations, etc.)
- ✅ **CPL calculations** for performance benchmarking
- ✅ **Funnel metrics** (CTR, click-to-conversion rates)
- ✅ **Spreadsheet-ready output** as list of dictionaries
- ✅ **CSV export** functionality
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
   cp .env.example .env
   # Edit .env with your Meta API credentials
   ```

## Configuration

### Required Environment Variables

Create a `.env` file with your Meta Marketing API credentials:

```env
META_ACCESS_TOKEN=your_meta_access_token_here
META_AD_ACCOUNT_ID=act_1234567890  
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
```

### Getting Meta API Credentials

1. **Meta App**: Create an app at [Meta for Developers](https://developers.facebook.com/)
2. **Access Token**: Generate a long-lived access token with `ads_read` permissions
3. **Ad Account ID**: Find your account ID in Meta Ads Manager (format: `act_1234567890`)

## Usage

### Basic Usage

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

# Data is ready as list of dictionaries for spreadsheet import
print(f"Fetched {len(ad_data)} ad records")
```

### Command Line Usage

```bash
python meta_api_fetcher.py
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