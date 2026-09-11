---
name: whatagraph-canvases
type: domain
description: Build designs — freeform documents where a slide deck, a printable client report and a continuous dashboard are one type in three formats. Blocks are positioned on the page and named by theme role, never by colour. Use when someone wants a deck, a presentation, a designed or printable report, a one-pager, or a dashboard view, rather than a grid report. Also covers design systems (brands) — the six decisions a design is drawn in.
required_tools:
  - list-canvases
  - manage-canvases
  - list-design-systems
  - fetch-data
optional_tools:
  - tool_name: list-sources
    purpose: Find the sources to fetch the numbers from before authoring, and the ids attach_sources takes.
  - tool_name: list-spaces
    purpose: Pick the space (client) the design belongs in.
  - tool_name: manage-design-systems
    purpose: Generate or create the brand the design is drawn in.
  - tool_name: delete-canvases
    purpose: Remove a design, or one page of one.
  - tool_name: manage-widgets
    purpose: Create and edit a widget the design owns, for the widget types no block draws.
  - tool_name: list-widgets
    purpose: Read the widgets a design owns, or find a report's widget to bind a block to.
---

# Designs

Tools covered: `list-canvases`, `manage-canvases`, `delete-canvases`, `list-design-systems`, `manage-design-systems`.

A **design** is a document made of pages, and each page is a `layout` plus positioned `blocks`.
A slide deck, a printable A4 client report and a continuous dashboard are the **same document
type in three formats**. They differ in exactly three things: the shape of the page, whether
page boundaries are shown, and the brand the block roles resolve to. Everything else — the
blocks, the composition rules, this playbook — is shared.

A design is **not a report**. A report is a grid of widgets on a layout the product decides. A
design is blocks you place, on a page you compose. Either can hold live numbers — a design's
blocks can be **bound** to a widget or a query and re-fetch every time somebody opens it — so
"does it stay current" is no longer the question that chooses between them. The question is
whether the output is a composed page. If the user wants the familiar report grid, they want
`whatagraph-reports`.

## Use this when

- "Build me a deck for Thursday's client review."
- "Turn last month's performance into a report I can send as a PDF."
- "Make a one-page summary of the quarter."
- "Fix page 4 — the headline is wrong."

## Choose the format first

| They said | Format | Why |
|---|---|---|
| deck, slides, presentation, "I'm presenting this" | `slide_16_9` | Projected, read across a room |
| client report, monthly report, PDF, "send it to them", print | `a4_portrait` | Read in the hand at arm's length |
| wide report, landscape, a printed spread | `a4_landscape` | The same paper, turned |
| dashboard, overview, "at a glance", a scrolling page | `dashboard` | Scanned at a desk, no bottom |

Ask when it is genuinely ambiguous; otherwise pick and say which you picked. Getting it wrong is
not fatal — but the format cannot be changed afterwards, because every frame was composed
against one page shape. A different format means authoring the pages again.

## The workflow

1. **Read the registry.** `list-canvases` `action=formats`. Page geometry, block budgets and the
   bands the chrome occupies are server-owned and change without a release. Never author from
   remembered numbers.
2. **Pick the brand.** `list-design-systems` `action=list`. Use the team's default unless the
   user asks for something else. A design with no brand is drawn in the default one — never
   unstyled — so this step is optional, not skippable-with-consequences.
3. **Fetch the data.** `list-sources`, then `fetch-data`. Do this *before* authoring: a design
   holds the numbers you write into it, and you cannot query from inside a page.
4. **Decide the story, then the design direction.** See *Choose a design direction* below.
5. **Author it in one call.** `manage-canvases` `action=create` with `pages`.
6. **Read it back.** `list-canvases` `action=show`, and `show_page` on anything you are unsure
   of. Then fix what is wrong with `patch_blocks`.
7. **Check it draws.** `list-canvases` `action=validate`. See *Checking a design still draws*
   below — this is the step that catches a page nobody wrote breaking.
8. **Look at it.** `preview_canvas`, if you have it. See *Looking at a page* below. A validator
   tells you a heading does not fit; only the picture tells you the page is ugly.

## Creating a design

```
manage-canvases action=create space_id=<id> name="Q3 client review" format=slide_16_9
                design_system_id=<id> pages=[ ...page objects... ]
```

`pages` is optional on `create` — without it you get one empty page — but passing it is the
normal way to build a design, and it is one call instead of two.

A page object:

```json
{
  "layout": "content",
  "kicker": "TRAFFIC",
  "source": "Google Analytics 4 · Last 90 days",
  "title": "Sessions climbed every month",
  "notes": "Speaker notes. Never drawn on the page.",
  "blocks": [
    { "id": "trend-heading", "type": "text",
      "frame": {"x": 0.06, "y": 0.0816, "w": 0.58, "h": 0.09},
      "text": {"role": "heading", "content": "Sessions climbed every month of the quarter"} },
    { "id": "trend-chart", "type": "chart",
      "frame": {"x": 0.06, "y": 0.2025, "w": 0.54, "h": 0.2588},
      "chart": {"chart_type": "line", "categories": ["Jul", "Aug", "Sep"],
                "series": [{"name": "Sessions", "values": [9840, 11200, 12400]}]} },
    { "id": "trend-takeaway", "type": "text",
      "frame": {"x": 0.65, "y": 0.2025, "w": 0.29, "h": 0.09},
      "text": {"role": "body",
               "content": "Organic search added most of the lift, and paid search finally turned profitable."} }
  ]
}
```

