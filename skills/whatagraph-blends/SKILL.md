---
name: whatagraph-blends
description: Combine data from different channels (Google Ads + Meta + GA4) into one virtual source by joining on shared dimensions (date, campaign name, etc.). Use when a widget needs to show cross-channel rows side-by-side or a computed metric needs numerator/denominator from separate sources.
---

# Blends

Tools covered: `list-blends`, `manage-blends`, `delete-blends`.

A **blend** joins 2+ sources into a single virtual source. The blend has its own integration source id, so widgets and custom metrics can treat the blend like any other source.

## Use this when

- "Put Google Ads spend and Meta Ads spend in the same table grouped by date."
- "Compute Blended ROAS = GA4 revenue / (Google Ads spend + Meta Ads spend)." (Blend first, custom metric second.)
- "Cross-channel performance widget that groups by campaign theme across 3 platforms."

## Blend vs source group — quick decision

| Goal | Use |
|---|---|
| Sources are ALL the same channel (5 Google Ads accounts) → one virtual source | Source group (`manage-source-groups`) |
| Sources are DIFFERENT channels that must join on a shared dimension | Blend |
| Sum one field across channels without joining | Custom metric `data_aggregation` |

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
       "report_type": "campaigns",
       "dimensions": ["universal_dimension_1137", "campaign_name"],
       "metrics":    ["impressions", "spend"]
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
- `report_type` — the source's report type external id. Auto-resolved when source has exactly one report type; required otherwise.
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

Most production blends use `full` — it avoids silent data loss. `inner` is a common source of "my data disappeared after blending" tickets.

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

## Using the blend in widgets

Treat the blend as a source. Pass the blend's integration source id as the widget's `source_id` via `manage-widgets`. The widget's metrics and dimensions come from the sub-sources; reference them via their external ids.

## Deleting a blend

```
delete-blends action=delete blend_id=<id>
```

Before deleting, check for usage — `list-blends action=show blend_id=<id>` returns `widgets_count`. Widgets referencing the blend break silently after delete.

## What MCP can't do here

- Pre-filter sub-source data before joining — apply widget-level filters instead.

## Common pitfalls

- **`join_type` vs `type`** — MCP uses `type` inside each join object. `join_type` is rejected.
- **`join_fields` vs `conditions`** — MCP uses `conditions` with `{left_source_id, left_dimension, right_source_id, right_dimension}` per pair. Legacy `groups` format is accepted but the simplified `conditions` format is the recommended one.
- **`inner` join silently dropping data** — most "where did my data go?" blend tickets are caused by `inner` on a dimension that doesn't match across sources (e.g. Google campaign name "Brand_US" vs Meta "Brand - US"). Use `full` unless you specifically want intersection.
- **Joining on non-shared dimension names** — if dimensions have different external ids per channel (e.g. `campaign_name` vs `campaign`), create a `metadata` custom dimension alias first so the external ids match, then join on the aliased field.
- **Including the same metric in multiple sub-sources** — the metric appears twice in widget field pickers (e.g. "Spend (Google)" and "Spend (Meta)"); use a custom metric of type `data_aggregation` on top of the blend if you want one combined "Spend" field.
- **Blend without date dimension in join** — rows from different periods get cartesian-joined. Always include a date dimension in your join conditions.
- **Currency mismatch across sub-sources** — the blend's `currency` field is cosmetic; actual values are as-stored. Normalize source-level currencies via `manage-sources action=set_currency` first.
