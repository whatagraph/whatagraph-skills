---
name: whatagraph-dynamic-integrations
type: domain
group: data_connections
description: Build a working Whatagraph data source from a third-party API's documentation, entirely through the MCP server, with no code deploy. Covers the draft to connect lifecycle, the manifest/spec/schema artifacts, authentication shapes, source discovery, report types, pagination, and the guards that restrict what a stored definition may contain. Use when asked to add or connect a data source Whatagraph does not already support, or to fix, extend, or re-sync one that was built this way.
required_tools:
  - list-dynamic-integrations
  - manage-dynamic-integrations
optional_tools:
  - tool_name: list-sources
    purpose: Confirm the discovered sources appear as normal channel sources after connect.
  - tool_name: fetch-data
    purpose: Verify stored numbers against the provider's own reporting before building widgets.
  - tool_name: delete-dynamic-integrations
    purpose: Tear down an integration that was drafted but never connected.
---

# Dynamic integrations

Tools covered: `manage-dynamic-integrations` (the whole build), `list-dynamic-integrations` (state
and version history), `delete-dynamic-integrations` (tear down an unconnected attempt).

You can add a data source Whatagraph does not support by writing its connector definition
yourself. The definition is stored as data rather than shipped as code, so nothing is deployed and
nobody writes PHP. Once published and connected it behaves like any other channel: it appears in
the catalog and in Source Management, its data is stored on the normal sync cadence, and widgets,
reports and `fetch-data` read it from storage.

You author three artifacts.

| Artifact | What it holds |
|---|---|
| `manifest_yaml` | The streams. Which endpoints to call, how to page them, how to shape each record, and how sources are discovered. |
| `spec_yaml` | The credentials to ask the user for, and the flow that proves them against the live API. |
| `schema` | The report types, dimensions and metrics a user picks from when building a widget. |

