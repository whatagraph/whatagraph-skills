---
name: binding-page-data
type: workflow
group: report_building
description: Bind the numbers of an HTML page made with create-document to the data they come from, so the page fills them in when it is saved, refreshes them later with no agent, switches date range and comparison on the page, and shows where each number came from. Load it before you write an HTML page that shows numbers from the customer's connected sources, such as a dashboard, a performance report, a scorecard, an account or campaign table, a chart of results over time, or any page the user wants "live", "kept up to date", "refreshed automatically" or "linked to the data". Also covers a number looked up on the internet, such as a benchmark. It does not apply to Whatagraph reports, to Markdown, CSV or text files, or to files made on the team computer.
required_tools:
  - create-document
  - list-sources
optional_tools:
  - tool_name: fetch-data
    purpose: Look at the rows a dataset will return before the page is built around them.
  - tool_name: read-document
    purpose: Read the page back before changing its manifest.
---

# Binding page data

An HTML page cannot fetch anything: the preview blocks every request. A page that shows a
customer's numbers therefore holds them, and numbers you type into it are wrong the next day and
cannot be traced.

Bind them instead. The page carries a **manifest** that says which query each number comes from.
Whatagraph runs the queries when you save the page, writes the numbers into it, and runs them again
on the schedule the person picks in the viewer, with no agent. The reader can switch the date range
on the page, on a share link and in a downloaded copy, and hovering a number shows its source,
metric, dates and fetch time.

Bind every number on the page that comes from a connected source. Type a number only when it is
part of the text someone wrote, such as a date or a target quoted in a sentence.

## 1. The manifest

Put one script element in the page's head. Whatagraph stores the fetched rows in a second element
beside it; never write that one yourself.

    <script type="application/json" id="wg-lineage">
    {
      "version": 1,
      "params": {
        "range": {"type": "date_range", "options": ["last7Days", "last30Days", "last90Days"], "default": "last30Days"},
        "compare": {"type": "compare", "options": ["previous", "last_year"], "default": "previous"}
      },
      "datasets": {
        "totals": {
          "resolver": "whatagraph",
          "label": "Google Ads account totals",
          "source_id": 4821,
          "metrics": ["cost", "clicks", "impressions", "conversions"],
          "date_range": "$range",
          "compare": "$compare"
        },
        "campaigns": {
          "resolver": "whatagraph",
          "source_id": 4821,
          "metrics": ["cost", "clicks", "conversions"],
          "dimensions": ["campaign"],
          "date_range": "$range",
          "compare": "$compare"
        }
      },
      "values": {
        "spend": {"dataset": "totals", "metric": "cost", "format": "currency:GBP:0", "label": "Spend"},
        "spend_change": {"dataset": "totals", "metric": "cost", "of": "change", "format": "change"},
        "ctr": {"dataset": "totals", "ratio": ["clicks", "impressions"], "format": "percent:2", "label": "CTR"},
        "brand_spend": {"dataset": "campaigns", "metric": "cost", "where": {"campaign": "Brand UK"}, "format": "currency:GBP:0"}
      }
    }
    </script>

**A dataset is one query**, and one fetch serves every value that reads it. Ask for few datasets
with several metrics each, not one dataset per number. A page has at most 40.

- `source_id`, `metrics` (1 to 20), `dimensions` (up to 6), `report_type` and `filters` mean what
  they mean in `fetch-data`. Take every field name from `list-sources action:
  list_dimensions_and_metrics` for that source and report type; a guessed name fails the fetch.
- `limit` is the most rows kept, 200 unless you say otherwise and at most 5000. A daily series by
  campaign needs a high limit.
- `date_range` is a period key (`yesterday`, `last7Days`, `last14Days`, `last30Days`, `last90Days`,
  `thisMonth`, `lastMonth` and the others the report calendar has; a wrong key is answered with
  the full list), fixed dates as `{"from": "2026-01-01", "till": "2026-03-31"}`, or `"$name"` to
  follow a parameter.
- `compare` is `none`, `previous`, `last_year`, or `"$name"`.
- An id starts with a letter and holds only letters, digits and underscores.

**A parameter is a control the reader switches.** Its type is `date_range` or `compare`, with up
to 6 options and a default. Every option is fetched and stored at each refresh, which is why the
control works with no network, and why options cost fetches: offer the ranges the reader will use,
not all of them. A page has at most 4 parameters. Anything else the reader switches, such as an
account or a campaign type, is a filter the page's own script applies to rows it already has.

