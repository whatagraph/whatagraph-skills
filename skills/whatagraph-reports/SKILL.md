---
name: whatagraph-reports
type: domain
description: Create, duplicate, and update reports. Reports live in spaces and contain one or more tabs of widgets. Use when a user wants a new client deliverable, to clone an existing report, or to bulk-swap the data sources a report points at.
required_tools:
  - list-blends
  - list-reports
  - list-source-groups
  - list-sources
  - list-spaces
  - list-templates
  - manage-report-tabs
  - manage-reports
  - manage-widgets
optional_tools:
  - tool_name: list-widgets
    purpose: Inspect / csv_export widgets when verifying a report.
  - tool_name: export-report
    purpose: Verify a built or duplicated report renders with data.
  - tool_name: manage-integrations
    purpose: Attach integration sources to a report.
---

# Reports

Tools covered: `list-reports`, `manage-reports`.

A **report** is a named container of tabs and widgets, scoped to a single **space** (client folder). Reports can be created blank, from a template (linked, auto-updating), or duplicated from an existing report.

A report references data through **report-local sources**. Before a widget on the report can use a data source, the source must be attached to the report — `manage-reports` exposes the attach / detach actions that mirror what the report builder UI does when a user picks a source from the side panel.

## Use this when

- Onboarding a new client — create a blank report or clone from template.
- Rolling out the same report structure to 20 clients — use a template.
- Attaching a data source to a report so widgets can use it — `attach_source`.
- Attaching a sample-data placeholder for a channel — `attach_source` with `channel_ids`.
- Detaching a source the report no longer needs — `detach_source`.
- Migrating a client from sample data to real data — `change_sources`.
- Bulk-swapping a disconnected source for a fresh one — `change_sources`.

## Listing

```
list-reports action=list                                    # paginated
list-reports action=list search="Acme" filter_space_ids=[<id>]
list-reports action=list filter_channel_ids=["google-ads"]  # filter by connected integration
list-reports action=list semantic_search="executive dashboard"  # embedding-based relevance ranking
list-reports action=show report_id=<id>                     # tabs + widgets
list-reports action=list_sources report_id=<id>             # sources used by widgets
list-reports action=resolve url_or_hash="https://live.whatagraph.com/client/123/live-report/456"
```

Each list item includes: `space_name` (parent space), `pages_count` (number of tabs), `sources_summary` (connected integration names like `["Google Ads", "Meta Ads"]`), and `updated_at`. Use these to identify reports without extra calls — `pages_count` and `sources_summary` help distinguish set-up reports from empty scratch ones.

Filter by integration with `filter_channel_ids` (accepts slugs like `"google-ads"`), by source with `filter_source_ids`, or by space with `filter_space_ids`. `semantic_search` finds reports by meaning, not just substring — returns a single bounded set of best matches ranked by relevance (no cursor pagination). `resolve` maps a live-report URL, share URL, hash, or numeric report ID to a `report_id`.

## Create a blank report in a space

```
manage-reports action=create
   client_id=<space_id>
   name="Acme — October 2025"
   tab_name="Overview"          # optional — names the default tab
```

- `client_id` = space id (the `team_client` id). Find via `list-spaces action=list`.
- A default tab is always created with the report (verified Jun 2026) — pass `tab_name` to name it, otherwise it's unnamed. Add further tabs via `manage-report-tabs action=create`.

## Create from a template (linked)

```
manage-reports action=create_from_template
   client_id=<space_id>
   template_id=<template_id>
   name="Custom Report Name"
```

Creates a new report **linked** to the template — structural changes on the template propagate to the report until unlinked. Both `create` and `create_from_template` accept `idempotency_key` for retry-safe creation. When the response shows `uses_sample_data: true`, remap sources with `change_sources` before handing the report over.

## Duplicate an existing report

```
manage-reports action=duplicate report_id=<source_report_id>
```

Copies tabs, widgets, filters, and layout. The duplicate is independent (not linked back to the source).

## Update report metadata

```
manage-reports action=update report_id=<id>
   name="..."
```

## Update the report date range

```
manage-reports action=update report_id=<id>
   date_range={
     "from": "2026-05-01", "till": "2026-05-31",
     "period": "custom",            # or a named period
     "compare_type": "previous",    # or "last_year"; omit for none
     "vs_from": "2026-04-01", "vs_till": "2026-04-30"   # optional explicit comparison window
   }
```

