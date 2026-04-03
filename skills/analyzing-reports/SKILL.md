---
name: analyzing-reports
description: >-
  Examine existing Whatagraph report structure, widgets, tabs, templates, themes,
  sharing settings, snapshots, and automations. Use when the user asks about
  their reports, wants to understand report layout, asks "what's in my report?",
  wants to review widget configurations, check sharing settings, see report
  templates, or optimize their report structure.
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

1. **Get report overview**:
   ```
   list-reports action: show, report_id: <id>
   ```
   This returns the report name, creation date, tab count, and source summary.

2. **List all tabs**:
   ```
   list-report-tabs action: list, report_id: <id>
   ```
   Each tab has a name and position. Note which tabs exist and their order.

3. **Examine widgets on each tab**:
   ```
   list-widgets action: list, report_id: <id>
   ```
   Widgets have types (KPI, chart, table, text, image) and configurations linking them to data sources and metrics.

4. **Deep-dive into specific widgets**:
   ```
   list-widgets action: show, report_id: <report_id>, widget_id: <id>
   ```
   Shows full widget configuration including metrics, dimensions, filters, and display options.

5. **Export widget data as CSV** (for data verification):
   ```
   list-widgets action: csv_export, report_id: <report_id>, widget_id: <id>
   ```

6. **Check report sources**:
   ```
   list-reports action: list_sources, report_id: <id>
   ```
   Shows which data sources are attached to the report.

7. **Review sharing and delivery**:
   ```
   view-sharing action: show, report_id: <id>
   list-automations action: list, report_id: <id>
   ```

8. **Check for saved snapshots**:
   ```
   list-snapshots action: list, report_id: <id>
   ```

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

Themes control visual styling (colors, fonts). Review which theme a report uses to understand branding consistency.

## Common Report Optimization Recommendations

When auditing reports, look for:

- **Too many widgets per tab**: More than 10-12 widgets per tab can be overwhelming. Suggest splitting into multiple tabs.
- **Missing date context**: Reports without date range widgets leave viewers guessing about the time period.
- **Inconsistent sources**: Widgets on the same tab pulling from different sources without clear labeling.
- **Unused tabs**: Tabs with no widgets or only placeholder content.
- **Missing KPI summary**: Reports that jump into detailed data without a high-level overview tab.
- **No automation**: Reports that are shared manually instead of using scheduled delivery.

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
