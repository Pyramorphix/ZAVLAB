"""
Manages all plotting operations including:
- Data preparation for plotting
- Subplot configuration
- Plot generation
- Axis configuration
"""
from PyQt6.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel, QHBoxLayout,
                             QSplitter, QVBoxLayout, QSpinBox, QGroupBox, QPushButton,
                             QComboBox, QTableWidget, QTabWidget, QFormLayout,
                             QDoubleSpinBox, QCheckBox, QListWidget, QDialog, QMessageBox,
                             QListWidgetItem, QColorDialog, QLineEdit, QTreeWidget,
                             QTreeWidgetItem)
from PyQt6.QtGui import QColor
from interactive_plot import INTERACTIVE_PLOT
from dialogs import SubplotPositionDialog, DataSeriesDialog
from PyQt6.QtCore import Qt
import numpy as np

class SubplotCell(QFrame):
    """
    Visual representation of a single grid cell
    - Shows occupied state with color coding
    - Displays tooltip with subplot information
    """

    def __init__(self, row: int, col: int, parent=None) -> None:
        """
        Initialize a grid cell.
        Args:
            row: Row index in the grid.
            col: Column index in the grid.
            parent: Parent widget.
        """


        super().__init__(parent)
        self.row: int = row
        self.col: int = col
        self.setFixedSize(40, 40)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")
        self.setToolTip(f"Cell ({row},{col})")
        self.occupied = False
        self.subplot_id = None

    def set_occupied(self, subplot_id: int, color: str) -> None:
        """
        Mark this cell as occupied by a subplot.
        Args:
            subplot_id: ID of the subplot.
            color: Color to set for the cell background.
        """

        self.occupied = True
        self.subplot_id = subplot_id
        self.setStyleSheet(f"background-color: {color}; border: 1px solid #333333;")
        self.setToolTip(f"Subplot {subplot_id}")

