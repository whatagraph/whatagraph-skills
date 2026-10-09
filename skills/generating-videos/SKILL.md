---
name: generating-videos
type: domain
group: team_workspace_branding
description: Make finished video ads as MP4 files, with real-looking footage, speech, voice-over, music and exact text. Instagram and Facebook Story and Reels ads (9:16), feed videos (4:5 and 1:1), creator testimonials, product films, unboxing videos, venue and travel montages, property tours, dealer offers, and motion versions of static ads. generate-video shoots each shot as live-action footage with its own sound and speech, generate-voiceover and generate-music make the voice and the music, and render-video cuts the shots together, mixes the sound and lays the copy, prices, legal lines and the client's real logo on top exactly as written. Use whenever the user wants a video, a Story or Reels ad, a video ad for any business, an animated ad or a motion version of an image. Load `designing-ad-creatives` for the idea and the copy, and `generating-images` for any still you need first.
required_tools:
  - render-video
optional_tools:
  - tool_name: generate-video
    purpose: Shoot one shot of the ad as a 10 second live-action clip with sound, including people speaking, from a prompt, a first frame or reference photos.
  - tool_name: generate-voiceover
    purpose: Record the voice-over from a script, with the pauses timed for captions.
  - tool_name: generate-music
    purpose: Make a 30 second instrumental music bed for the ad.
  - tool_name: generate-image
    purpose: Make the reference photo of a person or product that must look the same in every shot, or a still for a template-motion ad.
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

Tools covered: `generate-video`, `generate-voiceover`, `generate-music`, `render-video`.

- `generate-video` shoots one shot: a 10 second live-action clip at 1080 x 1920 with its own sound, such as a room, a sizzling pan or a splash. When you write the words, the person in it speaks them, with matching lip movement. It takes about a minute and costs about 155 credits at 1080p (100 at 720p).
- `generate-voiceover` performs your script with a professional voice, including the laughs, sighs and pauses you write into it, in a few seconds, for under 1 credit.
- `generate-music` makes a 30 second instrumental track for 4 credits.
- `render-video` cuts the shots together, mixes their sound with the voice-over and the music, and lays your HTML on top: the text, captions, logo and end card, exactly as written. It costs no credits except a fraction of a credit to read back what is said.

The video tools are not offered to every team; check your tool list. Teams whose AI processing must stay in the EU have only `render-video`, so they get template motion (the last section).

## Pick the format

