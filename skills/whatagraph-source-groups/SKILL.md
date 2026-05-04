---
name: whatagraph-source-groups
description: Combine multiple data sources of the SAME channel (e.g. five Google Ads sub-accounts) into one virtual aggregated source. Use when an agency manages many sub-accounts under one platform and wants unified reporting without building a blend.
---

# Source groups

Tools covered: `list-source-groups`, `manage-source-groups`, `delete-source-groups`.

A **source group** aggregates multiple sources of the same channel (e.g. multiple Google Ads accounts) into one virtual source. The group gets its own integration source id that widgets, blends, and custom metrics can reference as if it were a single source.

## Use this when

- Agency has 3 Google Ads sub-accounts under one client MCC — roll up to one "Google Ads" source.
- Property manager has 20 GBP locations — one aggregated source for reporting.
- Franchise brand has multiple Meta ad accounts per region — one virtual source per brand.

## Source group vs blend vs custom metric

| Goal | Use |
|---|---|
| 5 Google Ads accounts → 1 virtual "Google Ads Total" | Source group |
| Google Ads + Meta Ads joined on campaign | Blend |
| Sum of `spend` across Google + Meta without joining | Custom metric `data_aggregation` |

**Rule**: if the sources share a channel, source group is cheaper and simpler than blending. If they don't share a channel, you must blend or aggregate via a custom metric.

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
- `configs` — required. Each entry `{output_name: "<source_group_template_name>"}`. The `output_name` is the **source-group template name**, not the channel-native report type external id you see in `list-sources action=list_report_types`. For most channels the template name is the report type with a `_performance` suffix — e.g. Google Ads `campaign` → `campaign_performance`, `ad_group` → `ad_group_performance`, `geo_view` → `geo_performance`. If the API rejects an `output_name`, the error message lists every valid template name for that channel — copy one from the error verbatim. One entry per template you want the group to expose.
- `integration_source_ids` — array of source ids from `list-sources action=list`. All sources must be the same channel.
- `currency` — optional. Display currency.

## One config per group (strongly recommended)

Build a source group with exactly **one** entry in `configs`. Multiple-config groups are legacy behaviour kept for backwards compatibility — every new group should expose a single, well-scoped report type that all widgets / blends / custom metrics point at. If the user needs campaign-level *and* keyword-level rollups from the same set of sources, build two separate source groups, one per report type. This keeps each group's virtual table small, the query path straightforward, and widgets/filters unambiguous about which report type they're operating on.

```
configs=[{"output_name": "campaign_performance"}]    # one config — preferred
```

The legacy "many report types in one group" pattern looked like this and should not be reused:

```
# LEGACY — do not use for new groups
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

Some sources in the group may have disabled ETL configs after errors. Re-enable them:

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
- **Field ids** use the unprefixed `universal_metric_*` / `universal_dimension_*` form on the group's virtual source. The platform aggregates sub-sources automatically (SUM for summable numerics, grouped by the selected dimensions).

## Deleting a source group

```
delete-source-groups action=delete group_id=<id>
```

Widgets and custom metrics that point at the group's virtual source will break. Run `list-source-groups action=show group_id=<id>` first and check usage; rebuild widgets to reference individual sources before deleting.

## What MCP can't do here

- Remove one sub-source from the group without providing the full replacement list — use `update` with the full new `integration_source_ids` list.
- Change the channel of a group — not supported; create a new group.

## Common pitfalls

- **Mixing channels** — source groups require all sources from the SAME channel. Google Ads + Meta Ads → use a blend instead.
- **`output_name` is the source-group template name, not the channel-native report type** — e.g. `campaign_performance` for Google Ads, not `campaign`. The channel-native report type (`campaign`) is what you pass to `fetch-data` and `report_type_external_id` on the *original* sources, but the template name (`campaign_performance`) is what `manage-source-groups create configs` accepts. The two diverge on every paid-ads channel.
- **Empty group after creation** — freshly-created groups need time for ETL to populate; data may be empty for a few minutes for small accounts, longer for high-volume ones.
- **Group not appearing in widget picker immediately** — refresh the report; new groups sometimes cache-miss for a few seconds.
- **Very large groups (hundreds of sub-sources)** — query performance slows. The platform chunks queries for groups above a threshold. For very large rollups, consider a custom metric `data_aggregation` instead of a group.
- **Adding source groups consumes source credits** — each source in the group counts. Check plan headroom before bulk-creating.
- **`source_ids` vs `integration_source_ids`** — MCP expects `integration_source_ids`. `source_ids` is rejected.
- **Widget creation against a fresh group failing** — re-run `list-source-groups action=show` to verify `integration_source_id` exists and data has arrived before attaching widgets.
