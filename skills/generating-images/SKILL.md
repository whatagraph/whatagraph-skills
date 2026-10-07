---
name: generating-images
type: domain
group: team_workspace_branding
description: Create and edit any visual with generate-image as a finished design. Ads and their placement sets, social posts and carousels, offer posts, flyers, posters and menus, report and slide covers, email headers and banners, infographics, product and lifestyle photos, illustrations, 3D and typographic graphics, logo concepts, photo edits, resizes and translations. Use whenever the user wants something visual made or changed. For a full campaign built on the client's brand and ad results, also load `creating-ad-campaigns`. Do not use it for charts of real data, or to stand in for a real photo, screenshot, place, product or person.
required_tools:
  - generate-image
optional_tools:
  - tool_name: manage-assets
    purpose: Publish a generated image so a report, theme, HTML document or canvas can show it, or import an outside image (a logo, a product photo) to use as a reference.
  - tool_name: list-assets
    purpose: Find the client's logo, product photos or earlier generated images to use as references.
  - tool_name: search-assets
    purpose: Find a reference image in the team library by description.
  - tool_name: view-creatives
    purpose: Look at the client's existing ads to learn their visual style, or pass one as a reference for a variant.
  - tool_name: manage-widgets
    purpose: Put a published image into a report image widget.
  - tool_name: list-themes
    purpose: Read the brand colors, fonts and logo of a report theme.
  - tool_name: create-document
    purpose: Build an HTML page or board that shows published images.
---

# Generating images

Tool covered: `generate-image`.

`generate-image` renders whatever the prompt specifies. That includes photographs, illustration in any technique, 3D renders and pure typography. It also renders complete layouts: exact headlines, prices, buttons, logos and grids. It keeps a logo, a product or a character from a reference image, edits an image reliably, and re-lays out a design for another shape.

It does not decide anything. A vague request returns a vague picture: a stock photo with no message, or generic AI art. A full creative spec returns work that reads as if a top agency made it. **You are the creative director. Decide the idea, the style, the layout and the exact words, then write them down so that nothing is left to guess.**

## Use this when

The user wants something visual made or changed:

- An ad: a concept, a set of placements, A/B variants, an offer post, a translation, one version per location.
- A social post, a carousel, a story, a creator-style native ad.
- A flyer, a poster, a menu, an invitation, a card, a certificate.
- A report cover, a slide cover, a section banner, an email header, a website hero.
- An infographic or a results post, an explainer illustration, a comic, a map.
- A product or lifestyle photo, a mascot, logo concepts, a packaging mockup, a moodboard.
- An edit of an existing image: new background, cut-out on white, relit, extended, restyled, combined.

## Do not use it when

- **The image would stand in for something real.** Never generate a photo of a real property, a real event, a competitor's post, a platform screenshot, a real person or a product you have not seen. Find the real image (the client's uploads, `view-creatives`, an official source imported with `manage-assets`) or say you cannot.
- **The picture is a chart of real numbers.** Build a widget or a canvas chart. A generated chart cannot be checked or updated, and its bars are not guaranteed to scale. A results post that states a few numbers in large type is fine.
- **The request names a real, identifiable person** the user has not supplied a photo of. See "Rules you must not break".

## Deliver a finished design, not a picture

When the image carries a message (an ad, a post, a flyer, a cover, a banner with copy), the image is the deliverable. It holds the brand, the copy and the call to action, laid out on a grid. Write a creative spec with these six parts:

```
{Format}, {aspect ratio}, for {brand}, {what it is for}.
Brand system: logo {from image N | a wordmark '<name>' in <type style>}; colors {#hex for background, text and accent}; type {headline style; body style}.
Layout: {zone by zone, top to bottom: what sits where, alignment, relative size}.
Imagery: {the photo, illustration or render: subject, setting, technique, light, materials}.
Copy, exactly: headline '...'; support '...'; proof points '...'; offer '...'; button '...'. No other text.
Finish: a finished design as delivered by a top creative agency. Crisp, perfectly kerned typography on a clear grid, consistent margins, every word spelled exactly as given. Flat and full-bleed: no mockup, no frame, no app interface, no watermark.
```

An example that produced a production-ready feed ad:

