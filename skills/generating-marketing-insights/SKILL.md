---
name: generating-marketing-insights
description: >-
  Generate executive summaries, trend analysis, performance narratives, and
  actionable recommendations from Whatagraph marketing data. Use when the user
  asks for insights, wants a performance summary, needs help writing report
  commentary, asks "how did we do this month?", "give me the highlights",
  or wants data-driven recommendations for their marketing strategy.
---

# Generating Marketing Insights

Transform raw marketing data into meaningful narratives, executive summaries, and actionable recommendations. This skill combines data fetching with analytical interpretation to deliver business-ready insights.

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

4. **Are there overviews/KPI dashboards?**
   ```
   list-overviews action: list
   ```

### Step 2: Fetch Performance Data

Fetch data for the relevant period and channels:

```
fetch-data source_id: <id>, report_type: "<type>",
  metrics: ["impressions", "clicks", "spend", "conversions", "conversion_value"],
  dimensions: ["date"],
  from: "<period_start>", till: "<period_end>"
```

For period-over-period comparison, also fetch the previous period:
```
fetch-data source_id: <id>, ...,
  from: "<previous_period_start>", till: "<previous_period_end>"
```

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

If goals are set (check with `view-goals`):

1. **Progress vs. target** — What percentage of the goal has been achieved?
2. **Pace analysis** — Is the current pace sufficient to hit the target?
3. **Gap analysis** — How much improvement is needed to close any gap?
4. **Contributing factors** — What's driving or hindering progress?

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

## Tips

- Always check for goals (`view-goals`) and overviews (`list-overviews`) — the user may have already defined what metrics matter most to them.
- When the user asks for "insights", start broad (executive summary) and offer to drill deeper into specific channels or metrics.
- For recurring reports, establish a consistent structure so comparisons across periods are straightforward.
- Include both absolute numbers and percentages — executives prefer percentages, operators prefer absolute values.
- When data shows a significant negative trend, frame it constructively: identify the cause and suggest solutions rather than just highlighting the problem.
