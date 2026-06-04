---
name: whatagraph-snapshots
description: Save (create) and restore the structural state of a report — tabs, widgets, layout. Use when a user wants a checkpoint before a risky edit, to revert to a prior version, or to view snapshot history.
required_tools:
  - manage-snapshots
  - delete-snapshots
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
list-snapshots action=list report_id=<id>                     # paginated
list-snapshots action=list report_id=<id> per_page="32" page=2   # valid per_page: 16, 32, 64, 128
```

## Create (save) a snapshot

```
manage-snapshots action=create report_id=<id>
```

Captures the current structure. No `name` parameter — the snapshot is identified by creator + timestamp.

## Restore a snapshot (overwrites current structure)

```
manage-snapshots action=restore report_id=<id> snapshot_id=<id>
```

Restore rewrites the report's tabs, widgets, and layout to the snapshot state. **Destructive** — take a fresh `create` before restoring if the current state is also worth keeping.

## Deleting a snapshot

```
delete-snapshots action=delete report_id=<id> snapshot_id=<id>
```

Irreversible — the saved state is gone. Keep at least one recent snapshot before cleanup if the report is under active editing.

## What MCP can't do here

- Compare two snapshots (diff view) — UI only.
- Name a snapshot — UI only.

## Common pitfalls

- **Restore after source changes** — widgets can break if referenced sources/fields no longer exist. Re-run `list-widgets action=show` after restore and fix any broken sources via `manage-reports action=change_sources`.
- **Snapshots for compliance archival** — unreliable (data re-queries at view time). Use `manage-sharing action=download_pdf` or `action=export_excel` for compliance artifacts.
- **Accidental destructive restore** — always confirm with the user before `manage-snapshots action=restore`. There is no undo.
- **Creating a snapshot while widgets are broken** — snapshot captures the broken state. Fix widgets first, then snapshot.
