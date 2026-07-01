---
name: generating-report-digests
type: workflow
description: >-
  Produce a digest or summary of an existing Whatagraph report from a report
  URL or report ID. Use when the user pastes a live-report link
  (`https://live.whatagraph.com/client/{cid}/live-report/{rid}`), asks for the
  "daily triage", "main metrics from this report", "weekly digest", or wants a
  running summary of the same report. Distinct from fetching-marketing-metrics
  (which builds answers from raw sources) — this skill reads the already-built
  report as-is, including its widgets, date range, and comparison period.
required_tools:
  - list-reports
  - list-widgets
  - export-report
  - fetch-data
---

# Generating Report Digests

Many Whatagraph users run recurring prompts on top of a single report URL ("give me the main metric from each source in this report", "run my daily triage on this report", "summarize last week's performance from this report"). For these requests, do **not** rebuild the data from `fetch-data` — the report already encodes the user's chosen sources, metrics, dimensions, date range, and comparison period. Read the report directly.

## Resolving the Report

When the user pastes a report URL or share link, resolve it to a report ID:

```
list-reports action: resolve, url_or_hash: "<url or share hash>"
```

This handles full URLs (`https://live.whatagraph.com/client/{cid}/live-report/{rid}`), share hashes, and plain numeric IDs.

If the user mentions a report by name instead of URL, discover the ID:

```
list-reports action: list, search: "{name fragment}"
```

## Workflow: Report Digest

1. **Inspect the report** to learn its date range, comparison period, and source coverage:

   ```
   list-reports action: show, report_id: {id}
   ```

   The response includes `date_range.from`, `date_range.till`, and — when comparison is enabled — `date_range.vs_from`, `date_range.vs_till`, `date_range.compare_type`. If `vs_from` / `vs_till` are present, the report expects period-over-period output; surface both current and previous values in the digest.

2. **List the report's widgets** to understand its structure:

   ```
   list-widgets action: list, report_id: {id}
   ```

   This returns all widgets across all tabs with their `id`, `name`, `widget_type_name`, and `tab_id`. Skip non-data widgets (text, image, header, comment, calendar, control-filter types).

3. **Export widget data inline** using `csv_export` on each data widget:

   ```
   list-widgets action: csv_export, widget_id: {widget_id}
   ```

   This returns structured JSON with:
   - `widget.id`, `widget.title`, `widget.widget_type_name`, `widget.tab_id`
   - `widget.sources` — which channels/sources feed this widget
   - `csv_rows` — array of arrays (`string[][]`): first row is headers, subsequent rows are data
   - `contains_sample_data` — whether the data is sample/demo data
   - `data_status` — `"ready"` when data is available

   For comparison data, the CSV headers include `(prev)` suffix columns alongside current-period columns.

   **Note**: `export-report` exists but returns an `.xlsx` download URL (not inline data). It is useful for giving the user a downloadable file, but **not for LLM-driven digests** — use `csv_export` per widget instead.

4. **Build the digest from the csv_export results.** For each widget, include:
   - Widget title
   - Main metric(s) from `csv_rows`, with previous-period values when `(prev)` columns are present
   - Source/channel attribution from `widget.sources` if the user asked "per source"

   For reports with many widgets, batch the most important ones first (single-value KPIs, then tables, then charts).

5. **Respect what the report is scoped to.** If the user asks a question the report can't answer (e.g., "how did Google Ads do?" on a report with no Google Ads widget), say so explicitly rather than pivoting to `fetch-data`. The report is the user's source of truth for this workflow.

### Using `export-report` for downloadable files

If the user wants a **downloadable Excel file** rather than an inline digest:

```
export-report report_id: {id}
```

This returns `download_url` (temporary, expires in 1 hour), `file_size_bytes`, and `tabs`. Each widget becomes a separate sheet in the `.xlsx` file. This is async — the first call on an unwarmed report may take 30-90 seconds.

## Date Ranges

`export-report` accepts optional `from` / `till` (`YYYY-MM-DD`) parameters, but they are **only a fallback** for widgets that don't have their own configured range — most widgets ignore them. There is no MCP-only "render this report for a different window" capability; that intentionally mirrors the product, which has no preview-without-save mode.

If the user asks for the same digest over a different date range ("same report but for last 30 days"), the right paths are:

1. Tell the user to change the report's saved date range in Whatagraph and re-run the digest.
2. Or duplicate the report in Whatagraph and run the digest against the duplicate (each report has its own saved range).

Do **not** invent a different window via `from` / `till` and present the result as if it answered the user's question — many widgets use their configured date range instead.

### Date range discrepancy: digest data vs. what the user sees

If the digest data doesn't match what the user sees in the Whatagraph UI, the most common cause is **per-widget date range overrides**. Individual widgets can have their own date range that differs from the report-level range shown in `list-reports action: show`. When this happens:

- The `export-report` envelope for each widget includes a `date_range` field — check it to see the actual window that widget used.
- Widgets with overrides will show a different `date_range` than the report-level `date_range.from` / `date_range.till`.
- There is no MCP way to change a widget's configured range — the user must update it in the Whatagraph report editor.

## Performance Expectations

- First call on a report that has not been viewed recently can take 30–90 seconds while data is prepared.
- Follow-up calls on the same `report_id` run in under ~20 seconds for most reports.
- If a user is running a recurring digest (daily, weekly), encourage them to enable Scheduled Refresh on the report so it's pre-warmed; this dramatically improves latency and reliability for the digest workflow.
- If the report's saved date range was just changed, the first `export-report` call after the change does the warming synchronously — expect a longer response.

## What NOT To Do

- Do **not** fall back to `fetch-data` to "fill in" data that a widget already shows. The report's configured sources, metrics, and comparison period are the authoritative ones for a digest.
- Do **not** pass `from` / `till` to `export-report` expecting to change the report's date window — those parameters are a per-widget fallback, not a window override.
- Do **not** assume `export-report` returns inline data — it returns an `.xlsx` download URL. For LLM-readable data, use `csv_export` per widget.
