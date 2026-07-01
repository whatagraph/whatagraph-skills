---
name: whatagraph-filters
type: domain
description: Create saved filter configurations for a channel. Filters are per-channel conditions on a dimension or metric that can be attached to widgets or reports via the UI. Use when a user wants reusable "only this audience / only this campaign / only above $X" filtering.
required_tools:
  - list-filters
  - list-sources
  - list-widgets
  - manage-filters
---

# Filters

Tools covered: `list-filters`, `manage-filters`.

A **filter** belongs to a channel and is a reusable set of dimension or metric conditions. Filters are organized as row groups; within a row group conditions use OR, across row groups conditions use AND.

There are three ways to filter a widget:

1. **Direct create on target** (recommended) — pass `widget_config_id` or `source_id` on `manage-filters action=create`. Creates the filter directly on the target, no separate `attach` step, no orphaned team-level filter. Cannot pass both.
2. **Inline `filter_id` on `manage-widgets`** — pass `filter_id` (a team-level filter ID) in `rows[].configs[]` during `create` or `update`. Copies the team filter onto the config. Pass `filter_id: null` to detach.
3. **Create + attach** (two-step) — `manage-filters action=create` (team-level), then `manage-filters action=attach` to a `widget_config_id` or `source_id`.

All three mechanisms create a **config-scoped copy** (`team_available=false`) that does NOT appear in `list-filters action=list`. To see these copies, use `list-widgets action=show` → `configs[].inline_filters[]`. Each new attach **replaces** the single existing copy on the target silently.

### Filter precedence — merge, not override

When a widget has **both** a widget_config filter and a source filter, the runtime **merges** them: it builds a new filter whose rows are the source rows PLUS the widget_config rows. Different row groups are AND'd, so the result is the **intersection** of both filters — not an override.

To make a widget **ignore** its source-level filter, set `source_filter_off=true` on the widget config (visible via `list-widgets action=show`).

> **Avoid source-level filters unless explicitly requested.** A source filter applies to **every widget using that source across all reports** — not just the current report. This is a broad, account-wide change. It can also cause errors: the filter may reference a dimension or metric that doesn't exist in every report type the source's widgets use. Default to `widget_config_id` for per-widget filtering. Only use `source_id` when the user specifically wants all data from that source filtered (e.g. "I only want US data from this source" or "filter this source to only show organic traffic").

### Filter versions (v1 / v2)

On create, the version is auto-set per channel based on `supportsV2Filters()` — the agent cannot choose. v2 filters are pushed to the provider API; v1 filters are applied locally after fetch. The version is visible in `list-filters action=show` as `version`.

## Use this when

- "Show only campaigns with 'brand' in the name."
- "Exclude Test campaigns from this widget."
- "Filter conversions to only the specific event."
- "Show rows where spend > 100 AND clicks > 50."
- "Brand OR Competitor campaigns" in one group.

## Listing

```
list-filters action=list                       # all team filters
list-filters action=list channel_id=<id>       # only for one channel
list-filters action=show filter_id=<id>        # structure, values
```

Config-scoped copies (`team_available=false`) do not appear in `list-filters action=list`. Use `list-widgets action=show` → `configs[].inline_filters[]` to see them — each inline filter includes a `team_available` boolean to distinguish config-scoped from team-level filters. Also, `list-widgets action=list` includes `has_filters: bool` per widget, so you can check which widgets have filters without calling `show` on each one.

## Filter parameters (attribution windows, granularity, etc.)

Some channels expose **filter parameters** — channel-specific settings like attribution windows, granularity, conversion report time, or status filters. These control how filtered data is queried from the provider API (e.g. Pinterest Ads has View/Click/Engagement window, granularity, attribution type, and status filters).

### Discovering available parameters

```
list-filters action=list_parameters channel_id=<channel_id>
```

Returns the available parameters for the channel with their valid values. If the channel has no parameters, returns an empty `parameters` array.

### Setting parameters on create or update

Pass `filter_parameters` as a JSON object with `{"key": "value_id"}` for single-select, or `{"key": ["value_id_1", "value_id_2"]}` for multiselect.

**Parameter-only filter** (no dimension/metric condition needed):

```
manage-filters action=create
   channel_id=<channel_id>
   widget_config_id=<widget_config_id>
   filter_parameters={"view_window_days": "DAYS_7", "click_window_days": "DAYS_1"}
```

**Combined** — condition + parameters:

```
manage-filters action=create
   channel_id=<channel_id>
   dimension="universal_dimension_<id>"
   dimension_operator="contain_dimension"
   value="brand"
   widget_config_id=<widget_config_id>
   filter_parameters={"view_window_days": "DAYS_7", "click_window_days": "DAYS_1"}
```

