---
name: whatagraph-custom-api
type: domain
group: data_connections
description: Push your own numbers into Whatagraph over the Custom API, so data from a system Whatagraph has no connector for still lands on a report. Covers the one-time source setup, defining metrics and dimensions, sending daily data points, and correcting a day you already sent. Use when a user asks how to send their own data in, mentions the Custom API or an access token, or wants a metric Whatagraph cannot fetch for them.
required_tools:
  - list-sources
---

# Whatagraph Custom API

The Custom API is a data source you fill in yourself. You define the metrics and dimensions, then send one data point per day. Whatagraph stores them as an ordinary source, so the numbers work in any widget, report or blend, exactly like a source Whatagraph fetches.

Use it when Whatagraph has no connector for the system holding the data, or when the numbers only exist in a spreadsheet, a database or a script. Nothing needs to be built, and Whatagraph needs no access to the system: the data is pushed in.

**These are raw HTTP calls, not MCP tools.** Nothing in this skill goes through the Whatagraph MCP server. You need an assistant that can make HTTP requests, so Claude Code or Codex rather than a chat-only client. Verify that you can make an outbound POST before promising the user this will work.

## What a person has to do first

A Custom API source cannot be created over the API, and the access token cannot be read over it either. Ask the user to do this once, in the Whatagraph web app:

1. Open **Data → Sources**.
2. Click **Connect new source**.
3. Search for **Custom** and pick **Custom API**, under "Other".
4. Give it an **Access name**. This becomes the source's name in Whatagraph.
5. Open the source again (Data → Sources, then click it) and copy the **Access token**.

The token is the whole credential. Treat it like a password: never write it into a file you commit, and never echo it back into a chat transcript. The user can rotate it from the same panel.

One token belongs to exactly one Custom API source. A single source can hold data for many clients or entities at once: add a dimension such as `client` and filter per report, rather than creating a source each.

## Base URL and authentication

Base URL: `https://api.whatagraph.com`

Every request carries both headers:

