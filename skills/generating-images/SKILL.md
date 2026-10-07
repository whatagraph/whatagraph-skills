---
name: generating-images
type: domain
group: team_workspace_branding
description: Create and edit any visual as a finished, on-brand design with generate-image, and lay out exact text, logos, prices and charts with render-design. Ads and their placement sets, social posts and carousels, offer posts, flyers, posters and menus, report and slide covers, email headers and banners, infographics and results posts, product and lifestyle photos, illustrations, 3D and typographic graphics, logo concepts, photo edits, resizes and translations. Use whenever the user wants something visual made or changed. For ad layouts load `designing-ad-creatives`; for a full campaign built on the client's brand and ad results, also load `creating-ad-campaigns`. Do not use it to stand in for a real photo, screenshot, place, product or person.
required_tools:
  - generate-image
optional_tools:
  - tool_name: render-design
    purpose: Lay out exact copy, prices, legal text, the client's real logo and fonts, and charts of real numbers in HTML and CSS over generated imagery, and render the same layout at every placement size.
  - tool_name: manage-assets
    purpose: Publish a finished image so a report, theme, HTML document or canvas can show it, or import an outside image (a logo, a product photo) to use as a reference.
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

Tools covered: `generate-image`, `render-design`.

- `generate-image` renders whatever the prompt describes: photographs, illustration in any technique, 3D, typography and complete layouts with exact headlines and buttons. It keeps a logo, a product or a character from a reference image, edits reliably, and re-lays out a design for another shape.
- `render-design` turns an HTML and CSS layout into a PNG of an exact pixel size. Text is real type in any Google Font, the logo and product are the client's own pixels, and numbers and charts are exactly what you write. It is not available to every agent; check your tool list.

Neither decides anything. A vague request returns a vague picture: a stock photo with no message, or generic AI art. **You are the creative director. Decide the idea, the layout, the style and the exact words, then write them down so that nothing is left to guess.**

## Use this when

The user wants something visual made or changed:

- An ad: a concept, a set of placements, A/B variants, an offer post, a translation, one version per location.
- A social post, a carousel, a story, a creator-style native ad.
- A flyer, a poster, a menu, an invitation, a card, a certificate.
- A report cover, a slide cover, a section banner, an email header, a website hero.
- An infographic or a results post with the client's real numbers, an explainer, a map.
- A product or lifestyle photo, a mascot, logo concepts, a packaging mockup, a moodboard.
- An edit of an existing image: new background, cut-out on white, relit, extended, restyled, combined.

## Do not use it when

- **The image would stand in for something real.** Never generate a photo of a real property, a real event, a competitor's post, a platform screenshot, a real person or a product you have not seen. Find the real image (the client's uploads, `view-creatives`, an official source imported with `manage-assets`) or say you cannot.
- **A chart of real numbers would be drawn by the image model.** Its bars are not to scale and cannot be checked. Draw the chart in SVG or HTML with `render-design`, or build a widget. A generated picture may carry a few numbers in large type when they are exact.
- **The request names a real, identifiable person** the user has not supplied a photo of. See "Rules you must not break".

## Two ways to build a design

| | All in one image | Composed |
|---|---|---|
| How | `generate-image` renders picture, copy, logo and button together | `generate-image` makes the picture with empty space and no text; `render-design` lays the copy, logo, product photo, button and fine print on top |
| Use for | Social posts, concepts, lifestyle and editorial ads, posters, illustrated and 3D work, anything where type and image interact | Prices and offers, legal lines, more than about 25 words, the client's exact logo and brand font, charts of real numbers, carousels and every set that must stay identical across sizes |
| Strength | Type that belongs to the picture; fastest | Pixel-exact text, logo, product and numbers; re-renders at any size from the same layout |

Use composed whenever an error in a word, a price, the logo or a number would matter and `render-design` is in your tool list. Otherwise build it all in one image and check every word.

## The creative spec (all in one image)

When the image carries a message, the image is the deliverable. Write the spec as full sentences, the way you would brief a designer, with these parts:

