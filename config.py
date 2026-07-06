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
    xtick_labelsize: float
    ytick_labelsize: float
    xtick_rotation: float
    annotation_fontsize: float
    rectangle_edgecolor: str
    rectangle_linewidth: float
    show_axis_labels: bool
    colorbar_label: str

    @classmethod
    def from_mapping(cls, section: Mapping[str, object]) -> "AttentionConfig":
        name = "attention"
        return cls(
            figsize=_figsize(section, "figsize", name),
            colormap=_colormap(section, "colormap", name),
            xlabel_fontsize=_number(section, "xlabel_fontsize", name),
            ylabel_fontsize=_number(section, "ylabel_fontsize", name),
            xtick_labelsize=_number(section, "xtick_labelsize", name),
            ytick_labelsize=_number(section, "ytick_labelsize", name),
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
        )


@dataclass(frozen=True)
class TimeSeriesConfig:
    figsize: FigureSize
    xlabel_fontsize: float
    ylabel_fontsize: float
    xtick_labelsize: float
    ytick_labelsize: float
    line_width: float
    show_axis_labels: bool
    grid: bool
    colormap: str

    @classmethod
    def from_mapping(cls, section: Mapping[str, object]) -> "TimeSeriesConfig":
        name = "time_series"
        return cls(
            figsize=_figsize(section, "figsize", name),
            xlabel_fontsize=_number(section, "xlabel_fontsize", name),
            ylabel_fontsize=_number(section, "ylabel_fontsize", name),
            xtick_labelsize=_number(section, "xtick_labelsize", name),
            ytick_labelsize=_number(section, "ytick_labelsize", name),
            line_width=_number(section, "line_width", name),
            show_axis_labels=_boolean(
                section, "show_axis_labels", name, default=True
            ),
            grid=_boolean(section, "grid", name, default=True),
            colormap=_text(section, "colormap", name),
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
