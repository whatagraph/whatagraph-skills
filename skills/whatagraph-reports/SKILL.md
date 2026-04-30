---
name: whatagraph-reports
description: Create, duplicate, and update reports. Reports live in spaces and contain one or more tabs of widgets. Use when a user wants a new client deliverable, to clone an existing report, or to bulk-swap the data sources a report points at.
---

# Reports

Tools covered: `list-reports`, `manage-reports`, `delete-reports`.

A **report** is a named container of tabs and widgets, scoped to a single **space** (client folder). Reports can be created blank, from a template (linked, auto-updating), or duplicated from an existing report.

## Use this when

- Onboarding a new client — create a blank report or clone from template.
- Rolling out the same report structure to 20 clients — use a template.
- Migrating a client from sample data to real data — `change_sources`.
- Bulk-swapping a disconnected source for a fresh one — `change_sources`.

## Listing

```
list-reports action=list                                    # paginated
list-reports action=list search="Acme" filter_space_ids=[<id>]
list-reports action=show report_id=<id>                     # tabs + widgets
list-reports action=list_sources report_id=<id>             # sources used by widgets
```

## Create a blank report in a space

```
manage-reports action=create
   client_id=<space_id>
   name="Acme — October 2025"
```

- `client_id` = space id (the `team_client` id). Find via `list-spaces action=list`.
- The report starts with zero tabs — add tabs via `manage-report-tabs action=create`.

## Create from a template (linked)

```
manage-reports action=create_from_template
   client_id=<space_id>
   template_id=<template_id>
```

Creates a new report **linked** to the template — structural changes on the template propagate to the report until unlinked.

Afterward, remap sources using `change_sources`.

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

## Bulk-swap data sources (`change_sources`)

When a template-derived report comes with sample data, or a client is being migrated from Account A to Account B, swap all widget sources at once.

```
manage-reports action=change_sources report_id=<id>
   source_mapping={"<old_source_id>": <new_source_id>, "<old_source_id>": <new_source_id>}
```

Special cases:
- `"0"` as old id → replace sample data with a real source.
- `0` as new id → switch a real source to sample data.

Use `list-reports action=list_sources report_id=<id>` to discover current source ids.

## Deleting a report

```
delete-reports action=delete report_id=<id>
```

Soft-delete — the report disappears from the space but can be restored by support for a retention window. Always confirm with the user, and check `list-templates action=linked_reports` first if the report is linked to a template.

## What MCP can't do here

- Share a report — see `whatagraph-sharing`.
- Change a report's space after creation — duplicate into the new space instead.
- Unlink a template-linked report via MCP — UI only.
- Set or override date range on the whole report via MCP — use `manage-widgets` per widget for widget-level ranges; report-level date lives in options via UI.

## Common pitfalls

- **`space_id` vs `client_id`** — MCP uses `client_id` for the space. `space_id` is rejected.
- **`source_mapping` keys as source names** — keys must be the source id as a string (`"12345"`), values are the new source id as integer.
- **Creating from a template without re-mapping sources** — the report inherits whatever sources the template defined (often sample data); call `change_sources` immediately after creation.
- **Forgetting that linked reports auto-update** — edits to the template ripple into the linked report. Fine for standardization, surprising for one-off tweaks. If the client needs bespoke changes, duplicate instead of linking.
- **`create_from_template` on a template that's not yet filled out** — the resulting report inherits empty/sample widgets. Verify template via `list-templates action=show` before rolling out.
- **Asking to update tabs via `manage-reports`** — tabs have their own tool: `manage-report-tabs`.
