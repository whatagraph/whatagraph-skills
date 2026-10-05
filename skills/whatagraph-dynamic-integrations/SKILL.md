---
name: whatagraph-dynamic-integrations
type: domain
group: data_connections
description: Build a working Whatagraph data source from a third-party API's documentation, entirely through the MCP server, with no code deploy. Covers the draft to connect lifecycle, the manifest/spec/schema artifacts, where every key nests, authentication shapes, the connected account and its credentials, source discovery, report types, pagination, and the guards that restrict what a stored definition may contain. Use when asked to add or connect a data source Whatagraph does not already support, or to fix, extend, or re-sync one that was built this way.
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
| `spec_yaml` | The inputs to ask the user for, the flow that proves them against the live API, and the connected account the engine stores. |
| `schema` | The report types, dimensions and metrics a user picks from when building a widget. |

**A definition is far more restricted than a Whatagraph-shipped connector.** Read
[What a stored definition may contain](#what-a-stored-definition-may-contain) and
[Where every key goes](#where-every-key-goes) before writing any YAML. Most wasted cycles come
from copying an idiom that only built-in connectors are allowed, or from putting a valid key one
level too deep.

## Work in this order

```
draft -> test-auth -> sample -> publish -> connect
```

An `oauth2` definition replaces `test-auth` with a stop for the user, `set-oauth-client` and
`authorize` (see [OAuth2](#oauth2)):

```
draft -> STOP: user registers the redirect URLs -> set-oauth-client -> authorize -> user approves -> sample -> publish -> connect
```

Each step is gated on the one before it. Every response carries a `next` field saying what to do,
so follow that rather than guessing.

| Action | What it does | Key inputs |
|---|---|---|
| `draft` | Validates and stores a new version of the definition. Every guard runs here, including building every component the engine would build. Omit `channel_id` to create a new integration; the response returns the id you use for everything after. Pass `channel_id` to append a version to an existing one. | `title`, `manifest_yaml`, `spec_yaml`, `schema`, `host_allowlist` |
| `set-oauth-client` | `oauth2` only. Stores the client id and secret of the OAuth application the user registered with the provider. Never returns them. | `channel_id`, `client_id`, `client_secret` |
| `authorize` | `oauth2` only, in place of `test-auth`. Returns `authorize_url`, a Whatagraph link the user opens to approve access. The callback stores the connected account. | `channel_id` |
| `test-auth` | Runs the spec's `access_acquisition_flow` against the live API, on the newest draft. Failure stores nothing. Success stores the connected account for the steps that follow. | `channel_id`, `credentials` |
| `sample` | Reads live records from one stream of the newest draft through the whole engine, using the stored account. Publishing is gated on this. | `channel_id`, `stream`, `source_external_id`, `source_options`, `limit`, `last_days` |
| `publish` | Promotes the newest version to live, writes the report type, dimension and metric rows, and syncs the storage template. | `channel_id` |
| `connect` | Runs source discovery on the live version against the live API and attaches the discovered sources to the team. | `channel_id`, `source_external_ids` |
| `resync` | Re-fetches already-stored data after a definition fix. | `channel_id`, `source_external_id`, `from`, `till` |

`limit` defaults to 10 (max 100) and `last_days` to 30 (max 365). `sample` reads the last declared
stream when `stream` is omitted, so name it explicitly. Every action after the first `draft` needs
`channel_id`. Deleting is not an action here; it is the separate `delete-dynamic-integrations`
tool.

**All validation happens at `draft`.** `publish` does not re-validate. It only checks that the
newest version has a successful sample.

**Never skip `test-auth` and `sample`.** Static validation accepts YAML that fails against the real
API, and `publish` refuses a version that has never sampled successfully. Sample **every** data
stream, not just one, and show the records to the user so they can confirm the values before you
publish. That is the only cheap moment to catch a wrong field mapping.

**Re-drafting cannot affect live reports.** A new version is stored with the live pointer left
where it is, so only `publish` changes what the data path reads. A re-draft also clears the sample,
so sample again before re-publishing.

**The title is the exception: it applies at draft.** A re-draft renames the integration
immediately, even when it is published, so the team sees the new name in the connect modal before
anything is published. The first draft may append " (2)" when the team already has a connector with
that name. Re-draft with the `title` the first draft returned, unless the user asked for a
different name. Never re-draft a published integration just to test how something renders.

Use `list-dynamic-integrations` at any point. Each entry shows `status`, `live_version`,
`newest_version`, `has_unpublished_draft`, `newest_version_sampled` and `connected_source_count`.
Passing `channel_id` adds the `host_allowlist` and every version with its `sampled_at` and
`published_at`.

## Where every key goes

Every component accepts a fixed set of keys, and a key it does not read is refused at `draft` with
the list it does accept:

```
HttpRequester (the `requester` block) does not accept `record_selector`. It accepts: authenticator, ...
```

That error means the key is real but sits one level too deep or too shallow. Move it to the block
the table names, and do not remove it.

| Block | Accepts | Common misplacement |
|---|---|---|
| stream (`DeclarativeStream`) | `name`, `retriever`, `transformations` | `transformations` put inside `retriever` |
| `retriever` (`SimpleRetriever`) | `requester`, `paginator`, `record_selector`, `middlewares` | `paginator` or `record_selector` put inside `requester` |
| `requester` (`HttpRequester`) | `url_base`, `path`, `http_method`, `authenticator`, `request_headers`, `query_parameters`, `request_body`, `body_format`, `content_type`, `middlewares`, `throw_exception_on_error` | `record_selector`, `paginator`, `url` |
| spec `RequestFlowStep` | `requester`, `record_selector` | `record_selector` put inside `requester` |
| spec `TokenExchangeFlowStep` | `requester`, `record_selector`, `refresh_token_field` | as above |
| `ExternalTokenProvider` | `requester`, `record_selector` | as above |
| `record_selector` (`RecordSelector`) | `extractor`, `filter` | `field_path` put directly on the selector |
| `DpathExtractor` | `field_path`, `optional`, `wrap_array` | |
| `paginator` (`SimplePaginator`) | `pagination_strategy`, `page_token_option`, `page_size_option`, `page_path_option` | `page_size` put on the paginator instead of the strategy |
| `RequestOption` | `inject_into`, `field_path` | |
| `ChainedStream` | `name`, `streams`, `conditions`, `transformations`, `require_records` | |
| `DateChunkedStream` | `name`, `stream`, and exactly one of `chunk_days` or `period` | `streams` (it takes one `stream`) |

**Every requester needs `RetryHandler`, `RequestLogger` and `ResponseClassifier` in its
`middlewares`**, including nested ones: a token provider's requester and an auth-flow step's
requester. A requester without all three is rejected at draft.

Two blocks are called `middlewares` and they are different registries. The requester's list takes
`RetryHandler`, `RequestLogger`, `ResponseClassifier`, `RateLimiter`, `ConcurrencyLimiter` and
similar. The retriever's list takes record middlewares such as `Filter`, `Sort`, `Flatmap` and
`Wrap`. An authenticator is neither: it goes under the requester's `authenticator:` key.

The nesting, in one picture:

```yaml
streams:
  - type: DeclarativeStream
    name: "orders"
    retriever:
      type: SimpleRetriever
      requester:                 # how to call the endpoint, nothing about the response
        type: HttpRequester
        url_base: "https://api.example.com/v2"
        path: "orders"
        authenticator: { ... }
        middlewares: [ ... ]
      paginator: { ... }         # beside requester, not inside it
      record_selector: { ... }   # beside requester, not inside it
    transformations: [ ... ]     # beside retriever, not inside it
```

A spec `RequestFlowStep` has the same split: `requester` and `record_selector` are siblings under
the step.

Other key-level errors read the same way. A missing required key says "`k` is required for ...",
a wrong value type says "`k` for ... must be ...", and an unknown `type` lists every accepted type
name. Read the message and fix that one thing.

## What a stored definition may contain

These restrictions exist because a definition is a template the server evaluates on behalf of one
team. Built-in connectors are deliberately not held to them, so an idiom copied from Whatagraph's
own connector YAML, or from documentation describing it, is frequently rejected here.

### Interpolation is substitution only

A `{{ ... }}` expression may be **one dotted path into the interpolation context, and nothing
else**:

```
{{ name }}                                a submitted input (spec only)
{{ integration_source.external_id }}      the connected source's id
{{ integration_source.options.region }}   something discovery or the source form stored
{{ date_range.from.date }}                dates arrive already rendered
{{ runtime.nonce }}                       a value nothing else collides with
```

Everything else is refused at `draft`: filters (`|`), method calls, arithmetic, comparisons,
ternaries, null-coalescing (`??`), and `{% ... %}` statements of any kind. The guard reads the raw
YAML and the parsed document, so a comment or a YAML escape does not get one through.
Documentation for shipped connectors sometimes shows `{{ x ?? '' }}` or `{{ key|sha256 }}`. Those
work only in shipped connectors.

| Do not write | Write instead |
|---|---|
| `{{ date_range.from.format('Y-m-d') }}` | `{{ date_range.from.date }}` |
| `{{ date.getTimestamp() }}` | `{{ date_range.from.epoch }}` |
| `{{ date.getTimestamp() * 1000 }}` | `{{ date_range.from.epoch_ms }}` |
| `{{ api_key\|sha256 }}` | `{{ runtime.nonce }}` |
| `{{ user ~ ':' ~ pass \| base64 }}` | `SuppliedBasicCredentialsTokenProvider` (see Authentication) |
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
is the day after `till`, for an API whose range end is exclusive. Both bounds are the start of
their day.

### What each position can read

The context depends on where the template sits.

| Position | Can read |
|---|---|
| Requests (`url_base`, `path`, headers, query, body) and the source factory | `integration` (`id`, `service`, `title`), `integration_key` (`id`, `external_id`, `email`, `name`, `options`), `integration_source` (`id`, `external_id`, `name`, `options`), `date_range`, `report_type`, `metrics`, `dimensions`, `runtime.nonce`, and parent stream records keyed by stream name |
| Transformations (`AppendValues` and similar) and `ChainedStream` parameters | the current record's fields at the top level, `integration`, `integration_source` with only a short fixed list of option keys, `date_range`, `dimensions`, `runtime.nonce`. No `integration_key`. |
| The spec's auth flow and `account` block | the submitted inputs at the top level, plus fields earlier steps added, `integration`, `runtime.nonce` |

So a value a transformation needs from the source must come through the record. Append it in the
request position, or read it from the record the API returned.

Credentials are not in any template context. See
[The connected account](#the-connected-account-and-its-credentials).

### No YAML tags, but anchors are fine

A stored definition is parsed with tag support off, so `!int`, `!float`, `!array` and `!include`
are rejected with `Tags support is not enabled`. Write the plain value instead: `task_count: 1`,
not `!int "1"`. A metric's declared `type` coerces the value, so the cast is not needed.

Anchors and aliases **do** work, and you should use them. Every requester needs the same three
middlewares and usually the same authenticator, so declare each once in a `definitions:` block and alias it
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
    type: TokenAuthenticator
    token_provider:
      type: SuppliedCredentialTokenProvider
      credential: api_token
    token_placement:
      type: HeaderTokenPlacement
      scheme: bearer
  url_base: &url_base "https://api.example.com/v2"
```

### Hosts are declared, exactly matched, and all must resolve

`host_allowlist` is required, and an empty list is rejected because it could reach nothing.

- Each entry is a bare host name such as `api.example.com`: no scheme, port, path or trailing
  dot. Write an internationalised name in its `xn--` form.
- Every request must use HTTPS on port 443. A literal `url_base` naming another port is rejected
  at draft.
- Matching is exact. A subdomain of a declared host is not declared. If the auth endpoint is on a
  different host from the data endpoints, declare both.
- **Every declared host must resolve to a public address.** Each request resolves and pins all of
  them, not only the one it calls, so one entry that does not resolve blocks every request. Do not
  declare a host "just in case".
- Redirects are followed only to declared hosts, and each hop is re-checked.
- **List the brand's own API host first.** The catalog icon is taken from the first entry.

For a per-tenant base URL, the host is fixed once a credential is connected, so declare that
concrete host.

A blocked request is a permanent authoring mistake. It is not retried and does not mark the source
errored.

### Components a stored definition may not use

Each of these is rejected at draft. The deprecated ones name their replacement in the error.

| Rejected | Use instead |
|---|---|
| `DefaultPaginator` | `SimplePaginator` with a `pagination_strategy`, or `NoPagination` |
| `TokenPaginator` | `SimplePaginator` with a `CursorPagination` strategy |
| `CombinedStream` | `ChainedStream` with `require_records: true` |
| `MapRawDataToIntegrationData` | `NormalizeTimeValues` (or `NormalizeEpochTimeValues`) then `MapToIntegrationData` |
| `ApiKeyAuthenticator`, `InterpolatedTokenProvider`, `BasicHttpAuthenticator` | `TokenAuthenticator` with a supplied-credential provider (see Authentication) |
| `OAuth1Authenticator`, `OAuth1FormSigner` | `OAuth1RequestSigner` |
| `JwtFormField` | `TokenAuthenticator` with `JwtKeyPairTokenProvider` |
| `IntegrationKeyStoreFlowStep`, `IntegrationKeyCredentialStoreFlowStep` | a `connection_specification.account` block |
| `IntegrationSourceStoreFlowStep` | a `source_specification.source` block |
| `ExternalAuthorizationFlowUrlBuilder` | an `AuthorizationFlowUrlBuilder` with a literal `url_base` (see [OAuth2](#oauth2)) |
| any component that builds a database query or reads Whatagraph's own systems rather than calling the provider's API | an HTTP request to the provider |

### The spec may not use database validation rules

The text `exists:` and `unique:` is rejected anywhere in the spec, comments included. Validation
rules are typed components (see [Validation rules](#validation-rules)), so there is no way to name
those rules anyway. Just keep the strings out of comments.

### A schema entry declares only what is stored

A `schema.json` copied from anywhere else carries much more than this, and the extra keys are
rejected rather than silently dropped:

| Entry | Top level | Under `options` |
|---|---|---|
| report type | `external_id`, `name`, `options` | `groups` |
| dimension | `external_id`, `name`, `type`, `options` | `groups`, `report_types` |
| metric | `external_id`, `name`, `type`, `options` | `groups`, `report_types` |

Scope a field to certain report types with `options.report_types`, listing declared report type
ids. A top-level `report_types` on a field is rejected.

**A metric `formula` is rejected.** A dynamic integration does not compute formulas. Declare the
parts as metrics of their own and combine them in a custom metric on the report.

**A metric or dimension `external_id` must be a plain identifier**: a letter or underscore, then
letters, digits or underscores, at most 300 characters. It becomes the stored field name, so it is
rejected rather than rewritten. When the provider's key is not a legal name (`cost-usd`,
`2xx_count`), rename it in the stream with `ReplaceKeys` and use the new name here.

Dimension types: `string`, `date`, `datetime`, `timestamp`, `int`, `float`, `list`.
Metric types: `int`, `float`, `money`, `percent`.

A few synonyms from shipped schemas are coerced rather than rejected, so a native schema's types
mostly port as they are: metric `seconds`, `duration`, `decimal`, `number` become `float` and
`integer` becomes `int`; dimension `boolean`, `bool`, `text` become `string`, `integer` becomes
`int` and `number` becomes `float`. A genuinely unknown type still fails.

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
        url_base: *url_base
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
        url_base: *url_base
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
is rejected at draft. That includes streams nested inside a `ChainedStream` or a
`DateChunkedStream`.

A top-level name must start with a lowercase letter and use only `a-z`, digits, underscores and
dashes. The report-type match below is exact, so a stream named `Tasks` never serves report type
`tasks`.

**A stream that a template reads by name cannot contain a dash.** The template engine reads
`{{ campaigns-list.id }}` as a subtraction, and the path rule excludes a dash, so the definition is
refused. This applies to the parent of a `ChainedStream`, which the child references as
`{{ parent_name.field }}`. Use underscores there. A dash is fine in any other stream name.

For parent-child fetching, `ChainedStream` takes `require_records: true` to drop a parent record
whose child stream returned nothing. For an API that only accepts short date ranges, wrap the
stream in a `DateChunkedStream` with `chunk_days: 7` or `period: monthly` (`daily`, `weekly`,
`monthly`), and `date_range` is re-rendered for each chunk.

### Every report type needs a stream of the same name

A stream is bound to a report type by exact name. If `schema.report_types` has
`external_id: orders`, the manifest needs a stream named `orders`, or one stream named `general` to
serve them all. A mismatch is rejected at draft, and `schema.report_types` may not be empty. A
stream that matches no report type and is not the discovery stream produces a warning in the
draft response.

One platform is one integration. Different grains (account, campaign, ad; orders, order items,
abandoned carts) are **report types**, never separate integrations. Each report type gets its own
stored table under the same per-source transfer.

### Every data stream ends with `MapToIntegrationData`

It turns a raw API record into the `{date, dimensions, metrics}` row that storage reads. Leaving it
off is rejected at draft, because nothing later would report it: `sample` returns records, publish
creates the table, connect attaches the source, and the first real fetch then writes one row per
date with every dimension `N/A` and every metric `0`. A fetch that stored wrong values is not a
failed job, so nothing retries it and no error reaches anyone.

Put it last in the `transformations` list, which is a sibling of `retriever:` on the stream the
report type is matched to. If that stream is a `ChainedStream`, or is wrapped in a
`DateChunkedStream`, the transformation goes on the composite, not on each inner stream.

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

Other transformations available: `OnlyKeys`, `ReplaceKeys`, `LowerKeys`, `ConvertKeysToSnake`,
`Collapse`, `NormalizeNumericValues`, `MultiplyValues`, `ArrayToStringConcat`,
`NormalizeKeyValueList`, `LimitValueLength`, `MapPositionalListToMetrics`.

## Source discovery

`source_fetcher` is required, with both a `stream` and a `factory`. It runs at `connect` and
decides what sources exist.

`attributes.name` and `attributes.external_id` are both required. They are evaluated against each
discovery record with **its keys at the top level**, so a record `{"id": "123", "name": "Acme"}`
gives you `{{ id }}` and `{{ name }}`, not `{{ record.id }}`. Compose freely:
`"{{ name }} ({{ id }})"` is fine.

**An expression that resolves to nothing does not fail.** The source gets the placeholder
external id `-` or the name `N/A`, and a warning is logged. Because the placeholder id is a
constant, two records without an id collapse into one source. So check the `connect` result: a
source named `N/A` or with id `-` means the factory reads a key the record does not have.

If discovery returns an envelope rather than a bare array, the extractor's `field_path` must name
the key holding the list. `field_path: []` is correct **only** when the response root is itself an
array. Against `{"data": [...], "meta": {...}}` an empty path treats the whole envelope as one
record with no per-entity `id`, which is the most common cause of a single `N/A` source.

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
naming the chosen ones. Naming an id discovery did not return is refused. Discovery finding nothing
at all is an error.

Reconnecting leaves an already-connected source alone. A source that was removed earlier is
discovered again and written as a **new** source row, so widgets built on the removed row do not
come back with it.

## The spec

```yaml
definitions:
  <<: &validate
    type: ValidationFlowStep
    rules:
      - type: FieldValidationRuleSet
        field: name
        rules:
          - type: Required
          - type: IsText
          - type: MaxLength
            length: 256
      - type: FieldValidationRuleSet
        field: api_token
        rules:
          - type: Required
          - type: IsText
          - type: MaxLength
            length: 256

  <<: &check_connection
    type: RequestFlowStep
    requester:
      type: HttpRequester
      http_method: "GET"
      url_base: "https://api.example.com/v2"
      path: "user"
      # The manifest's own authenticator, unchanged. The engine drafts the account from
      # `account:` before the first step, so the probe reads the token the way a fetch does.
      authenticator:
        type: TokenAuthenticator
        token_provider:
          type: SuppliedCredentialTokenProvider
          credential: api_token
        token_placement:
          type: HeaderTokenPlacement
          scheme: bearer
      request_headers:
        type: SimpleRequestHeaders
        headers:
          Accept: "application/json"
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
    record_selector:              # a sibling of requester, not inside it
      type: RecordSelector
      extractor:
        type: DpathExtractor

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
  account:
    external_id: "{{ runtime.nonce }}"
    name: "{{ name }}"
    credentials:
      api_token: "{{ api_token }}"
    options:
      name: "{{ name }}"
  authorization_flow:
    type: apiKey
    access_acquisition_flow:
      - *validate
      - *check_connection
```

`connection_specification` holds three siblings: `properties` (the form), `account` (what the
engine stores) and `authorization_flow` (the steps that prove the inputs).

### Properties

Each property takes `type`, which is one of `string`, `select` or `warning`. It also takes
`label`, `description` (shown as the placeholder), `required`, `value` (a default), `when` (hide
the field when this path renders truthy), `readonly`, `readonly_on_update` and `learn_more`. A
`select` adds `options`, a list of `{value, label}`. A `warning` adds `text`. There is no `secret`
key. A value is secret because the `account` block stores it under `credentials`.

`required` only affects the form. The server enforces nothing unless a `ValidationFlowStep` says
so.

### The connected account and its credentials

The `account` block is the connected account (the integration key). The engine drafts it from the
submitted inputs before the first flow step, and saves it after the last step succeeds.

| Key | |
|---|---|
| `external_id` | Required. `{{ runtime.nonce }}` for one account per connect. A stable id from a probe response (for example `{{ account_id }}`) if the same account should be recognised on reconnect. A static string for a keyless API, so there is one invisible account. |
| `name` | Shown in the account list. Give it one, because the connect modal needs one. |
| `email` | Optional. |
| `credentials` | A flat map of `name: "{{ input }}"`. Each value is stored securely and is **not visible to any template**. Names are a letter, then letters, digits or underscores. Blank values are dropped. |
| `options` | A map of non-secret values. Everything here is readable as `{{ integration_key.options.* }}` in request templates, so **never put a secret here**. |

A manifest stream reads a credential **by name**, never by template:

```yaml
token_provider:
  type: SuppliedCredentialTokenProvider
  credential: api_token          # a name declared under account.credentials
```

Two traps:

- **`ValidationFlowStep` passes on only the fields it has rules for.** An input with no rule is
  gone by the time the account is saved, so `{{ that_input }}` renders empty and the connection
  fails. Give every input the account reads a rule, even if the rule is only `Required`.
- **A `RequestFlowStep` merges the fields its `record_selector` extracts into the flow data**, at
  the top level. Later steps and the `account` block read them as `{{ account_id }}`, not
  `{{ steps.x.account_id }}`. There is no steps namespace.

### Validation rules

`rules` is a list of `FieldValidationRuleSet` blocks, one per field, each with its own `rules`
list of constraints. The old map of rule strings (`api_token: "required|string"`) is
rejected at draft.

| Constraint | Keys |
|---|---|
| `Required`, `Nullable`, `IsText`, `IsWholeNumber`, `IsList`, `IsEmail`, `Lowercase`, `AlphaDash` | none |
| `IsUrl` | `schemes` (optional; `http`, `https`) |
| `MaxLength` | `length` |
| `MinValue`, `MaxValue` | `value` |
| `ExactCount` | `count` |
| `OneOf` | `values` |
| `DoesNotStartWith`, `DoesNotEndWith` | `values` |
| `SameAs` | `field` |
| `Matches`, `DoesNotMatch` | `pattern` (a full regex with delimiters, such as `/^pk_/`) |

A field may appear only once in one list. `ValidationFlowStep` also takes an optional `messages`
map.

### Rules the spec will fail on

**`authorization_flow` goes under `connection_specification`**, not at the spec's top level. A
top-level one is rejected with a message saying so. Declare `properties` and `account` beside it,
not inside it. A copy inside the flow is ignored, so it does nothing and misleads the next reader.

**A token-only API still needs an `access_acquisition_flow`.** Its steps *are* the request that
`test-auth` makes, so an empty or missing flow leaves nothing to verify. One `RequestFlowStep`
against a cheap authenticated endpoint is enough.

**The flow is a bare list.** There is no `steps:` wrapper.

**The step types are** `ValidationFlowStep`, `PermissionValidationFlowStep`, `RequestFlowStep` and
`TokenExchangeFlowStep`. There is no store step. The engine stores the account itself from the
`account` block.

**Classify auth failures.** Without a `ResponseClassifier` filter for 401/403 with `action: FAIL`,
`test-auth` reports success for a token the API just rejected. Auth-flow error text is user-facing,
so write `error_message` for a person reading it in the connect modal.

**`request_headers`, `query_parameters` and `request_body` are typed components.** Each needs its
own `type` (`SimpleRequestHeaders`, `SimpleQueryParameters`, `SimpleRequestBody`) with the values
nested under `headers`, `parameters` or `data`. A bare map is rejected.

**`url_base` must not end in a slash.** The engine adds the separator, so a trailing slash produces
a double slash, which providers answer with a redirect or a 404.

**Use `url_base` plus `path`,** not a single `url` key.

### Authentication shapes

There are three authenticator types: `TokenAuthenticator`, `OAuth1RequestSigner` and `NoAuth` (the
default when a requester declares none). `TokenAuthenticator` takes a `token_provider` (where the
value comes from), a `token_placement` (where it goes) and an optional `token_storage` (keep a
minted value until it expires). It interpolates nothing, so there is no header template to get
wrong.

| Shape | How |
|---|---|
| API key in a header | `SuppliedCredentialTokenProvider` with `credential: <name>`, and `HeaderTokenPlacement` with `scheme: bearer` (`Bearer x`), `token` (`Token x`) or `none` (the bare value). `name` sets a header other than `Authorization`. Many APIs want the bare value. |
| Key in the query string | `SuppliedCredentialTokenProvider` plus `QueryTokenPlacement` with `name: <parameter>`. |
| Two credential headers | `CompositeTokenPlacement` with a `placements` list, for example a `HeaderTokenPlacement` plus a `SuppliedCredentialHeaderPlacement` (`name`, `credential`). |
| A credential in the body | `SuppliedCredentialField` (`field_path`, `credential`) inside a `CompositeRequestBody`. |
| Basic auth | `SuppliedBasicCredentialsTokenProvider` with `user: <credential name>` and `password: <credential name>`, and `HeaderTokenPlacement` with `scheme: basic`. |
| Keyless or public API | No `authenticator`. Declare no credential properties and give `account.external_id` a static value, so there is one invisible account rather than a new one per connect. |
| Client credentials or a login call | `ExternalTokenProvider` (a `requester` and a `record_selector`) whose request body sends the stored id and secret with `SuppliedCredentialField`, plus `token_storage: { type: AccountCredentialStore, expiration_policy: { type: ConstantExpirationPolicy, every: <seconds> } }`. `access_token_field` (default `access_token`) names the response field that holds the token. `client_credentials` is not a flow type. |
| JWT signed with a key the user holds | `JwtKeyPairTokenProvider` with `private_key: <credential name>`, optional `passphrase`, `algorithm` (default `RS256`), `ttl_seconds` and `claims`. |
| OAuth1 (HMAC) | `OAuth1RequestSigner` as the requester's `authenticator`, with `consumer_key`, `consumer_secret`, `token_key`, `token_secret` naming credentials and `signature_method` `HMAC-SHA1` or `HMAC-SHA256`. |

A client-credentials exchange:

```yaml
authenticator:
  type: TokenAuthenticator
  token_provider:
    type: ExternalTokenProvider
    requester:
      type: HttpRequester
      http_method: "POST"
      url_base: "https://auth.example.com"
      path: "oauth/token"
      body_format: "form_params"
      middlewares:                # required on this inner requester too
        - <<: *retry
        - <<: *logger
        - <<: *classifier
      request_body:
        type: CompositeRequestBody
        fields:
          - { type: StaticField, field_path: [ grant_type ], value: client_credentials }
          - { type: SuppliedCredentialField, field_path: [ client_id ], credential: client_id }
          - { type: SuppliedCredentialField, field_path: [ client_secret ], credential: client_secret }
    record_selector:
      type: RecordSelector
      extractor:
        type: DpathExtractor
  token_placement:
    type: HeaderTokenPlacement
    scheme: bearer
  token_storage:
    type: AccountCredentialStore
    expiration_policy:
      type: ConstantExpirationPolicy
      every: 3540
```

Declare the token host in `host_allowlist` too.

If the provider supports OAuth2 with a consent screen, build an `oauth2` flow as described in
[OAuth2](#oauth2). Otherwise use a credential the user already holds: an API key, a personal access
token, a service account, or a client id and secret collected as properties.

A long-lived refresh token pasted into a property can be exchanged with an `ExternalTokenProvider`
that sends it with `SuppliedCredentialField`. This works only for a provider that keeps the refresh
token the same. If the provider issues a new refresh token on every refresh, the pasted one stops
working after the first refresh, so say so rather than shipping it. If an auth style can only be
signed with a secret held on the server, say so rather than shipping a definition that fails
authentication.

### OAuth2

An `oauth2` flow sends the user to the provider's consent screen and exchanges the code the
provider returns. It authenticates against an OAuth application **the user registers with the
provider themselves**. Whatagraph's own OAuth applications are never available to a dynamic
integration, so never try to reuse a shipped connector's client id.

**Run it in this order, and stop where it says stop.**

1. **`draft`.** The response includes `oauth_redirect_urls`, two URLs: the connect callback
   (ending `/add-integration/dynamic-<id>`) and the reconnect callback (ending `/verify-account`).
   They depend only on the integration id, so they never change for this integration.
2. **Stop and tell the user.** Do not call any other action yet. Show both `oauth_redirect_urls`
   exactly as returned, and ask the user to:
   - create an OAuth application with the provider, or open the one they have;
   - add **both** URLs as allowed redirect URLs (the provider's setting is usually named "Valid
     OAuth Redirect URIs", "Authorized redirect URIs" or "Callback URL");
   - grant the scopes the definition asks for;
   - tell you when it is saved, and give you the application's client id and client secret.

   The provider refuses the consent for any redirect URL it was not told about, so skipping this
   step only produces a failed connect later. Never invent or guess a client id.

   List **every** `oauth_redirect_urls` entry, never only the first: the reconnect callback is
   what a later re-authorization returns to, and leaving it out breaks that months later. Question
   text renders as markdown, so ask it as numbered steps with each URL in a code span, which the
   user copies exactly. Then ask for the client id and the client secret as separate questions:

   ```markdown
   Set up your <Provider> OAuth app:

   1. Open your app in the <Provider> developer console, or create one.
   2. Add both of these as <the provider's setting name>:
      - `<oauth_redirect_urls[0]>`
      - `<oauth_redirect_urls[1]>`
   3. Grant the scopes <scopes>, and save.

   Then paste the app's client ID below.
   ```
3. **`set-oauth-client`** with the `client_id` and `client_secret` the user gave. It stores them
   encrypted and never returns them. Do not repeat the secret back in the chat.
4. **`authorize`.** Give the user `authorize_url` as a link, and ask them to open it while signed
   in to Whatagraph and approve access. From an IQ Chat they come back to this conversation
   afterwards. Otherwise they see a page saying whether the account connected. Write it as a named
   markdown link, not a bare URL, and do not repeat the redirect URLs here; they were step 2:

   ```markdown
   [Approve access in <Provider>](<authorize_url>)

   Sign in, approve the requested access, and you will come back to this chat.
   ```
5. **`sample`** once the user says they are back. If `sample` answers that there are no stored
   credentials, the connect failed. Ask the user what the page or the notice said, and have them
   open the same `authorize_url` again after fixing the cause. Do not re-run `set-oauth-client`:
   the stored client is per integration, not per draft version, and re-drafting does not clear it.

**Consent runs the newest draft only until the first publish.** After that, every consent, the
one `authorize` starts included, runs the live version, so customers never run an unpublished
draft. A later draft that still works with the existing token samples and publishes as usual. A
later draft that needs a new consent, such as one that adds a scope, cannot be proven before it is
published, and it cannot be published until it samples. Tell the user so before re-drafting, and
build the new scope set as a new integration instead.

**Write the consent URLs and the code exchange with the engine's fields.** Draft refuses anything
else in an `oauth2` flow:

- `authorization_url` and `verification_url` are `AuthorizationFlowUrlBuilder` blocks whose
  `url_base` is a literal `https://` URL on a host in `host_allowlist`, with no user part,
  backslash, whitespace or port other than 443. Their `query_parameters` are `CompositeQueryParameters`,
  whose `fields` set `client_id` with a `PlatformCredentialField` (`credential: oauth_client_id`),
  `redirect_uri` with a `PlatformUrlField` (`url: connect` for `authorization_url`, `url: verify`
  for `verification_url`), and include a `StateField` after `redirect_uri`.
- The code exchange is a `TokenExchangeFlowStep`. It sends the client with `PlatformCredentialField`
  (`oauth_client_id`, `oauth_client_secret`) or `PlatformBasicCredentialsTokenProvider`, and it sends
  the **same** `redirect_uri` as the consent URL: a `PlatformUrlField` with `url: connect`, or an
  `InterpolatedField` whose value is `"{{ redirect_uri }}"`. Never use `CallbackUrlField` there. It
  builds a different URL, and the provider refuses the exchange. An exchange that sends no
  `redirect_uri` at all is refused too.
- `ExternalAuthorizationFlowUrlBuilder` is not available to a stored definition.

A complete flow, for a provider that issues long-lived access tokens:

```yaml
connection_specification:
  properties: {}
  account:
    external_id: "{{ id }}"
    name: "{{ name }}"
    credentials:
      access_token: "{{ access_token }}"
  authorization_flow:
    type: oauth2
    authorization_url:
      type: AuthorizationFlowUrlBuilder
      url_base: "https://www.example.com"
      path: "oauth/authorize"
      query_parameters:
        type: CompositeQueryParameters
        fields:
          - { type: StaticField, field_path: [ response_type ], value: "code" }
          - { type: PlatformCredentialField, field_path: [ client_id ], credential: oauth_client_id }
          - { type: PlatformUrlField, field_path: [ redirect_uri ], url: connect }
          - { type: StaticField, field_path: [ scope ], value: "read" }
          - { type: StateField, field_path: [ state ] }
    verification_url:
      type: AuthorizationFlowUrlBuilder
      url_base: "https://www.example.com"
      path: "oauth/authorize"
      query_parameters:
        type: CompositeQueryParameters
        fields:
          - { type: StaticField, field_path: [ response_type ], value: "code" }
          - { type: PlatformCredentialField, field_path: [ client_id ], credential: oauth_client_id }
          - { type: PlatformUrlField, field_path: [ redirect_uri ], url: verify }
          - { type: StaticField, field_path: [ scope ], value: "read" }
          - { type: StateField, field_path: [ state ] }
    access_acquisition_flow:
      - type: TokenExchangeFlowStep
        requester:
          type: HttpRequester
          http_method: "POST"
          url_base: "https://api.example.com"
          path: "oauth/token"
          body_format: "form_params"
          request_body:
            type: CompositeRequestBody
            fields:
              - { type: StaticField, field_path: [ grant_type ], value: "authorization_code" }
              - { type: PlatformCredentialField, field_path: [ client_id ], credential: oauth_client_id }
              - { type: PlatformCredentialField, field_path: [ client_secret ], credential: oauth_client_secret }
              - { type: PlatformUrlField, field_path: [ redirect_uri ], url: connect }
              - { type: InterpolatedField, field_path: [ code ], value: "{{ code }}" }
          middlewares:
            - <<: *retry
            - <<: *logger
            - <<: *classifier
      - type: RequestFlowStep          # reads the account the token belongs to
        requester:
          type: HttpRequester
          http_method: "GET"
          url_base: "https://api.example.com"
          path: "me"
          request_headers:
            type: SimpleRequestHeaders
            headers:
              Authorization: "Bearer {{ access_token }}"
          middlewares:
            - <<: *retry
            - <<: *logger
            - <<: *classifier
```

The streams then authenticate with `SuppliedCredentialTokenProvider` (`credential: access_token`)
and `HeaderTokenPlacement` (`scheme: bearer`). Declare every host the flow calls, the consent host
included, in `host_allowlist`.

For a provider whose access token expires, drop `access_token` from `account.credentials`. The
`TokenExchangeFlowStep` stores the refresh token the provider returns on its own. The streams then
mint an access token from it with an `ExternalTokenProvider`:

```yaml
authenticator:
  type: TokenAuthenticator
  token_placement:
    type: HeaderTokenPlacement
    scheme: bearer
  token_provider:
    type: ExternalTokenProvider
    requester:
      http_method: "POST"
      body_format: "form_params"
      url_base: "https://api.example.com"
      path: "oauth/token"
      request_body:
        type: CompositeRequestBody
        fields:
          - { type: RefreshTokenField, field_path: [ refresh_token ] }
          - { type: StaticField, field_path: [ grant_type ], value: "refresh_token" }
          - { type: PlatformCredentialField, field_path: [ client_id ], credential: oauth_client_id }
          - { type: PlatformCredentialField, field_path: [ client_secret ], credential: oauth_client_secret }
      middlewares:
        - <<: *retry
        - <<: *logger
        - <<: *classifier
  token_storage:
    type: AccountCredentialStore
    refresh_token_field: refresh_token
    expiration_policy:
      type: ConstantExpirationPolicy
      every: 3500
```

Set `every` a little under the provider's access token lifetime.

## Per-source inputs

A value the user types per source (a project name, a domain, a region) goes in
`source_specification`, not `connection_specification`:

```yaml
source_specification:
  properties:
    domain:
      type: string
      required: true
      label: "Domain to track"
  save_flow:
    - type: ValidationFlowStep
      rules:
        - type: FieldValidationRuleSet
          field: domain
          rules:
            - type: Required
            - type: IsText
  source:
    options:
      domain: "{{ domain }}"
```

- `save_flow` accepts only `ValidationFlowStep`. It passes on only the fields it has rules for.
- `source` takes `name` and `options` and nothing else. The engine renders it after the last
  save-flow step. `options` is merged over what the source already holds. A `name` that renders
  blank keeps the existing name.
- A data stream reads the values back as `{{ integration_source.options.domain }}`.

The form is filled in the source UI **after** connect, against a source that already exists.
Discovery never sees these values. When sampling before any source exists, pass stand-in values
with `source_options` together with `source_external_id` (see below). The form never runs during
`sample`.

## Pagination

An API that returns everything in one response needs no paginator: leave it out, or state
`NoPagination`. Getting it wrong in the other direction fails silently, because the engine chunks
a backfill by period and a single chunk easily exceeds one page. Without a paginator you store
page 1 of every chunk, and the connector looks like an API with little data in it.

A missing `page_token_option` has the same effect: the page parameter is never sent, so you get
page 1 forever.

```yaml
paginator:
  type: SimplePaginator
  pagination_strategy:
    type: PageIncrement          # or OffsetIncrement / LimitedPageIncrement / CursorPagination / LinkHeaderPagination
    page_size: 100
    initial_page: 0              # 0- or 1-indexed per the API; the default is 1
  page_token_option:
    type: RequestOption
    inject_into: "query_parameters"   # query_parameters | headers | body | path
    field_path: [ "page" ]            # a list, not a string
```

- `PageIncrement` stops when a page returns fewer records than `page_size`.
- `LimitedPageIncrement` adds `total_count`, for an API that reports how many records exist.
- `OffsetIncrement` steps by `page_size`; inject `offset` rather than `page`.
- `CursorPagination` needs a `cursor_value`, which is a template rendered against the response
  body. Variables are the body's top-level keys, with no `response.` or `body.` prefix. The last
  page usually has no cursor key, so always give it a default; an empty cursor is what stops the
  paginator. A plain path such as `paging.cursors.after` is not rendered and is sent to the API as
  literal text. For a Graph-style `paging` object:

  ```yaml
  pagination_strategy:
    type: CursorPagination
    page_size: 100
    cursor_value: "{{ paging.cursors.after | default('') }}"
  page_token_option:
    type: RequestOption
    inject_into: "query_parameters"
    field_path: [ "after" ]
  ```
- `LinkHeaderPagination` is for an API that returns the next page in a `Link` header rather than
  the body (`Link: <...?page=2>; rel="next"`), which `CursorPagination` cannot see. Set
  `extract_param` to the query parameter carried in that URL. It stops when the API omits
  `rel="next"`.
- Add a `page_size_option` (same shape as `page_token_option`) only if the API takes a page-size
  parameter.

Sampling cannot prove pagination works, because a broken paginator still returns page 1 and 10
rows look fine. After connect, check that a multi-month total exceeds one page. A total that is
exactly `page_size` times the number of chunks is the signature of a paginator that is not working.

## Responses that are not a list of objects

`DpathExtractor` expects the path to hold a list of records. Two other shapes have their own
extractor. Both go under `record_selector.extractor`.

**Parallel arrays**, where index `i` across the arrays is one record. Time-series endpoints do this
often:

```json
{ "daily": { "time": ["2026-01-01", "2026-01-02"], "temperature_max": [5.2, 6.1] } }
```

```yaml
extractor:
  type: ColumnsToRowsExtractor
  field_path: [ "daily" ]                       # the object holding the arrays; empty = the root
  keys: [ "time", "temperature_max" ]           # optional; omit to zip every array-valued key
```

Shorter columns are null-filled to the longest length.

**A map keyed by data**, usually a date:

```json
{ "2026-01-01": { "visits": 4 }, "2026-01-02": { "visits": 7 } }
```

```yaml
extractor:
  type: KeyedMapToRowsExtractor
  field_path: []                  # the map; empty = the root
  key_field: "date"               # each record gets the map key under this name
  values_are_lists: false         # true when each entry holds a list of records
```

Map as usual afterwards: normalize the date, then `MapToIntegrationData`.

## Errors and retries

Classify the API's responses with `ResponseClassifier` filters on each requester. As a safety net
the engine already treats 429 as a rate limit and 408 and 5xx as server errors, and retries them
even when no filter matches, so a forgotten filter does not fail a whole backfill permanently.
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
carry: `source_external_id` fills `{{ integration_source.external_id }}`, and `source_options`
fills `{{ integration_source.options.* }}`. `source_options` is used only when
`source_external_id` is also passed.

After connect, compare a few dates from `fetch-data` against the provider's own reporting before
building widgets. Attribution lag and timezone differences show up here and nowhere else.

## Evolution

Republishing an already-connected definition is additive: new fields and new report types
propagate, and only the new tables backfill. Renames and removals do not exist, so a rename is a
new `external_id`.

**A fix is not retroactive.** Correcting a definition and republishing changes how future fetches
behave. Data already stored stays wrong until you `resync` the range, because a fetch that
succeeded with wrong values is not a failed job and nothing re-runs it on its own. `resync`
defaults to the whole backfill ending today, and narrows with `source_external_id`, `from` and
`till`.

**The engine can upgrade a live definition written for an older engine.** When a live definition
uses a shape the engine has since replaced, the first fetch that fails to build it rewrites it,
appends and publishes a new version, and answers "It has been updated and republished, so this
request has to be made again." Retry, and `list-dynamic-integrations` shows the new version. If
the old shape cannot be rewritten, the error says the definition "has to be updated and
republished before it can fetch again". Re-draft it in the current shape and publish. A new
`draft` is never upgraded: an old shape in a new draft is simply rejected.

`delete-dynamic-integrations` tears down an integration that was drafted but never connected. It
asks for confirmation first: the first call returns a preview and a token, and the same call is
resent with the token. It is refused once the integration has had any source, **including one that
was removed since**, so an integration that was ever connected cannot be deleted with it.

## What the user sees

- **Connect modal**: the integration appears in the catalog with the inputs the spec declares, and
  with an icon taken from the first `host_allowlist` entry. A keyless connector skips the
  credential form.
- **Report drawer**: under stored data, since a dynamic integration is storage-backed.
- **Widget picker**: the full widget set, per report type.

**It belongs to that team alone.** No other team can see it, list it, connect to it or read its
data. An id belonging to another team reads as absent rather than forbidden.

## When something goes wrong

| Symptom | Cause |
|---|---|
| `draft` rejected | A guard caught it, and the message names the field and the fix. Read it rather than guessing. |
| "X does not accept `k`. It accepts: ..." | `k` is in the wrong block. See [Where every key goes](#where-every-key-goes). The most common one is `record_selector` or `paginator` inside `requester`. |
| "`k` is required for X" | Add the key to the block the message names. |
| "Requester ... is missing required middlewares" | Add `RetryHandler`, `RequestLogger` and `ResponseClassifier` to that requester, nested ones included. |
| "`type` for ... must be the name of a ... type" | A misspelled or retired type. The message lists the accepted names. |
| "`rules` ... must be a list of field validation rule set blocks" | Rules written as strings. Use `FieldValidationRuleSet` blocks. |
| `test-auth` fails | The credential or the flow. Check the endpoint, the placement `scheme`, and whether the API wants a prefix. |
| `test-auth` passes but `sample` says credentials are missing | The manifest names a `credential` that `account.credentials` does not declare, or declares under a different name. |
| The connection fails with an empty `external_id` or name | The `account` block reads an input that `ValidationFlowStep` dropped because it had no rule, or a probe field that the `record_selector` did not extract. |
| "Platform credential ... is not configured" | In an `oauth2` flow, `set-oauth-client` has not been called for this integration. Otherwise a `Platform*` component outside OAuth2: a dynamic integration has no other platform credentials, so collect the value from the user. |
| `sample` says there are no stored credentials after `authorize` | The OAuth2 connect failed and stored nothing. Ask the user what the page or notice said, fix the cause (usually a redirect URL missing from the provider's application), and have them open the same `authorize_url` again. |
| `sample` returns nothing | Usually the extractor's `field_path` does not match the response shape, or the date filter excludes everything. |
| `sample` returns one record that is the whole envelope | `field_path: []` against an enveloped response. Name the key holding the list. |
| A source named `N/A` or with external id `-` | The factory's `name` or `external_id` read a key the discovery record does not have. |
| Only ever one page of records | The paginator, or a missing `page_token_option`. |
| Every request blocked | A `host_allowlist` entry that does not resolve, or resolves to a private address. Every declared host is checked on every request. |
| One request blocked | Its host is not in `host_allowlist`, the URL is not HTTPS, or it names a port other than 443. |
| Every dimension `N/A` and every metric `0` | The stream never mapped its records, or a schema field is not a top-level key by the time the mapping runs. |
| Every row dated to the range start | No `NormalizeTimeValues` or `NormalizeEpochTimeValues` before the mapping. |
| A fetch says the definition "has been updated and republished" | The engine upgraded an old live definition. Retry the request. |
| Data still wrong after a fix | Republishing does not correct stored data. `resync` the range. |
