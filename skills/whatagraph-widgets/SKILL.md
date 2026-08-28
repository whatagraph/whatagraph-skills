---
name: whatagraph-widgets
type: domain
group: report_building
description: Build and lay out widgets on the 6-column grid — KPI rows, chart pairings, full-width tables, comment narration, image dividers — and create, update, duplicate, or batch-modify them. Use when designing a report tab's layout, sizing and positioning widgets on the grid, replicating the layout of a reference report (PDF/screenshot/existing report), swapping metrics on an existing widget, renaming the metric caption / series label a widget shows, colouring table cells by value with conditional formatting, bulk-swapping data sources across many widgets at once, or entering numbers by hand into an offline / manual-data widget. Also the widget reference for building a whole report out of numbers you already have — an analysis, a spreadsheet, a client's own figures — with no connected source at all; load `whatagraph-offline-reports` for that workflow. Carries the non-negotiable full-tab composition bar for self-directed builds — dashboard pages of 8–14 varied widgets, or editorial story chapters with styled narrative openers, argumentative titles, and closing takeaways; never a thin strip of token widgets.
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
    purpose: Move widgets to another tab (move_widgets).
  - tool_name: manage-custom-metrics
    purpose: Build a reusable calculated metric (e.g. Blended CPA) to bind like any other metric, instead of a per-widget formula row.
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
  - tool_name: preview-report
    purpose: Look at the built layout to verify every table's last row is present.
---

# Widgets

Tools covered: `list-widgets`, `manage-widgets`.

A **widget** is a visual data component on a tab. Widgets are typed (KPI card, line chart, table, pie chart, etc.) and each has a data source (or no source for comment/image widgets). Widgets expose rows and configs — a row groups metrics and dimensions; configs define the data.

> **The quality bar — read this before building anything.** Unless the user handed you a widget-by-widget spec or a reference to replicate, every tab you build is a **full, purposeful page**: it opens with narrative framing, develops one clear question with substantial, varied widgets, and leaves no dead grid. Two composition modes clear the bar — a **dashboard tab** (two or more header-led sections, typically 8–14 widgets) and an **editorial tab** (a chapter in a story: styled narrative opener, 3–8 *larger* widgets that argue one point, a closing takeaway comment) — see "Composing a full tab" for both; a report may mix them. What never clears the bar: one or two token widgets adrift in an empty grid, a strip of small KPIs plus a lone chart, a page with no narrative framing at all. The bar applies even when the tabs and their themes were named for you. **If your run has a limited step budget, economize on discovery and verification calls — bind `rows` at create, reuse the field catalog across widgets, batch, verify once at the end — never on the composition.**

## Use this when

- Adding a KPI card, chart, table, or funnel to a tab.
- Entering numbers by hand — offline spend, retainer fees, client targets — into an offline (manual-data) widget.
- Swapping the source on a set of widgets (migrating from sample to real data).
- Changing common settings (currency, footer visibility) across many widgets at once.
- Duplicating a widget or a set of widgets on a tab.

## A `warnings` entry blocks the next step

> ⚠️ **Read `warnings` on every `manage-widgets` response, and fix what it names before you move on.** A warning here is not advisory. It is the tool telling you that part of what you sent was stored somewhere nothing reads, so the widget on the report does not match the call you believe succeeded. The response still says `success: true`, because the widget row was written; the part you cared about was dropped.

The failure this exists to stop: an agent built six widgets in one step, and one of them carried its metrics under a row option the tool does not read. The response warned in plain words that the key was stored and had no effect. The agent read the warning, moved on, and a widget rendering "Metrics not selected" shipped to a customer-facing report.

So when `warnings` is non-empty:

1. Read each entry. Every one names the field it dropped and the field it belongs in.
2. Re-issue the call with the binding moved, or send an `update` that fixes the widget you just created.
3. Only then build the next widget.

Never treat a warning as a note to report back at the end of the run. By then the widget is on the report.

The hard errors are a separate matter: the tool now refuses several of these mistakes outright rather than warning (see "A create with no binding is refused" and "Bindings written one level too high"). An error means nothing was written, so you can correct the shape and send the same call again.

## Listing

```
list-widgets action=list report_id=<id>                    # grouped by tab, sorted by (position_y, position_x); each widget includes `has_filters` boolean and `widget_type_label` (human-readable)
list-widgets action=show report_id=<id> widget_id=<id>     # full widget details: layout, source binding, options, ai_text_settings, source_filter_off
list-widgets action=csv_export report_id=<id> widget_id=<id>
list-widgets action=list_icons                             # the row icon library — see Row icons
list-widgets action=conditional_formats report_id=<id> widget_id=<id>   # a table widget's cell colour rules — see Conditional formatting
```

> ⚠️ **Do not edit a field back just because `show` returned it.** The `show` response repeats the metric's name in `rows[].options.title` as well as `rows[].configs[].options.metrics[].name`, and only the **config** one is the caption the reader sees — the row title is just the placeholder shown until data loads. To rename a metric caption or series label, set `rows[].configs[].options.metrics[].name` — full rule in "Renaming a metric caption".

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
   name="<widget title>"               # always set on data widgets — see Titles
```

**Always pass `name` at create on data widgets** — one created without a name renders the platform's default label. Set each row's rendered metric label in `rows[].configs[].options.metrics[].name` at the same time (see "Titles — every widget and every metric row is labelled").

⚠️ **Four types reject `name` and `options.title` outright** — Comment (`21`), Calendar (`22`), Filter control (`137`), and Report shortcut (`141`). They never render a widget title, so passing one is refused rather than silently stored (Jul 2026). For a Comment, put the heading in the body text instead — `rows[].configs[].options.comment_widget_text.text` with a markdown `#` prefix. Image (`34`) does render a title and still takes `name`.

**On a SingleValue (`101`), List (`103`) or Offline SingleValue (`125`), pass `rows[].options.icon` in the same call** — those three types draw a row icon, and a row created without one falls back to a single hardcoded eye, identical on every card. See "Row icons".

**Always pass `rows` at create time on data widgets** — bind the metrics and dimensions in the same call. If `rows` is omitted, the widget falls back to the first metric in the source catalog — an arbitrary binding that rarely matches the widget's title, and on some sources no default applies at all, leaving the widget rendering **"Metrics not selected"** in the client-facing report. A create that returns `success` with no explicit binding is not a configured widget. Before binding, look the fields up with `list-sources action=list_dimensions_and_metrics` (never guess `external_id`s), keep every field in one config on the same `report_type`, and verify the result loads data (see "Fit for purpose").

### A create with no binding is refused

Since Aug 2026 a `create` on a data widget type is **rejected** when the call would leave the widget with no source and no metrics at all. The error says the report would render "Metrics not selected" and fall back to sample data, and it names the two fields that bind data: a top-level `source_id`, or `rows[].configs[].source_id` plus `rows[].configs[].options.metrics`. Nothing is written, so fix the shape and send the same call again.

Only `rows[].configs[].options.metrics` counts as a binding. A `metrics` array at row level is a display label, so it does not satisfy the check: a call carrying `rows` with metrics at row level, no configs, and no `source_id` anywhere is refused as unbound even though the word `metrics` appears in the payload. Row-level metrics with no matching config metrics are rejected by a second guard as well — see "`rows` → `configs` shape".

Three cases are deliberately outside the check:

- **`rows` omitted entirely.** That asks for a blank widget and gets one, reported as `is_sample_data`. Nothing was dropped. This is still not a configured widget — see the paragraph above.
- **A source bound with no metrics.** This is the documented default-metric flow. It stays a warning, and the warning is worth acting on: the default is an arbitrary catalog field.
- **Utility and offline types.** Comment (`21`), Calendar (`22`), Image (`34`), Report shortcut (`141`), Filter control (`137`) and the offline types (`125`–`136`) render from their own content, so "no source, no metrics" is their normal state.

The check runs on `create` only. An `update` that strips a binding is not refused, so read `warnings` on updates.

A row sent with a `title` and **no `configs` array** now warns as well. The top-level `source_id` keeps the create legal, but the row gets a placeholder config with nothing bound, and the widget renders the source's default metric rather than the one the title claims. The warning names `rows[].configs[].options.metrics`, and it is one to act on: check the key spelling and re-send the row with its config.

### Bindings written one level too high

A row's `options` is a free-form blob. Writing a source or a set of metrics there stores the value and binds nothing, because only `rows[].configs[].options` binds data. Six keys are now a **hard validation error** at row level, on create and on update, because each one means the whole binding was written one level too high:

`configs`, `source_id`, `source`, `sources`, `integration_id`, `channel_id`

The error names the row index and points at `rows[].configs[].source_id` and `rows[].configs[].options.metrics`. Two related keys behave differently and are worth knowing apart:

- **`filters`** is rejected by its own guard, with a message specific to filters. See "Filtering a widget".
- **`operators`** is a real key the renderer reads. It makes the row a formula row, and its shape is checked rather than refused. See "Formula rows".

Any other unrecognized row option key is still a warning, which you must act on under "A `warnings` entry blocks the next step". A widget already carrying a stray key from an earlier bad write stays editable, so the broken ones can be fixed.

### Dimension requirements by widget type

The tool validates that the correct dimensions are provided based on the widget type. **Dimensions must be in `rows[].configs[].options.dimensions`** (data binding), not in row-level options (which are display labels only).

Both ends of each range are enforced at create and update (Aug 2026): too few dimensions and too many are refused the same way. A count below is a hard limit, not a suggestion — an over-bound widget used to be accepted and then rendered wrong.

| Widget type | Dimension requirement |
|---|---|
| Time-series charts (104–107, 118–119) | **1 dimension required** — must be the integration's date dimension (e.g. `date`, `segments.date`, `ga:date`). Binding a non-date dimension while `breakdowns_enabled` is off is **rejected at create/update** (left unchecked it renders an empty/aggregated chart, and hard-errors on some sources such as Google Sheets). To split a bar/column chart by a category instead, set `breakdowns_enabled=true` (see Breakdown vs non-breakdown below) — then column/bar/stacked accept a categorical dimension (up to 2). |
| Table (102) | **At least 1 dimension required** — any dimension. |
| Heatmap (138) | **Exactly 2 dimensions required**. |
| GeoMap (140) | **1 geographic dimension required**. |
| Media (110, 111) | **At least 1 dimension required** — typically `creative_thumbnail_url` or similar. |
| Pie/Donut (108, 109) | **No dimension** unless `breakdowns_enabled=true` (then exactly 1). |
| SingleValue (101), Gauge (139), List (103), Funnel (115), Goal (123) | **No dimension** — binding one is rejected. |
| Comment (21), Calendar (22), Image (34) | **Skipped** — utility widgets with no data binding. |

**Metric counts are capped too.** Every data type above takes **exactly 1 metric per config** — including List (`103`) and the charts. The exceptions are Table (`102`) and Media expanded (`111`), which take any number, Media compact (`110`), which takes at most 2, and the offline types, which bind nothing. To show a second metric on a capped type, add a second row (non-breakdown mode) or use a Table.

Use `list-sources action=list_dimensions_and_metrics` to find the correct dimension external_ids for a source. The date dimension external_id varies by integration — always look it up rather than guessing.

> **A single value (101) always aggregates the whole dataset into one total** — it has no dimension and cannot rank or isolate a single entity. It will **not** show the "best" or "worst" campaign: a `sort` passed on its row or metric options is ignored (the tool returns a warning saying so). To surface a top/bottom performer, use a **Table (102)** with the entity dimension bound and the metric sorted desc/asc, or a saved filter (`whatagraph-filters`) pinning the specific entity.

### Surfacing a top / bottom N

"Top 10 campaigns", "worst-performing ads", "biggest spenders" are ranking asks — they need an **entity dimension bound and the metric sorted**, on a widget type that shows multiple rows (Table `102`, List `103`, or a bar/column chart). A SingleValue can't do this (see the callout above).

- **Sort** on the ranking metric: set `sort: "desc"` (top) or `"asc"` (bottom) on that metric's entry in `rows[].options.metrics[]` so the highest/lowest values lead. Full rules in "Sorting a widget" below.
- **Limit the rows** so "top N" actually shows N: the `manage-widgets` schema exposes **no** row-count / limit parameter on Table, List, or bar/column widgets, so cap the set another way — a `whatagraph-filters` condition that scopes to the entities of interest, or (when the report only needs the leaders) size the widget height to show N rows and rely on the sort. Do **not** fabricate a limit parameter that the tool doesn't accept.
- **Verify** with `export-report` / `list-widgets action=csv_export` that the leading rows are the intended ones and the ordering is correct — a mis-set sort silently returns the data in the wrong order.

**Time-series chart example** (area chart with date dimension):
```
manage-widgets action=create
   report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=105 source_id=<id>
   name="Impressions Over Time"
   rows=[{"options": {"title": "Impressions"},
          "configs": [{"options": {"report_type": "campaign", "metrics": ["impressions"], "dimensions": ["segments.date"]}}]}]
```

