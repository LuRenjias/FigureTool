"""Edit this file, then run: python -m FigureTool.app"""

# Variable order is shared by the attention matrix and time-series columns.
VARIABLE_LABELS = ["Variable A", "Variable B", "Variable C"]

# Shape: [variables, variables]. Rows are queries and columns are keys.
ATTENTION_MATRIX = [
    [0.487, 0.438, 0.075],
    [0.401, 0.526, 0.073],
    [0.164, 0.142, 0.694],
]

# Shape: [time steps, variables]. Default: 10 time steps and 3 variables.
TIME_SERIES_VALUES = [
    [2.3, 2.4, 1.2],
    [2.7, 2.8, 0.9],
    [2.5, 2.6, 1.3],
    [3.1, 3.0, 1.0],
    [2.8, 2.9, 1.4],
    [3.4, 3.5, 1.1],
    [3.0, 3.1, 0.8],
    [3.6, 3.7, 1.3],
    [3.3, 3.2, 1.0],
    [3.8, 3.9, 1.2],
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
