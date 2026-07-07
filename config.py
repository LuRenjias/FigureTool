"""Validated TOML configuration for FigureTool."""

from __future__ import annotations

import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

FigureSize = tuple[float, float]
ColorMapSpec = str | tuple[str, ...]


def _section(data: Mapping[str, object], name: str) -> Mapping[str, object]:
    value = data.get(name)
    if not isinstance(value, Mapping):
        raise ValueError(f"Missing plotting configuration section: {name}")
    return value


def _number(
    section: Mapping[str, object],
    name: str,
    section_name: str,
    *,
    positive: bool = True,
) -> float:
    value = section.get(name)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{section_name}.{name} must be a number.")
    result = float(value)
    if not math.isfinite(result) or (positive and result <= 0):
        condition = "positive and finite" if positive else "finite"
        raise ValueError(f"{section_name}.{name} must be {condition}.")
    return result


def _integer(
    section: Mapping[str, object], name: str, section_name: str
) -> int:
    value = _number(section, name, section_name)
    if not value.is_integer():
        raise ValueError(f"{section_name}.{name} must be an integer.")
    return int(value)


def _figsize(
    section: Mapping[str, object], name: str, section_name: str
) -> FigureSize:
    value = section.get(name)
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{section_name}.{name} must contain [width, height].")
    temporary = {"width": value[0], "height": value[1]}
    return (
        _number(temporary, "width", f"{section_name}.{name}"),
        _number(temporary, "height", f"{section_name}.{name}"),
    )


def _text(section: Mapping[str, object], name: str, section_name: str) -> str:
    value = section.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{section_name}.{name} must be a non-empty string.")
    return value


def _boolean(
    section: Mapping[str, object],
    name: str,
    section_name: str,
    *,
    default: bool,
) -> bool:
    value = section.get(name, default)
    if not isinstance(value, bool):
        raise ValueError(f"{section_name}.{name} must be true or false.")
    return value


def _choice(
    section: Mapping[str, object],
    name: str,
    section_name: str,
    choices: set[str],
) -> str:
    value = _text(section, name, section_name)
    if value not in choices:
        expected = ", ".join(sorted(choices))
        raise ValueError(f"{section_name}.{name} must be one of: {expected}.")
    return value


def _colormap(
    section: Mapping[str, object], name: str, section_name: str
) -> ColorMapSpec:
    value = section.get(name)
    if isinstance(value, str) and value.strip():
        return value
    if (
        isinstance(value, list)
        and len(value) >= 2
        and all(isinstance(color, str) and color.strip() for color in value)
    ):
        return tuple(value)
    raise ValueError(
        f"{section_name}.{name} must be a colormap name or a list of colors."
    )


@dataclass(frozen=True)
class AttentionConfig:
    figsize: FigureSize
    colormap: ColorMapSpec
    xlabel_fontsize: float
    ylabel_fontsize: float
    title_fontsize: float
    xtick_labelsize: float
    ytick_labelsize: float
    show_xticks: bool
    show_yticks: bool
    xtick_rotation: float
    annotation_fontsize: float
    rectangle_edgecolor: str
    rectangle_linewidth: float
    show_axis_labels: bool
    colorbar_label: str
    show_colorbar_label: bool
    colorbar_figsize: FigureSize
    colorbar_fraction: float
    colorbar_pad: float
    colorbar_tick_labelsize: float
    colorbar_label_fontsize: float

    @classmethod
    def from_mapping(cls, section: Mapping[str, object]) -> "AttentionConfig":
        name = "attention"
        return cls(
            figsize=_figsize(section, "figsize", name),
            colormap=_colormap(section, "colormap", name),
            xlabel_fontsize=_number(section, "xlabel_fontsize", name),
            ylabel_fontsize=_number(section, "ylabel_fontsize", name),
            title_fontsize=_number(section, "title_fontsize", name),
            xtick_labelsize=_number(section, "xtick_labelsize", name),
            ytick_labelsize=_number(section, "ytick_labelsize", name),
            show_xticks=_boolean(section, "show_xticks", name, default=True),
            show_yticks=_boolean(section, "show_yticks", name, default=True),
            xtick_rotation=_number(
                section, "xtick_rotation", name, positive=False
            ),
            annotation_fontsize=_number(section, "annotation_fontsize", name),
            rectangle_edgecolor=_text(section, "rectangle_edgecolor", name),
            rectangle_linewidth=_number(
                section, "rectangle_linewidth", name
            ),
            show_axis_labels=_boolean(
                section, "show_axis_labels", name, default=True
            ),
            colorbar_label=_text(section, "colorbar_label", name),
            show_colorbar_label=_boolean(
                section, "show_colorbar_label", name, default=True
            ),
            colorbar_figsize=_figsize(section, "colorbar_figsize", name),
            colorbar_fraction=_number(section, "colorbar_fraction", name),
            colorbar_pad=_number(section, "colorbar_pad", name),
            colorbar_tick_labelsize=_number(
                section, "colorbar_tick_labelsize", name
            ),
            colorbar_label_fontsize=_number(
                section, "colorbar_label_fontsize", name
            ),
        )


