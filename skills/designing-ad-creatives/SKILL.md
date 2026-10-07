---
name: designing-ad-creatives
type: domain
group: team_workspace_branding
description: The layout library for static ads and social creatives. 28 proven ad archetypes, from offer-first and product demos to comparisons, testimonials, creator-style posts, listicles, stat posts, event posters, menus, property listings and recruitment ads, each with its layout, copy slots and how to build it. Includes what separates the best real ads from the rest for performance, brand, local, B2B and social goals. Use before designing any ad, paid or organic social post, flyer or poster, and when choosing concepts for a campaign. Load `generating-images` for how to render and check the images.
required_tools:
  - generate-image
optional_tools:
  - tool_name: render-design
    purpose: Lay out exact copy, prices, logos and charts over a generated picture, and render the same layout at every size.
  - tool_name: view-creatives
    purpose: See the client's current ads, so new concepts build on what already works and stay in the brand's style.
---

# Designing ad creatives

This is the library of ad layouts. `generating-images` covers how to write the spec, compose, check and resize; this skill covers what to make.

The guidance comes from a review of about 2,400 real ads across Meta, Instagram, Google, TikTok, LinkedIn, Pinterest, Snapchat, programmatic display, Spotify and YouTube, in more than 60 industries. Ten reviewers scored every ad. Five judges with different goals then voted on the 217 best: a performance marketer, a brand creative director, a local-business marketer, a B2B demand marketer and a social-native creator. It also draws on the formats the leading ad tools generate and the published hit rates for those formats.

## What the best ads have in common

1. **One idea a stranger gets in one second.** One message, one focal point. The weakest ads were plain photos with no message, frames from videos with no hook, and layouts with too many competing blocks.
2. **The product proves the claim inside the image.** A phone that has just bounced down a staircase with its screen intact, a cleaner leaving one clean stripe through a muddy floor, a jacket dry in a downpour. Showing beats stating.
3. **They talk to one person.** A specific audience call-out ("For people who ..."), a pain in the buyer's own words, a question they actually ask. Slogans that any company could sign scored lowest with every judge.
4. **The offer is specific and the biggest thing on the canvas.** A price per unit, a savings figure, "pay nothing until March", a free first month, with one urgency cue. "Our biggest sale" with no number fails.
5. **Proof beats polish.** A number with a source, a real customer's words, a result with a timeframe, a demonstration.
6. **It looks like it belongs in the feed.** Candid, specific photography and a human voice beat stock smiles, starbursts, icon rows and glossy AI spectacle. Even a creator-style ad keeps the product unmistakable.
7. **It is ownable.** The brand's color, the product's shape or the brand name as a graphic element, so the ad could not belong to a competitor.
8. **Every size is designed on purpose.** A banner is one image, one line and one button. A shrunk feed ad loses the button and the proof.

The judges disagreed in useful ways, so weigh them by the goal:

| Goal | What wins |
|---|---|
| Sales and leads (performance) | A reason to act now (a specific offer and deadline) or proof that it works, in the first second; it looks like a post, not a brochure. |
| Brand and launches | One idea only this brand could own, shown with restraint: one strong image, very little type, the brand's own color and shapes. |
| Local businesses | What, where, when and the price at a glance, a local and trustworthy feel, and a layout the business could repeat every week. |
| B2B | Audience in the first line, one specific pain or outcome, proof (a number, a named customer, a source) and an offer worth a click (a diagnostic, a guide, a demo). |
| Social and organic | A human voice with a point of view (a joke, an identity call-out, "POV:"), candid imagery where the product is the punchline, something people would send to a friend or save. |

## Find the idea first

The winners are remembered for an idea and a line, not for polish. Before choosing a layout, find the idea with one of these moves, and write the headline:

| Move | How it looks |
|---|---|
| The product proves it | One frame where the product has just survived, fixed or beaten something. |
| Call out one person | "For the runners who check the weather three times", said with a wink, over a photo of exactly that person. |
| Personify the problem | The pest, the cold, the paperwork or the bill shown as a character, with a deadpan line. |
| Put the message on a familiar object | A door hanger, a receipt, a parking ticket, a luggage tag or a sticky note carries the copy. |
| The offer is the headline | "Pay nothing until March", "Your first box is on us", set huge, with the deadline. |
| A customer's own words | A real quote or comment as the hook, with the product as the answer. Only real ones. |
| One number that matters to them | Their money, their time, their result, with the source. |
| A surprising, real-looking photo | An animal, a mess, a funny moment, with a dry line that turns it into the benefit. |
| Build the shape from the brand | The product's silhouette, the logo or the brand color becomes the frame or the type. |