Every block carries an **`id`**, unique within the page. It is how you address that block later
with `patch_blocks`, so make them mean something: `hero-metric`, `trend-chart`, `cta`.

## Frames — the one thing worth getting exactly right

**All four frame values are fractions of the page's WIDTH**, origin top-left. Not of the height,
and not of the area.

That means `y` and `h` do **not** run 0 to 1. They run 0 to the format's `page_height`, which is
in the same unit:

| Format | `page_height` — how far down the page goes |
|---|---|
| `slide_16_9` | 0.5625 |
| `a4_landscape` | 0.7071 |
| `a4_portrait` | 1.4143 |
| `dashboard` | whatever the page declares, and it grows |

A block is on the page when `x + w ≤ 1` and `y + h ≤ page_height`. A block at `y: 0.8` is off the
bottom of a slide and halfway down an A4 page.

Why this unit: a continuous page can grow, and if `y` were a fraction of height then making a
dashboard taller would move every block already on it. In width units, growing a page changes
one number and moves nothing.

### Sizing a text frame

Nothing reflows. Text that needs more room than its `h` gives it is drawn *over* the blocks above
and below — which is how a heading ends up running through its own subtitle. Text that overruns
slightly is shrunk to fit; text that overruns badly is rejected, so give the frame the room
instead.

Count the lines before you choose `h`. For the default brand:

| Role | One line, in width units | Characters per line at `w: 1.0` |
|---|---|---|
| `heading` | 0.041 | 55 |
| `quote` | 0.034 | 85 |
| `subheading` | 0.028 | 105 |
| `body` | 0.023 | 142 |
| `caption` | 0.018 | 178 |
| `kicker` | 0.015 | 140 |

Read it like this: **characters per line = (the number above) × `w` ÷ `scale`**, and **one line
of height = (the number above) × `scale`**.

So a heading at `scale: 1.8` in a frame `w: 0.84` fits about `55 × 0.84 ÷ 1.8 ≈ 25` characters
per line, and each line is `0.041 × 1.8 ≈ 0.073` tall. A two-line heading there needs
`h: 0.15`.

The table holds for `slide_16_9`, `a4_portrait` and `dashboard` — that is not a coincidence, it
is the type scale being tuned to reading distance rather than to page size. On `a4_landscape`
the sheet is wider, so **multiply the characters by 1.41 and divide the line height by 1.41**.

**Two exceptions, and they are the ones that catch people.** Every format has a legibility floor,
and on both A4 formats it sits *above* what `caption` and `kicker` scale to — so they draw larger
than the table says, need more room than you asked for, and get clipped. Use these instead:

| Role | `a4_portrait` line / chars | `a4_landscape` line / chars |
|---|---|---|
| `caption` | 0.022 / 145 | 0.015 / 205 |
| `kicker` | 0.018 / 113 | 0.013 / 160 |

If the design's brand sets its own type scale, `list-canvases` `action=show` returns it as
`type_scale` and `format_preset.min_type_size`. Recompute from the size the page will actually
draw, which is `max(min_type_size, size × type_scale_ratio × scale)`: the line height is
`that × line_height ÷ design_width`, and the characters per line at `w: 1.0` are
`design_width ÷ (0.45 × that)` — `0.50` for a bold role. **Taking the floor into account is the
whole of it**; leaving it out is what clips a caption.

### How tall is everything else

Text is the block whose height you have to compute. The rest divide into two kinds, and knowing
which is the difference between a tidy page and a page with a hole in it:

- **A `chart`, a `bar_list`, an `image` and a `card` fill the frame you give them.** Make the
  frame the size you want the thing to be.
- **A `table` draws top-aligned at its natural height and does not stretch.** A row — the header
  included — is about **0.032 of the page width**, or **0.039 on `a4_portrait`**, where the
  legibility floor lifts the type. So a six-row table plus its header is `h: 0.22` on a slide or
  a dashboard and `h: 0.27` on A4. Give it more and you get an empty band under it; the
  validator will not complain, because nothing is broken — it just looks unfinished.

  **Round that number up, by about a tenth.** It is the height the rows need and not the height
  they should have: sized to it exactly, the last row's divider sits hard against the frame's
  edge, and one longer label or one extra row clips again. A three-row table wants `h: 0.11`
  rather than the `0.096` the arithmetic gives. The validator asks whether the content fits, so
  a table sized to the formula passes and still looks cramped — that judgement is yours, not
  the validator's.
- **A `metric` grows to fill its frame**, which is what makes a hero number work. Metrics that
  form a **row** are sized together — they take the smallest size any of them wants — so you do
  not have to match the lengths of `"$1.24M"` and `"$41.20"` by hand. A row is decided from the
  frames: metrics whose frames overlap vertically by more than half of the shorter one, whether
  they sit side by side or each inside its own `card`. What that means for you: **give a KPI band
  equal frames at the same `y`** and it will read as one row. A metric you want at hero size
  belongs at its own `y`, clear of the band, or it will be pulled down to the band's size.

### The rail

Start blocks at the format's `rail` — `0.06` on a slide, `0.0714` on A4 portrait, `0.04` on a
dashboard — and end them at `1 − rail`. It is where the chrome sits, so a heading at `0.08`
above a source line at `0.06` reads as a mistake, because it is one.

