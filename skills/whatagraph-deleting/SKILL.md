---
name: whatagraph-deleting
type: meta
group: deletion
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
optional_tools:
  - tool_name: manage-reports
    purpose: Detach a source / remove a widget reference before deleting it.
  - tool_name: manage-sharing
    purpose: Revoke sharing before deleting a report.
  - tool_name: manage-snapshots
    purpose: Manage snapshot references during cleanup.
  - tool_name: manage-source-groups
    purpose: Detach sub-sources before deleting a source group.
  - tool_name: manage-themes
    purpose: Reassign a theme before deleting one in use.
  - tool_name: manage-goals
    purpose: Remove goal references before deleting a metric.
  - tool_name: manage-integrations
    purpose: Detach integration sources during cleanup.
---

# Deleting things safely

Tools covered: every `delete-*` tool, `remove-integrations`, `remove-members`, plus the destructive modes hiding inside `manage-*` tools.

**Deletion is the highest-risk operation on this MCP surface.** Four rules before any call:

1. **Confirm intent with the user, then confirm the call with its token.** These are two separate things. The server refuses a destructive call and returns a preview with a single-use `confirm_token`; you resend the identical call with that token to execute it (see "The approval gate" below). That mechanism stops an accidental destruction, but it does not know what the user wants — so ask the user first, then confirm. One exception to *asking*: intermediate artifacts the agent itself created moments earlier as scaffolding within a documented flow (e.g. the linked intermediate report in the template → duplicate → delete flow, see `whatagraph-reports`) hold no user content and can be deleted without a confirmation round-trip. They still go through the token round-trip — the gate applies to every caller.
2. **Check usage first** (table below) — know what breaks before it breaks.
3. **Know the recovery class** — some deletes have a `restore` action, some need support, some are gone forever.
4. **Prefer update over delete-and-recreate** wherever dependents bind by id (source groups, blends, goals).

## The approval gate

Every `delete-*` / `remove-*` tool and the destructive `manage-*` actions listed below run behind a two-step gate. The first call **changes nothing** and comes back like this:

```json
{
  "success": false,
  "requires_approval": true,
  "tool": "delete-source-groups",
  "action": "delete",
  "warning": "This permanently deletes data that other objects read through, so it can break them too. It cannot be undone.",
  "blast_radius": "wide",
  "cascades_to": ["widgets", "blends", "reports", "transfers"],
  "arguments": { "action": "delete", "group_id": 1516 },
  "confirm_token": "UG4SPL8FWxyT90mvHcrmQ8zqYMwMMY9BG54xbC5j",
  "expires_in_seconds": 300
}
```

Read it, tell the user what it says, and only then resend the **identical** call with `confirm_token` set to that value.

Four things to know:

- **`requires_approval: true` is not an error.** Do not retry it as if the call failed, and do not report it to the user as a failure. It is the preview you asked for by making the call.
- **You cannot invent a token.** A token you were never handed is refused, and the refusal hands you a *fresh* token each time — so retrying a refused call never gets through. There is nothing to guess.
- **A token is single-use and expires in 300 seconds.** It runs its destruction once. Replaying it gives you another preview.
- **The token is bound to the exact arguments.** Change any of them and it stops working — you get a new preview for the new call, which is the point. `intent`, `idempotency_key`, and `agent_tool_status` are excluded, so rewording those on the confirming call is fine.

`blast_radius` tells you how far the damage reaches: `local` means only the thing you named, `wide` means other objects read through it and break too. `cascades_to` names the kinds that break.

**Never confirm a destruction the user did not ask for.** If the preview surprises you, report it back to the user instead of spending the token.

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

Permanent — cannot be undone (re-verified against the tool). It removes the group, **its configs, its member source entries, and the virtual integration source** in one go; widgets and custom metrics pointing at that virtual source break. Note the member sources are only detached from the group — the underlying connected sources themselves survive, so a deleted group is rebuildable from them, just not restorable. Run `list-source-groups action=show group_id=<id>` first. See also "When NOT to delete" — most "delete the group" requests are really update requests.

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

**Overviews (Measurements):**

```
delete-overviews action=delete overview_id=<id>
```

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