```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

There is no other parameter identifying the source. The token resolves it.

## The data model

- **Metrics** are the numbers: signups, clicks, revenue. Each one declares how days roll up into weeks and months.
- **Dimensions** are the labels that slice the numbers: channel, country, client.
- **Data points** are the rows. One data point is one day.
- The **Date dimension already exists**, along with every time grouping built from it (Year, Month, Week, Day of week). Never define it.

Define the metrics and dimensions before sending any data. A widget built on a dimension that is missing for part of its date range can error.

## Endpoints

| What | Call |
|---|---|
| List metrics | `GET /v1/integration-metrics` |
| Create a metric | `POST /v1/integration-metrics` |
| Read, update, delete one metric | `GET` / `PUT` / `DELETE /v1/integration-metrics/{id}` |
| List dimensions | `GET /v1/integration-dimensions` |
| Create a dimension | `POST /v1/integration-dimensions` |
| Read, update, delete one dimension | `GET` / `PUT` / `DELETE /v1/integration-dimensions/{id}` |
| List data points | `GET /v1/integration-source-data` |
| Push data points | `POST /v1/integration-source-data` |
| Read, update, delete one data point | `GET` / `PUT` / `DELETE /v1/integration-source-data/{id}` |

### Creating a metric

Every field is required.

```json
{
  "name": "Signups",
  "external_id": "signups",
  "type": "int",
  "accumulator": "sum",
  "negative_ratio": false
}
```

- `type`: `int`, `float`, `currency` or `percent`.
- `accumulator`: `sum`, `average` or `last`. This is how days roll up into a week or a month.
- `negative_ratio`: `true` when a decrease is the good direction, such as cost per signup. It only changes the period-over-period colour.

### Creating a dimension

```json
{ "name": "Channel", "external_id": "channel", "type": "string" }
```

- `type`: `string`, `int`, `time`, `float` or `date`. Do not create a `date` dimension; that one exists already.

### Pushing data points

The rows go in a `data` array. Each key is either `date` or one of your `external_id` values.

```json
{
  "data": [
    { "date": "2026-01-01", "channel": "Google", "signups": 42 },
    { "date": "2026-01-01", "channel": "Meta",   "signups": 17 }
  ]
}
```

`date` is required on every row. Send one row per day per combination of dimension values, and batch a whole day into one request rather than one request per row.

Each stored point comes back with its own hash, under the key **`id`** (for example `BEk2na2z79XVZqmr`). That hash is what the single-point `GET`, `PUT` and `DELETE` paths take. Keep it if you may need to correct the row later.

## How to work through it

1. **Read the schema first.** `GET` the metrics and the dimensions and compare against what you are about to send. Creating something that already exists is either an error or a duplicate, depending on which one it is (see the traps below).
2. **Create what is missing.** Metrics and dimensions first, data second.
3. **Send each day once.** Re-sending a day does not replace it. Track which dates you have sent.
4. **Correct a day by deleting and re-sending.** `GET /v1/integration-source-data` filtered to that date, `DELETE /v1/integration-source-data/{id}` for each point you are replacing, then `POST` the correct rows. To change one point whose hash you already have, `PUT` it instead.

## Reading a list back

All three list endpoints paginate, and **the default page size is 10**. A schema check that reads one page and concludes a metric is missing will then create a duplicate. Pass `per_page`, or follow the pagination links, or filter to the one record you are asking about.

Query parameters, on all three list endpoints:

- `per_page` — page size. Defaults to 10.
- `sort_field` — for metrics: `external_id`, `date`, `name`, `id`, `negative_ratio`. For dimensions: `external_id`, `name`, `type`, `id`. For data points: any key inside the stored row, defaulting to `date`.
- `sort_direction` — `asc` or `desc`. Defaults to `asc`.
- `filter` — a **JSON object, sent as a string**, for example `filter={"external_id":"signups"}`. Each entry matches on a substring, not on equality, so a filter for `signups` also matches `signups_paid`. Check the exact value in the response rather than trusting that one result means one match.

## Responses

- **Metric and dimension creates return `200`** with the created record under `data`, even though the published API reference says `201`. Treat any 2xx as success and read `data.id` rather than branching on the status code.
- **A data push returns `201`** with the array of stored points, each carrying its hash under `id`.
- `204` — deleted.
- `400` — the token is valid but is not connected to a source. The user has to connect it in source management.
- `401` — the `Authorization` header is missing, or the token is wrong.
- `409` — a **dimension** with that `external_id` already exists. Treat it as "already there" and move on.
- `422` — validation failed. Check that every required field is present and that each value matches the type you declared.
- `429` — rate limited. Retryable, see below.

## Rate limits

200 requests per minute per token. The `X-RateLimit-Remaining` header says how many are left. Batch rows into one request rather than sending one request per row. On `429`, back off and retry; a rate limit is temporary and never means the data was rejected.

## Traps

**Sending a day twice adds it twice.** The push endpoint always inserts. It never matches an existing row and updates it. Send the same date and dimension values again and there are now two rows, and a `sum` metric counts both. This is the single most likely way to get wrong numbers. Send each day once, and correct by deleting the hash and re-sending.

**A duplicate metric is not rejected.** Only dimensions return `409`. `integration_metrics` has no unique constraint, so posting the same metric `external_id` twice silently creates a second metric, and the widget picker then shows two entries with the same name. Read the metric list before creating.

**`PUT` on a data point replaces the whole row.** The body you send becomes the stored row in full. Any key you leave out is gone, not kept. Send every field, including `date`.

**Deleting the source in the web app destroys its data.** There is no recovery, and no export step warns first. Never suggest deleting and recreating a Custom API source as a fix.

**Daily granularity only.** One point per day. There is no hourly resolution, and the accumulator is what produces weekly and monthly figures.

## Metric type and how it renders

| `type` | `accumulator` | Shown as | Rolled up as |
|---|---|---|---|
| `int` | `sum` | `43` | sum of the days |
| `currency` | `average` | `$11.70` | mean across the days |
| `float` | `average` | `2.35` | mean across the days |

## End to end

```bash
BASE="https://api.whatagraph.com"
TOKEN="<ACCESS_TOKEN>"
H=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")

# Read the schema before creating anything.
curl -s "$BASE/v1/integration-metrics?per_page=100" "${H[@]}"
curl -s "$BASE/v1/integration-dimensions?per_page=100" "${H[@]}"

# Create what is missing.
curl -s -X POST "$BASE/v1/integration-metrics" "${H[@]}" \
  -d '{"name":"Signups","external_id":"signups","type":"int","accumulator":"sum","negative_ratio":false}'
curl -s -X POST "$BASE/v1/integration-dimensions" "${H[@]}" \
  -d '{"name":"Channel","external_id":"channel","type":"string"}'

# Push one day, all its dimension combinations in one request.
curl -s -X POST "$BASE/v1/integration-source-data" "${H[@]}" -d '{"data":[
  {"date":"2026-01-01","channel":"Google","signups":42},
  {"date":"2026-01-01","channel":"Meta","signups":17}
]}'

# Correct that day: find the points, delete them, send the right ones.
curl -s "$BASE/v1/integration-source-data?filter=%7B%22date%22%3A%222026-01-01%22%7D" "${H[@]}"
curl -s -X DELETE "$BASE/v1/integration-source-data/BEk2na2z79XVZqmr" "${H[@]}"
```

Then build the widget: pick the Custom API source, choose your metrics and dimensions, and filter on whichever dimension separates one client or entity from another.

## Where to go next

- Building the widget on top of the data: `whatagraph-widgets`.
- Checking what is connected and which metrics a source offers: `whatagraph-sources-and-data`.
- Numbers that look wrong after a push: re-read the duplicate-row trap above first, then `troubleshooting-data-issues`.
