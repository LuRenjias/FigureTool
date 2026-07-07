"""Generic single-attention and single-time-series plotters."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from .config import FigureToolConfig
from .style import FigureSaver, PlotStyle, finite_array

Region = tuple[int, int, int, int]


class AttentionHeatmapPlotter:
    """Draw one two-dimensional attention matrix."""

    def __init__(self, config: FigureToolConfig | None = None) -> None:
        self.config = config or FigureToolConfig.default()

    def plot(
        self,
        matrix: object,
        output_path: str | Path,
        *,
        row_labels: Sequence[str] | None = None,
        column_labels: Sequence[str] | None = None,
        title: str | None = None,
        vmin: float | None = None,
        vmax: float | None = None,
        annotate: bool = False,
        annotation_regions: Sequence[Region] | None = None,
        rectangle_regions: Sequence[Region] = (),
        show_colorbar: bool = True,
    ) -> Path:
        values = finite_array(matrix, "matrix")
        if values.ndim != 2:
            raise ValueError("matrix must be two-dimensional.")
        rows, columns = values.shape
        row_labels = self._labels(row_labels, rows, "row_labels")
        column_labels = self._labels(
            column_labels, columns, "column_labels"
        )
        lower = float(values.min()) if vmin is None else float(vmin)
        upper = float(values.max()) if vmax is None else float(vmax)
        if not np.isfinite([lower, upper]).all() or lower >= upper:
            raise ValueError("vmin and vmax must be finite and vmin < vmax.")

        PlotStyle.configure()
        settings = self.config.attention
        color_map = PlotStyle.resolve_colormap(
            settings.colormap, "figure_tool_attention"
        )
        normalization = mpl.colors.Normalize(vmin=lower, vmax=upper)
        figure, axis = plt.subplots(
            figsize=settings.figsize, constrained_layout=True
        )
        image = axis.imshow(
            values,
            cmap=color_map,
            norm=normalization,
            interpolation="nearest",
            aspect="equal",
        )
        axis.set_xticks(range(columns), column_labels)
        axis.set_yticks(range(rows), row_labels)
        plt.setp(
            axis.get_xticklabels(),
            rotation=settings.xtick_rotation,
            ha="right",
            rotation_mode="anchor",
        )
        axis.tick_params(
            axis="x",
            length=0,
            labelsize=settings.xtick_labelsize,
            bottom=settings.show_xticks,
            labelbottom=settings.show_xticks,
        )
        axis.tick_params(
            axis="y",
            length=0,
            labelsize=settings.ytick_labelsize,
            left=settings.show_yticks,
            labelleft=settings.show_yticks,
        )
        if settings.show_axis_labels:
            axis.set_xlabel("Key", fontsize=settings.xlabel_fontsize)
            axis.set_ylabel("Query", fontsize=settings.ylabel_fontsize)
        if title:
            axis.set_title(title, fontsize=settings.title_fontsize)
        for spine in axis.spines.values():
            spine.set_visible(False)

        self._validate_regions(rectangle_regions, rows, columns)
        for top, left, bottom, right in rectangle_regions:
            axis.add_patch(
                Rectangle(
                    (left - 0.5, top - 0.5),
                    right - left + 1,
                    bottom - top + 1,
                    fill=False,
                    edgecolor=settings.rectangle_edgecolor,
                    linewidth=settings.rectangle_linewidth,
                    clip_on=False,
                )
            )

        regions = list(annotation_regions or ())
        if annotate and not regions:
            regions = [(0, 0, rows - 1, columns - 1)]
        self._validate_regions(regions, rows, columns)
        for row in range(rows):
            for column in range(columns):
                if not any(
                    top <= row <= bottom and left <= column <= right
                    for top, left, bottom, right in regions
                ):
                    continue
                value = float(values[row, column])
                axis.text(
                    column,
                    row,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=settings.annotation_fontsize,
                    color=PlotStyle.annotation_color(
                        value, color_map, normalization
                    ),
                )
        if show_colorbar:
            colorbar = figure.colorbar(
                image,
                ax=axis,
                fraction=settings.colorbar_fraction,
                pad=settings.colorbar_pad,
            )
            colorbar.ax.tick_params(
                labelsize=settings.colorbar_tick_labelsize
            )
            if settings.show_colorbar_label:
                colorbar.set_label(
                    settings.colorbar_label,
                    fontsize=settings.colorbar_label_fontsize,
                )
        try:
            return FigureSaver.save(
                figure, output_path, dpi=self.config.dpi
            )
        finally:
            plt.close(figure)

    def plot_colorbar(
        self,
        matrix: object,
        output_path: str | Path,
        *,
        vmin: float | None = None,
        vmax: float | None = None,
    ) -> Path:
        """Draw only the vertical attention colorbar."""
        values = finite_array(matrix, "matrix")
        if values.ndim != 2:
            raise ValueError("matrix must be two-dimensional.")
        lower = float(values.min()) if vmin is None else float(vmin)
        upper = float(values.max()) if vmax is None else float(vmax)
        if not np.isfinite([lower, upper]).all() or lower >= upper:
            raise ValueError("vmin and vmax must be finite and vmin < vmax.")

        PlotStyle.configure()
        settings = self.config.attention
        color_map = PlotStyle.resolve_colormap(
            settings.colormap, "figure_tool_attention_colorbar"
        )
        normalization = mpl.colors.Normalize(vmin=lower, vmax=upper)
        figure = plt.figure(figsize=settings.colorbar_figsize)
        axis = figure.add_axes((0.12, 0.04, 0.125, 0.92))
        colorbar = figure.colorbar(
            mpl.cm.ScalarMappable(norm=normalization, cmap=color_map),
            cax=axis,
        )
        colorbar.ax.tick_params(labelsize=settings.colorbar_tick_labelsize)
        if settings.show_colorbar_label:
            colorbar.set_label(
                settings.colorbar_label,
                fontsize=settings.colorbar_label_fontsize,
            )
        try:
            return FigureSaver.save(
                figure, output_path, dpi=self.config.dpi
            )
        finally:
            plt.close(figure)

    @staticmethod
    def _labels(
        labels: Sequence[str] | None, size: int, name: str
    ) -> list[str]:
        if labels is None:
            return [str(index) for index in range(size)]
        result = [str(label) for label in labels]
        if len(result) != size:
            raise ValueError(f"{name} must contain {size} labels.")
        return result

    @staticmethod
    def _validate_regions(
        regions: Sequence[Region], rows: int, columns: int
    ) -> None:
        for region in regions:
            if len(region) != 4:
                raise ValueError("Each region must be (top, left, bottom, right).")
            top, left, bottom, right = region
            if not (
                0 <= top <= bottom < rows and 0 <= left <= right < columns
            ):
                raise ValueError(
                    f"Region {region} is outside matrix shape {(rows, columns)}."
                )


class TimeSeriesPlotter:
    """Draw one univariate or multivariate time-series window."""

    def __init__(self, config: FigureToolConfig | None = None) -> None:
        self.config = config or FigureToolConfig.default()

    def plot(
        self,
        values: object,
        output_path: str | Path,
        *,
        timestamps: Sequence[object] | None = None,
        labels: Sequence[str] | None = None,
        mask: object | None = None,
        standardize: bool = False,
        title: str | None = None,
        xlabel: str = "Time",
        ylabel: str = "Value",
        legend: bool = True,
    ) -> Path:
        series = finite_array(values, "values")
        if series.ndim == 1:
            series = series[:, None]
        if series.ndim != 2:
            raise ValueError("values must have shape [time] or [time, variables].")
        length, variables = series.shape
        if length == 0 or variables == 0:
            raise ValueError("values must not be empty.")
        names = self._labels(labels, variables)
        x_values = (
            np.arange(length)
            if timestamps is None
            else np.asarray(list(timestamps), dtype=object)
        )
        if len(x_values) != length:
            raise ValueError(f"timestamps must contain {length} values.")
        observed = self._mask(mask, series.shape)

        plotted = series.copy()
        if standardize:
            mean = plotted.mean(axis=0, keepdims=True)
            scale = plotted.std(axis=0, keepdims=True)
            plotted = (plotted - mean) / np.maximum(scale, 1e-12)
            ylabel = f"Standardized {ylabel.lower()}"
        plotted[~observed] = np.nan

        PlotStyle.configure()
        settings = self.config.time_series
        try:
            colors = mpl.colormaps[settings.colormap].colors
        except (KeyError, AttributeError) as error:
            raise ValueError(
                f"time_series.colormap must be a listed colormap, got "
                f"{settings.colormap!r}."
            ) from error
        figure, axis = plt.subplots(
            figsize=settings.figsize, constrained_layout=True
        )
        for index, name in enumerate(names):
            axis.plot(
                x_values,
                plotted[:, index],
                color=colors[index % len(colors)],
                linewidth=settings.line_width,
                label=name,
            )
        if settings.grid:
            axis.grid(axis="y", color="#B0B0B0", linewidth=0.5, alpha=0.3)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.tick_params(
            axis="x",
            labelsize=settings.xtick_labelsize,
            bottom=settings.show_xticks,
            labelbottom=settings.show_xticks,
        )
        axis.tick_params(
            axis="y",
            labelsize=settings.ytick_labelsize,
            left=settings.show_yticks,
            labelleft=settings.show_yticks,
        )
        if settings.show_axis_labels:
            axis.set_xlabel(xlabel, fontsize=settings.xlabel_fontsize)
            axis.set_ylabel(ylabel, fontsize=settings.ylabel_fontsize)
        if title:
            axis.set_title(title, fontsize=settings.title_fontsize)
        if legend:
            axis.legend(
                frameon=False,
                fontsize=settings.legend_fontsize,
            )
        try:
            return FigureSaver.save(
                figure, output_path, dpi=self.config.dpi
            )
        finally:
            plt.close(figure)

    def plot_legend(
        self,
        labels: Sequence[str],
        output_path: str | Path,
    ) -> Path:
        """Draw only the time-series legend."""
        names = [str(label) for label in labels]
        if not names:
            raise ValueError("labels must not be empty.")
        PlotStyle.configure()
        settings = self.config.time_series
        try:
            colors = mpl.colormaps[settings.colormap].colors
        except (KeyError, AttributeError) as error:
            raise ValueError(
                f"time_series.colormap must be a listed colormap, got "
                f"{settings.colormap!r}."
            ) from error
        figure = plt.figure(figsize=settings.legend_figsize)
        handles = [
            mpl.lines.Line2D(
                [],
                [],
                color=colors[index % len(colors)],
                linewidth=settings.line_width,
            )
            for index in range(len(names))
        ]
        figure.legend(
            handles,
            names,
            loc="center",
            ncol=min(settings.legend_columns, len(names)),
            frameon=False,
            fontsize=settings.legend_fontsize,
            borderaxespad=0.0,
        )
        try:
            return FigureSaver.save(
                figure, output_path, dpi=self.config.dpi
            )
        finally:
            plt.close(figure)

    @staticmethod
    def _labels(labels: Sequence[str] | None, variables: int) -> list[str]:
        if labels is None:
            return [f"Variable {index + 1}" for index in range(variables)]
        result = [str(label) for label in labels]
        if len(result) != variables:
            raise ValueError(f"labels must contain {variables} labels.")
        return result

    @staticmethod
    def _mask(mask: object | None, shape: tuple[int, int]) -> np.ndarray:
        if mask is None:
            return np.ones(shape, dtype=bool)
        result = np.asarray(mask)
        if result.shape == (shape[0],) and shape[1] == 1:
            result = result[:, None]
        if result.shape != shape:
            raise ValueError(f"mask must have shape {shape}.")
        return result.astype(bool, copy=False)
