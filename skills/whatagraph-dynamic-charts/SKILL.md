---
name: whatagraph-dynamic-charts
type: domain
description: Build chart families that have no dedicated widget type — scatter, bubble, heatmap, calendar heatmap, candlestick, box plot, radar, funnel, pie/donut/rose, polar bars, stacked and 100% stacked bars and areas, horizontal bars, bars-plus-line combo, top-N ranking — with the Dynamic Chart widget and a `chart_spec`. Also covers reference lines, running totals, and splitting one metric into a series per dimension value. Use when the chart asked for cannot be expressed by the standard widget types, or when writing, dry-running, or debugging a `chart_spec`.
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

Funnel and heatmap are the two families that exist in both places, and each has a widget type
of its own as well as a series type here. The native widget wins for the plain chart. Use the
series here only when the chart also needs something a dynamic chart adds, such as a
sort-and-limit transform over the stages, a reference line, or a running total.

| Asked for | Use |
|---|---|
| A plain funnel | Native Funnel widget (`115`) |
| A funnel that also needs a transform or a reference line | Dynamic chart, `funnel` series |
| A plain heatmap of one metric across two categorical dimensions | Native Heatmap widget (`138`) |
| A heatmap that also needs a transform or a reference line | Dynamic chart, `heatmap` series |
| One square per day across weeks and months (a calendar heatmap) | Dynamic chart, `calendar_heatmap` series. There is no widget type for this |

A "calendar heatmap" is not the native Heatmap widget under another name. The native widget
plots two categorical dimensions against each other, so it cannot lay days out in a calendar.
When the user says calendar, they mean `calendar_heatmap`.

A spec describes the chart in terms of the widget's **bindings** — which bound column drives
which visual channel — never in terms of values. The backend re-compiles it against freshly
loaded data on every render, so the chart stays correct when the date range, filters, or
bindings change.

## Use this when

- Two metrics against each other (spend vs conversions, CPC vs volume) → scatter.
- The same, plus a third metric as point size (budget, impressions) → bubble.
- One metric across **two** categorical dimensions (day × hour, channel × device) → heatmap.
- One metric per **day** over a long range, as one coloured square per day laid out in weeks
  and months → `calendar_heatmap`. Binds one date dimension and one metric.
- A ranked "top 10 campaigns by spend" bar → `sort` + `limit` on a bar series.
- A volume metric as bars with a rate metric as a line over the same dimension → combo.
- Open/close/low/high per period → candlestick.
- Share of a total across one dimension → `pie`, `donut`, or `rose` (slice radius also carries the value).
- A composition wrapped around a circle, for cyclical categories like hour or weekday → a stacked bar with `coordinate: "polar"`.
- How many survive each stage of an ordered sequence → `funnel`.
- The spread behind each category rather than one average, where the five summary numbers are already metrics → `boxplot`.
- A handful of things compared across the same three or more measures → `radar`.
- Parts adding up to a total over one dimension → bar or area series sharing a `stack`.
- Those parts as shares of each total rather than as their own sizes → the same, plus `stack_mode: "percent"`.
- Long category names, or more categories than fit across the tile → `orient: "horizontal"`.
- One metric as one series per value of a second dimension → `split_by`.
- A target, a benchmark, or the average of what is plotted, drawn as a rule across the chart → `reference_lines`.
- A metric as a running total along its axis → the `cumulative` transform.

Do **not** reach for this when a standard type already fits — a single trend line is a line
chart (`107`), share-of-total is a pie (`108`). Use the ordinary types where they apply; see
the `whatagraph-widgets` skill.

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
| `transform` | Applied in order before plotting. `sort`, `limit`, `cumulative`. `[{"op":"sort","by":"metric:spend","dir":"desc"},{"op":"limit","n":10}]` is how you build top-N — do not try to pre-filter the data. `{"op":"cumulative"}` turns the series into a running total, and carries the total across a gap in the data rather than dropping to zero. It needs no arguments: it adds up whichever channel the series measures. |
| `axes.x` / `axes.y` | Intent only: `category`, `value`, `time`, `log`. On a polar chart, x is the angle and y the radius. **There is no axis title** — reports never render one, so name the series instead (`series[].name`), which is what the legend and tooltip show. |
| `coordinate` | `cartesian` (default x/y grid) or `polar` for radial charts. Works with `bar`, `line`, `area`, `scatter`, `effectScatter` — not `heatmap`, `candlestick`, or `boxplot`. The pie family, `funnel`, `radar` and `calendar_heatmap` bring their own system and you never name it: setting `coordinate` for them is pointless, and they cannot share a chart with anything drawn in a different one. |
| `legend`, `tooltip` | `tooltip` is `item`, `axis`, or `none`. |
| `orient` | `vertical` (default) or `horizontal`, applied to the whole chart rather than to one series. A spec still binds the base axis to `x` and the measurement to `y`; the compiler swaps the axis roles. Binding a dimension to `y` stays an error either way. |
| `stack` | Series-level. Two series naming the same stack are drawn on top of each other, so the stack height is their total. |
| `stack_mode` | `absolute` (default) or `percent`. `percent` rewrites the values as shares of each stack's own total, which is how you get a 100% stacked chart. |
| `reference_lines` | Up to 4. Each is `{"value": 1000, "label": "Target"}`, or `{"op": "average", "label": "Average"}` to work the number out from what is plotted. `axis` picks `left` (default) or `right`. They need value axes, so on a polar, pie, funnel or radar chart they are skipped with a warning. They carry no colour, which follows the report theme. |
| `split_by` | Series-level, a dimension ref. One metric becomes one series per value of that dimension, which is otherwise not expressible because a series is fed by a single metric. |
| `indicators` | Series-level, radar only: the list of metric refs to draw an axis for, e.g. `["metric:sessions", "metric:users", "metric:views"]`. Three is the minimum. Radar names its value columns here instead of in `encode`. |
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
- **A dimension cannot drive a numeric channel.** `y`, `size`, `value`, the candlestick
  channels, the box plot channels and every radar indicator need metrics. A dimension there
  renders something meaningless, so it is rejected. `split_by` is the opposite: it needs a
  dimension, and a metric there is rejected too.
