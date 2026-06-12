---
name: whatagraph-widgets
description: Build and lay out widgets on the 6-column grid — KPI rows, chart pairings, full-width tables, comment narration, image dividers — and create, update, duplicate, or batch-modify them. Use when designing a report tab's layout, positioning widgets on the grid, swapping metrics on an existing widget, or bulk-swapping data sources across many widgets at once.
required_tools:
  - list-blends
  - list-report-tabs
  - list-reports
  - list-source-groups
  - list-sources
  - list-widgets
  - export-report
  - manage-report-tabs
  - manage-widgets
---

# Widgets

Tools covered: `list-widgets`, `manage-widgets`.

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
   channel_id=<channel_id>             # integer ID or slug, e.g. 5 or "google-ads"
   widget_type_id=<widget_type>        # prefer 101+ (new architecture)
   source_id=<report_local_source_id>  # omit for sample-data widget
```

You can pass `rows` at create time to bind metrics and dimensions immediately — no separate update needed. If `rows` is omitted, the widget defaults to the first metric in the source catalog.

### `source_id` — global or report-local

`source_id` accepts either a **global** source `id` from `list-sources` or a **report-local** `source_id` from `list-widgets` / `list-reports action=list_sources`. When a global ID is passed, the tool auto-attaches it to the report — no separate `attach_source` step is needed.

Discover already-attached sources via `list-reports action=list_sources report_id=<id>`. Source groups and blends are themselves data sources — use their `id` from `list-source-groups` / `list-blends`.

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

## Apply a premade widget

Adds a template widget pre-configured by Whatagraph for the channel (common KPI sets, common chart shapes). Faster than building from scratch. Discover premade IDs first — `list_premade` requires a `channel_id` (integer or slug):

```
list-widgets action=list_premade channel_id=<id>   # or slug, e.g. "google-ads"

manage-widgets action=apply_premade                # alias: create_premade
   report_id=<id>
   tab_id=<tab_id>
   widget_id=<premade_widget_id>                   # from list_premade — NOT an existing report widget
   source_id=<report_local_source_id>              # omit for sample-data premade