**A value is one figure of a dataset.**

- `metric` reads one metric. Without `where` it is the dataset's total; with `where` it is the sum
  over the rows whose dimensions equal the given text exactly.
- `ratio: [a, b]` divides one summed metric by another. Use it for every rate (CTR, CPC, CPA, ROAS,
  conversion rate) whenever the dataset has dimensions, because a rate summed over rows is wrong.
- `of` picks which figure: `current` (the default), `previous`, `change` (the relative change, a
  ratio) or `delta` (the difference). The last three need the dataset to have a `compare`.
- `format` is `number`, `currency:GBP`, `percent`, `change`, `multiple` or `compact`, each with an
  optional count of decimals at the end, as in `number:1` or `currency:EUR:0`. `percent` and
  `change` take a ratio: 0.042 shows as 4.2%, and `change` adds the sign.
- `label` is the name the hover card shows.

## 2. The markup

    <b data-wg-value="spend">–</b>
    <span data-wg-value="spend_change"></span>
    <button data-wg-param="range" data-wg-option="last7Days">7 days</button>
    <select data-wg-param="compare"><option value="previous">vs previous</option><option value="last_year">vs last year</option></select>
    <span data-wg-period="totals"></span> compared with <span data-wg-period="totals:previous"></span>

- `data-wg-value` fills the element with the value's formatted text. Type `–` inside it, never a
  number. The element also gets `data-wg-sign` (`positive`, `negative`, `zero`, `none`), so CSS
  can color a change.
- `data-wg-param` with `data-wg-option`, or on a `select`, switches a parameter. The picked option
  gets `data-wg-active`.
- `data-wg-period` shows the dates of a dataset's current range, or of its comparison.

Do not use a `form` element for the controls.

## 3. Tables and charts the page draws itself

A table of campaigns or a chart over time has as many numbers as the data has rows, so the page's
script draws it from the stored rows through `window.wgLineage`:

    wgLineage.ready(function (lineage) {
      function draw() {
        var rows = lineage.rows('campaigns');   // [{campaign, cost, clicks, conversions, previous: {...} or null}]
        // build the table or the chart from rows
      }
      draw();
      lineage.on('change', draw);               // a parameter switched, or new data arrived
    });

- `rows(id)` gives each row as an object by field name, with `previous` holding the same row of
  the comparison. `dataset(id)` gives `totals`, `previous`, `from`, `till`, `source`, `fetched_at`.
- `format(number, format)` writes a number as the values do. `value(id)` gives `{number, text}`.
- So that a number the script writes still answers a hover, give its element
  `data-wg-figure='{"dataset": "campaigns", "metric": "cost", "where": {"campaign": "Brand UK"},
  "format": "currency:GBP:0"}'`; with a `format` it is filled for you. Give a chart or a number
  worked out from several rows `data-wg-dataset="campaigns"` instead.
- Draw only from `rows` and `dataset`. A copy of the numbers in the script does not refresh.

## 4. A number from the internet

A benchmark or a competitor's price has no connected source. Give it a dataset with the `agent`
resolver, and say exactly what to look up, so that the same lookup can be repeated later:

    "benchmark": {"resolver": "agent", "label": "Search ads benchmark",
      "instruction": "The average click-through rate of Google Ads search campaigns across all industries, from the most recent WordStream benchmarks report. Store it as metric `ctr`, as a ratio (0.0642 for 6.42%)."}

A value reads it like any other: `{"dataset": "benchmark", "metric": "ctr", "format": "percent:2"}`.
Look the number up, then store it with the `data` argument of `edit-document`, with the address of
the page you read it on. A refresh asks an agent to look it up again.

## 5. After the save

The result of `create-document` and `edit-document` has a `lineage` field when the page is bound.

- `fetched` names the datasets that were fetched. A save that leaves a dataset unchanged does not
  fetch it again, so editing the markup costs nothing.
- `problems` lists what is wrong: a field the source does not have, a value that names a metric
  its dataset does not fetch, an element bound to an id the manifest lacks. Fix each one with
  `edit-document` before you reply. A manifest with a problem is saved as written and nothing is
  fetched, so the page shows `–` until it is fixed.
- The save changes the page, so use the `checksum` of the result for the next edit.

`read-document` shows the page without the stored rows. To see the numbers, look at the
screenshots of the check, and compare two or three of them with `fetch-data` for the same range.

In the reply, say that the numbers are linked to the data, which controls the page has, and that
the person sets how often it refreshes with the data control at the bottom left of the viewer.
