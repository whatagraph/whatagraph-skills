---
name: generating-videos
type: domain
group: team_workspace_branding
description: Make short videos with exact text, as finished MP4 files. Instagram and Facebook Story and Reels ads (9:16), feed videos (4:5 and 1:1), animated offer posts, motion versions of static ads, animated covers and short promos. render-video records an animated HTML layout, with the copy, prices, legal lines and the client's real logo exactly as written, optionally over a Veo clip from generate-video that animates the client's own product photo. Use whenever the user wants a video, a Story or Reels ad, an animated ad or a motion version of an image. Load `designing-ad-creatives` for the idea and the copy, and `generating-images` for any still you need first.
required_tools:
  - render-video
optional_tools:
  - tool_name: generate-video
    purpose: Turn a still, usually the client's product photo, into a 4 to 8 second clip with camera motion and sound, to lay the animated text over.
  - tool_name: generate-image
    purpose: Make a still to animate or to use as the background when the client has no suitable photo and the product need not be exact.
  - tool_name: manage-assets
    purpose: Publish a finished video so an HTML document can play it, or import the client's photo from a URL.
  - tool_name: view-creatives
    purpose: Find the client's best current ad or product photo to turn into a video.
  - tool_name: list-assets
    purpose: Find the client's logo, product photos or an earlier clip.
  - tool_name: search-assets
    purpose: Find a photo in the team library by description.
  - tool_name: create-document
    purpose: Build an HTML page or board that plays the published videos.
---

# Generating videos

Tools covered: `render-video`, `generate-video`.

- `render-video` records an HTML and CSS layout with CSS animations as an MP4 of an exact size and length. Text is real type, the logo and the product are the client's own pixels, and every price and legal line is exactly what you write. It costs no AI credits.
- `generate-video` makes a 4 to 8 second clip with sound from a prompt, usually by animating a still you pass as `start_image`. It costs far more than an image, takes one to two minutes, and is not offered to every team; check your tool list.

Most video ads that agencies run are not generated films. They are a real photo with a few moving elements, exact text and an end card with the offer. Build that first. Add a `generate-video` clip when real camera motion, light or weather would make the ad better, and never as a way to invent the product.

## Use this when

- A Story or Reels ad, or a set of them for several offers, cities or languages.
- A motion version of a static ad that already works. Find it with `view-creatives` or the client's report data.
- An animated offer post, a countdown, a short promo, an animated report cover or a results post with numbers that count up.

## Pick the path

| The client has | The product must be exact | Path |
|---|---|---|
| A good product photo | Yes (a car, a bottle, a phone screen) | **A. Photo motion**: `render-video` with the photo, a slow zoom and animated text. No model cost. |
| A good product photo | Yes, and the ad needs real camera motion or light | **B. Veo from the photo**: `generate-video` with the photo as `start_image`, then `render-video` over the clip. |
| No photo | No (a mood, a place, a service) | **C. Generated still**: `generate-image`, then path A or B. |
| No photo | Yes | Ask for a photo. Do not generate the product. |

Never ask `generate-video` to show a branded product it has not been given. Asked for an "unbranded" car, Veo put badges that look like Volkswagen's and Opel's on it, in three tests out of three, even with a negative prompt. A clip with another brand's logo cannot be published.

One clip serves every version. The text is in the HTML, so make one clip per photo and render each offer, city or language over the same clip.

## Path B: write the clip prompt

The prompt describes motion, light and sound. It never describes text, prices or logos, because those come from the HTML.

```
generate-video prompt="Animate this photo as a premium car commercial shot: a slow, smooth dolly push-in toward the car with a slight arc to the right. Reflections glide across the paint and the glass; the background stays still. Keep the car exactly as it is in the image, with the same shape, color, wheels and details. No text, no logos, no people. Sound: a quiet, modern ambient tone." start_image={"asset_ulid": "<photo>"} negative_prompt="text, logos, people, distorted wheels" title="Showroom push-in"
```

