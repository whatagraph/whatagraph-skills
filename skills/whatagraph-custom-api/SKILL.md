---
name: whatagraph-custom-api
type: domain
group: data_connections
description: Push your own numbers into Whatagraph, so data from a system Whatagraph has no connector for still lands on a report. Covers creating the source, defining metrics and dimensions, sending daily rows, and correcting a day you already sent. Use when a user asks how to send their own data in, mentions the Custom API or an access token, or wants a metric Whatagraph cannot fetch for them.
required_tools:
  - manage-custom-api
  - list-custom-api-data
  - list-sources
optional_tools:
  - tool_name: list-spaces
    purpose: Find the space IDs to assign a new source to.
  - tool_name: fetch-data
    purpose: Read the numbers back after pushing them, to check they landed.
---

# Whatagraph Custom API

A Custom API source is one you fill in yourself. You define the metrics and dimensions, then send one row per day. Whatagraph stores them as an ordinary source, so the numbers work in any widget, report or blend, exactly like a source Whatagraph fetches.

Use it when Whatagraph has no connector for the system holding the data, or when the numbers only exist in a spreadsheet, a database or a script. Nothing needs to be built, and Whatagraph needs no access to the system: the data is pushed in.

There are two ways to do this. **Use the MCP tools.** They are the whole job in three calls, they need no access token, and re-sending a day corrects it instead of doubling it. The raw HTTP path at the end of this skill is for a script running outside Whatagraph's MCP server, and it is the older and more error-prone of the two.

## The data model

- **Metrics** are the numbers: signups, clicks, revenue. Each one declares how days roll up into weeks and months.
- **Dimensions** are the labels that slice the numbers: channel, country, client.
- **Rows** are the data. One row is one day, for one combination of dimension values.
- The **Date dimension already exists**, along with every time grouping built from it (Year, Month, Week, Day of week). Never define it.

One source can hold data for many clients or entities at once. Add a dimension such as `client` and filter per report, rather than creating a source each.

## The three calls

### 1. Create the source

```
manage-custom-api action=create_source name="Vollan exports" space_ids=[12]
```

`space_ids` is optional. The response carries the `source_id` every later call needs.

If the user already has a Custom API source, find it with `list-sources` instead of making another.

### 2. Define the metrics and dimensions

```
manage-custom-api action=define_schema source_id=4471
  metrics=[{"external_id":"signups","name":"Signups","type":"int","accumulator":"sum","negative_ratio":false}]
  dimensions=[{"external_id":"channel","name":"Channel","type":"string"}]
```

- `type` for a metric: `int`, `float`, `currency` or `percent`.
- `accumulator`: `sum`, `average` or `last`. This is how days roll up into a week or a month.
- `negative_ratio`: `true` when a decrease is the good direction, such as cost per signup. It only changes the period-over-period colour.
- `type` for a dimension: `string`, `int`, `time`, `float` or `date`. Do not create a `date` dimension; that one exists already.

The call matches on `external_id`, so running it again updates what is there rather than creating a second entry with the same name.

Define the schema before sending rows. A widget built on a dimension that is missing for part of its date range can error.

### 3. Send the rows

```
manage-custom-api action=push_data source_id=4471 rows=[
  {"date":"2026-01-01","channel":"Google","signups":42},
  {"date":"2026-01-01","channel":"Meta","signups":17}
]
```

Each key is either `date` or one of your `external_id` values. `date` is required on every row and must be `YYYY-MM-DD`. Send one row per day per combination of dimension values.

**Re-sending a day corrects it.** The default mode is `replace_dates`, which drops whatever the source already holds for each date in the payload and then stores what you sent. So a retry after a timeout is safe, and fixing a day means sending that day again with the right numbers.

Pass `mode=append` only when you are deliberately adding more rows to a day you have already sent, for example streaming one dimension combination at a time. In that mode a date sent twice is stored twice, and a `sum` metric counts both.

A push is capped at 5000 rows per call. Above that the call is refused and nothing is stored, so split the work by date range and send the parts one after another.

## Reading it back

```
list-custom-api-data action=list_metrics source_id=4471
list-custom-api-data action=list_dimensions source_id=4471
list-custom-api-data action=list_data_points source_id=4471 from=2026-01-01 till=2026-01-31
```

Read the metrics and dimensions before defining any, so you update what is there instead of adding something almost identical next to it.

## Removing data

```
manage-custom-api action=delete_data source_id=4471 from=2026-01-01 till=2026-01-31
```

This removes every stored row in that range. It cannot be undone, so confirm the range with the user first.

## Things to get right

**Daily granularity only.** One row per day. There is no hourly resolution, and the accumulator is what produces weekly and monthly figures.

