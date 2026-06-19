---
name: whatagraph-integrations-admin
type: domain
description: Browse available integrations, connect sources from already-authenticated accounts, and assign sources to spaces. Use when onboarding a new client (adding their sub-accounts into Whatagraph) or when reallocating existing sources across client folders.
required_tools:
  - list-integrations
  - list-sources
  - list-spaces
  - manage-integrations
  - manage-sources
---

# Integrations & sources admin

Tools covered: `list-integrations`, `manage-integrations`, `manage-sources`.

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

## Connect a source from an already-authenticated account

```
manage-integrations action=add_sources
   channel_id=<channel_id>
   account_id=<connected_account_id>
   source_ids=["<external_id_1>", "<external_id_2>"]
```

- `source_ids` are the external ids returned by `list_available_sources`.
- After `add_sources`, the source appears in `list-sources action=list` with an `integration_source_id`.

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
```

Find `tag_id` and `tag_value_ids` via `list-sources action=list_metadata`.

## Removing sources or an entire account

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Pick the right scope first:

| You want to… | Use |
|---|---|
| Detach sources from this team only (account untouched, other teams unaffected) | `delete-sources` |
| Drop specific sources from an authenticated account | `remove-integrations action=remove_sources` |
| Disconnect the entire authenticated account (all its sources go; OAuth re-connect to re-add) | `remove-integrations action=delete_account` |

All three are high-impact: always check `list-sources action=list_usage source_ids=[...]` first — widgets, blends, source groups, and measurements referencing the removed sources break.

## What MCP can't do here

- Connect a new OAuth account — browser/UI flow only.
- Re-authorize an expired connection — UI only.

## Common pitfalls

- **Adding a source that's already connected** — may be skipped or surfaced as "already exists".
- **`source_ids` as integer ids in `add_sources`** — must be the external ids from `list_available_sources`.
- **Currency override without matching cost data** — `set_currency` sets display currency; it does not convert existing rows. Historical data keeps its stored currency.
- **`client_ids=[]` on `sync_to_clients`** — wipes space assignments. Intentional only when de-assigning.
- **Tagging source groups as sources** — source groups have their own integration_source_id; tag them directly if you want the group (not sub-sources) tagged.
- **Tag id on the wrong dimension** — tag values belong to specific tag dimensions. Cross-dimension values are rejected.