@dataclass(frozen=True)
class TimeSeriesConfig:
    figsize: FigureSize
    xlabel_fontsize: float
    ylabel_fontsize: float
    title_fontsize: float
    xtick_labelsize: float
    ytick_labelsize: float
    show_xticks: bool
    show_yticks: bool
    show_axis_arrows: bool
    axis_arrow_linewidth: float
    axis_arrow_mutation_scale: float
    line_width: float
    missing_mode: str
    show_axis_labels: bool
    grid: bool
    colormap: str
    legend_figsize: FigureSize
    legend_fontsize: float
    legend_columns: int

    @classmethod
    def from_mapping(cls, section: Mapping[str, object]) -> "TimeSeriesConfig":
        name = "time_series"
        return cls(
            figsize=_figsize(section, "figsize", name),
            xlabel_fontsize=_number(section, "xlabel_fontsize", name),
            ylabel_fontsize=_number(section, "ylabel_fontsize", name),
            title_fontsize=_number(section, "title_fontsize", name),
            xtick_labelsize=_number(section, "xtick_labelsize", name),
            ytick_labelsize=_number(section, "ytick_labelsize", name),
            show_xticks=_boolean(section, "show_xticks", name, default=True),
            show_yticks=_boolean(section, "show_yticks", name, default=True),
            show_axis_arrows=_boolean(
                section, "show_axis_arrows", name, default=True
            ),
            axis_arrow_linewidth=_number(
                section, "axis_arrow_linewidth", name
            ),
            axis_arrow_mutation_scale=_number(
                section, "axis_arrow_mutation_scale", name
            ),
            line_width=_number(section, "line_width", name),
            missing_mode=_choice(
                section, "missing_mode", name, {"blank", "dashed"}
            ),
            show_axis_labels=_boolean(
                section, "show_axis_labels", name, default=True
            ),
            grid=_boolean(section, "grid", name, default=True),
            colormap=_text(section, "colormap", name),
            legend_figsize=_figsize(section, "legend_figsize", name),
            legend_fontsize=_number(section, "legend_fontsize", name),
            legend_columns=_integer(section, "legend_columns", name),
        )


@dataclass(frozen=True)
class FigureToolConfig:
    attention: AttentionConfig
    time_series: TimeSeriesConfig
    dpi: int

    @classmethod
    def load(cls, path: str | Path) -> "FigureToolConfig":
        path = Path(path)
        with path.open("rb") as file:
            data = tomllib.load(file)
        output = _section(data, "output")
        dpi = _number(output, "dpi", "output")
        if not dpi.is_integer():
            raise ValueError("output.dpi must be an integer.")
        return cls(
            attention=AttentionConfig.from_mapping(_section(data, "attention")),
            time_series=TimeSeriesConfig.from_mapping(
                _section(data, "time_series")
            ),
            dpi=int(dpi),
        )

    @classmethod
    def default(cls) -> "FigureToolConfig":
        return cls.load(Path(__file__).with_name("plot_config.toml"))
