---
name: whatagraph-tab-layout
type: workflow
group: report_building
description: Decide what goes on a report page and how it reads. Load before you build or lay out a full tab, build a whole report from an open or partly specified request ("create a report for X", a list of tabs to fill), or replicate a reference report (PDF, screenshot, existing report). Covers the report's tab structure, choosing a visualization for each metric, titles, section headers, narrative openers and takeaways, the full-tab composition bar (dashboard and editorial pages), replicating a reference, layout examples, and the layout checks before handover. Load `whatagraph-widgets` first; this playbook carries no payload shapes.
required_tools:
  - list-sources
  - manage-widgets
optional_tools:
  - tool_name: manage-report-tabs
    purpose: Add the themed tabs a report needs.
  - tool_name: list-widgets
    purpose: Export a widget's rows to put real numbers into narrative text.
  - tool_name: export-report
    purpose: Check that every widget loads data and the page renders cleanly.
  - tool_name: preview-report
    purpose: Look at the rendered page to check text fit and table rows.
  - tool_name: manage-assets
    purpose: Import a hero or cover image before binding it to an Image widget.
---

# Tab layout

This playbook decides **what** to build and **how the page reads**. It assumes `whatagraph-widgets` is loaded: that playbook has the payload shapes, the binding rules, and the grid rules (6 columns, `width` 1..6, no overlaps, comment boxes that clip). They are not repeated here.

> **The quality bar.** Unless the user gave a widget-by-widget spec or a reference to replicate, a generic ask ("create a report for X") means a **multi-tab report that tells a story, where every tab is a full composed page**. A page opens with narrative framing, develops one clear question with substantial, varied widgets, and leaves no dead grid. Two page shapes clear the bar, and a report may mix them: a **dashboard tab** (two or more header-led sections, typically 8–14 widgets) and an **editorial tab** (a chapter in a story: styled opener, 3–8 *larger* widgets that argue one point, a closing takeaway). What never clears it: one or two token widgets adrift in an empty grid, a strip of small KPIs plus a lone chart, a page with no narrative framing, every tab shaped the same. The bar applies even when the tabs and their themes were named for you. **If your run has a limited step budget, save calls on discovery and verification (bind `rows` at create, reuse the field catalog across widgets, batch, verify once at the end), never on the composition.**

## Use this when

- Building a report from an open request ("create a report", "visualise this source", "build me a dashboard").
- Filling tabs that someone named for you, by prompt or by agent instructions.
- Building or laying out one full tab.
- Replicating the layout of a reference report, PDF or screenshot.

## First, decide what the request fixes

There is **no house layout and no default report structure**. The shape is decided fresh each time, in this order:

1. **A reference was provided** (a PDF, screenshot, live-report URL, or an existing report) → **replicate its structure** (see "Replicating a reference report"). Do not normalize it to a layout you prefer.
2. **A widget-by-widget spec** (which widget types, which metrics on each, where they sit) → build exactly that. **What they named is a contract.** Every named metric, tab and widget appears. Map the user's wording to the source's fields with `list-sources action=list_dimensions_and_metrics` (match by meaning, e.g. "cost" → the source's spend metric). Add nothing they did not ask for, keep their naming and order, and never collapse a detailed spec into something smaller. If a requested metric does not exist on the source, do not substitute silently: build the rest and tell the user what is missing and the closest available field.
3. **A partly specified request** → the named parts are contracts, and everything unspecified gets the full open-ended bar. This covers "aggregate Q2 data into a detailed report", "a report focused on conversions", a request that names metrics but not widgets or placement, and a tab list with per-tab themes.
   - ⚠️ **A tab list is not a widget spec.** Instructions such as *"Construct the report with these 6 tabs: 1. General Overview (cross-channel KPIs)… 2. Google Ads: performance widgets for spend, clicks, impressions, conversions…"* fix the tab set, the tab names, their order and each tab's focus, and nothing else. Every named tab is still a full composed page. Reading a tab list as "one widget per named metric" or "a couple of widgets per tab" ships six near-empty pages.
   - Named tabs but no widgets → build exactly their tabs, names and order kept, and compose **each one as a full page**. The tab's theme and named metrics scope *what* goes on the page, never *how little*.
   - Named metrics but no layout → bind those metrics and add the supporting composition around them (headers, trend, breakdown, detail).
   - One tab asked for → respect that, and still fill it.
4. **An open request with no tab, widget or metric detail** → *you* decide what is worth showing. Look at the data that is actually available, pick the most meaningful KPIs, choose the best visualization for each, and arrange them by analytical priority. Do not ship a single tab of generic KPIs. Different sources and metrics should produce different reports; if every report you build looks the same, you have defaulted to a template.

A short prompt never licenses a thin report. Sizing and placement only make *whatever you chose* render cleanly; they are not a recipe for what to build.

## The report's tab structure (open and partly specified requests)

- **Let the data set the tab count. For a metric-rich source, three tabs is the floor.** Inspect the fields first (`list-sources action=list_dimensions_and_metrics`), list the analytical themes the source supports, and give **each substantial theme its own tab**. A metric-rich source (GA4, Search Console, any mainstream ad platform: dozens of metrics across cost, conversions, devices, audience, geography, creatives, search terms) gets **at least 3 tabs, often 4–5**. A narrow source (a handful of metrics, one or two dimensions) may sustain only 2. A multi-source or blended request sustains more (a cross-channel overview plus one tab per channel). If you build 2 tabs for every source, you have stopped reading the data.
- **Read the prompt for scale.** "Client deliverable", "monthly report", "full performance report", "dashboard for the team" mean the fuller end. Only a deliberately small ask ("quick overview", "one-pager", "just the KPIs") caps the report at the lean end; then respect that cap.
- **Themes follow the data.** Examples only, never a template: overview / traffic, conversions / outcomes, spend / efficiency, audience / geography, creative / content, campaign deep-dive. No cost data means no spend tab; no creative dimension means no creative tab. When the data supports a theme, give it its own tab rather than putting two themes on one page.
- **Every tab is a full page.** If a theme cannot fill a page from the available fields, merge it into a related tab instead of shipping a thin one. When the tab list was an explicit instruction, build the fullest page the data supports and tell the user which tab is data-constrained and why.
- **Order tabs like a story, and name them for the reader.** A headline or hook first (the overview: what happened and why it matters), evidence chapters next (one question each), the most granular detail late (long per-entity tables), and, when the report argues a point, a closing "what it means" tab with the conclusion and next moves. Tab names are short labels ("Overview", "Conversions", "Audience"), not sentences. An editorial report may number them as chapters ("01 · The headline", "02 · Where the budget went", …, "06 · What it means").
- An "Overview" *tab* is unrelated to the standalone **Overview / Measurement** entity. When a prompt says "overview" outside a clear report-tab context, ask which one is meant (see `whatagraph-mcp-overview` and `whatagraph-overviews`).
- The first tab is created with the report: name it with `tab_name` at create. Add the other tabs with `manage-report-tabs action=create`.
- **The same bar for every data layer.** A single channel, GA4, a blend or source group, a Google Sheets source, or offline widgets with hand-entered figures all get the same story-shaped, full-page treatment. Offline and spreadsheet reports bind their exhibits through `rows[].data` or the sheet's columns; the composition, narrative and title rules do not change (for the offline build order, load `whatagraph-offline-reports`).
- **Build the container, the tabs and the widgets in one continuous flow.** A report is not created until its tabs hold widgets and those widgets have verified data. Never hand back an empty shell.

## Choosing a visualization for each metric and dimension

Match each piece of data to the visualization that fits its shape:

- **A headline total, the most important number** → SingleValue KPI (Gauge for a dial; Goal when there is a target to pace against).
- **A metric over time** → Line or Area chart with the date dimension.
- **A share of a whole by category** → Donut or Pie (breakdown).
- **One metric compared across categories** → Bar or Column chart.
- **A multi-metric breakdown by a dimension (rankings, "top X")** → Table, the workhorse when a dimension has many values and several metrics matter.
- **Sequential steps, a conversion path** → Funnel.
- **A geographic dimension** → GeoMap.
- **Ad creatives** → Media when the creatives are the point, or a Table with the channel's creative dimension when several metrics per creative matter (`whatagraph-widget-advanced` → "Ad creative thumbnails in a table").
- **Narration or context** → a Comment (an AI-text comment for an automatic summary), only when it adds value.
- **A cover, hero banner or visual divider** → an Image widget (`34`), full width `6×2`, imported through `manage-assets` first. Use it sparingly: one hero on the first tab, not a banner on every page.

**Let dimension cardinality narrow the choice:**

- **Few categories (about 2–7)** → pie or donut as a share of the whole; bar or column also reads cleanly.
- **Many categories (dozens or more)** → a pie becomes illegible and a bar chart runs off the axis. Use a **table** sorted by the primary metric, or a bar or column chart limited to the top N (`whatagraph-widgets` → "Surfacing a top / bottom N"). Never bind a high-cardinality dimension to a pie or donut.
- **Continuous over time** → line or area with the date dimension, however many dates.

Canonical mappings: gender split → pie or donut, never a table; device category → donut; channel grouping mix → donut; age brackets → column chart; campaign, landing-page or search-term detail → table sorted desc by the primary metric; staged conversion path → funnel; country or region → GeoMap; ad creatives → Media with the thumbnail dimension, or a table with that dimension when the ask is metric-heavy or ranked. When unsure of a dimension's cardinality, check it first: a breakdown that looks fine on sample data can overflow on the real account.

**Compose by analytical priority:** the few numbers that matter most first, then the main trend, then breakdowns and detail. The selection, mix and count of widgets follow what the data supports, so they vary from report to report.

**Pick metrics for meaning, not availability.** Outcomes and efficiency (conversions, revenue, cost per conversion, ROAS) tell the reader what they got; impressions and clicks only tell them what happened on the way. A strong headline row reads like a sentence: *what went in → what came out → what it cost per result* (spend → conversions → cost per conversion). Volume metrics still belong in the report, paired with the rate that gives them meaning (impressions with CTR, clicks with conversion rate), usually in the trend and breakdown sections. Each tab answers its own question: a conversions tab leads with conversion outcomes, an audience tab with audience splits, not the overview's spend cards again. If the user named the metrics, bind exactly those.

**Show a variety of widget types** when you choose the layout yourself: a row of KPI cards for the headline numbers, one or more charts (a trend plus a breakdown bar, column or donut), a detail table, and media or funnel widgets where the data supports them. If the user specified the widget types, follow their choice.

## Titles: every widget and every metric row is labelled

Never ship an untitled widget or an unlabelled series. A reader scanning the report should know what each widget shows without opening its config.

- Set the widget title with `name` on create, and make sure `hide_title` does not suppress it.
- Label every metric row through the config metric `name`, including each series of a multi-row chart, each funnel stage and each slice of a non-breakdown pie (`whatagraph-widgets` → "Renaming a metric caption" has the only field that works).
- Utility widgets (Comment, Image, Calendar) are exempt from the metric-row rule. Comment, Calendar, Filter control and Report shortcut render no title at all; a Comment's heading lives in its HTML body.
- The title states what is shown (metric + scope), and the bound fields must deliver it (see "Fit for purpose").
- **On editorial tabs, let titles carry the argument.** Use the pattern `Claim or metric — what it means / how it's defined`: "Commits per engineer per month — the only comparable measure", "Bus factor — engineers needed to cover half of all commits", "Adoption is not evenly spread — share of each engineer's commits that are agent-signed". Keep plain descriptive titles ("Sessions by channel") on dashboard tabs, where the reader scans. Never title a widget with a claim its data does not show.

## Section headers

A tab with more than one group of content (a KPI block, then a trend section, then a detail section) **introduces each group with a section header**: a full-width Comment widget (`21`, `channel_id=7`) carrying a short heading, like an `<h2>` in a document.

- **Shape:** `width: 6`, `height: 1` for a bare heading, placed as the first row of its section. A heading plus even one line of subtitle needs `height: 2`.
- **Text:** an HTML heading such as `<h2>Campaign performance</h2>` that names the section's theme without repeating the widget titles below. A few words. One `<p>` of context may sit under it, at `height: 2`.
- **When:** whenever a tab has two or more sections, which a full self-directed tab always has. The tab's first header can also serve as the page title.
- **When not:** a tab that is genuinely one section (a single full-page table the user asked for, a lean one-pager). Never stack two headers with nothing between them.
- **A header holds only its heading.** Intro text, narrative or an AI summary is a separate Comment sized for its text (`height: 2` for 1–2 sentences, `3` per paragraph, `4+` for a multi-paragraph AI block), and body copy is `<p>`, never a heading. Never append body text to a `6×1` header.

## Narrative comments: openers and takeaways

Where a header labels a dashboard section, an **editorial tab** opens and closes with a *narrative comment*: one Comment widget whose typography frames the page. Three levels, in HTML:

1. **Kicker**: one short ALL-CAPS line, small, bold and muted gray (such as `#7c8794`), e.g. `ENGINEERING PERFORMANCE · Q3 2026` or `THE CASE, IN ONE PARAGRAPH`.
2. **Headline**: one bold, large line (28–32px, or `<h2>`) that states the page's **claim in plain words**: "The team got smaller. The output went up." Never a label like "Overview".
3. **Body**: one or two paragraphs at 14–15px with the evidence in prose and real numbers ("per-engineer throughput went from 19.9 to 49.0 commits a month"). An optional final small muted line can carry sources or method.

Comment typography adds **no space between a heading and the text under it** (`p.p4` has no bottom margin, `h2` almost none, `<hr>` is unstyled), so a heading stacked on body text renders cramped. Build openers with explicit spacing:

```html
<p class="p3"><strong><span style="color: #7c8794">EYEBROW · CLIENT</span></strong></p>
<h2>The chapter's claim in one line</h2>
<p class="p3"><br></p>
<p class="p3">One or two sentences of scope, with real numbers.</p>
```

- Put the kicker in `p3`, which has a bottom margin, not `p4`, which has none.
- The empty `<p class="p3"><br></p>` between headline and body is the only reliable spacer.
- **Do not put `<hr>` between the headline and the body.** If you want a rule, put an empty paragraph on both sides of it.
- **Size:** `6×2` for kicker + headline + a sentence or two; `6×3`–`6×4` when the body runs to full paragraphs. Keep the copy within the box (the comment sizing rules in `whatagraph-widgets`); if it outgrows the height, trim it or grow the widget before writing. Never leave a dead grid row at the bottom of a comment.
- **Write the numbers in.** Real figures read as insight; "performance was strong this period" reads as padding. Pull figures from the widgets you built (`list-widgets action=csv_export`), or skip the claim.
- **Colours:** the muted kicker is safe on light themes. For the headline and body, set the size only and let the colour inherit from the theme; a hard-coded near-black breaks on dark themes. Hard-code colours only when you know the theme.
- **Takeaways close the loop.** A tab that argues something ends with a `6×2`+ narrative comment saying what the evidence means (kicker + body; no big headline needed). It is its own widget, on the last row, not text added to a header or another comment.

## Fit for purpose: fields must match the intent and each other

- **Fit the purpose.** "Spend by campaign" binds a cost metric and a campaign dimension, not impressions and date. "Conversion rate over time" binds a rate metric and the date dimension. Read the intent (prompt or title), then pick the fields that answer it.
- **Metric and dimension compatibility.** Bind only dimensions the metric can be broken down by. Look them up with `list-sources action=list_dimensions_and_metrics`; availability depends on the integration and the report type.
- **`report_type` compatibility.** Every field in a config belongs to the same `report_type`, or the widget errors with "Unavailable report type" or renders blank.
- **Widget-type compatibility.** Respect the dimension requirements in `whatagraph-widgets` (a time series needs the date dimension, a heatmap two dimensions, a SingleValue none, a GeoMap a geographic one).
- **Verify** with `export-report` or `list-widgets action=csv_export` that the widget returns what its title promises. `list-widgets action=show` echoes ids, not loaded data.

## Composing a full tab (self-directed builds)

When you decide the layout yourself (no reference, no widget list), each tab is a **complete page with a visual rhythm**. This applies just as fully when the tabs were named for you: a named tab scopes the page's *subject*, and the page is still yours to compose. Failures to design against: one or two widgets adrift in an empty grid; a row of identical KPI cards plus one chart; a single table floating in empty space; every tab shaped the same.

**Pick the tab's mode first**, per tab, by what the page is for:

- **Dashboard mode**: a working surface the reader scans for numbers (operations, campaign monitor, per-channel performance). Multiple header-led sections, a dense varied mix, typically 8–14 widgets.
- **Editorial mode**: a *chapter in an argument* (executive summary, monthly story, an analysis that builds to a conclusion). 3–8 **larger** widgets, each a deliberate exhibit, wrapped in a narrative opener and a closing takeaway. Editorial tabs earn their lower count by making every widget substantial (`3×4`, `6×4`, paired `3×6` tables, not token `2×2` cards) and by filling the page vertically just as fully.

A deliverable someone will *read* (client story, executive briefing, year in review, an analysis of what happened) defaults to editorial; a surface someone will *monitor* defaults to dashboard. Plan the tab as a sequence of moments before you place anything. Fall back to a single lean section only when the user asked for a one-pager.

**Anatomy of a dashboard tab** (an ordering principle, not a fixed list):

1. **Section 1 header** (Comment `6×1`).
2. **Headline row**: 2–3 KPI cards, `2×2` three across (`whatagraph-widgets` → "KPI card geometry"). Vary the form across tabs: a Gauge or Goal where there is a target, a List where several small numbers belong together.
3. **Main visual row**: the centrepiece, usually a wide trend or comparison chart, paired rather than alone: a `4×3` chart beside a `2×3` list, donut or KPI, or two `3×3` charts.
4. **Section 2 header**, then **breakdown and detail rows**: a full-width table, or a table beside the donut or bar that summarizes it; a GeoMap for geography; Media tiles for creatives; a Funnel for staged conversions.
5. **Section 3 where the data supports it**: another header plus secondary breakdowns, a narration Comment, or an AI-summary block. Most metric-rich sources support a third section on some tabs; reach for it rather than stopping at two.

**Anatomy of an editorial tab** (also a principle, not a template):

1. **A narrative opener** (Comment `6×2`) that states the chapter's claim (see "Narrative comments"). On the report's first tab an Image hero banner (`6×2`) may sit above it as a cover.
2. **The evidence**: 3–8 substantial widgets that develop exactly the opener's claim, in whatever geometry it needs: a strip of six narrow `1×2` KPIs; a `6×4` full-width chart whose title carries the argument; two `3×6` tables side by side comparing cohorts; a `2×2` grid of four `3×4` charts; a `6×5` table. Vary the geometry from chapter to chapter.
3. **A closing takeaway** (Comment `6×2`–`6×4`): what the evidence on this page means, plus caveats or a pointer to the next chapter. The final tab often closes the whole argument in one block ("The case, in one paragraph"). An AI-text comment can serve when hand-written insight is not available.

**Composition rules:**

- **Pair, don't strand.** No widget sits alone on a row unless it is genuinely full width (a `6`-wide table, trend chart or header). A small widget with 4 empty columns beside it is a layout bug: widen it, pair it, or move it.
- **Adjacency is meaning.** Widgets that answer the same question sit together: the KPI and the trend that explains it, the donut and the table that details it, the map and the top-regions list. A reader should be able to say what each *row* is about.
- **Vary the forms, within the tab and across tabs.** A tab of only KPI cards and one chart type looks machine-generated. The spend, audience and creative tabs should each look like what they are about.
- **The page is full.** Content develops down the grid (typically 8–14 grid rows) with no dead space, and every widget earns its place. A dashboard tab lands around 8–14 widgets in two or more sections; an editorial tab around 3–8 larger widgets wrapped in narrative. Never pad with near-duplicates to reach a count, and never stop at a half-empty page.
- **Give every KPI card its own icon**, picked for its metric (`whatagraph-widgets` → "Row icons"). A row of identical eye icons is the signature of icons left unset.
- **End flush.** The last row fills its width like every other row. If the tab ends with a `2`-wide orphan, rebalance the final rows.
- **Too thin to fill?** Do not pad; merge the theme into a related tab (see "The report's tab structure").

## Replicating a reference report (the priority when one is given)

- **Recreate every element** in the same top-to-bottom order: KPIs, charts, tables, funnels, creative tiles (Media `110` / `111`), comments. Do not drop or invent widgets.
- **Match per-row counts and proportions.** 3 across ⇒ `width 2` each; 2 across ⇒ `3` each; one full-width ⇒ `6`; an uneven pair (wide chart + narrow KPI) ⇒ e.g. `4 + 2`.
- **Match the widget type to what is shown.** A donut stays a donut, a funnel stays a funnel.
- **Preserve spacing and density.** Same sequence, and leave an empty row where the reference shows a gap. Do not tighten a deliberately sparse page or pad a dense one.
- **Ignore account and source names** printed on the reference ("Account: …"); that is metadata, not a filter.

## Examples: illustrations of range, not templates

**Copy the user's intent or reference, never these.** They exist to show that the structure should vary:

- **Dense paid-media page (dashboard, two sections):** header `x0 y0 6×1`; three KPIs `x0/x2/x4 y1 2×2`; donut `x0 y3 3×3` + table `x3 y3 3×3`; header `x0 y6 6×1`; detail table `x0 y7 6×3`; three creative tiles `x0/x2/x4 y10 2×3`.
- **Editorial headline chapter (opening tab):** hero Image `6×2` at `y0`; narrative opener `6×2` at `y2`; six narrow KPIs `1×2` at `y4`; an at-a-glance table `6×4` at `y6`; closing takeaway `6×2` at `y10`. Five rows, a full page, ten widgets.
- **Editorial comparison chapter:** opener `6×2`; two tall tables `3×6` side by side comparing periods, segments or regions. Three widgets; the pairing is the argument.
- **Editorial evidence chapter:** opener `6×2`; a `6×4` chart whose title carries the finding; a `2×2` grid of four `3×4` supporting charts or tables; takeaway `6×2`.
- **Lean summary:** three KPIs `2×2`, then one full-width trend `6×3`. Only when the user *asked* for a lean one-pager; an open "create a report" gets a full composition.
- **Exec narrative (text-led):** an AI-summary comment `6×3`, then two visuals `3×3 + 3×3`.
- **Uneven split:** a wide trend `4×3` beside a tall KPI list `2×3`.

If your output looks like the same example every time, go back to the user's request or reference.

## Layout checks before handover

Walk these on every built tab, then run the report handover checks in `whatagraph-reports` ("Before handing a report over"):

1. **Every tab is a full page**: a dashboard tab (headed sections, varied mix) or an editorial tab (opener, substantial widgets, takeaway). No tab with one or two token widgets, no half-empty grid below the last row, and the tabs read as a story front to back.
2. **Every binding is compatible**: fields checked against `list-sources action=list_dimensions_and_metrics`, one `report_type` per config, dimension requirements per widget type respected.
3. **The layout is clean and text fits its box**: rows fill their width, no gaps or overlaps, no stranded widget; every comment's copy is within its height budget. Overflow gives no API signal, so count the text and check the render with `preview-report` or `export-report`.
4. **Everything is titled and iconed**: report, tabs, widgets, metric rows; dashboard sections have header comments, editorial tabs their opener and takeaway; every SingleValue and List KPI row has an icon matched to its metric.

A tab failing any of these is not finished.
