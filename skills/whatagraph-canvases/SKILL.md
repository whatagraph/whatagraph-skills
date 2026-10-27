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
- "Put a channel filter at the top of this dashboard so they can narrow it themselves."
- "Make a one-page summary of the quarter."
- "Fix page 4 — the headline is wrong."
- "Show me where paid budget is being wasted." — one composed answer rather than a page, offered
  in the conversation for the person to place. See *Offering a group instead of writing one*.
- "Recreate this report in Whatagraph", with a PDF or deck attached — a replica, which is a
  different job from composing a deck. See *Replicating a file somebody gave you*.

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

## Replicating a file somebody gave you

When the person attaches a report, a deck or a PDF and asks for it **recreated, replicated,
rebuilt or copied**, the file decides the document, not you. Everything under *Composing for the
format* and *Choose a design direction first* is about deciding a document yourself, and none of
it applies: not the six to ten slides, not one idea per page, not the direction you would have
picked. The person is judging one thing, whether it looks like their report, and every page you
merge, drop or "improve" is a page that does not.

**Look at the pages, not only the text.** `read-document` with `pages` returns up to three pages
of the file as pictures per call. The extracted text carries the words and the figures but no
layout, colour, chart type or picture. Look at every page you build before you write it, and look
again at any page whose figures you are about to copy.

The steps:

1. **Inventory first.** Read the whole text once, then look at the pages, and write down what each
   page is: its number, its type (cover, section divider, KPI tiles, chart and commentary, table,
   funnel, screenshots, closing) and its blocks. Most reports repeat a dozen types across many
   pages. Put the inventory in the first page's `notes`, so a later turn can carry on.
2. **One frame-set per type.** Decide each type's frames once and reuse them exactly on every page
   of that type. A report where the KPI strip sits at a slightly different height on every page
   looks generated; the original did not.
3. **Keep every page, in order.** A 93-page report becomes a 93-page design. Merge or drop pages
   only when the person asks you to, and if the file is too long to finish in one turn, say how far
   you got and carry on in the next rather than condensing.
4. **Match the page shape.** A 16:9 deck is `slide_16_9`, an A4 report is `a4_portrait` or
   `a4_landscape`. Anything else is `custom`, with a `design_width` and each page's `page_height`
   set to the file's own proportions.
5. **Brand from the file.** Check `list-design-systems` first; a brand made for this client before
   is the one to reuse. Otherwise `manage-design-systems action=generate asset=<the file's id>`,
   with a `brief` naming the client: the model reads the pages, and a brand generated from a file
   keeps its exact colour on the panel instead of deepening it. Then `create` with what it
   returns.
6. **Build in batches.** `create` with the cover and the next four pages, then add the rest with
   `update_page` and no `page_id`, which appends one page per call. A refused write names every
   page that failed, so fix them all before resending. After each batch, `preview_canvas` one page
   of each type you introduced and compare it with the same page of the file.
7. **Copy figures from the page they are printed on.** Read each number and its change next to
   the label the file prints it under, from the page picture when the text is ambiguous. A delta
   belongs to the metric it sits beside; never carry one across from another page, and never fill
   a chart with values the file does not show. A figure you cannot read is `—`, and you say so.
8. **Bind every figure a channel reports, connected or not.** Check `list-sources`. A figure a
   connected source reports is a `binding` (see *Inline or bound*). A figure from a channel with no
   account connected yet keeps its typed-in payload **and** gets a binding naming the channel with
   `channel_id` instead of `sources` (see *A channel with no account yet*), so it becomes live the
   day the account is connected. A total across several ad platforms or a split by business unit is
   a blend or a source group plus a custom dimension (see *Totals across channels*). Only an offline
   buy or a computed share is typed in with no binding, copied exactly, with `notes` naming the file
   and page it came from.
9. **Report what you built, from the tool's answer.** Every write returns `data_blocks`: how many
   data blocks read a source, how many wait for a channel (`placeholder`) and how many are typed in.
   Your reply states the pages built against the pages in the file, those three numbers, the
   channels the person has to connect, and the page types you could not reproduce. Never say a
   design updates by itself while any of its figures are typed in or waiting.

**A funnel** (page views, add to cart, payment, purchase) is shapes, one card per funnel so four
platforms side by side stay inside a page's block budget. In each card: the platform name as a
`subheading` text, then one `stadium` `shape` per step with `fill: solid`, one `tint` for every step,
`role: caption`, and the step name and figure on two lines in `content` (`"Ajout panier\n9,640"`).
Each step is about 15% narrower than the one above it and centred under it. Between two steps, a
`circle` `shape` with `fill: soft` holds the conversion rate (`"40%"`). In page units, a 0.21 wide
card 0.44 tall fits four steps 0.06 tall with gaps of 0.036, and a rate circle needs about 0.042 of
the page's width: a smaller circle cuts a percentage off. Convert to the card's interior as
*Sizing a group's children* says.

**A dense page** (six small charts in a 3 x 2 grid, with a heading, tiles and a paragraph) can pass
a layout's block budget, which counts only the blocks on the page itself, not those inside a card.
Take `split` first, which holds 10 on a slide. Past that, put what the file draws as a box into a
`card`: a KPI tile strip is one card, a boxed commentary with its chart is one card. Do not wrap
blocks in a card the file does not box: a card draws a panel, and while `style.background:
transparent` hides it in the browser and the PDF, the PowerPoint and Google Slides exports draw it.

