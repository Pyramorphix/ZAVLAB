# Documentation for `configuration_doc.md`

The `configuration_doc.md` file outlines the parameters used in the `config.json` file, which defines the settings for plotting graphs using the `Earl` class. This documentation explains each parameter in `config.json` to help users create or modify the configuration file for their specific plotting needs.

---

## Configuration File Parameters

### **1. `subplots_settings`**
Defines the layout and appearance of subplots.

#### Structure:
```json
"subplots_settings": [
    {
        "rows_cols": [rows, cols],
        "figure_size": [width, height],
        "subplots_distribution": [indices]
    }
]
```

#### Parameters:
- **`rows_cols`** (list):  
  Specifies the number of rows and columns in the subplot grid.  
  Example: `[2, 3]` creates a grid with 2 rows and 3 columns.

- **`figure_size`** (list):  
  Sets the size of the entire figure in inches.  
  Example: `[12, 8]` creates a figure 12 inches wide and 8 inches tall.

- **`subplots_distribution`** (list):  
  Maps datasets to specific subplots. Each value corresponds to the subplot index for a dataset.  
  Example: `[0, 0, 1, 1, 2]` places the first two datasets in subplot 0, the next two in subplot 1, and the last dataset in subplot 2.

---

### **2. `axes_titles`**
Defines titles for the axes of each subplot.

#### Structure:
```json
"axes_titles": [
    ["X-axis title", "Y-axis title"],
    ["X-axis title", "Y-axis title", "Colorbar title"]
]
```

#### Parameters:
- **`X-axis title`** (str): Title for the X-axis of the subplot.
- **`Y-axis title`** (str): Title for the Y-axis of the subplot.
- **`Colorbar title`** (str, optional): Title for the colorbar (used in 3D plots).

#### Example:
```json
"axes_titles": [
    ["Time (s)", "Amplitude (m)"],
    ["X", "Y", "Magnitude"]
]
```

---

### **3. `axes_font_size`**
Controls the font size of axis titles.

#### Structure:
```json
"axes_font_size": [
    [subplot_index, [X_font_size, Y_font_size]],
    [subplot_index, [X_font_size, Y_font_size, Colorbar_font_size]]
]
```

#### Parameters:
- **`subplot_index`** (int): Index of the subplot to apply the font size.
- **`X_font_size`**, **`Y_font_size`**, **`Colorbar_font_size`** (int): Font sizes for the X-axis, Y-axis, and colorbar titles.

#### Example:
```json
"axes_font_size": [
    [0, [12, 14]],
    [1, [10, 10, 12]]
]
```

---

### **4. `subplots_titles_font_size`**
Sets the font size for subplot titles.

#### Structure:
```json
"subplots_titles_font_size": [
    [subplot_index, font_size]
]
```

#### Parameters:
- **`subplot_index`** (int): Index of the subplot.
- **`font_size`** (int): Font size for the subplot title.

#### Example:
```json
"subplots_titles_font_size": [
    [0, 16],
    [1, 18]
]
```

---

### **5. `axes_scaling`**
Defines scaling and limits for the axes.

#### Structure:
```json
"axes_scaling": [
    [subplot_index, "scaling_type", [[X_min, X_max, X_steps], [Y_min, Y_max, Y_steps]]]
]
```

#### Parameters:
- **`subplot_index`** (int): Index of the subplot.
- **`scaling_type`** (str): Determines how the axes are scaled.  
  - `"stretch"`: Scales the axes to fit the data.
  - `"divide"`: Divides the axes into equal intervals.
- **`X_min`, `X_max`, `X_steps`** (float): Minimum, maximum, and number of steps for the X-axis.
- **`Y_min`, `Y_max`, `Y_steps`** (float): Minimum, maximum, and number of steps for the Y-axis.

#### Example:
```json
"axes_scaling": [
    [0, "divide", [[0, 100, 11], [0, 50, 6]]],
    [1, "stretch", [0, 1.1, 0, 1.1]]
]
```

---