- Say "keep the [product] exactly as it is" whenever there is a `start_image`.
- One camera move per clip: push-in, pull-out, slow orbit, pan, or a locked camera with moving light, rain or steam. A hook is a change in the first second: a light switching on, rain starting, a door opening.
- Leave room for the text: the photo should have calm space in its upper half for a Story ad.
- `duration_seconds` 8 and `resolution` 1080p by default. 1080p needs 8 seconds; use 720p for 4 or 6. `quality` "draft" is a cheaper model for a motion test at 720p; it ignores `negative_prompt`.
- Cost at list price: an 8 second 1080p clip is about $0.96 at "standard" and $0.64 at "draft". A 4 second 720p draft is about $0.20.
- You get six frames of the clip back. Check that the product kept its shape and has no new logo or text before you build on it. If it changed, try once more with a simpler camera move, then fall back to path A.

## Write the animated layout

One HTML document with a `<style>` block, sized to the video. CSS `@keyframes` with `animation-delay` and `animation-fill-mode: both` do all the motion. JavaScript does not run, and a page with a `<script>` is refused. Fonts load from Google Fonts; every image comes in `images` as `{{image_1}}`, `{{image_2}}` and so on.

Over a clip (path B), leave `html` and `body` without a background: the page is laid over the clip and only its transparent parts show it. Draw scrims, gradients behind the text, as their own elements.

**Meta safe zones for Stories and Reels at 1080 x 1920.** Keep all text, logos and the button out of the top 14% (above y = 270), the bottom 35% (below y = 1248) and 6% on each side (65 px). Instagram draws its profile row, reply box and buttons there. The headline, offer, button and legal line all fit between y = 280 and y = 1240.

**A timeline that works for an 8 second Story ad:**

| Time | What happens |
|---|---|
| 0 to 0.5 s | The picture alone, already moving. The first frame must already show the product. |
| 0.3 to 1.5 s | Kicker and headline rise in, line by line. The brand is visible by 2 seconds. |
| 1.5 to 2.5 s | The offer or price pops in, the biggest number on screen. |
| 2.5 to 5 s | One supporting line (a term, a benefit, a proof). |
| 5 to 8 s | End card: a scrim fades in, then the brand name, the button and the legal line, held for at least 2.5 seconds. |

Stories show a video up to 15 seconds long in one card. Keep the message within that.

```
<html><head>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif}
.photo{position:absolute;inset:0;background:url({{image_1}}) center 70%/cover;animation:zoom 8s linear both}
.scrim{position:absolute;left:0;right:0;top:0;height:900px;background:linear-gradient(rgba(6,14,28,.6),rgba(6,14,28,0));animation:fade .6s both}
.top{position:absolute;left:72px;right:72px;top:380px}
.kicker{color:#ffd27a;font:700 30px Inter;letter-spacing:.14em;text-transform:uppercase;animation:rise .7s .25s both}
h1{margin:22px 0 30px;color:#fff;font:900 104px/.98 Archivo;text-transform:uppercase}
h1 span{display:block;animation:rise .8s .45s both}
h1 span:nth-child(2){animation-delay:.65s}
.price{color:#fff;font:600 32px Inter;animation:pop .7s 1.5s both}
.price strong{font:900 92px Archivo;color:#ffd27a}
.end{position:absolute;left:0;right:0;bottom:0;height:1000px;background:linear-gradient(to top,rgba(6,14,28,.92) 40%,rgba(6,14,28,0));animation:fade .6s 5s both}
.brand{position:absolute;left:72px;top:972px;color:#fff;font:700 34px Archivo;animation:rise .6s 5.2s both}
.cta{position:absolute;left:72px;top:1026px;padding:26px 48px;border-radius:48px;background:#ffd27a;color:#0b1424;font:700 40px Inter;animation:rise .6s 5.35s both}
.legal{position:absolute;left:72px;right:72px;top:1146px;color:rgba(255,255,255,.82);font:400 21px/1.35 Inter;animation:fade .6s 5.6s both}
@keyframes zoom{from{transform:scale(1)}to{transform:scale(1.12)}}
@keyframes rise{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:none}}
</style></head><body>
<div class="photo"></div><div class="scrim"></div>
<div class="top"><div class="kicker">Test drive weekend</div><h1><span>Meet the new</span><span>crossover.</span></h1>
<div class="price">from <strong>€249</strong> / month</div></div>
<div class="end"></div><div class="brand">NORTHLINE MOTORS · KLAIPĖDA</div><div class="cta">Book a test drive</div>
<div class="legal">Example: 36 months, 10,000 km a year, €2,990 down payment. WLTP combined 5.4 l/100 km, CO₂ 122 g/km.</div>
</body></html>
```

