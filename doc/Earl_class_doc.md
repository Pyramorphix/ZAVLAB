# Documentation for the `Earl` Class
The `Earl` class is a powerful tool for creating and customizing 2D and 3D plots with Matplotlib. It supports multi-subplot configurations, error bars, annotations, and lines. Users can configure plots via a JSON configuration file or override settings directly through method arguments.

---

**`REMEMBER WE DO NOT TAKE RESPONSIBILITY FOR ALL EARL ACTIONS IF YOU USE CONFIG FILES WRITTEN BY YOUSELF.`**

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
### **Initialization `__init__`**
Initializes the `Earl` class with an optional configuration file.
```python
from ZAVLAB.graph_plotting import Earl
example_graph = Earl()
```
#### Parameters:
- **`file_path_name_to_conf`** *(str, optional)*:  
  Path to the JSON configuration file that defines default plot settings. Defaults to `"../settings/config.json"`.
- **`file_path_name_to_line_conf`** *(str, optional)*:
  Path to the JSON configuration file that defines default lines settings. Defaults to **`None`**.
- **`verbose`** *(bool, optional)*:  
  If `True`, detailed messages about the plotting process and errors are printed. Defaults to `False`.
#### Example:
```python
graph = Earl(file_path_name_to_conf="./my_config.json",      file_path_name_to_line_conf ="./my_config_for_lines.json", verbose=True)
```
 It will use my_config.json as base graphs configuration and will print all information during plotting.
---
## **Methods**
### **`plot_graph()`**

This method plots a graph based on the provided data and configuration settings.

#### **Signature**
```python
graph_example.plot_graph(data_array=[[]], **kwargs)
```
#### **Parameters**
- **`data_array`** *(list of lists)*:  
  A nested list containing the data to be plotted. Each element represents a curve or graph:
  - **2D Data with(out) Errors:**
    ```python
    [ [[x_data, x_error], [y_data, y_error]] ] 
    [ [[x_data, x_error], [y_data]] ] 
    [ [[x_data], [y_data, y_error]] ] 
    [ [[x_data], [y_data]] ]
    ```
  - **3D Data:**
    ```python
    [ x_data, y_data, z_data ]
    ```

- **`kwargs`** *(optional)*: Additional arguments to customize the graph. These override the configuration file settings.

---

#### **Graph Customization Arguments**

