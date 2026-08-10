---
name: whatagraph-report-tabs
type: domain
description: Create, duplicate, rename, and reorder tabs within a report, and open or close rows in a tab's grid. Each tab is a page of widgets. Use when a report needs a new section (e.g. "Paid Search", "Social", "Organic"), when existing tabs need to be re-ordered or duplicated, when a widget has to go between two existing rows, or when a tab has blank rows to close up. Handles asks like "add a new page to this report", "rename the second tab", "reorder the report sections", "insert a row between these two widgets", or "remove the empty rows / close the gaps / compact the tab".
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
- "Add a row between these two widgets." / "Insert a line above the table."
- "Remove the empty rows." / "Close the gaps on this tab." / "Compact the layout."

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

> **A created tab is not done until it's a full page.** When building out a report — whether the tabs came from the user, an agent's instructions, or your own structure — every tab you create must be populated as a complete composed page before the report is handed over: two or more sections with headers, a varied widget mix, verified data (see `whatagraph-widgets` → "Composing a full tab" and `whatagraph-reports` → the pre-handover checklist). Never leave a tab empty or holding just one or two widgets — a named tab is a request for a full themed page, not a placeholder.

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

## Insert or remove rows in a tab

This is the UI's "Insert line below" / "Remove line". It moves widgets and nothing else — it adds no widget and deletes none.

```
manage-report-tabs action=insert_row_space report_id=<id> tab_id=<id>
   position_y=4          # first row to open
   row_count=2           # how many rows (defaults to 1)
```

Every widget starting at `position_y` or below moves down by `row_count`, in one call.

⚠️ **"Add a row" is finished when this returns.** A request for a row, a line, or a gap is a request for *empty space*. Do not follow it with a widget the user never asked for — creating a placeholder Comment ("New row") or any invented widget puts filler into a client-facing report. If the ask is genuinely ambiguous, open the space and say what you did, or ask which widget they want.

**When the user *did* ask for a widget there**, open the space first, then create it — `manage-widgets` cannot place a widget into an occupied row, and `auto_place=true` sends it to the nearest free slot instead of the row you asked for:

```
manage-report-tabs action=insert_row_space report_id=<id> tab_id=<id> position_y=4 row_count=2
manage-widgets action=create report_id=<id> tab_id=<id>
   position_x=0 position_y=4 options={width: 6, height: 2} …
```

Match `row_count` to the height of that widget, or it still overlaps the row below. Read the neighbours' real `height` (via `list-widgets`) rather than assuming 1 — heights vary.

`remove_row_space` is the inverse — it closes empty rows and moves everything below up:

```
manage-report-tabs action=remove_row_space report_id=<id> tab_id=<id>
   position_y=4 row_count=2
```

**The rows must already be empty.** This never deletes or resizes a widget: if anything occupies or reaches into the range, the call is rejected and the error names both the blocking widget ids and the rows that *are* free (`Free rows on this tab: 4–5.`). Read that list rather than guessing a second range — free rows are the gaps between widget spans, so they don't appear as any widget's `position_y`. To close a row that holds a widget, move or delete the widget first.

### Closing every gap on a tab

"Remove the empty rows", "close the gaps", "compact the tab" means every gap, and there is no single call for it yet. Do it in three steps:

1. `list-widgets action=list report_id=<id>` — you need `position_y` **and** `height`; `list-report-tabs action=show` returns positions without heights.
2. Expand each widget to the rows it occupies (`position_y` … `position_y + height - 1`) and take the gaps between those ranges. Gaps don't appear as any widget's `position_y`, so they have to be derived — with widgets at rows 0–2, 4–5, and 8–9, the gaps are row 3 and rows 6–7.
3. Call `remove_row_space` once per gap, **bottom-up** — closing a gap renumbers every row below it, so a top-down pass leaves your remaining ranges stale and the next call either rejects or closes the wrong rows.

For the example above: `remove_row_space position_y=6 row_count=2`, then `remove_row_space position_y=3 row_count=1`.

⚠️ **Don't compact by moving widgets instead.** Shifting each widget up with `manage-widgets action=update` reaches the same layout — upward moves never collide, so nothing rejects — but it is one call per widget, outside any transaction, and it rewrites positions the user never asked to change. Use `remove_row_space` and keep each gap closed in one atomic call.

Rows below the last widget need no action; they are already past the end of the content.

A widget that starts *above* the insertion row and reaches into it stays where it is, at its original height — nothing is resized. The gap then doesn't span every column, so the response returns `spanning_widget_ids` and says so; check those widgets' columns before choosing `position_x`.

Neither action works on a linked report — its widgets are managed by the linked template.

## Set report layout (print-ready)

```
manage-report-tabs action=set_layout report_id=<id>
   layout="printing_landscape_6x6"       # or "printing_portrait_4x8"
   border_radius_size="medium"           # none | small | medium | large
   show_page_numbers=true
```

Sets the report's grid orientation. Only works while the report has **no widgets** yet — changing it later would misplace existing widgets, so it's rejected.

**Prefer setting orientation at create instead.** For a brand-new report, pass `layout` directly to `manage-reports action=create` (it defaults to landscape) — a single call with no ordering foot-gun. Reach for `set_layout` here only to change the orientation of an already-created report that is *still empty*, or to also adjust `border_radius_size` / `show_page_numbers`.

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
- **Rebuilding a tab to insert one widget** — never move widgets one at a time to open a row, and never rebuild the tab in a temporary tab. `insert_row_space` does it in one call.
- **`insert_row_space` with a `row_count` smaller than the new widget** — the widget overlaps the row below and the create is rejected. Open as many rows as the widget is tall.
- **Compacting a tab by moving widgets up one at a time** — reaches the right layout without ever rejecting, which is why it looks fine, but it's one un-transactioned call per widget. Use `remove_row_space` per gap instead.
- **Closing gaps top-down** — the first removal renumbers every row below it, so later ranges are stale. Work bottom-up.
- **Deep-link to a specific tab** — share URL `#tab:<tab_id>` hash selects the tab (pattern: `https://live.whatagraph.com/client/<team_client_id>/live-report/<report_id>#tab:<tab_id>`).