The report-level date range is the baseline **every widget inherits** unless it sets its own `date_range`. Set it when replicating a report into a new period so the widgets — and the comparison deltas — use the right window. `list-reports action=show` returns the current `period`, `compare_type`, `vs_from`, and `vs_till` alongside `from`/`till`.

## Move a report to another space

```
manage-reports action=move report_id=<id> client_id=<target_space_id>
```

`keep_sources` defaults to `true` — attached sources travel with the report. Pass `keep_sources=false` to reset the report to sample data after the move (verified against the served schema, Jun 2026).

## Attach a data source to a report

Before creating a widget that points at a data source, attach the source to the report. This mirrors picking a source in the report builder side panel.

```
manage-reports action=attach_source report_id=<id>
   integration_source_id=<source_id_from_list-sources>

# Batch attach — multiple sources at once:
manage-reports action=attach_source report_id=<id>
   integration_source_ids=[<source_id_1>, <source_id_2>]
```

Response shape differs by count — see **Response reference** below. Creating a widget from the attached source also requires `channel_id`, `widget_type_id`, `tab_id`, and usually `report_type` — see `whatagraph-widgets`.

Source groups and blends work the same way — pass their `id` as `integration_source_id`. Re-attaching an already-attached source returns the existing report-local id (idempotent).

**The source must belong to the report's space.** A report lives in one space; a real source can only be attached if it is assigned to that space, or to no space at all ("All folders"). Attaching a source assigned only to *other* spaces is rejected (the report builder never offers it there, and such a binding gets reset to sample data on the next space sync). Check a source's `space_ids` via `list-sources action=show`; if the report's space isn't listed, assign it first with `manage-integrations action=sync_to_clients` (see `whatagraph-integrations-admin`). The same rule applies to the `to` side of `change_sources`.

## Attach a sample-data source for a channel

When a report should ship with sample data for a channel (template demos, blank reports during onboarding before the client connects), attach a sample placeholder for that channel using the `attach_source` action with `channel_ids` (plural array):

```
manage-reports action=attach_source report_id=<id>
   channel_ids=[<channel_id>]
```

Returns a report-local `source_id` with `is_sample_data: true`. Widgets created against this id show sample numbers; swap to a real source later via `change_sources`.

## Detach a data source from a report

Remove a source the report no longer uses. Two modes:

```
# Default: keep widgets, remap each one to another already-attached source of the same channel.
manage-reports action=detach_source report_id=<id> source_id=<report_local_source_id>

# Optional: delete dependent widgets along with the source.
manage-reports action=detach_source report_id=<id> source_id=<report_local_source_id>
   delete_widgets=true
```

Use `list-reports action=list_sources report_id=<id>` first to discover the report-local `source_id` to detach. See **Response reference** for the response shape.

## Bulk-swap data sources (`change_sources`)

When a template-derived report comes with sample data, or a client is being migrated from Account A to Account B, swap all widget sources at once.

```
manage-reports action=change_sources report_id=<id>
   source_mapping={"<old_source_id>": <new_source_id>, "<old_source_id>": <new_source_id>}
```

Keys are the **global** `integration_source_id` of the source being replaced (`"0"` for sample data); values are the new global `integration_source_id` (`0` to switch back to sample data).

Use `list-reports action=list_sources` to discover current source ids — see **Response reference** for the `list_sources` response shape and which id to use as the mapping key.

> **Verify the build.** After building or bulk-swapping, `export-report report_id=<id>` (or `list-widgets action=csv_export` per widget) and confirm every widget's `data_status` is `ready` with non-empty rows and expected metric names. `list-widgets action=show` is NOT sufficient — it echoes ids, not loaded data.

## Deleting a report

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: soft-delete (support-restorable within a retention window, not via MCP), pre-check `list-templates action=linked_reports` if it might be template-linked.

The `detach_source` action above is also destructive when called with `delete_widgets=true` — that behavior stays documented here because it's core to source migration; `whatagraph-deleting` covers it under "Deletes hiding in manage tools".

## What MCP can't do here

- Share a report — see `whatagraph-sharing`.
- Unlink a template-linked report via MCP — UI only.

## Response reference

### `create` / `duplicate`