The following arguments can be used with `plot_graph()` to customize the appearance of graphs and subplots. 
Your plot arguments can match to **figure** (the thing where all your plots placed), **subplots** (they are things where your plots are placed in figure), **curves** (your data that you want to place in the subplots). \
If type of argument is sub, then argument responds to subplots.\
If type of argument is data, then argument responds to curves.\
If type of argument is fig, then argument responds to figure.\
If argument does not specify any index (**`index`** later) {like [index, some_argument]}, that means that arguments correlate to subplots or data by there position in the list where they are placed. **POSITION IS COUNTED FROM 0**.\
`Example: [1, 2, 3], 1 is for subplot 0, 2 - subplot 1, 3 - subplot 2.` \
`Example: [1, "title"], "title" will be assigned to sublot with index 1.`\
Subplots are numbered from left to right, from top to bottom.\
Settings that include **i** can have a value of `-1`, which means the setting will be applied to all subplots that **do not have their own specific setting (for these argument)**.
Settings that composed from list of elements (without index) can be entered by user as one element that will be applied for all subplots or curves (depends on argument).
List of options for some of parameters are presented after the table.
| **Argument** |**Arg. type**| **Description** | **Possible input** | **Example** |
|--------------|-------------|-----------------|--------------------|-------------|
| **`rows_cols`** | fig |Specifies the number of rows and columns for subplots. | list of two integers: [ny, nx], where ny(nx) is number of rows(cols) in your figure.| `rows_cols=[2, 2]` |
| **`figure_size`** | fig |Size of the entire figure in inches. | list of two integers: [w, h], where w(h) is width(height) of your figure. | `figure_size=[12, 10]` |
| **`subplots_distribution`** | data | Specifies data position (in which subplot it is placed). | list of non-negative integers, where numbers show the index of a subplot. |`subplots_distribution=[0, 0, 1]` - places the first two datasets in subplot 0 and the next two in subplot 1. `subplots_distribution=0` places all datasets in subplot 0. |
| **`data_type`** | data | Specifies the type of data. Options: `"2D"` for 2D plots, `"3D"` for projection of 3d plot, where z coordinate is represented by color. | list of strings or one string, where strings are "2D" or "3D". | `data_type=["2D", "3D"]` or `data_type="2D"`|
| **`color`** | data | Colors for curves. Accepts hex codes | list of strings or one string, where strings represent color in hex format. |`color=["#FF5733", "#2ECC71"]` or `color="#FF5733"` |
| **`marker_shape`** | data | Shape of markers for data points. [Possible options](#marker-shapes-descriptions)| list of strings or one string, with marker shapes options. |`marker_shape=["o", "^"]` or `marker_shape="o"` |
| **`marker_size`** | data | Size of markers. (Default is 3) | List of int positive numbers or one number, which represents the size  of points (markers) | `marker_size=[1, 2]` or `marker_size=2` |
| **`label`** | data |Labels for curves. These appear in the legend. | list of strings or one string, where strings are label for data in legend. | `label=["Curve 1", "Curve 2"]` or `label="Curve 1"` |
| **`line_style`** | data | Line styles for curves. [Possible options](#line-style-descriptions)| list of strings or one string, with line_style options. |`line_style=["-", "--"]` or `line_style='-'` |
| **`line_width`** | data | Line width for curves. (Defualt is 0.5) | List of float or int non-negative numbers or one number| `line_width=[2, 0.8]` or `line_width=1.5` |
| **`line_alpha`** | data | Transparency of the lines (0 is fully transparent, 1 is opaque). (Default is 1)| list of float (int) numbers or one number, where they are from section [0, 1]. | `line_alpha=[1, 0.3]` or `line_alpha=0.5` |
| **`title_text`** | sub | Titles for each subplot, shown in the top-left corner. (Default is letters from English alphabet) | list of strings or one string, where strings are titles for subplots. | `title_text=["a", "b", "c"]` or `title_text="a"`|
| **`title_fsize`** | sub | Font size for subplot titles. (Default is 8) | list of elements like [index, font_size], where font_size is positive integer number. | `title_fsize=[[0, 10], [-1, 7]]` - subplot 0 will have title font size 10, other subplots will have titles font size 7 or `title_fsize=8` - all subplots titles font size are 8. |
| **`axes_title`** | sub |Titles for the axes. For 2D plots, use `["X", "Y"]`. For 3D plots, use `["X", "Y", "colorbar"]`. (Default for x(y)-axis - "X"("Y"), colorbar-axis - "") | list of elements like ["x-axis", "y-axis"] or ["x-axis", "y-axis", "cbar-axis"] where titles are strings. |`axes_title=[["zero plot x", "zero plot y"], ["first plot x", "first plot y", "first plot cbar"]]` or `axes_title="title_for_all_axes"`|
| **`axes_title_fsize`** | sub | Font size for axis labels. (Default settings are x(y)-axis - 8, cbar-axis - 10) | list of elements like `[index, [x_size, y_size]]` or `[index, [x_size, y_size, cbar_size]]`, where x(y, cbar)_size - positive integers, or one number for all axes.| `axes_title_fsize=[[0, [16, 16, 14]]]` - zero subplot axes have font sizes - 16, 16, 14, other will have default font size, or `axes_title_fsize = 8`|
| **`axes_scaling`** | sub | Controls axis limits and tick intervals. Use `"stretch"` for automatic scaling or `"divide"` to manually specify ranges. | list of elements like `[index, "stretch", [x_min, x_max, y_min, y_max]]`, where x(y)_min(max) - coefficient (int or float) that will be multiplied by min(max) number for x(y) axis of data that will be placed in the index-subplot. Or `[index, "divide", [[x_min, x_max, x_step], [y_min, y_max, y_step]]`, where x(y)_min(max) - limits for x, y axis, x(y)_step - number of steps in respective axes. | `axes_scaling=[[2, "divide", [[0, 10, 5], [0, 100, 10]]], [-1, "stretch", [0.9, 1.1, 0.9, 1.1]]]`, "divide" for second subplot, "stretch" for all other subplots. |
| **`axes_round_accuracy`** | sub | Defining rounding for axis labels of ticks. | list of elements like `[index, ["%0.xf", "%0.yf"]]`, where x(y) is an int number that axis ticks labels will rounded to. Or one string for all axes. | `axes_round_accuracy=[[0, ["%0.1f", "%0.2f"]], [-1, ["%0.2f", "%0.2f"]]]`, in zero subplot x axis will rounded to first decimal, y axis to second decimal, all others axes will be rounded to the second decimal. |
| **`axes_small_ticks`** | sub | Defining a number of small ticks on axes between two big ticks. | list of elements like `[index, [x, y]]`, where x(y) is an int number which is the number of small ticks in x, y axis. | `axes_small_ticks=[[0, [4, 5]], [-1, [5, 5]]]`, in zero subplot x  and y axis will have 3 and 4 small ticks, all others axes will 4 small ticks. |
| **`axes_log_scaling`** | sub | Enables logarithmic scaling for axes. | list of elements like `[index, [x_log, y_log]]`, where if x(y)_log equals to `1`, it enables and `0` disables. Or one number (0/1) for all axes. | `axes_log_scaling=[[0, [1, 0]]]`, in zero subplot x-axis will have logarithmic scaling, all others will have normal scaling(default). |
| **`colormap`** | sub | Color map for 3D plots. [Possible options](#colormap-options)| list of elements like [index, colormap], where colormap can be str, Colormap. Or one string (Colormap). |`colormap=[[2, "Spectral"]]`  - if in the second subplot has 3d data, it will be colored with "Spectral". |
| **`legend_position`**| sub | Position for legends in subplots. [Possible options](#legend-position-options)| list of elements like [index, legend_pos], where legend_pos is string. Or one string for all subplots. |`legend_position=[[1, "upper right"], [-1, "best"]]`, in the first subplot legend will be placed in the upper right edge of the subplot, in others the best position for legend will be placed in the best position.|
| **`legend_fsize`**| sub | Font size for legend position. (Default number is 8) | list of elements like [index, legends_font_size], where legends_font_size is positive number, or one nu,ber for all subplots. | `legend_fsize=[[0, 10]]` - zero subplot will have legend font size 10, all others default.|
|||||
---
#### Example
```python
graph.plot_graph(data_array=data_array, graph_types="2D", ls=["-"]*2 + ["--"]) #data_array has 3 elements for 2d graph. zero and first will have solid line, second will be dashed.
```
---

### **`show_plot()`**

Displays the plot in an interactive window.

#### Syntax:

```python
graph_example.show_plot()
```
---

### **`save_plot()`**

Saves the current plot to a file.

#### Parameters:

- `name` (str, default: `"graph.png"`):
  Name of the output file. The file format is determined by the extension (e.g., `.png`, `.jpg`).

#### Example:

```python
graph_example.save_plot(name="my_plot.png")
```
---
### **`save_config()`**

Saves the current plot configuration to a JSON file.

#### Parameters:

- `name` (str, default: `"New_config.json"`):
  Name of the configuration file.

#### Example:

```python
graph_example.save_config(name="./my_config.json")
```
---
### **`change_config_file()`**

Change the current plot configuration to a JSON file.

#### Parameters:

- `name` (str):
  Name of the configuration file.

#### Example:

```python
graph_example.change_config_file(name="./my_config.json")
```
---

### **`draw_lines()`**

Adds lines and annotations to the plot.

#### Parameters:
| **Argument** | **Description** | **Possible input** | **Example** |
|--------------|-----------------|--------------------|-------------|
| **`start_point`** | Starting coordinates of the line (Default is [0, 0])| list of elements like [x, y], where x(y) is int(float) number, or only one [x, y] list. | `start_point=[[0, 1], [0.5, 0.2]]` or `start_point=[0, 1]`|
| **`end_point`** | Ending coordinates of the line (Default is [1, 1])| list of elements like [x, y], where x(y) is int(float) number, or only one [x, y] list. | `end_point=[[0, 1], [0.5, 0.2]]` or `end_point=[0, 1]`|
| **`subplot_line`** | Subplot index where the line should be added (Default is 0).| list of indexes or one index (indexes are int non-negative numbers). | `subplot_pos_line=[1, 0, 2]`, `subplot_pos_line=1`|
| **`line_color`** | Colors for lines. Accepts hex codes. | list of strings or one string, where strings represent color in hex format. |`line_color=["#FF5733", "#2ECC71"]` or `line_color="#FF5733"` |
| **`line_style`** | Line styles for line. [Possible options](#line-style-descriptions)| list of strings or one string, with ls options. |`line_style=["-", "--"]` or `line_style='-'` |
| **`line_alpha`** | Transparency of the lines (0 is fully transparent, 1 is opaque). (Default is 1)| list of float (int) numbers or one number, where they are from section [0, 1]. | `line_alpha=[1, 0.3]` or `line_alpha=0.5` |
| **`line_width`** | Line width for curves. (Defualt is 1) | List of float or int non-negative numbers or one number| `line_width=[2, 0.8]` or `line_width=1.5` |
| **`label`** | Labels for curves. These appear in the legend. (Default is "")| list of strings or one string, where strings are label for data in legend. | `label=["Curve 1", "Curve 2"]` or `label="Curve 1"` |
| **`text`** | Annotation for lines (Default is "").| list of strings or one string | `text=["line 1", "line 2"]` or `text="line 1"`|
| **`text_pos`** | Position of the annotation text that will appear in the plot. False argument will calculate position correlated with line. (Default is [false, false])| list of elements like [x, y], where x(y) is int, float or False, or one element like these| `text_pos = [1, 0.2]`, `text_pos = [1, False]`, `text_pos = [False, 0.2]`, `text_pos = [[0.1, 3], [False, False], [False, 1.5]]` |.
| **`text_rotation`** | Angle that the text will be rotated for. Angles are measured in degree. (Default is 0)| List of angles in degrees (int or float) or one angle. | `text_rotation=[0, 1.5, -45]`, `text_rotation=90`|
| **`text_color`** | Color of the text annotation. Accepts hex codes. (Default is #000000 - black) | list of strings or one string, where strings are colors only in hex format. | `text_color=["#000000", "#641E16"]`, `text_color="#641E16"` |
| **`text_fsize`** | Font size for line's annotation. (Default is 8)| list of int or one int, where int numbers are non-negative. | `text_fsize=[9, 8]`, `text_fsize=10` |

#### Example:

```python
graph.draw_lines(
    start_point=[1, 10],
    end_point=[5, 50],
    text="Example Line",
    subplot_line=0,
    text_pos=[3, 30],
    text_rotation=45
)
```
---
### **`save_config_for_lines()`**

Saves the current lines configuration that drawn to a plot as a JSON file.

#### Parameters:

- `name` (str, default: `"New_config_for_lines.json"`):
  Name of the configuration file.

#### Example:

```python
graph_example.save_config_for_lines(name="./my_config_for_lines.json")
```
---
### **`change_config_for_lines_file()`**

Change the current lines configuration to a JSON file.

#### Parameters:

- `name` (str):
  Name of the configuration file.

#### Example:

```python
graph_example.change_config_for_lines_file(name="./my_config_for_lines.json")
```
---
### **`print_curve_settings()`**

Print settings for specified curves.

#### Parameters:

- `curve_index` (int):
  index of the curve that should be printed.

#### Example:

```python
graph_example.print_curve_settings(curve_index=0)
```
---
### **`print_subplot_settings()`**

Print settings for specified subplot.

#### Parameters:

- `subplot_index` (int):
  index of the subplot that should be printed.

#### Example:

```python
graph_example.print_subplot_settings(subplot_index=0)
```
---
### **`print_config()`**

Print configuration (config.json and config_for_line.json).

#### Example:

```python
graph_example.print_config()
```
---

### **Possible options for some parameters**
---
#### Line Style Descriptions

The following line styles can be used with the `ls` parameter:

- `"-"`: Solid line.
- `"--"`: Dashed line.
- `"-."`: Dash-dot line.
- `":"`: Dotted line.
---
#### Marker Shapes Descriptions
| Marker Shape | Description           | Symbol   |
|--------------|-----------------------|----------|
| `.`          | Point marker          | .        |
| `,`          | Pixel marker          | ,        |
| `o`          | Circle marker         | o        |
| `v`          | Triangle down marker  | ▼        |
| `^`          | Triangle up marker    | ▲        |
| `<`          | Triangle left marker  | ◀        |
| `>`          | Triangle right marker | ▶        |
| `1`          | Tri down marker       | ↓        |
| `2`          | Tri up marker         | ↑        |
| `3`          | Tri left marker       | ←        |
| `4`          | Tri right marker      | →        |
| `8`          | Octagon marker        | ⬣        |
| `s`          | Square marker         | □        |
| `p`          | Pentagon marker       | ⬠        |
| `P`          | Plus (filled) marker  | ⤬        |
| `*`          | Star marker           | ☆        |
| `h`          | Hexagon1 marker       | ⬡        |
| `H`          | Hexagon2 marker       | ⬡        |
| `+`          | Plus marker           | +        |
| `x`          | X marker              | ×        |
| `X`          | X (filled) marker     | ✕        |
| `D`          | Diamond marker        | ◊        |
| `d`          | Thin diamond marker   | ◊        |
| `\|`         | Vertical line marker  | │        |
| `_`          | Horizontal line marker| ─        |
| '""'         | None marker           |          |
|||
---
#### Colormap options
site where you can find possible options for colormap:
https://matplotlib.org/stable/users/explain/colors/colormaps.html 

**Remember!!! we do NOT take responsibility if you have made a mistake in colormap spelling.**

---
#### Legend position options
- 'best'
- 'upper right', 'upper left', 'lower left', 'lower right'
- 'right', 'center left', 'center right'
- 'lower center', 'upper center', 'center'
- 'outside' (interpreted as 'center right' for placement outside the plot)

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
    label=["2D Line", "3D Surface"],
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
