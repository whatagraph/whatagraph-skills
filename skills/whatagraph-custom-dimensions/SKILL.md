---
name: whatagraph-custom-dimensions
type: domain
description: Create derived dimensions — tag-based groupings, condition-based buckets, AI-classified categories, or metadata aliases. Use when the user wants to group/label dimension values (e.g. "Branded vs Non-branded", "Account Manager", "Channel Bucket") that aren't native to any source.
required_tools:
  - list-custom-dimensions
  - list-sources
  - manage-custom-dimensions
  - manage-filters
---

# Custom dimensions

Tools covered: `list-custom-dimensions`, `manage-custom-dimensions`.

A **custom dimension** is a derived field that groups, labels, or aliases existing dimension values. Once created, it appears in `list-sources action=list_dimensions_and_metrics` and can be used in widgets, blends, filters, and overviews.

## Use this when

- "Branded vs Non-branded" classification of campaigns.
- "Channel Bucket" grouping (Paid Search, Paid Social, Organic, Direct).
- Assigning an account manager to a source for team-level reporting.
- Normalizing inconsistent campaign naming across clients before blending.
- AI-classify campaign names into categories.

## Four dimension types — pick the right one

| `map_type` | What it does | Example |
|---|---|---|
| `metadata` | 1:1 alias of an existing dimension | Alias `campaign_name` to "Campaign" for consistency |
| `data` | Maps field values to named buckets via rules | `contains 'brand'` → "Branded" else "Non-branded" |
| `tag` | Manually-assigned tag per source | "Account Manager = Jane" across a list of sources |
| `ai` | AI-classified via a prompt | Classify campaign names into Brand / Generic / Display |

## Transformation level

| `transformation_level` | Meaning |
|---|---|
| `channel` | Dimension applies to every source of the channel |
| `source` | Dimension applies to specific sources |

## Listing

```
list-custom-dimensions action=list
list-custom-dimensions action=list_with_premades
list-custom-dimensions action=show dimension_id=<id>
list-custom-dimensions action=usage universal_dimension_ids=[<id>]
```

## Creating a `metadata` alias

```
manage-custom-dimensions action=create
   name="Campaign"
   map_type="metadata"
   transformation_level="channel"
   fields=[
     {"channel_id": <channel_id>, "field_external_id": "campaign_name", "report_type_external_id": "campaign"}
   ]
```

## Creating a `data` (condition-based) dimension

Each map has a result `value` (the bucket label) and one or more `conditions`. Each condition has an `operator`, a comparison `value`, and a `fields` array pointing at the source field(s) being matched against. Order matters — first matching map wins. Unmatched rows render blank unless you provide a fallback map (see "Simplified maps shortcuts" below).

```
manage-custom-dimensions action=create
   name="Brand Classification"
   map_type="data"
   transformation_level="channel"
   fields=[
     {"channel_id": <channel_id>, "field_external_id": "campaign_name", "report_type_external_id": "campaign"}
   ]
   maps=[
     {
       "value": "Branded",
       "conditions": [
         {
           "operator": "contains",
           "value": "brand",
           "fields": [{"channel_id": <channel_id>, "field_external_id": "campaign_name", "report_type_external_id": "campaign"}]
         }
       ]
     },
     {
       "value": "Competitor",
       "conditions": [
         {
           "operator": "contains",
           "value": "comp",
           "fields": [{"channel_id": <channel_id>, "field_external_id": "campaign_name", "report_type_external_id": "campaign"}]
         }
       ]
     }
   ]
```

Supported `operator` values (verified Jun 2026): `contains`, `includes`, `not_contain`, `exactly_matches`, `not_exactly_matches`, `starts_with`, `not_starts_with`, `ends_with`, `not_ends_with`, `matches_regex`, `not_matches_regex`. There is no `equals` — use `exactly_matches`. A condition's `value` also accepts an **array** for multi-value matching (e.g. `"operator": "includes", "value": ["Brand_US", "Brand_EU"]`) — one condition instead of one map per value. The same operator family is used by `manage-filters` (with the `_dimension` / `_metric` suffix added there).

### Simplified `maps` shortcuts (MCP-only)

`manage-custom-dimensions create` and `update` accept a shorter `maps` shape in addition to the full `{value, conditions: [{operator, value, fields}]}` payload. The MCP layer expands these to the full API shape before saving:

```
maps=[
  {"when": "contains", "value": "brand",       "then": "Branded"},
  {"when": "contains", "value": "competitor",  "then": "Competitor"},
  {"default": "Other"}    # catch-all fallback (verified May 2026)
]
```

