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
                             QListWidgetItem, QColorDialog)
from PyQt6.QtGui import QColor
from interactive_plot import INTERACTIVE_PLOT
from dialogs import SubplotPositionDialog, DataSeriesDialog
from PyQt6.QtCore import Qt

class SubplotCell(QFrame):
    """Visual representation of a single grid cell"""
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setFixedSize(40, 40)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")
        self.setToolTip(f"Cell ({row},{col})")
        self.occupied = False
        self.subplot_id = None

    def set_occupied(self, subplot_id, color):
        self.occupied = True
        self.subplot_id = subplot_id
        self.setStyleSheet(f"background-color: {color}; border: 1px solid #333333;")
        self.setToolTip(f"Subplot {subplot_id}")

class SubplotGrid(QWidget):
    """Visual grid for designing subplot layouts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.setLayout(self.grid_layout)
        self.cells = {}
        self.subplot_widgets = {}
        self.subplot_colors = {}
        self.current_color_idx = 0
        self.colors = [
            "#FFCCCC", "#CCFFCC", "#CCCCFF", "#FFFFCC", "#FFCCFF", "#CCFFFF",
            "#FFDDAA", "#DDFFAA", "#DDAADD", "#AADDAA", "#AADDFF", "#FFAADD"
        ]

    def create_grid(self, rows, cols):
        # Clear existing grid
        self.clear_grid()
        
        # Create new grid
        for r in range(rows):
            for c in range(cols):
                cell = SubplotCell(r, c)
                self.grid_layout.addWidget(cell, r, c)
                self.cells[(r, c)] = cell

    def clear_grid(self):
        """Clear the entire grid"""
        # Remove all widgets from the layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.cells = {}
        self.subplot_widgets = {}
        self.subplot_colors = {}
        self.current_color_idx = 0

    def add_subplot(self, row, col, row_span, col_span, subplot_id):
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
        
        # Mark all cells in the span as occupied
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                if (r, c) in self.cells:
                    self.cells[(r, c)].set_occupied(subplot_id, color)
        
        return True

    def remove_subplot(self, subplot_id):
        """Remove a subplot from the grid"""
        if subplot_id in self.subplot_widgets:
            # Remove the visual widget
            widget = self.subplot_widgets.pop(subplot_id)
            widget.deleteLater()
            
            # Remove the color reference
            if subplot_id in self.subplot_colors:
                del self.subplot_colors[subplot_id]
            
            # Reset cells
            for cell in self.cells.values():
                if cell.subplot_id == subplot_id:
                    cell.occupied = False
                    cell.subplot_id = None
                    cell.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")

    def update_subplot(self, subplot_id, row, col, row_span, col_span):
        """Update a subplot's position and size"""
        # First remove the old visualization
        self.remove_subplot(subplot_id)
        
        # Then add it back with new parameters
        self.add_subplot(row, col, row_span, col_span, subplot_id)

class SubplotEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize UI
        self.initUI()
        
        # Current subplot configuration
        self.subplots = []  # [id, row, col, row_span, col_span, data_series, show_grid]
        self.current_plot_id = 0
        self.selected_subplot_id = None
        
    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # Create a splitter for resizable panels
        splitter = QSplitter()
        main_layout.addWidget(splitter)
        
        # Left panel for configuration
        config_panel = QWidget()
        config_layout = QVBoxLayout()
        config_panel.setLayout(config_layout)
        
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
        
        self.create_grid_btn = QPushButton("Create Grid")
        self.create_grid_btn.clicked.connect(self.create_grid)
        grid_layout.addWidget(self.create_grid_btn, 0, 4)
        
        grid_group.setLayout(grid_layout)
        config_layout.addWidget(grid_group)
        
        # Visual grid display
        self.visual_group = QGroupBox("Subplot Layout")
        visual_layout = QVBoxLayout()
        self.visual_group.setLayout(visual_layout)
        
        self.grid_display = SubplotGrid()
        visual_layout.addWidget(self.grid_display)
        
        config_layout.addWidget(self.visual_group)

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
        self.add_subplot_btn.clicked.connect(self.add_subplot)
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
        # Subplot editing controls
        self.editor_group = QGroupBox("Edit Selected Subplot")
        self.editor_group.setEnabled(False)
        editor_layout = QVBoxLayout()
        self.editor_group.setLayout(editor_layout)
        
        # Tab widget for different editing options
        self.editor_tabs = QTabWidget()
        
        # Position tab
        position_tab = QWidget()
        position_layout = QGridLayout(position_tab)
        
        position_layout.addWidget(QLabel("Row:"), 0, 0)
        self.edit_row_spin = QSpinBox()
        self.edit_row_spin.setRange(0, 7)
        position_layout.addWidget(self.edit_row_spin, 0, 1)
        
        position_layout.addWidget(QLabel("Column:"), 0, 2)
        self.edit_col_spin = QSpinBox()
        self.edit_col_spin.setRange(0, 7)
        position_layout.addWidget(self.edit_col_spin, 0, 3)
        
        position_layout.addWidget(QLabel("Row Span:"), 1, 0)
        self.edit_row_span_spin = QSpinBox()
        self.edit_row_span_spin.setRange(1, 8)
        self.edit_row_span_spin.setValue(1)
        position_layout.addWidget(self.edit_row_span_spin, 1, 1)
        
        position_layout.addWidget(QLabel("Col Span:"), 1, 2)
        self.edit_col_span_spin = QSpinBox()
        self.edit_col_span_spin.setRange(1, 8)
        self.edit_col_span_spin.setValue(1)
        position_layout.addWidget(self.edit_col_span_spin, 1, 3)
        
        self.update_position_btn = QPushButton("Update Position/Size")
        self.update_position_btn.clicked.connect(self.update_subplot_position)
        position_layout.addWidget(self.update_position_btn, 2, 0, 1, 4)
        
        self.editor_tabs.addTab(position_tab, "Position")
        
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
        
        # Styling tab
        style_tab = QWidget()
        style_layout = QFormLayout(style_tab)
        
        self.data_styles_spin = QComboBox()
        self.data_styles_spin.addItems(["None"])
        style_layout.addRow("Data to change:", self.data_styles_spin)
        
        self.line_width_spin = QDoubleSpinBox()
        self.line_width_spin.setRange(0.1, 10.0)
        self.line_width_spin.setValue(1.0)
        style_layout.addRow("Line Width:", self.line_width_spin)
        
        self.line_color_btn = QPushButton("Choose Color")
        self.line_color_btn.clicked.connect(self.choose_line_color)
        style_layout.addRow("Line Color:", self.line_color_btn)
        
        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        style_layout.addRow(self.grid_checkbox)
        
        self.update_style_btn = QPushButton("Update Style")
        self.update_style_btn.clicked.connect(self.update_data_style)
        style_layout.addRow(self.update_style_btn)
        
        self.editor_tabs.addTab(style_tab, "Style")
        
        editor_layout.addWidget(self.editor_tabs)
        
        config_layout.addWidget(self.editor_group)
        
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
        
        # Initialize line color
        self.line_color = "#1f77b4"  # Default matplotlib blue
    
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

    def create_grid(self):
        """Create a new grid based on row/column configuration"""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        self.grid_display.create_grid(rows, cols)
        self.plot_canvas.subplots = []
        self.current_plot_id = 0
        self.update_subplot_list()
        self.clear_selection()
    
    def change_sub_pos(self, base_info, subs, max_row, max_col):
        input_pos_dialog = SubplotPositionDialog(base_info, subs, max_row, max_col)
        if input_pos_dialog.exec() == QDialog.DialogCode.Accepted:
                return input_pos_dialog.get_data()
        return None
    
    def add_subplot(self):
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
            "x":self.data_combo_x.currentText(),
            "y":self.data_combo_y.currentText(),
            "color":self.line_color, 
            "width":1.0
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
            True ,  # Show grid
            {"x-label":self.data_combo_x.currentText(),
            "y-label":self.data_combo_y.currentText()}
        ])
        self.current_plot_id += 1
        
        # Update visual display
        self.grid_display.add_subplot(row, col, row_span, col_span, plot_id)
        self.update_subplot_list()
        
        # Select the new subplot
        self.select_subplot(plot_id)
    
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
        self.grid_display.clear_grid()
        self.create_grid()
        self.clear_selection()
    
    def update_subplot_list(self):
        """Update the subplot list widget"""
        self.subplot_list.clear()
        
        for subplot in self.plot_canvas.subplots:
            plot_id, row, col, row_span, col_span, data_series, *_ = subplot
            data_info = ""
            for data in data_series:
                data_info += f"\n{data['y']}({data['x']}), line color - {data['color']}, line width - {data['width']}"
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
        
        # Find the subplot
        for subplot in self.plot_canvas.subplots:
            if subplot[0] == plot_id:
                # Populate position controls
                _, row, col, row_span, col_span, data_series, show_grid, subplot_info = subplot
                self.edit_row_spin.setValue(row)
                self.edit_col_spin.setValue(col)
                self.edit_row_span_spin.setValue(row_span)
                self.edit_col_span_spin.setValue(col_span)
                self.data_data_spin.clear()
                self.data_data_spin.addItems([f"{data['y']}({data['x']})" for data in data_series])
                self.data_data_spin.setCurrentIndex(0)
                # Populate data controls
                self.edit_data_combo_x.setCurrentText(data_series[0]["x"])
                self.edit_data_combo_y.setCurrentText(data_series[0]["y"])
                
                # Populate style controls
                self.data_styles_spin.clear()
                self.data_styles_spin.addItems([f"{data['y']}({data['x']})" for data in data_series])
                self.data_styles_spin.setCurrentIndex(0)
                self.line_width_spin.setValue(data_series[0]["width"])
                self.grid_checkbox.setChecked(show_grid)
                self.line_color = data_series[0]["color"]
                break
    
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
                result= self.change_sub_pos(base_info=[new_row, new_col, new_row_span, new_col_span, self.selected_subplot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                if result is None:
                    return
                else:
                    new_row, new_row_span, new_col, new_col_span = result
        if new_col + new_col_span > max_cols:
            reply = QMessageBox.question(self, "Invalid Position", f"Column span exceeds grid width (max col: {max_cols-1})" + "Do you want to change column span of your subplot?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                result = self.change_sub_pos(base_info=[new_row, new_col, new_row_span, new_col_span, self.selected_subplot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
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
                    result = self.change_sub_pos(base_info=[new_row, new_col, new_row_span, new_col_span, self.selected_subplot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
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
                self.grid_display.update_subplot(
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
                    if f"{data['y']}({data['x']})" == self.data_data_spin.currentText():
                        self.plot_canvas.subplots[i][5][counter]["x"] = new_data_x
                        self.plot_canvas.subplots[i][5][counter]["y"] = new_data_y
                if self.selected_subplot_id < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                break
        
        self.update_subplot_list()
    
    def choose_line_color(self):
        """Open color dialog to choose line color"""
        color = QColorDialog.getColor(initial=QColor(self.line_color))
        if color.isValid():
            self.line_color = color.name()
    
    def update_data_style(self):
        """Update the style properties for a subplot"""
        if self.selected_subplot_id is None:
            return
            
        new_color = self.line_color
        new_width = self.line_width_spin.value()
        new_grid = self.grid_checkbox.isChecked()
        
        # Update the subplot
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                for counter in range(len(self.plot_canvas.subplots[i][5])):
                    data = self.plot_canvas.subplots[i][5][counter]
                    if f"{data['y']}({data['x']})" == self.data_data_spin.currentText():
                        self.plot_canvas.subplots[i][5][counter]["color"] = new_color
                        self.plot_canvas.subplots[i][5][counter]["width"] = new_width
                self.plot_canvas.subplots[i][6] = new_grid
                
                if self.selected_subplot_id < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.update_one_plot(subplot, self.window())
                    # self.plot_canvas.canvas.blit(ax.bbox)
                    self.plot_canvas.canvas.draw()
                    self.plot_canvas.draw()
                break
        self.update_subplot_list()
    
    # Updated plot_graphs method in the SubplotEditor class
    def plot_graphs(self):
        self.plot_canvas.fig.clear()
        self.plot_canvas.canvas.draw()
        self.plot_canvas.plot_all_data(self.window(),  self.rows_spin.value(), self.cols_spin.value())
        
    def configure_data_series(self):
        headers = self.window().get_headers() 
        dialog = DataSeriesDialog(headers, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.get_series() != []:
                self.add_data_series_subplot(dialog.get_series(), dialog.get_subplot_info())

    def add_data_series_subplot(self, series, subplot_info):
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
                result= self.change_sub_pos(base_info=[row, col, row_span, col_span, self.current_plot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
                if result is None:
                    return
                else:
                    row, row_span, col, col_span = result          
        if col + col_span > max_cols:
            reply = QMessageBox.question(self, "Invalid Position", f"Column span exceeds grid width (max col: {max_cols-1})" + "Do you want to change column span of your subplot?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                result = self.change_sub_pos(base_info=[row, col, row_span, col_span, self.current_plot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
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
                    result = self.change_sub_pos(base_info=[row, col, row_span, col_span, self.current_plot_id], subs=self.plot_canvas.subplots, max_row=max_rows, max_col=max_cols)
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
            True,   # Show grid
            subplot_info
        ])
        self.current_plot_id += 1
        
        # Update visual display
        self.grid_display.add_subplot(row, col, row_span, col_span, plot_id)
        self.update_subplot_list()
        
        # Select the new subplot
        self.select_subplot(plot_id)
        

    def edit_data_series(self):
        if not self.selected_subplot_id:
            return
        
        # Find current series
        subplot = next((s for s in self.plot_canvas.subplots if s[0] == self.selected_subplot_id), None)
        if not subplot: return
        
        headers = self.window().get_headers()
        dialog = DataSeriesDialog(headers, self)
        dialog.series = subplot[5][:]  # Copy existing series
        for series in dialog.series:
            dialog.series_list.addItem(f"{series['x']} vs {series['y']}")
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            subplot[5] = dialog.get_series()
            self.update_subplot_list()
            self.plot_canvas.update_one_plot(subplot, self.window())
            self.plot_canvas.canvas.draw()
