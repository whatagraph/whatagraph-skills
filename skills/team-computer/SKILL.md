---
name: team-computer
type: domain
group: computer
description: Use the team computer for Python analysis, files and finished deliverables. Covers charts, decks, workbooks and reports with the wgviz helpers, a customer's brand or the look of an attached file, a report turned into a deck, forecasts and marketing mix models, long work as background jobs, and looking at and checking every file before it is handed over.
required_tools:
  - computer-exec
optional_tools:
  - tool_name: computer-job
    purpose: Run commands that need more than 60 seconds and resume from the completion event.
  - tool_name: computer-write-file
    purpose: Save scripts or text inputs before execution.
  - tool_name: computer-read-file
    purpose: Read large output, job logs, existing inputs or a rendered page.
  - tool_name: computer-list-files
    purpose: Discover existing inputs and completed files without guessing paths.
  - tool_name: computer-export
    purpose: Deliver an existing file as a downloadable conversation card.
  - tool_name: computer-chart
    purpose: Present an interactive chart from a supported ECharts specification.
  - tool_name: computer-import-attachment
    purpose: Bring an attachment from this conversation onto the computer.
  - tool_name: computer-fetch-data
    purpose: Write connected marketing data directly to a local file.
  - tool_name: computer-http-request
    purpose: Request data from an outside API, with a secret from the person's vault when it needs one, and save the answer as a local file.
---

# Team computer

The tool descriptions say how each computer tool works. This skill covers what they do not: inputs,
long work, the answer to the person, and deliverables that look finished the first time.

## Files and inputs

Keep private or temporary inputs out of `/team` unless the person intends to share them. An
attachment of this conversation comes onto the computer with `computer-import-attachment`. For
connected marketing data use `computer-fetch-data` with discovered source and field identifiers;
do not rebuild a large dataset from chat snippets. Use only the tools granted to this agent.

Start the work without exploring the computer. The tool descriptions name the folders, so do not
print the environment, list `/runs` or read `.run.json` first. Save a file that a later turn or the
person needs in `/team/<project>/`, or in `/agents/<your id>/` when it is private. A `/runs/<run>/`
folder is scratch for one turn, and a later turn cannot write to it.

Build a deliverable with one script that makes the file, run it, check the saved file, then export
it. Do not write separate test scripts, and do not add charts, sheets or slides beyond what the
person asked for.

## Long work

A model fit (for example a Meridian mix model with more than one chain), a forecast over many
series, or any script you expect to run longer than about half a minute is background work with
`computer-job`, not an inline command: an inline command that hits its limit is charged and
wasted, and its partial output is unusable. A quick single-chain check may stay inline; the fit
you will report from runs as a job.

Report a timeout or a failure plainly. Run the job again only after fixing its cause and checking
whether partial output already exists. Reuse a valid completed result rather than charging for the
same job again. If the job cannot be made to work and you change the method (fewer samples, a
simpler model, resampling an existing fit instead of refitting), say so in the answer and label it
truthfully in every deliverable. Never describe a substitute method as the one that was asked for,
and state what the failed job was and why.

Create a wake-up, a reminder or a recurring schedule only when the person asked for one. A finished
job wakes this conversation by itself, so it needs none. When the person says when to check back
("stop and check back in two hours"), create one wake-up at that time, and do not check or message
them before it.

## The answer

Write to the person in their words. The answer names what was made, the two or three findings
that matter, and what to decide next. Leave out job and run IDs, folder paths, script names,
package names and formulas in LaTeX or code notation; the person sees the files as cards. When a
background job failed, say "the first attempt failed because ..., I fixed it and ran it again" in
those plain words; do not describe a failure as a relaunch or an adjustment.

One client's file does not show another client's results. When the person asks to compare a client
with another client of the agency, a file meant for the first client calls the other one "a
comparable client" and keeps its name out of titles, sheets and file names. Say in your answer
that you did this, and name the other client there only. Use the names in the file when the person
says the file is internal.

Deliver the files the person asked for. Do not export a Markdown or text file (notes, a summary, a
read-me or a log) that nobody asked for; say its content in the answer instead. A read-me sheet
inside a workbook is part of the workbook and is fine.

## Product-style outputs