## Page chrome: `kicker` and `source`

Two things belong to the page rather than to a block:

- **`kicker`** — the small uppercase label above the heading, naming which part of the story this
  page belongs to. It is what lets the heading state a *finding* instead of a topic: kicker
  `MARKET SIZE`, heading *"One-fifth of world retail is now online"*.
- **`source`** — the credit line along the bottom. Set it on every page carrying numbers.

The document places both, at the same spot on every page. **Do not author them as blocks.**
Getting a kicker onto the same pixel eight times is precisely what free frames fail at, and a
deck where the label drifts a few pixels per page is what "generated" looks like.

They are free — they do not count against the block budget — and **they reserve their bands**.
With a `kicker`, blocks start at the format's `chrome.content_top` or below. With a `source`,
they end by `chrome.content_bottom`. A block inside either band is rejected, and the error names
the number. A continuous format has no bottom to pin a source to, so `dashboard` has no source
band — put the credit in a `caption` block at the end.

## Backgrounds and emphasis

Set `background` on the page: `default`, `dark`, or `accent` (the brand colour). Ink flips
automatically — **never restate a colour**. A page that names its ground and otherwise says
nothing about colour is what makes re-branding a forty-page document touch zero blocks.

Any block may set `"emphasis": true`, which paints it in the brand accent. **At most one per
page.** It is how you say "this is the number that matters". Two say nothing.

## Styling one block

A block may carry a `style` object overriding what the brand decided for it. **Leave it out
unless you were asked for it.** A design where nothing is styled re-brands completely and a
design where everything is styled re-brands not at all, and the person asking for one blue box
is not asking for the second thing.

```json
{
  "id": "b4", "type": "shape",
  "frame": { "x": 0.06, "y": 0.2, "w": 0.2, "h": 0.1 },
  "shape": { "kind": "rounded_rectangle", "content": "Blocked" },
  "style": { "background": "negative/12", "border_color": "negative", "border_width": 2 }
}
```

### Colours are strings that name something

Each of `background`, `border_color` and `ink` is one string, and four things it can be:

| Write | Means |
|---|---|
| `accent`, `primary`, `secondary`, `muted`, `border`, `card`, `background`, `positive`, `negative` | A role in the brand. Resolves per ground, so it reads on a dark page too |
| `brand.1` … `brand.6` | A slot in the brand's palette — the same colours a chart's series take |
| `transparent` | No paint at all |
| `#1A2B3C` | A literal |

Add `/NN` to any of them for opacity in percent. `accent/12` is a tinted band, `accent` is a
solid one, and the tint is almost always what a ground wants — a full-strength accent behind
text is what makes a page look like a warning.

**Reach for a role or a slot first.** A literal is the only one of the four that a re-brand does
not move, so a design full of literals is a design somebody has to restyle by hand later. Use one
when the colour is the point — a company's own red in a comparison, a traffic light — and not
because you happen to know a nice blue.

### The rest of the fields

- `border_width` — design pixels. `0` draws no edge, which is how you take a shape's outline off.
- `border_style` — `solid`, `dashed` or `dotted`.
- `radius` — corner rounding in design pixels.
- `shadow` — `none`, `soft` or `strong`.
- `opacity` — 0 to 1, over the whole block, its text included.

### What each type does with it

Every type reads the same object, and a few ignore parts of it that make no sense for them.

- A **connector** is a line, so it takes `ink` (and `border_color`, which means the same thing
  here) and `opacity`. It has no ground and no corner.
- A **divider** is its own ground, so `background` is its colour. It has no edge and no depth.
- An **image** has no text, so `ink` does nothing.
- A **shape**'s `background` replaces `tint` and `fill` outright rather than mixing with them.
  Set one or the other, never both.
- A **card**'s `background` replaces the ground it draws, and its children still resolve their
  ink against the card's `tone` — so a dark `tone` with a pale `background` gives you pale text
  on a pale ground. Pick one.

### Where this does not reach yet

**PowerPoint and Google Slides ignore `style` and draw the brand's own answer.** A block you
styled exports as an unstyled one — plainer, never broken. PDF and PNG are rendered by the
browser and are correct. Say so if somebody styles a deck they are about to export to .pptx.

## Layouts

`layout` names the page's archetype. It sets the block budget and tells the reader what kind of
page this is. Which layouts a format offers, and how many blocks each holds, is in
`action=formats` — read it there rather than from here. As a shape:

| Layout | For |
|---|---|
| `title` | The cover. What this is and who it is for |
| `section` | A divider naming the part of the story coming next. Usually a dark ground |
| `content` | The workhorse. A heading and the things that support it |
| `split` | Two columns of unequal weight — a chart and the sentence saying what it means |
| `full_chart` | One visual, edge to edge, with almost nothing around it |
| `quote` | A single statement at display size |
| `closing` | The ask, the next step, the contact line |

A continuous format offers only `content`, `split` and `full_chart` — there is no cover for a
page with no top. Exceeding a budget is rejected; split the content across more pages instead of
shrinking it.

## Block types