**Pictures come from the file's own pages.** `manage-assets action=crop_page asset_id=<the file>
page=<n> region={"x", "y", "w", "h"}` cuts a region out of that page and answers a public `url` for
an `image` block. The region is fractions of the page (0 to 1) from its top left, measured on the
picture `read-document` `pages` returned. Leave a small margin around the picture, crop each
creative or logo once, and reuse its `url` wherever the file repeats it. Use `fit: contain` when the
frame's shape differs from the crop's.

**It is always a new design.** Do not present a design that already exists as the replica, even
one with the same name made earlier in this conversation or by another agent. Build a new one, and
describe only what this turn wrote.

How the report's usual page types map onto blocks:

| In the file | In the design |
|---|---|
| Section divider: one huge title on a band | `section` layout, `dark` or `accent` background, `heading` at `scale` 2 or more; a band of colour is a `card` with no blocks. Two-tone italic display type is one `heading` with two `runs`, both `italic: true`, each with its own `ink` |
| KPI tiles: a dark box per figure with its label | A toned `card` (`tone: dark`) per tile, each holding a `metric`; tiles at one `y` and `h` form one row |
| Headline figures with icons and a change | `icon` plus `metric` with `delta`, `delta_direction` and `delta_sentiment` |
| Monthly trend: a small bar chart per measure | `chart`, `bar`, the months as categories |
| Horizontal bar ranking | Up to 6 rows: `bar_list`, `horizontal`. 7 to 12 rows: `chart`, `bar`, `orientation: horizontal`, usually with `show_data_labels` |
| Bars with a line on a second axis | `chart`, `bar`, and on the line's series `series_style` `{"type": "line", "scale": "secondary"}` |
| Pie or donut breakdown | `chart`, `pie` or `donut`, one series |
| Conversion funnel with step rates | One `card` per funnel, each step a `stadium` `shape` narrowing down the card, the step rate in a `circle` between steps (see *A funnel* below) |
| Table | `table`, every cell a formatted string |
| Commentary paragraph or bullet box | `text` with `role: body`, inside a `card` when the file boxes it |
| Ad creatives, screenshots, logos | `image` with the `url` that `manage-assets action=crop_page` returns for that region of the file's page (see below) |
| Learnings grid (continue, optimise, stop, start) | One `card` per column at one `y` and `h`, each with a heading and a body |

## The workflow

1. **Read the registry.** `list-canvases` `action=formats`. Page geometry, block budgets and the
   bands the chrome occupies are server-owned and change without a release. Never author from
   remembered numbers.
2. **Pick the brand.** `list-design-systems` `action=list`. Use the team's default unless the
   user asks for something else. A design with no brand is drawn in the default one — never
   unstyled — so this step is optional, not skippable-with-consequences.
3. **Fetch the data.** `list-sources`, then `fetch-data`. Do this *before* authoring: the story
   comes from reading the numbers, and you cannot query from inside a page. Keep every call you
   made, because each one becomes a `binding`: the block that shows that data carries the call's
   `source_id`, `report_type`, `metrics` and `dimensions`, not the figures it returned. See
   *Inline or bound*.
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
      "chart": {"chart_type": "bar"},
      "binding": {"kind": "query", "sources": [2], "metrics": ["sessions"],
                  "dimensions": ["sessionDefaultChannelGrouping"]} },
    { "id": "trend-takeaway", "type": "text",
      "frame": {"x": 0.65, "y": 0.2025, "w": 0.29, "h": 0.09},
      "text": {"role": "body",
               "content": "Organic search added most of the lift, and paid search finally turned profitable."} }
  ]
}
```

Every block carries an **`id`**, unique within the page. It is how you address that block later
with `patch_blocks`, so make them mean something: `hero-metric`, `trend-chart`, `cta`.

The chart above carries no numbers. It carries the query that produces them, which is how every
block showing a source's figures is written, in a deck as much as in a dashboard. The payload
fields under *Block types* are for the figures no source reports. See *Inline or bound*.

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
  frame the size you want the thing to be. An **`icon`** fills the largest square its frame
  holds, centred, so give it a square frame.
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
- An **icon** is nothing but ink: `ink` recolours the glyph, `emphasis` draws it in the accent,
  and a multicolour icon's further shades follow the ground's chart ramp.
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
  `donut`, `scatter`, `radar`. On a `bar`, `line` or `area` chart one series can draw as another of
  those three through `series_style[i].type`, which is how bars get a line through them. A `bar`
  chart with `orientation: horizontal` lays its categories down the side, first at the top.
- **`table`** — `headers` and `rows`; every row has one cell per header. **Every cell is a string
  you have already formatted** — `"1,842"`, `"$34.02"`, `"—"` — never a raw number, and never an
  object: a cell carries no colour or weight of its own, and a non-string cell is rejected. When a
  figure has to be coloured, it is not a table cell — pull it out into a `metric`, or write the
  sentence with a `run`.
- **`image`** — a public `https` `url`, plus `alt` and `fit` (`cover` crops, `contain`
  letterboxes).
- **`icon`** — one glyph from the icon library, the same library a single value widget picks
  from: `file`, written verbatim (`"Heart--Streamline-Sharp.svg"`, `"Ad-clicks.svg"`), plus
  `alt`. Browse the library with `list-widgets action=list_icons`; a file it does not have is
  refused. It draws in the block's ink, so a themed page recolours it. The `Streamline-Sharp`
  files are single-stroke line icons and take the ink wholesale; the older multicolour files
  take it for their first shade and the chart ramp for the rest, and the few drawn in fixed
  colours — the reactions, the search-engine logos — keep them.
- **`card`** — a surface holding other blocks. Give it `blocks`. **Child frames are fractions of
  the card on both axes**, not of the page, and **every child needs a real frame** — one filling
  its card is `{"x": 0, "y": 0, "w": 1, "h": 1}`. Cards cannot nest.
  **`"grouped": true`** turns the card into a **group**: one thing the reader clicks, moves and
  deletes, whose parts are reached by stepping into it. That is how a composed answer is written
  — see *Groups* below.
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
  **`metric`, `chart`, `table` and `bar_list` take a `binding` instead of the payload above**
  whenever the figures come from a source. A bound `chart` keeps its `chart_type` and `title`;
  a bound `metric` keeps nothing, and its label is the metric's own name from the catalogue. See
  *Inline or bound* for the rule and the shape.
- **`control`** — a filter the reader moves, and **where it sits decides what it reaches**.
  Inside a card carrying a `query` binding it is a slider, a row of chips or a switch that narrows
  the rows that card fetched, in the browser, without refetching anything. On the page, or inside
  a card with no binding, it names a `source` and re-queries every block around it bound to that
  source — the report's filter control, on a design. Neither changes the document. See *A
  control* and *A filter* under *Groups*.
- **`widget`** — an existing Whatagraph widget, drawn on the page. Its `binding` names the
  `widget_id`; the widget keeps its own configuration and picks up the design's brand. Chrome is
  off by default because the page already has its own text blocks. Give it at least 232 × 110
  design pixels — below that a widget refuses to render.

