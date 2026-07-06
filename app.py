#!/usr/bin/env python3
"""Command-line entry point for FigureTool."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from FigureTool import (  # noqa: E402
    AttentionHeatmapPlotter,
    FigureToolConfig,
    TimeSeriesPlotter,
)

TOOL_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render attention and time-series figures from a Python input file."
    )
    parser.add_argument(
        "--input", type=Path, default=TOOL_DIR / "input.py",
        help="Python input file (default: FigureTool/input.py).",
    )
    parser.add_argument(
        "--config", type=Path, default=TOOL_DIR / "plot_config.toml",
        help="TOML plot configuration.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=TOOL_DIR / "output",
        help="Directory in which figures are written.",
    )
    parser.add_argument(
        "--format", choices=("png", "pdf", "svg"), default="svg",
        help="Output format (default: svg).",
    )
    parser.add_argument(
        "--attention-filename", default="attention",
        help="Attention output filename; extension is optional.",
    )
    parser.add_argument(
        "--time-series-filename", default="time_series",
        help="Time-series output filename; extension is optional.",
    )
    parser.add_argument(
        "--separate-time-series-legend",
        action="store_true",
        help="Write the time-series legend to a separate file.",
    )
    parser.add_argument(
        "--separate-attention-colorbar",
        action="store_true",
        help="Write the attention colorbar to a separate file.",
    )
    parser.add_argument(
        "--attention-matrix-name",
        default="ATTENTION_MATRIX",
        help="Name of the attention-matrix variable in the input file.",
    )
    parser.add_argument(
        "--mask-name",
        default="MASK",
        help="Name of the mask variable in the input file.",
    )
    return parser


def load_input(path: Path) -> ModuleType:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Input file does not exist: {resolved}")
    specification = importlib.util.spec_from_file_location(
        "figure_tool_user_input", resolved
    )
    if specification is None or specification.loader is None:
        raise ImportError(f"Cannot load input file: {resolved}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def required(module: ModuleType, name: str) -> object:
    if not hasattr(module, name):
        raise ValueError(f"Input file must define {name}.")
    return getattr(module, name)


def output_filename(name: str, default_format: str) -> str:
    path = Path(name)
    if path.name != name or name in ("", ".", ".."):
        raise ValueError("Output filename must be a filename, not a path.")
    if not path.suffix:
        return f"{name}.{default_format}"
    if path.suffix.lower() not in {".png", ".pdf", ".svg"}:
        raise ValueError(
            "Output filename extension must be .png, .pdf, or .svg."
        )
    return name


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_data = load_input(args.input)
    config = FigureToolConfig.load(args.config)
    output_dir = args.output_dir.expanduser().resolve()

    labels = required(input_data, "VARIABLE_LABELS")
    attention_options = dict(getattr(input_data, "ATTENTION_OPTIONS", {}))
    time_series_options = dict(getattr(input_data, "TIME_SERIES_OPTIONS", {}))
    attention_filename = output_filename(args.attention_filename, args.format)
    time_series_filename = output_filename(
        args.time_series_filename, args.format
    )
    attention_matrix = required(input_data, args.attention_matrix_name)
    mask = required(input_data, args.mask_name)
    attention_plotter = AttentionHeatmapPlotter(config)
    if args.separate_attention_colorbar:
        attention_options["show_colorbar"] = False
    attention_path = attention_plotter.plot(
        attention_matrix,
        output_dir / attention_filename,
        row_labels=labels,
        column_labels=labels,
        **attention_options,
    )
    colorbar_path = None
    if args.separate_attention_colorbar:
        attention_file = Path(attention_filename)
        colorbar_filename = (
            f"{attention_file.stem}_colorbar{attention_file.suffix}"
        )
        colorbar_path = attention_plotter.plot_colorbar(
            attention_matrix,
            output_dir / colorbar_filename,
            vmin=attention_options.get("vmin"),
            vmax=attention_options.get("vmax"),
        )
    time_series_plotter = TimeSeriesPlotter(config)
    if args.separate_time_series_legend:
        time_series_options["legend"] = False
    time_series_path = time_series_plotter.plot(
        required(input_data, "TIME_SERIES_VALUES"),
        output_dir / time_series_filename,
        timestamps=getattr(input_data, "TIMESTAMPS", None),
        labels=labels,
        mask=mask,
        **time_series_options,
    )
    legend_path = None
    if args.separate_time_series_legend:
        series_path = Path(time_series_filename)
        legend_filename = f"{series_path.stem}_legend{series_path.suffix}"
        legend_path = time_series_plotter.plot_legend(
            labels, output_dir / legend_filename
        )
    print(f"Attention figure: {attention_path}")
    if colorbar_path is not None:
        print(f"Attention colorbar: {colorbar_path}")
    print(f"Time-series figure: {time_series_path}")
    if legend_path is not None:
        print(f"Time-series legend: {legend_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
