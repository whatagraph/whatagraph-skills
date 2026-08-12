---
name: whatagraph-integrations-admin
type: domain
group: data_connections
description: Browse available integrations, connect sources from already-authenticated accounts, and assign sources to spaces. Use when onboarding a new client (adding their sub-accounts into Whatagraph) or when reallocating existing sources across client folders.
required_tools:
  - list-integrations
  - list-sources
  - list-spaces
  - manage-integrations
  - manage-sources
optional_tools:
  - tool_name: remove-integrations
    purpose: Detach sources from an account or disconnect an authenticated account.
---

# Integrations & sources admin

Tools covered: `list-integrations`, `manage-integrations`, `manage-sources`, `remove-integrations`.

An **integration** (also called a channel) is an OAuth-authenticated connection to a third-party platform. Each integration has one or more **accounts** (authenticated user/admin accounts). Each account exposes **sources** (sub-accounts, properties, ad accounts). Sources are what show up in the source picker.

## Use this when

- Adding a new Google Ads sub-account from an already-connected MCC.
- Moving a source into a client's space for organization.
- Tagging sources (e.g. "EMEA", "US", "Pilot").
- Overriding currency for a source that reports in an unusual currency.

## Discover integrations and accounts

```
list-integrations action=list                          # all implemented channels
list-integrations action=list_grouped                  # by category + counts
list-integrations action=list_accounts channel_id=<id>
list-integrations action=list_available_sources account_id=<id> search="Acme"
```

`channel_id` accepts both numeric IDs and slugs (e.g. `5` or `"google-ads"`) on both `list-integrations` and `manage-integrations`.

## Connect a source from an already-authenticated account

```
manage-integrations action=add_sources
   channel_id=<channel_id>
   account_id=<connected_account_id>
   source_ids=["<external_id_1>", "<external_id_2>"]
```

- `source_ids` are the external ids returned by `list_available_sources`.
- After `add_sources`, the source appears in `list-sources action=list` with an `integration_source_id`.

### Sub-source integrations (Google Sheets, BigQuery, Snowflake, Google My Business)

Some integrations have a two-level hierarchy: **parent source** (spreadsheet, dataset) → **sub-source** (tab, table). When `list_available_sources` returns `has_sub_sources: true`, you must discover sub-sources before adding:

```
# 1. List parent sources — response includes has_sub_sources: true
list-integrations action=list_available_sources account_id=<id>

# 2. Pick a parent and list its sub-sources
list-integrations action=list_available_sub_sources
   account_id=<id>
   source_external_id=<parent_external_id>

# 3. Connect using the sub-source external_id (JSON format)
manage-integrations action=add_sources
   channel_id=<channel_id>
   account_id=<id>
   source_ids=["<sub_source_external_id>"]
```

Sub-source `external_id` values are JSON strings like `{"integration_source_id":"<spreadsheet_id>","sub_source_id":<tab_gid>}` — copy them verbatim from step 2. Both `list_available_sources` and `list_available_sub_sources` support `search` for name filtering.

## Assign a source to spaces

```
manage-integrations action=sync_to_clients
   source_id=<integration_source_id>
   client_ids=[<space_id_1>, <space_id_2>]
```

- `client_ids` are space ids (from `list-spaces`).
- Pass an empty array `[]` to remove from all spaces.

## Tag / re-currency a source

```
manage-sources action=tag
   source_ids=[<id>, <id>]
   tag_id=<tag_dimension_id>
   tag_value_ids=[<value_id>]

manage-sources action=set_currency
   source_ids=[<id>, <id>]
   currency="EUR"

manage-sources action=refresh
   source_ids=[<id>, <id>]          # max 10 per call
```

**`refresh`** clears the cached data for those sources so the next read re-fetches from the provider.
Reach for it after a reconnect, a currency change, or a "my numbers are stale / nothing is showing"
report — it is the fix for a stale cache, not for a broken connection. It is capped at **10 sources per
call** (more is rejected, so split into batches) because each refreshed source triggers a fresh
provider fetch and the cap protects the provider's rate limits. It clears caches only; it does not
re-run history, so give the next read a moment to repopulate.

Find `tag_id` and `tag_value_ids` via `list-sources action=list_metadata` (scope `tags`).

**`tag` only ASSIGNS tag values that already exist — it never creates them.** So "tag these EMEA"
when there is no EMEA tag yet is a two-step job, and step one belongs to a different tool: create the
tag dimension and its values with `manage-custom-dimensions action=create map_type=tag` (that call can
assign sources at the same time), then use `manage-sources action=tag` for later assignments. Passing a
`tag_id` or `tag_value_ids` that doesn't exist is rejected — it does not silently create one.

## Removing sources or an entire account

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Pick the right scope first:

| You want to… | Use |
|---|---|
| Detach sources from this team only (account untouched, other teams unaffected) | `delete-sources` |
| Drop specific sources from an authenticated account | `remove-integrations action=remove_sources account_id=<id> source_ids=[<int>, ...]` |
| Disconnect the entire authenticated account (all its sources go; OAuth re-connect to re-add) | `remove-integrations action=delete_account account_id=<id>` |

Both `remove-integrations` actions require `account_id`. `source_ids` on `remove_sources` are **integer** integration source IDs (from `list-sources`), not the external string IDs used by `add_sources`.

All three are high-impact: always check `list-sources action=list_usage source_ids=[...]` first — widgets, blends, source groups, and measurements referencing the removed sources break.

## What MCP can't do here

- Connect a new OAuth account — browser/UI flow only.
- Re-authorize an expired connection — UI only.

## Common pitfalls

- **Passing a parent ID to `add_sources` for sub-source integrations** — returns an error explaining you need `list_available_sub_sources` first. Always check `has_sub_sources` in the `list_available_sources` response.
- **Adding a source that's already connected** — may be skipped or surfaced as "already exists".
- **`source_ids` in `add_sources` vs `remove_sources`** — `add_sources` takes external string IDs from `list_available_sources`; `remove_sources` takes integer integration source IDs from `list-sources`. Same parameter name, different ID spaces.
- **Currency override without matching cost data** — `set_currency` sets display currency; it does not convert existing rows. Historical data keeps its stored currency.
- **`client_ids=[]` on `sync_to_clients`** — wipes space assignments. Intentional only when de-assigning.
- **Tagging source groups as sources** — source groups have their own integration_source_id; tag them directly if you want the group (not sub-sources) tagged.
- **Tag id on the wrong dimension** — tag values belong to specific tag dimensions. Cross-dimension values are rejected.
