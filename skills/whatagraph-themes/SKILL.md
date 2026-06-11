---
name: whatagraph-themes
description: Apply themes (logos, fonts, header/footer) and color palettes (chart series colors, widget chrome, report canvas) to reports, and create or update reusable palettes and themes. Use when branding a report for a client, applying consistent colors across widgets, or fixing off-brand or black-rendering charts. Covers the exact palette schema (widget_colors object, bare-hex chart_colors, additional_colors).
required_tools:
  - list-themes
  - list-widgets
  - manage-themes
---

# Themes & color palettes

Tools covered: `list-themes`, `manage-themes`.

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
list-themes action=list_themes report_id=<id>           # available themes for a report
list-themes action=list_colors report_id=<id>           # available palettes for a report
```

Themes and palettes are stored at the team level, but the listing endpoint is scoped per-report — `report_id` is required, and the response is filtered to the themes/palettes available to that specific report given the team's plan tier. To see every team-level theme, list against any report on the team.

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

## Create a custom color palette

```
manage-themes action=create_color
   name="Acme — Primary"
   colors={
     "widget_colors": {
       "widget_background": "#FFFFFF", "text_color": "#2B2B2B",
       "positive_color": "#5FA873",   "negative_color": "#D64545",
       "accent_fill_color": "#EAE6D8","accent_text_color": "#C0392B",
       "icon_symbol": "#FFFFFF",       "icon_background": "#C0392B",
       "neutral_color": "#9BA5B0",     "neutral_bg": "#F7FAFC",
       "list_odd_fill": "transparent", "list_even_fill": "#F6F5EC",
       "chart_axis_text": "#8A857A",   "chart_grid_lines": "#E6E3D6",
       "font_family": "inter"
     },
     "chart_colors": ["C0392B","8FA876","E0A33E","D67B5C","6E8B6B","7C9B9A","E8C49A","A0504A"],
     "additional_colors": {
       "background": "#F0F0E3", "report_accent": "#C0392B",
       "report_text_color": "#2B2B2B", "report_title_color": "#C0392B"
     },
     "theme_id": <theme_id>
   }
   options={"parent_id": <optional>, "parent_name": "<optional>"}
```

- **`widget_colors`** is an **object with named keys** — NOT a flat array. Keys: `widget_background`, `text_color`, `positive_color`, `negative_color`, `accent_fill_color`, `accent_text_color`, `icon_symbol`, `icon_background`, `neutral_color`, `neutral_bg`, `list_odd_fill`, `list_even_fill`, `chart_axis_text`, `chart_grid_lines`, `font_family`. These values may keep the leading `#`.
- **`chart_colors`** is an array of **bare hex with NO leading `#`** (6-digit `"C0392B"` or 8-digit-with-alpha `"6366f1ff"`). ⚠️ A `#`-prefixed value passes validation but **renders every chart series black** — always strip the `#` in `chart_colors`. Provide 8–12 colors to avoid repetition on large charts.
- **`additional_colors`** is an **object** controlling the report canvas: `background`, `report_accent`, `report_text_color`, `report_title_color`. Set these to drive the report background and title color; omit to keep the theme default.
- Tie a palette to a theme via `theme_id` in `colors`.

## Update a palette

```
manage-themes action=update_color
   color_id=<id>
   colors={"widget_colors": {...}, "chart_colors": [...bare hex...], "additional_colors": {...}}
```

Same shapes as `create_color` — `widget_colors`/`additional_colors` are objects, `chart_colors` stay **bare hex**. After updating a palette already enabled on a report, re-check the report render (`list-widgets action=csv_export` or the UI) to confirm the change propagated.

## Deleting a theme or palette

Destructive — covered in the `whatagraph-deleting` skill (load it for parameters, cascades, and recovery). Quick facts: two actions (`delete_theme` / `delete_color`), affected reports fall back to the team default, switch them to a replacement first via `enable_theme` / `enable_color`.

## What MCP can't do here

- Upload a logo image via MCP — logos are referenced by URL; upload via UI first.

## Common pitfalls

- **Palette with fewer colors than chart series** — colors repeat in cycle. Provide 8–12 colors to avoid visible repetition on large charts.
- **Charts rendering black** — `chart_colors` were supplied with a leading `#`. Use **bare hex** in `chart_colors` (`C0392B`, not `#C0392B`); `widget_colors` / `additional_colors` keep the `#`.
- **Theme vs palette confusion** — theme controls logos/fonts/layout; palette controls chart colors. A report can use theme A + palette B.
- **Logo URL not publicly accessible** — shared-link viewers won't see it. Use a CDN-backed public URL.
- **Brand colors with low contrast** — charts become unreadable. Test against white + dark report backgrounds.
- **Creating a palette without `theme_id`** — palette still works but isn't bound to a specific theme; any theme can use it.
- **Enabling a theme without also enabling its companion palette** — colors fall back to the team default, producing off-brand output.
