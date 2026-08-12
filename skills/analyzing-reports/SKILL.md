---
name: analyzing-reports
type: workflow
description: >-
  Examine existing Whatagraph report structure, widgets, tabs, templates, themes,
  sharing settings, snapshots, and automations. Use when the user asks about
  their reports, wants to understand report layout, asks "what's in my report?",
  wants to review widget configurations, check sharing settings, see report
  templates, or optimize their report structure.
required_tools:
  - list-automations
  - list-filters
  - list-report-tabs
  - list-reports
  - list-snapshots
  - list-sources
  - list-templates
  - list-themes
  - list-widgets
  - view-sharing
  - export-report
---

# Analyzing Reports

Help users understand, review, and optimize their Whatagraph reports. Reports are the primary deliverable in Whatagraph — they contain tabs (pages) with widgets that visualize marketing data.

## Report Hierarchy

```
Report
├── Tab 1 (page)
│   ├── Widget A (KPI card)
│   ├── Widget B (chart)
│   └── Widget C (table)
├── Tab 2 (page)
│   └── ...
├── Sources (connected data)
├── Theme (visual styling)
├── Sharing settings
├── Snapshots (saved versions)
└── Automations (scheduled delivery)
```

## Workflow: Full Report Audit

### Step 0 — Resolve URL or hash (if provided)

When the user provides a report URL, share link, or hash instead of a numeric ID, resolve it first:

```
list-reports action: resolve, url_or_hash: <url_or_hash>
```

This accepts full URLs (`https://live.whatagraph.com/#/live-report/7`), share URLs, and report hashes. Use the returned `report_id` for all subsequent steps.

### Step 1 — Get report overview

```
list-reports action: show, report_id: <id>
```

Returns the report name, creation date, date range, tab count, and source summary.

### Step 2 — List all tabs

```
list-report-tabs action: list, report_id: <id>
```

Each tab has a name and position. Note which tabs exist and their order.

### Step 3 — Examine widgets on each tab

```
list-widgets action: list, report_id: <id>
```

Widgets have types (KPI, chart, table, text, image) and configurations linking them to data sources and metrics.

### Step 4 — Deep-dive into specific widgets

```
list-widgets action: show, report_id: <report_id>, widget_id: <id>
```

Shows widget ids, layout, source binding, and row/config ids. Note:
- It may not return every metric, dimension, filter, or display option. For data/config verification, use `csv_export` (step 5).
- Check that every metric has an `external_id`. If a metric only has `label` and `type` but no `external_id`, flag it as a misconfiguration — the widget may silently show no data.
- Inline `filter_groups` can be empty (`[]`) even when a named filter is attached. This means the filter has no dimension/metric conditions (it may only set filter parameters like attribution windows, or it may be misconfigured). Use `list-filters action=show filter_id=<id>` to inspect the actual stored filter definition and its `default_inputs`.

### Step 5 — Export widget data as CSV (for data verification)

```
list-widgets action: csv_export, report_id: <report_id>, widget_id: <id>
```

`csv_export` returns data **inline** as `csv_rows: string[][]` — first row is headers (human-readable names like "Gross impressions"), subsequent rows are data values. To see raw field IDs, use `list-widgets action=show` instead.

For a full-report export — all widgets at once — use `export-report`. This is **architecturally different**: it generates a temporary `.xlsx` file server-side and returns a **download URL** (expires in 1 hour), one sheet per widget. It does NOT return inline data. Use shell tools (`head`, `cut`, `wc -l`) to inspect the downloaded file. The export may fail with a storage error if the file generation hasn't completed — retry after a short delay if this happens.

### Step 6 — Check report sources

```
list-reports action: list_sources, report_id: <id>
```

Returns a flat `sources` array. Each entry has `is_sample_data: bool`:
- **`is_sample_data: false`** — real connected accounts with `access_status` (`ok`, `error`, etc.). These are live data sources.
- **`is_sample_data: true`** — demo/sample data sources with no real account behind them. The `sample_source_id` is report-local.

Note which sources are real vs sample — sample data is static and won't reflect actual campaign performance.

### Step 7 — Review sharing and delivery

```
view-sharing action: show, report_id: <id>
list-automations action: list, report_id: <id>
```

### Step 8 — Check for saved snapshots

```
list-snapshots action: list, report_id: <id>
```

### Step 9 — Verify filters

For each widget with inline filters (visible in `list-widgets action=show` under `configs[].inline_filters[]`), verify the actual filter logic:

```
list-filters action: show, filter_id: <id>
```

Check `options.filter` for the dimension/metric conditions and `options.default_inputs` for filter parameters (attribution windows, granularity, etc.). A filter with empty conditions but populated `default_inputs` is a parameter-only filter — this is valid. A filter with both empty conditions AND empty `default_inputs` is likely misconfigured.

Also note the filter `version` (1 or 2): v2 filters are pushed to the provider API, v1 filters are applied locally after data fetch.

**Config-scoped filters**: Some inline filter IDs on widget configs point to config-scoped copies (`team_available: false`). These are NOT visible in `list-filters action=list` (which only returns team-available filters). They will appear in `list-filters action=show` if you query the specific ID. If a filter ID from a widget config returns "not found", it may have been deleted — note this as a potential misconfiguration rather than treating it as an error in the skill workflow.

## Field ID Families

