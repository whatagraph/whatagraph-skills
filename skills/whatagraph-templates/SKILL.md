---
name: whatagraph-templates
description: Convert an existing report into a reusable template and apply templates to new reports. Use when a user wants to standardize a report layout across many clients, roll out a monthly report across 20 accounts, or let auto-syncing keep client reports in step with a master template.
---

# Templates

Tools covered: `list-templates`, `manage-templates`, `delete-templates`, plus `manage-reports action=create_from_template`.

A **template** is a reusable report blueprint. Reports created `from_template` are **linked** — structural changes to the template automatically propagate into the linked reports.

## Use this when

- Standardizing the same report across many clients.
- Monthly paid media report that should look the same for every account.
- Rolling out a new widget across all client reports at once.
- One-time "use this starting point and then freely edit" → use `manage-reports action=duplicate` or convert back to unlinked in UI.

## Listing

```
list-templates action=list                                    # all team templates
list-templates action=show template_id=<id>                   # tabs + widget counts
list-templates action=linked_reports template_id=<id>         # reports using it
```

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

## Applying a template to a new report

```
manage-reports action=create_from_template
   client_id=<space_id>
   template_id=<template_id>
```

The resulting report is **linked** — future template edits propagate.

After creation, remap sources so widgets stop showing sample data:

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

Reports linked to the template stay in place but lose future auto-updates. Run `list-templates action=linked_reports template_id=<id>` first — deleting a widely-used template stops an agency's standardization pipeline.

## What MCP can't do here

- Unlink a linked report — UI only (and irreversible).
- Create an unlinked report from a template — duplicate a linked report if you want a one-off clone.

## Common pitfalls

- **Template edit propagates to all linked reports** — deleting a widget on the template removes it from every linked client report. Use `linked_reports` first.
- **Source mapping gaps after create_from_template** — widgets start on the template's default sources (often sample). Always follow up with `change_sources`.
- **Template name < 4 characters** — rejected.
- **Template references custom metrics or dimensions that don't exist in the target team** — won't resolve in the new report. Create the custom metrics/dimensions first, then apply.
- **Two templates with identical structure but different names** — client reports linked to the wrong template can show the wrong layout after your next edit. Keep a clear naming convention.
- **Confusing template vs theme** — templates store structure (tabs/widgets); themes store visual branding (colors/fonts). See `whatagraph-themes`.
