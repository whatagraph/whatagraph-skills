---
name: auditing-account-health
type: workflow
description: >-
  Review the overall health of a Whatagraph account including source connections,
  integration status, automation schedules, sharing configurations, goals,
  subscription details, and organizational structure. Use when the user asks
  for an account review, wants to check if everything is connected properly,
  asks "is my account set up correctly?", needs a health check, or wants to
  understand their subscription and usage.
required_tools:
  - view-team
  - list-integrations
  - list-sources
  - list-spaces
  - list-reports
  - list-automations
  - view-sharing
optional_tools:
  - tool_name: view-goals
    purpose: Goals & KPI tracking review (step 8).
  - tool_name: list-overviews
    purpose: Overview / KPI dashboard review (step 8).
  - tool_name: list-blends
    purpose: Blend review (step 9).
  - tool_name: list-source-groups
    purpose: Source-group review and sync-issue scan (step 9).
  - tool_name: list-custom-metrics
    purpose: Custom-fields usage review (step 10).
  - tool_name: list-custom-dimensions
    purpose: Custom-fields usage review (step 10).
---

# Auditing Account Health

Perform a comprehensive review of a Whatagraph account to identify connection issues, configuration gaps, underutilized features, and optimization opportunities.

## Full Account Health Check Workflow

### 1. Team & Subscription Overview

```
view-team action: show
view-team action: show_subscription
view-team action: members
```

`show` returns basic team info (id, name, status, plan, created_at). Subscription limits and usage are in a **separate action** — `show_subscription` — which returns `sources_total`, `sources_used`, `users_total`, `users_used`, `reports_count`. Use `members` to see the actual user roster (member_id, name, email, role).

Review:
- **Subscription plan** and limits (sources, reports, users) — from `show_subscription`
- **Team settings** and configuration — from `show`
- **Usage vs. limits** — compare `sources_used` vs `sources_total`, `users_used` vs `users_total`, `reports_count` vs `reports_total`
- **Null limits**: `sources_total: null`, `users_total: null`, or `reports_total: null` means "unlimited/unenforced" — do not flag as over-utilization

### 2. Integration Health

```
list-integrations action: list_grouped
```

Review:
- Which channels are connected
- How many accounts per channel
- Any expected channels that are missing

For each integration, check connected accounts:
```
list-integrations action: list_accounts, channel_id: <id>
```

### 3. Source Health Scan

Start with a quick aggregate check — no pagination needed:
```
list-sources action: health_summary
```
Returns `{ total, ok, error }` counts. If `error > 0`, drill into broken sources:

```
list-sources action: list, status: "issue", per_page: 128
```

Check for:
- **Broken sources** — filter directly with `list-sources action: list, status: "issue"` (valid `status` filter values are `all` / `active` / `issue` — there is no `error`). These need reconnection or troubleshooting
- **Orphan sources** — check `space_ids` in the list response; sources with `space_ids: []` are not assigned to any space
- **Source count** vs. subscription limits (from `show_subscription`)

For sources with errors:
```
list-sources action: show, source_id: <id>
```

To find **unused sources** (zero reports, blends, etc.), collect source IDs from `list` then check usage:
```
list-sources action: list_usage, source_ids: [id1, id2, ...]
```
This returns per-source usage counts (`reports_count`, `blends_count`, `transfers_count`, `source_groups_count`, `overviews_count`). Note: `list_usage` finds unused sources but does NOT detect orphans — orphan detection requires checking `space_ids` from the `list` action.

### 4. Space Organization

```
list-spaces action: list
```

Review:
- Are spaces organized logically (by client, project, or channel)?
- Are there empty spaces?
- Do spaces have appropriate source assignments?

For each space, check children:
```
list-spaces action: show, client_id: <id>
```

### 5. Report Coverage

```
list-reports action: list
```

Check:
- Number of reports vs. subscription limits
- Reports per space — are all spaces covered?
- Report naming conventions — are they consistent?

### 6. Automation & Delivery Audit

Use `list_all` to get an account-wide view of all automation schedules in a single call:

```
list-automations action: list_all, per_page: 100
```

You can narrow the results with optional filters:
- `search: "<report name>"` — filter by report name
- `frequency: "monthly"` — filter by delivery frequency

The response is minimal (id, frequency, send_time, delivery_day) and does **not** include receivers, timezone, or attachment settings. To verify how a specific automation is configured (recipient list, IANA timezone, PDF attachment, stop-on-issues), open the report in the UI — MCP does not expose those fields.

Review:
- Which reports have automated delivery scheduled?
- Delivery frequency (weekly, monthly, etc.)
- Are important reports missing automations?
- Reports with high activity but no automation are usually the highest-value gap to flag.

### 7. Sharing Configuration

For each important report:
```
view-sharing action: show, report_id: <id>
```

