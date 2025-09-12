"""
Manages all plotting operations including:
- Data preparation for plotting
- Subplot configuration
- Plot generation
- Axis configuration
"""


from PyQt6.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel, QHBoxLayout,
                             QSplitter, QVBoxLayout, QSpinBox, QGroupBox, QPushButton,
                             QComboBox, QTabWidget, QListWidget, QDialog, QMessageBox,
                             QListWidgetItem, QTableWidgetItem)
from PyQt6.QtGui import QColor
from interactive_plot import INTERACTIVE_PLOT
from dialogs import SubplotPositionDialog, DataSeriesDialog
from subplotsEditors import SubplotStyleTab, DataStyleTab, LineStyleTab, PositioningChoosingDataTab
from PyQt6.QtCore import Qt
import numpy as np

##Constants
Minimum_Height: int = 100


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


    def __init__(self, parent=None) -> None:
        """
        Initialize grid
        """


        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.setLayout(self.grid_layout)
        self.cells: dict = {}
        self.subplot_widgets: dict = {}
        self.subplot_labels: dict = {}
        self.subplot_colors: dict = {}
        self.current_color_idx: int = 0
        self.colors: list[str] = [
            "#FFCCCC", "#CCFFCC", "#CCCCFF", "#FFFFCC", "#FFCCFF", "#CCFFFF",
            "#FFDDAA", "#DDFFAA", "#DDAADD", "#AADDAA", "#AADDFF", "#FFAADD"
        ]
        self.rows: int = 0
        self.cols: int = 0

    def __create_grid__(self, rows: int, cols: int) -> None:
        """Create grid that visualize subplots position."""


        # Clear existing grid
        self.__clear_grid__()
        
        # Create new grid
        self.rows = rows
        self.cols = cols
        for r in range(rows):
            for c in range(cols):
                cell = SubplotCell(r, c)
                self.grid_layout.addWidget(cell, r, c)
                self.cells[(r, c)] = cell

    def __clear_grid__(self) -> None:
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

    def __add_subplot__(self, row: int, col: int, row_span: int, col_span: int, subplot_id: int) -> bool:
        """Add one subplot to the grid."""


        # Get a unique color for this subplot
        color = self.colors[self.current_color_idx % len(self.colors)]
        self.subplot_colors[subplot_id] = color
        self.current_color_idx += 1
        
        # Create a visual representation of the subplot
        subplot_widget: QFrame = QFrame()
        subplot_widget.setStyleSheet(f"background-color: {color}; border: 2px solid #333333;")
        subplot_widget.setContentsMargins(0, 0, 0, 0)
        
        # Add to layout with proper span
        self.grid_layout.addWidget(subplot_widget, row, col, row_span, col_span)
        self.subplot_widgets[subplot_id] = subplot_widget
        
        # Add label
        label: QLabel = QLabel(f"Subplot {subplot_id}")
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

    def  __remove_subplot__(self, subplot_id: int) -> None:
        """Remove the subplot from the grid."""


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

    def __update_subplot__(self, subplot_id: int, row: int, col: int, row_span: int, col_span: int) -> None:
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

    def __init__(self, parent=None) -> None:
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
        """Initialize form for grid configuraion."""


        grid_group: QGroupBox = QGroupBox("Subplots Configuration")
        grid_group.setToolTip("Here you can create grid to place your subplots \n(Choose size of the grid and click \"Cretae grid\")\n"
                              "If you add some subplots and want to change grid size, \nfor all subplots, that don't fit new sizes, question where\n to place them or delete will appear.")
        grid_layout: QGridLayout = QGridLayout()
        
        grid_layout.addWidget(QLabel("Rows number:"), 0, 0)
        self.rows_spin: QSpinBox = QSpinBox()
        self.rows_spin.setRange(1, 8)
        self.rows_spin.setValue(1)
        grid_layout.addWidget(self.rows_spin, 0, 1)
        
        grid_layout.addWidget(QLabel("Columns number:"), 0, 2)
        self.cols_spin: QSpinBox = QSpinBox()
        self.cols_spin.setRange(1, 8)
        self.cols_spin.setValue(1)
        grid_layout.addWidget(self.cols_spin, 0, 3)
        
        self.create_grid_btn: QPushButton = QPushButton("Create Grid")
        self.create_grid_btn.clicked.connect(self.__create_grid__)
        grid_layout.addWidget(self.create_grid_btn, 0, 4)
        
        grid_group.setLayout(grid_layout)
        config_layout.addWidget(grid_group)
        
        # Visual grid display
        self.visual_group: QGroupBox = QGroupBox("Subplot Layout")
        visual_layout: QVBoxLayout = QVBoxLayout()
        self.visual_group.setLayout(visual_layout)
        
        self.grid_display: SubplotGrid = SubplotGrid()
        visual_layout.addWidget(self.grid_display)
        
        config_layout.addWidget(self.visual_group)
    
    def __init_CreationControl__(self, config_layout: QVBoxLayout) -> None:
        """Initialize form for subplot position and size configuration."""

        creation_group: QGroupBox = QGroupBox("Create New Subplot")
        position_group: QGroupBox = QGroupBox("Choose subplot size and position")
        one_sub_group: QGroupBox = QGroupBox("Choose data for subplot")
        
        creation_layout: QGridLayout = QGridLayout()
        position_sub_layout: QGridLayout = QGridLayout()
        one_sub_layout:QGridLayout = QGridLayout()
        
        creation_group.setLayout(creation_layout)
        position_group.setLayout(position_sub_layout)
        one_sub_group.setLayout(one_sub_layout)
        
        position_sub_layout.addWidget(QLabel("Row\nposition:"), 0, 0)
        self.row_spin: QSpinBox = QSpinBox()
        self.row_spin.setRange(0, 7)
        self.row_spin.setMinimumWidth(60)
        position_sub_layout.addWidget(self.row_spin, 0, 1)
        
        position_sub_layout.addWidget(QLabel("Column\nposition:"), 0, 2)
        self.col_spin: QSpinBox = QSpinBox()
        self.col_spin.setRange(0, 7)
        self.col_spin.setMinimumWidth(60)
        position_sub_layout.addWidget(self.col_spin, 0, 3)
        
        position_sub_layout.addWidget(QLabel("Row Span:"), 1, 0)
        self.row_span_spin: QSpinBox = QSpinBox()
        self.row_span_spin.setRange(1, 8)
        self.row_span_spin.setValue(1)
        position_sub_layout.addWidget(self.row_span_spin, 1, 1)
        
        position_sub_layout.addWidget(QLabel("Col Span:"), 1, 2)
        self.col_span_spin: QSpinBox = QSpinBox()
        self.col_span_spin.setRange(1, 8)
        self.col_span_spin.setValue(1)
        position_sub_layout.addWidget(self.col_span_spin, 1, 3)
        
        one_sub_layout.addWidget(QLabel("X Data:"), 0, 0)
        self.data_combo_x: QComboBox = QComboBox()
        self.data_combo_x.addItems(["None"])
        one_sub_layout.addWidget(self.data_combo_x, 0, 1, 1, 3)

        one_sub_layout.addWidget(QLabel("X Error:"), 1, 0)
        self.data_combo_xerr: QComboBox = QComboBox()
        self.data_combo_xerr.addItems(["None"])
        one_sub_layout.addWidget(self.data_combo_xerr, 1, 1, 1, 3)

        one_sub_layout.addWidget(QLabel("Y Data:"), 2, 0)
        self.data_combo_y: QComboBox = QComboBox()
        self.data_combo_y.addItems(["None"])
        one_sub_layout.addWidget(self.data_combo_y, 2, 1, 1, 3)
        
        one_sub_layout.addWidget(QLabel("Y Error:"), 3, 0)
        self.data_combo_yerr: QComboBox = QComboBox()
        self.data_combo_yerr.addItems(["None"])
        one_sub_layout.addWidget(self.data_combo_yerr, 3, 1, 1, 3)

        self.add_subplot_btn: QPushButton = QPushButton("Add Subplot")
        self.add_subplot_btn.setToolTip("Click this button if you want to add subplot\n with chosen data to you grid to the position \nentered in \"Row position\", \"Column position\"\n with size in corresponding spans.")
        self.add_subplot_btn.clicked.connect(self.__add_subplot__)
        one_sub_layout.addWidget(self.add_subplot_btn, 4, 0, 1, 2)
        
        self.data_btn: QPushButton = QPushButton("Configure Data Series")
        self.data_btn.clicked.connect(self.configure_data_series)
        self.data_btn.setToolTip("In case you want to add more then one data set to your subplot use this button.\n" 
                                 "To add data series follow this steps:\n"
                                 "1. Choose columns in \"X Data\", \"Y Data\" (\"X Error\", \"Y Error\").\n"
                                 "2. Change some data style if you want.\n"
                                 "3. Click button \"+\"\n"
                                 "4. To Delete data you need to click this data in \"Data Series\" Window, then push the button \"-\".")
        creation_layout.addWidget(self.data_btn, 1, 0, 1, 4)
        
        self.clear_btn: QPushButton = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_subplots)
        creation_layout.addWidget(self.clear_btn, 2, 0, 1, 4)
        
        creation_layout.addWidget(position_group, 0, 0, 1, 3)
        creation_layout.addWidget(one_sub_group, 0, 3, 1, 1)
        config_layout.addWidget(creation_group)

    def __init_EditingControl__(self, config_layout: QVBoxLayout) -> None:
        """Initialize form with tabs for all settings."""
        
        # Subplot editing controls
        self.editor_group: QGroupBox = QGroupBox("Edit Selected Subplot")
        self.editor_group.setEnabled(False)
        editor_layout: QVBoxLayout = QVBoxLayout()
        self.editor_group.setToolTip("To unlock this part, you need firstly create subplot.")
        self.editor_group.setLayout(editor_layout)

        ## Tab widget for different editing options
        self.editor_tabs: QTabWidget = QTabWidget()

        #positioning, resizing, and choosing data tab
        self.position_size_data_tab = PositioningChoosingDataTab()
        self.editor_tabs.addTab(self.position_size_data_tab, "Pos., size, and data")
        self.position_size_data_tab.pos_data_signal.connect(lambda sig: self.__work_with_sub_data_signals__(sig))

        #data style tab
        self.data_style_tab = DataStyleTab()
        self.editor_tabs.addTab(self.data_style_tab, "Data style")
        self.data_style_tab.data_style_signal.connect(lambda sig: self.__update_data_style__(sig))

        #subplot style tab
        self.subplot_style_tab = SubplotStyleTab()
        self.subplot_style_tab.sub_style_signal.connect(self.__update_sub_style__)
        self.editor_tabs.addTab(self.subplot_style_tab, "Subplot style")

        #line style tab
        self.lines_tab = LineStyleTab()
        self.lines_tab.line_style_signal.connect(lambda msg: self.__work_with_lines_signals__(msg))
        self.editor_tabs.addTab(self.lines_tab, "Lines")

        #Combo Box for choosing which subplot will be changed
        subplot_to_change_layout = QHBoxLayout()
        self.subplot_spin = QComboBox()
        self.subplot_spin.addItems(["None"])
        self.subplot_spin.currentTextChanged.connect(self.get_sub_id_select)
        
        #add all widgets to layout
        subplot_to_change_layout.addWidget(QLabel("Subplot to change:"))
        subplot_to_change_layout.addWidget(self.subplot_spin)
        editor_layout.addLayout(subplot_to_change_layout)
        editor_layout.addWidget(self.editor_tabs)
        config_layout.addWidget(self.editor_group)

    def __initUI__(self) -> None:
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
        self.plot_canvas.interactive_plot_signal.connect(lambda sig: self.__work_with_plot_signals__(sig))
        self.plot_canvas.subplots = []
        # self.figure = Figure(figsize=(10, 8), dpi=100)
        plot_layout.addWidget(self.plot_canvas.canvas)
        
        # Set initial splitter sizes
        splitter.addWidget(plot_panel)
        splitter.addWidget(config_panel)
        # splitter.setSizes([500, 1100])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
    
    def __work_with_plot_signals__(self, sig):
        if isinstance(sig, list):
            if sig[0] == "change_subplot":
                self.plot_canvas.subplots[sig[1]] = sig[2]
                self.subplot_style_tab.populate_control(sig[2][6])
            elif sig[0] == "add line":
                self.select_subplot(sig[1])
                self.__add_line_to_subplot__(params=sig[2])

        
    def update_column_data(self, headers: list[str]) -> None:
        "updates all combo boxes that contain headers from the table"

        self.data_combo_x.clear()
        self.data_combo_x.addItems(["None"] + headers)
        self.data_combo_xerr.clear()
        self.data_combo_xerr.addItems(["None"] + headers)
        self.data_combo_y.clear()
        self.data_combo_y.addItems(["None"] + headers)
        self.data_combo_yerr.clear()
        self.data_combo_yerr.addItems(["None"] + headers)
        
        self.position_size_data_tab.update_headers_column_data(headers=headers)

    def __create_grid__(self) -> None:
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
            plot_id, row, col, row_span, col_span, data_series, sub_info, line_info = subplot
            if (row + row_span <= rows and col + col_span <= cols):
                # Subplot fits in new grid, re-add it
                self.grid_display.__add_subplot__(row, col, row_span, col_span, plot_id)
                self.__append_subplot__(plot_id, row, col, row_span, col_span, data_series, sub_info, line_info)
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
                plot_id, row, col, row_span, col_span, data_series, axes_info, title_info, legend_info, line_info = subplot
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
                        self.__append_subplot__(plot_id, row, col, row_span, col_span, data_series, sub_info, line_info)

                        non_fitting_subplots.remove(subplot)
                    else:
                        # Still doesn't fit after adjustment
                        QMessageBox.warning(self, "Still Doesn't Fit", 
                                            f"Subplot {plot_id} still doesn't fit after adjustment")
                else:
                    # User canceled adjustment
                    pass
                self.row_col = [rows, cols]

    def __change_sub_pos__(self, base_info: list[int], subs: list, max_row: int, max_col: int) -> None:
        """Call SubplotPositionDialog to change subplot position."""

        input_pos_dialog = SubplotPositionDialog(base_info, subs, max_row, max_col)
        if input_pos_dialog.exec() == QDialog.DialogCode.Accepted:
                return input_pos_dialog.get_data()
        return None
    
    def __add_subplot__(self) -> None:
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
            "xerr": self.data_combo_xerr.currentText(),
            "y":self.data_combo_y.currentText(),
            "yerr": self.data_combo_yerr.currentText(),
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
        axes_info = {"x-label":self.data_combo_x.currentText(),
             "x min": 0,
             "x max": 1,
             "x ticks": 10,
             "x small ticks": 5,
             "x label fs": 14,
             "x scale": 0,
             "x number of rounding digits": 1,
             "y-label":self.data_combo_y.currentText(),
             "y min": 0,
             "y max": 1,
             "y ticks": 10,
             "y small ticks": 5,
             "y label fs": 14,
             "y scale": 0,
             "y number of rounding digits": 1}
        title_info = {"title": "a",
             "title fs": 14}
        legend_info = {"legend position": "best",
              "legend fs": 14}
        grid_info = {"show grid": True}
        sub_info = {"axes": axes_info, "title": title_info, "legend": legend_info, "grid": grid_info}
        self.__append_subplot__(plot_id, row, col, row_span, col_span, data_series, sub_info, [])


        #min max value for series
        min_max_x = self.window().get_min_max_from_column(self.data_combo_x.currentText())
        min_max_y = self.window().get_min_max_from_column(self.data_combo_y.currentText())
        shift = [(min_max_x[1] - min_max_x[0]) / 20, (min_max_y[1] - min_max_y[0]) / 20]
        self.plot_canvas.subplots[-1][6]["axes"]["x min"] = min_max_x[0] - shift[0]
        self.plot_canvas.subplots[-1][6]["axes"]["x max"] = min_max_x[1] + shift[0]
        self.plot_canvas.subplots[-1][6]["axes"]["y min"] = min_max_y[0] - shift[0]
        self.plot_canvas.subplots[-1][6]["axes"]["y max"] = min_max_y[1] + shift[1]
        self.plot_canvas.subplots[-1][6]["axes"]["x number of rounding digits"] = max([self.find_first_nonzero_digit(min_max_x[0] - shift[0]),
                                                                        self.find_first_nonzero_digit(min_max_x[1] + shift[0])]) + 1
        self.plot_canvas.subplots[-1][6]["axes"]["y number of rounding digits"] = max([self.find_first_nonzero_digit(min_max_y[0] - shift[1]), 
                                                                        self.find_first_nonzero_digit(min_max_x[1] + shift[1])]) + 1
        self.current_plot_id += 1
        
        # Update visual display
        self.grid_display.__add_subplot__(row, col, row_span, col_span, plot_id)
        self.update_subplot_list()
        
        #update subplot lists
        self.subplot_spin.clear()
        self.subplot_spin.addItems(["Subplot " + str(sub[0]) for sub in self.plot_canvas.subplots[:] ])
        # Select the new subplot
        self.select_subplot(plot_id)
    
    def get_sub_id_select(self) -> None:
        """Define selected subplot id and load subplot's properties."""

        if self.subplot_spin.currentText().split():
            sub_id = int(self.subplot_spin.currentText().split()[-1])
            self.select_subplot(sub_id)

    def rectangles_overlap(self, rect1: tuple[int], rect2: tuple[int]) -> bool:
        """Check if two rectangles overlap. 
        Return:
            False if they don't overlap
            True if they overlap.
        """

        r1_row, r1_col, r1_row_span, r1_col_span = rect1
        r2_row, r2_col, r2_row_span, r2_col_span = rect2
        
        return not (r1_col + r1_col_span <= r2_col or 
                   r1_col >= r2_col + r2_col_span or 
                   r1_row + r1_row_span <= r2_row or 
                   r1_row >= r2_row + r2_row_span)
    
    def clear_subplots(self) -> None:
        """Clear all subplots"""

        self.plot_canvas.subplots = []
        self.plot_canvas.fig.clear()
        self.plot_canvas.canvas.draw()
        self.current_plot_id = 0
        self.grid_display.__clear_grid__()
        self.__create_grid__()
        self.clear_selection()
    
    def update_subplot_list(self) -> None:
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
    
    def subplot_selected(self) -> None:
        """Handle subplot selection from the list"""

        selected_items = self.subplot_list.selectedItems()
        if selected_items:
            plot_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.select_subplot(plot_id)
        else:
            self.clear_selection()
    
    def select_subplot(self, plot_id) -> None:
        """Select a subplot and load its properties into the editor"""

        self.selected_subplot_id = plot_id
        self.editor_group.setEnabled(True)
        

        self.subplot_spin.setCurrentIndex(plot_id)

        # Find the subplot
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == plot_id:
                # Populate position controls
                _, row, col, row_span, col_span, data_series, sub_info, line_info = subplot
                axes_info = sub_info["axes"]

                #min max value for series
                extremums = np.zeros((4, len(data_series)))
                for index, ser in enumerate(data_series):
                    min_max_x = self.window().get_min_max_from_column(ser["x"])
                    min_max_y = self.window().get_min_max_from_column(ser["y"])
                    extremums[0][index], extremums[1][index], extremums[2][index], extremums[3][index] = min_max_x[0], min_max_x[1], min_max_y[0], min_max_y[1]
                shift = [(np.max(extremums[1]) - np.min(extremums[0])) / 20, (np.max(extremums[3]) - np.min(extremums[2])) / 20]
                axes_info["x min"] = np.min(extremums[0]) - shift[0]
                axes_info["x max"] = np.max(extremums[1]) + shift[0]
                axes_info["y min"] = np.min(extremums[2]) - shift[1]
                axes_info["y max"] = np.max(extremums[3]) + shift[1]
                axes_info["x number of rounding digits"] = max([self.find_first_nonzero_digit(np.min(extremums[0]) - shift[0]),
                                                            self.find_first_nonzero_digit(np.max(extremums[1]) + shift[0])]) + 1
                axes_info["y number of rounding digits"] = max([self.find_first_nonzero_digit(np.min(extremums[2]) - shift[1]),
                                                            self.find_first_nonzero_digit(np.max(extremums[3]) + shift[1])]) + 1
                
                # Populate position, size and data (data series) controls
                self.position_size_data_tab.populate_control(row=row, col=col, row_span=row_span, col_span=col_span, data_series=data_series)

                # Populate style controls
                self.data_style_tab.__populate_controls__(data_series=data_series)

                #populate subplot control
                self.subplot_style_tab.populate_control(sub_info=sub_info)
            
                #populate line control
                self.__update_lines_table__()
                self.__add_subplot_lines(line_info=line_info)
                break
    
    def __add_subplot_lines(self, line_info) -> None:
        self.lines_tab.line.clear()
        for line in line_info:
            self.lines_tab.update_lines_labels(line)

    def __update_data_headers_spin__(self, data_series: dict) -> None:
        """updates all lists with data sets from subplot"""

        index = self.position_size_data_tab.data_data_spin.currentIndex()
        self.position_size_data_tab.data_data_spin.clear()
        self.position_size_data_tab.data_data_spin.addItems([f"{data['y']}({data['x']}) - {data['id']}" for data in data_series])
        self.position_size_data_tab.data_data_spin.setCurrentIndex(index)
        self.data_style_tab.__update_data_headers_spin__(data_series=data_series, index=index)

    def clear_selection(self) -> None:
        """Clear the current selection"""

        self.selected_subplot_id = None
        self.subplot_list.clearSelection()
        self.editor_group.setEnabled(False)

        self.position_size_data_tab.clear_selection()

        self.data_style_tab.clear_selection()

        self.subplot_style_tab.clear_selection()

    def __update_subplot_position__(self) -> None:
        """Update the position and size of a subplot"""

        if self.selected_subplot_id is None:
            return

        new_row = self.position_size_data_tab.edit_row_spin.value()
        new_col = self.position_size_data_tab.edit_col_spin.value()
        new_row_span = self.position_size_data_tab.edit_row_span_spin.value()
        new_col_span = self.position_size_data_tab.edit_col_span_spin.value()
        
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
    
    def __update_subplot_data__(self) -> None:
        """Update the data for a subplot"""

        if self.selected_subplot_id is None:
            return
            
        new_data_x = self.position_size_data_tab.edit_data_combo_x.currentText()
        new_data_y = self.position_size_data_tab.edit_data_combo_y.currentText()
        new_data_xerr = self.position_size_data_tab.edit_data_combo_xerr.currentText()
        new_data_yerr = self.position_size_data_tab.edit_data_combo_yerr.currentText()
        
        
        # Update the subplot
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                for counter in range(len(self.plot_canvas.subplots[i][5])):
                    data = self.plot_canvas.subplots[i][5][counter]
                    if str(data['id']) == self.position_size_data_tab.data_data_spin.currentText().split('-')[-1].lstrip().rstrip():
                        self.plot_canvas.subplots[i][5][counter]["x"] = new_data_x
                        self.plot_canvas.subplots[i][5][counter]["y"] = new_data_y
                        self.plot_canvas.subplots[i][5][counter]["xerr"] = new_data_xerr
                        self.plot_canvas.subplots[i][5][counter]["yerr"] = new_data_yerr
                if self.selected_subplot_id in self.plot_canvas.axes:
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                    
                self.__update_data_headers_spin__(self.plot_canvas.subplots[i][5])
                break
            
        self.update_subplot_list()
    
    def __update_sub_style__(self) -> None:
        """Update  style properties for the subplot"""

        if self.selected_subplot_id is None:
            return
        
        #read all data
        self.subplot_style_tab.current_subplot = self.subplot_style_tab.get_sub_style_info()
       
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                self.plot_canvas.subplots[i][6] = self.subplot_style_tab.current_subplot
                if self.selected_subplot_id in self.plot_canvas.axes:
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                self.update_subplot_list()
                break

    def __update_data_style__(self, index:str) -> None:
        """Update style properties for the subplot data"""

        if self.selected_subplot_id is None:
            return
            
        self.data_style_tab.current_data_style = self.data_style_tab.get_data_style_info()

        # Update the subplot
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                for counter in range(len(self.plot_canvas.subplots[i][5])):
                    data = self.plot_canvas.subplots[i][5][counter]
                    if str(data['id']) == index:
                        self.plot_canvas.subplots[i][5][counter]["color"] = self.data_style_tab.current_data_style["color"]
                        self.plot_canvas.subplots[i][5][counter]["width"] = self.data_style_tab.current_data_style["width"]
                        self.plot_canvas.subplots[i][5][counter]["label"] = self.data_style_tab.current_data_style["label"]
                        self.plot_canvas.subplots[i][5][counter]["ls"] = self.data_style_tab.current_data_style["ls"]
                        self.plot_canvas.subplots[i][5][counter]["alpha"] = self.data_style_tab.current_data_style["alpha"]
                        self.plot_canvas.subplots[i][5][counter]["marker"] = self.data_style_tab.current_data_style["marker"]
                        self.plot_canvas.subplots[i][5][counter]["marker size"] = self.data_style_tab.current_data_style["marker size"]
                if self.selected_subplot_id in self.plot_canvas.axes:
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                break
        self.update_subplot_list()
        
    
    def plot_graphs(self) -> None:
        """plot all subplots"""

        self.plot_canvas.canvas.draw()
        self.plot_canvas.plot_all_data(self.window(),  self.rows_spin.value(), self.cols_spin.value())
        
    def configure_data_series(self) -> None:
        headers = self.window().get_headers() 
        dialog = DataSeriesDialog(headers=headers, parent=self, max_id=0)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.get_series() != []:
                self.add_data_series_subplot(dialog.get_series(), dialog.get_axes_info(), dialog.get_title_info())

    def add_data_series_subplot(self, series: list[dict], axes_info: dict, title_info: dict) -> None:
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
        sub_info = {"axes": axes_info, "title": title_info, "legend": {"legend position": "best", "legend fs": 14}, "grid": {"show grid": True}}
        self.__append_subplot__(plot_id, row, col, row_span, col_span, series, sub_info, [])

        #min max value for series
        extremums = np.zeros((4, len(series)))
        for index, ser in enumerate(series):
            min_max_x = self.window().get_min_max_from_column(ser["x"])
            min_max_y = self.window().get_min_max_from_column(ser["y"])
            extremums[0][index], extremums[1][index], extremums[2][index], extremums[3][index] = min_max_x[0], min_max_x[1], min_max_y[0], min_max_y[1]
        shift = [(np.max(extremums[1]) - np.min(extremums[0])) / 20, (np.max(extremums[3]) - np.min(extremums[2])) / 20]
        axes_info["x min"] = np.min(extremums[0]) - shift[0]
        axes_info["x max"] = np.max(extremums[1]) + shift[0]
        axes_info["y min"] = np.min(extremums[2]) - shift[1]
        axes_info["y max"] = np.max(extremums[3]) + shift[1]
        axes_info["x number of rounding digits"] = max([self.find_first_nonzero_digit(np.min(extremums[0]) - shift[0]),
                                                 self.find_first_nonzero_digit(np.max(extremums[1]) + shift[0])]) + 1
        axes_info["y number of rounding digits"] = max([self.find_first_nonzero_digit(np.min(extremums[2]) - shift[1]), 
                                                 self.find_first_nonzero_digit(np.max(extremums[3]) + shift[1])]) + 1
        self.current_plot_id += 1
        
        # Update visual display
        self.grid_display.__add_subplot__(row, col, row_span, col_span, plot_id)
        self.update_subplot_list()
        
        #update subplot lists
        self.subplot_spin.clear()
        self.subplot_spin.addItems(["Subplot " + str(sub[0]) for sub in self.plot_canvas.subplots[:] ])

        # Select the new subplot
        self.select_subplot(plot_id)
        
    def __edit_data_series__(self):
        """Edit subplot data series by calling Data Series Dialog."""

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
            if self.selected_subplot_id in self.plot_canvas.axes:
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()

    def find_first_nonzero_digit(self, number:int|float) -> int:
        """Return order of the first non zero digit."""

        order = 0
        number = str(np.abs(number)).split(".")
        if len(number[0]) > 1:
            order = 1 - len(number[0])
            return order
        
        if number[0] == "0":
            for el in number[1]:
                if el != "0":
                    return order
                order += 1
            return order

        elif number[0] in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return 1
    
    def get_state(self) -> dict:
        """Returns the current state to save."""

        return {
            'grid': {
                'rows': self.grid_display.rows,
                'cols': self.grid_display.cols
            },
            'subplots': [
                {
                    'id': sub[0],
                    'position': {
                        'row': sub[1],
                        'col': sub[2],
                        'row_span': sub[3],
                        'col_span': sub[4]
                    },
                    'data_series': sub[5],
                    'sub_info': sub[6],
                    'lines': sub[7] if len(sub) > 7 else []
                }
                for sub in self.plot_canvas.subplots
            ],
            'current_id': self.current_plot_id
        }

    def set_state(self, state: dict) -> None:
        """Restores the state from the configuration."""

        # clear current data
        self.clear_subplots()
        
        # set grid size
        self.rows_spin.setValue(state['grid']['rows'])
        self.cols_spin.setValue(state['grid']['cols'])
        self.__create_grid__()
        
        # restore subplots
        for sub in state['subplots']:
            self.plot_canvas.subplots.append([
                sub['id'],
                sub['position']['row'],
                sub['position']['col'],
                sub['position']['row_span'],
                sub['position']['col_span'],
                sub['data_series'],
                sub['sub_info'],
                sub.get('lines', [])
            ])
            
            # update visual part
            pos = sub['position']
            self.grid_display.__add_subplot__(
                pos['row'],
                pos['col'],
                pos['row_span'],
                pos['col_span'],
                sub['id']
            )
            self.select_subplot(sub['id'])
        
        self.current_plot_id = state['current_id']
        self.update_subplot_list()
        self.plot_graphs()
        self.subplot_spin.clear()
        self.subplot_spin.addItems(["Subplot " + str(sub[0]) for sub in self.plot_canvas.subplots[:] ])

        self.editor_group.setEnabled(True)

        self.__update_lines_table__()
   
    def __add_line_to_subplot__(self, params=None) -> None:
        """Adds a line to the selected subgraph."""

        if self.selected_subplot_id is None:
            return
            
        # Get the line parameters
        if params == None:
            params = {
                'type': self.lines_tab.line_type_combo.currentIndex(),
                'color': self.lines_tab.line_color_draw,
                'width': self.lines_tab.line_width_spin.value(),
                'style': self.lines_tab.line_style_combo.currentText().split()[0],
                'id': self.lines_tab.lines_id,
                'label': "",
                'label_position': "Above the middle of the line",
                'label_font_size': 14
            }
            # Get the parameters depending on the type
            if params['type'] == 0:  # two points
                params.update({
                    'x1': self.lines_tab.x1_spin.value(),
                    'y1': self.lines_tab.y1_spin.value(),
                    'x2': self.lines_tab.x2_spin.value(),
                    'y2': self.lines_tab.y2_spin.value()
                })
            elif params['type'] == 1:  # equation
                params.update({
                    'k': self.lines_tab.k_spin.value(),
                    'b': self.lines_tab.b_spin.value()
                })
            elif params['type'] == 2:  # point and angle
                params.update({
                    'px': self.lines_tab.px_spin.value(),
                    'py': self.lines_tab.py_spin.value(),
                    'angle': self.lines_tab.angle_spin.value()
                })
        else:
            params["id"] = self.lines_tab.lines_id
        self.lines_tab.lines_id += 1

        

        # Add a line to the selected subgraph
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                if len(subplot) < 8:  # If there is no line slot yet
                    subplot.append([])
                subplot[7].append(params)
                # Update subplot
                if self.selected_subplot_id in self.plot_canvas.axes:
                    for line in subplot[7]:
                        ax = self.plot_canvas.draw_line(ax=self.plot_canvas.axes[subplot[0]], params=line)
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                self.__update_lines_table__()
                if len(subplot) > 7 and subplot[7]:  # If there are lines
                    self.__add_subplot_lines(subplot[7])
                break

    def __work_with_lines_signals__(self, msg: str) -> None:
        """Call function regarding the signal."""
        
        if msg == "line added":
            self.__add_line_to_subplot__()
        elif msg == "table changed":
            self.__update_lines_table__()
        elif msg.split()[0] == "delete line":
            self.__delete_line__(int(msg.split()[1]))
        elif msg.split(":")[0] == "line selected ":
            self.__on_line_selected__(int(msg.split(":")[1]))
        elif msg.split(":")[0] == "add label to row ":
            self.__add_label_to_line__(int(msg.split(":")[1]))
        elif msg.split(":")[0] == "change label ":
            self.__change_labels_params__(int(msg.split(":")[1]))
        elif msg.split(":")[0] == "toggle mode ":
            self.__toggle_drawing_mode__(bool(msg.split(":")[1]))
            
    def  __work_with_sub_data_signals__(self, msg: str) -> None:
        """Call function regarding the signal."""

        if msg == "update subplot position":
            self.__update_subplot_position__()
        elif msg == "update subplot data":
            self.__update_subplot_data__()
        elif msg == "edit data series":
            self.__edit_data_series__()

    def __update_lines_table__(self) -> None:
        """Updates the table of existing lines"""

        self.lines_tab.lines_table.setRowCount(0)
        
        # Finding the selected subgraph
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == self.selected_subplot_id:
                if len(subplot) > 7:  # If there are lines
                    for i, line in enumerate(subplot[7]):
                        row = self.lines_tab.lines_table.rowCount()
                        self.lines_tab.lines_table.insertRow(row)
                        
                        #Line id
                        self.lines_tab.lines_table.setItem(row, 0, QTableWidgetItem(str(line['id'])))

                        # Line type
                        types = ["By two points", "By equation", "By point and angle"]
                        self.lines_tab.lines_table.setItem(row, 1, QTableWidgetItem(types[line['type']]))
                        
                        # Parameters
                        if line['type'] == 0:
                            params_str = f"({line['x1']}, {line['y1']}) → ({line['x2']}, {line['y2']})"
                        elif line['type'] == 1:
                            params_str = f"y = {line['k']}x + {line['b']}"
                        else:
                            params_str = f"Точка: ({line['px']}, {line['py']}), Угол: {line['angle']}°"
                        self.lines_tab.lines_table.setItem(row, 2, QTableWidgetItem(params_str))
                        
                        # color
                        line_color_preview = QFrame()
                        line_color_preview.setFixedSize(10, 10)
                        line_color_preview.setStyleSheet(f"background-color: {line['color']};")
                        self.lines_tab.lines_table.setCellWidget(row, 3, line_color_preview)
                        
                        # width
                        self.lines_tab.lines_table.setItem(row, 4, QTableWidgetItem(str(line['width'])))
                        
                        #update label
                        self.lines_tab.lines_table.setItem(row, 5, QTableWidgetItem(line['label']))

                        #update label position
                        self.lines_tab.lines_table.setItem(row, 6, QTableWidgetItem(line['label_position']))
                        
                        # Delete button
                        delete_btn = QPushButton("Delete")
                        delete_btn.clicked.connect(lambda _, idx=i: self.__delete_line__(idx))
                        self.lines_tab.lines_table.setCellWidget(row, 7, delete_btn)
                break
    
    def __delete_line__(self, line_index: int) -> None:
        """Removes a line from a subgraph."""

        if self.selected_subplot_id is None:
            return
            
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id and len(subplot) > 7:
                if line_index < len(subplot[7]):
                    del subplot[7][line_index]
                    if self.selected_subplot_id in self.plot_canvas.axes:
                        
                        ax = self.plot_canvas.update_one_plot(subplot=subplot, win=self.window())
                        # self.plot_canvas.canvas.blit(ax.bbox)
                        self.plot_canvas.canvas.draw()
                        self.plot_canvas.draw()
                    self.__update_lines_table__()
                    self.lines_tab.__delete_line_label__(line_index)
                break

    def __on_line_selected__(self, row: int) -> None:
        """Fills in the signature fields when selecting a line."""

        # Find the selected subgraph and the line
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == self.selected_subplot_id and len(subplot) > 7:
                line = {}
                for l in subplot[7]:
                    if l['id'] == row:
                        line = l
                        self.lines_tab.line.setCurrentText(f"Line {l['id']}")
                        break
                if 'label' in line:
                    self.lines_tab.line_label_edit.setText(line['label'])
                if 'label_position' in line:
                    index = self.lines_tab.label_position_combo.findText(line['label_position'])
                    if index >= 0:
                        self.lines_tab.label_position_combo.setCurrentIndex(index)
                if 'label_font_size' in line:
                    self.lines_tab.label_font_size_spin.setValue(line['label_font_size'])
                break
    
    def __add_label_to_line__(self, row: int) -> None:
        """Add or updates a signature for a selected line."""

        # Find chosen subplot and line
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == self.selected_subplot_id and len(subplot) > 7:
                #new line settings
                line = {}
                for l in subplot[7]:
                    if l['id'] == row:
                        line = l
                        break
                line['label'] = self.lines_tab.line_label_edit.text()
                line['label_position'] = self.lines_tab.label_position_combo.currentText()
                line['label_font_size'] = self.lines_tab.label_font_size_spin.value()
                if self.selected_subplot_id in self.plot_canvas.axes:
                    ax = self.plot_canvas.draw_line(ax=self.plot_canvas.axes[subplot[0]], params=line)
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                self.__update_lines_table__()
                break
    
    def __change_labels_params__(self, index: int) -> None:
        """change label for selected line"""

        # Finding the selected subgraph
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == self.selected_subplot_id:
                if len(subplot) > 7:  # If there are lines
                    for i, line in enumerate(subplot[7]):
                        if line['id'] == index:
                            self.lines_tab.line_label_edit.setText(line['label'])
                            index = self.lines_tab.label_position_combo.findText(line['label_position'])
                            if index >= 0:
                                self.lines_tab.label_position_combo.setCurrentIndex(index)
                            self.lines_tab.label_font_size_spin.setValue(line['label_font_size'])
                            break
               
    def __toggle_drawing_mode__(self, enabled: bool) -> None:
        """
        Toggle line drawing mode on the plot canvas
        
        Args:
            enabled: Boolean indicating whether drawing mode should be activated
        """

        self.plot_canvas.toggle_drawing_mode(enabled)
        
    def __append_subplot__(self, plot_id:int, row:int, col:int, row_span:int, col_span:int, data_series:dict, sub_info:dict, line_info: list) -> None:
        self.plot_canvas.subplots.append([
                    plot_id,
                    row,
                    col,
                    row_span,
                    col_span,
                    data_series,
                    sub_info,
                    line_info
                ])