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
https://app.whatagraph.com/report/<report_id>
```

Use the number after `live-report/` or `report/` as `report_id`. The `client_id` in the URL refers to a space (folder) and is not needed for the MCP tools.

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

   This returns one envelope per widget containing the widget title, its configured source, and a `metrics` block with `value`, `previous_value`, `change`, `trend`, and a raw `csv` string. Use the structured `metrics` block for the digest — it's more reliable than parsing CSV.

3. **Build the digest from the returned envelopes**. For each widget, include:
   - Widget title
   - Main metric(s), with previous-period value and % change when `compare_type` is set on the report
   - Source/channel attribution if the user asked "per source"

   Skip text / image / header widgets — they have no `metrics` payload.

4. **Respect what the report is scoped to**. If the user asks a question the report can't answer (e.g., "how did Google Ads do?" on a report with no Google Ads widget), say so explicitly rather than pivoting to `fetch-data`. The report is the user's source of truth for this workflow.

## Overriding the Date Range

If the user asks for the same digest over a different date range ("same report but for last 30 days" / "now re-run on the last 7 days"), pass the overridden range to `export-report`:

```
export-report report_id: <id>,
  from: "2026-03-24", till: "2026-04-23",
  override_date_range: true
```

- `from` / `till` without `override_date_range` is only a fallback for widgets that don't have their own configured range — most widgets ignore it. Always pass `override_date_range: true` when the user's intent is "re-run with a different date range".
- After a date-range override, widget data is re-warmed from cache; the first call after an override may be slower than subsequent ones.

## Performance Expectations

- First call on a cold report (one that hasn't been viewed recently) can take 30–90 seconds because every widget's data is pulled from BigQuery / provider APIs and cached.
- Follow-up calls on the same `report_id` + same date range run in under ~20 seconds for most reports.
- If a user is running a recurring digest (daily, weekly), encourage them to enable Scheduled Refresh on the report so it's pre-warmed; this dramatically improves latency and reliability for the digest workflow.
- If the report has hit its scheduled refresh window but hasn't warmed yet (e.g., just after a date-range change), the first `export-report` call will do the warming synchronously — expect a longer response.

## What NOT To Do

- Do **not** iterate widget-by-widget with `list-widgets action: csv_export` for a full-report digest. That produces dozens of calls where `export-report` does it in one and includes comparison data.
- Do **not** fall back to `fetch-data` to "fill in" comparison metrics when `export-report` already returns `previous_value`. The report's comparison period is the authoritative one.
- Do **not** guess a report ID or change the report URL's `client_id` when discovering reports — use `list-reports action: list` with a `search` term.

## Recurring Digest Pattern (for agency / daily-triage users)

Agency users commonly run the same digest daily and occasionally diagnose 30-day trends. Recommended workflow pairing:

1. Keep two reports per client — a short-window (e.g., 7-day) and a long-window (e.g., 30-day) — both with Scheduled Refresh enabled. Point digests at whichever URL matches the question.
2. For ad-hoc ranges, prefer `override_date_range: true` on one of the existing reports over editing the report's configured range in the UI (which invalidates cache for other viewers).
3. When the user wants "main metrics per source", use the `sources` breakdown in each widget envelope — every widget is attributed to a single source (or blend).
