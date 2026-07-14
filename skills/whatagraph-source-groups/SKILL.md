---
name: whatagraph-source-groups
type: domain
description: Combine multiple data sources into one virtual aggregated source — same-channel (e.g. five Google Ads sub-accounts) or cross-channel (e.g. Meta + Google + Reddit + TikTok). Use when an agency wants unified reporting without building a blend.
required_tools:
  - list-source-groups
  - list-sources
  - fetch-data
  - manage-reports
  - manage-source-groups
  - manage-widgets
---

# Source groups

Tools covered: `list-source-groups`, `manage-source-groups`.

A **source group** aggregates multiple sources into one virtual source. Sources can be from the same channel (e.g. multiple Google Ads accounts) or from different channels (e.g. Meta Ads + Google Ads + Reddit Ads + TikTok — cross-channel aggregation). The group gets its own integration source id that widgets, blends, and custom metrics can reference as if it were a single source.

## Use this when

- Agency has 3 Google Ads sub-accounts under one client MCC — roll up to one "Google Ads" source.
- Property manager has 20 GBP locations — one aggregated source for reporting.
- Franchise brand has multiple Meta ad accounts per region — one virtual source per brand.
- Cross-channel rollup — combine Meta Ads + Google Ads + Reddit Ads + TikTok into one aggregated source with unified metrics (impressions, clicks, spend).

## Source group vs blend vs custom metric

| Goal | Use |
|---|---|
| 5 Google Ads accounts → 1 virtual "Google Ads Total" | Source group (same-channel) |
| Meta + Google + Reddit + TikTok → 1 aggregated source with unified metrics | Source group (cross-channel) |
| Sum of `spend` across Google + Meta into one total, no row-level join | Source group (cross-channel) |
| Google Ads + Meta Ads joined/matched on campaign name (side-by-side rows) | Blend |

**Rule**: source groups handle both same-channel and cross-channel aggregation and are simpler than blending — think of a source group as the templated, stored, auto-summarized version of a blend. Use a blend only when you need to **join** rows across channels on a shared dimension (e.g. matching campaign names between Google Ads and Meta Ads).

## Listing

```
list-source-groups action=list                       # paginated; supports search
list-source-groups action=show group_id=<id>         # sources, configs, currency
list-source-groups action=source_issues group_id=<id> # sources with disabled ETL
```

Note: `output_name` in the `show` response is read-only (computed from the config structure). It is not a create or update parameter.

### Valid `fields` paths

Use the `fields` parameter to select only the attributes you need (reduces response size).

- **`list`**: `id`, `name`, `description`, `currency`, `created_by`
- **`show`**: `id`, `name`, `description`, `currency`, `integration_source_id`, `sources`, `configs_count`, `configs`

Note: `integration_source_id` is only available on `show`, not `list`. To get a group's virtual source ID, use `show`.

## Creating a source group

Creation is a **strict, ordered pipeline** that mirrors how the app builds a group: resolve fields → **verify with a real fetch** → build one ETL config per channel → create the group from those configs. Do **not** skip a step, and do **not** advance until the current step fully succeeds. A group built on fields a channel can't actually return will look fine and then come back empty.

A **channel** = the integration a source belongs to. Steps 1–3 run once **per channel**, each time using one representative source for that channel.

### Step 0 — Pick sources, group them by channel

Choose the `integration_source_ids` (`list-sources action=list`). Group them by channel: a same-channel group has one channel, a cross-channel group has several. Note one representative source per channel.

### Step 1 — Resolve report type and fields (universal-first), per channel

For each channel's representative source, resolve:

- the **report type** (channel-native) — `list-sources action=list_report_types source_id=<src>`
- the **fields** — `list-sources action=list_dimensions_and_metrics source_id=<src> is_universal=true`