- **`text`** — `content` plus a `role`: `kicker`, `heading`, `subheading`, `body`, `caption`,
  `quote`. **`caption` is for credits and footnotes, never for what the page is saying** — it is
  the smallest type in the document. Prose is `body`. The role decides weight, colour and casing.
  Add `scale` (0.6–2.5) to make text louder or quieter than its role's default; that is how a
  "dramatic type" direction is expressed. **Never author a font size.**
  To colour part of a sentence, give **`runs`** instead of `content` — a list of
  `{"text": "...", "ink": "accent", "bold": true}`. This is how a designed page picks out the
  phrase that matters: *"The return held. **The delivery did not.**"* `ink` is one of `accent`,
  `primary`, `secondary`, `muted`, `positive`, `negative` — a theme role, never a value, so it
  stays right on a dark or accent page. Runs join with no separator, so put your own spaces in.
  Give `content` or `runs`, never both.
- **`metric`** — a headline number. `value` and `delta` are **pre-formatted strings you write**
  (`"$142K"`, `"+18%"`), never raw numbers. A `delta` must be paired with `delta_direction`
  (`up`/`down`/`flat`) — which way the number *moved*, which draws the arrow. Add
  `delta_sentiment` (`positive`/`negative`/`neutral`) to say whether that move is *good news*,
  which sets the colour. They are separate on purpose: a CPA falling 12% is `down` **and**
  `positive`. Omit the sentiment and the delta renders neutral rather than guessing.
- **`chart`** — `chart_type`, `categories`, `series`. Every series' `values` must be the same
  length as `categories`. `pie` and `donut` take one series. Types: `bar`, `line`, `area`, `pie`,
  `donut`, `scatter`, `radar`.
- **`table`** — `headers` and `rows`; every row has one cell per header. **Every cell is a string
  you have already formatted** — `"1,842"`, `"$34.02"`, `"—"` — never a raw number, and never an
  object: a cell carries no colour or weight of its own, and a non-string cell is rejected. When a
  figure has to be coloured, it is not a table cell — pull it out into a `metric`, or write the
  sentence with a `run`.
- **`image`** — a public `https` `url`, plus `alt` and `fit` (`cover` crops, `contain`
  letterboxes).
- **`card`** — a surface holding other blocks. Give it `blocks`. **Child frames are fractions of
  the card on both axes**, not of the page, and **every child needs a real frame** — one filling
  its card is `{"x": 0, "y": 0, "w": 1, "h": 1}`. Cards cannot nest.
  **`tone`** (`default`/`dark`/`accent`) makes the card a surface in its own right rather than a
  tint, so ink inside it inverts just as it does on a dark page. Put the text **inside** the
  toned card: a text block merely positioned over one still resolves its ink against the page and
  can come out unreadable.
  **A card with an empty `blocks` list is a band of colour** — that is how you author a split
  background or a colour field behind a title, which a page background cannot do. Set
  `"rounded": false` for a band, author it *before* the blocks that sit on it (blocks draw in
  order), and know it is exempt from the overlap check, because sitting behind things is the
  point.
- **`pill`** — a capsule for a short phrase: a byline, a credit, a status. `content`, or `runs`
  for mixed weight. With no `tone` it is a quiet outline; a `tone` fills it and inverts its text.
  It does not wrap — keep it to a phrase.
- **`divider`** — a rule. `{"accent": true}` is the short brand-coloured mark that belongs under a
  title heading; without it, a hairline separator.
- **`bar_list`** — a handful of labelled bars drawn as design rather than as a chart. Each item is
  `{label, value, ratio, emphasis?}` where `ratio` is 0..1 of the track and `value` is the
  formatted string shown. `horizontal` is a ranked comparison; `vertical` is a short progression.
  Max 6. **Prefer this over a chart for six or fewer figures** — it reads as part of the page
  instead of as a chart dropped onto it.
- **`widget`** — an existing Whatagraph widget, drawn on the page. Its `binding` names the
  `widget_id`; the widget keeps its own configuration and picks up the design's brand. Chrome is
  off by default because the page already has its own text blocks. Give it at least 232 × 110
  design pixels — below that a widget refuses to render.

## Inline or bound

Every data-bearing block — `metric`, `chart`, `table`, `bar_list` — either **carries** its
numbers or **fetches** them.

**Inline** is the default and the right answer for a deck or a printed report: you fetched the
data, you decided what the story was, and the page holds exactly the figures you wrote.

**Bound** is the right answer for a dashboard somebody opens twice a week. Give the block a
`binding` and no payload of its own — the resolver fills it every time the design is opened:

```json
{ "id": "sessions", "type": "metric", "frame": {"x": 0.04, "y": 0.16, "w": 0.2, "h": 0.11},
  "binding": { "kind": "query", "sources": [2], "metrics": ["sessions"], "compare": "previous" } }
```

- `sources` is one **integration source id** from `list-sources`, and `metrics` / `dimensions`
  are `external_id`s copied verbatim from the same tool. Do not guess them — the id families
  differ per channel.
- The **first metric** is what a `metric` or a `bar_list` draws. The **first dimension** becomes a
  chart's categories, a table's first column, a bar list's labels.
- A `metric` draws a delta only when there is a comparison to draw it from — set `compare` on the
  block, the page, or the document.
- A bound `table` or `bar_list` is **cut to what its frame holds**, so give it room for the rows
  you expect rather than assuming everything comes back.
- `kind: "widget"` with a `widget_id` draws a widget instead of a query — either one a report
  already has, or one the design owns. See *Three ways to make a block live* below.

