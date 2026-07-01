---
name: whatagraph-blends
type: domain
description: Combine data from different channels (Google Ads + Meta + GA4) into one virtual source by joining on shared dimensions (date, campaign name, etc.). Use when a widget needs to show cross-channel rows side-by-side or a computed metric needs numerator/denominator from separate sources.
required_tools:
  - list-blends
  - list-sources
  - fetch-data
  - manage-blends
  - manage-custom-dimensions
  - manage-custom-metrics
  - manage-reports
  - manage-source-groups
  - manage-sources
  - manage-widgets
---

# Blends

Tools covered: `list-blends`, `manage-blends`.

A **blend** joins 2+ sources into a single virtual source. The blend has its own integration source id, so widgets and custom metrics can treat the blend like any other source.

## Use this when

- "Put Google Ads spend and Meta Ads spend in the same table grouped by date."
- "Compute Blended ROAS = GA4 revenue / (Google Ads spend + Meta Ads spend)." (Blend first, custom metric second.)
- "Cross-channel performance widget that groups by campaign theme across 3 platforms."

## Blend vs source group — quick decision

| Goal | Use |
|---|---|
| Sources are ALL the same channel (5 Google Ads accounts) → one virtual source | Source group (`manage-source-groups`) |
| Combine the same field across sources/channels into one total, no row-level join needed | Source group (cross-channel rollup) |
| Sources are DIFFERENT channels that must be JOINED on a shared dimension (campaign, date) for side-by-side rows | Blend |

## Listing

```
list-blends action=list                # paginated; supports search
list-blends action=show blend_id=<id>  # full sub-sources, joins, widgets_count
```

## Creating a blend

```
manage-blends action=create
   name="Google Ads + Meta Ads — Campaign Blend"
   description="Cross-channel campaign performance"
   currency="USD"
   items=[
     {
       "integration_source_id": <google_ads_source>,
       "report_type": "campaign",
       "dimensions": ["universal_dimension_1137", "campaign_name"],
       "metrics":    ["universal_metric_1", "universal_metric_3"]
     },
     {
       "integration_source_id": <meta_ads_source>,
       "dimensions": ["universal_dimension_1137", "campaign_name"],
       "metrics":    ["universal_metric_1", "universal_metric_3"]
     }
   ]
   joins=[
     {
       "type": "full",
       "conditions": [
         {
           "left_source_id":  <google_ads_source>,
           "left_dimension":  "universal_dimension_1137",
           "right_source_id": <meta_ads_source>,
           "right_dimension": "universal_dimension_1137"
         },
         {
           "left_source_id":  <google_ads_source>,
           "left_dimension":  "campaign_name",
           "right_source_id": <meta_ads_source>,
           "right_dimension": "campaign_name"
         }
       ]
     }
   ]
```

### `items` — each sub-source

- `integration_source_id` — id from `list-sources action=list`.
- `report_type` — the source's report type external id. Auto-resolved when source has exactly one report type; required when multiple exist. **Omit entirely** when the source has zero report types (e.g. Facebook Ads, GA4) — run `list-sources action=list_report_types` to check.
- `dimensions` — array of dimension external ids.
- `metrics` — array of metric external ids.

### `joins` — how sub-sources connect

- `type`: `left`, `inner`, `full`, or `cross`.
- `conditions`: list of `{left_source_id, left_dimension, right_source_id, right_dimension}` pairs.

All conditions in one join are ANDed together. For more complex joins, add multiple join objects.

## Join type — the most important blend decision

| `type` | Behavior | When to use |
|---|---|---|
| `full` | Every row from both sides is kept; missing dimension pairs appear as nulls | Default; safest for "show everything" |
| `inner` | Only rows present in both sides | When you want ONLY campaigns that ran on both channels |
| `left` | All rows from left + matching from right | When the left source is the "primary" view |
| `cross` | Cartesian product | Rare; use only when you know why |