- **Candlestick channels are read positionally** (`open`, `close`, `low`, `high`). Binding
  them out of order draws wrong candles instead of failing — only use it when the four
  metrics genuinely mean those things.
- **Box plot channels are read positionally too**, as `min`, `q1`, `median`, `q3`, `max`.
  Nothing is computed: those five metrics must already hold the minimum, lower quartile,
  median, upper quartile and maximum. A missing one shifts every value after it into the
  wrong part of the box, so a box plot with the wrong order draws wrong whiskers and
  reports nothing.
- **Radar reads metrics as axes, not as series.** Every metric in `indicators` becomes a
  spoke, and every value of the dimension draws a shape across all of them. It takes one
  widget row, and extra rows are reported as ignored. Sort and limit to a handful of
  shapes — twenty overlapping shapes show nothing.
- **A funnel draws its stages in the order the row returns them.** It does not re-sort them
  by size. When the row is not already in funnel order, add a `sort` transform.
- **A calendar heatmap needs a date dimension**, bound to `x`, with the metric on `value`.
  The calendar places each row on the day that row names, so a column holding anything else
  is rejected rather than drawn. When the row binds a date alongside other dimensions, the
  date is the one the family uses, whichever order they are bound in.
- **A calendar heatmap spans the days the rows cover**, not the report's date range, so a
  chart drawn over a shorter window is not mostly empty squares. It wants a long range with
  daily data. Over a week or two it is a single row of squares and a bar chart reads better.
  It takes one widget row, and extra rows are reported as ignored.
- **Not every type can be split.** The pie family, `funnel`, `radar`, `heatmap`,
  `calendar_heatmap`, `candlestick` and `boxplot` cannot be, because their groups would be drawn on top of each
  other or their channels already describe one period rather than a group within it. A
  `split_by` on one of those does not fail the call: the series is drawn whole and a warning
  says so, so read the warnings rather than assuming it applied.
- **A split counts against a ceiling of 12 drawn series for the whole chart.** Past that the
  largest groups are drawn and a warning names how many were left out, which looks exactly
  like a complete chart. Sort and limit the row, or split by a dimension with fewer values.
- **Percent stacking only touches series that name a stack.** With none stacked there is no
  total to take a share of, so the values are drawn as they are and a warning says so. The
  normalized columns are then reported as percentages, so they lose the currency they were
  declared with.
- **Horizontal is ignored by heatmap, calendar heatmap and candlestick.** All three fall back
  to vertical with a warning: a heatmap spends both axes on categories, a calendar has no
  axes to turn, and ECharts does not rotate a candle.
- **Pass the spec as the top-level `chart_spec`**, never inside `options` — only the top-level
  parameter is validated and compiled.
- **The pie family takes `itemName` + `value`, not x/y**, and has no axes. It cannot share a chart with a series that needs them — one chart per family. `donut` and `rose` are `pie` with a different shape, so pick the name that matches the chart you mean. `funnel` takes the same bindings and the same rule. `radar` also positions itself, in a system of its own, so it cannot share a chart either.
- **Always sort and limit a pie or a scatter over a high-cardinality dimension.** A donut with 30 slices, or a scatter with 200 points, is noise — and it hides the very change you were looking for.
- **Sizing.** A dynamic chart defaults to a full-width 6×3 tile. Categorical x-axes need that
  width or labels truncate; scatter and heatmap read well closer to square. A calendar
  heatmap needs the full width, because its squares run left to right across the months.

## Not available yet

These fail validation deliberately — an operation that exists but does nothing is worse than
one that is absent, because you would build on it:

| Asked for | Why not | Offer instead |
|---|---|---|
| Bump / rank-over-time chart | Needs a `rank` transform that does not exist yet | Top-N bar, or a line of the underlying metric |
| Treemap, sunburst, sankey | Need hierarchical or link-shaped data, and aggregation the compiler does not do | Donut for composition, top-N bar for ranking |
| A box plot from raw rows | Nothing computes the quartiles. `boxplot` plots five metrics that already hold them | Scatter of the same rows, until the five summary metrics exist |

Say plainly that the family is not available and offer the nearest shipping one — do not
approximate it with a chart that looks similar but means something else.
