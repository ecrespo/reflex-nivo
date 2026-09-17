"""Sample datasets for the demo, shaped like the examples on nivo.rocks."""

from __future__ import annotations

import datetime as dt
import json
import math
import random
from functools import cache
from pathlib import Path
from typing import Any

COUNTRIES = ["AD", "AE", "AF", "AG", "AI", "AL", "AM"]
FOODS = ["hot dog", "burger", "sandwich", "kebab", "fries", "donut"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LANGUAGES = ["python", "go", "rust", "typescript", "elixir"]


def _rng(seed: int | None) -> random.Random:
    return random.Random(seed)


# --------------------------------------------------------------------------- #
# Bars & lines
# --------------------------------------------------------------------------- #
def bar_data(seed: int | None = 1) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [{"country": c, **{food: rng.randint(10, 190) for food in FOODS}} for c in COUNTRIES]


def bar_canvas_data(seed: int | None = 2, size: int = 120) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {"id": f"#{i:03d}", "a": rng.randint(5, 80), "b": rng.randint(5, 80), "c": rng.randint(5, 80)}
        for i in range(size)
    ]


def line_data(seed: int | None = 3) -> list[dict[str, Any]]:
    rng = _rng(seed)
    series = []
    for name in ["japan", "france", "us", "germany"]:
        value = rng.randint(80, 160)
        points = []
        for month in MONTHS:
            value = max(5, value + rng.randint(-35, 35))
            points.append({"x": month, "y": value})
        series.append({"id": name, "data": points})
    return series


def time_series(seed: int | None = 4, days: int = 90) -> list[dict[str, Any]]:
    rng = _rng(seed)
    start = dt.date(2026, 6, 1)
    series = []
    for name, base in [("requests", 420), ("errors", 60)]:
        value = base
        data = []
        for i in range(days):
            value = max(1, value + rng.randint(-base // 8, base // 8))
            data.append({"x": (start + dt.timedelta(days=i)).isoformat(), "y": value})
        series.append({"id": name, "data": data})
    return series


def line_canvas_data(seed: int | None = 5, series: int = 8, points: int = 400) -> list[dict[str, Any]]:
    rng = _rng(seed)
    result = []
    for s in range(series):
        phase = rng.random() * math.tau
        result.append(
            {
                "id": f"signal {s + 1}",
                "data": [
                    {"x": i, "y": round(math.sin(i / 25 + phase) * (10 + s * 3) + rng.gauss(0, 2), 2)}
                    for i in range(points)
                ],
            }
        )
    return result


# --------------------------------------------------------------------------- #
# Radial
# --------------------------------------------------------------------------- #
def pie_data(seed: int | None = 6) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [{"id": lang, "label": lang.title(), "value": rng.randint(50, 600)} for lang in LANGUAGES]


def radar_data(seed: int | None = 7) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {"taste": taste, **{wine: rng.randint(20, 120) for wine in ["chardonay", "carmenere", "syrah"]}}
        for taste in ["fruity", "bitter", "heavy", "strong", "sunny"]
    ]


def radial_bar_data(seed: int | None = 8) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {
            "id": store,
            "data": [{"x": cat, "y": rng.randint(20, 280)} for cat in ["Vegetables", "Fruits", "Meat"]],
        }
        for store in ["Supermarket", "Combini", "Online", "Marché"]
    ]


def polar_bar_data(seed: int | None = 9) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {
            "month": m,
            "rent": rng.randint(20, 60),
            "groceries": rng.randint(10, 40),
            "leisure": rng.randint(5, 30),
        }
        for m in MONTHS
    ]


def waffle_data() -> list[dict[str, Any]]:
    return [
        {"id": "cats", "label": "Cats", "value": 35},
        {"id": "dogs", "label": "Dogs", "value": 28},
        {"id": "rabbits", "label": "Rabbits", "value": 17},
    ]


# --------------------------------------------------------------------------- #
# Distributions
# --------------------------------------------------------------------------- #
def scatter_data(seed: int | None = 10, groups: int = 4, points: int = 40) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {
            "id": f"group {chr(65 + g)}",
            "data": [
                {"x": round(rng.gauss(30 + g * 15, 8), 1), "y": round(rng.gauss(60 - g * 8, 12), 1)}
                for _ in range(points)
            ],
        }
        for g in range(groups)
    ]


def swarm_data(seed: int | None = 11, size: int = 90) -> list[dict[str, Any]]:
    rng = _rng(seed)
    groups = ["group A", "group B", "group C"]
    return [
        {
            "id": f"{i}",
            "group": groups[i % 3],
            "price": round(rng.gauss(200 + (i % 3) * 60, 45), 1),
            "volume": rng.randint(4, 20),
        }
        for i in range(size)
    ]


