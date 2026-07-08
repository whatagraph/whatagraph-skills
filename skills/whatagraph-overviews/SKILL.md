---
name: whatagraph-overviews
type: domain
description: Create overviews — KPI dashboards that track metrics over time. The UI calls these "Measurements". Use when a user wants a single-page KPI dashboard with trend visualizations and comparisons, independent of any report.
required_tools:
  - list-overviews
  - list-sources
  - manage-overviews
  - manage-sources
  - delete-overviews
---

# Overviews (Measurements)

Tools covered: `list-overviews`, `manage-overviews`, `delete-overviews`.

An **overview** (UI name: "Measurement") is a KPI dashboard that tracks selected metrics over time with trend/column/heatmap visualizations and comparison framing. Overviews live at the team level and can optionally be associated with a space.

## Use this when

- Executive KPI dashboard for a client (6–8 metrics, trend view).
- Daily performance check-in for an in-house team.
- At-a-glance KPI tracker with comparison to previous period.
- Complement to a detailed report — overview for summary, report for deep-dive.

## Overview vs report — quick decision

| You want… | Use |
|---|---|
| One-page KPI dashboard with trend arrows and sparklines | Overview |
| Multi-tab detailed breakdown with many widgets and filters | Report |
| Cross-channel summary of 6–8 KPIs | Overview pointed at a cross-channel source group or blend |

## Listing overviews

```
list-overviews action=list                          # paginated list
list-overviews action=list search="Acme"            # filter by name
list-overviews action=show overview_id=<id>          # full details
```

Pagination: cursor-based with `cursor` parameter; `per_page` up to 500 (default 100).

## Creating an overview

```
manage-overviews action=create
   name="Acme — Executive Dashboard"
   source_id=<integration_source_id>
   report_type_external_id="campaign"               # if source has multiple report types
   space_id=<space_id>                              # optional
   metrics=[
     {
       "external_id": "universal_metric_3",
       "name": "Total Spend",
       "visualize": "graph",
       "sort": "desc"
     },
     {
       "external_id": "universal_metric_10",
       "name": "Conversions",
       "visualize": "column"
     }
   ]
   dimensions=[
     {"external_id": "campaign.name", "name": "Campaign", "sort": "asc"}
   ]
   comparison_display_type="percentage"              # or "absolute", "combined"
```

> The `external_id` values shown above (`universal_metric_3`, `campaign.name`) are channel-specific. Always look up the actual id for your source via `list-sources action=list_dimensions_and_metrics` — Google Ads native fields use dot notation (`campaign.name`, `metrics.clicks`), source groups use `universal_*` prefixes, and blends use `aggregation_*` prefixes. See `whatagraph-sources-and-data` for the field-id family table.

### `metrics` structure

Each metric entry:
- `external_id` (required) — from `list-sources action=list_dimensions_and_metrics`.
- `name` (optional) — display name, auto-filled if omitted.
- `visualize` — `graph`, `heatmap`, or `column`.
- `sort` — `asc` / `desc`.
- `sort_type` — `change` or `value`.
- `width` — column width.

### `dimensions` structure

Optional. Same shape as metrics but no `visualize`/`sort_type`.

### `comparison_display_type`

Default `percentage`. Values: `percentage`, `absolute`, `combined`.

## Updating an overview

`update` supports **partial updates** — only supply the fields you want to change. Omitted fields keep their current values.

```
# rename only
manage-overviews action=update overview_id=<id> name="New Name"

# replace metrics, keep everything else
manage-overviews action=update overview_id=<id> metrics=[...]

# full replacement (all fields supplied)
manage-overviews action=update overview_id=<id>
   name="..." source_id=<id> metrics=[...] dimensions=[...]
```

When `metrics` or `dimensions` are supplied, they **fully replace** the existing set — partial metric lists are not merged. Passing a different `space_id` moves the overview; omitting it leaves it in place.

## Deleting an overview

```
delete-overviews action=delete overview_id=<id>
```

Permanent — no restore path. See `whatagraph-deleting` for cascades and recovery context.

## What MCP can't do here

- Duplicate an overview — UI only (use `action=update` to modify an existing one).
- Sharing — overviews inherit sharing from their space; share the space (UI) instead.
- Set a target value on an overview metric — use `whatagraph-goals` to track goals alongside.

## Common pitfalls

- **One source per overview** — each overview is bound to one source. For cross-channel KPIs, first build a cross-channel source group or a blend (see `whatagraph-source-groups`, `whatagraph-blends`), then point the overview at that virtual source.
- **Metric IDs as display names** — `external_id` must be the field ID from `list_dimensions_and_metrics`, not the display name.
- **Forgetting `report_type_external_id`** when the source has multiple report types — leads to missing data or an error.
- **Too many metrics** — 6–8 is readable; more makes the dashboard noisy.
- **Mixed-currency metrics** — overview does not auto-convert. Normalize via source-level currency override (`manage-sources action=set_currency`) before building the overview.
- **`overview_id`** — all overview tools now use `overview_id` consistently (list, show, update, delete).
