---
name: whatagraph-destinations
type: domain
group: data_connections
description: Create data transfers that push Whatagraph-ingested data to external destinations (BigQuery, LookerStudio, local storage, Whatagraph storage), view the configured ones, inspect their job history, and control them (stop, resume, resync, update).
required_tools:
  - list-destinations
  - manage-destinations
  - list-sources
optional_tools:
  - tool_name: delete-destinations
    purpose: Permanently stop and delete a configured data transfer.
  - tool_name: manage-blends
    purpose: Store a blend's output instead of a single source's — blend storage is enabled on the blend, not through a transfer.
---

# Destinations & data transfers

Tools covered: `list-destinations`, `manage-destinations`, `delete-destinations`.

A **destination** = a configured transfer that pushes data from Whatagraph-ingested integration sources out to an external system (BigQuery, LookerStudio, etc.). This is the opposite direction of a data source (source = pulls in; destination = pushes out).

## Use this when

- "Send my Google Ads data to BigQuery every day."
- "Show me every active BigQuery transfer and its last-run status."
- "What's failing on this transfer's jobs?"
- "Which sources does this BigQuery transfer push?"

## Listing transfers

```
list-destinations action=list
list-destinations action=list status="active"
list-destinations action=list destination_id=1              # 1=BigQuery
list-destinations action=list issue="job"                    # only transfers with job issues
list-destinations action=list name="My Transfer"            # filter by transfer name
```

Pagination: `page` (integer, default 1) and `per_page` (integer, default 16, max 500). Same pagination applies to `list_jobs`.

`destination_id` values:
- `1` — BigQuery
- `2` — LocalStorage
- `3` — LookerStudio
- `4` — WhatagraphStorage

`issue` values: `job`, `account`, `source`.

### `storage_source_id` — from a transfer to a reportable source

A transfer to Whatagraph Storage (`destination_id=4`) creates a data source holding the stored data. Every row from `action=list` and `action=show` carries its id:

```
list-destinations action=list destination_id=4
# → [{"id": 309, "name": "...", "destination": "Whatagraph Storage", "storage_source_id": 448501, ...}]
```

The field is `null` for every other destination.

That id is an ordinary source id. Pass it to `manage-widgets` to build a widget on the stored data, or to `list-sources action=list_report_types` to see the tables the user mapped. Nothing has to be connected first: the source is created with the transfer.

Going the other way, `list-sources action=list` does not return storage sources unless you name the channel, so use `channels=["whatagraph-storage"]` there. See `whatagraph-sources-and-data`.

## Available destination types

```
list-destinations action=list_destination_types
```

Returns the destination types you can target — BigQuery (`1`), Looker Studio (`3`), Whatagraph Storage (`4`) — each with its required `components` (e.g. `oauth`, `name`, `projectId`, `dataset`, `location`, `configs`) and, for BigQuery, the full set of supported regions. Use it to discover which destinations exist and what each needs before inspecting transfers. Only connectable types are returned, so LocalStorage (`destination_id=2`, a legacy/internal type) does not appear here even though it is a valid `destination_id` filter on `action=list`.

## Creating a transfer

A transfer covers **one data source**. The source is named once, at the top level, and every table
in the transfer reads it. To send a second channel, create a second transfer.

Each entry in `configs` becomes one table and **consumes one source credit**.

### Call order

```
list-destinations action=list_destination_types              # which destinations, and what each needs
list-sources      action=list                                # the source id the transfer will read
list-sources      action=list_report_types    source_id=<id> # only when the source needs one
list-sources      action=list_dimensions_and_metrics source_id=<id> [report_type=<id>]
manage-destinations action=create validate_only=true ...     # check every table, create nothing
manage-destinations action=create ...                        # build it
```

Do not skip `list_dimensions_and_metrics`. Field ids are sent bare, as `external_id` strings copied
verbatim from that listing. An id the source does not expose is rejected by name.

### A minimal create

```
manage-destinations action=create
  destination_id=4
  name="Google Ads to storage"
  frequency="daily"
  integration_source_id=<source id>
  backfill_until="2026-01-01"
  configs=[
    {
      "name": "campaigns",
      "dimensions": ["<daily date dimension>", "campaign_name"],
      "metrics": ["impressions", "clicks"],
      "time_window": "daily"
    }
  ]
```

`frequency` is `daily` to keep syncing, or `noupdate` for a one-off load.

After creating a `destination_id=4` transfer, read its `storage_source_id` with `action=show`. That is the source to report on, and it exists as soon as the transfer does.

### Per-table keys in `configs`

| Key | Notes |
|---|---|
| `dimensions` | Required. Must include the source's daily date dimension. |
| `metrics` | Required. At least one. |
| `report_types` | A list of `external_id` strings. Only the first is used, because a table stores one report type. Omit for a source that exposes none. |
| `output_name` | The table name, required for every destination **except** Whatagraph Storage. Must match `^[a-zA-Z0-9][a-zA-Z0-9_]*[a-zA-Z0-9]$`. |
| `name` | The table name for Whatagraph Storage, used **instead of** `output_name`. |
| `time_window` | `daily` (default), `rolling_7_days`, or `monthly`. Fixed at creation and cannot be changed later. To re-cut a table's grain, create a new table. |
| `filter_type`, `filter_id` | Optional saved filter. See `whatagraph-filters`. |

There is no per-table `integration_source_id`. Sending one does nothing, because the source belongs
to the transfer.

### What each destination needs

| Destination | `integration_account_id` | `credentials` |
|---|---|---|
| Whatagraph Storage (`4`) | no | no |
| Looker Studio (`3`) | no | no |
| BigQuery (`1`) | **required** | **required**: `projectId`, `dataset`, `location` |