**Table example** (with categorical dimension):
```
manage-widgets action=create
   report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=102 source_id=<id>
   name="Campaign Performance"
   rows=[{"options": {"title": "Campaign Performance"},
          "configs": [{"options": {"report_type": "campaign", "metrics": ["impressions", "clicks"], "dimensions": ["campaign_name"]}}]}]
```

**SingleValue example** (no dimension needed):
```
manage-widgets action=create
   report_id=<id> tab_id=<tab_id>
   channel_id="google-ads" widget_type_id=101 source_id=<id>
   name="Total Impressions"
   rows=[{"options": {"title": "Impressions"},
          "configs": [{"options": {"report_type": "campaign", "metrics": ["impressions"]}}]}]
```

### `source_id` — global or report-local

`source_id` accepts either a **global** source `id` from `list-sources` or a **report-local** `source_id` from `list-widgets` / `list-reports action=list_sources`. When a global ID is passed, the tool auto-attaches it to the report — no separate `attach_source` step is needed.

Discover already-attached sources via `list-reports action=list_sources report_id=<id>`. Source groups and blends are themselves data sources — use their `id` from `list-source-groups` / `list-blends`.

### `widget_type_id` — widget types

Widget types are integers. `manage-widgets` writes current-generation types only: `101+`, their offline (manually entered data) counterparts, and the comment / image / calendar utility types. Anything older is rejected on create **and** update — including multi-source table (`37`), which is deprecated in favour of blends and source groups; combine sources there and bind the result to a table (`102`).

Common values exposed by `list-widgets`:

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
| Report shortcut (drill-down link to another report) | `141` (channel_id `7`; no `source_id`) |
| Dynamic chart (scatter, bubble, heatmap, candlestick, combo, top-N) | `142` — needs a `chart_spec`; load the `whatagraph-dynamic-charts` skill |

Offline (manual-data) types hold numbers you supply instead of reading a source. All take `channel_id=7` and no `source_id`, and their values go in `rows[].data` — see "Offline (manual-data) widgets" below. String names are the live name with an `offline_` prefix (`"offline_single_value"`, `"offline_table"`, …).

| Offline widget type | `widget_type_id` |
|---|---|
| Single value (KPI card) | `125` |
| Table | `126` |
| List | `127` |
| Column chart | `128` |
| Area chart | `129` |
| Bar chart | `130` |
| Line chart | `131` |
| Pie chart | `132` |
| Donut chart | `133` |
| Goal | `135` |
| Funnel | `136` |

Comment, image, calendar, report shortcut, and the offline types are the only widget types that take `channel_id=7` and no `source_id`. Filter control (`137`) needs a `channel_id` and `source_id` but does not load data — it renders as a dimension dropdown that filters other widgets on the tab. Every other data-bearing widget needs a `channel_id` matching the source's channel and a report-local `source_id`.

## Offline (manual-data) widgets

For numbers that live nowhere Whatagraph can connect to — offline spend, retainer fees, call volumes, a client's own targets. The widget holds the values themselves; there is no source, no metric binding, and no refresh.

Created like any other widget, with `channel_id=7`, an offline `widget_type_id`, and the values in a row-level **`data`** array. `data` is a sibling of `options` and `configs`, not a key inside either:

```
manage-widgets action=create
   report_id=<id>
   tab_id=<tab_id>
   channel_id=7
   widget_type_id=125                              # or "offline_single_value"
   name="Offline spend"
   options={"width": 2, "height": 2}
   rows=[{"options": {"title": "Retainer"},
          "data": [{"name": "Retainer", "value": "4500", "previous_value": "4000"}]}]
```

Update the same way — supplying `data` replaces that row's values wholesale:

```
manage-widgets action=update report_id=<id> widget_id=<id>
   rows=[{"data": [{"name": "Retainer", "value": "5000", "previous_value": "4500"}]}]
```

### Two `data` shapes, picked by widget type

**Entry list** — Single value (`125`), List (`127`), Pie (`132`), Donut (`133`), Funnel (`136`), Goal (`135`). One entry per KPI, list item, slice, or funnel step:

| Key | Required | Notes |
|---|---|---|
| `name` | yes | The visible label. This is where an offline widget's metric name comes from. |
| `value` | yes | The number. |
| `previous_value` | no | The comparison value behind the trend delta. |
| `negative_ratio` | no | `true` when a rise is bad (costs, refunds) so the delta colours correctly. Default `false`. |
| `start` / `target` | Goal only | The ends of the goal line. `target` is required on Goal; `start` defaults to `"0"`. Rejected on every other type. |

```
rows=[{"data": [
  {"name": "New users", "value": "125", "previous_value": "100"},
  {"name": "Refunds", "value": "1200", "previous_value": "900", "negative_ratio": true}
]}]
```

**Header row + data rows** — Table (`126`) and the time-series charts: Column (`128`), Area (`129`), Bar (`130`), Line (`131`). First inner array is the header, the first cell of every row is the dimension label, the rest are values:

```
rows=[{"data": [
  ["Page",     "Sessions", "CTR"],
  ["Homepage", "3000",     "25%"],
  ["Pricing",  "1450",     "12.5%"]
]}]
```

Every row must have as many cells as the header — cells are read by position, so a short or long row shifts every column after the gap, and the tool rejects it.

### Values

Stored as strings. Numbers are accepted and converted, so `1450` and `"1450"` are equivalent. A unit in the string is read by the formatter and drives how the value renders: `"25%"` → percentage, `"100 $"` → currency, `"12.5"` → one decimal place. `null` renders a blank cell.

**One value per cell, and one unit on it.** The formatter reads a cell as a single number carrying at most one unit. Anything else either renders wrong or breaks the widget:

| Write | Renders as |
|---|---|
| `"4.80"` | `4.80` |
| `"$4.80"` or `"4.80 $"` | `$4.80` |
| `"25%"` | `25%` |
| `"$4.80 - $7.40"` | **breaks the widget** — two symbols, see below |
| `"4500 USD"` | the literal text `4500 USD` — only symbols are recognised, not ISO codes |
| `"-5%"` | the literal text `-5%` — the percentage test rejects a leading sign |

A cell holding **two currency symbols** — a range like `"$4.80 - $7.40"`, or a total like `"$1,200 ($400/mo)"` — is classified as currency, but the backend cannot work out which code it is and returns the whole string in the `currency` field. The frontend then throws `RangeError: Invalid currency code` mid-render, and the widget flickers instead of drawing. This is the single most damaging thing you can put in an offline cell, and nothing on the write path rejects it.

To show a range, split it: two entries (`"CPC low"`, `"CPC high"`), or a Table with a `Low` and a `High` column. To annotate a number, put the prose in the entry's `name` or in a Comment widget, never in `value`.

### Rules worth knowing before you build one

- **No metric or dimension binding.** An offline widget's metrics are derived from its own values (from each entry's `name`, or the header row), so `rows[].configs[].options.metrics` is rejected on these types. The dual metric-array pattern used everywhere else does not apply here.
- **Omitting `data` on create leaves placeholder sample values.** A new offline widget is built from a template seeded with demo numbers (200,000 impressions against 15,000) and renders them verbatim. The tool warns when you do this — treat that warning as a widget not yet finished, and never leave one in a client-facing report.
- **One row is the norm.** Multiple values belong in a single row's `data` array, not in separate rows — a 3-item List or a 3-line Goal is one row with three entries.
- **`data` is per row.** If you do build a multi-row offline widget (e.g. two series on a line chart), give every row its own `data`; rows added beyond the template's count start empty and render "Couldn't find data to display" until they have values.
- **Hide the footer.** Every offline widget draws a footer that identifies the data as offline. In a client-facing or leadership report that is exactly wrong. Set `hide_footer: true` on every offline widget — easiest as one `manage-widgets action=batch_change_settings` pass after the report is built.

### Types with no offline counterpart

The offline range is `125`-`136`, but **`134` does not exist**. It is the position that Image holds in the equivalent non-offline range, and there is no offline Image type — use the normal Image widget, or a Comment widget with a background image (see "Comment and text widgets").

Heatmap, Gauge, GeoMap and Dynamic chart also have **no offline version**. They were added after the offline range was fixed. If you need a heatmap from manual data, use an offline Table with block shading (see "Faking a heatmap").

### Confirming your values landed

An offline row echoes a `data_summary` on create, on update, and on `list-widgets action=show`:

- Table and time-series shapes return `headers` and `data_row_count`.
- Every other shape returns `entry_names` and `entry_count`.

Read that to confirm your write. Offline rows return no `metrics` or `dimensions`, because an offline widget binds nothing.

One trap: a widget created **without** `data` reports the *template's* sample headers, because those sample values are what it will render. The placeholder warning on the same response tells you the numbers are not real. Do not read the summary as proof your data arrived without checking that the headers are yours.

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

Supply metrics on `configs[].options.metrics` (array of objects or strings; singular `metric` is auto-wrapped). Reads and writes use the same vocabulary: `list-widgets action=show` returns each config's bindings as `metrics` / `dimensions` / `report_types`, which is exactly what `manage-widgets` accepts back, so a config you read can be sent straight back.

The old storage keys `integration-metrics` / `integration-dimensions` / `integration-report-types` are **rejected** on input (changed Jul 2026) and are no longer returned by any response. They used to bind nothing while still displaying in the widget row, which left widgets rendering "Metrics not selected" after a write that reported success. If you see one in an error message, replace it with `metrics`, `dimensions`, or `report_type`.

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
           {"identifier": 0, "external_id": "universal_metric_3"}
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
| `icon` | string | Row icon (for List and SingleValue widgets). Must be a filename from the icon library — see [Row icons](#row-icons). |

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
  {"options": {"type": "column", "axis": "left", "title": "Source A", "metrics": [{"identifier": 0, "external_id": "<metric>"}]},
   "configs": [{"source_id": <A>, "integration_id": <channel>, "options": {"metrics": [{"identifier": 0, "external_id": "<metric>"}], "report_type": "<rt>"}}]},
  {"options": {"type": "column", "axis": "left", "title": "Source B", "metrics": [{"identifier": 0, "external_id": "<metric>"}]},
   "configs": [{"source_id": <B>, "integration_id": <channel>, "options": {"metrics": [{"identifier": 0, "external_id": "<metric>"}], "report_type": "<rt>"}}]}
]
```
> One row per source, each with a single config (its source) and the **same** metric, and **no** dimension — the sources become the columns. Set `axis: "left"` on every row; without it the editor's Left/Right axis sections render empty even though the data is bound.

### Formula rows — one metric divided by another

A row can render a calculation over the widget's own configs. `rows[].options.operators` makes it a formula row, and the value is a **flat list of tokens** the backend joins into an expression. There are two token types:

| Token | Shape | Meaning |
|---|---|---|
| Config reference | `{"type": "config", "id": <widget_config_id>}` | The value of an existing config on **this** widget. |
| Operator | `{"type": "operator", "operatorId": "divide"}` | One of `plus`, `minus`, `multiply`, `divide`, `bracket-left`, `bracket-right`. |

A cost per acquisition — spend divided by conversions — is three tokens:

```
rows=[{"options": {"formula_title": "Blended CPA",
                   "operators": [{"type": "config", "id": 55192462},
                                 {"type": "operator", "operatorId": "divide"},
                                 {"type": "config", "id": 55192463}]}}]
```

**A config token references a config that already exists. It does not carry a source or metrics of its own.** So a formula is always a two-call build:

1. `action=create` the widget with its configs bound the ordinary way — one config per operand, each with its own `source_id` and `options.metrics`.
2. `list-widgets action=show` to read the config ids back from `rows[].configs[].id`.
3. `action=update` with the `operators` token list referencing those ids.

A formula sent at `create` is **rejected** as soon as it names a config id, because no config exists yet for it to point at, and the error says to build the widget first. A formula referencing a config on a different widget is rejected too.

Three further rules the tool enforces:

- The operator sign is the **`operatorId` name**, not the symbol. `{"operatorId": "/"}` is refused; `divide` is correct.
- Every token needs a `type` of `config` or `operator`. There is no token for a numeric constant, so a formula cannot multiply by 100 or divide by 1000 here.
- Nesting a config **definition** inside a token — a `configs` array, or a `source_id` and `metrics` on the token itself — is refused. That shape describes a binding the renderer never looks at, so it used to produce a widget with no source and no metrics.

**A formula row is captioned by `rows[].options.formula_title`**, falling back to `options.title`. This is one of the few places a row-level label is the rendered label, because there is no single config metric to name (see "Titles").

**For a calculation you want on more than one widget, build it in `manage-custom-metrics` instead** and bind the result like any other metric. That is a real custom metric on the source, reusable across widgets and reports. Its formula is written as text over single-letter field identifiers, with `+ - * /`, parentheses, and numeric constants — `A/B` for a cost per acquisition, `A/B*100` for a rate. A formula row belongs to one widget and cannot hold a constant.

### Sorting a widget

Sorting is a **row display option**, not a config one. Set `sort` on the entry in `rows[].options.metrics[]` or `rows[].options.dimensions[]` whose `identifier` matches the binding you want to order by. This is the same field the UI writes when a user clicks a table column header.

| Field | Values | Notes |
|---|---|---|
| `sort` | `"asc"` \| `"desc"` \| `null` | The **direction**. `null` clears the sort. Anything else — a number, `"descending"` — is rejected. |
| `sort_type` | `"value"` \| `"change"` | Metrics only. `value` (the default) sorts by the number; `change` sorts by its movement against the comparison period. |
| `sort_order` | integer from 0 | Precedence when several columns are sorted — 0 is applied first. Filled in request order when omitted. |

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

**Sort a table by its dimension column** — same shape, on `dimensions[]`. `"asc"` is A–Z, `"desc"` is Z–A:

```
rows=[{"id": <row_id>,
       "options": {"dimensions": [{"identifier": 0, "external_id": "campaign_name", "sort": "asc"}]},
       "configs": [...]}]
