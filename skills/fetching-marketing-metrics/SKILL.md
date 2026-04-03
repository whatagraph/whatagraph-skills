---
name: fetching-marketing-metrics
description: >-
  Fetch and analyze raw marketing performance data from Whatagraph sources with
  proper metric and dimension selection, date ranges, and data interpretation.
  Use when the user asks for specific numbers, wants to see performance data,
  asks "how did my Google Ads perform last month?", needs data comparisons,
  or wants raw metric values from any connected source.
---

# Fetching Marketing Metrics

Retrieve marketing performance data from connected sources using the `fetch-data` tool. This skill covers selecting the right metrics, dimensions, date ranges, and interpreting the results.

## Before Fetching Data

Always confirm these three things before calling `fetch-data`:

1. **Source ID** — Use `list-sources` to find the correct source. Users often refer to sources by name (e.g., "my Google Ads account"), so match by `service` and `standard_name`.
2. **Available metrics and dimensions** — Call `list-sources` with `action: list_dimensions_and_metrics` and the `source_id` plus a `report_type` to see what fields are available.
3. **Report type** — Each source has one or more report types (e.g., `wg_daily_ad_performance`). Check with `list-sources` action `list_report_types` to see available report types for a source.

## Workflow: Fetching Data

1. **Identify the source**:
   ```
   list-sources action: list, search: "Google Ads"
   ```

2. **Check available report types**:
   ```
   list-sources action: list_report_types, source_id: <id>
   ```

3. **Check available metrics and dimensions**:
   ```
   list-sources action: list_dimensions_and_metrics, source_id: <id>, report_type: "<type>"
   ```

4. **Fetch the data**:
   ```
   fetch-data source_id: <id>, report_type: "<type>",
     metrics: ["impressions", "clicks", "spend"],
     dimensions: ["date"],
     from: "2026-03-01", till: "2026-03-31"
   ```

## Common Marketing Metrics by Channel

### Paid Advertising (Google Ads, Facebook Ads, LinkedIn Ads, TikTok Ads)
- **Reach & visibility**: `impressions`, `reach`
- **Engagement**: `clicks`, `link_clicks`, `ctr` (click-through rate)
- **Cost**: `spend`, `cpc` (cost per click), `cpm` (cost per 1000 impressions)
- **Conversions**: `conversions`, `conversion_value`, `cost_per_conversion`
- **ROAS**: `roas` or calculate as `conversion_value / spend`

### Web Analytics (Google Analytics 4)
- **Traffic**: `sessions`, `users`, `new_users`, `page_views`
- **Engagement**: `engagement_rate`, `average_session_duration`, `bounce_rate`
- **Conversions**: `conversions`, `conversion_rate`
- **Dimensions**: `source_medium`, `landing_page`, `device_category`, `country`

### Social Media (Facebook Page, Instagram, LinkedIn Page)
- **Reach**: `impressions`, `reach`, `followers`
- **Engagement**: `engagements`, `reactions`, `comments`, `shares`
- **Content**: `posts_published`, `video_views`

### Email Marketing (Mailchimp, HubSpot)
- **Delivery**: `emails_sent`, `emails_delivered`, `delivery_rate`
- **Engagement**: `opens`, `open_rate`, `clicks`, `click_rate`
- **Conversion**: `unsubscribes`, `bounce_rate`

## Date Range Patterns

| User Request | `from` | `till` |
|-------------|------------|----------|
| "Last month" | First day of previous month | Last day of previous month |
| "This month" | First day of current month | Today |
| "Last 30 days" | 30 days ago | Today |
| "Last quarter" | First day of previous quarter | Last day of previous quarter |
| "Year to date" | January 1 of current year | Today |
| "Last week" | Monday of previous week | Sunday of previous week |

## Interpreting Results

- **Null or missing values**: Some metrics may return null for certain date ranges if no data was collected. This is normal — explain it to the user rather than treating it as an error.
- **Currency**: Check the source's `currency` field from `list-sources` to know which currency cost metrics are reported in.
- **Aggregation**: Data is aggregated by the dimensions you specify. No dimensions = single totals row. Adding `date` dimension gives daily breakdown.
- **Rate metrics**: Metrics like CTR, conversion rate, and ROAS may be pre-calculated or may need manual calculation from component metrics depending on the source.

## Tips

- Start with fewer metrics and dimensions, then expand. Large requests may be slower.
- Always include a `date` dimension when users want to see trends over time.
- If a metric returns unexpected results, check if the report type is correct — different report types expose different metrics.
- Use `dimensions: ["campaign_name"]` for campaign-level breakdowns, `["ad_group_name"]` for ad group level, etc.
- For period-over-period comparisons, make two `fetch-data` calls with different date ranges and compare the results side by side.