When reviewing widget configurations, you'll encounter three field ID naming conventions:

| Family | Pattern | Example | Meaning |
|---|---|---|---|
| **Universal** | `universal_dimension_*`, `universal_metric_*` | `universal_metric_3` (Spend) | Cross-channel unified fields. Used by some channels (e.g. Google Ads) as the only valid metric IDs. |
| **Channel-native** | Varies by channel | `IMPRESSION_1_GROSS` (Pinterest), `impressions` (GSC), `campaign.name` (Google Ads) | Integration-specific IDs. Naming conventions differ: Pinterest uses ALL_CAPS, GSC uses lowercase, etc. |
| **Aggregation** (blend, combined) | `aggregation_metric_universal_metric_*`, `aggregation_dimension_universal_dimension_*` | `aggregation_metric_universal_metric_3` | A blend's **combined** value across its sub-sources. Note the doubled prefix — it wraps the inner id rather than carrying a number of its own. |
| **Per-sub-source** (blend) | `blend_metric_*`, `blend_dimension_*` | `blend_metric_939` | **One** sub-source's own column inside a blend. |
| **Group drill-down** | `universal_metric_*_integration_*`, `universal_metric_*_integration_source_*` | `universal_metric_3_integration_source_447726` | One channel's, or one sub-source's, contribution inside a source group. |

**What each family tells a reviewer.** On a blend widget, an `aggregation_*` field is the unified column while a `blend_*` field is a single channel — so a widget titled "Total Spend" bound to a `blend_*` field is showing one channel's spend under a total's label. That is a genuine finding, not a style note. On a source group, a plain `universal_*` field is the rollup and the `_integration_source_*` variants are single accounts; a "total" built from one of those has the same defect.

Two more review notes:

- **Read shape ≠ write shape.** These families are what the tools *return*; the ids accepted when *creating* a custom field on a blend are narrower. So do not flag a config as wrong merely because its ids differ from what a create call would take.
- `list-sources action=list_dimensions_and_metrics` discovers the valid ids for a source. The full family table by source type lives in `whatagraph-sources-and-data` → "Field-id family by source type"; blend-specific rules are in `whatagraph-blends`.

## Template Analysis

Templates are reusable report blueprints. Use them to understand best-practice report structures:

```
list-templates action: list
list-templates action: show, template_id: <id>
list-templates action: linked_reports, template_id: <id>
```

Templates show which reports were created from them, making it easy to identify standardized vs. custom reports.

## Theme Review

```
list-themes action: list_themes, report_id: <id>
```

Themes control visual styling (colors, fonts). If the list is empty, the report uses the system default theme — no custom branding is applied. To inspect a specific theme's colors and styling:

```
list-themes action: show_theme, report_id: <id>, theme_id: <id>
list-themes action: list_colors, report_id: <id>, theme_id: <id>
```

## Common Report Optimization Recommendations

When auditing reports, look for:

- **Duplicate KPI values across cards**: when several single-value widgets on the same tab display the exact same number — especially a round-looking value like `107,285` — treat it as a misconfiguration signal. The widgets likely all ended up pointing at the source's default metric. Inspect the affected widgets via `list-widgets action: show` (or `csv_export`) and confirm each has the metric the title implies.
- **Too many widgets per tab**: Well past ~15 widgets on one tab (without section headers breaking it up) can be overwhelming. Suggest splitting into multiple tabs. A composed full page normally runs 8–14 widgets across two or more sections — that range is healthy, not a flag.
- **Too few widgets per tab**: A tab holding only one or two widgets in an otherwise empty grid reads as unfinished — usually a build that stopped after a token widget per tab. Suggest composing each tab into a full page (headline KPIs, a trend or comparison chart, and a breakdown/detail section) or merging thin tabs together.
- **Missing date context**: Reports without date range widgets leave viewers guessing about the time period.
- **Inconsistent sources**: Widgets on the same tab pulling from different sources without clear labeling.
- **Unused tabs**: Tabs with no widgets or only placeholder content.
- **Missing KPI summary**: Reports that jump into detailed data without a high-level overview tab.
- **No automation**: Reports that are shared manually instead of using scheduled delivery.
- **Named filters with empty conditions**: Filters that have a descriptive name but empty `filter_groups` — verify via `list-filters action=show` whether they contain filter parameters or are genuinely empty.
- **Sample data sources in production reports**: Sample integrations provide static demo data. Flag if the user expects live data.

## Recommended Report Structure

A well-structured marketing report typically follows this pattern:

1. **Overview tab** — KPI summary cards showing top-level metrics (spend, conversions, ROAS)
2. **Channel-specific tabs** — One tab per major channel (Google Ads, Meta, SEO, etc.)
3. **Detailed breakdowns** — Campaign/ad group level tables with performance metrics
4. **Trends tab** — Time-series charts showing performance over the reporting period
5. **Recommendations** — Text widgets with narrative context and next steps

## Tips

- Use `list-widgets` with `action: csv_export` to verify that widget data matches expectations.
- When users ask "is my report set up correctly?", walk through the full audit workflow above.
- Cross-reference report sources with `list-sources` to check for disconnected or erroring sources.
- Snapshot analysis helps users understand how their reports have evolved over time.
- When a user pastes a URL, always start with `list-reports action=resolve` — don't manually parse URLs.
