---
name: whatagraph-widgets
type: domain
description: Build and lay out widgets on the 6-column grid — KPI rows, chart pairings, full-width tables, comment narration, image dividers — and create, update, duplicate, or batch-modify them. Use when designing a report tab's layout, sizing and positioning widgets on the grid, replicating the layout of a reference report (PDF/screenshot/existing report), swapping metrics on an existing widget, or bulk-swapping data sources across many widgets at once.
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
list-widgets action=list report_id=<id>                    # grouped by tab, sorted by (position_y, position_x); each widget includes `has_filters` boolean and `widget_type_label` (human-readable)
list-widgets action=show report_id=<id> widget_id=<id>     # full widget details: layout, source binding, options, ai_text_settings, source_filter_off
list-widgets action=csv_export report_id=<id> widget_id=<id>
```

Notes:
- All actions include widgets on **hidden tabs** by default. Use `tab_hidden=false` to exclude hidden tabs, or `tab_hidden=true` to show only hidden tabs. The `list` response includes a `tab_hidden` field on each tab. `csv_export` defaults to visible tabs only (`tab_hidden=false`) — pass `tab_hidden=true` to export a widget on a hidden tab.
- `csv_export` requires the **Widget CSV Export** premium feature — throws an authorization error without it. When `data_status=warning`, the response includes `retry_after_seconds: 60`. Some widgets return `success: false` when the integration doesn't support export.

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

### Dimension requirements by widget type

The tool validates that the correct dimensions are provided based on the widget type. **Dimensions must be in `rows[].configs[].options.dimensions`** (data binding), not in row-level options (which are display labels only).

| Widget type | Dimension requirement |
|---|---|
| Time-series charts (104–107, 118–119) | **1 dimension required** — must be the integration's date dimension (e.g. `date`, `segments.date`, `ga:date`). Binding a non-date dimension while `breakdowns_enabled` is off is **rejected at create/update** (left unchecked it renders an empty/aggregated chart, and hard-errors on some sources such as Google Sheets). To split a bar/column chart by a category instead, set `breakdowns_enabled=true` (see Breakdown vs non-breakdown below) — then column/bar/stacked accept a categorical dimension (up to 2). |
| Table (102) | **At least 1 dimension required** — any dimension. |
| Heatmap (138) | **Exactly 2 dimensions required**. |
| GeoMap (140) | **1 geographic dimension required**. |
| Media (110, 111) | **At least 1 dimension required** — typically `creative_thumbnail_url` or similar. |
| Pie/Donut (108, 109) | **No dimension** unless `breakdowns_enabled=true` (then exactly 1). |
| SingleValue (101), Gauge (139), List (103), Funnel (115), Goal (123) | **No dimension needed**. |
| Comment (21), Calendar (22), Image (34) | **Skipped** — utility widgets with no data binding. |

Use `list-sources action=list_dimensions_and_metrics` to find the correct dimension external_ids for a source. The date dimension external_id varies by integration — always look it up rather than guessing.

> **A single value (101) always aggregates the whole dataset into one total** — it has no dimension and cannot rank or isolate a single entity. It will **not** show the "best" or "worst" campaign: a `sort` passed on its row/metric options is silently ignored (the tool returns a warning saying so). To surface a top/bottom performer, use a **Table (102)** with the entity dimension bound and the metric sorted desc/asc, or a saved filter (`whatagraph-filters`) pinning the specific entity.

**Time-series chart example** (area chart with date dimension):
```
manage-widgets action=create
   report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=105 source_id=<id>
   rows=[{"configs": [{"options": {"report_type": "campaign", "metrics": ["impressions"], "dimensions": ["segments.date"]}}]}]
```

**Table example** (with categorical dimension):
```
manage-widgets action=create
   report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=102 source_id=<id>
   rows=[{"configs": [{"options": {"report_type": "campaign", "metrics": ["impressions", "clicks"], "dimensions": ["campaign_name"]}}]}]
```

**SingleValue example** (no dimension needed):
```
manage-widgets action=create
   report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=101 source_id=<id>
   rows=[{"configs": [{"options": {"report_type": "campaign", "metrics": ["impressions"]}}]}]