**Always prefer universal / unified fields** (`universal_metric_*`, `universal_dimension_*`) so the group aggregates cleanly across channels. Fall back to a channel's **native** fields only when no universal field fits. Resolve fields **per channel** — but that means *reading each channel's own `list_dimensions_and_metrics` output*, not deciding applicability from memory: the call already returns only the fields that apply to that channel (a universal field shows up only where it maps; native fields only on their own channel). Use a field only if it appears in that source's list. Include the Date dimension (`universal_dimension_1137`) so the group has a time axis. Do **not** add **Channel name** (`universal_dimension_1130`) or **Source name** (`universal_dimension_1131`) — the group injects both automatically on its virtual source. You never pass them to `create_config`; they're for reading/drilling only (see *Drilling into sub-sources*).

### Step 2 — Verify the selection actually fetches (per channel) — MANDATORY

Before creating anything, prove each channel's source returns data with the resolved fields, for **yesterday**:

```
fetch-data source_id=<representative source for the channel>
   report_type="<channel-native report type>"
   metrics=[<resolved metric external_ids>]
   dimensions=[<resolved dimension external_ids>]
   from="<yesterday>" till="<yesterday>"
```

- **Pass = `success: true`.** Zero rows is still a pass — the account may just have no activity yesterday.
- **Anything else is a failure.** A `data_not_ready` result means the source is still processing — **wait and re-run the same fetch**; never treat it as success and never proceed on it. `upstream_error` / `validation` are also failures — fix the inputs or retry.
- Repeat for every channel. **Continue only when every channel's verify fetch passes.**

### Step 3 — Create one team-internal ETL config per channel

For each channel, create its ETL config from the **verified** report type + fields:

```
manage-source-groups action=create_config
   integration_source_id=<representative source for the channel>
   name="<group name> — <channel>"
   report_types=[{"external_id": "<channel-native report type>"}]
   dimensions=[{"external_id": "...", "name": "..."}, ...]
   metrics=[{"external_id": "...", "name": "..."}, ...]
```

The channel is derived from the source — you don't pass it. Each call returns an `etl_config_id`. **Collect one `etl_config_id` per channel.** Continue only when every channel's config is created.

> The `dimensions` list is per-channel fields only. Leave out Channel name (`universal_dimension_1130`) and Source name (`universal_dimension_1131`) — injected automatically on the group.

> Some channels have **no report types** (e.g. Facebook Ads — `list_report_types` returns none). For those, omit `report_types` entirely (and omit `report_type` in the step-2 verify fetch too).

> **Applicability is server-enforced here.** A field the channel doesn't expose can't enter a config — the server rejects it. But it surfaces as a **generic error**, not a clean per-field message, so don't throw arbitrary fields and read the error to learn what fits. That's exactly why fields come from the channel's own `list_dimensions_and_metrics` (step 1) and are proven by the verify fetch (step 2) **before** this call.

### Step 4 — Create the source group

Create the group with all sources and a **single config** holding every channel's `etl_config_id`:

```
manage-source-groups action=create
   name="<group name>"
   description="..."        # optional
   currency="USD"          # optional
   configs=[{ "name": "<group name>", "etl_config_ids": [<all channel etl_config_ids>] }]
   integration_source_ids=[<all selected sources>]
```

- Pass **one** config. Its `etl_config_ids` must contain **exactly one ETL config per channel** present in `integration_source_ids` — that's why step 3 runs once per channel. Miss a channel and creation is rejected.
- `configs[].name` defaults to the group `name` when omitted.
- The response returns the group's virtual `integration_source_id` (use it in widgets) plus a `warmup_hint` — data takes a few minutes to populate.

## One config per group (strongly recommended)

A source group exposes **one** report-type level (e.g. campaign performance). If the user needs campaign-level *and* keyword-level rollups from the same sources, build **two separate source groups**, one per level. Per group that means one entry in `configs`, with one `etl_config_id` per channel inside it. This keeps each group focused and makes widgets, filters, and blends easier to reason about.

## Updating

How much you do depends on **what changes**. There are two cases.

### A — Simple update (no field changes)

Renaming, changing description/currency, or adding/removing sources of channels the group **already covers** — pass only what changes and **omit `configs`** entirely. No fetching, no config work.

```
manage-source-groups action=update group_id=<id>
   name="..."                 # any of these, all optional
   description="..."
   currency="EUR"
   integration_source_ids=[<full new source list>]   # replace-style — full list
```

