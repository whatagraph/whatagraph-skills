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

When the user asks for a video, the answer is a finished video made in this turn, not a storyboard or a still. This holds when the video is one part of a larger request, such as a report or a campaign board: make the video first, then put it in the document. Plan it, make it, check it and show it. Offer plans for more videos only after the first one is made.

The video tools are not offered to every team; check your tool list. Teams whose AI processing must stay in the EU have `generate-image` and `render-video` but no footage, voice-over or music, so they get template motion (the last section) with a photo from `generate-image`.

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
| Software, app, online service | **Product demo** | A person hits the problem and says it, to camera or in a voice-over · the real product on screen doing the job · the result on screen, such as the number or the finished page · the person's reaction, with the logo, the offer and the call to action |

A 15 second ad has four shots of 2.5 to 5 seconds. Make all four. A 10 second ad has two or three shots before its end card. When you have one clip for an ad, cut two or three parts of it (a wide moment, a close reaction, a later beat) instead of playing it from start to end: one unbroken clip under the whole ad reads as a stock video. One clip with an end card on it is not an ad, unless the user asked for a single clip. Stories show up to 15 seconds in one card, so keep a Story ad at 15 seconds or less.

## Pick a direction for each video

The format decides the shots. The direction decides how the video looks and reads: the footage, how words appear on screen, the end card and the pace. Without one, every video gets the same captions, the same end card and the same structure, and a set of three looks like one template with new words.

| Direction | The footage | Words on screen | End card | Fits |
|---|---|---|---|---|
| **Documentary** | Handheld or locked-off, available light, people in the middle of a task who never look at the camera | Subtitles as in a film: white sentence case, semibold, about 48 px, a soft shadow. A time or a place as one small line of the same type, such as "Tuesday, 11:42 pm" | The last shot held, darkened under the words, with the logo and one line | Pain and relief stories, services, B2B, honest brands |
| **Creator** | A phone held by the speaker or a friend; the person talks to the camera | The words the way people caption their own posts: bold white with a thin dark outline, two to five words at a time, in step with the speech | The creator says the call to action; the logo and one line over the last shot | Consumer products, apps, testimonials, younger audiences |
| **Kinetic type** | Short shots, often slow or still, each with a calm area | The script is the type: one to four words at a time, at least 160 px tall, changing in step with the voice-over every half second to a second, in the display face and the brand colors, placed in the calm part of each shot. There is no separate caption row. A full sentence in one block is a headline, not kinetic type | The line huge on a flat brand color, the logo under it | Bold claims, provocative B2B, launches, offers |
| **Title cards** | Shots in story order, with a full-frame card cut in between them | Each beat gets its own card: one short line, large, on an opaque flat brand color that hides the footage for 0.8 to 1.5 seconds, then a hard cut back to the next shot. Text laid over footage is not a title card. Speech over the shots gets plain subtitles | The last card: the logo, one line and the call to action | Stories told in steps or times of day, before and after, how-tos |
| **Cinematic** | Cinema camera, slow moves, graded color, wide shots and close-ups | Almost none: plain subtitles for speech and at most one line of type | The logo centered with space around it, one line under it | Premium brands, hospitality, real estate, fashion, cars |
| **Product close-up** | Macro shots: texture, steam, pours, hands, with strong sound | One word or the offer, set large at the calm moment | A flat brand color, the logo large, the offer and the call to action | Food, drink, beauty, gadgets |

- Follow the brand's own look when it has one: its ads (`view-creatives`), its website, its brand kit. A style the user names always wins. Otherwise pick the direction that suits the idea and the audience, not the first row.
- When you make two or more videos, give each one a different direction and write it next to the video in your plan, for example "Video 2, the queue: Title cards". Videos in a set share the brand's colors and fonts. They never share one HTML with new words in it.
- Take the colors and the type from the client's brand kit, never from these samples. Without a kit, choose them for the business, the audience and the direction. For the type, for example: a plain grotesk such as Inter or IBM Plex Sans for documentary subtitles, a heavy sans such as Archivo Black for creator captions, a condensed display face such as Anton or Bebas Neue for kinetic type, a sharp grotesk such as Inter Tight or a serif such as Fraunces for title cards, and a refined serif such as Cormorant Garamond for cinematic.

