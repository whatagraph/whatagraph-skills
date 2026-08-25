---
name: whatagraph-offline-reports
type: workflow
group: report_building
description: >-
  Build a complete Whatagraph report from numbers you already have, with no
  connected data source. Use when the user says "here is my analysis, make me a
  report", pastes figures, points at a spreadsheet or document, or asks for a
  deck-style leadership or board report that Whatagraph cannot pull by itself.
  Covers shaping external numbers into offline widgets, designing the page with
  text widgets, and the render limits that silently spoil a finished PDF.
required_tools:
  - list-reports
  - manage-reports
  - manage-report-tabs
  - manage-widgets
  - list-widgets
  - manage-themes
optional_tools:
  - tool_name: export-report
    purpose: Render the finished report to PDF to check the built output.
---

# Building a report from data you already have

Every other reporting playbook starts the same way: find a source, check its fields, bind a metric. This one does not. Here **you** are the source.

Use this when the numbers exist outside Whatagraph — an analysis you ran, a spreadsheet, a client's own figures, a board summary, anything no integration can supply. The report is built entirely from **offline widgets**, which hold their values directly.

Load `whatagraph-widgets` alongside this skill. That one has the exact payload shapes; this one is the order to do things in and the traps that only show up in the finished file.

## Use this when

- "Here is my analysis — build me a Whatagraph report from it."
- The user pastes figures, or points at a document or spreadsheet.
- A leadership, board or QBR report mixing commentary with numbers.
- Any report where the data does not come from a connected channel.

You can mix the two. A report may have connected widgets on one tab and offline widgets on another. Nothing here stops you binding real sources where they exist.

## Decide the shape before you build anything

Do not start creating widgets. Two decisions come first, and both are expensive to change later.

**1. What is the story?** An offline report is a document, not a dashboard. Group the numbers into sections, and give each section a tab. One tab per idea reads far better than one long tab, and it matters mechanically: in a PDF **each visible tab becomes exactly one page**. A tab is never split and never shares a page. So a section break belongs on a new tab, not lower down the same grid.

**2. What does each number want to be?** Map every figure to a widget type before you place anything:

| You have | Use | Type |
|---|---|---|
| One headline figure, maybe with a comparison | Single value | `125` |
| A ranked or itemised list | List | `127` |
| Rows and columns | Table | `126` |
| A value per period | Column `128`, Area `129`, Bar `130`, Line `131` |
| Parts of a whole | Pie `132`, Donut `133` |
| Progress toward a target | Goal | `135` |
| Stage-by-stage drop-off | Funnel | `136` |
| Narrative, headings, framing | Comment | `21` |

**Gaps to plan around.** There is no offline Heatmap, Gauge, GeoMap or Dynamic chart, and `134` does not exist (it is the Image position, and there is no offline image type). For a heatmap from manual data, use a Table with block shading — see below.

## Build order

1. **Create the report**, then its tabs, in reading order.
2. **Place a Comment widget at the top of each tab** as its heading. Do this first, not last — it forces you to name the section and it fixes the vertical rhythm of the page.
3. **Add the data widgets**, budgeting height by row count *before* placing them (see "Row budgeting").
4. **`hide_footer: true` on every offline widget.** One `manage-widgets action=batch_change_settings` pass over the whole report.
5. **Verify.** `list-widgets action=csv_export` confirms the values. It does **not** confirm the report looks right — see "Verifying".

## Shaping your numbers

Offline values go in a row-level `data` array. There are two shapes, and the widget type picks which one.

**Entry list** — Single value, List, Pie, Donut, Funnel, Goal:

```
rows=[{"data": [
  {"name": "New customers", "value": "418", "previous_value": "355"},
  {"name": "Churn",         "value": "27",  "previous_value": "31", "negative_ratio": true}
]}]
```

`name` is the visible label — an offline widget's metric name comes from here, so write it the way it should read on the page. `negative_ratio: true` tells the delta that a rise is bad, so costs and churn colour correctly instead of showing a red drop as a win.

**Header row + data rows** — Table and the time-series charts:

```
rows=[{"data": [
  ["Channel", "Spend",  "Leads", "CPL"],
  ["Search",  "12400",  "310",   "40.00"],
  ["Social",  "8900",   "154",   "57.79"]
]}]
```

Every row must have as many cells as the header — cells are read by position, so one short row shifts every column after the gap.

**Units drive formatting.** Values are stored as strings, and the formatter reads the unit: `"25%"` renders as a percentage, `"100 $"` as currency, `"12.5"` to one decimal place. So decide the presentation when you write the value. `null` renders blank.

**One row holds many values.** A three-item List is *one* row with three entries, not three rows. Use extra rows only for genuinely separate series, such as two lines on a line chart — and then give every row its own `data`.

## Row budgeting — do this before you place a table

A Table or List renders only the rows that fit its box and **drops the rest with no marker**. No ellipsis, no scrollbar in the PDF, no warning on write. `csv_export` still returns every row, so a data check passes while the page is wrong. This is the single most common way an offline report ships with a factual error in it.