```
{Format}, {aspect ratio}, for {brand}, {what it is for and who it is for}.
Brand system: logo {from image N | a wordmark '<name>' in <type style>}; colors {#hex with a role: background, text, accent}; type {headline style; body style}.
Layout: {zone by zone, top to bottom: what sits where, alignment, relative size}.
Imagery: {subject, setting, pose, light, lens, materials; or the illustration technique}.
Copy, exactly: headline '...'; support '...'; proof '...'; offer '...'; button '...'. No other text.
Finish: a finished design as delivered by a top creative agency. Crisp, perfectly kerned typography on a clear grid, consistent margins, every word spelled exactly as given. Flat and full-bleed: no mockup, no frame, no app interface, no watermark.
```

An example that produced a production-ready feed ad:

```
Paid social feed ad, 4:5, for Northpeak, an outdoor jacket brand, aimed at hikers who keep going when the weather turns.
Brand system: logo from image 1, in off-white; colors forest green #1F3A2E for the copy panel, signal orange #E8622C for the button, warm off-white #F4F1EA for text; headlines in a heavy condensed sans in capitals, body in a clean grotesk.
Layout: full-bleed photo; logo top-left; the lower third fades into forest green behind the copy; headline large and left-aligned; the support line under it; a rounded orange button bottom-right.
Imagery: a woman in her thirties stands on a misty ridge as the first snow falls, facing three-quarters toward the camera and looking out at the view; her right hand rests on the strap of her backpack and her left arm hangs relaxed. She wears exactly the jacket from image 2. 35mm lens at f/2.8, flat overcast light from the left, snowflakes in the air, visible fabric texture and fine lines at her eyes, not retouched.
Copy, exactly: headline 'Built for the first snow'; support 'Waterproof to 20,000 mm and only 480 g.'; button 'Shop the collection'. No other text.
Finish: (as above)
```

What each part prevents:

| Part | Without it |
|---|---|
| What it is for and who it is for | A generic stock image with no point of view. |
| Brand system with a role for each color | Off-brand colors, random fonts, a different logo each time. |
| Layout by zone | Everything centered, and the copy fights the image. |
| A stated pose for every person | Broken bodies: two right arms, a head facing backward. See "People and bodies". |
| Copy, exactly, ending with "No other text" | Invented taglines, prices, codes and misspellings. |
| The finish line | A mockup, a framed print, a phone screen, a layout that looks unfinished. |
| A headline of 7 words or fewer, at most three text blocks | Squeezed or wrapped text. Long copy belongs in the ad's caption or in a composed design. |
| The asset named, not the app ("vertical 9:16 ad", not "Instagram Story") | "Sponsored" labels, like buttons, usernames. |
| A fictional product never named after a real brand | The real brand's product and badge. |

For an image without copy (the picture under a composed design, a hero photo, a report banner whose title must stay editable), drop the copy line, say where the empty space is ("the upper 40% is calm sky with nothing in it"), and end with "No text, letters or logos."

## Composed designs with render-design

1. Generate the picture first with `generate-image`: the scene, the product and the people, with empty space where the copy will sit, and no text. Keep it, and pass it to `render-design` as an image.
2. Write the layout as one HTML document with a `<style>` block. Size the body to the exact width and height you request. Put each image in with `{{image_1}}`, `{{image_2}}` and so on, in the order of `images`. Load fonts with a Google Fonts `<link>`. JavaScript does not run, and nothing else loads from the web, so every picture, logo and icon must be passed in `images` or drawn in CSS or inline SVG.
3. Call `render-design` with `html`, `width`, `height`, `images` (each an `asset_ulid` or a Whatagraph-hosted `url`) and a `title`.
4. For every other placement, change only the CSS for the new size and render again with the same images. Copy, logo and product stay identical.

