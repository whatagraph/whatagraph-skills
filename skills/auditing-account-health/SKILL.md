---
name: auditing-account-health
description: >-
  Review the overall health of a Whatagraph account including source connections,
  integration status, automation schedules, sharing configurations, goals,
  subscription details, and organizational structure. Use when the user asks
  for an account review, wants to check if everything is connected properly,
  asks "is my account set up correctly?", needs a health check, or wants to
  understand their subscription and usage.
---

# Auditing Account Health

Perform a comprehensive review of a Whatagraph account to identify connection issues, configuration gaps, underutilized features, and optimization opportunities.

## Full Account Health Check Workflow

### 1. Team & Subscription Overview

```
view-team action: show
```

Review:
- **Subscription plan** and limits (sources, reports, users)
- **Team settings** and configuration
- **Usage vs. limits** — is the account near any capacity limits?

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
list-integrations action: list_accounts, integration_id: <id>
```

### 3. Source Health Scan

```
list-sources action: list, per_page: 50
```

Check for:
- **Error sources** (`has_error: true`) — these need reconnection or troubleshooting
- **Orphan sources** (`team_clients: []`) — sources not assigned to any space
- **Source count** vs. subscription limits

For sources with errors:
```
list-sources action: show, source_id: <id>
```

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
list-spaces action: show, space_id: <id>
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

```
list-automations action: list
```

Review:
- Which reports have automated delivery scheduled?
- Delivery frequency (weekly, monthly, etc.)
- Are important reports missing automations?

### 7. Sharing Configuration

For each important report:
```
view-sharing report_id: <id>
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

### 9. Blend & Source Group Review

```
list-blends action: list
list-source-groups action: list
```

Check:
- Are blends set up for cross-channel reporting?
- Do source groups include all expected sources?
- Any source groups with sync issues?

```
list-source-groups action: source_issues, group_id: <id>
```

### 10. Custom Fields Review

```
list-custom-metrics action: list
list-custom-dimensions action: list
```

Review:
- Are custom metrics/dimensions being used?
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

- **Disconnected sources**: Sources with `has_error: true` are not collecting data. This is the highest priority issue.
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