**A definition is far more restricted than a Whatagraph-shipped connector.** Read
[What a stored definition may contain](#what-a-stored-definition-may-contain) before writing any
YAML. Most wasted cycles come from copying an idiom that only built-in connectors are allowed.

## Work in this order

```
draft -> test-auth -> sample -> publish -> connect
```

Each step is gated on the one before it. Every response carries a `next` field saying what to do,
so follow that rather than guessing.

| Action | What it does | Key inputs |
|---|---|---|
| `draft` | Validates and stores a new version of the definition. Every guard runs here. Omit `channel_id` to create a new integration; the response returns the id you use for everything after. Pass `channel_id` to append a version to an existing one. | `title`, `manifest_yaml`, `spec_yaml`, `schema`, `host_allowlist` |
| `test-auth` | Runs the spec's `access_acquisition_flow` against the live API. Failure stores nothing. Success stores the credentials for the steps that follow. | `channel_id`, `credentials` |
| `sample` | Reads live records from one stream through the whole engine, using the stored credentials. Publishing is gated on this. | `channel_id`, `stream`, `source_external_id`, `source_options`, `limit`, `last_days` |
| `publish` | Promotes the newest version to live, writes the report type, dimension and metric rows, and syncs the storage template. | `channel_id` |
| `connect` | Runs the `source_fetcher` against the live API and attaches the discovered sources to the team. | `channel_id`, `source_external_ids` |
| `resync` | Re-fetches already-stored data after a definition fix. | `channel_id`, `source_external_id`, `from`, `till` |

`limit` defaults to 10 (max 100) and `last_days` to 30. Every action after the first `draft` needs
`channel_id`.

**Never skip `test-auth` and `sample`.** Static validation accepts YAML that fails against the real
API, and `publish` refuses a version that has never sampled successfully. Sample **every** data
stream, not just one, and show the records to the user so they can confirm the values before you
publish. That is the only cheap moment to catch a wrong field mapping.

**Re-drafting cannot affect live reports.** A new version is stored with the live pointer left
where it is, so only `publish` changes what the data path reads. A re-draft also clears the sample,
so sample again before re-publishing.

Use `list-dynamic-integrations` at any point to see an integration's live version, its newest
version, and whether that newest version has been sampled.

## What a stored definition may contain

These restrictions exist because a definition is a template the server evaluates on behalf of one
team. Built-in connectors are deliberately not held to them, so an idiom copied from Whatagraph's
own connector YAML, or from documentation describing it, is frequently rejected here.

### Interpolation is substitution only

A `{{ ... }}` expression may be **one dotted path into the interpolation context, and nothing
else**:

```
{{ api_token }}                            a submitted input
{{ integration_key.options.api_token }}    nested
{{ integration_source.external_id }}       the connected source's id
{{ date_range.from.date }}                 dates arrive already rendered
{{ runtime.nonce }}                        a value nothing else collides with
```

Everything else is refused at `draft`: filters (`|`), method calls, arithmetic, comparisons,
ternaries, null-coalescing, and `{% ... %}` statements of any kind. The guard reads the raw YAML
and the parsed document, so a comment or a YAML escape does not get one through.

| Do not write | Write instead |
|---|---|
| `{{ date_range.from.format('Y-m-d') }}` | `{{ date_range.from.date }}` |
| `{{ date.getTimestamp() }}` | `{{ date_range.from.epoch }}` |
| `{{ date.getTimestamp() * 1000 }}` | `{{ date_range.from.epoch_ms }}` |
| `{{ api_key\|sha256 }}` | `{{ runtime.nonce }}` |
| `{{ x ?? 'default' }}` or `{{ x ?: 'y' }}` | Nothing. Fetch the value in a stream and reference it, or hardcode the constant. |
| `{% if ... %}` | A separate stream, or a request filter. |

There is no format string to pass and no method to call, because each date is published
pre-rendered under several keys:

| Key | Example |
|---|---|
| `date` | `2026-03-14` |
| `compact` | `20260314` |
| `year` / `month` | `2026` / `2026-03` |
| `month_name` / `month_number` | `March` / `3` |
| `day_of_month` | `14` |
| `epoch` / `epoch_ms` | seconds / milliseconds |
| `iso_zulu` | `2026-03-14T00:00:00Z` |
| `datetime_local` | `2026-03-14 00:00:00` |
| `day_end.datetime_local` | `2026-03-14 23:59:59` |
| `source_tz.iso_zulu` / `team_tz.iso_zulu` | the same instant read in the source's or the team's timezone |

`date_range.from` and `date_range.till` both publish all of these, and `date_range.till_exclusive`
is the day after `till`, for an API whose range end is exclusive.

The context also holds `integration_key` (`external_id`, `email`, `name`, `options`),
`integration_source` (`id`, `external_id`, `name`, `options`), `integration` (`id`, `service`,
`title`), `report_type`, `metrics`, `dimensions`, and every field of the record currently being
processed, at the top level.

### No YAML tags, but anchors are fine

A stored definition is parsed with tag support off, so `!int`, `!float` and `!array` are rejected
with `Tags support is not enabled`. Write the plain value instead: `task_count: 1`, not
`!int "1"`. A metric's declared `type` coerces the value, so the cast is not needed.

Anchors and aliases **do** work, and you should use them. Every requester needs the same three
middlewares and the same authenticator, so declare each once in a `definitions:` block and alias it
in:

```yaml
definitions:
  <<: &retry
    type: RetryHandler
  <<: &logger
    type: RequestLogger
  <<: &classifier
    type: ResponseClassifier
    response_filters:
      - type: StatusCodeResponseFilter
        http_codes: [ 429 ]
        action: RETRY
        throw: RateLimitExceeded
      - type: StatusCodeResponseFilter
        http_codes: [ 500, 502, 503, 504 ]
        action: RETRY
        throw: TempDataGeneration
  <<: &auth
    type: ApiKeyAuthenticator
    header: "Authorization"
    token_provider:
      type: InterpolatedTokenProvider
      token: "{{ integration_key.options.api_token }}"
```

### Hosts are declared and exactly matched

`host_allowlist` is required, and an empty list is rejected because it could reach nothing. Every
request is checked against it: HTTPS only, exact host match (a subdomain of a declared host is not
declared), private and reserved addresses refused, and each redirect hop re-checked. If the spec's
auth endpoint is on a different host from the data endpoints, declare both.

For a per-tenant base URL the host is fixed once a credential is connected, so declare that
concrete host.

### The spec may not use database validation rules

`exists:` and `unique:` are rejected anywhere in the spec, comments included, because they would
let a stored definition probe database tables through credential validation. Use the other Laravel
rules freely (`required`, `string`, `max:256`).

### A schema entry declares only what is stored

A `schema.json` copied from anywhere else carries much more than this, and the extra keys are
rejected rather than silently dropped:

| Entry | Top level | Under `options` |
|---|---|---|
| report type | `external_id`, `name`, `options` | `groups` |
| dimension | `external_id`, `name`, `type`, `options` | `groups`, `report_types` |
| metric | `external_id`, `name`, `type`, `options` | `groups`, `report_types` |

Scope a field to certain report types with `options.report_types`.

Dimension types: `string`, `date`, `datetime`, `timestamp`, `int`, `float`, `list`.
Metric types: `int`, `float`, `money`, `percent`.

A few synonyms from shipped schemas are coerced rather than rejected, so a native schema mostly
ports as it is: metric `seconds`, `duration`, `decimal`, `number` become `float` and `integer`
becomes `int`; dimension `boolean`, `bool`, `text` become `string`, `integer` becomes `int` and
`number` becomes `float`. A genuinely unknown type still fails.

## The manifest

```yaml
source_fetcher:
  stream: "workspaces"
  factory:
    type: InterpolatedSourceFactory
    attributes:
      external_id: "{{ id }}"
      name: "{{ name }}"
      options:
        workspace_name: "{{ name }}"

streams:
  - type: DeclarativeStream
    name: "workspaces"
    retriever:
      type: SimpleRetriever
      requester:
        type: HttpRequester
        http_method: "GET"
        url_base: "https://api.example.com/v2"
        path: "team"
        request_headers:
          type: SimpleRequestHeaders
          headers:
            Accept: "application/json"
        authenticator: *auth
        middlewares:
          - <<: *retry
          - <<: *logger
          - <<: *classifier
      paginator:
        type: NoPagination
      record_selector:
        type: RecordSelector
        extractor:
          type: DpathExtractor
          field_path: [ "teams" ]

  - type: DeclarativeStream
    name: "tasks"
    retriever:
      type: SimpleRetriever
      requester:
        type: HttpRequester
        http_method: "GET"
        url_base: "https://api.example.com/v2"
        path: "team/{{ integration_source.external_id }}/task"
        request_headers:
          type: SimpleRequestHeaders
          headers:
            Accept: "application/json"
        authenticator: *auth
        middlewares:
          - <<: *retry
          - <<: *logger
          - <<: *classifier
        query_parameters:
          type: SimpleQueryParameters
          parameters:
            date_updated_gt: "{{ date_range.from.epoch_ms }}"
            date_updated_lt: "{{ date_range.till.epoch_ms }}"
      paginator:
        type: SimplePaginator
        pagination_strategy:
          type: PageIncrement
          page_size: 100
          initial_page: 0
        page_token_option:
          type: RequestOption
          inject_into: "query_parameters"
          field_path: [ "page" ]
      record_selector:
        type: RecordSelector
        extractor:
          type: DpathExtractor
          field_path: [ "tasks" ]
    transformations:
      - type: AppendValues
        map:
          status: "{{ status.status }}"
          task_count: 1
      - type: NormalizeEpochTimeValues
        datetime_value_unit: "milliseconds"
      - type: MapToIntegrationData
```

### A stream's name comes from `name`

Nothing reads the YAML key a stream sits under. The engine reads `name`, and a stream without one
is rejected at draft, because an unnamed stream cannot be reached by `source_fetcher` and every
unnamed stream collides under one name.

A name must start with a letter and use only `a-z`, digits, underscores and dashes. Lowercase it:
the report-type match below is exact, so a stream named `Tasks` never serves report type `tasks`.

**A stream that a template reads by name cannot contain a dash.** Twig reads
`{{ campaigns-list.id }}` as a subtraction, and the path rule excludes a dash, so the definition is
refused. This applies to the parent of a `ChainedStream`, which the child references as
`{{ parent_name.field }}`. Use underscores there. A dash is fine in any other stream name.

For parent-child fetching, `ChainedStream` takes `require_records: true` to drop a parent record
whose child stream returned nothing.

### Every report type needs a stream of the same name

A stream is bound to a report type by exact name. If `schema.report_types` has
`external_id: orders`, the manifest needs a stream named `orders`, or one stream named `general` to
serve them all. A mismatch is rejected at draft.

One platform is one integration. Different grains (account, campaign, ad; orders, order items,
abandoned carts) are **report types**, never separate integrations. Each report type gets its own
stored table under the same per-source transfer.

### Every data stream ends with `MapToIntegrationData`

It turns a raw API record into the `{date, dimensions, metrics}` row that storage reads. Leaving it
off is rejected at draft, because nothing later would report it: `sample` returns records, publish
creates the table, connect attaches the source, and the first real fetch then writes one row per
date with every dimension `N/A` and every metric `0`. A fetch that stored wrong values is not a
failed job, so nothing retries it and no error reaches anyone.

Put it last, as a sibling of `retriever:` on the stream the report type is matched to. If that
stream is a `ChainedStream`, or is wrapped in a `DateChunkedStream`, the transformation goes on the
composite, not on each inner stream.

### Every schema field must be a top-level key before the mapping runs

`MapToIntegrationData` looks up each declared metric and dimension by its `external_id` and reads
the value at that key. A missing metric becomes `0` and a missing dimension becomes `N/A`, with no
warning, so a field nested one level down is silently empty. Two cases come up constantly:

- **A nested value.** `{"status": {"status": "open"}}` against a dimension `status` stores the
  array, not `"open"`. Lift it first with `AppendValues`: `status: "{{ status.status }}"`.
- **A count.** No API returns a `task_count` field. When one record is one thing being counted,
  append the literal `task_count: 1` and let the metric's accumulator sum it.

Dates need the same care. A dimension declared `datetime` whose API value is an epoch offset needs
`NormalizeEpochTimeValues` before the mapping (`datetime_value_unit: "milliseconds"`, or
`date_value_unit` for a date dimension). A formatted string needs `NormalizeTimeValues`. Without
one, every row silently takes the fetch window's start date.

Other transformations available: `OnlyKeys`, `ReplaceKeys`, `Collapse`.

### Do not use these components

Each is rejected at draft with its replacement named.

| Rejected | Use instead |
|---|---|
| `DefaultPaginator` | `SimplePaginator` with a `pagination_strategy`, or `NoPagination` |
| `TokenPaginator` | `SimplePaginator` with a `CursorPagination` strategy |
| `MapRawDataToIntegrationData` | `NormalizeTimeValues` (or `NormalizeEpochTimeValues`) then `MapToIntegrationData` |

## Source discovery

`source_fetcher` is required, with both a `stream` and a `factory`. It runs at `connect` and
decides what sources exist.

`attributes.name` and `attributes.external_id` are both required. They are evaluated against each
discovery record with **its keys at the top level**, so a record `{"id": "123", "name": "Acme"}`
gives you `{{ id }}` and `{{ name }}`, not `{{ record.id }}`. Compose freely:
`"{{ name }} ({{ id }})"` is fine.

An expression that resolves to nothing is rejected, and the error lists the keys the record
actually had, so check there first when a name comes out empty. An empty `external_id` would
otherwise collide with every other empty one on the upsert key and collapse a whole discovery run
into one source.

If discovery returns an envelope rather than a bare array, the extractor's `field_path` must name
the key holding the list. `field_path: []` is correct **only** when the response root is itself an
array. Against `{"data": [...], "meta": {...}}` an empty path treats the whole envelope as one
record with no per-entity `id`, which is the most common cause of a nameless single source.

`DpathExtractor` takes two other options worth knowing. `optional: true` says a response
carrying nothing at that path is normal rather than an unrecognised shape, which is what an
endpoint returning an empty body for a quiet day needs. `wrap_array: true` says what was found is
one record rather than a list of them.

The fetcher stream must not use `MapToIntegrationData` or `ReplaceUniqueMetricValues`. Both need a
fetch date range and there is none during discovery, so both are rejected at draft. End that stream
after `AppendValues` or `OnlyKeys`.

`name` applies to sources discovered afterwards. Changing the expression does not rename sources
that already exist, because a user may have renamed one themselves and a reconnect must not undo
that.

**A single-source API still needs a stream-based fetcher.** Point it at the API's `me` or `account`
endpoint. One source is fine.

### Deciding what is a credential and what is a source

- If an input changes **who you are to the API**, it belongs in `connection_specification`.
- If it changes **what data you get**, it belongs in `source_specification`.
- If the API can **enumerate the choices itself**, it belongs in the `source_fetcher`.

Never hardcode an account or workspace id in a stream path. Read it from
`{{ integration_source.external_id }}`, or from `{{ integration_source.options.* }}` for anything
else the fetcher persisted, so every connected source works. Onboarding another client is another
credential on the same integration, never a second integration.

Putting a data parameter in `connection_specification` because it is convenient gives you one
account per value, which is the wrong grain and pollutes the account list.

### Connect attaches what the team chooses

When discovery finds one source, `connect` attaches it. When it finds several, nothing is attached
and the response returns them as `candidates`, because which sources a team wants is the team's
call and each one costs a source credit. Ask, then call `connect` again with `source_external_ids`
naming the chosen ones.

`connect` is idempotent. Reconnecting after a removal restores the same source rows, so widgets
built on them survive.

## The spec

```yaml
definitions:
  <<: &validate
    type: ValidationFlowStep
    rules:
      name: "required|string|max:256"
      api_token: "required|string|max:256"

  <<: &check_connection
    type: RequestFlowStep
    requester:
      type: HttpRequester
      http_method: "GET"
      url_base: "https://api.example.com/v2"
      path: "user"
      request_headers:
        type: SimpleRequestHeaders
        headers:
          Accept: "application/json"
      authenticator:
        type: ApiKeyAuthenticator
        header: "Authorization"
        token_provider:
          type: InterpolatedTokenProvider
          token: "{{ api_token }}"
      middlewares:
        - type: RetryHandler
        - type: RequestLogger
        - type: ResponseClassifier
          response_filters:
            - type: StatusCodeResponseFilter
              http_codes: [ 401, 403 ]
              action: FAIL
              throw: Validation
              error_message: "The API rejected this token."
    record_selector:
      type: RecordSelector
      extractor:
        type: DpathExtractor

  <<: &store
    type: IntegrationKeyStoreFlowStep
    external_id: "{{ runtime.nonce }}"
    name: "{{ name }}"
    options:
      name: "{{ name }}"
      api_token: "{{ api_token }}"

connection_specification:
  properties:
    name:
      type: string
      required: true
      label: "Connection name"
    api_token:
      type: string
      required: true
      label: "API token"
      description: "Where to find it in the provider's own settings."
  authorization_flow:
    type: apiKey
    access_acquisition_flow:
      - *validate
      - *check_connection
      - *store
```

### Rules the spec will fail on

**`authorization_flow` goes under `connection_specification`**, not at the spec's top level. This
is the single most common mistake, and it is rejected at draft saying so. `properties` nests the
same way, and declaring `properties` *inside* the flow is refused because two lists could then
disagree.

**A token-only API still needs an `access_acquisition_flow`.** Its steps *are* the request that
`test-auth` makes, so an empty or missing flow leaves nothing to verify. One `RequestFlowStep`
against a cheap authenticated endpoint is enough.

**The flow is a bare list.** There is no `steps:` wrapper.

**The step types are** `ValidationFlowStep`, `PermissionValidationFlowStep`, `RequestFlowStep` and
`IntegrationKeyStoreFlowStep`. Nothing else. End with `IntegrationKeyStoreFlowStep` to store the
proven credentials, and give it a `name` — the connect modal needs one.

**Classify auth failures.** Without a `ResponseClassifier` filter for 401/403 with `action: FAIL`,
`test-auth` reports success for a token the API just rejected. Auth-flow error text is user-facing,
so write `error_message` for a person reading it in the connect modal.

**`request_headers`, `query_parameters` and `request_body` are typed components.** Each needs its
own `type` (`SimpleRequestHeaders`, `SimpleQueryParameters`, `SimpleRequestBody`) with the values
nested under `headers`, `parameters` or `data`. A bare map is rejected.

**An authenticator is not a middleware.** It goes under the requester's `authenticator:` key.
Putting it in `middlewares:` fails, because they are different registries.

**`url_base` must not end in a slash.** The engine adds the separator, so a trailing slash produces
a double slash, which providers answer with a redirect or a 404.

**Use `url_base` plus `path`,** not a single `url` key.

### The credential lives in two different places

This is the failure that looks like it works: `test-auth` passes, and then `sample` returns the
API's own "missing credentials" error. The two moments read from different places.

| Where | Token expression | Why |
|---|---|---|
| The spec's auth flow | `{{ api_token }}` | The submitted inputs. Nothing is stored yet. |
| A manifest data stream | `{{ integration_key.options.api_token }}` | The stored key, written by the flow. |

So the `IntegrationKeyStoreFlowStep` that ends the flow must put the token into `options` under the
same name the manifest reads back.

### Authentication shapes

**There are no platform credentials.** A shipped connector reads its OAuth2 client id and secret,
service-account keys and per-tenant hosts from server configuration. A dynamic integration's
`integration_config` holds only its own id and a few capability flags, so anything of that kind
must be collected as a `connection_specification` property and read back from
`integration_key.options`.

| Shape | How |
|---|---|
| API key in a header | `ApiKeyAuthenticator` with an `InterpolatedTokenProvider`. Set `header` and, if the API wants one, the prefix in the token value. Many APIs want the token verbatim with no `Bearer `. |
| Key or secret in the query string | `NoAuth`, with the values as `SimpleQueryParameters` read from `integration_key.options`. |
| Keyless or public API | Declare no credential properties and give `IntegrationKeyStoreFlowStep` a static `external_id`, so there is one invisible singleton account rather than a new one per connect. |
| Client credentials | An `apiKey` flow whose `access_acquisition_flow` runs a token-exchange `RequestFlowStep` first, then stores the access token alongside the client id and secret. `client_credentials` is not a flow type. |
| OAuth1 (HMAC) | `OAuth1Authenticator` as a requester middleware, with `consumer_key`, `consumer_secret`, `token_key`, `token_secret` and `signature_method`, all read from stored options. |
| OAuth2 refresh | Collect the client id, secret and refresh token as properties, and have the token provider's refresh body read them from `integration_key.options`. Store all three, or the refresh at fetch time has nothing to read. |

There is no hosted OAuth redirect for a dynamic integration, so use a credential the user already
holds: an API key, a personal access token, or a long-lived refresh token pasted into a property.
If an auth style can only be signed with a secret held on the server, say so rather than shipping a
definition that fails authentication silently.

## Pagination

An API that returns everything in one response needs no paginator: leave it out, or state
`NoPagination`. Get it wrong in the other direction and the failure is silent, because the engine
chunks a backfill by period and a single chunk easily exceeds one page. Without a paginator you
store page 1 of every chunk and the connector looks like an API with little data in it.

A missing `page_token_option` has the same effect: the page parameter is never sent, so you get
page 1 forever.

```yaml
paginator:
  type: SimplePaginator
  pagination_strategy:
    type: PageIncrement          # or OffsetIncrement / CursorPagination / LinkHeaderPagination
    page_size: 100
    initial_page: 0              # 0- or 1-indexed per the API; the default is 1
  page_token_option:
    type: RequestOption
    inject_into: "query_parameters"   # query_parameters | headers | body | path
    field_path: [ "page" ]            # a list, not a string
```

- `PageIncrement` stops when a page returns fewer records than `page_size`.
- `OffsetIncrement` steps by `page_size`; inject `offset` rather than `page`.
- `CursorPagination` needs a `cursor_value` naming where the next token sits in the response body.
- `LinkHeaderPagination` is for an API that returns the next page in a `Link` header rather than
  the body (`Link: <...?page=2>; rel="next"`), which `CursorPagination` cannot see. Set
  `extract_param` to the query parameter carried in that URL. It stops when the API omits
  `rel="next"`.
- Add a `page_size_option` (same shape) only if the API takes a page-size parameter.

Sampling cannot prove pagination works, because a broken paginator still returns page 1 and 10
rows look fine. After connect, check that a multi-month total exceeds one page. A total that is
exactly `page_size` times the number of chunks is the signature of a paginator that is not working.

## Column-oriented responses

Some APIs return parallel arrays rather than a list of objects, where index `i` across the arrays
is one record. Time-series endpoints do this often:

```json
{ "daily": { "time": ["2026-01-01", "2026-01-02"], "temperature_max": [5.2, 6.1] } }
```

`DpathExtractor` cannot turn that into rows, because its path resolves to one object of columns.
Use `ColumnsToRowsExtractor`, which zips the sibling arrays into one record per index:

```yaml
record_selector:
  type: RecordSelector
  extractor:
    type: ColumnsToRowsExtractor
    field_path: [ "daily" ]                       # the object holding the arrays; empty = the root
    keys: [ "time", "temperature_max" ]           # optional; omit to zip every array-valued key
```

Shorter columns are null-filled to the longest length. Map as usual afterwards: normalize the date,
then `MapToIntegrationData`.

## Errors and retries

Classify the API's responses with `ResponseClassifier` filters on each requester. As a safety net
the engine already treats 429 as a rate limit and 408 and 5xx as server errors, and retries them
even when no filter matches, so a forgotten filter no longer fails a whole backfill permanently.
That is a net, not a substitute:

- **429 is never a failure.** Retry it. A rate limit must never mark a source as broken or ask the
  user to reconnect.
- **401 and 403 need an explicit filter**, in the auth flow and on data streams. They do not
  default to the reconnection flow.
- **Missing data is not an error.** A 404 on a day with no records should be `action: IGNORE`, and
  a response that legitimately carries nothing at the extractor's `field_path` needs
  `optional: true` on that extractor, not a failure.
- Anything non-transient that matches no filter surfaces the raw response body to the caller, which
  is your signal to add a filter for that status or shape.

## Getting a definition right

Read the API's **official documentation** for field meanings, not a sample response. A sample tells
you what one account happened to return, not what a field means or whether it is always present.

Start smaller than you think: one report type, one data stream, three or four dimensions, one or
two metrics. Get that green through `connect`, confirm real numbers with the user, then re-draft to
add more. A re-draft is cheap and cannot affect what is live.

When sampling a data stream before any source exists, stand in for what a connected source would
carry: `source_external_id` fills `{{ integration_source.external_id }}` and `source_options` fills
`{{ integration_source.options.* }}`. Values a user supplies per source are collected by the spec's
`source_specification.save_flow` after connect, not passed here.

After connect, compare a few dates from `fetch-data` against the provider's own reporting before
building widgets. Attribution lag and timezone differences show up here and nowhere else.

## Evolution

Republishing an already-connected definition is additive: new fields and new report types
propagate, and only the new tables backfill. Renames and removals do not exist, so a rename is a
new `external_id`.

**A fix is not retroactive.** Correcting a definition and republishing changes how future fetches
behave. Data already stored stays wrong until you `resync` the range, because a fetch that
succeeded with wrong values is not a failed job and nothing re-runs it on its own.

Use `delete-dynamic-integrations` to tear down an integration that was drafted but never connected.
It is refused once sources exist; remove those first.

## What the user sees

- **Connect modal**: the integration appears in the catalog with the inputs the spec declares. A
  keyless connector skips the credential form.
- **Report drawer**: under stored data, since a dynamic integration is storage-backed.
- **Widget picker**: the full widget set, per report type.

**It belongs to that team alone.** No other team can see it, list it, connect to it or read its
data. An id belonging to another team reads as absent rather than forbidden.

## When something goes wrong

| Symptom | Cause |
|---|---|
| `draft` rejected | A guard caught it, and the message names the field and the fix. Read it rather than guessing. |
| An error naming a missing key | The engine wanted a key that part of the definition does not declare. Add it where the message says and re-draft. |
| `test-auth` fails | The credential or the flow. Check the endpoint, the header shape, and whether the token needs a prefix. |
| `test-auth` passes but `sample` says credentials are missing | The data stream reads `{{ api_token }}` instead of `{{ integration_key.options.api_token }}`, or the store step did not persist it under that name. |
| `sample` returns nothing | Usually the extractor's `field_path` does not match the response shape, or the date filter excludes everything. |
| `sample` returns one nameless record | `field_path: []` against an enveloped response. Name the key holding the list. |
| Connect rejected for an empty source identity | The factory's `name` or `external_id` resolved to nothing. The error lists the keys the record had. |
| Only ever one page of records | The paginator, or a missing `page_token_option`. |
| A blocked request | The host is not in `host_allowlist`, or the URL is not HTTPS. |
| Every dimension `N/A` and every metric `0` | The stream never mapped its records, or a schema field is not a top-level key by the time the mapping runs. |
| Every row dated to the range start | No `NormalizeTimeValues` or `NormalizeEpochTimeValues` before the mapping. |
| Data still wrong after a fix | Republishing does not correct stored data. `resync` the range. |