## Groups

A **group** is a `card` with `"grouped": true`. It is how you answer a question with one thing
rather than five.

It is the same block type and the same fields as any other card. What the flag changes is how a
person handles it: one click selects the whole group, moving or deleting it moves or deletes
everything inside it, and the parts are reached by double-clicking into it. So a group is the
right shape whenever the blocks you are about to write only mean anything together.

**Reach for a group when somebody asks a question rather than for a page.** *"Show me where paid
budget is being wasted"* wants a few metrics, a table and a sentence saying what they mean, and
those blocks are one answer. Written as a group, the person can move that answer, copy it to
another page or throw it away in one gesture.

**Leave `grouped` off** for a band of colour, for a surface somebody will drop blocks onto later,
and for a single number with a caption under it. A plain card is already right for those, and the
flag only puts a step between the person and the contents.

Two limits worth knowing before you compose one:

- **A group counts as one block against the layout's budget**, however many children it holds. A
  `content` slide holds 8 blocks and a group of five costs one of them. That is a reason to
  compose a dense page out of groups, not a licence to put a whole page inside one — a group
  holding more than about six children is a page.
- **Groups do not nest**, because cards do not. A group's children are blocks, never groups.

A child keeps its own `id`, so `patch_blocks` reaches it by that id without resending the card.

### Sizing a group's children

**A child's frame is a fraction of the card's interior on both axes**, so `x`, `y`, `w` and `h`
all run 0 to 1 and one filling the card is `{"x": 0, "y": 0, "w": 1, "h": 1}`. This is the one
place in a design where `y` is not in the page's width units, and forgetting it is what puts
every child in the top eighth of the card.

The interior is the card's box less its padding, which is **0.012 of the page's width on each
side**. So in the page's own width units the interior is `card.w − 0.024` wide and
`card.h − 0.024` tall, and every number in this skill converts like this:

```
child w = (the width you need, in page width units) ÷ (card.w − 0.024)
child h = (the height you need, in page width units) ÷ (card.h − 0.024)
```

Worked: a `subheading` needs 0.028 of the page's width for one line. In a card `0.46 × 0.34` the
interior is 0.316 tall, so one line is `h: 0.028 ÷ 0.316 ≈ 0.09` — and give it `0.11`, for the
same reason a table wants its rows' height plus a tenth.

Three numbers get used at once inside a group, so they are collected here:

- **A table row, the header included, is 0.032 of the page's width** — 0.039 on `a4_portrait`.
- **A ranked `bar_list` row wants about 0.04 of the page's width** each, so six bars want 0.24.
  An authored list asking for more bars than its frame holds is refused, with the height to give
  it; a bound one is cut to what fits and says nothing.
- **Metrics form a row when their frames overlap vertically by more than half of the shorter
  one**, and a row is sized together. Inside a group that means a band of metrics wants one `y`
  and one `h`. Two bands at different `y` are two rows and are sized separately, so give them
  equal frames if they are meant to read as a pair.

On `a4_landscape` multiply the widths by 1.41 and divide the heights by 1.41, exactly as in the
type table above.

**Children must not overlap**, the same rule page blocks are held to, and the write is refused
naming the card and both children. Leave about 0.04, in card units, between one child and the
next.

**A chart inside a group is a supporting trend.** A chart that has to carry the page belongs on
the page at `full_chart` size, not inside a card a third of the page wide.

### One query for the whole group

**Put the `binding` on the card, not on each child.** The query then runs once, and every
`metric`, `chart`, `table` and `bar_list` inside the card is drawn from that one row set. Two
things follow, and both are the reason to do it:

- **The figures agree with each other.** A metric above a table is a figure about that table's
  own query, and the sentence underneath can say so.
- **The group costs one call instead of one per child.** A card with three metrics and a table
  used to make four; it makes one.

Bind the card exactly as you would bind a block — `sources`, `metrics`, `dimensions`,
`report_type`, `date_range`. Name every metric and dimension the group needs between them; a
child picks out the part it draws.

**Leave the children's own `binding` and payload off.** A child of a bound card needs neither, and
a child that carries a `binding` is opting out — it keeps its own query and its own request, which
is what you write when one block inside the group has to come from another source.

**Say which part each child draws with `projection.columns`**, naming metrics and dimensions by
the same `external_id` the card's binding uses:

- A **metric** needs one metric in `columns`, or it draws the first one the card fetched. Add
  `agg` to say how it collapses the rows — `sum` is the default and is the period's total, which
  is the same figure the report's single-value widget draws.
- A **chart** and a **bar_list** take a dimension and the metrics to plot. Omit `columns` and they
  take everything the card fetched, which is right when the card fetched exactly what they draw.
- A **table** omits `columns` to show every column, or names them to show fewer, in its own order.

```json
{ "id": "channels", "type": "card",
  "frame": {"x": 0.06, "y": 0.16, "w": 0.88, "h": 0.5},
  "binding": { "kind": "query", "sources": [12],
    "metrics": ["sessions", "conversions"], "dimensions": ["sessionDefaultChannelGrouping"] },
  "card": { "grouped": true, "rounded": true, "blocks": [
    { "id": "ch-sessions", "type": "metric", "frame": {"x": 0, "y": 0, "w": 0.3, "h": 0.2},
      "projection": {"columns": ["sessions"]} },
    { "id": "ch-conv", "type": "metric", "frame": {"x": 0.35, "y": 0, "w": 0.3, "h": 0.2},
      "projection": {"columns": ["conversions"]} },
    { "id": "ch-table", "type": "table", "frame": {"x": 0, "y": 0.26, "w": 1, "h": 0.74} }
  ] } }
```

**What still differs between children, and it is display rather than arithmetic.** A table shows
the rows its frame holds and a ranked bar list the bars its frame holds, so two children of one
group can show a different number of rows of the same row set. Nothing adds up what a table
happens to be showing, so this changes what is drawn and not what anything reports.

**One figure is worth knowing about.** A metric's `sum` is the total the data source reports for
the period, which is not always the sum of the rows beneath it: a ratio does not add up, and a
source that de-duplicates people over a range reports fewer than the daily figures total. That is
the right figure for a metric and it is why the sentence under a group should describe the ranking
rather than claim the column adds to the number above it.

