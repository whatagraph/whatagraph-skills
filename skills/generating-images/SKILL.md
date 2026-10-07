---
name: generating-images
type: domain
group: team_workspace_branding
description: Create and edit images of any kind with generate-image. Illustrations, report banners and covers, slide and HTML visuals, icons, posters and cards, characters and mascots, comics and maps, product and packaging mockups, photo edits, and ads with their variants, sizes and translations. Use whenever the user wants something visual made or changed. Do not use it for charts of real data, or to stand in for a real photo, screenshot, place, product or person.
required_tools:
  - generate-image
optional_tools:
  - tool_name: manage-assets
    purpose: Publish a generated image so a report, theme, HTML document or canvas can show it, or import an outside image to use as a reference.
  - tool_name: list-assets
    purpose: Find the client's logo, product photos or earlier generated images to use as references.
  - tool_name: search-assets
    purpose: Find a reference image in the team library by description.
  - tool_name: view-creatives
    purpose: Look at the client's existing ads before making a variant, and pass one as a reference.
  - tool_name: manage-widgets
    purpose: Put a published image into a report image widget.
  - tool_name: list-themes
    purpose: Read a report's brand colors and fonts before writing the prompt.
  - tool_name: create-document
    purpose: Build an HTML page that shows published images.
---

# Generating images

Tool covered: `generate-image`.

`generate-image` makes a new image from a text prompt, or changes an image you pass in. It handles almost any visual: photos, illustrations in any style, 3D renders, icons, diagrams with short labels, posters, comics, maps, mockups and ads. It renders short text exactly, keeps a product, logo or character from a reference image, and edits an existing image very reliably.

It does not have ideas of its own. Asked to "be creative", it draws the most obvious picture of the words in the prompt. **You are the art director: decide what the image should be, then describe it so precisely that nothing is left to guess.**

## Default to photography

These images go into client reports, pages and ads. Abstract 3D art and cartoon icons look like generic AI art there, and users reject them. Unless the user asks for an illustration, or the brand's own material is illustrated, make a photograph:

- **Show a real scene from the client's world:** their product category, their customers, their place of business. Not an abstract pattern, a visual metaphor or a floating object.
- **Direct it like a photo shoot.** Name the lens, the light and the materials ("shot on a 50mm lens, soft window light, linen, glass and stone textures"), and add "Not a 3D render, not an illustration."
- **Make people ordinary and fictional:** "a woman in her thirties", "natural skin texture, unposed". Never a real person (see "Rules you must not break").
- **Show the client's own product only from their photo,** passed as a `subject` reference. Without one, show the setting, the customer or the category, with plain unbranded packaging.
- **Leave out the motifs that mark an image as AI art:** abstract waves or ribbons, glowing particles, holograms, floating dashboards, neon gradients, and clay or plastic 3D icons.

Use an illustration when the user asks for one, when a variant must follow an illustrated ad, or for a diagram that explains an idea (see "Recipes").

## Use this when

The user wants something visual made or changed. Some examples:

- A cover image, section banner, background or illustration for a report, slide, canvas or HTML page.
- An icon set, a diagram-style illustration, an infographic with a few labels, a fantasy map, a comic strip that explains an idea.
- A mascot or character, and the same character in new scenes.
- A poster, invitation, birthday card, certificate design, menu, sticker sheet.
- Logo concepts, packaging mockups, a moodboard of creative directions.
- An edit of the user's own image: new background, cut-out on white, relit, extended to another shape, restyled, two images combined.
- An ad: a concept mockup, A/B variants, a new size, a translation, one version per location.

## Do not use it when

- **The image would stand in for something real.** Never generate a photo of a real property, a real event, a competitor's post, a platform screenshot, a real person or a product you have not seen. Find the real image (the client's uploads, `view-creatives`, an official source imported with `manage-assets`) or say you cannot. Users reject invented look-alikes, and they stop trusting the rest of the work.
- **The picture is a chart of real numbers.** Build a widget or a canvas chart. The model draws the numbers you give it, but nobody can check or update a picture, and bars are not guaranteed to scale.
- **The request names a real, identifiable person** the user has not supplied a photo of. See "Rules you must not break".

