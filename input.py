"""Edit this file, then run: python -m FigureTool.app"""

# Variable order is shared by the attention matrix and time-series columns.
VARIABLE_LABELS = ["Variable A", "Variable B", "Variable C"]

import numpy as np

NUM_TIME_STEPS = 100
TIMESTAMPS = list(range(1, NUM_TIME_STEPS + 1))

# ============================================================
# 注意力矩阵
# Shape: [variables, variables]
# Rows are queries and columns are keys.
#
# 变量 1、2 具有较强的双向注意力。
# 变量 3 与变量 1、2 关系较弱，主要关注自身。
# 每一行之和均为 1。
# ============================================================
ATTENTION_MATRIX = [
    [0.490, 0.450, 0.060],
    [0.440, 0.500, 0.060],
    [0.150, 0.130, 0.720],
]


# ============================================================
# 构造变量 1 和变量 2
# 二者均呈现先上升后下降的趋势。
# ============================================================
t = np.linspace(0.0, 1.0, NUM_TIME_STEPS)

# 平滑的单峰趋势，在中间时间步附近达到峰值。
base_trend = np.sin(np.pi * t)

variable_1 = 2.0 + 4.0 * base_trend + 0.08 * np.sin(6.0 * np.pi * t)

# 变量 2 与变量 1 高度相关，但保留轻微差异。
variable_2 = 1.6 + 3.9 * base_trend + 0.06 * np.cos(6.0 * np.pi * t)


# ============================================================
# 构造变量 3
#
# 前段和后段复用变量 1、2 的 base_trend。
# 峰值区域改为先下降后上升的局部反向趋势。
# ============================================================
variable_3 = 1.2 + 3.6 * base_trend + 0.06 * np.cos(6.0 * np.pi * t)

# 峰值区域两侧的边界值，用于保持趋势连续。
left_boundary = variable_3[34]
right_boundary = variable_3[65]
valley_value = 3.0

# 时间步 36—50：下降。
variable_3[35:50] = np.linspace(left_boundary, valley_value, 15)

# 时间步 51—65：上升。
variable_3[50:65] = np.linspace(valley_value, right_boundary, 15)

# 添加轻微、确定性的波动。
variable_3 += 0.05 * np.sin(8.0 * np.pi * t)


# ============================================================
# 合并时间序列
# Shape: [time steps, variables]
# ============================================================
time_series_array = np.column_stack([variable_1, variable_2, variable_3])

# 保留三位小数并转为普通 Python 列表。
TIME_SERIES_VALUES = np.round(time_series_array, 3).tolist()


# ============================================================
# 构造掩码
# Shape: [time steps, variables]
#
# True：该位置保留并参与绘图或计算。
# False：隐藏该位置。
#
# 在时间步 36—65，变量 3 的趋势与变量 1、2 不同，
# 因此将变量 3 对应的位置设置为 False。
# ============================================================
mask_array = np.ones((NUM_TIME_STEPS, 3), dtype=bool)

# Python 索引 35:65 对应时间步 36—65。
# mask_array[35:65, 2] = False

MASK = mask_array.tolist()

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