Deliverables must look finished the first time: no label printed over another, no text
running out of its box, no table stretched to fill a slide, no empty half-slides, no
shadows, gradients or clip-art. The way to get that is to build every chart, deck,
workbook and report with the installed `wgviz` helpers and to let them lay things out,
instead of placing text boxes and shapes by hand with python-pptx or matplotlib.

- Charts for a file: `wgviz.charts` (`bar`, `grouped_bar`, `stacked_bar`, `line`,
  `donut`, `kpi_cards`, `quadrant`, `heatmap`, and for a long pack `waterfall`, `ranking`
  (sorted bars with "us" highlighted), `scatter`, `stacked_area`, `combo` (a volume with its
  rate) and `small_multiples`). They apply the
  product style, label the values, put the legend under the plot and wrap or slant long
  category labels. Do not call matplotlib directly for a deliverable.
- Charts in the conversation: build the option with `wgviz.echarts` (`line`, `area`,
  `bar`, `column`, `pie`, `donut`, `scatter`, `heatmap`, `quadrant`) and save it with
  `wgviz.echarts.save`; then `computer-chart`. The helpers reserve room for axis labels
  and the legend; a hand-written option is the usual cause of a cut-off label.
- A pack of thirty or more slides, a board pack, a market or competitor study: load the
  `board-pack` skill. It has the stages, the deck and workbook structure and the way to continue
  over several turns.
- Decks: `wgviz.deck.Deck`. Title slide, then one idea per slide: `kpis` (cards with a
  notes area), `chart` (a chart PNG with a commentary column), `table` (only as tall as
  its rows, up to 14), `bullets` (at most six short lines), `columns` (two text columns),
  `image` (a screenshot with numbered callouts and optional markers), `two_up` (two
  screenshots side by side with captions and up to four numbered observations),
  `section` (a divider with one statement). A long pack also uses `agenda`, `summary`,
  `statement` (one number set very large), `chart_grid` (two to four charts), `screenshot`
  (a web page in a browser window, or with `facts=` a competitor profile), `decisions`,
  `gallery` (two to six pages side by side), `matrix` (who offers what), `timeline`, `quote`,
  `sources` (links that open), `notes` (speaker notes) and `picture` (a slide that is mostly one
  photo or page); `wgviz.help("deck")` has each one's arguments. Text is measured and shrinks to
  fit; keep it short anyway.
  Never build slide layouts from raw shapes when a Deck method exists.
- Choose the slides and their order from the story this customer needs, not from a fixed
  outline: a pitch opens with the problem and the answer, a monthly report with the numbers, a
  quarterly review with results, what drove them and the plan. A short deck needs no agenda,
  section or sources slide.
- A Whatagraph report turned into a deck: read the report and its widgets with the Whatagraph
  report tools, as the `generating-report-digests` skill shows, and give every widget its own
  slide in the report's order, unless the person asks for another grouping. The slide's title
  says what the widget shows, its chart is drawn again from the widget's data with the matching
  chart helper, and a table widget becomes a `table` slide. Do not put several widgets on one
  slide to save slides.
- Workbooks: `wgviz.excel.write_table` per sheet; a chart in a workbook is a native
  Excel chart from openpyxl, never a pasted image, and the workbook carries the numbers
  behind every chart in the deck. A read-me or notes sheet is written with
  `wgviz.excel.write_text(sheet, [paragraph, ...], title="Read me")`, so a printed or PDF copy
  does not cut a sentence. Both helpers set the print layout; do not set column widths by hand.
  Give every table its number formats by column: `write_table(..., formats=["text", "eur", "int", "percent", "ratio"])`
  (the names are in `excel.FORMATS`). A percentage is stored as a share (0.042) with the
  `"percent"` format, never as the text "4.2%". `write_frame(ws, frame, formats={...})` writes a
  data frame, `link(ws, "B4", url)` an address that opens, `highlight(ws, ref, "ROI")` shades a
  column by value, and `add_chart` draws `bar`, `stacked`, `percent`, `horizontal`, `line`,
  `area`, `pie` and `scatter` (`columns=[2, 3]` picks the table columns to plot). A workbook of
  many sheets starts with `cover(wb, title=..., notes=[...])` and ends with
  `add_index(wb, descriptions={sheet: what it holds})` and `polish(wb)`.
- Reports: `wgviz.report.Report` for PDF or Word.