These `manage-*` actions are destructive even though their tool names aren't. All of the ones marked **gated** go through the same preview-and-token round-trip as a `delete-*` call.

| Action | Reach | Why it destroys | Gated |
|---|---|---|---|
| `manage-source-groups` `update`, `update_config` | wide | Replaces the config collection — a config you leave out of `configs` is deleted. This is the call that caused the Aug 2026 incident. | yes |
| `manage-blends` `update` | wide | Replaces collections; sub-sources you do not re-send are dropped. | yes |
| `manage-custom-dimensions` `update`, `assign_tag_sources` | wide | Replaces fields / tag source assignments. | yes |
| `manage-custom-dimensions` `remove_tag` | wide | Permanently deletes the tag and its assignments. | yes |
| `manage-custom-metrics` `update` | wide | Replaces the field mappings. | yes |
| `manage-reports` `detach_source`, `change_sources` | wide | Detaches a source; with `delete_widgets=true` it deletes the dependent widgets too. | yes |
| `manage-reports` `move` | wide | Moves the report between spaces; report-local sources can drop. | yes |
| `manage-integrations` `sync_to_clients` | wide | An empty `client_ids` array wipes all of the source's space assignments. | yes |
| `manage-sources` `tag` | wide | Replaces the source's tag set. | yes |
| `manage-templates` `publish` | wide | Overwrites linked reports with the template's current structure. | yes |
| `manage-snapshots` `restore` | wide | Overwrites the report's current structure. Take a fresh `manage-snapshots action=create` first. | yes |
| `manage-widgets` `remove_row` | local | Deletes the row and its conditional formats. | yes |
| `manage-widgets` `update`, `set_conditional_formats`, `set_auto_colors` | local | Replaces the widget's own rows/formats. Routine, so it runs on the first call. | no |
| `manage-overviews` `update` | local | Replaces notifications and shares on that overview. | no |
| `manage-automations` `update` | local | Replaces the recipient list. | no |
| `manage-members` `update_member_role`, `update_invite` | local | Replaces the member's space access. | no |
| `manage-filters` `create` | local | Replaces a filter already on the target widget or source. | no |

The ungated ones still replace collections — they are just too routine to put an approval round-trip in front of. **Read the current state and send it back complete**, or the parts you omit are gone.

On `manage-reports action=detach_source`: the default mode (no `delete_widgets` flag) remaps widgets to another attached source of the same channel instead of deleting them, and the response discloses `remapped_to` including `is_sample_data` — check it, because a remap to sample data is rarely what the user wants.

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

- **Treating `requires_approval: true` as a failure** — it is the preview, and it is the normal first response to any gated call. Read it, tell the user, then resend the identical call with its `confirm_token`. Do not report it as an error and do not blind-retry it.
- **Guessing or reusing a `confirm_token`** — a token you were not handed is always refused, and a spent one is refused too. Take the token from the preview of that exact call.
- **Looking for a plain `confirm` boolean** — there isn't one. The proof of approval is the `confirm_token` from the preview.
- **All overview tools use `overview_id`** — list, show, update, and delete all use `overview_id` consistently.
- **`space_id` instead of `client_id`** — `delete-spaces` takes `client_id`; the Home space is rejected.
- **Assuming `delete-filters` takes only `filter_id`** — the schema requires `action=delete` too.
- **Looking for goal IDs in a `list-goals` tool** — goals are read via `view-goals`; shares via `view-sharing action=show`; invites via `manage-members`.
- **Treating `remove-members` as member removal** — it only cancels pending invites.
- **Treating `delete-sources` as global destruction** — it detaches from your team only; the source survives for other teams and can be reconnected.
- **One bad ID in a batch delete** — `delete-sources` and `delete-custom-metrics` validate all IDs before deleting anything; one unknown ID fails the entire call (the error lists the missing IDs). Nothing is partially deleted.
- **Passing `goal_id` to `delete-goals`** — the schema is batch-only; pass `goal_ids`, even for a single goal (one-element array).
- **Deleting the last tab or the Home space** — both are rejected by invariant; create a replacement tab first / Home is permanent.
- **Re-running a widget delete after a timeout** — safe: `delete-widgets action=delete` is idempotent and returns `already_deleted: true`.