```

`widget_id` here is the **premade's ID** from `list-widgets action=list_premade`, not a widget you created. A source whose channel doesn't match the premade's channel is rejected (verified Jun 2026) — scope `list_premade` to the source's own channel. Supports `position_x`/`position_y` and `options` (width, height). Same auto-attach rule applies: pass a global or report-local `source_id`.

## Update a widget

Supply metrics on `configs[].options.metrics` (array of objects or strings; singular `metric` is auto-wrapped). On write, the platform converts your `metrics` / `dimensions` payload to its internal storage shape `integration-metrics` / `integration-dimensions`, and `list-widgets action=show` will echo those keys back. That's expected — read paths return `integration-metrics`, write paths accept `metrics`. Do not hand-craft `integration-metrics` on input; supply `metrics` and let the platform convert.

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
- Replace-style: supplied `rows` replace previous rows. Row metadata (`title`, `description`) from existing rows is preserved when the new row omits them.
- Each row carries **two parallel metric arrays** that must agree:
  - `rows[].options.metrics: [{sort, identifier, external_id}]` — drives the rendered label and the value the renderer prints.
  - `rows[].configs[].options.metrics: [{name, identifier, external_id}]` — drives the actual data binding.
  - Both must be set; mismatched values between the two cause the widget to render the row's label with the config's data. The same parallelism applies for dimensions: `rows[].options.dimensions` (rendered label) vs. `configs[].options.dimensions` (binding).

### `date_range`

Overrides the report-level date for this widget. Fields: `from`, `till`, `period`, `compare_type`. Omit to inherit report date.

### `options`

Per-widget settings — legend, labels, sort, hide_footer, currency override, etc. Structure varies by widget type. `list-widgets action=show` may not return every display option. When exact display settings matter, verify the rendered result with `list-widgets action=csv_export`, `export-report`, or the UI.

Known `options` shapes:

- **Comment / text widget** (`widget_type_id=21`): on **write**, supply `{"comment_widget_text": {"text": "Hello\nWorld", "contentAlign": "top"}}` in `rows[].options` — `text` is a plain string, the platform converts it. The tool auto-propagates this to `configs[].options.comment_widget_text.text`. The legacy `{"text": "<html>", "comment": "<html>"}` shape also works for older accounts.
  - **Three formatting layers** — supply `text` OR `description` inside `comment_widget_text`, never both (verified Jun 2026):
    1. Plain `text` string → paragraphs.
    2. `text` with **markdown** → headings, bold, italic, lists, links (converted to a Tiptap document on save).
    3. A prebuilt **Tiptap doc** via `description` → `textStyle` marks (`color`, `fontSize`), `textAlign` attrs, `underline`, `highlight`, `link`. This is the **only** path to text colour, font size, and alignment — markdown has no syntax for them. The doc persists intact through update and round-trips through `list-widgets action=show`.

    ```
    "comment_widget_text": {
      "description": {
        "type": "doc",
        "content": [{
          "type": "paragraph",
          "attrs": {"textAlign": "center"},
          "content": [{
            "type": "text",
            "text": "Q2 Revenue",
            "marks": [{"type": "textStyle", "attrs": {"color": "#1A73E8", "fontSize": "24px"}}]
          }]
        }]
      },
      "contentAlign": "top"
    }
    ```
  - On **read**, `list-widgets action=show` returns the Tiptap document under `options.comment_widget_text.description`. A text/font **colour** baked into the comment content overrides the theme's `text_color` (CSS specificity), so applying a palette won't recolour comment text — set the colour via a `textStyle` mark for white-on-dark headers, or leave it uncoloured to inherit the theme.
  - **Always pre-fetch the existing row and config IDs before updating a comment widget.** Run `list-widgets action=show widget_id=<id>` and capture `rows[0].id` and `rows[0].configs[0].id`, then pass both back in the `manage-widgets update` call. Omitting `id` on rows/configs of a comment widget triggers an INSERT path that fails with `SQLSTATE[23000]: Column 'integration_id' cannot be null` because the comment row's `integration_id` is implicit on the existing record but missing on a fresh insert. The "omit ids to rebuild from scratch" guidance in the metric-binding callout applies only to **data-bearing** widgets, not to comment / image / calendar widgets.
- **Image widget** (`widget_type_id=34`): supply `{"image_url": "<url>", "url": "<url>"}` in `rows[].options`. The tool auto-propagates this to the config-side canonical shape `configs[].options.images: [{url, title}]`. You can also supply the config shape directly in `rows[].configs[].options`.
- **Single-value KPI** (`widget_type_id=101`): `{"compare_type": "previous_period"}` to surface the trend delta vs. the comparison window inherited from the report.
- **Funnel** (`widget_type_id=115`): each funnel **stage is its own row** with a single metric — one metric per row, in stage order. Putting multiple metrics in one config renders a single 100% stage instead of a multi-stage funnel.
- **Media / creative preview** (`widget_type_id=110`/`111`): bind the image dimension to the channel's **thumbnail** field — Meta/Facebook uses `creative_thumbnail_url` (not `ad_name`, which is text). Google Search ads are text-only (no thumbnail); `ad_image_url` populates only for Display/PMax/image ads.

## Breakdown vs non-breakdown (pie / donut / bar)

Breakdown is supported **only** on column (`104`), bar (`106`), pie (`108`), and donut (`109`) charts — on every other widget type `breakdowns_enabled` is ignored.

> **Time-series charts are different.** On area (`105`) and line (`107`) charts the X-axis is always the date — a categorical dimension bound on its own renders an **empty chart**. To split a time series by a category (e.g. clicks per campaign over time), bind the dimension AND set `options.breakdowns_enabled: true`; for a share-of-total view, use a breakdown donut/pie instead.

Pie, donut, bar, and column charts have two distinct modes that determine how slices/segments are generated:

**Breakdown mode** (`breakdowns_enabled: true`) — a single row with one metric and one dimension. The dimension values drive the slices (e.g. "clicks by ad group name"). Do not add multiple rows. Always set `breakdowns_show: true` when `breakdowns_enabled` is `true`.

```
manage-widgets action=create
   report_id=<id>
   tab_id=<tab_id>
   channel_id=<channel_id>
   widget_type_id=109                    # donut, pie, bar, column
   source_id=<report_local_source_id>
   options={"width": 4, "height": 3, "breakdowns_enabled": true, "breakdowns_show": true}
   rows=[
     {
       "options": {"title": "Clicks", "metrics": [...], "dimensions": [...]},
       "configs": [{"options": {"metrics": [...], "dimensions": [...], "report_type": "..."}}]
     }
   ]