```json
{
  "success": true,
  "report": {
    "id": 123,
    "name": "Acme — October 2025",
    "type": "ondemand",
    "space_id": 45,
    "default_tab_id": 678,
    "tabs": [{ "id": 678, "name": "Overview", "position": 0 }]
  }
}
```

### `create_from_template`

Same as `create` plus `linked_template_id`, `uses_sample_data`, and (when sample data is present) `sample_data_channels` and `next_steps`.

### `update`

```json
{
  "success": true,
  "report": { "id": 123, "name": "New Name", "type": "ondemand", "space_id": 45, "date_range": { ... } }
}
```

### `move`

```json
{
  "success": true,
  "message": "Report moved successfully.",
  "report": { "id": 123, "name": "Acme", "type": "ondemand", "space_id": 99 }
}
```

### `attach_source` (single)

```json
{
  "success": true, "report_id": 123,
  "source_id": 456, "integration_source_id": 447295,
  "channel_id": 5, "channel_name": "Google Ads", "name": "My Google Ads", "is_sample_data": false
}
```

### `attach_source` (batch — 2+ sources)

```json
{
  "success": true, "report_id": 123, "attached_count": 3,
  "sources": [
    { "source_id": 456, "integration_source_id": 447295, "channel_id": 5, "channel_name": "Google Ads", "name": "My Google Ads", "is_sample_data": false },
    { "source_id": 457, "integration_source_id": 447296, "channel_id": 12, "channel_name": "Facebook Ads", "name": "My Facebook", "is_sample_data": false }
  ]
}
```

### `detach_source`

```json
{
  "success": true, "report_id": 123, "source_id": 456, "channel_id": 5, "name": "My Google Ads",
  "deleted_widget_ids": [], "remapped_widget_ids": [789, 790],
  "remapped_to": { "source_id": 460, "source_name": "Other Source", "is_sample_data": false }
}
```

### `change_sources`

```json
{
  "success": true, "report_id": 123, "replaced_count": 1, "uses_sample_data": false,
  "replacements": [{
    "old_integration_source_id": null, "new_integration_source_id": 447295,
    "source_id": 456, "is_sample_data": false,
    "affected_widget_ids": [789, 790], "widget_count": 2
  }]
}
```

### `list_sources`

```json
{
  "success": true,
  "integration_sources": [
    { "id": 447295, "name": "My Google Ads", "external_id": "123-456", "channel_id": 5, "account_id": 10, "service": "google-ads", "status": "active", "access_status": "ok" }
  ],
  "sample_integrations": [
    { "id": 12, "service": "facebook-ads", "title": "Facebook Ads", "source_id": 460 }
  ]
}
```

`integration_sources[].id` is the **global** IntegrationSource id (use as `change_sources` key). `sample_integrations[].source_id` is the **report-local** id (use `"0"` as the `change_sources` key for sample data, not this value).

## Common pitfalls

- **`space_id` vs `client_id`** — The input key is `client_id` for the space; `space_id` is rejected. The create response echoes the space as `space_id` — don't feed that response key back as input.
- **`source_mapping` keys as source names** — keys must be the source id as a string (`"12345"`), values are the new source id as integer.
- **Creating a widget before attaching the source** — `manage-widgets` validates `source_id` against the report's attached sources. Call `attach_source` first and use the returned report-local `source_id`.
- **Detaching the last source of a channel without `delete_widgets=true`** — there is no fallback source to remap dependent widgets to; the call fails. Either pass `delete_widgets=true` or attach another source of the same channel first.
- **Creating from a template without re-mapping sources** — the report inherits whatever sources the template defined (often sample data); call `change_sources` immediately after creation.
- **Forgetting that linked reports auto-update** — edits to the template ripple into the linked report. Fine for standardization, surprising for one-off tweaks. If the client needs bespoke changes, duplicate instead of linking.
- **`create_from_template` on a template that's not yet filled out** — the resulting report inherits empty/sample widgets. Verify template via `list-templates action=show` before rolling out.
- **Attaching a source that isn't in the report's space** — `attach_source` (and the `to` side of `change_sources`) rejects a real source assigned only to other spaces. Assign it to the report's space first with `manage-integrations action=sync_to_clients`, or use a source set to "All folders".
- **Asking to update tabs via `manage-reports`** — tabs have their own tool: `manage-report-tabs`.
