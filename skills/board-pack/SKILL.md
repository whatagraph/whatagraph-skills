---
name: board-pack
type: domain
group: computer
description: Prepare a long pack alone from one request, such as a board pack, a quarterly business review, a market review or a competitor study with thirty or more slides, a model, a forecast, web research and screenshots. Covers how to work in stages over several turns and continue without anybody present, where to keep state, how to research competitors and benchmarks, the structure of the deck and the workbook, and the checks before delivery. Load it before team-computer and team-browser for such a request.
required_tools:
  - computer-exec
optional_tools:
  - tool_name: computer-job
    purpose: Run the mix model, the build of the files and the render in the background.
  - tool_name: browser-navigate
    purpose: Open competitor and publisher pages.
  - tool_name: browser-screenshot
    purpose: Save a clean picture of a page on the team computer for the deck.
  - tool_name: computer-export
    purpose: Deliver the finished deck and workbook.
---

# Board pack and other long packs

Load `team-computer` and `team-browser` as well, each in its own step: a step's tool output is
limited, and two skills loaded in the same step arrive cut off. This skill says how to run the
whole job; those two say how each tool and helper works.

A pack of thirty or more slides with a model, a forecast, research and screenshots is several
hours of an analyst's work. You do it alone, from one request, without anybody present. It does
not fit one turn, and it is not meant to: plan it as stages from the first minute.

**Turns.** A turn that uses the computer or the browser ends after about ten minutes, and the
platform tells you when the time is nearly over. Work in stages of about eight minutes. At the end
of a stage, before any warning: (1) write to the scratchpad what is done, which files hold it and
what comes next, (2) make sure a next turn will start, (3) end the turn with two or three plain
sentences on what is done and what you do next. A next turn starts by itself when a background
job of this conversation is still running or finished during this turn: its completion message
opens the next turn. Otherwise create a wakeup with `manage-schedules` (`action: create`,
`wait_minutes: 1`, `mode: continue_this_conversation`, and a `prompt` that says where to resume
and where the state is). Never create both, never poll, and never ask the person whether to
continue: the request already said so. Ask nothing that a careful analyst would decide alone.
When a tool result carries a SYSTEM NOTE about the time or the steps left in this turn, the stage
ends there, whatever you were in the middle of: your next call is `write-scratchpad`, the one
after it `manage-schedules`, and then you answer in two sentences. One more look at a slide or one
more page costs the turn, and a turn that is cut off schedules nothing. Deliver the files only in
a turn that has time left for it: checking, exporting both files and the final answer need about
three minutes, so when less is left, continue in the next turn.

**State lives in files, not in your memory.** The conversation is compacted between turns, so a
number or a fact that is only in an earlier message is lost. Use one project folder, for example
`/team/<client>-board-pack-<yyyy-mm>/`, with `data/` (every fetched frame as CSV), `shots/`
(screenshots), `charts/`, `notes/facts.json` (research facts, each with `source_url` and
`read_on`), `notes/progress.md`, `build_workbook.py` and `build_deck.py`. Every later stage reads
what it needs from these files. The plan (`write_plan`) holds the stages, and the scratchpad holds
the folder path and the next step. Time is the scarce thing in a turn, so update the plan once per
stage, not after every page or file, and do not read the plan back right after writing it. Put
several independent commands into one script instead of one command per call.

**The mix model.** A marketing mix model is fitted on the whole business outcome per week (all new revenue, all
orders), with one spend column and, when there is one, one impressions column per channel. The
revenue or the conversions that the ad platforms attribute to themselves are not that outcome:
they leave no baseline, and the platforms count the same sale more than once. Look for a source
that holds the business result (sales, new business, orders, a CRM or a shop) before you settle
for platform numbers, and show the platforms' own claim beside the model's as a finding.
Whether the model can be trusted is answered by `mmm.validate(frame, channels, out_dir=...)`: it
refits with a fifth of the weeks held out at random and says how well the model predicts them
(`verdict` is "holds", "weak" or "fails", `reading` is the sentence to say it with, and
`expected_vs_actual.csv` is the chart). Do not hold out the last weeks as one block: a mix model
explains the past and is not a forecast, so that test fails for a reason that says nothing about
the channels. Run `fit` and `validate` in the same background job. The baseline follows trend and
season by itself (`knots="auto"`). `mmm.curves_chart(result, path=...)` draws what each channel
returns as its spend grows, with a dot at today's spend: a curve that is flat at the dot is a
channel where more money no longer pays.

