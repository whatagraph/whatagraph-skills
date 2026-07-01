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

## Write-time validation

`manage-blends` validates join topology when you `create` or `update` (not just at fetch time). A blend that breaks these rules is rejected up front with a specific message. Below is each rule, the error you get, and the fix.

### Allowed topologies

| Topology | OK? | Format to use |
|---|---|---|
| 2 distinct sources, 1 join | ✓ | `conditions` (simplified) |
| 3+ distinct sources, chained | ✓ | one join object per adjacent pair: `joins=[{A–B},{B–C}]` |
| Self-join (same source twice) | ✓ | `groups/keys` only (see below) |
| One join spanning 3+ sources | ✗ | split into one join per pair |
| A sub-source with no join | ✗ | must connect into the chain (unless a `cross` join is present) |

### Shape minimums

`create` requires at least **2 items** and at least **1 join**. Each `groups/keys` group needs at least **2 keys** (one per side).

### Self-join requires `groups/keys` (not `conditions`)

A self-join uses the **same `integration_source_id` in two different items** (e.g. one source compared this-month vs last-month). The simplified `conditions` format keys a join by source id alone, so with the source repeated it can't tell which item you mean. The `groups/keys` format carries `col_index` (the 0-based position in `items`), which disambiguates.

- **Error (using `conditions` with a duplicated source):** *"Multiple items reference the same `integration_source_id`. The simplified `conditions` format cannot disambiguate which item to join. Use the legacy `groups/keys` format with explicit `col_index` instead."*
- **Fix — use `groups/keys`:**

```
joins=[
  {
    "type": "inner",
    "groups": [
      { "keys": [
        { "col_index": 0, "integration_source_id": <S>, "external_id": "<dim>" },
        { "col_index": 1, "integration_source_id": <S>, "external_id": "<dim>" }
      ] }
    ]
  }
]
```

`col_index` 0 and 1 point at the first and second item that both carry source `<S>`.

### One join connects exactly one pair of sources

Each join relates **two different** sub-sources. A single join cannot span three or more.

- **Error (a join condition touches the same source on both sides or only one source):** *"Each join condition must connect exactly two different sub-sources..."*
- **Error (one join spans 3+ sources):** *"A single join can only relate one pair of sub-sources, but join N spans more than two — this blend would be saved but every data fetch would fail with 'Incorrect blend setup'."*
- **Fix:** one join object per pair. To chain A–B–C: `joins=[{A–B join},{B–C join}]`.

### Every sub-source must be connected

All sub-sources must link (directly or transitively) into one chain.

- **Error:** *"Sub-source X is not connected to the rest of the blend by any join. Every sub-source must be linked into a single chain — add a join condition relating it to an already-connected sub-source."*
- **Fix:** add a join tying the orphaned source to one already in the chain. Exception: a `cross` join in the blend skips this connectivity check.

### Date dimensions join only to date dimensions

A temporal dimension (date, datetime, month, week, …) cannot be matched against a non-temporal one.

- **Error:** *"Join N matches incompatible dimension types: `<dim>` (date) on source A cannot be joined to `<dim>` (string) on source B. A date/time dimension must be joined to another date/time dimension."*
- **Fix:** join date→date and the other key (campaign name, etc.) separately. Keys whose type can't be resolved are skipped, not rejected. (Note: this check currently runs on `create` only.)

### Join keys must be declared dimensions

Every dimension named in a join must also appear in that sub-source's `dimensions` array.

- **Error:** *"Join condition references dimension `D` which is not declared in the `dimensions` of source ID S..."*
- **Fix:** add the join-key dimension to that item's `dimensions`.

### Non-cross joins need `conditions` or `groups`

Only a `cross` join may omit the join definition.

- **Error:** *"Join of type `X` requires `conditions` or `groups` to define how sources are connected..."*
- **Fix:** add `conditions` (or `groups`), or switch the type to `cross` if a cartesian product is what you want.

### Source must be in `items`

