---
name: whatagraph-deleting
type: meta
description: Safe deletion, removal, and revocation across all Whatagraph entities — what each delete tool actually does, what cascades, what is recoverable, and when NOT to delete. Use when the user asks to delete, remove, disconnect, revoke, clean up, or undo anything, or before calling any delete-* / remove-* tool.
required_tools:
  - list-blends
  - list-custom-dimensions
  - list-custom-metrics
  - list-reports
  - list-source-groups
  - list-sources
  - list-templates
  - view-goals
  - view-sharing
  - delete-automations
  - delete-blends
  - delete-custom-dimensions
  - delete-custom-metrics
  - delete-destinations
  - delete-filters
  - delete-goals
  - delete-overviews
  - delete-report-tabs
  - delete-reports
  - delete-sharing
  - delete-snapshots
  - delete-source-groups
  - delete-sources
  - delete-spaces
  - delete-templates
  - delete-themes
  - delete-widgets
  - remove-integrations
  - remove-members
---

# Deleting things safely

Tools covered: every `delete-*` tool, `remove-integrations`, `remove-members`, plus the destructive modes hiding inside `manage-*` tools.

**Deletion is the highest-risk operation on this MCP surface.** Four rules before any call:

1. **Confirm intent with the user.** There is no `confirm` parameter in any delete tool's schema. The agent should confirm with the user conversationally before calling any destructive tool.
2. **Check usage first** (table below) — know what breaks before it breaks.
3. **Know the recovery class** — some deletes have a `restore` action, some need support, some are gone forever.
4. **Prefer update over delete-and-recreate** wherever dependents bind by id (source groups, blends, goals).

## Use this when

- "Delete this report / widget / tab / blend / space / goal / theme…"
- "Disconnect this account", "remove these sources", "revoke the share link"
- "Clean up the test artifacts", "remove the old client folder"
- "Undo that delete", "restore the widget I just removed"

## Recovery classes (verified Jun 2026)

| Class | Tools | Recovery |
|---|---|---|
| Soft-delete with MCP `restore` action | `delete-widgets`, `delete-report-tabs` | same tool, `action=restore` |
| Soft-delete, support-restorable only | `delete-reports`, `delete-spaces` (cascades to its reports + measurements) | contact support, within the retention window |
| Soft, graceful | `delete-filters` (widgets keep rendering, unfiltered) | recreate the filter |
| **Permanent** | `delete-custom-metrics`, `delete-custom-dimensions` (and all their related mappings, tags, and fields), `delete-source-groups`, `delete-snapshots` | none |
| Team-level detach (rows survive globally) | `delete-sources` (detaches from this team only; other teams unaffected) | reconnect the source |
| Immediate revoke | `delete-sharing` (old link → 404) | create a new share |
| Everything else (blends, goals, overviews, automations, themes, templates, transfers) | per-entity reference below | no restore path via MCP — treat as permanent and pre-check usage |

## Check usage first

| Before deleting… | Run |
|---|---|
| sources (`delete-sources`, `remove-integrations`) | `list-sources action=list_usage source_ids=[...]` |
| custom dimensions / metrics | `list-custom-dimensions action=usage` / `list-custom-metrics action=usage` |
| a blend | `list-blends action=show blend_id=<id>` → check `widgets_count` |
| a source group | `list-source-groups action=show group_id=<id>` |
| a template | `list-templates action=linked_reports template_id=<id>` |
| a theme / palette | switch affected reports to a replacement first (`manage-themes action=enable_theme` / `enable_color`) |

## Per-entity reference

### Report contents

**Widgets** — single, batch, and restore:

```
delete-widgets action=delete       report_id=<id> widget_id=<id>
delete-widgets action=batch_delete report_id=<id> widget_ids=[<id>, <id>]
delete-widgets action=restore      report_id=<id> widget_id=<id>   # undo a soft-delete
```

Soft-delete with a restore window. `delete` on an already-deleted widget is idempotent — it returns `already_deleted: true` rather than an error. Confirm before deleting widgets with unique configs (formulas, custom filters) that aren't easily recreated.

**Report tabs** — cascade and restore:

```
delete-report-tabs action=delete  report_id=<id> tab_id=<id>
delete-report-tabs action=restore report_id=<id> tab_id=<id>
```

