---
name: generating-report-digests
description: >-
  Produce a digest or summary of an existing Whatagraph report from a report
  URL or report ID. Use when the user pastes a live-report link
  (`https://live.whatagraph.com/client/<cid>/live-report/<rid>`), asks for the
  "daily triage", "main metrics from this report", "weekly digest", or wants a
  running summary of the same report. Distinct from fetching-marketing-metrics
  (which builds answers from raw sources) — this skill reads the already-built
  report as-is, including its widgets, date range, and comparison period.
---

# Generating Report Digests

Many Whatagraph users run recurring prompts on top of a single report URL ("give me the main metric from each source in this report", "run my daily triage on this report", "summarize last week's performance from this report"). For these requests, do **not** rebuild the data from `fetch-data` — the report already encodes the user's chosen sources, metrics, dimensions, date range, and comparison period. Read the report directly.

## Extracting the Report ID

Whatagraph report URLs look like:

```
https://live.whatagraph.com/client/<client_id>/live-report/<report_id>
```

Use the number after `live-report/` as `report_id`. The `client_id` in the URL refers to a space (folder) and is not needed for the MCP tools.

If the user mentions a report by name instead of URL, discover the ID:

```
list-reports action: list, search: "<name fragment>"
```

## Workflow: Report Digest

1. **Inspect the report** to learn its date range, comparison period, and source coverage:

   ```
   list-reports action: show, report_id: <id>
   ```

   The response includes `date_range.from`, `date_range.till`, and — when comparison is enabled — `date_range.vs_from`, `date_range.vs_till`, `date_range.compare_type`. If `vs_from` / `vs_till` are present, the report expects period-over-period output; surface both current and previous values in the digest.

2. **Export the report's data** in one call:

   ```
   export-report report_id: <id>
   ```

   This returns one envelope per widget containing the widget title, its configured source(s), the widget's date range (with `vs_from` / `vs_till` / `compare_type` when comparison is set), a structured `metrics` array, and a raw `csv` string.

   For each metric, the `metrics` array carries:
   - `name`, `external_id`, `type`, `currency`
   - `value` — current-period value
   - `previous_value` — value over the comparison window (null when comparison is off)
   - `absolute_change`, `percentage_change` — pre-computed deltas from the platform

   Use the structured `metrics` block as the primary source for digests on **single-value, table, list, pie, and KPI-style widgets** — it's more reliable than parsing CSV.

3. **For time-series / chart widgets, read the `csv` string instead.** The `metrics` block on these widgets only reflects the first bucket. The CSV interleaves rows so previous-period values are visible alongside current-period ones:
   - Date dimensions: previous rows are emitted first with calendar-shifted dates (e.g. `2024-01-01` → `2025-01-01`), then current rows.
   - Non-date dimensions (e.g. `Day of week`, `Device`): previous rows get a ` (prev)` suffix in the same column (e.g. `Wednesday (prev)`).
   - When a chart carries multiple metrics, all metrics share the first metric's dimension column; values are positioned by index, so the CSV columns are `<dimension> | <metric_1> | <metric_2> | …` with one row per dimension bucket.

4. **For non-time-series widgets, the `csv` string also carries comparison side-by-side.** Each numeric metric expands to two columns: `<Metric>` (current) and `<Metric> (prev)` (previous-period). Goal widgets keep their existing `<Metric>` / `<Metric> Goal` layout — they don't get a `(prev)` column.

5. **Build the digest from the returned envelopes.** For each widget, include:
   - Widget title
   - Main metric(s), with previous-period value and `percentage_change` when `compare_type` is set on the report
   - Source/channel attribution if the user asked "per source"

   Skip text / image / header / comment / calendar / control-filter widgets — `export-report` already excludes most of these, and the rest have no `metrics` payload (`exportable: false`).

6. **Respect what the report is scoped to.** If the user asks a question the report can't answer (e.g., "how did Google Ads do?" on a report with no Google Ads widget), say so explicitly rather than pivoting to `fetch-data`. The report is the user's source of truth for this workflow.

## Date Ranges

`export-report` accepts optional `from` / `till` (`YYYY-MM-DD`) parameters, but they are **only a fallback** for widgets that don't have their own configured range — most widgets ignore them. There is no MCP-only "render this report for a different window" capability; that intentionally mirrors the product, which has no preview-without-save mode.

If the user asks for the same digest over a different date range ("same report but for last 30 days"), the right paths are:

1. Tell the user to change the report's saved date range in Whatagraph and re-run the digest. Cache re-warms automatically after a date-range change.
2. Or duplicate the report in Whatagraph and run the digest against the duplicate (each report has its own saved range).

Do **not** invent a different window via `from` / `till` and present the result as if it answered the user's question — most widgets will silently ignore the override and return data for their configured range.

## Performance Expectations

- First call on a cold report (one that hasn't been viewed recently) can take 30–90 seconds because every widget's data is pulled from BigQuery / provider APIs and cached.
- Follow-up calls on the same `report_id` run in under ~20 seconds for most reports.
- If a user is running a recurring digest (daily, weekly), encourage them to enable Scheduled Refresh on the report so it's pre-warmed; this dramatically improves latency and reliability for the digest workflow.
- If the report's saved date range was just changed, the first `export-report` call after the change does the warming synchronously — expect a longer response.

## What NOT To Do

- Do **not** iterate widget-by-widget with `list-widgets action: csv_export` for a full-report digest. That produces dozens of calls where `export-report` does it in one and includes comparison data.
- Do **not** fall back to `fetch-data` to "fill in" comparison metrics when `export-report` already returns `previous_value`. The report's comparison period is the authoritative one.
- Do **not** pass `from` / `till` to `export-report` to "re-run for a different window" — those parameters are a per-widget fallback, not a window override.
