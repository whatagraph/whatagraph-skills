---
name: whatagraph-reports
type: domain
group: report_building
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
  - tool_name: manage-spaces
    purpose: Create a drafts space to build in when the destination space is not yet approved.
---

# Reports

Tools covered: `list-reports`, `manage-reports`.

A **report** is a named container of tabs and widgets, scoped to a single **space** (client folder). Reports can be created blank, from a template, or duplicated from an existing report.

> **Building the report's contents?** Load `whatagraph-widgets` for the widget writes and `whatagraph-tab-layout` for what goes on each page. Unless the user gave a widget-by-widget spec or a reference to replicate, a generic ask ("create a report for X") means a **multi-tab report where every tab is a full composed page**; `whatagraph-tab-layout` holds that bar, the tab structure rules, and the layout checks.

> **Default: build from scratch. Templates are opt-in, never a shortcut.** `create_from_template` is used only when the request or the agent's instructions explicitly say to use a template (or name one). An open request like "create a report for X" is a scratch build — do not scan the team's templates, and never browse Whatagraph's pre-made template gallery, for a match first. When a template IS explicitly called for, use the **user's own (team-created) template** — the one they named or built — not a pre-made gallery template, unless the instructions name a gallery template specifically. When a template is used, run `change_sources` immediately after `create_from_template`.
>
> **Default: deliver unlinked.** `create_from_template` always produces a **linked** report (template edits propagate into it). Do not hand over a linked report unless the user specifically asks for linking/auto-sync, or it is clearly relevant in the context (e.g. the task is scaling one layout across many clients, or a standardization rollout where reports must stay in step with a master template). For everything else, convert to an independent copy via the duplicate flow in "Create from a template" below.

A report references data through **report-local sources**. Before a widget on the report can use a data source, the source must be attached to the report — `manage-reports` exposes the attach / detach actions that mirror what the report builder UI does when a user picks a source from the side panel.

## Use this when

- Onboarding a new client — create a blank report (from scratch by default); clone from template only when explicitly requested.
- Rolling out the same report structure to 20 clients — use a template; keeping the reports linked is appropriate here because the scaling context makes auto-sync relevant.
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
   layout="printing_landscape_6x6"   # optional — orientation; defaults to landscape
   layout_whitelabel="first_and_last"  # optional — header and footer; defaults to first_and_last
```

- `client_id` = space id (the `team_client` id). Find via `list-spaces action=list`.
- **Never guess the destination space.** `client_id` is not a detail to fill in from the closest-matching space name — a space can be client-facing, and a half-built report that appears there is visible to the client. Follow "Choosing the destination space" below before you call `create`.
- A default tab is always created with the report (verified Jun 2026) — pass `tab_name` to name it, otherwise it's unnamed. Add further tabs via `manage-report-tabs action=create`.
- **Orientation is set here, at create.** `layout` is optional and **defaults to `printing_landscape_6x6`** (wide 6-column grid) when omitted — pass `printing_portrait_4x8` (narrow 4-column grid) only when the user asks for portrait. Setting it inline is the recommended path: a brand-new report has no widgets, so there is no ordering foot-gun and no need to follow up with `manage-report-tabs action=set_layout`. Once widgets exist the layout can no longer be changed via MCP, so decide orientation at create time.
- **The header and footer are on by default.** `layout_whitelabel` is the toggle that draws the theme header and footer, and it defaults to `first_and_last` (first and last page). Pass `all` to draw them on every page, or `none` to hide them. A team whose plan does not include whitelabelling cannot hide them, and `none` is rejected with an error saying so. Unlike `layout`, this one is not fixed at create: change it later with `manage-report-tabs action=set_layout`, on a report with widgets too. See `whatagraph-report-tabs`.

### Choosing the destination space

The space is the user's call, not yours. A report is created in the state you leave it — half-composed, sample data, wrong logo — and if the space is client-facing, that state is what the client sees. Picking the space by name match ("WellJoy Marketing Reports" for a WellJoy report) is the failure this rule exists to stop.

**Ask which space to build in.** One question, before `create`. Show the candidates so the answer is one word:

```
list-spaces action=list                                     # or search="Acme"
list-reports action=list filter_space_ids=[<id>] per_page=5  # what this space already holds
```

If the space already holds finished, client-named reports, treat it as client-facing and say so when you ask.

**When you cannot ask** — an autonomous run, or the user is unavailable — build in a drafts space, then move on approval:

1. Build in the user's own drafts/staging space (a space named like "DRAFTS", "Internal", "Sandbox"). If none exists, create one: `manage-spaces action=create name="Drafts"`.
2. Hand over the finished report and name the space it is in.
3. Move it only after the user approves the destination: `manage-reports action=move report_id=<id> client_id=<target_space_id>` (see "Move a report to another space").

Do not skip step 3 by moving the report yourself, and do not share a report out of a drafts space — the move comes first.

## Create from a template

Only when explicitly requested — see the callout at the top. `create_from_template` always creates a **linked** report (there is no unlink flag, and MCP cannot unlink); whether you keep the link depends on the ask.

```
manage-reports action=create_from_template
   client_id=<space_id>
   template_id=<template_id>
   name="Custom Report Name"
   layout="printing_portrait_4x8"    # optional — overrides the template's orientation
   layout_whitelabel="none"          # optional — header and footer; defaults to first_and_last