```

**Non-breakdown mode** (`breakdowns_enabled: false`) — multiple rows, each with a different metric and **no dimensions**. Each row becomes a slice (e.g. "impressions vs clicks"). Set `breakdowns_show: true` to allow users to toggle breakdown on in the UI.

```
manage-widgets action=create
   report_id=<id>
   tab_id=<tab_id>
   channel_id=<channel_id>
   widget_type_id=109
   source_id=<report_local_source_id>
   options={"width": 4, "height": 3, "breakdowns_enabled": false, "breakdowns_show": true}
   rows=[
     {
       "options": {"title": "Impressions", "metrics": [...]},
       "configs": [{"options": {"metrics": [...], "report_type": "..."}}]
     },
     {
       "options": {"title": "Clicks", "metrics": [...]},
       "configs": [{"options": {"metrics": [...], "report_type": "..."}}]
     }
   ]
```

| | Breakdown | Non-breakdown |
|---|---|---|
| Slices driven by | Dimension values | Multiple metric rows |
| Rows | 1 row: 1 metric + 1 dimension | N rows: 1 metric each, no dimensions |
| `breakdowns_enabled` | `true` | `false` |
| Use case | "Show clicks split by ad group" | "Compare impressions vs clicks" |

### Toggle breakdown (use with caution)

```
manage-widgets action=toggle_breakdown report_id=<id> widget_id=<id>
```

> **Warning:** `toggle_breakdown` **deletes all existing rows** and reinitializes them from the integration's default template. Any custom metric, dimension, or report type bindings are lost and replaced with defaults. Only use this on widgets with default configs. For widgets with custom bindings, set `breakdowns_enabled` via `options` at create time or via `manage-widgets action=update` instead. (One of the destructive modes catalogued in `whatagraph-deleting`.)

## AI text on comment widgets

Configure AI-generated text (summary, wins, issues, recommendations, or a custom prompt) on a comment widget:

```
manage-widgets action=update_ai_text report_id=<id> widget_id=<id>
   ai_text={
     "types": ["summary"],          # summary | wins | issues | recommendations | custom (≥1 required)
     "load_type": "report_page",    # or "full_report"
     "language": "English",
     "summary_length": "short",     # or "long"
     "custom_prompt": "...",        # required when types includes "custom"
     "auto_update": false           # false triggers immediate generation; true regenerates automatically
   }