**Stages that work.**

1. Frame and data. Load the skills you need, write the plan, find the client's sources, fetch
   the history to `data/` (daily rows, every channel, and the source that holds the business
   result). Take the whole history, not a round start date: ask for five years back in one fetch
   and see where the rows begin, because a mix model wants two years or more and a forecast wants
   every season it can get. Say how fresh the data is. Write the mix model script (`mmm.fit`, `mmm.validate` and
   `mmm.curves_chart` in one script) and start it as a background job. Do not wait for it:
   continue with the research while it runs.
2. Competitors in the browser. For each competitor open the home page, the pricing page and one
   product or feature page. On each page read the text you need with `browser-extract`, then take
   the picture with `browser-screenshot` (`save_to`, `clean: true`; add `height: 1800` for a
   pricing table that is below the first screen). After each competitor append its facts to
   `notes/facts.json`: who it is for, the headline it leads with, plans and entry price with what
   the price includes, how it charges (per client, per source, per user), what it says about AI,
   proof it shows (customer logos, review scores), and anything that changed recently. Write the
   notes from a script file that you save with `computer-write-file` and run, never through
   `python3 -c "..."`: the shell removes every `$` amount from such a command ("$44/mo" is saved as
   "4/mo", "$5.42" as ".42") and nothing fails. Copy each price as the page states it, with its
   currency sign and its billing period. Four or five competitors fit one turn. A site that blocks the browser or shows a challenge page
   ("Just a moment", "Verify you are human") is noted as not readable and skipped; never put a
   challenge page in a deck.
3. Industry, benchmarks and news, read from pages you open. This is a stage of its own, and it
   is research, not recall: what you remember about benchmarks, market sizes and announcements is
   out of date and often wrong, and an address written from memory is old or does not exist. Do
   not type a page's address from memory: start from a results page in the browser
   (`https://duckduckgo.com/html/?q=google+ads+benchmarks+2026+b2b+software` or
   `https://www.bing.com/search?q=...`) or from web search, pick the current page of the original
   publisher, then open that page in the browser, read the figure
   there with `browser-extract`, and save its picture like a competitor page. Look for: benchmarks
   for the client's channels and industry (cost per click, click rate, conversion rate, cost per
   lead or per trial), the size and the direction of the market, and what each competitor
   announced in the last months (their own blog, changelog or press page is on their site, which
   you may already open). Write every fact to `notes/facts.json` with `source_url`, the publisher,
   the date of the page and `read_on`. Aim for eight to twelve source pages. A site that is not
   allowed or does not load is skipped; never fill the gap from memory.
   **What was not read does not enter the pack.** No benchmark, market figure, news item or date
   without a page you opened in this work. A `quote` slide shows words you read on a page, word
   for word, with its address; never compose a quote or an attribution. A number that comes to
   mind with a publisher's name attached ("WordStream says 5.34") is memory, not research, however
   sure it feels: it enters the notes only after you have read it on the open page. End the stage
   with `python3 -c "from wgviz import research; research.check('/team/<project>')"`: it holds
   every fact in `notes/*.json` against the pages that were opened and names each fact whose source
   was never opened or has no address, and each value that the shell damaged (an amount with
   no currency, or one that starts at its decimal point). Open those pages, find a page that does
   open, or take the fact out; write a damaged value again from the page text; build the benchmark, market and news slides from `research.read(folder)`, which
   returns only the facts that were read. The file check runs the same comparison on the notes and
   on every link in the deck, and the files are not delivered while it finds something. When a
   figure cannot be read anywhere, the pack says so ("no current public benchmark could be read
   for LinkedIn") instead of showing a number: a gap is honest, a recalled number is not.
4. Analysis. Read the finished model (`mmm.load`), its validation and its curves. Build the
   performance tables, the 13 week forecast, the comparison with the benchmarks you read and the
   comparison of the platforms' own claims with the model. Draw every chart to `charts/` (expect
   fifteen to twenty five). Keep every figure in one dictionary that both builders read
   (`notes/figures.json`). Two rules of reading: the return of marketing is the model's
   incremental revenue divided by spend, never all revenue divided by spend, because revenue that
   would have come anyway is not a return on the budget; and one chart shows one measure, so a cost
   per click of 3 and a cost per trial of 700 go into two charts (`chart_grid`) or a table, never
   onto one axis where the small one disappears. A chart placed on a slide that has a title is
   drawn without a title of its own.
