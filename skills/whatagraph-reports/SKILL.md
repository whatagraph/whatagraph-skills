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
---

# Reports

Tools covered: `list-reports`, `manage-reports`.

A **report** is a named container of tabs and widgets, scoped to a single **space** (client folder). Reports can be created blank, from a template, or duplicated from an existing report.

> **The quality bar.** Unless the user gave a widget-by-widget spec or a reference to replicate, a generic ask ("create a report for X") means a **multi-tab report where every tab is a full composed page** — two or more sections, a varied widget mix, typically 8–14 widgets per tab. Defaulting to ~6 or fewer widgets on a tab is under-building, not efficiency. Full rules in "Building a report when the request doesn't specify structure" and the pre-handover checklist below, plus `whatagraph-widgets` → "Composing a full tab".

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
```

- `client_id` = space id (the `team_client` id). Find via `list-spaces action=list`.
- A default tab is always created with the report (verified Jun 2026) — pass `tab_name` to name it, otherwise it's unnamed. Add further tabs via `manage-report-tabs action=create`.
- **Orientation is set here, at create.** `layout` is optional and **defaults to `printing_landscape_6x6`** (wide 6-column grid) when omitted — pass `printing_portrait_4x8` (narrow 4-column grid) only when the user asks for portrait. Setting it inline is the recommended path: a brand-new report has no widgets, so there is no ordering foot-gun and no need to follow up with `manage-report-tabs action=set_layout`. Once widgets exist the layout can no longer be changed via MCP, so decide orientation at create time.

## Create from a template

Only when explicitly requested — see the callout at the top. `create_from_template` always creates a **linked** report (there is no unlink flag, and MCP cannot unlink); whether you keep the link depends on the ask.

```
manage-reports action=create_from_template
   client_id=<space_id>
   template_id=<template_id>
   name="Custom Report Name"
   layout="printing_portrait_4x8"    # optional — overrides the template's orientation
