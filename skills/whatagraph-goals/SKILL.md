---
name: whatagraph-goals
type: domain
description: Create goals — targets on metrics (monthly spend caps, lead targets, ROAS floors) with time periods and optional dimension filtering. Use when a user wants to track progress toward a number by a deadline.
required_tools:
  - list-sources
  - view-goals
  - manage-goals
  - delete-goals
  - manage-widgets
---

# Goals

Tools covered: `view-goals`, `manage-goals`, `delete-goals`.

A **goal** is a target value on a metric for a specific period (daily, weekly, monthly, quarterly, yearly, or static). Goals can be hit (`target`), capped (`limit`), or bound to a range.

## Use this when

- "Track monthly spend against a $50k cap." → `condition=limit`, `max_value=50000`, `period=monthly`.
- "Show the team pacing toward 200 leads this month." → `condition=target`, `max_value=200`.
- "ROAS between 3 and 5." → `condition=range`, `min_value=3`, `max_value=5`.
- "One-off Q2 revenue target." → `period=static`, `repeat=0`.


## Known limitations

- Goal creation may not be available for every team or MCP server version. If `manage-goals action=create` is unavailable, use `view-goals` for existing goals and create new goals in the Whatagraph UI.
- Goals are identified by `metric_external_id` + `integration_source_id` + `report_type_external_id` + `dimension_key` (plus the measurement, when the goal sits on one); do not rely on `name` as the unique identifier.
- **The report type is part of that key even when you never passed it.** On a single-report-type source it is resolved for you and then matched exactly, so "I left it blank" does not make the key looser. Two goals differing *only* by report type are fine; a second goal identical in every other respect is refused as a conflict, and the error names the existing `goal_id` to view or update instead.
- **The timeframe is *not* part of the key.** So one metric on one source cannot carry both a monthly and a quarterly goal at the same scope — the second attempt is a conflict, not a second goal. To track the same metric over two timeframes, separate them by `dimension_key` or by measurement, or update the existing goal instead.
- **One goal per (metric, source, report type, dimension filter) combination.** Creating a second goal with the same `metric_external_id`, `integration_source_id`, `report_type_external_id`, and `dimension_key` returns a conflict error:
  ```
  {"category":"conflict","message":"A goal already exists for metric universal_metric_3 on source ID 632871"}
  ```
  The `dimension_key` is part of the key: a dimension-filtered goal and an unfiltered goal on the same metric+source coexist (e.g. an overall spend goal plus a "Search campaigns only" spend goal), and two goals on the same metric with *different* dimension filters coexist too. Always call `view-goals action=list source_id=<id>` first and check whether the exact combination is already covered. To change a target, update the existing goal via `manage-goals action=update goal_id=<id>` rather than creating a duplicate. To track the same metric on multiple sources, create one goal per source.

## Listing

```
view-goals action=list                             # all goals
view-goals action=list source_id=<id>              # filter by source
view-goals action=list search="spend"              # search by goal name or metric name
view-goals action=show goal_id=<id>                # full details
```

Pagination: page-number based (not cursor). `page` (integer, default 1) and `per_page` (integer, default 64, max 500). Use `last_page` from the response to know total pages.

`list` and `show` return **configuration only** — the target, the period, the direction. No current value, no verdict. Their `active` field means the goal is still running, **not** that it is being met. Never conclude from `list` or `show` that a goal is healthy, on track, or within its limit.

## Checking whether goals are being met

```
view-goals action=status goal_ids=[4455, 4017]
```

This is the only action that fetches actual data and decides. Per goal it returns:

| Field | Meaning |
|-------|---------|
| `status` | `on_track`, `off_track`, or `unknown` |
| `current_value` | Measured value so far in the goal's period |
| `goal_value` | The target, pro-rated to the working period |
| `percentage` | `current_value` as a share of `goal_value` |
| `projected_value` | Where the metric lands at the end of the period if the current run-rate holds |
| `current_pacing` | Run-rate per day, measured over a trailing 7-day window |
| `remaining_value` | How much is still needed (floored at 0) |
| `days_remaining` | Days left in the goal's period |

Response totals: `off_track_count`, `on_track_count`, `evaluated_count`, `unknown_goal_ids`, `missing_goal_ids`.