5. Build, look, check, deliver. Write `build_workbook.py` and `build_deck.py` as files and run them
   (as a background job when they need more than a minute; the render of a long deck does). A fix
   is then an edit of one line, not a rewrite. `deck.preview(dir)`, read every sheet, fix, then
   `python3 -m wgviz.verify` on both files until they are clean, then `computer-export` both.
   Look at the contact sheets, not at forty single pages: open a single page only to check
   something a sheet shows. A screenshot that shows a blank, unstyled or half-loaded page, a
   challenge page or a pop-up is taken out, and the page is described in words. The sources slide
   and the sources sheet come from `wgviz.images.pages_read(project_folder)`, which lists every
   page that was opened and captured, so nothing is retyped and nothing unread is cited.

**The deck of a board pack** (35 to 45 slides). A board reads the first three slides and looks at
the rest, so: title, `agenda`, `summary` with the answer and its reasons, `kpis`. Then one part
per question, each opened by `section`:

- Performance (5 to 8 slides): spend, outcome and efficiency by channel and over time, pacing of
  the current month, what changed against the previous period.
- What marketing really adds (6 to 9): what the model is in two sentences, `waterfall` of the
  baseline and each channel, return per euro with 90% ranges (`bar` with `intervals`), the
  response curves, the platforms' claim beside the model's, the validation (actual against
  expected with the held-out weeks), the recommended reallocation as a table, and its limits.
- The next 13 weeks (2 to 3): forecast with its range, what it means against the target.
- Market and benchmarks (4 to 6): us against published benchmarks (`grouped_bar` or `ranking`),
  the market's direction, `timeline` of the news, a `quote` when a source says it better.
- Competitors (12 to 16): three `gallery` slides that show the pages you captured side by side
  (the home pages, the pricing pages, the product or AI pages, up to six on each, the most
  important competitors first), a `matrix` of who offers what (every
  cell from your notes of the page, "us" highlighted), a `ranking` of entry prices made comparable
  (the same number of clients or sources for everyone, and say which), then one profile per
  competitor that matters most (four or five, never more): `screenshot(path, facts=[...])` with the same
  five or six labels for each (who it is for, what it leads with, entry price and what it
  includes, how it charges, what it says about AI, what it means for us), and one closing slide
  on where we stand. The remaining competitors get a row in the matrix and the workbook and their
  pages appear in the galleries or in an appendix gallery, so that nearly every page you captured
  is shown once. No layout is used more than three times in a row.
- What to do (2 to 3): `decisions` with two to four decisions, each with the number it moves and
  that number's period, what it costs or puts at risk, the evidence in a sentence, an owner and a
  date. Before you write them, read your notes of our own site again: do not ask the board to
  build what our site already offers (say what exists and what the decision adds), and do not
  tick a capability for us in the matrix that our site does not show. A recommended budget is
  compared with the spend of the last 13 weeks, not only with the average of the modelled period.
  Then next steps as a `timeline`.
- The demonstration-data note, when the data is demonstration data, stands on the summary slide
  or the key numbers slide as one small line, where a reader who stops early still sees it.
- Appendix: method and data notes (what is measured, what is modelled, what the model cannot
  support, what is demonstration data, how you scored anything you scored yourself), and
  `sources` from `images.pages_read`.

The title of a slide is its finding ("Review sites return the most per euro"), not its topic
("ROI by channel"), in at most 70 characters so it stays on one line. The size of the word
matches the size of the number: +2.7% is "steady", not "strong". An estimate "suggests" or
"estimates"; it never "proves" or "confirms". The text beside a chart says what to conclude
(`takeaways=[...]`), it does not repeat the values the chart already shows. A table on a slide has
at most six columns and eight rows; the full table is in the workbook. A deck helper prints a
`WGVIZ NOTE` when it does not use something you passed (a key it does not read, takeaways that do
not fit, a table set too small): read the output of the build and fix every note.

**Two checks hold the pack to what was read and computed**, and the files are not delivered
while they find something, so work with them from the start. (1) The browser saves the text of
every page whose picture you save, and `research.check(folder)` holds the first price of every
note about a competitor (keys that speak of a price, a plan or a cost) against the text of that
competitor's pages: a price that is on none of them was recalled, not read. Write the price as the
page states it (its own currency, its plan, its billing period) and keep a converted or computed
amount in a separate field such as `comparable_monthly_eur`. (2) Every amount in the deck's text
(money, and any number of a thousand or more) must be in `notes/figures.json`, in the model's or
the forecast's result files, or in the chart or table of the same slide. So compute every amount
you want to say in the analysis script, store it in `figures.json` and build the sentence from
there; an amount you cannot compute from the data is not said.

