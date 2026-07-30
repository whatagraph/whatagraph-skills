---
name: generating-marketing-insights
type: workflow
description: >-
  Generate executive summaries, trend analysis, performance narratives, and
  actionable recommendations from Whatagraph marketing data. Use when the user
  asks for insights, wants a performance summary, needs help writing report
  commentary, asks "how did we do this month?", "give me the highlights",
  or wants data-driven recommendations for their marketing strategy.
required_tools:
  - list-integrations
  - list-overviews
  - list-reports
  - view-goals
  - fetch-data
---

# Generating Marketing Insights

Transform raw marketing data into meaningful narratives, executive summaries, and actionable recommendations. This skill combines data fetching with analytical interpretation to deliver business-ready insights.

## Decision Point: Report Digest vs. Raw Data Insights

Before starting, check whether the user already has a Whatagraph report covering the relevant data:

- **User references a specific report or pastes a live-report URL** → use the `generating-report-digests` skill. It reads the report's pre-built widgets, date range, and comparison period in one call — no need to re-fetch raw data. Use the digest as the fact base and layer analytical narrative on top.
- **No existing report / user wants data not in any report** → proceed with the fetch-based workflow below.

## Insight Generation Workflow

### Step 1: Gather Context

Before generating insights, understand the scope:

1. **What channels are active?**
   ```
   list-integrations action: list_grouped
   ```

2. **What reports exist?** (to understand what the user already tracks)
   ```
   list-reports action: list
   ```

3. **What goals are set?**
   ```
   view-goals action: list
   ```
   Note: `view-goals` uses **page-number pagination** (`page`, `per_page` as "16"/"32"/"64"/"128", `last_page`, `total_count`), not cursor pagination. Goals may not exist on the account — if `total_count: 0`, skip the Goal Progress Framework and rely on raw data instead.

4. **Are there overviews/KPI dashboards?**
   ```
   list-overviews action: list
   ```

### Step 1.5: Discover Available Fields

Before fetching, look up the actual field IDs for each source. Field names vary by channel — `impressions` works on Facebook Ads but Google Ads uses `universal_metric_1`. **Never guess field names.**

```
list-sources action: list_report_types, source_id: <id>
list-sources action: list_dimensions_and_metrics, source_id: <id>, report_type: "<type>", premade_only: true
```

`premade_only: true` returns the ~10-20 headline metrics (cost, clicks, impressions, conversions, etc.) — usually sufficient for an insights summary. Copy `external_id` values verbatim into your `fetch-data` call.

### Step 2: Fetch Performance Data

Fetch data using the field IDs discovered above:

```
fetch-data source_id: <id>, report_type: "<type>",
  metrics: [<ids from list_dimensions_and_metrics>],
  dimensions: ["date"],
  from: "<period_start>", till: "<period_end>"
```

For period-over-period comparison, use `compare_type` in a **single call** (no need for two separate calls):
```
fetch-data source_id: <id>, report_type: "<type>",
  metrics: [...], dimensions: ["date"],
  from: "<period_start>", till: "<period_end>",
  compare_type: "previous"
```

Supported `compare_type` values: `previous` (same duration shifted back), `last_year` (year-over-year), `custom` (with `vs_from`/`vs_till`). The response includes a `comparison` block with its own `rows` and `totals`.

### Step 3: Analyze and Narrate

Structure insights using the frameworks below.

## Insight Frameworks

### Executive Summary Framework

Use this structure for high-level performance summaries:

1. **Headline metric** — Lead with the single most important number (e.g., "Revenue grew 23% month-over-month")
2. **Key wins** — 2-3 positive trends or achievements
3. **Areas of concern** — 1-2 metrics that declined or underperformed
4. **Context** — External factors that may have influenced performance (seasonality, campaigns, market changes)
5. **Recommended actions** — 2-3 specific, actionable next steps

### Trend Analysis Framework

For time-series data:

1. **Overall direction** — Is the metric trending up, down, or stable?
2. **Rate of change** — How fast is it changing? Accelerating or decelerating?
3. **Anomalies** — Any spikes or dips that stand out?
4. **Patterns** — Weekly cycles, month-end effects, day-of-week patterns?
5. **Forecast implication** — If this trend continues, what does it mean?

### Channel Performance Framework

For cross-channel comparison:

1. **Efficiency ranking** — Which channels have the best ROAS/CPC/CPA?
2. **Volume contribution** — What share of total traffic/conversions does each channel drive?
3. **Trend by channel** — Is each channel improving or declining?
4. **Budget allocation** — Is spend proportional to performance?
5. **Opportunity identification** — Which channels could benefit from more/less investment?

### Goal Progress Framework

If goals are set (`view-goals action: list`), measure them before saying anything about progress:

```
view-goals action: status goal_ids: [<up to 20 ids>]
```

The response answers the first three questions directly — don't derive them by hand:

1. **Progress vs. target** — `percentage`, `current_value` vs `goal_value`.
2. **Pace analysis** — `projected_value` (where the metric lands at the current run-rate) against `goal_value`, plus `current_pacing` and `days_remaining`. `status: off_track` already encodes "the current pace misses".
3. **Gap analysis** — `remaining_value`.
4. **Contributing factors** — the one part `status` cannot answer; break the metric down by dimension with `fetch-data`.

Goals reported as `unknown` were not measured — name them as unchecked rather than folding them into the healthy pile.

## Writing Style for Marketing Insights

- **Lead with impact**: Start with the most significant finding, not background.
- **Use specific numbers**: "CTR increased from 2.1% to 3.4%" not "CTR improved significantly."
- **Provide context**: Compare to previous periods, industry benchmarks, or goals.
- **Be actionable**: Every insight should suggest a next step.
- **Use plain language**: Avoid jargon unless the audience is technical.
- **Quantify changes**: Use percentages for relative changes, absolute numbers for totals.

## Common Calculations

- **Period-over-period change**: `(current - previous) / previous * 100`
- **ROAS**: `conversion_value / spend`
- **CPC**: `spend / clicks`
- **CPA**: `spend / conversions`
- **CTR**: `clicks / impressions * 100`
- **Conversion rate**: `conversions / clicks * 100`

## Handling Incomplete or Ambiguous Data

- **Missing metrics**: If a needed metric isn't available, note the limitation and suggest alternatives.
- **Low data volume**: For small datasets, warn that trends may not be statistically significant.
- **Multiple attribution models**: When conversion numbers seem high, note potential multi-touch attribution overlap.
- **Stale data**: Check if the source's last sync date is recent. Outdated data should be flagged.
- **Duplicate KPI values**: if the source report has several KPIs displaying the same value (see the duplicate-KPI signal in `analyzing-reports`), do not produce an insight. Tell the user the report is misconfigured and offer to help diagnose. Insights written from a broken report mislead the customer.

## Tips

- Always check for goals (`view-goals`) and overviews (`list-overviews`) — the user may have already defined what metrics matter most to them.
- When the user asks for "insights", start broad (executive summary) and offer to drill deeper into specific channels or metrics.
- For recurring reports, establish a consistent structure so comparisons across periods are straightforward.
- Include both absolute numbers and percentages — executives prefer percentages, operators prefer absolute values.
- When data shows a significant negative trend, frame it constructively: identify the cause and suggest solutions rather than just highlighting the problem.
