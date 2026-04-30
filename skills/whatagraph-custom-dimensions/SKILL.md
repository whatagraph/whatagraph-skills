---
name: whatagraph-custom-dimensions
description: Create derived dimensions — tag-based groupings, condition-based buckets, AI-classified categories, or metadata aliases. Use when the user wants to group/label dimension values (e.g. "Branded vs Non-branded", "Account Manager", "Channel Bucket") that aren't native to any source.
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

```
manage-custom-dimensions action=create
   name="Brand Classification"
   map_type="data"
   transformation_level="channel"
   fields=[
     {"channel_id": <channel_id>, "field_external_id": "campaign_name", "report_type_external_id": "campaign"}
   ]
   maps=[
     {"when": "contains",       "value": "brand", "then": "Branded"},
     {"when": "contains",       "value": "comp",  "then": "Competitor"},
     {"when": "matches_regex",  "value": "^BRND_","then": "Branded"},
     {"default": "Non-branded"}
   ]
```

Rule order matters — first match wins. Supported `when` operators: `equals`, `contains`, `starts_with`, `ends_with`, `matches_regex`.

## Creating a `tag` dimension

```
manage-custom-dimensions action=create
   name="Account Manager"
   map_type="tag"
   transformation_level="source"
   tags=[
     {"tag": "Jane", "source_ids": [<src1>, <src2>, <src5>]},
     {"tag": "Mike", "source_ids": [<src3>, <src4>]}
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

## What MCP can't do here

- Delete — UI only.

## Common pitfalls

- **Regex escaping** — JSON-escape backslashes (`"\\b"` not `"\b"`). Preview with `preview_ai` or a small test before wide rollout.
- **Rule order** — first match wins. Put specific rules before general ones.
- **`data` dimension with no `default`** — unmatched values render blank. Always include `{"default": "..."}` unless intentional.
- **Tag dimension applied to source group's `source_id`** — applies to the group as a whole, not per-sub-source. For per-sub-source tagging, pass the individual source IDs.
- **AI dimension prompt too open** — constrain outputs: "Return only one of: <list>". Unbounded prompts produce variant category names.
- **Prompt-only without `fields`** — `ai` map_type still requires a source field via `fields` (or `integration_source_id` + `field_external_id` pair inside the preview call).
- **`channel_id` vs `integration_source_id`** — channel-level fields use `channel_id`; source-level fields use `integration_source_id`. Match to `transformation_level`.
- **Universal / organized dimensions** — their `field_external_id` starts with `universal_` prefix; pass exactly as returned by `list-sources action=list_dimensions_and_metrics`.
