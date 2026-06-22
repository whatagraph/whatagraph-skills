---
name: whatagraph-source-groups
type: domain
description: Combine multiple data sources into one virtual aggregated source — same-channel (e.g. five Google Ads sub-accounts) or cross-channel (e.g. Meta + Google + Reddit + TikTok). Use when an agency wants unified reporting without building a blend.
required_tools:
  - list-source-groups
  - list-sources
  - fetch-data
  - manage-reports
  - manage-source-groups
  - manage-widgets
---

# Source groups

Tools covered: `list-source-groups`, `manage-source-groups`.

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
| Sum of `spend` across Google + Meta into one total, no row-level join | Source group (cross-channel) |
| Google Ads + Meta Ads joined/matched on campaign name (side-by-side rows) | Blend |

**Rule**: source groups handle both same-channel and cross-channel aggregation and are simpler than blending — think of a source group as the templated, stored, auto-summarized version of a blend. Use a blend only when you need to **join** rows across channels on a shared dimension (e.g. matching campaign names between Google Ads and Meta Ads).

## Listing

```
list-source-groups action=list                       # paginated; supports search
list-source-groups action=show group_id=<id>         # sources, configs, currency
list-source-groups action=source_issues group_id=<id> # sources with disabled ETL
```

## Creating a source group

**Discover valid `output_name` values first** — they vary by channel and channel combination:

```
list-source-groups action=list_output_names source_ids=[<src1>, <src2>]
```

Premade output templates routinely come back with `name: null` — **`output_name` is the identifier; a null display name does NOT mean the entry is invalid** (verified Jun 2026). Pick the `output_name` matching the granularity you need, then create:

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
- `configs` — required. Each entry `{output_name: "<level>"}` where `<level>` is the granularity the group should expose: campaign performance, ad / ad-group performance, keyword performance, audience performance, geo performance, etc. Pick the level that matches the widgets you'll build on top — one config per level, and prefer one config per group (see "One config per group" below). The exact string is the **source-group template name** for that channel, *not* the channel-native report type external id you see in `list-sources action=list_report_types`. For most channels the template name is the report type with a `_performance` suffix — e.g. Google Ads `campaign` → `campaign_performance`, `ad_group` → `ad_group_performance`, `geo_view` → `geo_performance` — but Facebook Ads and others diverge (see the per-channel reference table below). Discover the valid set with `list-source-groups action=list_output_names source_ids=[...]`.
- `integration_source_ids` — array of source ids from `list-sources action=list`. Sources can be from the same channel or different channels (cross-channel aggregation is supported).
- `currency` — optional. Display currency.
- `configs[].dimensions` — optional. Array of `{external_id, name}` objects to select specific dimensions. When omitted, all template dimensions are used.
- `configs[].metrics` — optional. Array of `{external_id, name}` objects to select specific metrics. When omitted, all template metrics are used. Use `list-sources action=list_dimensions_and_metrics` with `is_universal=true` to discover valid universal field IDs.

> **Date dimension is auto-included.** Every source group config automatically includes the Date dimension (`universal_dimension_1137`). Do **not** pass it in the `dimensions` array — doing so creates a duplicate Date entry in the unified fields.

#### Per-channel `output_name` reference

Template names diverge across channels — Google Ads-flavoured names like `campaign_performance` are not portable. Verified examples:

| Channel | Valid `output_name` (verified) |
|---|---|
| Google Ads | `campaign_performance`, `ad_group_performance`, `keyword_performance`, `geo_performance`, … |
| Facebook Ads | `campaign_performance`, `ad_group_performance`, `ad_performance`, `creatives_performance`, `age_performance`, `gender_performance`, `geo_performance`, `device_performance` |
| LinkedIn Ads | `campaign_performance` |
| Snapchat | `campaign_performance` |
| GA4 | TBD — not exercised in QA |

Prefer `list-source-groups action=list_output_names source_ids=[...]` to discover the valid set for your exact sources. As a last resort only, a rejected `output_name` returns an error that enumerates every valid template name for that channel.

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

**Always edit a group with `update`, never delete-and-recreate.** A rebuild mints a **new** virtual `source_id`, which silently detaches every source-level custom metric, widget, and report binding that pointed at the old one. `update` preserves the group's virtual `source_id`, so dependents stay attached.

When a config supplies explicit `dimensions`/`metrics`, each field is attached only to the channels that actually expose it. Channel-native fields are skipped for channels that don't own them, and a `universal_*` (custom) field is attached only to the channels it actually maps to — the same applicability rule the UI uses to prune per-channel fields, **not** blanket-applied to every channel in the group. A custom field that maps to none of the group's channels is attached nowhere — so don't expect, say, a Facebook-only custom metric to show up on the Google columns of a cross-channel group; map it to those channels first. A cross-channel group won't break a channel by assigning it a field it can't fetch.

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

`resolve_issues` re-enables and **restarts the ETL transfer** on the sources you list. If one of those sources is **shared with other groups or reports**, restarting it re-syncs them too — they'll briefly show "downloading historical data" until the transfer catches up. Scope `integration_source_ids` to the sources that actually need it, and expect a transient re-sync on anything sharing them.

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

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: permanent (the virtual source is removed), widgets and custom metrics pointing at the group break, pre-check `list-source-groups action=show group_id=<id>`. To *change* a group, always use `update` — never delete-and-recreate (see above).

## What MCP can't do here

- Remove one sub-source from the group without providing the full replacement list — use `update` with the full new `integration_source_ids` list.

## Common pitfalls

- **Cross-channel `output_name` selection** — when mixing channels (e.g. Google Ads + Meta Ads + TikTok), use `list-source-groups action=list_output_names source_ids=[...]` to find template names that work across all supplied channels. Not every template is valid for every channel combination.
- **`output_name` is the source-group template name, not the channel-native report type** — e.g. `campaign_performance` for Google Ads, not `campaign`. The channel-native report type (`campaign`) is what you pass to `fetch-data` and `report_type_external_id` on the *original* sources, but the template name (`campaign_performance`) is what `manage-source-groups create configs` accepts. The two diverge on every paid-ads channel.
- **Editing a group? Use `update`, never delete+recreate** — a rebuild changes the virtual `source_id` and orphans source-level custom metrics and widget bindings.
- **`resolve_issues` on a shared source re-syncs other groups** — scope `integration_source_ids` narrowly and expect a transient re-download on anything sharing those sources.
- **Empty group after creation** — freshly-created groups need time for ETL to populate; data may be empty for a few minutes for small accounts, longer for high-volume ones.
- **Group not appearing in widget picker immediately** — refresh the report; new groups can take a few seconds to appear.
- **Very large groups (hundreds of sub-sources)** — query performance can slow down. For very large rollups, keep one config per group and split into focused groups by report type rather than one sprawling group.
- **Adding source groups can affect plan usage** — check the team's plan limits before bulk-creating groups.
- **`source_ids` vs `integration_source_ids`** — MCP expects `integration_source_ids`. `source_ids` is rejected.
- **Widget creation against a fresh group failing** — re-run `list-source-groups action=show` to verify `integration_source_id` exists and data has arrived before attaching widgets.
