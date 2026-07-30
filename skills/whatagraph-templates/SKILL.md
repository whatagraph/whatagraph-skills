---
name: whatagraph-templates
type: domain
description: Convert an existing report into a reusable template and apply templates to new reports. Use when a user wants to standardize a report layout across many clients, roll out a monthly report across 20 accounts, or let auto-syncing keep client reports in step with a master template.
required_tools:
  - list-templates
  - manage-reports
  - manage-templates
  - delete-templates
---

# Templates

Tools covered: `list-templates`, `manage-templates`, `delete-templates`, plus `manage-reports action=create_from_template`.

A **template** is a reusable report blueprint. Reports created `from_template` are **linked** — structural changes propagate into linked reports, but **only through the edit → publish cycle** (not by editing the original source report).

> **Templates are opt-in.** Apply a template only when the user or the agent's instructions explicitly call for one (or name one) — an open "create a report" request is a scratch build (see `whatagraph-reports`). When a template is called for, use the team's own (user-created) template; never auto-pick from Whatagraph's pre-made template gallery unless the instructions name a gallery template. And by default deliver an **unlinked** report — keep the link only when linking/auto-sync (scaling one layout across clients) is explicitly requested.

## Use this when

- Standardizing the same report across many clients.
- Monthly paid media report that should look the same for every account.
- Rolling out a new widget across all client reports at once.
- One-time "use this starting point and then freely edit" → use `manage-reports action=duplicate` or convert back to unlinked in UI.

## Listing

```
list-templates action=list                                    # all team templates
list-templates action=list search="Paid Media"                # filter by name
list-templates action=show template_id=<id>                   # tabs + widget counts
list-templates action=linked_reports template_id=<id>         # reports using it
```

Pagination: cursor-based with `cursor` parameter; `per_page` up to 500 (default 100).

## Creating a template from an existing report

```
manage-templates action=create
   report_id=<source_report_id>
```

Converts the report's structure (tabs, widgets, layout, theme) into a template. The original report is not affected.

## Updating

```
manage-templates action=update template_id=<id>
   name="Monthly Paid Media v3"
```

Name must be at least 4 characters.

## Editing a template (edit → modify → publish)

Structural changes to a template only reach linked reports through this cycle. Editing the original source report does NOT propagate.

**Step 1 — Open a draft:**

```
manage-templates action=edit template_id=<id>
```

Returns a `draft_report.id` — a temporary report you can modify with `manage-report-tabs` and `manage-widgets`. Optionally pass `client_id=<space_id>` to host the draft in a specific space (defaults to Home).

**Step 2 — Modify the draft** using standard report-editing tools (add/remove widgets, reorder tabs, etc.) on the draft report ID.

**Step 3 — Publish:**

```
manage-templates action=publish template_id=<id>
```

Pushes the draft back into the template AND propagates changes to all linked reports. The draft is consumed on publish.

`report_id` is optional — if omitted, the most recent draft for the template is used automatically. You can still pass it explicitly if needed:

```
manage-templates action=publish template_id=<id> report_id=<draft_report_id>
```

## Applying a template to a new report

```
manage-reports action=create_from_template
   client_id=<space_id>
   template_id=<template_id>
```

The resulting report is always **linked** — future template edits propagate. There is no unlink flag, so pick the delivery mode explicitly:

- **Default — one-off report (unlinked delivery).** Unless the request/instructions explicitly ask for a linked, auto-syncing report, convert to an independent copy: `create_from_template` → `manage-reports action=duplicate` on the new report (the duplicate is not linked) → delete the linked intermediate (scaffolding you just created — no confirmation needed) → rename the duplicate and continue on it. The full step-by-step lives in `whatagraph-reports` → "Create from a template".
- **Explicit scaling — keep the link.** When the ask is to keep many client reports in step with one master template, keep the report as created.

After creation, remap sources on the report you're handing over so widgets stop showing sample data:

```
manage-reports action=change_sources report_id=<new_report_id>
   source_mapping={"<old_src>": <new_src>, "0": <new_src>}
```

## Discovering linked reports before editing a template

```
list-templates action=linked_reports template_id=<id>
```

Returns the list of reports that will auto-update when the template changes. Review before making destructive template edits.

## Deleting a template

```
delete-templates action=delete template_id=<id>
```

Linked reports survive but lose future auto-updates. Pre-check `list-templates action=linked_reports template_id=<id>` to see what stops syncing.

## What MCP can't do here

- Unlink a linked report — UI only (and irreversible).
- Create an unlinked report from a template in one call — instead, duplicate the linked report and delete the linked intermediate (this is the default delivery flow above).

## Common pitfalls

- **Applying a template nobody asked for** — an open report request is a scratch build. Don't browse team templates or the pre-made gallery for a "good enough" starting point; templates enter the flow only when explicitly requested or named in instructions.
- **Delivering a linked report by default** — `create_from_template` always links, but most one-off asks want an independent report. Run the duplicate → delete-intermediate flow unless auto-sync was explicitly requested.
- **Editing the source report doesn't propagate** — only the edit → publish cycle pushes changes to linked reports. Editing the original report that was converted into a template has no effect on links.
- **Template publish propagates to all linked reports** — deleting a widget on the draft and publishing removes it from every linked client report. Use `linked_reports` first.
- **Source mapping gaps after create_from_template** — widgets start on the template's default sources (often sample). Always follow up with `change_sources`.
- **Template name < 4 characters** — rejected.
- **Template references custom metrics or dimensions that don't exist in the target team** — won't resolve in the new report. Create the custom metrics/dimensions first, then apply.
- **Two templates with identical structure but different names** — client reports linked to the wrong template can show the wrong layout after your next edit. Keep a clear naming convention.
- **Confusing template vs theme** — templates store structure (tabs/widgets); themes store visual branding (colors/fonts). See `whatagraph-themes`.
