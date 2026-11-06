---
name: whatagraph-sharing
type: domain
group: distribution_lifecycle
description: Create, update and revoke public share links for reports, overviews and documents (files an agent made, such as a web page, deck or PDF), with optional password protection. Use when a user wants to give a client a view-only link, lock the date range viewers see, turn AI chat on inside a shared view, or share a document from the chat. For a PDF or a spreadsheet, load `whatagraph-export` instead — getting a file out of a report is not sharing.
required_tools:
  - view-sharing
  - manage-sharing
optional_tools:
  - tool_name: delete-sharing
    purpose: Revoke a public share link.
---

# Sharing

Tools covered: `view-sharing`, `manage-sharing`, `delete-sharing`.

A **share** is a public, view-only URL for a report, an overview or a document. Anyone with the link (and optional password) can view; no login required. Each report, overview and document has at most one link.

Every sharing tool takes exactly one target:

| Target | Parameter | Find the id with |
|---|---|---|
| Report | `report_id` (integer) | `list-reports` |
| Overview | `overview_id` (integer) | `list-overviews` |
| Document | `document_id` (ULID) | the id `create_document` returned, or `list-assets` |

> **PDF and Excel are not here.** They live in `whatagraph-export`, on the read-only `export-report` tool. Exporting a report no longer touches its share status, so never create a share link as a step towards producing a file — load `whatagraph-export` and call `export-report` directly.

> **These tools are available to you — use them directly.** `view-sharing` and `manage-sharing` are part of the write toolset: if your connection can create or edit reports, it can create share links too. When asked for a share link, create it programmatically with `manage-sharing action=create` and return the `share_url` — do **not** fall back to telling the user to share manually in the app. This includes documents: do not tell the user to press the share button on a document's card, share it yourself.

> **Never describe a link you have not read.** Before saying a link exists, is still active or is unchanged, call `view-sharing action=show` for that target and quote its `share_url`. Editing a document keeps its link, but only `view-sharing` tells you whether there is one. If `manage-sharing` is genuinely absent from your available tools, the MCP connector needs to be re-added or refreshed to pick up the write tools (a freshly added connector can lag) — tell the user that specific step instead of only giving UI instructions.

## Use this when

- A client asks for a link to their report.
- Locking the date range so viewers can't change it.
- Enabling or disabling AI chat (IQ) inside the shared view.
- Giving a client a link to a document an agent wrote (a web page, deck, PDF or other file).

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

## Share an overview

The same calls with `overview_id` instead of `report_id`. An overview share supports `require_password`, `password` and `disable_date_changing`; it has no `options` and no date range. Its `share_url` looks like `.../shared/o/<ulid>`, and `share_id` (a ULID) is optional on `update`.

## Share a document

A document is a file an agent made in a conversation: a web page, deck, PDF, spreadsheet and so on. Uploaded files and notes cannot be shared. Inside a conversation you can share the documents that conversation can open.

```
manage-sharing action=create
   document_id=<document_ulid>
   require_password=false
   expires_at="2026-12-31T23:59:00+00:00"
   allow_download=true
```

- `require_password` / `password` — as for reports (12 characters or more).
- `expires_at` — optional ISO 8601 date-time in the future; the link stops working then. Omit for a link that never expires.
- `allow_download` — optional, defaults to `true`. When `false`, people with the link can view but not download the file.
- `disable_date_changing` and `options` do not apply to documents.

The response's `share_settings` holds `id`, `share_url` (`.../shared/d/<ulid>`, on the team's own domain when it has one), `require_password`, `expires_at`, `expired` and `allow_download`. `view-sharing action=show document_id=<ulid>` returns the same fields.

`update` works the same way as for reports: pass `document_id` and only the settings to change; the others keep their current value, and the password is kept unless you send a new one. The link itself does not change when the document is edited.

## Common pitfalls

- **Sharing a report just to export it** — unnecessary, and it publishes the report. `export-report` needs no share link; see `whatagraph-export`.
- **Password too short** — minimum 12 characters; shorter passwords are rejected.
- **Forgetting `require_password=true` when setting `password`** — password is ignored when `require_password` is `false`.
- **Sending the URL without the password in a separate channel** — password in URL/chat defeats protection.
- **Password reset required to invalidate** — there's no revoke-all-sessions button; change the password to invalidate cookies.
- **Iq_chat on reports without AI setup** — IQ requires the team's AI feature. If disabled at team level, the toggle has no effect.
- **Disable-date-changing and template-linked reports** — viewers with locked dates still see date changes when the template updates.

## Revoking a share link

```
delete-sharing action=delete report_id=<id> share_id=<id>
delete-sharing action=delete overview_id=<id>
delete-sharing action=delete document_id=<ulid>
```

`share_id` is required for a report and optional for an overview or a document, since those have at most one link. Deleting a document's link and sharing it again gives a **new** URL; the old one stays dead.

Invalidates the public URL immediately — anyone with the old link gets a 404. Use when a client relationship ends or a password leaked. Do this before regenerating a share so stale links don't linger. To invalidate viewer sessions while keeping the link, change the password via `update` instead — see `whatagraph-deleting` for the full destructive-action playbook. If `delete-sharing` isn't exposed on this server, load `whatagraph-deleting` to check what is available.

## What MCP can't do here

- Allowlist specific email addresses — not exposed via MCP; UI only.
