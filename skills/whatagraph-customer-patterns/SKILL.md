---
name: whatagraph-customer-patterns
type: meta
description: Common multi-tool flows and decision trees across Whatagraph skills. Load alongside domain skills when working on end-to-end capabilities like "onboard a new client", "build a cross-channel report", "fix a data mismatch", or "set up a client portal".
required_tools: []
optional_tools:
  - view-team
  - list-integrations
  - list-sources
  - list-reports
  - list-widgets
  - list-filters
  - list-templates
  - fetch-data
  - export-report
  - preview-report
  - manage-spaces
  - manage-sources
  - manage-integrations
  - manage-reports
  - manage-report-tabs
  - manage-widgets
  - manage-custom-metrics
  - manage-overviews
  - manage-themes
  - manage-sharing
  - manage-automations
---

# Customer patterns — end-to-end flows

Multi-tool patterns that keep coming up. Use alongside the domain skills.

> **Say only what the calls proved.** Whatever the flow, never state a data status in the closing message — "verified", "real non-zero data", "all widgets pulling" — that no `fetch-data`, `export-report` or `csv_export` call in this run returned. Without a verify call the data is unverified and the message says so; a call that returned warnings, sample data, or a broken source is reported as that. Name only metrics the report actually holds, not ones you offered as a next step.

## Decision trees

### Same-channel rollup vs cross-channel rollup vs join

"I want combined numbers across sources":

```
Rows JOINED on a shared key (campaign_name, date), or numbers that must be live?
├── Yes → Blend, for a handful of sources. See whatagraph-blends.
└── No  → Source group — summed, scales to dozens or hundreds. See whatagraph-source-groups.

Both work same-channel and cross-channel; channel count decides nothing.
```

Combining across sources is always a **source group** or **blend** — never a custom metric (a custom metric only computes on the source it is attached to). For a combined **ratio** (blended ROAS/CPA), build the source group/blend first, then a `data_formula` metric on top of it.

### Filter scope

```
Does this filter apply to EVERY widget using this source?
├── Yes → Source-level filter on the source/source-group
└── No  → Is the same filter needed on many widgets across a report?
         ├── Yes → Saved filter config, apply per widget (see whatagraph-filters)
         └── No  → Set filter inline on the widget via manage-widgets options
```

### Template linked vs one-off

Templates only enter the flow when the request or agent instructions explicitly call for one — an open report request is a scratch build (see `whatagraph-reports`). When a template IS in play:

```
Does the user ask for auto-sync, or does the context clearly call for it (one template kept in step across many client reports)?
├── Yes → Create from template and keep it linked (manage-reports action=create_from_template)
└── No  → Independent report (the default):
         • From a template → create_from_template → duplicate the new report → delete the linked intermediate
         • From an existing report → manage-reports action=duplicate
```

### Overview (measurement) vs report

```
One-page KPI dashboard with 4–8 tiles that execs want to glance at?
├── Yes → Overview / Measurement (whatagraph-overviews)
└── No  → Report with tabs (whatagraph-reports)
```

### Source group vs blend

See "I want combined numbers across sources" above — same decision.

## End-to-end flows

### 1. Onboard a new client

1. `view-team action=show_subscription` — confirm seat/asset headroom.
2. `manage-spaces action=create name="Client Name"` — capture the new `client_id`.
3. `list-integrations action=list_accounts channel_id=<id>` per channel in use.
4. `list-integrations action=list_available_sources account_id=<id>` to find the client's sub-accounts.
5. `manage-integrations action=add_sources channel_id=<id> account_id=<id> source_ids=[...]` per channel.
6. `manage-integrations action=sync_to_clients source_id=<id> client_ids=[<client_id>]` to attach each source to the space.
7. Decide: single-source report, source group, or blend?
   - Sources summed, or many of them → source group (same channel or across).
   - Rows joined side by side, or live numbers → blend (a handful).
