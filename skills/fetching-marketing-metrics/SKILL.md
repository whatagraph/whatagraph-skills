---
name: fetching-marketing-metrics
description: >-
  Fetch and analyze raw marketing performance data from any connected Whatagraph
  source via fetch-data — pick the right report type, metrics, and dimensions,
  narrow large field catalogs efficiently with the filter parameter, set date
  ranges, and interpret the results. Use when the user asks for specific numbers
  or performance ("how did Google Ads do last month?", spend, ROAS, CPA, CPC,
  sessions, conversions, opens), wants period-over-period comparisons, or needs
  raw metric values from a channel, source group, or blend.
required_tools:
  - list-integrations
  - list-sources
  - fetch-data
---

# Fetching Marketing Metrics

Retrieve marketing performance data from connected sources using the `fetch-data` tool. This skill covers selecting the right metrics, dimensions, date ranges, and interpreting the results.

## Critical Rule: Never Guess Field Names

**Every metric and dimension name you pass to `fetch-data` must come from a `list-sources` `action: list_dimensions_and_metrics` response for the exact same `source_id` + `report_type` combination. Never rely on your prior knowledge of the native platform's API.**

Whatagraph exposes a field catalog whose id format varies by channel — some channels keep the platform's native names, others normalize them. The format you can't predict, so look it up; these are common mistakes:

| Wrong (guess) | Actual Whatagraph field |
|--------------------------|--------------------------|
| `sessionDefaultChannelGroup` (GA4, wrong suffix) | GA4 keeps its native camelCase API names verbatim — the real id is `sessionDefaultChannelGrouping` (and `sessions`, `sessionSourceMedium`, `defaultChannelGrouping` all work as-is). Look up the exact spelling. |
| `campaignName`, `campaign_name` | varies — Google Ads exposes `campaign.name` (dot, not underscore); source groups expose `universal_dimension_<n>`; blends expose `aggregation_dimension_universal_dimension_<n>` |
| `spend` (generic) | varies by channel — `metrics.cost_micros` on Google Ads, `spend` on Meta, `universal_metric_3` on source groups |
| `date` (on sources without time dimension) | some report types don't support date at all — check first |
| `universal_metric_N` | these appear on **source groups and blends**, not on native channel sources. On native sources (Google Ads, Meta, GA4, etc.) use the channel-native id from `list_dimensions_and_metrics`. On source groups the catalog returns `universal_metric_N` / `universal_dimension_N` ids; on blends it returns `aggregation_metric_universal_metric_N` / `aggregation_dimension_universal_dimension_N` (or `blend_*` prefixes). Never guess the number — look it up each time. |

If `fetch-data` returns `Invalid metrics: X` or `Invalid dimensions: X`, do not retry with a variant spelling. Re-run `list-sources action: list_dimensions_and_metrics` with the correct `source_id` and `report_type` and pick a name from the response verbatim.

## Before Fetching Data

Always confirm these three things before calling `fetch-data`:

1. **Source ID** — Use `list-sources action: list, channels: ["<slug>"]` to find the correct source. Users often refer to sources by channel name (e.g., "my Google Ads account") — filter with the channel slug (`channels: ["google-ads"]`) rather than `search`, because `search` matches the source's custom *name* (which users rename to things like "GSN|CA" or "Whatagraph"), not the channel type.
2. **Report type** — Many sources expose multiple report types (e.g., Google Ads has `ACCOUNT`, `CAMPAIGN`, `AD_GROUP`, `AD`; Bing Ads has `customer`, `campaign`, `ad_group`, etc.). Always call `list-sources` with `action: list_report_types` before fetching. If the source has more than one report type, `fetch-data` **will error** unless you pass `report_type`.
3. **Available metrics and dimensions** — Call `list-sources` with `action: list_dimensions_and_metrics` with both `source_id` **and** `report_type` to see what fields are available. The response is specific to that report type — switching report types changes the catalog.

### Narrowing a large field catalog — use `filter` first

Big channels expose **hundreds** of fields per report type (Google Ads `campaign` has 500+), and this response is cursor-paginated and capped (~50 KB) — so a bare `list_dimensions_and_metrics` call returns a truncated, mostly-config list you then have to scan. When you already know the metric or dimension the user named, **filter the catalog in one call** instead of pulling and paginating the whole thing:

```
list-sources action: list_dimensions_and_metrics, source_id: <id>, report_type: "campaign", filter: "cost"
→ only fields whose name or external_id contains "cost"
  (e.g. metrics.cost_micros, metrics.cost_per_conversion, metrics.average_cost)
```

