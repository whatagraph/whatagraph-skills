---
name: whatagraph-custom-metrics
type: domain
description: Create calculated or unified metrics on top of a data source — formulas (ROAS, CPA, CPL), cross-source sum metrics (data_aggregation), and metric aliases / unified names. Use when a standard channel metric isn't enough. A data_aggregation metric sums the same metric across sources into one total; a cross-source ratio (blended ROAS/CPA) still needs a source group or blend (see whatagraph-source-groups / whatagraph-blends).
required_tools:
  - list-custom-metrics
  - manage-custom-metrics
  - list-sources
  - fetch-data
optional_tools:
  - tool_name: manage-custom-dimensions
    purpose: Alias fields or add a blend dimension when building the metric.
  - tool_name: list-widgets
    purpose: csv_export to preview a metric that only resolves at the widget layer.
  - tool_name: export-report
    purpose: Preview a metric rendered on a source group / blend widget.
  - tool_name: manage-widgets
    purpose: Remove widget references before deleting a metric.
  - tool_name: manage-filters
    purpose: Remove filter references before deleting a metric.
---

# Custom metrics

Tools covered: `list-custom-metrics`, `manage-custom-metrics`.

A **custom metric** is a calculated field that behaves like any other metric. Use it in a widget, in a blend, in a goal, or in an overview.

## Use this when

- User asks for ROAS, CPA, CPL, CPM, CTR — any formula not native to the channel.
- Renaming a native metric for a client-facing report (alias / unified name).
- Expressing "Budget remaining" as `A - B`.

**Also this:** to sum the **same** metric across multiple sources/channels into one total (e.g. one "Total Spend" across Google + Meta + LinkedIn), use a `data_aggregation` custom metric — it maps the field on each source and sums them, no virtual source required. See "Creating a `data_aggregation` metric" below.

**Not this:** a cross-source **ratio** (blended ROAS/CPA) where numerator and denominator come from different sources. A single custom metric can't divide across independently-aggregated sources — build a **source group** (rollup) or **blend** (join) first, then a `data_formula` on top of it. See `whatagraph-source-groups` and `whatagraph-blends`.

## Three metric types — pick the right one

| `map_type` | What it does | Example |
|---|---|---|
| `data_formula` | Formula with field identifiers A, B, C… | `A/B` for ROAS |
| `data_aggregation` | Sums the same metric across the sources/channels you map into one total | "Total Spend" across Google + Meta + LinkedIn |
| `metadata` | 1:1 mapping — alias / unified name for an existing field | Rename "Spend" to "Ad Cost"; unify "Cost" (Google) and "Amount spent" (Meta) under one name |

`data_aggregation` totals the **same** metric across sources into one value — no source group or blend needed. Reach for a **source group** (rollup) or **blend** (join) instead when you need a reusable virtual combined source, a cross-source **ratio**, or a join on a shared dimension. See `whatagraph-source-groups` and `whatagraph-blends`.

## Transformation level

| `transformation_level` | Meaning |
|---|---|
| `channel` | Metric applies to all sources of a channel (e.g. every Google Ads source) |
| `source` | Metric applies to one specific source |

Use `channel` for reusable cross-source metrics (most common). Use `source` to scope to one account. There is no `widget` transformation level — build per-widget formulas via `manage-widgets` instead.

## Listing

```
list-custom-metrics action=list
list-custom-metrics action=list_with_premades       # includes platform-native metrics
list-custom-metrics action=show metric_id=<id>
list-custom-metrics action=usage universal_metric_ids=[<id>, <id>]
```

`list` items carry a `transformation_level` field; `list_with_premades` items (platform-native metrics) do not.

### `show` — where a metric is valid (`resolves_on` / `usage_hint`)

`list-custom-metrics action=show metric_id=<id>` returns, alongside the metric config, two resolution fields that answer "where does this metric actually work":

- **`resolves_on`** — `{ channels: [{id, service, title}], sources: [{id, name}] }` — the exact channels and sources the metric's mapped fields land on. An empty `{}` means it maps to nothing. Check this before `fetch-data`: a custom metric only resolves on these channels/sources, and only for their mapped report types.
- **`usage_hint`** — a one-line reminder that the metric is referenced as `universal_metric_<id>` and does **not** resolve on a source group or blend unless the field was mapped there.

This is why a `universal_metric_<id>` fails on a source-group / blend `integration_source_id` — `resolves_on` will not list the group or blend. See "Using a custom metric in `fetch-data`" below.

### Finding an existing metric

Before creating a metric, search for one that already exists.

```
list-custom-metrics action=list search="ROAS"                       # name substring match
list-custom-metrics action=list semantic_search="customer acquisition cost"   # by meaning — finds CAC even if named differently
list-custom-metrics action=list type=channel                        # filter by transformation level
list-custom-metrics action=list_with_premades map_type=data_formula # filter by map type (incl. premade/system metrics)
list-custom-metrics action=list_with_premades integrations=[<id>]   # filter by integration
```