def boxplot_data(seed: int | None = 12) -> list[dict[str, Any]]:
    rng = _rng(seed)
    rows = []
    for g, (mu, sd) in {"Alpha": (10, 2), "Beta": (13, 3), "Gamma": (8, 1.5), "Delta": (15, 4)}.items():
        for sub in ["F", "M"]:
            for _ in range(40):
                rows.append(
                    {
                        "group": g,
                        "subgroup": sub,
                        "mu": mu,
                        "sd": sd,
                        "n": 40,
                        "value": round(rng.gauss(mu, sd), 2),
                    }
                )
    return rows


def heatmap_data(seed: int | None = 13) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {"id": day, "data": [{"x": f"{h:02d}h", "y": rng.randint(-40, 100)} for h in range(0, 24, 2)]}
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    ]


def voronoi_data(seed: int | None = 14, size: int = 60) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [{"id": f"p{i}", "x": rng.random() * 100, "y": rng.random() * 100} for i in range(size)]


# --------------------------------------------------------------------------- #
# Hierarchies
# --------------------------------------------------------------------------- #
@cache
def hierarchy() -> dict[str, Any]:
    rng = _rng(15)

    def leaves(prefix: str, n: int) -> list[dict[str, Any]]:
        return [{"name": f"{prefix}{i}", "loc": rng.randint(1_000, 90_000)} for i in range(1, n + 1)]

    return {
        "name": "reflex-app",
        "children": [
            {
                "name": "frontend",
                "children": [
                    {"name": "components", "children": leaves("comp_", 5)},
                    {"name": "pages", "children": leaves("page_", 4)},
                    {"name": "styles", "children": leaves("css_", 2)},
                ],
            },
            {
                "name": "backend",
                "children": [
                    {"name": "state", "children": leaves("state_", 4)},
                    {"name": "models", "children": leaves("model_", 3)},
                    {"name": "api", "children": leaves("route_", 3)},
                ],
            },
            {"name": "tests", "children": leaves("test_", 4)},
            {"name": "docs", "children": leaves("doc_", 2)},
        ],
    }


# --------------------------------------------------------------------------- #
# Flows & relations
# --------------------------------------------------------------------------- #
def sankey_data() -> dict[str, Any]:
    nodes = ["Visitors", "Organic", "Ads", "Social", "Signup", "Bounce", "Trial", "Paid"]
    links = [
        ("Visitors", "Organic", 120),
        ("Visitors", "Ads", 80),
        ("Visitors", "Social", 50),
        ("Organic", "Signup", 70),
        ("Organic", "Bounce", 50),
        ("Ads", "Signup", 30),
        ("Ads", "Bounce", 50),
        ("Social", "Signup", 20),
        ("Social", "Bounce", 30),
        ("Signup", "Trial", 90),
        ("Signup", "Paid", 30),
    ]
    return {
        "nodes": [{"id": n} for n in nodes],
        "links": [{"source": s, "target": t, "value": v} for s, t, v in links],
    }


CHORD_KEYS = ["John", "Raoul", "Jane", "Marcel", "Ibrahim"]


def chord_matrix(seed: int | None = 16) -> list[list[int]]:
    rng = _rng(seed)
    return [[rng.randint(0, 400) for _ in CHORD_KEYS] for _ in CHORD_KEYS]


def network_data(seed: int | None = 17) -> dict[str, Any]:
    rng = _rng(seed)
    nodes = [{"id": "core", "height": 2, "size": 28, "color": "rgb(97, 205, 187)"}]
    links = []
    for i in range(6):
        hub = f"hub {i}"
        nodes.append({"id": hub, "height": 1, "size": 18, "color": "rgb(244, 117, 96)"})
        links.append({"source": "core", "target": hub, "distance": 60})
        for j in range(rng.randint(3, 6)):
            leaf = f"{hub}.{j}"
            nodes.append({"id": leaf, "height": 0, "size": 10, "color": "rgb(232, 193, 160)"})
            links.append({"source": hub, "target": leaf, "distance": 40})
    return {"nodes": nodes, "links": links}


def parallel_data(seed: int | None = 18, size: int = 30) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {
            "id": f"car {i}",
            "kind": rng.choice(["sedan", "suv", "sport"]),
            "power": rng.randint(90, 420),
            "weight": rng.randint(900, 2400),
            "consumption": round(rng.uniform(4, 16), 1),
            "price": rng.randint(15, 120),
        }
        for i in range(size)
    ]