Write copy the way a person talks, not the way a brochure does:

- Concrete and specific: "Dry after 3 hours of rain", not "Unbeatable protection".
- The wit carries the benefit; a joke that leaves out the product is wasted.
- A headline of 3 to 9 words, one support line, a button of three words or fewer.
- No slogans any company could sign ("Experience the difference", "Elevate your everyday"), no exclamation marks in a row, no invented numbers.
- In the client's language and voice; match formality and humor to the brand.

## Do not look like an AI template

In a blind test, three judges compared AI-made ads built with this skill against the best real ads from the review. They scored them the same on average, and three AI-made ads ranked in the top five of 32. The judges still picked out every AI-made ad, by these tells. Avoid them:

- **The same structure every time**: a photo, a dark panel at the bottom, a pill button. Vary the layout between concepts: type over the image, type as the image, a split, a poster, a sticker, a note.
- **Flawless pictures**: waxy faces, glossy food, spotless props and perfect symmetry. Ask for real-world imperfection: a scuff on the object, crumbs, uneven light, a lived-in background, food that looks eaten from, not styled for a catalog.
- **Spec lines joined with middle dots** ("Waterproof · Recycled · 480 g") on every ad. Write one plain sentence, or set the points as separate elements.
- **Generic details**: a made-up date or town where none is needed. Real ads carry the brand's real specifics: the phone number, the web address, the store count, a legal line. Use the client's.
- **Everything perfectly aligned and evenly spaced.** One element that breaks the grid (a tilted sticker, a handwritten note, a cropped word) makes a layout feel made by a person.

## Choose two or three archetypes

Pick archetypes from different groups below, so the concepts test different ideas rather than the same ad in new colors. Match them to the goal, the product and what the client's data says has worked (`view-creatives`). For a campaign, `creating-ad-campaigns` explains how to pick them from the client's results.

Each entry gives: when to use it, the layout, the copy slots, how to build it (all in one image with `generate-image`, or composed with `render-design` over a generated picture), the detail that made the best real ads stand out, and what to avoid. Ratios assume a 4:5 feed ad unless stated.

## A. Sell the product

**1. Product demo hero.** When: a product with a visible benefit. Layout: the product large (55 to 65% of the height) doing what it promises, in a real or styled setting; headline top-left; a small logo; a button. Copy: a headline of 2 to 6 words naming the benefit or the audience, one proof line ("5x more durable"), a friction reducer (free shipping, an end date). Build: all in one image, product as `subject`. Best: the product does something unexpected that proves the claim (a glass bottle standing upright and unbroken in a pile of gravel). Avoid: a floating product on a gradient with a spec headline.

**2. Offer first.** When: a sale, a launch price, a free trial, a seasonal promotion. Layout: the offer set huge (15 to 25% of the height) in the accent color; one support line with the deadline or code; the product or a mood image smaller; logo and button at the bottom. Copy: the offer phrased as the buyer's gain ("Save $1,000", "First month free"), the deadline, short terms. Build: composed when the price or terms must be exact. Best: the discount dressed in the brand's world (an elegant serif number on a seasonal texture, a vintage label on a field of the product), or a risk-free offer. Avoid: a teaser with no number, several prices fighting, terms too small to read.

**3. Weekly price ad.** When: grocery, retail, pharmacy and local deals. Layout: 1 to 4 product cut-outs on a clean ground, each with a big price; the store's color bar and logo; the date range. Copy: product names and prices exactly as supplied, "This week only", the dates. Build: composed, always: prices must be exact. Best: one hero deal far larger than the rest, appetizing photography, the brand's color as the frame. Avoid: a dozen small items, clip-art bursts on every product.

**4. Feature callouts.** When: a product with three or four concrete advantages. Layout: the product centered on a plain or real-room background; 3 to 4 short labels around it, each joined to the exact spot by a thin line; a headline on top. Copy: a headline with the problem or the offer; labels of 2 to 4 words with numbers where possible ("24 h cold", "480 g"). Build: composed for exact labels over a generated product photo. Best: few, readable callouts over a rich real-world scene, or the features turned into a picture (a row of products showing how it grows with the user). Avoid: tiny labels on a dark photo, a bullet list under a packshot.

**5. Bundle or flatlay.** When: kits, gift sets, "everything you need". Layout: an overhead shot of the items arranged on a textured surface; numbered tags or labels; the bundle price in a badge. Copy: "Everything you need for ...", the item names, the bundle price. Build: all in one image with the products as `subject` references, labels composed. Avoid: items that do not exist in the client's range.