Check:
- Are reports shared with the right stakeholders?
- Are public sharing links active when they should be?
- Are there reports shared that shouldn't be?

### 8. Goals & KPI Tracking

```
view-goals action: list
list-overviews action: list
```

Review:
- Are goals set for key metrics?
- Are overviews (KPI dashboards) configured?
- Do goals align with the channels and sources that are connected?

`list` covers goal **setup** only — it says nothing about whether goals are being met. If the audit is meant to report attainment, measure it:

```
view-goals action: status goal_ids: [<up to 20 ids from the list above>]
```

Batch in twenties, and report `unknown` goals as blind spots. Do not describe goals as healthy, on track, or within limit unless a `status` call said so — `active: true` in the `list` response only means the goal is still running.

### 9. Blend & Source Group Review

```
list-blends action: list
list-source-groups action: list
```

The `list` response includes `source_count` and `channel_names` per blend — often enough to assess blend health without calling `show`. For deeper inspection (join config, usage stats):
```
list-blends action: show, blend_id: <id>
```

For each source group, inspect per-config detail:
```
list-source-groups action: show, group_id: <id>
```
Returns each config's `id`, `output_name`, and `etl_config_ids` — useful for understanding the group's data pipeline setup.

Check for sync issues — omit `group_id` to scan all groups at once:
```
list-source-groups action: source_issues                    # all groups
list-source-groups action: source_issues, group_id: <id>    # one group
```

Review:
- Are blends set up for cross-channel reporting?
- Do source groups include all expected sources? (check `show` for the sources array per group)
- Any source groups with sync issues?

### 10. Custom Fields Review

```
list-custom-metrics action: list
list-custom-dimensions action: list
```

To check if custom fields are actually being used, query usage per field:
```
list-custom-metrics action: usage, universal_metric_ids: [id1, id2, ...]
list-custom-dimensions action: usage, universal_dimension_ids: [id1, id2, ...]
```

For tag-type custom dimensions, inspect the tags and their source assignments:
```
list-custom-dimensions action: list_tags, dimension_id: <id>
```

Review:
- Are custom metrics/dimensions being used? (check `usage` action)
- Are tag-type dimensions properly assigned to sources?
- Are there opportunities to create useful custom fields?

## Health Check Summary Template

After completing the audit, present findings in this structure:

### Account Overview
- **Plan**: [plan name]
- **Sources**: [used] / [limit]
- **Reports**: [count]
- **Integrations**: [list of connected channels]

### Health Status

| Area | Status | Details |
|------|--------|---------|
| Source Connections | [OK/Warning/Critical] | [X] sources healthy, [Y] with errors |
| Space Organization | [OK/Warning] | [X] spaces, [Y] reports |
| Report Coverage | [OK/Warning] | All spaces have reports / [X] spaces without reports |
| Automations | [OK/Warning] | [X] reports with delivery / [Y] without |
| Sharing | [OK/Info] | [X] reports shared |
| Goals & KPIs | [OK/Warning] | [X] goals set / Overviews: [Y] |
| Cross-Channel | [OK/Info] | [X] blends, [Y] source groups |

### Recommendations
1. [Most critical action item]
2. [Second priority]
3. [Third priority]

## Common Issues to Flag

- **Plan over-utilisation**: when `sources_used > sources_total` (visible in `view-team action=show_subscription`), surface this first. It blocks new source connection and indicates the account is on a stale plan or in the middle of a migration. Recommend either upgrading or removing unused sources before anything else. **Exception**: legacy plans may show `sources_total: 0` meaning "unlimited" — do not flag this as over-utilisation.
- **Disconnected sources**: Sources with `status: "issue"` are not collecting data. This is the highest priority issue.
- **No automations**: If reports exist but have no scheduled delivery, clients may not be receiving their reports automatically.
- **Orphan sources**: Sources not in any space may indicate incomplete setup.
- **Missing blends**: If multiple channels are connected but no blends exist, the user is missing out on cross-channel insights.
- **No goals set**: Without goals, there's no way to track progress against targets in overviews.
- **Underutilized features**: Custom metrics/dimensions not being used, no snapshots for historical tracking.

## Tips

- Start the audit from the team overview and work outward — this gives you the context of subscription limits and overall scale.
- Focus on actionable findings. Don't flag minor issues that don't impact the user's workflow.
- For agencies with many spaces, sample a few representative ones rather than auditing every single space.
- If the account is on a limited plan, note which features are restricted and whether upgrading would unlock value.
- For accounts with >50 sources, use `list-sources action=list` with `fields=id,name,space_ids,status` to find orphans (`space_ids: []`) and broken sources (`status: "issue"`). Then pass collected IDs to `list-sources action=list_usage source_ids=[...]` to find unused sources (zero usage counts). These are two separate checks — `list_usage` cannot detect orphans.