`integration_source_ids` is replace-style (the full list replaces the old one). Adding a source of a **brand-new channel** is not simple — it needs a config for that channel (case B).

### B — Changing fields, or adding a new channel

Mirror creation, but reuse what exists. First read current state:

```
list-source-groups action=show group_id=<id>
# returns each config's `id` and `etl_config_ids` (+ the integration per id)
```

1. **Per existing channel whose fields change** — verify-fetch (yesterday) the new selection (only `success:true` proceeds), then PATCH that channel's config (its `etl_config_id` from `show`):
   ```
   manage-source-groups action=update_config
      etl_config_id=<existing id>
      integration_source_id=<a representative source of that channel>
      report_types=[...]  dimensions=[...]  metrics=[...]
   ```
   The id comes back unchanged. **Skip any channel whose fields don't change.**
2. **Per new channel added** — verify-fetch → `create_config` → new `etl_config_id` (as in creation step 3).
3. **Update the group** with the existing config `id` and the **full** id set:
   ```
   manage-source-groups action=update group_id=<id>
      configs=[{ id:<existing source_group_config id>,
                 etl_config_ids:[<every channel's id — unchanged + patched + new>] }]
      integration_source_ids=[<all sources, incl. any new ones>]
   ```

- **Reuse the existing config `id`** (from `show`) — never omit it; a missing id makes a new config and orphans dependents.
- The single config's `etl_config_ids` must still cover **every** channel in `integration_source_ids` (one id per channel), exactly like create. Don't drop unchanged channels' ids — re-pass them as-is.
- Channels you didn't touch are **not** re-fetched.

**Always edit a group with `update`, never delete-and-recreate.** A rebuild mints a **new** virtual `source_id`, which silently detaches every source-level custom metric, widget, and report binding that pointed at the old one. `update` preserves the group's virtual `source_id`, so dependents stay attached.

## Duplicating

```
manage-source-groups action=duplicate group_id=<id>
```

## Resolving sync issues

Some sources in the group may need attention after sync errors. Check affected sources and resolve them:

```
list-source-groups action=source_issues group_id=<id>        # view affected sources
manage-source-groups action=resolve_issues group_id=<id>
   integration_source_ids=[<affected_source_ids>]
```

`resolve_issues` re-enables and **restarts the ETL transfer** on the sources you list. If one of those sources is **shared with other groups or reports**, restarting it re-syncs them too — they'll briefly show "downloading historical data" until the transfer catches up. Scope `integration_source_ids` to the sources that actually need it, and expect a transient re-sync on anything sharing them.

## Using the group in widgets

The group exposes its own integration source id (found via `list-source-groups action=show` as `integration_source_id`). Attach it to the report first, then create the widget against the returned report-local `source_id`:

```
manage-reports action=attach_source report_id=<id>
   integration_source_id=<group_integration_source_id>
# response.source_id is the report-local id

manage-widgets action=create report_id=<id> tab_id=<tab_id>
   channel_id=<group_channel_id>
   source_id=<that report-local id>
   widget_type_id=<...>
```

The group's metrics and dimensions are the union of what its ETL configs expose.

## Reading data from a group directly

You don't need a widget to preview data from a source group. Use `fetch-data` on the group's `integration_source_id`:

```
fetch-data source_id=<group integration_source_id>
  report_type="<the report type the group exposes>"
  metrics=["universal_metric_1", "universal_metric_2", "universal_metric_3"]
  dimensions=["universal_dimension_1137"]
  from="2026-04-01" till="2026-04-15"
```

Notes:

- **`report_type`** is the report type the group exposes — run `list-sources action=list_report_types source_id=<group integration_source_id>` to see the exact string. This is the group's own report type, not the original sources' channel-native report type you passed to `create_config`.
- **Field ids** use the `universal_metric_*` / `universal_dimension_*` form on the group's source. The platform aggregates sub-sources automatically.

## Drilling into sub-sources

