---
name: whatagraph-goals
description: Create goals — targets on metrics (monthly spend caps, lead targets, ROAS floors) with time periods and optional dimension filtering. Use when a user wants to track progress toward a number by a deadline.
---

# Goals

Tools covered: `view-goals`, `manage-goals`, `delete-goals`.

A **goal** is a target value on a metric for a specific period (daily, weekly, monthly, quarterly, yearly, or static). Goals can be hit (`target`), capped (`limit`), or bound to a range.

## Use this when

- "Track monthly spend against a $50k cap." → `condition=limit`, `max_value=50000`, `period=monthly`.
- "Show the team pacing toward 200 leads this month." → `condition=target`, `max_value=200`.
- "ROAS between 3 and 5." → `condition=range`, `min_value=3`, `max_value=5`.
- "One-off Q2 revenue target." → `period=static`, `repeat=0`.

## Listing

```
view-goals action=list                             # all goals
view-goals action=list source_id=<id>              # filter by source
view-goals action=show goal_id=<id>                # full details
```

## Creating a goal

```
manage-goals action=create
   integration_source_id=<source_id>
   metric_external_id="universal_metric_3"
   report_type_external_id="campaign"           # if source has multiple report types
   condition="limit"                             # target | limit | range
   period="monthly"                              # daily | weekly | monthly | quarterly | yearly | static
   repeat="1"                                    # "1" repeats, "0" one-off
   max_value=50000
```

### `condition`

| `condition` | Uses | Meaning |
|---|---|---|
| `target` | `max_value` | Goal is met when metric ≥ `max_value` |
| `limit` | `max_value` | Goal is met when metric ≤ `max_value` |
| `range` | `min_value` + `max_value` | Goal is met when metric is within range |

### `period` + `repeat`

- `daily` / `weekly` / `monthly` / `quarterly` / `yearly` — recurring; combine with `repeat="1"`.
- `static` — one-off bounded period; combine with `repeat="0"`.

### Goal with dimension filter

Scope the goal to specific dimension values:

```
manage-goals action=create
   integration_source_id=<source_id>
   metric_external_id="universal_metric_10"
   condition="target" period="monthly" repeat="1" max_value=200
   dimension_key=[{"dimension":"campaign_type","value":"Search"}]
```

## Updating

```
manage-goals action=update goal_id=<id>
   condition="..." period="..." min_value=... max_value=... repeat="..."
```

## Attaching a goal to a widget

The widget type "Goal" is how a goal renders in a report. Create via `manage-widgets action=create` with the goal-widget type on the target tab. Goals also surface in overviews, measurement dashboards, and the dedicated Goals page in the UI.

## Deleting a goal

```
delete-goals action=delete goal_id=<id>
```

Any goal widgets referencing the deleted goal will show an empty state until re-attached.

## What MCP can't do here

- Bulk create goals — one at a time.
- Custom pacing schedules — linear only; for seasonal/custom pacing, reach out to support.

## Common pitfalls

- **`repeat` as int vs string** — MCP expects `"1"` / `"0"` as strings.
- **`condition=limit` but passing `min_value`** — `min_value` is only used for `range`. Pass `max_value` for limit caps.
- **Goal on a source group** — pass the source group's integration source id (the exposed virtual source) as `integration_source_id`.
- **Goal on a blended metric** — same pattern; pass the blend's integration source id.
- **Period mismatch with report date range** — if the report shows "Last 30 days" but goal is `monthly`, the widget shows mid-period state. Align the report range with the goal period for clean visuals.
- **`target_value` / `target` param** — not a thing; use `max_value` (with `min_value` for `range`).
- **Dimension filter on a dimension the source doesn't have** — goal creates but never fires. Always verify the dimension via `list-sources action=list_dimensions_and_metrics` first.
