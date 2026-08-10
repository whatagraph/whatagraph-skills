---
name: whatagraph-dynamic-integrations
type: domain
description: Build a working Whatagraph integration from a third-party API's documentation, entirely through the Whatagraph MCP server — no code deploy. Activates when asked to add, build or connect a data source Whatagraph does not already support, or to fix one that was built this way.
required_tools:
  - manage-dynamic-integrations
  - list-dynamic-integrations
---

# Building a Whatagraph integration

You can add a new data source to Whatagraph yourself, from the API's documentation, using the
`manage-dynamic-integrations` tool. The connector is stored as data rather than code, so nothing
needs deploying and nobody needs to write PHP.

What you author is three artifacts:

| Artifact | What it is |
|---|---|
| `manifest_yaml` | The streams — which endpoints to call, how to page them, how to shape records |
| `spec_yaml` | The credentials to ask for, and the flow that proves them against the live API |
| `schema` | The report types, dimensions and metrics a user will pick from in a widget |

## Work in this order, and do not skip

```
draft → test-auth → sample → publish → connect
```

Each step is gated on the previous one. The response to every call carries a `next` field telling
you what to do — follow it.

1. **`draft`** — store the three artifacts. Omit `integration_id` to create a new integration;
   the response gives you the id you use for everything after. Pass `integration_id` to store a
   new version of an existing one.
2. **`test-auth`** — pass `credentials`. This runs your spec's authorization flow against the
   real API. A 401 fails and stores nothing. **If this fails, your spec is wrong — fix it and
   re-draft. Do not continue.**
3. **`sample`** — reads real records through the whole engine. **Show the records to the user and
   confirm the values are what they expect before publishing.** Sample every data stream, not
   just one. This is the only cheap moment to catch a wrong field mapping.
4. **`publish`** — creates the report types, dimensions and metrics, and a stored table per
   report type. Requires the version you are publishing to have been sampled.
5. **`connect`** — discovers the sources and attaches them. After this the integration behaves
   like any other channel: it appears in the catalog, in Source Management, and in widgets.

Use `list-dynamic-integrations` at any point to see where something is: its live version, its
newest version, and whether that newest version has been sampled.

## Rules that will save you a wasted cycle

**A stream's name is `$parameters.name`, not the YAML key it sits under.** Nothing reads that
key. The engine takes the name from `$parameters.name` and otherwise calls the stream `N/A`, so a
stream without one cannot be reached by `source_fetcher`, and every unnamed stream collides under
the same name. Give each stream `$parameters.name` matching its key — it is rejected at draft
otherwise:

```yaml
streams:
  tasks:
    type: DeclarativeStream
    $parameters:
      name: tasks
```

**Every report type needs a stream with the same name.** A stream is matched to a report type by
exact name. If `schema.report_types` has `external_id: orders`, the manifest needs a stream named
`orders` — or one stream named `general` to serve them all. A typo here is rejected at `draft`.

**Declare every host.** `host_allowlist` is required and enforced on every request: HTTPS only,
exact host match (a subdomain of a declared host is *not* declared), no private addresses,
redirects re-checked per hop. If your spec's auth endpoint is on a different host from your data
endpoints, declare both.

**The source_fetcher stream is special.** It discovers sources, and there is no date range during
discovery — so it must not use `MapToIntegrationData` or `ReplaceUniqueMetricValues`. Both are
rejected at draft. End that stream after `AppendValues` or `OnlyKeys`.

**The source_fetcher factory names the sources, and the record's keys are at the top level.**
`attributes.name` and `attributes.external_id` are both required — they are what each discovered
source is called and keyed on — and the expressions are evaluated against the discovery record
with its keys **unwrapped**, plus `integration_account` and `source_inputs`. So a record
`{"id": "123", "name": "Acme"}` gives you `{{ id }}` and `{{ name }}`, *not* `{{ record.id }}`:

```yaml
source_fetcher:
  stream: workspaces
  factory:
    type: InterpolatedSourceFactory
    attributes:
      external_id: "{{ id }}"
      name: "{{ name }}"
      # Optional. Anything a data stream needs to read back off the source at fetch time.
      options:
        workspace_id: "{{ id }}"
```

Compose freely — `"{{ name }} ({{ id }})"` is fine. An expression that resolves to nothing is
rejected, and the error lists the keys the record actually had, so check there first when a name
comes out empty: an empty `external_id` would otherwise collide with every other empty one on the
upsert key and collapse a whole discovery run into a single source.

Note that `name` applies to sources discovered **afterwards**. Changing the expression does not
rename sources that already exist — users can rename a source themselves, and a reconnect must
not undo that.

**`authorization_flow` goes under `connection_specification`**, not at the spec's top level. This
is the most common mistake and it is rejected at draft with a message telling you so.

**A token-only API still needs an auth flow.** `authorization_flow.access_acquisition_flow` is
required even for `type: apiKey`, because its steps *are* the request `test-auth` makes to prove
the credentials. Omitting it is rejected at draft.