```

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
| Media compact (creative preview) | `110` |
| Media expanded (creative preview) | `111` |
| Stacked bar chart | `118` |
| Stacked column chart | `119` |
| Heatmap | `138` |
| Gauge (dial-style single value) | `139` |
| GeoMap (geographic map, BETA) | `140` |
| Filter control (dimension dropdown) | `137` |

Comment, image, and calendar widgets are the only widget types that take `channel_id=7` and no `source_id`. Filter control (`137`) needs a `channel_id` and `source_id` but does not load data — it renders as a dimension dropdown that filters other widgets on the tab. Every other data-bearing widget needs a `channel_id` matching the source's channel and a report-local `source_id`.

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

**Linked reports**: `apply_premade` / `create_premade` is rejected on reports linked to a template (`linked_template_id` is set). Use `create` instead, or unlink the report first.

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

### Row-level `options` (chart widgets)

For multi-row chart widgets (Column, Line, Area, Bar), rows support additional options that control per-row rendering:

| Row option | Type | Notes |
|---|---|---|
| `type` | string | Chart series type for this row: `column`, `line`, `area`, `spline`, `splineArea`. Use to create mixed/combo charts (e.g. one row as column, another as line). |
| `axis` | `left` \| `right` | Which Y-axis this row binds to. **Set it on every row of a combined chart (column/line/area)** — use `left` unless you specifically want a dual-axis split. A row left without `axis` still binds its metric, but the widget editor groups rows onto the Left/Right axis by exact match, so an axis-less row shows on neither and the Edit panel looks empty. |
| `cumulative` | boolean | Show cumulative values for this row. |
| `trend_line` | string | Trend line type. |
| `trend_line_period` | integer | Trend line period. |
| `sort` | `asc` \| `desc` | Sort direction on this row's metric. |
| `icon` | string | Row icon (for List and SingleValue widgets). |

Example — mixed column + line chart:
```
rows=[
  {"options": {"type": "column", "axis": "left", "metrics": [...]}, "configs": [...]},
  {"options": {"type": "line", "axis": "right", "metrics": [...]}, "configs": [...]}
]
```

Example — cross-channel column chart (compare one metric across sources, no date dimension):
```
rows=[
  {"options": {"type": "column", "axis": "left", "title": "Source A", "metrics": [{"sort": 0, "identifier": 0, "external_id": "<metric>"}]},
   "configs": [{"source_id": <A>, "integration_id": <channel>, "options": {"metrics": [{"identifier": 0, "external_id": "<metric>"}], "report_type": "<rt>"}}]},
  {"options": {"type": "column", "axis": "left", "title": "Source B", "metrics": [{"sort": 0, "identifier": 0, "external_id": "<metric>"}]},
   "configs": [{"source_id": <B>, "integration_id": <channel>, "options": {"metrics": [{"identifier": 0, "external_id": "<metric>"}], "report_type": "<rt>"}}]}
]
```
> One row per source, each with a single config (its source) and the **same** metric, and **no** dimension — the sources become the columns. Set `axis: "left"` on every row; without it the editor's Left/Right axis sections render empty even though the data is bound.

### `rows` → `configs` shape

- Each widget has one or more rows.
- Each row has one or more configs.
- Each config pairs a metric with an optional dimension.
- Replace-style: supplied `rows` replace previous rows. Row metadata (`title`, `description`) from existing rows is preserved when the new row omits them.
- Each row carries **two parallel metric arrays** that must agree:
  - `rows[].options.metrics: [{sort, identifier, external_id}]` — drives the rendered label and the value the renderer prints.
  - `rows[].configs[].options.metrics: [{name, identifier, external_id}]` — drives the actual data binding.
  - Both must be set; mismatched values between the two cause the widget to render the row's label with the config's data. The same parallelism applies for dimensions: `rows[].options.dimensions` (rendered label) vs. `configs[].options.dimensions` (binding).
  - **The tool rejects updates where row-level metrics/dimensions are provided but the config has no matching `options.metrics`/`options.dimensions`.** Row-level fields are display labels only — the actual data binding lives in config options. If you get this error, move your metrics/dimensions into `rows[].configs[].options.metrics` (and `options.dimensions`).

### `date_range`

Overrides the report-level date for this widget. Fields: `from`, `till`, `period`, `compare_type`. Omit to inherit report date.

### `options`

Per-widget settings passed inside `options` on create/update. Structure varies by widget type. `list-widgets action=show` may not return every display option. When exact display settings matter, verify the rendered result with `list-widgets action=csv_export`, `export-report`, or the UI.

#### Display toggles

| Option | Type | Applies to |
|---|---|---|
| `hide_title` | boolean | Most data widgets (not SingleValue, Calendar, Comment, Image) |
| `hide_footer` | boolean | All data widgets |
| `hide_legend` | boolean | All chart types |
| `show_icons` | boolean | List, MediaCompact |
| `show_zebra_lines` | boolean | List, Table, Pie, Donut, Funnel |
| `show_list_row_numbers` | boolean | List |
| `show_totals` | boolean | Table (summary row) |
| `show_summary_column` | boolean | Table (only when column dimensions exist) |
| `show_chart_labels` | boolean | All chart types, Goal, Heatmap |
| `show_funnel_line_conversions` | boolean | Funnel (individual conversion rate) |
| `show_funnel_overall_conversions` | boolean | Funnel (total conversion rate) |
| `content_scrollable` | boolean | Table, Media (vertical scroll) |
| `content_horizontal_scrollable` | boolean | Table only |
| `display_dimensions_as_columns` | boolean | Table only |
| `wrap_text` | boolean | Table only |
| `show_search_bar` | boolean | Table, List (shows a row search box) |
| `active_theme_color_id` | integer | Any widget — overrides the theme color for this widget. Get available color IDs from the report's theme via `list-themes` |

#### Value formatting

| Option | Type | Applies to |
|---|---|---|
| `decimal_place` | integer 0–5 | Most data widgets |
| `currency` | string (e.g. `"USD"`) | Data widgets with currency metrics |
| `shorten_numbers` | boolean | SingleValue |
| `comparison_display_type` | `percentage` \| `absolute` \| `combined` | SingleValue, List, Table |
| `value_display_type` | `value` \| `percentage` \| `combined` | Pie, Donut |

#### Chart label settings (when `show_chart_labels` is true)

| Option | Type | Notes |
|---|---|---|
| `chart_label_position` | string | `top`, `bottom`, `left`, `right`, `insideTop`, `insideTopLeft`, `insideTopRight`, `insideBottom`, `insideBottomLeft`, `insideBottomRight`, `insideLeft`, `insideRight`. Default: `insideRight` for bar types, `top` for vertical charts |
| `chart_label_rotation` | `horizontal` \| `vertical` | |
| `chart_label_size` | integer | 10 (very small), 12 (small), 14 (medium), 16 (large) |
| `chart_label_distance` | integer 0–15 | |
| `chart_label_bg_enabled` | boolean | |
| `chart_label_bg_opacity` | integer 0–100 | Only when `chart_label_bg_enabled` is true |

#### Axis and grouping (charts)

| Option | Type | Notes |
|---|---|---|
| `histogram` | string | Data grouping: `auto`, `1 day`, `1 week`, `1 month`, `1 quarter`, `1 year` |
| `left_axis_value` | object | `{"from": <number>, "to": <number>}`. Set to `null` to reset to Auto |
| `right_axis_value` | object | Same shape; restricted when breakdown is on |

#### Text alignment (SingleValue only)

| Option | Type | Values |
|---|---|---|
| `vertical_text_alignment` | string | `start`, `center`, `end` |
| `horizontal_text_alignment` | string | `left`, `center`, `end` |

#### Type-specific options

| Option | Type | Widget type |
|---|---|---|
| `geo_map_region` | string | GeoMap (`140`). Values: `world`, `north-america`, `south-america`, `europe`, `asia`, `africa`, `oceania`, `emea`, `apac`, `latam`, `mena`, `noram`, `eu-eea`, `nordics`, `baltics`, `dach`, `benelux`, `iberia`, `uk-ireland`, `anz` |
| `goal_date_range` | object | Goal (`123`). `{"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "visible_time_line": true}` |

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
  - **Background image**: set `background_image_url` (public http/https URL) or `background_image_data` (base64-encoded JPG/PNG, max 10 MB) with optional `background_image_filename` in `rows[].options`. This adds a full-bleed background behind the comment text.
  - **Updating a comment widget with omitted row/config IDs now works.** `manage-widgets update` carries forward the existing config's `integration_id` (and `source_id` / `report_type`) when you omit it, so a comment-widget rows-update that leaves out `rows[].id` / `configs[].id` succeeds rather than erroring on a missing `integration_id`. Pre-fetching the IDs via `list-widgets action=show` (capture `rows[0].id` and `rows[0].configs[0].id` and pass them back) is still the cleanest way to update one specific row in place and avoid replacing the rows — but it is no longer required to avoid a failure.
- **Image widget** (`widget_type_id=34`): supply `{"image_url": "<url>"}` or `{"image_data": "<base64 JPG/PNG>"}` (max 10 MB) with optional `image_filename` in `rows[].options`. `image_data` accepts a base64-encoded image directly — no multipart upload needed. The tool auto-propagates this to the config-side canonical shape `configs[].options.images: [{url, title}]`. You can also supply the config shape directly in `rows[].configs[].options`. Additional display options: `background_size` (`auto_fit` | `scale_to_fit` | `scale_to_fill`) and `alignment` (`left` | `center` | `right`) — pass these in row options alongside `image_url`.
- **Single-value KPI** (`widget_type_id=101`): set `{"comparison_display_type": "combined"}` (or `"percentage"` / `"absolute"`) to surface the trend delta vs. the comparison window inherited from the report. `compare_type` is not a valid widget option key — it is a date-range field and the widget rejects it.
- **Funnel** (`widget_type_id=115`): each funnel **stage is its own row** with a single metric — one metric per row, in stage order. Putting multiple metrics in one config renders a single 100% stage instead of a multi-stage funnel.
- **Goal widget** (`widget_type_id=123`): set `options.goal_date_range` with `start_date`, `end_date`, and `visible_time_line` (boolean — controls the "Time passed" indicator line). Each row represents a goal line and requires `options.title` (goal name), `options.start_value` (baseline, typically 0), and `options.end_value` (target number). `end_value` must be greater than `start_value`. The metric in `configs[].options.metrics` tracks progress toward the target.
- **Filter control** (`widget_type_id=137`): bind a **dimension** (not a metric) via rows — the widget renders as a dropdown filter that other widgets on the tab respond to. No date range is needed. Does not load data itself.
- **Gauge** (`widget_type_id=139`): dial-style single metric display. Same configuration as SingleValue (`101`) but different visual rendering — use when a circular dial is more appropriate than a plain number. Supports `start_value` and `end_value` in row options to set the gauge range.
- **Heatmap** (`widget_type_id=138`): heat-colored grid showing metric values across time/dimension. Same configuration as SingleValue (`101`).
- **GeoMap** (`widget_type_id=140`, BETA): geographic map. Set `options.geo_map_region` to control the displayed region (see Type-specific options table above). Bind a dimension with country/region data.
- **Media / creative preview** (`widget_type_id=110`/`111`): bind the image dimension to the channel's **thumbnail** field — Meta/Facebook uses `creative_thumbnail_url` (not `ad_name`, which is text). Google Search ads are text-only (no thumbnail); `ad_image_url` populates only for Display/PMax/image ads.

## Breakdown vs non-breakdown (pie / donut / bar)

Breakdown is supported **only** on column (`104`), bar (`106`), stacked column (`119`), stacked bar (`118`), pie (`108`), and donut (`109`) charts — on every other widget type `breakdowns_enabled` is ignored.

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

## AI text on comment widgets

Configure AI-generated text (summary, wins, issues, recommendations, or a custom prompt) on a comment widget:

```
manage-widgets action=update_ai_text report_id=<id> widget_id=<id>
   ai_text={
     "types": ["summary"],          # summary | wins | issues | recommendations | custom (≥1 required)
     "load_type": "report_page",    # or "full_report" or "full_report_visible" (excludes hidden tabs)
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

Copies are packed into the next free grid slots and tile across the 6 columns, so duplicating a widget many times fills a clean grid. Duplicate a full row of widgets together (not one widget repeatedly) to keep the layout balanced.

When position is omitted, the copy is auto-placed at the next free grid slot — it does NOT land at the original widget's position. When an explicit position is given, the same overlap rules from the Layout grid model apply (`auto_place` behaviour). `batch_duplicate` always auto-places and tracks each copy's rect in-memory so subsequent copies tile alongside rather than stacking.

**Cross-tab duplication**:

Pass `target_tab_id=<tab_id>` to duplicate widgets to a different tab in the same report — no `manage-report-tabs` needed.

```
manage-widgets action=duplicate report_id=<id> widget_id=<id> target_tab_id=<tab_id>
manage-widgets action=batch_duplicate report_id=<id> widget_ids=[...] target_tab_id=<tab_id>
```

- The target tab must belong to the same report — cross-report duplication is not supported.
- The copy lands on the target tab's grid using the same positioning rules above (auto-placed by default, not at the original position).
- Data sources are carried over since both tabs share the same report's attached sources.

## Add / remove rows

Multi-row widgets (combo charts, funnels, non-breakdown pie/donut) have one row per series or stage. Use `add_row` and `remove_row` to manage them without rebuilding the entire `rows` array.

```
manage-widgets action=add_row    report_id=<id> widget_id=<id>
manage-widgets action=remove_row report_id=<id> widget_id=<id> row_id=<row_id>
```

- `add_row` copies the last row's config (integration, source, report type) into a new row. Update the new row's metric afterwards with a regular `update`.
- `remove_row` deletes the row and all its config children (metrics, dimensions, report types). Cannot remove the last remaining row.
- Find row IDs with `list-widgets action=show`.

## Batch operations

```
manage-widgets action=batch_change_source
   report_id=<id> widget_ids=[...] source_id=<report_local_source_id>

manage-widgets action=batch_change_settings
   report_id=<id> widget_ids=[...]
   settings={"currency":"EUR","hide_footer":true}

manage-widgets action=batch_change_date_range
   report_id=<id> widget_ids=[...]
   date_range={"from":"2025-01-01","till":"2025-03-31","period":"custom"}

manage-widgets action=batch_delete_date_range
   report_id=<id> widget_ids=[...]

manage-widgets action=batch_change_filter_visibility
   report_id=<id> widget_ids=[...] source_filter_off=true
```

`batch_change_source` accepts both global and report-local source IDs — auto-attaches if needed. The new source's channel must match the widgets' channel — cross-channel source swaps are rejected with an error naming the mismatched widgets. `batch_change_date_range` sets a widget-level date range override on all specified widgets. `batch_delete_date_range` removes date range overrides (widgets revert to the report date). `batch_change_filter_visibility` toggles `source_filter_off` across many widgets — set `true` to disable source-level filters, `false` to re-enable them.

Use when swapping ~10+ widgets at once — much faster than per-widget updates.

## Currency conversion

Convert money metrics on a widget to a different currency. Requires the Data Transformation premium feature.

```
list-widgets action=currency_exchange report_id=<id> widget_id=<id>
# → lists convertible money metrics with external_id, original_currency, exchange_currency

manage-widgets action=convert_currency report_id=<id> widget_id=<id>
   currency_conversions=[{"external_id": "<metric_external_id>", "exchange_currency": "USD"}]

manage-widgets action=restore_currency report_id=<id> widget_id=<id>
# → reverts all converted money metrics back to their original currency
```

Use `currency_exchange` first to discover which metrics are convertible and their current `external_id` (a converted metric's id becomes `universal_metric_*`).

## Layout grid model

The report uses a **6-column grid**. Every widget occupies a rectangle defined by four properties:

| Property | Range | Default | Notes |
|---|---|---|---|
| `position_x` | 0..5 | 0 | Horizontal column (0-based). Must satisfy `position_x + width ≤ 6`. |
| `position_y` | 0..∞ | next row below existing widgets | Vertical row (0-based, no upper limit). |
| `options.width` | 1..6 | 2 | Width in grid columns. |
| `options.height` | ≥1 | 2 | Height in grid rows. |

> **Input/output asymmetry:** On **input** (create/update), pass `width` and `height` inside `options`. On **output**, they appear as **top-level** fields (`width`, `height`). When using `fields` filtering, use the top-level names: `fields="width,height"` — not `options.width`.

**Overlap rule:** On `create`, `update`, and `duplicate`, the server rejects widgets that overlap an existing widget — unless `auto_place=true`, which picks the nearest free slot instead. On `create`, when `position_x`/`position_y` are omitted entirely, auto-placement is the default. On `update`, overlap is checked when `position_x` or `position_y` is provided (the widget being updated is excluded from the check). `duplicate` and `batch_duplicate` auto-position the copy at the next available row.

### The layout comes from the data and the user, not from a default

**There is no house layout, and no default report structure.** The tab's shape is decided fresh each time, in this order of priority:

1. **A reference was provided** — a PDF, screenshot, live-report URL, or an existing report → **replicate its structure** (see "Replicating a reference report"). Don't normalize it to a layout you prefer.
2. **The user described what they want** → build to that intent: the metrics, breakdowns, and emphasis they asked for.
3. **No reference and no specific ask** → *you* decide what's worth showing and how. This is a judgment call, not a fallback skeleton: look at the data that's actually available (which metrics, which dimensions), pick the most meaningful KPIs, choose the best visualization for each (see below), and arrange them in a sensible information hierarchy. Different sources and metrics should produce different reports — if every report you build looks the same, you've defaulted to a template.

Sizing and positioning (further down) only make *whatever you chose* render cleanly — they are not a recipe for what to build.

### Choosing a visualization for each metric / dimension

When you're deciding what to show — case 3 above, or filling gaps in a loose request — match each piece of data to the visualization that fits its shape. Let the data pick the widget, not habit:

- **A headline total / the single most important number** → SingleValue KPI (Gauge for a dial feel; Goal when there's a target to pace against).
- **A metric over time (trend)** → Line or Area chart — bind the date dimension.
- **A metric split by a category, as share of a whole** → Donut or Pie (breakdown).
- **Comparing one metric across categories** → Bar or Column chart.
- **A detailed, multi-metric breakdown by a dimension (rankings, "top X")** → Table — the workhorse when a dimension has many values and several metrics matter.
- **Sequential steps / a conversion path** → Funnel.
- **A geographic dimension** → GeoMap.
- **Ad / creative performance with thumbnails** → Media.
- **Narration or context** → a Comment (AI-text comment for an auto summary) — only when it adds value.

Compose by analytical priority: surface the few numbers that matter most first, then the main trend, then the breakdowns and detail. But the **selection, mix, and count** of widgets follow from what the data supports — so they vary from report to report. Don't force a fixed set or a minimum count.

### Sizing — driven by content, not a fixed table

Pick each widget's size from what its content needs to be legible, then fit it into the row you're building. These are affordances, not defaults:

- **KPI / SingleValue / Gauge / Goal** — just a number; keep it small so several share a row. A full-row single value reads as a header.
- **Table / MultiSource / Heatmap** — needs width or columns truncate; usually most or all of the row, taller as rows grow.
- **Line / Area / time-series chart** — needs width for the trend to be legible (often the full row). Also needs its **date dimension** bound (see "Dimension requirements") or it collapses to a single value.
- **Bar / Column chart** — compact when paired with a sibling, full-width when it's the focus.
- **Pie / Donut** — roughly square; a full-row pie wastes space.
- **List / Funnel** — narrow-to-medium; sit well beside a chart.
- **Media / creative preview** — one tile per creative, grouped across a row.
- **Comment** — full-row as a section header/divider, or taller for an AI text block. **Size the height to the text it holds:** `height: 1` fits only a single short heading line; a sentence or two needs `height: 2`; a full paragraph `height: 3`; a multi-paragraph AI summary `4+`. Under-sizing clips or overflows the text in the rendered report, so when in doubt give it more height — and prefer splitting a long block across widgets (or trimming the copy) over cramming it into a short box.
- **GeoMap** — medium.

**Hard constraints (always):** `width` 1..6, `height` ≥ 1, `position_x + width ≤ 6`, and no two widgets overlap.

### Placing widgets cleanly

Once you know the structure, lay it out top to bottom:

1. **Work in rows.** Each row's widths sum to ≤ 6. Track the running `y` — a row of height-2 widgets at `y=0` means the next row starts at `y=2`.
2. **Set `position_x` / `position_y` / `width` / `height` explicitly** on every widget so rows land where you intend. `auto_place=true` (the default when you omit position) just drops a widget in the next free slot — fine for a one-off add, not for a designed or replicated layout.
3. **Pack to match your intent** — no gaps and no overlaps, but mirror the *reference's* density: don't tighten a deliberately sparse page, don't pad a dense one.
4. **Build, then verify** with `export-report` (or `list-widgets action=csv_export`) — confirm the layout and that every widget loaded data. `list-widgets action=show` echoes positions but not rendered data.

### Replicating a reference report (the priority when one is given)

Reproduce the reference faithfully — do not substitute a default arrangement:

- **Recreate every element**, in the same top-to-bottom order — KPIs, charts, tables, funnels, ad/creative tiles (Media `110` / `111`), comments/text. Don't drop or invent widgets.
- **Match per-row counts and proportions.** Count how many widgets share each row and split the 6 columns to mirror their relative widths: 3 across ⇒ `width 2` each; 2 across ⇒ `width 3` each; one full-width ⇒ `6`; an uneven pair (wide chart + narrow KPI) ⇒ e.g. `4 + 2`.
- **Match the widget type to what's shown** — a donut stays a donut, a funnel stays a funnel; don't swap in your preferred type.
- **Preserve spacing and density** — same sequence, and leave an empty row where the reference shows a gap.
- **Ignore account / source names** printed on the reference (e.g. "Account: …") — that's metadata, not a filter.

### Examples — illustrations of range, NOT templates

Different requests produce different shapes. **Copy the user's intent or reference — never copy these.** They exist only to show that the structure should vary:

- **Dense paid-media page (varied, many widgets):** a `6×1` header comment; a row of three KPIs `2×2`; a donut `3×3` beside a table `3×3`; a full-width detail table `6×3`; a row of three ad creatives `2×3`. (Coordinates for this one shape: comment `x0 y0 6×1`; KPIs `x0/x2/x4 y1 2×2`; donut `x0 y3 3×3` + table `x3 y3 3×3`; table `x0 y6 6×3`; media `x0/x2/x4 y9 2×3`.)
- **Lean summary (sparse, few widgets):** three KPIs `2×2` across the top, then one full-width trend chart `6×3`. Nothing more — don't pad it out.
- **Exec narrative (text-led):** an AI-summary comment `6×3` at the top, then two supporting visuals `3×3 + 3×3`.
- **Uneven split:** a wide trend chart `4×3` beside a tall KPI list `2×3`.

If your output looks like the same example every time, you've defaulted to a template — go back to the user's request or reference.

## Filtering a widget

There are three ways to filter a widget. Pick the simplest one that fits:

**Option 1 — Create directly on the target** (recommended):
```
# Filter one widget config
manage-filters action=create channel_id=<id> dimension="campaign.name" dimension_operator="contain_dimension" value="brand" name="Branded" widget_config_id=<config id>

# Filter all widgets on a source
manage-filters action=create channel_id=<id> dimension="campaign.name" dimension_operator="contain_dimension" value="brand" name="Branded" source_id=<source id>
```
One call, no orphaned team filter, no attach step. The channel must match the target's channel. Replaces any existing filter on that target. Cannot pass both `widget_config_id` and `source_id`.

**Option 2 — Inline `filter_id` on `manage-widgets`** (use when a team-level filter already exists):
```
manage-widgets action=create|update ... rows=[{configs: [{filter_id: <team filter id>}]}]
```
Pass `filter_id` in `rows[].configs[]` to attach an existing team-level filter. Pass `filter_id: null` to detach. The filter's channel must match the config's channel.

**Option 3 — Two-step create + attach** (use when attaching the same filter to multiple targets):
```
manage-filters action=create channel_id=<id> dimension="campaign.name" dimension_operator="contain_dimension" value="brand" name="Branded"
manage-filters action=attach filter_id=<new id> widget_config_id=<config id>
```

### Filter precedence

A widget applies **one** filter, not both:
- If a **widget_config filter** exists, it is used.
- Otherwise, if the config's **source** has a filter, that source filter is used.
- Widget-config filters always take priority over source-level filters.

> **Avoid source-level filters unless explicitly requested.** A source filter applies to **every widget using that source across all reports** — not just the current report. It can also cause errors when the filter references a dimension or metric that doesn't exist in every report type the source's widgets use. Default to `widget_config_id` for per-widget filtering. Only use `source_id` when the user specifically wants all data from that source filtered (e.g. "I only want US data from this source").

`list-widgets action=show` returns all filters in `inline_filters` with a `scope` field (`widget_config` or `source`) and a `team_available` boolean. Filters with `team_available: false` are config-scoped — they won't appear in `list-filters action=list` (which only shows team-level filters). Only one scope applies at runtime per the precedence above.

Other notes:
- `source_filter_off` (a `manage-widgets` `create`/`update` parameter) only **toggles** existing source-level filters on/off for the widget — it does not author them.
- Passing `filters`, `filter`, or `inline_filters` on `manage-widgets` is rejected — use `filter_id` or the `manage-filters` tool instead.

Load `whatagraph-filters` for the full operator list and row-group (AND/OR) semantics.

## Deleting widgets

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: soft-delete with a `restore` action, batch via `batch_delete`, idempotent on already-deleted widgets. Note that delete-and-recreate is the documented workaround when a metric `external_id` update no-ops (see Common pitfalls).

## What MCP can't do here

- Move widgets to another tab — use `manage-report-tabs action=move_widgets`.
- Set widget-level permissions — UI only.
- Cross-report widget copy — duplicate within the same report only (use `target_tab_id` for cross-tab duplication).
- **Edit the generated AI text itself** — `update_ai_text` configures the settings and triggers generation, but the produced text can only be hand-edited in the UI.

## Idempotency

`create`, `apply_premade`, and `create_premade` accept an optional `idempotency_key` (a client-generated UUID). If a timeout or network error leaves the result uncertain, resend the same call with the same key — the original result is returned instead of creating a duplicate. Use a fresh key for each distinct operation.

## Common pitfalls

- **Date dimension ambiguity** — a source may expose more than one date-typed dimension (e.g. `universal_dimension_1137` "Date" and `universal_dimension_150` "Date OLD"). Prefer the plainly-named current one and verify with `csv_export`. This is integration-dependent.
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
- **Widget `name` vs row-level `title`** — `name` sets `options.title`, the heading above the chart/table. `rows[].options.title` labels individual data rows (metric name in a KPI, series name in a chart legend). To rename the visible metric label, update `rows[].options.title`, not `name`.
- **Duplicate metric/dimension bindings** — binding the same `external_id` twice in one config is silently de-duplicated (keeps first occurrence). A warning is returned, but the widget ends up with one series, not two. To chart two series of the same metric, use separate rows.
- **`tab_id` missing on create** — required. Find via `list-report-tabs action=list`.
- **`sort` warning on single-value widgets** — the "`sort` has no effect" warning only fires for row-level `sort` (a data-sort directive). The `sort` field inside `rows[].options.metrics[]` is a positional ordinal index required by the dual-array pattern — it does not trigger the warning.
- **AI text (`update_ai_text`) errors** — if generation fails with a timeout, the settings are saved; retry after ~30 seconds. A non-timeout error may indicate the AI feature is not available on the team's plan.
