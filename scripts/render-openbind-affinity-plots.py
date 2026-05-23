#!/usr/bin/env python
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / "lab/experiment-lab/projects/openbind-affinity-baseline-stress"
OUT = ROOT / "assets/images/posts/openbind-affinity-baseline-audit"

R002 = LAB / "experiments/exp_02_mw_property_baseline_stress/artifacts/runs/r002"
R003 = LAB / "experiments/exp_03_scaffold_cluster_sensitivity/artifacts/runs/r003"

BLUE = "#3f41ff"
HATCH_STROKE = "#EAEAFC"
HATCH_OUTLINE = "#3f41ff"
HATCH_FILL = "#EAEAFC"
INK = "#111111"
MUTED = "#5f6672"
GRID = "#e6e8ee"
AXIS = "#cfd4dd"
GRAY = "#9aa1ad"
DARK_GRAY = "#7f8796"
LIGHT_BLUE = "#eef0ff"
LIGHT_GRAY = "#eef0f4"

PUBLISHED = {
    "aev_plig",
    "aqaffinity",
    "boltz_2",
    "clogp",
    "gnina_crystal",
    "molecular_weight",
    "smina_crystal",
}

DISPLAY_METHOD = {
    "cv_ecfp_ridge": "ECFP ridge",
    "cv_rdkit_descriptor_rf": "RDKit RF",
    "cv_rdkit_descriptor_ridge": "RDKit ridge",
    "cv_mw_clogp_ridge": "MW+cLogP ridge",
    "molecular_weight": "molecular weight",
    "gnina_crystal": "gnina crystal",
    "boltz_2": "Boltz-2",
    "smina_crystal": "smina crystal",
    "aev_plig": "AEV-PLIG",
    "aqaffinity": "AqAffinity",
    "clogp": "cLogP",
}

FIG1_GROUP_TOP = {
    "cv_ecfp_ridge": 112,
    "molecular_weight": 226,
    "gnina_crystal": 340,
}
FIG1_GROUP_BOTTOM = {
    "cv_ecfp_ridge": 226,
    "molecular_weight": 340,
    "gnina_crystal": 552,
}

FIG1_GROUP_LABEL_X = 48
FIG1_GROUP_RULE_X = 174
FIG1_LABEL_LEFT = 196
FIG1_PLOT_LEFT = 270
FIG1_PLOT_RIGHT = 1010


