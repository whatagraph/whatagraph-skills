---
name: whatagraph-widgets
type: domain
group: report_building
description: Create, read, update, batch-modify and position widgets on a report tab. Covers binding metrics and dimensions, widget types, comment and image widgets (HTML text, AI text, background images), the 6-column grid with sizing and placement rules, row icons, sorting, breakdown charts, widget filters, offline (manual-data) values, and batch source, settings and date-range changes. Use for any widget write and for reading widgets back. Also the widget reference for a report built from numbers you already have (load `whatagraph-offline-reports` for that workflow). Load `whatagraph-tab-layout` as well before building or laying out a full tab or replicating a reference report, and `whatagraph-widget-advanced` for formula rows, duplicating, conditional formatting, currency conversion or table column widths.
required_tools:
  - list-widgets
  - list-reports
  - list-report-tabs
  - list-sources
  - manage-widgets
optional_tools:
  - tool_name: list-blends
    purpose: Resolve a blend's id when binding a blend as the widget's source.
  - tool_name: list-source-groups
    purpose: Resolve a source group's id when binding a group as the widget's source.
  - tool_name: manage-report-tabs
    purpose: Move widgets to another tab, or open and close rows on a tab.
  - tool_name: manage-filters
    purpose: Create or attach a filter on a widget config.
  - tool_name: list-filters
    purpose: Find an existing team-level filter to attach inline.
  - tool_name: list-themes
    purpose: Look up theme colour ids for active_theme_color_id.
  - tool_name: export-report
    purpose: Render the built layout to PDF for a person to check.
  - tool_name: manage-assets
    purpose: Import and publish a remote image before binding it to a widget.
  - tool_name: view-creatives
    purpose: Look at the actual ad-creative images a media widget pulls, to QA creatives after building.
  - tool_name: preview-report
    purpose: Look at the built layout to verify text fits and every table's last row is present.
---

# Widgets

Tools covered: `list-widgets`, `manage-widgets`.

A **widget** is a visual data component on a tab. Widgets are typed (KPI card, line chart, table, pie chart, etc.) and each has a data source (or no source for comment and image widgets). A widget has rows, and each row has configs: the row holds display settings, the configs bind the data.

**Load another playbook as well when the task needs it:**

- **`whatagraph-tab-layout`**: before you build or lay out a full tab, build a report from an open or partly specified request, or replicate a reference report. It decides what goes on the page (visualization choice, titles, section headers, narrative comments, the full-page composition bar). A named tab is a full page, not a slot for one or two widgets.
- **`whatagraph-widget-advanced`**: for formula rows, duplicating widgets (also to another tab), conditional formatting, currency conversion, or table column widths.

## Use this when

- Adding, editing or removing a KPI card, chart, table, funnel, comment or image on a tab.
- Reading widgets back: their bindings, layout, text or settings.
- Entering numbers by hand (offline spend, retainer fees, client targets) into an offline widget.
- Swapping the source, settings or date range on many widgets at once.

## A `warnings` entry blocks the next step

> ⚠️ **Read `warnings` on every `manage-widgets` response, and fix what it names before you move on.** The response still says `success: true`, because the widget row was written, but a warning means part of what you sent was stored where nothing reads it. The widget on the report does not match the call you think succeeded.

A warning that was read and skipped has already shipped a widget showing "Metrics not selected" to a client report. So when `warnings` is not empty:

1. Read each entry. Each one names the field it dropped and the field it belongs in.
2. Re-send the call with the binding moved, or send an `update` that fixes the widget.
3. Only then build the next widget.

Never keep a warning to report at the end of the run. Hard errors are different: an error means nothing was written, so correct the shape and send the same call again.

## Listing

```
list-widgets action=list report_id=<id>                    # grouped by tab, sorted by (position_y, position_x); each widget has `has_filters` and `widget_type_label`
list-widgets action=show report_id=<id> widget_id=<id>     # full details: layout, source binding, options, ai_text_settings, source_filter_off
list-widgets action=csv_export report_id=<id> widget_id=<id>
list-widgets action=list_icons                             # the row icon library, see "Row icons"
```

- All actions include widgets on **hidden tabs** by default. `tab_hidden=false` excludes them, `tab_hidden=true` shows only them. `list` returns `tab_hidden` on each tab. `csv_export` defaults to visible tabs only; pass `tab_hidden=true` to export a widget on a hidden tab.
- `csv_export` needs the **Widget CSV Export** premium feature (an authorization error without it). With `data_status=warning` the response has `retry_after_seconds: 60`. Some integrations do not support export and return `success: false`.
- ⚠️ **Do not edit a field back just because `show` returned it.** `show` repeats the metric's name in `rows[].options.title` and in `rows[].configs[].options.metrics[].name`. Only the config one is the caption the reader sees (see "Renaming a metric caption").

## Create a widget from scratch

```
manage-widgets action=create
   report_id=<id>
   tab_id=<tab_id>                     # required; find with list-report-tabs action=list
   channel_id=<channel_id>             # required; integer or slug, e.g. 5 or "google-ads"; the source's channel
   widget_type_id=<widget_type>        # required; 101+ (current generation)
   source_id=<report_local_source_id>  # omit for a sample-data widget
   name="<widget title>"               # always set on data widgets
```

- **Always pass `name` on data widgets.** Without it the widget shows the platform's default label. Set each row's metric label at the same time, in `rows[].configs[].options.metrics[].name`.
- ⚠️ **Four types reject `name` and `options.title`**: Comment (`21`), Calendar (`22`), Filter control (`137`) and Report shortcut (`141`). They render no title, so a value is refused (also in `batch_change_settings`). Put a Comment's heading in its HTML body (`<h2>…</h2>` in `comment_widget_text.text`). Image (`34`) renders a title and takes `name`.
- **On SingleValue (`101`), List (`103`) or Offline SingleValue (`125`), pass `rows[].options.icon` in the same call.** Without it every card gets the same eye icon (see "Row icons").
- **Always pass `rows` at create on data widgets.** Without `rows` the widget binds the first metric in the source catalog (an arbitrary field that rarely matches the title), and on some sources nothing at all, so it renders **"Metrics not selected"**. A create that returns `success` with no explicit binding is not a configured widget. Look the fields up with `list-sources action=list_dimensions_and_metrics` (never guess an `external_id`), keep every field in one config on the same `report_type` (a mix gives "Unavailable report type" or a blank widget), and verify that data loads with `export-report` or `list-widgets action=csv_export`.

### A create with no binding is refused

A `create` on a data widget type is **rejected** when it would leave the widget with no source and no metrics. The error names the two fields that bind data: a top-level `source_id`, or `rows[].configs[].source_id` plus `rows[].configs[].options.metrics`. Nothing is written; fix the shape and send the call again.

Only `rows[].configs[].options.metrics` counts as a binding. A `metrics` array at row level is a display label: rows with row-level metrics, no configs and no `source_id` anywhere are refused as unbound. Row-level metrics with no matching config metrics are rejected by a second guard too (see "`rows` → `configs` shape").

Outside the check:

- **`rows` omitted entirely** gives a blank widget, reported as `is_sample_data`. Still not a configured widget.
- **A source bound with no metrics** is the default-metric flow. It stays a warning, and you should act on it: the default is an arbitrary catalog field.
- **Utility and offline types**: Comment (`21`), Calendar (`22`), Image (`34`), Report shortcut (`141`), Filter control (`137`) and the offline types (`125`–`136`) render their own content.

The check runs on `create` only. An `update` that strips a binding is not refused, so read `warnings` on updates.

A row sent with a `title` and **no `configs` array** warns as well: the row gets a placeholder config with nothing bound, and the widget renders the source's default metric, not the one the title claims. Check the key spelling and re-send the row with its config.

### Bindings written one level too high

A row's `options` is a free-form blob. A source or metrics written there are stored and bind nothing, because only `rows[].configs[].options` binds data. Six keys are a **hard validation error** at row level, on create and update:

`configs`, `source_id`, `source`, `sources`, `integration_id`, `channel_id`

