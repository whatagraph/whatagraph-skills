---
name: whatagraph-source-groups
description: Combine multiple data sources of the SAME channel (e.g. five Google Ads sub-accounts) into one virtual aggregated source. Use when an agency manages many sub-accounts under one platform and wants unified reporting without building a blend.
---

# Source groups

Tools covered: `list-source-groups`, `manage-source-groups`.

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
   configs=[{"output_name": "campaign"}]
   integration_source_ids=[<src1>, <src2>, <src3>]
```

### Parameters

- `name` — group display name.
- `configs` — required. Each entry `{output_name: "<report_type_external_id>"}`. The output name is the channel's report type external id (e.g. `campaign` for Google Ads, not `campaign_performance`). One entry per report type you want the group to expose.
- `integration_source_ids` — array of source ids from `list-sources action=list`. All sources must be the same channel.
- `currency` — optional. Display currency.

## Multi-report-type source groups

If the channel has multiple report types and you want all of them, list one config per report type:

```
configs=[
  {"output_name": "campaign"},
  {"output_name": "keyword"},
  {"output_name": "ad_group"}
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
manage-source-groups action=source_issues group_id=<id>      # view affected sources
manage-source-groups action=resolve_issues group_id=<id>
   integration_source_ids=[<affected_source_ids>]
```

## Using the group in widgets

The group exposes its own integration source id (found via `list-source-groups action=show` as `integration_source_id`). Use that id as a widget's `source_id`. The group's metrics and dimensions are the union of what the sub-sources expose.

## What MCP can't do here

- Delete a source group — UI only.
- Remove one sub-source from the group without providing the full replacement list — use `update` with the full new `integration_source_ids` list.
- Change the channel of a group — not supported; create a new group.

## Common pitfalls

- **Mixing channels** — source groups require all sources from the SAME channel. Google Ads + Meta Ads → use a blend instead.
- **`output_name` is the native channel report type** — e.g. `campaign` for Google Ads. Custom metrics on top of the group use the group's exposed report type when referencing fields.
- **Empty group after creation** — freshly-created groups need time for ETL to populate; data may be empty for a few minutes for small accounts, longer for high-volume ones.
- **Group not appearing in widget picker immediately** — refresh the report; new groups sometimes cache-miss for a few seconds.
- **Very large groups (hundreds of sub-sources)** — query performance slows. The platform chunks queries for groups above a threshold. For very large rollups, consider a custom metric `data_aggregation` instead of a group.
- **Adding source groups consumes source credits** — each source in the group counts. Check plan headroom before bulk-creating.
- **`source_ids` vs `integration_source_ids`** — MCP expects `integration_source_ids`. `source_ids` is rejected.
- **Widget creation against a fresh group failing** — re-run `list-source-groups action=show` to verify `integration_source_id` exists and data has arrived before attaching widgets.