```
render-video html="<the layout>" width=1080 height=1920 duration_seconds=8 images=[{"asset_ulid": "<photo>"}] title="Test drive weekend story"
```

For path B, drop `.photo` and pass the clip instead: `background_video_asset_ulid=<clip asset_ulid>`. The clip's sound is kept; pass `mute=true` to drop it.

The design rules of `generating-images` still apply: one display face and one text face, the headline the largest thing after the product, the price in the accent color, no pills, badges, card shadows or checkmark lists, and a logo at least 15% of the width.

## Legal lines, labels and claims

- Every price, rate, term, consumption figure and legal sentence comes from the user, word for word. If the user has not given the legal line for an offer, ask for it, or render it with a clear placeholder and say so. Never invent figures.
- Car ads in the EU must show the official WLTP fuel or energy consumption and CO₂ emissions. Germany also requires the CO₂ class (A to G) on screen, and a link is not enough. France requires one of three set mobility messages, the hashtag #SeDéplacerMoinsPolluer and the CO₂ class. Ask which market the ad runs in.
- A finance offer that shows a rate or a monthly price needs its standard credit information. From 20 November 2026 EU credit ads also carry a warning such as "Borrowing money costs money". Hold the legal line on the end card for at least 2.5 seconds.
- When the video contains a generated clip or a generated image, show a small "AI generated" label inside the safe zone (top right, below y = 270) and say so in the legal line. Meta adds its own "AI info" label from the file's metadata as well.

## Check every video before you show it

Both tools return six frames from the first to the last. Check:

1. The first frame already shows the product, not an empty or black screen.
2. Every line of text is inside the safe zone, readable, and spelled exactly as given.
3. The price and the button are on screen together on the end card, and the legal line is complete.
4. Nothing overlaps: a headline wrapping to a third line is the usual cause. Shorten it or reduce the size, then render again.
5. Over a clip: the product has not changed shape and no new text or logo appeared.

Then tell the user what you made: the file name, size and length, and what it cost (the `credits_used` of each `generate-video` call; `render-video` costs nothing).

## Versions and sizes

- One idea, several offers or languages: keep the clip and the layout, change only the text, and render each version with its own `title`.
- Feed placements: render the same layout at 1080 x 1350 (4:5) and 1080 x 1080 (1:1). Change only the CSS; keep text out of the outer 6% on every side.
- A video without a clip has no sound. Say so: the user can add music from Meta's licensed library in Ads Manager. More than three quarters of Reels are watched with sound on, so a clip's own sound is worth keeping.

## Putting a video somewhere

A video is private to the conversation until you publish it. `manage-assets` runs only after the `whatagraph-assets` skill is loaded in the conversation:

```
manage-assets action=publish asset_id=<asset_ulid>      → {"url": "<public_url>"}
```

In an HTML document, play it with `<video src="<public_url>" controls playsinline muted loop preload="metadata"></video>`. A document plays only published Whatagraph videos; a video that is not published, or any other URL, stays blank. Autoplay works only together with `muted`. To show a set of Story ads, put each in a 9:16 phone frame with its title and what it cost.

## What it cannot do

- Real footage of the client's product in motion. A clip animates a still; it does not film anything.
- Talking people, voice-overs or lip-sync, and anyone real. Never a celebrity or public figure.
- Editing a video the user uploads.
- Music to order. A clip has the sound Veo makes for the scene.
- `generate-video` for teams whose AI processing must stay in the EU. `render-video` calls no AI model, so path A works for them.
