---
name: whatagraph-blends
type: domain
group: data_modeling
description: Combine data from different channels (Google Ads + Meta + GA4) into one virtual source by joining on shared dimensions (date, campaign name, etc.). Use when a widget needs to show cross-channel rows side-by-side or a computed metric needs numerator/denominator from separate sources.
required_tools:
  - list-blends
  - list-filters
  - list-sources
  - fetch-data
  - manage-blends
optional_tools:
  - tool_name: manage-custom-metrics
    purpose: Build a data_formula metric (e.g. Blended ROAS) on top of the blend.
  - tool_name: manage-custom-dimensions
    purpose: Add a custom dimension / alias on the blend to align join keys.
  - tool_name: manage-sources
    purpose: Normalise source currency / create a dimension alias before joining.
  - tool_name: manage-source-groups
    purpose: Decision-table alternative — a source group when no row-level join is needed.
  - tool_name: manage-reports
    purpose: Attach the blend's virtual source to a report before charting it.
  - tool_name: manage-widgets
    purpose: Render the blend in a widget once it is attached to a report.
  - tool_name: export-report
    purpose: Verify the built widgets show ready, non-empty data.
  - tool_name: list-widgets
    purpose: csv_export a widget to verify the blend renders correctly.
  - tool_name: manage-filters
    purpose: Attach or adjust a filter on a widget rendering the blend.
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
list-blends action=list                # paginated; includes source_count, channel_names per blend
list-blends action=show blend_id=<id>  # full sub-sources, joins, widgets_count, per-sub-source filter
```

Only `show` reports each sub-source's `filter`. `list` does not, so never conclude a blend is unfiltered from a `list` response.

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
- `filter_id` — optional. Narrows THIS sub-source's rows before the join runs. See "Filtering one sub-source" below.

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

## Filtering one sub-source

A sub-source can carry its own filter. That filter runs on that channel's rows **before** the join.

This is not the same as filtering the blend's output, and the two give different answers. Filter Google Search Console to one set of pages before a full outer join and you keep every row from the other sources; filter the joined output instead and you drop the other sources' unmatched rows too. When the user asks to narrow one channel inside a blend, filter that sub-source.

Each sub-source holds **at most one** filter. Attaching a new one replaces the old.

### Three ways to set it

**1. While creating or updating the blend** — `items[].filter_id`, pointing at a team-level filter from `list-filters action=list`:

```
manage-blends action=create
   name="MCP articles source"
   items=[
     { "integration_source_id": <bigquery_source>, "dimensions": [...], "metrics": [...] },
     { "integration_source_id": <gsc_source>, "dimensions": [...], "metrics": [...],
       "filter_id": <mcp_articles_filter_id> }
   ]
   joins=[...]
```

A **copy** of the filter is attached, so the team-level original stays reusable and unchanged.

**2. Directly on an existing sub-source** — `manage-filters action=create` with `blend_sub_source_id`:

```
manage-filters action=create
   channel_id=<the sub-source's channel>
   blend_sub_source_id=<sub_sources[].id from list-blends action=show>
   dimension="page" dimension_operator="contain_dimension" value="/mcp/"
