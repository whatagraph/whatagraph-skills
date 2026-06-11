---
name: whatagraph-sources-and-data
description: Discover and query Whatagraph data sources — find which accounts are connected, list report types and the available metrics and dimensions (narrowing large catalogs with the filter parameter), pull raw numbers via fetch-data, and check where a source is used. Covers native channels, source groups, and blends. Use this before any reporting task to establish what data is available.
required_tools:
  - list-integrations
  - list-sources
  - fetch-data
  - manage-integrations
  - manage-sources
---

# Data sources and fetching data

Tools covered: `list-sources`, `list-integrations`, `fetch-data`, `manage-sources`.

A **data source** is one connected account (one Google Ads account, one GA4 property, one Shopify store). A **channel** (or integration) is the type of account (Google Ads, GA4, Shopify). Users often say "my Facebook account" when they mean a Facebook Ads data source.

## Use this when

- The user wants to know what accounts are connected to their team.
- Before building any widget, to confirm which metrics/dimensions are available.
- To pull raw numbers for ad-hoc analysis without building a widget.
- To see where a specific source is used across reports, blends, groups.
- To tag sources or override the display currency.

## Discovery sequence (do this first)

```
list-sources action=list                                      # paginated list
list-sources action=list search="Acme"                        # filter by name
list-sources action=list channels=[<integration_id>]          # one channel — resolve the id via list-integrations, never hardcode
list-sources action=list space_ids=[<space_id>]               # sources in one space
list-sources action=list status="issue"                       # broken sources only
list-sources action=list only_untagged=true                   # sources without tags
list-sources action=list currencies=["EUR","USD"]             # by currency
```

Returns source `id`, `name`, channel, space assignments, currency, and access status.

Deep-dive a single source:

```
list-sources action=show source_id=<id>
```

## Available report types, metrics, dimensions

Most sources expose multiple **report types** (e.g. "campaign", "ad", "keyword"). Each report type has its own metrics and dimensions.

```
list-sources action=list_report_types source_id=<id>
# → [{"external_id":"campaign","name":"Campaigns"}, ...]

list-sources action=list_dimensions_and_metrics
   source_id=<id>
   report_type="campaign"
# → {"dimensions":[...],"metrics":[...]}
```

**Always run `list_report_types` first** when you don't know the report type. `list_dimensions_and_metrics` requires `report_type` when a source has multiple. Some sources (e.g. Facebook Ads, GA4) return zero report types — omit `report_type` entirely for those. If you pass an invalid report type, the error lists valid options — use that list.

### Narrowing a large field catalog — use `filter`

Big channels return hundreds of fields per report type, and `list_dimensions_and_metrics` is cursor-paginated and capped (~50 KB). When you already know the field the user named, filter instead of pulling and scanning everything:

```
list-sources action=list_dimensions_and_metrics source_id=<id> report_type="campaign" filter="cost"
# → only fields whose name or external_id contains "cost"
```

- **`filter`** — case-insensitive substring on the display name **and** the `external_id`. Make it your default first move whenever the user named the metric/dimension ("spend", "roas", "sessions", "conversions").
- **`is_universal=true`** — only the unified `universal_*` fields (source groups / blends); `false` — only channel-native fields; omit for all.
- This call is **paginated**: decide whether to continue with `page.has_more` (not `estimated_total`, which is commonly `null` on this action), passing `page.cursor`. Prefer `filter` / `is_universal` / `per_page` over paging the whole catalog.

## Fetching raw data

Field ids in `metrics` and `dimensions` are the channel-native `external_id` returned by `list_dimensions_and_metrics` — not display names, not what the native platform's API calls them. For Google Ads campaign-level fetches that means `metrics.clicks`, `metrics.impressions`, `metrics.cost_micros`, and the dimension is `campaign.name` (dot, not underscore). For source groups and blends the ids are different again — see the family table below.

```
fetch-data
   source_id=<google_ads_source_id>
   report_type="campaign"
   metrics=["metrics.clicks","metrics.impressions","metrics.cost_micros"]
   dimensions=["campaign.name"]
   from="2025-10-01"
   till="2025-10-31"
   limit=100
```

Response: rows of metric values grouped by dimensions.

### Field-id family by source type

