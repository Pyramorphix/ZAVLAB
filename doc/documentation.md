# Documentation for the `Earl` Class

The `Earl` class is a powerful tool for creating and customizing 2D and 3D plots with Matplotlib. It supports multi-subplot configurations, error bars, annotations, and lines. Users can configure plots via a JSON configuration file or override settings directly through method arguments.

---

**`REMEMBER WE DON'T TAKE RESPONSIBILITY FOR ALL EARL ACTIONS IF YOU USE CONFIG FILES WRITTEN BY YOUSELF.`**

---

This document provides a brief explanation of the `Earl` class and its parameters.

---

## Overview

The `Earl` class is a powerful tool for managing and plotting data using `matplotlib`, based on configuration settings defined in a JSON file. It allows users to create complex visualizations with multiple subplots, customizable appearance settings, and data management capabilities.

---

## **Class Overview**
The `Earl` class enables:
- Flexible plotting of 2D and 3D graphs.
- Error bar support for data visualization.
- Multi-subplot customization with individual or global settings.
- Line drawing and annotation.
- Saving plots and configurations for reuse.

---
### **1.Initialization `__init__`**
Initializes the `Earl` class with an optional configuration file.
```python
from ZAVLAB.graph_plotting import Earl
example_graph = Earl()
```
#### Parameters:
- **`file_path_name_to_conf`** *(str, optional)*:  
  Path to the JSON configuration file that defines default plot settings. Defaults to `"./settings/config.json"`.
- **`verbose`** *(bool, optional)*:  
  If `True`, detailed messages about the plotting process and errors are printed. Defaults to `False`.
#### Example:
```python
graph = Earl(file_path_name_to_conf="./my_config.json", verbose=True)
```
 It will use my_config.json as base graphs configuration and will print all information during plotting.
---
## **Methods**
### 1. **`plot_graph()`**

This method plots a graph based on the provided data and configuration settings.

#### **Signature**
```python
plot_graph(data_array=[[]], **kwargs)
```
#### **Parameters**
- **`data_array`** *(list of lists)*:  
  A nested list containing the data to be plotted. Each element represents a curve or graph:
  - **2D Data with Errors:**
    ```python
    [
        [[x_data, x_error], [y_data, y_error]]
    ]
    ```
  - **2D Data without Errors:**
    ```python
    [
        [[x_data], [y_data]]
    ]
    ```
  - **3D Data:**
    ```python
    [
        x_data, y_data, z_data
    ]
    ```

- **`kwargs`** *(optional)*: Additional arguments to customize the graph. These override the configuration file settings.

---

### **Graph Customization Arguments**

The following arguments can be used with `plot_graph()` to customize the appearance of graphs and subplots. Settings that include **subplot indexes** can have a value of `-1`, which means the setting will be applied to all subplots that **do not have their own specific setting**.