**Deleting the source in the web app destroys its data.** There is no recovery, and no export step warns first. Never suggest deleting and recreating a Custom API source as a fix.

**A metric's type and accumulator decide how it reads.**

| `type` | `accumulator` | Shown as | Rolled up as |
|---|---|---|---|
| `int` | `sum` | `43` | sum of the days |
| `currency` | `average` | `$11.70` | mean across the days |
| `float` | `average` | `2.35` | mean across the days |

## Then build the widget

Pick the Custom API source, choose your metrics and dimensions, and filter on whichever dimension separates one client or entity from another. See `whatagraph-widgets`.

## The raw HTTP path

Use this only for a script running outside Whatagraph's MCP server. It reaches the same source and the same data, but the tools above handle several traps that this path leaves to you.

The user has to create the source themselves first, in the Whatagraph web app: **Data → Sources → Connect new source**, search for **Custom**, pick **Custom API** under "Other", give it an **Access name**, then open the source again and copy the **Access token**.

The token is the whole credential. Treat it like a password: never write it into a file you commit, and never echo it back into a chat transcript. The user can rotate it from the same panel. One token belongs to exactly one Custom API source, and the token is what identifies the source, so there is no other parameter naming it.

Base URL: `https://api.whatagraph.com`. Every request carries `Authorization: Bearer <ACCESS_TOKEN>` and `Content-Type: application/json`.

| What | Call |
|---|---|
| List, create metrics | `GET` / `POST /v1/integration-metrics` |
| Read, update, delete one metric | `GET` / `PUT` / `DELETE /v1/integration-metrics/{id}` |
| List, create dimensions | `GET` / `POST /v1/integration-dimensions` |
| Read, update, delete one dimension | `GET` / `PUT` / `DELETE /v1/integration-dimensions/{id}` |
| List, push data points | `GET` / `POST /v1/integration-source-data` |
| Read, update, delete one data point | `GET` / `PUT` / `DELETE /v1/integration-source-data/{id}` |

The bodies match the tool payloads above. Data points go in a `data` array rather than `rows`. Each stored point comes back with its own hash under the key `id`, which is what the single-point paths take.

Responses: metric and dimension creates return `200` (the published reference says `201`, so read `data.id` rather than branching on the status code), a data push returns `201`, `204` means deleted, `400` means the token is valid but not connected to a source, `401` means the header is missing or the token is wrong, `409` means a dimension with that `external_id` already exists, `422` means validation failed, and `429` means rate limited. The limit is 200 requests per minute per token, and `X-RateLimit-Remaining` says how many are left. A `429` is retryable and never means the data was rejected.

Four traps this path leaves to you, all of which the tools handle:

**Sending a day twice adds it twice.** `POST /v1/integration-source-data` always inserts. It never matches an existing row and updates it. This is the single most likely way to get wrong numbers here. Track which dates you have sent. To correct a day, `GET /v1/integration-source-data` filtered to that date, `DELETE` each point by its hash, then `POST` the right rows.

**A duplicate metric is not rejected.** Only dimensions return `409`. Posting the same metric `external_id` twice silently creates a second metric, and the widget picker then shows two entries with the same name. Read the metric list before creating.

**The list endpoints default to 10 per page.** A schema check that reads one page and concludes a metric is missing will then create a duplicate. Pass `per_page`, or follow the pagination links. The other query parameters are `sort_field`, `sort_direction` (`asc` or `desc`), and `filter`, which is a JSON object sent as a string, for example `filter={"external_id":"signups"}`. Each filter entry matches on a substring rather than on equality, so a filter for `signups` also matches `signups_paid`.

**`PUT` on a data point replaces the whole row.** The body you send becomes the stored row in full. Any key you leave out is gone, not kept. Send every field, including `date`.

```bash
BASE="https://api.whatagraph.com"
TOKEN="<ACCESS_TOKEN>"
H=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")

# Read the schema before creating anything.
curl -s "$BASE/v1/integration-metrics?per_page=100" "${H[@]}"

# Create what is missing.
curl -s -X POST "$BASE/v1/integration-metrics" "${H[@]}" \
  -d '{"name":"Signups","external_id":"signups","type":"int","accumulator":"sum","negative_ratio":false}'

# Push one day, all its dimension combinations in one request.
curl -s -X POST "$BASE/v1/integration-source-data" "${H[@]}" -d '{"data":[
  {"date":"2026-01-01","channel":"Google","signups":42},
  {"date":"2026-01-01","channel":"Meta","signups":17}
]}'
```

## Where to go next

- Building the widget on top of the data: `whatagraph-widgets`.
- Checking what is connected and which metrics a source offers: `whatagraph-sources-and-data`.
- Numbers that look wrong after a push: re-read the duplicate-row trap above first, then `troubleshooting-data-issues`.
