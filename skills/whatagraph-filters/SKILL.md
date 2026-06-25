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

### Filter precedence

A widget applies **one** filter at runtime, not both:
- If a **widget_config filter** exists, it is used.
- Otherwise, if the config's **source** has a filter, that is used.
- Widget-config filters always take priority over source-level filters.

> **Avoid source-level filters unless explicitly requested.** A source filter applies to **every widget using that source across all reports** — not just the current report. This is a broad, account-wide change. It can also cause errors: the filter may reference a dimension or metric that doesn't exist in every report type the source's widgets use (e.g. a metric filter on a source where some widgets use a report type that lacks that metric). Default to `widget_config_id` for per-widget filtering. Only use `source_id` when the user specifically wants all data from that source filtered (e.g. "I only want US data from this source" or "filter this source to only show organic traffic").

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

## Creating a dimension filter

```
# Team-level reusable filter (default)
manage-filters action=create
   channel_id=<channel_id>
   dimension="campaign.name"
   dimension_operator="contain_dimension"
   value="brand"
   group="AND"
   name="Branded campaigns"

# Direct on a widget config (no attach needed, no team-level filter created)
manage-filters action=create
   channel_id=<channel_id>
   dimension="campaign.name"
   dimension_operator="contain_dimension"
   value="brand"
   name="Branded campaigns"
   widget_config_id=<widget_config_id>

# Direct on a source (applies to all widgets using this source)
manage-filters action=create
   channel_id=<channel_id>
   dimension="campaign.name"
   dimension_operator="contain_dimension"
   value="brand"
   name="Branded campaigns"
   source_id=<source_id>
```

When `widget_config_id` or `source_id` is provided, the filter is created directly on that target with `team_available=false`. Any existing filter on the target is replaced. The channel must match the target's channel. Cannot pass both `widget_config_id` and `source_id`.

> **Important — filter dimension ids are channel-native, not universal.** The dimension ids accepted by `manage-filters` are the channel's raw dotted-path ids (Google Ads `campaign.name`, `segments.day_of_week`, `ad_group.status`; Facebook Ads `campaign_name`, `adset_name`; etc.) — **not** the `universal_dimension_*` ids returned by `list-sources action=list_dimensions_and_metrics`. If you pass a `universal_dimension_*` value the API rejects it and lists every valid filter dimension for the channel in the error message; copy the right one from there. The set of filterable dimensions is also smaller than the set of reportable dimensions on each channel.

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
   metric="spend"
   metric_operator="greater_metric"
   value="100"
   group="AND"
```

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
   dimension="campaign_name"
   dimension_operator="contain_dimension"
   value="competitor"
   group="OR"            # OR appends to the last row group; AND creates a new row group
   row_index=0           # target a specific row group for OR appends
```

Row group logic:
- `group="AND"` creates a new row group.
- `group="OR"` adds to the row group at `row_index` (0-based).
- Different row groups are combined with AND; conditions inside a row group are combined with OR.

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
