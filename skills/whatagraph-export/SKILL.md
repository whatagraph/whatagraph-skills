---
name: whatagraph-export
type: domain
description: Export report data as an Excel (.xlsx) download or get inline widget data via csv_export. Use when a user wants raw data out of a report as spreadsheet rows, or needs a downloadable file.
required_tools:
  - list-sources
  - list-widgets
  - export-report
  - manage-sharing
---

# Exporting Report Data

Two export paths exist — pick based on what you need:

| Path | Returns | Best for |
|------|---------|----------|
| `export-report` | `.xlsx` download URL (temporary, 1-hour expiry) | Giving users a downloadable Excel file |
| `list-widgets action=csv_export` | Inline `csv_rows: string[][]` (JSON) | AI/LLM processing, per-widget data extraction |

**Feature gate**: Both paths require the `widget-csv-export` plan feature. Teams without it get a "csv export feature not included in your plan" error.

## Use this when

- "Give me every widget's data from this report as a spreadsheet." → `export-report`
- "Export just the Campaigns tab." → `export-report` with `tab_id`
- "What are the numbers in this widget?" → `csv_export` (inline data)
- Ad hoc data extraction for analysis in Excel / BigQuery / Python.

## Excel export (download URL)

```
export-report report_id=<id>
export-report report_id=<id> tab_id=<tab_id>
export-report report_id=<id> widget_ids=[<id1>, <id2>]
```

Response:
```json
{
  "success": true,
  "report": { "id": ..., "name": ..., "date_range": { "from": ..., "till": ... } },
  "tabs": [{ "tab_id": ..., "tab_name": ... }],
  "download_url": "https://...",
  "file_size_bytes": ...,
  "message": "Excel export ready. Download URL expires in 1 hour."
}
```

Each widget becomes a separate sheet in the `.xlsx` file. Comment, calendar, image, and filter-control widgets are excluded server-side.

**Feature gate**: `export-report` requires the `widget-csv-export` plan feature. Teams without it get a permission error.

### Fallback date range

Widgets without their own configured date range use this fallback:

```
export-report report_id=<id> from="2025-10-01" till="2025-10-31"
```

Widgets with their own `date_range` ignore this fallback.

## Inline widget data (csv_export)

For AI/LLM workflows where you need to read widget data programmatically:

```
list-widgets action=csv_export widget_id=<id>
```

Response:
```json
{
  "success": true,
  "widget": { "id": ..., "title": "...", "widget_type_name": "...", "sources": [...] },
  "csv_rows": [["Header1", "Header2"], ["value1", "value2"], ...],
  "contains_sample_data": false,
  "data_status": "ready"
}
```

`csv_rows` is an array of arrays — first row is headers, subsequent rows are data. When comparison is active, headers include `(prev)` suffix columns.

## Other export paths

- **Excel via sharing**: `manage-sharing action=export_excel report_id=<id>` — same xlsx output as `export-report`.
- **PDF**: `manage-sharing action=download_pdf report_id=<id>` — starts the render and returns a `pdf_job_id`. Then `manage-sharing action=get_pdf report_id=<id> pdf_job_id=<pdf_job_id>` returns the download URL once `status` is `ready`. See `whatagraph-sharing`. **Warning**: `download_pdf` auto-creates a public share link if none exists.

## What MCP can't do here

- Filter the export by dimension or date post-hoc — the widget's own filters and date range apply.
- Export custom dimension/metric definitions — only widget data.
- Read the xlsx file contents inline — the download URL must be fetched externally.

## Common pitfalls

- **Expecting inline CSV from `export-report`** — it returns a download URL, not inline data. Use `csv_export` for inline data.
- **Download URL expiry** — the temporary URL expires in 1 hour. Generate a fresh one if needed.
- **Huge exports** — very large reports can take 30-90 seconds on first call. Use `tab_id` or `widget_ids` to narrow scope.
- **Image / comment / calendar / filter widgets** — skipped entirely in export. Passing their IDs in `widget_ids` yields nothing (no error).
- **`download_pdf` side effect** — silently creates a public share link if the report doesn't have one.
- **Fallback dates without both `from` and `till`** — both must be provided together.