| **Argument**                | **Description**|     Possible input                                                                                                                                                              | **Example**                                                                                   |
|-----------------------------|--------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| **`rows_cols`** | Specifies the number of rows and columns for subplots. | list of two integers: [ny, nx], where ny(nx) is number of rows(cols) in your figure.| `rows_cols=[2, 2]` |
| **`figure_size`** | Size of the entire figure in inches. | list of two integers: [w, h], where w(h) is width(height) of your figure. | `figure_size=[12, 10]` |
| **`subplots_distribution`** | Specifies subplot positions for curves or graphs. | list of non-negative integers,where index of these inegers represents the number of dataset and numbers shows the index of a subplot, or one non-negative integers for all datasets. |`subplots_distribution=[0, 0, 1]` - places the first two datasets in subplot 0 and the next two in subplot 1.  `subplots_distribution=0` places all datasets in subplot 0. |
| **`graph_types`**           | Specifies the type of graph. Options: `"2D"` for 2D plots, `"3D"` for 3D.| plots.                                                                                                 | `graph_types=["2D", "3D"]`                                                                    |
| **`ls`**                    | Line styles for curves. Options include: `'-'` (solid), `'--'` (dashed), `':'` (dotted), etc.                                                                                    | `ls=["-", "--"]`                                                                              |
| **`colors`**                | Colors for curves. Accepts hex codes or predefined names.                                                                                                                        | `colors=["#FF5733", "#2ECC71"]`                                                               |
| **`labels`**                | Labels for curves. These appear in the legend.                                                                                                                                   | `labels=["Curve 1", "Curve 2"]`                                                               |
| **`axes_titles`**           | Titles for the axes. For 2D plots, use `["X", "Y"]`. For 3D plots, use `["X", "Y", "colorbar"]`.                                                                                 | `axes_titles=[["Time", "Amplitude"]]`                                                        |
| **`subplots_titles_text`**  | Titles for each subplot, shown in the top-left corner.                                                                                                                           | `subplots_titles_text=["a", "b", "c"]`                                                        |
| **`axes_font_size`**        | Font size for axis labels. Can apply to all subplots or individual ones. Use `[index, [x_size, y_size]]`.                                                                         | `axes_font_size=[[0, [16, 16]], [-1, [12, 12]]]`                                              |
| **`line_width`**            | Line width for curves. Default is `0.5`.                                                                                                                                         | `line_width=[1, 2]`                                                                           |
| **`marker_size`**           | Size of markers. Default is `3`.                                                                                                                                                 | `marker_size=[4, 5]`                                                                          |
| **`marker_shape`**          | Shape of markers for data points. Options include `'o'` (circle), `'v'` (triangle_down), `'^'` (triangle_up), etc.                                                              | `marker_shape=["o", "^"]`                                                                     |
| **`logarithmic_scaling`**   | Enables logarithmic scaling for axes. Specify for each subplot: `[x_log, y_log]` where `1` enables and `0` disables. If the index is `-1`, it applies to all subplots.            | `logarithmic_scaling=[[0, [1, 0]], [-1, [0, 1]]]`                                             |
| **`axes_scaling`**          | Controls axis limits and tick intervals. Use `"stretch"` for automatic scaling or `"divide"` to manually specify ranges.                                                         | `axes_scaling=[[2, "divide", [[0, 10, 5], [0, 100, 10]]]]`                                    |
| **`colormap`**              | Color map for 3D plots. Options: `"plasma"`, `"Spectral"`, `"YlOrRd"`, etc.                                                                                                     | `colormap=[[2, "Spectral"]]`                                                                  |
| **`axes_round_accuracy`**   | Format for rounding axis labels.                                                                                                                                                 | `axes_round_accuracy=[[0, ["%0.1f", "%0.2f"]], [-1, ["%0.2f", "%0.2f"]]]`                     |
| **`subplots_legend_position`**| Position for legends in subplots. Options include `"best"`, `"upper right"`, `"lower left"`, etc.                                                                                | `subplots_legend_position=[[0, "upper right"], [-1, "best"]]`                                 |

---

- **`rows_cols`** (list, default: `[1, 1]`):Number of rows and columns of subplots.Example: `[2, 2]` creates a 2x2 grid of subplots.
- **`figure_size`** (list, default: `[10, 8]`):Size of the figure in inches. Example: `[12, 6]`.
- **`subplots_distribution`** (list, optional):Assigns datasets to specific subplots by index.Example: `[0, 0, 1, 1]` places the first two datasets in subplot 0 and the next two in subplot 1.
- **`ls`** (list, optional):
  Line styles for each dataset.Example: `["-", "--", ":", "-."]`.For available styles, refer to the **Line Style Descriptions** section below.
- **`labels`** (list, optional):Labels for the plotted datasets.
- **`graph_types`** (list, optional):Determines the type of each graph.

  - `"2D"` for 2D plots.
  - `"3D"` for 3D surface plots.