```
<html><head>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@800&family=Inter:wght@500;700&display=swap" rel="stylesheet">
<style>
body{margin:0;width:1080px;height:1350px;position:relative;overflow:hidden;font-family:Inter,sans-serif}
.photo{position:absolute;inset:0;background:url({{image_1}}) center/cover}
.panel{position:absolute;left:0;right:0;bottom:0;height:430px;background:linear-gradient(to bottom,rgba(31,58,46,0),#1F3A2E 34%)}
.logo{position:absolute;top:60px;left:64px;width:220px}
h1{position:absolute;left:64px;right:64px;bottom:210px;margin:0;font:800 132px/.9 'Barlow Condensed';text-transform:uppercase;color:#F4F1EA}
.price{position:absolute;left:64px;bottom:84px;font:700 44px Inter;color:#F4F1EA}
.btn{position:absolute;right:64px;bottom:72px;padding:26px 44px;border-radius:999px;background:#E8622C;color:#fff;font:700 36px Inter}
.legal{position:absolute;left:64px;bottom:32px;font:500 20px Inter;color:rgba(244,241,234,.75)}
</style></head><body>
<div class="photo"></div><div class="panel"></div><img class="logo" src="{{image_2}}">
<h1>Built for the<br>first snow</h1><div class="price">From €189</div><div class="btn">Shop now</div>
<div class="legal">Free returns within 30 days.</div>
</body></html>
```

Layout rules that make a composed design look designed, not templated: one display face and one text face; a strict margin (5 to 6% of the width) on every side; the headline the largest thing after the hero; the offer or number set in the accent color; a soft gradient or a solid panel behind text instead of a drop shadow; at most four text elements; and nothing in a placement's unsafe zone. For a chart, draw bars and labels in inline SVG from the real numbers, with one accent color for the series the post is about.

## Choose the mode and the style on purpose

First decide the mode, because it sets the layout:

- **Performance** (sales, sign-ups, offers): the product or the offer dominates, the headline carries the benefit, a proof point appears (a number, a rating the client can stand behind), the button is high-contrast, and the grid is tight.
- **Editorial** (brand, launches, covers): one strong image, five words of copy or fewer, generous white space, display or serif type, a small logo.

Then pick the style. Follow the brand's existing material when it has any: its ads (`view-creatives`), its theme (`list-themes`), its website. A style the user names always wins. Otherwise pick what fits the brand, the audience and the placement, and vary it across concepts:

| Style | Fits | Put in the spec |
|---|---|---|
| Photographic: lifestyle, product, editorial | Most consumer brands, fashion, food, travel, beauty | Subject, setting, pose, lens, one light source, materials (see "Make it look real") |
| Product-led graphic | Offers, launches, e-commerce | The product as a cut-out with a contact shadow, color blocks, the offer or price as the hero |
| Typographic | Sales, announcements, bold brands | The grid, type style and sizes, no imagery |
| Illustration | Events, local businesses, explainers, friendly brands | The technique (flat vector, risograph, linocut, gouache, hand-drawn, isometric), line and texture |
| 3D | Apps, fintech, playful brands | The material (glossy, jelly, clay), the lighting, a solid background color |
| Editorial or magazine | Covers, reports, premium brands | A display serif, generous margins, a photo inset |
| Creator or native | Social ads that must not look like ads | Phone-camera framing, caption boxes, imperfect light; no app buttons or usernames |
| Infographic | Results, how-tos, B2B posts | Numbered rows, simple line icons, one accent color for the numbers |

Avoid the defaults that look like generic AI art unless the brand uses them: abstract waves and ribbons, glowing particles, holograms, floating dashboards, neon gradients, and a lone person gazing at a sunset.

## Make it look real

Photographs read as AI when the light has no source, the skin is waxy, everything is symmetric and centered, and the subject looks cut out over a blurred background. Write the photo like a shoot:

- One physical light source and its direction: "window light from the left, late afternoon, a hard shadow under the jaw", "flat overcast daylight", "on-camera flash at night".
- A lens and an aperture: "35mm at f/2.8", "85mm at f/2, focus on the near eye, the background falling off gradually".
- Texture and imperfection: "visible pores and fine lines", "slightly asymmetric smile", "creased linen", "a lived-in kitchen with a few things out of place", "not retouched".
- Candid framing: "caught mid-step, off-center, as if from a documentary".
- A real camera look when it fits the brand: "35mm film with fine grain", "shot on a phone in daylight", "disposable camera flash".
- Leave out "8K", "hyperrealistic", "masterpiece", "cinematic" and "ultra-detailed": they produce the glossy AI look.
- Objects and food need imperfection too: a scuff on a ceramic, crumbs, a drip, a slightly uneven stack. Spotless props and glossy catalog food give an image away as generated.