```

**Metrics and dimensions are separate sort groups, and only one can be active.** The UI clears every sort in one group whenever the other is sorted, so a request that sorts a metric *and* a dimension on the same row is rejected. To switch groups, set `sort: null` on the entries of the group you are leaving in the same call.

Read the current state back from `list-widgets action=show` — the three fields sit on each entry of `rows[].options.metrics` / `rows[].options.dimensions`, in the shape `manage-widgets` accepts back.

There is **no** row-level `sort`. `rows[].options.sort` is a pre-new-architecture key that nothing on a `101`+ widget reads; setting it stores a value, orders nothing, and returns a warning saying so.

### Row icons

> ⚠️ **Set the icon yourself on every 101 / 103 / 125 row you build. There is no useful default.** When `rows[].options.icon` is absent, the backend copies the icon from the bound metric's catalog definition — and almost no metric has one (GA4, Google Ads, Meta and the rest all store `NULL`), so it falls back to a single hardcoded file, `Visible--Streamline-Sharp.svg`, the eye. Every KPI card in the report then carries the same eye. The write returns `success` and the card renders, so nothing tells you afterwards. Reports built without this step have shipped with 15 identical eye icons.

Three widget types render a row icon. `manage-widgets` rejects `options.icon` on every other type, so treat this as a whitelist:

| `widget_type_id` | Type | Behaviour |
|---|---|---|
| 101 | SingleValue | Icon on **row 0 only**. Always drawn when set — no toggle. |
| 125 | Offline SingleValue | Same as 101. |
| 103 | List | Icon **per row**, gated by the widget option `show_icons`. |

Offline List (127) is **not** on the list, even though plain List is. It builds its lines from the offline data entries inside the row instead of from the rows themselves, so it never reads the icon column.

On 103, new List widgets are created with `show_icons: true`, but the API reports `false` whenever the key is absent. If an icon does not appear, read `options.show_icons` with `action=show` and set it explicitly.

The value is a filename from a fixed library — never invent one. Browse it with:

```
list-widgets action=list_icons                            # every set, paginated (per_page, cursor)
list-widgets action=list_icons search=revenue             # matches name, tags and groups
list-widgets action=list_icons icon_set=sharp-line        # the current library
```

**One call covers a whole report.** Pull the library once — `list-widgets action=list_icons icon_set=sharp-line per_page=500` — before you start building, and pick from that one response for every card on every tab. Match the icon to the *meaning* of the metric: sessions/users → a user or traffic icon, revenue/spend → money, clicks → a cursor, conversions → a target, impressions/views → visibility, time on page → a clock. The `groups` and `tags` on each entry are there for exactly this, and `search` matches both (`search=money`, `search=click`). Cards sitting in one row should differ from each other — that contrast is most of what the icon is for.

Each entry returns `icon` (the filename to write), `name`, `icon_set`, `groups` and `tags`. Write it back verbatim, at create as well as on update:

```
manage-widgets action=create report_id=<id> tab_id=<id> widget_type_id=101
   channel_id=<id> source_id=<id> name="Sessions"
   rows=[{"options": {"icon": "User-Group--Streamline-Sharp.svg"},
          "configs": [{"channel_id": <id>, "source_id": <id>,
                       "options": {"report_type": "session",
                                   "metrics": [{"external_id": "sessions", "name": "Sessions", "identifier": 0}]}}]}]
```

```
manage-widgets action=update report_id=<id> widget_id=<id>
   rows=[{"options": {"icon": "Visible--Streamline-Sharp.svg", ...}, "configs": [...]}]
```

Bind it at create — it costs no extra call, and an icon added later needs a second `update` per widget.

Read it back with `list-widgets action=show`: `rows[].icon` is the authoritative value, even though you write it under `rows[].options.icon`. Ignore any `icon` still sitting in `rows[].options` — that is legacy data the renderer does not read. Pass `"icon": null` to clear the icon.

Both icon sets render on all three types. Two entries in the library have no file behind them — `twitter.svg` and `twitter-ads.svg` — and draw blank; pick another icon.

### `rows` → `configs` shape

- Each widget has one or more rows.
- Each row has one or more configs.
- Each config pairs a metric with an optional dimension.
- Replace-style: supplied `rows` replace previous rows. Row metadata (`title`, `description`) from existing rows is preserved when the new row omits them.
- Each row carries **two parallel metric arrays** that must agree:
  - `rows[].options.metrics: [{identifier, external_id}]` — the row's display entry, and where per-column display settings live (`sort`, `decimal_place`, `width`). See "Sorting a widget".
  - `rows[].configs[].options.metrics: [{name, identifier, external_id}]` — drives the actual data binding.
  - Both must be set; mismatched values between the two cause the widget to render the row's label with the config's data. The same parallelism applies for dimensions: `rows[].options.dimensions` (rendered label) vs. `configs[].options.dimensions` (binding).
  - **The tool rejects updates where row-level metrics/dimensions are provided but the config has no matching `options.metrics`/`options.dimensions`.** Row-level fields are display labels only — the actual data binding lives in config options. If you get this error, move your metrics/dimensions into `rows[].configs[].options.metrics` (and `options.dimensions`).

### `date_range`

Overrides the report-level date for this widget. Fields: `from`, `till`, `period`, `compare_type`. Omit to inherit report date.

> **Comparison deltas depend on a report-level comparison being set.** A KPI/SingleValue configured with `comparison_display_type` (`percentage` / `absolute` / `combined`) only renders a delta if there's a comparison window to diff against — which normally comes from the **report-level** `compare_type` that the widget inherits (`compare_type` is a date-range field, not a widget option — the widget rejects it). If your KPI cards show no trend, confirm the report has a `compare_type` set (see `whatagraph-reports` → "Set the date range at creation"), or give the widget its own `date_range` with a `compare_type`.

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
| `wrap_text` | boolean | Table only. **Breaks by character, not by word** — see the pitfall below |
| `show_search_bar` | boolean | Table, List (shows a row search box) |
| `active_theme_color_id` | integer | Any widget — overrides the report's colour palette for this one widget. Pass the `id` of a palette from `list-themes action=list_colors`, verbatim. It is a **palette id**, not an index into a palette's colours — you select a whole palette, not one colour |

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
| `chart_label_position` | string | `top`, `bottom`, `left`, `right`, `insideTop`, `insideTopLeft`, `insideTopRight`, `insideBottom`, `insideBottomLeft`, `insideBottomRight`, `insideLeft`, `insideRight`. Default: `insideRight` for bar types, `top` for vertical charts. **On bar types, keep an `inside*` position** — see the pitfall below |
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
| `pie_top_n` | integer | Pie (`108`), Donut (`109`). `5`, `10`, or `20` — keep the top N slices and sum the remainder into a single "Other". Omit or set `null` to show every slice |
| `background_size` | string | Image (`34`). `auto_fit`, `scale_to_fit`, `scale_to_fill` |
| `alignment` | string | Image (`34`). `left`, `center`, `right` |
| `description` | string | SingleValue (`101`) — the only type that renders it. Omitting it clears the template's "Edit description" placeholder rather than printing it |

#### Goal / target line (Column, Area, Bar, Line charts)

A horizontal reference line drawn at a fixed y-axis value. Unrelated to the Goal widget type (`123`).

| Option | Type | Notes |
|---|---|---|
| `goal_line_enabled` | boolean | Turns the line on |
| `goal_line_value` | number | The y-axis value to draw at. Required when enabled |
| `goal_line_label` | string | Optional caption |
| `goal_line_color` | string | Optional hex |

Known `options` shapes:

- **Comment / text widget** (`widget_type_id=21`): on **write**, supply `{"comment_widget_text": {"text": "<h2>Hello</h2><p>World</p>", "contentAlign": "top"}}` in `rows[].options`. **The body is HTML** (Aug 2026 — see "The body is HTML, and only HTML" below). The tool auto-propagates this to `configs[].options.comment_widget_text`, on **update** as well as create (fixed Jul 2026 — update previously accepted these row options and wrote nothing, so the change appeared to succeed and the widget kept its old content). The legacy `{"text": "<html>", "comment": "<html>"}` row aliases also work for older accounts.
  - ⚠️ **Body text is required — a comment is nothing but its body.** `create` refuses a comment widget with no body content (Jul 2026): it would persist as a blank box while the call returned `success`, which is exactly how agents came to report section headers that were nowhere on the report. Supply the text, a background image, or `ai_text` (see "AI text on comment widgets"). Empty and whitespace-only text count as no body, because both normalise to a valid-but-blank paragraph.
  - ⚠️ **Structure comes from tags, not from newlines.** `<h2>Heading</h2><p>Body</p>` is two blocks whether or not there is a line break between them; `"Heading\nBody"` with no tags is one paragraph. LLM tool-callers also frequently double-escape control characters, sending the literal two characters `\` and `n` instead of a newline — those are converted on save, but they were never what created the blocks. If a rendered comment runs everything together, the body was missing its `<p>` and `<h2>` tags.
  - **The body is HTML, and only HTML** (Aug 2026). Put it in `comment_widget_text.text`. Two formats that used to be accepted are now **rejected**, because each failed in a way the tool reported as `success`:

    - **Markdown** — a comment renders it literally. `# Heading` reached the reader with the hash still on it. Send `<h1>Heading</h1>`.
    - **A Tiptap/ProseMirror document** in `description` — the renderer loads it strictly, so one unknown node, mark or attribute *anywhere* in the document blanks the **entire widget**. This is what put empty white boxes at the top of five customer report pages. There is no partial failure and no warning; the widget just renders nothing.

    Text with **no tags at all** is not rejected — it is kept as a single paragraph, and the response says so in `warnings`. If you wanted headings or separate paragraphs, add the markup.

    **Full vocabulary.** Everything outside this list is stripped on save and reported in `warnings`:

    | Category | Available |
    |---|---|
    | Blocks | `<p>`, `<h1>`–`<h3>`, `<ul>`, `<ol>`, `<li>`, `<blockquote>`, `<pre>`, `<hr>`, `<br>` |
    | Inline | `<strong>`, `<em>`, `<u>`, `<s>`, `<mark>`, `<code>`, `<a href>`, `<span>` |
    | Styles | `color` and `font-size` (8–96px) on `<span>`; `text-align` (`left`/`center`/`right`/`justify`) on `<p>` and `<h1>`–`<h3>`; `class` on `<p>` |

    `<h4>`–`<h6>` are demoted to `<h3>`, the deepest the editor renders. Unknown tags are unwrapped and their text kept. `<script>`, `<style>` and `<iframe>` are dropped with their contents. Link `href`s must be `http`, `https`, `mailto` or `tel` — anything else is stripped, because the report refuses to open it anyway.

    **Prefer the named paragraph classes over a raw `font-size`.** The product's own styles are:

    | Style | Size | Write it as |
    |---|---|---|
    | Heading 1 | 40px | `<h1>` |
    | Heading 2 | 30px | `<h2>` |
    | Heading 3 | 21px | `<h3>` |
    | Paragraph 1 | 18px | `<p class="p1">` |
    | Paragraph 2 | 16px | `<p class="p2">` |
    | Paragraph 3 | 14px | `<p class="p3">` — the default |
    | Paragraph 4 | 13px | `<p class="p4">` |

    A custom `font-size` is validated for range but still has a cost: a person who later touches the style picker in the UI **strips every custom size** in the block. The named classes above survive that. Use `font-size` only for a size the named styles do not offer.

    `<mark>` is **on or off** — the highlight takes no colour.

    **Worked example — kicker, heading, rule, body with value-coded emphasis.** This is the shape most report text blocks want:

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

    **Editing an existing comment.** Read `list-widgets action=show` and write `comment_widget_text.description` straight back — it always comes back as HTML, even for a comment written in the UI (which is stored as a Tiptap document and converted on read). So a read-modify-write round trip works, and saving an editor-written comment quietly migrates it to HTML.

  - **`contentAlign`** is `top`, `center` or `bottom`, and sets where the text sits vertically in the widget box. It defaults to `top`. Use `center` for a short hero line in a tall box — a one-line statement pinned to the top of a `6×3` widget looks like a mistake.
  - On **read**, `list-widgets action=show` returns the body as **HTML** under `options.comment_widget_text.description`, whatever it was written with — a comment authored in the UI is stored as a Tiptap document and converted on read, so what you read is what you can write. The plain text comes back under `.text`. A text/font **colour** baked into the comment content overrides the theme's `text_color` (CSS specificity), so applying a palette won't recolour comment text — set the colour with a `<span style="color: …">` for white-on-dark headers, or leave it uncoloured to inherit the theme.
  - **Background image — the cover and section-divider pattern.** Set `background_image_url` (public http/https URL) or `background_image_data` (base64-encoded JPG/PNG, max 10 MB), with optional `background_image_filename`, in `rows[].options`. The image renders full-bleed behind the text.

    This is how you build a report cover or a section divider in **one** widget instead of stacking an image widget above a text widget. Put the heading in the HTML body, set `contentAlign: "center"`, and give the text a light `<span style="color: …">` so it reads against the image. Import remote images first (see the assets skill) and check the resolution against the rendered width.
  - **Updating a comment widget — `rows[].id` is optional.** `manage-widgets update` carries forward the existing config's `integration_id` (and `source_id` / `report_type`) when you omit it. A row supplied **without** `rows[].id` updates the existing row in the same position, keeping its configs and their bindings — as of Jul 2026 it no longer rebuilds the row from scratch, which used to discard the comment's body and leave a blank widget. Pass `rows[0].id` (from `list-widgets action=show`) when you need to reorder rows or be explicit about which row you mean. Setting the text to `""` or whitespace is still refused — it renders as a blank box.
