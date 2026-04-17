#!/usr/bin/env python3
"""Generate seed-grid uncertainty SVGs for the FLIP ESM2 mini report.

The script intentionally uses only the Python standard library so the blog
environment does not need pandas, numpy, or matplotlib.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from html import escape
from pathlib import Path
from statistics import mean


BLOG_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ROOT = Path(
    "/home/soleaf/jupyterlab/lab/experiment-lab/projects/flip-esm2-lowlabel-lora/experiments"
)
OUTPUT_DIR = BLOG_ROOT / "assets/images/posts/frozen-esm2-lora-low-label-protein-fitness"


RUNS = {
    "gb1_lora": EXPERIMENT_ROOT
    / "exp_30_gb1_35m_lora_b128_b192_b256_balanced_batch8/artifacts/runs/r031/per_seed_metrics.csv",
    "gb1_frozen_128_256": EXPERIMENT_ROOT
    / "exp_29_gb1_35m_frozen_b128_b256_balanced_seed_grid/artifacts/runs/r030/per_seed_metrics.csv",
    "gb1_frozen_192": EXPERIMENT_ROOT
    / "exp_27_gb1_35m_frozen_b192_balanced_seed_grid/artifacts/runs/r028/per_seed_metrics.csv",
    "aav_lora": EXPERIMENT_ROOT
    / "exp_32_aav_35m_lora_b128_b192_b256_balanced_batch8/artifacts/runs/r033/per_seed_metrics.csv",
    "aav_frozen": EXPERIMENT_ROOT
    / "exp_31_aav_35m_frozen_b128_b192_b256_balanced/artifacts/runs/r032/per_seed_metrics.csv",
}


BLUE = "#3f41ff"
FROZEN = "#149b8f"
FROZEN_DARK = "#0b6f66"
INK = "#111111"
MUTED = "#5f6672"
GRID = "#e6e8ee"


@dataclass(frozen=True)
class Series:
    dataset: str
    condition: str
    budget: int
    values: tuple[float, ...]

    @property
    def mean(self) -> float:
        return mean(self.values)

    @property
    def low(self) -> float:
        return min(self.values)

    @property
    def high(self) -> float:
        return max(self.values)


def read_metric_values(path: Path, budgets: set[int] | None = None) -> dict[int, tuple[float, ...]]:
    rows: dict[int, list[tuple[int, int, float]]] = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            budget = int(row["budget"])
            if budgets is not None and budget not in budgets:
                continue
            rows.setdefault(budget, []).append(
                (int(row["budget_seed"]), int(row["training_seed"]), float(row["test_spearman"]))
            )
    return {
        budget: tuple(value for _, _, value in sorted(entries))
        for budget, entries in sorted(rows.items())
    }


def load_series() -> dict[str, list[Series]]:
    gb1_lora = read_metric_values(RUNS["gb1_lora"])
    gb1_frozen = read_metric_values(RUNS["gb1_frozen_128_256"])
    gb1_frozen.update(read_metric_values(RUNS["gb1_frozen_192"]))
    aav_lora = read_metric_values(RUNS["aav_lora"])
    aav_frozen = read_metric_values(RUNS["aav_frozen"])

    def pack(dataset: str, condition: str, values: dict[int, tuple[float, ...]]) -> list[Series]:
        return [Series(dataset, condition, budget, values[budget]) for budget in (128, 192, 256)]

    return {
        "gb1_lora": pack("GB1", "LoRA", gb1_lora),
        "gb1_frozen": pack("GB1", "Frozen", gb1_frozen),
        "aav_lora": pack("AAV", "LoRA", aav_lora),
        "aav_frozen": pack("AAV", "Frozen", aav_frozen),
    }


def fmt(value: float) -> str:
    return f"{value:.3f}"


def xscale(value: float, x0: float, width: float, xmin: float, xmax: float) -> float:
    return x0 + (value - xmin) / (xmax - xmin) * width


def text(x: float, y: float, body: str, **attrs: str | int | float) -> str:
    attr_text = " ".join(f'{key.replace("_", "-")}="{escape(str(value))}"' for key, value in attrs.items())
    return f'<text x="{x:.1f}" y="{y:.1f}" {attr_text}>{escape(body)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, **attrs: str | int | float) -> str:
    attr_text = " ".join(f'{key.replace("_", "-")}="{escape(str(value))}"' for key, value in attrs.items())
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {attr_text}/>'


def circle(x: float, y: float, r: float, **attrs: str | int | float) -> str:
    attr_text = " ".join(f'{key.replace("_", "-")}="{escape(str(value))}"' for key, value in attrs.items())
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" {attr_text}/>'


def diamond(x: float, y: float, r: float, **attrs: str | int | float) -> str:
    attr_text = " ".join(f'{key.replace("_", "-")}="{escape(str(value))}"' for key, value in attrs.items())
    points = f"{x:.1f},{y-r:.1f} {x+r:.1f},{y:.1f} {x:.1f},{y+r:.1f} {x-r:.1f},{y:.1f}"
    return f'<polygon points="{points}" {attr_text}/>'


def draw_series(
    series: Series,
    x0: float,
    width: float,
    y: float,
    xmin: float,
    xmax: float,
    marker: str,
) -> list[str]:
    parts: list[str] = []
    color = BLUE if series.condition == "LoRA" else FROZEN
    mean_x = xscale(series.mean, x0, width, xmin, xmax)
    low_x = xscale(series.low, x0, width, xmin, xmax)
    high_x = xscale(series.high, x0, width, xmin, xmax)
    offsets = (-5, -2, 3, 5, -4, 1, 4, -1, 2)

    parts.append(line(low_x, y, high_x, y, stroke=color, stroke_width=2.0, opacity=0.55))
    parts.append(line(low_x, y - 5, low_x, y + 5, stroke=color, stroke_width=1.7, opacity=0.65))
    parts.append(line(high_x, y - 5, high_x, y + 5, stroke=color, stroke_width=1.7, opacity=0.65))

    for idx, value in enumerate(series.values):
        px = xscale(value, x0, width, xmin, xmax)
        py = y + offsets[idx % len(offsets)]
        if series.condition == "LoRA":
            parts.append(circle(px, py, 3.4, fill=BLUE, opacity=0.26))
        else:
            parts.append(circle(px, py, 3.5, fill=FROZEN, stroke=FROZEN_DARK, stroke_width=0.8, opacity=0.30))

    if marker == "circle":
        if series.condition == "LoRA":
            parts.append(circle(mean_x, y, 6.3, fill=BLUE, stroke="#ffffff", stroke_width=1.4))
        else:
            parts.append(circle(mean_x, y, 6.3, fill=FROZEN, stroke="#ffffff", stroke_width=1.4))
    else:
        if series.condition == "LoRA":
            parts.append(diamond(mean_x, y, 7.4, fill=BLUE, stroke="#ffffff", stroke_width=1.4))
        else:
            parts.append(diamond(mean_x, y, 7.4, fill=FROZEN, stroke="#ffffff", stroke_width=1.4))

    label_x = mean_x + 11
    anchor = "start"
    if label_x > x0 + width - 12:
        label_x = mean_x - 11
        anchor = "end"
    parts.append(
        text(
            label_x,
            y + 4,
            fmt(series.mean),
            font_size=11,
            font_weight=700,
            fill=BLUE if series.condition == "LoRA" else FROZEN_DARK,
            text_anchor=anchor,
        )
    )
    return parts


def defs() -> str:
    return f"""
  <defs>
    <filter id="shadow" x="-12%" y="-18%" width="124%" height="136%">
      <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#111111" flood-opacity="0.07"/>
    </filter>
  </defs>"""


def draw_panel(
    title: str,
    lora: list[Series],
    frozen: list[Series],
    tx: float,
    ty: float,
    xmin: float,
    xmax: float,
    width: float,
    tick_values: tuple[float, ...],
) -> str:
    x0 = 76
    y0 = 34
    centers = {128: 36, 192: 96, 256: 156}
    parts: list[str] = []
    parts.append(f'<g transform="translate({tx:.0f} {ty:.0f})">')
    parts.append(text(190, 0, title, text_anchor="middle", font_size=15, font_weight=700, fill=INK))
    parts.append('<g transform="translate(0 28)">')
    axis_bottom = 190
    parts.append(
        text(
            10,
            95,
            "Label budget",
            text_anchor="middle",
            font_size=11,
            font_weight=700,
            fill=MUTED,
            transform="rotate(-90 10 95)",
        )
    )
    for tick in tick_values:
        x = xscale(tick, x0, width, xmin, xmax)
        dash = "" if abs(tick) < 1e-9 else ' stroke-dasharray="4 8"'
        parts.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{axis_bottom}" stroke="{GRID}" stroke-width="1"{dash}/>')
        parts.append(
            text(
                x,
                axis_bottom + 27,
                "0" if abs(tick) < 1e-9 else f"{tick:.1f}",
                text_anchor="middle",
                font_size=12,
                font_weight=500,
                fill=MUTED,
            )
        )
    parts.append(line(x0, axis_bottom, x0 + width, axis_bottom, stroke=GRID, stroke_width=1))

    for budget in (128, 192, 256):
        parts.append(
            text(
                58,
                centers[budget] + 5,
                str(budget),
                text_anchor="end",
                font_size=12,
                font_weight=600,
                fill=MUTED,
            )
        )

    for series in lora:
        parts.extend(draw_series(series, x0, width, centers[series.budget] - 9, xmin, xmax, marker="circle"))
    for series in frozen:
        parts.extend(draw_series(series, x0, width, centers[series.budget] + 11, xmin, xmax, marker="circle"))

    parts.append("</g></g>")
    return "\n".join(parts)


def featured_svg(series: dict[str, list[Series]]) -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 480" role="img" aria-labelledby="title desc">',
        "  <title id=\"title\">LoRA and frozen Spearman seed-grid ranges by dataset and budget</title>",
        "  <desc id=\"desc\">A two-panel point-range chart compares LoRA and frozen test Spearman across GB1 and AAV budgets. Each panel uses a local x-axis range fitted to the observed seed-pair values. Small points show the nine seed-pair runs, large markers show means, and horizontal lines show min-max seed-pair ranges.</desc>",
        '  <rect width="1040" height="480" fill="#ffffff"/>',
        defs(),
        '  <g font-family="Plus Jakarta Sans, Segoe UI, Roboto, Helvetica, Arial, sans-serif">',
        '    <g transform="translate(52 36)" filter="url(#shadow)">',
        '      <rect x="0" y="0" width="936" height="364" rx="24" fill="#ffffff" stroke="#e6e8ee"/>',
        "    </g>",
        draw_panel("GB1 Test Spearman", series["gb1_lora"], series["gb1_frozen"], 104, 100, 0.25, 0.70, 300, (0.3, 0.4, 0.5, 0.6, 0.7)),
        draw_panel("AAV Test Spearman", series["aav_lora"], series["aav_frozen"], 548, 100, -0.45, 0.55, 300, (-0.4, -0.2, 0.0, 0.2, 0.4)),
        '    <g transform="translate(432 444)" font-size="14" font-weight="500" fill="#111111">',
        '      <circle cx="7" cy="-3" r="6" fill="#3f41ff"/>',
        '      <text x="24" y="2">LoRA</text>',
        f'      <circle cx="108" cy="-3" r="6" fill="{FROZEN}"/>',
        '      <text x="125" y="2">Frozen</text>',
        "    </g>",
        "  </g>",
        "</svg>",
    ]
    return "\n".join(parts)


def aav_svg(series: dict[str, list[Series]]) -> str:
    xmin, xmax = -0.45, 0.55
    ticks = (-0.4, -0.2, 0.0, 0.2, 0.4)
    x0 = 154
    width = 680
    centers = {128: 56, 192: 136, 256: 216}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 460" role="img" aria-labelledby="title desc">',
        '  <title id="title">AAV LoRA and frozen Spearman seed-grid ranges by budget</title>',
        '  <desc id="desc">A point-range chart compares AAV LoRA and frozen test Spearman across budgets 128, 192, and 256. Small points show the nine seed-pair runs, large markers show means, and horizontal lines show min-max seed-pair ranges.</desc>',
        '  <rect width="1040" height="460" fill="#ffffff"/>',
        defs(),
        '  <g font-family="Plus Jakarta Sans, Segoe UI, Roboto, Helvetica, Arial, sans-serif">',
        '    <g transform="translate(118 60)">',
        text(420, 0, "AAV Test Spearman", text_anchor="middle", font_size=15, font_weight=700, fill=INK),
        '      <g transform="translate(0 30)">',
    ]
    axis_bottom = 270
    parts.append(
        "        "
        + text(
            18,
            136,
            "Label budget",
            text_anchor="middle",
            font_size=11,
            font_weight=700,
            fill=MUTED,
            transform="rotate(-90 18 136)",
        )
    )
    for tick in ticks:
        x = xscale(tick, x0, width, xmin, xmax)
        dash = "" if abs(tick) < 1e-9 else ' stroke-dasharray="4 8"'
        parts.append(f'        <line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{axis_bottom}" stroke="{GRID}" stroke-width="1"{dash}/>')
        parts.append(
            "        "
            + text(
                x,
                axis_bottom + 30,
                "0" if abs(tick) < 1e-9 else f"{tick:.1f}",
                text_anchor="middle",
                font_size=12,
                font_weight=500,
                fill=MUTED,
            )
        )
    parts.append("        " + line(x0, axis_bottom, x0 + width, axis_bottom, stroke=GRID, stroke_width=1))
    for budget in (128, 192, 256):
        parts.append(
            "        "
            + text(
                116,
                centers[budget] + 5,
                str(budget),
                text_anchor="end",
                font_size=12,
                font_weight=600,
                fill=MUTED,
            )
        )
    for item in series["aav_lora"]:
        parts.extend("        " + part for part in draw_series(item, x0, width, centers[item.budget] - 11, xmin, xmax, marker="diamond"))
    for item in series["aav_frozen"]:
        parts.extend("        " + part for part in draw_series(item, x0, width, centers[item.budget] + 13, xmin, xmax, marker="diamond"))
    parts.extend(
        [
            "      </g>",
            "    </g>",
            '    <g transform="translate(432 422)" font-size="14" font-weight="500" fill="#111111">',
            '      <circle cx="7" cy="-3" r="6" fill="#3f41ff"/>',
            '      <text x="24" y="2">LoRA</text>',
            f'      <circle cx="108" cy="-3" r="6" fill="{FROZEN}"/>',
            '      <text x="125" y="2">Frozen</text>',
            "    </g>",
            "  </g>",
            "</svg>",
        ]
    )
    return "\n".join(parts)


def main() -> None:
    series = load_series()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "featured-result-map.svg").write_text(featured_svg(series), encoding="utf-8")
    (OUTPUT_DIR / "aav-lora-signal.svg").write_text(aav_svg(series), encoding="utf-8")


if __name__ == "__main__":
    main()
