---
name: cross-channel-analytics
description: >-
  Analyze marketing performance across multiple channels using Whatagraph blends,
  source groups, and custom metrics/dimensions. Use when the user wants to
  compare channels, see unified cross-platform metrics, understand blended data,
  asks "how do all my channels compare?", "what's my total spend across
  platforms?", or needs help with cross-channel attribution and reporting.
---

# Cross-Channel Analytics

Help users analyze marketing performance across multiple channels by leveraging Whatagraph's blends, source groups, and custom fields. Cross-channel analytics is one of Whatagraph's core strengths — combining data from Google Ads, Meta, LinkedIn, GA4, and other platforms into unified views.

## Key Concepts

- **Blends** combine data from multiple sources into a single virtual source by mapping metrics across platforms (e.g., "Spend" from Google Ads + "Spend" from Facebook Ads). Use `list-blends` to explore them.
- **Source groups** aggregate multiple sources of the same integration type into one unified source (e.g., 10 Google Ads accounts rolled into one). Use `list-source-groups` to explore them.
- **Custom metrics** are user-defined calculated metrics that can work across channels (e.g., "Total Spend" = Google Ads spend + Meta spend). Use `list-custom-metrics`.
- **Custom dimensions** are user-defined dimensions for cross-channel categorization. Use `list-custom-dimensions`.

## Workflow: Cross-Channel Performance Overview

1. **Discover available blends**:
   ```
   list-blends action: list
   ```
   Blends are the primary mechanism for cross-channel reporting. Each blend combines specific sources.

2. **Inspect a blend's configuration**:
   ```
   list-blends action: show, blend_id: <id>
   ```
   This reveals which sources are blended and how metrics map across them.

3. **Fetch cross-channel data from the blend**:

   Blend field ids use one of two prefix families — always look them up before fetching:

   ```
   list-sources action: list_dimensions_and_metrics, source_id: <blend_source_id>
   ```

   Depending on how the blend was configured you will see either:
   - **`aggregation_*` prefixes** — universal blends: `aggregation_metric_universal_metric_1`, `aggregation_dimension_universal_dimension_1137`
   - **`blend_*` prefixes** — channel-native blends: `blend_metric_spend`, `blend_dimension_date`

   Use the verbatim ids from that response in `fetch-data`:

   ```
   fetch-data source_id: <blend_source_id>,
     metrics: ["aggregation_metric_universal_metric_1",
               "aggregation_metric_universal_metric_2"],
     dimensions: ["aggregation_dimension_universal_dimension_1137"],
     from: "2026-03-01", till: "2026-03-31"
   ```

   **First-call warmup:** blends often return `Your data is being processed... please wait...` with `retryable: false` on their first fetch. Treat this as transient — wait ~10–15 seconds and retry. See the "Handling Errors" section of `fetching-marketing-metrics` for the full retry pattern.

   **Incorrect blend setup error:** if `fetch-data` returns an error categorised as `setup_error` (e.g. "Incorrect blend setup"), the blend itself is misconfigured — not the fetch call. Use `list-blends action: show, blend_id: <id>` to inspect the source mapping. Common causes: a source was removed after the blend was created, or a required metric mapping is missing. The fix is in the UI blend editor — reconnect the missing source or re-map the metrics.

4. **For channel-by-channel comparison**, fetch data from each source individually and present side by side:
   ```
   # Google Ads
   fetch-data source_id: <google_ads_id>, ...
   # Facebook Ads
   fetch-data source_id: <facebook_ads_id>, ...
   ```

## Workflow: Source Group Analysis

Source groups are particularly useful for agencies managing many accounts of the same type.

1. **List source groups**:
   ```
   list-source-groups action: list
   ```

2. **Inspect group membership**:
   ```
   list-source-groups action: show, group_id: <id>
   ```
   Shows all sources in the group and their ETL configurations.

3. **Check for sync issues**:
   ```
   list-source-groups action: source_issues, group_id: <id>
   ```
   Lists sources with disabled ETL configs — these are not contributing data.

## Workflow: Custom Metrics and Dimensions

1. **List custom metrics**:
   ```
   list-custom-metrics action: list
   ```
   Custom metrics enable cross-channel calculations like total spend, blended ROAS, or weighted averages.

2. **Inspect a custom metric formula**:
   ```
   list-custom-metrics action: show, metric_id: <id>
   ```

3. **List custom dimensions**:
   ```
   list-custom-dimensions action: list
   ```

## Common Cross-Channel Analysis Patterns

### Total Performance Summary
Fetch key metrics from each channel and present a unified summary:
- **Total Spend**: Sum of spend across all paid channels
- **Total Conversions**: Sum of conversions (watch for attribution overlap)
- **Blended ROAS**: Total conversion value / Total spend
- **Blended CPC**: Total spend / Total clicks

### Channel Comparison Table
| Channel | Spend | Clicks | Conversions | CPC | ROAS |
|---------|-------|--------|------------|-----|------|
| Google Ads | ... | ... | ... | ... | ... |
| Facebook Ads | ... | ... | ... | ... | ... |
| LinkedIn Ads | ... | ... | ... | ... | ... |
| **Total** | ... | ... | ... | ... | ... |

### Trend Analysis Across Channels
Fetch daily data from each channel with `dimensions: ["date"]` and create a combined time series to show how total performance evolves.

### Channel Mix Analysis
Calculate each channel's share of total spend, conversions, or traffic to understand budget allocation effectiveness.

## Important Considerations

- **Metric naming varies across platforms**: "Clicks" in Google Ads may be "link_clicks" in Facebook Ads. Blends handle this mapping, but when comparing sources directly, check metric names with `list_dimensions_and_metrics`.
- **Currency differences**: Sources may report in different currencies. Check the `currency` field on each source.
- **Attribution overlap**: When summing conversions across channels, the total may exceed actual conversions due to multi-touch attribution. Note this when presenting cross-channel totals.
- **Date alignment**: Ensure all channel data covers the exact same date range for fair comparison.

## Tips

- When users ask "what's working best?", compare channels by efficiency metrics (ROAS, CPC, cost per conversion) rather than just volume.
- For budget allocation questions, calculate the marginal efficiency of each channel.
- Source groups with many sources (50+) may take longer to return data. Set expectations about load times.
- If a blend shows unexpected numbers, inspect its source mapping — a metric might be incorrectly mapped or a source might be missing.
