---
name: whatagraph-custom-metrics
description: Create calculated or unified metrics on top of one or more data sources — formulas (ROAS, CPA, CPL), aggregations (total paid spend across channels), and metric aliases. Use when a standard channel metric isn't enough or when a derived metric needs to exist across multiple sources.
---

# Custom metrics

Tools covered: `list-custom-metrics`, `manage-custom-metrics`, `delete-custom-metrics`.

A **custom metric** is a calculated field that behaves like any other metric. Use it in a widget, in a blend, in a goal, or in an overview.

## Use this when

- User asks for ROAS, CPA, CPL, CPM, CTR — any formula not native to the channel.
- "Total spend" across Google Ads + Meta Ads + LinkedIn needs to be one metric.
- Renaming a native metric for a client-facing report.
- Expressing "Budget remaining" as `A - B`.

## Three metric types — pick the right one

| `map_type` | What it does | Example |
|---|---|---|
| `metadata` | 1:1 mapping (alias of an existing field) | Rename "Spend" to "Ad Cost" |
| `data_aggregation` | Sum one field across many sources | Total Paid Spend across Google + Meta + LinkedIn |
| `data_formula` | Formula with field identifiers A, B, C… | `A/B` for ROAS |

## Transformation level

| `transformation_level` | Meaning |
|---|---|
| `channel` | Metric applies to all sources of a channel (e.g. every Google Ads source) |
| `source` | Metric applies to one specific source |
| `widget` | Metric is per-widget only |

Use `channel` for reusable cross-source metrics (most common). Use `source` to scope to one account. Use `widget` for one-off formulas (prefer per-widget formulas via `manage-widgets` for those).

## Listing

```
list-custom-metrics action=list
list-custom-metrics action=list_with_premades       # includes platform-native metrics
list-custom-metrics action=show metric_id=<id>
list-custom-metrics action=usage universal_metric_ids=[<id>, <id>]
```

## Creating a `data_formula` metric

```
manage-custom-metrics action=create
   name="Google Ads CTR %"
   description="clicks / impressions * 100"
   map_type="data_formula"
   transformation_level="channel"
   fields=[
     {
       "channel_id": 5,
       "field_external_id": "metrics.clicks",
       "report_type_external_id": "campaign",
       "identifier": "A"
     },
     {
       "channel_id": 5,
       "field_external_id": "metrics.impressions",
       "report_type_external_id": "campaign",
       "identifier": "B"
     }
   ]
   formula="A/B*100"
   formula_value_type="percent"
   accumulator="average"
   aggregation_level="aggregate"
   formula_increase="positive"
```

### Required extra params for `data_formula`

The tool rejects `data_formula` creates without these four:

| param | values | use |
|---|---|---|
| `formula_value_type` | `int`, `percent`, `float`, `currency`, `seconds`, `milliseconds` | How the result renders |
| `accumulator` | `sum`, `average`, `last`, `first` | How values roll up across rows/time |
| `aggregation_level` | `aggregate`, `row` | `aggregate` = apply formula on totals; `row` = apply per row, then accumulate |
| `formula_increase` | `positive`, `negative` | `positive` = higher is better (revenue, CTR); `negative` = lower is better (CPA, CPL) |

All four must be set. If any is missing, the tool returns an error that names the missing parameter.

### Which `field_external_id` works where

`field_external_id` is whatever `list-sources action=list_dimensions_and_metrics` returns for the field you want. Three forms are accepted:

1. **Platform-unified metric ids** — `universal_metric_<n>` (e.g. `universal_metric_1` = Impressions, `universal_metric_2` = Clicks, `universal_metric_3` = Spend). Use these when you want the formula to work identically on any channel that exposes the unified slot.
2. **Channel-native ids** — `metrics.clicks`, `metrics.impressions`, `spend`, `impressions`, etc. Use these when the field only exists on one channel.
3. **Existing custom metric ids** — `universal_metric_<custom_metric_id>` (e.g. `universal_metric_511018`). Use these to build derived metrics on top of another custom metric. Include the `_metric_` infix; the shorter `universal_<id>` form is not valid.

The same applies to `manage-custom-dimensions` — accepts `universal_dimension_<n>`, channel-native ids, and existing `universal_dimension_<custom_dimension_id>`.

### Formula rules

- Uses **single-letter identifiers** (`A`, `B`, `C`…), NOT `{placeholder}` tokens.
- No spaces around operators, no braces: `(A-B)/B` not `(A - B) / B`.
- Operators: `+ - * /`, parentheses.
- Division by zero → empty cell.

