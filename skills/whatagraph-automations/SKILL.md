---
name: whatagraph-automations
type: domain
group: distribution_lifecycle
description: Schedule automated report delivery by email — daily, weekly, monthly, etc. — with optional PDF attachment, comparison-period framing, and manual approval gates. Also covers unautomating a report. Use when a user wants a recurring report sent to clients or a distribution list, or wants to stop one.
required_tools:
  - list-automations
  - list-sources
  - manage-automations
optional_tools:
  - tool_name: delete-automations
    purpose: Unautomate a report — the only way to make an automated report manual again.
  - tool_name: manage-reports
    purpose: Set the report's date range while it is unautomated, before scheduling it again.
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
list-automations action=list_all                    # account-wide, cursor-paginated
list-automations action=list_all search="report name" frequency="monthly"
```

Both `list` and `list_all` return a standard `page` envelope (`cursor`, `has_more`, `estimated_total`). `list_all` returns a slim payload per automation (`id`, `report_id`, `report_name`, `frequency`, `send_time`, `delivery_day`, `time_zone`). Use `show` for full details.

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

`delivery_day` is a **named key**, not a number. The valid keys depend on `frequency` — numeric forms like `"day_5"` and a "last day of month" key do **not** exist, and an unrecognized value is rejected.

| `frequency` | `delivery_day` |
|---|---|
| `daily` | `"daily"` |
| `weekly`, `bi_weekly`, `tri_weekly` | a weekday name `"monday"` … `"sunday"` |
| `monthly`, `bi_monthly` | an ordinal day `"first_day_month"`, `"second_day_month"` … `"tenth_day_month"`, or `"fifteenth_day_month"`; or a weekday-of-month `"first_monday_month"`/`"second_monday_month"`/`"third_monday_month"`, `"first_tuesday_month"` … `"first_sunday_month"` |
| `quarterly` | `"first_day_quarter"` … `"tenth_day_quarter"` |
| `yearly` | `"first_day_year"` … `"tenth_day_year"` |

To deliver on the 2nd of every month, use `delivery_day="second_day_month"` — not `"day_2"`. There is no key for the 11th–14th, 16th–31st, or the last day of the month; pick the nearest supported ordinal.

### Frequency ↔ report period constraints

Not all frequencies work with all report date periods. The report's saved date range determines which frequencies are valid:

| Report period category | Allowed frequencies |
|---|---|
| Day-level / rolling (`yesterday`, `today`, `last7Days`, `thisWeek`, `thisMonth`, etc.) | All (`daily` through `yearly`) |
| Weekly (`lastWeek`, `last2Week`, `last3Week`) | All except `daily` |
| Monthly (`lastMonth`, `last3Month` … `last25Month`) | `monthly`, `bi_monthly`, `quarterly`, `yearly` |
| Quarterly (`lastQuarter`) | `quarterly`, `yearly` only |
| Yearly (`lastYear`) | `yearly` only |
| Custom date range | None — automation is blocked entirely |

An invalid combination returns a clear error listing valid frequencies. Reports with custom date ranges cannot be automated at all.

### MCP limitation: one automation per report

Via MCP, only **one automation per report** is allowed. Attempting to create a second returns a `conflict` error. To change delivery targets, update the existing automation rather than creating a new one.

> **Warning:** an automation emails real recipients on a schedule. When setting one up on a user's behalf, test with your own (or the user's own) address first, or set `needs_approval=true` so nothing goes out without review. Create and update responses echo the saved `receivers` (verified Jun 2026) — check them before calling it done.

### Key parameter naming

- `time_zone` (with underscore) — IANA format, e.g. `"Europe/Vilnius"`.
- `receivers` — array of email strings.
- `compare_type` — values are `previous` or `last_year` (nullable). No "none" — omit the field.
- `include_report_pdf_in_email` — boolean for PDF attachment.
- `needs_approval` — boolean; when `true`, each cycle must be approved via `action=review`.
- `stop_on_issues` — boolean; pauses delivery when data source has sync issues.
- `disable_date_range_change` — boolean; prevents report date range changes from affecting the automation.
- `notify_sent` — boolean; sends a notification when the automation delivers.

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

Changeable fields: `frequency`, `delivery_day`, `send_time`, `time_zone`, `receivers`, `compare_type`, `include_report_pdf_in_email`, `needs_approval`, `stop_on_issues`, `disable_date_range_change`, `notify_sent`, `options`.

## PDF settings

Pass via `options.pdf_settings={...}` for advanced PDF options. Check `list-automations action=show` for current options.

## Unautomating a report

"Unautomate", "make it manual again", "stop the schedule" and "delete the automation" are all the same operation. There is no separate unautomate action and no pause flag — removing the automation *is* how a report goes back to manual.

```
delete-automations action=delete report_id=<report_id> automation_id=<id>
```

The report's `type` flips from `automated` back to on-demand, and it starts using its own date range again. Deliveries stop immediately.

`manage-automations` cannot do this — it has only `create`, `update` and `review`. If a user asks to unautomate and `delete-automations` is not in your tool list, say so and tell them a team owner has to grant it; do not tell them it is impossible.

Destructive, so confirm first, especially if recipients rely on the schedule. The recipient list and any pending deliveries go with the automation and are not recoverable — recreating the schedule afterwards means re-entering the recipients. The report itself, its widgets and its own saved date range are untouched. Full cascade and recovery detail is in the `whatagraph-deleting` skill.

## Changing the date range of an automated report

An automated report does **not** read the date range saved on the report. Its widgets read the range the schedule generates for each delivery, derived from the report's saved range plus the frequency. So `manage-reports action=update` with a `date_range` is rejected on an automated report with a `conflict` error rather than silently doing nothing.

To change the range, unautomate first:

1. `delete-automations` — the report becomes manual.
2. `manage-reports action=update report_id=<id> date_range={...}`.
3. `manage-automations action=create` — schedules again from the new range, and re-enter the recipients.

`manage-automations action=update` is not a shortcut here. It regenerates the delivery range from the report's saved range, and that saved range is exactly what step 2 changes. On its own, updating the automation only shifts the delivery window.

Note that a report on a custom date range cannot be automated at all, so step 2 constrains what step 3 can do.

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