class SubplotGrid(QWidget):
    """
    Visual grid for designing subplot layouts:
    - Manages cell grid creation/clearing
    - Tracks subplot positions and overlaps
    - Handles visual representation of subplots
    """


    def __init__(self, parent=None):
        """
        Initialize grid
        """


        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.setLayout(self.grid_layout)
        self.cells = {}
        self.subplot_widgets = {}
        self.subplot_labels = {}
        self.subplot_colors = {}
        self.current_color_idx = 0
        self.colors = [
            "#FFCCCC", "#CCFFCC", "#CCCCFF", "#FFFFCC", "#FFCCFF", "#CCFFFF",
            "#FFDDAA", "#DDFFAA", "#DDAADD", "#AADDAA", "#AADDFF", "#FFAADD"
        ]

    def __create_grid__(self, rows, cols):
        """Create grid that visualize subplots position."""


        # Clear existing grid
        self.__clear_grid__()
        
        # Create new grid
        for r in range(rows):
            for c in range(cols):
                cell = SubplotCell(r, c)
                self.grid_layout.addWidget(cell, r, c)
                self.cells[(r, c)] = cell

    def __clear_grid__(self):
        """Clear the entire grid"""


        # Remove all widgets from the layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.cells = {}
        self.subplot_widgets = {}
        self.subplot_labels = {}
        self.subplot_colors = {}
        self.current_color_idx = 0

    def __add_subplot__(self, row, col, row_span, col_span, subplot_id):
        """Add one subplot to the grid."""


        # Get a unique color for this subplot
        color = self.colors[self.current_color_idx % len(self.colors)]
        self.subplot_colors[subplot_id] = color
        self.current_color_idx += 1
        
        # Create a visual representation of the subplot
        subplot_widget = QFrame()
        subplot_widget.setStyleSheet(f"background-color: {color}; border: 2px solid #333333;")
        subplot_widget.setContentsMargins(0, 0, 0, 0)
        
        # Add to layout with proper span
        self.grid_layout.addWidget(subplot_widget, row, col, row_span, col_span)
        self.subplot_widgets[subplot_id] = subplot_widget
        
        # Add label
        label = QLabel(f"Subplot {subplot_id}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("background-color: transparent; font-weight: bold;")
        self.grid_layout.addWidget(label, row, col, row_span, col_span, Qt.AlignmentFlag.AlignCenter)
        self.subplot_labels[subplot_id] = label
        
        # Mark all cells in the span as occupied
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                if (r, c) in self.cells:
                    self.cells[(r, c)].set_occupied(subplot_id, color)
        
        
        return True

    def  __remove_subplot__(self, subplot_id):
        """Remove the subplot from the grid"""


        if subplot_id in self.subplot_widgets:
            # Remove the visual widget
            widget = self.subplot_widgets.pop(subplot_id)
            widget.deleteLater()
            
            # Remove the color reference
            if subplot_id in self.subplot_colors:
                del self.subplot_colors[subplot_id]
            
            if subplot_id in self.subplot_labels:
                label = self.subplot_labels.pop(subplot_id)
                label.deleteLater()

            # Reset cells
            for cell in self.cells.values():
                if cell.subplot_id == subplot_id:
                    cell.occupied = False
                    cell.subplot_id = None
                    cell.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")

    def __update_subplot__(self, subplot_id, row, col, row_span, col_span):
        """Update a subplot's position and size"""

        # First remove the old visualization
        self. __remove_subplot__(subplot_id)
        
        # Then add it back with new parameters
        self.__add_subplot__(row, col, row_span, col_span, subplot_id)

class SubplotEditor(QWidget):
    """
    Main subplot management interface:
    - Grid configuration and visualization
    - Subplot creation/editing tools
    - Data series management
    - Plot generation controls
    """


    def __init__(self, parent=None):
        """Intialize subplotEditor"""

        super().__init__(parent)

        # Current subplot configuration
        self.subplots = []  # [id, row, col, row_span, col_span, data_series, show_grid]
        self.current_plot_id = 0
        self.selected_subplot_id = None
        self.row_col: list[int] = [0, 0]

        # Initialize line color
        self.line_color = "#1f77b4"  # Default matplotlib blue


        # Initialize UI
        self.__initUI__()
        
        
    def __init_GridConfiguration(self, config_layout: QVBoxLayout) -> None:
        # Grid configuration
        grid_group = QGroupBox("Grid Configuration")
        grid_layout = QGridLayout()
        
        grid_layout.addWidget(QLabel("Rows number:"), 0, 0)
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 8)
        self.rows_spin.setValue(1)
        grid_layout.addWidget(self.rows_spin, 0, 1)
        
        grid_layout.addWidget(QLabel("Columns number:"), 0, 2)
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 8)
        self.cols_spin.setValue(1)
        grid_layout.addWidget(self.cols_spin, 0, 3)
        
        self.__create_grid___btn = QPushButton("Create Grid")
        self.__create_grid___btn.clicked.connect(self.__create_grid__)
        grid_layout.addWidget(self.__create_grid___btn, 0, 4)
        
        grid_group.setLayout(grid_layout)
        config_layout.addWidget(grid_group)
        
        # Visual grid display
        self.visual_group = QGroupBox("Subplot Layout")
        visual_layout = QVBoxLayout()
        self.visual_group.setLayout(visual_layout)
        
        self.grid_display = SubplotGrid()
        visual_layout.addWidget(self.grid_display)
        
        config_layout.addWidget(self.visual_group)
    
    def __init_CreationControl__(self, config_layout: QVBoxLayout) -> None:
        # Subplot creation controls
        creation_group = QGroupBox("Create New Subplot")
        position_group = QGroupBox("Choose subplot size and position")
        one_sub_group = QGroupBox("Choose data for subplot")
        
        creation_layout = QGridLayout()
        position_sub_layout = QGridLayout()
        one_sub_layout = QGridLayout()
        
        creation_group.setLayout(creation_layout)
        position_group.setLayout(position_sub_layout)
        one_sub_group.setLayout(one_sub_layout)
        
        position_sub_layout.addWidget(QLabel("Row position:"), 0, 0)
        self.row_spin = QSpinBox()
        self.row_spin.setRange(0, 7)
        position_sub_layout.addWidget(self.row_spin, 0, 1)
        
        position_sub_layout.addWidget(QLabel("Column position:"), 0, 2)
        self.col_spin = QSpinBox()
        self.col_spin.setRange(0, 7)
        position_sub_layout.addWidget(self.col_spin, 0, 3)
        
        position_sub_layout.addWidget(QLabel("Row Span:"), 1, 0)
        self.row_span_spin = QSpinBox()
        self.row_span_spin.setRange(1, 8)
        self.row_span_spin.setValue(1)
        position_sub_layout.addWidget(self.row_span_spin, 1, 1)
        
        position_sub_layout.addWidget(QLabel("Col Span:"), 1, 2)
        self.col_span_spin = QSpinBox()
        self.col_span_spin.setRange(1, 8)
        self.col_span_spin.setValue(1)
        position_sub_layout.addWidget(self.col_span_spin, 1, 3)
        
        one_sub_layout.addWidget(QLabel("Data x:"), 0, 0)
        self.data_combo_x = QComboBox()
        self.data_combo_x.addItems(["None"])
        one_sub_layout.addWidget(self.data_combo_x, 0, 1, 1, 3)
        one_sub_layout.addWidget(QLabel("Data y:"), 1, 0)
        self.data_combo_y = QComboBox()
        self.data_combo_y.addItems(["None"])
        one_sub_layout.addWidget(self.data_combo_y, 1, 1, 1, 3)
        
        self.add_subplot_btn = QPushButton("Add Subplot")
        self.add_subplot_btn.clicked.connect(self.__add_subplot__)
        one_sub_layout.addWidget(self.add_subplot_btn, 2, 0, 1, 2)
        
        self.data_btn = QPushButton("Configure Data Series")
        self.data_btn.clicked.connect(self.configure_data_series)
        creation_layout.addWidget(self.data_btn, 1, 0, 1, 4)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_subplots)
        creation_layout.addWidget(self.clear_btn, 2, 0, 1, 4)
        
        creation_layout.addWidget(position_group, 0, 0, 1, 3)
        creation_layout.addWidget(one_sub_group, 0, 3, 1, 1)
        config_layout.addWidget(creation_group)

    def __init_EditingControl__(self, config_layout: QVBoxLayout) -> None:
        # Subplot editing controls
        self.editor_group = QGroupBox("Edit Selected Subplot")
        self.editor_group.setEnabled(False)
        editor_layout = QVBoxLayout()
        self.editor_group.setLayout(editor_layout)
        # Tab widget for different editing options
        self.editor_tabs = QTabWidget()
        self.__init_position_tab__()
        self.__init_data_tab__()
        self.__init_style_tab__()
        self.__init_subplot_style_tab__()
    
        subplot_to_change_layout = QHBoxLayout()
        self.subplot_spin = QComboBox()
        self.subplot_spin.addItems(["None"])
        self.subplot_spin.currentTextChanged.connect(self.get_sub_id_select)
        
        subplot_to_change_layout.addWidget(QLabel("Subplot to change:"))
        subplot_to_change_layout.addWidget(self.subplot_spin)
        editor_layout.addLayout(subplot_to_change_layout)
        editor_layout.addWidget(self.editor_tabs)
        config_layout.addWidget(self.editor_group)

    def __init_position_tab__(self) -> None:
        # Position tab
        position_tab = QWidget()
        position_layout = QGridLayout(position_tab)

        position_layout.addWidget(QLabel("Row:"), 1, 0)
        self.edit_row_spin = QSpinBox()
        self.edit_row_spin.setRange(0, 7)
        position_layout.addWidget(self.edit_row_spin, 1, 1)
        
        position_layout.addWidget(QLabel("Column:"), 1, 2)
        self.edit_col_spin = QSpinBox()
        self.edit_col_spin.setRange(0, 7)
        position_layout.addWidget(self.edit_col_spin, 1, 3)
        
        position_layout.addWidget(QLabel("Row Span:"), 2, 0)
        self.edit_row_span_spin = QSpinBox()
        self.edit_row_span_spin.setRange(1, 8)
        self.edit_row_span_spin.setValue(1)
        position_layout.addWidget(self.edit_row_span_spin, 2, 1)
        
        position_layout.addWidget(QLabel("Col Span:"), 2, 2)
        self.edit_col_span_spin = QSpinBox()
        self.edit_col_span_spin.setRange(1, 8)
        self.edit_col_span_spin.setValue(1)
        position_layout.addWidget(self.edit_col_span_spin, 2, 3)
        
        self.update_position_btn = QPushButton("Update Position/Size")
        self.update_position_btn.clicked.connect(self.update_subplot_position)
        position_layout.addWidget(self.update_position_btn, 3, 0, 1, 4)
        
        self.editor_tabs.addTab(position_tab, "Position")
    
    def __init_data_tab__(self) -> None:
        # Data tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        self.data_data_spin = QComboBox()
        self.data_data_spin.addItems(["None"])
        data_layout.addWidget(QLabel("Data to change:"))
        data_layout.addWidget(self.data_data_spin)
 
        data_layout.addWidget(QLabel("Data x:"))
        self.edit_data_combo_x = QComboBox()
        self.edit_data_combo_x.addItems(["None"])
        data_layout.addWidget(self.edit_data_combo_x)

        data_layout.addWidget(QLabel("Data y:"))
        self.edit_data_combo_y = QComboBox()
        self.edit_data_combo_y.addItems(["None"])
        data_layout.addWidget(self.edit_data_combo_y)
        
        self.edit_data_btn = QPushButton("Edit Data Series")
        self.edit_data_btn.clicked.connect(self.edit_data_series)
        data_layout.addWidget(self.edit_data_btn)

        self.update_data_btn = QPushButton("Update Data")
        self.update_data_btn.clicked.connect(self.update_subplot_data)
        data_layout.addWidget(self.update_data_btn)
        
        self.editor_tabs.addTab(data_tab, "Data")
    
    def __init_style_tab__(self) -> None:
        """Initialize tab for styling data in subplots."""


        # Styling tab
        style_tab = QWidget()
        style_layout = QFormLayout(style_tab)
        
        self.data_styles_spin = QComboBox()
        self.data_styles_spin.addItems(["None"])
        self.data_styles_spin.currentTextChanged.connect(self.data_styles_changed)
        style_layout.addRow("Data to change:", self.data_styles_spin)
        
        self.line_label = QLineEdit()
        self.line_label.setText("y(x)")
        self.line_label.setPlaceholderText("Enter line label...")
        style_layout.addRow("Line Label:", self.line_label)

        self.line_width_spin = QDoubleSpinBox()
        self.line_width_spin.setMinimum(0)
        # self.line_width_spin.setRange(0.1, 10.0)
        self.line_width_spin.setValue(1.0)
        style_layout.addRow("Line Width:", self.line_width_spin)
        
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
        
        self.line_style_spin = QComboBox()
        self.line_style_spin.addItems(["Nothing", "- (solid)", ": (solid)", "-- (dashed)", "-. (dashdot)"])
        self.line_style_spin.setCurrentIndex(0)
        style_layout.addRow("Line style:", self.line_style_spin)
        
        self.line_transparancy = QDoubleSpinBox()
        self.line_transparancy.setRange(0.0, 1.0)
        self.line_transparancy.setValue(1.0)
        self.line_transparancy.setSingleStep(0.01)
        self.line_transparancy.setDecimals(2)
        style_layout.addRow("Line transparancy:", self.line_transparancy)

        self.dotes_marker_shape = QComboBox()
        self.dotes_marker_shape.addItems(["o", "", ".", ",", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "D", "d", "|", "_"])
        self.dotes_marker_shape.setCurrentIndex(0)
        style_layout.addRow("Marker shape:", self.dotes_marker_shape)

        self.dotes_marker_size = QSpinBox()
        self.dotes_marker_size.setMinimum(0)
        self.dotes_marker_size.setValue(3)
        style_layout.addRow("Marker size:", self.dotes_marker_size)


        self.update_style_btn = QPushButton("Update Data Style")
        self.update_style_btn.clicked.connect(self.__update_data_style__)
        style_layout.addRow(self.update_style_btn)
        
        self.editor_tabs.addTab(style_tab, "Data style")

    def __init_subplot_style_tab__(self) -> None:
        """Initialize UI for subplots styling tab."""

        #prapare tab
        sub_style_tab = QWidget()
        sub_style_layout = QVBoxLayout(sub_style_tab)
        self.editor_tabs.addTab(sub_style_tab, "Sublot style")

        self.settings_tree = QTreeWidget()
        self.settings_tree.setHeaderLabels(["Parameters", "Values"])
        self.settings_tree.setAlternatingRowColors(True)
        #create all tab widgets
        #axis settings
        self.__add_axes_group__()

        #subplot settings
        self.__add_subplot_main_settings_group()

        sub_style_layout.addWidget(self.settings_tree)

        self.update_sub_style_btn = QPushButton("Update Subplot Style")
        self.update_sub_style_btn.clicked.connect(self.__update_sub_style__)
        sub_style_layout.addWidget(self.update_sub_style_btn)

    def __add_axes_group__(self):
        """Add a tree group for axes settings."""
        group_main = QTreeWidgetItem(self.settings_tree, ["Axes"])
        group_x = QTreeWidgetItem(group_main, ["X axis"])
        group_y = QTreeWidgetItem(group_main, ["Y axis"])

        params = [
            ("X Axis Title", "text", "X"),
            ("X labels font size", "int", 14, 0),
            ("X Min", "float", 0.0),
            ("X Max", "float", 1.0),
            ("X ticks number", "int", 1, 0),
            ("X small ticks number", "int", 1, 0),
            ("X number of accuracy", "int", 1, 0),
            ("X scale", "combo", "Linear", ["Linear", "Logarithmic"]),

            ("Y Axis Title", "text", "Y"),
            ("Y labels font size", "int", 14, 0),
            ("Y Min", "float", 0.0),
            ("Y Max", "float", 1.0),
            ("Y ticks number", "int", 1, 0),
            ("Y small ticks number", "int", 1, 0),
            ("Y number of accuracy", "int", 1, 0),
            ("Y scale", "combo", "Linear", ["Linear", "Logarithmic"]),            
        ]

        self.x_title = None
        self.x_min = None
        self.x_max = None
        self.x_ticks = None
        self.x_small_ticks = None
        self.x_labels_fs = None
        self.x_scale = None
        self.x_number_of_ac = None

        self.y_title = None
        self.y_min = None
        self.y_max = None
        self.y_ticks = None
        self.y_small_ticks = None
        self.y_labels_fs = None
        self.y_scale = None
        self.y_number_of_ac = None

        for name, ptype, default, *args in params:
            if name[0] == "X":
                editor = self.__add_parameter__(group_x, name, ptype, default, *args)
            else:
                editor = self.__add_parameter__(group_y, name, ptype, default, *args)

            # Save references to important editors
            if name == "X Axis Title":
                self.x_title: QLineEdit = editor
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
            elif name == "X labels font size":
                self.x_labels_fs: QSpinBox = editor
            elif name == "X scale":
                self.x_scale: QComboBox = editor
                self.x_scale.currentTextChanged.connect(self.update_some_axes_states)
            elif name == "X number of accuracy":
                self.x_number_of_ac: QSpinBox = editor
            elif name == "Y Axis Title":
                self.y_title: QLineEdit = editor
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
            elif name == "Y labels font size":
                self.y_labels_fs: QSpinBox = editor
            elif name == "Y scale":
                self.y_scale: QComboBox = editor
                self.y_scale.currentTextChanged.connect(self.update_some_axes_states)
            elif name == "Y number of accuracy":
                self.y_number_of_ac: QSpinBox = editor

    def __add_subplot_main_settings_group(self) -> None:
        """Add main settings for subplot group."""


        group: QTreeWidgetItem = QTreeWidgetItem(self.settings_tree, ["Subplot main settings"])
        title_group: QTreeWidgetItem = QTreeWidgetItem(group, ["Title"])
        legend_group: QTreeWidgetItem = QTreeWidgetItem(group, ["Legend"])

        params = [
            ("Subplot Title", "text", "a"),
            ("Subplot title font size", "int", 14, 0),
            ("Legend position", "combo", "best", ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center']),
            ("Legend font size", "int", 14, 0)
        ]

        self.subplot_title = None
        self.subplot_title_fs = None
        self.legend_position = None
        self.legend_fs = None

        for name, ptype, default, *args in params[:2]:
            editor = self.__add_parameter__(title_group, name, ptype, default, *args)
            if name == "Subplot Title":
                self.subplot_title: QLineEdit = editor
            elif name == "Subplot title font size":
                self.subplot_title_fs: QSpinBox = editor

        for name, ptype, default, *args in params[2:]:
            editor = self.__add_parameter__(legend_group, name, ptype, default, *args)
            if name == "Legend position":
                self.legend_position: QComboBox = editor
            elif name == "Legend font size":
                self.legend_fs: QSpinBox = editor

        #grid preset
        grid_group:QTreeWidgetItem = QTreeWidgetItem(group, ["Grid"])
        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        self.settings_tree.setItemWidget(grid_group, 1, self.grid_checkbox)

    def validate_x_limits(self) -> None:
        """Ensure X Min < X Max"""


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
        """Ensure Y Min < Y Max"""


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

    def highlight_invalid(self, editor):
        """Highlight editor with red border to indicate invalid value"""


        if isinstance(editor, (QDoubleSpinBox, QSpinBox)):
            editor.setStyleSheet("border: 1px solid red;")
        elif isinstance(editor, QLineEdit):
            editor.setStyleSheet("QLineEdit { border: 1px solid red; }")

    def reset_highlight(self, editor):
        """Reset editor's style to default"""


        if isinstance(editor, (QDoubleSpinBox, QSpinBox)):
            editor.setStyleSheet("")
        elif isinstance(editor, QLineEdit):
            editor.setStyleSheet("QLineEdit { border: none; }")

    def update_some_axes_states(self) -> None:
        """Change tates of some axis parameters if axis scaling is changed."""
    
    def __add_parameter__(self, parent, name, ptype, default, *args):
        """Add a parameter to the group and return the editor widget"""


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
    
    def __initUI__(self):
        """Initialize UI for subplot Editor window"""

        #main layout      
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # Create a splitter for resizable panels
        splitter = QSplitter()
        main_layout.addWidget(splitter)
        
        # Left panel for configuration
        config_panel = QWidget()
        config_layout = QVBoxLayout()
        config_panel.setLayout(config_layout)
        
        #init Grid Configuration
        self.__init_GridConfiguration(config_layout=config_layout)

        #init CreationControl
        self.__init_CreationControl__(config_layout=config_layout)
        
        # Subplot editing controls (different tabs)
        self.__init_EditingControl__(config_layout=config_layout)

        
        # Plot button
        self.plot_btn = QPushButton("Generate Plot")
        self.plot_btn.clicked.connect(self.plot_graphs)
        config_layout.addWidget(self.plot_btn)
        
        # Right panel for plotting
        plot_panel = QWidget()
        plot_layout = QVBoxLayout()
        plot_panel.setLayout(plot_layout)
        
        
        # Subplot list
        self.subplot_list = QListWidget()
        self.subplot_list.setMaximumHeight(150)
        self.subplot_list.itemSelectionChanged.connect(self.subplot_selected)
        plot_layout.addWidget(self.subplot_list)
        
        # Matplotlib figure
        self.plot_canvas = INTERACTIVE_PLOT()
        self.plot_canvas.subplots = []
        # self.figure = Figure(figsize=(10, 8), dpi=100)
        plot_layout.addWidget(self.plot_canvas.canvas)
        
        # Set initial splitter sizes
        splitter.addWidget(plot_panel)
        splitter.addWidget(config_panel)
        # splitter.setSizes([500, 1100])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
    
    def update_column_data(self, headers: list[str]) -> None:
        "updates all combo boxes that contain headers from the table"
        self.data_combo_x.clear()
        self.data_combo_x.addItems(["None"] + headers)
        self.data_combo_y.clear()
        self.data_combo_y.addItems(["None"] + headers)
        self.edit_data_combo_x.clear()
        self.edit_data_combo_x.addItems(["None"] + headers)
        self.edit_data_combo_y.clear()
        self.edit_data_combo_y.addItems(["None"] + headers)

    def __create_grid__(self):
        """Create a new grid based on row/column configuration"""

        #get entered row/col value
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        # Store current subplots before clearing
        
        current_subplots = self.plot_canvas.subplots[:]
        self.grid_display.__create_grid__(rows, cols)
        self.plot_canvas.subplots = []
        self.current_plot_id = 0
        
        # Try to re-add subplots that fit in the new grid
        non_fitting_subplots = []
        for subplot in current_subplots:
            plot_id, row, col, row_span, col_span, data_series, axes_info, title_info, legend_info = subplot
            if (row + row_span <= rows and col + col_span <= cols):
                # Subplot fits in new grid, re-add it
                self.grid_display.__add_subplot__(row, col, row_span, col_span, plot_id)
                self.plot_canvas.subplots.append([
                    plot_id,
                    row,
                    col,
                    row_span,
                    col_span,
                    data_series,
                    axes_info,
                    title_info,
                    legend_info
                ])
                # Update current plot ID to avoid conflicts
                if plot_id >= self.current_plot_id:
                    self.current_plot_id = plot_id + 1
            else:
                non_fitting_subplots.append(subplot)

        # Handle subplots that don't fit
        if non_fitting_subplots:
            self.__handle_non_fitting_subplots__(non_fitting_subplots=non_fitting_subplots, current_subplots=current_subplots)

        self.update_subplot_list()
        self.clear_selection()

    def __handle_non_fitting_subplots__(self, non_fitting_subplots: list, current_subplots: list) -> None:
        """Handle subplots that don't fit after grid resizing."""

        #make and configure MessageBox
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Subplots Don't Fit")
        msg_box.setText(f"Subplots with id " + ", ".join([str(subplot[0]) for subplot in non_fitting_subplots]) + f" {'do not' if len(non_fitting_subplots) else 'does not'} fit in the new grid.")
        msg_box.setInformativeText("What would you like to do? (You can delete one of the sublots but adjusting others by clicking \"Adjust Positions\" -> \"Cancel\")")
        
        #options for user
        adjust_button = msg_box.addButton("Adjust Positions", QMessageBox.ButtonRole.YesRole)
        delete_button = msg_box.addButton("Delete Them", QMessageBox.ButtonRole.NoRole)
        cancel_button = msg_box.addButton("Cancel Resize", QMessageBox.ButtonRole.RejectRole)
        
        #wait until one of the options clicked
        msg_box.exec()
        
        clicked = msg_box.clickedButton()
        
        if clicked == cancel_button:
            # Revert to previous grid size
            self.grid_display.__create_grid__(self.row_col[0] if self.row_col[0] else 1, 
                                        self.row_col[1] if self.row_col[1] else 1)
            # Re-add all original subplots
            self.plot_canvas.subplots = []
            for subplot in current_subplots:
                pid, r, c, rs, cs, *other = subplot
                self.grid_display.__add_subplot__(r, c, rs, cs, pid)
                self.plot_canvas.subplots.append(subplot)
            self.update_subplot_list()
            self.clear_selection()
            return
        elif clicked == delete_button:
            # Simply don't re-add these subplots
            self.row_col = [rows, cols]
            pass
        elif clicked == adjust_button:
            # Try to adjust each non-fitting subplot
            rows = self.rows_spin.value()
            cols = self.cols_spin.value()
            for subplot in non_fitting_subplots[:]:  # Use a copy since we may modify the list
                plot_id, row, col, row_span, col_span, data_series, axes_info, title_info, legend_info = subplot
                result = self.__change_sub_pos__(
                    base_info=[row, col, row_span, col_span, plot_id],
                    subs=self.plot_canvas.subplots,
                    max_row=rows,
                    max_col=cols
                )
                if result:
                    new_row, new_row_span, new_col, new_col_span = result
                    # Check if adjusted subplot now fits
                    if new_row + new_row_span <= rows and new_col + new_col_span <= cols:
                        self.grid_display.__add_subplot__(new_row, new_col, new_row_span, new_col_span, plot_id)
                        self.plot_canvas.subplots.append([
                            plot_id,
                            new_row,
                            new_col,
                            new_row_span,
                            new_col_span,
                            data_series,
                            axes_info,
                            title_info,
                            legend_info
                        ])
                        non_fitting_subplots.remove(subplot)
                    else:
                        # Still doesn't fit after adjustment
                        QMessageBox.warning(self, "Still Doesn't Fit", 
                                            f"Subplot {plot_id} still doesn't fit after adjustment")
                else:
                    # User canceled adjustment
                    pass
                self.row_col = [rows, cols]


    def __change_sub_pos__(self, base_info, subs, max_row, max_col):
        input_pos_dialog = SubplotPositionDialog(base_info, subs, max_row, max_col)
        if input_pos_dialog.exec() == QDialog.DialogCode.Accepted:
                return input_pos_dialog.get_data()
        return None
    
    def __add_subplot__(self):
        """Add a new subplot to the configuration"""


        row = self.row_spin.value()
        col = self.col_spin.value()
        row_span = self.row_span_spin.value()
        col_span = self.col_span_spin.value()
        
        # Check if subplot fits in grid
        max_rows = self.rows_spin.value()
        max_cols = self.cols_spin.value()
        
        if row + row_span > max_rows:
            QMessageBox.warning(self, "Invalid Position", 
                                f"Row span exceeds grid height (max row: {max_rows-1})")
            return
            
        if col + col_span > max_cols:
            QMessageBox.warning(self, "Invalid Position", 
                                f"Column span exceeds grid width (max col: {max_cols-1})")
            return
            
        # Check for overlaps
        for subplot in self.plot_canvas.subplots:
            s_row, s_col, s_row_span, s_col_span, *_ = subplot[1:8]
            
            # Check if rectangles overlap
            if self.rectangles_overlap(
                (row, col, row_span, col_span),
                (s_row, s_col, s_row_span, s_col_span)
            ):
                QMessageBox.warning(self, "Overlap Detected", 
                                    "This subplot overlaps with an existing one")

                return
        data_series = [{
            "id": 0,
            "x":self.data_combo_x.currentText(),
            "y":self.data_combo_y.currentText(),
            "color":self.line_color, 
            "width":1.0,
            "label": f"{self.data_combo_y.currentText()}({self.data_combo_x.currentText()})",
            "ls": "",
            "alpha": 1.0,
            "marker": "o",
            "marker size": 3
        }]
        # Add subplot
        plot_id = self.current_plot_id
        self.plot_canvas.subplots.append([
            plot_id,
            row,
            col,
            row_span,
            col_span,
            data_series,
            {"x-label":self.data_combo_x.currentText(),
             "x min": 0,
             "x max": 1,
             "x ticks": 10,
             "x small ticks": 5,
             "x label fs": 14,
             "x scale": 0,
             "x number of accuracy": 1,
             "y-label":self.data_combo_y.currentText(),
             "y min": 0,
             "y max": 1,
             "y ticks": 10,
             "y small ticks": 5,
             "y label fs": 14,
             "y scale": 0,
             "y number of accuracy": 1,
             "show grid": True},
             {"title": "a",
             "title fs": 14},
             {"legend position": "best",
              "legend fs": 14}
        ])
        self.current_plot_id += 1
        
        # Update visual display
        self.grid_display.__add_subplot__(row, col, row_span, col_span, plot_id)
        self.update_subplot_list()
        
        #update subplot lists
        self.subplot_spin.clear()
        self.subplot_spin.addItems(["Subplot " + str(sub[0]) for sub in self.plot_canvas.subplots[:] ])
        # Select the new subplot
        self.select_subplot(plot_id)
    
    def get_sub_id_select(self):
        if self.subplot_spin.currentText().split():
            sub_id = int(self.subplot_spin.currentText().split()[-1])
            self.select_subplot(sub_id)

    def rectangles_overlap(self, rect1, rect2):
        """Check if two rectangles overlap"""
        r1_row, r1_col, r1_row_span, r1_col_span = rect1
        r2_row, r2_col, r2_row_span, r2_col_span = rect2
        
        return not (r1_col + r1_col_span <= r2_col or 
                   r1_col >= r2_col + r2_col_span or 
                   r1_row + r1_row_span <= r2_row or 
                   r1_row >= r2_row + r2_row_span)
    
    def clear_subplots(self):
        """Clear all subplots"""
        self.plot_canvas.subplots = []
        self.plot_canvas.fig.clear()
        self.plot_canvas.canvas.draw()
        self.current_plot_id = 0
        self.grid_display.__clear_grid__()
        self.__create_grid__()
        self.clear_selection()
    
    def update_subplot_list(self):
        """Update the subplot list widget"""
        self.subplot_list.clear()
        for subplot in self.plot_canvas.subplots:
            plot_id, row, col, row_span, col_span, data_series, *_ = subplot
            data_info = ""
            for data in data_series:
                data_info += f"\n{data['y']}({data['x']}) - index {data['id']}, line color - {data['color']}, line width - {data['width']}"
            item = QListWidgetItem(f"Subplot {plot_id}: {row},{col} [{row_span}x{col_span}] - " + data_info)
            item.setData(Qt.ItemDataRole.UserRole, plot_id)
            self.subplot_list.addItem(item)
    
    def subplot_selected(self):
        """Handle subplot selection from the list"""
        selected_items = self.subplot_list.selectedItems()
        if selected_items:
            plot_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.select_subplot(plot_id)
        else:
            self.clear_selection()
    
    def select_subplot(self, plot_id):
        """Select a subplot and load its properties into the editor"""
        self.selected_subplot_id = plot_id
        self.editor_group.setEnabled(True)
        

        self.subplot_spin.setCurrentIndex(plot_id)

        # Find the subplot
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == plot_id:
                # Populate position controls
                _, row, col, row_span, col_span, data_series, axes_info, title_info, legend_info = subplot
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
                
                # Populate style controls
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
                #populate subplot control
                #Axes
                #x axis
                self.x_title.setText(axes_info["x-label"])
                self.x_labels_fs.setValue(axes_info["x label fs"])
                self.x_min.setValue(0)
                self.x_max.setValue(10)
                self.x_ticks.setValue(axes_info["x ticks"])
                self.x_small_ticks.setValue(axes_info["x small ticks"])
                self.x_scale.setCurrentIndex(axes_info["x scale"])
                self.x_number_of_ac.setValue(axes_info["x number of accuracy"])

                #y axis
                self.y_title.setText(axes_info["y-label"])
                self.y_labels_fs.setValue(axes_info["y label fs"])
                self.y_min.setValue(0)
                self.y_max.setValue(10)
                self.y_ticks.setValue(axes_info["y ticks"])
                self.y_small_ticks.setValue(axes_info["y small ticks"])
                self.y_scale.setCurrentIndex(axes_info["y scale"])
                self.y_number_of_ac.setValue(axes_info["y number of accuracy"])
                
                #Subplot main settings
                #Title
                self.subplot_title.setText(title_info["title"])
                self.subplot_title_fs.setValue(title_info["title fs"])

                #Legend
                self.legend_position.setCurrentText(legend_info["legend position"])
                self.legend_fs.setValue(legend_info["legend fs"])
                
                #grid   
                self.grid_checkbox.setChecked(axes_info["show grid"])

                break

    def __update_data_headers_spin__(self, data_series) -> None:
        """updates all lists with data sets from subplot"""

        index = self.data_data_spin.currentIndex()
        self.data_data_spin.clear()
        self.data_data_spin.addItems([f"{data['y']}({data['x']}) - {data['id']}" for data in data_series])
        self.data_data_spin.setCurrentIndex(index)
        self.data_styles_spin.clear()
        self.data_styles_spin.addItems([f"{data['y']}({data['x']}) - {data['id']}" for data in data_series])
        self.data_styles_spin.setCurrentIndex(index)
        self.line_label.setText(f"{data_series[index]['y']}({data_series[index]['x']})")


    def clear_selection(self):
        """Clear the current selection"""
        self.selected_subplot_id = None
        self.subplot_list.clearSelection()
        self.editor_group.setEnabled(False)
        self.edit_row_spin.setValue(0)
        self.edit_col_spin.setValue(0)
        self.edit_row_span_spin.setValue(1)
        self.edit_col_span_spin.setValue(1)
        self.edit_data_combo_x.setCurrentIndex(0)
        self.edit_data_combo_y.setCurrentIndex(0)

        self.line_width_spin.setValue(1.0)
        self.grid_checkbox.setChecked(True)
        self.line_color = "#1f77b4"
        self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 1px solid #888; border-radius: 3px;")
        self.color_preview.setProperty("color", self.line_color)
        self.line_style_spin.setCurrentText("Nothing")
        self.line_transparancy.setValue(1.0)
        self.dotes_marker_shape.setCurrentText('o')
        self.dotes_marker_size.setValue(3)

    def update_subplot_position(self):
        """Update the position and size of a subplot"""
        if self.selected_subplot_id is None:
            return
            
        new_row = self.edit_row_spin.value()
        new_col = self.edit_col_spin.value()
        new_row_span = self.edit_row_span_spin.value()
        new_col_span = self.edit_col_span_spin.value()
        
        # Check if subplot fits in grid
        max_rows = self.rows_spin.value()
        max_cols = self.cols_spin.value()
        
        if new_row + new_row_span > max_rows:
            reply = QMessageBox.question(self, "Invalid Position", f"Row span exceeds grid height (max row: {max_rows-1})" + "Do you want to change row span of your subplot?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                result= self.__change_sub_pos__(base_info=[new_row, new_col, new_row_span, new_col_span, self.selected_subplot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                if result is None:
                    return
                else:
                    new_row, new_row_span, new_col, new_col_span = result
        if new_col + new_col_span > max_cols:
            reply = QMessageBox.question(self, "Invalid Position", f"Column span exceeds grid width (max col: {max_cols-1})" + "Do you want to change column span of your subplot?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                result = self.__change_sub_pos__(base_info=[new_row, new_col, new_row_span, new_col_span, self.selected_subplot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                if result is None:
                    return
                else:
                    new_row, new_row_span, new_col, new_col_span = result
            
        # Check for overlaps with other subplots
        for subplot in self.plot_canvas.subplots:
            s_id, s_row, s_col, s_row_span, s_col_span, *_ = subplot
            if s_id == self.selected_subplot_id:
                continue
                
            if self.rectangles_overlap(
                (new_row, new_col, new_row_span, new_col_span),
                (s_row, s_col, s_row_span, s_col_span)
            ):
                reply = QMessageBox.question(self, "Overlap Detected", "This subplot overlaps with an existing one. \n Do you want to change position of the subplot that you are adding?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    result = self.__change_sub_pos__(base_info=[new_row, new_col, new_row_span, new_col_span, self.selected_subplot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                    if result is None:
                        return
                    else:
                        new_row, new_row_span, new_col, new_col_span = result
        
        # Update the subplot
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                self.plot_canvas.subplots[i][1] = new_row
                self.plot_canvas.subplots[i][2] = new_col
                self.plot_canvas.subplots[i][3] = new_row_span
                self.plot_canvas.subplots[i][4] = new_col_span
                
                # Update visual display
                self.grid_display.__update_subplot__(
                    self.selected_subplot_id, 
                    new_row, new_col, new_row_span, new_col_span
                )
                break
        
        self.update_subplot_list()
    
    def update_subplot_data(self):
        """Update the data for a subplot"""
        if self.selected_subplot_id is None:
            return
            
        new_data_x = self.edit_data_combo_x.currentText()
        new_data_y = self.edit_data_combo_y.currentText()
        
        # Update the subplot
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                for counter in range(len(self.plot_canvas.subplots[i][5])):
                    data = self.plot_canvas.subplots[i][5][counter]
                    if str(data['id']) == self.data_data_spin.currentText().split('-')[-1].lstrip().rstrip():
                        self.plot_canvas.subplots[i][5][counter]["x"] = new_data_x
                        self.plot_canvas.subplots[i][5][counter]["y"] = new_data_y
                if self.selected_subplot_id < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                    
                self.__update_data_headers_spin__(self.plot_canvas.subplots[i][5])
                break
            
        self.update_subplot_list()
    
    def choose_line_color(self):
        """Open color dialog to choose line color"""
        color = QColorDialog.getColor(initial=QColor(self.line_color))
        if color.isValid():
            self.line_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 0px solid #888; border-radius: 3px;")
            self.color_preview.setProperty("color", self.line_color)
    
    def __update_sub_style__(self):
        """Update  style properties for the subplot"""

        if self.selected_subplot_id is None:
            return
        
        #read all data
        x_label: str = self.x_title.text()
        x_min:float = self.x_min.value()
        x_max: float = self.x_max.value()
        x_ticks: int = self.x_ticks.value()
        x_small_ticks: int = self.x_small_ticks.value()
        x_label_fs: int = self.x_labels_fs.value()
        x_scale: int = self.x_scale.currentIndex() #0 - linear, 1 - log
        x_number_of_accuracy: int = self.x_number_of_ac.value()

        y_label: str = self.y_title.text()
        y_min = self.y_min.value()
        y_max = self.y_max.value()
        y_ticks: int = self.y_ticks.value()
        y_small_ticks: int = self.y_small_ticks.value()
        y_label_fs: int = self.y_labels_fs.value()
        y_scale: int = self.y_scale.currentIndex()
        y_number_of_accuracy: int = self.y_number_of_ac.value()

        #title
        title: str = self.subplot_title.text()
        title_fs: int = self.subplot_title_fs.value()

        #legend
        legend_pos: str = self.legend_position.currentText()
        legend_fs: int = self.legend_fs.value()

        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                self.plot_canvas.subplots[i][6]["x-label"] = x_label
                self.plot_canvas.subplots[i][6]["x min"] = x_min
                self.plot_canvas.subplots[i][6]["x max"] = x_max
                self.plot_canvas.subplots[i][6]["x ticks"] = x_ticks
                self.plot_canvas.subplots[i][6]["x small ticks"] = x_small_ticks
                self.plot_canvas.subplots[i][6]["x label fs"] = x_label_fs
                self.plot_canvas.subplots[i][6]["x scale"] = x_scale
                self.plot_canvas.subplots[i][6]["x number of accuracy"] = x_number_of_accuracy

                self.plot_canvas.subplots[i][6]["y-label"] = y_label
                self.plot_canvas.subplots[i][6]["y min"] = y_min
                self.plot_canvas.subplots[i][6]["y max"] = y_max
                self.plot_canvas.subplots[i][6]["y ticks"] = y_ticks
                self.plot_canvas.subplots[i][6]["y small ticks"] = y_small_ticks
                self.plot_canvas.subplots[i][6]["y label fs"] = y_label_fs
                self.plot_canvas.subplots[i][6]["y scale"] = y_scale
                self.plot_canvas.subplots[i][6]["y number of accuracy"] = y_number_of_accuracy

                self.plot_canvas.subplots[i][7]["title"] = title
                self.plot_canvas.subplots[i][7]["title fs"] = title_fs

                self.plot_canvas.subplots[i][8]["legend position"] = legend_pos
                self.plot_canvas.subplots[i][8]["legend fs"] = legend_fs

                if self.selected_subplot_id < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                self.update_subplot_list()
                break

    def __update_data_style__(self):
        """Update style properties for the subplot data"""
        if self.selected_subplot_id is None:
            return
            
        new_color = self.line_color
        new_width = self.line_width_spin.value()
        new_grid = self.grid_checkbox.isChecked()
        new_label = self.line_label.text()
        new_ls = self.line_style_spin.currentText().split()[0]
        new_alpha = self.line_transparancy.value()
        new_marker = self.dotes_marker_shape.currentText()
        new_marker_size = self.dotes_marker_size.value()

        if new_ls == "Nothing":
            new_ls = ""
        # Update the subplot
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                for counter in range(len(self.plot_canvas.subplots[i][5])):
                    data = self.plot_canvas.subplots[i][5][counter]
                    if str(data['id']) == self.data_styles_spin.currentText().split('-')[-1].lstrip().rstrip():
                        self.plot_canvas.subplots[i][5][counter]["color"] = new_color
                        self.plot_canvas.subplots[i][5][counter]["width"] = new_width
                        self.plot_canvas.subplots[i][5][counter]["label"] = new_label
                        self.plot_canvas.subplots[i][5][counter]["ls"] = new_ls
                        self.plot_canvas.subplots[i][5][counter]["alpha"] = new_alpha
                        self.plot_canvas.subplots[i][5][counter]["marker"] = new_marker
                        self.plot_canvas.subplots[i][5][counter]["marker size"] = new_marker_size

                self.plot_canvas.subplots[i][6]["show grid"] = new_grid
                
                if self.selected_subplot_id < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                break
        self.update_subplot_list()
    
    # Updated plot_graphs method in the SubplotEditor class
    def plot_graphs(self):
        self.plot_canvas.canvas.draw()
        self.plot_canvas.plot_all_data(self.window(),  self.rows_spin.value(), self.cols_spin.value())
        
    def configure_data_series(self):
        headers = self.window().get_headers() 
        dialog = DataSeriesDialog(headers=headers, parent=self, max_id=0)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.get_series() != []:
                self.add_data_series_subplot(dialog.get_series(), dialog.get_axes_info(), dialog.get_title_info())

    def add_data_series_subplot(self, series, axes_info, title_info):
        """Add a new subplot to the configuration"""
        row = self.row_spin.value()
        col = self.col_spin.value()
        row_span = self.row_span_spin.value()
        col_span = self.col_span_spin.value()
        
        # Check if subplot fits in grid
        max_rows = self.rows_spin.value()
        max_cols = self.cols_spin.value()
        
        if row + row_span > max_rows:
            reply = QMessageBox.question(self, "Invalid Position", f"Row span exceeds grid height (max row: {max_rows-1})" + "Do you want to change row span of your subplot?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                result= self.__change_sub_pos__(base_info=[row, col, row_span, col_span, self.current_plot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                if result is None:
                    return
                else:
                    row, row_span, col, col_span = result          
        if col + col_span > max_cols:
            reply = QMessageBox.question(self, "Invalid Position", f"Column span exceeds grid width (max col: {max_cols-1})" + "Do you want to change column span of your subplot?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                result = self.__change_sub_pos__(base_info=[row, col, row_span, col_span, self.current_plot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                if result is None:
                    return
                else:
                    row, row_span, col, col_span = result
            
        # Check for overlaps
        for subplot in self.plot_canvas.subplots:
            s_row, s_col, s_row_span, s_col_span, *_ = subplot[1:8]
            
            # Check if rectangles overlap
            if self.rectangles_overlap(
                (row, col, row_span, col_span),
                (s_row, s_col, s_row_span, s_col_span)
            ):
                reply = QMessageBox.question(self, "Overlap Detected", "This subplot overlaps with an existing one. \n Do you want to change position of the subplot that you are adding?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    result = self.__change_sub_pos__(base_info=[row, col, row_span, col_span, self.current_plot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                    if result is None:
                        return
                    else:
                        row, row_span, col, col_span = result
 
        plot_id = self.current_plot_id
        self.plot_canvas.subplots.append([
            plot_id,
            row,
            col,
            row_span,
            col_span,
            series,
            axes_info,
            title_info,
            {"legend position": "best", "legend fs": 14}
        ])
        self.current_plot_id += 1
        
        # Update visual display
        self.grid_display.__add_subplot__(row, col, row_span, col_span, plot_id)
        self.update_subplot_list()
        
        #update subplot lists
        self.subplot_spin.clear()
        self.subplot_spin.addItems(["Subplot " + str(sub[0]) for sub in self.plot_canvas.subplots[:] ])

        # Select the new subplot
        self.select_subplot(plot_id)
        

    def edit_data_series(self):
        if self.selected_subplot_id == None:
            return
        
        # Find current series
        subplot = next((s for s in self.plot_canvas.subplots if s[0] == self.selected_subplot_id), None)
        if not subplot: return     
        headers = self.window().get_headers()
        series = [subs[5] for subs in self.plot_canvas.subplots if subs[0] == self.selected_subplot_id][0] 
        cur_id = np.max([ser["id"] for ser in series])

        dialog = DataSeriesDialog(headers=headers, parent=self, max_id=cur_id+1)
        dialog.series = subplot[5][:]  # Copy existing series
        for series in dialog.series:
            dialog.series_list.addItem(f"{series['x']} vs {series['y']}")
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            subplot[5] = dialog.get_series()
            self.update_subplot_list()
            if self.selected_subplot_id < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()

    def data_styles_changed(self) -> None:
        if not self.data_styles_spin.currentText():
            return
        self.line_label.setText(self.data_styles_spin.currentText().split('-')[0][:-1])
        data_id = int(self.data_styles_spin.currentText().split('-')[1])
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == self.selected_subplot_id:
                _, row, col, row_span, col_span, data_series, *other_info = subplot
                for series in data_series:
                    if series['id'] == data_id:
                        self.line_color = series["color"]
                        self.line_width_spin.setValue(series["width"])
                        self.color_preview.setStyleSheet(f"background-color: {self.line_color}; border: 1px solid #888; border-radius: 3px;")
                        self.color_preview.setProperty("color", self.line_color)
                        self.line_style_spin.setCurrentText(series["ls"])
                        self.line_transparancy.setValue(series["alpha"])
                        self.dotes_marker_shape.setCurrentText(series["marker"])
                        self.dotes_marker_size.setValue(series["marker size"])

    #def __combo_box_changed
