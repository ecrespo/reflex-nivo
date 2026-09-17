# Changelog

## 0.1.1 — 2026-09-17

Fixes found reviewing the wrappers against the nivo bundles.

- **@nivo/geo**: the wrappers no longer expose what nivo never reads. `GeoMap` offered
  `on_mouse_enter`/`on_mouse_move`/`on_mouse_leave`, `GeoMapCanvas` and `ChoroplethCanvas` offered
  enter/leave and `Choropleth` all three, none of which nivo calls — ten handlers that could never
  fire. `defs`, `fill` and `legends` are gone from `GeoMap`/`GeoMapCanvas`, and `defs`/`fill` from
  `ChoroplethCanvas`, for the same reason. What nivo does read (`Choropleth`'s `defs`/`fill`/
  `legends`, `ChoroplethCanvas`'s `legends`, `on_mouse_move` on both canvas variants) is untouched.
  A handler for one of the removed callbacks now lands on the container, where it does fire.
- **`on_active_id_change`** (Pie, PieCanvas) declares the id it receives instead of a datum dict; it
  is the only nivo callback whose first argument is not an object.
- **Calendar dates from state** get the same local-midnight treatment as literal ones. Only plain
  `YYYY-MM-DD` strings written in the page were normalized, so `from_date=State.start` still shifted
  a day (and a year) west of Greenwich.
- **`key`** goes to the container, the element that is actually the list item in `rx.foreach`.
- **The auto theme is injected once per page** instead of being serialized into every chart: a
  chart's props go from ~4.4 KB to ~230 bytes, a ten-chart page from ~43 KB to ~2.3 KB.
- **Templates**: a value the serializer drops (a DOM node, a React event) interpolates as empty text
  instead of the literal `undefined`, and the template cache is bounded at 256 entries, so a
  template driven by a state Var no longer grows it without end.
- **Stubs**: `create()` is typed as returning `Component`, which is what every factory returns — the
  stubs promised the chart class. `scripts/generate_components.py` now regenerates them, and CI
  fails if the generated wrappers or stubs drift from the generator.

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
