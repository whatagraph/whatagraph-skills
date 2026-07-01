---
name: troubleshooting-data-issues
type: workflow
description: >-
  Diagnose data discrepancies, source connection problems, blend and source group
  issues, filter behavior, and missing data in Whatagraph. Use when the user
  reports incorrect numbers, missing data, broken sources, discrepancies between
  Whatagraph and native platforms, blend errors, source group sync problems,
  or asks "why is my data wrong?" or "my source isn't working."
required_tools:
  - list-blends
  - list-filters
  - list-integrations
  - list-source-groups
  - list-sources
  - list-widgets
  - export-report
  - fetch-data
  - load-skill
---

# Troubleshooting Data Issues

Systematically diagnose and explain data issues in Whatagraph. Since all MCP tools are read-only, the goal is to identify the root cause and provide clear guidance on what needs to be fixed.

## Triage: Identify the Issue Type

Ask clarifying questions to determine which category the issue falls into:

1. **Source connection error** — A source shows an error icon or hasn't synced
2. **Data discrepancy** — Numbers in Whatagraph don't match the native platform
3. **Missing data** — Expected data isn't appearing in reports or widgets
4. **Blend/source group issue** — Cross-source data isn't combining correctly
5. **Filter problem** — Filters producing unexpected results or excluding data
6. **Widget configuration error** — Widget showing wrong metrics or dimensions

## Workflow: Source Connection Issues

1. **Check source health**:
   ```
   list-sources action: show, source_id: <id>
   ```
   Look for `status: "issue"` (the value and the `list-sources` filter are `issue`, not `error`) — this indicates a connection problem. Note that `show` confirms the error status but does **not** expose the error message or failure reason — MCP has no field for that. To read the actual error description, open the source in the Whatagraph UI (Settings → Sources) where the specific error is displayed.

2. **Check if the source is used anywhere**:
   ```
   list-sources action: list_usage, source_ids: [<id>]
   ```
   Returns report/blend/transfer/source-group/overview counts. If all zeros, the source isn't used in any report — that explains "missing data" immediately.

3. **Check the integration account**:
   ```
   list-integrations action: list_accounts, channel_id: <id>
   ```
   Account-level errors often affect all sources under that account.

4. **Verify the source is assigned to the right spaces**:
   ```
   list-sources action: show, source_id: <id>
   ```
   Check `space_ids` — empty means the source isn't in any space. Also note the `currency` field — currency mismatches between sources are a common discrepancy cause.

4. **Common causes**: Expired connections, revoked permissions, API quota limits, or the external account being deleted/renamed. For all of these, the user must reconnect or fix permissions in the UI — MCP cannot trigger a reconnection.

## Workflow: Data Discrepancies

1. **Confirm the date range**: Ensure the user is comparing the same dates in both Whatagraph and the native platform.

2. **Check report types first** — many sources (Google Ads has 64) expose multiple report types:
   ```
   list-sources action: list_report_types, source_id: <id>
   ```

