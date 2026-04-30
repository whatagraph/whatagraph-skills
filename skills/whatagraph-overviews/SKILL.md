---
name: whatagraph-overviews
description: Create overviews — KPI dashboards that track metrics over time. The UI calls these "Measurements". Use when a user wants a single-page KPI dashboard with trend visualizations and comparisons, independent of any report.
---

# Overviews (Measurements)

Tools covered: `list-overviews`, `manage-overviews`.

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
| Cross-channel summary of 6–8 KPIs | Overview (with custom aggregation metrics for cross-channel KPIs) |

## Listing overviews

```
list-overviews action=list                          # paginated list
list-overviews action=show measurement_id=<id>      # full details
```

Note: the input parameter is `measurement_id`, not `overview_id`.

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
     {"external_id": "campaign_name", "name": "Campaign", "sort": "asc"}
   ]
   comparison_display_type="percentage"              # or "absolute", "combined"
```

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

## What MCP can't do here

- Update, duplicate, or delete an overview — UI only.
- Sharing — overviews inherit sharing from their space; share the space (UI) instead.
- Set a target value on an overview metric — use `whatagraph-goals` to track goals alongside.

## Common pitfalls

- **One source per overview** — each overview is bound to one source. For cross-channel KPIs, first create a custom metric of type `data_aggregation` or a blend (see `whatagraph-custom-metrics`, `whatagraph-blends`), then point the overview at that source.
- **Metric IDs as display names** — `external_id` must be the field ID from `list_dimensions_and_metrics`, not the display name.
- **Forgetting `report_type_external_id`** when the source has multiple report types — leads to missing data or an error.
- **Too many metrics** — 6–8 is readable; more makes the dashboard noisy.
- **Mixed-currency metrics** — overview does not auto-convert. Normalize via source-level currency override (`manage-sources action=set_currency`) before building the overview.
- **`measurement_id` vs `overview_id`** — tool parameters use `measurement_id`. The UI says "Measurement"; the tool name says "overview". Both refer to the same thing.