## People and bodies

Generated people break in predictable ways: two left or right hands, an arm from the wrong shoulder, a head turned backward on a body seen from behind, fused fingers. A pose such as "pulling on a jacket" broke the body in every attempt in testing. A stated, simple pose did not. So:

- **State the pose of every person**: which way the body faces, what each hand does, and where each arm is. "She faces three-quarters toward the camera; her right hand is in her jacket pocket; her left arm hangs relaxed."
- **Prefer stable poses**: standing, walking, sitting, looking at the view, holding one object with both hands, hands in pockets or on backpack straps. Avoid dressing and undressing, stretching, crossed or tangled arms, and bodies that touch (hugs, handshakes), unless they are the point of the image.
- **Fewer people.** One person is safest, two is fine, a crowd only at a distance.
- **Hide hands that do not matter**: crop at the waist, or put them in pockets.
- **For a complex pose**, pass a photo of the pose as an `other` reference: "Use the pose from image 3."

## Workflow

1. **Collect the brand kit.** The logo and product photos (`list-assets`, `search-assets`, or ask), colors and fonts (`list-themes`, the brand's ads, the website, or ask), and the tone. Pass the logo as a `logo` reference and the product as a `subject` reference instead of describing them. Without a logo, set the brand name as a wordmark and tell the user it is a placeholder. Without a product photo, make one clean packshot first (the product alone on a plain background), and pass it as `subject` in every image of the set, so the product looks the same everywhere.
2. **Pin down the brief.** The goal, the audience, the offer, the placements and anything that must appear. Ask one question only when the goal or the offer is missing and cannot be inferred.
3. **Decide the concept and the layout.** For an ad, pick an archetype from `designing-ad-creatives`. For an open request, think of 2 or 3 ideas that differ in angle and in style, and render each as its own call, or pick one with the user.
4. **Write the copy.** A headline of 7 words or fewer, one support line, up to three proof points, the offer, and a button of three words or fewer. Prices, claims, codes, dates and legal text come from the user or the data, word for word.
5. **Build it**: the spec and `generate-image`, or the picture and then `render-design`.
6. **Check it** (below), and fix what fails.
7. **Adapt it to every placement the user needs.** See "Editing, resizing and series".
8. **Show it and offer the next step.** The user sees each image in the chat as its own card, so do not repeat it as a markdown image. Give each file's real pixel size, from the tool result. If a size the user asked for could not be made, or a tool failed and you used another way, say so in one line; never list a file at a size it does not have. To use an image elsewhere, publish it (see "Putting an image somewhere").

## Check every image before you show it

You get every image back. Look at it the way a picky client would, in this order:

1. **Bodies.** For each person: which way does the body face? Follow each arm from its shoulder to its hand, and check it ends in one hand with five fingers on the correct side. Check the head faces the same way as the body, the clothes are worn the right way round, and the legs and feet make sense. Any doubt counts as a failure.
2. **Words.** Read every word in the image aloud, letter by letter, against the spec, separators and symbols included. There is no other lettering anywhere, including signs and labels in the background.
3. **Brand and counts.** The logo and the product match their references side by side: shape, colors, label text. Colors are on brand, and text has strong contrast with what is behind it. When the copy states a count (12 eggs, 3 bottles, 4 seats), count them in the image: image models often get counts wrong, so fix the image or make the copy match what is shown.
4. **Placement.** Text and logo stay inside the safe zones and nothing important is cut off. In a 9:16 image, the last line of text sits above 65% of the height.
5. **Claims.** Nothing appears that the brief does not support: no extra numbers, badges, ratings or platform logos.
6. **Design.** One clear focal point, one message a viewer gets in three seconds, the hierarchy headline then image then button, and an image that still reads at thumbnail size.

Fix a failure with one `generate-image` call that passes the image as `edit_base` and names the single change, and repeat what must stay: "Change only her left arm so it hangs relaxed at her side, ending in her left hand. Keep everything else exactly the same." Editing beats re-rolling. A body that is wrong in several places is faster to regenerate with a simpler pose. In a composed design, fix the HTML and render again. Stop after three rounds and tell the user what is still wrong.

## Format playbook

| Format | Ratio and pixels | What makes it work |
|---|---|---|
| Feed ad | 4:5 (1080x1350) or 1:1 (1080x1080) | One hero, a headline, up to three proof points, a button, a small logo. |
| Story or Reel ad | 9:16 (1080x1920) | Keep text and logo out of the top 14%, the bottom 35% and 6% on each side; the image still fills the frame. A large headline and the button in the middle. |
| Landscape ad (LinkedIn, web) | 16:9 or 1.91:1 (1200x628) | Copy on one side, the image on the other. |
| Google display and Performance Max images | 1.91:1, 1:1, 4:5 | No text, logo or button in the image: Google assembles the ad from the image plus separate headline, description and logo assets. Keep the subject in the center 80%, and deliver the copy as text. |
| Billboard or wide banner | 21:9, 4:1 or 8:1 | Seven words or fewer, readable from a distance. |
| Email header | 4:1 (1200x300), 2K | Copy and a button on the left, the product on the right, light and calm. |
| Offer or sale post | 1:1 or 4:5 | The offer is the hero ("-20%"); the end date and terms are small. |
| Carousel | 4:5 or 1:1 | Slide 1 is the hook. Make the other slides as a series. |
| Flyer, poster or menu | 2:3 or 3:4, 2K | The title, then what, when, where and the price, all exact. |
| Report or slide cover | 3:4 or 16:9, 2K | Put the title in the image for a standalone cover. Leave it out when the image sits under an editable title in a report, and keep that area calm. |
| Infographic or results post | 4:5 | Three to five points, numbers only from the data, one accent color for the numbers. Composed when the numbers matter. |
| Logo concepts | 1:1 | A 2x2 grid of directions; say they are raster sketches. |
| Photo only | Any | Direct it like a shoot: subject, setting, pose, lens, light, materials. |

## Reference images

Pass up to 6 in `reference_images`, each with an `asset_ulid` (or a Whatagraph-hosted `url`, such as one from `view-creatives`) and a `role`:

| Role | Use for | The tool tells the model |
|---|---|---|
| `edit_base` | The image you are changing | Change only what is asked; keep everything else identical. |
| `subject` | A product, object or character to keep | Keep its shape, colors, details and text. |
| `logo` | The client's own logo | Reproduce it exactly; do not redraw it. |
| `style` | An image whose look to follow | Follow the look; do not copy its logo, brand, text or products. |
| `person` | A person in a photo the user uploaded | Keep their appearance. |
| `other` | A pose, a wireframe, anything else | |

Refer to each reference in the spec by its number ("the logo from image 1", "exactly the jacket from image 2"). To fix an exact layout, pass a rough wireframe or an approved earlier design as `other` and write "Keep the exact layout of image N". To use an image from outside Whatagraph, import it first with `manage-assets` (load `whatagraph-assets` first) and pass its `asset_ulid`.

A real person can only come from a photo a person uploaded to the conversation or the library. The tool checks where each reference came from, so a photo you imported or generated does not count, whatever role you give it.

## Editing, resizing and series

**Edit.** Pass the image as `edit_base` and describe only the change: "Replace the background with a plain white #FFFFFF background", "Make it a rainy evening; keep everything else". You can chain several edits without drift. Ask for a plain white background for a cut-out; transparent backgrounds are not possible.

**Resize to another placement.** For a composed design, render the same layout again with CSS for the new size. For a design made all in one image, pass the approved design as `edit_base` with the new `aspect_ratio`, and say how to extend the scene and where the copy goes. Do not re-render it from a `style` reference: a new render changes the artwork and tends to ignore the safe zones.

```
Adapt this ad to a vertical 9:16 story. Extend the photo upward and downward naturally.
Keep the person, the product, the logo and every word identical in font and color.
Logo below the top 14% of the height; headline, feature line and button stacked in the
middle, all text above the bottom 35% and away from the sides. Flat and full-bleed.
```

**Translate or localize.** Composed: change the words in the HTML. All in one image: pass the ad as `edit_base`: "Translate the headline to German: '...' and the button to '...'. Keep everything else identical." For one version per location, change only the city, address or price. Use `draft` quality for many quick versions and `standard` for the final ones.

**A series that must match** (carousel slides, report section banners, an icon set). Make the first one. For each of the others, reuse its HTML, or pass the first as `edit_base`: "Same layout, fonts, colors and margins. Change only the headline to '...' and the photo to ...".

**A mascot or recurring character.** Design it once on a plain background, then pass it as `subject` in every later scene.

## Quality, size and shape

| `quality` | Speed | Use for |
|---|---|---|
| `standard` (default) | about 15 to 25 s | Everything the user will see or publish. |
| `draft` | about 3 s, 1K only | Many quick variants, one version per location, early exploration. |

- `size`: `1K` by default. Use `2K` for flyers, posters, covers, email headers, full-width banners and pictures under a composed design. Use `4K` only for print.
- `aspect_ratio`: 1:1, 4:5, 5:4, 3:4, 4:3, 2:3, 3:2, 9:16, 16:9, 21:9, 4:1, 1:4, 8:1, 1:8.
- `generate-image` picks its own pixel size for a ratio: a 16:9 image at 1K comes back at about 1376x768, not 1200x628, and a 4:5 image at about 928x1152, not 1080x1350. When a placement needs exact pixels, build it with `render-design`, which renders exactly the width and height you give.
- `variations` (1 to 4) renders the same spec again, one image after another. For a hero image with people, two variations and the cleaner one is often faster than fixing one. To compare different ideas, call once per idea instead.

Every generated image costs AI credits; a render does not. Make what the user asked for, and ask before making more than 12 images in one go.

## Putting an image somewhere

A generated or rendered image is private to the conversation until you publish it. `manage-assets` runs only after the `whatagraph-assets` skill is loaded in the conversation, so load that skill before the first `manage-assets` call:

```
manage-assets action=publish asset_id=<asset_ulid>      → {"url": "<public_url>"}
```

Use the returned `url` for a report image widget (`manage-widgets`, `image_url`), a theme header or footer image, an `<img>` tag in an HTML document (which only loads published Whatagraph images), a canvas image block, or a link in an email. Publishing makes the image viewable by anyone with the URL, so publish only what the audience should see.

## Rules you must not break

- No real, identifiable person unless a person uploaded their photo and may use it; pass it with role `person`. Never a celebrity, politician or other public figure, never a fake endorsement, and never a quote or review attributed to a real person.
- No fabricated evidence: no fake screenshots of real platforms, fake reviews, ratings or press logos, forged documents, receipts or IDs, and no realistic pictures of events that did not happen. A review, rating or "as seen in" appears only when the client has it, word for word.
- No third-party logos unless they are the client's own and come from the client as a reference image. That includes platform and partner logos (Google, Meta, TikTok and the like), even when the client's older ads show them: draw neutral icons instead, unless the user confirms the client may use them.
- No invented facts in the image: prices, discounts, codes, awards, ratings, results and legal text come from the user or the data, word for word. That includes the numbers on a product screen or dashboard mockup: use the client's real figures, or leave them out.
- Say an image is AI-generated when someone could take it for a real photo. Every generated image carries an embedded AI-provenance marker, and some platforms and regions require an AI label on ads.

If a tool refuses a request, tell the user why in plain words and offer an alternative that fits the rules.

## What it cannot do

- Transparent backgrounds. Use a plain white background, or a composed design.
- Animation, GIFs or video.
- Layered files for a design tool. A composed design's HTML can be edited and rendered again; the output is a flat PNG.
- Exact brand fonts or very small text in `generate-image`. Use `render-design`, or keep fine print large, check it, and fix it with an edit.
- Generated images for teams whose AI processing must stay in the EU: `generate-image` is not offered to them. `render-design` calls no AI model.