| Source type | Metric id form | Dimension id form |
|---|---|---|
| Native source (Google Ads campaign) | `metrics.clicks`, `metrics.cost_micros` | `campaign.name`, `segments.date` |
| Source group (channel rollup, channel_id=154) | `universal_metric_<n>` | `universal_dimension_<n>` |
| Blend (cross-channel, channel_id=142) — fetch-data | `aggregation_metric_universal_metric_<n>` | `aggregation_dimension_universal_dimension_<n>` |
| Blend — per-sub-source fields (rare in fetch) | `blend_metric_<id>` | `blend_dimension_<id>` |

If `fetch-data` returns `Invalid metrics: X` or `Invalid dimensions: X`, do not retry with a variant spelling. Re-run `list_dimensions_and_metrics` and pick the value verbatim from the response — including dots and prefixes.

### Handling "data is being processed"

`fetch-data` may return a transient warmup error on the first call after creating a blend or source group, or after a long idle period:

```
{"success": false, "error": {"category": "internal", "message": "Your data is being processed... please wait...", "retryable": false}}
```

**Important:** `retryable: false` is misleading on this specific message — the condition is transient. Wait ~10–15 seconds and retry the same call once or twice. Most blends warm up within 30 seconds; declarative connectors can take 2–3 minutes on first fetch. The legacy pending response shape (`{"status":"pending","retry_after":30}`) is also seen on some integrations — same handling: wait the indicated seconds and retry.

Do NOT surface the warmup error to the user as a hard failure. Treat any "data is being processed" / "please wait" / `retry_after` response as a retry-with-backoff signal regardless of the `retryable` flag.

## Listing integrations (channels)

```
list-integrations action=list                           # all integrations
list-integrations action=list_grouped                   # grouped by category
list-integrations action=list_accounts channel_id=2     # connected accounts
list-integrations action=list_available_sources account_id=<id> search="Acme"
```

Use this when the user asks "what platforms does Whatagraph support?" or wants to connect a new sub-account from an already-authenticated integration.

## Where is a source used?

```
list-sources action=list_usage source_ids=[<id>, <id>]
```

Returns usage counts across reports, blends, source groups, transfers, and overviews (measurements). Critical before disconnecting or replacing a source — shows what breaks.

## Metadata discovery (tag dimensions, tag values, etc.)

```
list-sources action=list_metadata
```

Returns available tag dimensions and their allowed values — use to build `manage-sources action=tag` calls.

## Modifying sources

```
manage-sources action=set_currency
   source_ids=[<id>, <id>]
   currency="EUR"

manage-sources action=tag
   source_ids=[<id>]
   tag_id=<tag_dimension_id>        # from list_metadata
   tag_value_ids=[<value_id>, ...]  # empty array = remove all tag values in that dimension
```

**Currency override** is the most common fix when numbers look wrong — a USD Google Ads account reporting into a EUR-default team needs an explicit override here. Override affects display only; historical data rows keep their stored currency.

## Deleting sources

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: team-level detach (other teams unaffected, reconnect to restore), dependent widgets/blends/groups/measurements break, pre-check `list-sources action=list_usage source_ids=[...]`.

## What MCP can't do here

- Connect a new OAuth integration account — UI only.
- Re-authorize a source with an expired connection — UI only.
- Assign a source to a space — use `manage-integrations action=sync_to_clients` (see `whatagraph-integrations-admin`).

## Common pitfalls

- **"My data isn't showing"** — run `list-sources action=show source_id=<id>` and check `status`. If `issue`, the source needs re-authorization in the UI.
- **Numbers don't match the channel** — verify currency and timezone on `show`. Common mismatch sources.
- **Passing metric names instead of ids** — `fetch-data` expects the `external_id` (e.g. `spend`), not the display name ("Spend"). Use `list_dimensions_and_metrics` to discover correct ids.
- **Too many sources with similar names** — narrow with `search` + `channels` + `space_ids`.
- **Missing historical data after connect** — backfill can take hours. `fetch-data` returns empty for missing days until ETL finishes.
- **`manage-sources action=set_currency` when `currency="USD"` already** — no-op, does not convert existing rows.
- **Tag values on the wrong dimension** — each tag value belongs to one tag dimension. Cross-dimension values are rejected.
