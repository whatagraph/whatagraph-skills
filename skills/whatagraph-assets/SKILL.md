---
name: whatagraph-assets
type: domain
description: Import, find, read and publish files in the team's asset library — brand images for report widgets and themes, and documents you can search and read. Use when a report needs a logo, a cover image or a background, when you must turn a remote image URL into one that is safe to put in a report, or when the answer lives in an uploaded document rather than in marketing data.
required_tools:
  - list-assets
  - search-assets
  - read-document
  - manage-assets
---

# Assets: files, images and documents

Tools covered: `list-assets`, `search-assets`, `read-document`, `manage-assets`.

The asset library holds files that belong to the team. Two jobs use it:

- **Images for reports** — a logo, a cover photo, a section-divider background. An image must be *published* before a report can show it.
- **Documents you can read** — uploaded text that `search-assets` and `read-document` reach. Use these when the answer is in a file, not in marketing data.

Every asset hangs off one **owner node**: the team, a space (client), or a report. In an agent conversation it can also belong to the agent or the conversation. You see an asset if you can reach its owner node.

## Use this when

- A report needs a logo, cover image, or a comment-widget background.
- You have a remote image URL and need a URL that is safe to put in a report.
- You need to find or read a document the team uploaded.
- An image already in the library must be reused in a new report.

## The rule that matters most: never hand-assemble base64

Widgets accept `image_data` and `background_image_data` as base64. **Do not build that string yourself.** Any base64 beyond a few hundred bytes gets mis-transcribed, and the write fails with `Invalid base64 in image_data` — or worse, succeeds with a corrupt image. Import the file instead and pass a URL.

Use `image_data` only for bytes you already hold exactly, never for bytes you are reproducing.

## Putting an image into a report

Three steps, in order. Skipping any of them puts a hotlink to somebody else's server into a customer's report.

```
manage-assets action=import_url
   url="https://example.com/logo.png"
   target_scope=team                          # keeps it reusable across reports

   → {"asset": {"ulid": "<asset_ulid>", "title": "logo.png", "kind": "attachment", ...}}

manage-assets action=publish asset_id=<asset_ulid>

   → {"url": "<public_url>", "asset": {...}}

manage-widgets action=update report_id=<report_id> widget_id=<widget_id>
   rows=[{"options": {"image_url": "<public_url>"}}]
```

Pass **only** the `url` that `publish` returns. Never the original remote URL.

A Whatagraph URL that is already published needs no import. If import or publish fails, leave the widget or theme unchanged, and tell the user — never fall back to the raw URL and never substitute a different image.

The same three steps apply to a comment widget's `background_image_url` and to a theme's header/footer `images[].url`.

### What `publish` does

It copies the image bytes to public storage and returns a stable public `url`. The point is that a shared report must render for a logged-out viewer, so the image has to be publicly fetchable.

**That is a real visibility change.** `publish` makes the image publicly fetchable by anyone with the URL — it is the same exposure model as any report image, but it applies to *any* image you can reach, not only curated brand logos. Publish brand assets and images meant for the client. Do not publish something a viewer of that report should not see.

### `import_url` limits

- **`https://` only.** No `http://`, no other scheme.
- **Port 443 only**, and no credentials embedded in the URL.
- **25 MB ceiling.**
- Private and internal addresses are refused.

## Check resolution before publishing

The rendered report page is **1440 CSS px** wide. So a full-width (6-column) image renders at roughly 1400 px, and more on a high-DPI screen.

**Source images at 2x the rendered width or better** — roughly 2500 px and up for a full-width band. An 800 px image stretched across a full-width header is visibly soft, and it is one of the most obvious defects in a finished report.

Nothing returns an image's dimensions — `list-assets` gives you `byte_size`, not width and height. Check the image itself before you import it.

## Finding an asset

```
list-assets                                     # everything you can reach
list-assets scope=team                          # team-owned only
list-assets kind=attachment
list-assets tag="brand"
list-assets filter_space_ids=[<space_id>]       # owned exactly at that space
list-assets filter_report_ids=[<report_id>]     # owned exactly at that report
list-assets fields="ulid,title,mime_type"       # trim the response
```

