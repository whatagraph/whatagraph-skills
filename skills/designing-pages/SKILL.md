---
name: designing-pages
type: domain
group: team_workspace_branding
description: Design an HTML page with create-document, or a website or web app built on the team computer, so that it is made for its customer, in their look and in the form their use of it needs, and does not look generated. Covers reports, plans, briefs, proposals, summaries, campaign boards, showcases of ads and videos, dashboards, menus and price lists, landing pages, sign-up and booking sites, and small tools. Says where the look comes from (the customer's website through view-website, their logo, their ads, their brand guide, what they already make), how to decide what the page should be and do, which patterns every generated page shares and which of them the automatic check names, what to do when nothing about the brand can be found, and how to check every fact. Load it before you write any HTML page or the first page of a site. It does not apply to Markdown, CSV, JSON or text files.
required_tools:
  - create-document
optional_tools:
  - tool_name: view-website
    purpose: See the customer's website as a person does, with screenshots, the colors and fonts it uses and its logo saved as an image, before you choose the look of a page.
  - tool_name: search-assets
    purpose: Find the customer's logo, brand guide, earlier reports and photos in the team library.
  - tool_name: list-assets
    purpose: Browse the files the user attached or the team keeps for the customer.
  - tool_name: read-document
    purpose: Read a brand guide or an earlier report the user attached.
  - tool_name: view-creatives
    purpose: Look at the customer's real ads, which show their colors, type and photography.
  - tool_name: list-themes
    purpose: Read a report theme, when the page belongs with the customer's Whatagraph report.
  - tool_name: manage-assets
    purpose: Publish the logo and the images a page shows, and import an image from the customer's website.
---

# Designing pages

A page you write with `create-document`, or a site you build on the team computer, is made for one
customer: an agency's client, the client's manager or the client's own customers. It should look
like that customer's, and work the way they will use it. It should not look like every other
generated page, and it should not look like the pages you made for other customers.

This skill gives you no style, no layout and no structure. A house style, a fixed outline or a
default form for each kind of document is exactly what makes generated pages look alike, whoever
they are for. The look of each page comes from its customer, and its form comes from what the
customer needs and wants from it. This skill says how to find both, and which patterns to leave out.

## 1. Find the customer's look

Use every source you have, in this order, and stop when you know the look:

1. **What the user gave you.** Colors, fonts, a brand guide, an earlier report or deck, a file to
   follow. Follow it exactly. Read an attached file and look at it before you start.
2. **A saved brand kit.** A memory note named "Brand kit: <customer>" from earlier work.
3. **The customer's website.** Open it with `view-website`, usually the home page. It shows the
   site in two screenshots, lists the colors with where the site uses them, names the fonts, and
   saves the logo as an image in the conversation. When the user says "use our website", "match
   our brand" or "like our site", this is the step: a report theme or a guess is not the website.
   When you only have the customer's name, find the address with web search if you have it, or in
   the customer's sources and earlier conversations. Do not guess a domain; ask when you cannot find
   it.
4. **The customer's files.** The logo and brand images in the team library (search for "logo",
   the customer's name, "brand").
5. **The customer's ads.** `view-creatives` shows the ads they run, with their colors, type and
   photography.
6. **A report theme.** Only when the page belongs with the customer's Whatagraph report, or when
   nothing above exists. Someone chose it for charts; it may not be the brand.

Before the first line of HTML, write the look down in a few lines: the background, the text color,
the accents and what each one marks, the heading face and the body face, how the brand uses
photographs, space and motion, and its tone. Save it as the brand kit note when the customer will
come back.

The website's own parts (a navigation bar, a hero, buttons, cards, a footer) belong on a page that
is part of the customer's site. For any other page, take the look and the tone, and let the page's
use decide its parts (section 2).

**Fonts.** A font from Google Fonts can be used directly. Most brand fonts are not on Google Fonts:
they come from Typekit, from the brand's own server or from a paid foundry. For such a font, look
at it in the screenshot and describe it before you choose:

- its kind: a geometric, grotesque or humanist sans, a slab, or an old-style, transitional or
  high-contrast serif;
- its width (narrow, normal or wide) and how tall its lowercase letters are;
- its ends and corners: round or square, soft or sharp.

Then choose the Google Font that shares those traits, and say in the reply which font stands in
for which. Do not reach for the same face for every brand. Plus Jakarta Sans, Inter and Poppins
are what generated pages use when nothing was decided, so choose one of them only when the
brand uses it or its traits really match.

**Logo.** Use the logo `view-website` saved, or the file from the library. To show it on a page,
load the `whatagraph-assets` skill and publish the logo with `manage-assets`: a publish made
before that skill is loaded is refused. Never redraw a logo or set the name in another font as the
logo. `shown_on` tells you which background the logo was made for: a white logo needs a dark
background. When no logo file exists, set the name as plain text in the page's heading face, and
tell the user that it stands in for the logo. When `view-website` cannot open a real customer's
site, do not invent a mark or a color for them: say so, and ask for the logo or the brand guide.

## 2. Decide what the page should be and do

No kind of page has a fixed form. A monthly report can be a long read, a few screens to click
through in a meeting, a dashboard with a view per channel, one chart the reader can play with, or a
story that unfolds as it scrolls. A plan can be a document, a timeline, or a budget the client can
move around. Decide for this customer, from:

- **The request.** What they asked for, in their words. When they name a form ("a one-pager",
  "something to click through in the meeting", "an app for our staff", "keep it simple"), build that.
- **How it will be used.** Read once and filed, shown to a room, opened on a phone, explored to
  answer the reader's own questions, used every week as a tool, or sent on to the customer's own
  customers. Each of these wants a different page.
- **What the customer already makes and likes.** Their earlier reports, decks and sites, an
  attached example, a saved note about their taste. A brand whose site moves and plays can have a
  page that does. A customer who reads dense tables may want density rather than space.
- **What the content is.** Numbers over time, a comparison, a place, a product, a schedule, a
  choice between options, a set of ads: each has forms that show it best, and a table is only one
  of them.

Then use what a web page can do whenever it serves that use, and only then: charts drawn to scale
that show their values under the pointer, a switch between channels or periods, a slider that
recomputes a budget split, a table the reader can sort, ads and videos that play where they sit,
motion that shows a change happening, a view of a product or a place in 3D. Every control must
change something the reader wants to see. A page read once from top to bottom is one of these
choices, not the default.

When the request leaves the use open and the person is in the conversation, you may ask one
question about it. Otherwise decide, and say in the reply what you made and why it suits them.

Give each page something only this customer and this subject would have: their own data in a form
made for it, their products, their places, their words, their photographs. Pages for two customers
should not share a layout.

**What the preview of a document allows.** Scripts load from cdnjs.cloudflare.com and
cdn.jsdelivr.net, which serve the common chart, 3D and animation libraries. Fonts load from Google
Fonts. The page cannot fetch data files, so put the data in the page. Motion may draw things in or
move them, but every text and number must also be readable when it does not run: in a printed copy,
for a reader who turned motion off, and in the check's screenshots. A site on the team computer can
install what it needs instead.

## 3. What makes a page look generated

People called generated pages "vibe-coded" because of these patterns. Each one is the default a
model reaches for when nothing else was decided, so it makes pages for different customers look
alike. Leave each one out unless the customer's brand or the request calls for it.

- **The same page for every customer:** a centered column with a title block, numbered sections
  with a rule under each heading, a table in every section and a footer line. However well it is
  set, it is a template.
- **Labels in rounded shapes:** pills, badges, tags and chips, above all ones that repeat a
  heading or show a field name ("Archetype: Founder story"). A status that is a word belongs in
  the sentence or the table, colored only when the color carries the meaning.
- **A small uppercase label above every heading**, also called an eyebrow.
- **Boxes:** every block in a rounded box with a shadow, and boxes inside boxes.
- **A row of number tiles** at the top that repeats the brief. A number belongs where it is
  explained.
- **Controls that do nothing for the reader:** tabs or filters that hide content the reader needs
  all of, a print or export button, a dark mode switch, cards that lift on hover and lead nowhere.
- **Decoration:** glows, frosted glass, gradients on text or behind blocks, emoji used as icons,
  colored stripes down the side of cards, blurred blobs, motion that only moves.
- **Startup-template parts on a site:** a small tag next to the name ("Run club", "Beta"), a
  pill above the headline, a row of round counters ("450+ runners", "3x weekly") that nobody gave,
  and a success message with confetti or an emoji.
- **The default dark theme:** a near-black navy page with one neon accent (lime, emerald, violet),
  glowing buttons and gradient stripes, when the customer's brand is not dark.
- **The default stack:** Tailwind's grey and indigo, violet or emerald, set in Inter or the
  system font, when these are not the customer's own.
- **Colors without meaning:** a different color for each card or each label.
- **The process left in the page:** "Generated by", "Draft 2", the brief's own words as section
  titles, notes to yourself.

After each save, the check of `create-document` lists the patterns it finds under
`template_patterns`, with examples. Change each one before you reply, unless the brand or the
request calls for it.

No check runs on a site you build on the team computer. There, take a `browser-screenshot` of each
page you built and go through this list against it yourself, one item at a time, and change what
you find before you reply.

## 4. When nothing about the brand can be found

Sometimes there is no website, no logo, no ad, no theme, and the user does not answer. Do not fall
back on the default stack, and do not fall back on a plain page either. Decide the look:

- **From the subject and the reader.** Ask what a good designer working for this customer's
  industry and readers would choose. A law firm's annual report, a bakery's menu and a game
  studio's media kit share no palette, no typeface and no shape. Choose the faces, the colors and
  what each color marks, and keep to them. A fictional or new brand is no exception: the faces
  generated pages fall back on (Plus Jakarta Sans, Inter, Poppins) and a dark page with a neon
  accent are what nobody chose, so they are not a choice for the subject either.
- **The form still comes from section 2.**
- **Say it.** Tell the user in the reply which look you chose, and that their website, logo or
  brand guide would let you match the brand.

## 5. Before you save, and before you reply

**Check every fact before you save.** A page written to sound complete fills its gaps with
plausible content, and the reader cannot tell it from what they gave you. So read your page once
against the request before the first save, and again before saving any change that adds text. For
every number, name, date, address, source and claim, find where it came from:

- the request or a file the user gave;
- the customer's data, fetched in this conversation;
- a page you read in this conversation.

Delete whatever has none of these, or ask the user for it. A figure you work out from the numbers
you were given stays when the page shows how it was worked out. What gets added most often: a
budget split nobody gave, named retailers, markets or partners, benchmarks and targets, tactics
and plans nobody asked for, reference numbers, an office address or phone number, time saved,
counts of integrations or clients, a "Source:" line naming tools nobody used, a "Generated on"
date, "Confidential" labels, and praise such as "above industry benchmarks". On a site, also
member counts, testimonials, opening times, places and team names, and a message that says
something happened when nothing does it, such as "we've sent you a welcome email" from a form that
sends nothing. When a page needs content nobody gave, such as the text of an about section, write
it from what you were told, or leave a short, plain placeholder that says what belongs there.

**After each save** (on the team computer, after each change, with a screenshot of each page):

- Fix every problem the check lists, and change every template pattern it names unless the brand
  calls for it. On the team computer, go through the list in section 3 yourself.
- Look at the screenshots. Does the page do what this customer needs from it? Would the customer
  recognise their own brand in it? Would a page you made for another customer look the same? Is
  anything on the page that its reader does not need?
- Every control you built works, and at phone width nothing scrolls sideways.

**In the reply,** say what you made and why it suits this customer, and name what stands in for
the brand: a Google Font in place of the brand's own font, a name set as text in place of a logo,
or the look you chose when nothing was found.