Deleting a tab soft-deletes its widgets with it; `restore` brings them back. A report must keep **at least one tab** — deleting the last remaining tab is rejected; add or duplicate a replacement first.

**Snapshots** — the only pure hard-delete on report contents:

```
delete-snapshots action=delete report_id=<id> snapshot_id=<id>
```

Irreversible — the saved structure is gone. Keep at least one recent snapshot if the report is under active editing.

### Reports & spaces

**Reports:**

```
delete-reports action=delete report_id=<id>
```

Soft-delete — the report disappears from the space; support can restore it within a retention window, MCP cannot. Check `list-templates action=linked_reports` first if the report might be linked to a template.

**Spaces:**

```
delete-spaces action=delete client_id=<id>
```

The parameter is `client_id`, not `space_id`. Reports and measurements inside the space are soft-deleted with it (support-restorable). The Home space cannot be deleted. Deleting a client folder is visible to the whole team — always confirm.

### Data sources & accounts

**Team-level source detach:**

```
delete-sources action=delete source_ids=[<id>, <id>]
```

Batch-only (always an array). This detaches the sources from **your team** — the underlying source rows survive globally and other teams are unaffected; reconnecting restores access. All-or-nothing validation: every ID must belong to the team or the whole call fails, listing the missing IDs. Run `list-sources action=list_usage` first — widgets, blends, source groups, and measurements referencing the source break.

**Account-level removal:**

```
remove-integrations action=remove_sources account_id=<id> source_ids=[<id>, <id>]
remove-integrations action=delete_account account_id=<id>
```

- `remove_sources` — disconnect specific sources from an authenticated account; the account and its other sources stay.
- `delete_account` — removes the account **and every source on it**. OAuth re-connection (UI flow) is required to re-add.

### Virtual sources (blends, source groups)

**Blends:**

```
delete-blends action=delete blend_id=<id>
```

The tool has **no usage guard** — it will happily delete a blend that widgets depend on, and those widgets break. Check `list-blends action=show blend_id=<id>` → `widgets_count` yourself first.

**Source groups:**

```
delete-source-groups action=delete group_id=<id>
```

Permanent — cannot be undone. The group's virtual integration source is removed; widgets and custom metrics pointing at it break. Run `list-source-groups action=show group_id=<id>` first. See also "When NOT to delete" — most "delete the group" requests are really update requests.

### Custom fields

```
delete-custom-metrics    action=delete metric_ids=[<id>, <id>]
delete-custom-dimensions action=delete dimension_ids=[<id>, <id>]
```

Batch-only arrays. **Permanent** — custom dimensions go with all their related mappings, tags, and fields; custom metrics likewise. All-or-nothing ID validation (one unknown ID fails the whole call). A field still used by widgets or filters is **blocked**: the call returns a conflict listing the affected widgets, reports, and filters. Remove those references first (`manage-widgets` / `manage-filters`), or pass `force=true` to delete anyway and accept the breakage — `force` is available on **both** `delete-custom-metrics` and `delete-custom-dimensions`. Pre-check with `list-custom-metrics action=usage` / `list-custom-dimensions action=usage`.

### Config objects

**Filters:**

```
delete-filters action=delete filter_id=<id>
```

The schema **requires `action=delete`** alongside `filter_id` (verified Jun 2026). Soft delete — widgets referencing the filter lose the filtering but keep rendering.

**Goals** — batch-only; IDs come from `view-goals` (there is no `list-goals`):

```
delete-goals action=delete goal_ids=[<id>, <id>]   # one goal? still a one-element array
```

The schema has no singular `goal_id` (verified Jun 2026). Goal widgets referencing a deleted goal show an empty state until re-attached.

**Overviews (Measurements)** — the parameter is `measurement_id`, not `overview_id`:

```
delete-overviews action=delete measurement_id=<id>
```

Delete + recreate is also the only "modify" path for overviews — there is no update action.

**Automations** — two-key scoping:

```
delete-automations action=delete report_id=<id> automation_id=<id>
```

Stops future deliveries immediately. Confirm first if recipients rely on the schedule.

**Themes & palettes** — two actions, one tool:

```
delete-themes action=delete_theme theme_id=<id>
delete-themes action=delete_color color_id=<id>
```