Formats in the order they win on Meta (Motion's 2025 library): unboxing, offer, demo, testimonial, before and after. Pick by the business and what the client has.

| Business | Format | The four shots |
|---|---|---|
| Online shop: beauty, fashion, gadgets | **Creator testimonial** | The creator says the hook to camera · the product in use · a close-up detail · the creator says the offer |
| Online shop, subscription | **Unboxing** | Hands open the box, with a line · the product comes out · it is used · the reaction and the offer |
| Beauty, food, drinks | **Product film** | A macro hook (a drop, a pour, steam) · the product in hand · in use · the hero shot with the offer |
| Restaurant, café, bar | **Guest reaction and kitchen** | A guest's first bite and line · the kitchen · the dish · the full room, with the offer |
| Gym, studio, clinic | **Class or service montage** | The energy (a shout, a lift) · the people · the coach or expert says the offer · the end of the class |
| Hotel, travel | **Travel montage** | A drone shot · a guest's reaction · the pool, the view or the room · breakfast, with the offer |
| Real estate | **Property tour** | The door opening · the main room · the kitchen or bedroom · the view, with the price card |
| Car dealer | **Dealer offer** | The car on the road · people inside · the key handover · the car parked, with the offer and its legal line |

A 15 second ad has four shots of 2.5 to 5 seconds. Stories show up to 15 seconds in one card.

Template motion (a photo with moving text, no generated footage) is still right for a quick price change, a sale or a countdown, and for EU teams. See the last section.

## Plan before you spend

A clip costs about as much as 40 images. Write the plan first, then make every shot once.

1. The shots, from the table above, each with what is seen and heard and any spoken line.
2. The lines: the creator's or guest's words are spoken in the clip. A voice-over goes over shots in which nobody speaks.
3. The copy: the captions of every line, the end card's brand, offer, button and legal line.
4. The cost: four shots at 1080p are about 620 credits, the voice and the music about 5.

When the brief is thin (no offer, no brand line, no market), ask once before you generate anything.

## Make it look real

The footage looks real when the prompt describes real footage and real people. It looks AI-made when it describes perfection.

- **Say what kind of footage it is.** "Real handheld phone footage filmed by a friend" for a creator or guest; "Real commercial footage, cinema camera, shallow depth of field" for a product film; "Smooth gimbal shot, real estate video" for a tour; "Drone footage" for a hotel.
- **Cast ordinary people.** Write their age, hair, clothes and what they do: "a woman in her late twenties with big dark curly hair, gold hoops and a black top". Never "beautiful", "flawless skin", "influencer" or "model": those words produce the glossy AI look. Vary ages, body types and backgrounds across a set.
- **Write the light and the place.** "Dim, warm tungsten and candle light, waiters passing behind her" makes a real trattoria; "a restaurant" makes a stock image.
- **Write spoken words like this:** `she says: "Squat-proof. I checked. Twice."` Keep each line under 12 words. Add a reaction around it: a laugh, a glance at the product.
- **Write the sound**, and end the prompt with "No music, no subtitles, no text." The music comes from `generate-music`. A clip's music would clash with it.
- **Never ask for text, logos, prices or brand names in a clip.** They come out misspelled. Put them in the HTML.
- **No real people.** No celebrity, no public figure, no named person, and no lookalike of one.

### Keep the same person or product in every shot

1. Make one reference photo first with `generate-image`. It must look like a candid phone photo, such as "a real, candid photo taken on a recent iPhone, natural light", not a studio shot. A studio render looks like clay in video.
2. Check it before you spend on video. The product must look like no real brand's (an "unbranded" car came out as a copy of a real model, badge included), and every printed word must be spelled exactly right. Fix it with one `generate-image` edit if not.
3. Pass it as `start_image` for a shot that starts from exactly that picture. Pass it in `reference_images` (up to 3) for the same person or product in a new scene. When the client has a real product photo, use that instead, always.

### Check every clip

Each clip comes back with six frames and `spoken_lines`, the words said with their start and end times. Check that the person and the product look the same as in the reference, that no logo or text appeared, and that the line was said once and as written. The model sometimes repeats a line or adds words; cut around them, and only remake the shot if the line is missing.

## Cut it together with render-video

```
render-video html="<captions and end card>" clips=[
  {"asset_ulid": "<hook>",  "start_seconds": 4.2, "duration_seconds": 3.8, "speech": true},
  {"asset_ulid": "<broll>", "start_seconds": 1.0, "duration_seconds": 2.6, "volume": 0.7},
  {"asset_ulid": "<macro>", "start_seconds": 0.5, "duration_seconds": 2.4, "volume": 0.7},
  {"asset_ulid": "<offer>", "start_seconds": 2.8, "duration_seconds": 6.2, "speech": true}
] voiceovers=[{"asset_ulid": "<voice>", "start_seconds": 4.0}] music={"asset_ulid": "<music>"} title="Pasta night story"
```

- **Cut by the spoken lines.** Start a speaking shot 0.3 to 0.5 seconds before its first word and end it 0.3 seconds after its last. Mark it `"speech": true`, so the music drops under it.
- **Open on motion.** The first frame is already mid-action: a bite, a pour, a person turning. Never a still or a black frame.
- **Room sound.** Keep 1 for speaking shots. Use 0.5 to 0.8 for other shots, so their sound sits under the music.
- **Voice-over.** Write it for the ear, at about 2.5 words a second, in short sentences, and write the performance into the script. The voice reads the script as a transcript, so anything that is not a word to say goes in a tag or in `style`:
  - Vocal sounds and pauses in angle brackets, where they happen: `<laugh>`, `<chuckle>`, `<giggle>`, `<sigh>`, `<breath>`, `<gasp>`, `<whispers>`, `<short pause>`, `<long pause>`.
  - CAPITALS on the one word to stress, and `...` or `--` for a natural hesitation.
  - The overall delivery in `style`, in a few words, such as "warm and playful". Leave it empty when the script already carries the performance. Pick the voice for age and accent; `style` cannot change them.
  - Example: `"Okay, confession... <short pause> I came in for ONE cardamom bun. <laugh> I left with four. <sigh> No regrets."`
  - Add `pronunciations` for invented brand names, such as `{"word": "Dewlune", "say": "Dew-loon"}`. Place the voice-over over shots in which nobody speaks, and never on top of a spoken line.
- **Music.** Make one track per ad and leave its volume at the default. render-video fades it in and out, lowers it under every voice and speaking shot, and sets the loudness Instagram plays at.

### Captions and the end card

Most Reels are watched with the sound off, so caption every spoken line and voice-over phrase. Leave the tags and the CAPITALS out of the captions: write the words as they read normally.

- The time of a line in the ad = where its shot starts in the ad + (the line's `start` in `spoken_lines` − the shot's `start_seconds`). A voice-over phrase starts at its `start_seconds` + its segment's `start`.
- The style that reads as native: white bold text, about 50 px, on a dark translucent box, centered at about y = 1010. Each caption pops in at its start and fades at its end.
- The end card takes the last 3.5 to 4.5 seconds: brand name, the offer, the button and the legal line together. Put it where the shot is calm (often the sky or a wall), never over the product, a face or a label. Move captions that overlap it above it, at about y = 640.
- Leave `html` and `body` without a background. Draw scrims as their own elements.

```
<style>
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif;background:transparent}
.cap{position:absolute;left:66px;right:66px;top:1010px;display:flex;justify-content:center;opacity:0;
  animation:capIn .22s cubic-bezier(.2,.9,.3,1.2) both, capOut .15s ease-in forwards}
.cap span{padding:12px 22px 14px;border-radius:16px;background:rgba(0,0,0,.58);color:#fff;font:800 50px/1.16 Inter;text-align:center}
@keyframes capIn{from{opacity:0;transform:translateY(14px) scale(.96)}to{opacity:1;transform:none}}
@keyframes capOut{from{opacity:1}to{opacity:0}}
</style>
<!-- animation-delay: start, end - 0.15 -->
<div class="cap" style="animation-delay:.72s,3.75s"><span>Okay… this is the best carbonara in the city.</span></div>
```

render-video returns `spoken_lines` for the finished ad. Compare them with your script: every line present, in order, said once.

## The AI label is the customer's decision

The EU AI Act (Article 50(4)) asks whoever publishes a "deep fake" to show a visible label. In ads, that means realistic AI-generated people, or an AI image of a product that could mislead about the real product. The file's C2PA metadata does not count as that label. The obligation is the advertiser's, not ours, so the user decides:

- When an ad shows realistic generated people (a creator, guests, a coach) or a generated product, say once, in one line, that EU rules expect a visible AI label on such ads, and ask whether to add it.
- If they want it, add the small label. It is the letters "AI" in the top right corner, inside the safe zone, from the first frame to the last:

```
.ai{position:absolute;top:282px;right:66px;width:52px;height:40px;border-radius:9px;background:rgba(0,0,0,.42);
  color:#fff;font:800 22px/40px Inter;text-align:center;letter-spacing:.04em}
<div class="ai">AI</div>
```

- A real product photo on a generated background, or a clearly fictional scene, does not need it.
- A creator's line is the brand's presenter speaking, never a real customer's experience. Write "Squat-proof. I checked." as a demo, and never "I've used it for three months and my acne is gone." EU consumer law bans fake consumer reviews, with or without a label.

## Legal lines and claims

- Every price, rate, term, consumption figure and legal sentence comes from the user, word for word. If the user has not given the legal line for an offer, ask for it, or render it with a clear placeholder and say so. Never invent figures.
- Car ads in the EU must show the official WLTP fuel or energy consumption and CO₂ emissions. Germany also requires the CO₂ class (A to G) on screen, and a link is not enough. France requires one of three set mobility messages, the hashtag #SeDéplacerMoinsPolluer and the CO₂ class. Ask which market the ad runs in.
- A finance offer that shows a rate or a monthly price needs its standard credit information. From 20 November 2026 EU credit ads also carry a warning such as "Borrowing money costs money". Hold the legal line on the end card for at least 2.5 seconds.

## Meta safe zones (Stories and Reels, 1080 x 1920)

Keep all text, logos and buttons out of the top 14% (above y = 270), the bottom 35% (below y = 1248) and 6% on each side (65 px). Instagram draws its profile row, reply box and buttons there.

## Check every video before you show it

1. The first frame is already moving and shows the subject.
2. Every caption matches its spoken line in time and words, and every line is inside the safe zone and spelled exactly as given.
3. The end card covers no product, face or label; the price and the button are on screen together; the legal line is complete.
4. The person and the product look the same in every shot, and no logo or text appeared in any clip.
5. `spoken_lines` of the finished ad match the script.

Then tell the user what you made: the file name, size and length, the cost (the sum of `credits_used`), and the AI label question when it applies.

## Versions and sizes

- One ad, several offers or languages: keep the clips, change the voice-over, captions and end card, and render each version with its own `title`. A new language needs new spoken shots, because the people speak in the clip.
- Feed placements: render at 1080 x 1350 (4:5) and 1080 x 1080 (1:1). The shots are cropped to fill the frame; change only the CSS and keep text out of the outer 6%.

## Template motion: a photo with moving text

For a quick offer, a sale, a countdown, or a team without generate-video. Pass the photo in `images`, animate it with a slow CSS zoom, and build the text with CSS `@keyframes`. JavaScript does not run, and a page with a `<script>` is refused. An 8 second timeline:

| Time | What happens |
|---|---|
| 0 to 0.5 s | The picture alone, already moving. |
| 0.3 to 1.5 s | Kicker and headline rise in, line by line. The brand is visible by 2 seconds. |
| 1.5 to 2.5 s | The offer or price pops in, the biggest number on screen. |
| 5 to 8 s | End card: brand, button and legal line, held for at least 2.5 seconds. |

```
render-video html="<the layout with {{image_1}}>" width=1080 height=1920 duration_seconds=8 images=[{"asset_ulid": "<photo>"}] title="Weekend offer story"
```

Without clips, a video has no sound. Say so: the user can add music from Meta's licensed library in Ads Manager.

The design rules of `generating-images` still apply: one display face and one text face, the headline the largest thing after the product, the price in the accent color, and a logo at least 15% of the width.

## Putting a video somewhere

A video is private to the conversation until you publish it. `manage-assets` runs only after the `whatagraph-assets` skill is loaded in the conversation:

```
manage-assets action=publish asset_id=<asset_ulid>      → {"url": "<public_url>"}
```

In an HTML document, play it with `<video src="<public_url>" controls playsinline preload="metadata"></video>`. A document plays only published Whatagraph videos; a video that is not published, or any other URL, stays blank. Autoplay works only with `muted`, so for ads with sound show the controls and a poster. To show a set of ads, put each in a 9:16 phone frame with its title, its format and what it cost.

## What it cannot do

- Film the client's real product. Without the client's photo, a generated product is an invention; for anything that must be exact (a car, a package, a phone screen) ask for a photo.
- Real people: no celebrity, public figure or named person, and no voice cloning.
- Edit a video the user uploads, or extend a clip past 10 seconds; cut several shots instead.
- Any of the generating tools for teams whose AI processing must stay in the EU. `render-video` calls no generating model, so template motion works for them.
