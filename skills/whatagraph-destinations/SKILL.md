---
name: whatagraph-destinations
type: domain
description: View configured data transfers that push Whatagraph-ingested data to external destinations (BigQuery, LookerStudio, local storage, Whatagraph storage), inspect their job history, and control existing transfers (stop, resume, resync, update). Creating a new transfer is UI-only.
required_tools:
  - list-destinations
  - manage-destinations
  - delete-destinations
---

# Destinations & data transfers

Tools covered: `list-destinations`, `manage-destinations`, `delete-destinations`.

A **destination** = a configured transfer that pushes data from Whatagraph-ingested integration sources out to an external system (BigQuery, LookerStudio, etc.). This is the opposite direction of a data source (source = pulls in; destination = pushes out).

## Use this when

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

## Available destination types

```
list-destinations action=list_destination_types
```

Returns the destination types you can target — BigQuery (`1`), Looker Studio (`3`), Whatagraph Storage (`4`) — each with its required `components` (e.g. `oauth`, `name`, `projectId`, `dataset`, `location`, `configs`) and, for BigQuery, the full set of supported regions. Use it to discover which destinations exist and what each needs before inspecting transfers. Only connectable types are returned, so LocalStorage (`destination_id=2`, a legacy/internal type) does not appear here even though it is a valid `destination_id` filter on `action=list`.

## Inspecting one transfer

```
list-destinations action=show transfer_id=<id>
```

Returns configs (one per source/report-type combo), target, schedule.

## Listing a transfer's jobs

```
list-destinations action=list_jobs transfer_id=<id>
list-destinations action=list_jobs transfer_id=<id> state="issue"
list-destinations action=list_jobs transfer_id=<id> config_id=<id>
```

`state` values: `queued`, `running`, `completed`, `issue`.

## Controlling a transfer

```
manage-destinations action=stop   transfer_id=<id>                       # pause syncing new data
manage-destinations action=resume transfer_id=<id>                       # re-activate + backfill missed dates
manage-destinations action=resync transfer_id=<id> from=<date> to=<date> # re-fetch a date range (transfer must be ACTIVE)
manage-destinations action=update transfer_id=<id> name="New name"       # rename and/or change backfill window
manage-destinations action=update transfer_id=<id> backfill_until=<date>
```

- `resync` requires the transfer to be ACTIVE — resume a stopped transfer first. It also rejects when a backfill is still in progress; wait for it to finish.
- `update` needs at least one of `name` / `backfill_until`. `backfill_until` must be on or before yesterday. Moving it further back queues additional ETL jobs for the newly-covered dates.

## Deleting a transfer

```
delete-destinations action=delete transfer_id=<id>
```

Stops the outbound transfer permanently. Previously delivered rows in the destination are outside Whatagraph's control. See `whatagraph-deleting` for cascades and recovery context.

## What MCP can't do here

- Create a new transfer — UI only.
- Reset a transfer's jobs — UI only.

## Common pitfalls

- **Confusing destinations with data sources** — destinations push data out; data sources pull in. Different tool.
- **Assuming MCP can create a transfer** — existing transfers can be controlled (`stop`/`resume`/`resync`/`update`), but initial transfer setup and scheduling is UI-only.
- **`issue=account` vs `issue=source`** — `account` means the authenticated integration account expired; `source` means the sub-source is failing. Different fixes.
- **Stale `running` jobs on stopped transfers** — if a transfer was paused or stopped while jobs were in flight, those jobs can remain in `running` state indefinitely without ever completing. They are not actually executing. Always check the transfer's overall status (`list-destinations action=show`) before interpreting job states — a `running` job under a stopped transfer is effectively stuck, not in-progress.