```

**Default — one-off report from a template (unlinked delivery).** Most template requests ("use my monthly template for Acme") want an independent report, not one that silently changes whenever the template is edited. Produce the independent copy like this:

1. `create_from_template` → note the new (linked) `report.id`.
2. `manage-reports action=duplicate report_id=<linked_id>` — the duplicate is independent (not linked to the template).
3. Delete the linked intermediate (`delete-reports`) — it is scaffolding you created seconds ago with no user content, so this delete needs no confirmation round-trip.
4. Continue on the duplicate: rename it to the intended name (`manage-reports action=update`), then `change_sources`, date range, theming.

**Scaling — keep the link.** Keep the report from step 1 as-is (linked) when the user specifically asks for auto-sync, or the context makes it clearly relevant — rolling one layout out across many clients, or centralized template maintenance where reports must stay in step with a master template. Structural changes on the template propagate to it until unlinked.

Both `create` and `create_from_template` accept `idempotency_key` for retry-safe creation. When the response shows `uses_sample_data: true`, remap sources with `change_sources` before handing the report over.

`layout` is optional here and — unlike blank `create` — is **not** defaulted: omit it to keep the template's own orientation, pass it only to override. An explicit `layout` is honoured only while the new report still has no widgets; a template that already carries widgets rejects the override, so keep the template's orientation in that case.

## Duplicate an existing report

```
manage-reports action=duplicate report_id=<source_report_id>
```

Copies tabs, widgets, filters, and layout. The duplicate is independent (not linked back to the source).

## Building a report when the request doesn't specify structure

This governs *what* to build on `manage-reports action=create` (and on `create_from_template` / `duplicate` when the user asks to flesh a report out). The sizing, placement, and field-binding mechanics live in `whatagraph-widgets` — this section only decides the report's shape.

First, decide which mode you're in:

1. **The user specified the full structure** — they enumerated the actual **widgets** (a widget-by-widget spec: which widget types, which metrics on each, where they sit), or handed a reference (PDF / screenshot / live-report URL / existing report). → Build exactly that: **what they named is a contract.** Every named metric, tab, and widget appears — map the user's wording to the source's exact fields via `list-sources action=list_dimensions_and_metrics` (match by meaning when their term differs from the field name, e.g. "cost" → the source's spend metric). Nothing they didn't ask for is added, their naming and order are kept, and a detailed spec is never collapsed into something smaller. If something requested doesn't exist on the source (a metric the integration doesn't expose), don't silently substitute — build the rest and tell the user what's missing and the closest available field. Skip the rest of this section and follow the reference/instruction faithfully (see `whatagraph-widgets` → "Replicating a reference report").

   ⚠️ **A tab list is not a widget spec.** Instructions that enumerate tabs and per-tab themes or metric lists — e.g. *"Construct the report with these 6 tabs: 1. General Overview (cross-channel KPIs)… 2. Google Ads: performance widgets for spend, clicks, impressions, conversions…"* — do **not** put you in this mode. They fix the tab set, tab names, order, and each tab's focus, and nothing else. That is a **partially-specified request** (see below): every named tab still gets the full open-ended composition bar — multiple sections, a varied widget mix, a complete page. Reading a tab list as "one widget per named metric" or "a couple of widgets per tab" is the classic failure: it ships six near-empty pages and calls them a report.

2. **The request is open-ended** — "create a report", "visualise this source", "build me a dashboard", "make a report for `<channel>`", with no tab / widget / metric detail. → Do **not** ship a single tab of generic KPIs. Build a detailed, multi-tab report as below.

An open-ended report is **multi-tab and thematic**:

- **Let the data set the tab count — and for any metric-rich source, three tabs is the floor.** Inspect the available metrics and dimensions first (`list-sources action=list_dimensions_and_metrics`), enumerate the distinct analytical themes the source actually supports, and give **each substantial theme its own tab**. Calibrate against what you find: a **metric-rich source** — GA4, Search Console, or any mainstream ad platform, i.e. anything exposing dozens of metrics across several dimension families (cost, conversions, devices, audience, geography, creatives, search terms) — gets **at least 3 tabs, often 4–5**; a genuinely narrow source (a handful of metrics, one or two dimensions) may only sustain 2; a multi-source or blended request sustains more (e.g. a cross-channel overview tab plus one tab per channel). Two tabs is the floor for the **narrow case only** — never the default landing spot. If you find yourself building 2 tabs for every source regardless of its richness, you've stopped reading the data.
- **Read the prompt for scale signals too.** "Client deliverable", "monthly report", "full performance report", "dashboard for the team" all imply the fuller end of the range even when the user never says "detailed". Only a deliberately small ask ("quick overview", "one-pager", "just the KPIs") caps the report at the lean end — and then respect that cap.
- Which themes apply depends entirely on what the source(s) actually expose. Illustrative theme shapes **only** (never a fixed template): an overview / traffic tab, a conversions / outcomes tab, a spend / efficiency tab, an audience / geography tab, a creative / content tab, a campaign-deep-dive tab. A source with no cost data gets no spend tab; a source with no creative dimension gets no creative tab — and conversely, when the data supports a theme, add its tab rather than compressing two themes onto one page.
- **Every tab must be a full page — at least two sections, not one.** A tab holding one lone table, or a strip of KPIs plus a single chart, reads as unfinished and leaves no room to showcase more than a couple of widget types. Each themed tab gets a complete composition of **two or more sections** (three where the data supports it), each with its own header, KPIs, charts, and detail working together (see `whatagraph-widgets` → "Composing a full tab"). If a theme can't fill a page from the available data, merge it into a related tab instead of shipping a thin one.
- **Order tabs like a story, and name them for the reader.** The report reads front to back: the broadest tab first (overview / headline results), themed deep-dives next, the most granular detail (long per-entity tables) last. Tab names are short, client-readable labels — "Overview", "Conversions", "Audience" — not sentences or metric lists. (An "Overview" *tab* inside a report is unrelated to the standalone **Overview / Measurement** entity — when a user's prompt says "overview" outside a clear report-tab context, disambiguate before building; see `whatagraph-mcp-overview` → the "Overview is overloaded" callout and `whatagraph-overviews`.)
- The report's first tab is created with the report itself — name it after its theme via `tab_name`. Add the remaining themed tabs with `manage-report-tabs action=create`.
- Different sources → different tab sets. If every open-ended report you build has the same tabs, you've defaulted to a template — go back to the data.

**Populate every tab via `whatagraph-widgets`.** Report creation only makes the container and the tabs. Load and follow `whatagraph-widgets` to fill each tab — it owns widget-type selection, fit-for-purpose metric/dimension binding, the grid layout (no gaps/overlaps), titles, section headers, and the full-tab composition guidance. A report is not "created" until its tabs hold widgets and those widgets have verified data (`export-report`). Build the container, tabs, and widgets in one continuous flow — don't hand back an empty shell.

**Before handing any report over, walk this checklist — every mode, every time:**

1. **Every tab is a full page** — two or more sections with headers, a varied widget mix, no tab with just one or two widgets, no half-empty grid below the last row.
2. **Every widget loads real data** — `export-report` (or per-widget `csv_export`) shows `data_status: ready` with non-empty rows and the expected metric names. No "Metrics not selected", no "Unavailable report type", no widget still on sample data unless sample data was the ask.
3. **Every binding is compatible** — metrics and dimensions verified against `list-sources action=list_dimensions_and_metrics`, all fields in a config share one `report_type`, dimension requirements per widget type respected (see `whatagraph-widgets`).
4. **Layout is clean** — rows fill their width, no gaps or overlaps, no stranded widget with empty columns beside it.
5. **Everything is titled** — report, tabs, widgets, metric rows; section headers introduce each section.
6. **Date range and comparison are set** at report level so KPI deltas render.
7. **The report is themed** (below).

A report failing any of these is not finished — fix it before reporting the build as done.

**Style the report before handing it over.** A finished deliverable is themed, not default-chrome. Once the widgets are built and their data verified, load `whatagraph-themes` and apply a theme and color palette: the client's branding when the space or prompt indicates one, otherwise a coherent existing team theme. The delivery flow is **build → verify (`export-report`) → style (`whatagraph-themes`)** — the styling pass is part of creating the report, not an optional extra. Skip it only when the user explicitly says to leave the default look, or the report already carries the intended theme (e.g. it was duplicated from a styled report). In an agent-fleet context, theming/branding is preferentially **delegated to the branding/delivery agent** (theme, palette, fonts, then sharing/automation); applying via `whatagraph-themes` directly is the standalone fallback. Either way the chain is build → verify → brand — a report is not done until it is themed.

**Partially-specified requests get the full open-ended bar for everything unspecified.** "Aggregate Q2 data into a detailed report", "report focused on conversions", a tab list with per-tab themes, or a request naming metrics but not widgets/placement is NOT spec mode — the named focus, tabs, sources, metrics, and window are contracts, but the structure of everything unspecified (widget mix, sections, layout, headers) follows the open-ended rules above in full. A short prompt never licenses a thin report.

**Partial detail** — honour whatever the user specified and use judgment only for the gaps: if they named the tabs but not the widgets, build exactly their tabs (names and order kept) and compose **each one as a full page** per `whatagraph-widgets` → "Composing a full tab" — the tab's stated theme and any named metrics scope *what* goes on the page, never *how little*; if they named metrics but not layout, bind those metrics and lay them out cleanly, adding the supporting composition (headers, trend, breakdown, detail) around them; if they asked for one tab only, respect that — and still fill it.

**The per-tab floor is absolute.** However the tab list came about — user prompt, agent instructions, or your own theming — **no tab ships with one or two widgets.** A named tab is a request for a complete themed page (two or more sections, a varied widget mix, roughly 8–14 widgets — see `whatagraph-widgets` → "Composing a full tab"), not a container for a token KPI. If a named tab's theme genuinely can't sustain a full page from the available fields, don't ship it thin: merge it into a related tab, or — when the tab list was an explicit instruction — build the fullest page the data supports and tell the user which tab is data-constrained and why.

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

- **`space_id` vs `client_id`** — The input key is `client_id` for the space; `space_id` is rejected. The create response echoes the space as `space_id` — don't feed that response key back as input.
- **`source_mapping` keys as source names** — keys must be the source id as a string (`"12345"`), values are the new source id as integer.
- **Creating a widget before attaching the source** — `manage-widgets` validates `source_id` against the report's attached sources. Call `attach_source` first and use the returned report-local `source_id`.
- **Detaching the last source of a channel without `delete_widgets=true`** — there is no fallback source to remap dependent widgets to; the call fails. Either pass `delete_widgets=true` or attach another source of the same channel first.
- **Building a report when the user meant an Overview (or vice versa)** — "overview" in a prompt can mean a report tab, a summary-style report, or the standalone **Overview / Measurement** entity (`whatagraph-overviews`). Inside a tab list or report context it's a tab; a bare "create an overview for X" is ambiguous — ask the user which they mean before building. See `whatagraph-mcp-overview` for the full disambiguation rules.
- **Treating a tab list as a full spec** — instructions that enumerate tabs and per-tab metric themes fix the tab set and focus, nothing more. Building one or two widgets per named tab ships a shell of near-empty pages; each named tab gets the full composition bar (see "Building a report when the request doesn't specify structure" and the pre-handover checklist).
- **Reaching for a template on an open request** — "create a report for X" means build from scratch. Scanning `list-templates` (or the pre-made gallery) for something that "fits" is a template pick nobody asked for.
- **Handing over a linked report nobody asked to be linked** — `create_from_template` always links. Unless the user asked for auto-sync or the context clearly calls for it (a many-client scaling rollout), run the duplicate → delete-intermediate flow so the delivered report is independent.
- **Creating from a template without re-mapping sources** — the report inherits whatever sources the template defined (often sample data); call `change_sources` immediately after creation.
- **Forgetting that linked reports auto-update** — edits to the template ripple into the linked report. Fine for standardization, surprising for one-off tweaks. If the client needs bespoke changes, duplicate instead of linking.
- **`create_from_template` on a template that's not yet filled out** — the resulting report inherits empty/sample widgets. Verify template via `list-templates action=show` before rolling out.
- **Attaching a source that isn't in the report's space** — `attach_source` (and the `to` side of `change_sources`) rejects a real source assigned only to other spaces. Assign it to the report's space first with `manage-integrations action=sync_to_clients`, or use a source set to "All folders".
- **Asking to update tabs via `manage-reports`** — tabs have their own tool: `manage-report-tabs`.
