---
name: whatagraph-sources-and-data
type: domain
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
list-sources action=health_summary                            # quick ok/error/total counts — no pagination
list-sources action=list                                      # paginated list
list-sources action=list search="Acme"                        # filter by name substring
list-sources action=list semantic_search="paid advertising"   # meaning-based search (finds Google Ads, Facebook Ads, etc.)
list-sources action=list channels=[<integration_id>]          # one channel — resolve the id via list-integrations, never hardcode
list-sources action=list space_ids=[<space_id>]               # sources in one space
list-sources action=list status="issue"                       # broken sources only
list-sources action=list only_untagged=true                   # sources without tags
list-sources action=list currencies=["EUR","USD"]             # by currency
list-sources action=list tags=[<tag_id>]                      # by tag IDs
list-sources action=list sort_by="name-asc"                   # newest (default), oldest, name-asc, name-desc
```

Returns source `id`, `name`, channel, space assignments, currency, and access status.

Deep-dive a single source:

```
list-sources action=show source_id=<id>
```

### Trimming the response — `fields`

`list` and `show` accept `fields` (comma-separated) to return only the attributes you need and stay under the ~50 KB cap. For sources the selectable paths are:

`id, name, external_id, channel_id, channel_name, account_id, currency, status, space_ids, tag_ids`

`channel` and `integration` are accepted as aliases for `channel_id`; `service`, `platform`, and `integration_name` are aliases for `channel_name`. The set is per-tool and not uniform — if you pass an unknown path the call is rejected and the error lists the valid paths; read that list and retry once instead of guessing. Don't assume nested paths such as `options.currency` exist.

## Available report types, metrics, dimensions

Most sources expose multiple **report types** (e.g. "campaign", "ad", "keyword"). Each report type has its own metrics and dimensions.

```
list-sources action=list_report_types source_id=<id>
# → [{"external_id":"campaign","name":"Campaigns"}, ...]

list-sources action=list_dimensions_and_metrics
   source_id=<id>
   report_type="campaign"
   field_kind="metrics"                    # "metrics" or "dimensions" to filter; omit for both
   premade_only=true                       # only the ~20 headline fields; omit for full catalog
# → {"dimensions":[...],"metrics":[...]}
```

Each source in `list` and `show` responses includes `requires_report_type` (boolean). When `true`, you must call `list_report_types` and pass the result to widget/fetch calls. When `false` (e.g. Facebook Ads, GA4), skip `list_report_types` entirely — omit `report_type` from subsequent calls. If you pass an invalid report type, the error lists valid options — use that list.

### Finding a field by name — try `resolve_fields` first

To get the `external_id` for a metric or dimension the user named, make `resolve_fields` your first move — it takes `source_id` + a natural-language `query` (e.g. "how much did we spend" → Cost) and returns the best-matching fields ranked by relevance, no exact spelling needed. Pass `report_type` too when the source has multiple report types. Fall back to `list_dimensions_and_metrics` with `filter` (below) only when `resolve_fields` returns nothing.

```
list-sources action=resolve_fields source_id=<id> query="how much did we spend"
# → best-matching fields (e.g. metrics.cost_micros) ranked by relevance
```

### Narrowing a large field catalog — use `filter`

Big channels return hundreds of fields per report type, and `list_dimensions_and_metrics` is cursor-paginated and capped (~50 KB). When you already know the field the user named, filter instead of pulling and scanning everything:

```
list-sources action=list_dimensions_and_metrics source_id=<id> report_type="campaign" filter="cost"
# → only fields whose name or external_id contains "cost"
```

- **`filter`** — case-insensitive substring on the display name **and** the `external_id`. Make it your default first move whenever the user named the metric/dimension ("spend", "roas", "sessions", "conversions").
- **`is_universal=true`** — only the unified `universal_*` fields (source groups / blends); `false` — only channel-native fields; omit for all.
- This call is **paginated**: decide whether to continue with `page.has_more` (not `estimated_total`, which is commonly `null` on this action), passing `page.cursor`. Prefer `filter` / `is_universal` / `per_page` over paging the whole catalog.

### Deprecated fields

Fields the channel has retired carry `deprecated_at`, and `deprecated: true` once that date has passed. Both keys are only present when a date is set, so absence means the field is current.

- Fields whose deprecation has **already taken effect** are left out of the catalog entirely — they no longer return data. If a widget is bound to one, `list-widgets action=show` flags it inline (`"deprecated": true` on the bound metric), which is the way to tell a retired binding apart from a typo.
- Fields with a **future** `deprecated_at` are still listed and still work, but are sorted to the bottom of the catalog (so onto the last page). Treat them as "migrate before this date", not as a choice.
- `manage-widgets` refuses to bind a field whose deprecation has taken effect, and warns when binding one that is only scheduled.

To replace a retired metric: read the widget with `list-widgets action=show` to see which bound fields are flagged, then look for the current equivalent in the catalog — the replacement usually shares wording with the old name (e.g. a retired "Likes" metric replaced by "Followers"). `resolve_fields` with a natural-language query is the fastest way to find it.

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

Response: rows of metric values grouped by dimensions. `limit` controls page size (default 100, max 1000).

### Comparison in a single call

Use `compare_type` to get comparison data alongside the primary data:

```
fetch-data source_id=<id> metrics=[...] from="2025-10-01" till="2025-10-31"
   compare_type="previous"              # auto-calculates the previous period