- `{when, value, then}` — single-condition map; `then` is the bucket label, `when`/`value` describe the operator + comparison value, fields default to the top-level `fields` array.
- `{default: "<label>"}` — fallback bucket that catches anything not matched by earlier maps. Persists as a map with `operator: "contains", value: ""` on the underlying field, which matches every non-null value. Add it as the **last** entry; first match wins.

Use the full shape when you need multiple conditions per bucket, cross-field comparisons, or to bind each map to a specific field different from the top-level `fields`. Use the simplified shape for the common "label by substring" pattern with an optional fallback.

Each condition's `fields` entry has the same shape as a top-level `fields` entry: `{channel_id, field_external_id, report_type_external_id?}` at channel level, or `{integration_source_id, field_external_id, report_type_external_id?}` at source level. On a blend or source-group source, use the unprefixed `universal_dimension_*` form (e.g. `universal_dimension_1` for Campaign Name) — the platform-prefixed `aggregation_dimension_*` and `blend_dimension_*` ids returned by `list-sources action=list_dimensions_and_metrics` are *not* accepted on `manage-custom-dimensions create` even though they show up on read.

## Creating a `tag` dimension

`tag` dimensions use a different field-name convention than the rest of the SKILL family — entries take `{name, sources}`, not `{tag, source_ids}`. Sending `{tag, source_ids}` returns a 500 with `Undefined array key "name"` (and once corrected to `name`, an `Undefined array key "sources"` follow-up). The working shape:

```
manage-custom-dimensions action=create
   name="Account Manager"
   map_type="tag"
   transformation_level="source"
   tags=[
     {"name": "Jane", "sources": [<src1>, <src2>, <src5>]},
     {"name": "Mike", "sources": [<src3>, <src4>]}
   ]
```

Add more tags later:

```
manage-custom-dimensions action=add_tag dimension_id=<id>
   tag="Alex" source_ids=[<src6>]
```

## Creating an `ai` dimension

```
manage-custom-dimensions action=create
   name="Campaign Intent"
   map_type="ai"
   transformation_level="source"
   fields=[{"integration_source_id": <source_id>, "field_external_id": "campaign_name"}]
   prompt="Classify this campaign name into one of: Brand, Generic, Retargeting, Display. Return only the category name."
```

Preview the AI output before saving:

```
manage-custom-dimensions action=preview_ai
   prompt="..."
   integration_source_id=<source_id>
```

## Updating

```
manage-custom-dimensions action=update dimension_id=<id>
   name="..." fields=[...] maps=[...] tags=[...] prompt="..."
```

Replace-style for arrays — the new `maps`/`tags`/`fields` list replaces the previous one.

## Duplicating

```
manage-custom-dimensions action=duplicate dimension_id=<id>
```

## Checking usage before modifying

```
list-custom-dimensions action=usage universal_dimension_ids=[<id>]
```

## Deleting custom dimensions

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: permanent (mappings, tags, and fields go with it). A dimension still used by widgets or filters is **blocked** — the call returns a conflict listing the affected widgets, reports, and filters. Remove those references first (`manage-widgets` / `manage-filters`), or re-run with `force=true` to delete anyway. Pre-check with `list-custom-dimensions action=usage`.

## Common pitfalls

- **Regex escaping** — JSON-escape backslashes (`"\\b"` not `"\b"`). Preview with `preview_ai` or a small test before wide rollout.
- **Rule order** — first match wins. Put specific rules before general ones.
- **`data` dimension expecting a `default` shortcut** — the MCP `maps` array does accept `{default: "<label>"}` as a fallback entry (see "Simplified maps shortcuts" above). Place it last in the `maps` array — first match wins, so any preceding map with matching conditions takes precedence. If you skip the fallback entirely, unmatched rows render blank.
- **Tag dimension applied to source group's `source_id`** — applies to the group as a whole, not per-sub-source. For per-sub-source tagging, pass the individual source IDs.
- **AI dimension prompt too open** — constrain outputs: "Return only one of: <list>". Unbounded prompts produce variant category names.
- **Prompt-only without `fields`** — `ai` map_type still requires a source field via `fields` (or `integration_source_id` + `field_external_id` pair inside the preview call).
- **`channel_id` vs `integration_source_id`** — channel-level fields use `channel_id`; source-level fields use `integration_source_id`. Match to `transformation_level`.
- **Universal / organized dimensions** — their `field_external_id` starts with `universal_` prefix; pass exactly as returned by `list-sources action=list_dimensions_and_metrics`.