```
Paid social feed ad, 4:5, for Northpeak, an outdoor jacket brand.
Brand system: logo from image 1, in off-white; colors forest green #1F3A2E, signal orange #E8622C, warm off-white #F4F1EA; headlines in a heavy condensed sans, body in a clean grotesk.
Layout: full-bleed photo; the logo top-left; the lower third fades to forest green behind the copy; headline in large off-white condensed caps; a feature line under it; a rounded signal-orange button bottom-right.
Imagery: a woman in her thirties hiking a misty ridge as the first snow falls, wearing exactly the jacket from image 2, three-quarter view, 35mm lens, cold overcast light, real fabric texture.
Copy, exactly: headline 'Built for the first snow'; feature line 'Waterproof 20K · Recycled insulation · 480 g'; button 'Shop the collection'. No other text.
Finish: a finished design as delivered by a top creative agency. Crisp, perfectly kerned typography on a clear grid, consistent margins, every word spelled exactly as given. Flat and full-bleed: no mockup, no frame, no app interface, no watermark.
```

What each part prevents:

| Part | Without it |
|---|---|
| Brand system with a role for each color | Off-brand colors, random fonts, a different logo each time. |
| Layout by zone | Everything centered, and the copy fights the image. |
| Copy, exactly, ending with "No other text" | Invented taglines, prices, codes and misspellings. |
| The finish line | A mockup, a framed print, a phone screen, a layout that looks unfinished. |
| A headline of 7 words or fewer | Squeezed or wrapped text. Long copy belongs in the ad's caption, not in the image. |
| The asset named, not the app ("vertical 9:16 ad", not "Instagram Story") | "Sponsored" labels, like buttons, usernames. |
| A fictional product never named after a real brand | The real brand's product and badge. |
| Full sentences that say what the image is for | A keyword soup that the model reads literally. |
| A named type style for each text ("heavy condensed sans, all caps") | A default font that looks like a template. |

For an image without copy (a background, a hero photo under an HTML title, a report banner whose title must stay editable), drop the copy line and end with "No text, letters or logos."

## Choose the mode and the style on purpose

First decide the mode, because it sets the layout:

- **Performance** (sales, sign-ups, offers): the product dominates, the headline carries the benefit or the offer, a proof point appears (a number, a rating the client can stand behind), the button is high-contrast, and the grid is tight.
- **Editorial** (brand, launches, covers): one strong image, five words of copy or fewer, generous white space, display or serif type, and a small logo.

Then pick the style. Follow the brand's existing material when it has any: its ads (`view-creatives`), its theme (`list-themes`), its website. A style the user names always wins. Otherwise pick the style that fits the brand, the audience and the placement:

| Style | Fits | Put in the spec |
|---|---|---|
| Photographic: lifestyle, product, editorial | Most consumer brands, fashion, food, travel, beauty | Subject and setting, lens, light, materials, "natural skin texture", "not a 3D render" |
| Product-led graphic | Offers, launches, e-commerce | The product as a cut-out, color blocks, the offer or price as the hero |
| Typographic | Sales, announcements, bold brands | The grid, type style and sizes, no imagery |
| Illustration | Events, local businesses, explainers, friendly brands | The technique (flat vector, risograph, linocut, watercolor, hand-drawn, isometric), line and texture |
| 3D | Apps, fintech, playful brands | The material (glossy, jelly, clay), the lighting, a solid background color |
| Editorial or magazine | Covers, reports, premium brands | A display serif, generous margins, a photo inset |
| Creator or native | Social ads that must not look like ads | Phone-camera framing, caption boxes, imperfect light; no app buttons or usernames |
| Infographic | Results, how-tos, B2B posts | Numbered rows, simple line icons, one accent color for the numbers |

Avoid the defaults that look like generic AI art unless the brand uses them: abstract waves and ribbons, glowing particles, holograms, floating dashboards and neon gradients.

## Workflow