The plain `universal_metric_*` / `universal_dimension_*` form returns the group **aggregate** (one rolled-up total). The group also exposes the contribution of each channel and each sub-source — the main reason to use a group over a blend. Two ways:

- **Break the aggregate into rows** — add `universal_dimension_1130` (Channel name) or `universal_dimension_1131` (Source name) to a normal group fetch; you get one row per channel / per sub-source instead of one total.
- **Pick a single channel's or source's metric** — every universal metric also exists as `..._integration_<integrationId>` (one channel's sub-total) and `..._integration_source_<sourceId>` (one sub-source's contribution).

```
fetch-data source_id=<group integration_source_id>
  report_type="<the report type the group exposes>"
  metrics=["universal_metric_1"]
  dimensions=["universal_dimension_1131", "universal_dimension_1137"]   # Source name + Date
  from="2026-04-01" till="2026-04-15"
```

`whatagraph-sources-and-data` ("Source-group breakdown metrics") owns the exact id forms and the rule for choosing a variant over a filter — load it for those. Group-specific notes:

- **Don't hand-construct the ids.** List them with `list-sources action=list_dimensions_and_metrics source_id=<group integration_source_id>` and pick the `_integration_source_<id>` / `_integration_<id>` variants; each field's `group` attribute names its channel/source.
- The per-source variants exist only on **multi-source** groups, and are dropped on very large (consolidated) groups — break out by `universal_dimension_1131` there instead.

## Deleting a source group

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: permanent (the virtual source is removed), widgets and custom metrics pointing at the group break, pre-check `list-source-groups action=show group_id=<id>`. To *change* a group, always use `update` — never delete-and-recreate (see above).

## What MCP can't do here

- Remove one sub-source from the group without providing the full replacement list — use `update` with the full new `integration_source_ids` list.

## Common pitfalls

- **Skipping the verify fetch (step 2)** — never create configs or a group on fields you haven't proven fetch. `data_not_ready` is **not** success: wait and re-run the same fetch until it returns `success: true` (zero rows is fine), then proceed.
- **Putting Channel name / Source name in `create_config`** — `universal_dimension_1130` / `universal_dimension_1131` are injected automatically on the group. Don't include them in a config's `dimensions`; they're read/drill-only fields.
- **Missing a channel's ETL config** — the single create config's `etl_config_ids` must cover **every** channel in `integration_source_ids` (one config per channel from `create_config`). Miss one and `create` is rejected.
- **Resolving fields once for all channels** — a universal field applies to a channel only if it maps to that channel, and native fields are channel-specific. Each channel's `list_dimensions_and_metrics` is the source of truth — resolve per channel from it (step 1). Pass a field a channel doesn't expose and config-create fails with an opaque server error, not a clear "field X doesn't apply" message.
- **Editing a group? Use `update`, never delete+recreate** — a rebuild changes the virtual `source_id` and orphans source-level custom metrics and widget bindings.
- **`resolve_issues` on a shared source re-syncs other groups** — scope `integration_source_ids` narrowly and expect a transient re-download on anything sharing those sources.
- **Empty group right after creation** — ETL needs a few minutes to populate; the create response includes a `warmup_hint` and `retry_after_seconds`. Wait before fetching from the group.
- **Group not appearing in widget picker immediately** — refresh the report; new groups can take a few seconds to appear.
- **Very large groups (hundreds of sub-sources)** — query performance can slow down. Keep one report-type level per group and split into focused groups rather than one sprawling group.
- **Adding source groups can affect plan usage** — creating or expanding a group consumes source credits; check the team's plan limits before bulk-creating.
- **`source_ids` vs `integration_source_ids`** — `create` expects `integration_source_ids`; `create_config` expects a single `integration_source_id`.
- **Widget creation against a fresh group failing** — re-run `list-source-groups action=show` to verify `integration_source_id` exists and data has arrived before attaching widgets.
- **Per-source metrics missing on a huge group** — the `universal_metric_<id>_integration_source_<subId>` family is generated only for multi-source groups and is **not** available on very large (consolidated) groups, where it's dropped to avoid query blow-up. Break out by `universal_dimension_1131` (Source name) instead.