Template motion (a photo with moving text, no generated footage) is a fallback. Use it only when the user asks for a quick price change, a sale or a countdown, or when your tool list has no `generate-video` (EU teams). See the last section. When the user asks for a Story, a Reel or a video ad and you have `generate-video`, make live-action shots with sound. A silent animation of text over a picture does not answer that request.

## Plan before you spend

A clip costs about as much as 40 images. Write the plan first, then make every shot once.

1. The direction, and the shots from the format table, each with what is seen and heard and any spoken line.
2. The lines: the creator's or guest's words are spoken in the clip. A voice-over goes over shots in which nobody speaks.
3. The copy: the captions of every line, and the end card written out as its three things, word for word: the logo, the one line and the call to action (plus the legal line when the offer needs one).
4. The cost: four shots at 1080p are about 620 credits, the voice and the music about 5.

When the brief is thin (no offer, no brand line, no market) and there is no website, brand kit or earlier ad to take it from, ask once before you generate anything. Otherwise make the video in this turn. The plan is a step toward the video, never the answer to a request for one.

## Make it look real

The footage looks real when the prompt describes real footage and real people. It looks AI-made when it describes perfection.

- **Say what kind of footage it is.** "Real handheld phone footage filmed by a friend" for a creator or guest; "Real commercial footage, cinema camera, shallow depth of field" for a product film; "Smooth gimbal shot, real estate video" for a tour; "Drone footage" for a hotel.
- **Cast ordinary people.** Write their age, hair, clothes and what they do: "a woman in her late twenties with big dark curly hair, gold hoops and a black top". Never "beautiful", "flawless skin", "influencer" or "model": those words produce the glossy AI look. Vary ages, body types and backgrounds across a set.
- **Write the light and the place.** "Dim, warm tungsten and candle light, waiters passing behind her" makes a real trattoria; "a restaurant" makes a stock image.
- **Write spoken words like this:** `she says: "Squat-proof. I checked. Twice."` Keep each line under 12 words, in the language of the ad. Add a reaction around it: a laugh, a glance at the product.
- **People speak only the words you write.** "Talking", "chatting" or "says something" with no line in quotes makes the model invent the words, often in English in an ad for another language. When nobody should speak, write "no one speaks". A caption shows the words that are said, never a translation of them.
- **Write the sound**, and end the prompt with "No music, no subtitles, no text." The music comes from `generate-music`. A clip's music would clash with it.
- **Never ask for text, logos, prices or brand names in a clip.** They come out misspelled. Put them in the HTML.
- **No real people.** No celebrity, no public figure, no named person, and no lookalike of one.

### Keep the same person or product in every shot

When one person appears in two or more shots, the reference photo is required. A prompt that says "the same woman" without it gives a different person in each shot.

1. Make one reference photo first with `generate-image`. It must look like a candid phone photo, such as "a real, candid photo taken on a recent iPhone, natural light", not a studio shot. A studio render looks like clay in video.
2. Check it before you spend on video. The product must look like no real brand's (an "unbranded" car came out as a copy of a real model, badge included), and every printed word must be spelled exactly right. Fix it with one `generate-image` edit if not.
3. Pass it as `start_image` for a shot that starts from exactly that picture. Pass it in `reference_images` (up to 3) for the same person or product in a new scene. When the client has a real product photo, use that instead, always.

### Software and apps: real people, real screens

A software ad is still a live-action ad. The people are generated footage; the product is real screenshots.

