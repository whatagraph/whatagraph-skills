---
name: cross-channel-analytics
type: workflow
description: >-
  Analyze marketing performance across multiple channels using Whatagraph blends,
  source groups, and custom metrics/dimensions. Use when the user wants to
  compare channels, see unified cross-platform metrics, understand blended data,
  asks "how do all my channels compare?", "what's my total spend across
  platforms?", or needs help with cross-channel attribution and reporting.
required_tools:
  - list-blends
  - list-custom-dimensions
  - list-custom-metrics
  - list-source-groups
  - list-sources
  - fetch-data
---

# Cross-Channel Analytics

Help users analyze marketing performance across multiple channels by leveraging Whatagraph's blends, source groups, and custom fields. Cross-channel analytics is one of Whatagraph's core strengths — combining data from Google Ads, Meta, LinkedIn, GA4, and other platforms into unified views.

## Key Concepts

- **Blends** combine data from multiple sources into a single virtual source by mapping metrics across platforms (e.g., "Spend" from Google Ads + "Spend" from Facebook Ads). Use `list-blends` to explore them.
- **Source groups** aggregate multiple sources of the same integration type into one unified source (e.g., 10 Google Ads accounts rolled into one). Use `list-source-groups` to explore them.
- **Custom metrics** are user-defined calculated metrics that can work across channels (e.g., "Total Spend" = Google Ads spend + Meta spend). Use `list-custom-metrics`.
- **Custom dimensions** are user-defined dimensions for cross-channel categorization. Use `list-custom-dimensions`.

## Workflow: Cross-Channel Performance Overview

1. **Discover available blends**:
   ```
   list-blends action: list
   ```
   Blends are the primary mechanism for cross-channel reporting. Each blend's list entry includes `source_count` and `channel_names` — often enough to pick the right blend without calling `show`.

2. **Inspect a blend's configuration**:
   ```
   list-blends action: show, blend_id: <id>
   ```
   This reveals which sources are blended and how metrics map across them.

   **Read the join, not just the source list.** `show` returns the sub-sources *and* the joins between
   them, and the join is what decides whether a number looks wrong. Each join names a `type` and the
   dimensions the two sides are matched on:

   | Join type | Keeps |
   |---|---|
   | `full` | Every row from both sides; unmatched rows appear with the other side's fields empty |
   | `inner` | Only rows whose join-key values exist on **both** sides |
   | `left` / `right` | Every row from that one side, plus matches from the other |
   | `union` | Rows stacked rather than matched side by side |
   | `cross` | Every combination — multiplies rows, so almost never what a report wants |

   Diagnosing from this: **totals lower than the channels added up** usually means `inner` silently
   dropped rows whose join key existed on only one side. **Rows where a dimension is empty** are the
   normal, expected sign of a `full` join whose join-key values don't overlap — which itself tells you
   the keys don't align (a campaign-name join across an ad platform and an analytics property rarely
   matches, so a date-level join is often the honest one). **Row counts far larger than either source**
   points at `cross`, or at a join key that is not unique on either side.

3. **Fetch cross-channel data from the blend**:

   Blend field ids use one of two prefix families — always look them up before fetching:

   ```
   list-sources action: list_dimensions_and_metrics, source_id: <blend_source_id>
   ```

   The two families mean different things, and picking the wrong one is a common cause of a number
   that looks "wrong" rather than an error:

   - **`aggregation_*`** — the **combined** value across sub-sources, e.g.
     `aggregation_metric_universal_metric_1`, `aggregation_dimension_universal_dimension_1137`. This is
     the one unified column. Use it for "total spend across channels".
   - **`blend_*`** — **one sub-source's own** column, e.g. `blend_metric_spend`, `blend_dimension_date`.
     Use it to show channels side by side, or as the operand of a per-channel calculation.

   So a single "Spend" figure comes from the `aggregation_*` field; reaching for a `blend_*` field
   instead silently gives you one channel's spend presented as the total. Note also that `blend_*`
   fields carry **no channel label** — the same metric on two sub-sources comes back with the same
   display name, so map each id to its sub-source via `list-blends action: show` before using it.

   Use the verbatim ids from that response in `fetch-data`:

   ```
   fetch-data source_id: <blend_source_id>,
     metrics: ["aggregation_metric_universal_metric_1",
               "aggregation_metric_universal_metric_2"],
     dimensions: ["aggregation_dimension_universal_dimension_1137"],
     from: "2026-03-01", till: "2026-03-31"
   ```

   **First-call transient:** a blend is computed live (it stores nothing), so its data is available immediately. But the first fetch can still return `Your data is being processed... please wait...` with `retryable: false` — that signals an **underlying sub-source** isn't ready yet (still fetching from its API, rate-limited, or period not aggregated), not a blend warmup. Treat it as transient — wait ~10–15 seconds and retry the same call. See the "Handling Errors" section of `fetching-marketing-metrics` for the full retry pattern.

   **Incorrect blend setup error:** if `fetch-data` returns an error categorised as `setup_error` (e.g. "Incorrect blend setup"), the blend itself is misconfigured — not the fetch call. Use `list-blends action: show, blend_id: <id>` to inspect the source mapping. Common causes: a source was removed after the blend was created, or a required metric mapping is missing. The fix is in the UI blend editor — reconnect the missing source or re-map the metrics.