```

`client_id` follows the same rule as blank `create` — see "Choosing the destination space". The template does not decide the space, and the linked intermediate below is created in whatever space you pass, so build it in a drafts space too.

**Default — one-off report from a template (unlinked delivery).** Most template requests ("use my monthly template for Acme") want an independent report, not one that silently changes whenever the template is edited. Produce the independent copy like this:

1. `create_from_template` → note the new (linked) `report.id`.
2. `manage-reports action=duplicate report_id=<linked_id>` — the duplicate is independent (not linked to the template).
3. Delete the linked intermediate (`delete-reports`) — it is scaffolding you created seconds ago with no user content, so this delete needs no confirmation round-trip.
4. Continue on the duplicate: rename it to the intended name (`manage-reports action=update`), then `change_sources`, date range, theming.

**Scaling — keep the link.** Keep the report from step 1 as-is (linked) when the user specifically asks for auto-sync, or the context makes it clearly relevant — rolling one layout out across many clients, or centralized template maintenance where reports must stay in step with a master template. Structural changes on the template propagate to it until unlinked.

Both `create` and `create_from_template` accept `idempotency_key` for retry-safe creation. When the response shows `uses_sample_data: true`, remap sources with `change_sources` before handing the report over.

`layout` is optional here and — unlike blank `create` — is **not** defaulted: omit it to keep the template's own orientation, pass it only to override. An explicit `layout` is honoured only while the new report still has no widgets; a template that already carries widgets rejects the override, so keep the template's orientation in that case.

`layout_whitelabel` works the same way here as on blank `create`, and it does not need `layout` alongside it. The header and footer are not part of the grid, so passing it on its own is accepted even when the template already carries widgets.

## Duplicate an existing report

```
manage-reports action=duplicate report_id=<source_report_id>
```

Copies tabs, widgets, filters, and layout. The duplicate is independent (not linked back to the source).

## Building the report's contents

Report creation makes only the container and its first tab. To decide the tabs and fill them (open or partly specified requests, a list of tabs to fill, or a reference to replicate), load `whatagraph-tab-layout`, and use `whatagraph-widgets` for the widget calls. Build the container, tabs and widgets in one continuous flow; never hand back an empty shell.

## Before handing a report over

Run this after the layout checks in `whatagraph-tab-layout`, and on any report you created, duplicated or rebuilt:

1. **Every widget loads real data**: `export-report` (or `list-widgets action=csv_export` per widget) shows `data_status: ready`, non-empty rows and the expected metric names. No "Metrics not selected", no "Unavailable report type", no widget on sample data unless sample data was the ask. `list-widgets action=show` is not enough; it echoes ids, not data.
2. **Date range and comparison are set** at report level, so KPI deltas render (see "Set the date range at creation").
3. **The report is themed** (below).
4. **It sits in the space the user nominated**, which was asked for, not inferred. A report still in a drafts space is handed over as such and moved only after the user approves the destination ("Choosing the destination space").
5. **The confirmation message claims only what the calls proved.** Never state a data status ("Verified", "real non-zero data", "pulling through all layers") that no `fetch-data`, `export-report` or `csv_export` call in this run returned. No verify call means the data is unverified, and the message says so. A call that came back with warnings, sample data or a broken source is reported as that. Name only metrics the report actually holds, never one that appears only in a "suggested next steps" line.

A report failing any of these is not finished.

**Style the report before handing it over.** Once the widgets are built and their data verified, load `whatagraph-themes` and apply a theme and colour palette: the client's branding when the space or prompt shows one, otherwise a coherent existing team theme. The flow is **build → verify (`export-report`) → style**. Skip styling only when the user says to keep the default look, or the report already has the intended theme (e.g. duplicated from a styled report). In an agent fleet, theming is preferably delegated to the branding or delivery agent (theme, palette, fonts, then sharing and automation); `whatagraph-themes` directly is the standalone fallback.

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

## Set the date range at creation (default: last 30 days)

The report-level date range is the baseline every widget inherits, and the report-level `compare_type` is what makes each KPI's trend delta render. A report created without a date range leaves widgets on an undefined window, and KPI cards configured with `comparison_display_type` show no delta because there's no comparison period to diff against. So set both as part of building the report — don't leave them unset.

- **Default window: the last 30 days**, unless the user specifies a period or explicit dates. Prefer a **rolling** last-30-days period so the report stays current after creation rather than freezing on fixed dates — use the platform's rolling `period: "last30Days"` (accepted by the `manage-reports` `date_range.period` schema, alongside `thisMonth`, `lastWeek`, etc.) with `from`/`till` covering the trailing 30 days. Fall back to explicit `from`/`till` with `period: "custom"` only if a rolling window doesn't fit the ask.
- **Default comparison: previous period** (`compare_type: "previous"`), so KPI deltas are meaningful out of the box. Omit the comparison only if the user asks for no comparison, or set `compare_type: "last_year"` if they ask for year-over-year.
- **The user's window always wins.** If they name a period ("last quarter", "March", "this year") or explicit dates, use that and don't apply the 30-day default. If they name a window but no comparison, still apply the previous-period comparison unless they decline it.
- Set this via `manage-reports action=update … date_range={…}` (shape and fields documented in "Update the report date range" above) right after creating the report, before or alongside populating widgets. Individual widgets can still override with their own `date_range` when a specific widget needs a different window.

## Move a report to another space

> **Needs approval.** `move` can drop the report's attached sources, and widgets reading them break. The first call returns a preview and changes nothing; resend the identical call with the `confirm_token` from that preview to execute it. See `whatagraph-deleting` → "The approval gate".

```
manage-reports action=move report_id=<id> client_id=<target_space_id>
```

`keep_sources` defaults to `true` — attached sources travel with the report. Pass `keep_sources=false` to reset the report to sample data after the move (verified against the served schema, Jun 2026).

This is also the second half of the build-in-drafts flow: it is how an approved report leaves the drafts space for its real one. Run it only once the user has confirmed the target space — see "Choosing the destination space".

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

> **Needs approval.** `detach_source` removes a source widgets read through, and with `delete_widgets=true` deletes those widgets. The first call returns a preview and changes nothing; resend the identical call with the `confirm_token` from that preview to execute it. See `whatagraph-deleting` → "The approval gate".

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

> **Needs approval.** `change_sources` repoints every widget at once; a wrong mapping breaks the whole report. The first call returns a preview and changes nothing; resend the identical call with the `confirm_token` from that preview to execute it. See `whatagraph-deleting` → "The approval gate".

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
    "layout": "printing_landscape_6x6",
    "layout_type": "desktop_landscape",
    "default_tab_id": 678,
    "tabs": [{ "id": 678, "name": "Overview", "position": 0 }]
  }
}
```