- Shots 1 and 4 come from `generate-video`: a person with the problem, saying it, and the same person once it is solved. Make both clips, and pass the same reference photo to both, so it is the same person. One clip followed by a long end card is not the ad.
- Shots 2 and 3 show the real product. A generated clip invents an interface with misspelled words, so never ask for a screen in a clip. Find real screenshots in the team library (`search-assets` for "screenshot", "dashboard" or "report"), on the client's website (import them with `manage-assets action=import_url`), or from the user. Pass them in render-video's `images` and show each one in a phone or laptop frame drawn in CSS, on the brand color, covering the frame for that shot. Fit the whole screenshot inside the device (`object-fit: contain`), and never crop words off its edges: a wide banner cut to "ld reporting" looks broken. Move them: a slow push in, a scroll, a ring around the number that matters. render-video needs a clip under every second for the sound, so under these shots play a calm part of a people clip at volume 0.5.
- Without a real screenshot, never draw a made-up interface, in a clip or in the HTML: no dashboard, chart, report or app screen built in CSS, and no number the client did not give. Let the people shots tell the story, put one short claim of up to six words in large type on the brand color in shots 2 and 3, and ask the user for screenshots in your reply.
- Add a voice-over over the shots in which nobody speaks, and music.

### Only the finished video goes in the chat

Clips, voice-overs and music are parts of the ad, so the chat does not show them. The user sees the video that render-video makes. Each clip takes about a minute, so tell the user in one line what you are making before you start. Set `show_in_chat: true` only when the user asked for a single clip, a voice-over or a music track on its own.

### Check every clip

Each clip comes back with six frames and `spoken_lines`, the words said with their start and end times. Check that the person and the product look the same as in the reference, that no logo or text appeared, and that the line was said once and as written. If a shot shows a different person, remake it with the reference photo before you cut: two faces in one story read as two people. The model sometimes repeats a line or adds words; cut around them, and only remake the shot if the line is missing.

## Cut it together with render-video

```
render-video html="<captions and end card>" clips=[
  {"asset_ulid": "<hook>",  "start_seconds": 4.2, "duration_seconds": 3.8, "speech": true},
  {"asset_ulid": "<broll>", "start_seconds": 1.0, "duration_seconds": 2.6, "volume": 0.7},
  {"asset_ulid": "<macro>", "start_seconds": 0.5, "duration_seconds": 2.4, "volume": 0.7},
  {"asset_ulid": "<offer>", "start_seconds": 2.8, "duration_seconds": 6.2, "speech": true}
] voiceovers=[{"asset_ulid": "<voice>", "start_seconds": 4.0}] music={"asset_ulid": "<music>"} title="Pasta night story"
```

- **Cut by the spoken lines.** Start a speaking shot 0.3 to 0.5 seconds before its first word and end it 0.3 seconds after its last. Mark it `"speech": true`, so the music drops under it. Read `spoken_lines` of every clip you use, including the ones you meant as silent shots: a part that starts or ends inside a line cuts the speaker off mid-word, and render-video refuses it. To use such a shot for its picture only, set its volume to 0.
- **Open on motion.** The first frame is already mid-action: a bite, a pour, a person turning. Never a still or a black frame.
- **Room sound.** Keep 1 for speaking shots. Use 0.5 to 0.8 for other shots, so their sound sits under the music.
- **Voice-over.** Write it for the ear, in short sentences, in the language of the ad, and write the performance into the script. The voice reads the script as a transcript and speaks the language it is written in, so anything that is not a word to say goes in a tag or in `style`:
  - Vocal sounds and pauses in angle brackets, where they happen: `<laugh>`, `<chuckle>`, `<giggle>`, `<sigh>`, `<breath>`, `<gasp>`, `<whispers>`, `<short pause>`, `<long pause>`.
  - CAPITALS on the one word to stress, and `...` or `--` for a natural hesitation.
  - Numbers, prices, percentages and dates as words, in the form the sentence needs: "iki penkiasdešimties procentų", not "iki 50 %". From digits the voice can pick the wrong grammatical case.
  - The overall delivery in `style`, in a few words, such as "warm and playful". Never a language or an accent: the voice already speaks the script's language natively, and naming one makes it worse. Leave it empty when the script already carries the performance. Pick the voice for gender, age and tone.
  - Example: `"Okay, confession... <short pause> I came in for ONE cardamom bun. <laugh> I left with four. <sigh> No regrets."`
  - Add `pronunciations` in IPA between slashes for invented brand names and for names from another language than the script, such as `{"word": "Kavos", "say": "/kɐˈvoːs/"}` for a Lithuanian brand in an English ad. Leave the words of the script's own language alone: the voice already says them well, and an English respelling makes a foreign name sound English.
  - Check `duration_seconds`. When the voice-over is longer than the shots it covers, shorten the script and record it again. The same message takes a different length in each language.
  - Each take differs a little. When the user says a take sounds wrong or accented, record it again.
  - Place the voice-over over shots in which nobody speaks, and never on top of a spoken line.