`off_track` means the goal is **projected** to miss a target or breach a limit at the current run-rate — not merely that it is behind an even pace. A goal already over a `limit` is off track; a `target` already achieved is on track.

`unknown` means the goal could not be measured at all — a disconnected source, a metric that no longer exists, an empty response. The `error` field says why. Report it as a blind spot; never count it as a pass.

`goal_ids` is **required and capped at 20 per call**, because each goal costs two source fetches (the working period plus the trailing pacing window). To check a whole account: `list` first, then `status` in batches of 20. `missing_goal_ids` tells you which requested IDs did not exist for the team, so a stale ID silently drops out of the batch rather than failing it.

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
   name="Monthly Spend Cap"                      # optional, persisted and shown in list/show
```

### `condition`

| `condition` | Uses | Meaning |
|---|---|---|
| `target` | `max_value` | Goal is met when metric ≥ `max_value` |
| `limit` | `max_value` | Goal is met when metric ≤ `max_value` |
| `range` | `min_value` + `max_value` | Goal is met when metric is within range |

### `period` + `repeat`

The two are **independent** settings, both required on `create`. Nothing rejects an "odd" combination, so these are conventions that match user intent, not validation rules:

- `daily` / `weekly` / `monthly` / `quarterly` / `yearly` — a recurring timeframe; normally `repeat="1"`.
- `static` — a one-off bounded period; normally `repeat="0"`.

Pairing them the other way is accepted and simply means what it says (a `monthly` goal with `repeat="0"` measures one month and does not roll forward). So do not treat a mismatch as an error to fix — check what the user actually wanted.

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
   name="Updated Goal Name"
```

## Attaching a goal to a widget

A goal renders in a report through a goal widget. Create it via `manage-widgets action=create` with the goal-widget type on the target tab. Goals also surface in overviews, measurement dashboards, and the dedicated Goals page in the UI.

**There is more than one goal widget type.** Pick by where the numbers come from:

- **Goal** — the standard one, tracking a metric on a connected source. This is the default choice.
- **Offline goal** — for manually entered (offline) data rather than a connected source. See `whatagraph-offline-reports`.

Each also exists in an older, pre-current-generation form that `manage-widgets` **rejects** on create and update. So take the type id from the current set rather than an older reference or a legacy report you are copying — an id that renders fine in an existing report is not necessarily one you can create. See `whatagraph-widgets` for the writable type ids.

Colour note: goal progress bars are filled with the palette's accent fill colour, which falls back to the first chart colour when unset — so set it deliberately on a report built around goals (see `whatagraph-themes`).

## Deleting a goal

```
delete-goals action=delete goal_ids=[<id1>, <id2>]
```

Batch-only — always an array, even for one goal. Goal widgets show an empty state until re-attached. IDs come from `view-goals`. See `whatagraph-deleting` for cascades and recovery context.

## What MCP can't do here

- Bulk create goals — one at a time.
- Custom pacing schedules — linear only; for seasonal/custom pacing, reach out to support.
- Check more than 20 goals in one call — `action=status` caps `goal_ids` at 20; batch larger checks.

## Common pitfalls

- **Reading `active: true` from `list` as "the goal is being met"** — it only means the goal is still running. Answering "all goals are healthy" off a `list` response states a verdict that was never measured. Call `action=status` or say you have not checked.
- **`repeat` as int vs string** — MCP expects `"1"` / `"0"` as strings.
- **`condition=limit` but passing `min_value`** — `min_value` is only used for `range`. Pass `max_value` for limit caps.
- **Goal on a source group** — pass the source group's integration source id (the exposed virtual source) as `integration_source_id`.
- **Goal on a blended metric** — same pattern; pass the blend's integration source id.
- **Period mismatch with report date range** — if the report shows "Last 30 days" but goal is `monthly`, the widget shows mid-period state. Align the report range with the goal period for clean visuals.
- **`target_value` / `target` param** — not a thing; use `max_value` (with `min_value` for `range`).
- **Dimension filter on a dimension the source doesn't have** — goal creates but never fires. Always verify the dimension via `list-sources action=list_dimensions_and_metrics` first.
