---
name: whatagraph-snapshots
type: domain
group: distribution_lifecycle
description: Save (create) and restore the structural state of a report — tabs, widgets, layout. Use when a user wants a checkpoint before a risky edit, to revert to a prior version, or to view snapshot history. Handles asks like "save a backup of this report before I change it", "undo my changes and go back to the previous version", or "show me this report's version history".
required_tools:
  - list-snapshots
  - manage-snapshots
optional_tools:
  - tool_name: delete-snapshots
    purpose: Remove an old snapshot when pruning version history.
  - tool_name: list-widgets
    purpose: Re-read widgets after a restore to find ones broken by source changes.
  - tool_name: manage-reports
    purpose: Repair a widget's broken source binding after a restore.
  - tool_name: manage-sharing
    purpose: Produce a PDF/Excel compliance artifact — snapshots re-query at view time.
---

# Snapshots

Tools covered: `list-snapshots`, `manage-snapshots`, `delete-snapshots`.

A **snapshot** captures a report's structure (tabs, widget configs, layout, theme) at a point in time. Data values are not stored — they re-query at view time against current sources.

## Use this when

- "Snapshot this report before I swap all its sources."
- "Roll the report back to the version we had before the rebrand."
- Auditing when the report was last saved.

## Listing

```
list-snapshots action=list report_id=<id>
list-snapshots action=list report_id=<id> per_page=32 cursor=<cursor>
```

Pagination: cursor-based (not page-number). `per_page` is an integer (default 100, max 500). Pass `cursor` from `page.cursor` in the response to get the next page.

## Viewing snapshot details

```
list-snapshots action=show report_id=<id> snapshot_id=<id>
```

Returns full snapshot details: `pages_count`, `widgets_count`, `sources_count`, `type`, `created_by`, and `created_at`. Use this to inspect what a snapshot contains before deciding to restore it.

## Create (save) a snapshot

```
manage-snapshots action=create report_id=<id>
```

Captures the current structure. No `name` parameter — the snapshot is identified by creator + timestamp.

## Restore a snapshot (overwrites current structure)

> **Needs approval.** `restore` overwrites the report's current tabs, widgets, and sources. The first call returns a preview and changes nothing; resend the identical call with the `confirm_token` from that preview to execute it. See `whatagraph-deleting` → "The approval gate".

```
manage-snapshots action=restore report_id=<id> snapshot_id=<id>
```

Restore rewrites the report's tabs, widgets, and layout to the snapshot state. **Destructive** — take a fresh `create` before restoring if the current state is also worth keeping.

## Deleting a snapshot

```
delete-snapshots action=delete report_id=<id> snapshot_id=<id>
```

Permanent — no restore of any kind. Keep at least one recent snapshot on actively edited reports. See `whatagraph-deleting` for broader deletion context.

## What MCP can't do here

- Compare two snapshots (diff view) — UI only.
- Name a snapshot — UI only.

## Common pitfalls

- **Restore after source changes** — widgets can break if referenced sources/fields no longer exist. Re-run `list-widgets action=show` after restore and fix any broken sources via `manage-reports action=change_sources`.
- **Snapshots for compliance archival** — unreliable (data re-queries at view time). Use `export-report` (`format=pdf` or the default `xlsx`) for compliance artifacts.
- **Accidental destructive restore** — always confirm with the user before `manage-snapshots action=restore`. There is no undo.
- **Creating a snapshot while widgets are broken** — snapshot captures the broken state. Fix widgets first, then snapshot.