```

Only comment widgets (`widget_type_id=21`) are supported. Unless `auto_update` is `true`, the call also triggers an immediate summary generation.

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

`batch_change_source` accepts both global and report-local source IDs — auto-attaches if needed.

Use when swapping ~10+ widgets at once — much faster than per-widget updates.

## Layout grid model

The report uses a **6-column grid**. Every widget occupies a rectangle defined by four properties:

| Property | Range | Default | Notes |
|---|---|---|---|
| `position_x` | 0..5 | 0 | Horizontal column (0-based). Must satisfy `position_x + width ≤ 6`. |
| `position_y` | 0..∞ | next row below existing widgets | Vertical row (0-based, no upper limit). |
| `options.width` | 1..6 | 2 | Width in grid columns. |
| `options.height` | ≥1 | 2 | Height in grid rows. |

> **Input/output asymmetry:** On **input** (create/update), pass `width` and `height` inside `options`. On **output**, they appear as **top-level** fields (`width`, `height`). When using `fields` filtering, use the top-level names: `fields="width,height"` — not `options.width`.

**Overlap rule:** On `create`, the server rejects widgets that overlap an existing widget at the same `(x, y, width, height)` rectangle — unless `auto_place=true`, which picks the nearest free slot instead (the response then carries `auto_placed: true` with the chosen position). When `position_x`/`position_y` are omitted entirely, auto-placement is the default. `duplicate` and `batch_duplicate` auto-position the copy at the next available row.

### Sizing guidelines

- **KPI / single-value card** — 2×1 or 2×2; never full row. Three KPIs across = `2×1 × 3`.
- **Line / column chart** — 4×3 minimum readable; 6-wide (full row) for trend emphasis. Common: `4×3 + 2×3` (chart + side KPI).
- **Table** — full width (6×N); narrower tables truncate columns.
- **Pie / donut** — 2×2 or 3×3; full-row pies waste space.
- **Goal** — 2×2 to 3×2; matches KPI card sizing.
- **Comment / image** — 6×1 for section headers; 2–3 wide for sidebar callouts.

## Deleting widgets

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: soft-delete with a `restore` action, batch via `batch_delete`, idempotent on already-deleted widgets. Note that delete-and-recreate is the documented workaround when a metric `external_id` update no-ops (see Common pitfalls).

## What MCP can't do here

- Move widgets to another tab — use `manage-report-tabs action=move_widgets`.
- Set widget-level permissions — UI only.
- Cross-report widget copy — duplicate within report only.
- **Edit the generated AI text itself** — `update_ai_text` configures the settings and triggers generation, but the produced text can only be hand-edited in the UI.

## Common pitfalls

- **Full-width single-value widgets** — looks like a section header; use 2×2 or 2×1 instead.
- **Table summary row sums percentages** — the footer sums percent columns as numbers (25% + 30% = 55%); disable footer for percent-heavy tables.
- **Updating metrics on a widget that uses a source group** — after the group's sources change, the widget may need to re-save to pick up field definitions. Verify via `list-widgets action=show`.
- **Metric-only update drops the binding ("Unavailable report type")** — when updating a config in place, always carry its `integration_id`, `source_id`, and `report_type` alongside the new `metrics`/`dimensions`. Omitting them on a source-group or report-type-bound widget can rebuild the config without its report-type binding and leave the widget blank. Prefer name/position-only edits on those widgets, and verify data with `csv_export` after any metric change.
- **Creating without `channel_id`** — required at create time; channel_id = the source's channel.
- **Creating without `widget_type_id`** — required; verify via existing widgets on the tab.
- **Passing an invalid `source_id`** — the tool accepts both global and report-local IDs, but will error if the ID doesn't exist. Use `list-sources` or `list-reports action=list_sources` to find valid IDs.
- **`metrics=[]` as a top-level param** — wrong shape. Metrics live inside `rows[].options.metrics` (row label) and `rows[].configs[].options.metrics` (data binding).
- **Hand-crafting `integration-metrics` / `integration-dimensions` on input** — supply `metrics` and `dimensions` instead; the platform converts to the internal storage keys automatically. `list-widgets action=show` echoes the internal keys back — that's expected, not an error.
- **Batch operations without `widget_ids`** — the array is required. Empty array = no-op, not "all widgets".
- **Widget breaks after batch source swap** — the new source may not have the same report type or fields; always verify with `list-widgets action=show` after.
- **`metric.external_id` change appears to no-op** — when the widget already has a config bound to a metric on a source group / blend, re-supplying a different `metric.external_id` in the same config sometimes leaves the original metric in place. The `list-widgets action=show` response masks this (it only echoes channel + source ids, not the metric). Always confirm via `list-widgets action=csv_export` or `export-report` after a metric swap; if the CSV still shows the previous metric name, delete and recreate the widget rather than trying to update it in place.
- **Widget title differs from `name`** — `name` is saved on the widget record, but the title rendered in the report can be controlled by widget display options. Verify important titles in the UI.
- **`tab_id` missing on create** — required. Find via `list-report-tabs action=list`.
