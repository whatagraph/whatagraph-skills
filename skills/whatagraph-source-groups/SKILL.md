---
name: whatagraph-source-groups
description: Combine multiple data sources into one virtual aggregated source — same-channel (e.g. five Google Ads sub-accounts) or cross-channel (e.g. Meta + Google + Reddit + TikTok). Use when an agency wants unified reporting without building a blend.
---

# Source groups

Tools covered: `list-source-groups`, `manage-source-groups`, `delete-source-groups`.

A **source group** aggregates multiple sources into one virtual source. Sources can be from the same channel (e.g. multiple Google Ads accounts) or from different channels (e.g. Meta Ads + Google Ads + Reddit Ads + TikTok — cross-channel aggregation). The group gets its own integration source id that widgets, blends, and custom metrics can reference as if it were a single source.

## Use this when

- Agency has 3 Google Ads sub-accounts under one client MCC — roll up to one "Google Ads" source.
- Property manager has 20 GBP locations — one aggregated source for reporting.
- Franchise brand has multiple Meta ad accounts per region — one virtual source per brand.
- Cross-channel rollup — combine Meta Ads + Google Ads + Reddit Ads + TikTok into one aggregated source with unified metrics (impressions, clicks, spend).

## Source group vs blend vs custom metric

| Goal | Use |
|---|---|
| 5 Google Ads accounts → 1 virtual "Google Ads Total" | Source group (same-channel) |
| Meta + Google + Reddit + TikTok → 1 aggregated source with unified metrics | Source group (cross-channel) |
| Google Ads + Meta Ads joined/matched on campaign name | Blend |
| Sum of `spend` across Google + Meta without joining | Custom metric `data_aggregation` |

**Rule**: source groups handle both same-channel and cross-channel aggregation and are simpler than blending. Use a blend only when you need to **join** rows across channels on a shared dimension (e.g. matching campaign names between Google Ads and Meta Ads). Use a custom metric `data_aggregation` for a single summed field across sources without creating a full group.

## Listing

```
list-source-groups action=list                       # paginated; supports search
list-source-groups action=show group_id=<id>         # sources, configs, currency
list-source-groups action=source_issues group_id=<id> # sources with disabled ETL
```

## Creating a source group

```
manage-source-groups action=create
   name="Acme — Google Ads Rollup"
   description="All Acme Google Ads sub-accounts"
   currency="USD"
   configs=[{"output_name": "campaign_performance"}]
   integration_source_ids=[<src1>, <src2>, <src3>]
```

### Parameters

- `name` — group display name.
- `configs` — required. Each entry `{output_name: "<level>"}` where `<level>` is the granularity the group should expose: campaign performance, ad / ad-group performance, keyword performance, audience performance, geo performance, etc. Pick the level that matches the widgets you'll build on top — one config per level, and prefer one config per group (see "One config per group" below). The exact string is the **source-group template name** for that channel, *not* the channel-native report type external id you see in `list-sources action=list_report_types`. For most channels the template name is the report type with a `_performance` suffix — e.g. Google Ads `campaign` → `campaign_performance`, `ad_group` → `ad_group_performance`, `geo_view` → `geo_performance` — but Facebook Ads and others diverge (see the per-channel reference table below). If the API rejects an `output_name`, the error response lists every valid template name for that channel; copy one verbatim.
- `integration_source_ids` — array of source ids from `list-sources action=list`. Sources can be from the same channel or different channels (cross-channel aggregation is supported).
- `currency` — optional. Display currency.

#### Per-channel `output_name` reference

Template names diverge across channels — Google Ads-flavoured names like `campaign_performance` are not portable. Verified examples:

| Channel | Valid `output_name` (verified) |
|---|---|
| Google Ads | `campaign_performance`, `ad_group_performance`, `keyword_performance`, `geo_performance`, … |
| Facebook Ads | `creatives_performance` (note: not `campaigns_performance` or `campaign_performance`) |
| GA4 | TBD — not exercised in QA |
| LinkedIn Ads | TBD — not exercised in QA |

When in doubt, send a deliberately wrong `output_name` and read the rejection — the error response enumerates every valid template name for that channel.

## One config per group (strongly recommended)