**When each child really does need its own query** — different sources, different date ranges,
genuinely different questions — leave the card unbound and bind the children. That still works,
and the two ways can sit on one card. Expect the figures not to agree, and do not write a sentence
saying they do.

### A control: letting the reader narrow the group

A **control** is a slider, a row of chips or a switch that sits inside a bound card and narrows
the rows that card fetched. Every metric, chart, table and bar list in the card redraws from what
is left. It changes nothing in the document, costs no fetch, and works for somebody reading a
share link.

Inside a card carrying a `query` binding its `field` must be one of the metrics or dimensions
that binding names, and it takes no `source` — the card already names one. The same block **on
the page, or inside a card with no binding, is a filter** that re-queries instead of narrowing;
see *A filter* below.

Three kinds:

- `range` — a slider over a metric. Needs `min` and `max` in the metric's own units, and compares
  with `gte` ("at least", the default) or `lte` ("at most").
- `choice` — one value of a dimension. **Leave `options` off** and the values the query returned
  are offered, which is almost always what you want; nobody knows in advance which channels a
  month of traffic will contain. `eq` picks one, `in` picks several.
- `toggle` — a switch. On, it keeps the rows that have anything at all in `field`: a non-zero
  figure in a metric column, a value in a dimension column.

`value` is what the control is set to when the page opens, and the only thing about it that is
stored. A PDF, a PowerPoint file and a Google Slides deck are all drawn at that value. Omit it and
the control starts filtering nothing, which is the right default for a page a person will read
before they touch anything.

```json
{ "id": "min-sessions", "type": "control",
  "frame": {"x": 0.03, "y": 0.24, "w": 0.42, "h": 0.1},
  "control": { "kind": "range", "label": "Sessions at least",
    "field": "sessions", "min": 0, "max": 20000, "step": 500 } }
```

**One control per card is plenty**, and give it a frame of its own — a strip above the table it
narrows reads best. A choice over a dimension with many values draws many chips, so either give it
room across the card or name the handful of `options` worth offering.

**A ratio cannot be narrowed into a total.** When a control drops a row, a metric whose column is
a rate draws nothing rather than a figure, because adding two percentages together means nothing
and there is no way to recompute the rate from one column. Put the counts in a group that has a
control on it and leave the rate to the table, or set `agg` to `avg` and say in the sentence that
it is an average of the rows on screen.

### A filter: letting the reader refilter the page

The same `control` block **on the page**, or inside a card with no binding, is a filter over the
page rather than over one card. It names a `source` and a `field`, and when the reader moves it
every block around it bound to that source — a metric, a chart, a table, a bound card, a `widget`
block — is fetched again with one more filter row, the way a report's Filter Control refetches
every widget of its source. Nothing is stored but the control's own default: a reader's pick lives
in their browser, travels with the data requests, and is drawn into the PDF or PNG they export.

**Placement decides reach, and there is no scope field to disagree with it.**

- **On the page**: every block on the page bound to `source`, wherever it sits, a bound card and a
  widget block included.
- **Inside a card with no binding**: that card's blocks only.
- **Inside a card carrying a `query` binding**: it is the group control of the previous section —
  it narrows the card's rows in the browser and is refused a `source`.

A block bound to another source is left alone, and a block that reads nothing — an inlined
figure — is reached by nothing. `targets` narrows the reach to the block ids it names, each of
which must be one the control reaches anyway. Leave it off; that is the usual case.

Three kinds, and when each is honest:

- `choice` — a select over a dimension. Leave `options` off and the source's own values are
  fetched when the select opens. **A source that lists values for none of its dimensions offers
  an empty select** — Google Analytics 4 is one — so there, write the `options` yourself when the
  set is known (the default channel groupings are), or use `text`. `eq` picks one, `in` several.
- `text` — a text box matched by what the dimension contains: "campaigns containing `brand`".
  Page only: inside a bound card the rows are already fetched and a `choice` over them is the
  honest control. Give it `"apply": "button"`, because every apply re-queries every block the
  control reaches, and nobody wants that per keystroke.
- `range` — a slider over a metric, with `min`, `max` and `gte` or `lte`, as in a card. It
  applies when released.

`toggle` stays in the card: no filter can ask a source whether a column "holds anything at all".

`apply` is `change` (the default) or `button`. `value` is the stored default — what a reader who
never touches the control sees, and what a share link, a frozen copy and an export start from.
Omit it and the page opens unfiltered.

**A deck refuses it.** A page filter is allowed in the dashboard, A4 and custom formats and is
rejected on a slide: a presentation has nobody to move it. Put the control inside a bound card
there, pin the question in the binding's `filters`, or leave it out.

**Name a source a block on the page reads.** The validator cannot check this, because the control
fetches nothing on its own: a filter over a source no block is bound to saves cleanly and reaches
nothing. Copy `source` from the `binding.sources` of the blocks it should move.

A dashboard page with a channel filter over three metrics and a table, all reading one source:

```json
{ "layout": "content", "page_height": 0.9, "blocks": [
  { "id": "channel", "type": "control",
    "frame": {"x": 0.04, "y": 0.04, "w": 0.3, "h": 0.06},
    "control": { "kind": "choice", "label": "Channel", "source": 2,
      "field": "sessionDefaultChannelGrouping",
      "options": ["Organic Search", "Paid Search", "Direct", "Referral", "Organic Social", "Email"] } },
  { "id": "sessions", "type": "metric", "frame": {"x": 0.04, "y": 0.14, "w": 0.28, "h": 0.12},
    "binding": { "kind": "query", "sources": [2], "metrics": ["sessions"], "compare": "previous" } },
  { "id": "conversions", "type": "metric", "frame": {"x": 0.36, "y": 0.14, "w": 0.28, "h": 0.12},
    "binding": { "kind": "query", "sources": [2], "metrics": ["conversions"], "compare": "previous" } },
  { "id": "revenue", "type": "metric", "frame": {"x": 0.68, "y": 0.14, "w": 0.28, "h": 0.12},
    "binding": { "kind": "query", "sources": [2], "metrics": ["totalRevenue"], "compare": "previous" } },
  { "id": "pages", "type": "table", "frame": {"x": 0.04, "y": 0.3, "w": 0.92, "h": 0.5},
    "binding": { "kind": "query", "sources": [2],
      "metrics": ["sessions", "conversions"], "dimensions": ["pagePath"] } }
] }
```

