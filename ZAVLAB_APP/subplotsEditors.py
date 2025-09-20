from PyQt6.QtWidgets import (QApplication, QWidget, QFormLayout,
                            QComboBox, QLineEdit, QDoubleSpinBox,
                            QHBoxLayout, QLineEdit, QPushButton,
                            QFrame, QLabel, QSpinBox, QColorDialog,
                            QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                            QCheckBox, QScrollArea, QGroupBox, QStackedWidget,
                            QTableWidget, QHeaderView, QGridLayout, QSizePolicy)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal
import numpy as np


####Constants for axes scaling and minimum UI height
AXES_SCALING = 100
Minimum_Height = 100
####

class DataStyleTab(QWidget):
    """A widget for styling data series (lines) within subplots."""

    #signal emitted when some action happens.
    data_style_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.line_color = "#ff0000"  # Default line color (red)
        self.current_data_style: dict = {}  # Stores current style properties
        self.__init_style_tab_ui()  # Initialize UI

    def __init_style_tab_ui(self) -> None:
        """Initializes the UI components for data styling."""
        
        # Main layout setup
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        #container with scroller
        scroll_container: QScrollArea = QScrollArea(self)
        scroll_container.setWidgetResizable(True)
        scroll_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        scroll_container.setMinimumHeight(Minimum_Height)

        #style layout
        style_widget: QWidget = QWidget()
        style_layout = QFormLayout(style_widget)
        scroll_container.setWidget(style_widget)
        main_layout.addWidget(scroll_container)

        #widget to choose subplot
        self.data_styles_spin = QComboBox()
        self.data_styles_spin.addItems(["None"])
        self.data_styles_spin.currentTextChanged.connect(self.__data_styles_changed__)
        style_layout.addRow("Data to change:", self.data_styles_spin)
        
        #widget to change line label
        self.line_label = QLineEdit()
        self.line_label.setText("y(x)")
        self.line_label.setPlaceholderText("Enter line label...")
        style_layout.addRow("Line Label:", self.line_label)

        #widgets for setting line parameters
        #width
        self.line_width_spin = QDoubleSpinBox()
        self.line_width_spin.setMinimum(0)
        self.line_width_spin.setRange(0.1, 10.0)
        self.line_width_spin.setValue(1.0)
        style_layout.addRow("Line Width:", self.line_width_spin)
        
        #color
        color_layout = QHBoxLayout()
        self.line_color_btn = QPushButton("Choose Color")
        self.line_color_btn.clicked.connect(self.choose_line_color)
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 1px solid #888; border-radius: 3px;")
        self.color_preview.setProperty("color", self.line_color)
        color_layout.addWidget(QLabel("Line Color:"))
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.line_color_btn)
        style_layout.addRow(color_layout)
        
        #line style
        self.line_style_spin = QComboBox()
        self.line_style_spin.addItems(["Nothing", "- (solid)", ": (solid)", "-- (dashed)", "-. (dashdot)"])
        self.line_style_spin.setCurrentIndex(0)
        style_layout.addRow("Line style:", self.line_style_spin)
        
        #line transparancy
        self.line_transparancy = QDoubleSpinBox()
        self.line_transparancy.setRange(0.0, 1.0)
        self.line_transparancy.setValue(1.0)
        self.line_transparancy.setSingleStep(0.01)
        self.line_transparancy.setDecimals(2)
        style_layout.addRow("Line transparancy:", self.line_transparancy)

        #line markers
        self.dotes_marker_shape = QComboBox()
        self.dotes_marker_shape.addItems(["o", "", ".", ",", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "D", "d", "|", "_"])
        self.dotes_marker_shape.setCurrentIndex(0)
        style_layout.addRow("Marker shape:", self.dotes_marker_shape)

        #line marker sizes
        self.dotes_marker_size = QSpinBox()
        self.dotes_marker_size.setMinimum(0)
        self.dotes_marker_size.setValue(3)
        style_layout.addRow("Marker size:", self.dotes_marker_size)

        
        #update button
        self.update_style_btn = QPushButton("Update Data Style")
        self.update_style_btn.clicked.connect(self.__update_data_style__)
        style_layout.addRow(self.update_style_btn)
        
    
    def __data_styles_changed__(self) -> None:
        """Handles changes in data selection and updates controls accordingly."""

        if not self.data_styles_spin.currentText():
            return
        
        self.line_label.setText(self.data_styles_spin.currentText().split('-')[0][:-1])
        data_id = int(self.data_styles_spin.currentText().split('-')[1])
        series = self.current_data_style
        if series:
            if series['id'] == data_id:
                self.line_color = series["color"]
                self.line_width_spin.setValue(series["width"])
                self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 1px solid #888; border-radius: 3px;")
                self.color_preview.setProperty("color", self.line_color)
                self.line_style_spin.setCurrentText(series["ls"])
                self.line_transparancy.setValue(series["alpha"])
                self.dotes_marker_shape.setCurrentText(series["marker"])
                self.dotes_marker_size.setValue(series["marker size"])

    def choose_line_color(self) -> None:
        """Opens color dialog for line color selection."""

        color = QColorDialog.getColor(initial=QColor(self.line_color))
        if color.isValid():
            self.line_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 0px solid #888; border-radius: 3px;")
            self.color_preview.setProperty("color", self.line_color)

    def __update_data_style__(self) -> None:
        """Emits signal to update data style with current parameters."""

        self.data_style_signal.emit(self.data_styles_spin.currentText().split('-')[-1].lstrip().rstrip())

    def __populate_controls__(self, data_series: dict) -> None:
        """Populates controls with data from selected series."""

        self.data_styles_spin.clear()
        self.data_styles_spin.addItems([f"{data['y']}({data['x']}) - {data['id']}" for data in data_series])
        self.data_styles_spin.setCurrentIndex(0)
        self.line_label.setText(f"{data_series[0]['y']}({data_series[0]['x']})")
        self.line_width_spin.setValue(data_series[0]["width"])
        self.line_color = data_series[0]["color"]
        self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 1px solid #888; border-radius: 3px;")
        self.color_preview.setProperty("color", self.line_color) 
        self.line_style_spin.setCurrentText(data_series[0]["ls"])
        self.line_transparancy.setValue(data_series[0]["alpha"])
        self.dotes_marker_shape.setCurrentText(data_series[0]["marker"])
        self.dotes_marker_size.setValue(data_series[0]["marker size"])

    def __update_data_headers_spin__(self, data_series: dict, index: int) -> None:
        """Updates data selection combo box with new headers."""

        self.data_styles_spin.clear()
        self.data_styles_spin.addItems([f"{data['y']}({data['x']}) - {data['id']}" for data in data_series])
        self.data_styles_spin.setCurrentIndex(index)
        self.line_label.setText(f"{data_series[index]['y']}({data_series[index]['x']})")

    def get_data_style_info(self) -> dict:
        """Returns current data style settings as a dictionary."""

        new_color: str = self.line_color
        new_width: int = self.line_width_spin.value()
        new_label: str = self.line_label.text()
        new_ls = self.line_style_spin.currentText().split()[0]
        new_alpha = self.line_transparancy.value()
        new_marker = self.dotes_marker_shape.currentText()
        new_marker_size = self.dotes_marker_size.value()
        if new_ls == "Nothing":
            new_ls = ""
        return {"color" : new_color, "width" : new_width, "label": new_label,
                "ls": new_ls, "alpha": new_alpha, "marker": new_marker,
                "marker size": new_marker_size, "id": int(self.data_styles_spin.currentText().split()[-1])}

    def clear_selection(self) -> None:
        """Resets all controls to default values."""

        self.line_width_spin.setValue(1.0)
        self.line_color = "#1f77b4"
        self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 1px solid #888; border-radius: 3px;")
        self.color_preview.setProperty("color", self.line_color)
        self.line_style_spin.setCurrentText("Nothing")
        self.line_transparancy.setValue(1.0)
        self.dotes_marker_shape.setCurrentText('o')
        self.dotes_marker_size.setValue(3)

    def edit_line_style(self, line) -> None:
        """
        Used for interactive user interaction with plot.
        Edit style properties of a selected plot line:
        - Switches to style tab
        - Loads current line properties into editors
        - Highlights the selected line
        
        Args:
            line: Matplotlib line object to edit
        """


        # get subplot ID
        subplot_id = line._subplot_id
        self.select_subplot(subplot_id)
        
        # Find data_series by ID
        series_id = line._series_id
        for i, series in enumerate(self.plot_canvas.subplots):
            if series[0] == subplot_id:
                for j, data_series in enumerate(series[5]):
                    if data_series.get('id', -1) == series_id:
                        # set current series
                        self.data_styles_spin.setCurrentText("Subplot " + str(series_id))
                        
                        # Switching to the style tab
                        self.editor_tabs.setCurrentIndex(2)  # tab "Data style"
                        
                        # Set the current color
                        self.line_color = data_series['color']
                        self.color_preview.setStyleSheet(f"background-color: {self.line_color};")
                        
                        # Set the current width and ls
                        self.line_width_spin.setValue(data_series['width'])
                        self.line_style_spin.setCurrentText(data_series['ls'])
                        return