`filter_space_ids` and `filter_report_ids` match assets owned **exactly** at those nodes. They do not include the team-level assets that a report can also reach.

**Field names** — get these right, because `fields` rejects anything else:

| Field | Notes |
|---|---|
| `ulid` | The asset id. This is what every other action takes. |
| `title` | Usually the original filename. |
| `kind` | `attachment`, `document`, or `note`. |
| `owner_model_type` / `owner_model_id` | Which node owns it. |
| `mime_type` | |
| `byte_size` | The size. **Not** `size`. |
| `parse_status` | `pending`, `processing`, `done`, `failed`, `skipped`. |
| `embedding_status` | Whether semantic search can reach it yet. |
| `summary` | A short generated summary. Never the full text. |
| `tags` | |

There is no `type` field and no `size` field — they are `kind` and `byte_size`. Pagination is cursor-based: `per_page` up to 500 (default 100), then pass `page.cursor` as `cursor`.

## Reading documents

`list-assets` returns a manifest and a short summary, never the full text.

```
search-assets query="Q3 media plan"             # keyword + semantic, max 50 results
search-assets query="budget" scope=team kind=document

read-document ulid=<asset_ulid>                 # the extracted text
read-document ulid=<asset_ulid> offset=20000 limit=20000   # page a long file
```

`search-assets` combines keyword matching with semantic matching, so it finds paraphrases the keywords miss. `read-document` defaults to 20000 characters and caps at 50000 — page with `offset` for anything longer.

**Never guess a file's contents from its title or summary. Read it.** Image and PDF attachments return a short pointer instead of text, because there is nothing extracted to read.

## Organising the library

```
manage-assets action=tag asset_id=<asset_ulid> tags=["brand", "logo"]
manage-assets action=promote asset_id=<asset_ulid> target_scope=team
manage-assets action=set_visibility asset_id=<asset_ulid> visibility=private
```

- **`tag`** adds tags. Tags are how you find an asset again with `list-assets tag=...`.
- **`promote`** moves an asset to a different owner node. Move a report-scoped image to `team` when a second report needs it — that is better than importing it twice.
- **`set_visibility`** takes `private` or `public`.

`import_url` and `promote` both need an explicit `target_scope`. There is no silent default:

| `target_scope` | Also required |
|---|---|
| `team` | — |
| `client` | `target_space_id` |
| `report` | `target_report_id` |
| `agent` / `conversation` | Only valid inside an agent conversation |

**Default to `target_scope=team`** for anything a report will display. A report-scoped image cannot be reused, and duplicating it later is worse than scoping it correctly now.

## Common pitfalls

- **Hand-writing base64 into `image_data`** — it corrupts. Import and publish instead. This is the single most common way an image write fails.
- **Passing a remote URL straight to a widget** — nothing validates that the URL still works. It can rot, sit behind a login, or block hotlinking, and the break shows up in the customer's report, not yours.
- **Forgetting `publish`** — an imported but unpublished asset is not publicly fetchable, so the image is blank for anyone viewing the shared report.
- **`fields="...,type,size"`** — rejected. The names are `kind` and `byte_size`.
- **Importing to `report` scope by habit** — the asset is then stuck on that report. Use `team` unless it genuinely belongs to one report.
- **Publishing something private** — `publish` makes the image fetchable by anyone with the URL. Check what you are publishing.
- **A soft, pixelated header image** — the source was too small. Full-width needs roughly 2500 px; see "Check resolution before publishing".

## What MCP can't do here

- Upload raw bytes as a file — `import_url` fetches from a URL. To get a local file in, the user uploads it in the UI first.
- Resize, crop, or convert an image — import it at the resolution you need.
- Read image or PDF text — `read-document` returns a pointer for those, not extracted text.
- Delete an asset — not exposed here; see `whatagraph-deleting`.