```

**3. Copying an existing team filter onto a sub-source** — `manage-filters action=attach`:

```
manage-filters action=attach filter_id=<team_filter_id> blend_sub_source_id=<sub_source_id>
```

`blend_sub_source_id` is the `sub_sources[].id` from `list-blends action=show` — NOT the `integration_source_id`, and not a report-local `source_id`.

### Reading it back

`list-blends action=show blend_id=<id>` returns a `filter` on every `sub_sources[]` entry — `null` when none, otherwise `{id, name, version, options}`. Read this before changing a blend so you don't silently drop a filter a user set in the UI.

### Keeping, replacing, and removing on update

`manage-blends action=update` is replace-style for `items`, but filters are the exception:

| You send | Result |
|---|---|
| No `filter_id` on the item | Existing filter is **kept** |
| `filter_id: <id>` | Existing filter is replaced by a copy of that filter |
| `filter_id: 0` | Existing filter is **removed** |

`filter_id` accepts a team-level filter id or the id `list-blends action=show` reported for that sub-source, so a read round-trips straight back into an update.

### Editing an attached filter

You cannot. `manage-filters action=add` and `action=update` only reach team-level filters, so a filter already sitting on a sub-source is read-only. To change its conditions, build the filter you want at team level and re-attach it (way 1 or 3 above), which replaces the old one.

### Match the channel

The filter must belong to the **sub-source's own channel**. A filter built for another channel matches no rows, so all three routes reject a mismatch up front — you will not get a silently dead filter.

Confirm the channel from `list-blends action=show` → `sub_sources[].channel_name`, then pass that `channel_id` on create or pick a filter from `list-filters action=list channel_id=<that channel>`.

## Duplicating

```
manage-blends action=duplicate blend_id=<id>
```

Useful for blend variants ("Inner version of the full blend" to compare). Sub-source filters are copied too, so the duplicate is filtered the same way as the original.

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
| `universal_metric_<n>` / `universal_dimension_<n>` (cross-channel canonical) | ✗ metric — **rejected on channel 142** (see below) | ✓ dimension (`map_type=data`, preferred) | ✗ | (resolves on sub-source, not blend) |
| `aggregation_metric_universal_metric_<n>` / `aggregation_dimension_universal_dimension_<n>` (aggregated unified output; native-field equivalents `aggregation_metric_blend_metric_<n>` / `aggregation_dimension_join_key_<n>` behave the same) | ✗ metric (see below) | ✓ dimension (prefix stripped, re-resolved) | ✓ | ✓ aggregated |
| `blend_metric_<n>` / `blend_dimension_<n>` (per-sub-source) | ✓ metric **use this** (as `data_formula` fields) | ✓ dimension (own resolver) | ✗ | ✓ per-sub-source |

Rule of thumb: build a `data_formula` custom **metric** on a blend off `blend_metric_<n>` ids (the other metric families are rejected on channel 142); a `map_type=data` custom **dimension** accepts any of the three families — prefer `universal_dimension_<n>`; `aggregation_*` is for **reading** the unified output via `fetch-data`.

### Custom fields on a blend — which field-id family the `fields` array accepts

**Custom metric** (`map_type=data_formula`) — reference `blend_metric_<n>` field ids, each with the blend's `integration_source_id`. `universal_metric_<n>` (and its `aggregation_metric_universal_metric_<n>` read form) are **rejected**: `manage-custom-metrics create` checks that each id resolves in the blend's field catalog, and a blend catalog only exposes `blend_metric_*` / `aggregation_metric_*` — never a bare `universal_metric_<n>`. The error is:

> `Universal metric 'universal_metric_<id>' does not resolve on channel 142 — it is not available there, so a custom metric mapping it to this channel would fail at fetch time.`

(The check is skipped when the blend catalog is cold/empty, so a `universal_*` create may occasionally slip through and then fail at fetch time — another reason to always use `blend_metric_*`.)

**Custom dimension** (`map_type=data`) — the `fields` array accepts **any** family the blend catalog returns: `universal_dimension_<n>`, `blend_dimension_<n>`, or `aggregation_dimension_<n>` (the `aggregation_dimension_` prefix is stripped and re-resolved to the underlying id). Unlike metrics, dimensions have **no** channel-142 catalog gate — none of these forms are rejected on create. Prefer `universal_dimension_<n>` when the field has a unified slot.

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

**A `map_type=data_aggregation` custom metric on a blend is single-column, not cross-channel.** It can only reference `blend_metric_<n>` ids, and each `blend_metric_<n>` is scoped to ONE sub-source's column (e.g. `blend_metric_957` = Facebook Spend only). So a `data_aggregation` metric over a single `blend_metric_<n>` CANNOT produce a cross-channel SUM. For the true cross-channel total, do NOT build a custom metric — READ the auto-exposed `aggregation_metric_universal_metric_<n>` field via `fetch-data` (the blend already sums it across sub-sources). Reserve custom `data_formula` metrics for cross-sub-source ratios (e.g. Blended ROAS above).

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

## What MCP cannot do here

Know these before you promise a user a result. If one blocks you, say so — do not hand back manual UI instructions as if the tool had no opinion.

- **Edit a filter that is already on a sub-source.** `manage-filters action=add` / `action=update` only reach team-level filters. Build a replacement at team level and re-attach it.
- **Put more than one filter on a sub-source.** One filter per sub-source; attaching replaces. Express multiple conditions as rows inside a single filter (`manage-filters action=add`, before attaching).
- **See sub-source filters from `list-blends action=list`.** Only `action=show` returns them.
- **Reach a blend sub-source with `source_id`.** `source_id` on `manage-filters` means a report-local source. Blend sub-sources need `blend_sub_source_id`.
- **Use a filter from a different channel.** All three routes reject it.

## Common pitfalls

- **Picking the wrong field id family when reading** — use `aggregation_metric_*`/`aggregation_dimension_*` to read the blend's unified output, not the sub-source native ids (those won't resolve on the blend itself).
- **Picking the wrong field id family when writing custom fields on a blend** — a `data_formula` custom metric on a blend takes `blend_metric_<n>` (per-sub-source) ids as its `A`/`B` fields (from `list-sources action=list_dimensions_and_metrics`), each with the blend's `integration_source_id`; `universal_metric_<n>` is **rejected on channel 142** (see "Custom fields on a blend" above). A `manage-custom-dimensions action=create map_type=data` custom dimension is the opposite — it accepts `universal_dimension_<n>`, `blend_dimension_<n>`, or `aggregation_dimension_<n>` on a blend (prefer `universal_dimension_<n>`); none are rejected.
- **Filtering the blend output when the user meant one channel** — a filter on the widget or on the report-local blend source runs AFTER the join, so on a `full` join it also drops the other sources' unmatched rows. To narrow one channel, filter that sub-source instead (see "Filtering one sub-source").
- **Dropping a UI-set sub-source filter on update** — `list-blends action=show` first and check `sub_sources[].filter`. Leaving `filter_id` off an item keeps the filter, but sending a different `filter_id` silently replaces it.
- **`join_type` vs `type`** — use `type` inside each join object.
- **`join_fields` vs `conditions`** — use `conditions` with `{left_source_id, left_dimension, right_source_id, right_dimension}` per pair.
- **`inner` join excluding data** — most "where did my data go?" blend issues are caused by `inner` on a dimension that doesn't match across sources (e.g. Google campaign name "Brand_US" vs Meta "Brand - US"). Use `full` unless you specifically want intersection.
- **Joining on non-shared dimension names** — if dimensions have different external ids per channel (e.g. `campaign_name` vs `campaign`), create a `metadata` custom dimension alias first so the external ids match, then join on the aliased field.
- **Including the same metric in multiple sub-sources** — the metric appears twice in widget field pickers (e.g. "Spend (Google)" and "Spend (Meta)"); read the blend's auto-aggregated `aggregation_metric_*` field for the single combined "Spend" — the blend already sums it across sub-sources, so no extra custom metric is needed.
- **Blend without date dimension in join** — rows from different periods get cartesian-joined. Always include a date dimension in your join conditions.
- **Currency mismatch across sub-sources** — the blend's `currency` field is cosmetic; actual values are as-stored. Normalize source-level currencies via `manage-sources action=set_currency` first.