The `layout` / `layout_type` fields are returned by `create` only (it echoes the orientation it applied — landscape by default). `duplicate` copies the source report's layout but does not echo these fields in its response.

### `create_from_template`

Same as `create` plus `linked_template_id`, `uses_sample_data`, and (when sample data is present) `sample_data_channels` and `next_steps`. `layout` / `layout_type` reflect the template's layout unless an explicit `layout` was passed to override it.

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

- **`space_id` as input**: the space key is `client_id`; `space_id` is rejected. The create response echoes `space_id`; do not feed it back.
- **`source_mapping` keys**: keys are source ids as strings (`"12345"`), values are integers.
- **Creating a widget before attaching its source**: `manage-widgets` checks `source_id` against the report's attached sources. Attach first and use the returned report-local `source_id`.
- **Detaching the last source of a channel without `delete_widgets=true`**: there is nothing to remap to, so the call fails. Pass `delete_widgets=true` or attach another source of that channel first.
- **"Overview" is ambiguous**: it can mean a report tab, a summary-style report, or the standalone **Overview / Measurement** entity (`whatagraph-overviews`). A bare "create an overview for X" needs a question before building (`whatagraph-mcp-overview`).
- **A template on an open request**: "create a report for X" is a scratch build; do not scan `list-templates` or the gallery for a fit.
- **Linked reports change with their template**: fine for standardization, surprising for one-off tweaks. For bespoke changes, duplicate instead.
- **A template that is not filled out** gives empty or sample widgets. Check it with `list-templates action=show` before rolling it out.
- **Editing tabs through `manage-reports`**: tabs have their own tool, `manage-report-tabs`.