- **Music.** Make one track per ad and leave its volume at the default. render-video fades it in and out, lowers it under every voice and speaking shot, and sets the loudness Instagram plays at.

### Words over the shots

Over the footage sit only the words of the story: the captions, a line that says when or where, and in the kinetic type direction the big words. They are type set on the picture, the way film and TV set words, with a soft shadow, or with a soft dark scrim rising from the edge of the frame when the shot is bright or busy.

- Nothing holds the words. No box or bubble behind a caption, no pill, chip, badge, tag or framed label, no border, glass or blurred panel, no card with a shadow, no logo in a corner, no drawn button. A colored shape with rounded corners over a shot reads as an app, so leave it out even where it would add contrast. Use the shadow, the scrim or a calmer position instead.
- A time, a place, "POV:" or a chapter name is part of the story. Set it as plain type in the caption face, or put it on a title card.
- Most Reels are watched with the sound off, so caption every spoken line and voice-over phrase, in the type of the direction. Leave the tags and the CAPITALS out of the captions: write the words as they read normally.
- The time of a line in the ad = where its shot starts in the ad + (the line's `start` in `spoken_lines` − the shot's `start_seconds`). A voice-over phrase starts at its `start_seconds` + its segment's `start`. Creator captions that show a few words at a time split a line's time across its words.
- Captions sit with their bottom edge at about y = 1240, just above the bottom 35% where Instagram draws its own text.
- A caption never covers a face. Look at the frames of each shot before you place its captions: people in a wide shot often have their heads near the middle of the frame. When a face is where the caption would sit, move that shot's captions below the face, or above the heads at about y = 330.
- One caption at a time, as one block of text of two lines at most, about 12 words. Split a longer line into two captions. Each caption ends before the next one starts, and the last one ends before the end card appears. When a caption names who speaks, put the name in the same line in bold (`<b>Max:</b> Squat-proof.`). To color one word, wrap it in `<b class="hl">` and give `.hl` only a color.
- No emoji in captions, the end card or any text. The renderer has no emoji font, so an emoji shows as an empty gap.
- The words follow the design rules of `generating-images` for composed designs: no interface components, a display face for the big words, no symbols typed as text. Put big type where the shot is calm (often the sky or a wall), never over the product, a face or a label.
- Leave `html` and `body` without a background. Draw scrims as their own elements.
- Text in Chinese, Japanese, Korean, Arabic, Hebrew, Thai or Hindi needs the Noto Sans font for that script from Google Fonts (Noto Sans SC, Noto Sans JP, Noto Sans KR, Noto Sans Arabic, Noto Sans Hebrew, Noto Sans Thai, Noto Sans Devanagari), named first in `font-family`. The renderer has fonts for Latin, Greek and Cyrillic letters only, so other letters show as empty boxes without it. Set `dir="rtl"` on Arabic and Hebrew text.

### The end card

