---
name: whatagraph-widget-advanced
type: domain
group: report_building
description: Less common widget features. Load when you need a formula row (one metric divided by another on a single widget), to duplicate widgets (in place, in batches, or to another tab), to colour table cells by value with conditional formatting (manual rules or auto colors), to convert a widget's money metrics to another currency or restore them, to set table column widths, or to show ad creative thumbnails in a table. Load `whatagraph-widgets` first; this playbook assumes its binding rules.
required_tools:
  - list-widgets
  - manage-widgets
optional_tools:
  - tool_name: manage-custom-metrics
    purpose: Build a reusable calculated metric instead of a per-widget formula row.
  - tool_name: list-sources
    purpose: Find the channel's creative dimension for table thumbnails.
  - tool_name: manage-report-tabs
    purpose: Move widgets to another tab instead of copying them.
---

# Advanced widget features

This playbook covers less common features of `manage-widgets`. It assumes `whatagraph-widgets` is loaded for the `rows` → `configs` shape, the binding rules, and the grid rules.

## Formula rows: one metric divided by another

A row can render a calculation over the widget's own configs. `rows[].options.operators` makes it a formula row. The value is a **flat list of tokens** that the backend joins into an expression. There are two token types:

| Token | Shape | Meaning |
|---|---|---|
| Config reference | `{"type": "config", "id": <widget_config_id>}` | The value of an existing config on **this** widget. |
| Operator | `{"type": "operator", "operatorId": "divide"}` | One of `plus`, `minus`, `multiply`, `divide`, `bracket-left`, `bracket-right`. |

A cost per acquisition (spend divided by conversions) is three tokens:

```
rows=[{"options": {"formula_title": "Blended CPA",
                   "operators": [{"type": "config", "id": 55192462},
                                 {"type": "operator", "operatorId": "divide"},
                                 {"type": "config", "id": 55192463}]}}]
```

**A config token references a config that already exists. It carries no source or metrics of its own.** So a formula is always a two-call build:

1. `manage-widgets action=create` the widget with its configs bound the ordinary way: one config per operand, each with its own `source_id` and `options.metrics`.
2. `list-widgets action=show` to read the config ids from `rows[].configs[].id`.
3. `manage-widgets action=update` with the `operators` token list that references those ids.

A formula sent at `create` is **rejected** as soon as it names a config id, because no config exists yet. A formula that references a config on a different widget is rejected too. The tool also enforces:

- The operator is the **`operatorId` name**, not the symbol. `{"operatorId": "/"}` is refused; `divide` is correct.
- Every token has a `type` of `config` or `operator`. There is no numeric-constant token, so a formula row cannot multiply by 100 or divide by 1000.
- A config **definition** nested inside a token (a `configs` array, or a `source_id` and `metrics` on the token) is refused. Nothing reads a config there, so that shape used to give a widget with no source and no metrics.

**A formula row is captioned by `rows[].options.formula_title`**, falling back to `options.title`. This is one of the few places where a row-level label is the rendered label, because there is no single config metric to name.

**For a calculation you want on more than one widget, use `manage-custom-metrics` instead** and bind the result like any other metric. That is a real custom metric on the source, reusable across widgets and reports. Its formula is text over single-letter field identifiers, with `+ - * /`, parentheses and numeric constants: `A/B` for a cost per acquisition, `A/B*100` for a rate.

## Duplicate widgets

```
manage-widgets action=duplicate       report_id=<id> widget_id=<id>
manage-widgets action=batch_duplicate report_id=<id> widget_ids=[<id1>, <id2>, <id3>]
```

- When no position is given, the copy is auto-placed at the next free grid slot. It does **not** land at the original widget's position. With an explicit position, the normal overlap rules apply (`auto_place` behaviour).
- `batch_duplicate` always auto-places and tracks each copy's rectangle, so the copies tile across the 6 columns instead of stacking. Duplicate a full row of widgets together, not one widget many times, to keep the layout balanced.
- Conditional formatting is copied with the widget; no extra work is needed.