3. **Find the right metric** — use `resolve_fields` for natural-language lookup:
   ```
   list-sources action: resolve_fields, source_id: <id>, query: "spend"
   ```
   Returns semantically matched fields ranked by relevance. Fall back to `list_dimensions_and_metrics` with `filter` if `resolve_fields` returns nothing (it doesn't work on all integrations):
   ```
   list-sources action: list_dimensions_and_metrics, source_id: <id>, report_type: "<type>", filter: "cost"
   ```

4. **Fetch raw data for comparison**:
   ```
   fetch-data source_id: <id>, report_type: "<type>",
     metrics: ["<metric>"], dimensions: ["date"],
     from: "<start>", till: "<end>"
   ```
   Compare day-by-day values with the native platform.

5. **Check for filters**: Hidden filters on widgets or report-level filters can exclude data:
   ```
   list-filters action: list
   list-widgets action: show, report_id: <report_id>, widget_id: <id>
   ```
   `show` exposes `inline_filters` with full detail: filter ID, name, scope, version (1 or 2), and `filter_groups` with dimension/metric, operator, and value. This is sufficient for diagnosing widget-level filters. Use `list-widgets action: csv_export` when you need the actual rendered data output.

6. **Common causes**:
   - **Currency mismatches**: Sources may report in different currencies (e.g., EUR vs USD). Check `currency` in `list-sources action: show` for each source. Mixing currencies in blends or comparisons without conversion produces wrong totals.
   - **Field ID family mismatch**: Widgets use universal IDs (`universal_metric_*`), but `list_dimensions_and_metrics` also returns channel-native IDs (`metrics.clicks` for Google Ads, `spend` for Meta). Source groups use `universal_metric_*` / `universal_dimension_*`; blends use `aggregation_metric_*` / `aggregation_dimension_*`. Using the wrong family returns no data or errors.
   - **Wrong report type**: Sources like Google Ads have 60+ report types (campaign, ad_group, ad, keyword, etc.). A widget using the wrong report type shows different metrics than expected.
   - **Time zone differences**: Whatagraph may aggregate data in a different timezone than the native platform.
   - **Attribution models**: Different attribution windows (e.g., 7-day click vs 28-day click in Meta).
   - **Data freshness**: Some integrations have a 24-48 hour delay. Recent data may not yet be synced.
   - **Metric definitions**: "Conversions" can mean different things across platforms. Check the specific metric description.

## Workflow: Blend and Source Group Issues

Blends and source groups combine data from multiple sources, which introduces complexity.

1. **Inspect the blend**:
   ```
   list-blends action: show, blend_id: <id>
   ```
   Check which sources are included and how they're joined.

2. **Inspect source group**:
   ```
   list-source-groups action: show, group_id: <id>
   ```
   Check the sources and their ETL configurations.

3. **Check for source issues within the group**:
   ```
   list-source-groups action: source_issues, group_id: <id>
   ```
   This specifically lists sources with disabled ETL configs (sync problems).

4. **Common causes**:
   - **Metric mapping mismatches**: Different sources may map similar metrics differently in a blend.
   - **Missing sources**: A source was removed from the group but the blend still references it.
   - **ETL disabled**: Individual source ETL configs within a group can be disabled, causing gaps.

## Workflow: Filter Issues

1. **List all filters**:
   ```
   list-filters action: list
   ```

2. **Inspect a specific filter**:
   ```
   list-filters action: show, filter_id: <id>
   ```
   Check the filter options and values to understand what's being included/excluded.

3. **Check widget-level filters**:
   ```
   list-widgets action: show, report_id: <report_id>, widget_id: <id>
   ```
   Widgets can have their own filter configurations that override or layer on top of report-level filters, but current `show` responses may omit option details. If the filter is not visible there, verify through `csv_export` / `export-report` and the UI.

4. **Common causes**:
   - **Filters applied to blended sources vs original sources**: Filters may behave differently when applied to blends compared to individual sources.
   - **Dimension value mismatches**: Filter values must exactly match the dimension values in the source data.
   - **Inherited vs widget-specific filters**: Report-level filters cascade to all widgets unless overridden.

## Escalation Guidance

If the issue cannot be diagnosed with read-only tools:
- **Source connection errors**: Advise the user to reconnect the source in Whatagraph settings or check permissions on the external platform.
- **Data sync issues**: Suggest waiting 24-48 hours for data to fully sync, then re-check.
- **Persistent discrepancies**: Recommend contacting Whatagraph support with the specific source ID, date range, and metric names for deeper investigation.
- **ETL/sync problems**: Note the specific source IDs with issues so support can investigate the pipeline.

## Tips

- Always start by reproducing the issue — fetch the actual data and compare it to what the user expects.
- Time zone differences are the #1 cause of "small" data discrepancies (1-5% off).
- When comparing data, use the `date` dimension to get daily breakdowns — this makes it easier to spot where discrepancies occur.
- Source groups with many sources (50+) may have performance-related delays. Check individual source health.
- **Use `error.category` to decide how to react.** `data_not_ready` (data still processing) and `rate_limited` are **transient — retry with backoff** (a `rate_limited` response carries a `retry_after`; wait that many seconds), not real failures. `validation` / `not_found` mean fix your input; `permission_denied` / `auth` are account-level — tell the user. Read-only tools (`list-*` / `view-*` / `load-skill`) have a separate, higher rate-limit bucket, so discovery rarely throttles — pace write calls instead.
