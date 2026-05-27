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
| Area chart | `105` |
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

The MCP tool reads metrics from `configs[].options.metrics` (array of objects or strings) and dimensions from `configs[].options.dimensions`. A singular `metric` / `dimension` string is also accepted and auto-wrapped. Do **not** use the internal storage keys `integration-metrics` or `integration-levels` — the tool does not read those and the binding will be silently empty.

```
manage-widgets action=update
   report_id=<id>
   widget_id=<id>
   name="October Spend"
   options={...}
   rows=[
     {
       "options": {
         "metrics": [
           {"sort": 0, "identifier": 0, "external_id": "universal_metric_3"}
         ]
       },
       "configs": [
         {
           "integration_id": <channel_id>,
           "source_id":      <report_local_source_id>,
           "options": {
             "metrics":    [{"name": "Spend",  "identifier": 0, "external_id": "universal_metric_3"}],
             "dimensions": [{"name": "Date",   "identifier": 0, "external_id": "universal_dimension_1137"}],
             "report_type": "campaign"
           }
         }
       ]
     }
   ]
   date_range={"from":"2025-10-01","till":"2025-10-31","period":"custom","compare_type":"previous"}
```

To find the current shape on an existing widget, call `list-widgets action=show widget_id=<id>` first; the response shows `rows[].id`, `rows[].configs[].id`, and the populated `options` arrays. When you pass row/config `id` fields, the platform updates that row/config in place. For the cleanest binding, omit `rows[].id` and `configs[].id` — the platform replaces the rows from scratch, which is the only path that reliably persists a fresh metric/dimension binding (see callout below).

> **Binding metrics on a fresh widget is currently unreliable via `manage-widgets update`.** When a config still carries its original `id`, supplying a new `metrics` payload sometimes leaves the previously bound metric in place — `list-widgets action=show` masks this because it echoes channel + source ids only, not the bound metric. Workarounds:
>
> 1. Omit the row's `id` and the config's `id` so the platform re-creates the rows from scratch and applies the new `options.metrics`. Note this also creates a new report-local source mapping (see Common pitfalls).
> 2. After the update, verify with `list-widgets action=csv_export` or `export-report` — if the CSV still shows the previous metric, delete and recreate the widget rather than trying to update it in place.
> 3. On widgets pointed at a **virtual source** (blend / source group), the renderer may still ignore the bind even with the storage shape — finishing the configuration in the UI is currently required for those.

### `rows` → `configs` shape

- Each widget has one or more rows.
- Each row has one or more configs.
- Each config pairs a metric with an optional dimension.
- Replace-style: supplied `rows` replace previous rows.
- Each row carries **two parallel metric arrays** that must agree:
  - `rows[].options.metrics: [{sort, identifier, external_id}]` — drives the rendered label and the value the renderer prints.
  - `rows[].configs[].options.metrics: [{name, identifier, external_id}]` — drives the actual data binding.
  - Both must be set; mismatched values between the two cause the widget to render the row's label with the config's data. The same parallelism applies for dimensions: `rows[].options.dimensions` (rendered label) vs. `configs[].options.dimensions` (binding).

### `date_range`

Overrides the report-level date for this widget. Fields: `from`, `till`, `period`, `compare_type`. Omit to inherit report date.

### `options`

Per-widget settings — legend, labels, sort, hide_footer, currency override, etc. Structure varies by widget type. `list-widgets action=show` may not return every display option. When exact display settings matter, verify the rendered result with `list-widgets action=csv_export`, `export-report`, or the UI.

Known `options` shapes:

- **Comment / text widget** (`widget_type_id=21`): on **write**, supply `{"comment_widget_text": {"text": "Hello\nWorld", "contentAlign": "top"}}` — `text` is a plain string, the platform converts it. The legacy `{"text": "<html>", "comment": "<html>"}` shape also works for older accounts.
  - On **read**, `list-widgets action=show` returns the converted Tiptap document under `options.comment_widget_text.description` (a `{type: "doc", content: [...]}` tree). Do **not** round-trip the `description` shape on write — re-send the flat `text` string instead, otherwise the platform will refuse the payload or persist an empty comment.
  - **Always pre-fetch the existing row and config IDs before updating a comment widget.** Run `list-widgets action=show widget_id=<id>` and capture `rows[0].id` and `rows[0].configs[0].id`, then pass both back in the `manage-widgets update` call. Omitting `id` on rows/configs of a comment widget triggers an INSERT path that fails with `SQLSTATE[23000]: Column 'integration_id' cannot be null` because the comment row's `integration_id` is implicit on the existing record but missing on a fresh insert. The "omit ids to rebuild from scratch" guidance in the metric-binding callout applies only to **data-bearing** widgets, not to comment / image / calendar widgets.
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

## Sizing rules (6-column report grid)

These guidelines describe the layout you should aim for in the **UI**, not arguments you can pass to `manage-widgets`. The `update` action accepts content/config fields such as `name`, `options`, `rows`, and `date_range`; positioning and sizing are adjusted in the UI after the data layer is configured.

The default Whatagraph report grid is **6 columns wide** — `manage-widgets` defaults `options.width` to `6`, and observed widgets across real reports stay within `width=1..6`.

- **KPI / single-value card** — 2×1 or 2×2 in the UI; never full row. Three KPIs across a row = `2×1 × 3`.
- **Line / column chart** — 4×3 minimum readable; 6-wide (full row) for trend emphasis. A common chart row is `4×3 + 2×3` (chart + side KPI/legend).
- **Table** — full width (6×N); narrower tables truncate columns.
- **Pie / donut** — 2×2 or 3×3; full-row pies waste space.
- **Goal** — 2×2 to 3×2; matches KPI card sizing.
- **Comment / image** — 6×small for section headers; 2–3 wide for sidebar callouts.

If a customer's account uses a wider grid, inspect an existing widget on a real report via `list-widgets action=list` and use the largest observed `options.width` as the row width before sizing new widgets.

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
- **`metrics=[]` as a top-level param** — wrong shape. Metrics live inside `rows[].options.metrics` (row label) and `rows[].configs[].options.metrics` (data binding).
- **Using `integration-metrics` / `integration-levels` in config options** — the MCP tool does not read those internal storage keys. Use `metrics` and `dimensions` instead.
- **Batch operations without `widget_ids`** — the array is required. Empty array = no-op, not "all widgets".
- **Widget breaks after batch source swap** — the new source may not have the same report type or fields; always verify with `list-widgets action=show` after.
- **`metric.external_id` change appears to no-op** — when the widget already has a config bound to a metric on a source group / blend, re-supplying a different `metric.external_id` in the same config sometimes leaves the original metric in place. The `list-widgets action=show` response masks this (it only echoes channel + source ids, not the metric). Always confirm via `list-widgets action=csv_export` or `export-report` after a metric swap; if the CSV still shows the previous metric name, delete and recreate the widget rather than trying to update it in place.
- **Widget title differs from `name`** — `name` is saved on the widget record, but the title rendered in the report can be controlled by widget display options. Verify important titles in the UI.
- **`tab_id` missing on create** — required. Find via `list-report-tabs action=list`.
