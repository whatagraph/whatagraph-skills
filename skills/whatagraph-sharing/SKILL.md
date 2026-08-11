---
name: whatagraph-sharing
type: domain
group: distribution_lifecycle
description: Create and update public share links for reports with optional password protection, generate PDFs, and export reports to Excel. Use when a user wants to give a client a view-only link, generate a PDF, or download report data as a spreadsheet.
required_tools:
  - view-sharing
  - manage-sharing
optional_tools:
  - tool_name: delete-sharing
    purpose: Revoke a public share link.
---

# Sharing, PDF, Excel

Tools covered: `view-sharing`, `manage-sharing`, `delete-sharing`.

A **share** is a public, view-only URL for a report. Anyone with the link (and optional password) can view; no login required.

> **These tools are available to you — use them directly.** `view-sharing` and `manage-sharing` are part of the write toolset: if your connection can create or edit reports, it can create share links too. When asked for a share link, create it programmatically with `manage-sharing action=create` and return the `share_url` — do **not** fall back to telling the user to share manually in the app. If `manage-sharing` is genuinely absent from your available tools, the MCP connector needs to be re-added or refreshed to pick up the write tools (a freshly added connector can lag) — tell the user that specific step instead of only giving UI instructions.

## Use this when

- A client asks for a link to their report.
- Generating a PDF of the current report state.
- Exporting report data as Excel for client deliverables.
- Locking the date range so viewers can't change it.
- Enabling or disabling AI chat (IQ) inside the shared view.

## View current share settings

```
view-sharing action=show report_id=<report_id>
```

Response fields: `is_shared` (boolean), and when shared: `share_settings.id`, `share_settings.hash`, `share_settings.share_url`, `share_settings.require_password`, `share_settings.disable_date_changing`, `share_settings.options` (e.g. `{"iq_chat": true}`), `share_settings.date_range`.

## Create a share link

```
manage-sharing action=create
   report_id=<report_id>
   require_password=true
   password="client-only-2025"
   disable_date_changing=false
   options={"iq_chat": true}
```

- `require_password` boolean — optional, defaults to `false`. When `true`, `password` is also required (minimum 12 characters).
- `disable_date_changing` boolean — optional, defaults to `false`. When `true`, viewers cannot change the report's date range.
- `options.iq_chat` — enable the in-share AI chat ("IQ") so the client can ask questions about their data.

**Idempotent:** if a share link already exists for the report, `create` returns an error pointing to `update` — it will not create a duplicate or silently overwrite the existing link.

The response includes a `share_url` field — that is the public viewer URL to hand to clients. It lives on the team's share domain (e.g. `https://reports.live/shared/<hash>`, or the team's custom domain on white-labeled accounts). For a specific tab, append `#tab:<tab_id>`.

The `live.whatagraph.com/client/<team_client_id>/live-report/<report_id>` URL is the signed-in editor view used by teammates inside the app — it is **not** the public share URL and external clients can't authenticate. Always copy `share_url` from the response when handing a link to an external viewer; never substitute the live URL.

## Update an existing share

```
manage-sharing action=update report_id=<report_id>
   require_password=true password="new-password"
   disable_date_changing=true
   options={"iq_chat": false}
```

`share_id` is optional — if omitted, the report's share link is resolved automatically from `report_id` (each report has at most one). You can still pass `share_id` explicitly if you already have it. Changing the password invalidates existing share sessions.

## Generate a PDF

```
manage-sharing action=download_pdf report_id=<report_id>
```

Starts PDF generation. Layout is fixed: A4 landscape, 1440px width. The response contains the downloadable PDF URL or a job identifier; polling may be required for large reports.

**Warning**: `download_pdf` auto-creates a public share link if one does not already exist (required for PDF rendering). This is a side effect — the report becomes publicly accessible even if you only wanted a PDF.

## Export to Excel

```
manage-sharing action=export_excel report_id=<report_id>
```

Returns an Excel file with the report's widget data. Layout: one sheet per report tab.

## Common pitfalls

- **Password too short** — minimum 12 characters; shorter passwords are rejected.
- **Forgetting `require_password=true` when setting `password`** — password is ignored when `require_password` is `false`.
- **Sending the URL without the password in a separate channel** — password in URL/chat defeats protection.
- **Password reset required to invalidate** — there's no revoke-all-sessions button; change the password to invalidate cookies.
- **PDF with Meta/Google creative images** — platform creative URLs rotate; long-lived PDFs may have broken thumbnails.
- **Iq_chat on reports without AI setup** — IQ requires the team's AI feature. If disabled at team level, the toggle has no effect.
- **Excel export for non-tabular widgets** — comment, image, and filter-control widgets produce no rows.
- **Disable-date-changing and template-linked reports** — viewers with locked dates still see date changes when the template updates.

## Revoking a share link

```
delete-sharing action=delete report_id=<id> share_id=<id>
```

Invalidates the public URL immediately — anyone with the old link gets a 404. Use when a client relationship ends or a password leaked. Do this before regenerating a share so stale links don't linger. To invalidate viewer sessions while keeping the link, change the password via `update` instead — see `whatagraph-deleting` for the full destructive-action playbook. If `delete-sharing` isn't exposed on this server, load `whatagraph-deleting` to check what is available.

## What MCP can't do here

- Allowlist specific email addresses — not exposed via MCP; UI only.