def setup() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": AXIS,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "font.family": ["DejaVu Sans", "sans-serif"],
            "font.size": 11,
            "svg.fonttype": "none",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save(fig: plt.Figure, stem: str, png: bool = True, svg: bool = True) -> None:
    if svg:
        fig.savefig(OUT / f"{stem}.svg", format="svg", bbox_inches="tight", pad_inches=0.08)
    if png:
        fig.savefig(OUT / f"{stem}.png", dpi=180, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def style_axis(ax: plt.Axes, *, xgrid: bool = True, ygrid: bool = False) -> None:
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(axis="both", length=0, pad=7)
    if xgrid:
        ax.grid(axis="x", color=GRID, linewidth=1, linestyle=(0, (3, 7)))
    if ygrid:
        ax.grid(axis="y", color=GRID, linewidth=1, linestyle=(0, (3, 7)))
    ax.set_axisbelow(True)


def label_bars(ax: plt.Axes, bars, *, pad: float = 0.012) -> None:
    x0, x1 = ax.get_xlim()
    span = x1 - x0
    for bar in bars:
        value = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        if value >= 0:
            x = value + pad * span
            ha = "left"
        else:
            x = 0.008
            ha = "left"
        ax.text(x, y, f"{value:.3f}", va="center", ha=ha, color=INK, fontsize=10.5, fontweight="semibold")


def title_block(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.5, 0.965, title, ha="center", va="top", color=INK, fontsize=15, fontweight="bold")
    if subtitle:
        fig.text(0.5, 0.925, subtitle, ha="center", va="top", color=MUTED, fontsize=10.8, fontweight="medium")


def sx(value: float, *, left: float = 330, right: float = 930, min_v: float = -0.12, max_v: float = 0.72) -> float:
    return left + (value - min_v) / (max_v - min_v) * (right - left)


def write_raw_vs_residual_svg(metrics: pd.DataFrame) -> None:
    method_order = [
        "cv_ecfp_ridge",
        "cv_rdkit_descriptor_rf",
        "cv_rdkit_descriptor_ridge",
        "molecular_weight",
        "cv_mw_clogp_ridge",
        "clogp",
        "gnina_crystal",
        "boltz_2",
        "smina_crystal",
        "aev_plig",
        "aqaffinity",
    ]
    role = {
        "cv_ecfp_ridge": "same-campaign ligand-only control",
        "cv_rdkit_descriptor_rf": "same-campaign ligand-only control",
        "cv_rdkit_descriptor_ridge": "same-campaign ligand-only control",
        "molecular_weight": "property baseline",
        "cv_mw_clogp_ridge": "property baseline",
        "clogp": "property baseline",
        "gnina_crystal": "published prediction file",
        "boltz_2": "published prediction file",
        "smina_crystal": "published prediction file",
        "aev_plig": "published prediction file",
        "aqaffinity": "published prediction file",
    }
    role_label = {
        "cv_ecfp_ridge": ("EV-A71 TRAINED", "LIGAND-ONLY"),
        "molecular_weight": ("SIMPLE PROPERTY", "BASELINES"),
        "gnina_crystal": ("PUBLISHED", "BENCHMARK SCORES"),
    }
    rows = metrics.set_index("method").loc[method_order].reset_index()
    width, height = 1120, 650
    label_left = FIG1_LABEL_LEFT
    plot_left, plot_right = FIG1_PLOT_LEFT, FIG1_PLOT_RIGHT
    group_label_x = FIG1_GROUP_LABEL_X
    group_rule_x = FIG1_GROUP_RULE_X
    zero = sx(0, left=plot_left, right=plot_right)
    y0, step = 126, 38
    row_h = 14
    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '  <title id="title">Raw and residual OpenBind affinity score comparison</title>',
        '  <desc id="desc">Horizontal bar chart comparing Spearman correlation with original pKD and Spearman correlation after removing MW+cLogP trend for EV-A71 trained ligand-only controls, simple property baselines, and published benchmark scores.</desc>',
        f'  <rect width="{width}" height="{height}" fill="#ffffff"/>',
        "  <defs>",
        '    <pattern id="removal-hatch" width="6" height="6" patternUnits="userSpaceOnUse">',
        f'      <rect width="6" height="6" fill="{HATCH_FILL}"/>',
        f'      <path d="M-1 -1 L7 7 M7 -1 L-1 7" stroke="{HATCH_STROKE}" stroke-width="1.15" opacity="0.68"/>',
        "    </pattern>",
        "    <style>",
        "      text { font-family: 'Plus Jakarta Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }",
        "      .title { fill: #111111; font-size: 15px; font-weight: 700; }",
        "      .method { fill: #111111; font-size: 12.5px; font-weight: 650; }",
        "      .role { fill: #5f6672; font-size: 9.6px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }",
        "      .tick { fill: #5f6672; font-size: 12px; font-weight: 500; }",
        "      .axis-label { fill: #5f6672; font-size: 12.5px; font-weight: 600; }",
        "      .grid { stroke: #e6e8ee; stroke-width: 1; stroke-dasharray: 4 8; }",
        "      .axis { stroke: #cfd4dd; stroke-width: 1.2; }",
        "      .zero { stroke: #5f6672; stroke-width: 1.35; }",
        "      .raw { fill: #3f41ff; }",
        "      .adjusted { fill: url(#removal-hatch); stroke: #3f41ff; stroke-width: 0.9; }",
        "      .divider { stroke: #e6e8ee; stroke-width: 1; }",
        "      .legend { fill: #5f6672; font-size: 11.5px; font-weight: 600; }",
        "    </style>",
        "  </defs>",
        '  <text x="560" y="42" text-anchor="middle" class="title">pKD correlation is not the residual signal</text>',
        '  <rect x="438" y="74" width="18" height="14" rx="4" class="raw"/>',
        '  <text x="464" y="86" class="legend">original pKD</text>',
        '  <rect x="572" y="74" width="18" height="14" rx="4" class="adjusted"/>',
        '  <text x="598" y="86" class="legend">after MW+cLogP removal</text>',
    ]
    for tick in [-0.1, 0.0, 0.1, 0.3, 0.5, 0.7]:
        x = sx(tick, left=plot_left, right=plot_right)
        if tick not in {-0.1, 0.7}:
            cls = "zero" if tick == 0 else "grid"
            lines.append(f'  <line x1="{x:.1f}" y1="98" x2="{x:.1f}" y2="556" class="{cls}"/>')
        label = "0" if tick == 0 else f"{tick:.1f}"
        lines.append(f'  <text x="{x:.1f}" y="584" text-anchor="middle" class="tick">{label}</text>')
    lines.append(f'  <line x1="{plot_left}" y1="556" x2="{plot_right}" y2="556" class="axis"/>')
    lines.append(f'  <line x1="{group_rule_x}" y1="112" x2="{group_rule_x}" y2="552" class="divider"/>')
    lines.append(f'  <text x="{(plot_left + plot_right) / 2:.1f}" y="620" text-anchor="middle" class="axis-label">Spearman correlation</text>')

    for idx, row in rows.iterrows():
        method = str(row["method"])
        raw = float(row["raw_spearman"])
        residual = float(row["residual_spearman"])
        y = y0 + idx * step
        if method in role_label:
            top = FIG1_GROUP_TOP[method]
            bottom = FIG1_GROUP_BOTTOM[method]
            center = (top + bottom) / 2
            first, second = role_label[method]
            lines.append(f'  <text x="{group_label_x}" y="{center - 6:.1f}" class="role">{escape(first)}</text>')
            lines.append(f'  <text x="{group_label_x}" y="{center + 7:.1f}" class="role">{escape(second)}</text>')
        if idx in [3, 6]:
            lines.append(f'  <line x1="{group_label_x}" y1="{y - 18}" x2="{plot_right}" y2="{y - 18}" class="divider"/>')
        lines.append(f'  <text x="{label_left}" y="{y + 4}" class="method">{escape(DISPLAY_METHOD.get(method, method))}</text>')
        raw_x0 = min(zero, sx(raw, left=plot_left, right=plot_right))
        raw_w = abs(sx(raw, left=plot_left, right=plot_right) - zero)
        res_x0 = min(zero, sx(residual, left=plot_left, right=plot_right))
        res_w = abs(sx(residual, left=plot_left, right=plot_right) - zero)
        lines.append(f'  <rect x="{raw_x0:.1f}" y="{y - 15}" width="{raw_w:.1f}" height="{row_h}" rx="7" class="raw"/>')
        lines.append(f'  <rect x="{res_x0:.1f}" y="{y + 5}" width="{res_w:.1f}" height="{row_h}" rx="7" class="adjusted"/>')

    lines.append("</svg>\n")
    (OUT / "raw-vs-residual-spearman.svg").write_text("\n".join(lines), encoding="utf-8")


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    candidates = {
        "regular": ["DejaVuSans.ttf"],
        "medium": ["DejaVuSans.ttf"],
        "semibold": ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"],
        "bold": ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"],
    }[weight]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_center(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, fnt: ImageFont.FreeTypeFont, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2), text, font=fnt, fill=fill)


