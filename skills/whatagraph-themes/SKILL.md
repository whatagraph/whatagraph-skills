---
name: whatagraph-themes
type: domain
group: team_workspace_branding
description: Apply themes (logos, fonts, header/footer) and color palettes (chart series colors, widget chrome, report canvas) to reports, and create or update reusable palettes and themes. Use when branding a report for a client, applying consistent colors across widgets, or fixing off-brand charts. Covers the exact palette schema (widget_colors object, chart_colors array, additional_colors).
required_tools:
  - list-themes
  - list-widgets
  - manage-themes
optional_tools:
  - tool_name: delete-themes
    purpose: Delete a theme or color palette.
  - tool_name: manage-widgets
    purpose: Apply a theme colour id to an individual widget.
---

# Themes & color palettes

Tools covered: `list-themes`, `manage-themes`, `delete-themes`.

Two concepts:
- **Theme** — logo, fonts, header/footer layout, overall visual skin.
- **Color palette** — the specific colors used in chart series, widget backgrounds, accents.

Themes and palettes live at the team level. They're applied per-report.

> The `manage-themes` tool description is intentionally brief. Detailed color format rules (bare hex vs raw CSS), resolution order, dark-theme guidance, and email theme setup are documented here in this skill, not in the tool description. Always load this skill before creating or updating themes/palettes.

## Use this when

- Apply the client's logo and brand fonts to a specific report.
- Set a consistent color palette across all series in a report's charts.
- Switch a report to a dark variant of the team theme.

## Listing

```
list-themes action=list_themes                          # team-level themes
list-themes action=list_themes search="Acme"            # filter by name
list-themes action=list_colors                          # team-level palettes
list-themes action=list_colors search="dark"            # filter palettes by name
list-themes action=list_themes report_id=<id>           # report + team themes, with active status
list-themes action=list_colors report_id=<id>           # report + team palettes, with active status
list-themes action=show_theme report_id=<id> theme_id=<id>   # one theme: name, header, footer, style options
```

Pagination: cursor-based with `cursor` parameter; `per_page` up to 500 (default 100).

Themes and palettes are stored at the team level. `report_id` is optional on the list actions (verified Jun 2026) — omit it for team-level items only; pass it to also see report-level items and which one is active on that report. `show_theme` requires both `report_id` and `theme_id`.

Both `list_themes` and `list_colors` include context fields:
- `applied_theme_id` / `applied_color_id` — the ID active on the report, or `null`
- `applied_theme_source` / `applied_color_source` — `"team"`, `"report"`, `"system"`, or `null`. When `"system"`, the applied theme/palette is a built-in premade not included in the list — `team_has_themes: false` with a non-null `applied_theme_id` is expected in this case
- `team_has_themes` / `team_has_colors` — whether the team has any custom themes/palettes

### Colouring one widget differently

The `id` of a palette from `list_colors` is exactly what a widget's `active_theme_color_id` takes. Pass it verbatim through `manage-widgets`:

```
list-themes action=list_colors report_id=<report_id>
   → [{"id": "<colour_id>", "name": "Signal Red", "theme_id": "<theme_id>", "source": "team", "is_active": false}, ...]

manage-widgets action=update report_id=<report_id> widget_id=<widget_id>
   options={"active_theme_color_id": <colour_id>}
```

Two things to be clear about. It is a **palette id, not a single colour** — you are switching that widget to a whole palette, not picking one swatch out of one. And `is_active` marks the palette currently applied to the *report*, which is unrelated to what an individual widget overrides.

## Apply a theme to a report

```
manage-themes action=enable_theme
   report_id=<id>
   theme_id=<id>
```

Response includes `report_state.applied_theme_id` and `report_state.applied_color_id` confirming the report's current state after the change.

## Apply a color palette to a report

```
manage-themes action=enable_color
   report_id=<id>
   color_id=<id>
```

Response includes `report_state.applied_theme_id` and `report_state.applied_color_id` confirming the report's current state after the change. When a palette is bound to a theme, `enable_color` also activates that theme automatically.

## Create a custom theme

```
manage-themes action=create_theme
   name="Acme Brand — Light"
   options={
     "header": {...},
     "footer": {...}
   }
```

