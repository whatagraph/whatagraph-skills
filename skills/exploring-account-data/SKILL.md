---
name: exploring-account-data
description: >-
  Navigate and discover data sources, integrations, report types, metrics,
  dimensions, spaces, reports, and the overall account structure in a Whatagraph
  account — including narrowing large field catalogs with the filter parameter.
  Use when the user asks what data is available, wants to understand their account
  setup, needs to find specific sources or integrations, or asks questions like
  "what channels do I have connected?" or "show me my reports."
---

# Exploring Account Data

Help users discover and navigate the data available in their Whatagraph account. This is the foundational skill for understanding what's connected, what metrics are available, and how the account is organized.

## Key Concepts

- **Sources** are connected data accounts (e.g., a specific Google Ads account). Use `list-sources` to browse them.
- **Channels** (called "integrations" in the API) are platform types like Facebook Ads, Google Analytics 4, etc. Use `list-integrations` to see available channels.
- **Spaces** are organizational folders that group reports and sources by client or project. Use `list-spaces` to browse them.
- **Reports** contain tabs (pages) with widgets that visualize data. Use `list-reports`, `list-report-tabs`, and `list-widgets` to navigate the hierarchy.
- **Custom fields** include user-created metrics and dimensions that extend built-in ones. Use `list-custom-metrics` and `list-custom-dimensions`.

## Workflow: Discovering Available Data

1. **Start with integrations** to understand which channels are connected:
   - Call `list-integrations` with `action: list_grouped` for a channel-by-channel overview
   - This shows which platforms (Google Ads, Meta, GA4, etc.) are active

2. **Browse data sources** to see specific connected accounts:
   - Call `list-sources` with `action: list` to see all sources
   - Filter by integration type using `channels` (array of integration IDs)
   - Use `action: list_report_types` on a source to see its available report types
   - Use `action: list_dimensions_and_metrics` to discover available fields for a source — and when you already know the field the user named, narrow the catalog in one call with `filter: "<keyword>"` (case-insensitive substring on name/`external_id`) instead of paging through hundreds of fields; `is_universal: true` limits the result to the unified `universal_*` fields

3. **Explore the account structure**:
   - Call `list-spaces` with `action: list` to see client folders
   - Call `list-reports` with `action: list` to see all reports
   - Use `filter_space_ids` to see reports within a specific space

4. **Understand available metrics and dimensions**:
   - For a specific source: `list-sources` with `action: list_dimensions_and_metrics`
   - For custom fields: `list-custom-metrics` and `list-custom-dimensions`
   - Always check what report types a source supports before attempting to fetch data

## Tool Quick Reference

| Tool | Key Actions | Use When |
|------|------------|----------|
| `list-sources` | `list`, `show`, `list_report_types`, `list_dimensions_and_metrics`, `list_usage` | Finding data sources, checking available metrics |
| `list-integrations` | `list`, `list_grouped`, `list_accounts`, `list_available_sources` | Understanding connected channels |
| `list-spaces` | `list`, `show`, `children` | Navigating client/project folders |
| `list-reports` | `list`, `show`, `list_sources` | Finding and examining reports |
| `list-report-tabs` | `list`, `show` | Browsing tabs (pages) within a report |
| `list-widgets` | `list`, `show`, `csv_export` | Exploring widgets on report tabs |
| `list-blends` | `list`, `show` | Cross-channel blended data sources |
| `list-source-groups` | `list`, `show`, `source_issues` | Aggregated same-type sources |
| `list-custom-metrics` | `list`, `list_with_premades`, `show`, `usage` | User-created and premade metrics |
| `list-custom-dimensions` | `list`, `list_with_premades`, `show`, `usage` | User-created and premade dimensions |
| `list-themes` | `list_themes`, `list_colors` | Report visual themes and palettes |
| `list-overviews` | `list`, `show` | KPI tracking dashboards |
| `view-goals` | `list`, `show` | Metric targets and progress |
| `view-team` | `show`, `search`, `roles`, `show_subscription`, `list_plans` | Account settings, overview search, subscription |

## Report Types: Required for Most Paid Channels

Most paid advertising sources (Google Ads, Bing/Microsoft Ads, etc.) and several analytics sources (Google Search Console, Ahrefs) expose **multiple report types** — one per entity level (account, campaign, ad group, ad, keyword, …) or per search type (web, image, video). Each report type has its own catalog of dimensions and metrics.

When exploring such a source:

1. `list-sources action: list_report_types, source_id: <id>` — always do this before `list_dimensions_and_metrics` or `fetch-data`.
2. If the response has more than one entry, **pass `report_type` explicitly** on every subsequent call. Omitting it causes:
   - `list-sources action: list_dimensions_and_metrics` → `Multiple report types are available. Please specify a report_type parameter.`
   - `fetch-data` → `This source has multiple report types. The report_type parameter is required — choose one of: ...`

Single-report-type sources (e.g., most social pages, email platforms) return exactly one entry from `list_report_types` and you can omit the param.

**Some sources return `report_types: []`** (zero report types) — notably Facebook Ads and GA4. Always call `list-sources action=list_report_types source_id=<id>` first and check the `note` field. If `note` says "This data source does not support report types", omit `report_type` entirely in subsequent calls; do not guess at report-type names.

## Tips

- `view-team action: search` searches **overview names only** — it does not search reports, spaces, or sources. To find reports by name use `list-reports action: list, search: "<term>"`; for spaces use `list-spaces action: list, search: "<term>"`; for sources use `list-sources action: list, search: "<term>"`.
- When a user asks "what data do I have?", start with `list-integrations` (action: `list_grouped`) for the big picture, then drill into specific sources.
- Source IDs are needed for data fetching. Always confirm the source ID before calling `fetch-data`.
- The `list_usage` action on `list-sources` shows which reports and widgets reference a source — useful for understanding data dependencies.
- Never fabricate source IDs from memory. If `list-sources` / `fetch-data` responds with `Invalid source_id`, rerun `list-sources action: list` with a `search` term rather than guessing.
- When narrowing sources by `channels`, resolve integration ids from `list-integrations` for **this** team — don't hardcode a channel id from memory. On `list_dimensions_and_metrics`, prefer `filter`/`is_universal` to narrow, and use `page.has_more` (not `estimated_total`, often `null`) to decide whether to paginate.
