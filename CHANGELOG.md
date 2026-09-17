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
