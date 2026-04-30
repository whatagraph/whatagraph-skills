---
name: whatagraph-customer-patterns
description: Common multi-tool flows and decision trees across Whatagraph skills. Load alongside domain skills when working on end-to-end capabilities like "onboard a new client", "build a cross-channel report", "fix a data mismatch", or "set up a client portal".
---

# Customer patterns — end-to-end flows

Multi-tool patterns that keep coming up. Use alongside the domain skills.

## Decision trees

### Same-channel rollup vs cross-channel join vs summed metric

"I want combined numbers":

```
Do the sources share a channel (all Google Ads, all Meta)?
├── Yes → Source group. See whatagraph-source-groups.
└── No  → Does the widget need to join them on a shared dimension (campaign_name, date)?
         ├── Yes → Blend. See whatagraph-blends.
         └── No  → Custom metric, map_type=data_aggregation. See whatagraph-custom-metrics.
```

### Filter scope

```
Does this filter apply to EVERY widget using this source?
├── Yes → Source-level filter on the source/source-group
└── No  → Is the same filter needed on many widgets across a report?
         ├── Yes → Saved filter config, apply per widget (see whatagraph-filters)
         └── No  → Set filter inline on the widget via manage-widgets options
```

### Template linked vs one-off

```
Will this client ever need heavy structural custom changes?
├── Yes → Duplicate from an existing report (manage-reports action=duplicate) — independent copy
└── No  → Create from template (manage-reports action=create_from_template) — linked, auto-updates
```

### Overview (measurement) vs report

```
One-page KPI dashboard with 4–8 tiles that execs want to glance at?
├── Yes → Overview / Measurement (whatagraph-overviews)
└── No  → Report with tabs (whatagraph-reports)
```

### Source group vs blend

```
Are all the sources the same channel (e.g. all Google Ads)?
├── Yes → Source group (whatagraph-source-groups)
└── No  → Blend (whatagraph-blends)
```

## End-to-end flows

### 1. Onboard a new client

1. `view-team action=show_subscription` — confirm seat/asset headroom.
2. `manage-spaces action=create name="Client Name"` — capture the new `client_id`.
3. `list-integrations action=list_accounts channel_id=<id>` per channel in use.
4. `list-integrations action=list_available_sources account_id=<id>` to find the client's sub-accounts.
5. `manage-integrations action=add_sources channel_id=<id> account_id=<id> source_ids=[...]` per channel.
6. `manage-integrations action=sync_to_clients source_id=<id> client_ids=[<client_id>]` to attach each source to the space.
7. Decide: single-source report, source group, or blend?
   - Multiple accounts on the same channel → source group.
   - Multi-channel view → blend.
8. `manage-reports action=create_from_template client_id=<client_id> template_id=<tpl>` — apply the team's standard report template.
9. `manage-reports action=change_sources report_id=<new_id> source_mapping={"0": <new_source_id>, "<old>": <new>}` — swap template sample data for the client's sources.
10. `manage-themes action=enable_theme report_id=<id> theme_id=<client_theme_id>` + `enable_color` with the brand palette.
11. `manage-sharing action=create report_id=<id> require_password=true password="..."` — generate the client share link.
12. `manage-automations action=create` — schedule monthly delivery.

### 2. Cross-channel paid media report

Inputs: Google Ads, Meta Ads, LinkedIn Ads sources; GA4 for revenue.

1. Create a source group per channel when a client has multiple ad accounts on one platform. `manage-source-groups action=create`.
2. Build a blend that joins each channel (or channel source group) on `campaign_name` + `date`. Start with `join_type=full` unless you know dimensions align perfectly. `manage-blends action=create`.
3. Create a custom metric `map_type=data_formula` for Blended ROAS on the blend. `formula="A/B"`, `formula_value_type="float"`.
4. `manage-reports action=create` → add tabs Overview, Google, Meta, LinkedIn, GA4, Blended (via `manage-report-tabs action=create`).
5. On the Blended tab, widgets point at the blend's source and use the Blended ROAS custom metric.
6. `manage-sharing action=create` for the client share link.
7. `manage-overviews action=create` for a client-facing KPI summary.

### 3. Fix "data doesn't match the platform"

1. `list-sources action=show source_id=<id>` — check currency and access status.
2. Compare source currency with the report/team default. Mismatch → `manage-sources action=set_currency`.
3. Check source status — if `issue`, the source is disconnected; have the user reconnect in UI.
4. `fetch-data source_id=<id> metrics=[...] from=... till=...` — does the raw data match the platform's own export?
   - Yes → issue is at widget level (wrong filter, wrong formula, wrong dimension pairing).
   - No → issue is upstream (stale ETL, rate limits, attribution lag). Try again after a few minutes.
5. Scan saved filters for stale entries: `list-filters action=list source_id=<id>`.
6. Cross-check `list-sources action=list_usage source_ids=[<id>]` — a different variant (another source group or blend) may be feeding the widget you think is direct.

### 4. Rebrand all reports for a client

1. `manage-themes action=create_theme` with client logo (hosted on public CDN) and fonts.
2. `manage-themes action=create_color` with brand chart + widget palette (8–12 colors).
3. For each client report: `manage-themes action=enable_theme` + `enable_color`.
4. Spot-check the first report via `manage-sharing action=download_pdf` to confirm the branding renders.

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
3. Data QA: `manage-sharing action=download_pdf` → skim the PDF → fix issues.
4. Create share link: `manage-sharing action=create report_id=<id> require_password=true password="..."`.
5. Capture the URL from the response and hand it to the client.
6. If recurring, attach an automation: `manage-automations action=create frequency=monthly receivers=["client@..."] time_zone="Europe/London"`.

## Common pitfalls across flows

- **Reference IDs from the wrong domain** — spaces use `client_id`, sources use `source_id` (integration_source_id), widgets use `widget_id`. Skills state the required naming.
- **Mixing up channel-native vs Whatagraph-native report type names** — custom metrics use channel-native names (e.g. `campaign`); source groups use Whatagraph-native names (e.g. `campaign_performance`). Wrong family → "Report type X not found for channel Y".
- **Creating from template without running `change_sources`** — widgets stay on sample data.
- **Automations without `time_zone`** — always include IANA timezone; local time ≠ team timezone by default.
- **Sharing link without password on sensitive reports** — anyone with the URL can view.