Each section (`header`/`footer`) accepts:
- `images` — array of `{url, title, scale_to_fill, alignment, width, height}`
- `text` — string or null
- `text_alignment` — `"left"`, `"center"`, or `"right"` (default: `"right"`)
- `text_format` — `{"italic": bool, "bold": bool}` (default: both false)
- `text_color` — CSS hex (default: `"#516D8E"`)
- `background_color` — CSS hex (default: `"#ffffff"`)
- `apply_to_footer` / `apply_to_header` — bool, mirrors this section to the other

Use `list-themes action=show_theme` to see an existing theme's full `options` shape.

## Update a theme

```
manage-themes action=update_theme
   theme_id=<id>
   name="Acme Brand — Dark"                       # optional
   options={ "header": {...}, "footer": {...} }    # optional
```

Updates an existing custom theme's `name` and/or `options` (header/footer/branding). Fetch the current shape via `list-themes action=list_themes` first and submit the full `options` you want to keep.

> **Warning:** if the theme has `header.apply_to_footer: true` (or `footer.apply_to_header: true`), every `update_theme` mirrors that section onto the other — images included, so editing the header can silently delete the footer's images. To edit them independently, set the flag to `false` in the same update.

## Create a custom color palette

```
manage-themes action=create_color
   name="Acme — Primary"
   colors={
     "widget_colors": {
       "text_color": "2B2B2B",         "neutral_color": "9BA5B0",
       "positive_color": "5FA873",     "negative_color": "D64545",
       "accent_fill_color": "EAE6D8",  "accent_text_color": "C0392B",
       "chart_axis_text": "8A857A",    "chart_grid_lines": "E6E3D6",
       "neutral_bg": "F7FAFC",         "font_family": "inter",
       "widget_background": "#FFFFFF", "icon_symbol": "#FFFFFF",
       "icon_background": "#C0392B",   "list_odd_fill": "transparent",
       "list_even_fill": "#F6F5EC",
       "shades": ["6CD094","FEC644","34587C","ECADAD","76D18A","94D1EB"]
     },
     "chart_colors": ["C0392B","8FA876","E0A33E","D67B5C","6E8B6B","7C9B9A","E8C49A","A0504A"],
     "additional_colors": {
       "background": "#F0F0E3", "report_accent": "C0392B",
       "report_text_color": "2B2B2B", "report_title_color": "C0392B"
     },
     "theme_id": <theme_id>
   }
   options={"parent_id": <optional>, "parent_name": "<optional>"}
```

- **`widget_colors`** is an **object with named keys** — NOT a flat array. Keys: `text_color`, `positive_color`, `negative_color`, `accent_fill_color`, `accent_text_color`, `neutral_color`, `neutral_bg`, `chart_axis_text`, `chart_grid_lines`, `widget_background`, `icon_symbol`, `icon_background`, `list_odd_fill`, `list_even_fill`, `font_family`, `shades`.
- **Required on `create_color`:** `font_family` (e.g. `"inherit"`), `accent_text_color`, `positive_color`, `negative_color` (bare hex), and `shades` (array of 6 bare hex strings — a legacy field no longer rendered by the UI, but still required by frontend validation when users edit palettes). If unsure what to pass, pick 6 hex values from your `chart_colors`.
- **Hex format matters — two groups of keys:**
  - **Text / accent / chart-line colors are bare hex (NO `#`):** `text_color`, `neutral_color`, `neutral_bg`, `positive_color`, `negative_color`, `accent_fill_color`, `accent_text_color`, `chart_axis_text`, `chart_grid_lines`, and `additional_colors.report_accent` / `report_text_color` / `report_title_color`. The renderer prepends the `#` itself, so a value stored **with** a `#` becomes `##RRGGBB` — an invalid color — and the element falls back to a default (commonly **dark, unreadable text/numbers**). Pass `"2B2B2B"`, not `"#2B2B2B"`.
  - **Backgrounds / fills / icons are raw CSS values (KEEP the `#`, or use `rgba()` / `transparent` / a gradient):** `widget_background`, `icon_symbol`, `icon_background`, `list_odd_fill`, `list_even_fill`, and `additional_colors.background`.