fetch-data source_id=<id> metrics=[...] from="2025-10-01" till="2025-10-31"
   compare_type="custom" vs_from="2025-04-01" vs_till="2025-04-30"
```

Values: `previous` (matching-length previous period), `last_year` (same dates, year prior), `custom` (explicit `vs_from`/`vs_till`).

### Field-id family by source type

| Source type | Metric id form | Dimension id form |
|---|---|---|
| Native source (Google Ads campaign) | `metrics.clicks`, `metrics.cost_micros` | `campaign.name`, `segments.date` |
| Source group (channel rollup, channel_id=154 — verified Jun 2026) | `universal_metric_<n>` | `universal_dimension_<n>` |
| Source group — per channel (one channel's sub-total) | `universal_metric_<n>_integration_<integrationId>` | — |
| Source group — per source (one sub-source's contribution) | `universal_metric_<n>_integration_source_<sourceId>` | `universal_dimension_1130` (Channel name) / `1131` (Source name) split the aggregate |
| Blend (cross-channel, channel_id=142 — verified Jun 2026) — fetch-data | `aggregation_metric_universal_metric_<n>` | `aggregation_dimension_universal_dimension_<n>` |
| Blend — per-sub-source fields (rare in fetch) | `blend_metric_<id>` | `blend_dimension_<id>` |

If `fetch-data` returns `Invalid metrics: X` or `Invalid dimensions: X`, do not retry with a variant spelling. Re-run `list_dimensions_and_metrics` and pick the value verbatim from the response — including dots and prefixes.

### Source-group breakdown metrics — pick the variant, don't filter

Every universal metric on a source group exists in **three tiers**:

- **Aggregate** — `universal_metric_<n>` — every source of every channel, summed.
- **Per channel** — `universal_metric_<n>_integration_<integrationId>` — all sources of one channel, summed (e.g. all Google Ads accounts in the group).
- **Per source** — `universal_metric_<n>_integration_source_<sourceId>` — one sub-source's contribution.

Two SYSTEM dimensions break the aggregate into rows instead: `universal_dimension_1130` (Channel name) and `universal_dimension_1131` (Source name).

When the user wants **one channel's or one source's** number out of a group — "show all Spend for Google Ads channels in this group", "just the X account's clicks" — **pick the matching `_integration_<id>` / `_integration_source_<id>` metric variant**. Do **not** add a channel/source filter, and do **not** fetch the full aggregate and try to subset it — the variant already isolates it. The user never types these ids; you resolve them: each field returned by `list_dimensions_and_metrics` carries a `group` attribute (`integration_6`, `integration_source_4038`, …) naming the channel/source it belongs to — match on that, never hand-construct the id.

Caveats: the per-source variants exist only on **multi-source** groups, and are dropped on very large (consolidated) groups — there, break out by `universal_dimension_1131` (Source name) instead.

### Handling "data is being processed"

`fetch-data` may return a transient error on the first call after creating a blend or source group, or after a long idle period:

```
{"success": false, "error": {"category": "internal", "message": "Your data is being processed... please wait...", "retryable": false}}
```

**Important:** `retryable: false` is misleading on this specific message — the condition is transient. Wait ~10–15 seconds and retry the same call once or twice. What's actually pending differs by source type: a **blend** stores nothing and is computed live, so this means one of its **underlying sub-sources** isn't ready yet (still fetching from its API, rate-limited, or period not aggregated) — there is no blend warmup. A **source group** is ETL/BigQuery-populated and genuinely takes a few minutes to populate after creation. **Declarative connectors** can take 2–3 minutes on first fetch. The legacy pending response shape (`{"status":"pending","retry_after":30}`) is also seen on some integrations — same handling: wait the indicated seconds and retry.

Do NOT surface this error to the user as a hard failure. Treat any "data is being processed" / "please wait" / `retry_after` response as a retry-with-backoff signal regardless of the `retryable` flag.

## Listing integrations (channels)

```
list-integrations action=list                           # all integrations
list-integrations action=list_grouped                   # grouped by category
list-integrations action=list_accounts channel_id=2     # connected accounts
list-integrations action=list_available_sources account_id=<id> search="Acme"
```

Use this when the user asks "what platforms does Whatagraph support?" or wants to connect a new sub-account from an already-authenticated integration.

### Sub-source integrations

Some integrations (Google Sheets, BigQuery, Snowflake, Google My Business) have parent → sub-source hierarchy. When `list_available_sources` returns `has_sub_sources: true`, discover sub-sources before adding:

```
list-integrations action=list_available_sub_sources
   account_id=<id>
   source_external_id=<parent_external_id>   # from list_available_sources
   search="tab name"                          # optional name filter