Most blends should use `full` — it avoids excluding rows that only exist in one source. `inner` is a common source of "my data disappeared after blending" questions.

## Updating

```
manage-blends action=update blend_id=<id>
   items=[...]  joins=[...]
```

Replace-style — full `items` and `joins` lists replace previous values.

## Duplicating

```
manage-blends action=duplicate blend_id=<id>
```

Useful for blend variants ("Inner version of the full blend" to compare).

## Unified dimensions and metrics across sub-sources

A blend is only useful when the sub-sources expose equivalent dimensions and metrics that can be joined and aggregated. In practice that means:

- **Dimensions**: pick the same set of universal dimensions on every sub-source (e.g. `universal_dimension_1137` = Date on every channel, plus a shared key like campaign name or channel name).
- **Metrics**: pick the same set of universal metrics on every sub-source (e.g. `universal_metric_1` = Impressions, `universal_metric_2` = Clicks, `universal_metric_3` = Spend). The blend then exposes one aggregated metric per universal slot across the whole blend.
- **Types and summability**: the joined metrics must be the same data type (integer/float/currency) and summable — counts, impressions, clicks, spend. Average or ratio metrics should not be blended directly; blend the numerator and denominator separately, then build a custom `data_formula` metric on top of the blend.

## Using the blend in widgets

A blend is a virtual source with its own `integration_source_id` (the `id` returned by `list-blends`). Attach it to the report first, then create the widget against the returned report-local `source_id`:

```
manage-reports action=attach_source report_id=<id>
   integration_source_id=<blend_id>
# response.source_id is the report-local id

manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id=<blend_channel_id>
   source_id=<that report-local id>
   widget_type_id=<...>
```

When picking metrics/dimensions on the widget, use the blend-level ids returned by `list-sources action=list_dimensions_and_metrics source_id=<blend_id>`:

- **Aggregated universal fields** — `aggregation_metric_universal_metric_<id>` and `aggregation_dimension_universal_dimension_<id>` — one row per unified field across all sub-sources.
- **Aggregated native fields** — when the same channel-native (non-universal) metric is present on multiple sub-sources, the blend also exposes `aggregation_metric_blend_metric_<id>`, and a join-key dimension chained across sub-sources is exposed as `aggregation_dimension_join_key_<id>`. These are the aggregated read forms for native fields that have no universal slot — use them like the `aggregation_*_universal_*` forms.
- **Per-sub-source fields** — `blend_metric_<id>` and `blend_dimension_<id>` — keep each sub-source's metric distinct (useful when you want `Google Spend` and `Meta Spend` as separate columns).

## Field-id families on a blend — which form goes where

`list-sources action=list_dimensions_and_metrics source_id=<blend_id>` returns three concurrent field families. They are not interchangeable; pick the right one for the call you're making.

| Field id family | `manage-custom-metrics create` | `manage-custom-dimensions create` | `fetch-data` on the blend | UI widget picker |
|---|---|---|---|---|
| `universal_metric_<n>` / `universal_dimension_<n>` (cross-channel canonical) | ✓ (as `data_formula` fields) | ✓ (`map_type=data`) | ✗ | (resolves on sub-source, not blend) |
| `aggregation_metric_universal_metric_<n>` / `aggregation_dimension_universal_dimension_<n>` (aggregated unified output; native-field equivalents `aggregation_metric_blend_metric_<n>` / `aggregation_dimension_join_key_<n>` behave the same) | ✗ | ✗ | ✓ | ✓ aggregated |
| `blend_metric_<n>` / `blend_dimension_<n>` (per-sub-source) | ✓ (as `data_formula` fields) | ✗ | ✗ | ✓ per-sub-source |

Rule of thumb: use `universal_*` to **build** custom fields, `aggregation_*` to **read** the unified output, and `blend_*` to **build** custom fields keyed off one specific sub-source.

## Reading blend data directly

Call `fetch-data` with the blend's integration source id and the aggregation field ids:

