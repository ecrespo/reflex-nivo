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
- The event serializer no longer writes `null` into arrays when it stops (depth bound raised from 6
  to 12, and dropped entries are skipped): a hierarchy datum from a drill-down handler can be fed
  straight back to the chart as `data=` without breaking d3-hierarchy.