- The end card takes the last 3.5 to 4.5 seconds and follows the direction (see its column in the table).
- It holds three things: the logo, one line with the offer, and the call to action written as a few words, plus the legal line when the offer needs one. Count them before you render. A second line under the headline, a tagline, a badge, a rule, a second logo or a button is a fourth thing, so cut it. Instagram adds its own button below the Story, so a drawn one only repeats it.
- The most common failure is a landing-page hero: a small logo icon next to the brand name, a small uppercase label, a headline, a grey line under it and a rounded button, all centered in the middle of the frame. It reads as a website, not as the end of an ad. Build the end card from the direction instead, at the sizes of the sample: the logo 300 to 450 px wide, the line in the display face at 96 px or more, the call to action as words at about 44 px.
- The logo is the client's real logo file passed in `images`, at least 300 px wide on a flat color and at least 160 px over the last shot. When the file is only a square icon, set the brand name as a wordmark in type next to or under it, at the same visual size. Without a logo, set the wordmark at that size.
- Design it like the last frame of a commercial: the last shot, darkened only where the words sit; a full-frame flat brand color; or the line set huge as type. No card, panel, glass, chips, row of stats, button, or dark radial glow over the whole frame.

### Samples, one per direction

These show the treatment, not a template to repeat. Every color, face and word in them is a placeholder from an imagined client: replace them with the client's brand kit, and when there is none, choose them for the client's business and audience. A bakery, a law firm, a festival and a software company should not end up with the same type and colors. Change the size and the position to fit the shot, and load every face you use from Google Fonts in the `<link>`, as the first sample does.

Documentary, with the whole page around it:

```
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&family=Fraunces:opsz,wght@9..144,600&display=swap" rel="stylesheet">
<style>
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent}
.sub{position:absolute;left:90px;right:90px;bottom:680px;margin:0;text-align:center;color:#fff;
  font:600 48px/1.26 Inter,sans-serif;text-shadow:0 2px 3px rgba(0,0,0,.8),0 0 28px rgba(0,0,0,.6);
  opacity:0;animation:on .12s linear both,off .12s linear forwards}
.when{position:absolute;left:72px;top:330px;margin:0;color:#fff;font:600 32px Inter,sans-serif;
  text-shadow:0 1px 3px rgba(0,0,0,.8);opacity:0;animation:on .3s linear both,off .3s linear forwards}
.scrim{position:absolute;left:0;right:0;bottom:0;height:1000px;opacity:0;
  background:linear-gradient(to top,rgba(0,0,0,.6),rgba(0,0,0,0));animation:on .3s linear both,off .3s linear forwards}
.end{position:absolute;inset:0;background:#B5462A;opacity:0;animation:on .3s ease-out 11s forwards}
.end img{position:absolute;left:50%;top:560px;width:400px;transform:translateX(-50%)}
.end .line{position:absolute;left:66px;right:66px;top:860px;margin:0;font:600 104px/1 Fraunces,serif;color:#FFF4E6;text-align:center}
.end .cta{position:absolute;left:66px;right:66px;top:1130px;font:700 42px Inter,sans-serif;color:#FFF4E6;text-align:center}
@keyframes on{from{opacity:0}to{opacity:1}}
@keyframes off{from{opacity:1}to{opacity:0}}
</style>
<!-- animation-delay: start, end - the fade time. Add the scrim only under a bright or busy shot. -->
<div class="scrim" style="animation-delay:.6s,3.5s"></div>
<p class="when" style="animation-delay:.3s,3.4s">Thursday, 8:40 pm</p>
<p class="sub" style="animation-delay:.72s,3.63s">Okay… this is the best carbonara in the city.</p>
<!-- the end card, the last 4 seconds of a 15 second ad: one brand color, the logo, one line, the call to action -->
<div class="end"><img src="{{image_1}}"><h1 class="line">Pasta night is Thursday</h1><div class="cta">Book a table</div></div>
```

`{{image_1}}` is the logo passed in `images`.

The end card on the last shot instead, for documentary, kinetic type and cinematic videos: the shot keeps playing, darkened from below, with the line large and the logo and the call to action under it.

