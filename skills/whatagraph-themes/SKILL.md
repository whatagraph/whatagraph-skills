---
name: whatagraph-themes
description: Apply themes (logos, fonts, header/footer) and color palettes (series colors) to reports. Use when a user wants to brand a report for a client, apply consistent colors across widgets, or create a reusable palette/theme.
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

## Create a custom color palette

```
manage-themes action=create_color
   name="Acme — Primary"
   colors={
     "widget_colors": ["#FF6B00", "#14213D", "#FCA311", "#E5E5E5"],
     "chart_colors":  ["#FF6B00", "#14213D", "#FCA311", "#E5E5E5", "#000000"],
     "theme_id": <theme_id>
   }
   options={"parent_id": <optional>, "parent_name": "<optional>"}
```

- `widget_colors` — accents used on widget chrome.
- `chart_colors` — series colors on charts (line, bar, pie, etc.).
- Tie a palette to a theme via `theme_id` in `colors`.

## Update a palette

```
manage-themes action=update_color
   color_id=<id>
   colors={"widget_colors":[...], "chart_colors":[...]}
```

## What MCP can't do here

- Delete a theme or palette — UI only.
- Upload a logo image via MCP — logos are referenced by URL; upload via UI first.
- Update a theme's options via MCP (`update_theme` does not exist) — UI only.

## Common pitfalls

- **Palette with fewer colors than chart series** — colors repeat in cycle. Provide 8–12 colors to avoid visible repetition on large charts.
- **Theme vs palette confusion** — theme controls logos/fonts/layout; palette controls chart colors. A report can use theme A + palette B.
- **Logo URL not publicly accessible** — shared-link viewers won't see it. Use a CDN-backed public URL.
- **Brand colors with low contrast** — charts become unreadable. Test against white + dark report backgrounds.
- **Creating a palette without `theme_id`** — palette still works but isn't bound to a specific theme; any theme can use it.
- **Enabling a theme without also enabling its companion palette** — colors fall back to the team default, producing off-brand output.
