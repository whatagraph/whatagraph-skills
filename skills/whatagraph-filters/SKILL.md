---
name: whatagraph-filters
description: Create saved filter configurations for a channel. Filters are per-channel conditions on a dimension or metric that can be attached to widgets or reports via the UI. Use when a user wants reusable "only this audience / only this campaign / only above $X" filtering.
---

# Filters

Tools covered: `list-filters`, `manage-filters`, `delete-filters`.

A **filter** belongs to a channel and is a reusable set of dimension or metric conditions. Filters are organized as row groups; within a row group conditions use OR, across row groups conditions use AND.

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
manage-filters action=create
   channel_id=<channel_id>
   dimension="campaign_name"
   dimension_operator="contain_dimension"
   value="brand"
   group="AND"
```

Valid `dimension_operator`:
- `contain_dimension`, `not_contain_dimension`
- `exactly_matches_dimension`, `not_exactly_matches_dimension`
- `includes`, `excludes`
- `starts_with_dimension`, `ends_with_dimension`
- `matches_regex_dimension`
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

```
delete-filters filter_id=<id>
```

This tool takes only `filter_id` — no `action` parameter. Soft-delete. Widgets referencing the filter lose the filter behavior but keep rendering.

## What MCP can't do here

- Attach a filter to a widget or report via MCP — do it through the UI, or create the filter inline on the widget via `manage-widgets`.
- Reorder row groups — UI only.

## Common pitfalls

- **`contains` vs `contain_dimension`** — MCP operators have the `_dimension` or `_metric` suffix. `contains` alone is rejected.
- **Mixing metric + dimension in same row group** — not allowed. Create separate row groups (`group="AND"`).
- **`value` for `empty_*` / `not_empty_*`** — not needed. Omit `value`.
- **Regex escaping** — JSON-escape backslashes (`"\\b"`).
- **Filter created on the wrong `channel_id`** — filters are per-channel; make sure to match the source's channel.
- **Case sensitivity** — `contain_dimension` is case-insensitive; `exactly_matches_dimension` is case-sensitive.
- **Forgetting that `value` is a string** — always pass strings, even for numeric metric thresholds (`"100"` not `100`).
