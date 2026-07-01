---
name: whatagraph-report-tabs
type: domain
description: Create, duplicate, rename, and reorder tabs within a report. Each tab is a page of widgets. Use when a report needs a new section (e.g. "Paid Search", "Social", "Organic") or when existing tabs need to be re-ordered or duplicated. Handles asks like "add a new page to this report", "rename the second tab", or "reorder the report sections".
required_tools:
  - list-report-tabs
  - manage-report-tabs
  - delete-report-tabs
  - manage-widgets
---

# Report tabs (pages)

Tools covered: `list-report-tabs`, `manage-report-tabs`, `delete-report-tabs`.

A **tab** is a page inside a report. Each tab holds its own widgets. Reports can have one or many tabs; tabs appear in the top navigation of the report.

## Use this when

- "Add a 'Paid Social' tab to this report."
- "Duplicate the Overview tab as a starting point for a client variant."
- "Reorder tabs — Overview first, Paid second, Organic third."
- "Move these three widgets from the Overview tab to a new Campaigns tab."

## Listing

```
list-report-tabs action=list report_id=<id>               # summaries (visible tabs only)
list-report-tabs action=list report_id=<id> include_hidden=true   # include hidden tabs
list-report-tabs action=show report_id=<id> tab_id=<id>   # full widget list
```

By default, `list` returns only visible tabs. Pass `include_hidden: true` to include hidden tabs; when set, each tab includes a `hidden` boolean field.

## Create a tab

Reports are created with one default tab whose `name` is `null`. Always run `list-report-tabs action=list` first, then `update` that default tab's name in place rather than calling `create` for the report's first named tab — otherwise you leave an unnamed default tab alongside the new one.

```
list-report-tabs action=list report_id=<id>
# response: [{id: <default_tab_id>, name: null, …}]

manage-report-tabs action=update report_id=<id>
   tab_id=<default_tab_id> name="Overview"
```

Use `create` only for additional tabs beyond the first:

```
manage-report-tabs action=create report_id=<id> name="Paid Social"
manage-report-tabs action=create report_id=<id> name="Hidden Tab" hidden=true
```

The new tab starts empty — add widgets via `manage-widgets action=create` or `manage-widgets action=create_premade`.

## Duplicate a tab

```
manage-report-tabs action=duplicate report_id=<id> tab_id=<source_tab_id>
```

Clones the tab and all its widgets. Duplicated widgets preserve source and config. Useful for creating a per-channel variant of a template tab.

## Rename or hide/show a tab

```
manage-report-tabs action=update report_id=<id> tab_id=<id> name="New Name"
manage-report-tabs action=update report_id=<id> tab_id=<id> hidden=true    # hide from viewers
manage-report-tabs action=update report_id=<id> tab_id=<id> hidden=false   # make visible again
```

Hidden tabs are excluded from shared/exported views. Use `list-widgets tab_hidden=true` to find widgets on hidden tabs, or `tab_hidden=false` for visible-only.

## Reorder tabs

```
manage-report-tabs action=sort report_id=<id>
   tab_order=[<tab_id_1>, <tab_id_2>, <tab_id_3>]
```

Pass the **full** list of tab ids in the desired order. Partial lists are rejected.

## Move widgets between tabs

```
manage-report-tabs action=move_widgets
   report_id=<id>
   tab_id=<source_tab_id>
   widget_ids=[<w1>, <w2>]
   target_tab_id=<destination_tab_id>
```

Widgets retain their configs and sources; only their tab assignment changes.

## Set tab layout (print-ready)

```
manage-report-tabs action=set_layout report_id=<id> tab_id=<id>
   layout="printing_landscape_6x6"       # or "printing_portrait_4x8"
   border_radius_size="medium"           # none | small | medium | large
   show_page_numbers=true
```

Only works on tabs with **no widgets** yet — set layout before adding widgets. Useful for print-optimized report pages.

## Deleting / restoring a tab

```
delete-report-tabs action=delete  report_id=<id> tab_id=<id>
delete-report-tabs action=restore report_id=<id> tab_id=<id>
```

Soft-delete — the tab's widgets soft-delete and restore with it. A report must keep at least one tab; deleting the last one is rejected. See `whatagraph-deleting` for full context.

> **Verify the build.** After building or bulk-swapping, `export-report report_id=<id>` (or `list-widgets action=csv_export` per widget) and confirm every widget's `data_status` is `ready` with non-empty rows and expected metric names. `list-widgets action=show` is NOT sufficient — it echoes ids, not loaded data.

## What MCP can't do here

- Set a tab-specific date range via MCP — date range lives at widget level; override there if needed (`manage-widgets action=update` with `date_range=`).
- Protect a tab from editing — UI only.

## Common pitfalls

- **`sort` with a partial list** — must include every tab id. Missing ids cause rejection.
- **Leftover empty "New tab"** — the UI auto-creates an empty tab on new reports; rename it with `manage-report-tabs action=update`, or delete it (see `whatagraph-deleting`).
- **Duplicate tab with widgets on disconnected sources** — duplication preserves broken state; `change_sources` on the report after duplicating.
- **Too many tabs (10+)** — client-facing reports with 10+ tabs overwhelm readers. Consolidate into a few themes.
- **Moving widgets across reports** — not supported; widgets are scoped to their report. Duplicate the widget in target report, delete original.
- **Deep-link to a specific tab** — share URL `#tab:<tab_id>` hash selects the tab (pattern: `https://live.whatagraph.com/client/<team_client_id>/live-report/<report_id>#tab:<tab_id>`).