Every block the filter reaches draws a small caption of its own — *Filtered by Channel: Paid
Search* — so the reader sees what was narrowed, and nothing in your text needs to say so. The
deltas keep drawing: the comparison period is filtered the same way.

A write that puts a filter where it cannot work is refused with the fix in the message — the
`source` it is missing, the kind that belongs in a card, the slide it cannot sit on, the target
it would not reach. Repair from the message; do not drop the filter to get past it.

### Suggested actions: the changes worth making to a group

`actions` on a card is a short list of one-tap changes offered while somebody has the group
selected. Each one is a label, the `block_id` it changes, the `path` of the field it sets, and
the values the chips cycle through.

**It is not a control.** A control narrows what the group *shows* and changes nothing in the
document. An action **edits the document**: it is stored, it can be undone, and only somebody who
can edit the design sees it. Use a control for "only the channels above 10,000 sessions", and an
action for "draw that as a line instead".

```json
"card": { "grouped": true, "rounded": true,
  "actions": [
    { "label": "Chart type", "block_id": "ps-trend", "path": "chart.chart_type",
      "options": ["bar", "line", "area"] },
    { "label": "Surface", "block_id": "paid-summary", "path": "card.tone",
      "options": [null, "dark"] }
  ],
  "blocks": [ ... ] }
```

**Pick two or three, and pick them for this group.** The argument the page is making is what
decides them: a trend that could be read as a ranking wants the chart type, a funnel wants the
bar list's orientation, a card meant to stand out on a busy page wants its surface. A row for
every setting the blocks have is not a suggestion, and the Style panel already lists those.

**Leave `actions` off** and the editor offers a set worked out from what the children are, which
is right for an ordinary group. Write the field only when you know something about this group
that the children do not say.

The fields an action may set, and nothing else:

| `path` | On | Values |
|---|---|---|
| `chart.chart_type` | `chart` | `bar`, `line`, `area`, `pie`, `donut`, `scatter`, `radar` |
| `chart.fill` | `chart` | `solid`, `hatched` |
| `chart.show_data_labels` | `chart` | true, false |
| `chart.show_grid_lines` | `chart` | true, false |
| `chart.show_legend` | `chart` | true, false |
| `chart.line_curve` | `chart` | `sharp`, `smooth` |
| `bar_list.orientation` | `bar_list` | `horizontal`, `vertical` |
| `text.role` | `text` | `kicker`, `heading`, `subheading`, `body`, `caption`, `quote` |
| `text.align` | `text` | `left`, `center`, `right` |
| `card.tone` | the card | `default`, `dark`, `accent`, or null for no surface |
| `card.rounded` | the card | true, false |
| `emphasis` | any drawn block | true, false — draws its ink in the brand accent |

A `path` outside that list is rejected, and so is one the named block's type does not have. Every
action needs between two and six options: one chip has nothing to switch to.

**Nothing here refetches.** These are all changes to how a block is drawn, which is why they are
instant and undoable. What a block's figures are comes from the card's `binding` and each child's
`projection`, and neither is something an action can set.

### Four group recipes

The four shapes that keep coming up, with the arithmetic done. Card frames are in the page's
width units and suit a slide or a dashboard; child frames are in card units. On `a4_portrait`
give the card more height, because the page is taller and its type is larger.

Change the children to suit the question. A page built from four identical recipes is a template.

The frames are all any of them shows. **Put the query on the card**, as *One query for the whole
group* above describes, and give each metric a `projection`; the recipes leave the binding out
only so the layout is readable.

**1. Performance summary** — how something is doing, at a glance. A row of metrics over a trend.

```json
{ "id": "paid-summary", "type": "card",
  "frame": {"x": 0.06, "y": 0.16, "w": 0.46, "h": 0.34},
  "card": { "grouped": true, "rounded": true, "blocks": [
    { "id": "ps-heading", "type": "text", "frame": {"x": 0, "y": 0, "w": 1, "h": 0.11},
      "text": {"role": "subheading", "content": "Paid search, last 30 days"} },
    { "id": "ps-spend",  "type": "metric", "frame": {"x": 0,    "y": 0.15, "w": 0.30, "h": 0.22} },
    { "id": "ps-conv",   "type": "metric", "frame": {"x": 0.35, "y": 0.15, "w": 0.30, "h": 0.22} },
    { "id": "ps-cpa",    "type": "metric", "frame": {"x": 0.70, "y": 0.15, "w": 0.30, "h": 0.22} },
    { "id": "ps-trend",  "type": "chart",  "frame": {"x": 0,    "y": 0.43, "w": 1,    "h": 0.45} },
    { "id": "ps-note",   "type": "text",   "frame": {"x": 0,    "y": 0.90, "w": 1,    "h": 0.10},
      "text": {"role": "caption", "content": "Cost per acquisition fell for the third month running."} }
  ] } }
```

The three metrics share a `y` and an `h`, so they are one row and take one size.

**2. Breakdown** — what the total is made of. A table ranked beside the same figures as bars.

| Child | Frame, in card units |
|---|---|
| heading, `subheading` | `{"x": 0, "y": 0, "w": 1, "h": 0.10}` |
| `table` | `{"x": 0, "y": 0.14, "w": 0.56, "h": 0.72}` |
| `bar_list`, `horizontal` | `{"x": 0.6, "y": 0.14, "w": 0.4, "h": 0.72}` |
| caption | `{"x": 0, "y": 0.90, "w": 1, "h": 0.10}` |

Card frame `{"x": 0.06, "y": 0.14, "w": 0.6, "h": 0.4}`. The table's frame is 0.271 of the page
tall, which is a header and six rows with the tenth of slack a table wants; the bar list's is the
same, which is six bars. Put the query on the card so both are drawn from one row set, and let
the table carry the detail while the bars carry the ranking.

**3. Comparison** — this period against the one before it, or one channel against another.

