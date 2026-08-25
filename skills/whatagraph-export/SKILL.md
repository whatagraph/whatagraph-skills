---
name: whatagraph-export
type: domain
group: report_building
description: Export a report as a rendered PDF or an Excel (.xlsx) download, or get inline widget data via csv_export. Use when a user wants a PDF of a report or a single tab, raw data out of a report as spreadsheet rows, or any downloadable file.
required_tools:
  - list-sources
  - list-widgets
  - export-report
---

# Exporting Report Data

Three export paths exist — pick based on what you need:

| Path | Returns | Best for |
|------|---------|----------|
| `export-report format=pdf` | PDF download URL (temporary, 1-hour expiry) | The report as a document, for a client or for checking how it renders |
| `export-report` (default `format=xlsx`) | `.xlsx` download URL (temporary, 1-hour expiry) | Giving users a downloadable Excel file |
| `list-widgets action=csv_export` | Inline `csv_rows: string[][]` (JSON) | AI/LLM processing, per-widget data extraction |

**Exporting never shares the report.** `export-report` is read-only and leaves a report exactly as shared or unshared as it was. Do not create a share link in order to get a file.

**Feature gate**: the two data paths — `format=xlsx` and `csv_export` — require the `widget-csv-export` plan feature. Teams without it get a "csv export feature not included in your plan" error. `format=pdf` is **not** gated on that feature.

## Use this when

- "Give me a PDF of this report." → `export-report format=pdf`
- "Just the Meta tab as a PDF." → `export-report format=pdf tab_id=<tab_id>`
- "Give me every widget's data from this report as a spreadsheet." → `export-report`
- "Export just the Campaigns tab." → `export-report` with `tab_id`
- "What are the numbers in this widget?" → `csv_export` (inline data)
- Ad hoc data extraction for analysis in Excel / BigQuery / Python.

## PDF export

Rendering is asynchronous, so it takes **two calls**.

**1. Start the render.** Omit `pdf_job_id`:

```
export-report report_id=<id> format=pdf
export-report report_id=<id> format=pdf tab_id=<tab_id>
```

Response:
```json
{
  "success": true,
  "status": "pending",
  "report_id": 831817,
  "tab_id": null,
  "pdf_job_id": "aqYZLyGDYSlcuyZxAJcbB6r49TcEYCq5UUmn1AjH",
  "message": "PDF rendering has been queued. ..."
}
```

**2. Collect it.** Pass the `pdf_job_id` back to the same tool:

```
export-report report_id=<id> format=pdf pdf_job_id=<pdf_job_id>
```

The `status` field tells you what to do next:

- `pending` — still rendering. Wait a few seconds, then call again. Do not poll in a tight loop.
- `ready` — the response carries `download_url`, `expires_in_seconds`, `file_name` and `file_size_bytes`.
- `expired` — the job id is unknown, or the render is older than 24 hours. Start a new one.

A small report is usually ready in a few seconds; a report with many tabs takes longer. **The `download_url` expires one hour after you get it.** If it lapses, call again with the same `pdf_job_id` for a fresh URL.

### One tab or the whole report

Without `tab_id` you get the whole report: every **visible** tab renders as exactly one page. Hidden tabs are skipped.

With `tab_id` you get a single-page document for that tab alone. Pass it whenever the user names one tab — do not render the whole report and tell them to ignore the other pages, and do not suggest hiding tabs or printing from the browser as a workaround.

### Layout is fixed

Landscape, 1440 CSS px wide, one page per tab, and each page as tall as that tab's own content — so **pages in one document can differ in size**. None of this is configurable from MCP, so never promise a page size, an orientation, or a particular tab split.

### Parameters that do not apply

`widget_ids`, `from` and `till` are `xlsx` only and are ignored for `format=pdf`. A PDF renders at the report's own date range (or, for an automated report, the range its automation last ran for). To change what a PDF covers, change the report's date range first.

**To verify a PDF you generated:** a multi-page PDF can mix page sizes, and most tools report only the first page's dimensions — so examine every page. Also check the last row of every table (see `whatagraph-widgets` → "Tables truncate silently").

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

**Feature gate**: `format=xlsx` requires the `widget-csv-export` plan feature. Teams without it get a permission error. `format=pdf` does not.

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

## What MCP can't do here

- Filter the export by dimension or date post-hoc — the widget's own filters and date range apply.
- Export custom dimension/metric definitions — only widget data.
- Read the xlsx file contents inline — the download URL must be fetched externally.

## Common pitfalls

- **Reading the first `format=pdf` response as the finished PDF** — it only queues the render. The file comes from the second call, with the `pdf_job_id`.
- **Calling for the PDF once and giving up** — the first collecting call almost always returns `pending`. Wait a few seconds, then call again. Do not poll in a tight loop.
- **Expecting inline CSV from `export-report`** — it returns a download URL, not inline data. Use `csv_export` for inline data.
- **Download URL expiry** — the temporary URL expires in 1 hour. Generate a fresh one if needed.
- **PDF with Meta/Google creative images** — platform creative URLs rotate, so a long-lived PDF may end up with broken thumbnails.
- **Huge exports** — very large reports can take 30-90 seconds on first call. Use `tab_id` or `widget_ids` to narrow scope.
- **Image / comment / calendar / filter widgets** — skipped entirely in export. Passing their IDs in `widget_ids` yields nothing (no error).
- **Fallback dates without both `from` and `till`** — both must be provided together.