class SubplotStyleTab(QWidget):
    """A widget for styling subplot properties including axes, title, legend, and grid."""
    
    #signal emitted when some action happens.
    sub_style_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.__init_subplot_style_tab_ui__()
    
    def __init_subplot_style_tab_ui__(self) -> None:
        """Initializes the UI components for subplot styling."""

        #main layout
        sub_style_layout = QVBoxLayout(self)

        #main tree
        self.settings_tree = QTreeWidget()
        self.settings_tree.setHeaderLabels(["Parameters", "Values"])
        self.settings_tree.setAlternatingRowColors(True)

        #set size policy
        self.settings_tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        # set automatic resizing for columns
        self.settings_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.settings_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.settings_tree.setUniformRowHeights(True)

        #create all tab widgets
        #axis settings
        self.__add_axes_group__()

        #subplot settings
        self.__add_subplot_main_settings_group()

        sub_style_layout.addWidget(self.settings_tree)

        #update columns size after adding all columns
        self.settings_tree.header().setStretchLastSection(False)
        self.settings_tree.resizeColumnToContents(0)
        self.settings_tree.resizeColumnToContents(1)

        self.update_sub_style_btn = QPushButton("Update Subplot Style")
        self.update_sub_style_btn.clicked.connect(self.__update_sub_style__)
        sub_style_layout.addWidget(self.update_sub_style_btn)
    
    def __update_sub_style__(self) -> None:
        """Emits signal to update subplot style."""

        self.sub_style_signal.emit("sub style changed")

    def __add_axes_group__(self) -> None:
        """Adds axes settings group to the tree widget."""

        #main group
        group_main = QTreeWidgetItem(self.settings_tree, ["Axes"])
        group_x = QTreeWidgetItem(group_main, ["X axis"])
        group_y = QTreeWidgetItem(group_main, ["Y axis"])

        #Axes parameters
        params = [
            ("X Axis Title", "text", "X"),
            ("X labels font size", "int", 14, 0),
            ("X Min", "float", 0.0),
            ("X Max", "float", 1.0),
            ("X ticks number", "int", 1, 0),
            ("X small ticks number", "int", 1, 0),
            ("X number of rounding digits", "int", 1),
            ("X scale", "combo", "Linear", ["Linear", "Logarithmic"]),

            ("Y Axis Title", "text", "Y"),
            ("Y labels font size", "int", 14, 0),
            ("Y Min", "float", 0.0),
            ("Y Max", "float", 1.0),
            ("Y ticks number", "int", 1, 0),
            ("Y small ticks number", "int", 1, 0),
            ("Y number of rounding digits", "int", 1),
            ("Y scale", "combo", "Linear", ["Linear", "Logarithmic"]),            
        ]

        #axes widgets
        #x
        self.x_title = None
        self.x_min = None
        self.x_max = None
        self.x_ticks = None
        self.x_small_ticks = None
        self.x_labels_fs = None
        self.x_scale = None
        self.x_number_of_ac = None

        #y
        self.y_title = None
        self.y_min = None
        self.y_max = None
        self.y_ticks = None
        self.y_small_ticks = None
        self.y_labels_fs = None
        self.y_scale = None
        self.y_number_of_ac = None

        #set all axes widgets
        for name, ptype, default, *args in params:
            if name[0] == "X":
                editor = self.__add_parameter__(group_x, name, ptype, default, *args)
            else:
                editor = self.__add_parameter__(group_y, name, ptype, default, *args)

            # Save references to important editors
            if name == "X Axis Title":
                self.x_title: QLineEdit = editor
                self.x_title.setPlaceholderText("Enter label or formula (Example: fraction-$\\frac{a}{b}$(дробь))")
                self.x_title.setToolTip(
                                        "Use LaTeX syntax for formulas:\n"
                                        "• Fractions: \\frac{numerator}{denominator}\n"
                                        "• Degrees: x^2\n"
                                        "• Greek letters: \\alpha, \\beta\n"
                                        "• Roots: \\sqrt{x}\n"
                                        "Be sure to conclude formulas in $...$"
                                    )
            elif name == "X Min":
                self.x_min: QDoubleSpinBox = editor
                self.x_min.valueChanged.connect(self.validate_x_limits)
            elif name == "X Max":
                self.x_max: QDoubleSpinBox = editor
                self.x_max.valueChanged.connect(self.validate_x_limits)
            elif name == "X ticks number":
                self.x_ticks: QSpinBox = editor
            elif name == "X small ticks number":
                self.x_small_ticks: QSpinBox = editor
                self.x_small_ticks.setRange(0, 1000)
            elif name == "X labels font size":
                self.x_labels_fs: QSpinBox = editor
            elif name == "X scale":
                self.x_scale: QComboBox = editor
                self.x_scale.currentTextChanged.connect(self.update_some_xAxis_states)
            elif name == "X number of rounding digits":
                self.x_number_of_ac: QSpinBox = editor
                self.x_number_of_ac.setMinimum(-100)
                self.x_number_of_ac.valueChanged.connect(self.update_range)

            elif name == "Y Axis Title":
                self.y_title: QLineEdit = editor
                self.y_title.setPlaceholderText("Enter label or formula (Example: fraction-$\\frac{a}{b}$(дробь))")
                self.y_title.setToolTip(
                                        "Use LaTeX syntax for formulas:\n"
                                        "• Fractions: \\frac{numerator}{denominator}\n"
                                        "• Degrees: x^2\n"
                                        "• Greek letters: \\alpha, \\beta\n"
                                        "• Roots: \\sqrt{x}\n"
                                        "Be sure to conclude formulas in $...$"
                                    )
            elif name == "Y Min":
                self.y_min: QDoubleSpinBox = editor
                self.y_min.valueChanged.connect(self.validate_y_limits)
            elif name == "Y Max":
                self.y_max: QDoubleSpinBox = editor
                self.y_max.valueChanged.connect(self.validate_y_limits)
            elif name == "Y ticks number":
                self.y_ticks: QSpinBox = editor
            elif name == "Y small ticks number":
                self.y_small_ticks: QSpinBox = editor
                self.y_small_ticks.setRange(0, 1000)
            elif name == "Y labels font size":
                self.y_labels_fs: QSpinBox = editor
            elif name == "Y scale":
                self.y_scale: QComboBox = editor
                self.y_scale.currentTextChanged.connect(self.update_some_yAxis_states)
            elif name == "Y number of rounding digits":
                self.y_number_of_ac: QSpinBox = editor
                self.y_number_of_ac.setMinimum(-100)
                self.y_number_of_ac.valueChanged.connect(self.update_range)

    def update_range(self) -> None:
        """Updates limits for axes."""

        axes_info = {"x min": self.x_min.value(), "x max": self.x_max.value(), "x number of rounding digits": self.x_number_of_ac.value(),
                     "y min": self.y_min.value(), "y max": self.y_max.value(), "y number of rounding digits": self.y_number_of_ac.value()}
        self.__set_new_axes_ranges__(axes_info)

    def __add_subplot_main_settings_group(self) -> None:
        """Adds main subplot settings group to the tree widget."""

        #tree for subplot group
        group: QTreeWidgetItem = QTreeWidgetItem(self.settings_tree, ["Subplot main settings"])
        title_group: QTreeWidgetItem = QTreeWidgetItem(group, ["Title"])
        legend_group: QTreeWidgetItem = QTreeWidgetItem(group, ["Legend"])

        #subplot params
        params = [
            ("Subplot Title", "text", "a"),
            ("Subplot title font size", "int", 14, 0),
            ("Legend position", "combo", "best", ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center']),
            ("Legend font size", "int", 14, 0)
        ]

        #subplot widgets
        self.subplot_title = None
        self.subplot_title_fs = None
        self.legend_position = None
        self.legend_fs = None

        #set subplot widgets
        for name, ptype, default, *args in params[:2]:
            editor = self.__add_parameter__(title_group, name, ptype, default, *args)
            if name == "Subplot Title":
                self.subplot_title: QLineEdit = editor
                self.subplot_title.setPlaceholderText("Enter label or formula (Example: fraction-$\\frac{a}{b}$(дробь))")
                self.subplot_title.setToolTip(
                                        "Use LaTeX syntax for formulas:\n"
                                        "• Fractions: \\frac{numerator}{denominator}\n"
                                        "• Degrees: x^2\n"
                                        "• Greek letters: \\alpha, \\beta\n"
                                        "• Roots: \\sqrt{x}\n"
                                        "Be sure to conclude formulas in $...$"
                                    )
            elif name == "Subplot title font size":
                self.subplot_title_fs: QSpinBox = editor

        for name, ptype, default, *args in params[2:]:
            editor = self.__add_parameter__(legend_group, name, ptype, default, *args)
            if name == "Legend position":
                self.legend_position: QComboBox = editor
            elif name == "Legend font size":
                self.legend_fs: QSpinBox = editor

        #grid preset
        grid_group: QTreeWidgetItem = QTreeWidgetItem(group, ["Grid"])
        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        self.settings_tree.setItemWidget(grid_group, 1, self.grid_checkbox)

    def validate_x_limits(self) -> None:
        """Validates X axis limits to ensure min < max."""

        if not self.x_min or not self.x_max:
            return
            
        x_min: float = self.x_min.value()
        x_max: float = self.x_max.value()
        
        if x_min >= x_max:
            # Adjust min/max to maintain valid range
            if self.x_min.hasFocus():
                # If user is editing min, adjust max
                self.x_max.setValue(x_min + 0.1)
            else:
                # If user is editing max, adjust min
                self.x_min.setValue(x_max - 0.1)
                
            # Highlight problematic fields
            self.highlight_invalid(self.x_min)
            self.highlight_invalid(self.x_max)
        else:
            # Reset highlighting if valid
            self.reset_highlight(self.x_min)
            self.reset_highlight(self.x_max)

    def validate_y_limits(self) -> None:
        """Validates Y axis limits to ensure min < max."""

        if not self.y_min or not self.y_max:
            return
            
        y_min: float = self.y_min.value()
        y_max: float = self.y_max.value()
        
        if y_min >= y_max:
            # Adjust min/max to maintain valid range
            if self.y_min.hasFocus():
                # If user is editing min, adjust max
                self.y_max.setValue(y_min + 0.1)
            else:
                # If user is editing max, adjust min
                self.y_min.setValue(y_max - 0.1)
                
            # Highlight problematic fields
            self.highlight_invalid(self.y_min)
            self.highlight_invalid(self.y_max)
        else:
            # Reset highlighting if valid
            self.reset_highlight(self.y_min)
            self.reset_highlight(self.y_max)

    def highlight_invalid(self, editor: QDoubleSpinBox | QSpinBox | QLineEdit) -> None:
        """Highlight editor with red border to indicate invalid value"""

        if isinstance(editor, (QDoubleSpinBox, QSpinBox)):
            editor.setStyleSheet("border: 1px solid red;")
        elif isinstance(editor, QLineEdit):
            editor.setStyleSheet("QLineEdit { border: 1px solid red; }")

    def reset_highlight(self, editor: QDoubleSpinBox | QSpinBox | QLineEdit) -> None:
        """Removes highlight from input fields."""

        if isinstance(editor, (QDoubleSpinBox, QSpinBox)):
            editor.setStyleSheet("")
        elif isinstance(editor, QLineEdit):
            editor.setStyleSheet("QLineEdit { border: none; }")

    def update_some_xAxis_states(self) -> None:
        """Updates X axis state when scale type changes."""

        if self.x_min.value() <= 0 and self.x_max.value() > 0:
            self.x_min.setValue(self.x_max.value() / 100)
        elif self.x_min.value() < 0 and self.x_max.value() <= 0:
            self.x_min.setValue(1)
            self.x_max.setValue(10)
    
    def update_some_yAxis_states(self) -> None:
        """Updates Y axis state when scale type changes."""

        if self.y_min.value() <= 0 and self.y_max.value() > 0:
            self.y_min.setValue(self.y_max.value() / 100)
        elif self.y_min.value() < 0 and self.y_max.value() <= 0:
            self.y_min.setValue(1)
            self.y_max.setValue(10)

    def __add_parameter__(self, parent: QTreeWidgetItem, name: str, ptype: str, default: str|float|int, *args: tuple) -> None:
        """
        Adds a parameter row to the tree widget with appropriate editor.
        
        Return: editor widget
        """

        #tree for params
        param_item = QTreeWidgetItem(parent, [name])
        editor = None
        
        # Create editor based on parameter type
        if ptype == "float":
            editor = QDoubleSpinBox()
            editor.setValue(default)
            # Set reasonable default range if not provided
            min_val = args[0] if len(args) > 0 else -1000000.0
            max_val = args[1] if len(args) > 1 else 1000000.0
            editor.setRange(min_val, max_val)
            editor.setSingleStep(0.1)
            editor.setDecimals(4)
            editor.setStyleSheet("""
                QDoubleSpinBox:focus {
                    border: 1px solid #4CAF50;
                }
            """)
        elif ptype == "int":
            editor = QSpinBox()
            editor.setValue(default)
            # Set reasonable default range if not provided
            min_val = args[0] if (len(args) > 0 and args[0] >=0) else 0
            max_val = args[1] if len(args) > 1 else 1000000
            editor.setRange(min_val, max_val)
            if len(args) > 2:  # Suffix (unit)
                editor.setSuffix(f" {args[2]}")
            editor.setStyleSheet("""
                QSpinBox:focus {
                    border: 1px solid #4CAF50;
                }
            """)
        elif ptype == "combo":
            editor = QComboBox()
            # If the next argument is a list, use it, else use all remaining args
            if args and isinstance(args[0], list):
                editor.addItems(args[0])
            else:
                editor.addItems(args)
            editor.setCurrentText(default)
            editor.setStyleSheet("""
                QComboBox:focus {
                    border: 1px solid #4CAF50;
                }
            """)
        elif ptype == "text":
            editor = QLineEdit()
            editor.setText(default)
            editor.setPlaceholderText("Enter text...")
            editor.setStyleSheet("""
                QLineEdit:focus {
                    border: 1px solid #4CAF50;
                }
            """)
        
        if editor:
            self.settings_tree.setItemWidget(param_item, 1, editor)
            return editor
        return None

    def __set_new_axes_ranges__(self, axes_info: dict) -> None:
        """Sets new ranges for axis limits based on scaling factors."""

        if np.sign(axes_info["x min"]) == 1:
            x_min = axes_info["x min"] * AXES_SCALING * (-1)
        elif np.sign(axes_info["x min"]) == -1:
            x_min = axes_info["x min"] * AXES_SCALING
        else:
            x_min = axes_info["x max"] * AXES_SCALING * (-1)

        if np.sign(axes_info["x max"]) == 1:
            x_max = axes_info["x max"] * AXES_SCALING
        elif np.sign(axes_info["x max"]) == -1:
            x_max = -axes_info["x max"] * AXES_SCALING * (-1)
        else:
            x_max = axes_info["x min"] * AXES_SCALING * (-1)
        
        if np.sign(axes_info["y min"]) == 1:
            y_min = axes_info["y min"] * AXES_SCALING * (-1)
        elif np.sign(axes_info["y min"]) == -1:
            y_min = axes_info["y min"] * AXES_SCALING
        else:
            y_min = axes_info["y max"] * AXES_SCALING * (-1)

        if np.sign(axes_info["y max"]) == 1:
            y_max = axes_info["y max"] * AXES_SCALING
        elif np.sign(axes_info["y max"]) == -1:
            y_max = axes_info["y max"] * AXES_SCALING * (-1)
        else:
            y_max = axes_info["y min"] * AXES_SCALING * (-1)

        self.x_min.setRange(x_min, x_max)
        self.x_min.setSingleStep(10 ** (-1 * axes_info["x number of rounding digits"]))
        if axes_info["x number of rounding digits"] > -1:
            self.x_min.setDecimals(axes_info["x number of rounding digits"])
        self.x_max.setRange(x_min, x_max)
        self.x_max.setSingleStep(10 ** (-1 * axes_info["x number of rounding digits"]))
        if axes_info["x number of rounding digits"] > -1:
            self.x_max.setDecimals(axes_info["x number of rounding digits"])

        self.y_min.setRange(y_min, y_max)
        self.y_min.setSingleStep(10 ** (-1 * axes_info["y number of rounding digits"]))
        if axes_info["y number of rounding digits"] > -1:
            self.y_min.setDecimals(axes_info["y number of rounding digits"])
        self.y_max.setRange(y_min, y_max)
        self.y_max.setSingleStep(10 ** (-1 * axes_info["y number of rounding digits"]))
        if axes_info["y number of rounding digits"] > -1:
            self.y_max.setDecimals(axes_info["y number of rounding digits"])

    def get_sub_style_info(self) -> dict:
        """Returns current subplot style settings as nested dictionaries."""

        axes_info = self.get_axes_info()
        title_info = self.get_title_info()
        legend_info = self.get_legend_info()
        grid_info = self.get_grid_info()

        return {"axes": axes_info, "title": title_info, "legend": legend_info, "grid": grid_info}
    
    def get_axes_info(self) -> dict:
        """return current information about subplot axes."""

        #x axis
        x_label: str = self.x_title.text()
        x_min:float = self.x_min.value()
        x_max: float = self.x_max.value()
        x_ticks: int = self.x_ticks.value()
        x_small_ticks: int = self.x_small_ticks.value()
        x_label_fs: int = self.x_labels_fs.value()
        x_scale: int = self.x_scale.currentIndex() #0 - linear, 1 - log
        x_number_of_accuracy: int = self.x_number_of_ac.value()

        #y axis
        y_label: str = self.y_title.text()
        y_min: float = self.y_min.value()
        y_max: float = self.y_max.value()
        y_ticks: int = self.y_ticks.value()
        y_small_ticks: int = self.y_small_ticks.value()
        y_label_fs: int = self.y_labels_fs.value()
        y_scale: int = self.y_scale.currentIndex()
        y_number_of_accuracy: int = self.y_number_of_ac.value()

        return {"x-label": x_label,
                "x min": x_min,
                "x max": x_max,
                "x ticks": x_ticks,
                "x small ticks": x_small_ticks,
                "x label fs" : x_label_fs,
                "x scale" : x_scale,
                "x number of rounding digits": x_number_of_accuracy,
                "y-label": y_label,
                "y min": y_min,
                "y max": y_max,
                "y ticks": y_ticks,
                "y small ticks": y_small_ticks,
                "y label fs" : y_label_fs,
                "y scale" : y_scale,
                "y number of rounding digits": y_number_of_accuracy,
            }
    
    def get_title_info(self) -> dict:
        """return current subplot title info."""

        title: str = self.subplot_title.text()
        title_fs: int = self.subplot_title_fs.value()

        return {"title": title, "title fs": title_fs}
    
    def get_legend_info(self) -> dict:
        """return current legend info."""

        legend_pos: str = self.legend_position.currentText()
        legend_fs: int = self.legend_fs.value()

        return {"legend position": legend_pos, "legend fs": legend_fs}
    
    def get_grid_info(self) -> dict:
        """return current subplot grid info."""

        grid: bool = self.grid_checkbox.isChecked()

        return {"show grid": grid}
    
    def clear_selection(self) -> None:
        """Resets all controls to default values."""

        self.x_title.setText('x')
        self.x_min.setValue(0)
        self.x_max.setValue(1)
        self.x_ticks.setValue(5)
        self.x_small_ticks.setValue(5)
        self.x_labels_fs.setValue(14)
        self.x_scale.setCurrentIndex(0)
        self.x_number_of_ac.setValue(4)

        self.y_title.setText('x')
        self.y_min.setValue(0)
        self.y_max.setValue(1)
        self.y_ticks.setValue(5)
        self.y_small_ticks.setValue(5)
        self.y_labels_fs.setValue(14)
        self.y_scale.setCurrentIndex(0)
        self.y_number_of_ac.setValue(4)

        self.subplot_title.setText('a')
        self.subplot_title_fs.setValue(14)
        self.legend_position.setCurrentText("best")
        self.legend_fs.setValue(14)
        self.grid_checkbox.setChecked(True)

    def populate_control(self, sub_info: dict) -> None:
        """Populates controls with existing subplot properties."""

        #get subplot info
        axes_info: dict = sub_info["axes"]
        title_info: dict = sub_info["title"]
        legend_info: dict = sub_info["legend"]
        grid_info: dict = sub_info["grid"]
        self.current_subplot = sub_info
        
        #Axes
        #x axis
        self.x_title.setText(axes_info["x-label"])
        self.x_labels_fs.setValue(axes_info["x label fs"])
        self.x_min.setValue(axes_info["x min"])
        self.x_max.setValue(axes_info["x max"])
        self.x_ticks.setValue(axes_info["x ticks"])
        self.x_small_ticks.setValue(axes_info["x small ticks"])
        self.x_scale.setCurrentIndex(axes_info["x scale"])
        self.x_number_of_ac.setValue(axes_info["x number of rounding digits"])


        #y axis
        self.y_title.setText(axes_info["y-label"])
        self.y_labels_fs.setValue(axes_info["y label fs"])
        self.y_min.setValue(axes_info["y min"])
        self.y_max.setValue(axes_info["y max"])
        self.y_ticks.setValue(axes_info["y ticks"])
        self.y_small_ticks.setValue(axes_info["y small ticks"])
        self.y_scale.setCurrentIndex(axes_info["y scale"])
        self.y_number_of_ac.setValue(axes_info["y number of rounding digits"])

        self.__set_new_axes_ranges__(axes_info)

        #Subplot main settings
        #Title
        self.subplot_title.setText(title_info["title"])
        self.subplot_title_fs.setValue(title_info["title fs"])

        #Legend
        self.legend_position.setCurrentText(legend_info["legend position"])
        self.legend_fs.setValue(legend_info["legend fs"])
        
        #grid   
        self.grid_checkbox.setChecked(grid_info["show grid"])


class LineStyleTab(QWidget):
    """
    A widget for adding and managing annotation lines (e.g., trend lines, guides).
    Supports three line creation methods: by two points, by equation, and by point+angle.
    """

    #Emitted for line-related actions.
    line_style_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.__init_line_style_tab_ui__()

    def __init_line_style_tab_ui__(self) -> None:
        """Initializes the UI components for line styling."""

        #main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        #container with scroller
        scroll_container: QScrollArea = QScrollArea(self)
        scroll_container.setWidgetResizable(True)
        scroll_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        scroll_container.setMinimumHeight(Minimum_Height)

        #main widget
        lines_tab: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(lines_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # The group for adding new lines
        add_group: QGroupBox = QGroupBox("Add line")
        add_layout: QFormLayout = QFormLayout()
        self.lines_id: int = 0

        self.draw_btn: QPushButton = QPushButton("Draw Line ")
        self.draw_btn.setCheckable(True)
        self.draw_btn.setToolTip("If you want to draw line without using line equations or points, you can use this button.\n"
                                 "Follow this steps:\n"
                                 "1. Click \"Draw Line\" button.\n"
                                 "2. Click first time your subplot, this will be starting point of your line.\n"
                                 "3. Click second time your subplot, that will be ending point.\n"
                                 "3. Then pops up dialog window for chossing label text and position.\n"
                                 "4. After pushing \"OK\" button, you line will appear in table with all subplot's lines (in the bottom of this tab).")
        self.draw_btn.toggled.connect(self.toggle_drawing_mode)

        # Add to appropriate layout position
        add_layout.addWidget(self.draw_btn)

        # The group for line labels
        label_group: QGroupBox = QGroupBox("Line label")
        label_layout: QFormLayout = QFormLayout()
        
        # Line type
        self.line_type_combo: QComboBox = QComboBox()
        self.line_type_combo.addItems(["By two points", "By equation", "By point and angle"])
        self.line_type_combo.currentIndexChanged.connect(self.update_line_params_ui)
        add_layout.addRow("Line type:", self.line_type_combo)
        
        # Container for parameters
        self.line_params_stack:QStackedWidget = QStackedWidget()
        
        # Widget for two points
        two_points_widget: QWidget = QWidget()
        two_points_layout: QFormLayout = QFormLayout(two_points_widget)
        self.x1_spin: QDoubleSpinBox = QDoubleSpinBox()
        self.x1_spin.setRange(-10000, 10000)
        self.y1_spin: QDoubleSpinBox = QDoubleSpinBox()
        self.y1_spin.setRange(-10000, 10000)
        self.x2_spin:QDoubleSpinBox = QDoubleSpinBox()
        self.x2_spin.setRange(-10000, 10000)
        self.y2_spin:QDoubleSpinBox = QDoubleSpinBox()
        self.y2_spin.setRange(-10000, 10000)
        two_points_layout.addRow("x1:", self.x1_spin)
        two_points_layout.addRow("y1:", self.y1_spin)
        two_points_layout.addRow("x2:", self.x2_spin)
        two_points_layout.addRow("y2:", self.y2_spin)
        self.line_params_stack.addWidget(two_points_widget)
        
        # Widget for the equation
        equation_widget: QWidget = QWidget()
        equation_layout:QFormLayout = QFormLayout(equation_widget)
        self.k_spin:QDoubleSpinBox = QDoubleSpinBox()
        self.k_spin.setRange(-100, 100)
        self.k_spin.setValue(1.0)
        self.b_spin:QDoubleSpinBox = QDoubleSpinBox()
        self.b_spin.setRange(-10000, 10000)
        equation_layout.addRow("k (angular coefficient):", self.k_spin)
        equation_layout.addRow("b (shift):", self.b_spin)
        self.line_params_stack.addWidget(equation_widget)
        
        # Widget for a point and an angle
        point_angle_widget: QWidget = QWidget()
        point_angle_layout: QFormLayout = QFormLayout(point_angle_widget)
        self.px_spin: QDoubleSpinBox = QDoubleSpinBox()
        self.px_spin.setRange(-10000, 10000)
        self.py_spin: QDoubleSpinBox = QDoubleSpinBox()
        self.py_spin.setRange(-10000, 10000)
        self.angle_spin: QDoubleSpinBox = QDoubleSpinBox()
        self.angle_spin.setRange(-np.pi, np.pi)
        self.angle_spin.setValue(np.pi / 4)
        point_angle_layout.addRow("x choordinate:", self.px_spin)
        point_angle_layout.addRow("y choordinate:", self.py_spin)
        point_angle_layout.addRow("Angle (in radians):", self.angle_spin)
        self.line_params_stack.addWidget(point_angle_widget)
        
        add_layout.addRow(self.line_params_stack)
        
        # line style
        color_layout: QHBoxLayout = QHBoxLayout()
        self.line_draw_color_btn:  QPushButton = QPushButton("Choose color")
        self.line_draw_color_btn.clicked.connect(self.choose_line_color)
        self.line_color_preview: QFrame = QFrame()
        self.line_color_preview.setFixedSize(24, 24)
        self.line_color_draw: str = "#ff0000"
        self.line_color_preview.setStyleSheet(f"background-color: {self.line_color_draw}; border: 1px solid #888;")
        color_layout.addWidget(QLabel("Line color:"))
        color_layout.addWidget(self.line_color_preview)
        color_layout.addWidget(self.line_draw_color_btn)
        add_layout.addRow(color_layout)
        
        self.line_width_spin: QDoubleSpinBox = QDoubleSpinBox()
        self.line_width_spin.setValue(1.5)
        self.line_width_spin.setRange(0.1, 10)
        add_layout.addRow("Line width:", self.line_width_spin)
        
        self.line_style_combo: QComboBox = QComboBox()
        self.line_style_combo.addItems(["- (solid)", "-- (dashed)", "-. (dashdot)", ": (dotted)"])
        add_layout.addRow("Line style:", self.line_style_combo)
        
        self.add_line_btn: QPushButton = QPushButton("Add line")
        self.add_line_btn.clicked.connect(self.add_line_to_subplot)
        add_layout.addRow(self.add_line_btn)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        
        #set labels widgets
        self.line: QComboBox = QComboBox()
        self.line.currentTextChanged.connect(self.change_labels_params)
        label_layout.addRow("Choose line:", self.line)
        self.line_label_edit: QLineEdit = QLineEdit()
        self.line_label_edit.setPlaceholderText("Enter label or formula (Example: fraction-$\\frac{a}{b}$(дробь))")
        self.line_label_edit.setToolTip(
                                "Use LaTeX syntax for formulas:\n"
                                "• Fractions: \\frac{numerator}{denominator}\n"
                                "• Degrees: x^2\n"
                                "• Greek letters: \\alpha, \\beta\n"
                                "• Roots: \\sqrt{x}\n"
                                "Be sure to conclude formulas in $...$"
                            )

        label_layout.addRow("Label text:", self.line_label_edit)
        
        self.label_position_combo: QComboBox = QComboBox()
        self.label_position_combo.addItems([
            "Above the beginning of the line",
            "Above the middle of the line",
            "Above the end of the line",
            "Under the beginning of the line",
            "Under the middle of the line",
            "Under the end of the line",
            "To the left of the beginning",
            "To the left of the middle",
            "To the left of the end",
            "To the right of the beginning",
            "To the right of the middle",
            "To the right of the end"
            ])
        self.label_position_combo.setCurrentIndex(1)
        label_layout.addRow("Label poisition:", self.label_position_combo)
        
        self.label_font_size_spin: QSpinBox = QSpinBox()
        self.label_font_size_spin.setRange(0, 36)
        self.label_font_size_spin.setValue(10)
        label_layout.addRow("Label font size:", self.label_font_size_spin)
        
        self.add_label_btn: QPushButton = QPushButton("Add/Upgrade label")
        self.add_label_btn.clicked.connect(self.add_label_to_line)
        label_layout.addRow(self.add_label_btn)
        
        label_group.setLayout(label_layout)
        layout.addWidget(label_group)

        # List of existing lines
        self.lines_group: QGroupBox = QGroupBox("Existing line")
        lines_layout: QVBoxLayout = QVBoxLayout()
        
        self.lines_table: QTableWidget = QTableWidget(0, 8)
        self.lines_table.setHorizontalHeaderLabels(["Id", "Type", "Parameter", "Color", "Width", "Label", "Position", "Delete"])
        self.lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lines_table.verticalHeader().setVisible(False)
        lines_layout.addWidget(self.lines_table)
        
        self.lines_group.setLayout(lines_layout)
        layout.addWidget(self.lines_group)

        # Add tab
        scroll_container.setWidget(lines_tab)
        main_layout.addWidget(scroll_container)

        # processing table item selection
        self.lines_table.itemSelectionChanged.connect(self.on_line_selected)

    def update_line_params_ui(self) -> None:
        """Updates the UI depending on the selected line creation method."""

        self.line_params_stack.setCurrentIndex(self.line_type_combo.currentIndex())
    
    def choose_line_color(self) -> None:
        """Opens color dialog for line color selection."""

        color: QColor = QColorDialog.getColor(QColor(self.line_color_draw), self)
        if color.isValid():
            self.line_color_draw = color.name()
            self.line_color_preview.setStyleSheet(f"background-color: {self.line_color_draw}; border: 1px solid #888;")
    
    def add_line_to_subplot(self) -> None:
        """Handles adding new line to the subplot."""

        self.line_style_signal.emit("line added")

    def update_lines_labels(self, line: dict) -> None:
        """Updates line labels from existing line data."""
    
        self.line.addItems(["Line " + str(line['id'])])
        self.line.setCurrentText("Line " + str(line['id']))
        self.line_label_edit.setText(line['label'])
        index = self.label_position_combo.findText(line['label_position'])
        if index >= 0:
            self.label_position_combo.setCurrentIndex(index)
        self.label_font_size_spin.setValue(line['label_font_size'])

    def update_lines_table(self) -> None:
        """Updates table of existing lines"""

        self.line_style_signal.emit("table changed")
    
    def delete_line(self, line_index: int) -> None:
        """Removes line from a subplot."""

        self.line_style_signal.emit("delete line " + str(line_index))
        
    def __delete_line_label__(self, line_index: int) -> None:
        """Delete position for adding label for line with index line_index."""

        index = self.line.findText("Line " + str(line_index))
        if index >= 0:
            self.line.removeItem(index)

    def on_line_selected(self) -> None:
        """
        Handles line selection from table.
        Fills in the signature fields when selecting a line.
        """

        try:
            row = self.lines_table.selectedItems()[0].text()

            self.line_style_signal.emit("line selected : " + row)
        except:
            return
    
    def add_label_to_line(self) -> None:
        """Add or updates a signature for a selected line."""

        if self.line.currentText() == '':
            return 
        row = self.line.currentText().split()[-1]

        self.line_style_signal.emit("add label to row : " + row)
        return
    
    def change_labels_params(self) -> None:
        """Handles changes to label parameters."""

        if self.line.currentText()=='':
            return
        index = self.line.currentText().split()[-1]

        self.line_style_signal.emit("change label : " + index)
        return
    
                    
    def toggle_drawing_mode(self, enabled: bool) -> None:
        """
        Toggle line drawing mode on the plot canvas
        
        Args:
            enabled: Boolean indicating whether drawing mode should be activated
        """

        self.line_style_signal.emit("toggle mode : " + str(enabled))
        
        # Update button appearance
        if enabled:
            self.draw_btn.setStyleSheet("background-color: #aaffaa;")
            self.draw_btn.setText("Drawing Mode (click to finish)")
        else:
            self.draw_btn.setStyleSheet("")
            self.draw_btn.setText("Draw Line")


class PositioningChoosingDataTab(QWidget):
    """A widget for managing subplot position, size, and associated data series."""

    # Emitted for position/data changes.
    pos_data_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.__init_pos_data_tab__()
    
    def __init_pos_data_tab__(self) -> None:
        """Initializes the UI components for position/data management."""
    
        #main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        #container with scroller
        scroll_container: QScrollArea = QScrollArea(self)
        scroll_container.setWidgetResizable(True)
        scroll_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        scroll_container.setMinimumHeight(Minimum_Height)

        #main widget
        pos_data_group: QWidget = QWidget()
        self.pos_data_layout: QVBoxLayout = QVBoxLayout(pos_data_group)
        pos_data_group.setLayout(self.pos_data_layout)
        self.pos_data_layout.setContentsMargins(0, 0, 0, 0) 
        pos_data_group.setLayout(self.pos_data_layout)

        #position and size of a subplot
        self.__init_position_size_ui__()

        #data on a subplot
        self.__init_data_ui__()

        #set main widgets
        scroll_container.setWidget(pos_data_group)
        main_layout.addWidget(scroll_container)

    def __init_position_size_ui__(self) -> None:
        """Initialize ui for changing position and size of a subplot."""

        ##The group to change position
        #make group
        pos_group: QGroupBox = QGroupBox("Change subplot position and size")
        pos_layout: QGridLayout = QGridLayout(pos_group)

        #make and add all widgets
        pos_layout.addWidget(QLabel("Row:"), 1, 0)
        self.edit_row_spin: QSpinBox = QSpinBox()
        self.edit_row_spin.setRange(0, 7)
        pos_layout.addWidget(self.edit_row_spin, 1, 1)
        
        pos_layout.addWidget(QLabel("Column:"), 1, 2)
        self.edit_col_spin: QSpinBox = QSpinBox()
        self.edit_col_spin.setRange(0, 7)
        pos_layout.addWidget(self.edit_col_spin, 1, 3)
        
        pos_layout.addWidget(QLabel("Row Span:"), 2, 0)
        self.edit_row_span_spin: QSpinBox = QSpinBox()
        self.edit_row_span_spin.setRange(1, 8)
        self.edit_row_span_spin.setValue(1)
        pos_layout.addWidget(self.edit_row_span_spin, 2, 1)
        
        pos_layout.addWidget(QLabel("Col Span:"), 2, 2)
        self.edit_col_span_spin: QSpinBox = QSpinBox()
        self.edit_col_span_spin.setRange(1, 8)
        self.edit_col_span_spin.setValue(1)
        pos_layout.addWidget(self.edit_col_span_spin, 2, 3)
        
        self.update_position_btn: QPushButton = QPushButton("Update Position/Size")
        self.update_position_btn.clicked.connect(self.update_subplot_position)
        pos_layout.addWidget(self.update_position_btn, 3, 0, 1, 4)

        #add to the main widget
        pos_group.setLayout(pos_layout)
        self.pos_data_layout.addWidget(pos_group)

    def __init_data_ui__(self) -> None:
        """Initialize ui for changing data sets"""
        
        ##The group to change data
        #make group
        data_group: QGroupBox = QGroupBox("Change data placed in subplot")
        data_layout: QFormLayout = QFormLayout(data_group)
        
        #make and add all widgets
        self.data_data_spin: QComboBox = QComboBox()
        self.data_data_spin.addItems(["None"])
        data_layout.addRow("Data to change:", self.data_data_spin)
 
        # data_layout.addWidget(QLabel("X Data:"))
        self.edit_data_combo_x: QComboBox = QComboBox()
        self.edit_data_combo_x.addItems(["None"])
        data_layout.addRow("X Data:", self.edit_data_combo_x)

        # data_layout.addWidget(QLabel("X Error:"))
        self.edit_data_combo_xerr: QComboBox = QComboBox()
        self.edit_data_combo_xerr.addItems(["None"])
        data_layout.addRow("X Error:", self.edit_data_combo_xerr)

        # data_layout.addWidget(QLabel("Y Data:"))
        self.edit_data_combo_y = QComboBox()
        self.edit_data_combo_y.addItems(["None"])
        data_layout.addRow("Y Data:", self.edit_data_combo_y)

        # data_layout.addWidget(QLabel("Y Error:"))
        self.edit_data_combo_yerr = QComboBox()
        self.edit_data_combo_yerr.addItems(["None"])
        data_layout.addRow("Y Error:", self.edit_data_combo_yerr)
        
        self.edit_data_btn = QPushButton("Edit Data Series")
        self.edit_data_btn.clicked.connect(self.edit_data_series)
        data_layout.addRow(self.edit_data_btn)

        self.update_data_btn = QPushButton("Update Data")
        self.update_data_btn.clicked.connect(self.update_subplot_data)
        data_layout.addRow(self.update_data_btn)
        
        #add to the main widget
        data_group.setLayout(data_layout)
        self.pos_data_layout.addWidget(data_group)
    
    def update_subplot_position(self) -> None:
        """Handles subplot position/size updates."""

        self.pos_data_signal.emit("update subplot position")
        return
    
    def update_subplot_data(self) -> None:
        """Handles data series updates."""

        self.pos_data_signal.emit("update subplot data")
    
    def edit_data_series(self) -> None:
        """Initiates data series editing."""

        self.pos_data_signal.emit("edit data series")

    def update_headers_column_data(self, headers: list[str]) -> None:
        """Updates combo boxes with available data headers."""

        self.edit_data_combo_x.clear()
        self.edit_data_combo_x.addItems(["None"] + headers)
        self.edit_data_combo_xerr.clear()
        self.edit_data_combo_xerr.addItems(["None"] + headers)
        self.edit_data_combo_y.clear()
        self.edit_data_combo_y.addItems(["None"] + headers)
        self.edit_data_combo_yerr.clear()
        self.edit_data_combo_yerr.addItems(["None"] + headers)
    
    def clear_selection(self) -> None:
        """Resets all controls to default values."""

        self.edit_row_spin.setValue(0)
        self.edit_col_spin.setValue(0)
        self.edit_row_span_spin.setValue(1)
        self.edit_col_span_spin.setValue(1)
        self.edit_data_combo_x.setCurrentIndex(0)
        self.edit_data_combo_y.setCurrentIndex(0)
        self.edit_data_combo_xerr.setCurrentIndex(0)
        self.edit_data_combo_yerr.setCurrentIndex(0)
    
    def populate_control(self, row: int, col: int, row_span: int, col_span: int, data_series: list[dict]) -> None:
        """Populates controls with existing subplot properties."""

        #populate position and size control
        self.edit_row_spin.setValue(row)
        self.edit_col_spin.setValue(col)
        self.edit_row_span_spin.setValue(row_span)
        self.edit_col_span_spin.setValue(col_span)
        self.data_data_spin.clear()
        self.data_data_spin.addItems([f"{data['y']}({data['x']}) - {data['id']}" for data in data_series])
        self.data_data_spin.setCurrentIndex(0)

        # Populate data controls
        self.edit_data_combo_x.setCurrentText(data_series[0]["x"])
        self.edit_data_combo_y.setCurrentText(data_series[0]["y"])
        self.edit_data_combo_xerr.setCurrentText(data_series[0]["xerr"])
        self.edit_data_combo_yerr.setCurrentText(data_series[0]["yerr"])