| Child | Frame, in card units |
|---|---|
| heading, `subheading` | `{"x": 0, "y": 0, "w": 1, "h": 0.10}` |
| first row, two `metric`s | `{"x": 0, "y": 0.13, "w": 0.48, "h": 0.16}` and `{"x": 0.52, "y": 0.13, "w": 0.48, "h": 0.16}` |
| second row, two `metric`s | `{"x": 0, "y": 0.32, "w": 0.48, "h": 0.16}` and `{"x": 0.52, "y": 0.32, "w": 0.48, "h": 0.16}` |
| `chart`, `bar`, two series | `{"x": 0, "y": 0.54, "w": 1, "h": 0.46}` |

Card frame `{"x": 0.06, "y": 0.14, "w": 0.5, "h": 0.4}`. The two metric rows do not overlap
vertically, so each is sized on its own members — the equal frames are what keep the two bands
looking like a pair. Name what each row is in the metric labels, not in a fifth text block.

**4. Funnel** — the stages, and what came out of the end.

| Child | Frame, in card units |
|---|---|
| heading, `subheading` | `{"x": 0, "y": 0, "w": 1, "h": 0.10}` |
| `bar_list`, `horizontal` | `{"x": 0, "y": 0.13, "w": 1, "h": 0.55}` |
| three `metric`s | `{"x": 0, "y": 0.74, "w": 0.31, "h": 0.26}`, `{"x": 0.345, …}`, `{"x": 0.69, …}` |

Card frame `{"x": 0.06, "y": 0.14, "w": 0.44, "h": 0.42}`. The bar list's frame is 0.218 of the
page tall, which holds five stages, and its `ratio` values are what make it read as a funnel —
give the first stage `1.0` and each later one its share of it. The metrics below are the
conversions the stages produced, in one row so they take one size.

### Offering a group instead of writing one

```
propose_group title="Paid search, last month" card={…} canvas_id=<id>
```

Composes the group and shows it to the person in the conversation, drawn with real data and with
its controls working, **without changing any document**. They press a button to put it on a page.

**Which one to use is decided by what they asked for, not by how big the change is.**

| They said | You do |
|---|---|
| "add a channel table to this page", "put three KPIs at the top", "make the chart a bar chart" | `manage-canvases` — write it |
| "show me where paid budget is being wasted", "what would a device breakdown look like", "can you make me a summary of last month" | `propose_group` — offer it |

When no design is open, `propose_group` is the only one of the two that makes sense: there is no
page to write to. Pass `space_id` there, because the draft has to be kept somewhere.

The `card` is exactly the block you would have written onto a page — `"type": "card"`,
`"grouped": true`, its parts in `card.blocks`, one `binding` on the card and a `projection` on each
child. Writing the card's own fields on their own — `{"frame": …, "binding": …, "grouped": true,
"blocks": [...]}`, with no `id` and no `type` — means the same thing and is accepted. **Every entry
in `blocks` still needs its own `id`, `type` and `frame`,** whichever way round you write the card.

The card's `frame` is optional: only `h` is read, as how tall the group is against its width, and
where it sits is decided by the page it is eventually placed on.

Three things to get right:

- **Pass `canvas_id` whenever a design is open.** The group is drawn at that design's size and in
  its brand, which is what makes the picture in the conversation the same picture they will get on
  the page. Without it the draft falls back to a 16:9 slide in the space's default brand, and the
  card in the chat says so.
- **Do not also write it onto a page.** The person places it. Writing it as well puts the group in
  their document twice, and the second copy is the one they did not ask for.
- **Say in one sentence what the group shows.** The card is already in front of them, so describe
  the answer, not the blocks: *"Paid search spend is up 18% while conversions are flat — the table
  breaks it down by campaign."* not *"I have created a card with three metric blocks and a table."*

To change a proposal after they ask for something different, edit page 1 of the draft design the
call returned with `manage-canvases action=patch_blocks`, and the card in the conversation redraws.
Propose a new one only when they want a different answer rather than a change to this one.

## Inline or bound

Every data-bearing block — `metric`, `chart`, `table`, `bar_list` — either **carries** its
numbers or **fetches** them.

**Bound is the default, in every format.** A figure a connected source reports is written as a
`binding` on the block, never typed into it. The binding is the `fetch-data` call you already
made: `source_id` becomes `sources`, and `report_type`, `metrics` and `dimensions` are copied
over as they are. This holds for a deck and a printed page as much as for a dashboard. A typed-in
figure is connected to nothing: the editor's Data panel says "Not connected to data" on every
such block, nothing can refresh it, and the person opening the design cannot see where it came
from. A design full of them reads as invented, however carefully each number was fetched, and
"why is this not linked to the source you pulled it from" is the first thing they will ask.

**Inline** is for the figures no source reports: a number you computed from two fetched ones (a
share, a ratio of ratios), a figure you researched on the web, an estimate, a target. Write those
as formatted strings and say in `notes` how each was arrived at.

**A deck's numbers do not drift when they are bound.** Set the document's `date_range` to the
period the deck is about (`lastQuarter` for a quarterly review, `lastMonth` for a monthly one) and
`compare` to what the deltas are against, and every bound block reads that period. A PDF, a
PowerPoint file and a Google Slides deck resolve the bindings when they are exported, so they
carry the numbers the page shows. When the person wants a copy that never changes, `freeze` makes
one and the design stays live.

Give the block a `binding` and no payload of its own — the resolver fills it every time the
design is opened:

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
- `filters` pins a condition on the query: a flat list of `{"dimension" | "metric", "operator",
  "value" | "values", "join"}` in the `manage-filters` vocabulary (`includes`, `contains`, `>=`,
  …), rows joined with `and` unless one says `or`. That is the filter the **author** decides;
  the filter the **reader** moves is a `control` — see *A filter* under *Groups*.
- A bound `table` or `bar_list` is **cut to what its frame holds**, so give it room for the rows
  you expect rather than assuming everything comes back.
- `kind: "widget"` with a `widget_id` draws a widget instead of a query — either one a report
  already has, or one the design owns. See *Three ways to make a block live* below.
- A **card** takes a `query` binding too, and that binds every data block inside it to one row
  set. It is the right answer whenever a card's children are all about the same question. See
  *One query for the whole group*.

**Dates cascade: document → page → block.** Set `date_range` once on the design and every bound
block follows it; a page or a block overrides it with a period key of its own. `inherit` is the
default on a binding and is almost always what you want — one picker moving a whole document is
the point. A **share link** can pin a period too, standing in for the document's own rung, which
is how a client gets March while the dashboard keeps rolling.

```
manage-canvases action=update canvas_id=12 date_range=lastQuarter compare=previous
```

A block can also pin **dates** instead of a key. `date_from` and `date_till` with no `date_range`
is a fixed range; that is how a monthly trend from January to July sits on a page about July.
`date_range: "customRangeYesterday"` with a `date_from` runs from that date up to yesterday, and
`thisYearExclToday` is the year to date. Both dates are `YYYY-MM-DD`.

```json
{ "kind": "query", "sources": [2], "metrics": ["spend"], "dimensions": ["date"], "grouping": "1 month",
  "date_from": "2026-01-01", "date_till": "2026-07-31" }
