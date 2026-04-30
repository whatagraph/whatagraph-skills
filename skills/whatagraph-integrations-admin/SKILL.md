---
name: whatagraph-integrations-admin
description: Browse available integrations, connect sources from already-authenticated accounts, and assign sources to spaces. Use when onboarding a new client (adding their sub-accounts into Whatagraph) or when reallocating existing sources across client folders.
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

## Connect a source from an already-authenticated account

```
manage-integrations action=add_sources
   channel_id=<channel_id>
   account_id=<connected_account_id>
   source_ids=["<external_id_1>", "<external_id_2>"]
```

- `source_ids` are the **external** ids returned by `list_available_sources` — NOT integer database ids.
- After `add_sources`, the source appears in `list-sources action=list` with a new internal `integration_source_id`.

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

```
remove-integrations action=remove_sources account_id=<id> source_ids=[<id>, <id>]
remove-integrations action=delete_account  account_id=<id>
```

- `remove_sources` — drop specific sources from an authenticated account. Other sources on the same account stay connected.
- `delete_account` — disconnect the entire authenticated account. All its sources go with it.

Both operations are high-impact. Always check `list-sources action=list_usage source_ids=[...]` first — widgets, blends, source groups, and measurements referencing the removed sources break.

To delete sources without touching the account (e.g., clean up individual sources at the team level), see `delete-sources` in `whatagraph-sources-and-data`.

## What MCP can't do here

- Connect a new OAuth account — browser/UI flow only.
- Re-authorize an expired token — UI only.

## Common pitfalls

- **Adding a source that's already connected** — skipped silently or surfaced as "already exists".
- **`source_ids` as integer ids in `add_sources`** — must be the external ids from `list_available_sources`.
- **Currency override without matching cost data** — `set_currency` sets display currency; it does not convert existing rows. Historical data keeps its stored currency.
- **`client_ids=[]` on `sync_to_clients`** — wipes space assignments. Intentional only when de-assigning.
- **Tagging source groups as sources** — source groups have their own integration_source_id; tag them directly if you want the group (not sub-sources) tagged.
- **Tag id on the wrong dimension** — tag values belong to specific tag dimensions. Cross-dimension values are rejected.