4. **For channel-by-channel comparison**, fetch data from each source individually and present side by side:
   ```
   # Google Ads
   fetch-data source_id: <google_ads_id>, ...
   # Facebook Ads
   fetch-data source_id: <facebook_ads_id>, ...
   ```

## Workflow: Source Group Analysis

Source groups are particularly useful for agencies managing many accounts of the same type.

1. **List source groups**:
   ```
   list-source-groups action: list
   ```

2. **Inspect group membership**:
   ```
   list-source-groups action: show, group_id: <id>
   ```
   Shows all sources in the group and their ETL configurations.

   **Check `configs_count` before you interpret anything.** A group holds one or more *configs*, each
   an output the group produces, and `show` returns per-config `id`, `name`, `output_name`, plus
   `etl_config_ids` and `etl_configs` (each with its `channel_name`).

   - **One config** — the normal, current shape. One unified output; read it as a single source.
   - **More than one config** — an older group shape. Each config aggregates its own set of fields and
     is read separately, so a metric present in one config is not necessarily available in another. If
     a field you expect is missing, check whether you are reading the right config before concluding
     the group is broken.

   `output_name` is **read-only** — it is computed from the config's structure, not something anyone
   set. Use `etl_configs[].channel_name` to see which channels actually back a config; a channel absent
   there contributes nothing, whatever the group's source list suggests.

3. **Check for sync issues**:
   ```
   list-source-groups action: source_issues, group_id: <id>
   ```
   Lists sources with disabled ETL configs — these are not contributing data.

## Workflow: Custom Metrics and Dimensions

1. **List custom metrics**:
   ```
   list-custom-metrics action: list
   list-custom-metrics action: list, semantic_search: "customer acquisition cost"   # by meaning
   list-custom-metrics action: list, type: "channel"                                # by scope
   ```

   **Know which kind of metric you are looking at** — it decides what the number means:

   | Kind | What it does |
   |---|---|
   | `data_aggregation` | Sums the **same** metric across the sources it maps, into one total. This is the primitive behind "total spend across accounts" — no group or blend involved. |
   | `data_formula` | Calculates from other fields (ROAS, CPA, CPC). Its operands are named `A`, `B`, … |
   | `metadata` | An alias / unified name for an existing field. No maths. |

   Scope matters just as much: a metric's **transformation level** is either `channel` (applies to every
   source of that channel) or `source` (one specific account). Filter by it with `type:`. A metric
   scoped to one source will look "missing" on the others — that is the scope, not a fault.

   **The cross-source ratio caveat.** A `data_aggregation` metric totals one metric across sources, but
   a *ratio* whose numerator and denominator each need aggregating first (blended ROAS, blended CPA)
   cannot be done by one metric alone — it needs a group or blend underneath, then a `data_formula` on
   top of that combined source. So when a "blended" ratio looks wrong, check whether it was built on a
   combined source at all, or is quietly averaging per-source ratios.

   `list_with_premades` additionally filters by `map_type` (the full set, including
   `currency_exchange`, `tag`, `system`, `ai`) and by `integrations`.

2. **Inspect a custom metric formula**:
   ```
   list-custom-metrics action: show, metric_id: <id>
   ```

3. **List custom dimensions**:
   ```
   list-custom-dimensions action: list
   ```

## Common Cross-Channel Analysis Patterns

### Total Performance Summary
Fetch key metrics from each channel and present a unified summary:
- **Total Spend**: Sum of spend across all paid channels
- **Total Conversions**: Sum of conversions (watch for attribution overlap)
- **Blended ROAS**: Total conversion value / Total spend
- **Blended CPC**: Total spend / Total clicks

### Channel Comparison Table
| Channel | Spend | Clicks | Conversions | CPC | ROAS |
|---------|-------|--------|------------|-----|------|
| Google Ads | ... | ... | ... | ... | ... |
| Facebook Ads | ... | ... | ... | ... | ... |
| LinkedIn Ads | ... | ... | ... | ... | ... |
| **Total** | ... | ... | ... | ... | ... |

### Trend Analysis Across Channels
Fetch daily data from each channel with `dimensions: ["date"]` and create a combined time series to show how total performance evolves.

### Channel Mix Analysis
Calculate each channel's share of total spend, conversions, or traffic to understand budget allocation effectiveness.

## Important Considerations

- **Metric naming varies across platforms**: "Clicks" in Google Ads may be "link_clicks" in Facebook Ads. Blends handle this mapping, but when comparing sources directly, check metric names with `list_dimensions_and_metrics`.
- **Currency differences**: Sources may report in different currencies. Check the `currency` field on each source.
- **Attribution overlap**: When summing conversions across channels, the total may exceed actual conversions due to multi-touch attribution. Note this when presenting cross-channel totals.
- **Date alignment**: Ensure all channel data covers the exact same date range for fair comparison.

## Tips

- When users ask "what's working best?", compare channels by efficiency metrics (ROAS, CPC, cost per conversion) rather than just volume.
- For budget allocation questions, calculate the marginal efficiency of each channel.
- Source groups with many sources (50+) may take longer to return data. Set expectations about load times.
- If a blend shows unexpected numbers, inspect its source mapping — a metric might be incorrectly mapped or a source might be missing.