- **`chart_colors`** is an array of bare hex values (6-digit `"C0392B"` or 8-digit-with-alpha `"6366f1ff"`). A leading `#` is stripped automatically; non-hex values are rejected. Provide 8–12 colors to avoid repetition on large charts.
- **`additional_colors`** is an **object** controlling the report canvas: `background` (raw CSS), `report_accent`, `report_text_color`, `report_title_color` (bare hex). Set these to drive the report background and title color; omit to keep the theme default.
- Tie a palette to a theme via `theme_id` in `colors`. Binding is organizational only — any palette can be applied to any report regardless of which theme it's bound to. Omitting `theme_id` creates an unbound palette that works with any theme.

### Designing a palette that hangs together

When you compose a palette yourself (no exact brand values supplied), don't pick each key independently — derive the whole set from one starting point so the report reads as a single design:

- **Start from one accent.** Take the brand/primary color (from the prompt, the client's logo, or the space name's known brand) as `report_accent` / `accent_text_color` / `icon_background`, and derive everything else from it — same temperature (warm accent → warm greys and fills, cool accent → cool ones), never a mix of clashing families.
- **`chart_colors` are siblings, not a grab-bag.** Use distinct **hues** at broadly similar saturation and lightness so no series shouts over the others — vary the hue around the wheel, not just the shade of one color. Order the array so adjacent entries contrast clearly (series are colored in array order; two near-identical neighbours make consecutive series indistinguishable). Provide 8–12.
- **Keep semantic colors unambiguous.** `positive_color` stays recognizably green-ish and `negative_color` red-ish, both clearly distinct from the nearby `chart_colors` — if a chart series uses nearly the same red as the negative delta, trend arrows stop reading at a glance. For the same reason avoid leaning the chart series heavily on red+green pairs.
- **Chrome recedes, data speaks.** `chart_axis_text` and `chart_grid_lines` are quiet, low-saturation greys tinted toward the palette's temperature — grid lines lighter than axis text, both far quieter than any chart color. `neutral_color` sits between `text_color` and the background.
- **Contrast where text lives.** `text_color` on `widget_background`, `accent_text_color` on `accent_fill_color`, and `report_title_color` / `report_text_color` on `additional_colors.background` must each be comfortably readable (aim for roughly WCAG-AA-level contrast). This is where near-miss palettes fail.
- **Let the canvas lift the cards.** Make `additional_colors.background` a subtle tint one step away from `widget_background` (slightly darker or warmer/cooler) so widgets read as cards on a page; `list_even_fill` is a barely-visible step from `widget_background`, not a loud stripe.
- **Theme and palette agree.** The theme's header/footer `text_color` / `background_color` come from the same family as the palette (accent or its neutrals) — a blue-branded header on an earth-toned palette reads as two different reports stapled together. When creating both, derive them from the same accent; when applying a palette to a report with an existing theme, check the pair side by side.
- **Verify on a real page.** After applying, export a tab that holds a table + chart + KPI (`export-report`) and check: series distinguishable, deltas obviously green/red, text readable on every surface, header matching the page. Adjust with `update_color` rather than shipping a near-miss.

### Dark themes — set the full key set

When the background is dark you must darken the foreground keys too, or widgets keep their light defaults and text disappears:

- **Set `text_color`, `neutral_color`, `report_text_color`, `report_title_color` to a light/near-white bare hex** (e.g. `"F5F7FA"`) — not the default dark.
- **Set `list_even_fill` (and `list_odd_fill`) to a dark or `"transparent"` value.** These are the alternating "zebra" row fills for list / table / funnel widgets. If you omit them, the renderer applies a hardcoded **light** even-row fill, so on a dark theme the even rows show a pale band with invisible light text. Use `list_odd_fill: "transparent"`, `list_even_fill: "#1F2430"` (a slightly lighter shade of `widget_background`), keeping the `#` since these are raw-CSS keys.
- Set `widget_background` and `additional_colors.background` to your dark colors (raw CSS, keep `#`).
- After applying a dark palette, re-check a report that contains a **list, table, or funnel** widget — those are where missing zebra fills bite, not the single-value scorecards.

## Update a palette

```
manage-themes action=update_color
   color_id=<id>
   colors={"widget_colors": {...}, "chart_colors": [...hex...], "additional_colors": {...}}
```

Same shapes as `create_color` — `widget_colors`/`additional_colors` are objects, `chart_colors` is the hex array (leading `#` stripped automatically). Note `chart_colors` is an indexed array and is replaced entirely on update — pass the full desired list. After updating a palette already enabled on a report, re-check the report render (`list-widgets action=csv_export` or the UI) to confirm the change propagated.