Style and brand. Every helper draws in one theme: by default the Whatagraph look (white and
light grey surfaces, near-black text, the Whatagraph pink as a small accent, Inter). A customer
who names brand colours, a typeface or a company name, attaches a logo or a file to follow, or asks
for their report theme gets exactly that, for every chart, slide, page and sheet of the deliverable:

- Brand colours in the request: `style.use(style.Theme.from_colors(["#0B3D2E", "#BEF264"], brand="Northstar Digital"))`
  before the first chart or `Deck(...)`; the first colour becomes the accent and the list the
  chart palette. Add `font="Georgia"` for a named typeface and `logo="/team/brand/logo.png"`
  for an attached logo (import the attachment first). `Deck(..., theme=...)` and
  `Report(..., theme=...)` accept the same theme.
- The customer's own PowerPoint template (an attached .pptx or .potx): import it and pass it as
  `Deck(..., template="/team/brand/template.pptx")`. Its master, background and body font are
  under every slide.
- No colours given, but the customer has a website: open its home page in the browser, save a
  screenshot and the logo image, and read the colours with `wgviz.images.brand_colors(path)`.
  Look at the logo and the page before you use them. A brand whose pages are dark gets
  `Theme.from_colors([...], background="#0B1F33")`; the text and the surfaces follow it.
- Photos of the customer's products, stores or campaigns (from their site or attached):
  `Deck(..., cover=path)` puts one on the title slide and `deck.picture(path, title=..., text=...,
  layout="right" | "left" | "full")` makes a slide of one.
- "Our report theme" or "the colours of our reports": read the applied palette with the themes
  tool (`show_color`), then `style.Theme.from_report_theme(payload, brand="Client A")`.
- An attached file that shows the look to follow (an earlier deck, a report PDF, a brand guide or
  an image): import it and look at every page (render a PDF or a deck with `wgviz.render.pages`
  first; read an image as it is). Copy its colours, its typeface and its layout, not only the
  colours: pass the colours and the typeface to `from_colors`, and follow where it places the
  title, the chart and the text, its cover and its closing page, with the Deck slide types that
  match. Never guess a brand colour from memory. Say in the answer which colours and typeface you
  used and what of the layout the helpers could not follow.
- One accent, at most three colours on a slide beside the chart palette, no gradients,
  shadows or clip art, and a chart placed on a slide that already has a title is drawn without
  its own title. Do not paint large areas in the accent.

Before handing a deck, a document or a workbook over, look at it: `deck.render(dir)` or
`wgviz.render.pages(path, dir)` writes one PNG per page, and `computer-read-file` on a
PNG shows it to you. Read every page image. If a label is cut, text overflows, two
elements overlap or a slide is mostly empty, fix the input (shorter text, fewer rows,
another slide type) and render again. Hand over only what you have seen. For a deck of more
than twelve slides use `deck.preview(dir)`: it renders the deck and tiles the pages twelve to a
sheet with their slide numbers, so forty slides are four pictures to read. Read every sheet, then
open a single page only where a sheet shows something to check.

Screenshots from the browser belong in these deliverables when the request is about what a page
looks like. Take each one as the `team-browser` skill describes. `Deck.screenshot`,
`Deck.gallery`, `Deck.image` and `Deck.two_up` place it; they cut a tall page from its top to the
shape of its frame and size the file, so twenty screenshots do not make the deck too heavy to
deliver. Pass the page's address as `url=` and the day as `captured=`, and write the observations
from what is visible in the picture, not from memory of the brand. `wgviz.images.crop(path,
top=0.2, height=0.5)` cuts the band worth showing when the top of the page is not it.

Read the helpers' signatures once, in one command, instead of opening their source:

```python
import wgviz
wgviz.help("deck")      # or wgviz.help() for every module: style, charts, echarts, deck, report, excel, forecast, mmm, render
```

`Deck(..., brand="the agency", client="the client")` writes both into the footer: the agency is
the author of the pack, the client is who it is about. `Deck(..., title_slide=False)` starts with
the first content slide when the person has named what the first slide is; a bullet may be a pair
`("Lead-in", "rest of the sentence")` for a bold lead-in, `bullets(..., numbered=True)` numbers the
list, and you never type a bullet, a dash or a number at the start of an item; `charts.bar(..., color=[...])` takes one colour per bar to highlight one of them.

