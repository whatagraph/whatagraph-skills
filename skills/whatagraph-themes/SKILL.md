---
name: whatagraph-themes
type: domain
description: Apply themes (logos, fonts, header/footer) and color palettes (chart series colors, widget chrome, report canvas) to reports, and create or update reusable palettes and themes. Use when branding a report for a client, applying consistent colors across widgets, or fixing off-brand charts. Covers the exact palette schema (widget_colors object, chart_colors array, additional_colors).
required_tools:
  - list-themes
  - list-widgets
  - manage-themes
  - delete-themes
---

# Themes & color palettes

Tools covered: `list-themes`, `manage-themes`, `delete-themes`.

Two concepts:
- **Theme** — logo, fonts, header/footer layout, overall visual skin.
- **Color palette** — the specific colors used in chart series, widget backgrounds, accents.

Themes and palettes live at the team level. They're applied per-report.

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

## Apply a theme to a report

```
manage-themes action=enable_theme
   report_id=<id>
   theme_id=<id>
```

## Apply a color palette to a report

```
manage-themes action=enable_color
   report_id=<id>
   color_id=<id>
```

## Create a custom theme

```
manage-themes action=create_theme
   name="Acme Brand — Light"
   options={
     "header": {...},
     "footer": {...}
   }
```

See `list-themes action=list_themes` for an existing theme's `options` shape.

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
- **Required on `create_color`:** `font_family` (e.g. `"inherit"`), `accent_text_color`, `positive_color`, `negative_color` (bare hex), and `shades` (array of 6 bare hex strings — a legacy field no longer rendered by the UI, but still required by frontend validation when users edit palettes). Pick 6 diverse colors that complement the palette.
- **Hex format matters — two groups of keys:**
  - **Text / accent / chart-line colors are bare hex (NO `#`):** `text_color`, `neutral_color`, `neutral_bg`, `positive_color`, `negative_color`, `accent_fill_color`, `accent_text_color`, `chart_axis_text`, `chart_grid_lines`, and `additional_colors.report_accent` / `report_text_color` / `report_title_color`. The renderer prepends the `#` itself, so a value stored **with** a `#` becomes `##RRGGBB` — an invalid color — and the element falls back to a default (commonly **dark, unreadable text/numbers**). Pass `"2B2B2B"`, not `"#2B2B2B"`.
  - **Backgrounds / fills / icons are raw CSS values (KEEP the `#`, or use `rgba()` / `transparent` / a gradient):** `widget_background`, `icon_symbol`, `icon_background`, `list_odd_fill`, `list_even_fill`, and `additional_colors.background`.
- **`chart_colors`** is an array of bare hex values (6-digit `"C0392B"` or 8-digit-with-alpha `"6366f1ff"`). A leading `#` is stripped automatically; non-hex values are rejected. Provide 8–12 colors to avoid repetition on large charts.
- **`additional_colors`** is an **object** controlling the report canvas: `background` (raw CSS), `report_accent`, `report_text_color`, `report_title_color` (bare hex). Set these to drive the report background and title color; omit to keep the theme default.
- Tie a palette to a theme via `theme_id` in `colors`.

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
- **Creating a palette without `theme_id`** — palette still works but isn't bound to a specific theme; any theme can use it.
- **Enabling a theme without also enabling its companion palette** — colors fall back to the team default, producing off-brand output.
- **Editing one section silently rewrites the other** — with `header.apply_to_footer: true` (or `footer.apply_to_header: true`), every `update_theme` mirrors that section onto the other, images included. Set the flag to `false` in the same update to edit them independently.