**To another tab of the same report**, pass `target_tab_id`:

```
manage-widgets action=duplicate       report_id=<id> widget_id=<id>      target_tab_id=<tab_id>
manage-widgets action=batch_duplicate report_id=<id> widget_ids=[...]    target_tab_id=<tab_id>
```

- The target tab must belong to the same report. Copying a widget to another report is not supported.
- The copy is placed on the target tab with the same rules (auto-placed by default).
- Data sources carry over, because both tabs share the report's attached sources.

To move widgets (not copy them) to another tab, use `manage-report-tabs action=move_widgets`.

## Conditional formatting

Colour a table cell by its own value. Each metric (each column) uses one of two modes:

- **Manual rules**: your thresholds, with **both** colours per rule: `text_color` and `background_color`, each independent and optional. Set only `text_color` to recolour the number and leave the background alone. "Red under 100."
- **Auto colors**: one base colour for the background, shaded into seven tints across the column's own lowest-to-highest values. **You do not control the text colour**; it is derived per cell for contrast. "Heatmap this column."

**A metric uses one mode, never both.** The renderer prefers the auto shade and ignores rules, so setting one mode clears the other and says so in `warnings`. A metric set up in the UI earlier can still hold both: check `mode` when manual rules store but never paint.

**Live Table (`102`) only.** Every other widget type is rejected, including offline tables (`126`). For an offline table, see "Faking a heatmap" in `whatagraph-widgets`.

```
list-widgets action=conditional_formats report_id=<id> widget_id=<id>
# → per metric: mode (manual | auto | none), auto_color, and every rule in evaluation order
# → narrow with metric_external_id=<id>

manage-widgets action=set_conditional_formats report_id=<id> widget_id=<id>
   metric_external_id="clicks"
   conditional_formats=[
     {"operator": "greater_than",  "value": 1000,                  "text_color": "#ffffff", "background_color": "#059669"},
     {"operator": "between",       "value": 100, "value_end": 1000, "text_color": "#2a2b30", "background_color": "#fde68a"},
     {"operator": "less_or_equal", "value": 100,                   "text_color": "#ffffff", "background_color": "#dc2626"}
   ]

manage-widgets action=add_conditional_formats ...   # appends, keeps existing rules
```

### Auto colors

```
manage-widgets action=set_auto_colors report_id=<id> widget_id=<id>
   metric_external_id="impressions" auto_color="#059669"

manage-widgets action=set_auto_colors ... auto_color=null   # back to unformatted
```

The seven tints run light to dark from the column's minimum to its maximum and are recomputed on every render, so the colours move when the data does. That suits "show me the big numbers" and is wrong for "flag anything under target". Auto colors takes no `text_color`: if the ask names a text colour, or a threshold must stay put, use manual rules.

### Rules

| Field | Notes |
| --- | --- |
| `operator` | `greater_than`, `greater_or_equal`, `less_than`, `less_or_equal`, `equal`, `not_equal`, `between` |
| `value` | Number to compare the cell against. Required. |
| `value_end` | **Required for `between`**, which matches `value`..`value_end` inclusive. Ignored otherwise. |
| `text_color`, `background_color` | 6-digit hex (`#059669`). Both optional. Colour names and 3-digit hex are rejected; they render as nothing. |
| `position` | Evaluation order. Defaults to the array order you send. |

**First match wins.** Rules are evaluated in `position` order and the first match paints the cell. Order from narrowest to widest: a catch-all `greater_than 0` sent first matches everything, and the bands after it never fire.

### `set` is replace-all

`set_conditional_formats` makes the rules you send the metric's **complete** set and deletes anything already there. Read first with `list-widgets action=conditional_formats`, or you will drop rules a user set in the UI.

- **Adding a band** → `add_conditional_formats`, which appends.
- **Clearing a column** → `set_conditional_formats` with `conditional_formats=[]`.

### Reading back

`list-widgets action=show` flags each table metric with `has_conditional_format`, so you can see which columns carry rules without a second call. Use `action=conditional_formats` to read the rules.