The error names the row index and points at `rows[].configs[].source_id` and `rows[].configs[].options.metrics`. Two related keys:

- **`filters`** is rejected by its own guard (see "Filtering a widget").
- **`operators`** is a real key: it makes the row a formula row (see `whatagraph-widget-advanced`).

Any other unknown row option key is a warning, which you must act on. A widget carrying a stray key from an earlier write stays editable.

### Dimension requirements by widget type

**Dimensions bind in `rows[].configs[].options.dimensions`**, not in row-level options (display labels only). Both ends of each range are enforced at create and update: too few and too many are both refused.

| Widget type | Dimension requirement |
|---|---|
| Time-series charts (104–107, 118–119) | **1 dimension, the integration's date dimension** (e.g. `date`, `segments.date`, `ga:date`). A non-date dimension with `breakdowns_enabled` off is **rejected** (it would render an empty or aggregated chart, and errors on some sources such as Google Sheets). To split a bar or column chart by a category, set `breakdowns_enabled=true` (see "Breakdown vs non-breakdown"); column, bar and stacked then accept a categorical dimension (up to 2). |
| Table (102) | **At least 1 dimension**, any dimension. The channel's creative dimension also draws the ad image in each row (`whatagraph-widget-advanced` → "Ad creative thumbnails in a table"). |
| Heatmap (138) | **Exactly 2 categorical dimensions.** A calendar heatmap is a different chart: Dynamic chart (142). |
| GeoMap (140) | **1 geographic dimension.** |
| Media (110, 111) | **At least 1 dimension**, typically `creative_thumbnail_url` or similar. |
| Pie/Donut (108, 109) | **No dimension** unless `breakdowns_enabled=true` (then exactly 1). |
| SingleValue (101), Gauge (139), List (103), Funnel (115), Goal (123) | **No dimension**; binding one is rejected. |
| Comment (21), Calendar (22), Image (34) | Skipped: no data binding. |

**Metric counts are capped too.** Every data type takes **exactly 1 metric per config**, List (`103`) and the charts included. Exceptions: Table (`102`) and Media expanded (`111`) take any number, Media compact (`110`) at most 2, and offline types bind nothing. To show a second metric on a capped type, add a second row (non-breakdown mode) or use a Table.

The date dimension's `external_id` varies by integration: look it up with `list-sources action=list_dimensions_and_metrics`. Some sources expose more than one date dimension (e.g. "Date" and "Date OLD"); prefer the plainly named current one and verify with `csv_export`.

> **A SingleValue (101) always aggregates the whole dataset into one total.** It cannot rank or isolate one entity, so it will not show the "best" or "worst" campaign, and a `sort` on it is ignored (with a warning). For a top or bottom performer use a **Table (102)** with the entity dimension bound and the metric sorted, or a saved filter (`whatagraph-filters`) that pins the entity.

### Surfacing a top / bottom N

"Top 10 campaigns" and "worst-performing ads" need **an entity dimension bound and the metric sorted**, on a type that shows many rows (Table `102`, List `103`, or a bar or column chart).

- **Sort** the ranking metric `desc` (top) or `asc` (bottom) (see "Sorting a widget").
- **Limit the rows** another way: `manage-widgets` has **no** row-count or limit parameter on Table, List or bar/column widgets. Use a `whatagraph-filters` condition, or size the widget height to show N rows and rely on the sort. Do not invent a limit parameter.
- **Verify** the leading rows and order with `export-report` or `list-widgets action=csv_export`.

**Examples:**

```
# Area chart over time (date dimension)
manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=105 source_id=<id>
   name="Impressions Over Time"
   rows=[{"options": {"title": "Impressions"},
          "configs": [{"options": {"report_type": "campaign", "metrics": ["impressions"], "dimensions": ["segments.date"]}}]}]

# Table (categorical dimension)
manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=102 source_id=<id>
   name="Campaign Performance"
   rows=[{"options": {"title": "Campaign Performance"},
          "configs": [{"options": {"report_type": "campaign", "metrics": ["impressions", "clicks"], "dimensions": ["campaign_name"]}}]}]

# SingleValue (no dimension)
manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=101 source_id=<id>
   name="Total Impressions"
   rows=[{"options": {"title": "Impressions", "icon": "<icon from list_icons>"},
          "configs": [{"options": {"report_type": "campaign", "metrics": ["impressions"]}}]}]
```

### `source_id`: global or report-local

`source_id` accepts a **global** source `id` from `list-sources` or a **report-local** `source_id` from `list-widgets` / `list-reports action=list_sources`. A global id is attached to the report automatically. An id that does not exist is an error. Source groups and blends are sources too: use their `id` from `list-source-groups` / `list-blends`.

### `widget_type_id`: widget types

`manage-widgets` writes current-generation types only: `101+`, their offline counterparts, and the comment, image and calendar utility types. Older types are rejected on create **and** update, including multi-source table (`37`): combine sources in a blend or source group and bind it to a table (`102`).

| Widget type | `widget_type_id` |
|---|---|
| Single value (KPI card) | `101` |
| Table | `102` |
| List | `103` |
| Column / Area / Bar / Line chart | `104` / `105` / `106` / `107` |
| Pie / Donut chart | `108` / `109` |
| Media compact / expanded (creative preview) | `110` / `111` |
| Funnel | `115` |
| Stacked bar / stacked column chart | `118` / `119` |
| Goal | `123` |
| Filter control (dimension dropdown) | `137` |
| Heatmap | `138` |
| Gauge (dial-style single value) | `139` |
| GeoMap (BETA) | `140` |
| Comment / text | `21` (`channel_id=7` = Custom data; no `source_id`) |
| Calendar / date control | `22` (`channel_id=7`; no `source_id`) |
| Image | `34` (`channel_id=7`; no `source_id`) |
| Report shortcut (link to another report) | `141` (`channel_id=7`; no `source_id`) |
| Dynamic chart (scatter, bubble, heatmap, calendar heatmap, candlestick, box plot, radar, funnel, polar bar, stacked and 100% stacked, horizontal bars, bars-plus-line, top-N) | `142`, name a `chart_type`, or write a `chart_spec` when no family fits: load `whatagraph-dynamic-charts` |

Offline types (`channel_id=7`, no `source_id`, values in `rows[].data`; string names carry an `offline_` prefix, e.g. `"offline_single_value"`): Single value `125`, Table `126`, List `127`, Column `128`, Area `129`, Bar `130`, Line `131`, Pie `132`, Donut `133`, Goal `135`, Funnel `136`.

Only comment, image, calendar, report shortcut and the offline types take `channel_id=7` and no `source_id`. Filter control (`137`) needs a `channel_id` and `source_id` but loads no data. Every other data widget needs the source's `channel_id` and a report-local `source_id`.

## Offline (manual-data) widgets

