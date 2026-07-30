---
name: whatagraph-mcp-overview
type: meta
description: Orientation skill for the Whatagraph MCP server. Read first when working on any Whatagraph task. Explains the mental model (spaces → reports → tabs → widgets; data sources, source groups, blends; overviews; templates) and routes to the right specialized skill — both the configuration skills and the read-only analysis/insight skills (fetching metrics, report digests, marketing insights, account-health audits, troubleshooting).
required_tools:
  - list-skills
  - list-sources
  - list-spaces
  - view-team
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
| Finding what data is connected, what metrics/dimensions are available; pulling raw numbers | `whatagraph-sources-and-data`, `fetching-marketing-metrics` |
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
| Deleting, removing, disconnecting, revoking anything | `whatagraph-deleting` |
| Patterns that cross multiple domains | `whatagraph-customer-patterns` |

## Analysis, insight & troubleshooting tasks

These read-only workflow skills sit on top of the domain skills above — reach for them when the goal is to **understand** data rather than **configure** the platform:

| If the user wants to… | Reach for this skill |
|---|---|
| Pull specific numbers / answer "how did X perform?" (ad-hoc metrics) | `fetching-marketing-metrics` |
| Orient in an unfamiliar account — what's connected, what's available | `exploring-account-data` |
| Summarize / digest an existing report (often from a live-report URL) | `generating-report-digests` |
| Turn data into an executive narrative or insights write-up | `generating-marketing-insights` |
| Audit or critique an existing report's structure and widgets | `analyzing-reports` |
| Compare/analyze across channels using blends & source groups | `cross-channel-analytics` |
| Health-check the whole account (connections, sharing, goals, usage) | `auditing-account-health` |
| Diagnose wrong/missing numbers, broken sources, blend/filter issues | `troubleshooting-data-issues` |

**Three discovery-flavored skills overlap — pick by intent:** ad-hoc numbers → `fetching-marketing-metrics`; account orientation ("what do I have?") → `exploring-account-data`; the source/field reference and raw-fetch mechanics → `whatagraph-sources-and-data`. All three teach the `filter` parameter for narrowing large field catalogs.

> To find a skill, call `list-skills action=search` with the key term for the task (e.g. `filter`, `blend`, `digest`, `audit`).

## Ground rules for every MCP call

1. **Never guess IDs.** Always discover them with a `list-*` or `view-*` tool first. Every write tool (`manage-*`, `delete-*`) takes IDs returned by the corresponding read tool. Channel (integration) ids are no exception — resolve them via `list-sources action=list_metadata scope=integrations` instead of reusing numbers remembered from examples or other accounts; wherever a `channel_id` is accepted, the channel slug (e.g. `"google-ads"`) also works and is safer than a bare number (verified Jun 2026).
2. **Respect `retry_after` on `fetch-data`.** When the response indicates data is being prepared, wait that many seconds and retry with the same parameters. Do not escalate to the user as an error.
3. **Read before writing.** Before a `manage-*` call, run the matching `list-*` / `show` action to confirm the asset exists and see its current shape.
4. **Confirm destructive actions.** Always confirm intent with the user before any `delete-*` / `remove-*` call — there is no `confirm` parameter; the confirmation is you asking. Recovery varies: widgets and report tabs have a `restore` action, reports and spaces are restorable by support within a retention window, custom metrics/dimensions, source groups, and snapshots are permanently gone. Load `whatagraph-deleting` before any delete or removal.
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
| "sample data", "demo data" | a read-only placeholder source the platform provides per channel so a report can be built or previewed before real data is connected. Sample sources coexist with real sources of the same channel. In `list-reports action=list_sources` they appear under `sample_integrations` (separate from `integration_sources`). |
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
5. Build a report: `manage-reports create` (pass `layout` to set page orientation — landscape by default) → `manage-report-tabs create` → `manage-reports attach_source` (one call per data source the report needs) → `manage-widgets create` (using the report-local `source_id` returned by attach). There is no default report structure — replicate the report they referenced/uploaded, build to the intent they described, or (when there's neither) decide yourself which metrics/dimensions/KPIs are worth showing and the best visualization for each, composing by analytical priority. Don't reach for the same arrangement every time. Load `whatagraph-widgets` for the layout playbook. **Templates are opt-in**: never scan team templates or Whatagraph's pre-made template gallery to shortcut a build — use a template only when the user or agent instructions explicitly say so, and deliver the result unlinked unless linking is explicitly requested (see `whatagraph-reports` / `whatagraph-templates`).
6. Apply a theme with `manage-themes enable_theme` if the user wants custom branding.
7. **Only when the user explicitly asks for it** — share the report (`manage-sharing create`) or schedule delivery (`manage-automations create`). Building a report does not imply sharing it: never create a share link or an automation unprompted. (Note: downloading a PDF via `manage-sharing download_pdf` creates a public share link as a side effect of rendering — only download a PDF when asked.)

Every step is covered in the matching domain skill. Load those skills on demand rather than trying to remember everything in this overview.