8. Build the client report **from scratch by default** (`manage-reports action=create` → tabs → widgets, per `whatagraph-reports`). Use `create_from_template client_id=<client_id> template_id=<tpl>` only when the instructions name the team's own template — and deliver it unlinked (duplicate the new report, delete the linked intermediate) unless the user asked for auto-sync or the context makes it clearly relevant (this onboarding is part of a many-client rollout kept in step with a master template). Never pull a template from Whatagraph's pre-made gallery unprompted.
9. If a template was used: `manage-reports action=change_sources report_id=<new_id> source_mapping={"0": <new_source_id>, "<old>": <new>}` — swap template sample data for the client's sources.
10. `manage-themes action=enable_theme report_id=<id> theme_id=<client_theme_id>` + `enable_color` with the brand palette.
11. `manage-sharing action=create report_id=<id> require_password=true password="<share_password>"` — generate the client share link.
12. `manage-automations action=create` — schedule monthly delivery.

> **Verify the build.** After building or bulk-swapping, `export-report report_id=<id>` (or `list-widgets action=csv_export` per widget) and confirm every widget's `data_status` is `ready` with non-empty rows and expected metric names. `list-widgets action=show` is NOT sufficient — it echoes ids, not loaded data.

### 2. Cross-channel paid media report

Inputs: Google Ads, Meta Ads, LinkedIn Ads sources; GA4 for revenue.

1. **Source groups (one config each).** For each channel where the client has multiple ad accounts, build one source group with **one** `configs` entry (e.g. `[{"name": "Campaign Performance", "etl_config_ids": [<ids>]}]` for Google Ads campaign-level data). Note: `output_name` is a read-only field returned by `list-source-groups show`, not a create parameter. If they need campaign-level *and* keyword-level rollups, build two separate groups — one config per group. See `whatagraph-source-groups` for why the legacy multi-config pattern is discouraged.
2. **Blend.** Build a blend that joins the channel sources (or their source groups) on a shared date dimension (`universal_dimension_1137`) plus a shared grouping key like campaign or channel name. Pick the **same universal dimensions and metrics** on every sub-source of the blend — blends are designed around unified dimensions and integer/summable metrics (impressions, clicks, spend). Use `type="full"` to keep all rows from both sides (nulls where a dimension is missing on one side). Use `type="inner"` to keep only rows present in both sides.
3. **Custom metrics.**
   - On each source group: `manage-custom-metrics action=create map_type=data_formula transformation_level=channel` with `aggregation_level="aggregate"` and `formula_increase="positive"` or `"negative"`. Use channel-native field ids, or platform-unified `universal_metric_<n>` ids when the formula should work on any channel that exposes the slot.
   - **Any channel-native id written in this skill is illustrative, not authoritative.** Names like `metrics.clicks` or `spend` are shapes to recognise, not values to paste: they are channel-specific, differ in punctuation between channels, and change as providers change their APIs. Resolve every one against `list-sources action=list_dimensions_and_metrics` for the actual source before using it, and paste it back verbatim. On several channels the native metric will not resolve at all and the `universal_metric_<n>` form is the only one that works — so treat a rejected native id as "look it up", not "the platform is broken".
   - On the blend: build the cross-channel formula metric at `transformation_level=source` with the constituent sources' native fields as A, B, C, D.
4. **Report shell.** `manage-reports action=create` → add tabs Overview, Google, Meta, LinkedIn, GA4, Blended (via `manage-report-tabs action=create`).
5. **Attach the data sources.** For each source group, blend, or per-channel source the report needs, call `manage-reports action=attach_source report_id=<id> integration_source_id=<id>`. Capture the returned report-local `source_id` for each — widgets reference these, not the global ids. When attaching a sample-data placeholder via `manage-reports action=attach_source channel_ids=[<channel_id>]`, the response carries `is_sample_data: true` and `integration_source_id: null` — reference it via the report-local `source_id`. Use `is_sample_data` to distinguish real sources from placeholders in onboarding flows.
6. **Widgets.** Create widgets with `manage-widgets action=create` or `create_premade`, passing the report-local `source_id` from the attach step. Use `list-sources action=list_dimensions_and_metrics` on the group or blend to pick the right field ids (`universal_metric_*` / `universal_dimension_*` on source groups; `aggregation_metric_universal_metric_*` / `aggregation_dimension_universal_dimension_*` on blends).
7. **Verify.** `list-widgets action=show` on each widget to confirm ids/source binding, then use `list-widgets action=csv_export` or `export-report` to confirm metrics and options. Use `fetch-data` on the source group (with `universal_metric_*` / `universal_dimension_*`) and on the blend (with `aggregation_metric_*` / `aggregation_dimension_*`) to sanity-check the aggregated numbers.
8. **Share and automate.** `manage-sharing action=create` for the client share link; `manage-automations action=create` to schedule delivery; `manage-overviews action=create` for an exec-facing KPI summary.