- **Error:** *"Join references source ID S which is not in the items list."*
- **Fix:** the `left_source_id`/`right_source_id` (or a key's `integration_source_id`) must be one of the `items` integration source ids.

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
| `universal_metric_<n>` / `universal_dimension_<n>` (cross-channel canonical) | ✗ for metrics — **rejected on channel 142** (see below) | ✓ (`map_type=data`) | ✗ | (resolves on sub-source, not blend) |
| `aggregation_metric_universal_metric_<n>` / `aggregation_dimension_universal_dimension_<n>` (aggregated unified output; native-field equivalents `aggregation_metric_blend_metric_<n>` / `aggregation_dimension_join_key_<n>` behave the same) | ✗ (see below) | ✗ | ✓ | ✓ aggregated |
| `blend_metric_<n>` / `blend_dimension_<n>` (per-sub-source) | ✓ **use this** (as `data_formula` fields) | ✗ | ✗ | ✓ per-sub-source |

Rule of thumb: build a `data_formula` custom **metric** on a blend off `blend_metric_<n>` ids; `aggregation_*` is for **reading** the unified output; `universal_dimension_*` is what a `map_type=data` custom **dimension** builds off.

### Custom metric on a blend — use `blend_metric_*`, not `universal_metric_*`

A `data_formula` custom metric on a blend (channel 142) must reference `blend_metric_<n>` field ids, each with the blend's `integration_source_id`. `universal_metric_<n>` (and its `aggregation_metric_universal_metric_<n>` read form) are **rejected**: `manage-custom-metrics create` checks that each id resolves in the blend's field catalog, and a blend catalog only exposes `blend_metric_*` / `aggregation_metric_*` — never a bare `universal_metric_*`. The error is:

> `Universal metric 'universal_metric_<id>' does not resolve on channel 142 — it is not available there, so a custom metric mapping it to this channel would fail at fetch time.`

(The check is skipped when the blend catalog is cold/empty, so a `universal_*` create may occasionally slip through and then fail at fetch time — another reason to always use `blend_metric_*`.)

```
manage-custom-metrics action=create
   name="Blended ROAS"
   map_type="data_formula"
   transformation_level="source"
   fields=[
     {"integration_source_id": <blend_source_id>, "field_external_id": "blend_metric_<revenue_id>", "identifier": "A"},
     {"integration_source_id": <blend_source_id>, "field_external_id": "blend_metric_<spend_id>",   "identifier": "B"}
   ]
   formula="A/B"
   formula_value_type="float"
   accumulator="average"
   summary_accumulator="average"
   aggregation_level="aggregate"
   formula_increase="positive"
```

Get the `blend_metric_<n>` ids from `list-sources action=list_dimensions_and_metrics source_id=<blend_id>`. `blend_metric_*` fields require `integration_source_id` (the blend's source) — not `channel_id`.

## Decoding `blend_metric_<n>` / `blend_dimension_<n>` — which channel a field belongs to

`list_dimensions_and_metrics` returns these ids but **not** the channel they came from — the `name` is the bare field name, so two sub-sources both exposing "Spend" come back as two `blend_metric_<n>` entries named "Spend" with no channel hint. Don't guess by name.

To decode, call `list-blends action=show blend_id=<id>`. Each `sub_sources[]` entry is one channel and carries `integration` (the channel), `source_name`, and `integration_source_id`; its `metrics[]` and `dimensions[]` each carry a numeric `id`. **The `<n>` in `blend_metric_<n>` equals that `metrics[].id`** (and `blend_dimension_<n>` equals a `dimensions[].id`).

So `blend_metric_42` belongs to whichever `sub_sources[]` entry has a metric with `id == 42` — read that entry's `integration` / `source_name` to name the channel. (The `external_id` shown there is the channel-native id like `cost_micros`, not the `blend_metric_*` form — match on `id`, not `external_id`.)

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
- **Picking the wrong field id family when writing custom fields on a blend** — a `data_formula` custom metric on a blend takes `blend_metric_<n>` (per-sub-source) ids as its `A`/`B` fields (from `list-sources action=list_dimensions_and_metrics`), each with the blend's `integration_source_id`. `universal_metric_<n>` is **rejected on channel 142** (see "Custom metric on a blend" above). `manage-custom-dimensions action=create map_type=data` expects the `universal_dimension_<n>` form on a blend, not `aggregation_dimension_*` / `blend_dimension_*`.
- **`join_type` vs `type`** — use `type` inside each join object.
- **`join_fields` vs `conditions`** — use `conditions` with `{left_source_id, left_dimension, right_source_id, right_dimension}` per pair.
- **`inner` join excluding data** — most "where did my data go?" blend issues are caused by `inner` on a dimension that doesn't match across sources (e.g. Google campaign name "Brand_US" vs Meta "Brand - US"). Use `full` unless you specifically want intersection.
- **Joining on non-shared dimension names** — if dimensions have different external ids per channel (e.g. `campaign_name` vs `campaign`), create a `metadata` custom dimension alias first so the external ids match, then join on the aliased field.
- **Including the same metric in multiple sub-sources** — the metric appears twice in widget field pickers (e.g. "Spend (Google)" and "Spend (Meta)"); read the blend's auto-aggregated `aggregation_metric_*` field for the single combined "Spend" — the blend already sums it across sub-sources, so no extra custom metric is needed.
- **Blend without date dimension in join** — rows from different periods get cartesian-joined. Always include a date dimension in your join conditions.
- **Currency mismatch across sub-sources** — the blend's `currency` field is cosmetic; actual values are as-stored. Normalize source-level currencies via `manage-sources action=set_currency` first.
