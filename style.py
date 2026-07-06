"""Shared Matplotlib style and figure savers."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import numpy as np

from .config import ColorMapSpec


class PlotStyle:
    @staticmethod
    def configure() -> None:
        mpl.rcParams.update(
            {
                "font.family": "DejaVu Sans",
                "font.size": 8.5,
                "axes.titlesize": 10,
                "axes.labelsize": 9,
                "xtick.labelsize": 7.5,
                "ytick.labelsize": 7.5,
                "pdf.fonttype": 42,
                "ps.fonttype": 42,
                "savefig.facecolor": "white",
                "figure.facecolor": "white",
            }
        )

    @staticmethod
    def resolve_colormap(
        specification: ColorMapSpec, custom_name: str
    ) -> mpl.colors.Colormap:
        if isinstance(specification, str):
            try:
                return mpl.colormaps[specification]
            except KeyError as error:
                raise ValueError(
                    f"Unknown Matplotlib colormap: {specification!r}."
                ) from error
        invalid = [
            color for color in specification if not mpl.colors.is_color_like(color)
        ]
        if invalid:
            raise ValueError(f"Invalid colors: {invalid}.")
        return mpl.colors.LinearSegmentedColormap.from_list(
            custom_name, list(specification)
        )

    @staticmethod
    def annotation_color(
        value: float,
        color_map: mpl.colors.Colormap,
        normalization: mpl.colors.Normalize,
    ) -> str:
        red, green, blue, _ = color_map(normalization(value))
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return "black" if luminance > 0.55 else "white"


class FigureSaver:
    """Save a figure according to the output filename extension."""

    SUPPORTED_SUFFIXES = {".png", ".pdf", ".svg"}

    @classmethod
    def save(
        cls,
        figure: mpl.figure.Figure,
        output_path: str | Path,
        *,
        dpi: int,
    ) -> Path:
        path = Path(output_path).expanduser()
        suffix = path.suffix.lower()
        if suffix not in cls.SUPPORTED_SUFFIXES:
            supported = ", ".join(sorted(cls.SUPPORTED_SUFFIXES))
            raise ValueError(f"Output extension must be one of: {supported}.")
        path.parent.mkdir(parents=True, exist_ok=True)
        options: dict[str, object] = {"bbox_inches": "tight"}
        if suffix == ".png":
            options["dpi"] = dpi
        figure.savefig(path, **options)
        return path.resolve()


class PngPlotter:
    def __init__(self, dpi: int) -> None:
        self.dpi = dpi

    def save(self, figure: mpl.figure.Figure, output_path: str | Path) -> Path:
        path = Path(output_path)
        if path.suffix.lower() != ".png":
            raise ValueError("PngPlotter output path must end with .png.")
        return FigureSaver.save(figure, path, dpi=self.dpi)


class PdfPlotter:
    @staticmethod
    def save(figure: mpl.figure.Figure, output_path: str | Path) -> Path:
        path = Path(output_path)
        if path.suffix.lower() != ".pdf":
            raise ValueError("PdfPlotter output path must end with .pdf.")
        return FigureSaver.save(figure, path, dpi=300)


class SvgPlotter:
    @staticmethod
    def save(figure: mpl.figure.Figure, output_path: str | Path) -> Path:
        path = Path(output_path)
        if path.suffix.lower() != ".svg":
            raise ValueError("SvgPlotter output path must end with .svg.")
        return FigureSaver.save(figure, path, dpi=300)


def finite_array(values: object, name: str) -> np.ndarray:
    array = np.asarray(values)
    if not np.issubdtype(array.dtype, np.number):
        raise TypeError(f"{name} must contain numeric values.")
    array = array.astype(float, copy=False)
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain only finite values.")
    return array