## Workflow

1. **Collect the inputs.** Brand colors and fonts (`list-themes`, or ask), the logo and product photos (`list-assets`, `search-assets`), the image being changed. Ask for a logo rather than inventing one.
2. **Decide the concept.** For anything open-ended, think of 2 to 4 concrete scenes that differ in subject, setting and mood. Prefer a specific scene ("a skincare shelf in morning light") to a generic one ("a beauty product"). Pick one with the user, or render each as its own call.
3. **Write the prompt** with the template below.
4. **Call `generate-image`.** Pass reference images with their roles.
5. **Check the result.** You get each image back. Read every word in it against the prompt, check logos, products and faces, and check that nothing important is cut off. Fix a mistake with one more call that passes the image as `edit_base` and names exactly what to change. Stop after two fixes and tell the user what is still wrong.
6. **Show it and offer the next step.** The user already sees each image in the chat as its own card, so do not repeat it as a markdown image. To use it elsewhere, publish it (see "Putting an image somewhere").

## The prompt template

```
{Asset type} for {where it will be used}, {aspect ratio}, flat and full-bleed.
Subject: {what it shows, what is happening, where}.
Style: {photo: lens, light and materials, "Not a 3D render, not an illustration" (default) | the illustration style the user or the brand asked for}.
Palette: {color #hex}, {#hex}, {#hex}.
Composition: {where the subject sits}; {where text goes}, with margins.
Text, exactly: '{line 1}', '{line 2}'. No other text, letters, logos or app interface.
```

Leave out the lines that do not apply. A background has no text line; a photo edit may only need one sentence.

What each rule prevents:

| Rule | Failure it prevents |
|---|---|
| Say "flat and full-bleed" | The design comes back as a printed card in a hand, a framed picture, a magazine page or a device mockup. |
| Name the asset, not the app ("vertical 9:16 image", not "Instagram Story") and add "no app interface" | The model draws app chrome: "Sponsored", like and send buttons, a video timestamp. |
| Quote every word that must appear and end with "No other text" | Invented taglines, prices, discount codes, brand names, camera settings. |
| Keep on-image text short, about 12 words or fewer | Long text gets squeezed or reflowed badly. Legal lines are the exception: quote them in full. |
| Give colors as hex codes | Off-brand colors. |
| For vertical formats, say "the image fills the whole frame; text only in the middle 60% of the height" | Asked to leave areas "free", the model leaves blank bands. |
| Never name a real brand for a fictional product | It draws the real brand's product and badge. |
| Describe one clear idea | Several competing ideas produce a cluttered image. |

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

To use an image from outside Whatagraph, import it first with `manage-assets` (load `whatagraph-assets` first, see below) and pass its `asset_ulid`. Describe in the prompt what each reference is for ("put the product from the first image into the scene of the second").

A real person can only come from a photo a person uploaded to the conversation or the library. The tool checks where each reference came from, so a photo you imported or generated does not count, whatever role you give it.

## Editing an image

Pass the image as `edit_base` and describe only the change: "Replace the background with a plain white #FFFFFF background", "Translate the headline to German: '...'", "Make it a rainy evening; keep everything else". Edits keep the rest of the image very closely, and you can chain several edits without the image drifting.

- **Cut-out:** ask for a plain white background. Transparent backgrounds are not possible.
- **New shape:** pass the image as `edit_base` with the new `aspect_ratio` and say how to extend the scene.
- **Same character, new scene:** pass the character as `subject` and describe the new scene.

## Quality, size and shape

| `quality` | Speed | Use for |
|---|---|---|
| `standard` (default) | about 15 to 20 s | Everything the user will see or publish. |
| `draft` | about 3 s, 1K only | Many quick variants, one version per location, backgrounds, early exploration. |

