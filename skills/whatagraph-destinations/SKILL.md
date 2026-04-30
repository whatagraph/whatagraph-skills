---
name: whatagraph-destinations
description: View configured data transfers that push Whatagraph-ingested data to external destinations (BigQuery, LookerStudio, local storage, Whatagraph storage) and inspect their job history. Read-only via MCP.
---

# Destinations & data transfers (read-only)

Tool covered: `list-destinations`.

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
```

`destination_id` values:
- `1` — BigQuery
- `2` — LocalStorage
- `3` — LookerStudio
- `4` — WhatagraphStorage

`issue` values: `job`, `account`, `source`.

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

## What MCP can't do here

- Create a new transfer — UI only.
- Update or pause a transfer — UI only.
- Trigger a manual sync — UI only.
- Delete a transfer or reset its jobs — UI only.

## Common pitfalls

- **Confusing destinations with data sources** — destinations push data out; data sources pull in. Different tool.
- **Assuming MCP can create a transfer** — only viewing is supported. The UI handles transfer setup and scheduling.
- **`issue=account`** vs `issue=source`** — `account` means the authenticated integration account expired; `source` means the sub-source is failing. Different fixes.
