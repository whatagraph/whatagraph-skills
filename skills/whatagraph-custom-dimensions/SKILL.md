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

Discover the source's `field_external_id`s with `list-sources action=list_dimensions_and_metrics`. **Prerequisite:** on multi-report-type sources this call requires a `report_type` — run `list-sources action=list_report_types` for the target source first; if it returns more than one report type (e.g. Google Ads, 60+), pass `report_type` on the discovery call, or it errors "Multiple report types are available. Please specify a report_type parameter." Zero-report-type sources (e.g. Facebook Ads, GA4) omit `report_type` entirely.

## Use this when

- "Branded vs Non-branded" classification of campaigns.
- "Channel Bucket" grouping (Paid Search, Paid Social, Organic, Direct).
- Assigning an account manager to a source for team-level reporting.
- Normalizing inconsistent campaign naming across clients before blending.
- AI-classify campaign names into categories.

## Four dimension types — pick the right one

| `map_type` | What it does | Example |
|---|---|---|
| `metadata` | 1:1 alias of an existing dimension | Alias `<campaign field>` to "Campaign" for consistency |
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
list-custom-dimensions action=list_tags dimension_id=<id>
list-custom-dimensions action=usage universal_dimension_ids=[<id>]
```

`show` returns compact summaries for tag dimensions: `tag_count` and `source_count` instead of the full tags array. Use `list_tags` to get paginated tag details with assigned source IDs. Both `list_tags` and `list` support cursor pagination via `cursor` and `per_page` parameters.

## Field IDs are per-channel — discover them, don't copy

`field_external_id`, `channel_id`, and `report_type_external_id` are **channel-specific**. Before building any `fields` entry, fetch the real values with `list-sources action=list_dimensions_and_metrics` for your target channel/source and pass each id exactly as returned (universal / organized dimensions come back with a `universal_` prefix — keep it). The `campaign_name` / `report_type_external_id: "campaign"` pair in the examples below only shows the *shape*: it exists on some ad channels and is absent on others, so pasting it verbatim will fail validation on the wrong channel.

The premade "Campaign Name" is a **universal / organized** dimension exposed as `universal_dimension_1` (keep the `universal_` prefix) — this is distinct from a channel-native campaign field. On Google Ads / GA4 the channel-native id is **dotted** (e.g. `campaign.name`); bare `campaign_name` is not in those catalogs and will fail resolution. Always resolve the exact id via `list-sources action=list_dimensions_and_metrics` and paste it as returned.

## Creating a `metadata` alias

```
manage-custom-dimensions action=create
   name="Campaign"
   map_type="metadata"
   transformation_level="channel"
   fields=[
     # example ids — resolve real ones via list_dimensions_and_metrics first
     {"channel_id": <channel_id>, "field_external_id": "<field_external_id>", "report_type_external_id": "<report_type>"}
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
     # example ids — resolve real ones via list_dimensions_and_metrics first
     {"channel_id": <channel_id>, "field_external_id": "<field_external_id>", "report_type_external_id": "<report_type>"}
   ]
   maps=[
     {
       "value": "Branded",
       "conditions": [
         {
           "operator": "contains",
           "value": "brand",
           "fields": [{"channel_id": <channel_id>, "field_external_id": "<field_external_id>", "report_type_external_id": "<report_type>"}]
         }
       ]
     },
     {
       "value": "Competitor",
       "conditions": [
         {
           "operator": "contains",
           "value": "comp",
           "fields": [{"channel_id": <channel_id>, "field_external_id": "<field_external_id>", "report_type_external_id": "<report_type>"}]
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

Each condition's `fields` entry has the same shape as a top-level `fields` entry: `{channel_id, field_external_id, report_type_external_id?}` at channel level, or `{integration_source_id, field_external_id, report_type_external_id?}` at source level. On a blend source (channel 142), the `fields` array accepts **any** family the blend catalog returns — `universal_dimension_<n>`, `blend_dimension_<n>`, or `aggregation_dimension_<n>` (the `aggregation_dimension_` prefix is stripped and re-resolved); prefer `universal_dimension_<n>` (e.g. `universal_dimension_1` for Campaign Name). There is no channel-142 gate on dimensions — the opposite of custom **metrics**, where `universal_metric_<n>` is rejected on a blend. See `whatagraph-blends` → "Custom fields on a blend". On a source-group source, use the unprefixed `universal_dimension_*` form.

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

Manage tags after creation:

```
# Add a tag
manage-custom-dimensions action=add_tag dimension_id=<id>
   tag="Alex" source_ids=[<src6>]

# Assign/replace sources on an existing tag
manage-custom-dimensions action=assign_tag_sources dimension_id=<id>
   tag="Alex" source_ids=[<src7>, <src8>]

# Clear all sources from a tag (pass empty array)
manage-custom-dimensions action=assign_tag_sources dimension_id=<id>
   tag="Alex" source_ids=[]

# Remove a tag entirely
manage-custom-dimensions action=remove_tag dimension_id=<id>
   tag="Alex"

# List tags with pagination
list-custom-dimensions action=list_tags dimension_id=<id> per_page=50
```

## Creating an `ai` dimension

```
manage-custom-dimensions action=create
   name="Campaign Intent"
   map_type="ai"
   transformation_level="source"
   # example id — resolve real one via list_dimensions_and_metrics first
   fields=[{"integration_source_id": <source_id>, "field_external_id": "<field_external_id>"}]
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
- **Field discovery on multi-report-type channels** — on channels with many report types (e.g. Google Ads, 60+), `list_dimensions_and_metrics` errors without `report_type`. Run `list_report_types` first; pass `report_type` when >1 exists; omit it for zero-report-type sources.
- **Guessed / copied field ids** — never invent a `field_external_id` or reuse one from the examples; resolve it per channel via `list-sources action=list_dimensions_and_metrics` (see "Field IDs are per-channel" above). Universal / organized dimensions keep their `universal_` prefix.
- **Compact tag responses** — `create`, `update`, and `show` return `tag_count`/`source_count` instead of full tag arrays to stay under MCP transport limits. Use `list_tags` to get individual tag details with source IDs.
- **`assign_tag_sources` replaces, not appends** — the `source_ids` array replaces the tag's entire source list. To add a source, include all existing source IDs plus the new one. Pass an empty array to clear all sources.