Only `action` is schema-required; the matching ID (`theme_id` / `color_id`) is enforced at runtime per action. Reports using the deleted theme/palette fall back to the team default — switch them to a replacement first.

**Templates** — the benign cascade:

```
delete-templates action=delete template_id=<id>
```

Linked reports **survive** — they stay in place and keep their content; they only lose future auto-updates from the template. Run `list-templates action=linked_reports template_id=<id>` first so you know whose standardization pipeline stops.

**Destination transfers:**

```
delete-destinations action=delete transfer_id=<id>
```

Stops the outbound data transfer (e.g. to BigQuery). The transfer config is removed; previously delivered rows in the destination are outside Whatagraph's control.

### Sharing

```
delete-sharing action=delete report_id=<id> share_id=<id>
```

Invalidates the public URL immediately — anyone with the old link gets a 404. `share_id` comes from `view-sharing action=show`. Full revocation lifecycle (when to revoke vs change the password) lives in `whatagraph-sharing`.

### Team

```
remove-members action=cancel_invite invite_id=<id>
```

The only action is `cancel_invite` — despite the tool name, it can NOT remove an accepted member (UI only). `invite_id` comes from `manage-members`.

## Deletes hiding in manage tools

These `manage-*` actions are destructive even though their tool names aren't:

- `manage-reports action=detach_source delete_widgets=true` — deletes the dependent widgets along with the source. The default mode (no flag) remaps widgets to another attached source of the same channel instead, and the response discloses `remapped_to` including `is_sample_data` — check it: a remap to sample data is rarely what the user wants.
- `manage-integrations action=sync_to_clients client_ids=[]` — an empty array wipes all of the source's space assignments.
- `manage-snapshots action=restore` — destructive overwrite of the report's current structure; take a fresh `manage-snapshots action=create` first.

## When NOT to delete

- **Source groups: update, never delete-and-recreate.** A rebuild mints a new virtual `source_id`, silently orphaning every widget, custom metric, and report binding that pointed at the old one. Use `manage-source-groups action=update`.
- **Goals: update on conflict.** One goal per (metric, source) pair — if a create returns a conflict, the right move is `manage-goals action=update goal_id=<id>` on the existing goal, not delete + recreate.
- **Sharing: change the password to invalidate sessions.** Delete the share only when the URL itself must die; a password change via `manage-sharing action=update` invalidates existing viewer sessions while keeping the link.
- **Widgets: delete-and-recreate IS sometimes correct.** When a metric `external_id` update no-ops on an existing config (a known limitation — see `whatagraph-widgets`), deleting and recreating the widget is the documented workaround.

## What MCP can't do here

- Remove an accepted team member — UI only (`remove-members` covers pending invites only).
- Restore deleted reports or spaces — support only, within the retention window.
- Restore custom metrics, custom dimensions, source groups, or snapshots — nothing can; they're permanent.
- Empty-trash / purge soft-deleted items — not exposed.

## Common pitfalls

- **Probing for a `confirm` parameter** — none exists in any delete tool's schema. Deletion is a conversational directive — confirm with the user before calling.
- **`overview_id` instead of `measurement_id`** — `delete-overviews` takes `measurement_id`.
- **`space_id` instead of `client_id`** — `delete-spaces` takes `client_id`; the Home space is rejected.
- **Assuming `delete-filters` takes only `filter_id`** — the schema requires `action=delete` too.
- **Looking for goal IDs in a `list-goals` tool** — goals are read via `view-goals`; shares via `view-sharing action=show`; invites via `manage-members`.
- **Treating `remove-members` as member removal** — it only cancels pending invites.
- **Treating `delete-sources` as global destruction** — it detaches from your team only; the source survives for other teams and can be reconnected.
- **One bad ID in a batch delete** — `delete-sources` and `delete-custom-metrics` validate all IDs before deleting anything; one unknown ID fails the entire call (the error lists the missing IDs). Nothing is partially deleted.
- **Passing `goal_id` to `delete-goals`** — the schema is batch-only; pass `goal_ids`, even for a single goal (one-element array).
- **Deleting the last tab or the Home space** — both are rejected by invariant; create a replacement tab first / Home is permanent.
- **Re-running a widget delete after a timeout** — safe: `delete-widgets action=delete` is idempotent and returns `already_deleted: true`.