- `size`: `1K` by default. Use `2K` for full-width report banners and covers, which need about 2,500 px of width to look sharp. Use `4K` only for print or very large heroes.
- `aspect_ratio`: 1:1, 4:5, 5:4, 3:4, 4:3, 2:3, 3:2, 9:16, 16:9, 21:9, 4:1, 1:4, 8:1, 1:8.
- `variations` (1 to 4) renders the same prompt again, one image after another, so each one adds its full time. To compare different ideas, call once per idea instead.

Every image costs AI credits. Make what the user asked for, and ask before making more than 8 in one go.

## Putting an image somewhere

A generated image is private to the conversation until you publish it. `manage-assets` runs only after the `whatagraph-assets` skill is loaded in the conversation, so load that skill before the first `manage-assets` call:

```
manage-assets action=publish asset_id=<asset_ulid>      → {"url": "<public_url>"}
```

Use the returned `url` for a report image widget (`manage-widgets`, `image_url`), a theme header or footer image, an `<img>` tag in an HTML document (which only loads published Whatagraph images), a canvas image block, or a link in an email. Publishing makes the image viewable by anyone with the URL, so publish only what the audience should see.

## Recipes

**A series that must match** (report section banners, slide headers, a set of icons). Make the first one. For each of the others, pass the first as `edit_base`: "Same banner: same background, font, size and position. Only change the text to '...'."

**A cover or hero image for a report or page.** Ask what the report is about and who reads it. Photograph a scene from the client's business, not an abstract pattern. Leave clean space where the title will sit ("keep the left third empty") and do not put the title in the image, so it stays editable.

**An illustration that explains an idea** (a funnel, a customer journey, how attribution works). Pick one visual metaphor, keep labels to a few words each, and quote them. For a sequence, a 3 or 4 panel comic with short speech bubbles works well.

**A mascot or recurring character.** Design it once on a plain background, then pass it as `subject` in every later scene.

**Photo edits.** `edit_base` plus one sentence saying what changes. Say "keep the person, product and text identical" when they must not move.

**Brand and design exploration** (logo concepts, packaging, moodboards). Show several directions side by side in one image ("a 2x2 grid of four concepts"), or one call per direction. Say these are concepts: a generated logo is a raster sketch, not a vector file.

**Ads.**
- *Variants of an ad that is running:* look at it with `view-creatives`, then pass it as `edit_base` (same layout, new scene) or `style` (new layout, same look). Keep the product, price, logo and legal text identical and say so.
- *One ad, many locations or languages:* make or receive the master, then one `draft` call per version with the master as `edit_base`: "Change the store name to '...' and the address to '...'. Keep everything else identical."
- *A concept mockup of an idea you recommended:* one prompt per idea with the template, labeled as a concept for the user.

**Cards, posters and invitations.** Quote the exact names, dates and places, and keep them to a few lines.

## Rules you must not break

- No real, identifiable person unless a person uploaded their photo and may use it; pass it with role `person`. Never a celebrity, politician or other public figure, never a fake endorsement, and never a quote or review attributed to a real person.
- No fabricated evidence: no fake screenshots of real platforms, fake reviews, forged documents, receipts or IDs, and no realistic pictures of events that did not happen.
- No third-party logos unless they are the client's own and come from the client as a reference image.
- No invented facts in the image: prices, discounts, codes, awards, ratings and legal text come from the user, word for word.
- Say an image is AI-generated when someone could take it for a real photo. Every generated image also carries an embedded AI-provenance marker.

If the tool refuses a request, tell the user why in plain words and offer an alternative that fits the rules.

## What it cannot do

- Transparent backgrounds. Use a plain white background instead.
- Animation, GIFs or video.
- Vector files. Logo concepts are raster images.
- Exact brand fonts. It follows the look of a reference, not the font file.
- Guarantee very small text. Check fine print in the result and fix it with an edit.
- Generate images for teams whose AI processing must stay in the EU. The tool is not offered to them.