- `search` — name substring. Works on `list` and `list_with_premades`.
- `semantic_search` — meaning-based match ("cost per lead" finds CPL). **`list` only.** Default 10 results.
- `type` — transformation level, enum: `channel`, `source`. **`list` only.**
- `map_type` — map type, enum: `metadata`, `data`, `data_aggregation`, `data_formula`, `currency_exchange`, `tag`, `system`, `ai`. **`list_with_premades` only.**
- `integrations` — integration ID array. **`list_with_premades` only.**
- Paginate with `cursor` (pass `page.cursor` from prior response) and `per_page` (max 500, default 100).

## Creating a `data_formula` metric

```
manage-custom-metrics action=create
   name="Google Ads CTR %"
   description="clicks / impressions"
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
   formula="A/B"
   formula_value_type="percent"
   accumulator="average"
   summary_accumulator="average"
   aggregation_level="aggregate"
   formula_increase="positive"
```

### Required extra params for `data_formula`

The tool rejects `data_formula` creates without these four:

| param | values | use |
|---|---|---|
| `formula_value_type` | `int`, `percent`, `float`, `currency`, `seconds`, `milliseconds` | How the result renders |
| `accumulator` | `sum`, `average`, `last`, `first` | How values roll up across rows/time |
| `summary_accumulator` | `sum`, `average`, `last`, `first` | How the total/summary row is calculated (optional, defaults to `accumulator` value) |
| `aggregation_level` | `aggregate`, `row` | `aggregate` = apply formula on totals; `row` = apply per row, then accumulate |
| `formula_increase` | `positive`, `negative` | `positive` = higher is better (revenue, CTR); `negative` = lower is better (CPA, CPL) |

`formula_value_type`, `accumulator`, `aggregation_level`, and `formula_increase` must be set. If any is missing, the tool returns an error that names the missing parameter. `summary_accumulator` is optional but recommended for ratio metrics.

### Recommended settings per metric class

| Metric class | Example | `formula_value_type` | `accumulator` | `summary_accumulator` | `aggregation_level` | `formula_increase` |
|---|---|---|---|---|---|---|
| Rate / percentage | CTR, ACoS, conversion rate | `percent` | `average` | `average` | `aggregate` | `positive` |
| Cost-per-action | CPA, CPL, CPM | `currency` | `average` | `average` | `aggregate` | `negative` |
| Return ratio | ROAS | `float` | `average` | `average` | `aggregate` | `positive` |
| Summable total | Total spend, total clicks | `currency` / `int` | `sum` | `sum` | `row` | varies |

### Which `field_external_id` works where

`field_external_id` is whatever `list-sources action=list_dimensions_and_metrics` returns for the field you want. Three forms are accepted:

1. **Platform-unified metric ids** — `universal_metric_<n>` (e.g. `universal_metric_1` = Impressions, `universal_metric_2` = Clicks, `universal_metric_3` = Spend). Use these when you want the formula to work identically on any channel that exposes the unified slot.
2. **Channel-native ids** — `metrics.clicks`, `metrics.impressions`, `spend`, `impressions`, etc. Use these when the field only exists on one channel.
3. **Existing custom metric ids** — `universal_metric_<custom_metric_id>` (e.g. `universal_metric_511018`). Use these to build derived metrics on top of another custom metric. Include the `_metric_` infix; the shorter `universal_<id>` form is not valid.

The same applies to `manage-custom-dimensions` — accepts `universal_dimension_<n>`, channel-native ids, and existing `universal_dimension_<custom_dimension_id>`.

