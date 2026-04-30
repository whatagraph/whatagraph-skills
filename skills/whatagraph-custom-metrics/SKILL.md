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

Missing any of them returns:

> Error: The aggregation_level parameter is required for data_formula metrics. Values: aggregate, row. The formula_increase parameter is required for data_formula metrics. Values: positive (higher=better), negative (lower=better).

### Which `field_external_id` works where

The backend resolves fields in this order by `field_external_id` prefix:

1. `universal_*` prefix → looked up against the team's custom metric library (needs the numeric custom metric ID, e.g. `universal_511018`). **Platform-premade IDs like `universal_metric_1` / `universal_metric_2` / `universal_metric_3` are rejected here** — the parser strips `universal_` and tries to cast `metric_1` to an integer, which fails with *"Universal metric with ID 0 not found"*. For premade metrics, use the channel-native ID instead (see below).
2. Otherwise with `integration_source_id` → resolved as a source-level native metric on that source's channel (e.g. `metrics.clicks` on a Google Ads source, `spend` on a Facebook Ads source).
3. Otherwise with `channel_id` → resolved as a channel-level native metric (e.g. `metrics.impressions` for channel 5 / Google Ads).

**Rule of thumb:** use the native channel/source `field_external_id` you get back from `list-sources action=list_dimensions_and_metrics` (things like `metrics.clicks`, `metrics.impressions`, `spend`, `impressions`, `clicks`), not the `universal_metric_*` premade IDs — they're for use in `fetch-data` queries, not for wiring into custom metric fields.

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
     {"integration_source_id": <meta_ads_source>,   "field_external_id": "spend",             "report_type_external_id": "campaigns"},
     {"integration_source_id": <linkedin_ads_source>, "field_external_id": "cost"}
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

Once created, a custom metric has a new `external_id` of the form `universal_<metric_id>` (e.g. `universal_511018`). Use that directly in `fetch-data`:

```
fetch-data source_id=<underlying source>
  report_type="campaign"
  metrics=["universal_511018"]
  dimensions=["universal_dimension_1137"]
  from="2026-04-01" till="2026-04-15"
```

The metric resolves on any source of the same channel where the underlying native fields exist. It does **not** flow through source-group virtual sources — to read an aggregated CTR across a source group, call `fetch-data` on each constituent source and compute client-side, or rely on the widget layer when rendering in a report.

## What MCP can't do here

- Tag or currency-exchange map types via MCP — only `metadata`, `data_aggregation`, `data_formula` are exposed.
- `transformation_level=widget` (widget-local custom formulas) — enum value exists in code but the MCP schema currently only accepts `channel` and `source`. Build widget-local formulas via `manage-widgets` instead.
- Custom metrics on top of a blend's virtual source (channel id 142). The tool rejects blend field ids and blend source ids — write the formula using each constituent source's native fields at `transformation_level=source`, or compute the derived metric inside the widget.

## Common pitfalls

- **Using `{placeholder}` tokens in formulas** — wrong. Use `A/B` style identifiers only.
- **Passing metric display names as `field_external_id`** — field IDs come from `list-sources action=list_dimensions_and_metrics`, not display names.
- **Passing `universal_metric_1` / `universal_metric_2` / `universal_metric_3` as `field_external_id`** — rejected with *"Universal metric with ID 0 not found"*. Use the channel-native ID (e.g. `metrics.clicks`, `metrics.impressions`).
- **Missing any of `accumulator`, `aggregation_level`, `formula_increase`, `formula_value_type` on a `data_formula` create** — all four are required.
- **`transformation_level=channel` with `integration_source_id` fields** — use `channel_id` at channel level; use `integration_source_id` at source level.
- **Cross-channel aggregation without unified field names** — if Google Ads calls it `metrics.cost_micros` and Meta calls it `spend`, you still pick each per-source native field; the aggregation happens on the metric's output, not on the input names.
- **Division by zero** → empty cell, not infinity. Add a fallback in client messaging if customers see blanks.
- **Formula spaces** — `A / B` with spaces is rejected. Write `A/B`.