**What a slide says is what its picture shows.** Write a competitor's facts right after reading
its pages, from the text you just extracted, never from what you know about the company: prices
and plans change, and the price in a profile is the price visible in the picture beside it (say
which plan and which billing). The picture of a profile is the page its facts come from. Before
you write a chart's title, look at the numbers it plots: the title must be true for every bar it
covers, and when one bar says the opposite the title says that too ("cheaper clicks on three of
four channels; LinkedIn costs more"). "Grew steadily" needs a line that rises. Changes are written
with `format_value(x, "signed:€")`, which gives "+€218,000" and "-€198,656". The mix model's
summary sentence is `result["reading"]`: use it instead of writing your own, so that all revenue
is never called the revenue marketing made.

**One meaning per word, one period per number.** "Return" is the model's incremental revenue
divided by spend, and nothing else is called return; all new revenue divided by spend, if shown at
all, is "new revenue per euro of spend" and is never the headline. Every amount names its period
on the slide where it stands ("over the 88 modelled weeks", "in the next 13 weeks", "a quarter"),
and a gain from the model that covers the whole modelled period is brought to the period of the
decision (`result["reallocation"]["expected_change_per_13_weeks"]`) and called an estimate, with
the optimiser's limit said once (`["constraint"]`). A comparison with last year or last quarter is
computed from the data in the same script and names both periods; never type a growth figure. A
month or a week that is not complete is left out of a trend chart or marked as partial. The
forecast is named by its dates ("14 September to 13 December"), not by a quarter it does not match.
Model internals stay in the appendix in plain words (say "the four runs of the model agree", not
"R-hat 1.006"). No more than two text-only slides in a row. Every screenshot slide names its
address and the day it was captured. Add `notes()` on the slides a presenter will speak to.

**What an audit of a delivered pack found wrong, so check these before you build.**
- One reporting period: the complete weeks the model uses. Every total, share, cost per trial,
  segment table and platform reported value is computed for that period from the weekly or daily
  frame, never taken from the totals a data tool printed (they cover other days). The same measure
  has one value in the whole pack.
- A monthly trend is grouped by calendar month from the daily frame, without the month that is
  not complete. Weeks grouped into months give months of four or five weeks and a false zigzag.
- A figure in another currency stays in its currency. Convert only with a rate you read in this
  work (the European Central Bank's euro reference rates page), record the rate and its date in
  the notes, and state both where the converted figure stands. Never assume a rate.
- Compare like with like. A search benchmark is held against our search campaigns only (filter
  the campaign level data), not the whole account with display in it; a cost per lead is not a
  cost per trial. Say what each side measures, and let the title claim only what survives that.
- The shift and the gain of a reallocation are two numbers: the euros moved between channels per
  13 weeks, and the revenue the model expects from it. Compute both; give the gain as rounded.
- A holdout test shows that the model predicts revenue. It does not show that the split between
  baseline and channels is right. Write "estimates" with the range beside every channel return;
  never "proves", "verified" or "confirmed".
- With under three years of weekly history the forecast carries no season. Put beside it what
  the same weeks brought a year before and how the last 13 weeks compare with the year before,
  and say when the forecast is therefore likely cautious. Forecast spend is an assumption.
- An entry price is the price of a plan, not of an add-on or a pack. Before writing that we lack
  something, search the saved text of our own pages for it (`grep -il mcp shots/whatagraph-*.txt`).
- In the workbook a count, a rate and a return never carry the euro format, and a click cost
  shows two decimals.

**The workbook** (12 to 16 sheets) carries every number of the deck: `cover`, contents
(`add_index` last), key numbers, channel performance, monthly trend, the weekly frame the model
was fitted on, model results with ranges, response curves, validation, reallocation, forecast,
benchmarks with their sources, competitor facts, pricing, news, sources with links. Native charts
next to the main tables.

**The answer at the end** names the two files, the answer to the person's question in one
sentence, the three to five findings that matter, what to decide, and what limits the pack has
(which data is demonstration data, which sites could not be read). No paths, no tool names.