**6. Catalog frame.** When: one image per product from a feed, many products. Layout: the product photo inside a branded frame: a color border or bottom bar, the logo, the price with the old price struck through, a "% off" badge. Build: composed, one layout rendered per product. Avoid: a different frame per product.

## B. Show the change

**7. Before and after.** When: cleaning, home improvement, beauty, software (the old way and the new way). Layout: a 50/50 split with a thin divider; "Before" and "After" tags in matching corners; identical framing and light, so only the change differs; the result line across the bottom. Copy: the result with its timeframe ("in 14 days"). Build: make the "after" first, then pass it as `edit_base` to make the "before", so the framing matches; compose the tags. Best: the split itself is the drama (a diagonal cut, one object torn in two). Avoid: before-and-after for weight loss and some health claims, which ad platforms restrict, and any result the client cannot prove.

**8. Problem and solution.** When: the product fixes a pain the viewer feels. Layout: the frustration shown large (tangled cables, a messy inbox, a cold room), a question headline, and the product small in a corner with "There is a fix". Copy: the pain in the buyer's words ("Still waking up at 3 am?"). Build: all in one image. Avoid: fear-based "alert" layouts.

**9. Us versus them.** When: a clear advantage over the usual alternative. Layout: two columns; the brand's product with a brand-color header on the left, "the usual way" in grey on the right; 4 to 6 rows with checks and crosses. Copy: a title ("Not all X are equal"), short attributes. Build: composed, so the rows are exact. Best: the viewer can pick a side in one second; honest, specific attributes. Avoid: naming or showing a competitor's brand or product, unless the client confirms it is allowed.

## C. Proof

**10. Testimonial.** When: the client has a real review or quote. Layout: one quote set large in quote type with personality (an elegant italic, a handwritten note), the reviewer's first name and initial, the product nearby or a real-looking photo of it in use. Copy: the quote word for word, 15 to 35 words with the key phrase bold. Build: composed. Best: a voice with personality and a specific, funny or relatable quote; real-looking customer content. Avoid: inventing a review, a rating or a name; generic praise in a template card.

**11. Big number.** When: one statistic that matters to the viewer. Layout: the number at 30 to 40% of the height in the accent color; a qualifier line under it; the source in small type; a small product or logo. Copy: the number, what it means for the viewer, the source and year. Build: composed. Best: a number about the viewer's own wallet or life, or set like a fine book page in serif numerals; a product-shaped chart (a battery whose cells are the bars). Avoid: brag numbers about the company.

**12. Social proof stack.** When: many real reviews or a strong rating. Layout: 3 to 5 short real review snippets offset around the product; the aggregate rating as the headline. Build: composed. Avoid: any review or rating the client does not have.

**13. Results post.** When: a client success or a monthly result for a report, LinkedIn or a case study. Layout: a headline with the outcome, a small real chart or three numbered points, the logo. Copy: real numbers from the data with the period. Build: composed, chart in inline SVG. Avoid: a chart drawn by the image model.

## D. Native and creator formats

**14. Creator frame.** When: TikTok, Reels, Stories, younger audiences, products that show well in hand. Layout: a candid phone-camera photo (a real room, imperfect light) of a person holding or using the product; a caption box in the platform's text style with a first-person hook. Copy: a hook that promises a result or asks a question ("POV: you finally found a jacket that ..."), ideally with a timeframe. Build: all in one image; state the pose and both hands. Best: the product is clearly in shot and is the punchline. Avoid: app buttons, usernames, like counts, and a joke that never mentions the product.

**15. Note, chat or handwritten sign.** When: a personal, low-key voice; "reasons I switched"; a founder's note. Layout: a plain note page, a chat between two friends, or a sticky note or cardboard sign in a real scene, written in the brand's own voice. Copy: a short list or exchange that names the benefit. Build: composed for the note and chat; all in one image for a sign in a scene. Avoid: copying a specific app's interface and logo, fake engagement numbers, and a "real customer" chat that did not happen.

**16. Comment reply.** When: the client has a real comment or question from a customer. Layout: the comment in a neutral speech bubble as the hook; the answer as the image (a demo, the product). Build: composed. Avoid: inventing the comment or its likes.

## E. Story and lifestyle

**17. Lifestyle with a hook.** When: brand and performance for consumer products and services. Layout: a full-bleed photo of the product in use with deliberate empty space on one side; the headline in that space with a soft gradient for contrast; a small logo. Copy: a precise headline that talks to one person (an identity call-out, a question, a short story that ends in a number). Build: all in one image, or composed over the photo. Best: the photo and the headline share a tone (a deadpan line over a funny real photo). Avoid: generic stock smiles and slogans like "Explore more".

