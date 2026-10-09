---
name: creating-ad-campaigns
type: workflow
description: Plan and produce a complete, on-brand ad campaign from the client's brand and their real ad results across every connected channel. Covers the brand kit (from the website when possible), what has worked in Meta, Google, TikTok, LinkedIn, Pinterest and Snapchat, 2 to 4 concepts built on proven ad archetypes with copy and a test hypothesis, finished ads in every placement, names that bring the results back, a board to present them, and refreshes of tired ads. Use when the user asks for ad concepts, new creatives, a campaign, variants to test, ads "like our best ones", or a refresh of tired ads. Load `designing-ad-creatives` for the layouts and `generating-images` for the image work.
required_tools:
  - generate-image
  - view-creatives
optional_tools:
  - tool_name: render-design
    purpose: Lay out exact copy, prices, logos and charts over generated pictures, and render every placement from one layout.
  - tool_name: list-reports
    purpose: Find a report with media widgets that shows the client's ads.
  - tool_name: list-widgets
    purpose: Find the media widgets and pull ad-level numbers with csv_export.
  - tool_name: list-sources
    purpose: Find the client's ad accounts on every channel and the ad-level fields they expose.
  - tool_name: fetch-data
    purpose: Pull ad-level results (spend, CTR, CPA, ROAS) for the period.
  - tool_name: list-themes
    purpose: Read the brand colors, fonts and logo of the client's report theme.
  - tool_name: list-assets
    purpose: Find the client's logo and product photos.
  - tool_name: search-assets
    purpose: Find brand files in the team library by description.
  - tool_name: manage-assets
    purpose: Import a logo or product photo from the client's website, and publish the finished ads.
  - tool_name: create-document
    purpose: Build the campaign board that presents the concepts.
---

# Creating ad campaigns

A strong answer to "make us some new ads" looks like this:

> Here is what has worked across your channels and why. Here are three new concepts built on it, each testing one idea. Each one is a finished ad in feed, story and landscape, with the headline, primary text and button. Everything is on one board you can send to the client, and every ad is named so its results come back into Whatagraph.

Whatagraph can do what ad tools cannot: it sees the client's real ads next to their real results on every channel at once. Meta's tools learn only from Meta, and Google's only from Google. Use that. Every concept should say which proven pattern it builds on, or which untested idea it tries, and what it tests.

Load `designing-ad-creatives` (the archetypes and what makes ads win) and `generating-images` (the spec, the composed designs, the checks) before the first image. This skill decides what to make and in what order.

## 1. Build the brand kit

Collect it once per client and save it as a memory note named "Brand kit: <client>", so the next campaign starts from it.

- **From the website**, when you have web access: the logo, the color palette as hex codes with roles (background, text, accent), the fonts (from the page styles), hero product photos, prices, current offers, guarantees, shipping and return terms, the tone in 3 to 7 words, and the phrases customers use in reviews. Import the logo and product photos with `manage-assets` (load `whatagraph-assets` first).
- **From Whatagraph**: the report theme (`list-themes`), the team library (`list-assets`, `search-assets`) and the current ads (`view-creatives`).
- **From the user**: anything missing that matters, in one question.

Write fonts as a Google Font name or a style ("a heavy condensed sans", "a refined lowercase serif"). Note anything the brand always does (a color band, a sticker, a photo style). Claims, prices and reviews go in the note word for word with their source. If there is no logo, set the brand name as a wordmark and say it is a placeholder. Never invent a logo for a real client.

## 2. Find what has worked, on every channel

Skip this only for a brand-new client with no ads.

1. Pick the KPI: the user's, or the account's obvious one (ROAS or CPA for e-commerce and leads, CTR or cost per thousand for awareness).
2. Pull ad-level results for the last 30 to 90 days from every connected ad channel (`list-sources`, then `fetch-data` with each channel's ad dimension, or `list-widgets action=csv_export` on a report's ad tables). `fetching-marketing-metrics` has the mechanics.
3. Keep the ads with meaningful spend. Take the top five and the bottom five by the KPI per channel.
4. Look at them with `view-creatives` (`generating-marketing-insights` has the creative analysis framework). Tag each one: the archetype from `designing-ad-creatives`, the idea move, the hook, the image type (product, person, lifestyle, creator, graphic), the offer, the text density and the format.
5. Compare by tag: which archetypes, hooks and offers show up among the winners and not among the losers, and on which channel. With enough ads, report a hit rate: the share of a tag's ads that beat the account's median KPI.
6. Save the findings to the memory note "Creative memory: <client>" with the numbers, and update it after each campaign.

State findings as observations with numbers ("all three of the best ads by ROAS on Meta and TikTok show the jacket worn outdoors in bad weather; the two studio packshots have the highest CPA"). Do not claim a cause the data cannot show.

