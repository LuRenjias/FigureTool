# FigureTool

用于绘制单个注意力矩阵和单个时间序列窗口的轻量工具。支持 `.png`、
`.pdf` 和 `.svg` 输出，输出格式由文件扩展名决定。

```python
import numpy as np

from FigureTool import AttentionHeatmapPlotter, TimeSeriesPlotter

attention = np.random.default_rng(0).random((3, 3))
AttentionHeatmapPlotter().plot(
    attention,
    "figures/attention.svg",
    row_labels=["A", "B", "C"],
    column_labels=["A", "B", "C"],
    annotate=True,
    title="Variable attention",
)

values = np.random.default_rng(0).normal(size=(96, 3))
mask = np.ones_like(values, dtype=bool)
mask[20:35, 1] = False
TimeSeriesPlotter().plot(
    values,
    "figures/time_series.png",
    labels=["A", "B", "C"],
    mask=mask,
    standardize=True,
    title="Input window",
)
```

默认样式位于 `plot_config.toml`。使用其他配置：

```python
from FigureTool import FigureToolConfig, TimeSeriesPlotter

config = FigureToolConfig.load("my_plot_config.toml")
plotter = TimeSeriesPlotter(config)
```

## 通过 app.py 绘图

编辑 `FigureTool/input.py`，然后从项目根目录运行：

```bash
conda run -n tslib python -m FigureTool.app
```

默认输出为 `FigureTool/output/attention.svg` 和
`FigureTool/output/time_series.svg`。可通过 `--input`、`--config`、
`--output-dir`、`--format`、`--attention-filename` 和
`--time-series-filename` 指定输入、配置、输出目录、格式及文件名。例如：

```bash
conda run -n tslib python -m FigureTool.app \
  --format png \
  --attention-filename my_attention \
  --time-series-filename my_series.svg
```

文件名不带扩展名时使用 `--format`；带扩展名时以文件名中的格式为准。

默认情况下图例位于时间序列图内。使用
`--separate-time-series-legend` 可将图例输出到单独文件：

```bash
conda run -n tslib python -m FigureTool.app \
  --time-series-filename my_series.svg \
  --separate-time-series-legend
```

此时输出 `my_series.svg` 和 `my_series_legend.svg`。

默认情况下 colorbar 位于注意力图内。使用
`--separate-attention-colorbar` 可将其输出到单独文件：

```bash
conda run -n tslib python -m FigureTool.app \
  --attention-filename my_attention.svg \
  --separate-attention-colorbar
```

此时输出 `my_attention.svg` 和 `my_attention_colorbar.svg`。

也支持直接运行 `conda run -n tslib python FigureTool/app.py`。