| Output | Helper |
|---|---|
| PNG charts | `from wgviz import charts`: bar, grouped_bar, stacked_bar, line with bands, donut, kpi_cards, quadrant, heatmap, waterfall, ranking, scatter, stacked_area, combo, small_multiples |
| Branded PDF | `from wgviz.report import Report`: kpis, chart, table, heading, text, bullets, save |
| Branded 16:9 presentation | `from wgviz.deck import Deck`: kpis, chart (with takeaways and source), chart_grid, table, matrix, bullets, columns, image, two_up, screenshot (callouts or facts), gallery, agenda, summary, statement, decisions, section, timeline, quote, sources, notes, save, render, preview; `theme=` and `logo=` for a customer's look |
| Pictures | `from wgviz import images`: fit (crop to a shape and size for a slide), crop (cut a band), contact_sheets, size |
| Style and brand | `from wgviz import style`: `Theme`, `Theme.from_colors`, `Theme.from_report_theme`, `Theme.load`, `style.use`, `style.current` |
| Workbook | `from wgviz.excel import write_table, write_frame, add_chart, link, highlight, cover, add_index, polish, verify_totals, FORMATS` |
| Interactive chart | `from wgviz import echarts as ec`, then `computer-chart` if granted |
| Forecast | `from wgviz import forecast`: complete_weeks for a weekly series from daily rows; run with date_col, value_col and horizon; read `warnings`; target_plan, chart and echarts_option |
| Marketing mix model | `from wgviz import mmm`: fit with frame, channels and out_dir at `quality="standard"`, then validate (can it predict weeks it never saw), both in one background job; read `warnings`, `diagnostics`, the 90% intervals and the validation verdict; curves_chart for spend against return |

## Forecasts

A request to forecast or project a series (spend, conversions or revenue to month end,
next month or next quarter) is a statistical forecast: fit the forecast helper on the
daily or weekly history, and report the point forecast with its prediction interval and
the model it chose. A straight-line run rate (average per day times the days left) is
pacing arithmetic, not a forecast; show it alongside when the user asks about pacing, and
say which figure is which. A forecast chart shows the actuals, the forecast beyond the
last actual date and the interval band.

A weekly series for a forecast comes from `forecast.complete_weeks(daily, date_col=..., value_cols=[...])`,
which keeps full Monday-to-Sunday weeks only. A partial last week looks like a collapse to the
model and pulls the whole forecast down. Read `result["warnings"]` after every `forecast.run`: it
says when the last period looks incomplete and when the forecast total is more than a third away
from the same number of recent periods. Fix the input or explain the change before you report it.
A forecast of spend, clicks, conversions or revenue is never below zero; the helper cuts it there.

With under three years of weekly history the forecast carries no season. Put beside it what the
same weeks brought a year before and how the last 13 weeks compare with the year before, and say
when the forecast is therefore likely cautious. Forecast spend is an assumption.

## Marketing mix models

A marketing mix model is fitted on the whole business outcome per week (all new revenue, all
orders), with one spend column and, when there is one, one impressions column per channel. The
revenue or the conversions that the ad platforms attribute to themselves are not that outcome:
they leave no baseline, and the platforms count the same sale more than once. Look for a source
that holds the business result (sales, new business, orders, a CRM or a shop) before you settle
for platform numbers, and show the platforms' own claim beside the model's as a finding.

A mix model that a person will act on is fitted with `mmm.fit(...)` at its default
`quality="standard"` (four chains), as a background job, and `mmm.validate(frame, channels,
out_dir=...)` runs in the same job. `validate` refits with a fifth of the weeks held out at random
and says how well the model predicts them: `verdict` is "holds", "weak" or "fails", `reading` is
the sentence to say it with, and `expected_vs_actual.csv` is the chart. Do not hold out the last
weeks as one block: a mix model explains the past and is not a forecast, so that test fails for a
reason that says nothing about the channels. The baseline follows trend and season by itself
(`knots="auto"`). `mmm.curves_chart(result, path=...)` draws what each channel returns as its
spend grows, with a dot at today's spend: a curve that is flat at the dot is a channel where more
money no longer pays.