PARALLEL_VARIABLES = [
    {
        "id": "power",
        "value": "power",
        "min": 0,
        "max": 450,
        "legend": "power (hp)",
        "legendPosition": "start",
        "legendOffset": 20,
    },
    {
        "id": "weight",
        "value": "weight",
        "min": 800,
        "max": 2500,
        "legend": "weight (kg)",
        "legendPosition": "start",
        "legendOffset": 20,
    },
    {
        "id": "consumption",
        "value": "consumption",
        "min": 0,
        "max": 18,
        "legend": "l/100km",
        "legendPosition": "start",
        "legendOffset": 20,
    },
    {
        "id": "price",
        "value": "price",
        "min": 0,
        "max": 130,
        "legend": "price (k€)",
        "legendPosition": "start",
        "legendOffset": 20,
    },
]


def funnel_data() -> list[dict[str, Any]]:
    return [
        {"id": "visited", "label": "Visited", "value": 88_000},
        {"id": "signed_up", "label": "Signed up", "value": 41_200},
        {"id": "activated", "label": "Activated", "value": 22_900},
        {"id": "subscribed", "label": "Subscribed", "value": 8_300},
        {"id": "renewed", "label": "Renewed", "value": 5_100},
    ]


def marimekko_data(seed: int | None = 19) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {
            "statement": s,
            "participation": rng.randint(5, 30),
            "stronglyAgree": rng.randint(5, 30),
            "agree": rng.randint(5, 30),
            "disagree": rng.randint(5, 30),
            "stronglyDisagree": rng.randint(5, 30),
        }
        for s in ["it's good", "it's sweet", "it's spicy", "worth eating", "worth buying"]
    ]


MARIMEKKO_DIMENSIONS = [
    {"id": "disagree strongly", "value": "stronglyDisagree"},
    {"id": "disagree", "value": "disagree"},
    {"id": "agree", "value": "agree"},
    {"id": "agree strongly", "value": "stronglyAgree"},
]


# --------------------------------------------------------------------------- #
# Time
# --------------------------------------------------------------------------- #
def calendar_data(
    seed: int | None = 20, start: dt.date = dt.date(2025, 1, 1), days: int = 620
) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {"day": (start + dt.timedelta(days=i)).isoformat(), "value": rng.randint(0, 400)}
        for i in range(days)
        if rng.random() > 0.25
    ]


def stream_data(seed: int | None = 21) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {name: rng.randint(10, 200) for name in ["Raoul", "Josiane", "Marcel", "René", "Paul", "Jacques"]}
        for _ in range(16)
    ]


def bump_data(seed: int | None = 22) -> list[dict[str, Any]]:
    rng = _rng(seed)
    teams = ["Serie A", "Serie B", "Serie C", "Serie D", "Serie E", "Serie F"]
    years = list(range(2019, 2027))
    ranks = {t: [] for t in teams}
    for _ in years:
        order = teams[:]
        rng.shuffle(order)
        for rank, team in enumerate(order, 1):
            ranks[team].append(rank)
    return [
        {"id": t, "data": [{"x": y, "y": r} for y, r in zip(years, ranks[t], strict=True)]} for t in teams
    ]


def area_bump_data(seed: int | None = 23) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [
        {"id": tech, "data": [{"x": year, "y": rng.randint(10, 40)} for year in range(2019, 2027)]}
        for tech in ["JavaScript", "Python", "Go", "Rust", "Elixir"]
    ]


def bullet_data() -> list[dict[str, Any]]:
    return [
        {"id": "revenue", "title": "Revenue", "ranges": [150, 225, 300], "measures": [220], "markers": [250]},
        {"id": "profit", "title": "Profit", "ranges": [20, 25, 30], "measures": [21, 23], "markers": [26]},
        {
            "id": "orders",
            "title": "Orders",
            "ranges": [350, 500, 600],
            "measures": [100, 320],
            "markers": [550],
        },
        {
            "id": "satisfaction",
            "title": "NPS",
            "ranges": [3.5, 4.25, 5],
            "measures": [3.2, 4.7],
            "markers": [4.4],
        },
    ]


# --------------------------------------------------------------------------- #
# Geo
# --------------------------------------------------------------------------- #
@cache
def world_features() -> list[dict[str, Any]]:
    path = Path(__file__).parent / "geo" / "world_countries.json"
    return json.loads(path.read_text())["features"]


def choropleth_data(seed: int | None = 24) -> list[dict[str, Any]]:
    rng = _rng(seed)
    return [{"id": f["id"], "value": rng.randint(0, 1_000_000)} for f in world_features()]
