---
name: whatagraph-automations
description: Schedule automated report delivery by email — daily, weekly, monthly, etc. — with optional PDF attachment, comparison-period framing, and manual approval gates. Use when a user wants a recurring report sent to clients or a distribution list.
required_tools:
  - manage-automations
  - delete-automations
---

# Automations (scheduled report delivery)

Tools covered: `list-automations`, `manage-automations`, `delete-automations`.

An **automation** = one report + a schedule + a list of email recipients. Multiple automations per report are allowed (e.g. weekly to the ops team, monthly to executives).

## Use this when

- "Send this report every Monday morning to the client."
- "Monthly executive summary on the 1st."
- "Daily spend snapshot to the team."
- "Pause automation when data source has issues."
- "Require manual approval before each delivery."

## Listing

```
list-automations action=list report_id=<report_id>
list-automations action=show report_id=<report_id> automation_id=<id>
```

## Creating an automation

```
manage-automations action=create
   report_id=<report_id>
   frequency="weekly"
   delivery_day="monday"
   send_time="09:00"
   time_zone="Europe/London"
   receivers=["<client_email>","<team_email>"]
   compare_type="previous"                 # or "last_year" (nullable)
   include_report_pdf_in_email=true
   needs_approval=false
   stop_on_issues=true
```

### Frequency + delivery_day

| `frequency` | `delivery_day` |
|---|---|
| `daily` | not used |
| `weekly`, `bi_weekly`, `tri_weekly` | `"monday"` … `"sunday"` |
| `monthly`, `bi_monthly` | `"first_day_month"`, `"last_day_month"`, or a specific day like `"day_5"` |
| `quarterly`, `yearly` | same day syntax |

### Key parameter naming

- `time_zone` (with underscore) — IANA format, e.g. `"Europe/Vilnius"`.
- `receivers` — array of email strings.
- `compare_type` — values are `previous` or `last_year` (nullable). No "none" — omit the field.
- `include_report_pdf_in_email` — boolean for PDF attachment.
- `needs_approval` — boolean; when `true`, each cycle must be approved via `action=review`.
- `stop_on_issues` — boolean; pauses delivery when data source has sync issues.

## Approving a pending delivery

```
manage-automations action=review automation_id=<id> report_id=<report_id>
```

Use when `needs_approval=true` and there's a pending cycle awaiting review.

## Updating

```
manage-automations action=update automation_id=<id> report_id=<report_id>
   frequency="monthly" delivery_day="first_day_month"
   receivers=["..."]
```

Changeable fields: `frequency`, `delivery_day`, `send_time`, `time_zone`, `receivers`, `compare_type`, `include_report_pdf_in_email`, `needs_approval`, `stop_on_issues`, `options`.

## PDF settings

Pass via `options.pdf_settings={...}` for advanced PDF options. Check `list-automations action=show` for current options.

## Deleting an automation

```
delete-automations action=delete report_id=<id> automation_id=<id>
```

Stops future deliveries immediately. Confirm with the user first if recipients are relying on the schedule.

## What MCP can't do here

- Pause/resume (no dedicated action) — use `update` to change schedule or set `stop_on_issues=true` and resolve the source issue externally.
- Slack delivery — not exposed via MCP.
- SMS / webhook delivery — not supported.

## Common pitfalls

- **`timezone` vs `time_zone`** — MCP expects `time_zone` with underscore.
- **`recipients` vs `receivers`** — MCP expects `receivers`.
- **`previous_period` vs `previous`** — MCP expects `previous` (or `last_year`). Other strings are rejected.
- **`include_pdf` vs `include_report_pdf_in_email`** — MCP expects the long name.
- **`review_before_send` vs `needs_approval`** — MCP expects `needs_approval`.
- **Delivery day off by one** — `time_zone` drives which "yesterday" a daily report uses. Mismatch between source timezone and automation timezone can create off-by-one date issues.
- **Invalid recipient email** — verify delivery history if some recipients do not receive the automation.
- **`stop_on_issues=true` but source keeps failing** — the automation stays stopped until the source is fixed. Check `list-sources action=list status=issue` regularly.
- **Too many automations per report** — distinct purposes (weekly-ops, monthly-exec) are fine, but duplicates cause recipient confusion.