### 3. Fix "data doesn't match the platform"

1. `list-sources action=show source_id=<id>` — check currency and access status.
2. Compare source currency with the report/team default. Mismatch → `manage-sources action=set_currency`.
3. Check source status — if `issue`, the source is disconnected; have the user reconnect in UI.
4. `fetch-data source_id=<id> metrics=[...] from=... till=...` — does the raw data match the platform's own export?
   - Yes → issue is at widget level (wrong filter, wrong formula, wrong dimension pairing).
   - No → issue is upstream (stale ETL, rate limits, attribution lag). Try again after a few minutes.
5. Check field ID family — widgets on source groups must use `universal_metric_*` / `universal_dimension_*`; widgets on blends must use `aggregation_metric_*` / `aggregation_dimension_*`; widgets on native sources use channel-native IDs (shapes like `metrics.clicks` or `spend` — always resolved per source, never assumed). Wrong family → wrong or no data.
6. Scan saved filters for stale entries: `list-filters action=list source_id=<id>`.
7. Cross-check `list-sources action=list_usage source_ids=[<id>]` — a different variant (another source group or blend) may be feeding the widget you think is direct.

### 4. Rebrand all reports for a client

1. `manage-themes action=create_theme` with client logo (hosted on public CDN) and fonts.
2. `manage-themes action=create_color` with brand chart + widget palette (8–12 colors).
3. For each client report: `manage-themes action=enable_theme` + `enable_color`.
4. Spot-check the first report via `preview-report` to confirm the branding renders.

### 5. Roll out a new tab across all client reports

Only applicable if those reports are linked to a template.

1. `list-templates action=linked_reports template_id=<id>` — confirm which reports will auto-update.
2. Edit the template report (the template is backed by its source report):
   - `manage-report-tabs action=create` on the template's backing report.
   - `manage-widgets action=create_premade` or `create` for each new widget on that tab.
3. `list-reports action=show report_id=<linked_report>` on a sample linked report — verify the new tab appears.

### 6. Prepare a report for an exec review (single share link)

1. Create or pick the report.
2. Apply branding (themes + palette).
3. Data QA: `preview-report` → look at the pages → fix issues.
4. Create share link: `manage-sharing action=create report_id=<id> require_password=true password="<share_password>"`.
5. Capture the URL from the response and hand it to the client.
6. If recurring, attach an automation: `manage-automations action=create frequency=monthly receivers=["client@..."] time_zone="Europe/London"`.

## Common pitfalls across flows

- **Reference IDs from the wrong domain** — spaces use `client_id`, sources use `source_id` (integration_source_id), widgets use `widget_id`. Skills state the required naming.
- **Mixing up channel-native vs Whatagraph-native report type names** — custom metrics use channel-native names (e.g. `campaign`); source groups use Whatagraph-native names (e.g. `campaign_performance`). Wrong family → "Report type X not found for channel Y".
- **Creating widgets before attaching sources** — `manage-widgets` validates `source_id` against report-local sources. Always run `manage-reports action=attach_source` first and use the returned `source_id`.
- **Defaulting to a template (or the pre-made gallery) when no one asked** — open report requests are scratch builds; templates are opt-in, and template-created reports ship unlinked unless the user asked for auto-sync or the context clearly calls for it.
- **Creating from template without running `change_sources`** — widgets stay on sample data.
- **Automations without `time_zone`** — always include IANA timezone; local time ≠ team timezone by default.
- **Sharing link without password on confidential reports** — anyone with the URL can view.
- **Claiming a data status nothing verified** — a closing "Data Status: Verified" with no `fetch-data`, `export-report`, or `csv_export` call behind it is a false report, however right the build looks. Run the verify call, or say the data is unverified.
