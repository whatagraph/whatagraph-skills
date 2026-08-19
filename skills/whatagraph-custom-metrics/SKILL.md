---
name: whatagraph-custom-metrics
type: domain
group: data_modeling
description: Create calculated or unified metrics on top of a data source — formulas (ROAS, CPA, CPL) and metric aliases / unified names. Use when a standard channel metric isn't enough. Anything that combines several sources — a total or a ratio across them — needs a source group or blend underneath first (see whatagraph-source-groups / whatagraph-blends).
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

**Not this:** anything that has to combine **multiple sources** — whether a plain total ("Total Spend" across Google + Meta + LinkedIn) or a ratio (blended ROAS/CPA) whose numerator and denominator come from different sources. A custom metric only ever reads fields on the source it is mapped to; it cannot add up or divide across independently-aggregated sources. Build a **source group** (rollup) or **blend** (join) first, then put a `data_formula` on top of that combined source. See `whatagraph-source-groups` and `whatagraph-blends`.

## Two metric types — pick the right one

| `map_type` | What it does | Example |
|---|---|---|
| `data_formula` | Formula with field identifiers A, B, C… | `A/B` for ROAS |
| `metadata` | 1:1 mapping — alias / unified name for an existing field | Rename "Spend" to "Ad Cost"; unify "Cost" (Google) and "Amount spent" (Meta) under one name |

Both map types are scoped to the source they are mapped on. For a **combined** number across sources — a total, a cross-source **ratio**, a reusable virtual combined source, or a join on a shared dimension — build a **source group** (rollup) or **blend** (join) first. See `whatagraph-source-groups` and `whatagraph-blends`.

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
- `map_type` — map type, enum: `metadata`, `data`, `data_formula`, `currency_exchange`, `tag`, `system`, `ai`. **`list_with_premades` only.**
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
| `accumulator` | `sum`, `average`, `last`, `first` | How values roll up within one entity over time. Only shapes widget totals when `aggregation_level=row` — with `aggregate`, totals are recomputed from summed parent fields and this setting is silently inert (see "Aggregation level" below) |
| `summary_accumulator` | `sum`, `average`, `last`, `first` | How to combine values across entities in summary/totals rows (e.g. `last` budget per campaign, then `sum` across campaigns). Optional, defaults to `accumulator` value. Only applies when `aggregation_level=row` and the widget carries an aggregation-key dimension |
| `aggregation_level` | `aggregate`, `row` | `aggregate` = apply formula on already-summed totals (right for ratios like ROAS/CPA); `row` = apply per row first, then accumulate — **required** for `accumulator`/`summary_accumulator` to shape totals of non-additive values |
| `formula_increase` | `positive`, `negative` | `positive` = higher is better (revenue, CTR); `negative` = lower is better (CPA, CPL) |

`formula_value_type`, `accumulator`, `aggregation_level`, and `formula_increase` must be set. If any is missing, the tool returns an error that names the missing parameter. `summary_accumulator` is optional but recommended for ratio metrics.

### Recommended settings per metric class

| Metric class | Example | `formula_value_type` | `accumulator` | `summary_accumulator` | `aggregation_level` | `formula_increase` |
|---|---|---|---|---|---|---|
| Rate / percentage | CTR, ACoS, conversion rate | `percent` | `average` | `average` | `aggregate` | `positive` |
| Cost-per-action | CPA, CPL, CPM | `currency` | `average` | `average` | `aggregate` | `negative` |
| Return ratio | ROAS | `float` | `average` | `average` | `aggregate` | `positive` |
| Summable total | Total spend, total clicks | `currency` / `int` | `sum` | `sum` | `row` | varies |
| Non-additive value | Budget, target, balance | `currency` / `int` | `last` | `sum` | `row` | varies |

### Aggregation level — `aggregate` vs `row` (critical for non-additive metrics)

`aggregation_level` controls **when** the formula is evaluated relative to row aggregation, and it determines whether `accumulator`/`summary_accumulator` actually affect widget totals.