## 3. Write the concepts

Propose 2 to 4 concepts, each a different archetype and idea, not the same ad in a new color. Meta's delivery groups ads that look alike and treats them as one, so small tweaks do not get tested. Mix:

- **Iterate the winner**: the same idea with a new hook, the same hook with a new image, or the same concept in a new archetype.
- **White space**: an archetype or angle the account has never tried, chosen for the goal and the audience.

For each concept write:

- **Name**, **archetype** and **idea** (one line from "Find the idea first" in `designing-ad-creatives`), with the three headline options you considered and why the chosen one wins.
- **Builds on**: the winning pattern from step 2 with its number, or "white space" and why.
- **Hypothesis**: the one thing it tests ("an offer-first ad beats the lifestyle ad for cold audiences").
- **Style and mode**: the style from `generating-images`, and whether it is built all in one image or composed.
- **Copy, written before any image**: the words in the image (a headline of 3 to 9 words, the proof, the offer, a button of three words or fewer) and the platform's text fields:

  | Platform | Fields |
  |---|---|
  | Meta | Primary text up to 125 characters before the "more" cut, headline about 27 characters, description, call-to-action button. |
  | Google display and Performance Max | Short headlines of 30 characters, a long headline of 90, descriptions of 90, business name. The images carry no text. |
  | LinkedIn | Introductory text up to 150 characters, headline up to 70. |
  | TikTok | Ad text up to 100 characters; the words in the image or video do the work. |
  | Pinterest | Title up to 100 characters, description up to 500; text on the pin itself short and large. |

  When the client has written ads before, use their best-performing copy as the model for tone and length.

Keep the brand system fixed across concepts, so the campaign reads as one brand.

## 4. Produce the ads

1. **Pictures first.** Without a product photo, make one packshot and use it in every concept, so the product is identical. Make the pictures each concept needs: one-image ads with the full spec, or text-free pictures with empty space for composed designs. Use `standard` quality.
2. **Master per concept** at 4:5, with the logo and product as references or as the client's own image files in a composed layout.
3. **Check it** with the checks in `generating-images`: bodies, every word, logo and product, counts, safe zones, claims, then the design. Fix with an edit or with the layout.
4. **Every placement.** Composed: render the same layout for 1080x1920 (story and reel, text out of the top 14%, the bottom 35% and the sides), 1080x1080, 1200x628 and any banner sizes. One-image: adapt the approved master with `edit_base` and the new ratio. For Google display and Performance Max, make text-free versions and deliver the copy as text assets.
5. **Variants.** For a test, change one thing per variant (the headline, the image or the offer), so a result can be read.
6. **Name every ad so its results come back**: `<client>_<campaign>_<concept>_<archetype>_<placement>_v<n>`, for example `northpeak_firstsnow_c2_offerfirst_9x16_v1`. The name appears in Whatagraph's ad-level data, so the next campaign can read which concept, archetype and placement won.
7. **Credits.** Generated images cost credits; renders do not. Three concepts in four placements is about twelve images, fewer when composed. Ask before going beyond that, and use `draft` for exploration.

## 5. Present the campaign

1. Publish the finished ads with `manage-assets action=publish`.
2. Build one board with `create-document`: an HTML page in the client's colors. Start with the brand kit and what has worked, with the numbers. For each concept show the name, archetype, idea, hypothesis and what it builds on; the ads in each placement (`<img>` with the published URLs); and the headline, primary text and button as copyable text. End with a test plan: which concept runs first, the budget split, the KPI that decides, and when to read the result.
3. In the chat, give the three-line summary: what has worked, the concepts, and the next step.

Offer the next steps: translations, one version per location, more variants of the strongest concept, or a creative report that tracks the new ads by their names once they run.

## Refreshing tired ads

When the user asks for a refresh, or a review shows an ad tiring (CTR falling for two or more weeks while frequency rises, or CPA rising at a steady budget), start from that ad. Keep what made it win (the idea, the hook, the product shot) and change the most-seen element: the image, the scene, the color or the archetype. Make two or three refreshes and name them as new versions of the original. An agent schedule can run this review every month and propose refreshes before results fall.

## Rules

- Prices, claims, results, reviews, ratings and legal text come from the user, the website or the data, word for word, with their source in the brand kit note.
- No fabricated proof: no invented reviews, ratings, customer comments, press logos, statistics or endorsements. See "Rules you must not break" in `generating-images`.
- Comparisons show "the usual way", never a named competitor or its product, unless the client confirms it is allowed.
- Follow platform policies: before-and-after and personal-attribute rules on Meta, and health, finance, housing and employment restrictions.
- An ad that could pass for a real photo is AI-generated. Tell the client, because platforms label AI content and some regions require it on ads (for example the EU AI Act transparency rules from August 2026).
- Call the work concepts until the client approves them.
