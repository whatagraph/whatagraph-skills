---
name: whatagraph-mcp-overview
description: Orientation skill for the Whatagraph MCP server. Read first when working on any Whatagraph task. Explains the mental model (spaces → reports → tabs → widgets; data sources and source groups; blends; overviews; templates) and which specialized skill to reach for next.
---

# Whatagraph MCP overview

Whatagraph is a marketing reporting platform. Users connect data sources (Google Ads, GA4, Meta Ads, HubSpot, LinkedIn, Shopify, Google Sheets, and 60+ others), build reports, share them with clients, and schedule deliveries.

Work on any Whatagraph task by keeping the hierarchy in mind:

```
Space  (client folder)
└── Report
    └── Tab (page)
        └── Widget (chart, table, single value, image, text, goal)
```

Data flows into widgets from:
- **Data source** — one connected account (e.g. one Google Ads account).
- **Source group** — multiple accounts of the same channel rolled up.
- **Blend** — two or more sources (any channels) joined on shared dimensions.

## Mental model for the tools

| If the user is working on… | Reach for this skill |
|---|---|
| Finding what data is connected, what metrics/dimensions are available, pulling raw numbers | `whatagraph-sources-and-data` |
| Client folders, organizing reports under clients | `whatagraph-spaces` |
| Creating/editing reports, tabs, widgets | `whatagraph-reports`, `whatagraph-report-tabs`, `whatagraph-widgets` |
| Combining multiple accounts from the same channel | `whatagraph-source-groups` |
| Combining data from multiple channels into one visualization | `whatagraph-blends` |
| Building a formula metric or a unified metric across channels | `whatagraph-custom-metrics` |
| Grouping/bucketing/tagging dimension values | `whatagraph-custom-dimensions` |
| Saved filter configurations | `whatagraph-filters` |
| KPI tracking dashboards ("Measurements" in new UI) | `whatagraph-overviews` |
| Target/pacing tracking on a metric | `whatagraph-goals` |
| Reusable report blueprints, linked reports | `whatagraph-templates` |
| Saving and restoring a report's structure | `whatagraph-snapshots` |
| Visual branding, colors, fonts, logo | `whatagraph-themes` |
| Public share links, password protection | `whatagraph-sharing` |
| Scheduled email delivery | `whatagraph-automations` |
| PDF/CSV export of a whole report | `whatagraph-export` |
| Pushing data to BigQuery / data warehouse | `whatagraph-destinations` |
| Inviting teammates, roles, subscription | `whatagraph-team-and-members` |
| Connecting a new integration account to the team | `whatagraph-integrations-admin` |
| Patterns that cross multiple domains | `whatagraph-customer-patterns` |

## Ground rules for every MCP call

1. **Never guess IDs.** Always discover them with a `list-*` or `view-*` tool first. Every write tool (`manage-*`, `delete-*`) takes IDs returned by the corresponding read tool.
2. **Respect `retry_after` on `fetch-data`.** When the response indicates data is being prepared, wait that many seconds and retry with the same parameters. Do not escalate to the user as an error.
3. **Read before writing.** Before a `manage-*` call, run the matching `list-*` / `show` action to confirm the asset exists and see its current shape.
4. **Confirm destructive actions.** For `delete-*` tools, always confirm intent with the user first. Deletes are not reversible from the MCP surface.
5. **Check `show` after a write.** After a create/update, re-fetch via `show` to confirm the change landed as expected.
6. **Attach a source to the report before pointing a widget at it.** `manage-widgets` only accepts the report-local `sources.id`. Use `manage-reports action=attach_source integration_source_id=<global_id>` first — the response includes the report-local `source_id` to pass into `manage-widgets`. The same flow works for source groups and blends (they are data sources too). When updating a widget config without supplying the existing `config.id`, the platform creates a fresh report-local source mapping rather than reusing the existing one — leading to duplicate report-local sources for the same global integration source. Either always pass the existing `config.id` (recommended) or run `list-reports action=list_sources` after each such update to detect orphans.
7. **Some write/delete tools require access.** If a `manage-*` / `delete-*` call is not available for a team, continue with the available read tools and explain which action needs enablement.
8. **Use field IDs exactly as returned by the tools.** Custom fields usually use `universal_metric_<id>` / `universal_dimension_<id>`. Blends and source groups may expose different field-id families for reading than for creating related custom fields, so check the domain skill before writing.
9. **`show` responses may be summarized.** Some endpoints omit advanced settings, especially widget display options. For widget data/config verification, use `list-widgets action=csv_export` or `export-report`.

## How users describe things (UI ↔ MCP parameter mapping)

Users rarely say "data source"; they say things like "my Google Ads account". Translate:

| User says | Means in the tool |
|---|---|
| "client folder", "client", "folder" | a space — use `list-spaces` |
| "account", "ad account", "property" | a data source — use `list-sources` |
| "channel", "integration" | an integration (e.g. Google Ads, GA4) |
| "page", "section" inside a report | a report tab |
| "dashboard", "KPI dashboard", "measurement" | an overview (the UI now calls it "Measurement") |
| "combined data", "aggregated accounts" | source group (same channel) or blend (multi-channel) |
| "scheduled send", "auto-send", "delivery" | an automation |
| "share link", "public link" | sharing + the returned URL |
| "template report" | a report template (linked report pattern) |

## The golden flow for new users

1. `view-team action=show` — confirm plan, features enabled.
2. `list-spaces action=list` — see client folders.
3. `list-sources action=list` (optionally filtered by a space) — see what's connected.
4. Decide whether you need to aggregate same-channel accounts (`source-groups`) or combine different channels (`blends`).
5. Build a report: `manage-reports create` → `manage-report-tabs create` → `manage-reports attach_source` (one call per data source the report needs) → `manage-widgets create` (using the report-local `source_id` returned by attach).
6. Apply a theme with `manage-themes enable_theme`.
7. Share with `manage-sharing create` and schedule with `manage-automations create`.

Every step is covered in the matching domain skill. Load those skills on demand rather than trying to remember everything in this overview.