**On a blend source (channel 142)** the forms above do not apply — use `blend_metric_<n>` ids (with the blend's `integration_source_id`, not `channel_id`). `universal_metric_<n>` and `aggregation_metric_universal_metric_<n>` are **rejected** on a blend because they don't resolve in the blend's field catalog. See `whatagraph-blends` → "Custom fields on a blend" for the worked payload.

### Formula rules

- Uses **single-letter identifiers** (`A`, `B`, `C`…), NOT `{placeholder}` tokens.
- No spaces around operators, no braces: `(A-B)/B` not `(A - B) / B`.
- Operators: `+ - * /`, parentheses.
- Division by zero → empty cell.

### `formula_value_type`

Required for `data_formula`. Values: `int`, `percent`, `float`, `currency`, `seconds`, `milliseconds`.

- Use `percent` for CTR, ACoS, conversion rate. **The `percent` type automatically scales the raw value ×100 for display — write the formula as a raw ratio (`A/B`), NOT `A/B*100`.** Using `*100` with `percent` double-scales and produces results 100× too high.
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

### `summary_accumulator`

Optional. Controls how the total/summary row is calculated, independent of per-row accumulation. Accepts the same values as `accumulator`: `sum`, `average`, `last`, `first`. Defaults to the `accumulator` value if omitted.

Set `summary_accumulator="average"` for ratio/rate metrics (CTR, ROAS, CPA) so the summary row shows a weighted average rather than a sum of per-row values.

## Creating a `data_aggregation` metric (sum across sources)

`data_aggregation` sums the **same** metric across the sources or channels you map, producing one combined total — no source group or blend needed. Map the field once per source; the tool sums the mapped fields.

```
manage-custom-metrics action=create
   name="Total Ad Spend"
   map_type="data_aggregation"
   transformation_level="channel"
   fields=[
     {"channel_id": <google_ads_channel>, "field_external_id": "universal_metric_3"},
     {"channel_id": <meta_ads_channel>,   "field_external_id": "universal_metric_3"}
   ]
```

Unlike `data_formula`, `data_aggregation` needs **none** of `formula`, `formula_value_type`, `accumulator`, `aggregation_level`, or `formula_increase`, and its `fields` take **no** `identifier`. Just `name`, `map_type`, `transformation_level`, and the `fields` to sum. (The tool fixes the aggregation to `sum_of` automatically.)

- Use the unified `universal_metric_<n>` slot (e.g. `universal_metric_3` = Spend) when summing a metric that every mapped channel exposes; use channel-native ids (`spend`, `metrics.cost_micros`) when the field is channel-specific.
- `transformation_level=channel` maps one field per channel (every source of that channel contributes); `source` maps specific `integration_source_id`s.

### When to use a source group / blend instead

A `data_aggregation` metric only **sums** one metric. Reach for a **source group** (rollup into one virtual source) or **blend** (join on a shared dimension) when you need:

- a cross-source **ratio** (blended ROAS / CPA) where numerator and denominator aggregate separately — build the group/blend, then a `data_formula` on top whose `A`/`B` reference the aggregated fields (on a source group as `universal_metric_*`, on a blend as `blend_metric_*`);
- a reusable virtual combined source that widgets, goals, and other blends can target directly;
- a join across sources on a shared dimension.

See `whatagraph-source-groups` and `whatagraph-blends`.

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

Returns three maps — `affected_widget_count`, `affected_report_count`, and `affected_filter_count` — each keyed by metric id (the `universal_metric_` prefix stripped), value = the count. Filters **are** counted, so this is the real blast radius before a modify/delete.

```
{
  "success": true,
  "affected_widget_count": { "511018": 4 },
  "affected_report_count": { "511018": 2 },
  "affected_filter_count": { "511018": 1 }
}
```

## Deleting custom metrics

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: permanent, batch-only (`metric_ids` array, all-or-nothing ID validation). A metric still used by widgets or filters is **blocked** — the call returns a conflict listing the affected widgets, reports, and filters. Remove those references first (`manage-widgets` / `manage-filters`), or re-run with `force=true` to delete anyway. Pre-check with `list-custom-metrics action=usage`.

## Using a custom metric in `fetch-data`

Once created, a custom metric has a new `external_id` of the form `universal_metric_<metric_id>` (e.g. `universal_metric_511018`) — visible in `list-sources action=list_dimensions_and_metrics` next to the platform-native metrics. Use that directly in `fetch-data`:

```
fetch-data source_id=<source_id>
  report_type="campaign"
  metrics=["universal_metric_511018"]
  dimensions=["universal_dimension_1137"]
  from="2026-04-01" till="2026-04-15"
```

To confirm which channels/sources a metric resolves on before fetching, check `resolves_on` from `list-custom-metrics action=show` (see "Listing" above) — it lists exactly where the metric's mapped fields land, and never a source group or blend unless the field was mapped there.

**Custom metrics on a source-group's virtual `integration_source_id` cannot be read via `fetch-data` on the group itself.** The platform aggregates sub-source data at the widget/export layer, not at the `fetch-data` boundary. To preview a custom metric on a source group, call `fetch-data` against each constituent source individually, or render the metric in a widget and read it via `list-widgets action=csv_export` / `export-report`. The error message returned by `fetch-data` on the group strips the `_metric_` infix, so the diagnostic looks like `Invalid metrics: universal_<id>` — that is *not* a hint that the legacy form would have worked; the metric simply does not resolve at the group level.

## What MCP can't do here

- Custom metrics use `data_formula` (calculations), `data_aggregation` (sum the same metric across sources), and `metadata` (alias / unified name). For a cross-source **ratio** (not a plain sum), use a source group or blend, then a `data_formula` on top (see above).
- `transformation_level=widget` — build widget-local formulas via `manage-widgets` instead.

## Common pitfalls

- **`formula="A/B*100"` with `formula_value_type="percent"`** — double-scales! `percent` already ×100 for display. Write `formula="A/B"` instead. A ThruPlay Rate of 7.09% would show as 708.9% with `*100`.
- **Using `{placeholder}` tokens in formulas** — wrong. Use `A/B` style identifiers only.
- **Passing metric display names as `field_external_id`** — field IDs come from `list-sources action=list_dimensions_and_metrics`, not display names.
- **Missing any of `accumulator`, `aggregation_level`, `formula_increase`, `formula_value_type` on a `data_formula` create** — all four are required.
- **`transformation_level=channel` with `integration_source_id` fields** — use `channel_id` at channel level; use `integration_source_id` at source level.
- **Reaching for a source group/blend just to sum one metric across sources** — a `data_aggregation` custom metric already does this: map the field per source, no virtual source needed. Save the group/blend for cross-source ratios, joins, or a reusable combined source.
- **Division by zero** → empty cell, not infinity.
- **Formula spaces** — `A / B` with spaces is rejected. Write `A/B`.
