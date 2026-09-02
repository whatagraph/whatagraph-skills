---
name: whatagraph-dynamic-charts
type: domain
description: Build chart families that have no dedicated widget type — scatter, bubble, stacked bar/area, heatmap, calendar heatmap, candlestick, box plot, pie/donut/rose, funnel, radar, polar bars, top-N ranking — with the Dynamic Chart widget, either by naming a `chart_type` or by writing a `chart_spec`. Use when the chart asked for cannot be expressed by the standard widget types, or when writing, dry-running, or debugging a chart.
required_tools:
  - list-sources
  - list-widgets
  - manage-widgets
---

# Dynamic charts

Tools covered: `list-widgets` (`chart_presets`), `manage-widgets` (`chart_spec`, `dry_run`).

Whatagraph has a widget type per chart family — column, line, pie, funnel, geomap. When a user
wants a family that is not on that list, you do not need a new widget type: create a **Dynamic
Chart** (`widget_type_id: 142`, name `dynamic_chart`) and describe the chart with a
`chart_spec`.

A spec describes the chart in terms of the widget's **bindings** — which bound column drives
which visual channel — never in terms of values. The backend re-compiles it against freshly
loaded data on every render, so the chart stays correct when the date range, filters, or
bindings change.

## Use this when

- Two metrics against each other (spend vs conversions, CPC vs volume) → scatter.
- The same, plus a third metric as point size (budget, impressions) → bubble.
- One metric across **two** categorical dimensions (day × hour, channel × device) → heatmap.
- A ranked "top 10 campaigns by spend" bar → `sort` + `limit` on a bar series.
- A volume metric as bars with a rate metric as a line over the same dimension → two series in one `chart_spec`. There is no `combo` family any more; each row picks its own series type.
- Open/close/low/high per period → candlestick.
- Minimum, lower quartile, median, upper quartile and maximum per category → box plot.
- Share of a total across one dimension → `pie`, `donut`, or `rose` (slice radius also carries the value).
- Stages of a conversion, largest first → funnel.
- Several metrics compared shape-against-shape, three or more axes → radar.
- One metric per day across weeks and months → calendar heatmap.
- Metrics summed on top of each other, per row → stacked bar or stacked area.
- A composition wrapped around a circle, for cyclical categories like hour or weekday → a stacked bar with `coordinate: "polar"`.

Do **not** reach for this when a standard type already fits — a single trend line is a line
chart (`107`), share-of-total is a pie (`108`). Use the ordinary types where they apply; see
the `whatagraph-widgets` skill.

## Name a `chart_type` first, and only reach for `chart_spec` when no family fits

`manage-widgets` takes a `chart_type`: the family name, with the bindings read off the
widget's own rows on every render. That is the normal way to set one up. The user can then
edit the widget in the drawer, and adding a metric plots it.

    chart_type: line | area | bar | stacked_bar | stacked_area | scatter | bubble
              | candlestick | boxplot | heatmap | calendar_heatmap
              | pie | donut | rose | funnel | radar | polar_stacked_bar

`list-widgets` with `action=chart_presets` returns the current list with what each family
needs bound, so read it rather than trusting this one.

A `chart_spec` pins every column by id, so the chart stops following the bindings and the
user can no longer change what it plots in the drawer. Use it only for a chart no family
describes — two different series types on one grid, say, such as bars plus a line.

## The loop

Work in this order. Skipping step 3 is how you ship a chart that plots nothing.

1. **Bind the data first.** A dynamic chart reads ordinary widget rows. Create or update it
   with `rows[].configs[].options.metrics` / `.dimensions`, exactly as for any other widget.
   The spec can only reference columns that are actually bound. (Use `metrics` /`dimensions` —
   the `integration-metrics` echo keys are accepted as input but do not create the bindings.)
2. **Start from a preset.** `list-widgets` with `action=chart_presets` returns one entry per
   family with a runnable `example_chart_spec`, the channels that family requires, and how
   many metrics/dimensions it needs. No `report_id` required.
3. **Dry-run it.** `manage-widgets action=update widget_id=<id> dry_run=true chart_spec={…}`
   compiles the spec against the widget's real data and saves nothing. Read the response:

   | Field | What it tells you |
   |---|---|
   | `bindings` | One line per series naming the column behind each channel and how many points were plotted. **Read this.** "0 points plotted", or a column name you did not expect, is the bug. |
   | `available_columns` | What each row actually binds, per row index — use it to fix a bad ref. |
   | `sample_rows` | The head of each dataset, after any sort/limit. |
   | `option` | The compiled ECharts option. |

4. **Save it.** Re-send without `dry_run`. Create and update both return the spec read back
   from the database plus the same `bindings` digest, so you can confirm what was stored.

A dry run only compiles the spec — it rejects a call that also carries `rows` or `options`
rather than silently dropping them, and it needs an existing widget, so it works with
`action=update`, not `create`.

## Writing a spec

