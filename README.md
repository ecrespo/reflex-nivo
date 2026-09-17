# reflex-nivo

Every chart of [nivo](https://nivo.rocks) — the React data-visualization library built on d3 — as a
[Reflex](https://reflex.dev) custom component.

- **51 components** from **28 nivo packages**, SVG, Canvas and HTML renderers (nivo `0.99.0`).
- **snake_case props** generated from nivo's TypeScript declarations, with types and nivo docs links.
- **Events land in Python**: `on_click`, `on_mouse_enter`, `on_node_click`, `on_arc_click`… receive the
  datum as a JSON-safe `dict` (cycles, DOM nodes and React events are stripped in the browser).
- **Follows Reflex's light/dark mode** out of the box.
- Helpers for axes, legends, scales, color configs, patterns/gradients, markers and annotations,
  plus `nivo.tooltip("<b>{id}</b>: {formattedValue}")` templates and a `nivo.js(...)` escape hatch.

```bash
pip install reflex-nivo
```

## Quick start

```python
import reflex as rx
import reflex_nivo as nivo


class State(rx.State):
    rows: list[dict] = [
        {"country": "AD", "burger": 120, "fries": 80},
        {"country": "AE", "burger": 95, "fries": 130},
    ]
    selected: str = ""

    @rx.event
    def on_bar_click(self, datum: dict):
        self.selected = f"{datum['indexValue']} · {datum['id']} = {datum['value']}"


def index():
    return rx.vstack(
        nivo.bar(
            data=State.rows,
            keys=["burger", "fries"],
            index_by="country",
            group_mode="grouped",
            colors=nivo.scheme("nivo"),
            margin=nivo.margin(top=20, right=110, bottom=50, left=60),
            axis_bottom=nivo.axis(legend="country", legend_position="middle", legend_offset=36),
            legends=[nivo.legend(data_from="keys", anchor="bottom-right", translate_x=100)],
            tooltip=nivo.tooltip("<b>{indexValue}</b> · {id}: {formattedValue}"),
            on_click=State.on_bar_click,
            height="400px",
        ),
        rx.text(State.selected),
    )


app = rx.App()
app.add_page(index)
```

## Components

Each factory wraps nivo's `Responsive*` export. Classes use the nivo name (`nivo.Bar`, `nivo.HeatMapCanvas`…).

| Family | SVG | Canvas | HTML |
| --- | --- | --- | --- |
| Bar | `bar` | `bar_canvas` | |
| Line | `line` | `line_canvas` | |
| Pie | `pie` | `pie_canvas` | |
| Radar · RadialBar · PolarBar | `radar` · `radial_bar` · `polar_bar` | | |
| Waffle | `waffle` | `waffle_canvas` | `waffle_html` |
| ScatterPlot | `scatterplot` | `scatterplot_canvas` | |
| SwarmPlot | `swarmplot` | `swarmplot_canvas` | |
| BoxPlot · Voronoi | `boxplot` · `voronoi` | | |
| HeatMap | `heatmap` | `heatmap_canvas` | |
| TreeMap | `treemap` | `treemap_canvas` | `treemap_html` |
| CirclePacking | `circle_packing` | `circle_packing_canvas` | `circle_packing_html` |
| Sunburst | `sunburst` | | |
| Icicle | `icicle` | | `icicle_html` |
| Tree | `tree` | `tree_canvas` | |
| Sankey · Funnel · Marimekko | `sankey` · `funnel` · `marimekko` | | |
| Chord | `chord` | `chord_canvas` | |
| Network | `network` | `network_canvas` | |
| ParallelCoordinates | `parallel_coordinates` | `parallel_coordinates_canvas` | |
| Calendar | `calendar` | `calendar_canvas` | |
| TimeRange · Stream · Bump · AreaBump · Bullet | `time_range` · `stream` · `bump` · `area_bump` · `bullet` | | |
| GeoMap | `geo_map` | `geo_map_canvas` | |
| Choropleth | `choropleth` | `choropleth_canvas` | |

The data shape and every prop are documented on nivo.rocks (each class docstring links to its page).
Convert prop names to snake_case: `indexBy` → `index_by`, `enableGridX` → `enable_grid_x`.

### Renamed props

| nivo | reflex-nivo | why |
| --- | --- | --- |
| `id` (Pie, Sunburst, CirclePacking, SwarmPlot, Marimekko) | `id_by` | `id` is the HTML id of the container |
| `from` / `to` (Calendar, TimeRange) | `from_date` / `to_date` | `from` is a Python keyword |

Plain `YYYY-MM-DD` values for `from_date`/`to_date` are sent as local midnight, so calendars do not
shift one day (and one year) back west of Greenwich.

## Sizing

nivo's responsive charts fill their parent, so every factory returns the chart inside a `<div>`.
`width` (default `"100%"`), `height` (default `"400px"`) and any other CSS prop, `class_name`, `id`
or `style` go to that container. Anything that is neither a nivo prop nor CSS raises a `TypeError`
with a suggestion, so typos like `enable_gridx` do not fail silently.

```python
nivo.pie(data=State.pie, height="320px", max_width="600px", margin_x="auto")
```

(`margin` itself is nivo's chart margin: use `nivo.margin(top=.., right=.., bottom=.., left=..)`.)

## Events

All nivo callbacks are exposed as event triggers. The handler receives nivo's first callback argument
(datum, point, slice, node, cell, serie, link, feature, dimensions, active id…), serialized in the
browser: functions, DOM nodes and React events are dropped, repeated/cyclic objects are replaced by
their `id`, and depth is bounded.

```python
class State(rx.State):
    @rx.event
    def drill_down(self, node: dict):
        if node["data"].get("children"):
            self.sunburst = node["data"]  # the raw datum travels with the event


nivo.sunburst(data=State.sunburst, id_by="name", value="loc", on_click=State.drill_down)
```

Only the callbacks a chart actually declares carry a datum, and they differ per chart: `@nivo/bar`
exposes `on_click`, `on_mouse_enter` and `on_mouse_leave`, while `@nivo/stream` exposes none of them.
Any other `on_*` is attached to the wrapping `<div>` as a plain DOM event, so it fires for the whole
chart area but receives no datum (write the handler without arguments). An `on_*` that is neither
raises a `TypeError` listing the chart's nivo callbacks.

`on_mouse_move` fires very often; on the charts that expose it, prefer click/enter/leave or throttle
it: `on_mouse_move=State.hover.throttle(100)`.

### Hiding a prop

Passing `None` sends JavaScript `null`, which turns the feature off instead of falling back to nivo's
default — that is how you hide an axis:

```python
nivo.bar(data=State.rows, axis_bottom=None, axis_left=None)  # no axes
nivo.pie(data=State.pie, theme=None)  # nivo's own theme instead of the Reflex one
```

## Helpers

```python
nivo.margin(top=20, right=20, bottom=40, left=50)
nivo.axis(legend="price", legend_position="middle", legend_offset=-40, tick_rotation=-45, format=" >-$.2f")
nivo.legend(
    anchor="bottom-right", direction="column", translate_x=100, effects=[nivo.hover_effect(item_opacity=1)]
)
nivo.scale("time", format="%Y-%m-%d", precision="day")
nivo.scheme("category10")  # {"scheme": "category10"}
nivo.inherit("color", ("darker", 1.6))  # inherited color
nivo.from_theme("background")  # color from theme
nivo.marker("y", 100, legend="target")
nivo.annotation({"id": "fries"}, type_="circle", note="max", note_x=40, note_y=-30)
nivo.pattern_dots_def("dots", background="inherit", color="#38bcb2")
nivo.pattern_lines_def("lines", rotation=-45) / nivo.pattern_squares_def(...) / nivo.linear_gradient_def(...)
nivo.fill_rule("dots", {"id": "fries"})
nivo.props(any_snake_case="option")  # generic camelCase dict builder
```

Constants: `nivo.COLOR_SCHEMES` (categorical/diverging/sequential), `nivo.CURVES`, `nivo.MOTION_CONFIGS`.

### Functions: templates, tooltips and raw JS

nivo accepts functions for labels, formatters, accessors, tooltips and custom layers.

```python
# Formatter/label from a {path} template, evaluated in the browser:
label = nivo.template("{id}: {formattedValue}")

# Tooltip component from an HTML template. Interpolated values are escaped, the container
# uses the chart theme's tooltip style. The template itself can be a state Var.
tooltip = nivo.tooltip("<b>{datum.label}</b><br/>{datum.formattedValue}", style={"min_width": "120px"})

# Anything else: a raw JavaScript expression (never build it from user input).
value_format = nivo.js("v => `${v.toLocaleString()} €`")
node_size = nivo.js("n => n.size")
```

Most formatters also accept d3-format / d3-time-format strings directly (`value_format=".2s"`,
`axis(format="%b %d")`).

## Themes

Charts use `nivo.themes.auto()` unless you pass `theme=`: a light/dark pair built on the Radix gray
scale that switches with `rx.color_mode`. Customize or pin it:

```python
theme = nivo.themes.auto({"grid": {"line": {"strokeDasharray": "4 4"}}})  # both modes
theme = nivo.themes.auto(light={"text": {"fill": "#333"}}, dark={"text": {"fill": "#eee"}})
theme = nivo.themes.DARK  # fixed
theme = State.computed_theme  # any nivo theme dict
theme = {}  # nivo's own default
```

## Demo

`nivo_demo/` is a 10-page app that uses all 51 components with live state controls, an event
inspector, drill-down/zoom interactions, geo projections, canvas variants with thousands of marks and
customization examples.

```bash
uv venv && uv pip install -e . && cd nivo_demo && uv pip install -r requirements.txt
uv run reflex run   # http://localhost:3010 (backend on 8010)
```

World country shapes in the demo come from the nivo website dataset (Natural Earth).

## Regenerating the wrappers

The chart modules in `custom_components/reflex_nivo/charts/` are generated from nivo's typings:

```bash
# in a scratch directory
npm i typescript@5 @types/react@19 react@19 react-dom@19 @nivo/{bar,line,pie,...}@0.99.0
node /path/to/reflex-nivo/scripts/extract_nivo_props.cjs bar boxplot bullet bump calendar chord \
  circle-packing funnel heatmap icicle line marimekko network pie polar-bar radar radial-bar sankey \
  scatterplot stream sunburst swarmplot tree treemap voronoi waffle > /path/to/reflex-nivo/scripts/nivo_props.json
# back in the repo (geo and parallel-coordinates ship no usable typings: see scripts/nivo_manual_props.json)
python scripts/generate_components.py
```

Bump `NIVO_VERSION` in `custom_components/reflex_nivo/constants.py` together with the extraction.

## Development

```bash
uv pip install -e ".[dev]"
uv run pytest
uv run reflex component build     # generates .pyi stubs, then sdist + wheel in dist/
```

## License

MIT © Ernesto Crespo. nivo is MIT © Raphaël Benitte.
