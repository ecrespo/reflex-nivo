# Changelog

## 0.1.0 — 2026-09-17

First release.

- 51 Reflex components wrapping every nivo 0.99.0 chart (SVG, Canvas and HTML variants), generated
  from nivo's TypeScript declarations (`scripts/extract_nivo_props.cjs` + `scripts/generate_components.py`).
- Sized container wrapper with CSS/typo validation.
- JSON-safe event payloads for every nivo callback.
- `nivo.tooltip` / `nivo.template` / `nivo.js` for function props.
- Helpers: `margin`, `axis`, `legend`, `hover_effect`, `scale`, `scheme`, `inherit`, `from_theme`,
  `marker`, `annotation`, pattern/gradient defs, `fill_rule`, `props`.
- Light/dark `themes.auto()` following Reflex's color mode.
- Workarounds: `id_by`, `from_date`/`to_date` renames, local-midnight calendar dates, default
  `layers` for `GeoMapCanvas`.
- 10-page demo app using all components.

Fixed before the first publication:

- Reflex style shorthands (`margin_x`, `bg`, `padding_y`…) are accepted on the chart container; they
  are not CSS property names, so they used to raise a `TypeError` — including in the README's own
  sizing example.
- An explicit `None` now travels as JavaScript `null`, so `axis_bottom=None` really hides the axis
  as documented instead of letting nivo apply its own default. `theme=None` means nivo's own theme;
  omitting `theme` still follows Reflex's color mode.
- Event triggers every Reflex component inherits (`on_click`, `on_mouse_move`…) are no longer sent
  to charts that do not declare them as nivo callbacks, where they were silently dead. They now
  reach the wrapping `<div>` as DOM events, and an unknown `on_*` raises a `TypeError` listing the
  chart's nivo callbacks.
- The event serializer no longer writes `null` into arrays when it stops, and reaches deep enough
  for real hierarchies (bound raised from 6 to 20 levels, dropped entries skipped): a drill-down
  datum can be fed straight back to the chart as `data=` without breaking d3-hierarchy.
- `nivo.tooltip()` no longer renders its template through `dangerouslySetInnerHTML`. Templates may
  use a fixed set of attribute-less tags (`b`, `strong`, `i`, `em`, `u`, `s`, `small`, `code`,
  `span`, `div`, `p`, `br`), which become React elements; everything else, including every
  interpolated value, is rendered as text. A template or a datum built from user input can no
  longer inject an element or an event handler.
- Objects that appear more than once in an event payload without being a cycle keep their data
  instead of disappearing; only a repeat that carries an `id` is replaced by that id, which also
  cuts a dense sankey link payload from ~175 KB to ~2.5 KB. Cycle detection now tracks the path
  being walked, and a node budget bounds pathological structures.
