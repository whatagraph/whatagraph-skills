---
name: designing-pages
type: domain
group: team_workspace_branding
description: Design an HTML page with create-document so that it looks made for its client and its subject, not generated. Covers reports, plans, briefs, proposals, one-page summaries, campaign boards, showcases of ads and videos, menus and price lists, landing pages and small tools. Says where the look comes from (the client's website through view-website, their logo, their ads, their brand guide), how the kind of document sets the form of the page, what makes a page look generated, which of those patterns the automatic check names, and what to do when nothing about the brand can be found. Load it before you write any HTML page. It does not apply to Markdown, CSV, JSON or text files.
required_tools:
  - create-document
optional_tools:
  - tool_name: view-website
    purpose: See the client's website as a person does, with screenshots, the colors and fonts it uses and its logo saved as an image, before you choose the look of a page.
  - tool_name: search-assets
    purpose: Find the client's logo, brand guide, earlier reports and photos in the team library.
  - tool_name: list-assets
    purpose: Browse the files the user attached or the team keeps for the client.
  - tool_name: read-document
    purpose: Read a brand guide or an earlier report the user attached.
  - tool_name: view-creatives
    purpose: Look at the client's real ads, which show their colors, type and photography.
  - tool_name: list-themes
    purpose: Read a report theme, when the page belongs with the client's Whatagraph report.
  - tool_name: manage-assets
    purpose: Publish the logo and the images a page shows, and import an image from the client's website.
---

# Designing pages

A page you write with `create-document` is read by the client, or by the client's manager. It
should look as if someone who knows the client and the subject made it. It should not look like
the page that every generated page looks like.

This skill does not give you a style. A house style, applied to every client, is exactly what
makes generated pages recognisable. The look of each page comes from its client, and its form
comes from the kind of document it is. This skill says how to find both, and what to leave out.

## 1. Find the client's look before you write

Use every source you have, in this order, and stop when you know the look:

1. **What the user gave you.** Colors, fonts, a brand guide, an earlier report or deck, a file to
   follow. Follow it exactly. Read an attached file and look at it before you start.
2. **A saved brand kit.** A memory note named "Brand kit: <client>" from earlier work.
3. **The client's website.** Open it with `view-website`, usually the home page. It shows the
   site in two screenshots, lists the colors with where the site uses them, names the fonts, and
   saves the logo as an image in the conversation. When the user says "use our website", "match
   our brand" or "like our site", this is the step: a report theme or a guess is not the website.
   When you only have the client's name, find the address with web search if you have it, or in
   the client's sources and earlier conversations. Do not guess a domain; ask when you cannot find
   it.
4. **The client's files.** The logo and brand images in the team library (search for "logo",
   the client's name, "brand").
5. **The client's ads.** `view-creatives` shows the ads they run, with their colors, type and
   photography.
6. **A report theme.** Only when the page belongs with the client's Whatagraph report, or when
   nothing above exists. Someone chose it for charts; it may not be the brand.

Before the first line of HTML, write the look down in two or three lines: the background, the
text color, one or two accents and what each one marks, the heading face and the body face, and
how the brand uses photographs and space. Save it as the brand kit note when the client will come
back.

**Take the look, not the website's layout.** A website is built from web parts: a navigation bar,
a hero, buttons, cards and a footer. A report built from those parts looks like a landing page.
Take the colors, the type, the photography and the tone, and use them in the form of the page you
are making.

**Fonts.** A font from Google Fonts can be used directly. For any other font, choose the Google
Font closest in shape (a geometric sans for a geometric sans, a high-contrast serif for a
high-contrast serif) and say which one you chose.

**Logo.** Use the logo `view-website` saved, or the file from the library. Publish it to show it
on a page. Never redraw a logo or set the name in another font as the logo. `shown_on` tells you
which background the logo was made for: a white logo needs a dark background. When no logo file
exists, set the name as plain text in the page's heading face, and tell the user that it stands in
for the logo.

## 2. Let the kind of document set the form

Before you lay anything out, name what the page is in the real world, and follow the conventions
of that kind of document. Different kinds look different from each other, so a menu and a
quarterly report by the same agent no longer look alike.

| The page is | Make it like | Its conventions |
| --- | --- | --- |
| A monthly or quarterly report | A printed report | A title block, sections whose headings are findings, charts and tables with their period and source, numbers inside the sentences that explain them |
| A plan, a brief or a proposal | A document | Numbered sections, plain paragraphs, a table for the schedule or the budget, next steps and owners at the end |
| A summary for a manager | A memo | The answer first, three to five points, one chart at most |
| A campaign or creative board | A presentation board | The work large, one short paragraph beside each piece, nothing else |
| A showcase of ads or videos | A gallery | Each piece at its real shape, a caption under it |
| A menu, a price list, a timetable | The thing itself | What a printed one has, in the client's look |
| A landing page for the client's customers | The client's own website | Its sections, its buttons, its tone |
| A calculator or a small tool | A tool | The inputs and the answer, and nothing around them |

A long report is read from top to bottom. A list of contents at the start helps; app parts do not
(section 3).

## 3. What makes a page look generated

People called generated pages "vibe-coded" because of these patterns. Each one is the default a
model reaches for when nothing else was decided. Leave each one out unless the client's brand or
the request calls for it.

- **Labels in rounded shapes:** pills, badges, tags and chips, above all ones that repeat a
  heading or show a field name ("Archetype: Founder story"). Words belong in sentences or in a
  table. A status is a word in a table column, colored only when the color carries the meaning.
- **A small uppercase label above every heading**, also called an eyebrow.
- **Boxes:** every block in a rounded box with a shadow, and boxes inside boxes. Separate the
  parts of a page with space, a rule or a change of background. A box is for the one thing that
  must stand apart.
- **A row of number tiles** at the top that repeats the brief. A number belongs where it is
  explained.
- **App parts in a document:** a navigation bar fixed to the top, filter chips, tabs for content
  that is read in order, hover effects, a print or export button, a dark mode switch.
- **Decoration:** glows, frosted glass, gradients on text or behind blocks, emoji used as icons,
  colored stripes down the side of cards, blurred blobs.
- **The default stack:** Tailwind's grey and indigo, violet or emerald, set in Inter or the
  system font, when these are not the client's own.
- **Colors without meaning:** a different color for each card or each label.
- **The process left in the page:** "Generated by", "Draft 2", the brief's own words as section
  titles, notes to yourself.

After each save, the check of `create-document` lists the patterns it finds under
`template_patterns`, with examples. Change each one before you reply, unless the brand or the
request calls for it.

## 4. When nothing about the brand can be found

Sometimes there is no website, no logo, no ad, no theme, and the user does not answer. Do not fall
back on the default stack. Decide the look instead:

- **Form.** The kind of document from section 2 already gives the page its structure.
- **Type and color from the subject and the reader.** Ask what a good designer working in the
  client's industry would choose. A law firm's annual report, a bakery's menu and a game studio's
  media kit do not share a palette or a typeface. Choose one pair of faces and two or three colors,
  each with one role, and keep to them.
- **Restraint.** One accent, no decoration and a plain structure. A plain page that is set well
  looks made. A decorated page looks generated.
- **Say it.** Tell the user in the reply which look you used, and that their website, logo or
  brand guide would let you match the brand.

## 5. Before you reply

- Fix every problem the check lists, and change every template pattern it names unless the brand
  calls for it.
- Every fact on the page comes from the request, the client's data or a page you read. Do not add
  an email address, a phone number, a time saved, a count of integrations, a percentage or a quote
  that nobody gave you. A figure you work out from the numbers you were given is fine when the page
  shows how.
- Look at the two screenshots. Does the page look like the kind of document it is? Would the
  client recognise their own brand in it? Is anything on the page that its reader does not need?
- At phone width nothing scrolls sideways, and a wide table scrolls inside its own box.