## Email themes (whitelabel)

Requires the `whitelabel` feature. Controls branding on report-delivery emails (sender name, button colors, heading/body/footer text, images).

```
list-themes action=list_email_themes                    # team email themes
list-themes action=list_web_domains                     # custom web domains
list-themes action=list_email_domains                   # custom email domains
manage-themes action=create_email_theme name="Acme Email" options={...}
manage-themes action=update_email_theme email_theme_id=<id> options={...}
manage-themes action=enable_email_theme report_id=<id> email_theme_id=<id>  # report_id optional (omit for team-level)
```

`create_email_theme` requires `name`, `web_domain_id`, and `email_domain_id` — get the last two from `list_web_domains` / `list_email_domains`; both must belong to the team or be premade. On `update_email_theme` the theme keeps its current domains when you omit them.

### Email theme `options`

| Key | Notes |
|---|---|
| `background_color` | Email body background |
| `heading_text`, `heading_text_color` | |
| `body_text`, `body_text_color` | |
| `footer_text`, `footer_text_color` | `footer_text` is nullable |
| `button_text`, `button_text_color`, `button_background_color` | The "View report" call to action |
| `sender_name` | Display name on the From line |
| `sender_email` | **Local part only** — the part before the `@`. Validated as a full address against `sender_email_domain` |
| `sender_email_domain` | The domain half, from `list_email_domains` |
| `subject_text` | |
| `reply_name`, `reply_to_email` | |
| `images[]` | `{title, url, alignment, scale_to_fill}`. Import and publish a remote image first — see the header/footer image rule above |

## Deleting a theme or palette

```
delete-themes action=delete_theme theme_id=<id>
delete-themes action=delete_color color_id=<id>
```

Affected reports fall back to the team default. Switch them to a replacement first via `enable_theme` / `enable_color`. See `whatagraph-deleting` for full context.

## What MCP can't do here

- Upload a logo image via MCP — logos are referenced by URL; upload via UI first.

## Common pitfalls

- **Palette with fewer colors than chart series** — colors repeat in cycle. Provide 8–12 colors to avoid visible repetition on large charts.
- **Putting a `#` on a text/accent color** — `text_color`, `neutral_color`, `positive_color`, `negative_color`, `accent_fill_color`, `accent_text_color`, `chart_axis_text`, `chart_grid_lines`, `report_accent`, `report_text_color`, `report_title_color` and `chart_colors` are **bare hex**; the renderer prepends the `#`, so a stored `#RRGGBB` becomes `##RRGGBB` and the text/numbers silently render in a dark default. Only the raw-CSS keys (`widget_background`, `icon_symbol`, `icon_background`, `list_odd_fill`, `list_even_fill`, `background`) keep the `#` (or take `rgba()`/`transparent`/gradient).
- **Dark theme with default zebra fills** — omitting `list_even_fill` on a dark palette leaves the hardcoded light default, so list/table/funnel even-rows become unreadable. Set `list_even_fill`/`list_odd_fill` explicitly (see "Dark themes" above).
- **Theme vs palette confusion** — theme controls logos/fonts/layout; palette controls chart colors. A report can use theme A + palette B.
- **Passing a palette's `theme_id` field to `enable_theme`** — palettes returned by `list_colors` carry a `theme_id` attribute (the theme they're bound to); that is **not** the palette's own id and the palette's id is not a theme id. `enable_theme` takes a theme id from `list_themes`; `enable_color` takes a palette id from `list_colors`. Mixing them up enables the wrong asset or errors.
- **Logo URL not publicly accessible** — shared-link viewers won't see it. Use a CDN-backed public URL.
- **Brand colors with low contrast** — charts become unreadable. Test against white + dark report backgrounds.
- **Creating a palette without `theme_id`** — palette still works; binding is purely organizational and any palette can be applied to any report regardless of theme binding.
- **Enabling a theme without also enabling its companion palette** — colors fall back to the team default, producing off-brand output.
- **Editing one section silently rewrites the other** — with `header.apply_to_footer: true` (or `footer.apply_to_header: true`), every `update_theme` mirrors that section onto the other, images included. Set the flag to `false` in the same update to edit them independently.