```

A period is a **calendar key, and it is camelCase**: `last30Days`, `lastMonth`, `thisQuarter`,
`last12Month`. Snake case looks right and is not — an unknown key is refused with the full list,
so read the message rather than guessing again.

`data_mode` follows the bindings: the first binding written onto a design promotes it from
`inlined` to `bound`, so there is nothing to set. `inlined` only ever describes a design that has
no bindings at all.

### A channel with no account yet

A report copied from a file usually names channels the team has not connected: Meta, TikTok,
DV360. Do not settle for typing those figures in. Bind them to the **channel** instead of a
source, and keep the payload you copied from the file:

```json
{ "id": "meta-spend", "type": "metric", "frame": {"x": 0.04, "y": 0.16, "w": 0.2, "h": 0.11},
  "metric": {"value": "$41,200", "label": "Spend"},
  "binding": { "kind": "query", "channel_id": 4, "metrics": ["spend"] } }
```

- `channel_id` is the channel's id from `list-integrations`; `metrics` and `dimensions` come from
  `list-sources` `action=list_dimensions_and_metrics` with that `channel_id` and no `source_id`.
  A metric the channel does not have is refused when the block is read, naming the ones it does.
- The block draws its payload until the channel is mapped, so the page looks like the file.
- Bind a **block**, not a card: a card's query feeds its children and has nothing to show
  meanwhile, so a card waiting for a channel is refused.
- Once the person connects the account, one call makes every such block live, on every page:

```
manage-canvases action=map_channel canvas_id=12 channel_id=4 source_ids=[318]
```

### Totals across channels, and splits by business unit

A figure summed over several ad platforms is one source when the platforms are blended. A
**blend** (`manage-blends`) or a cross-channel **source group** (`manage-source-groups`) is an
integration source like any other, so a binding names its id in `sources`. Their summed metrics
have their own ids: list them with `list-sources action=list_dimensions_and_metrics` on the blend or group (a
blend's are `aggregation_metric_universal_metric_<id>`; a source group's need its `report_type`).
`list-sources action=list` hides blends and groups unless you pass their channel in `channels`.

A split the file makes by **business unit, product or objective** usually lives only in campaign
names. Make it a custom dimension with `manage-custom-dimensions` (`map_type: data`, one rule per
unit, such as campaign name `contains` "brand" then "Brand") and name its
`universal_dimension_<id>` in `dimensions` or in a `filters` condition. Make one dimension per
split and reuse it on every page.

### A summary: letting the page write its own narrative

Commentary is data too. A paragraph that says "sessions rose 18% while spend held" is a figure
typed into prose, and it goes stale the first time the range moves. A `text` block with a
`summary` binding is written by the model from the data blocks around it, stored on the block,
and written again whenever the data it read changes. It is the report's AI summary, drawn in the
design's own typography.

```json
{ "id": "takeaways", "type": "text", "frame": {"x": 0.06, "y": 0.34, "w": 0.88, "h": 0.16},
  "text": { "role": "body" },
  "binding": { "kind": "summary", "sections": ["wins", "issues"] } }