**18. Founder letter.** When: a new brand, a mission, a recovery after a problem. Layout: an authentic photo of the founder (only from a photo the user uploaded) beside a letter on paper texture, signed. Build: composed. Avoid: a generated face presented as the real founder.

**19. Visual metaphor.** When: brand awareness, services that are hard to show (finance, insurance, software). Layout: one everyday object that carries the whole message on a quiet field, very little type. Copy: one line that names the benefit. Build: all in one image. Best: an idea only this category could own (a seat belt buckled around a piggy bank for an insurer). Avoid: borrowed spectacle such as epic AI landscapes.

## F. Information

**20. Listicle.** When: education, saves on Instagram and Pinterest, considered purchases. Layout: "5 reasons ..." at the top; a numbered list with large numerals in the accent color on one half; the product or a photo on the other half. Copy: 3 to 5 items of 3 to 7 words each. Build: composed. Avoid: a generic list in corporate colors with no product and no next step.

**21. How it works in three steps.** When: a process, an app, a service. Layout: three numbered steps in a row or column, each an icon or small image and 2 to 5 words, connected by arrows, ending in the result. Build: composed, icons in SVG.

**22. Myth versus fact.** When: an objection stops people from buying. Layout: a split or a carousel; "Myth" with the objection, "Fact" with the answer and proof. Build: composed.

## G. Formats with their own rules

**23. Typographic statement.** When: a bold voice, a pun, a local claim, a deadline. Layout: type only, set large on a brand-color field, perhaps one small image. Copy: one line of 3 to 9 words that carries a pun, a pain in plain words, or an offer with a deadline. Build: composed for a brand font, or all in one image. Best: total confidence in the line and a setting that matches it (a bakery's "Open at 6. Sold out by 9." in a big serif on flour white). Avoid: mission statements and slogans with no reason to act.

**24. Event poster or flyer.** When: concerts, festivals, talks, sports, store events. Layout: the event's identity built into the shape (the edition number made from the instruments, the venue's silhouette cut from a pattern); then what, when, where and the price, all exact; a ticket button for paid placements. Copy: the event name, date, venue, price, deadline or places left. Build: all in one image for art-led posters, composed for exact details. Best: print texture (risograph grain, halftone, painted portraits) and real emotion; a reason to buy now. Avoid: templates with a stack of logos and a long line-up in small type.

**25. Food and menu.** When: restaurants, delivery, food brands. Layout: the indulgent moment large and close (melting cheese, an overhead platter); the dish name or the offer short and large; a small round badge with an easy or free promise. Copy: dish names and prices exactly as supplied. Build: all in one image for a hero dish, composed for a menu. Best: warm texture and trend colors; recipe-card framing. Avoid: starbursts and banners on top of the food.

**26. Property listing.** When: real estate sales and rentals. Layout: one perfect view (a sunlit window onto a landmark, the living room at golden hour) with quiet serif type; the decision facts (rooms, size, price band) in one line; a viewing button. Build: only from the client's real property photos, edited (light, sky, staging) with `edit_base`; never a generated property presented as real. Avoid: annotated maps and badge-covered renders.

**27. Recruitment.** When: hiring. Layout: a real employee photo (uploaded) or a lifestyle scene of the benefit; the role, the location and one concrete incentive set large; an apply button. Copy: the named role, the salary or bonus, the schedule. Best: the job shown as a life (a driver at the school gate at 3 pm, because the shifts end at 2). Avoid: stock handshakes and job-description text blocks.

**28. Software and app proof.** When: SaaS and apps. Layout: the buyer's pain as the headline in their own words, then the product screen showing a result (a chart going the right way, a finished step) in the brand's colors. Copy: the role or platform called out in the first line, a low-commitment offer (a diagnostic, a demo). Build: composed, with the client's real screenshot as an image, or a clean UI drawn in HTML with the client's real figures. Avoid: a generic dashboard, a stock hand holding a phone, invented numbers on the screen.

## Display banners

Design each banner size on purpose: one image, one short line, one button and a small logo. Keep the subject away from the edges. A banner that simply shrinks a feed ad loses the proof and the button. Google display and Performance Max images carry no text at all; their copy goes into the text assets.

## Before you show the concepts

For each concept, say in one line which archetype it uses and why it fits this goal and audience. Check it against the eight points at the top: one idea, the product proving the claim, one person addressed, a specific offer, proof, native feel, ownable, and designed for its size. Then run the checks in `generating-images`.
