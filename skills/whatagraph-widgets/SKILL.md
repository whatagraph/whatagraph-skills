---
name: whatagraph-widgets
description: Create, update, duplicate, and batch-modify widgets on report tabs. Widgets are the visual data components — charts, tables, KPI cards, funnels, goals, maps, images, text. Use when building a report page, swapping metrics on an existing widget, or bulk-swapping data sources across many widgets at once.
---

# Widgets

Tools covered: `list-widgets`, `manage-widgets`, `delete-widgets`.

A **widget** is a visual data component on a tab. Widgets are typed (KPI card, line chart, table, pie chart, etc.) and each has a data source (or no source for comment/image widgets). Widgets expose rows and configs — a row groups metrics and dimensions; configs define the data.

## Use this when

- Adding a KPI card, chart, table, or funnel to a tab.
- Swapping the source on a set of widgets (migrating from sample to real data).
- Changing common settings (currency, footer visibility) across many widgets at once.
- Duplicating a widget or a set of widgets on a tab.

## Listing

```
list-widgets action=list report_id=<id>                    # grouped by tab
list-widgets action=show report_id=<id> widget_id=<id>     # full config
list-widgets action=csv_export report_id=<id> widget_id=<id>
```

## Create a widget from scratch

```
manage-widgets action=create
   report_id=<id>
   tab_id=<tab_id>
   channel_id=<channel_id>
   widget_type_id=<widget_type>        # prefer 101+ (new architecture)
   source_id=<integration_source_id>   # omit for sample-data widget
```

After creation, fill in configs via `manage-widgets action=update`.

### `widget_type_id` — widget types

Widget types are integers. Higher values (101+) use the newer widget architecture with richer configs — prefer these unless you have a specific reason to use an older type. Common types:
- KPI / single-value card
- Line / area / column / bar chart
- Pie / donut chart
- Table
- Funnel
- Goal
- Map / geo
- Image / creative
- Comment / text

Discover exact ids by creating one in the UI and inspecting via `list-widgets action=show`.

## Create a premade widget

Adds a template widget pre-configured by Whatagraph for the channel (common KPI sets, common chart shapes). Faster than building from scratch.

```
manage-widgets action=create_premade
   report_id=<id>
   tab_id=<tab_id>
   source_id=<integration_source_id>   # omit for sample-data premade
```

## Update a widget

```
manage-widgets action=update
   report_id=<id>
   widget_id=<id>
   name="October Spend"
   options={...}
   rows=[
     {
       "id": <row_id_or_null>,
       "options": {...},
       "configs": [
         {
           "metric":    {"external_id": "universal_metric_3", "name": "Spend"},
           "dimension": {"external_id": "campaign_name"}
         }
       ]
     }
   ]
   date_range={"from":"2025-10-01","till":"2025-10-31","period":"custom","compare_type":"previous"}
```

### `rows` → `configs` shape

- Each widget has one or more rows.
- Each row has one or more configs.
- Each config pairs a metric with an optional dimension.
- Replace-style: supplied `rows` replace previous rows.

### `date_range`

Overrides the report-level date for this widget. Fields: `from`, `till`, `period`, `compare_type`. Omit to inherit report date.

### `options`

Per-widget settings — legend, labels, sort, hide_footer, currency override, etc. Structure varies by widget type. Inspect an existing widget via `list-widgets action=show` to see valid keys.

## Toggle breakdown on pie / donut / bar

```
manage-widgets action=toggle_breakdown report_id=<id> widget_id=<id>
```

## Duplicate

```
manage-widgets action=duplicate   report_id=<id> widget_id=<id>
manage-widgets action=batch_duplicate report_id=<id> widget_ids=[<id1>, <id2>, <id3>]
```

## Batch operations

```
manage-widgets action=batch_change_source
   report_id=<id> widget_ids=[...] source_id=<new_source_id>

manage-widgets action=batch_change_settings
   report_id=<id> widget_ids=[...]
   settings={"currency":"EUR","hide_footer":true}
```

Use when swapping ~10+ widgets at once — much faster than per-widget updates.

## Sizing rules (12-column grid)

- **KPI / single-value card** — defaults to 2×1 or 2×2, not full width. Full-width single-value widgets look like headers, not metrics.
- **Line / column chart** — 6×3 minimum readable; 12-wide for trend emphasis.
- **Table** — full width (12×N); narrower tables truncate columns.
- **Pie / donut** — 4×4 or 6×4; full-width pies waste space.
- **Goal** — 3×2 to 4×3; matches KPI card sizing.
- **Comment / image** — 12×small for section headers; 4–6 wide for sidebar callouts.

## Deleting widgets

```
delete-widgets action=delete       report_id=<id> widget_id=<id>
delete-widgets action=batch_delete report_id=<id> widget_ids=[<id>, <id>, <id>]
delete-widgets action=restore      report_id=<id> widget_id=<id>   # undo a soft-delete
```

Deletes are soft — a restore window exists. After a second delete or report-level cleanup, they become permanent. Confirm with the user before deleting widgets that have unique configs (formulas, custom filters) that aren't easily recreated.

## What MCP can't do here

- Move widgets to another tab — use `manage-report-tabs action=move_widgets`.
- Set widget-level permissions — UI only.
- Cross-report widget copy — duplicate within report only.

## Common pitfalls

- **Full-width single-value widgets** — looks like a section header; use 2×2 or 2×1 instead.
- **Table summary row sums percentages** — the footer sums percent columns as numbers (25% + 30% = 55%); disable footer for percent-heavy tables.
- **Updating metrics on a widget that uses a source group** — after the group's sources change, the widget may need to re-save to pick up field definitions. Verify via `list-widgets action=show`.
- **Creating without `channel_id`** — required at create time; channel_id = the source's channel.
- **Creating without `widget_type_id`** — required; verify via existing widgets on the tab.
- **`metrics=[]` as a top-level param** — wrong shape. Metrics live inside `rows[].configs[].metric`.
- **Passing plain metric strings in `configs`** — configs expect `{"metric": {"external_id": "..."}}` shape, not bare strings.
- **Batch operations without `widget_ids`** — the array is required. Empty array = no-op, not "all widgets".
- **Widget breaks after batch source swap** — the new source may not have the same report type or fields; always verify with `list-widgets action=show` after.
- **`tab_id` missing on create** — required. Find via `list-report-tabs action=list`.