### `formula_value_type`

Required for `data_formula`. Values: `int`, `percent`, `float`, `currency`, `seconds`, `milliseconds`.

- Use `percent` for CTR, ACoS, conversion rate.
- Use `currency` for CPA, CPL, revenue-per-X.
- Use `float` for ROAS.
- Use `int` for whole-number counts (rare for formulas).
- Use `seconds` / `milliseconds` for time-based metrics.

### `accumulator`

Required for `data_formula`. How the value rolls up over time:

| `accumulator` | Behavior |
|---|---|
| `sum` | Sum per row, then sum across rows |
| `average` | Row-average — recommended for ratios like ROAS |
| `last` | Last data point only |
| `first` | First data point only |

For ratio metrics (ROAS, CPA, CTR): use `average`. For summable metrics: `sum`.

## Creating a `data_aggregation` metric

Sums one field across multiple sources.

```
manage-custom-metrics action=create
   name="Total Paid Spend"
   map_type="data_aggregation"
   transformation_level="source"
   fields=[
     {"integration_source_id": <google_ads_source>, "field_external_id": "universal_metric_3", "report_type_external_id": "campaign"},
     {"integration_source_id": <meta_ads_source>,   "field_external_id": "universal_metric_3", "report_type_external_id": "campaigns"},
     {"integration_source_id": <linkedin_ads_source>, "field_external_id": "universal_metric_3"}
   ]
```

Pick `transformation_level=source` when aggregating across specific sources.

## Creating a `metadata` alias

```
manage-custom-metrics action=create
   name="Ad Cost"
   map_type="metadata"
   transformation_level="channel"
   fields=[
     {"channel_id": <channel_id>, "field_external_id": "universal_metric_3", "report_type_external_id": "campaign"}
   ]
```

## Updating

```
manage-custom-metrics action=update metric_id=<id>
   name="..." fields=[...] formula="..." formula_value_type="..." accumulator="..."
```

Replace-style — the full `fields` list replaces the previous one.

## Duplicating

```
manage-custom-metrics action=duplicate metric_id=<id>
```

## Checking usage before modifying

```
list-custom-metrics action=usage universal_metric_ids=[<id>]
```

Returns the number of widgets/reports affected.

## Using a custom metric in `fetch-data`

Once created, a custom metric has a new `external_id` of the form `universal_metric_<metric_id>` (e.g. `universal_metric_511018`) — visible in `list-sources action=list_dimensions_and_metrics` next to the platform-native metrics. Use that directly in `fetch-data`:

```
fetch-data source_id=<source_id>
  report_type="campaign"
  metrics=["universal_metric_511018"]
  dimensions=["universal_dimension_1137"]
  from="2026-04-01" till="2026-04-15"
```

**Custom metrics on a source-group's virtual `integration_source_id` cannot be read via `fetch-data` on the group itself.** The platform aggregates sub-source data at the widget/export layer, not at the `fetch-data` boundary. To preview a custom metric on a source group, call `fetch-data` against each constituent source individually, or render the metric in a widget and read it via `list-widgets action=csv_export` / `export-report`. The error message returned by `fetch-data` on the group strips the `_metric_` infix, so the diagnostic looks like `Invalid metrics: universal_<id>` — that is *not* a hint that the legacy form would have worked; the metric simply does not resolve at the group level.

## What MCP can't do here

- Only `metadata`, `data_aggregation`, and `data_formula` map types are exposed.
- `transformation_level=widget` — build widget-local formulas via `manage-widgets` instead.

## Common pitfalls

- **Using `{placeholder}` tokens in formulas** — wrong. Use `A/B` style identifiers only.
- **Passing metric display names as `field_external_id`** — field IDs come from `list-sources action=list_dimensions_and_metrics`, not display names.
- **Missing any of `accumulator`, `aggregation_level`, `formula_increase`, `formula_value_type` on a `data_formula` create** — all four are required.
- **`transformation_level=channel` with `integration_source_id` fields** — use `channel_id` at channel level; use `integration_source_id` at source level.
- **Cross-channel aggregation without unified field names** — if Google Ads calls it `metrics.cost_micros` and Meta calls it `spend`, you still pick each per-source native field; the aggregation happens on the metric's output, not on the input names.
- **Division by zero** → empty cell, not infinity.
- **Formula spaces** — `A / B` with spaces is rejected. Write `A/B`.