```
.endshot{position:absolute;inset:0;opacity:0;animation:on .3s ease-out 6.4s forwards;
  background:linear-gradient(to top,rgba(0,0,0,.78) 0%,rgba(0,0,0,.45) 45%,rgba(0,0,0,0) 70%)}
.endshot .line{position:absolute;left:72px;right:72px;top:760px;margin:0;color:#fff;font:400 132px/.9 Anton,sans-serif;text-transform:uppercase}
.endshot img{position:absolute;left:72px;top:1010px;width:420px}
.endshot .cta{position:absolute;left:72px;top:1160px;margin:0;color:#fff;font:700 44px Inter,sans-serif}
<div class="endshot"><h1 class="line">Your first class is on us</h1><img src="{{image_1}}"><p class="cta">Book a class</p></div>
```

Creator, a few words at a time in step with the speech:

```
.say{position:absolute;left:80px;right:80px;bottom:700px;margin:0;text-align:center;color:#fff;font:900 66px/1.08 'Archivo Black',sans-serif;
  text-shadow:-3px -3px 0 #000,3px -3px 0 #000,-3px 3px 0 #000,3px 3px 0 #000,0 5px 0 #000;opacity:0;animation:on .06s linear both,off .06s linear forwards}
```

Kinetic type, set in the calm part of the shot:

```
.big{position:absolute;left:66px;right:66px;top:330px;margin:0;color:#FFF4E6;font:400 210px/.84 Anton,sans-serif;text-transform:uppercase;
  text-shadow:0 6px 30px rgba(0,0,0,.35);opacity:0;animation:rise .25s cubic-bezier(.2,.8,.2,1) both,off .1s linear forwards}
@keyframes rise{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}
```

Title cards, cut in hard between shots:

```
.card{position:absolute;inset:0;background:#2E4A3B;opacity:0;animation:on .01s linear both,off .01s linear forwards}
.card p{position:absolute;left:96px;right:96px;top:780px;margin:0;color:#F4EEE3;font:600 88px/1.04 'Inter Tight',sans-serif}
```

render-video returns `spoken_lines` for the finished ad. Compare them with your script: every line present, in order, said once.

## The AI label is the customer's decision

The EU AI Act (Article 50(4)) asks whoever publishes a "deep fake" to show a visible label. In ads, that means realistic AI-generated people, or an AI image of a product that could mislead about the real product. The file's C2PA metadata does not count as that label. The obligation is the advertiser's, not ours, so the user decides:

- When an ad shows realistic generated people (a creator, guests, a coach) or a generated product, say once, in one line, that EU rules expect a visible AI label on such ads, and ask whether to add it.
- If they want it, add the small label. It is the letters "AI" as plain type in the top right corner, inside the safe zone, from the first frame to the last:

```
.ai{position:absolute;top:290px;right:72px;margin:0;color:#fff;font:700 26px Inter,sans-serif;letter-spacing:.08em;
  text-shadow:0 1px 2px rgba(0,0,0,.75),0 0 12px rgba(0,0,0,.4)}
<p class="ai">AI</p>
```

- A real product photo on a generated background, or a clearly fictional scene, does not need it.
- A creator's line is the brand's presenter speaking, never a real customer's experience. Write "Squat-proof. I checked." as a demo, and never "I've used it for three months and my acne is gone." EU consumer law bans fake consumer reviews, with or without a label.

## Legal lines and claims

- Every price, rate, term, consumption figure and legal sentence comes from the user, word for word. What the product does is a claim too: take it from the brief, the website or the client, not from what such products usually do. If the user has not given the legal line for an offer, ask for it, or render it with a clear placeholder and say so. Never invent figures.
- Car ads in the EU must show the official WLTP fuel or energy consumption and CO₂ emissions. Germany also requires the CO₂ class (A to G) on screen, and a link is not enough. France requires one of three set mobility messages, the hashtag #SeDéplacerMoinsPolluer and the CO₂ class. Ask which market the ad runs in.
- A finance offer that shows a rate or a monthly price needs its standard credit information. From 20 November 2026 EU credit ads also carry a warning such as "Borrowing money costs money". Hold the legal line on the end card for at least 2.5 seconds.