Whatagraph Storage and Looker Studio derive everything from the team, so they work end to end from
MCP. **BigQuery does not yet.** No tool lists the connected destination accounts or their BigQuery
projects, so ask the user for `integration_account_id` and `credentials.projectId`, or ask them to
create the BigQuery transfer in the Whatagraph app and manage it here afterwards.

### Rules the create enforces

- **Only a source whose channel reads through the unified data layer can be transferred.** Others are
  refused by name. The app does not offer them in its channel list either.

- **Every table must include the source's daily date dimension**, including when `time_window` is not
  `daily`. Without it the pipeline stamps every row with the day it was fetched, and the whole table
  collapses onto one date. A windowed table still stores rows under it; the pipeline writes the
  window start there.

  The required id is often a **universal** dimension id (for example `universal_dimension_1137`), not
  the channel's native date field. Both appear in `list_dimensions_and_metrics`, and only the one the
  tool names is accepted. If the create is refused, the error states the exact id to add.

- **Every table is checked against the source before anything is written.** The tool asks the provider
  for one day per table. A rejected report type, dimension or metric comes back as an error naming
  that table. A day with no rows is accepted, because the question is whether the provider accepts the
  fields, not whether the source had data yesterday. A rate limit or an upstream failure comes back as
  retryable rather than as a table to fix.

- **`backfill_until` must be on or before yesterday**, and has a ceiling: 3 years back for Whatagraph
  Storage, 10 years for the other destinations, and 1 month on a trial team. A longer range queues
  more ETL jobs.

### Building a multi-table transfer

`validate_only=true` runs the per-table check and creates nothing, so tables can be assembled and
checked one at a time before one final create.

```
manage-destinations action=create validate_only=true ...   # repeat while adding tables
manage-destinations action=create ...                      # then build it once
```

Pass an `idempotency_key` on the real create. A retried call after a lost response returns the
original transfer instead of building a second one and spending the credits twice.

### Storing a blend

A blend's output is not stored through a transfer. Enable storage on the blend itself with
`manage-blends`. See `whatagraph-blends`.

## Inspecting one transfer

```
list-destinations action=show transfer_id=<id>
```

Returns the transfer's tables (one config per table), target, and schedule.

## Listing a transfer's jobs

```
list-destinations action=list_jobs transfer_id=<id>
list-destinations action=list_jobs transfer_id=<id> state="issue"
list-destinations action=list_jobs transfer_id=<id> config_id=<id>
```

`state` values: `queued`, `running`, `completed`, `issue`.

**A transfer is not pass-or-fail — it is a set of configs, one per table, each syncing on its own.** So one config can be failing while the rest complete happily, and the transfer still reports as active. When a user says "the export is broken", find out *which part*:

1. `action=show` to list the transfer's configs.
2. `action=list_jobs transfer_id=<id> state="issue"` to see only the failing jobs, then read each job's `config_id` to identify the affected table.
3. Narrow to one config with `config_id=<id>` to read just its history.

This matters when interpreting a resync too: a resync re-fetches the range for the transfer, so a range that only one config missed is re-pulled for all of them. Confirm the scope before promising a targeted fix, and check `list_jobs` afterwards rather than assuming success.

## Controlling a transfer

```
manage-destinations action=stop   transfer_id=<id>                       # pause syncing new data
manage-destinations action=resume transfer_id=<id>                       # re-activate + backfill missed dates
manage-destinations action=resync transfer_id=<id> from=<date> to=<date> # re-fetch a date range (transfer must be ACTIVE)
manage-destinations action=update transfer_id=<id> name="New name"       # rename and/or change backfill window
manage-destinations action=update transfer_id=<id> backfill_until=<date>
```

- `resync` requires the transfer to be ACTIVE — resume a stopped transfer first. It also rejects when a backfill is still in progress; wait for it to finish.
- **`resync` takes `from` / `to` — not `from` / `till`.** Every neighbouring tool (exports, fetches, share settings) ends a date range with `till`, and this one action does not. `till` is not accepted here, so a copied range silently fails validation on a parameter name rather than on the dates. `to` must be on or after `from`.
- `update` needs at least one of `name` / `backfill_until`. `backfill_until` must be on or before yesterday. Moving it further back queues additional ETL jobs for the newly-covered dates.

## Deleting a transfer

```
delete-destinations action=delete transfer_id=<id>
```

Stops the outbound transfer permanently. Previously delivered rows in the destination are outside Whatagraph's control. See `whatagraph-deleting` for cascades and recovery context.

## What MCP can't do here

- Reset a transfer's jobs — UI only.
- Create a BigQuery transfer unaided — the account and project ids have to come from the user. See
  "What each destination needs" above.
- Change a table's `time_window`, or add a table to an existing transfer.

## Common pitfalls

- **Confusing destinations with data sources** — destinations push data out; data sources pull in. Different tool.
- **Putting two channels in one transfer** — a transfer reads one source, named once in `integration_source_id`. A second channel needs a second transfer.
- **Inventing field ids** — `dimensions` and `metrics` take `external_id` strings copied verbatim from `list-sources` `action=list_dimensions_and_metrics`, never display names.
- **Creating before validating** — each table costs a source credit and queues its backfill immediately. Use `validate_only=true` first.
- **`issue=account` vs `issue=source`** — `account` means the authenticated integration account expired; `source` means the sub-source is failing. Different fixes.
- **Stale `running` jobs on stopped transfers** — if a transfer was paused or stopped while jobs were in flight, those jobs can remain in `running` state indefinitely without ever completing. They are not actually executing. Always check the transfer's overall status (`list-destinations action=show`) before interpreting job states — a `running` job under a stopped transfer is effectively stuck, not in-progress.
