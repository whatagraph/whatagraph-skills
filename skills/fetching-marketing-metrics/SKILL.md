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

## Critical Rule: Never Guess Field Names

**Every metric and dimension name you pass to `fetch-data` must come from a `list-sources` `action: list_dimensions_and_metrics` response for the exact same `source_id` + `report_type` combination. Never rely on your prior knowledge of the native platform's API.**

Whatagraph exposes a normalized field catalog that differs from each platform's native API. The following guesses are common and all fail:

| Wrong (native-API guess) | Actual Whatagraph field |
|--------------------------|--------------------------|
| `sessionDefaultChannelGroup` (GA4) | look it up — often `default_channel_group` |
| `campaignName`, `campaign_name` | usually `campaign` |
| `spend` (generic) | varies by channel — `cost`, `spend`, or a custom metric |
| `date` (on sources without time dimension) | some report types don't support date at all — check first |
| `universal_metric_N` | these are positional IDs, never stable — look up the actual name |

If `fetch-data` returns `Invalid metrics: X` or `Invalid dimensions: X`, do not retry with a variant spelling. Re-run `list-sources action: list_dimensions_and_metrics` with the correct `source_id` and `report_type` and pick a name from the response verbatim.

## Before Fetching Data

Always confirm these three things before calling `fetch-data`:

1. **Source ID** — Use `list-sources` to find the correct source. Users often refer to sources by name (e.g., "my Google Ads account"), so match by `service` and `standard_name`.
2. **Report type** — Many sources expose multiple report types (e.g., Google Ads has `ACCOUNT`, `CAMPAIGN`, `AD_GROUP`, `AD`; Bing Ads has `customer`, `campaign`, `ad_group`, etc.). Always call `list-sources` with `action: list_report_types` before fetching. If the source has more than one report type, `fetch-data` **will error** unless you pass `report_type`.
3. **Available metrics and dimensions** — Call `list-sources` with `action: list_dimensions_and_metrics` with both `source_id` **and** `report_type` to see what fields are available. The response is specific to that report type — switching report types changes the catalog.

### Recovering from "Multiple report types are available"

This is the single most common `fetch-data` error. Recovery:

```
list-sources action: list_report_types, source_id: <id>
→ returns e.g. [{"id": "campaign", "name": "Campaign"}, ...]

list-sources action: list_dimensions_and_metrics, source_id: <id>, report_type: "campaign"
→ returns the field catalog for that report type

fetch-data source_id: <id>, report_type: "campaign", metrics: [...], dimensions: [...]
```

If the user's question doesn't imply a report type, default to the most granular level that still supports `date` (usually `campaign` for paid, or the entity-level report for each channel). Never pick `ACCOUNT`/`customer` as a fallback — it often lacks the dimensions users want.

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

> The tables below are **orientation only** — they show the *kinds* of metrics you'll typically find on each channel, not verbatim field names. Actual names vary by integration and report type. Always confirm via `list-sources action: list_dimensions_and_metrics` before passing a name to `fetch-data`.

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
- Keep requests to **≤ 10 metrics per call** — larger requests are rejected with `Requests are limited to 10 metrics.`
- For period-over-period comparisons, make two `fetch-data` calls with different date ranges and compare the results side by side. (If the user has a Whatagraph report with a built-in comparison period, prefer the `generating-report-digests` skill, which surfaces comparison metrics directly.)

## Handling Errors (read before retrying)

- `Invalid metrics: X` / `Invalid dimensions: X` — do NOT retry with a spelling variant. Re-run `list-sources action: list_dimensions_and_metrics`.
- `Multiple report types are available.` — the source has multiple report types; you must pass `report_type`. See recovery pattern above.
- `The dimensions and metrics are incompatible.` — this report type does not support that combination. Pick a different report type or drop the dimension (typically the finest-grained dimension).
- `Invalid source_id.` — the source ID was fabricated or stale. Re-run `list-sources action: list` with a `search` term matching the user's words.
- `Ahrefs API usage limit reached.` / `Error validating access token:` / other provider errors — these are account-level issues the user must resolve; tell them which source is broken and stop retrying.
- `One or more GA4 metric names contain unsupported characters.` — you used a GA4-native field name. Switch to the Whatagraph normalized name via `list-sources action: list_dimensions_and_metrics`.
