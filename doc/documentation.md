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
### **1.Initialization `__init__`**
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
### 1. **`plot_graph()`**

This method plots a graph based on the provided data and configuration settings.

#### **Signature**
```python
plot_graph(data_array=[[]], **kwargs)
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

### **Graph Customization Arguments**

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
| **`graph_types`** | data | Specifies the type of graph. Options: `"2D"` for 2D plots, `"3D"` for projection of 3d plot, where z coordinate is represented by color. | list of strings or one string, where strings are "2D" or "3D". | `graph_types=["2D", "3D"]` or `graph_types="2D"`|
| **`color`** | data | Colors for curves. Accepts hex codes | list of strings or one string, where strings represent color in hex format. |`color=["#FF5733", "#2ECC71"]` or `color="#FF5733"` |
| **`marker_shape`** | data | Shape of markers for data points. [Possible options](#marker-shapes-descriptions)| list of strings or one string, with marker shapes options. |`marker_shape=["o", "^"]` or `marker_shape="o"` |
| **`marker_size`** | data | Size of markers. (Default is 3) | List of int positive numbers or one number, which represents the size  of points (markers) | `marker_size=[1, 2]` or `marker_size=2` |
| **`labels`** | data |Labels for curves. These appear in the legend. | list of strings or one string, where strings are labels for data in legend. | `labels=["Curve 1", "Curve 2"]` or `labels="Curve 1"` |
| **`ls`** | data | Line styles for curves. [Possible options](#line-style-descriptions)| list of strings or one string, with ls options. |`ls=["-", "--"]` or `ls='-'` |
 **`line_width`** | data | Line width for curves. (Defualt is 0.5) | List of float or int non-negative numbers or one number| `line_width=[2, 0.8]` or `line_width=1.5` |
|**`line_alpha`** | data | Transparency of the lines (0 is fully transparent, 1 is opaque). (Default is 1)| list of float (int) numbers or one number, where they are from section [0, 1]. | `line_alpha=[1, 0.3]` or `line_alpha=0.5` |
| **`subplots_titles_text`** | sub | Titles for each subplot, shown in the top-left corner. (Default is letters from English alphabet) | list of strings or one string, where strings are titles for subplots. | `subplots_titles_text=["a", "b", "c"]` or `subplots_titles_text="a"`|
| **`subplots_titles_font_size`** | sub | Font size for subplot titles. (Default is 8) | list of elements like [index, font_size], where font_size is positive integer number. | `subplots_titles_font_size=[[0, 10], [-1, 7]]` - subplot 0 will have title font size 10, other subplots will have titles font size 7 or `subplots_titles_font_size=8` - all subplots titles font size are 8. |
| **`axes_titles`** | sub |Titles for the axes. For 2D plots, use `["X", "Y"]`. For 3D plots, use `["X", "Y", "colorbar"]`. (Default for x(y)-axis - "X"("Y"), colorbar-axis - "") | list of elements like ["x-axis", "y-axis"] or ["x-axis", "y-axis", "cbar-axis"] where titles are strings. |`axes_titles=[["null plot x", "null plot y"], ["first plot x", "first plot y", "first plot cbar"]]` or `axes_titles="title_for_all_axes"`|
| **`axes_font_size`** | sub | Font size for axis labels. (Default settings are x(y)-axis - 8, cbar-axis - 10) | list of elements like `[index, [x_size, y_size]]` or `[index, [x_size, y_size, cbar_size]]`, where x(y, cbar)_size - positive integers, or one number for all axes.| `axes_font_size=[[0, [16, 16, 14]]]` - null subplot axes have font sizes - 16, 16, 14, other will have default font size, or `axes_font_size = 8`|
| **`axes_scaling`** | sub | Controls axis limits and tick intervals. Use `"stretch"` for automatic scaling or `"divide"` to manually specify ranges. | list of elements like `[index, "stretch", [x_min, x_max, y_min, y_max]]`, where x(y)_min(max) - coefficient (int or float) that will be multiplied by min(max) number for x(y) axis of data that will be placed in the index-subplot. Or `[index, "divide", [[x_min, x_max, x_step], [y_min, y_max, y_step]]`, where x(y)_min(max) - limits for x, y axis, x(y)_step - number of steps in respective axes. | `axes_scaling=[[2, "divide", [[0, 10, 5], [0, 100, 10]]], [-1, "stretch", [0.9, 1.1, 0.9, 1.1]]]`, "divide" for second subplot, "stretch" for all other subplots. |
| **`axes_round_accuracy`** | sub | Defining rounding for axis labels of ticks. | list of elements like `[index, ["%0.xf", "%0.yf"]]`, where x(y) is an int number that axis ticks labels will rounded to. Or one string for all axes. | `axes_round_accuracy=[[0, ["%0.1f", "%0.2f"]], [-1, ["%0.2f", "%0.2f"]]]`, in null subplot x axis will rounded to first decimal, y axis to second decimal, all others axes will be rounded to the second decimal. |
| **`logarithmic_scaling`** | sub | Enables logarithmic scaling for axes. | list of elements like `[index, [x_log, y_log]]`, where if x(y)_log equals to `1`, it enables and `0` disables. Or one number (0/1) for all axes. | `logarithmic_scaling=[[0, [1, 0]]]`, in null subplot x-axis will have logarithmic scaling, all others will have normal scaling(default). |
| **`colormap`** | sub | Color map for 3D plots. [Possible options](#colormap-options)| list of elements like [index, colormap], where colormap can be str, Colormap. Or one string (Colormap). |`colormap=[[2, "Spectral"]]`  - if in the second subplot has 3d data, it will be colored with "Spectral". |
| **`subplots_legend_position`**| sub | Position for legends in subplots. [Possible options](#legend-position-options)| list of elements like [index, legend_pos], where legend_pos is string. Or one string for all subplots. |`subplots_legend_position=[[1, "upper right"], [-1, "best"]]`, in the first subplot legend will be placed in the upper right edge of the subplot, in others the best position for legend will be placed in the best position.|
| **`legends_font_size`**| sub | Font size for legend position. (Default number is 8) | list of elements like [index, legends_font_size], where legends_font_size is positive number, or one nu,ber for all subplots. | `legends_font_size=[[0, 10]]` - null subplot will have legend font size 10, all others default.|
---
## **Possible options for some parameters**
---
### Line Style Descriptions

The following line styles can be used with the `ls` parameter:

- `"-"`: Solid line.
- `"--"`: Dashed line.
- `"-."`: Dash-dot line.
- `":"`: Dotted line.
---
### Marker Shapes Descriptions
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
### Colormap options
site where you can find possible options for colormap:
https://matplotlib.org/stable/users/explain/colors/colormaps.html 

**Remember!!! we do NOT take responsibility if you have made a mistake in colormap spelling.**

---
### Legend position options
o 'best'
o 'upper right', 'upper left', 'lower left', 'lower right'
o 'right', 'center left', 'center right'
o 'lower center', 'upper center', 'center'
o 'outside' (interpreted as 'center right' for placement outside the plot)