- **Image widget** (`widget_type_id=34`): supply `{"image_url": "<url>"}` or `{"image_data": "<base64 JPG/PNG>"}` (max 10 MB) with optional `image_filename` in `rows[].options`. `image_data` accepts a base64-encoded image directly — no multipart upload needed. The tool auto-propagates this to the config-side canonical shape `configs[].options.images: [{url, title}]`, on **update** as well as create (fixed Jul 2026 — swapping an image through update previously wrote nothing and left the old one in place). You can also supply the config shape directly in `rows[].configs[].options`. Additional display options: `background_size` (`auto_fit` | `scale_to_fit` | `scale_to_fill`) and `alignment` (`left` | `center` | `right`) — pass these in row options alongside `image_url`.
  - A malformed `image_url` (no scheme/host, or a non-http scheme) and invalid or oversized base64 are now rejected on update too, before anything is written — previously update accepted both silently.
- **Remote image URLs must be imported before widget use.** For `image_url` and a comment widget's `background_image_url`, do not pass an external URL: call `manage-assets action=import_url` with `target_scope=team` so the asset stays reusable, then `manage-assets action=publish` with the `asset.ulid` the import returned, and pass only the `url` that `publish` returns. A Whatagraph URL that is already published needs no import. `image_data` / `background_image_data` are unaffected — they carry the bytes already. If import or publish fails, fix the URL or ask the user for the image and leave the widget unchanged; never fall back to the raw URL and never invent a replacement. `manage-widgets` stores the URL verbatim and only checks its scheme and host, so an external URL stays a live hotlink: it can rot, sit behind a login, or block hotlinking, and one recalled rather than fetched may not exist at all — which is how a broken image reaches a customer's report. The same rule applies to theme header/footer `images[].url` via `manage-themes`.
- **Single-value KPI** (`widget_type_id=101`): set `{"comparison_display_type": "combined"}` (or `"percentage"` / `"absolute"`) to surface the trend delta vs. the comparison window inherited from the report. `compare_type` is not a valid widget option key — it is a date-range field and the widget rejects it.
- **Funnel** (`widget_type_id=115`): each funnel **stage is its own row** with a single metric — one metric per row, in stage order. Putting multiple metrics in one config renders a single 100% stage instead of a multi-stage funnel.
- **Goal widget** (`widget_type_id=123`): set `options.goal_date_range` with `start_date`, `end_date`, and `visible_time_line` (boolean — controls the "Time passed" indicator line). Each row represents a goal line and requires `options.title` (goal name), `options.start_value` (baseline, typically 0), and `options.end_value` (target number). Note that `options.title` only labels the line while it has no data — once the goal loads, the rendered label is the config metric's `name` (see "Renaming a metric caption"), so set both to the same text. `end_value` must be greater than `start_value`. The metric in `configs[].options.metrics` tracks progress toward the target.
- **Filter control** (`widget_type_id=137`): bind a **dimension** (not a metric) via rows — the widget renders as a dropdown filter that other widgets on the tab respond to. No date range is needed. Does not load data itself.
- **Gauge** (`widget_type_id=139`): dial-style single metric display. Same configuration as SingleValue (`101`) but different visual rendering — use when a circular dial is more appropriate than a plain number. Supports `start_value` and `end_value` in row options to set the gauge range.
- **Heatmap** (`widget_type_id=138`): heat-coloured grid of one metric across two dimensions — one becomes the rows, the other the columns (e.g. `sessions` by `deviceCategory` × `browser`). Bind **exactly 2 dimensions and exactly 1 metric** in a single config; anything else is rejected. `breakdowns_enabled` stays off. This is **not** configured like a SingleValue (`101`), which takes no dimensions at all.
- **GeoMap** (`widget_type_id=140`, BETA): geographic map. Set `options.geo_map_region` to control the displayed region (see Type-specific options table above). Bind a dimension with country/region data.
- **Dynamic chart** (`widget_type_id=142`): the type for chart families with no dedicated widget type — scatter, bubble (a third metric as point size), heatmap across two dimensions, candlestick, bars-plus-line combo, and ranked top-N. Bind rows as usual, then describe the chart with a `chart_spec`. Load the `whatagraph-dynamic-charts` skill before writing one; it is refused at create without a spec.
- **Media / creative preview** (`widget_type_id=110`/`111`): bind the image dimension to the channel's **thumbnail** field — Meta/Facebook uses `creative_thumbnail_url` (not `ad_name`, which is text). Google Search ads are text-only (no thumbnail); `ad_image_url` populates only for Display/PMax/image ads.
- **Report shortcut** (`widget_type_id=141`): a drill-down card linking to another report in the same team. `channel_id=7`, no `source_id`, no metrics/dimensions. Set the link in `rows[].configs[].options`:

  ```
  "rows": [{"configs": [{"options": {
    "linked_report_id": <report_id>,                # must belong to the team — cross-team IDs are rejected
    "linked_report_thumbnail_style": "card"         # card | image | title_only (optional)
  }}]}]
  ```

  Find target report IDs with `list-reports`. On read, `list-widgets action=show` returns a `linked_report` field with the target's name, URL, space, and last-edit info. Default size is 2×2. **Sharing cascade:** when the parent report is shared, every report reachable via report shortcuts is shared automatically (recursively, inheriting the parent share's password and date-lock settings) so drill-down keeps working in the public view.

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
   name="Clicks by Ad Group"
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
   name="Impressions vs Clicks"
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
     "summary_length": "long",      # or "short" — a sentence count, not a style; see below
     "custom_prompt": "...",        # required when types includes "custom"
     "auto_update": false           # false queues the summary now; true regenerates on every refresh
   }
```

Only comment widgets (`widget_type_id=21`) are supported. Unless `auto_update` is `true`, the call also queues the summary.

**The summary is not in that response.** Generation runs in the background, because reading every widget in a report takes longer than a tool call is given, so a large report used to return nothing at all. The call returns `status: pending` and a `summary_job_id`. Collect it with a second call:

```
manage-widgets action=update_ai_text report_id=<id> widget_id=<id> summary_job_id=<id>
```

`ai_text` is not needed on a collecting call. Read `status`:

| `status` | What to do |
|---|---|
| `pending` | Still generating. Wait a few seconds and call again. Do not poll in a tight loop. |
| `ready` | `content` carries the summary, already written to the widget. |
| `failed` | `message` says why. Queue a new one with `ai_text`. |
| `expired` | The job id is unknown or older than 24 hours. Queue a new one with `ai_text`. |

Queueing twice for the same widget returns the **same** `summary_job_id` rather than starting a second pass, so a retry is safe.

A sample-data refusal still comes back on the **first** call, not on a collect, so you learn immediately when every widget the summary would read serves sample data.

> `summary_length` is a **sentence count per type**: `short` = 3 sentences, `long` = 8. `types` stack — each one generates its own block — so `["summary","wins","issues","recommendations"]` at `long` produces roughly 32 sentences, and `["summary"]` at `short` produces three.
>
> - **`short` is for a caption beside a single chart.** Never use it on a full-width page-level block — a three-sentence summary in a full-width comment is the floor of what the feature can produce, and it reads that way.
> - Page-level default: `summary_length: "long"` with `types: ["summary","recommendations"]`; on an outcome or conclusion tab, `["summary","wins","issues","recommendations"]`.
> - On the report's **first** tab use `load_type: "full_report"`. A page-scoped summary of tab 1 cannot reference what the later tabs show, which is the entire point of an executive summary.
> - Pass `auto_update: false` on a build-and-hand-over run, then collect with the `summary_job_id`, so you can confirm the length you actually got. With `auto_update: true` only the settings are saved, nothing is queued, and the widget stays empty until the next refresh.
> - **Size the host comment to the text**: `6×3` minimum for `long` single-type, `6×4`–`6×6` for `long` multi-type. A long summary in a `6×2` clips or scrolls, and a scrolled block truncates in PDF export — check with `export-report` before shipping.

**`ai_text` is also accepted on `create`** (Jul 2026), taking the same fields, so an AI-narration comment is one call instead of a create followed by `update_ai_text`. When `auto_update` is `false` the create queues the summary and returns `ai_text_status: pending` with an `ai_text_summary_job_id`; pass that as `summary_job_id` to `update_ai_text` with the new widget's id to collect it. With `auto_update: true` only the settings are saved and neither key comes back. This is also how you create a comment with no hand-written body — `ai_text` satisfies the body-text requirement, since the AI supplies the content. Passing `ai_text` on any other widget type is rejected.

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

> **`remove_row` needs approval.** It deletes the row and its conditional formats. The first call returns a preview and changes nothing; resend the identical call with the `confirm_token` from that preview to execute it. `add_row` is not gated. See `whatagraph-deleting` → "The approval gate".

Multi-row widgets (combo charts, funnels, non-breakdown pie/donut) have one row per series or stage. Use `add_row` and `remove_row` to manage them without rebuilding the entire `rows` array.

```
manage-widgets action=add_row    report_id=<id> widget_id=<id>
manage-widgets action=remove_row report_id=<id> widget_id=<id> row_id=<row_id>
```

- `add_row` copies the last row's config (integration, source, report type) into a new row. Update the new row's metric afterwards with a regular `update`.
- `remove_row` deletes the row and all its config children (metrics, dimensions, report types) — including any conditional formatting on it, which the response reports in `warnings`. Cannot remove the last remaining row.
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

`batch_change_settings` takes the same option keys as `options`, so a `title` in `settings` is refused when any selected widget is a Comment (`21`), Calendar (`22`), Filter control (`137`), or Report shortcut (`141`) — the error names the offending widgets. Drop those from `widget_ids`, or drop `title` from `settings`.

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

## Conditional formatting

Colour a table cell by its own value. Two modes, per metric (per column):

- **Manual rules** — your thresholds, and **both** colours per rule: `text_color` and `background_color`, each independent and each optional. Set only `text_color` to recolour the number and leave the cell background alone. "Red under 100."
- **Auto colors** — one base colour for the background, shaded into seven tints across the column's own lowest-to-highest value. **You do not control the text colour**: it is contrast-derived per cell (dark on light tints, white on dark). "Heatmap this column."

**A metric uses one mode or the other, never both.** The renderer prefers the auto shade and never looks at the rules, so setting one mode clears the other and says so in `warnings`.

**Table (`102`) only.** Only the table renderer paints these colours. Every other widget type is rejected rather than storing rules that never draw. Offline tables (`126`) are not supported either — see "Faking a heatmap" for those.

```
list-widgets action=conditional_formats report_id=<id> widget_id=<id>
# → per metric: mode (`manual` | `auto` | `none`), auto_color, and every rule in evaluation order
# → narrow with metric_external_id=<id>

manage-widgets action=set_conditional_formats report_id=<id> widget_id=<id>
   metric_external_id="clicks"
   conditional_formats=[
     {"operator": "greater_than",  "value": 1000,                  "text_color": "#ffffff", "background_color": "#059669"},
     {"operator": "between",       "value": 100, "value_end": 1000, "text_color": "#2a2b30", "background_color": "#fde68a"},
     {"operator": "less_or_equal", "value": 100,                   "text_color": "#ffffff", "background_color": "#dc2626"}
   ]

manage-widgets action=add_conditional_formats ...   # appends, keeps existing rules
```

### Auto colors

No thresholds to author — pick a base colour and the column shades itself.

```
manage-widgets action=set_auto_colors report_id=<id> widget_id=<id>
   metric_external_id="impressions" auto_color="#059669"