```

Returns sub-source names and JSON `external_id` values ready for `manage-integrations action=add_sources`. See `whatagraph-integrations-admin` for the full connect flow.

## Where is a source used?

```
list-sources action=list_usage source_ids=[<id>, <id>]
```

Returns usage counts across reports, blends, source groups, transfers, and overviews (measurements). Critical before disconnecting or replacing a source — shows what breaks.

## Metadata discovery and per-channel counts

`list-sources action=list_metadata` returns reference metadata for source management, scoped by `scope`:

- `integrations` (default) — the integrations this team can use, each with `has_accounts_for_current_user`. This is the **catalog of what can be connected**, not a count of connected sources per channel.
- `accounts`, `spaces`, `users`, `tags`, `categories` — the matching option lists. Use `scope=tags` for tag dimensions and their allowed values when building `manage-sources action=tag` calls.
- `all` — every scope at once; may exceed the size cap on large accounts, so prefer a single scope.

To count **connected** sources per channel, page `list-sources action=list` (use `fields=id,channel_id` to stay small) and aggregate by `channel_id`; `list-integrations action=list_grouped` gives a category-level overview.

## Modifying sources

```
manage-sources action=set_currency
   source_ids=[<id>, <id>]
   currency="EUR"

manage-sources action=tag
   source_ids=[<id>]
   tag_id=<tag_dimension_id>        # from list_metadata scope=tags
   tag_value_ids=[<value_id>, ...]  # empty array = remove all tag values in that dimension

manage-sources action=refresh
   source_ids=[<id>, <id>]          # max 10 per call
```

**`refresh`** clears cached data so the next read re-fetches fresh data from the provider. Useful for "my data isn't showing" troubleshooting after a source reconnect or data delay.

**`tag` only assigns values that already exist.** It is not a create path — an unknown `tag_id` or `tag_value_ids` is rejected, not created. To make a new tag (the tag dimension plus its values, optionally assigning sources in the same call), use `manage-custom-dimensions action=create map_type=tag`, then come back here for later assignments. See `whatagraph-custom-dimensions`.

**Currency override** is the most common fix when numbers look wrong — a USD Google Ads account reporting into a EUR-default team needs an explicit override here. Override affects display only; historical data rows keep their stored currency.

## Deleting sources

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: team-level detach (other teams unaffected, reconnect to restore), dependent widgets/blends/groups/measurements break, pre-check `list-sources action=list_usage source_ids=[...]`.

## What MCP can't do here

- Connect a new OAuth integration account — UI only.
- Re-authorize a source with an expired connection — UI only.
- Assign a source to a space — use `manage-integrations action=sync_to_clients` (see `whatagraph-integrations-admin`).

## Common pitfalls

- **"My data isn't showing"** — run `list-sources action=show source_id=<id>` and check `status`. If `issue`, the source needs re-authorization in the UI. When `status` is `error`, the response includes `error_reason` describing why the source is broken.
- **Numbers don't match the channel** — verify currency and timezone on `show`. Common mismatch sources.
- **Passing metric names instead of ids** — `fetch-data` expects the `external_id` (e.g. `spend`), not the display name ("Spend"). Use `list_dimensions_and_metrics` to discover correct ids.
- **Too many sources with similar names** — narrow with `search` + `channels` + `space_ids`.
- **Missing historical data after connect** — backfill can take hours. `fetch-data` returns empty for missing days until ETL finishes.
- **`manage-sources action=set_currency` when `currency="USD"` already** — no-op, does not convert existing rows.
- **Tag values on the wrong dimension** — each tag value belongs to one tag dimension. Cross-dimension values are rejected.