1. **Collect the brand kit.** The logo and product photos (`list-assets`, `search-assets`, or ask), colors and fonts (`list-themes`, the brand's ads, or ask), and the tone. Pass the logo as a `logo` reference and the product as a `subject` reference instead of describing them: the model then reproduces them exactly. Without a logo, set the brand name as a wordmark and tell the user it is a placeholder. Without a product photo, make one clean packshot first (the product alone on a plain background), and pass it as `subject` in every image of the set, so the product looks the same everywhere.
2. **Pin down the brief.** The goal, the audience, the offer, the placements and anything that must appear. Ask one question only when the goal or the offer is missing and cannot be inferred.
3. **Decide the concept.** For an open request, think of 2 or 3 ideas that differ in angle (benefit, problem, proof, offer, emotion) and in style. Render each as its own call, or pick one with the user.
4. **Write the copy.** A headline of 7 words or fewer, one support line, up to three proof points, the offer, and a button of three words or fewer. Prices, claims, codes, dates and legal text come from the user or the data, word for word.
5. **Write the spec and call `generate-image`.** Use the six parts above. Pass references with their roles.
6. **Check the result.** You get every image back. First the hard gates; any failure means a fix:
   - Every word matches the spec, separators and symbols included, and there is no other lettering.
   - The logo and the product match their references.
   - Colors are on brand, and text has strong contrast with what is behind it.
   - Text and logo stay inside the safe zones, and nothing important is cut off. In a 9:16 image, the last line of text sits above 65% of the height.
   - There are no stray marks, distorted hands or app chrome, and no claim the brief does not support.

   Then judge the design: one clear focal point, a single message a viewer gets in three seconds, the hierarchy headline then image then button, and an image that still reads at thumbnail size. Fix a problem with one call that passes the image as `edit_base` and names the single change ("keep everything the same, but ..."); editing beats re-rolling. Stop after three rounds and tell the user what is still wrong.
7. **Adapt it to every placement the user needs.** See "Resizing and series".
8. **Show it and offer the next step.** The user sees each image in the chat as its own card, so do not repeat it as a markdown image. To use an image elsewhere, publish it (see "Putting an image somewhere").

## Format playbook

| Format | Ratio and size | What makes it work |
|---|---|---|
| Feed ad | 4:5 or 1:1, 1K | One hero image, a headline, up to three proof points, a button, a small logo. |
| Story or Reel ad | 9:16, 1K | Keep text and logo out of the top 14%, the bottom 35% and 6% on each side; the image still fills the whole frame. A large headline and the button in the middle. |
| Landscape ad (LinkedIn, web) | 16:9, 1K | Copy on one side and the image on the other. |
| Google display and Performance Max images | 16:9, 1:1, 4:5 | No text, logo or button in the image: Google assembles the ad from the image plus separate headline, description and logo assets. Keep the subject in the center 80%, and deliver the copy as text. |
| Billboard or wide banner | 21:9, 4:1 or 8:1 | Seven words or fewer, readable from a distance. |
| Email header | 4:1, 2K | Copy and a button on the left, the product on the right, light and calm. |
| Offer or sale post | 1:1 or 4:5 | The offer is the hero ("-20%"); the end date and terms are small. |
| Carousel | 4:5 or 1:1 | Slide 1 is the hook. Make the other slides as a series (see below). |
| Flyer, poster or menu | 2:3 or 3:4, 2K | The title, then what, when, where and the price, all exact. |
| Report or slide cover | 3:4 or 16:9, 2K | Put the title in the image for a standalone cover. Leave it out when the image sits under an editable title in a report, and keep that area calm. |
| Infographic or results post | 4:5, 2K | Three to five points, numbers only from the data, one accent color for the numbers. |
| Logo concepts | 1:1 | A 2x2 grid of directions; say they are raster sketches. |
| Photo only | Any | Direct it like a photo shoot: subject, setting, lens, light, materials. |

## Reference images

Pass up to 6 in `reference_images`, each with an `asset_ulid` (or a Whatagraph-hosted `url`, such as one from `view-creatives`) and a `role`:

| Role | Use for | The tool tells the model |
|---|---|---|
| `edit_base` | The image you are changing | Change only what is asked; keep everything else identical. |
| `subject` | A product, object or character to keep | Keep its shape, colors, details and text. |
| `logo` | The client's own logo | Reproduce it exactly; do not redraw it. |
| `style` | An image whose look to follow | Follow the look; do not copy its logo, brand, text or products. |
| `person` | A person in a photo the user uploaded | Keep their appearance. |
| `other` | Anything else | |

Refer to each reference in the spec by its number ("the logo from image 1", "exactly the jacket from image 2"). To fix an exact layout, pass a rough wireframe or an approved earlier design as `other` and write "Keep the exact layout of image N". To use an image from outside Whatagraph, import it first with `manage-assets` (load `whatagraph-assets` first, see below) and pass its `asset_ulid`.

A real person can only come from a photo a person uploaded to the conversation or the library. The tool checks where each reference came from, so a photo you imported or generated does not count, whatever role you give it.

## Editing, resizing and series

**Edit.** Pass the image as `edit_base` and describe only the change: "Replace the background with a plain white #FFFFFF background", "Make it a rainy evening; keep everything else". Edits keep the rest of the image closely, and you can chain several edits without drift. Ask for a plain white background for a cut-out; transparent backgrounds are not possible.

**Resize to another placement.** Pass the approved design as `edit_base` with the new `aspect_ratio`, and say how to extend the scene and where the copy goes. Do not re-render it from a `style` reference: a new render changes the artwork and tends to ignore the safe zones.

```
Adapt this ad to a vertical 9:16 story. Extend the photo upward and downward naturally.
Keep the person, the product, the logo and every word identical in font and color.
Logo below the top 14% of the height; headline, feature line and button stacked in the
middle, all text above the bottom 35% and away from the sides. Flat and full-bleed.
```

**Translate or localize.** Pass the ad as `edit_base`: "Translate the headline to German: '...' and the button to '...'. Keep everything else identical." For one version per location, change only the city, address or price. Use `draft` quality for many versions and `standard` for the final ones.

**A series that must match** (carousel slides, report section banners, slide headers, an icon set). Make the first one. For each of the others, pass the first as `edit_base`: "Same layout, fonts, colors and margins. Change only the headline to '...' and the photo to ...".

**A mascot or recurring character.** Design it once on a plain background, then pass it as `subject` in every later scene.

## Quality, size and shape

| `quality` | Speed | Use for |
|---|---|---|
| `standard` (default) | about 15 to 25 s | Everything the user will see or publish. |
| `draft` | about 3 s, 1K only | Many quick variants, one version per location, early exploration. |

- `size`: `1K` by default. Use `2K` for flyers, posters, covers, email headers and full-width banners. Use `4K` only for print.
- `aspect_ratio`: 1:1, 4:5, 5:4, 3:4, 4:3, 2:3, 3:2, 9:16, 16:9, 21:9, 4:1, 1:4, 8:1, 1:8.
- `variations` (1 to 4) renders the same spec again, one image after another. To compare different ideas, call once per idea instead.

Every image costs AI credits. Make what the user asked for, and ask before making more than 12 in one go.

## Putting an image somewhere

A generated image is private to the conversation until you publish it. `manage-assets` runs only after the `whatagraph-assets` skill is loaded in the conversation, so load that skill before the first `manage-assets` call:

```
manage-assets action=publish asset_id=<asset_ulid>      → {"url": "<public_url>"}
```

Use the returned `url` for a report image widget (`manage-widgets`, `image_url`), a theme header or footer image, an `<img>` tag in an HTML document (which only loads published Whatagraph images), a canvas image block, or a link in an email. Publishing makes the image viewable by anyone with the URL, so publish only what the audience should see.

## Rules you must not break

- No real, identifiable person unless a person uploaded their photo and may use it; pass it with role `person`. Never a celebrity, politician or other public figure, never a fake endorsement, and never a quote or review attributed to a real person.
- No fabricated evidence: no fake screenshots of real platforms, fake reviews, forged documents, receipts or IDs, and no realistic pictures of events that did not happen.
- No third-party logos unless they are the client's own and come from the client as a reference image. That includes platform and partner logos (Google, Meta, TikTok and the like), even when the client's older ads show them: draw neutral icons instead, unless the user confirms the client may use them.
- No invented facts in the image: prices, discounts, codes, awards, ratings, results and legal text come from the user or the data, word for word. That includes the numbers on a product screen or dashboard mockup: use the client's real figures, or leave them out.
- Say an image is AI-generated when someone could take it for a real photo. Every generated image also carries an embedded AI-provenance marker.

If the tool refuses a request, tell the user why in plain words and offer an alternative that fits the rules.

## What it cannot do

- Transparent backgrounds. Use a plain white background instead.
- Animation, GIFs or video.
- Vector or layered files. Designs and logo concepts are flat raster images.
- Exact brand fonts. It follows a described style or a reference, not the font file.
- Guarantee very small text. Keep fine print large enough to read, check it in the result and fix it with an edit.
- Generate images for teams whose AI processing must stay in the EU. The tool is not offered to them.