### **6. `logarithmic_scaling`**
Enables logarithmic scaling for the axes.

#### Structure:
```json
"logarithmic_scaling": [
    [subplot_index, [X_log, Y_log]]
]
```

#### Parameters:
- **`subplot_index`** (int): Index of the subplot.
- **`X_log`**, **`Y_log`** (int):  
  - `1`: Apply logarithmic scaling.  
  - `0`: Keep linear scaling.

#### Example:
```json
"logarithmic_scaling": [
    [0, [1, 0]],
    [1, [0, 1]]
]
```

---

### **7. `axes_round_accuracy`**
Sets the number formatting for tick labels.

#### Structure:
```json
"axes_round_accuracy": [
    [subplot_index, ["X_format", "Y_format"]]
]
```

#### Parameters:
- **`subplot_index`** (int): Index of the subplot.
- **`X_format`**, **`Y_format`** (str): Formatting strings for the X and Y axes.  
  Example formats:  
  - `"%0.0f"`: No decimal places.  
  - `"%0.1f"`: One decimal place.

#### Example:
```json
"axes_round_accuracy": [
    [0, ["%0.0f", "%0.1f"]],
    [1, ["%0.2f", "%0.0f"]]
]
```

---

### **8. `axes_number_of_small_ticks`**
Defines the number of minor ticks between major ticks.

#### Structure:
```json
"axes_number_of_small_ticks": [
    [subplot_index, [X_ticks, Y_ticks]]
]
```

#### Parameters:
- **`subplot_index`** (int): Index of the subplot.
- **`X_ticks`**, **`Y_ticks`** (int): Number of minor ticks for the X and Y axes.

#### Example:
```json
"axes_number_of_small_ticks": [
    [0, [5, 5]],
    [1, [3, 4]]
]
```

---

### **9. `colormap`**
Specifies the colormap for 3D plots.

#### Structure:
```json
"colormap": [
    [subplot_index, "colormap_name"]
]
```

#### Parameters:
- **`subplot_index`** (int): Index of the subplot.
- **`colormap_name`** (str): Name of the colormap.  
  Example colormaps: `"Spectral"`, `"YlOrRd"`, `"viridis"`.

#### Example:
```json
"colormap": [
    [0, "Spectral"],
    [1, "YlOrRd"]
]
```

---

### **10. `colors`**
Defines custom colors for lines or markers in the plot.

#### Structure:
```json
"colors": ["#FF5733", "#2ECC71", ...]
```

#### Parameters:
- **`colors`** (list of strings): List of color codes (hexadecimal or named colors).

#### Example:
```json
"colors": ["#FF5733", "#2ECC71", "#3498DB"]
```

---

### **11. `line_style`**
Defines the line styles for datasets.

#### Structure:
```json
"line_style": ["-", "--", "-.", ":"]
```

#### Parameters:
- **`line_style`** (list of strings): Line styles for each dataset.  
  Available styles:  
  - `"-"`: Solid line.  
  - `"--"`: Dashed line.  
  - `"-."`: Dash-dot line.  
  - `":"`: Dotted line.

---

### **12. `marker_shape`**
Defines the marker shapes for datasets.

#### Structure:
```json
"marker_shape": ["o", "s", "x", "*"]
```

#### Parameters:
- **`marker_shape`** (list of strings): Marker shapes for each dataset.  
  Available shapes:  
  - `"o"`: Circle.  
  - `"s"`: Square.  
  - `"x"`: Cross.  
  - `"*"`: Star.

---

### **13. `legend_position`**
Sets the legend position for the plot.

#### Structure:
```json
"legend_position": "best"
```

#### Parameters:
- **`legend_position`** (str): Position of the legend.  
  Common options: `"best"`, `"upper left"`, `"lower right"`, `"center"`.

---

## Example `config.json`

```json
{
    "subplots_settings": [
        {
            "rows_cols": [2, 2],
            "figure_size": [12, 8],
            "subplots_distribution": [0, 0, 1, 1]
        }
    ],
    "axes_titles": [