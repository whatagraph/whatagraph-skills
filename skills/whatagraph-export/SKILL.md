---
name: whatagraph-export
description: Export a whole report (all tabs + widgets) or a single tab / specific widgets as CSV in one call. Use when a user wants raw data out of a report as spreadsheet rows.
---

# Export report to CSV

Tool covered: `export-report`.

Exports every widget's tabular data as CSV in one call, grouped by tab. Faster than calling `list-widgets action=csv_export` per widget.

## Use this when

- "Give me every widget's data from this report as CSV."
- "Only the Campaigns tab, please."
- "Only these three widgets."
- Ad hoc data extraction for further analysis in Excel / BigQuery / Python.

## Full report

```
export-report report_id=<id>
```

## One tab

```
export-report report_id=<id> tab_id=<tab_id>
```

## Specific widgets

```
export-report report_id=<id> widget_ids=[<id1>, <id2>, <id3>]
```

## Fallback date range

Widgets without their own configured date range use this fallback:

```
export-report report_id=<id> from="2025-10-01" till="2025-10-31"
```

Widgets with their own `date_range` ignore this fallback.

## What's excluded

Comment, calendar, image, and filter-control widgets have no tabular data and are skipped from the export.

## Other export paths

- Single-widget CSV via `list-widgets action=csv_export report_id=<id> widget_id=<id>`.
- Report as Excel (.xlsx) via `manage-sharing action=export_excel`.
- Report as PDF via `manage-sharing action=download_pdf`.

## What MCP can't do here

- Filter the export by dimension or date post-hoc — the widget's own filters and date range apply.
- Export custom dimension/metric definitions — only widget data.

## Common pitfalls

- **Empty CSV blocks** — disconnected source or empty date range returns an empty CSV section. Verify source with `list-sources action=show`.
- **Huge exports** — very large reports can stall. Use `tab_id` or `widget_ids` to narrow scope.
- **Image / comment widgets** — produce metadata-only rows. Filter them out of your widget_ids list when you want only tabular data.
- **Fallback dates without both `from` and `till`** — both must be provided together.