- **`colormap`** (list, optional):Specifies the colormap for 3D plots.Example: `[[1, "Spectral"], [2, "YlOrRd"]]` assigns the colormap "Spectral" to subplot 1 and "YlOrRd" to subplot 2.
- **`axes_titles`** (list, optional):Titles for the X, Y, and (for 3D) Z/colorbar axes.Example: `[["X-axis", "Y-axis"], ["X", "Y", "Colorbar"]]`.
- **`axes_font_size`** (list, optional):Font sizes for the axes titles.Example: `[[0, [16, 16]], [1, [14, 14, 14]]]`.
- **`subplots_titles_font_size`** (list, optional):Font size for subplot titles.Example: `[[1, 20]]`.
- **`axes_scaling`** (list, optional):Controls scaling and limits for the axes.Example: `[[0, "divide", [[0, 10, 11], [0, 100, 11]]]]` divides the X-axis into 11 intervals from 0 to 10 and the Y-axis into 11 intervals from 0 to 100.
- **`logarithmic_scaling`** (list, optional):Enables logarithmic scaling for axes.Example: `[[0, [1, 0]]]` applies logarithmic scaling to the X-axis of subplot 0.
- **`axes_round_accuracy`** (list, optional):Formatting for tick labels on axes.Example: `[[0, ["%0.0f", "%0.1f"]]]`.
- **`line_width`** (list, optional):Width of the lines in the plot. Example: `[1, 2, 3]`.
- **`line_alpha`** (float, optional):Transparency of the lines (0 is fully transparent, 1 is opaque).
- **`marker_shape`** (list, optional):Marker shapes for each dataset.Example: `["o", "x", "s", "*"]`.For available shapes, refer to the **Marker Shape Descriptions** section below.
- **`marker_size`** (list, optional):
  Size of the markers. Example: `[5, 10, 15]`.

---

### **3. `save_plot`**

Saves the current plot to a file.

#### Parameters:

- `name` (str, default: `"graph.png"`):
  Name of the output file. The file format is determined by the extension (e.g., `.png`, `.jpg`).

#### Example:

```python
graph.save_plot(name="my_plot.png")
```

---

### **4. `draw_lines`**

Adds lines and annotations to the plot.

#### Parameters:

- **`start_point`** (list):Starting coordinates of the line. Example: `[x_start, y_start]`.
- **`end_point`** (list):Ending coordinates of the line. Example: `[x_end, y_end]`.
- **`text`** (str):Annotation text for the line.
- **`subplot_pos_line`** (int):Subplot index where the line should be added.
- **`text_pos`** (list, optional):Position of the annotation text. Example: `[x_text, y_text]`.
- **`text_rotation`** (int, default: `0`):
  Rotation angle for the annotation text.

#### Example:

```python
graph.draw_lines(
    start_point=[1, 10],
    end_point=[5, 50],
    text="Example Line",
    subplot_pos_line=0,
    text_pos=[3, 30],
    text_rotation=45
)
```

---

### **5. `show_plot`**

Displays the plot in an interactive window.

#### Syntax:

```python
show_plot()
```

---

### **6. `save_config`**

Saves the current plot configuration to a JSON file.

#### Parameters:

- `name` (str, default: `"config.json"`):
  Name of the configuration file.

#### Example:

```python
graph.save_config(name="./my_config.json")
```

---

## Line Style Descriptions

The following line styles can be used with the `ls` parameter:

- `"-"`: Solid line.
- `"--"`: Dashed line.
- `"-."`: Dash-dot line.
- `":"`: Dotted line.

---

## Marker Shape Descriptions

The following marker shapes can be used with the `marker_shape` parameter:

- `"o"`: Circle.
- `"s"`: Square.
- `"x"`: Cross.
- `"*"`: Star.
- `"D"`: Diamond.
- `"+"`: Plus.
- `"v"`: Downward triangle.
- `"^"`: Upward triangle.

---

## Example: Full Customization

```python
import numpy as np
from ZAVLAB.graph_plotting import Earl

# Create an instance of Earl
graph = Earl()

# Define data
data_array = [
    [[np.linspace(1, 10, 10)], [np.linspace(10, 100, 10)]],  # 2D dataset
    [np.linspace(-10, 10, 100), np.linspace(-10, 10, 100), np.random.rand(100, 100)],  # 3D dataset
]

# Plot the data
graph.plot_graph(
    data_array=data_array,
    ls=["-", ""],
    labels=["2D Line", "3D Surface"],
    rows_cols=[1, 2],
    figure_size=[12, 6],
    graph_types=["2D", "3D"],
    colormap=[[1, "Spectral"]],
    axes_titles=[["X-axis", "Y-axis"], ["X", "Y", "Colorbar"]],
)

# Add a line and annotation
graph.draw_lines(
    start_point=[1, 10],
    end_point=[5, 50],
    text="Example Line",
    subplot_pos_line=0,
)

# Display the plot
graph.show_plot()

# Save the plot and configuration
graph.save_plot(name="custom_plot.png")
graph.save_config(name="custom_config.json")
```

---

This documentation provides a brief explanation of all parameters to help users utilize the `Earl` class effectively. For more advanced examples, refer to the `examples` folder in the repository.