Use the `key` and `values[].id` from `list_parameters` to construct the object. Parameters with `type: "select"` require a value from the predefined list — invalid values return a validation error. Parameters with `type: "text"` or `type: "number"` accept freeform values (e.g. `{"database": "us", "display_limit": "10"}`).

Filter parameters can also be set or changed on an existing filter via `update`:

```
manage-filters action=update filter_id=<id>
   filter_parameters={"view_window_days": "DAYS_30"}
```

**Update replaces all parameters** — it does not merge. If the filter had `view_window_days` + `granularity` and you update with only `{"view_window_days": "DAYS_30"}`, the `granularity` setting is removed. To keep existing parameters, include them all in the update call.

## Field IDs — both universal and channel-native work

`manage-filters` accepts **both** channel-native IDs (e.g. `campaign.name`, `metrics.cost`) **and** `universal_dimension_*` / `universal_metric_*` IDs.

Use `list-sources action=list_dimensions_and_metrics` to discover field IDs — it returns `universal_*` IDs, and these are valid filter fields. Some channels (e.g. Google Ads) resolve metrics **only** via `universal_metric_*` — channel-native metric IDs like `metrics.cost` or `spend` fail validation on those channels. When in doubt, use the universal IDs returned by the discovery tool.

The set of filterable dimensions/metrics may be smaller than the full reportable set. If a field is rejected, the error message lists every valid filter field for the channel.

## Creating a dimension filter

```
# Team-level reusable filter (default)
manage-filters action=create
   channel_id=<channel_id>
   dimension="universal_dimension_<id>"
   dimension_operator="contain_dimension"
   value="brand"
   group="AND"
   name="Branded campaigns"

# Direct on a widget config (no attach needed, no team-level filter created)
manage-filters action=create
   channel_id=<channel_id>
   dimension="universal_dimension_<id>"
   dimension_operator="contain_dimension"
   value="brand"
   name="Branded campaigns"
   widget_config_id=<widget_config_id>

# Direct on a source (applies to all widgets using this source)
manage-filters action=create
   channel_id=<channel_id>
   dimension="universal_dimension_<id>"
   dimension_operator="contain_dimension"
   value="brand"
   name="Branded campaigns"
   source_id=<source_id>
```

When `widget_config_id` or `source_id` is provided, the filter is created directly on that target with `team_available=false`. Any existing filter on the target is replaced. The channel must match the target's channel. Cannot pass both `widget_config_id` and `source_id`.

On a successful `create`, the `name` you pass is persisted on the filter and shown in `list-filters action=show`.

Valid `dimension_operator`:
- `contain_dimension`, `not_contain_dimension`
- `exactly_matches_dimension`, `not_exactly_matches_dimension`
- `includes`, `excludes`
- `starts_with_dimension`, `not_starts_with_dimension`
- `ends_with_dimension`, `not_ends_with_dimension`
- `matches_regex_dimension`, `not_matches_regex_dimension`
- `empty_dimension`, `not_empty_dimension` (no `value` needed)

## Creating a metric filter

```
manage-filters action=create
   channel_id=<channel_id>
   metric="universal_metric_<id>"
   metric_operator="greater_metric"
   value="100"
   group="AND"
```

Discover metric IDs via `list-sources action=list_dimensions_and_metrics`. Use the `universal_metric_*` IDs it returns — on some channels (e.g. Google Ads), only universal metric IDs pass validation.

Valid `metric_operator`:
- `equal_metric`, `not_equal_metric`
- `greater_metric`, `greater_or_equal_metric`
- `less_metric`, `less_or_equal_metric`
- `empty_metric`, `not_empty_metric`

Dimensions and metrics cannot be mixed in the same row group.

## Adding a condition to an existing filter

```
manage-filters action=add
   filter_id=<id>
   dimension="universal_dimension_<id>"
   dimension_operator="contain_dimension"
   value="competitor"
   group="OR"            # OR appends to the last row group; AND creates a new row group
   row_index=0           # target a specific row group for OR appends
```

Row group logic:
- `group="AND"` creates a new row group.
- `group="OR"` adds to the row group at `row_index` (0-based).
- Different row groups are combined with AND; conditions inside a row group are combined with OR.
- Some channels restrict group operators — e.g. Google Search Console allows only AND across groups (no OR within a group). If OR is rejected, fall back to AND row groups.

When re-reading a filter after adding an OR condition, the OR operator is stored on the first condition of the row group.

## Updating