manage-widgets action=set_auto_colors ... auto_color=null   # back to unformatted
```

The seven tints run light-to-dark from the column's own minimum to its maximum, recomputed on every render, and each cell's text colour is contrast-derived — auto colors takes no `text_color`, so if the ask names a specific text colour you need manual rules. Because the range is derived from the data, the colours move when the data does — which is what you want for "show me the big numbers" and wrong for "flag anything under target". Use manual rules when a specific number matters.

### Rules

| Field | Notes |
| --- | --- |
| `operator` | `greater_than`, `greater_or_equal`, `less_than`, `less_or_equal`, `equal`, `not_equal`, `between` |
| `value` | Number to compare the cell against. Required. |
| `value_end` | **Required for `between`**, which matches `value`..`value_end` inclusive. Ignored otherwise. |
| `text_color`, `background_color` | 6-digit hex (`#059669`). Independent and both optional — omit one to leave that half of the cell alone. Colour names and 3-digit hex are rejected; they render as nothing. |
| `position` | Evaluation order. Defaults to the array order you send. |

**First match wins.** The rules are evaluated in `position` order and the first one that matches paints the cell. Order from narrowest to widest, or a catch-all `greater_than 0` first will swallow every band after it.

### `set` is replace-all

`set_conditional_formats` makes the rules you send the metric's **complete** set — anything already there is deleted. Read first with `list-widgets action=conditional_formats`, or you will silently drop rules a user set in the UI. Two safe shapes:

- **Adding a band** → `add_conditional_formats`, which appends and leaves the rest alone.
- **Clearing a column** → `set_conditional_formats` with `conditional_formats=[]`.

### Reading back

`list-widgets action=show` flags each table metric with `has_conditional_format`, so you can tell which columns already carry rules without a second call. The flag appears only on table widgets. Use `action=conditional_formats` to read the rules themselves.

### Formatting is attached to the config, not the metric

Rules are stored against the widget **config** the row binds — the first config of the row, which is where the UI writes them too. Two consequences:

- **A rebuilt row loses its formatting.** The "omit `rows[].id` to rebuild the binding" workaround (see Common pitfalls) recreates the row, and formatting cannot outlive the row it hangs off. `manage-widgets` re-attaches the rules when only the config is replaced, and warns you in `warnings` when a removed row took its rules with it — but there is no way to move them across a full row rebuild. **Read the rules out first, rebuild, then write them back.**
- **`remove_row` discards them**, and reports how many in `warnings`.

`duplicate` and `batch_duplicate` carry formatting across correctly; no extra work needed.

Auto colors is stored in the config's `options.auto_colors`, so it rides along with any config edit — but a full row rebuild loses it the same way manual rules do.

## Layout grid model

The report uses a **6-column grid**. Every widget occupies a rectangle defined by four properties:

> **Grid width follows the report's layout.** Landscape (`printing_landscape_6x6`, the default) is the 6-column grid documented here. Portrait (`printing_portrait_4x8`) is a **4-column** grid — every width / `position_x` rule below caps at 4 instead of 6. Orientation is chosen at report create time (see `whatagraph-reports` → "Create a blank report in a space") and can't change once widgets exist. Landscape renders a wider, shorter page: favor wide rows.

> **A tab is a page.** In a PDF, each visible tab becomes exactly one page, as tall as its own content — tabs are never split and never combined. Thus a tall tab makes a tall page, not two pages. Put a section break on a new tab, not lower down the grid. See `whatagraph-export` → "PDF export".

| Property | Range | Default | Notes |
|---|---|---|---|
| `position_x` | 0..5 | 0 | Horizontal column (0-based). Must satisfy `position_x + width ≤ 6`. |
| `position_y` | 0..∞ | next row below existing widgets | Vertical row (0-based, no upper limit). |
| `options.width` | 1..6 | 2 | Width in grid columns. |
| `options.height` | ≥1 | 2 | Height in grid rows. |

> **Input/output asymmetry:** On **input** (create/update), pass `width` and `height` inside `options`. On **output**, they appear as **top-level** fields (`width`, `height`). When using `fields` filtering, use the top-level names: `fields="width,height"` — not `options.width`.

**Overlap rule:** On `create`, `update`, and `duplicate`, the server rejects widgets that overlap an existing widget — unless `auto_place=true`, which picks the nearest free slot instead. On `create`, when `position_x`/`position_y` are omitted entirely, auto-placement is the default. On `update`, overlap is checked when `position_x` or `position_y` is provided (the widget being updated is excluded from the check). `duplicate` and `batch_duplicate` auto-position the copy at the next available row.

