---
name: exploring-account-data
description: >-
  Navigate and discover data sources, integrations, metrics, dimensions, spaces,
  reports, and the overall account structure in a Whatagraph account. Use when
  the user asks what data is available, wants to understand their account setup,
  needs to find specific sources or integrations, or asks questions like "what
  channels do I have connected?" or "show me my reports."
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
   - Filter by integration type using `filter_integration_ids`
   - Use `action: list_metadata` on a source to see its available report types
   - Use `action: list_dimensions_and_metrics` to discover available fields for a source

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
| `list-sources` | `list`, `show`, `list_metadata`, `list_dimensions_and_metrics`, `list_usage` | Finding data sources, checking available metrics |
| `list-integrations` | `list`, `list_grouped`, `list_accounts`, `list_available_sources` | Understanding connected channels |
| `list-spaces` | `list`, `show`, `children` | Navigating client/project folders |
| `list-reports` | `list`, `show`, `list_sources` | Finding and examining reports |
| `list-custom-metrics` | `list`, `show` | Discovering user-created metrics |
| `list-custom-dimensions` | `list`, `show` | Discovering user-created dimensions |
| `view-team` | `show`, `search` | Account settings, global search |

## Tips

- Use `view-team` with `action: search` and a `query` to find anything across the account — sources, reports, spaces, blends, and more.
- When a user asks "what data do I have?", start with `list-integrations` (action: `list_grouped`) for the big picture, then drill into specific sources.
- Source IDs are needed for data fetching. Always confirm the source ID before calling `fetch-data`.
- The `list_usage` action on `list-sources` shows which reports and widgets reference a source — useful for understanding data dependencies.