```
manage-filters action=update filter_id=<id>
   dimension_operator="exactly_matches_dimension"
   value="brand"
```

Update applies to ALL rows in the filter — useful for renaming a value or switching an operator across the whole filter.

## Deleting a filter

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: soft delete, requires `action=delete` + `filter_id`, widgets referencing the filter keep rendering (unfiltered).

## Attaching a filter

After creating a filter, attach it to a widget or to a report-level source:

```
# Attach to a widget
manage-filters action=attach filter_id=<id> widget_config_id=<id>

# Attach to a report-level source (applies to all widgets using that source)
manage-filters action=attach filter_id=<id> source_id=<id>
```

Use `list-widgets action=show` to find `widget_config_id` values, and `list-sources action=list` to find `source_id` values.

`create` and `attach` support `idempotency_key` for retry-safe operations.

## Response reference

### `list-filters action=list`

```json
{
  "success": true,
  "filters": [
    { "id": 123, "name": "Branded campaigns", "integration": "Google Ads", "model_type": "team", "team_available": true }
  ],
  "page": { "cursor": null, "has_more": false, "estimated_total": 5 }
}
```

Only team-level filters (`team_available: true`) appear here. Config-scoped copies do not.

### `list-filters action=list_parameters`

```json
{
  "success": true,
  "channel_id": 118,
  "channel_name": "Pinterest Ads",
  "parameters": [
    {
      "key": "view_window_days",
      "label": "View window",
      "type": "select",
      "values": [
        { "id": "DAYS_0", "name": "0" },
        { "id": "DAYS_1", "name": "1 Day" },
        { "id": "DAYS_7", "name": "7 Days" },
        { "id": "DAYS_30", "name": "30 Days" }
      ]
    }
  ]
}
```

Pass `values[].id` as the value in `filter_parameters` on `manage-filters create/update`. Channels without parameters return `"parameters": []`.

### `list-filters action=show`

```json
{
  "success": true,
  "filter": {
    "id": 123, "name": "Branded campaigns", "integration": "Google Ads",
    "channel_id": 5, "model_type": "team", "model_id": null,
    "team_available": true, "version": 2,
    "options": {
      "filter": [
        [
          { "group_id": "g1", "order_id": "o1", "operator": null, "dimension": "universal_dimension_1", "metric": null, "filter_operator": "contain_dimension", "value": "brand" },
          { "group_id": "g1", "order_id": "o2", "operator": "OR", "dimension": "universal_dimension_1", "metric": null, "filter_operator": "contain_dimension", "value": "competitor" }
        ],
        [
          { "group_id": "g2", "order_id": "o3", "operator": null, "dimension": null, "metric": "universal_metric_3", "filter_operator": "greater_metric", "value": "100" }
        ]
      ],
      "default_inputs": []
    }
  }
}
```

`options.filter` is an array of row groups (AND). Each row group is an array of conditions (OR within). The `operator` field on the first condition of a row group is `null`; subsequent conditions in the same group have `"OR"`. `default_inputs` holds UI-populated pre-selected values for filter dropdowns — always `[]` for MCP-created filters; safe to ignore.

### `manage-filters action=create` / `add` / `update` / `attach`

All four actions return the same shape:

```json
{
  "success": true,
  "filter": {
    "id": 456, "name": "Branded campaigns",
    "channel_id": 5, "model_type": "widget_config",
    "team_available": false, "version": 2,
    "options": {
      "filter": [[ ... ]],
      "default_inputs": []
    }
  }
}
```

`model_type` is `"team"` for team-level filters, `"widget_config"` or `"source"` for config-scoped copies. `team_available` is `false` for config-scoped copies.

## What MCP can't do here

- Reorder row groups — UI only.

## Common pitfalls

- **`contains` vs `contain_dimension`** — MCP operators have the `_dimension` or `_metric` suffix. `contains` alone is rejected.
- **Mixing metric + dimension in same row group** — not allowed. Create separate row groups (`group="AND"`).
- **`value` for `empty_*` / `not_empty_*`** — not needed. Omit `value`.
- **Regex escaping** — JSON-escape backslashes (`"\\b"`).
- **Filter created on the wrong `channel_id`** — filters are per-channel; make sure to match the source's channel.
- **Case sensitivity** — `contain_dimension` is case-insensitive; `exactly_matches_dimension` is case-sensitive.
- **Forgetting that `value` is a string** — always pass strings, even for numeric metric thresholds (`"100"` not `100`).
- **Channel-native metric IDs failing** — on some channels (e.g. Google Ads), only `universal_metric_*` IDs work. Always try the universal IDs from `list_dimensions_and_metrics` first.