The step types are `ValidationFlowStep`, `PermissionValidationFlowStep`, `RequestFlowStep` and
`IntegrationKeyStoreFlowStep` — nothing else, and a wrong name is rejected at draft. The one that
makes the authenticated request is **`RequestFlowStep`**, with a `requester` and a
`record_selector`; point it at a cheap authenticated endpoint such as the API's `me` or account
route. End with `IntegrationKeyStoreFlowStep` to store the proven credentials.

The flow is a **bare list**. There is no `steps:` wrapper, and adding one is rejected at draft.

Copy this shape rather than inventing one — every key here is required by the component that
reads it, and a missing one is rejected naming the key:

```yaml
connection_specification:
  properties:
    name:
      type: string
      required: true
      title: "Connection name"
    api_token:
      type: string
      required: true
      title: "API token"
  authorization_flow:
    type: apiKey
    access_acquisition_flow:
      - type: ValidationFlowStep
        rules:
          name: "required|string|max:256"
          api_token: "required|string|max:256"
      - type: RequestFlowStep
        requester:
          type: HttpRequester
          http_method: "GET"
          url_base: "https://api.example.com/v2"
          path: "user"
          request_headers:
            Accept: "application/json"
          # Interpolated from the submitted inputs, not from a stored key — nothing is
          # stored yet at this point in the flow.
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
      - type: IntegrationKeyStoreFlowStep
        external_id: "{{ uuid() }}"
        name: "{{ name }}"
        options:
          name: "{{ name }}"
          api_token: "{{ api_token }}"
```

Note `url_base` plus `path` rather than a single `url`, the three mandatory middlewares on
**every** requester including nested ones, and `token_provider` nested inside the
authenticator — those four are the ones most often missed.

**Your data streams need their own authenticator, and it reads a different place.** This is the
one that looks like it works: `test-auth` passes and then `sample` comes back with the API's own
"missing credentials" error. The two interpolate from different sources, because at different
moments the credential lives in different places:

| Where | Token expression | Why |
|---|---|---|
| The spec's auth flow | `{{ api_token }}` | The submitted inputs. Nothing is stored yet. |
| A manifest data stream | `{{ integration_key.options.api_token }}` | The stored key, saved by the flow. |

So the manifest repeats the authenticator on **every** stream requester, reading
`integration_key.options.*` — and the `IntegrationKeyStoreFlowStep` that ends your auth flow must
put the token in `options` under the same name, or there is nothing there to read. Declare the
authenticator once as a YAML anchor and alias it into each requester.

**Classify auth failures.** Give the `ResponseClassifier` in your auth flow a filter for 401/403
with `action: FAIL`. Without it, `test-auth` reports success for a token the API just rejected.

**An authenticator is not a middleware.** It goes under the requester's `authenticator:` key.
Putting it in `middlewares:` fails — they are different registries.

**Pagination is easy to get silently wrong.** A missing `page_token_option` means the page
parameter is never sent and you get page 1 forever, looking like an API with one page of data.
Use `SimplePaginator` with a `pagination_strategy` and a `page_token_option`. `DefaultPaginator`
and `TokenPaginator` are dead and rejected at draft.

**Twig is sandboxed.** Only some methods are callable. `getTimestamp()` works; `getTimestampMs()`
does not — compose `{{ date.getTimestamp() * 1000 }}` instead. If an expression is rejected,
compose from what is allowed rather than assuming the method should work.

## Getting a definition right

Read the API's **official documentation** for the fields, not a sample response — a sample tells
you what one account happened to return, not what the field means or whether it is always there.

Start smaller than you think. One report type, one data stream, three or four dimensions and one
or two metrics. Get that green through `connect`, confirm real numbers with the user, and then
re-draft to add more. A re-draft is cheap and cannot affect what is already live: only `publish`
moves what the data path reads.

Sensible starting shape:

- **Source discovery**: whatever endpoint lists the user's accounts, workspaces or properties.
  If the API has only one implicit account, point the stream at its `/me` or `/account`
  endpoint — one source is fine.
- **Data stream**: the endpoint that returns the records, with a date filter driven by
  `{{ date_range.from }}` / `{{ date_range.till }}`.
- **Dimensions**: the things a user would group or filter by. **Metrics**: the things they would
  sum or average.

## When something goes wrong

Read the error message. These guards are written for you specifically — they name the field and
the fix, because you cannot read Whatagraph's source code.

| Symptom | Cause |
|---|---|
| `draft` rejected | A guard caught it. The message says what to change. |
| `test-auth` fails | Credentials or the auth flow. Check the endpoint, the header shape, and whether the token needs a prefix. |
| `sample` returns nothing | Usually the record selector's `field_path` does not match the response shape, or the date filter excludes everything. |
| Only ever one page of records | Pagination. Check `page_token_option` exists and `inject_into` is right. |
| Blocked request | The host is not in `host_allowlist`, or it is not HTTPS. |
| Data is wrong after a fix | Republishing does not correct data already stored. Use `resync`. |

## Two things to tell the user

**It is theirs alone.** An integration you build belongs to that team. No other team can see it,
list it, connect to it or read its data.

**A fix is not retroactive.** Correcting a definition and republishing changes how *future*
fetches work. Data already stored stays as it was until you `resync` the range.