- **`filter`** is a case-insensitive substring match on both the display name and the `external_id`. Make it your **default first move** whenever the user named the field — "spend", "roas", "conversions", "sessions", "clicks". It turns a 500-field scan into a handful of fields in one call.
- **`premade_only: true`** returns only the curated headline metrics/dimensions (~20 fields: cost, clicks, impressions, conversions, etc.) instead of the full 500+ catalog. Use this as the default when the user asks a general question ("how did we do?") and you don't yet know which specific fields to fetch.
- **`is_universal: true`** returns only the platform-unified `universal_*` fields (useful on source groups and blends); `is_universal: false` returns only channel-native fields; omit for all.
- **`per_page: 500`** — when you do need the full catalog (rare), set `per_page: 500` to minimize pagination round-trips instead of the default 100.
- This call is **paginated**: check `page.has_more` and `page.estimated_total` to know how many fields remain, and pass `page.cursor` to continue. Prefer `filter` / `premade_only` / `is_universal` over paging through the full catalog.
- To narrow *sources* to a single channel, pass **channel slugs** to `list-sources action: list` — e.g. `channels: ["google-ads"]`, `channels: ["facebook-ads"]`. Slugs are resolved automatically; **do not guess integer IDs**. Common slugs: `google-ads`, `facebook-ads`, `google-analytics-4`, `linkedin-ads`, `tiktok`, `bing-ads`, `instagram-business`, `hubspot`, `mailchimp`.

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

1. **Identify the source** — filter by channel slug, not by name search:
   ```
   list-sources action: list, channels: ["google-ads"]
   ```

2. **Check available report types**:
   ```
   list-sources action: list_report_types, source_id: <id>
   ```

3. **Check available metrics and dimensions** — use `filter` or `premade_only` to avoid paginating 500+ fields:
   ```
   # When you know the metric name:
   list-sources action: list_dimensions_and_metrics, source_id: <id>, report_type: "<type>", filter: "cost"

   # When you need an overview of what's available:
   list-sources action: list_dimensions_and_metrics, source_id: <id>, report_type: "<type>", premade_only: true
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

Alternatively, pass a `period` preset instead of `from`/`till` and let the source compute the range. A wide set is supported — among them `today`, `yesterday`, `last7Days`/`last14Days`/`last30Days`/`last90Days`, `lastWeek`, `lastMonth`, `lastQuarter`, `lastYear`, `thisWeek`/`thisMonth`/`thisQuarter`/`thisYear`, the `full*` variants (`fullWeek`, `fullMonth`, `fullQuarter`, `fullYear` — the most recent fully-completed period), and the `*ExclToday` variants (`thisWeekExclToday`, `thisMonthExclToday`, …). If you pass an invalid key the error lists every valid period — copy one from there.

## Interpreting Results

- **Null or missing values**: Some metrics may return null for certain date ranges if no data was collected. This is normal — explain it to the user rather than treating it as an error.
- **Currency**: Check the source's `currency` field from `list-sources` to know which currency cost metrics are reported in.
- **Aggregation**: Data is aggregated by the dimensions you specify. No dimensions = single totals row. Adding `date` dimension gives daily breakdown.
- **Rate metrics**: Metrics like CTR, conversion rate, and ROAS may be pre-calculated or may need manual calculation from component metrics depending on the source.

## Tips

- Start with fewer metrics and dimensions, then expand. Large requests may be slower.
- Always include a `date` dimension when users want to see trends over time.
- If a metric returns unexpected results, check if the report type is correct — different report types expose different metrics.
- Keep each call focused — fetch the metrics you actually need rather than the whole catalog. There is no hard cap on the number of metrics, but large requests are slower and the response is byte-capped (~50 KB) and paginated. The `limit` parameter caps the number of **rows** returned (default 100, max 1000), not metrics.
- For period-over-period comparisons, make two `fetch-data` calls with different date ranges and compare the results side by side. (If the user has a Whatagraph report with a built-in comparison period, prefer the `generating-report-digests` skill, which surfaces comparison metrics directly.)

## Handling Errors (read before retrying)

- `Invalid metrics: X` / `Invalid dimensions: X` — do NOT retry with a spelling variant. Re-run `list-sources action: list_dimensions_and_metrics`.
- `Multiple report types are available.` — the source has multiple report types; you must pass `report_type`. See recovery pattern above.
- `The dimensions and metrics are incompatible.` — this report type does not support that combination. Pick a different report type or drop the dimension (typically the finest-grained dimension).
- `Invalid source_id.` — the source ID was fabricated or stale. Re-run `list-sources action: list` with a `search` term matching the user's words.
- Provider access or usage-limit errors are account-level issues the user must resolve; tell them which source needs attention and stop retrying.
- `One or more GA4 metric names contain unsupported characters.` — the GA4 field id you passed isn't a valid one (GA4 ids are the native camelCase names like `sessions`, `sessionSourceMedium` — valid names work as-is, so this means the spelling is wrong, not that GA4 names need rewriting). Re-check the exact `external_id` via `list-sources action: list_dimensions_and_metrics`.
- **`Your data is being processed... please wait...`** — transient warmup state. Common on blends and source groups the first time they're queried, or after a long idle period. The response often comes back with `retryable: false`, but **the condition is retryable**: wait 10–15 seconds and call again with the same parameters. Two retries with backoff (10s, 30s) is enough for almost every case; declarative connectors (e.g. some Fivetran-backed sources) can take up to ~3 minutes on first fetch. Do NOT surface this to the user as a hard failure or treat `retryable: false` as authoritative on this specific message. Same handling applies to the legacy `{"status":"pending","retry_after":<n>}` shape — wait the indicated seconds and retry.