For numbers Whatagraph cannot connect to (offline spend, retainer fees, call volumes, a client's targets). The widget holds the values: no source, no metric binding, no refresh. For building a whole report this way, load `whatagraph-offline-reports`.

Values go in a row-level **`data`** array, a sibling of `options` and `configs`. On update, `data` replaces that row's values wholesale.

```
manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id=7 widget_type_id=125 name="Offline spend"
   options={"width": 2, "height": 2}
   rows=[{"options": {"title": "Retainer"},
          "data": [{"name": "Retainer", "value": "4500", "previous_value": "4000"}]}]

manage-widgets action=update report_id=<id> widget_id=<id>
   rows=[{"data": [{"name": "Retainer", "value": "5000", "previous_value": "4500"}]}]
```

**Two `data` shapes, picked by widget type:**

- **Entry list**: Single value (`125`), List (`127`), Pie (`132`), Donut (`133`), Funnel (`136`), Goal (`135`). One entry per KPI, item, slice or step: `name` (required, the visible label and the metric name), `value` (required), `previous_value` (optional, the comparison behind the delta), `negative_ratio` (optional, `true` when a rise is bad, such as costs or refunds). Goal only: `target` (required) and `start` (default `"0"`); both are rejected on other types.
- **Header row + data rows**: Table (`126`) and Column / Area / Bar / Line (`128`–`131`). The first inner array is the header; the first cell of every row is the dimension label. Every row must have as many cells as the header, or the tool rejects it.

```
rows=[{"data": [
  ["Page",     "Sessions", "CTR"],
  ["Homepage", "3000",     "25%"],
  ["Pricing",  "1450",     "12.5%"]
]}]
```

**Values** are stored as strings (numbers are converted). The unit drives formatting: `"25%"` → percentage, `"$4.80"` or `"4.80 $"` → currency, `"12.5"` → one decimal. `null` is a blank cell. Only symbols are read: `"4500 USD"` and `"-5%"` render as literal text.

⚠️ **One value and one unit per cell.** A cell with **two currency symbols** (a range like `"$4.80 - $7.40"`, or `"$1,200 ($400/mo)"`) makes the frontend throw `RangeError: Invalid currency code`, and the widget flickers and never draws. Nothing rejects it on write. Split a range into two entries or two columns (`Low`, `High`), and put any prose in the entry's `name` or a Comment, never in `value`.

**Rules:**

- **No binding.** `rows[].configs[].options.metrics` is rejected on offline types; the metric names come from the entries' `name` or the header row. `rows[].options.value` / `previous_value` bind nothing and come back as an unrecognized-key warning.
- **Omitting `data` on create leaves the template's demo numbers** (200,000 impressions against 15,000), with a warning. Treat it as unfinished and send the `data`.
- **One row is the norm**: a 3-item List or a 3-line Goal is one row with three entries. If a widget needs several rows (two series on a line chart), give each its own `data`; rows beyond the template's count render "Couldn't find data to display" until filled.
- **Hide the footer**: set `hide_footer: true` on every offline widget, easiest in one `batch_change_settings` pass.
- **No offline version** of Image (`134` does not exist), Heatmap, Gauge, GeoMap or Dynamic chart. For a manual heatmap use an offline Table with block shading (see "Faking a heatmap").
- **Confirm the write** with the `data_summary` echoed on create, update and `show`: `headers` and `data_row_count` for table and time-series shapes, `entry_names` and `entry_count` for the rest. A widget created without `data` reports the *template's* headers, so check the headers are yours.
- On deployments before Aug 2026 the `offline_` string names resolved to old types and were rejected; pass the integer id there.

## Apply a premade widget

A template widget pre-configured by Whatagraph for the channel. Find premade ids first (`channel_id` required):

```
list-widgets action=list_premade channel_id=<id>   # or a slug, e.g. "google-ads"

manage-widgets action=apply_premade                # alias: create_premade
   report_id=<id> tab_id=<tab_id>
   widget_id=<premade_widget_id>                   # from list_premade, NOT a report widget
   source_id=<report_local_source_id>              # omit for sample data
```

A source from another channel is rejected, so scope `list_premade` to the source's channel. Supports `position_x` / `position_y` and `options` (width, height); the source auto-attaches like on `create`. Rejected on reports linked to a template (`linked_template_id` set): use `create` there.

## Update a widget

Metrics go in `configs[].options.metrics` (objects or strings; a singular `metric` is wrapped). `list-widgets action=show` returns each config's bindings as `metrics` / `dimensions` / `report_types`, the same vocabulary `manage-widgets` accepts, so a config you read can be sent back. The old keys `integration-metrics` / `integration-dimensions` / `integration-report-types` are **rejected**; use `metrics`, `dimensions`, `report_type`.

```
manage-widgets action=update
   report_id=<id> widget_id=<id>
   name="October Spend"
   options={...}
   rows=[{
     "options": {"metrics": [{"identifier": 0, "external_id": "universal_metric_3"}]},
     "configs": [{
       "integration_id": <channel_id>,
       "source_id":      <report_local_source_id>,
       "options": {
         "metrics":    [{"name": "Spend", "identifier": 0, "external_id": "universal_metric_3"}],
         "dimensions": [{"name": "Date",  "identifier": 0, "external_id": "universal_dimension_1137"}],
         "report_type": "campaign"
       }
     }]
   }]
   date_range={"from":"2025-10-01","till":"2025-10-31","period":"custom","compare_type":"previous"}
```

Read the current shape with `list-widgets action=show` first (`rows[].id`, `rows[].configs[].id`). Passing row and config `id`s updates them in place. **When editing a config in place, always carry its `integration_id` / `channel_id`, `source_id` and `report_type`** with the new metrics: a metric-only update can rebuild the config without its report type and blank the widget ("Unavailable report type"), especially on source-group or report-type-bound widgets.

> **A new metric binding on an existing config sometimes does not stick.** With the config's original `id`, a new `metrics` payload can leave the old metric bound, and `show` hides this (it echoes channel and source ids, not the metric). This is most common on source groups and blends.
>
> 1. Omit the row `id` and config `id` so the rows are rebuilt from scratch with the new metrics. This creates a new report-local source mapping, and it drops any conditional formatting on the row (see `whatagraph-widget-advanced`).
> 2. Verify with `list-widgets action=csv_export` or `export-report`. If the old metric still shows, delete and recreate the widget.
> 3. On a **blend or source group**, the renderer may still ignore the binding; finishing the setup in the UI is then required.

After a source group's sources change, a widget on it may need a re-save to pick up the new fields; check with `show`.

### Row-level `options` (chart widgets)

For multi-row Column, Line, Area and Bar charts. A Dynamic Chart (`142`) set to a `chart_type` family reads `type`, `axis`, `cumulative` and `fill` off its rows the same way (see `whatagraph-dynamic-charts`):

| Row option | Type | Notes |
|---|---|---|
| `type` | string | Series type: `column`, `line`, `area`, `spline`, `splineArea`. Mix them for a combo chart. |
| `axis` | `left` \| `right` | **Set it on every row of a combined chart**, `left` unless you want a dual axis. An axis-less row still binds, but the editor shows it on neither axis and the Edit panel looks empty. |
| `cumulative` | boolean | Cumulative values for this row. |
| `fill` | `solid` \| `hatched` | Draws the row in its own colour with diagonal stripes of the widget background, telling two series apart without a second theme colour. **Bars only**: on a line or area it is stored and draws nothing. |
| `trend_line` / `trend_line_period` | string / integer | Trend line type and period. |
| `icon` | string | Row icon (List and SingleValue only), see "Row icons". |

```
# Mixed column + line chart
rows=[
  {"options": {"type": "column", "axis": "left",  "metrics": [...]}, "configs": [...]},
  {"options": {"type": "line",   "axis": "right", "metrics": [...]}, "configs": [...]}
]

# One metric compared across sources: one row per source, same metric, NO dimension; the sources become the columns
rows=[
  {"options": {"type": "column", "axis": "left", "title": "Source A", "metrics": [{"identifier": 0, "external_id": "<metric>"}]},
   "configs": [{"source_id": <A>, "integration_id": <channel>, "options": {"metrics": [{"identifier": 0, "external_id": "<metric>"}], "report_type": "<rt>"}}]},
  {"options": {"type": "column", "axis": "left", "title": "Source B", "metrics": [{"identifier": 0, "external_id": "<metric>"}]},
   "configs": [{"source_id": <B>, "integration_id": <channel>, "options": {"metrics": [{"identifier": 0, "external_id": "<metric>"}], "report_type": "<rt>"}}]}
]
```

### Renaming a metric caption

⚠️ **One field renames the caption a reader sees: `rows[].configs[].options.metrics[].name`.** The `show` response also has the old name in `rows[].options.title`, which looks more like the answer and is not. Do not copy the shape `show` returns; go straight to the config metric.

```
manage-widgets action=update widget_id=<id>
  rows=[{id: <row_id>, configs: [{id: <config_id>, channel_id: <channel_id>, source_id: <source_id>,
    options: {report_type: "<report_type>",
              metrics: [{external_id: "clicks", name: "Hot Leads", identifier: 0}]}}]}]
```

Carry `channel_id`, `source_id` and `report_type` as with any in-place config edit. When `rows[].options.title` is left unset, `manage-widgets` copies the config metric names into the row display options, so the editor and the caption stay in step. Rename a dimension label the same way, with `configs[].options.dimensions[].name`.

The two decoys:

- `rows[].options.title` is the placeholder shown **before** data arrives. Writing it returns `success`, looks right for a moment, and reverts when data loads. An explicit `options.title` also stops the automatic copying above, so the fields disagree.
- `rows[].options.metrics[].label` is read by nothing on a current-generation widget (it is a leftover on premade and seeded widgets). Responses on types `101`+ strip it. Current widgets read only `decimal_place`, `width` and `sort` from `rows[].options.metrics[]`.

A warning flags a row-level label set without a config metric `name`. Where the rendered label comes from:

| Type | Rendered label |
|---|---|
| SingleValue `101`, Gauge `139`, List `103` | Config metric `name`; row `options.title` only until data loads. |
| Charts `104`–`107`, `115`, `118`, `119`, Pie/Donut `108`/`109` | Config metric `name`; series names never fall back to the row title. |
| Table `102`, Media `110`/`111`, Heatmap `138`, GeoMap `140` | Config metric / dimension `name`, column headers included. |
| Goal `123` | Config metric `name`. `options.title` is still required at create and shows while there is no data; set both to the same text. |

Exceptions where the row-level field **is** the label: formula rows (`rows[].options.formula_title`, see `whatagraph-widget-advanced`); offline widgets (`125`–`136`), labelled by each `data` entry's `name`; and pre-`101` legacy types, which read `rows[].options.title` first.

### Sorting a widget

Sorting is a **row display option**. Set `sort` on the entry in `rows[].options.metrics[]` or `rows[].options.dimensions[]` whose `identifier` matches the binding, the same field the UI writes when a user clicks a column header.

| Field | Values | Notes |
|---|---|---|
| `sort` | `"asc"` \| `"desc"` \| `null` | The **direction**. `null` clears it. Anything else (a number, `"descending"`) is rejected. |
| `sort_type` | `"value"` \| `"change"` | Metrics only. `value` (default) sorts by the number, `change` by its movement against the comparison period. |
| `sort_order` | integer from 0 | Precedence when several columns are sorted; 0 first. Filled in request order when omitted. |

```
manage-widgets action=update report_id=<id> widget_id=<id>
   rows=[{"id": <row_id>,
          "options": {"metrics": [{"identifier": 0, "external_id": "sessions", "sort": "desc"},
                                  {"identifier": 1, "external_id": "clicks"}]},
          "configs": [{"id": <config_id>, "channel_id": <channel_id>, "source_id": <source_id>,
                       "options": {"report_type": "<report_type>",
                                   "metrics": [{"external_id": "sessions", "name": "Sessions", "identifier": 0},
                                               {"external_id": "clicks", "name": "Clicks", "identifier": 1}]}}]}]
```

Sort by a dimension column with the same shape on `dimensions[]` (`"asc"` is A–Z):

```
rows=[{"id": <row_id>,
       "options": {"dimensions": [{"identifier": 0, "external_id": "campaign_name", "sort": "asc"}]},
       "configs": [...]}]
```

- **Metrics and dimensions are separate sort groups; only one can be active.** A request that sorts both on one row is rejected. To switch, set `sort: null` on the group you leave, in the same call.
- There is **no** row-level sort: `rows[].options.sort` is an old key that nothing reads, and it returns a warning.

### Row icons

> ⚠️ **Set the icon yourself on every 101 / 103 / 125 row. There is no useful default.** Without `rows[].options.icon` the backend copies the bound metric's catalog icon, and almost no metric has one, so it falls back to one hardcoded eye (`Visible--Streamline-Sharp.svg`). The write returns `success`, and every KPI card in the report carries the same eye.

Only three types render a row icon; `options.icon` is rejected on all others:

| `widget_type_id` | Type | Behaviour |
|---|---|---|
| 101 | SingleValue | Icon on **row 0 only**, always drawn when set. |
| 125 | Offline SingleValue | Same as 101. |
| 103 | List | Icon **per row**, shown when the widget option `show_icons` is on. New Lists are created with it on, but the API reports `false` when the key is absent; if an icon does not show, set `show_icons` explicitly. |

Offline List (`127`) draws no icons, because it builds its lines from the data entries, not the rows.

The value is a filename from a fixed library; never invent one.

```
list-widgets action=list_icons                            # every set, paginated (per_page, cursor)
list-widgets action=list_icons search=revenue             # matches name, tags and groups
list-widgets action=list_icons icon_set=sharp-line        # the current library
```

**One call covers a whole report:** pull `list-widgets action=list_icons icon_set=sharp-line per_page=500` once and pick from it for every card. Match the icon to the metric's meaning: sessions or users → a person or traffic icon, revenue or spend → money, clicks → a cursor, conversions → a target, impressions or views → visibility, time on page → a clock. `search` matches `groups` and `tags` (`search=money`, `search=click`). Cards in one row should differ from each other.

Write the returned `icon` filename verbatim in `rows[].options.icon`, at create (no extra call) or on update:

```
manage-widgets action=update report_id=<id> widget_id=<id>
   rows=[{"options": {"icon": "User-Group--Streamline-Sharp.svg", ...}, "configs": [...]}]
```

Read it back from `rows[].icon` in `show`; ignore any `icon` still in `rows[].options` (legacy data). `"icon": null` clears it. Both icon sets render on all three types. `twitter.svg` and `twitter-ads.svg` have no file and draw blank.

### `rows` → `configs` shape

- A widget has one or more rows; a row has one or more configs; a config pairs metrics with optional dimensions.
- Supplied `rows` replace the previous rows. Row `title` and `description` are kept when the new row omits them.
- Each row carries **two parallel metric arrays** that must agree:
  - `rows[].options.metrics: [{identifier, external_id}]`: the display entry, holding per-column settings (`sort`, `decimal_place`, `width`).
  - `rows[].configs[].options.metrics: [{name, identifier, external_id}]`: the data binding.
  - Mismatched values render the row's label with the config's data. Dimensions work the same way (`rows[].options.dimensions` vs `configs[].options.dimensions`).
  - **Row-level metrics or dimensions with no matching config `options.metrics` / `options.dimensions` are rejected.** Move them into the config.
- `metrics=[]` as a top-level parameter is the wrong shape.
- The same `external_id` twice in one config is de-duplicated (first kept, with a warning), so the widget shows one series. For two series of the same metric, use two rows.

### `date_range`

Overrides the report date for this widget: `from`, `till`, `period`, `compare_type`. Omit to inherit.

> **Comparison deltas need a comparison window.** A KPI with `comparison_display_type` (`percentage` / `absolute` / `combined`) shows a delta only when there is a window to compare against, normally the **report-level** `compare_type` it inherits. `compare_type` is a date-range field, not a widget option, and the widget rejects it. If KPI cards show no trend, set the report's `compare_type` (`whatagraph-reports` → "Set the date range at creation") or give the widget its own `date_range` with one.

### `options`

Per-widget settings in `options` on create and update; the structure varies by type. `show` may not return every display option, so verify exact display settings with `csv_export`, `export-report` or the UI.

#### Display toggles

| Option | Type | Applies to |
|---|---|---|
| `hide_title` | boolean | Most data widgets (not SingleValue, Calendar, Comment, Image) |
| `hide_footer` | boolean | All data widgets |
| `hide_legend` | boolean | All chart types |
| `show_icons` | boolean | List, MediaCompact |
| `show_zebra_lines` | boolean | List, Table, Pie, Donut, Funnel |
| `show_list_row_numbers` | boolean | List |
| `show_totals` | boolean | Table (summary row). It **sums percentage columns as numbers** (25% + 30% = 55%), so turn it off on percent-heavy tables. |
| `show_summary_column` | boolean | Table (only with column dimensions) |
| `show_chart_labels` | boolean | All chart types, Goal, Heatmap |
| `chart_series_labels` | `pills` \| `series_ends` \| `off` | Where a chart names its series. `pills` is a row of chips above the plot; `series_ends` writes each name at the end of its line (only when every series is a left-to-right line or area); `off` hides them |
| `chart_smooth_lines` | boolean | Curves line and area series instead of drawing straight segments, including a Dynamic Chart drawing those |
| `show_funnel_line_conversions` / `show_funnel_overall_conversions` | boolean | Funnel (per-step / total conversion rate) |
| `content_scrollable` | boolean | Table, Media (vertical scroll) |
| `content_horizontal_scrollable` | boolean | Table only |
| `display_dimensions_as_columns` | boolean | Table only |
| `wrap_text` | boolean | Table only. **Breaks at the character, not the word** (a PDF shows `instabilit y`), and no option changes this. Keep cells to one line (about 40–45 characters in a four-column full-width table, less in narrow columns) and put longer prose in a Comment. |
| `show_search_bar` | boolean | Table, List |
| `thumbnail_size` | `small` \| `medium` \| `large` | Table with a creative dimension (default `small`) |
| `active_theme_color_id` | integer | Any widget: overrides the report's palette for this widget. Pass a palette `id` from `list-themes action=list_colors` verbatim; it selects a whole palette, not one colour. |

#### Value formatting

| Option | Type | Applies to |
|---|---|---|
| `decimal_place` | integer 0–5 | Most data widgets |
| `currency` | string (e.g. `"USD"`) | Data widgets with currency metrics |
| `shorten_numbers` | boolean | SingleValue |
| `comparison_display_type` | `percentage` \| `absolute` \| `combined` | SingleValue, List, Table |
| `value_display_type` | `value` \| `percentage` \| `combined` | Pie, Donut |

#### Chart labels (when `show_chart_labels` is true)

| Option | Type | Notes |
|---|---|---|
| `chart_label_position` | string | `top`, `bottom`, `left`, `right`, `insideTop`, `insideTopLeft`, `insideTopRight`, `insideBottom`, `insideBottomLeft`, `insideBottomRight`, `insideLeft`, `insideRight`. Default `insideRight` for bar types, `top` for vertical charts. |
| `chart_label_rotation` | `horizontal` \| `vertical` | |
| `chart_label_size` | integer | 10, 12, 14, 16 |
| `chart_label_distance` | integer 0–15 | |
| `chart_label_bg_enabled` | boolean | |
| `chart_label_bg_opacity` | integer 0–100 | Only with `chart_label_bg_enabled` |

⚠️ **On bar types (horizontal bars, offline Bar included) keep an `inside*` label position.** The label colour is computed to contrast with the bar fill, so an outside position puts a pale label on a pale background, where it is invisible. If the label must sit outside, set `chart_label_bg_enabled: true` to draw a chip behind it. Column, Line and Area labels are always dark and are not affected.

#### Axis, alignment and type-specific options

| Option | Type | Applies to / notes |
|---|---|---|
| `histogram` | string | Charts: `auto`, `1 day`, `1 week`, `1 month`, `1 quarter`, `1 year` |
| `left_axis_value` / `right_axis_value` | object | Charts: `{"from": <n>, "to": <n>}`, `null` resets to Auto. The right axis is restricted with breakdown on. |
| `vertical_text_alignment` | `start` \| `center` \| `end` | SingleValue |
| `horizontal_text_alignment` | `left` \| `center` \| `end` | SingleValue |
| `geo_map_region` | string | GeoMap: `world`, `north-america`, `south-america`, `europe`, `asia`, `africa`, `oceania`, `emea`, `apac`, `latam`, `mena`, `noram`, `eu-eea`, `nordics`, `baltics`, `dach`, `benelux`, `iberia`, `uk-ireland`, `anz` |
| `goal_date_range` | object | Goal: `{"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "visible_time_line": true}` |
| `show_metrics_list` | boolean | Pie, Donut, Funnel: `false` hands the whole tile to the chart, which then names its own parts. Default `true` |
| `funnel_style` | `stepped` \| `classic` | Funnel: `stepped` draws one bar per stage with the drop shaded and needs no metrics list; `classic` is the stacked bands of older reports. The tool creates funnels as `stepped` |
| `pie_top_n` | integer | Pie, Donut: `5`, `10` or `20` keeps the top N slices and sums the rest into "Other"; `null` shows all |
| `background_size` / `alignment` | string | Image: `auto_fit` \| `scale_to_fit` \| `scale_to_fill`; `left` \| `center` \| `right` |
| `description` | string | SingleValue only. Omitting it clears the template's "Edit description" placeholder. |
| `goal_line_enabled`, `goal_line_value`, `goal_line_label`, `goal_line_color` | boolean, number, string, hex | Column, Area, Bar, Line: a horizontal reference line at a fixed y value (`goal_line_value` required when enabled). Unrelated to the Goal widget. |

#### Shapes by widget type

- **Single-value KPI** (`101`): `{"comparison_display_type": "combined"}` (or `percentage` / `absolute`) shows the delta against the inherited comparison window.
- **Funnel** (`115`): **each stage is its own row** with one metric, in stage order. Several metrics in one config render a single 100% stage.
- **Goal** (`123`): set `options.goal_date_range`. Each row is a goal line and needs `options.title`, `options.start_value` (baseline, usually 0) and `options.end_value` (the target, greater than `start_value`); the config metric tracks progress and its `name` is the label once data loads.
- **Filter control** (`137`): bind a **dimension**, not a metric. It renders as a dropdown that filters the tab's other widgets; no date range, no data of its own.
- **Gauge** (`139`): configured like SingleValue, drawn as a dial. `start_value` and `end_value` in row options set the range.
- **Heatmap** (`138`): one metric across two categorical dimensions (rows × columns, e.g. `sessions` by `deviceCategory` × `browser`). **Exactly 2 dimensions and 1 metric** in one config; `breakdowns_enabled` stays off.
- **GeoMap** (`140`, BETA): set `geo_map_region`; bind a country or region dimension.
- **Media / creative preview** (`110`/`111`): bind the channel's **thumbnail** dimension (`creative_thumbnail_url` on Meta / Facebook, not `ad_name`). Google Search ads are text only; `ad_image_url` fills only for Display / PMax / image ads. A Table can show the same creatives per row (`whatagraph-widget-advanced` → "Ad creative thumbnails in a table"). After building a Media widget, `view-creatives report_id=<id> widget_ids=[<widget_id>]` returns the actual ad images, so you can confirm they loaded. Use it for any creative analysis or QA instead of guessing from URLs (details in `whatagraph-export`).
- **Dynamic chart** (`142`): bind rows as usual, then name a `chart_type`; write a `chart_spec` only for a chart no family describes, such as bars plus a line. It also adds reference lines, running totals, and one series per dimension value; refused at create with neither a type nor a spec. **When the user names a chart that is not one of the type names above, load `whatagraph-dynamic-charts` before picking a type.** Some names collide with a native type (a "calendar heatmap" is not Heatmap `138`). Do not conclude the skill is unavailable without calling `load-skill`; if that call fails, say so instead of substituting a chart.
- **Report shortcut** (`141`): a drill-down card linking to another report of the same team; `channel_id=7`, no source, no metrics. Set the link in `rows[].configs[].options`:

  ```
  "rows": [{"configs": [{"options": {
    "linked_report_id": <report_id>,              # same team only; cross-team ids are rejected
    "linked_report_thumbnail_style": "image",     # card | image | title_only; "image" is required to show a photo
    "images": [{"url": "<published url>", "title": "<caption>"}],   # optional photo instead of the live preview
    "alignment": "center", "background_size": "scale_to_fit"         # set with images, as the UI does
  }}]}]
  ```

  `image_url`, `background_image_url`, `thumbnail_style` and `style` are rejected on this type (the error names `images`). Find target ids with `list-reports`; `show` returns a `linked_report` field (name, URL, space, last edit). Default size 2×2. **Sharing cascades:** when the parent report is shared, every report reachable through shortcuts is shared too, recursively, with the parent share's password and date lock.

## Comment and image widgets

### Comment / text widget (`21`)

Write the body in `rows[].options.comment_widget_text`; the tool copies it to the config on create **and** update. Older accounts also accept the legacy `{"text": "<html>", "comment": "<html>"}` row aliases.

```
rows=[{"options": {"comment_widget_text": {"text": "<h2>Hello</h2><p>World</p>", "contentAlign": "top"}}}]
```

- ⚠️ **The body is HTML, and only HTML.** **Markdown is rejected** (it rendered with the `#` showing; send `<h1>Heading</h1>`). **A Tiptap / ProseMirror document in `description` is rejected** (one unknown node anywhere blanked the whole widget, with no warning). Text with **no tags** is kept as one paragraph, with a warning.
- ⚠️ **Body text is required.** `create` refuses a comment with no body; empty and whitespace-only text count as none. Supply text, a background image, or `ai_text`.
- ⚠️ **Structure comes from tags, not newlines.** `<h2>Heading</h2><p>Body</p>` is two blocks; `"Heading\nBody"` is one paragraph. A literal two-character `\n` (a double-escaped newline) is converted on save, but if a rendered comment shows a visible `\n` or runs everything together in heading size, re-send with real `<p>` and `<h2>` tags, or split it into a header widget and a text widget.
- **Show the body to the user as plain text or markdown, never as HTML.** When you ask the user to approve comment content, show it in chat as text or markdown and keep the HTML for the tool call (a customer shown the HTML answered "I can't read code"). After writing, check the render with `preview-report tab_id=<tab_id>`.
- **Vocabulary.** Everything else is stripped on save and reported in `warnings`:

  | Category | Available |
  |---|---|
  | Blocks | `<p>`, `<h1>`–`<h3>`, `<ul>`, `<ol>`, `<li>`, `<blockquote>`, `<pre>`, `<hr>`, `<br>` |
  | Inline | `<strong>`, `<em>`, `<u>`, `<s>`, `<mark>`, `<code>`, `<a href>`, `<span>` |
  | Styles | `color` and `font-size` (8–96px) on `<span>`; `text-align` (`left`/`center`/`right`/`justify`) on `<p>` and `<h1>`–`<h3>`; `class` on `<p>` |

  `<h4>`–`<h6>` become `<h3>`. Unknown tags are unwrapped and their text kept. `<script>`, `<style>` and `<iframe>` are dropped with their contents. Link `href`s must be `http`, `https`, `mailto` or `tel`. `<mark>` is on or off; it takes no colour.
- **Prefer the named styles over a raw `font-size`**, because a person who later uses the UI style picker strips every custom size in the block: Heading 1 `<h1>` 40px, Heading 2 `<h2>` 30px, Heading 3 `<h3>` 21px, Paragraph 1 `<p class="p1">` 18px, Paragraph 2 `p2` 16px, Paragraph 3 `p3` 14px (default), Paragraph 4 `p4` 13px.
- **`contentAlign`**: `top` (default), `center` or `bottom`. Use `center` for a short line in a tall box.
- **Reading and editing.** `show` returns the body as HTML in `options.comment_widget_text.description` (even for a comment written in the UI) and the plain text in `.text`. Write `description` straight back for a read-modify-write.
- **Colour.** A colour inside the comment content overrides the theme's `text_color`, so a palette change does not recolour it. Use `<span style="color: …">` for white-on-dark text, or leave text uncoloured to inherit the theme.
- **Updating: `rows[].id` is optional.** The existing config's `integration_id`, `source_id` and `report_type` are carried forward, and a row without `id` updates the row in the same position, keeping its configs. Pass `rows[0].id` to reorder rows or be explicit. Setting the text to `""` is refused (a blank box). On an older deployment where a row-level comment or image edit returns success and changes nothing, write the config shape directly in `rows[].configs[].options`.
- **Background image: one widget for a cover or section divider.** Set `background_image_url` (published URL, see below) or `background_image_data` (base64 JPG/PNG, max 10 MB), with optional `background_image_filename`, in `rows[].options`. It renders full-bleed behind the text. Put the heading in the body, set `contentAlign: "center"`, and use a light `<span style="color: …">` so it reads against the image. Check the image resolution against the rendered width.

Worked example (kicker, heading, rule, body with value-coded emphasis):

```
rows=[{"options": {"comment_widget_text": {
  "contentAlign": "top",
  "text": "<p class=\"p4\"><strong><span style=\"color: #8a94a6\">SECTION LABEL</span></strong></p>"
          "<h2>The finding, in one line</h2>"
          "<hr>"
          "<p>Throughput rose to <strong><span style=\"color: #1e8e3e\">49.0</span></strong>"
          " while merge rate fell to <mark><strong>74.6%</strong></mark>.</p>"
}}}]
```

**A number that must carry colour** belongs in a Comment: a `<span style="color: …">` for a good or bad number, or `<mark>` for a highlight. Comments are the only place outside table formatting where a number can carry meaning through colour.

### Image widget (`34`)

Supply `{"image_url": "<published url>"}` or `{"image_data": "<base64 JPG/PNG>"}` (max 10 MB), with optional `image_filename`, in `rows[].options`. The tool copies it to `configs[].options.images: [{url, title}]` on create and update (you can also send that config shape directly). Display options `background_size` and `alignment` go in the row options too. A malformed `image_url` (no scheme or host, or a non-http scheme) and invalid or oversized base64 are rejected before anything is written.

### Remote images must be imported first

For `image_url`, a comment's `background_image_url`, and a Report shortcut's `images[0].url`, never pass an external URL. Call `manage-assets action=import_url` with `target_scope=team`, then `manage-assets action=publish` with the returned `asset.ulid`, and pass only the `url` that `publish` returns (load `whatagraph-assets` for the procedure). A published Whatagraph URL needs no import, and `image_data` / `background_image_data` carry the bytes already. An external URL is stored verbatim as a hotlink that can rot, sit behind a login or not exist at all. If import or publish fails, fix the URL or ask the user for the image and leave the widget unchanged; never fall back to the raw URL or invent one. Theme header and footer images (`manage-themes`) follow the same rule.

## AI text on comment widgets

```
manage-widgets action=update_ai_text report_id=<id> widget_id=<id>
   ai_text={
     "types": ["summary"],          # summary | wins | issues | recommendations | custom (at least 1)
     "load_type": "report_page",    # or "full_report", or "full_report_visible" (excludes hidden tabs)
     "language": "English",
     "summary_length": "long",      # or "short": a sentence count, see below
     "custom_prompt": "...",        # required when types includes "custom"
     "auto_update": false           # false queues the summary now; true regenerates on every refresh
   }
```

Comment widgets (`21`) only; `ai_text` on any other type is rejected. **The summary is not in that response.** Generation runs in the background, and the call returns `status: pending` with a `summary_job_id`. Collect it with:

```
manage-widgets action=update_ai_text report_id=<id> widget_id=<id> summary_job_id=<id>   # no ai_text needed
```

| `status` | What to do |
|---|---|
| `pending` | Still generating. Wait a few seconds and call again; do not poll in a tight loop. |
| `ready` | `content` has the summary, already written to the widget. |
| `failed` | `message` says why. Queue a new one by sending `ai_text` again. A failure that names the plan can mean the team does not have the AI feature. |
| `expired` | Unknown job id, or older than 24 hours. Queue a new one. |

Settings are saved either way. Queueing twice returns the **same** `summary_job_id`, so a retry is safe. A sample-data refusal comes back on the first call.

> `summary_length` is a **sentence count per type**: `short` = 3, `long` = 8. Types stack, so `["summary","wins","issues","recommendations"]` at `long` gives about 32 sentences.
>
> - **`short` is for a caption beside one chart.** Never on a full-width page-level block.
> - Page-level default: `long` with `["summary","recommendations"]`; on an outcome or conclusion tab, all four types.
> - On the report's **first** tab use `load_type: "full_report"`, so the executive summary can refer to the later tabs.
> - Pass `auto_update: false` on a build-and-hand-over run and collect with the job id, so you can check the length you got. With `true` nothing is queued and the widget stays empty until the next refresh.
> - **Size the comment to the text**: `6×3` minimum for `long` single-type, `6×4`–`6×6` for `long` multi-type. A long summary in a `6×2` clips, and a scrolled block truncates in the PDF; check with `export-report`.

**`ai_text` is also accepted on `create`**, with the same fields. With `auto_update: false` the create queues the summary and returns `ai_text_status: pending` and `ai_text_summary_job_id`; collect it with `update_ai_text`, passing that id as `summary_job_id` and the new widget's id. `ai_text` satisfies the body requirement, so this is how to create a comment with no hand-written text. The generated text itself can only be hand-edited in the UI.

## Breakdown vs non-breakdown (pie / donut / bar / column)

Breakdown works **only** on column (`104`), bar (`106`), stacked column (`119`), stacked bar (`118`), pie (`108`) and donut (`109`); other types ignore `breakdowns_enabled`.

> **Time series are different.** On area (`105`) and line (`107`) the x-axis is always the date, and a categorical dimension alone renders an **empty chart**. To split a time series by a category (clicks per campaign over time), bind the dimension **and** set `options.breakdowns_enabled: true`. For a share of the total, use a breakdown donut or pie.

**Breakdown mode** (`breakdowns_enabled: true`): **one row** with one metric and one dimension; the dimension values make the slices. Do not add rows. Always set `breakdowns_show: true` with it.

```
manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id=<channel_id> widget_type_id=109 source_id=<id>
   name="Clicks by Ad Group"
   options={"width": 4, "height": 3, "breakdowns_enabled": true, "breakdowns_show": true}
   rows=[{"options": {"title": "Clicks", "metrics": [...], "dimensions": [...]},
          "configs": [{"options": {"metrics": [...], "dimensions": [...], "report_type": "..."}}]}]
```

**Non-breakdown mode** (`breakdowns_enabled: false`): **one row per metric, no dimensions**; each row is a slice ("impressions vs clicks"). Set `breakdowns_show: true` so users can switch breakdown on in the UI.

```
   options={"width": 4, "height": 3, "breakdowns_enabled": false, "breakdowns_show": true}
   rows=[{"options": {"title": "Impressions", "metrics": [...]}, "configs": [{"options": {"metrics": [...], "report_type": "..."}}]},
         {"options": {"title": "Clicks",      "metrics": [...]}, "configs": [{"options": {"metrics": [...], "report_type": "..."}}]}]
```

## Add / remove rows

Multi-row widgets (combo charts, funnels, non-breakdown pies) have one row per series or stage.

```
manage-widgets action=add_row    report_id=<id> widget_id=<id>
manage-widgets action=remove_row report_id=<id> widget_id=<id> row_id=<row_id>
```

- `add_row` copies the last row's config (integration, source, report type); set its metric afterwards with `update`.
- **`remove_row` needs approval.** The first call returns a preview and changes nothing; resend the identical call with its `confirm_token` (`whatagraph-deleting` → "The approval gate"). It deletes the row, its configs and their conditional formatting (reported in `warnings`). The last row cannot be removed.
- Find row ids with `list-widgets action=show`.

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

- `widget_ids` is required. An empty array is a no-op, not "all widgets".
- `batch_change_source` takes global or report-local ids and auto-attaches. The new source must be the widgets' channel; a cross-channel swap is rejected with the mismatched widgets named. The new source may lack a report type or field the widgets use, so check them with `show` afterwards.
- `batch_change_date_range` sets a widget-level override; `batch_delete_date_range` removes it (the widgets inherit the report date again).
- `batch_change_filter_visibility` sets `source_filter_off` on many widgets: `true` disables source-level filters, `false` re-enables them.
- `batch_change_settings` takes the `options` keys, so a `title` is refused when a selected widget is a Comment, Calendar, Filter control or Report shortcut (the error names them). Drop those widgets or the `title`.
- Use batches for about 10 or more widgets.

## Layout grid model

The report uses a **6-column grid**. Every widget is a rectangle:

| Property | Range | Default | Notes |
|---|---|---|---|
| `position_x` | 0..5 | 0 | Column (0-based). `position_x + width ≤ 6`. |
| `position_y` | 0..∞ | next row below existing widgets | Row (0-based). |
| `options.width` | 1..6 | 2 | Width in columns. |
| `options.height` | ≥1 | 2 | Height in grid rows. |

> **Grid width follows the report layout.** Landscape (`printing_landscape_6x6`, the default) is the 6-column grid. Portrait (`printing_portrait_4x8`) has **4 columns**: every width and `position_x` limit caps at 4. Orientation is set at report create and cannot change once widgets exist. Landscape gives a wider, shorter page: favour wide rows.

> **A tab is a page.** In a PDF each visible tab is exactly one page, as tall as its content; tabs are never split or combined. Put a section break on a new tab, not lower down the grid (`whatagraph-export` → "PDF export").

> **Input and output differ:** pass `width` and `height` inside `options` on create and update; they come back as **top-level** `width` and `height`. With `fields`, use `fields="width,height"`.

**Overlaps are rejected** on `create` and `update` unless `auto_place=true`, which picks the nearest free slot. On `create` with no `position_x` / `position_y`, auto-placement is the default. On `update`, overlap is checked when a position is given (the widget itself excluded).

**Inserting between two rows:** the target row is occupied, and `auto_place=true` sends the widget elsewhere. Open the row first with `manage-report-tabs action=insert_row_space` (`position_y` = the row to open, `row_count` = the new widget's height), then `create` at that position. Never shift widgets one at a time, and never rebuild the tab elsewhere (`whatagraph-report-tabs` → "Insert or remove rows in a tab").

**Removing empty rows** ("close the gaps", "compact the tab", "remove the blank rows"): use `manage-report-tabs action=remove_row_space` (`position_y` = first empty row, `row_count` = how many), not one `update` per widget. To clear every gap, work out the gaps from each widget's `position_y` + `height`, then call `remove_row_space` once per gap **from the bottom up**, because closing a gap renumbers every row below it. The call is rejected if a widget occupies or reaches into the rows, and the error names the blocking widgets and the rows that are free.

⚠️ **A request for "a row" or "a line" is a request for empty space, not a widget.** `insert_row_space` completes it. Do not create a placeholder Comment ("New row"); create a widget only when the user named one, and never guess its type or content.

### Sizing: driven by content

Size scales with data: the more rows, series or columns a widget carries, the larger it is. **A widget with a lot of data gets more area, not a scrollbar.**

- **KPI / SingleValue / Gauge / Goal**: small, so several share a row. A full-row single value reads as a header; use `2×2`.
- **Table / Heatmap**: most or all of the row, taller as rows grow.
- **Line / Area / time series**: wide (often the full row), with the date dimension bound.
- **Bar / Column**: compact beside a sibling, full width when it is the focus.
- **Pie / Donut**: roughly square. **List / Funnel**: narrow to medium, beside a chart. **GeoMap**: medium. **Media**: one tile per creative across a row.
- **Comment**: full row for a header, taller for text. **Size the height to the rendered text** (below).

**Hard constraints:** `width` 1..6, `height` ≥ 1, `position_x + width ≤ 6`, no overlaps.

#### KPI card geometry

The SingleValue value font has three fixed size steps, set by the card's size:

| Card size | How the number reads |
|---|---|
| exactly 1 column wide | smallest; footer and icon hidden (title too, unless ≥2 rows tall) |
| 2–3 columns wide, ≤3 rows tall | standard: the same at `2×2` and `3×2` |
| ≥3 columns wide **and** ≥4 rows tall | large (about double) |

- **Default KPI cards are `2×2`, three across**, never `3×2` two across: the same number in twice the box looks like a small number in a large frame.
- A hero number needs **at least 3 columns and 4 rows**; `3×3` is still the standard step.
- Make a SingleValue 1 column wide only on purpose (a narrow KPI strip at height ≥2), never for a headline number and never at height 1.
- Set `vertical_text_alignment: "center"` and `horizontal_text_alignment: "center"` on every SingleValue unless you have a reason not to; the defaults park the value bottom-left.
- **Never let the widget title and the metric caption be the same string.** `hide_title` is rejected on SingleValue, so set the config metric `name` to something complementary (`"Last 30 days"`, `"vs previous period"`) and keep the metric in the widget title.
- `shorten_numbers: true` only on cards ≤2 columns wide, where 6+ digits would clip.

#### Sizing comment widgets (`21`): a fixed box that clips

A comment renders in a **fixed pixel box** from its integer `height` (about 100–120px per unit, of which only 80–90px is usable at `height: 1` after padding). It **never grows with its content**: overflow is cut off mid-line with no scrollbar, and the write returns `success` either way.

- **A heading plus any subtext needs `height: 2` minimum.** A heading costs about 40px alone, so heading + one wrapped body line overflows a height-1 box. `height: 1` holds one line: a bare heading *or* one short body line.
- **Budget one grid unit per about 2 rendered lines, and count the heading as a line** (a 28–32px headline takes most of a unit). A `6×2` opener fits a kicker, a headline and about two short sentences.
- **Count wrapped lines, not sentences.** One unit holds about two lines of 14–15px text (160–200 characters at `width: 6`); a subtitle of 12+ words wraps to two lines at full width, sooner in a narrower comment.
- **When unsure, add 1 to `height`.** A slightly tall card looks fine; a clipped one looks broken. Split a long block across widgets or trim the copy rather than cramming it.

| Content (at `width: 6`) | Minimum `height` |
|---|---|
| One short line: a bare heading *or* one body line | 1 |
| Heading + 1–2 lines | **2** |
| Heading + 3–4 lines, or a full paragraph | 3 |
| Multi-paragraph or AI-summary block | 4+, then verify |

**Always verify** a created or edited comment with `preview-report` or `export-report`: a truncated widget still returns `success`.

#### When titles show, and how long they can be

**A `height: 1` widget shows no title**, description, icon or footer. The same at `width: 1`, except a SingleValue 1 wide and 2+ tall shows its title. So a `6×1` Comment header is fine (its heading is body text), but a `4×1` chart's `name` shows nowhere.

A shown title is **one line, cut with an ellipsis**; it never wraps:

| `width` | Title space | Safe length |
|---|---|---|
| 1 | 184 px | ~16 characters |
| 2 | 426 px | ~38 characters |
| 3 | 668 px | ~60 characters |
| 4 | 910 px | ~84 characters |
| 6 | 1394 px | ~128 characters |

Character counts assume a wide bold font at the default size; a larger theme title font fits less.

### Placing widgets cleanly

1. **Work in rows.** Each row's widths sum to ≤ 6. Track the running `y`: a row of height-2 widgets at `y=0` means the next row starts at `y=2`.
2. **Set `position_x`, `position_y`, `width` and `height` explicitly** on every widget of a designed or replicated layout. `auto_place` (the default when position is omitted) is fine for a one-off add.
3. **Fill each row left to right and start the next row flush** against the previous one. If a row does not reach 6, widen a widget or add one rather than leaving a gap. No empty column mid-row and no empty row between populated rows, unless a reference shows one.
4. **Row recipes** (starting points): three KPI cards `2+2+2` (h2); two charts `3+3` or `4+2` (h3); a full-width table or trend `6` (h3, taller as rows grow); a section header `6×1`; three creative tiles `2+2+2` (h3).
5. **Verify** with `export-report` or `list-widgets action=csv_export` that the layout is right and every widget loaded data (`show` echoes positions, not rendered data). Then style the report (`whatagraph-reports` → "Style the report").

## Tables truncate silently

**A Table or List renders only the rows that fit its box and drops the rest with no marker**: no ellipsis, no scrollbar in the PDF, no warning on write. `csv_export` and `export-report` still return every row, so a data check passes while the rendered report is wrong. On screen the widget scrolls; a PDF keeps only the first screenful.

- **Row height is fixed**: short with `display_dimensions_as_columns` on, taller without it, and taller with more dimensions.
- **Widget height is fixed by grid units**, the same on every tab, and linear in units.
- Working figure: **a table shows about `3.5 × height − 3` rows** (`height: 5` ≈ 14 rows). It moves with the theme font and the dimension count, and tall tables have stopped well short of it. Use it to budget, not to prove.

What to do:

1. **Budget the height before placing**: at least `(rows + 3) ÷ 3.5`.
2. **20 or more rows**: split the data into two side-by-side tables (`3 + 3`). This is the most reliable fix.
3. **15 or more rows with one value each**: use a Bar chart, which scales and never drops a series.
4. **After rendering, confirm the last row of every table is present**: `preview-report tab_id=<tab_id>` and look at the image. Without `preview-report`, render with `export-report format=pdf`, check it yourself when you can read files, and otherwise ask the user to check, naming the tables and rows to look at (`whatagraph-export`).

## Filtering a widget

Pick the simplest of three ways:

**1. Create the filter directly on the target** (recommended):

```
manage-filters action=create channel_id=<id> dimension="campaign.name" dimension_operator="contain_dimension" value="brand" name="Branded" widget_config_id=<config id>
manage-filters action=create channel_id=<id> dimension="campaign.name" dimension_operator="contain_dimension" value="brand" name="Branded" source_id=<source id>
```

One call, no orphaned team filter. The channel must match the target's. It replaces any existing filter on that target. Pass `widget_config_id` or `source_id`, not both.

**2. An existing team filter, inline** in `rows[].configs[]`: `manage-widgets action=update ... rows=[{configs: [{filter_id: <team filter id>}]}]`. `filter_id: null` detaches. The channel must match.

**3. Create, then attach** (one filter on several targets): `manage-filters action=create ...` without a target, then `manage-filters action=attach filter_id=<id> widget_config_id=<config id>`.

**Precedence:** a widget applies **one** filter. A widget-config filter wins; otherwise the source's filter applies.

> **Avoid source-level filters unless asked.** A source filter applies to **every widget using that source in every report**, and can error where it names a field a report type lacks. Default to `widget_config_id`; use `source_id` only when the user wants all data from that source filtered ("only US data from this source").

- `show` returns all filters in `inline_filters`, with a `scope` (`widget_config` or `source`) and `team_available`. Config-scoped filters (`team_available: false`) do not appear in `list-filters action=list`.
- `source_filter_off` on `manage-widgets` only toggles existing source filters for the widget; it does not create them.
- `filters`, `filter` and `inline_filters` on `manage-widgets` are rejected; use `filter_id` or `manage-filters`.
- Load `whatagraph-filters` for operators and AND/OR row groups.

## Deleting widgets

Destructive: load `whatagraph-deleting` for parameters, cascades and recovery. Soft delete with a `restore` action, `batch_delete` for many, idempotent on deleted widgets. Delete-and-recreate is the fix when a metric update does not stick (see "Update a widget").

## What MCP can't do here

- Move widgets to another tab: use `manage-report-tabs action=move_widgets`.
- Reposition many widgets at once: there is no batch reposition; open or close rows with `manage-report-tabs action=insert_row_space` / `remove_row_space`.
- Set widget-level permissions: UI only.
- Copy a widget to another report: duplicate works within one report only (`whatagraph-widget-advanced`).
- Edit the generated AI text: UI only.
- Colour cells on anything but a live Table (`102`): KPI cards and offline tables cannot carry conditional formatting.

### Faking a heatmap

For an offline table, encode intensity in the cell text: a shade glyph per bucket (`█` highest, then `▓`, `▒`, `░`, `·` for none) or a short bar like `██████░░░░`. It survives the PDF and needs no colour support. Keep it to one glyph plus the number in a narrow column; a ten-cell bar overflows and truncates. For a single coloured value, use a Comment (see "Comment / text widget").

## Idempotency

`create`, `apply_premade` and `create_premade` accept an optional `idempotency_key` (a client UUID). If a timeout leaves the result uncertain, resend the same call with the same key to get the original result instead of a duplicate. Use a fresh key for each distinct operation.