**Dates cascade: document → page → block.** Set `date_range` once on the design and every bound
block follows it; a page or a block overrides it with a period key of its own. `inherit` is the
default on a binding and is almost always what you want — one picker moving a whole document is
the point. A **share link** can pin a period too, standing in for the document's own rung, which
is how a client gets March while the dashboard keeps rolling.

```
manage-canvases action=update canvas_id=12 data_mode=bound date_range=last30Days compare=previous
```

A period is a **calendar key, and it is camelCase**: `last30Days`, `lastMonth`, `thisQuarter`,
`last12Month`. Snake case looks right and is not — an unknown key is refused with the full list,
so read the message rather than guessing again.

`data_mode=bound` is what makes a document live. Leave it `inlined` (the default) for a deck.

### Three ways to make a block live

A `binding` has two kinds, and the `widget` kind covers two different situations, so there are
three answers and they are not interchangeable.

**A `query` binding is the default.** One source, some metrics, resolved on every open. Nothing is
created, nothing has to be cleaned up, and the block is the whole statement of what it shows.
Reach for this first for a dashboard's numbers, charts, tables and bar lists.

One thing it does **not** do: a query binding names a source without **attaching** it to the
design. `sources` on a binding is the global integration source id, so the numbers are live and
correct while the design's channels panel stays empty. Attach the channel yourself when the design
should show which sources it reads:

```
manage-canvases action=attach_sources canvas_id=12 source_ids=[2]
```

Ids are the global ones from `list-sources`, the same family the binding takes. Attaching one that
is already attached changes nothing and says so, so a repeat is safe. `list-canvases action=show`
reports the design's `channels`, each with the document-local `source_id` that `manage-widgets`
takes. Attaching is also the **prerequisite for a widget the design owns** on any real channel:
`manage-widgets action=create design_id=…` attaches whatever source its widget reads, so doing it
first is a choice about what the panel shows rather than a step you can skip.

**A widget the design owns** is for what a block cannot draw. A block draws four shapes — a metric,
a chart, a table, a bar list — and the reporting side has widget types that are none of them, plus
per-widget behaviour a binding has no field for. Create one when the ask needs any of these:

- a funnel, a goal, a geo map, a media widget, or a dynamic chart family (scatter, bubble,
  heatmap, candlestick, combo, top-N)
- conditional formatting or auto colors on a table's column
- currency conversion on a money metric
- values typed by hand rather than fetched, which is what the offline widget types are for
- a source filter, or a date range pinned per widget with a comparison of its own
- a widget the person can go on editing in the drawer afterwards, with the report's own editor

**And create one whenever the person asked for one.** The list above is about what a block cannot
draw, and that is not the only reason to make a widget. "Use a report table", "put the widget on
it", or a widget type named out loud is a decision already taken, and a `table` block handed back
instead is the wrong answer however well it draws. Take the ask literally: `manage-widgets
action=create` with the type they named, `widget_type_id="table"` for the plain table. The one
case you cannot honour is a refused type, and there you name which type it is and what the design
will draw instead, rather than substituting a block silently.

**A report's widget** is for showing something a report already has, where the two should stay the
same. Find the id with `list-widgets action=list report_id=…` and bind to it. Editing it edits the
report's widget, because it is the report's widget.

### Creating a widget the design owns

Two calls, in this order, and both belong in the same turn.

```
manage-widgets action=create design_id=12 page_id=41 channel_id="9" widget_type_id="115"
  rows=[{ "configs": [{ "source_id": 2, "options": { "metrics": [...] } }] }]
→ { "widget": { "id": 8814, ... } }

manage-canvases action=patch_blocks canvas_id=12 page_id=41
  blocks=[{ "id": "funnel", "type": "widget", "frame": {"x":0.06,"y":0.18,"w":0.4,"h":0.3},
            "binding": { "kind": "widget", "widget_id": 8814 } }]
```

The widget is invisible until the block exists — a widget is data and a block is what draws it. A
widget with no block pointing at it is deleted on the design's next page save, which is also the
cleanup if the second call fails: nothing is left behind, and nothing has to be swept.

Removing the block removes the widget, so there is no widget delete to make. `delete-widgets`
refuses a design and says so.

Everything the design's own widget editor can change, `manage-widgets action=update` can change
with `design_id`: sources, metrics, dimensions, filters, row labels, settings, conditional
formats, currency. `list-widgets action=list design_id=12` reads them back by page, and reports the
`blocks` drawing each one — an empty list there is a widget about to be reaped.

Six things a design refuses, most because its own editor offers no equivalent:

| Refused | Why, and what to do instead |
|---|---|
| `position_x`, `position_y`, `auto_place`, `target_tab_id` | A design has no widget grid. The block's `frame` places it. |
| `action=apply_premade` | Premade widgets are a report library. Create the widget with `action=create`. |
| `action=duplicate`, `batch_duplicate` | Copy the block with `patch_blocks`; the widget follows it. |
| `action=update_ai_text` | AI text is a comment widget's setting. A design writes prose in `text` blocks. |
| Comment, calendar, image, filter control, report shortcut types | The design draws these with its own blocks, or has no surface for them. |
| Multi-source table (37) | Deprecated in favour of blends and source groups, so nothing creates one any more, and a design will not draw an existing one either. Use `widget_type_id="table"`, or a `table` block. |