| `aggregation_level` | How it works | When to use |
|---|---|---|
| `aggregate` | Parent fields (A, B) are **summed first**, then the formula runs on the totals. `accumulator`/`summary_accumulator` are **silently inert** — totals are always recomputed from summed fields. | Ratios where the total should be formula(sum(A), sum(B)) — e.g. CPC = total_spend / total_clicks. Most ratio metrics (CPC, CTR, ROAS, CPA) belong here. |
| `row` | Formula runs **per row first**, then `accumulator` rolls up within each entity and `summary_accumulator` combines across entities in the totals row. | Non-additive values (budgets, targets, balances) where you need `last`/`first` to pick one value per entity, then `sum`/`average` across entities. Also needed for any metric where summing per-row formula results is the desired behavior. |

**The trap:** setting `accumulator=last` with `aggregation_level=aggregate` looks correct but the `last` setting is silently ignored — totals still sum the parent fields and recompute. A "LAST budget" metric configured this way produces SUM-inflated totals (e.g. 157,500 instead of 9,500).

**Aggregation-key dimensions:** for `row`-level metrics to group correctly in widget totals, the widget needs an aggregation-key dimension — a dimension flagged `is_aggregation_key`, a widget-level `aggregation_key_overrides` config option, or a blend join key. Without one, per-row accumulation has no entity boundary to group by. Set the aggregation key via `manage-widgets` config `options.aggregation_key_overrides`:

```
options.aggregation_key_overrides: [{"external_id": "<dimension>", "is_aggregation_key": true}]
```

This marks a bound dimension (e.g. campaign) as the entity key. The metric's `accumulator` then aggregates within each entity (e.g. `last` budget per campaign) and `summary_accumulator` combines across entities (e.g. `sum` of last-budgets) in the summary row.

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

## Totalling one metric across several sources

There is **no custom-metric map type that sums a field across sources.** A custom metric is scoped to the source it is mapped on, so it can never add up sources for you. Build the combined source first, then read or calculate on top of it:

- **Source group** (rollup) — combines the sources into one virtual source; its `universal_metric_*` fields are already the cross-source totals. Best choice for a plain "Total Spend across accounts".
- **Blend** (join on a shared dimension) — the cross-sub-source total is auto-exposed as `aggregation_metric_universal_metric_<n>`; read it via `fetch-data`, don't rebuild it.

Then add a `data_formula` metric on top when you need a **ratio** of those totals (blended ROAS / CPA), with `A`/`B` referencing the aggregated fields — `universal_metric_*` on a source group, `blend_metric_*` on a blend.

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

- Custom metrics use `data_formula` (calculations) and `metadata` (alias / unified name) only. Nothing here combines sources — for a cross-source **total or ratio**, build a source group or blend, then read its aggregated field or put a `data_formula` on top (see above).
- `transformation_level=widget` — build widget-local formulas via `manage-widgets` instead.

## Common pitfalls

- **`accumulator=last` (or `first`) with `aggregation_level=aggregate`** — the accumulator is silently inert. Totals are recomputed from summed parent fields regardless, so a "LAST budget" metric still SUM-inflates. Use `aggregation_level=row` for non-additive values, and set an aggregation-key dimension on the widget.
- **`formula="A/B*100"` with `formula_value_type="percent"`** — double-scales! `percent` already ×100 for display. Write `formula="A/B"` instead. A ThruPlay Rate of 7.09% would show as 708.9% with `*100`.
- **Using `{placeholder}` tokens in formulas** — wrong. Use `A/B` style identifiers only.
- **Passing metric display names as `field_external_id`** — field IDs come from `list-sources action=list_dimensions_and_metrics`, not display names.
- **Missing any of `accumulator`, `aggregation_level`, `formula_increase`, `formula_value_type` on a `data_formula` create** — all four are required.
- **`transformation_level=channel` with `integration_source_id` fields** — use `channel_id` at channel level; use `integration_source_id` at source level.
- **Trying to total a metric across sources with a custom metric** — no map type does this. Build a source group (or blend) and read its aggregated field instead.
- **Division by zero** → empty cell, not infinity.
- **Formula spaces** — `A / B` with spaces is rejected. Write `A/B`.