Budget first: a table shows roughly `3.5 x height - 3` rows. So `height: 5` fits about 14.

- **20 or more rows: split into two side-by-side tables** (`3 + 3`). Each then shows half. This is the most reliable fix.
- **15 or more rows carrying one value each: use a Bar chart.** Charts scale to their space and never drop a series.
- **Always confirm the last row is present** in the rendered output. The arithmetic is a budget, not a guarantee.

## Text widgets are your design system

In a report built this way, Comment widgets usually carry a third of the page — every heading, every piece of framing, every methodology note. Treat them as layout, not as leftovers.

Supply the body as **HTML** in `comment_widget_text.text` whenever a block needs any structure — markdown is rejected, and so is a hand-written Tiptap document (one bad node blanks the whole widget). You get `<h1>`-`<h3>`, `<ul>`, `<ol>`, `<blockquote>`, `<hr>`, plus `<strong>`, `<em>`, `<u>`, `<mark>`, `<a href>` and `<span style>` for colour and size.

Four patterns carry most of the work:

- **Section heading** — a `6x1` Comment at the top of each tab with an `<h2>`. A `height: 1` widget shows no *title*, but a Comment's heading is body text, so it renders.
- **Kicker + heading + rule** — a small muted `<p class="p4">`, then an `<h2>`, then an `<hr>`. This reads as a designed section opener rather than a stray sentence.
- **Value-coded emphasis.** Offline tables have no conditional formatting, but inside a Comment you *do* control colour per run of text. A `<span style="color: #1e8e3e">` on a good or bad number, or a `<mark>` for a background chip, is the only place in an MCP-built report where a number carries its own colour. `<mark>` is on or off — it takes no colour.
- **Cover and section dividers.** A Comment accepts a background image that renders full-bleed behind the text. That makes a cover **one** widget, not an image band stacked above a text block. Set `contentAlign: "center"` and a light text colour. Import the image first — see `whatagraph-assets`.

Use the product's named text styles rather than a raw `font-size`: `<h1>`-`<h3>`, and `<p class="p1">` to `<p class="p4">`. A custom `font-size` is stripped the moment somebody edits that block in the UI; the named styles survive.

## Faking a heatmap

Cell values are strings, so encode intensity in the text. Prefix a shade glyph per bucket — `█` highest, then `▓`, `▒`, `░`, and `·` for none — or use a short proportional bar like `██████░░░░`. This survives PDF rendering and needs no colour support.

Keep it to one glyph plus the number in a narrow column. A ten-cell bar overflows and the column truncates.

## Finishing touches that make it not look generated

- **`hide_footer: true` everywhere.** Every offline widget otherwise draws a footer announcing that the data is offline. In a client or leadership report that is exactly wrong.
- **Vary the KPI icons.** Every offline Single value defaults to the *same* icon, so an unvaried KPI row reads as machine-made at a glance. Pick one per card from `list-widgets action=list_icons`.
- **Never leave a widget without `data`.** A new offline widget renders the template's demo numbers (200,000 impressions against 15,000) and the call still returns success. The tool warns you; treat that warning as unfinished work.
- **Keep table cells on one line.** `wrap_text` breaks at the character, not the word, so a wrapped cell can split a word in half. Roughly 40 to 45 characters fits a four-column full-width table. Longer prose belongs in a Comment.
- **Watch title lengths.** Titles never wrap; they clamp to one line. Roughly 16 characters at `width: 1`, 38 at 2, 60 at 3, 84 at 4, 128 at 6. And a `height: 1` widget shows no title at all.

## Verifying

Three checks, and they catch different things:

1. **`list-widgets action=csv_export`** — confirms the *values* are right. It reads every row, including rows that will not render, so it cannot catch truncation.
2. **The `data_summary` on each write response** — confirms your data landed. Offline rows echo `headers` and `data_row_count`, or `entry_names` and `entry_count`. One trap: a widget created without `data` reports the *template's* sample headers, so check that the headers are yours.
3. **Look at the rendered output.** This is the only check that catches a dropped table row, a clipped title, an invisible chart label or a soft image. `export-report format=pdf` queues the render and returns a `pdf_job_id`; calling it again with that `pdf_job_id` gives you the download URL once it is ready (see `whatagraph-export`). Examine the file yourself if you can read it. If you cannot, ask the user to look, and tell them exactly what to look at: the last row of every table, and every page.

## Common pitfalls

- **Treating offline widgets as an edge case.** They are a first-class way to build an entire report. Nothing about a report needs a connected source.
- **Binding a metric on an offline widget.** There is no binding. `rows[].configs[].options.metrics` is rejected on these types — the values *are* the widget.
- **Building one long tab.** It becomes one very tall PDF page. Split by section into tabs.
- **Verifying with `csv_export` alone.** It passes on reports that render wrong. See "Verifying".
- **Leaving the offline footer on.** The fastest tell that a report was machine-built.
- **Faking a heading with an oversized bold paragraph.** Use a `heading` node. It is one attribute and it is theme-consistent.
