---
name: whatagraph-sources-and-data
description: Discover and query Whatagraph data sources — find which accounts are connected, list available metrics and dimensions, pull raw numbers, and check where a source is being used. Use this before any reporting task to establish what data is available.
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
list-sources action=list channels=[2]                         # only Google Ads
list-sources action=list team_clients=[<space_id>]            # sources in one space
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

**Always run `list_report_types` first** when you don't know the report type. `list_dimensions_and_metrics` requires `report_type` when a source has multiple. If you pass an invalid report type, the error lists valid options — use that list.

## Fetching raw data

```
fetch-data
   source_id=<id>
   report_type="campaign"
   metrics=["spend","clicks","impressions"]
   dimensions=["campaign_name"]
   from="2025-10-01"
   till="2025-10-31"
   limit=100
```

Response: rows of metric values grouped by dimensions.

**`retry_after` handling:** when the response indicates data is being prepared (e.g. `{"status":"pending","retry_after":30}`), wait the indicated seconds and call again with the same parameters. Do NOT surface this as an error. Most integrations return in 5–30 seconds; some declarative connectors can take 2–3 minutes on first fetch.

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

## What MCP can't do here

- Connect a new OAuth integration account — UI only.
- Re-authorize a source with an expired token — UI only.
- Delete a source — UI only.
- Assign a source to a space — use `manage-integrations action=sync_to_clients` (see `whatagraph-integrations-admin`).

## Common pitfalls

- **"My data isn't showing"** — run `list-sources action=show source_id=<id>` and check `status`. If `issue`, the source needs re-authorization in the UI.
- **Numbers don't match the channel** — verify currency and timezone on `show`. Common mismatch sources.
- **Passing metric names instead of ids** — `fetch-data` expects the `external_id` (e.g. `spend`), not the display name ("Spend"). Use `list_dimensions_and_metrics` to discover correct ids.
- **Too many sources with similar names** — narrow with `search` + `channels` + `team_clients`.
- **Missing historical data after connect** — backfill can take hours. `fetch-data` returns empty for missing days until ETL finishes.
- **`manage-sources action=set_currency` when `currency="USD"` already** — no-op, does not convert existing rows.
- **Tag values on the wrong dimension** — each tag value belongs to one tag dimension. Cross-dimension values are rejected.