A widget block is also the one block the PowerPoint and Google Slides writers cannot draw as
shapes — see the export table above. If a table or a chart will do, use `table` or `chart`.

**Freeze** keeps a copy of today: `manage-canvases action=freeze canvas_id=12` resolves every
bound block once and stores the result as a static twin. The design itself stays live and keeps
its bindings — freezing is how you make "the report as of March" *without* giving up the
dashboard.

**Sharing and exporting are the person's, not yours.** A design is published from its own header —
a link that opens signed out, with an optional password, an expiry, and switches for download and
date changing — and exported from beside it. There is no tool for either, and that is deliberate:
publishing to a client is a decision. What you can do is make the document worth sharing, which
mostly means the next section.

Four exports, and the difference between them is worth knowing when somebody says which one they
want:

| They ask for | They get | Cost |
|---|---|---|
| a PDF, a PNG | the page itself, drawn headlessly | nothing is lost |
| a PowerPoint file | editable shapes, tables and native charts | a `widget` block becomes a picture |
| a Google Slides deck | the same, with charts that stay editable in Google | 16:9 only, and no `widget` blocks at all |

PDF and PNG cannot disagree with the screen, because they *are* the screen. The two writers redraw
each page from the spec, so they are the ones with a cost — and both costs land on `widget` blocks,
which is worth remembering when you are choosing between a `widget` and a `chart` for something
that will be presented from PowerPoint.

## Composing for the format

The three families are read at different distances, and that is the whole of what makes their
composition rules different. Everything above is shared; this is not.

### Slides — read across a room

Six to ten pages for a review. Twenty is a report nobody will sit through.

- **One idea per page.** If a page needs two headings, it is two pages.
- **Big and few.** Three to five metrics at most; six numbers is a table, and a table on a
  projected slide is unreadable. A hero number gets its own page: a `metric` with no `label` and
  no `delta` grows to fill its frame, so give it room and put almost nothing else there.
- **Dark pages are punctuation.** One for the title, one for a single arresting number, one to
  close. A deck that is all light is flat; a deck that is all dark is exhausting.
- **A chart needs room.** Below about a third of the page in either direction its labels stop
  being readable. Use `full_chart` when a chart matters, and cap categories at around 12.
- **Cards carry the detail.** A number with a sentence explaining it, set in a card, is the unit
  a good deck is built from. Three of those across a page beats three bare numbers floating.
- **Kicker on every content page, source on every page with numbers.** They cost nothing and they
  are what turns a bare heading into a composed slide.

### A4 — read in the hand

The opposite instinct. The page is close to the eye, so it holds four times what a slide does —
the `content` budget is 16 blocks on portrait against a slide's 8 — and a page with a slide's
worth of content on it looks empty and expensive.

- **Density is correct here.** Tables belong on A4. So do captions, footnotes and a source line
  under each exhibit.
- **Portrait runs 0 → 1.4143: it is tall.** Compose it as stacked bands down the page, each band
  a heading and the evidence under it, three or four bands to a page. Landscape runs 0 → 0.7071
  and wants columns instead — two or three, at a shared `y`.
- **Lead with the answer.** A printed page is scanned before it is read: heading, then one
  `subheading` line stating the finding in a sentence, then the evidence.
- **Keep the rhythm across pages.** Same rail, same band heights, same place for the source. A
  printed report is read as a sequence of pages laid side by side, and drift shows.
- **A cover earns its place** — `title` with the client, the period and the headline result — and
  a `closing` page with recommendations does too. Sections in between if the report is long.

### Dashboards — scanned at a desk, with no bottom

- **`paged` is off and the page grows.** Declare `page_height` yourself, as the sum of the bands
  you are placing plus the top and bottom margins. If the content does not fit, make the page
  taller — never compress the bands.
- **The budget is per unit of height**, not per page: 12 `content` blocks per 1.0 of height. A
  page of height 2.5 holds 30. That is the format saying "grow, do not cram".
- **Build it in bands.** A row of KPI metrics at a shared `y` and `h`; then a chart band; then a
  table. Blocks in a row share `y` and `h`; blocks in a column share `x` and `w`.
- **The top band is the answer.** Whoever opens this reads the first screen and often no more.
  Put the three or four numbers that matter at the top, with their deltas.
- **No source band.** Put the credit in a `caption` block at the bottom, at the rail.
- **Smaller type is fine.** The legibility floor is lower here than on a slide because the reader
  is 60cm away, so `caption` and `body` do real work.
- **No `title`, `section`, `quote` or `closing`.** A page with no top has no cover.

## Choose a design direction first

**Before writing any page, decide how this document looks.** Do not reach for the same answer
every time — two decks built a week apart should not be recognisably the same deck with different
numbers.

Pick one position on each axis and hold it throughout:

- **Type** — restrained (headings near `scale` 1) or dramatic (a short heading at `scale` 1.8–2.5
  owning half the page). Whatever you pick, keep it consistent across pages.
- **Structure** — centred, left-rail (everything aligned to one margin), or asymmetric (content
  weighted to one side, space left empty on the other).
- **Accent** — sparing (one accent in the whole document), per-page, or structural (the accent
  carries a repeating element such as every kicker).
- **Surface rhythm** — mostly light with one or two dark pages; alternating; or dark-led with
  light content pages.
- **Density** — airy or substantial.

Some directions that work, as illustrations rather than a menu — invent others:

- *Editorial*: dramatic type, left-rail, sparing accent, mostly light, airy.
- *Briefing*: restrained type, centred, per-page accent, alternating surfaces, substantial.
- *Statement*: dramatic type, asymmetric, structural accent, dark-led, very airy.

State the direction you picked in the first page's `notes`, so a later revision can hold it.

Then vary **within** the direction. A document where every page is kicker-heading-three-cards is
a template, not a design. Change what carries the page: sometimes a number, sometimes a chart,
sometimes a single sentence, sometimes a table.

## Design rules

Hard floors. Hold these whatever direction you chose.

- **A heading states the finding, not the topic** — "Paid search carried the quarter", never
  "Paid search".
- **Align things.** Blocks in a row share `y` and `h`; blocks in a column share `x` and `w`.
  Ragged frames are the clearest tell of a generated document. Asymmetry is a choice;
  misalignment is a mistake.
- **Blocks must not overlap.** They are placed absolutely and nothing pushes them aside, so an
  overlap is one block drawn over another. The write is rejected with both ids named.
- **Leave the margins alone.** Content inside the rail on both sides, clear of the chrome bands.
- **Nothing emphasised, or everything, is the same as nothing.** Exactly one per page.
- **Detail goes in `notes`.** Caveats, methodology, the numbers behind the numbers.
- **Cite the source** on every page carrying numbers.

## Reading and revising

```
list-canvases action=show canvas_id=<id>            # the outline: every page, its layout, its block count
list-canvases action=show_page canvas_id=<id> page_id=<id>   # one page's full spec
list-canvases action=validate canvas_id=<id>        # which pages will draw wrong, if any
list-canvases action=preview canvas_id=<id>         # look at a page (two calls — see below)
```

`show` deliberately does not return every page's blocks — a whole document would blow the
response cap. Read the pages you need, one at a time.

Fix one block without resending the page:

```
manage-canvases action=patch_blocks canvas_id=<id> page_id=<id>
                blocks=[{...the corrected block, same id...}]
                remove_block_ids=["stray-caption"]
```

Blocks whose `id` already exists are replaced in place; new ids are appended.

Rewrite a whole page — `pages` carries the page objects for every action, so this is `pages` with
exactly one entry, and more than one is refused:

```
manage-canvases action=update_page canvas_id=<id> page_id=<id> pages=[{...one page...}]
```

Omit `page_id` and the page is appended to the end instead. `action=sort_pages` takes every page
id in the new order.

### Not overwriting somebody's edit

Every page read returns an `updated_at`. Send it back as **`seen_at`** on your next write to that
page, and a write that would overwrite an edit made since you read it is refused with the current
timestamp instead of silently winning. People and agents edit the same page; this is what stops
one of them losing work with no error anywhere.

## Looking at a page

```
preview_canvas canvas_id=<id> page_id=<id>
```

Renders one page as an image, by the same renderer that draws it on screen and in the PDF.

**If `preview_canvas` is not in your tool list, use `list-canvases action=preview` instead.** It is
the same render delivered the other way, in two calls:

```
list-canvases action=preview canvas_id=<id> page_id=<id>     # returns a render_job_id
list-canvases action=preview canvas_id=<id> render_job_id=<id>   # returns the image
```

Wait between the two. A render takes twenty to thirty seconds, and much longer for a design bound
to live data, so a tight polling loop just spends turns. The turn rule below applies to that shape
too: until the second call hands you the image, you have not seen the page.

**You cannot see the image in the turn that calls this.** The call answers with a confirmation and
nothing else. The picture arrives on the *following* turn, which you will be given automatically.

So: call it, then **end your turn without saying anything about the page**. Describing it from the
spec in the meantime produces a confident and completely wrong answer — the first agent to use this
invented a kicker, three cards and a revenue figure that were not on the page, then described the
real page correctly one turn later.

What to do with it: look for what a validator cannot express. A heading colliding with a chart
that both technically fit. A page that is half empty. Numbers too small to read at the size the
page is actually viewed. A card whose contents are crowded against its edges. Say what is wrong
in words first, then fix it with `patch_blocks` and look again.

Use it after authoring a design, after a layout change you are unsure of, and whenever somebody
says a page looks wrong and you cannot see why from the spec.

## Checking a design still draws

```
list-canvases action=validate canvas_id=<id>
```

Every write you make is validated as you make it, so this is not a second check on your own work.
It answers a question your writes cannot: **has something changed underneath a page that was
already correct.** The type scale belongs to the brand, so switching a design to a brand with
larger headings can leave a heading that no longer fits its frame, and nothing was written, so
nothing was validated.

Call it after a run of edits, after changing a design's brand, and before telling anyone a design
is ready to share.

It reports content that does not fit the frame it was given, per page, in the same words a
rejected write uses. It deliberately says nothing about composition — a page where somebody
dragged a caption over a card is reported by nothing, because that is a choice rather than a
fault. So `valid: true` means nothing will draw clipped, not that every page follows the rules
you author by.

Repair each issue the way you would repair a rejected write: give the block more room, or shorten
its content. Then validate again.

## When a write is rejected

Composition is validated server-side and the message names the block and the fix:

> Page 3: Block `hero` runs off the bottom of the page: y 0.42 + h 0.20 = 0.62, and this page is
> 0.5625 tall. Frames are fractions of the page WIDTH, so a slide_16_9 page runs 0 to 0.5625 down.
> Shorten it to h 0.14 or move it up.