```json
{
  "series": [
    {
      "type": "scatter",
      "row": 0,
      "encode": {
        "x": "metric:spend",
        "y": "metric:conversions",
        "size": "metric:clicks",
        "itemName": "dimension:campaign"
      }
    }
  ],
  "axes": {
    "x": { "type": "value" },
    "y": { "type": "value" }
  },
  "legend": true,
  "tooltip": "item"
}
```

| Key | Meaning |
|---|---|
| `type` | The series type. `chart_presets` returns the current list; anything outside it is rejected rather than drawn blank. |
| `row` | Zero-based index of the widget row this series reads (default `0`). Several series may read the same row or different rows. |
| `encode` | Which bound column drives which visual channel. Refs are `metric:<external_id>` / `dimension:<external_id>`; `metric:0` / `dimension:0` positional forms also work, but prefer by-id — it survives re-ordering of the bindings and you can verify it by reading the response back. |
| `size` | What turns a scatter into a bubble chart: a third metric becomes point size. |
| `transform` | Applied in order before plotting. `[{"op":"sort","by":"metric:spend","dir":"desc"},{"op":"limit","n":10}]` is how you build top-N — do not try to pre-filter the data. |
| `axes.x` / `axes.y` | Intent only: `category`, `value`, `time`, `log`. On a polar chart, x is the angle and y the radius. **There is no axis title** — reports never render one, so name the series instead (`series[].name`), which is what the legend and tooltip show. |
| `coordinate` | `cartesian` (default x/y grid) or `polar` for radial charts. Works with `bar`, `line`, `scatter`, `effectScatter` — not `heatmap` or `candlestick`. |
| `legend`, `tooltip` | `tooltip` is `item`, `axis`, or `none`. |
| `preset` | Optional label from the catalogue. The `series` carry the chart; the label carries nothing. |

Tick formatting, label rotation, colours, grid geometry and data labels are deliberately
**not** in the spec — they follow the report's theme and its widget settings (`hide_legend`,
`show_chart_labels`, `decimal_place`, `currency`), which the report owns and you cannot see.

## Rules that will bite you

- **A dynamic chart with no `chart_spec` is refused at create.** There is nothing to draw, so
  no widget is created rather than a blank one left behind.
- **A spec whose refs do not resolve is refused too.** On create nothing is left behind; on
  update the previous spec is restored. The error names what the row actually binds — re-bind
  from that, do not retry the same spec.
- **If a row failed to load**, the error says so ("Rows that failed to load: row 0: warning —
  Metrics not selected"). That is a widget problem, not a spec problem: fix the bindings or
  the source, then dry-run again.
- **A dimension cannot drive a numeric channel.** `y`, `size`, `value`, and the candlestick
  channels need metrics. A dimension there renders something meaningless, so it is rejected.
- **Candlestick channels are read positionally** (`open`, `close`, `low`, `high`). Binding
  them out of order draws wrong candles instead of failing — only use it when the four
  metrics genuinely mean those things.
- **A box plot reads five metrics positionally** (minimum, lower quartile, median, upper
  quartile, maximum) and computes nothing. Bound out of order it draws a box whose whiskers
  and quartiles are wrong and reports nothing, so only use it when the row genuinely binds
  those five summary statistics.
- **A calendar heatmap needs a DATE dimension.** Anything else is refused, because the
  calendar places each row on the day it names. It wants a long range of daily data; over a
  week or two it is a row of squares and a bar chart reads better.
- **Pass the spec as the top-level `chart_spec`**, never inside `options` — only the top-level
  parameter is validated and compiled.
- **The pie family takes `itemName` + `value`, not x/y**, and has no axes. It cannot share a chart with a series that needs them — one chart per family. `donut` and `rose` are `pie` with a different shape, so pick the name that matches the chart you mean.
- **Always sort and limit a pie or a scatter over a high-cardinality dimension.** A donut with 30 slices, or a scatter with 200 points, is noise — and it hides the very change you were looking for.
- **Sizing.** A dynamic chart defaults to a full-width 6×3 tile. Categorical x-axes need that
  width or labels truncate; scatter and heatmap read well closer to square.

## Not available yet

These fail validation deliberately — an operation that exists but does nothing is worse than
one that is absent, because you would build on it:

| Asked for | Why not | Offer instead |
|---|---|---|
| Bump / rank-over-time chart | Needs a `rank` transform that does not exist yet | Top-N bar, or a line of the underlying metric |
| Gauge | Needs a minimum, maximum and target the spec has no channel for | The dedicated Gauge widget type (`139`) |
| Treemap, sunburst, sankey | Need hierarchical or link-shaped data, and aggregation the compiler does not do | Donut for composition, top-N bar for ranking |

Box plot and radar used to be listed here. Both ship now: `chart_type: boxplot` takes five
precomputed summary metrics, and `chart_type: radar` takes three or more metrics as its axes.
Do not refuse them.

Say plainly that the family is not available and offer the nearest shipping one — do not
approximate it with a chart that looks similar but means something else.