Build a source group with exactly **one** entry in `configs`. If the user needs campaign-level *and* keyword-level rollups from the same set of sources, build two separate source groups, one per report type. This keeps each group focused and makes widgets, filters, and blends easier to reason about.

```
configs=[{"output_name": "campaign_performance"}]    # one config — preferred
```

Avoid putting multiple report types in one group:

```
configs=[
  {"output_name": "campaign_performance"},
  {"output_name": "keyword_performance"},
  {"output_name": "ad_group_performance"}
]
```

## Updating

```
manage-source-groups action=update group_id=<id>
   name="..."  integration_source_ids=[...]  configs=[...]
```

Replace-style — full lists replace previous values.

## Duplicating

```
manage-source-groups action=duplicate group_id=<id>
```

## Resolving sync issues

Some sources in the group may need attention after sync errors. Check affected sources and resolve them:

```
list-source-groups action=source_issues group_id=<id>        # view affected sources
manage-source-groups action=resolve_issues group_id=<id>
   integration_source_ids=[<affected_source_ids>]
```

## Using the group in widgets

The group exposes its own integration source id (found via `list-source-groups action=show` as `integration_source_id`). Attach it to the report first, then create the widget against the returned report-local `source_id`:

```
manage-reports action=attach_source report_id=<id>
   integration_source_id=<group_integration_source_id>
# response.source_id is the report-local id

manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id=<group_channel_id>
   source_id=<that report-local id>
   widget_type_id=<...>
```

The group's metrics and dimensions are the union of what the sub-sources expose — e.g. for a Google Ads group with one `campaign_performance` config, you get every Google Ads campaign-level metric and dimension.

## Reading data from a group directly

You don't need a widget to preview data from a source group. Use `fetch-data` on the group's `integration_source_id`:

```
fetch-data source_id=<group integration_source_id>
  report_type="<platform report type>"
  metrics=["universal_metric_1", "universal_metric_2", "universal_metric_3"]
  dimensions=["universal_dimension_1137"]
  from="2026-04-01" till="2026-04-15"
```

Notes:

- **`report_type`** is the source-group template name the group exposes (e.g. `campaign_performance` for a Google Ads campaign rollup), not the original source's channel-native report type (`campaign`). It usually matches the `output_name` you supplied when creating the group. Run `list-sources action=list_report_types source_id=<group integration_source_id>` to see the exact string to pass.
- **Field ids** use the `universal_metric_*` / `universal_dimension_*` form on the group's source. The platform aggregates sub-sources automatically.

## Deleting a source group

```
delete-source-groups action=delete group_id=<id>
```

Widgets and custom metrics that point at the group's virtual source will break. Run `list-source-groups action=show group_id=<id>` first and check usage; rebuild widgets to reference individual sources before deleting.

## What MCP can't do here

- Remove one sub-source from the group without providing the full replacement list — use `update` with the full new `integration_source_ids` list.

## Common pitfalls

- **Cross-channel `output_name` selection** — when mixing channels (e.g. Google Ads + Meta Ads + TikTok), use `list-source-groups action=list_output_names source_ids=[...]` to find template names that work across all supplied channels. Not every template is valid for every channel combination.
- **`output_name` is the source-group template name, not the channel-native report type** — e.g. `campaign_performance` for Google Ads, not `campaign`. The channel-native report type (`campaign`) is what you pass to `fetch-data` and `report_type_external_id` on the *original* sources, but the template name (`campaign_performance`) is what `manage-source-groups create configs` accepts. The two diverge on every paid-ads channel.
- **Empty group after creation** — freshly-created groups need time for ETL to populate; data may be empty for a few minutes for small accounts, longer for high-volume ones.
- **Group not appearing in widget picker immediately** — refresh the report; new groups can take a few seconds to appear.
- **Very large groups (hundreds of sub-sources)** — query performance can slow down. For very large rollups, consider a custom metric `data_aggregation` instead of a group.
- **Adding source groups can affect plan usage** — check the team's plan limits before bulk-creating groups.
- **`source_ids` vs `integration_source_ids`** — MCP expects `integration_source_ids`. `source_ids` is rejected.
- **Widget creation against a fresh group failing** — re-run `list-source-groups action=show` to verify `integration_source_id` exists and data has arrived before attaching widgets.