### Formatting is attached to the config, not the metric

Rules (and auto colors, stored in the config's `options.auto_colors`) belong to the widget **config** the row binds: the row's first config, where the UI writes them too.

- **A rebuilt row loses its formatting.** The "omit `rows[].id` to rebuild the binding" workaround in `whatagraph-widgets` recreates the row, and formatting cannot outlive it. `manage-widgets` re-attaches the rules when only the config is replaced, and warns in `warnings` when a removed row took its rules with it. **Read the rules out first, rebuild, then write them back**, and check `warnings` on every table update.
- **`remove_row` discards them**, and reports how many in `warnings`.

## Currency conversion

Convert a widget's money metrics to another currency. Needs the Data Transformation premium feature.

```
list-widgets action=currency_exchange report_id=<id> widget_id=<id>
# → convertible money metrics with external_id, original_currency, exchange_currency

manage-widgets action=convert_currency report_id=<id> widget_id=<id>
   currency_conversions=[{"external_id": "<metric_external_id>", "exchange_currency": "USD"}]

manage-widgets action=restore_currency report_id=<id> widget_id=<id>
# → reverts every converted money metric to its original currency
```

Call `currency_exchange` first to find the convertible metrics and their current `external_id`. A converted metric's id becomes `universal_metric_*`.

## Ad creative thumbnails in a table

A **Table (`102`)** shows the ad creative image in each row when it binds the channel's creative URL dimension, the same one a Media widget binds (e.g. `creative_thumbnail_url` on Meta / Facebook Ads). Nothing else needs switching on.

- **Find the dimension** with `list-sources action=list_dimensions_and_metrics` and bind it like any other dimension. The image comes from the dimension the integration types `creative_url` (its name reads like a thumbnail or image URL).
- **A `creative_link` dimension is separate and optional.** It adds an "Open ad preview" link and draws no image. Leave it out when `display_dimensions_as_columns` is on, where it becomes a column of raw URLs.
- **It changes what one row means.** A creative URL is per ad, so adding it to a campaign-level table splits each campaign into one row per creative. Expect the row count to grow (`whatagraph-widgets` → "Tables truncate silently").
- **Size** with `thumbnail_size`: `small` (default, 32px), `medium` (48px), `large` (64px). Rows grow to fit.
- **Placement**: with `display_dimensions_as_columns` off, the thumbnail sits left of the row's labels (the column is named after the first non-creative dimension); with it on, the creative gets its own column, which cannot be sorted.
- **The image is never cropped**; clicking it opens the full-size preview.
- **Some channels cannot do this.** X (Twitter), X Ads, StackAdapt and Semrush have no creative dimension. Google Search text ads have no image, and `ad_image_url` fills only for Display / PMax / image ads. Check the dimension list before promising thumbnails.

**Table or Media?** Media (`110` / `111`) gives each creative a large tile, best when the creatives are the point and one or two metrics per tile are enough. A table with the creative dimension suits several metrics per creative, or creatives ranked by spend, CTR or conversions.

## Table column widths

Column width is a row display option, in the same place as `sort`, never on the config binding (which stores no width). Set `width` in pixels (greater than 0) on the entry in `rows[].options.metrics[]` or `rows[].options.dimensions[]` whose `external_id` or `identifier` matches the binding. `null` returns the column to automatic sizing.

```
rows=[{"id": <row_id>,
       "options": {"metrics": [{"identifier": 0, "external_id": "sessions", "width": 220}],
                   "dimensions": [{"identifier": 1, "external_id": "campaign_name", "width": 400}]},
       "configs": [...]}]
```

Widths you do not mention are kept, and columns without a width share the space that is left.

On an **offline table** (`126`) the columns are the header cells of `data[0]`, which bind nothing, so address them by position: pass `options.dimensions` entries whose `identifier` is the 0-based column index.

```
rows=[{"id": <row_id>, "options": {"dimensions": [{"identifier": 3, "width": 400}]}}]
```