**Inserting between two existing rows:** there is no widget-level way to do this — the row you want is occupied, and `auto_place=true` sends the widget to the nearest free slot instead of the row you asked for. Open the row first with `manage-report-tabs action=insert_row_space` (`position_y` = the row to open, `row_count` = the height of the widget you're adding), then `create` at that exact position. Never shift widgets one at a time to make room, and never rebuild the tab elsewhere — see `whatagraph-report-tabs` → "Insert or remove rows in a tab".

**Removing empty rows — "close the gaps", "compact the tab", "tighten it up", "remove the blank rows":** use `manage-report-tabs action=remove_row_space` (`position_y` = the first empty row, `row_count` = how many). Do **not** close gaps by moving widgets up one `manage-widgets action=update` at a time — that works (upward moves never collide) but takes one call per widget with no transaction, and it reflows the tab silently.

To clear **every** gap on a tab, expand each widget's rows from `position_y` + `height`, find the gaps between them, then call `remove_row_space` once per gap **working bottom-up** — closing a gap renumbers every row below it, so a top-down pass invalidates the ranges you computed. The rows must already be empty: the call is rejected if a widget occupies or reaches into them, and the error names both the blocking widget ids and the rows that *are* free.

⚠️ **A request for "a row" or "a line" is a request for empty space, not for a widget.** `insert_row_space` completes it on its own. Don't invent a widget to fill the gap — a placeholder Comment reading "New row" is filler in a client-facing report. Only create a widget when the user named one, and never guess its type or content.

### The layout comes from the data and the user, not from a default

**There is no house layout, and no default report structure.** The tab's shape is decided fresh each time, in this order of priority:

1. **A reference was provided** — a PDF, screenshot, live-report URL, or an existing report → **replicate its structure** (see "Replicating a reference report"). Don't normalize it to a layout you prefer.
2. **The user described what they want** → build to that intent: the metrics, breakdowns, and emphasis they asked for. But a description of *what a tab is about* is not a description of *the layout*: a tab named with a theme or a metric list ("Google Ads: performance widgets for spend, clicks, impressions, conversions") fixes the tab's focus and which metrics must appear — the page composition around them still follows case 3 and "Composing a full tab" in full. Only an actual widget-by-widget spec pins the layout itself.
3. **No reference and no widget-level spec** → *you* decide what's worth showing and how. This is a judgment call, not a fallback skeleton: look at the data that's actually available (which metrics, which dimensions), pick the most meaningful KPIs, choose the best visualization for each (see below), and arrange them in a sensible information hierarchy. Different sources and metrics should produce different reports — if every report you build looks the same, you've defaulted to a template.

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
- **A cover, hero banner, or visual divider** → an Image widget (`34`), full-width `6×2` — a generated or brand visual that opens the report's first tab or marks a major transition. Import the image via `manage-assets` first (see the image-import rule); use sparingly — one hero on the first tab, not a banner on every page.

**Let dimension cardinality narrow the choice.** How many values a dimension has decides which of the above actually reads well:

- **Few categories (≈2–7)** → pie / donut work as a share-of-whole; a bar / column chart also reads cleanly.
- **Many categories (dozens+)** → a pie/donut becomes an illegible confetti of slices and a bar chart runs off the axis. Use a **table** sorted by the primary metric, or a bar/column chart **limited to the top N** (see "Surfacing a top / bottom N" below). Never bind a high-cardinality dimension to a pie or donut.
- **Continuous over time** → line / area with the date dimension, regardless of how many dates.

Canonical mappings that follow from this: **gender split → pie/donut, never a table**; device category → donut; channel grouping mix → donut; age brackets → column chart; campaign / landing-page / search-term detail → table sorted desc by the primary metric; staged conversion path → funnel; country/region → GeoMap; ad creatives → Media with the thumbnail dimension.

When unsure of a dimension's cardinality, check it before choosing the widget — a breakdown that looks fine on sample data can overflow on the real account.

Compose by analytical priority: surface the few numbers that matter most first, then the main trend, then the breakdowns and detail. But the **selection, mix, and count** of widgets follow from what the data supports — so they vary from report to report. Don't force a fixed set or a minimum count.

**Pick metrics for meaning, not availability.** When choosing metrics yourself, the most valuable numbers are outcomes and efficiency, not raw volume: conversions, revenue, cost per conversion / ROAS tell the reader what they *got*; impressions and clicks only tell them what happened along the way. A strong headline row reads like a sentence — *what went in → what came out → what it cost per result* (e.g. spend → conversions → cost per conversion) — not a lineup of disconnected counters. Volume metrics still belong in the report, but paired with the rate that makes them meaningful (impressions with CTR, clicks with conversion rate), usually in the trend and breakdown sections rather than the headline row. And each tab answers its own question: a conversions tab leads with conversion outcomes, an audience tab with audience splits — not the same spend/impressions cards repeated from the overview. (If the user named the metrics, bind exactly those — this heuristic only fills gaps.)

**Show a variety of widget types.** When you are choosing the layout yourself — no reference and no specific ask — a good report uses a *mix* of the types above rather than a wall of the same widget: typically a row of KPI / SingleValue cards for the headline numbers, one or more charts (a trend line/area plus a breakdown bar / column / donut), a detail table, and media or funnel widgets where the data supports them. Match each type to the data as described above; the point is that a self-directed report should demonstrate the format's range, not repeat one widget. If the user specified the widget types, follow their choice instead of diversifying. For how to arrange the mix into a complete page — headers, pairing, row rhythm — see "Composing a full tab" below.

### Titles — every widget and every metric row is labelled

Every data widget carries a **title**, and every metric row carries a **row label** — never ship an untitled widget or an unlabelled series. A reader scanning the report should know what each widget shows without opening its config.

- Set the widget title via `name` on create/update, and confirm it isn't suppressed by `hide_title` (see Display toggles).
- Set each row's metric label in **`rows[].configs[].options.metrics[].name`** — on every current-generation type (`101`–`123`, `137`–`140`) that is the caption the reader sees. For multi-row charts, funnels, and non-breakdown pie/donut, give **each** row's metric its own `name` so every series / stage / slice is named. Rename a dimension label the same way, with `rows[].configs[].options.dimensions[].name`.
- **Never label a row with `rows[].options.title` or `rows[].options.metrics[].label`.** The first is only a pre-data placeholder, the second is read by nothing — writing to either succeeds and shows nothing. See "Renaming a metric caption" below for the full rule and its exceptions.
- Utility widgets (Comment `21`, Image `34`, Calendar `22`) are exempt from the metric-row rule, but a Comment used as a section header still carries its heading text.
- **Comment (`21`), Calendar (`22`), Filter control (`137`), and Report shortcut (`141`) render no title at all and reject `name` / `options.title`.** Don't try to label them — a Comment's heading lives in its body text (`comment_widget_text.text`, markdown `#`), and the other three are labelled by what they contain. Image (`34`) does render a title.
- The title states what's shown (metric + scope). Because the title makes a promise to the reader, the bound fields must actually deliver it — see "Fit for purpose" below.
- **On editorial tabs, let titles carry the argument.** A widget title can state the finding or define the measure, not just name the metric — the professional pattern is `Claim or metric — what it means / how it's defined`: "Commits per engineer per month — the only comparable measure", "Bus factor — engineers needed to cover half of all commits", "Adoption is not evenly spread — share of each engineer's commits that are agent-signed". Use it when the widget is an exhibit in a story; keep plain descriptive titles ("Sessions by channel") on dashboard tabs where the reader scans rather than reads. Never title a widget with a claim its data doesn't show.

#### Renaming a metric caption

⚠️ **There is exactly one writable field for this, and the widget carries decoys that look more like it.** A `list-widgets action=show` response shows the old metric name in both `rows[].options.title` and `rows[].configs[].options.metrics[].name`. Only the config one is the rendered caption; the row title is the pre-data placeholder. Writing to the row title is accepted, returns `success`, changes the stored row, and changes nothing the reader sees. Do not copy the shape you see in the `show` response — go straight to the config metric. `manage-widgets` returns a warning if you set a row-level label without a config metric `name`.

To change the metric label a reader sees — "Clicks" → "Hot Leads" — set the `name` on the **config** metric:

```
manage-widgets action=update widget_id=<id>
  rows=[{id: <row_id>, configs: [{id: <config_id>, channel_id: <channel_id>, source_id: <source_id>,
    options: {report_type: "<report_type>",
              metrics: [{external_id: "clicks", name: "Hot Leads", identifier: 0}]}}]}]
```

Carry `channel_id`, `source_id`, and `report_type` on the config, exactly as with any other in-place config edit — a metric-only update can rebuild the config without its report-type binding and blank the widget.

Nothing else is needed: when a request leaves `rows[].options.title` unset, `manage-widgets` copies the config metric names into the row display options for you, so the editor chip and the rendered caption stay in step.

**Why the two decoys fail, in detail:**

- `rows[].options.title` is the placeholder the renderer shows *before* data arrives; once the widget loads, the caption is the config metric's name. Setting it on its own reads back as `success`, looks right for a moment, then reverts to the old metric name as soon as the data lands. Worse, an explicit `options.title` in the request suppresses the automatic mirroring above, so the two fields stay in disagreement — which is the state that produces this bug.
- `rows[].options.metrics[].label` is not read at all on a current-generation widget — not by the renderer, not by the editor, not by the backend. It is a leftover from the pre-new-architecture widget shape that premade and seeded widgets still carry. New-arch code reads only `decimal_place`, `width`, and `sort` out of `rows[].options.metrics[]`. A rename written to `label` is invisible from the moment it is stored. Since Aug 2026 the widget tools strip it from responses on types `101`+, so you should not see it at all; on an older deployment it still comes back holding the metric's name, and it is still inert there.

Change the config metric name; leave both of these alone.

This holds for every type that renders a metric label:

| Type | Where the rendered label comes from |
|---|---|
| SingleValue `101`, Gauge `139`, List `103` | Config metric `name`. Row `options.title` shows only until data loads. |
| Charts `104`–`107`, `115`, `118`, `119`, Pie/Donut `108`/`109` | Config metric `name`. Series names never fall back to the row title. |
| Table `102`, Media `110`/`111`, Heatmap `138`, GeoMap `140` | Config metric / dimension `name` — column headers included. |
| Goal `123` | Config metric `name` for the goal line's label. `options.title` is still required at create, and is what shows while the line has no data. |

Three real exceptions, where the row-level field **is** the label:

- **Multi-channel formula rows** — a row carrying `options.operators` is captioned by `rows[].options.formula_title`, falling back to `options.title`. There is no config metric to name, because the row renders a calculation over its configs rather than one of them. See "Formula rows".
- **Offline widgets (`125`–`136`)** — the label is the `name` on each entry of the row's `data` array. Config bindings are rejected on these types.
- **Pre-new-architecture types (below `101`)** — the old renderer really does read `rows[].options.title` first. Only relevant on legacy widgets; create everything new at `101`+.

### Section headers — introduce each section of a tab with a Comment widget

A tab that holds more than one group of content (a KPI block, then a trend section, then a breakdown / detail section) should **introduce each group with a section header**: a full-width Comment widget (`21`, `channel_id=7`) carrying a short heading — the report-page equivalent of an `<h2>` in a document.

- **Shape:** full row (`width: 6`), `height: 1` for a bare heading (a heading plus a one-line subtitle needs `height: 2` — see Comment sizing above). Place it as the first row of the section it introduces.
- **Text:** an HTML heading in `rows[].options.comment_widget_text.text` — e.g. `<h2>Campaign performance</h2>` — naming the section's theme, not repeating the widget titles below it. Keep it to a few words; optionally add one `<p>` of context beneath the heading. Colour, size and alignment go inline — see the Comment widget notes under `### options`.
- **When to use one:** whenever a tab has two or more distinct sections — which a full, self-directed tab always does by default, since two sections is the floor (see "Composing a full tab"). The tab's *first* header also serves as the page title when the tab name alone isn't enough.
- **When not to:** a tab that is genuinely one section (a single full-page table the user asked for, a lean one-pager) doesn't need a header row per widget — headers earn their row only when they separate something. Never stack two headers with no content between them.
- **A section header holds ONLY the `<h2>` line.** Body copy — an intro paragraph, narrative text, or an AI summary — is a **separate** comment widget sized per the Comment sizing rule (`height: 2` for 1–2 sentences, `height: 3` per paragraph, `height: 4+` for a multi-paragraph AI text block), and body copy is `<p>`, never a heading. Never append body text to a 6×1 header — a 6×1 comment fits exactly one short heading line, nothing more.

### Narrative comments — openers and takeaways for editorial tabs

Where a bare `## …` header labels a dashboard section, an **editorial tab** opens and closes with a *narrative comment* — a single Comment widget whose typography does the framing. The professional pattern is three levels in one Tiptap `description`:

1. **Kicker** — one short ALL-CAPS line, small and muted (`fontSize: "12px"`, bold, a gray such as `#7c8794`): the report/section eyebrow, e.g. `ENGINEERING PERFORMANCE · Q3 2026` or `THE CASE, IN ONE PARAGRAPH`.
2. **Headline** — one bold, large line (`fontSize: "28px"`–`"32px"`) that states the page's **claim in plain words**: "The team got smaller. The output went up." — never a label like "Overview" or "Performance".
3. **Body** — one or two paragraphs at `14px`–`15px` carrying the evidence in prose, with real numbers from the data ("per-engineer throughput went from 19.9 to 49.0 commits a month"). An optional final `12px` muted line can carry sources or methodology.

```
"comment_widget_text": {
  "description": {"type": "doc", "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "Q3 PERFORMANCE · ACME", "marks": [{"type": "bold"}, {"type": "textStyle", "attrs": {"fontSize": "12px", "color": "#7c8794"}}]}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "Spend fell 12% — conversions didn't.", "marks": [{"type": "bold"}, {"type": "textStyle", "attrs": {"fontSize": "30px"}}]}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "Efficiency gains in Search offset the budget cut: CPA improved from $41 to $33 while conversion volume held flat.", "marks": [{"type": "textStyle", "attrs": {"fontSize": "14px"}}]}]}
  ]},
  "contentAlign": "top"
}
```

- **Size:** `6×2` for kicker + headline + a sentence or two; `6×3`–`6×4` when the body runs to full paragraphs (a closing "what it all means" block). Hold the copy to the box's budget (see Comment sizing under "Sizing"): if the prose outgrows the height, trim it or grow the widget before writing — overflow is invisible to the API and only shows up in the rendered report. Size the block to its content and never leave a dead grid row at the bottom of a comment.
- **Comment typography has no automatic spacing between a heading and the text under it.** The stylesheet's tightest elements carry no bottom margin (`p.p4` none, `h2` almost none, `<hr>` unstyled), so a heading stacked directly on body text renders as a cramped block with the body touching the headline. Build openers with explicit spacing:

  ```html
  <p class="p3"><strong><span style="color: #7c8794">EYEBROW · CLIENT</span></strong></p>
  <h2>The chapter's claim in one line</h2>
  <p class="p3"><br></p>
  <p class="p3">One or two sentences of scope, with real numbers.</p>
  ```

  - Put the kicker in `p3`, which has a bottom margin — not `p4`, which has none.
  - An empty `<p class="p3"><br></p>` between the headline and the body is the only reliable spacer — its Tiptap equivalent is an empty `{"type": "paragraph"}` node between the headline and body paragraphs. Without it the body touches the heading.
  - **Do not put `<hr>` between the headline and the body.** If a rule is wanted, put an empty paragraph on both sides of it.
- **Write the numbers in.** A narrative comment with real figures from the data reads as insight; one full of generic filler ("performance was strong this period") reads as padding — pull the figures from the widgets you just built (`csv_export`) or skip the claim.
- **Colors:** the muted-gray kicker is safe on light themes; for the headline and body, prefer setting `fontSize` only and letting the text color inherit from the theme — a hard-coded near-black breaks on dark themes (a baked-in color overrides the theme's `text_color`). Bake colors in only when you know the theme.
- **Takeaways close the loop.** A tab that argues something ends with a `6×2`+ narrative comment stating what the evidence means (kicker + body, no big headline needed). Don't bolt the takeaway text onto a header or an existing comment — it's its own widget, last row of the tab.

### Fit for purpose — fields must match the intent and each other

Whatever the widget's stated purpose is — the user's prompt, or the widget's own title — the bound fields must serve it, and they must be mutually compatible. Selecting fields that don't fit the title, or that don't belong together, produces a misleading, blank, or erroring widget.

- **Fit the purpose.** A widget titled "Spend by campaign" binds a cost metric and a campaign dimension — not impressions and date. A "Conversion rate over time" widget binds a rate metric and the date dimension. Read the intent (prompt or title), then pick the metric(s) and dimension(s) that answer it. If you set the title, the fields must deliver what the title promises.
- **Metric ↔ dimension compatibility.** Only bind dimensions the metric can actually be broken down by. Look up what a source exposes with `list-sources action=list_dimensions_and_metrics` rather than assuming a dimension exists — availability is integration- and report-type-specific.
- **`report_type` compatibility.** Every metric and dimension in a config must belong to the **same `report_type`**. Mixing a metric from one report type with a dimension from another yields an "Unavailable report type" error or a blank widget. Choose the report type that carries all the fields the widget needs, and set it in `configs[].options.report_type`.
- **Widget-type compatibility.** Respect the "Dimension requirements by widget type" table above — e.g. a time-series chart needs the integration's date dimension, a heatmap needs exactly two dimensions, a SingleValue takes none, a GeoMap needs a geographic dimension. Don't bind a field the widget type can't use.
- **Verify.** After binding, confirm with `export-report` or `list-widgets action=csv_export` that the widget returns the metric and breakdown the title implies — not an unrelated or empty result. (`list-widgets action=show` echoes ids, not loaded data.)

### Sizing — driven by content, not a fixed table

Size scales with data density: the more rows / series / columns a widget carries, the larger it should be — grow a table's height with its row count and give the tab's centerpiece chart the widest slot, rather than shrinking dense content to fit a slot. **A widget carrying a lot of data gets more area, not a scrollbar.**

Pick each widget's size from what its content needs to be legible, then fit it into the row you're building. These are affordances, not defaults:

- **KPI / SingleValue / Gauge / Goal** — just a number; keep it small so several share a row. A full-row single value reads as a header.
- **Table / MultiSource / Heatmap** — needs width or columns truncate; usually most or all of the row, taller as rows grow.
- **Line / Area / time-series chart** — needs width for the trend to be legible (often the full row). Also needs its **date dimension** bound (see "Dimension requirements") or it collapses to a single value.
- **Bar / Column chart** — compact when paired with a sibling, full-width when it's the focus.
- **Pie / Donut** — roughly square; a full-row pie wastes space.
- **List / Funnel** — narrow-to-medium; sit well beside a chart.
- **Media / creative preview** — one tile per creative, grouped across a row.
- **Comment** — full-row as a section header/divider, or taller for an AI text block. **Size the height to the text it holds:** `height: 1` fits only a single short heading line; a sentence or two needs `height: 2`; a full paragraph `height: 3`; a multi-paragraph AI summary `4+`. Under-sizing clips or overflows the text in the rendered report, so when in doubt give it more height — and prefer splitting a long block across widgets (or trimming the copy) over cramming it into a short box. **Budget the copy against the box before writing it:** on the 6-wide grid, one grid row of height holds roughly two lines of 14–15px body text (≈ 160–200 characters), and a large narrative headline (28–32px) consumes most of a row by itself — so a `6×2` opener fits a kicker line, a headline, and about two short sentences, no more. The API gives no overflow signal — the write succeeds whether the text fits or not — so count the text first, and when it exceeds the budget, grow the widget or cut words; never ship prose that outruns its box.
- **GeoMap** — medium.

**Hard constraints (always):** `width` 1..6, `height` ≥ 1, `position_x + width ≤ 6`, and no two widgets overlap.

### Titles: when they show, and how long they can be

**A `height: 1` widget shows no title at all** — at that size the renderer hides the title, the description, the icon and the footer. The same applies at `width: 1`, with one exception: a SingleValue that is 1 wide and 2 or more tall does show its title. So a `6×1` Comment used as a section header is fine (its heading is body text), but a `4×1` chart with a `name` renders that name nowhere.

When a title does show, it is **clamped to one line** and cut with an ellipsis. It never wraps. Budget:

| `width` | Title space | Safe title length |
|---|---|---|
| 1 | 184 px | ~16 characters |
| 2 | 426 px | ~38 characters |
| 3 | 668 px | ~60 characters |
| 4 | 910 px | ~84 characters |
| 6 | 1394 px | ~128 characters |

The pixel figures are exact. The character counts are measured against a wide bold sans at the default title size, so they are a safe floor — a narrower theme font fits more. A theme with a larger title font fits less, so verify if the theme is not the default.

### Placing widgets cleanly

Once you know the structure, lay it out top to bottom:

1. **Work in rows.** Each row's widths sum to ≤ 6. Track the running `y` — a row of height-2 widgets at `y=0` means the next row starts at `y=2`.
2. **Set `position_x` / `position_y` / `width` / `height` explicitly** on every widget so rows land where you intend. `auto_place=true` (the default when you omit position) just drops a widget in the next free slot — fine for a one-off add, not for a designed or replicated layout.
3. **Pack to match your intent** — no gaps and no overlaps, but mirror the *reference's* density: don't tighten a deliberately sparse page, don't pad a dense one.
4. **Fill each row left-to-right and start the next row flush against the previous one.** A row's widths sum to ≤ 6; if a row doesn't reach 6, widen a widget or add another rather than leaving a trailing gap. Don't leave an empty column mid-row or an empty row between populated rows — the only intentional blank space is one a *reference* deliberately shows (see "Replicating a reference report").
5. **Standard row recipes on the 6-column grid** (starting points, not the only options): three KPI cards = `2+2+2` (h2 — never `3+3` two-across; the value font doesn't grow with width, see "KPI card geometry" under Composing a full tab); two charts = `3+3` or `4+2` (h3); full-width table or trend = `6` (h3, taller as row count grows — a widget carrying a lot of data gets more area, not a scrollbar); section header comment = `6×1`; three creative tiles = `2+2+2` (h3).
6. **Build, then verify** with `export-report` (or `list-widgets action=csv_export`) — confirm the layout and that every widget loaded data. `list-widgets action=show` echoes positions but not rendered data.
7. **Finish with styling.** Once every tab is composed and verified, load `whatagraph-themes` and apply a theme and color palette (client branding when known, otherwise a coherent team theme). An unstyled report is an unfinished report — see `whatagraph-reports` → "Style the report before handing it over".

### Composing a full tab (self-directed builds)

When you're deciding the layout yourself — no reference, no explicit widget list — each tab is a **complete page with a visual rhythm**, not a strip of cards or a lone widget. **This section applies just as fully when the tabs were named for you** — by the user's prompt or an agent's instructions ("build these 6 tabs: Overview, Google Ads, Meta Ads, …"). A named tab with a theme or metric list scopes the page's *subject*; the page itself is still yours to compose, and it gets the complete treatment below. The failure modes to design against: a tab holding one or two widgets adrift in an empty grid (the classic outcome of misreading a tab list as a widget list); a row of identical KPI cards plus one chart and nothing else; a tab whose only occupant is a single table floating in empty space; every tab in the report shaped the same way.

**First, pick the tab's composition mode.** There are two ways a tab clears the bar, and a report may mix them — choose per tab, by what the page is for:

- **Dashboard mode** — the page is a working surface the reader scans for numbers: an operations tab, a campaign monitor, a per-channel performance page. Multiple header-led sections, a dense varied mix, typically 8–14 widgets.
- **Editorial mode** — the page is a *chapter in an argument*: an executive summary, a monthly story, an analysis that builds to a conclusion. Fewer but **larger** widgets (3–8 per tab), each one a deliberate exhibit, wrapped in narrative: a styled opener that states the chapter's claim, and a closing takeaway that says what the evidence means. Editorial tabs earn their lower count by making every widget substantial (`3×4`, `6×4`, paired `3×6` tables — not token `2×2` cards) and by filling the page vertically just as fully.

When the user's ask reads like a deliverable someone will *read* (client story, executive briefing, year-in-review, analysis "of what happened"), default to editorial; when it reads like a surface someone will *monitor*, default to dashboard. Either way, plan the tab as a sequence of moments before you place anything, and fall back to a single lean section only when the user explicitly asked for a one-pager.

**Anatomy of a dashboard tab** (an ordering principle, not a fixed list — every element must still be justified by the data):

1. **Section 1 — a header** (Comment `6×1`) naming the page or its first section.
2. **A headline row** — 2–3 small KPI cards (`2×2`, three across — see "KPI card geometry" below) carrying the tab's most important totals. Vary the form across tabs: a Gauge or Goal where there's a target, a List where several small numbers belong together.
3. **A main visual row** — the tab's centrepiece, usually a wide trend or comparison chart. Pair it rather than leaving it alone: a `4×3` chart beside a `2×3` list/donut/KPI, or two `3×3` charts side by side.
4. **Section 2 — another header**, then **breakdown / detail rows** — a full-width table, or a table beside the donut/bar that summarizes it; a GeoMap for geography; Media tiles for creatives; a Funnel for staged conversions.
5. **Section 3 where the data supports it** — a further header plus secondary breakdowns, a narration Comment, or an AI-summary block. Most metric-rich sources support a third section on at least some tabs; reach for it rather than stopping at two.

**KPI card geometry decides how big the number looks.** The SingleValue value font is tiered by card size, not fluid — three fixed steps, not a smooth scale:

| card size | how the number reads |
|---|---|
| exactly 1 column wide | smallest tier; footer and icon are hidden (the title too, unless the card is ≥2 rows tall) |
| 2–3 cols wide, ≤3 rows tall | standard tier — the same size at `2×2` and at `3×2` |
| ≥3 cols wide **and** ≥4 rows tall | large tier (roughly double) |

- **Default KPI cards are `2×2`, three across.** Never `3×2` two-across: identical number, twice the box, half the card empty — it reads as a small number in a large frame, which is the most common complaint about agent-built KPI rows.
- A hero number needs a card that is **at least 3 columns wide AND at least 4 rows tall**. `3×3` is still the standard tier — height is the lever people miss.
- Make a SingleValue exactly 1 column wide only deliberately (a narrow editorial KPI strip at height ≥2, where the title survives) — never for a headline number, and never at height 1, where the title vanishes too.
- Set `vertical_text_alignment: "center"` and `horizontal_text_alignment: "center"` on every SingleValue unless you have a reason not to. The defaults park the value in the bottom-left corner of the card, which makes a wide card look emptier still.
- **Never let the widget title and the metric caption be the same string.** A card showing "Sessions" in bold, "Sessions" again small, then the number, is two labels doing one job. `hide_title` is rejected on SingleValue, so the caption is the only lever: set `rows[].configs[].options.metrics[].name` to something complementary (`"Last 30 days"`, `"vs previous period"`) and keep the metric name in the widget `title`.
- `shorten_numbers: true` only on cards ≤2 columns wide, where 6+ digits would clip.

**Anatomy of an editorial tab** (equally a principle, not a template):

1. **A narrative opener** (Comment, `6×2`) that *frames the chapter*: a small muted kicker line, a large bold headline that states the claim ("The team got smaller. The output went up." — not "Overview"), and one or two sentences of supporting context with real numbers. Built with a Tiptap `description` for the typography — see "Narrative comments" below. On the report's first tab, an **Image widget hero banner** (`6×2`, a generated or brand visual imported via `manage-assets`) may sit above the opener as a cover.
2. **The evidence** — 3–8 substantial widgets that develop exactly the claim the opener made, in whatever geometry the evidence needs: a strip of six narrow `1×2` KPIs; a `6×4` full-width chart whose title carries the argument; two `3×6` tables side by side comparing cohorts; a `2×2` grid of four `3×4` charts; a `6×5` heatmap-style table. The geometry varies chapter to chapter — an editorial report where every tab has the same shape has stopped telling a story.
3. **A closing takeaway** (Comment, `6×2`–`6×4`) that says what the evidence on this page *means* — the sentence the reader should leave with, plus caveats or a pointer to the next chapter. The report's final tab typically closes with the whole argument in one block ("The case, in one paragraph"). An AI-text comment can serve as the takeaway when hand-written insight isn't available.

**Composition rules that make it read well:**

- **Pair, don't strand.** No widget sits alone on a row unless it's genuinely full-width (a `6`-wide table, trend chart, or header). A small widget with 4 empty columns beside it is a layout bug — widen it, pair it, or move it into another row.
- **Adjacency is meaning.** Widgets that answer the same question sit next to each other: the KPI and the trend that explains it, the donut and the table that details it, the map and the top-regions list. A reader should be able to say what each *row* is about, not just each widget.
- **Vary the forms — within the tab and across tabs.** A tab drawing only on KPI cards and one chart type looks machine-generated. Draw on the full range the data supports (see "Choosing a visualization"), and don't repeat the same overview shape on every tab — the spend tab, audience tab, and creative tab should each look like what they're about.
- **Depth over sprawl — and fullness over count.** The real invariant is that **the page is full**: content develops down the grid (typically 8–14 grid rows) with no dead space, and every widget earns its place. Widget count follows the mode — a dashboard tab lands around 8–14 widgets across two or more sections; an editorial tab lands around 3–8 *larger* widgets wrapped in narrative, and is every bit as finished. Never pad with near-duplicate widgets to hit a count — but equally, never stop at a half-empty page because something rendered. A tab with one or two token widgets satisfies neither mode.
- **Give every KPI card its own icon.** A headline row of SingleValue cards is where the reader's eye lands first, and the icons are half of what distinguishes one card from the next. Pick each one for the metric it sits on (see "Row icons") — a row of identical eye icons is the signature of icons left unset.
- **End flush.** The last row fills its width like every other row. If the tab ends with a `2`-wide orphan, rebalance the final rows (widen the table, resize the pair) so the page bottom is a clean edge.
- **Too thin to fill?** If a theme can't sustain a full page from the available fields, don't pad it — merge it into a related tab (see `whatagraph-reports` → "Building a report when the request doesn't specify structure").

### Replicating a reference report (the priority when one is given)

Reproduce the reference faithfully — do not substitute a default arrangement:

- **Recreate every element**, in the same top-to-bottom order — KPIs, charts, tables, funnels, ad/creative tiles (Media `110` / `111`), comments/text. Don't drop or invent widgets.
- **Match per-row counts and proportions.** Count how many widgets share each row and split the 6 columns to mirror their relative widths: 3 across ⇒ `width 2` each; 2 across ⇒ `width 3` each; one full-width ⇒ `6`; an uneven pair (wide chart + narrow KPI) ⇒ e.g. `4 + 2`.
- **Match the widget type to what's shown** — a donut stays a donut, a funnel stays a funnel; don't swap in your preferred type.
- **Preserve spacing and density** — same sequence, and leave an empty row where the reference shows a gap.
- **Ignore account / source names** printed on the reference (e.g. "Account: …") — that's metadata, not a filter.

### Examples — illustrations of range, NOT templates

Different requests produce different shapes. **Copy the user's intent or reference — never copy these.** They exist only to show that the structure should vary:

- **Dense paid-media page (dashboard mode, varied, many widgets, two sections):** *Section 1* — a `6×1` header comment; a row of three KPIs `2×2`; a donut `3×3` beside a table `3×3`. *Section 2* — a second `6×1` header; a full-width detail table `6×3`; a row of three ad creatives `2×3`. (Coordinates for this one shape: header `x0 y0 6×1`; KPIs `x0/x2/x4 y1 2×2`; donut `x0 y3 3×3` + table `x3 y3 3×3`; header `x0 y6 6×1`; table `x0 y7 6×3`; media `x0/x2/x4 y10 2×3`.)
- **Editorial headline chapter (a report's opening tab):** hero Image `6×2` at `y0`; narrative opener comment `6×2` at `y2` (kicker + claim headline + context); a strip of six narrow KPIs `1×2` at `y4`; a full-width at-a-glance table `6×4` at `y6`; a closing takeaway comment `6×2` at `y10`. Five rows, page full, only 10 widgets — and it reads like a magazine cover, not a dashboard.
- **Editorial comparison chapter:** narrative opener `6×2`; two tall tables `3×6` side by side comparing cohorts (periods, segments, regions). Three widgets, full page — the pairing *is* the argument.
- **Editorial evidence chapter:** narrative opener `6×2`; a `6×4` full-width chart whose title carries the finding; a `2×2` grid of four `3×4` supporting charts/tables; closing takeaway `6×2`.
- **Lean summary (sparse, few widgets):** three KPIs `2×2` across the top, then one full-width trend chart `6×3`. Nothing more — don't pad it out. This shape is for when the user *asked* for a lean one-pager — an open-ended "create a report" gets a full composition (see "Composing a full tab"), not this.
- **Exec narrative (text-led):** an AI-summary comment `6×3` at the top, then two supporting visuals `3×3 + 3×3`.
- **Uneven split:** a wide trend chart `4×3` beside a tall KPI list `2×3`.

If your output looks like the same example every time, you've defaulted to a template — go back to the user's request or reference.

## Tables truncate silently

**A Table or List renders only the rows that fit its box. It drops the rest with no marker** — no ellipsis, no cut-off row, no scrollbar in the PDF, and no warning when you write the widget. `csv_export` and `export-report` still return every row. Thus a data check passes while the rendered report is wrong.

This is why the defect survives review: on screen the widget scrolls, so a person who scrolls the report sees all the rows. A PDF cannot scroll, so it keeps only the first screenful. The same widget is correct on screen and wrong in the file.

### What sets the number of rows that fit

Two quantities are fixed. Neither one adapts to your data:

- **Row height is fixed.** Rows do not shrink to fit. A row is short when the table shows dimensions as columns. It is taller when the table does not, and it grows with the number of dimensions.
- **Widget height is fixed by grid units, not by the tab.** A widget with `height: h` always renders the same number of pixels tall, whatever else is on the tab. Two tabs with the same widget give that widget the same height. Height is linear in grid units.

As a working figure, **a table shows approximately `3.5 × height − 3` rows.** A `height: 5` table shows approximately 14 rows.

Use that number to budget, not to prove. The exact count moves with the theme font size and with the number of dimensions. Tall tables have also been seen to stop well short of the figure. **Never trust the arithmetic alone. Always confirm the last row.**

### What to do

1. **Budget the height from the row count before you place the widget.** Give a table a `height` of at least `(rows + 3) ÷ 3.5`.
2. **For 20 or more rows, split the data into two side-by-side tables** (`3 + 3`). Each table then shows half the rows. This is the most reliable fix.
3. **For 15 or more rows that carry one value each, use a Bar chart.** Charts scale to the space they get. They never drop a series.
4. **After you render, confirm that the last row of every table is present.** This is the only check that finds the defect. Use `preview-report tab_id=<tab_id>` and look at the returned image. If you do not have `preview-report`, render with `export-report format=pdf` and ask the user to check, and tell them which tables and which rows to look at. See `whatagraph-export`. Examine the PDF yourself when you can read files; otherwise ask the user to look, and tell them which tables and which rows to check.

A taller widget does show more rows, but sometimes fewer than the arithmetic promises. Verify — do not assume.

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
- Open or close space between existing rows — use `manage-report-tabs action=insert_row_space` / `remove_row_space`. There is no batch reposition on `manage-widgets`, so this is how you make room; moving widgets individually fails on overlap.
- Set widget-level permissions — UI only.
- Cross-report widget copy — duplicate within the same report only (use `target_tab_id` for cross-tab duplication).
- **Edit the generated AI text itself** — `update_ai_text` configures the settings and triggers generation, but the produced text can only be hand-edited in the UI.
- **Conditional formatting outside the live table (`102`)** — the colour rules are exposed (see "Conditional formatting"), but only the live table renders them. KPI cards and offline tables cannot carry them; see "Faking a heatmap" below.

### Faking a heatmap

Only the live table (`102`) can colour cells by value. For an offline table, cell values are strings, so encode the intensity in the text itself. Prefix a shade glyph per bucket — `█` highest, then `▓`, `▒`, `░`, and `·` for none — or use a proportional bar like `██████░░░░`. This survives PDF rendering and needs no colour support. Keep it to one glyph plus the number in a narrow column: a ten-cell bar overflows and the column truncates.

For a single value that must carry its own colour, put it in a Comment widget instead. There you *do* control colour per run of text — a `textStyle` colour mark for a good or bad number, or a `highlight` mark for a background chip. This is the only place in an MCP-built report where a number can carry meaning through colour.

## Idempotency

`create`, `apply_premade`, and `create_premade` accept an optional `idempotency_key` (a client-generated UUID). If a timeout or network error leaves the result uncertain, resend the same call with the same key — the original result is returned instead of creating a duplicate. Use a fresh key for each distinct operation.

## Common pitfalls

- **A widget rendering "Metrics not selected"** — it was created without `rows` (or with a config whose `options.metrics` is empty), so nothing is bound. A create carrying no binding at all is now refused (see "A create with no binding is refused"), but an omitted `rows` still returns `success` with a sample-data widget, which is how this reaches shipped reports. Always bind at create, and always verify with `export-report` / `csv_export` — see "Always pass `rows` at create time".
- **A binding written at row level instead of on the config** — `rows[].options.source_id`, `options.configs`, `options.channel_id` and their aliases bind nothing, because only `rows[].configs[].options` binds data. Six such keys are refused outright now; before that they were stored, the call returned `success`, and the widget rendered "Metrics not selected" against a null source. Move the source to `rows[].configs[].source_id` and the metrics to `rows[].configs[].options.metrics` — see "Bindings written one level too high".
- **A calculated metric that stored a formula and rendered nothing** — the calculation was described by nesting whole config definitions inside `rows[].options.operators`, each with its own `source_id` and `metrics`. Nothing reads a config there. A formula row is a flat token list referencing config ids that already exist on the widget, so it needs a `create` then an `update`; that shape is enforced now. For a calculation you want on more than one widget, use `manage-custom-metrics` — see "Formula rows".
- **A tab with one or two widgets floating in an empty grid** — the tab list in the instructions was misread as a widget list. A named tab ("Google Ads", "Weather Report for New York") is a full themed page, not a slot for one widget per named metric — compose it per "Composing a full tab", whoever named the tab.
- **Date dimension ambiguity** — a source may expose more than one date-typed dimension (e.g. `universal_dimension_1137` "Date" and `universal_dimension_150` "Date OLD"). Prefer the plainly-named current one and verify with `csv_export`. This is integration-dependent.
- **Every KPI card carrying the same eye icon** — `rows[].options.icon` was never set, so each row fell back to the hardcoded default `Visible--Streamline-Sharp.svg`. Metric catalogs carry no icons of their own, so this happens on every integration and on every card. Pull the library once with `list-widgets action=list_icons` and bind an icon per row at create — see "Row icons".
- **Full-width single-value widgets** — looks like a section header; use 2×2 or 2×1 instead.
- **`wrap_text: true` splitting words in half** — a wrapped table cell breaks at the character, not at the word, so a finished PDF shows things like `instabilit y` and `2 026 commits`. No option changes this. Keep table cells short enough to sit on one line — roughly 40 to 45 characters in a four-column full-width table, less in narrower columns — and move longer prose into a Comment widget, which wraps correctly.
- **Bar-chart value labels that disappear** — on bar types (horizontal bars, including the offline Bar chart) the label colour is calculated to contrast with the **bar fill**, because the label is expected to sit on the bar. An *outside* position (`top`, `bottom`, `left`, `right`) puts the label on the chart background but keeps that colour, so a pale label lands on a pale background and becomes invisible. The labels are drawn; you cannot see them. Keep an `inside*` position on bar types — the default `insideRight` is correct — or, if you must put the label outside, set `chart_label_bg_enabled: true`, which draws a chip in the bar colour behind the text and makes it legible again. Vertical charts (Column, Line, Area) are not affected: their labels are always dark.
- **A table that looks complete but is missing its last rows** — the widget shows only the rows that fit its box and drops the rest with no marker. `csv_export` still returns every row, so data checks pass. See "Tables truncate silently".
- **Table summary row sums percentages** — the footer sums percent columns as numbers (25% + 30% = 55%); disable footer for percent-heavy tables.
- **Updating metrics on a widget that uses a source group** — after the group's sources change, the widget may need to re-save to pick up field definitions. Verify via `list-widgets action=show`.
- **Metric-only update drops the binding ("Unavailable report type")** — when updating a config in place, always carry its `integration_id`, `source_id`, and `report_type` alongside the new `metrics`/`dimensions`. Omitting them on a source-group or report-type-bound widget can rebuild the config without its report-type binding and leave the widget blank. Prefer name/position-only edits on those widgets, and verify data with `csv_export` after any metric change.
- **Creating without `channel_id`** — required at create time; channel_id = the source's channel.
- **Creating without `widget_type_id`** — required; verify via existing widgets on the tab.
- **Passing an invalid `source_id`** — the tool accepts both global and report-local IDs, but will error if the ID doesn't exist. Use `list-sources` or `list-reports action=list_sources` to find valid IDs.
- **`metrics=[]` as a top-level param** — wrong shape. Metrics live inside `rows[].options.metrics` (row label) and `rows[].configs[].options.metrics` (data binding).
- **Sending `integration-metrics` / `integration-dimensions` / `integration-report-types`** — rejected with an error naming the key to use instead (`metrics`, `dimensions`, `report_type`). These are pre-new-architecture storage keys that bind nothing on a current widget. No response returns them any more either, so there is nothing to copy them from.
- **Batch operations without `widget_ids`** — the array is required. Empty array = no-op, not "all widgets".
- **Widget breaks after batch source swap** — the new source may not have the same report type or fields; always verify with `list-widgets action=show` after.
- **`metric.external_id` change appears to no-op** — when the widget already has a config bound to a metric on a source group / blend, re-supplying a different `metric.external_id` in the same config sometimes leaves the original metric in place. The `list-widgets action=show` response masks this (it only echoes channel + source ids, not the metric). Always confirm via `list-widgets action=csv_export` or `export-report` after a metric swap; if the CSV still shows the previous metric name, delete and recreate the widget rather than trying to update it in place.
- **A metric rename that returns `success` and changes nothing on screen** — the new caption was written to `rows[].options.title` or `rows[].options.metrics[].label`. Neither is an input; the rendered caption is `rows[].configs[].options.metrics[].name`. The row title version looks correct until the data arrives, then snaps back; the `label` version is invisible immediately, because nothing reads it. A warning now flags this on write. Set the config metric `name` instead — see "Renaming a metric caption".
- **Widget `name` vs row-level `title`** — `name` sets the widget-level `options.title`, the heading above the chart/table. `rows[].options.title` is a row display option, not the metric caption; don't reach for it to rename a metric.
- **Titling a type that has no title** — `name` / `options.title` on a Comment (`21`), Calendar (`22`), Filter control (`137`), or Report shortcut (`141`) is rejected, on create, update, and `batch_change_settings`. These types render no title, so the value used to be stored and never shown — which read back as success and led to reporting headers that did not exist. A Comment's heading belongs in its body text.
- **A comment widget that renders as an empty box** — the body text never arrived. Either it was never supplied (now rejected at create), or an update rebuilt the row without it: a row passed without `rows[].id` is recreated from scratch and drops the existing text. Pass the row's `id`, or re-send `comment_widget_text`. Both failure modes are refused now rather than returning success.
- **A comment/image edit that "worked" but changed nothing** — row-level `comment_widget_text`, the legacy `text`/`comment` aliases, and image `image_url` / `image_data` were only applied on create; on update they were accepted and dropped. Fixed Jul 2026. If you hit this on an older deployment, write the config shape directly in `rows[].configs[].options` instead.
- **Duplicate metric/dimension bindings** — binding the same `external_id` twice in one config is silently de-duplicated (keeps first occurrence). A warning is returned, but the widget ends up with one series, not two. To chart two series of the same metric, use separate rows.
- **`tab_id` missing on create** — required. Find via `list-report-tabs action=list`.
- **A sort that stores fine and orders nothing** — `sort` is the sort **direction**, `"asc"` / `"desc"` / `null`, on the entry in `rows[].options.metrics[]` or `rows[].options.dimensions[]`. It is not a position or an index. `sort: 0` used to be accepted and skipped outright by the backend (which matches on truthiness), so the write returned success and the widget came back in the source's own order; it is rejected now. See "Sorting a widget".
- **`sort` on a single-value widget** — inert wherever you put it: a `101` aggregates everything into one number and has no rows to order. The tool warns. Use a Table (`102`) with the dimension bound.
- **AI text (`update_ai_text`) errors** — generation runs in the background, so a failure arrives on the collecting call as `status: failed` with the reason in `message`, not as an error on the first call. The settings are already saved either way. Queue a new summary by sending `ai_text` again. A failure that names the plan may mean the AI feature is not available to the team.
- **An offline widget showing 200,000 impressions you never entered** — it was created without `rows[].data`, so it still holds the template's placeholder sample numbers. The create response warns about this. Send an `update` with the row's `data` to replace them.
- **An offline widget whose icon flickers and never draws** — a cell holds two currency symbols, typically a range like `"$4.80 - $7.40"`. The backend cannot resolve which currency that is and hands the whole string back as the currency code; the frontend throws `RangeError: Invalid currency code` on every render attempt, and the retry loop is the flicker. Nothing rejects this on write, and a human typing it into the offline-data grid hits it too. Split the range into two entries or two table columns. See "Values".
- **Offline values passed as row options** — `rows[].options.value` / `previous_value` bind nothing. Row `options` is a free-form blob, so these used to persist silently and the call still reported success; they now come back as an "unrecognized `options` keys" warning. Offline values belong in the row's `data` array.
- **Binding a metric on an offline widget** — rejected. These widgets derive their metrics from their own values, and a binding written here is reverted before the response is built, so it used to return success with a metric the widget never had. Use `data` instead; `name` on each entry is the metric label.
- **`"offline_single_value"` and friends** — the `offline_`-prefixed string names resolve to the writable current-generation types (`125`+). On deployments before Aug 2026 they resolved to the pre-new-architecture types (`25`+) and were then rejected as too old — pass the integer ID there.
- **Conditional formatting that vanished after an unrelated edit** — the rules hang off the widget config, so a row rebuilt from scratch (the "omit `rows[].id`" workaround) cannot keep them. Read them out with `list-widgets action=conditional_formats` before any structural edit and write them back after. `manage-widgets` re-attaches them when only the config is replaced and warns in `warnings` when a row removal discarded them, so check `warnings` on every table update.
- **`set_conditional_formats` wiping the rules you didn't send** — it is replace-all, not a merge. Use `add_conditional_formats` to append a band, and `set_conditional_formats` with an empty array only when you mean to clear the column.
- **Manual rules that store fine and never paint** — the metric is in auto-colors mode, which the renderer prefers. Both write actions now clear the other mode and tell you in `warnings`, but a metric that was set up in the UI before this can hold both; check `mode` in `list-widgets action=conditional_formats`.
- **Auto colours that shift between runs** — the seven tints are anchored to the column's own min and max, so new data remaps every cell. Expected. Use manual rules when a threshold must stay put.
- **Only the top band ever colouring** — the rules are evaluated in `position` order and the first match wins. A wide rule sent first (`greater_than 0`) matches everything and the narrower bands after it never fire. Order narrowest first.
- **A conditional format that stores fine and never paints** — the widget is not a live table (`102`). This is now rejected outright, but on deployments before Aug 2026 the rule was stored silently against a type that never draws it.
- **Literal `\n` in comment text** — a comment widget whose rendered text shows a visible `\n` (and renders entirely in heading size) received a double-escaped newline: the string contained the two characters backslash + n instead of a line break. Recreate with real newlines, or split into a header widget + a separate text-block widget.