```

- **`text` carries only `role`** (and `align` or `scale` if you want them). No `content`, no
  `runs`: the resolver writes them.
- **Where it sits decides what it reads.** On the page it reads every data block on that page.
  Inside a card it reads that card. `scope: "document"` reads every page, for an executive summary
  at the front of a deck. `targets: ["revenue_chart"]` reads only the blocks named, for "what does
  this chart say". Text, images, icons, shapes and controls are never read; the page's title,
  kicker and headings travel along so the model knows what the page is about.
- **`sections`** are `summary`, `wins`, `issues`, `recommendations` and `custom`, written in the
  order given. `custom` needs `custom_prompt`. `length` is `short` (about three sentences a
  section, the default) or `long` (about eight). `language` takes the report's list, `English` by
  default.
- **`refresh`** is `auto` (rewritten when the data moves) or `manual` (kept until somebody asks for
  new words). Leave it off: it defaults to `auto` where the team has AI summary auto-update and
  `manual` where it does not, and the team's plan is checked on every read anyway.
- **Nothing is written when you save the block.** The words are written the first time the page
  is opened, which costs one model call and a few seconds. To write them now and read what came
  out, call:

  ```
  manage-canvases action=regenerate_summary canvas_id=12 page_id=41 block_id=takeaways
  → { "text": "Summary\nSessions rose 18%…", "inputs": ["sessions", "spend", "trend"] }
  ```

  `inputs` names the blocks it read. An empty one means the summary had nothing to read: put it
  where the data blocks are, or name them in `targets`. The same call is how you change words the
  person did not like, `manual` or not.
- **Give it room.** One short section is three or four lines of body text; two sections with
  their headings are about twice that. The block cannot be sized from its words because you do
  not have them, so size the frame for the sections and length you asked for. A frame that is too
  small clips the summary; the editor flags it, and nothing in the write refuses it.
- **A summary over sample data only is refused** when it is read, as the report's is. One over a
  mix leaves the sample blocks out of the narrative.

**Write the narrative as a summary, not as typed text.** Your own `text` blocks are for headings,
framing and what no data says ("Q3 was the first quarter on the new pricing"). The paragraph that
reads the numbers back to the person belongs to a summary block. Do not inline it, even when you
have just read the same numbers in `fetch-data`: to the person, typed commentary next to bound
figures looks like the agent typed the numbers in, and it will disagree with them next month.

### Three ways to make a block live

A `binding` that fetches figures has two kinds (the third, `summary`, writes words and is above),
and the `widget` kind covers two different situations, so there are three answers and they are not
interchangeable.

**A `query` binding is the default.** One source, some metrics, resolved on every open. Nothing is
created, nothing has to be cleaned up, and the block is the whole statement of what it shows.
Reach for this first for any block's numbers, charts, tables and bar lists, whatever the format.

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
- a date range pinned per widget with a comparison of its own. A fixed filter on a query is
  `binding.filters`, and a filter the reader moves is a `control`; neither needs a widget
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
  pages=[{ "blocks": [{ "id": "funnel", "type": "widget", "frame": {"x":0.06,"y":0.18,"w":0.4,"h":0.3},
                        "binding": { "kind": "widget", "widget_id": 8814 } }] }]
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
| `action=update_ai_text` | AI text is a comment widget's setting. On a design it is a `text` block with a `summary` binding; see *A summary*. |
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
| a PowerPoint file | editable shapes, tables and native charts; an `icon` stays a vector | a `widget` block becomes a picture |
| a Google Slides deck | the same, with charts that stay editable in Google | 16:9 only, and no `widget` or `icon` blocks at all |

PDF and PNG cannot disagree with the screen, because they *are* the screen. The two writers redraw
each page from the spec, so they are the ones with a cost — and both costs land on `widget` blocks,
which is worth remembering when you are choosing between a `widget` and a `chart` for something
that will be presented from PowerPoint. Google Slides also draws an `icon` as a labelled gap: it
takes pictures from a public URL only, and the glyph is markup the server holds.

## Composing for the format

The three families are read at different distances, and that is the whole of what makes their
composition rules different. Everything above is shared; this is not.

### Slides — read across a room

Six to ten pages for a review. Twenty is a report nobody will sit through. (A replica keeps the
file's page count instead; see *Replicating a file somebody gave you*.)

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
- **The numbers are bound here too.** A slide's metric reads the quarter from its source exactly
  as a dashboard's does. What makes it a slide is the composition, never typed-in figures.

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
  Put the three or four numbers that matter at the top, bound and with `compare` set so their
  deltas draw.
- **A filter at the top when the reader will want to narrow.** One `control` strip in the first
  band, over the source the KPI row reads, reaches every bound block below it. See *A filter*
  under *Groups*. It is the one format where a page filter is the normal shape.
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
                pages=[{ "blocks": [{...the corrected block, same id...}] }]
                remove_block_ids=["stray-caption"]
```

Blocks whose `id` already exists are replaced in place; new ids are appended. The blocks ride in
`pages` with one entry, the same field every other action writes blocks through; a page's other
fields are ignored here, so `layout` can be left off.

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
fit its frame, a pill or a table wider than its frame (neither wraps, so both are cut off), bars given too little room, block budgets, chrome bands, duplicate block ids, a
data-bearing block carrying neither values nor a binding, and a `control` placed where it cannot
work.

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

`generate` saves nothing — keep what it returns and pass its `decisions` to `create`. Pass
`asset` with a file's id (a brand book, a deck to match, a logo or a screenshot) to have the
brand read from it.

Attach a brand with `manage-canvases` `action=update design_system_id=<id>`. Switching it
restyles every page and touches no block.

**Changing an existing brand restyles every design already drawn in it.** When one design needs
its own look, make a new brand rather than editing the shared one.

Two things worth knowing: the `mono` chart palette yields only two separable colours by
construction — pick it only when two is what the charts need. And a brand colour may be any hex,
not only one from the named grid; it is deepened until white type reads on it.

Surface a brand you made as an artifact card in the chat rather than listing its hex values in
prose. The card draws the brand — its name set in its own typeface, on its own page colour, with
its chart palette beside it — and how it looks is the whole of what the person is judging.

## What this cannot do yet

- **Exporting on somebody's behalf.** There is no export tool and there will not be one — the
  person presses the button. See *Sharing and exporting* above for what each one costs.
- **Changing a format.** Every frame was composed against one page shape. Author again in the new
  format.
- **Uploading an image.** `image` blocks take a public `https` URL. A picture inside an attached
  file is placed with `manage-assets action=crop_page`; any other picture needs a URL already.
- **Styling a block in an Office export.** A block's own `style` reaches the browser, the PDF and
  the PNG. The PowerPoint and Google Slides writers draw the brand instead.

Surface a finished design as an artifact card in the chat rather than writing a link to it.

## Common pitfalls

- **A replica condensed into a summary.** Asked to recreate a file, keep every page. The
  composition rules are for documents you decide, not for copies.
- **Describing a design as live while its figures are typed in.** Read `data_blocks` in the write's
  answer and report it. Typed-in figures do not change next month.
- **Copying from the text alone.** The text has no layout and loses which number sits under which
  label. Look at the page with `read-document` `pages`.

- **Figures from a source typed into a block.** You fetched it, so bind it: the block carries the
  `fetch-data` call as its `binding`, not the answer it returned. A typed-in figure shows as "Not
  connected to data" and nothing can refresh it. Inline only what no source reports.
- **Commentary on the numbers typed into a `text` block.** It is a figure in prose, and it goes
  stale with the range. Use a `summary` binding; keep your own text for headings and framing.
- **A summary placed away from what it should read.** On the page it reads the page; inside a
  card it reads only that card. An empty `inputs` from `regenerate_summary` means it read nothing.
- **A whole design inlined because it is a deck or a print.** The format changes the composition,
  not where the numbers come from. Pin the period with the document's `date_range` instead.
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
- **A filter in a deck.** A page `control` is refused on a slide; a presentation has nobody to move
  it. Narrow with a control inside a bound card, or pin the condition in the binding's `filters`.
- **A filter whose source no block uses.** It saves and reaches nothing, and no message says so.
  `control.source` is the id the `binding.sources` on the same page hold.
- **`source` left off a page filter, or written on a card's control.** On the page it is required;
  inside a card carrying a `query` binding it is refused. The message says which you have.
