---
name: creating-ad-campaigns
type: workflow
description: Plan and produce a complete, on-brand ad campaign from the client's brand and their real ad results. Covers the brand kit, what is working in their account now, 2 to 4 concepts with copy and a test hypothesis, finished ads in every placement, and a board to present them. Use when the user asks for ad concepts, new creatives, a campaign, variants to test, ads "like our best ones", or a refresh of tired ads. Load `generating-images` for the image work.
required_tools:
  - generate-image
  - view-creatives
optional_tools:
  - tool_name: list-reports
    purpose: Find a report with media widgets that shows the client's ads.
  - tool_name: list-widgets
    purpose: Find the media widgets and pull ad-level numbers with csv_export.
  - tool_name: list-sources
    purpose: Find the client's ad accounts and the ad-level fields they expose.
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

> Here is what is working in your account right now and why. Here are three new concepts built on it, each with a hypothesis to test. Each one is a finished ad in feed, story and landscape, with the headline, primary text and button. Everything is on one board you can send to the client.

Whatagraph can do what a generic image tool cannot: it can see the client's real ads next to their real results. Use that. Every concept should say which current ad or pattern it builds on, and what it tests.

Load `generating-images` before the first image. It has the creative spec, the styles, the format playbook and the resizing recipe. This skill decides what to make; that one decides how to render it.

## 1. Build the brand kit

Collect it once per client, and save it as a memory note named "Brand kit: <client>" so the next campaign starts from it.

- **Logo and product photos:** `list-assets` or `search-assets` in the team library, or ask the user. With web access, read the client's website and import the logo and product images with `manage-assets` (load `whatagraph-assets` first).
- **Colors and fonts:** the client's report theme (`list-themes`), their current ads, or their website. Write colors as hex codes with a role (background, text, accent) and fonts as a style ("heavy condensed sans", "refined lowercase serif").
- **Voice and visual style:** read three or four current ads and the website. Note the tone (playful, premium, technical), the imagery (people, product, illustration) and anything the brand always does (a color band, a sticker, a photo style).
- **Offer facts:** products, prices, current offers, shipping and return terms, and claims the client can stand behind. Only use what the user, the website or the data states.

If there is no logo, set the brand name as a wordmark and say it is a placeholder. Never invent a logo for a real client.

## 2. Find what is working

When the client's ad accounts are connected, ground the campaign in their results. Skip this step only for a brand-new client with no ads.

1. Pick the KPI: the user's, or the account's obvious one (ROAS or CPA for e-commerce and leads, CTR for awareness).
2. Pull ad-level results for the last 30 to 90 days: spend, impressions, CTR, conversions, CPA or ROAS. Use `fetch-data` with the channel's ad dimension, or `list-widgets action=csv_export` on a report's ad table. `fetching-marketing-metrics` has the mechanics.
3. Rank the ads by the KPI among those with real spend, and take the top three to five and the bottom three.
4. Look at them with `view-creatives` on a report with media widgets (`generating-marketing-insights` has the creative analysis framework). If no report has a media widget for the channel, say so and work from the brand kit.
5. Write down what the winners share and the losers lack: the hook, the image type (product, person, lifestyle, UGC), the offer, the text density, the format, the colors.

State findings as observations with numbers ("the three best ads by ROAS all show the jacket being worn outdoors; the two studio packshots have the highest CPA"). Do not claim a cause the data cannot show.

## 3. Write the concepts

Propose 2 to 4 concepts. Each one is a different angle, not the same ad in a new color. Meta's delivery system groups ads that look alike and treats them as one, so small tweaks do not get tested:

| Angle | The ad says |
|---|---|
| Benefit | What the product does for you. |
| Problem and solution | The pain, then the fix. |
| Proof | A number, a result, a review the client can stand behind. |
| Offer | The deal and its deadline. |
| Emotion or identity | Who you become, or the feeling. |
| Native or creator | A real person talking, in a social-native look. |

For each concept write:

- **Name** and **angle**.
- **Builds on:** the winning pattern or ad from step 2, with its number.
- **Hypothesis:** the one thing it tests ("a price-led headline beats a benefit headline for the same image").
- **Style:** from the style table in `generating-images`, matched to the brand.
- **Copy, written before any image:** the words in the image (a headline of 7 words or fewer, proof points, the offer, a button of 3 words or fewer), and the platform's text fields:

  | Platform | Fields |
  |---|---|
  | Meta | Primary text up to 125 characters before the "more" cut, headline about 27 characters, description, call-to-action button. |
  | Google display and Performance Max | Short headlines of 30 characters, a long headline of 90, descriptions of 90, business name. The images carry no text. |
  | LinkedIn | Introductory text up to 150 characters, headline up to 70. |
  | TikTok | Ad text up to 100 characters; the words in the video or image do the work. |

  When the client has written ads before, use their best-performing copy as the model for tone and length.

Keep the brand system fixed across concepts so the campaign reads as one brand.

## 4. Produce the ads

1. **Master first.** For each concept, render the master at 4:5 (or 1:1) with the full creative spec. Pass the logo and the product as references. Use `standard` quality.
2. **Check it** against the checklist in `generating-images`, and fix it with an `edit_base` call when needed.
3. **Every placement.** Adapt each approved master with the resizing recipe: 9:16 for stories and reels (text out of the top 14%, the bottom 35% and the sides), 1:1 for the square feed, 16:9 for LinkedIn, wider banners on request. For Google display and Performance Max, make text-free versions of the image and deliver the copy as text assets.
4. **Variants.** For a test, change one thing per variant (the headline, the image, or the offer) with an `edit_base` call, so a result can be read.
5. **Name every ad so its results come back.** Give each ad a name the client uses when uploading it: `<client>_<campaign>_<concept>_<angle>_<placement>_v<n>`, for example `northpeak_firstsnow_c2_offer_9x16_v1`. The ad name then appears in Whatagraph's ad-level data, and the next campaign can read which concept, angle and placement won.
6. **Credits.** Three concepts in four placements is twelve images. Ask before going beyond that, and use `draft` for exploration.

## 5. Present the campaign

1. Publish the finished ads with `manage-assets action=publish`.
2. Build one board with `create-document`: an HTML page in the client's colors. For each concept it shows the name, the angle, the hypothesis and what it builds on. Below that come the ads in each placement (`<img>` with the published URLs), and then the headline, primary text and button as copyable text. End with a short test plan: which concept to run first, the budget split, and the KPI that decides.
3. In the chat, give the three-line summary: what is working, the concepts, and the next step.

Offer the next steps: translations, one version per location, more variants of the strongest concept, or a creative report that tracks the new ads by their names once they run.

## Refreshing tired ads

When the user asks for a refresh, or a review shows an ad tiring (CTR falling for two or more weeks while frequency rises, or CPA rising at a steady budget), start from that ad. Keep what made it win (the hook, the angle, the product shot) and change the most-seen element: the image, the scene or the color. Make two or three refreshes and name them as new versions of the original. An agent schedule can run this review every month.

## Rules

- Prices, claims, results, reviews and legal text come from the user, the website or the data, word for word.
- No competitor logos, and no fake reviews, screenshots or endorsements. See "Rules you must not break" in `generating-images`.
- Call the work concepts until the client approves them.
- An ad that could pass for a real photo is AI-generated, and the client must be able to say so where the platform requires it.
