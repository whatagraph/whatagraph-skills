---
name: whatagraph-sharing
type: domain
group: distribution_lifecycle
description: Create and update public share links for reports with optional password protection, generate and download PDFs, and export reports to Excel. Use when a user wants to give a client a view-only link, generate a PDF and get the rendered file, or download report data as a spreadsheet.
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
- Generating a PDF of the current report state, and getting the rendered file.
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

**Report shortcut cascade:** if the report contains Report shortcut widgets (`widget_type_id=141`, drill-down links to other reports), sharing it automatically shares every linked report too — recursively, so nested shortcuts keep working in the public view. Auto-created child shares inherit the parent's password and date-lock settings; linked reports that already have their own share keep their existing settings untouched.

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

Starts PDF generation in the background. **The response does not contain the PDF** — rendering takes time. The response contains a `pdf_job_id`. Give that id to `get_pdf` to get the file.

**What gets produced:** each visible report tab renders as **exactly one page**. A tab is never split across two pages, and two tabs never share one page. Hidden tabs are not rendered. Page width is fixed at 1440 CSS px. **Page height changes from tab to tab**, because each page is as tall as that tab's rendered content. Thus pages in one document can have different sizes. The orientation is landscape. You cannot change any of this from MCP.

**Warning**: `download_pdf` auto-creates a public share link if one does not already exist (required for PDF rendering). This is a side effect — the report becomes publicly accessible even if you only wanted a PDF.

## Get the generated PDF

```
manage-sharing action=get_pdf
   report_id=<report_id>
   pdf_job_id=<pdf_job_id>
```

Gets a PDF that `download_pdf` started. The `status` field tells you what to do next:

- `pending` — the render is still running. Wait a few seconds, then call again.
- `ready` — the file is available. The response contains `download_url`, `expires_in_seconds`, `file_name` and `file_size_bytes`.
- `expired` — the job id is unknown, or the file is too old to get. Run `download_pdf` again for a new one.

A small report is usually ready in a few seconds. A report with many tabs takes longer. Wait between calls — do not poll in a tight loop.

**The `download_url` expires one hour after you get it.** Use it immediately. If it expires, call `get_pdf` again with the same `pdf_job_id` for a new URL.

**To verify a PDF that you generated:** a multi-page PDF can mix page sizes, and most tools show only the first page's dimensions. Examine every page. Also check the last row of every table (see `whatagraph-widgets` → "Tables truncate silently").

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
- **Reading the `download_pdf` response as the finished PDF** — it only starts the render. The file comes from `get_pdf`.
- **Calling `get_pdf` once and giving up** — a first call almost always returns `pending`. Wait, then call again.
- **Keeping a `download_url` for later** — it expires in one hour. Call `get_pdf` again for a fresh one.
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
