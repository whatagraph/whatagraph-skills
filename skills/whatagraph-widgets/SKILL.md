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
list-widgets action=show report_id=<id> widget_id=<id>     # ids/layout/source binding only
list-widgets action=csv_export report_id=<id> widget_id=<id>
```

## Create a widget from scratch

```
manage-widgets action=create
   report_id=<id>
   tab_id=<tab_id>
   channel_id=<channel_id>
   widget_type_id=<widget_type>        # prefer 101+ (new architecture)
   source_id=<report_local_source_id>  # omit for sample-data widget
```

After creation, fill in configs via `manage-widgets action=update`.

### `source_id` — report-local sources only

`manage-widgets` validates `source_id` against the **sources already attached to the report** (the report-local `sources.id`, not the global `integration_sources.id`). Attach the source first via `manage-reports`:

1. `manage-reports action=attach_source report_id=<id> integration_source_id=<global_source_id>` — returns the report-local `source_id`.
2. `manage-widgets action=create ... source_id=<that report-local id>`.

Discover already-attached sources via `list-reports action=list_sources report_id=<id>`. Source groups and blends are themselves data sources — attach them the same way using their `id` from `list-source-groups` / `list-blends`.

### `widget_type_id` — widget types

Widget types are integers. Prefer the modern types (`101+`) unless you have a specific reason to use an older type. Common values exposed by `list-widgets`:

| Widget type | `widget_type_id` |
|---|---|
| Single value (KPI card) | `101` |
| Table | `102` |
| List | `103` |
| Column chart | `104` |
| Bar chart | `106` |
| Line chart | `107` |
| Pie chart | `108` |
| Donut chart | `109` |
| Funnel | `115` |
| Goal | `123` |
| Comment / text | `21` (channel_id `7` = Custom data; no `source_id` needed) |
| Image | `34` (channel_id `7`; no `source_id`) |
| Calendar / date control | `22` (channel_id `7`; no `source_id`) |
| Media expanded (creative preview) | `111` |

Comment, image, and calendar widgets are the only widget types that take `channel_id=7` and no `source_id`. Every data-bearing widget needs a `channel_id` matching the source's channel and a report-local `source_id`.

## Create a premade widget

Adds a template widget pre-configured by Whatagraph for the channel (common KPI sets, common chart shapes). Faster than building from scratch.

```
manage-widgets action=create_premade
   report_id=<id>
   tab_id=<tab_id>
   widget_id=<existing_widget_id>      # required
   source_id=<report_local_source_id>  # omit for sample-data premade
```

`create_premade` requires an existing `widget_id` that the premade configuration is applied to. Create a blank widget first with the right `channel_id` and `widget_type_id`, then call `create_premade` with that widget's id.

Same attach-first rule: the source must be attached to the report via `manage-reports action=attach_source` before referencing it here.

## Update a widget

```
manage-widgets action=update
   report_id=<id>
   widget_id=<id>
   name="October Spend"
   options={...}
   rows=[
     {
       "id": <existing_row_id>,
       "options": {...},
       "configs": [
         {
           "id": <existing_config_id>,
           "channel_id": <channel_id>,
           "source_id":  <report_local_source_id>,
           "report_type": {"external_id": "campaign"},
           "metric":    {"external_id": "universal_metric_3", "name": "Spend"},
           "dimension": {"external_id": "universal_dimension_1137", "name": "Date"}
         }
       ]
     }
   ]
   date_range={"from":"2025-10-01","till":"2025-10-31","period":"custom","compare_type":"previous"}
```

`id` on each row and on each existing config is required and must be an integer. To find them, call `list-widgets action=show widget_id=<id>` first; the response includes `rows[].id` and `rows[].configs[].id`. To add another row/config safely, duplicate an existing widget or create a new widget, then re-run `list-widgets action=show` after updates to discover the current `rows[].id` / `configs[].id` set.

### `rows` → `configs` shape

- Each widget has one or more rows.
- Each row has one or more configs.
- Each config pairs a metric with an optional dimension.
- Replace-style: supplied `rows` replace previous rows.

### `date_range`

Overrides the report-level date for this widget. Fields: `from`, `till`, `period`, `compare_type`. Omit to inherit report date.

### `options`

Per-widget settings — legend, labels, sort, hide_footer, currency override, etc. Structure varies by widget type. `list-widgets action=show` may not return every display option. When exact display settings matter, verify the rendered result with `list-widgets action=csv_export`, `export-report`, or the UI.

Known `options` shapes:

- **Comment / text widget** (`widget_type_id=21`): `{"text": "<html>", "comment": "<html>"}` — set both keys for best compatibility.
- **Image widget** (`widget_type_id=34`): `{"image_url": "<url>", "url": "<url>"}` — set both keys for best compatibility.
- **Single-value KPI** (`widget_type_id=101`): `{"compare_type": "previous_period"}` to surface the trend delta vs. the comparison window inherited from the report.

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
   report_id=<id> widget_ids=[...] source_id=<report_local_source_id>

manage-widgets action=batch_change_settings
   report_id=<id> widget_ids=[...]
   settings={"currency":"EUR","hide_footer":true}
```

`batch_change_source` requires the new source to already be attached to the report. Attach it first via `manage-reports action=attach_source`.

Use when swapping ~10+ widgets at once — much faster than per-widget updates.

## Sizing rules (12-column grid)

These guidelines describe the layout you should aim for in the **UI**, not arguments you can pass to `manage-widgets`. The `update` action accepts content/config fields such as `name`, `options`, `rows`, and `date_range`; positioning and sizing are adjusted in the UI after the data layer is configured.

- **KPI / single-value card** — 2×1 or 2×2 in the UI; never full width.
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
- **Passing a global `integration_sources.id` as `source_id`** — widgets only accept the report-local `sources.id`. Attach first via `manage-reports action=attach_source` and use the returned `source_id`.
- **`metrics=[]` as a top-level param** — wrong shape. Metrics live inside `rows[].configs[].metric`.
- **Passing plain metric strings in `configs`** — configs expect `{"metric": {"external_id": "..."}}` shape, not bare strings.
- **Batch operations without `widget_ids`** — the array is required. Empty array = no-op, not "all widgets".
- **Widget breaks after batch source swap** — the new source may not have the same report type or fields; always verify with `list-widgets action=show` after.
- **`metric.external_id` change appears to no-op** — when the widget already has a config bound to a metric on a source group / blend, re-supplying a different `metric.external_id` in the same config sometimes leaves the original metric in place. The `list-widgets action=show` response masks this (it only echoes channel + source ids, not the metric). Always confirm via `list-widgets action=csv_export` or `export-report` after a metric swap; if the CSV still shows the previous metric name, delete and recreate the widget rather than trying to update it in place.
- **Widget title differs from `name`** — `name` is saved on the widget record, but the title rendered in the report can be controlled by widget display options. Verify important titles in the UI.
- **`tab_id` missing on create** — required. Find via `list-report-tabs action=list`.