```
fetch-data
   source_id=<blend_id>
   dimensions=["aggregation_dimension_universal_dimension_1137"]
   metrics=["aggregation_metric_universal_metric_1",
            "aggregation_metric_universal_metric_2",
            "aggregation_metric_universal_metric_3"]
   from="2025-10-01" till="2025-10-31"
```

One row per date (or per join-key value) with the unified metrics summed across sub-sources.

To preview per-sub-source values, call `fetch-data` on each sub-source's integration source id individually with its own native or universal field ids.

## Reading data right after creating a blend

A blend stores nothing — it is computed live on every `fetch-data`, by fetching each sub-source and joining the results in-request. So a blend's data is **available immediately after create**; there is no blend warmup or pre-computation to wait for.

The first fetch can still come back with `Your data is being processed... please wait...` (or `Retry in N seconds`). That is **not** the blend warming up — it means an **underlying sub-source** isn't ready yet: a direct-fetch integration still pulling from the third-party API, a rate limit, or the provider hasn't aggregated the requested period yet.

- **Treat it as transient.** Wait and re-run the **same** call. `retryable: false` on that specific message is misleading — the condition is retryable. When the error gives `Retry in N seconds`, honor that N (it comes from the source).
- **If a sub-source stays not-ready, investigate that source — not the blend.** Fetch the sub-source directly (its own `integration_source_id`) to see its state.
- **Zeros are not "broken".** A sub-source may legitimately have no data for the period. Confirm by fetching that sub-source directly for the same dates.

> **Verify the build.** After building or bulk-swapping, `export-report report_id=<id>` (or `list-widgets action=csv_export` per widget) and confirm every widget's `data_status` is `ready` with non-empty rows and expected metric names. `list-widgets action=show` is NOT sufficient — it echoes ids, not loaded data.

## Deleting a blend

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: no usage guard in the tool, widgets referencing the blend break, pre-check `list-blends action=show blend_id=<id>` → `widgets_count`.

## Common pitfalls

- **Picking the wrong field id family when reading** — use `aggregation_metric_*`/`aggregation_dimension_*` to read the blend's unified output, not the sub-source native ids (those won't resolve on the blend itself).
- **Picking the wrong field id family when writing custom fields on a blend** — a `data_formula` custom metric on a blend takes `universal_metric_<n>` (unified slot) or `blend_metric_<n>` (per-sub-source) ids as its `A`/`B` fields (from `list-sources action=list_dimensions_and_metrics`). `manage-custom-dimensions action=create map_type=data` expects the `universal_dimension_<n>` form on a blend, not `aggregation_dimension_*` / `blend_dimension_*`.
- **`join_type` vs `type`** — use `type` inside each join object.
- **`join_fields` vs `conditions`** — use `conditions` with `{left_source_id, left_dimension, right_source_id, right_dimension}` per pair.
- **`inner` join excluding data** — most "where did my data go?" blend issues are caused by `inner` on a dimension that doesn't match across sources (e.g. Google campaign name "Brand_US" vs Meta "Brand - US"). Use `full` unless you specifically want intersection.
- **Joining on non-shared dimension names** — if dimensions have different external ids per channel (e.g. `campaign_name` vs `campaign`), create a `metadata` custom dimension alias first so the external ids match, then join on the aliased field.
- **Including the same metric in multiple sub-sources** — the metric appears twice in widget field pickers (e.g. "Spend (Google)" and "Spend (Meta)"); read the blend's auto-aggregated `aggregation_metric_*` field for the single combined "Spend" — the blend already sums it across sub-sources, so no extra custom metric is needed.
- **Blend without date dimension in join** — rows from different periods get cartesian-joined. Always include a date dimension in your join conditions.
- **Currency mismatch across sub-sources** — the blend's `currency` field is cosmetic; actual values are as-stored. Normalize source-level currencies via `manage-sources action=set_currency` first.
