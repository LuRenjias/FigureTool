"""Edit this file, then run: python -m FigureTool.app"""

# Variable order is shared by the attention matrix and time-series columns.
VARIABLE_LABELS = ["Variable A", "Variable B", "Variable C"]

# Shape: [variables, variables]. Rows are queries and columns are keys.
ATTENTION_MATRIX = [
    [0.70, 0.20, 0.10],
    [0.15, 0.65, 0.20],
    [0.10, 0.25, 0.65],
]

# Shape: [time steps, variables]. Default: 10 time steps and 3 variables.
TIME_SERIES_VALUES = [
    [1.0, 2.0, 1.5],
    [1.2, 2.2, 1.4],
    [1.4, 2.1, 1.6],
    [1.3, 2.4, 1.8],
    [1.6, 2.6, 1.7],
    [1.8, 2.5, 2.0],
    [1.7, 2.8, 2.2],
    [2.0, 3.0, 2.1],
    [2.2, 2.9, 2.4],
    [2.4, 3.2, 2.6],
]

# Optional horizontal-axis values; length must equal the number of time steps.
TIMESTAMPS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Optional observation mask, with the same shape as TIME_SERIES_VALUES.
# True means observed; False hides that point from the plotted line.
MASK = [
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
]

# Optional keyword arguments passed to AttentionHeatmapPlotter.plot().
ATTENTION_OPTIONS = {
    "title": "Attention",
    "annotate": True,
    "show_colorbar": True,
    # Zero-based (top, left, bottom, right) coordinates.
    "rectangle_regions": [],
}

# Optional keyword arguments passed to TimeSeriesPlotter.plot().
TIME_SERIES_OPTIONS = {
    "title": "Time series",
    "xlabel": "Time step",
    "ylabel": "Value",
    "standardize": False,
    "legend": True,
}