**Repair from the message and resend.** Do not simplify the page to get past the validator — the
error tells you the number to change, and dropping the block instead makes the document worse
than the rule was protecting it from. The rules are: overlap, off-page frames, text that will not
fit its frame, bars given too little room, block budgets, chrome bands, duplicate block ids, and
a data-bearing block carrying neither values nor a binding.

## Brands

A brand — a **design system** — is six named decisions: a brand colour, a mood (Light, Dark,
Bold), a chart palette, a typeface pairing, a shape, and a logo. Everything a block role resolves
to is derived from those six and cannot be authored directly, which is why a block can never
carry an off-brand colour.

```
list-design-systems action=catalog      # the named things: colours, moods, palettes, typefaces, shapes, presets
list-design-systems action=list         # the team's brands
```

Use the team's default unless the user asks otherwise. To make one:

```
manage-design-systems action=generate brief="a warm editorial brand for an independent bookshop
                                            — deep forest green, a paper-cream page, a serif for headings"
manage-design-systems action=create name="Bookshop" decisions={...the six it returned...}
```

`generate` saves nothing — keep what it returns and pass its `decisions` to `create`.

Attach a brand with `manage-canvases` `action=update design_system_id=<id>`. Switching it
restyles every page and touches no block.

**Changing an existing brand restyles every design already drawn in it.** When one design needs
its own look, make a new brand rather than editing the shared one.

Two things worth knowing: the `mono` chart palette yields only two separable colours by
construction — pick it only when two is what the charts need. And a brand colour may be any hex,
not only one from the named grid; it is deepened until white type reads on it.

## What this cannot do yet

- **Exporting on somebody's behalf.** There is no export tool and there will not be one — the
  person presses the button. See *Sharing and exporting* above for what each one costs.
- **Changing a format.** Every frame was composed against one page shape. Author again in the new
  format.
- **Uploading an image.** `image` blocks take a public `https` URL that already exists.
- **Styling a block in an Office export.** A block's own `style` reaches the browser, the PDF and
  the PNG. The PowerPoint and Google Slides writers draw the brand instead.

Surface a finished design as an artifact card in the chat rather than writing a link to it.

## Common pitfalls

- **Authoring before fetching.** You cannot query from inside a page. Fetch first.
- **A report and a design confused.** "Live, always current, in the reporting tool" means a
  report. "I'm presenting this Thursday" or "send them a PDF" means a design.
- **Treating `y` as a fraction of height.** It is a fraction of the *width*, like every other
  frame value. A block at `y: 0.8` is off the bottom of a slide.
- **A frame sized for the heading you first imagined.** Count the characters and the lines. This
  is the single most common rejection.
- **A kicker or source authored as a text block.** Use the page's fields. A hand-placed one drifts
  page to page and collides with the band the real one occupies.
- **Card children framed as if they were on the page.** Inside a card, `{"x":0,"y":0,"w":1,"h":1}`
  fills it. Page-level fractions there push the content into a corner.
- **Text over a toned card rather than inside it.** It resolves its ink against the page and can
  come out invisible.
- **Markdown in `content`.** `"**Audit referral sources**"` renders with the asterisks showing.
  Nothing parses markdown. Use `runs` with `bold`, or a `heading` and a `body` block.
- **Raw numbers in `value`, or in a table cell.** `142000` reads badly and a table cell that is
  not a string is rejected outright. Format every figure yourself: `"$142K"`, `"1,842"`.
- **Sentiment left off a delta, or confused with direction.** A falling CPA is `down` and
  `positive`. `down` alone renders a win in neutral grey.
- **Series not aligned with categories.** Three months of categories needs exactly three values in
  every series.
- **`set_pages` used for a small fix.** It replaces every page. To change one block, use
  `patch_blocks`.
- **A chart used for three numbers.** Use `bar_list` — axes and a legend around three bars is
  noise.
- **A widget created and never bound to a block.** It draws nothing and is deleted on the next page
  save. Create the widget and add its block in the same turn.
- **A dashboard of `query` bindings handed over with an empty channels panel.** The numbers are
  right and the design looks like it reads nothing. Attach the sources with `attach_sources`.
- **A widget used where a `query` binding would do.** A metric, a chart, a table or a bar list
  needs no widget. Create one for what the list above names, or because the person asked for a
  widget.
- **A `table` block handed back to somebody who asked for a report table widget.** The block is
  the right default and it is not what they asked for. An explicit ask outranks the default.
- **A dashboard page compressed to fit.** Raise `page_height`. It grows; that is the point of the
  format.
- **A table frame far taller than its rows.** A table does not stretch. Size the frame to the rows
  plus about a tenth — see *How tall is everything else*.
- **A table frame sized to its rows exactly.** The other half of the same mistake, and the one a
  validator cannot see: the bottom row is drawn, so nothing is clipped and nothing is reported,
  but it is jammed against the frame's edge and the next edit clips it.
- **A caption or kicker in a frame sized from the main table on A4.** The legibility floor is above
  what those two roles scale to there, so they draw about a fifth larger than the table says and a
  one-line caption becomes a clipped two-line one. Use the exception table.
- **A deck of ten `content` pages.** Vary the layout and the background. A dark `section` page and
  a `full_chart` are what give a document rhythm.