To reuse a finished fit, call `mmm.load(out_dir)`, which repeats the fit's warnings; do not read
`summary.json` yourself, and say in the answer and in the file that the fit is from an earlier run
and when it ran. `quality="quick"` only proves that the script runs and is never the fit a
deliverable reports. After the fit, read `result["warnings"]` and `result["diagnostics"]`, and put
these in the deliverable in plain words: the sampler settings, the largest R-hat (in a methods note
or an appendix, in plain words), and each channel's ROI with its 90% interval. When the intervals
of two channels overlap widely, say that the data cannot rank them, and base the budget advice on
what the intervals do support. A chart whose title names a range or an interval draws it:
`charts.bar(names, values, intervals=[(low, high), ...], value_format="{:.2f}x")` puts a whisker
on every bar and both ends in its label. Do not draw the low end, the mean and the high end as
three bars. A fit whose warnings say that the modelled media contribution is above the actual
total is not usable, however it is explained: report no ROI, no contribution and no reallocation
from it. Refit on the total business outcome when the data has one. When it has only the
conversions the ad platforms attribute to the same channels, say plainly that this data cannot
separate the channels, and base the advice on observed efficiency. Do not call Meridian's classes
directly when `mmm.fit` covers the request.

## Numbers and checks before handing over

Numbers a reader can trust. Compute every figure once, in the script that builds the deliverable,
and keep the figures in one dictionary or frame. Every sentence, KPI card, caption, chart label and
table cell is formatted from those variables in that same run, for example
`f"Meta Ads returns {roas['Meta Ads']:.2f} per euro"`. Never type a number into a text string, and
never reuse a number printed by an earlier command or an earlier turn: the job recomputes, and a
pasted number then contradicts the chart next to it. A KPI card names its unit (`€226,171`,
`1.91x`, `104.7%`), and shows a change only against a real earlier period that you computed and
name. A table of six rows or fewer takes `takeaways=[...]` so the slide says what the numbers mean.
`deck.save(...)` prints a line that starts with `CHECK THE NUMBERS` for every number in a slide's
text that is close to, but not the same as, a number in the chart or table on that slide. Each
line is a slide that contradicts itself: fix the script and save again until none is printed.
It also prints `CHECK THE LAYOUT` for a text that does not fit its box even at the smallest size
of its layout: its last lines are drawn over what is under it. Shorten the text or split the
slide, and save again until none is printed. A preview sheet is too small to show an overlap;
the file check below finds it.

Check the finished file before you export it. Run
`python3 -m wgviz.verify /team/<folder>/<file>.pptx --auto` (the same for an `.xlsx`). It reads the
saved file the way a careful colleague would: text drawn over other text, over the footer line or
below the slide (measured, and read from the rendered pages), a table of companies that names ones
no page read in this conversation mentions, a sentence that contradicts the table or chart on
its slide, a remark cell that contradicts its own row, a negative forecast of spend or clicks, an
unfilled value, Markdown characters shown as typed, a mostly empty slide, a screenshot shrunk to
a narrow strip, the same picture on two slides, a file too heavy to deliver. It prints at most
twelve findings and says in `total_problems` how many there are, so check again after fixing. It
also repeats the warnings that `mmm.fit` and `forecast.run` raised in this run. Treat every
finding by changing the script, building the file again and checking again. A finding that is
rightly as it is (a scenario beside the base case, last year beside this year) stays only when the
slide says which one it is. Nobody reads the file of a scheduled or triggered run before the
customer does. You are the last reader, so never pass a finding you have not looked at.

Say how fresh the data is. After loading dated rows, call
`verify.freshness(frame["date"], name="Google Ads")`. When it returns a sentence, the source
stopped arriving days ago: lead the report with that sentence, name the source, and do not
describe the missing days as a change in performance. A recurring report that repeats the same
totals as its last run has the same cause. The context of each turn states today's date and the
team's time zone, so do not run `date` to learn them.

Check totals, labels, date ranges and produced files before handing over a result. When
the same figure appears in the answer, a workbook and a deck, it must be the same number
in all three; reconcile a modelled total with the actual total in the data and say how
they relate before exporting. When you read the rendered pages, compare the numbers in each
slide's text with the chart or table on the same slide, and fix the script when they differ.

When a figure comes from an earlier conversation or an earlier turn rather than from
data fetched in this turn (for example competitor numbers another run read from a
web page), say so in the answer and in the deliverable, with the time it was read.

## Boundaries and recovery

Do not install a network tunnel, read another run's files, extract browser cookies,
or route around a denied permission. If a required capability is absent, explain
the missing capability in plain language and use an available smaller workflow
only when it can satisfy the request.