def draw_left_center(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, fnt: ImageFont.FreeTypeFont, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0], xy[1] - (box[3] - box[1]) / 2), text, font=fnt, fill=fill)


def write_raw_vs_residual_png(metrics: pd.DataFrame) -> None:
    method_order = [
        "cv_ecfp_ridge",
        "cv_rdkit_descriptor_rf",
        "cv_rdkit_descriptor_ridge",
        "molecular_weight",
        "cv_mw_clogp_ridge",
        "clogp",
        "gnina_crystal",
        "boltz_2",
        "smina_crystal",
        "aev_plig",
        "aqaffinity",
    ]
    role = {
        "cv_ecfp_ridge": "control",
        "cv_rdkit_descriptor_rf": "control",
        "cv_rdkit_descriptor_ridge": "control",
        "molecular_weight": "property",
        "cv_mw_clogp_ridge": "property",
        "clogp": "property",
        "gnina_crystal": "published",
        "boltz_2": "published",
        "smina_crystal": "published",
        "aev_plig": "published",
        "aqaffinity": "published",
    }
    role_label = {
        "cv_ecfp_ridge": ("EV-A71 TRAINED", "LIGAND-ONLY"),
        "molecular_weight": ("SIMPLE PROPERTY", "BASELINES"),
        "gnina_crystal": ("PUBLISHED", "BENCHMARK SCORES"),
    }
    rows = metrics.set_index("method").loc[method_order].reset_index()
    scale = 1.6
    width, height = int(1120 * scale), int(650 * scale)
    image = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(image)

    def sc(v: float) -> int:
        return int(round(v * scale))

    def tx(v: float) -> int:
        return sc(sx(v, left=FIG1_PLOT_LEFT, right=FIG1_PLOT_RIGHT))

    def rect(
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        fill: str,
        outline: str | None = None,
        width_px: int = 1,
        radius: int = 7,
    ) -> None:
        draw.rounded_rectangle((sc(x0), sc(y0), sc(x1), sc(y1)), radius=sc(radius), fill=fill, outline=outline, width=width_px)

    def hatch_rect(x0: float, y0: float, x1: float, y1: float) -> None:
        px0, py0, px1, py1 = sc(x0), sc(y0), sc(x1), sc(y1)
        if px1 <= px0 or py1 <= py0:
            return
        hatch = Image.new("RGB", image.size, HATCH_FILL)
        hatch_draw = ImageDraw.Draw(hatch)
        mask = Image.new("L", image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((px0, py0, px1, py1), radius=sc(7), fill=255)
        step = max(3, sc(6))
        span = max(px1 - px0, py1 - py0) + step * 2
        for x in range(px0 - span, px1 + span, step):
            hatch_draw.line((x, py0 - step, x + span, py1 + step), fill=HATCH_STROKE, width=max(1, sc(1)))
            hatch_draw.line((x, py1 + step, x + span, py0 - step), fill=HATCH_STROKE, width=max(1, sc(1)))
        image.paste(hatch, (0, 0), mask)
        draw.rounded_rectangle((px0, py0, px1, py1), radius=sc(7), outline=HATCH_OUTLINE, width=max(1, sc(1)))

    title_font = font(sc(15), "bold")
    method_font = font(sc(12), "semibold")
    role_font = font(sc(10), "semibold")
    tick_font = font(sc(12), "regular")
    axis_font = font(sc(12), "semibold")

    draw_center(draw, (sc(560), sc(42)), "pKD correlation is not the residual signal", title_font, INK)
    rect(438, 74, 456, 88, BLUE, radius=4)
    draw.text((sc(464), sc(73)), "original pKD", font=role_font, fill=MUTED)
    hatch_rect(572, 74, 590, 88)
    draw.text((sc(598), sc(73)), "after MW+cLogP removal", font=role_font, fill=MUTED)

    for tick in [-0.1, 0.0, 0.1, 0.3, 0.5, 0.7]:
        x = tx(tick)
        if tick in {-0.1, 0.7}:
            draw_center(draw, (x, sc(584)), f"{tick:.1f}", tick_font, MUTED)
            continue
        color = MUTED if tick == 0 else GRID
        width_px = sc(1.35) if tick == 0 else sc(1)
        dash = sc(4)
        gap = sc(8)
        if tick == 0:
            draw.line((x, sc(86), x, sc(552)), fill=color, width=max(1, width_px))
        else:
            y = sc(86)
            while y < sc(556):
                draw.line((x, y, x, min(y + dash, sc(556))), fill=color, width=1)
                y += dash + gap
        draw_center(draw, (x, sc(584)), "0" if tick == 0 else f"{tick:.1f}", tick_font, MUTED)
    draw.line((sc(FIG1_PLOT_LEFT), sc(556), sc(FIG1_PLOT_RIGHT), sc(556)), fill=AXIS, width=sc(1))
    draw.line((sc(FIG1_GROUP_RULE_X), sc(112), sc(FIG1_GROUP_RULE_X), sc(552)), fill=GRID, width=1)
    draw_center(draw, (sc((FIG1_PLOT_LEFT + FIG1_PLOT_RIGHT) / 2), sc(620)), "Spearman correlation", axis_font, MUTED)

    zero = tx(0)
    y0, step, row_h = 126, 38, 14
    for idx, row in rows.iterrows():
        method = str(row["method"])
        raw = float(row["raw_spearman"])
        residual = float(row["residual_spearman"])
        y = y0 + idx * step
        if method in role_label:
            center = (FIG1_GROUP_TOP[method] + FIG1_GROUP_BOTTOM[method]) / 2
            first, second = role_label[method]
            draw.text((sc(FIG1_GROUP_LABEL_X), sc(center - 16)), first, font=role_font, fill=MUTED)
            draw.text((sc(FIG1_GROUP_LABEL_X), sc(center - 3)), second, font=role_font, fill=MUTED)
        if idx in [3, 6]:
            draw.line((sc(FIG1_GROUP_LABEL_X), sc(y - 18), sc(FIG1_PLOT_RIGHT), sc(y - 18)), fill=GRID, width=1)
        draw.text((sc(FIG1_LABEL_LEFT), sc(y - 7)), DISPLAY_METHOD.get(method, method), font=method_font, fill=INK)
        raw_end = tx(raw)
        res_end = tx(residual)
        rect(min(zero, raw_end) / scale, y - 15, max(zero, raw_end) / scale, y - 1, BLUE)
        hatch_rect(min(zero, res_end) / scale, y + 5, max(zero, res_end) / scale, y + 19)

    image.convert("RGB").save(OUT / "raw-vs-residual-spearman.png", quality=95)


def write_social_thumbnail_from_figure1() -> None:
    source = Image.open(OUT / "raw-vs-residual-spearman.png").convert("RGB")
    target_w, target_h = 1200, 627
    scale = min(target_w / source.width, target_h / source.height)
    resized = source.resize((int(round(source.width * scale)), int(round(source.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h), "white")
    left = (target_w - resized.width) // 2
    top = (target_h - resized.height) // 2
    canvas.paste(resized, (left, top))
    canvas.save(OUT / "social-thumbnail.png", quality=95)


def write_pkd_vs_mw_svg(df: pd.DataFrame) -> None:
    width, height = 1120, 650
    plot_left, plot_right = 118, 1040
    plot_top, plot_bottom = 100, 544
    x_min, x_max = 180, 510
    y_min, y_max = 3.2, 8.1

    def px(value: float) -> float:
        return plot_left + (value - x_min) / (x_max - x_min) * (plot_right - plot_left)

    def py(value: float) -> float:
        return plot_bottom - (value - y_min) / (y_max - y_min) * (plot_bottom - plot_top)

    x = df["mw_rdkit"].to_numpy()
    y = df["experimental_pKD"].to_numpy()
    coef = np.polyfit(x, y, deg=1)
    trend_x = np.array([x_min, x_max])
    trend_y = coef[0] * trend_x + coef[1]

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '  <title id="title">Molecular weight and raw pKD relationship</title>',
        '  <desc id="desc">Scatter plot showing the positive relationship between RDKit molecular weight and experimental pKD in the OpenBind EV-A71 2A compound-level table.</desc>',
        f'  <rect width="{width}" height="{height}" fill="#ffffff"/>',
        "  <defs>",
        "    <style>",
        "      text { font-family: 'Plus Jakarta Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }",
        "      .title { fill: #111111; font-size: 15px; font-weight: 700; }",
        "      .tick { fill: #5f6672; font-size: 12px; font-weight: 500; }",
        "      .axis-label { fill: #5f6672; font-size: 12.5px; font-weight: 600; }",
        "      .grid { stroke: #e6e8ee; stroke-width: 1; stroke-dasharray: 4 8; }",
        "      .axis { stroke: #cfd4dd; stroke-width: 1.2; }",
        "      .trend { stroke: #4a4f59; stroke-width: 2.0; }",
        "      .point { fill: #3f41ff; opacity: 0.46; stroke: #ffffff; stroke-width: 0.6; }",
        "    </style>",
        "  </defs>",
        '  <text x="560" y="42" text-anchor="middle" class="title">Molecular weight already tracks raw pKD</text>',
    ]
    for tick in [200, 250, 300, 350, 400, 450, 500]:
        x_pos = px(tick)
        lines.append(f'  <line x1="{x_pos:.1f}" y1="{plot_top}" x2="{x_pos:.1f}" y2="{plot_bottom}" class="grid"/>')
        lines.append(f'  <text x="{x_pos:.1f}" y="578" text-anchor="middle" class="tick">{tick}</text>')
    for tick in [4, 5, 6, 7, 8]:
        y_pos = py(tick)
        lines.append(f'  <line x1="{plot_left}" y1="{y_pos:.1f}" x2="{plot_right}" y2="{y_pos:.1f}" class="grid"/>')
        lines.append(f'  <text x="92" y="{y_pos + 4:.1f}" text-anchor="middle" class="tick">{tick}</text>')
    lines.append(f'  <line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" class="axis"/>')
    lines.append(f'  <line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_bottom}" class="axis"/>')
    lines.append(f'  <text x="{(plot_left + plot_right) / 2:.1f}" y="620" text-anchor="middle" class="axis-label">RDKit molecular weight</text>')
    lines.append('  <text x="30" y="330" text-anchor="middle" transform="rotate(-90 30 330)" class="axis-label">Experimental pKD</text>')
    lines.append(f'  <line x1="{px(trend_x[0]):.1f}" y1="{py(trend_y[0]):.1f}" x2="{px(trend_x[1]):.1f}" y2="{py(trend_y[1]):.1f}" class="trend"/>')
    for mw, pkd in zip(x, y):
        lines.append(f'  <circle cx="{px(float(mw)):.1f}" cy="{py(float(pkd)):.1f}" r="2.8" class="point"/>')
    lines.append("</svg>\n")
    (OUT / "pkd-vs-mw.svg").write_text("\n".join(lines), encoding="utf-8")


def write_pkd_vs_mw_png(df: pd.DataFrame) -> None:
    scale = 1.6
    width, height = int(1120 * scale), int(650 * scale)
    plot_left, plot_right = 118, 1040
    plot_top, plot_bottom = 100, 544
    x_min, x_max = 180, 510
    y_min, y_max = 3.2, 8.1
    image = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(image)

    def sc(v: float) -> int:
        return int(round(v * scale))

    def px(value: float) -> int:
        return sc(plot_left + (value - x_min) / (x_max - x_min) * (plot_right - plot_left))

    def py(value: float) -> int:
        return sc(plot_bottom - (value - y_min) / (y_max - y_min) * (plot_bottom - plot_top))

    title_font = font(sc(15), "bold")
    tick_font = font(sc(12), "regular")
    axis_font = font(sc(12), "semibold")

    draw_center(draw, (sc(560), sc(42)), "Molecular weight already tracks raw pKD", title_font, INK)
    for tick in [200, 250, 300, 350, 400, 450, 500]:
        x_pos = px(tick)
        y_pos = sc(plot_top)
        while y_pos < sc(plot_bottom):
            draw.line((x_pos, y_pos, x_pos, min(y_pos + sc(4), sc(plot_bottom))), fill=GRID, width=1)
            y_pos += sc(12)
        draw_center(draw, (x_pos, sc(578)), str(tick), tick_font, MUTED)
    for tick in [4, 5, 6, 7, 8]:
        y_pos = py(tick)
        x_pos = sc(plot_left)
        while x_pos < sc(plot_right):
            draw.line((x_pos, y_pos, min(x_pos + sc(4), sc(plot_right)), y_pos), fill=GRID, width=1)
            x_pos += sc(12)
        draw_center(draw, (sc(92), y_pos), str(tick), tick_font, MUTED)
    draw.line((sc(plot_left), sc(plot_bottom), sc(plot_right), sc(plot_bottom)), fill=AXIS, width=sc(1))
    draw.line((sc(plot_left), sc(plot_top), sc(plot_left), sc(plot_bottom)), fill=AXIS, width=sc(1))
    draw_center(draw, (sc((plot_left + plot_right) / 2), sc(620)), "RDKit molecular weight", axis_font, MUTED)
    label = "Experimental pKD"
    label_box = draw.textbbox((0, 0), label, font=axis_font)
    label_w = label_box[2] - label_box[0]
    label_h = label_box[3] - label_box[1]
    label_layer = Image.new("RGBA", (label_w + sc(8), label_h + sc(8)), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label_layer)
    label_draw.text((sc(4), sc(4)), label, font=axis_font, fill=MUTED)
    rotated = label_layer.rotate(90, expand=True)
    image.alpha_composite(rotated, (sc(30) - rotated.width // 2, sc(330) - rotated.height // 2))

    x = df["mw_rdkit"].to_numpy()
    y = df["experimental_pKD"].to_numpy()
    coef = np.polyfit(x, y, deg=1)
    trend_x = np.array([x_min, x_max])
    trend_y = coef[0] * trend_x + coef[1]
    draw.line((px(float(trend_x[0])), py(float(trend_y[0])), px(float(trend_x[1])), py(float(trend_y[1]))), fill="#4a4f59", width=sc(2))
    r = sc(2.8)
    for mw, pkd in zip(x, y):
        cx, cy = px(float(mw)), py(float(pkd))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(63, 65, 255, 118), outline=(255, 255, 255, 220), width=max(1, sc(0.6)))
    image.convert("RGB").save(OUT / "pkd-vs-mw.png", quality=95)


def write_grouped_residual_svg(grouped: pd.DataFrame) -> None:
    method_order = [
        "cv_ecfp_ridge",
        "cv_rdkit_descriptor_rf",
        "cv_rdkit_descriptor_ridge",
        "molecular_weight",
        "cv_mw_clogp_ridge",
        "clogp",
        "gnina_crystal",
        "boltz_2",
        "smina_crystal",
        "aev_plig",
        "aqaffinity",
    ]
    role = {
        "cv_ecfp_ridge": "control",
        "cv_rdkit_descriptor_rf": "control",
        "cv_rdkit_descriptor_ridge": "control",
        "molecular_weight": "property",
        "cv_mw_clogp_ridge": "property",
        "clogp": "property",
        "gnina_crystal": "published",
        "boltz_2": "published",
        "smina_crystal": "published",
        "aev_plig": "published",
        "aqaffinity": "published",
    }
    role_label = {
        "cv_ecfp_ridge": ("EV-A71 TRAINED", "LIGAND-ONLY"),
        "molecular_weight": ("SIMPLE PROPERTY", "BASELINES"),
        "gnina_crystal": ("PUBLISHED", "BENCHMARK SCORES"),
    }
    rows = grouped[grouped["group_col"].eq("butina_tanimoto_0p6_cluster")].set_index("method").loc[method_order].reset_index()
    width, height = 1120, 650
    group_label_x, group_rule_x = 48, 174
    label_left = 196
    plot_left, plot_right = 356, 1010
    x_min, x_max = -0.2, 0.52
    y0, step, bar_h = 126, 38, 12

    def gx(value: float) -> float:
        return plot_left + (value - x_min) / (x_max - x_min) * (plot_right - plot_left)

    def clamp(value: float) -> float:
        return min(max(value, x_min), x_max)

    group_top = {"cv_ecfp_ridge": 112, "molecular_weight": 226, "gnina_crystal": 340}
    group_bottom = {"cv_ecfp_ridge": 226, "molecular_weight": 340, "gnina_crystal": 552}
    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '  <title id="title">Grouped residual Spearman sensitivity</title>',
        '  <desc id="desc">Horizontal bar chart showing Butina Tanimoto 0.6 grouped residual Spearman means with bootstrap 95 percent intervals.</desc>',
        f'  <rect width="{width}" height="{height}" fill="#ffffff"/>',
        "  <defs>",
        '    <pattern id="control-stripe" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">',
        f'      <rect width="8" height="8" fill="{BLUE}"/>',
        '      <line x1="0" y1="0" x2="0" y2="8" stroke="#ffffff" stroke-width="2.2" opacity="0.45"/>',
        "    </pattern>",
        "    <style>",
        "      text { font-family: 'Plus Jakarta Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }",
        "      .title { fill: #111111; font-size: 15px; font-weight: 700; }",
        "      .method { fill: #111111; font-size: 12.5px; font-weight: 650; }",
        "      .role { fill: #5f6672; font-size: 9.6px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }",
        "      .tick { fill: #5f6672; font-size: 12px; font-weight: 500; }",
        "      .axis-label { fill: #5f6672; font-size: 12.5px; font-weight: 600; }",
        "      .grid { stroke: #e6e8ee; stroke-width: 1; stroke-dasharray: 4 8; }",
        "      .axis { stroke: #cfd4dd; stroke-width: 1.2; }",
        "      .zero { stroke: #5f6672; stroke-width: 1.35; }",
        "      .ci { stroke: #5f6672; stroke-width: 1.15; }",
        "      .bar-control { fill: url(#control-stripe); }",
        "      .bar-property { fill: #b9c0cc; }",
        "      .bar-published { fill: #7f8796; }",
        "      .divider { stroke: #e6e8ee; stroke-width: 1; }",
        "    </style>",
        "  </defs>",
        '  <text x="560" y="42" text-anchor="middle" class="title">Grouped sensitivity preserves the residual gap</text>',
    ]
    for tick in [-0.2, -0.1, 0.0, 0.1, 0.3, 0.5]:
        x = gx(tick)
        if tick != -0.2:
            cls = "zero" if tick == 0 else "grid"
            lines.append(f'  <line x1="{x:.1f}" y1="98" x2="{x:.1f}" y2="556" class="{cls}"/>')
        label = "0" if tick == 0 else f"{tick:.1f}"
        lines.append(f'  <text x="{x:.1f}" y="584" text-anchor="middle" class="tick">{label}</text>')
    lines.append(f'  <line x1="{plot_left}" y1="556" x2="{plot_right}" y2="556" class="axis"/>')
    lines.append(f'  <line x1="{group_rule_x}" y1="112" x2="{group_rule_x}" y2="552" class="divider"/>')
    lines.append(f'  <text x="{(plot_left + plot_right) / 2:.1f}" y="620" text-anchor="middle" class="axis-label">Grouped residual Spearman mean</text>')
    zero = gx(0)
    for idx, row in rows.iterrows():
        method = str(row["method"])
        y = y0 + idx * step
        if method in role_label:
            center = (group_top[method] + group_bottom[method]) / 2
            first, second = role_label[method]
            lines.append(f'  <text x="{group_label_x}" y="{center - 6:.1f}" class="role">{escape(first)}</text>')
            lines.append(f'  <text x="{group_label_x}" y="{center + 7:.1f}" class="role">{escape(second)}</text>')
        if idx in [3, 6]:
            lines.append(f'  <line x1="{group_label_x}" y1="{y - 18}" x2="{plot_right}" y2="{y - 18}" class="divider"/>')
        lines.append(f'  <text x="{label_left}" y="{y + 4}" class="method">{escape(DISPLAY_METHOD.get(method, method))}</text>')
        mean = float(row["mean_residual_spearman"])
        ci_low = float(row["ci_low"])
        ci_high = float(row["ci_high"])
        bar_x0 = min(zero, gx(mean))
        bar_w = abs(gx(mean) - zero)
        cls = {"control": "bar-control", "property": "bar-property", "published": "bar-published"}[role[method]]
        ci_low_x = gx(clamp(ci_low))
        ci_high_x = gx(clamp(ci_high))
        lines.append(f'  <line x1="{ci_low_x:.1f}" y1="{y + 2}" x2="{ci_high_x:.1f}" y2="{y + 2}" class="ci"/>')
        lines.append(f'  <line x1="{ci_low_x:.1f}" y1="{y - 4}" x2="{ci_low_x:.1f}" y2="{y + 8}" class="ci"/>')
        lines.append(f'  <line x1="{ci_high_x:.1f}" y1="{y - 4}" x2="{ci_high_x:.1f}" y2="{y + 8}" class="ci"/>')
        lines.append(f'  <rect x="{bar_x0:.1f}" y="{y - 4}" width="{bar_w:.1f}" height="{bar_h}" rx="4" class="{cls}"/>')
    lines.append("</svg>\n")
    (OUT / "butina-grouped-residual-spearman.svg").write_text("\n".join(lines), encoding="utf-8")


def write_grouped_residual_png(grouped: pd.DataFrame) -> None:
    method_order = [
        "cv_ecfp_ridge",
        "cv_rdkit_descriptor_rf",
        "cv_rdkit_descriptor_ridge",
        "molecular_weight",
        "cv_mw_clogp_ridge",
        "clogp",
        "gnina_crystal",
        "boltz_2",
        "smina_crystal",
        "aev_plig",
        "aqaffinity",
    ]
    role = {
        "cv_ecfp_ridge": "control",
        "cv_rdkit_descriptor_rf": "control",
        "cv_rdkit_descriptor_ridge": "control",
        "molecular_weight": "property",
        "cv_mw_clogp_ridge": "property",
        "clogp": "property",
        "gnina_crystal": "published",
        "boltz_2": "published",
        "smina_crystal": "published",
        "aev_plig": "published",
        "aqaffinity": "published",
    }
    role_label = {
        "cv_ecfp_ridge": ("EV-A71 TRAINED", "LIGAND-ONLY"),
        "molecular_weight": ("SIMPLE PROPERTY", "BASELINES"),
        "gnina_crystal": ("PUBLISHED", "BENCHMARK SCORES"),
    }
    rows = grouped[grouped["group_col"].eq("butina_tanimoto_0p6_cluster")].set_index("method").loc[method_order].reset_index()
    scale = 1.6
    width, height = int(1120 * scale), int(650 * scale)
    image = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(image)
    group_label_x, group_rule_x = 48, 174
    label_left = 196
    plot_left, plot_right = 356, 1010
    x_min, x_max = -0.2, 0.52

    def sc(v: float) -> int:
        return int(round(v * scale))

    def gx(value: float) -> int:
        return sc(plot_left + (value - x_min) / (x_max - x_min) * (plot_right - plot_left))

    def clamp(value: float) -> float:
        return min(max(value, x_min), x_max)

    title_font = font(sc(15), "bold")
    role_font = font(sc(10), "semibold")
    method_font = font(sc(12), "semibold")
    tick_font = font(sc(12), "regular")
    axis_font = font(sc(12), "semibold")

    draw_center(draw, (sc(560), sc(42)), "Grouped sensitivity preserves the residual gap", title_font, INK)
    for tick in [-0.2, -0.1, 0.0, 0.1, 0.3, 0.5]:
        x = gx(tick)
        if tick != -0.2:
            color = MUTED if tick == 0 else GRID
            width_px = sc(1.35) if tick == 0 else 1
            if tick == 0:
                draw.line((x, sc(98), x, sc(556)), fill=color, width=width_px)
            else:
                y = sc(98)
                while y < sc(556):
                    draw.line((x, y, x, min(y + sc(4), sc(556))), fill=color, width=width_px)
                    y += sc(12)
        draw_center(draw, (x, sc(584)), "0" if tick == 0 else f"{tick:.1f}", tick_font, MUTED)
    draw.line((sc(plot_left), sc(556), sc(plot_right), sc(556)), fill=AXIS, width=sc(1))
    draw.line((sc(group_rule_x), sc(112), sc(group_rule_x), sc(552)), fill=GRID, width=1)
    draw_center(draw, (sc((plot_left + plot_right) / 2), sc(620)), "Grouped residual Spearman mean", axis_font, MUTED)

    group_top = {"cv_ecfp_ridge": 112, "molecular_weight": 226, "gnina_crystal": 340}
    group_bottom = {"cv_ecfp_ridge": 226, "molecular_weight": 340, "gnina_crystal": 552}
    zero = gx(0)
    y0, step, bar_h = 126, 38, 12
    for idx, row in rows.iterrows():
        method = str(row["method"])
        y = y0 + idx * step
        if method in role_label:
            center = (group_top[method] + group_bottom[method]) / 2
            first, second = role_label[method]
            draw.text((sc(group_label_x), sc(center - 16)), first, font=role_font, fill=MUTED)
            draw.text((sc(group_label_x), sc(center - 3)), second, font=role_font, fill=MUTED)
        if idx in [3, 6]:
            draw.line((sc(group_label_x), sc(y - 18), sc(plot_right), sc(y - 18)), fill=GRID, width=1)
        draw.text((sc(label_left), sc(y - 7)), DISPLAY_METHOD.get(method, method), font=method_font, fill=INK)
        mean = float(row["mean_residual_spearman"])
        ci_low = float(row["ci_low"])
        ci_high = float(row["ci_high"])
        ci_low_x = gx(clamp(ci_low))
        ci_high_x = gx(clamp(ci_high))
        draw.line((ci_low_x, sc(y + 2), ci_high_x, sc(y + 2)), fill=MUTED, width=sc(1))
        draw.line((ci_low_x, sc(y - 4), ci_low_x, sc(y + 8)), fill=MUTED, width=sc(1))
        draw.line((ci_high_x, sc(y - 4), ci_high_x, sc(y + 8)), fill=MUTED, width=sc(1))
        x0, x1 = min(zero, gx(mean)), max(zero, gx(mean))
        fill = {"control": BLUE, "property": "#b9c0cc", "published": DARK_GRAY}[role[method]]
        draw.rounded_rectangle((x0, sc(y - 4), x1, sc(y + bar_h - 4)), radius=sc(4), fill=fill)
        if role[method] == "control":
            for x in range(x0 - sc(20), x1 + sc(20), sc(8)):
                draw.line((x, sc(y + bar_h - 4), x + sc(20), sc(y - 4)), fill=(255, 255, 255, 90), width=sc(2))
    image.convert("RGB").save(OUT / "butina-grouped-residual-spearman.png", quality=95)


def raw_vs_residual() -> None:
    metrics = pd.read_csv(R002 / "method_metrics.csv")
    metrics = metrics.sort_values("raw_spearman", ascending=True).copy()
    methods = metrics["method"].tolist()
    y = np.arange(len(methods))

    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    raw = ax.barh(y + 0.18, metrics["raw_spearman"], height=0.30, color=LIGHT_BLUE, edgecolor=BLUE, linewidth=1.0, label="pKD Spearman")
    residual_colors = [BLUE if m not in PUBLISHED else DARK_GRAY for m in methods]
    residual = ax.barh(y - 0.18, metrics["residual_spearman"], height=0.30, color=residual_colors, label="MW+cLogP residual")
    for bar, method in zip(residual, methods):
        if method not in PUBLISHED:
            bar.set_hatch("////")
            bar.set_edgecolor(BLUE)
            bar.set_linewidth(1.0)

    ax.axvline(0, color=AXIS, linewidth=1)
    ax.set_xlim(-0.12, 0.74)
    ax.set_yticks(y)
    ax.set_yticklabels([DISPLAY_METHOD.get(m, m) for m in methods], color=INK, fontsize=10.2)
    ax.set_xlabel("Spearman correlation", fontweight="semibold")
    title_block(
        fig,
        "Raw affinity ranking separates from MW+cLogP residual signal",
        "",
    )
    style_axis(ax)
    label_bars(ax, residual)
    ax.legend(
        loc="lower right",
        frameon=False,
        fontsize=10.5,
        labelcolor=MUTED,
        handlelength=1.4,
        borderaxespad=0.8,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    save(fig, "raw-vs-residual-spearman")
    write_raw_vs_residual_svg(metrics)
    write_raw_vs_residual_png(metrics)
    write_social_thumbnail_from_figure1()


def pkd_vs_mw() -> None:
    df = pd.read_csv(R002 / "openbind_clean_compound_table_with_residuals.csv")
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    ax.scatter(
        df["mw_rdkit"],
        df["experimental_pKD"],
        s=22,
        facecolor=BLUE,
        edgecolor="white",
        linewidth=0.45,
        alpha=0.62,
    )
    x = df["mw_rdkit"].to_numpy()
    y = df["experimental_pKD"].to_numpy()
    coef = np.polyfit(x, y, deg=1)
    xs = np.linspace(x.min(), x.max(), 200)
    ax.plot(xs, coef[0] * xs + coef[1], color=INK, linewidth=1.8, alpha=0.8)
    ax.text(
        0.04,
        0.93,
        "MW alone Spearman = 0.484",
        transform=ax.transAxes,
        color=INK,
        fontsize=11.5,
        fontweight="bold",
        bbox={"boxstyle": "round,pad=0.35,rounding_size=0.12", "facecolor": "white", "edgecolor": AXIS, "linewidth": 1},
    )
    ax.set_xlabel("RDKit molecular weight", fontweight="semibold")
    ax.set_ylabel("Experimental pKD", fontweight="semibold")
    title_block(
        fig,
        "Molecular weight already tracks raw pKD",
        "",
    )
    style_axis(ax, xgrid=True, ygrid=True)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    save(fig, "pkd-vs-mw")
    write_pkd_vs_mw_svg(df)
    write_pkd_vs_mw_png(df)


def grouped_residual() -> None:
    grouped = pd.read_csv(R003 / "grouped_intervals.csv")
    top = grouped[grouped["group_col"].eq("butina_tanimoto_0p6_cluster")].sort_values("mean_residual_spearman", ascending=True)
    methods = top["method"].tolist()
    y = np.arange(len(methods))
    colors = [BLUE if m not in PUBLISHED else DARK_GRAY for m in methods]
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    xerr = np.vstack([top["mean_residual_spearman"] - top["ci_low"], top["ci_high"] - top["mean_residual_spearman"]])
    bars = ax.barh(y, top["mean_residual_spearman"], height=0.44, color=colors)
    for bar, method in zip(bars, methods):
        if method not in PUBLISHED:
            bar.set_hatch("////")
            bar.set_edgecolor(BLUE)
            bar.set_linewidth(1.0)
    ax.errorbar(
        top["mean_residual_spearman"],
        y,
        xerr=xerr,
        fmt="none",
        ecolor=INK,
        elinewidth=1.0,
        capsize=3,
        alpha=0.72,
    )
    ax.axvline(0, color=AXIS, linewidth=1)
    ax.set_xlim(-0.20, 0.56)
    ax.set_yticks(y)
    ax.set_yticklabels([DISPLAY_METHOD.get(m, m) for m in methods], color=INK, fontsize=10.2)
    ax.set_xlabel("Grouped residual Spearman mean", fontweight="semibold")
    title_block(
        fig,
        "Grouped sensitivity preserves the residual gap",
        "",
    )
    style_axis(ax)
    label_bars(ax, bars)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    save(fig, "butina-grouped-residual-spearman")
    write_grouped_residual_svg(grouped)
    write_grouped_residual_png(grouped)


def main() -> None:
    setup()
    raw_vs_residual()
    pkd_vs_mw()
    grouped_residual()


if __name__ == "__main__":
    main()