## Meta safe zones (Stories and Reels, 1080 x 1920)

Keep all text and logos out of the top 14% (above y = 270), the bottom 35% (below y = 1248) and 6% on each side (65 px). Instagram draws its profile row, reply box and buttons there.

## Check every video before you show it

1. The first frame is already moving and shows the subject.
2. It has sound: spoken lines or a voice-over, and music.
3. Every caption matches its spoken line in time and words, sits inside the safe zone, is spelled exactly as given, is alone on screen and covers no face.
4. Over the shots there is only type: the captions, a when or where line, or the big words of kinetic type. No box, bubble, pill, badge, framed label, panel, logo or button sits over any shot.
5. No speaker is cut off: every spoken line in the finished ad is complete, and in the language of the ad.
6. The end card is the last 3.5 to 4.5 seconds and holds three things: the logo at least 300 px wide, one line and the call to action as words, plus the legal line when needed. It covers no product, face or label. Look at its frame in render-video's result: a label above the line, a second line under it or a shape around the call to action means it is a web page, so remove them and render again.
7. When you made several videos, each has its own direction, done as the table describes it (kinetic type changes every second, title cards hide the footage), and no two share the same layout of words or the same end card.
8. No interface, dashboard or chart appears that is not a real screenshot, and every number on screen comes from the client.
9. The person and the product look the same in every shot, and no logo or text appeared in any clip.
10. `spoken_lines` of the finished ad match the script.

Then tell the user what you made: the file name, size and length, the cost (the sum of `credits_used`), and the AI label question when it applies.

## Versions and sizes

- One ad, several offers or languages: keep the clips, change the voice-over, captions and end card, and render each version with its own `title`. Write each language's script for that language instead of translating word for word, and check its length again. A new language needs new spoken shots, because the people speak in the clip.
- Feed placements: render at 1080 x 1350 (4:5) and 1080 x 1080 (1:1). The shots are cropped to fill the frame; change only the CSS and keep text out of the outer 6%.

## Template motion: a photo with moving text

For a quick offer, a sale, a countdown, or a team without generate-video. Pass the photo in `images`, animate it with a slow CSS zoom, and build the text with CSS `@keyframes`. JavaScript does not run, and a page with a `<script>` is refused. An 8 second timeline:

| Time | What happens |
|---|---|
| 0 to 0.5 s | The picture alone, already moving. |
| 0.3 to 1.5 s | A short first line and the headline rise in, line by line, as plain type. The brand is visible by 2 seconds. |
| 1.5 to 2.5 s | The offer or price pops in, the biggest number on screen. |
| 5 to 8 s | End card: the logo, the offer, the call to action and the legal line, held for at least 2.5 seconds. |

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

In an HTML document, play it with `<video src="<public_url>#t=0.1" controls playsinline preload="metadata"></video>`. The `#t=0.1` shows the video's own first frame before it plays. A document plays only published Whatagraph videos; a video that is not published, or any other URL, stays blank. Autoplay works only with `muted`, so for ads with sound show the controls. To show a set of ads, put each in a 9:16 phone frame with its title, its format and what it cost.

When you put a new video in a document in place of a picture or an older video:

- Do not use the old picture as the `poster`. It makes the page look unchanged. Leave `poster` out and keep `#t=0.1`.
- Rewrite the text around it to describe the video you made: its shots, length, lines and captions. A storyboard that still describes a different plan tells the reader the video is wrong.
- After the edit, check that every `<video>` in the document points to the published URL of the video you just made.

## What it cannot do

- Film the client's real product. Without the client's photo, a generated product is an invention; for anything that must be exact (a car, a package, a phone screen) ask for a photo.
- Real people: no celebrity, public figure or named person, and no voice cloning.
- Edit a video the user uploads, or extend a clip past 10 seconds; cut several shots instead.
- Footage, voice-over or music for teams whose AI processing must stay in the EU. They have `generate-image` and `render-video`, so template motion with a generated photo works for them.
