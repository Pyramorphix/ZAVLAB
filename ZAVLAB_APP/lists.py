import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QDoubleSpinBox, QSpinBox, QComboBox, QLabel, QLineEdit,
    QColorDialog, QHBoxLayout, QFrame, QStyledItemDelegate, QStyle
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPolygonF, QPen, QBrush, 
    QStandardItemModel, QStandardItem
)
from PyQt6.QtCore import Qt, QPointF, QRect, QSize

class MarkerDelegate(QStyledItemDelegate):
    """Custom delegate to draw markers in combo box items"""
    def paint(self, painter, option, index):
        # Draw default background and selection
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, option.palette.alternateBase())
        
        # Get marker name and color
        marker_name = index.data(Qt.ItemDataRole.DisplayRole)
        marker_color = index.data(Qt.ItemDataRole.UserRole) or QColor("#000000")
        
        # Set up painter
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#333333"), 1.5)
        painter.setPen(pen)
        painter.setBrush(QBrush(marker_color))
        
        # Calculate drawing area
        rect = option.rect
        size = min(rect.height() - 6, 20)
        center_x = rect.left() + 30
        center_y = rect.center().y()
        
        # Draw different markers based on name
        if marker_name == "Circle":
            painter.drawEllipse(QPointF(center_x, center_y), size/2, size/2)
        elif marker_name == "Square":
            painter.drawRect(center_x - size/2, center_y - size/2, size, size)
        elif marker_name == "Triangle":
            triangle = QPolygonF([
                QPointF(center_x, center_y - size/2),
                QPointF(center_x + size/2, center_y + size/2),
                QPointF(center_x - size/2, center_y + size/2)
            ])
            painter.drawPolygon(triangle)
        elif marker_name == "Diamond":
            diamond = QPolygonF([
                QPointF(center_x, center_y - size/2),
                QPointF(center_x + size/2, center_y),
                QPointF(center_x, center_y + size/2),
                QPointF(center_x - size/2, center_y)
            ])
            painter.drawPolygon(diamond)
        elif marker_name == "Cross":
            painter.drawLine(center_x - size/2, center_y, center_x + size/2, center_y)
            painter.drawLine(center_x, center_y - size/2, center_x, center_y + size/2)
        elif marker_name == "Plus":
            painter.drawLine(center_x - size/2, center_y, center_x + size/2, center_y)
            painter.drawLine(center_x, center_y - size/2, center_x, center_y + size/2)
        elif marker_name == "Star":
            # Draw a simple star (combination of plus and cross)
            painter.drawLine(center_x - size/2, center_y, center_x + size/2, center_y)
            painter.drawLine(center_x, center_y - size/2, center_x, center_y + size/2)
            painter.drawLine(center_x - size/3, center_y - size/3, 
                            center_x + size/3, center_y + size/3)
            painter.drawLine(center_x - size/3, center_y + size/3, 
                            center_x + size/3, center_y - size/3)
        
        # Draw text
        text_rect = QRect(rect.left() + 50, rect.top(), rect.width() - 50, rect.height())
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, marker_name)

    def sizeHint(self, option, index):
        return QSize(150, 24)

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chart Settings")
        self.resize(600, 500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Data Visualization Parameters")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tree widget for parameters
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Parameter", "Value"])
        self.tree.setColumnWidth(0, 300)
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet("""
            QTreeWidget::item { padding: 5px; }
            QTreeWidget::item:selected { background-color: #e6f3ff; }
        """)
        main_layout.addWidget(self.tree, 1)
        
        # Adding parameter groups
        self.add_axes_group()
        self.add_lines_group()
        self.add_markers_group()
        self.add_other_group()
        
        # Control buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)
        
        self.toggle_button = QPushButton("Expand All")
        self.toggle_button.clicked.connect(self.toggle_all_groups)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        
        apply_button = QPushButton("Apply Settings")
        apply_button.clicked.connect(self.apply_settings)
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(apply_button)
        main_layout.addLayout(buttons_layout)
        
        # Initial state: all groups collapsed
        self.collapse_all_groups()

    def add_axes_group(self):
        """Add axes settings group"""
        group = QTreeWidgetItem(self.tree, ["Axes"])
        group.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))
        group.setIcon(0, self.style().standardIcon(
            self.style().StandardPixmap.SP_DirIcon
        ))
        
        # Parameters for the group
        params = [
            ("X Axis Title", "text", "X Axis"),
            ("Y Axis Title", "text", "Y Axis"),
            ("X Min", "float", 0.0),
            ("X Max", "float", 10.0),
            ("Y Min", "float", -1.0),
            ("Y Max", "float", 1.0),
            ("X Scale", "combo", "Linear", ["Linear", "Logarithmic"]),
            ("Y Scale", "combo", "Linear", ["Linear", "Logarithmic"]),
            ("X Grid Step", "float", 1.0, 0.1, 10.0),
            ("Y Grid Step", "float", 0.5, 0.1, 10.0),
            ("Show Grid", "combo", "Yes", ["Yes", "No"])
        ]
        
        # Store references to editors
        self.x_min_editor = None
        self.x_max_editor = None
        self.y_min_editor = None
        self.y_max_editor = None
        self.x_scale_combo = None
        self.y_scale_combo = None
        self.x_grid_step_editor = None
        self.y_grid_step_editor = None
        
        for name, ptype, default, *args in params:
            editor = self.add_parameter(group, name, ptype, default, *args)
            
            # Save references to important editors
            if name == "X Min":
                self.x_min_editor = editor
                self.x_min_editor.valueChanged.connect(self.validate_x_limits)
            elif name == "X Max":
                self.x_max_editor = editor
                self.x_max_editor.valueChanged.connect(self.validate_x_limits)
            elif name == "Y Min":
                self.y_min_editor = editor
                self.y_min_editor.valueChanged.connect(self.validate_y_limits)
            elif name == "Y Max":
                self.y_max_editor = editor
                self.y_max_editor.valueChanged.connect(self.validate_y_limits)
            elif name == "X Scale":
                self.x_scale_combo = editor
                self.x_scale_combo.currentTextChanged.connect(self.update_grid_step_state)
            elif name == "Y Scale":
                self.y_scale_combo = editor
                self.y_scale_combo.currentTextChanged.connect(self.update_grid_step_state)
            elif name == "X Grid Step":
                self.x_grid_step_editor = editor
            elif name == "Y Grid Step":
                self.y_grid_step_editor = editor

    def add_lines_group(self):
        """Add lines settings group"""
        group = QTreeWidgetItem(self.tree, ["Lines"])
        group.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))
        group.setIcon(0, self.style().standardIcon(
            self.style().StandardPixmap.SP_FileIcon
        ))
        
        # Create parameters with color picker button
        params = [
            ("Line Width", "float", 1.5),
            ("Line Color", "color", "#0000FF"),  # Blue by default
            ("Line Style", "combo", "Solid", ["Solid", "Dashed", "Dash-Dot"]),
            ("Transparency", "int", 100, 10, 100, "%")
        ]
        
        for name, ptype, default, *args in params:
            self.add_parameter(group, name, ptype, default, *args)

    def add_markers_group(self):
        """Add markers settings group with visual representation"""
        group = QTreeWidgetItem(self.tree, ["Data Points"])
        group.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))
        group.setIcon(0, self.style().standardIcon(
            self.style().StandardPixmap.SP_ComputerIcon
        ))
        
        # Create parameters
        params = [
            ("Show Markers", "combo", "Yes", ["Yes", "No"]),
            ("Marker Size", "int", 8, 1, 20),
            ("Marker Shape", "marker", "Circle", ["Circle", "Square", "Triangle", "Diamond", "Cross", "Plus", "Star"]),
            ("Fill Color", "color", "#00FF00")  # Green by default
        ]
        
        # Store reference to fill color editor
        self.marker_fill_color = None
        
        for name, ptype, default, *args in params:
            editor = self.add_parameter(group, name, ptype, default, *args)
            
            # Save reference to fill color editor
            if name == "Fill Color":
                self.marker_fill_color = editor

    def add_other_group(self):
        """Add other settings group"""
        group = QTreeWidgetItem(self.tree, ["Additional Settings"])
        group.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))
        group.setIcon(0, self.style().standardIcon(
            self.style().StandardPixmap.SP_FileDialogDetailedView
        ))
        
        params = [
            ("Chart Title", "text", "Data Visualization"),
            ("Antialiasing", "combo", "Enabled", ["Enabled", "Disabled"]),
            ("Rendering Quality", "combo", "High", ["Low", "Medium", "High"]),
            ("Legend Font Size", "int", 12, 8, 20, "pt"),
            ("Legend Position", "combo", "Top Right", 
             ["Top Right", "Top Left", "Bottom Right", "Bottom Left"])
        ]
        
        for name, ptype, default, *args in params:
            self.add_parameter(group, name, ptype, default, *args)

    def add_parameter(self, parent, name, ptype, default, *args):
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
        elif ptype == "int":
            editor = QSpinBox()
            editor.setValue(default)
            # Set reasonable default range if not provided
            min_val = args[0] if len(args) > 0 else -1000000
            max_val = args[1] if len(args) > 1 else 1000000
            editor.setRange(min_val, max_val)
            if len(args) > 2:  # Suffix (unit)
                editor.setSuffix(f" {args[2]}")
        elif ptype == "combo":
            editor = QComboBox()
            # If the next argument is a list, use it, else use all remaining args
            if args and isinstance(args[0], list):
                editor.addItems(args[0])
            else:
                editor.addItems(args)
            editor.setCurrentText(default)
            editor.setStyleSheet("QComboBox { padding: 3px; }")
        elif ptype == "text":
            editor = QLineEdit()
            editor.setText(default)
            editor.setPlaceholderText("Enter text...")
            editor.setStyleSheet("""
                QLineEdit {
                    padding: 3px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                QLineEdit:focus {
                    border: 1px solid #4CAF50;
                }
            """)
        elif ptype == "color":
            # Create container for color widget and button
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)
            
            # Color preview widget (square)
            color_preview = QFrame()
            color_preview.setFixedSize(24, 24)
            color_preview.setStyleSheet(f"background-color: {default}; border: 1px solid #888; border-radius: 3px;")
            color_preview.setProperty("color", default)
            
            # Color button
            color_button = QPushButton("Choose color")
            color_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    border: 1px solid #888;
                    border-radius: 3px;
                    background-color: #f0f0f0;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            color_button.setCursor(Qt.CursorShape.PointingHandCursor)
            color_button.clicked.connect(lambda: self.choose_color(color_preview))
            
            layout.addWidget(color_preview)
            layout.addWidget(color_button)
            layout.addStretch()
            
            editor = container
        elif ptype == "marker":
            # Create combo box with visual markers
            editor = QComboBox()
            editor.setItemDelegate(MarkerDelegate(editor))
            
            # Get marker names
            marker_names = args[0] if isinstance(args[0], list) else args
            
            # Add items with color data
            for name in marker_names:
                item = QStandardItem(name)
                # Store current fill color for markers
                if self.marker_fill_color:
                    container = self.marker_fill_color
                    color_preview = container.findChild(QFrame)
                    if color_preview:
                        item.setData(QColor(color_preview.property("color")), Qt.ItemDataRole.UserRole)
                editor.model().appendRow(item)
            
            # Set current item
            editor.setCurrentText(default)
            
            # Style the combo box
            editor.setStyleSheet("""
                QComboBox {
                    padding: 3px;
                }
                QComboBox::drop-down {
                    border: none;
                }
            """)
        
        if editor:
            self.tree.setItemWidget(param_item, 1, editor)
            return editor
        return None

    def choose_color(self, preview_widget):
        """Open color dialog to choose color"""
        current_color = preview_widget.property("color")
        color = QColorDialog.getColor(initial=QColor(current_color), parent=self)
        if color.isValid():
            hex_color = color.name()
            preview_widget.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #888; border-radius: 3px;")
            preview_widget.setProperty("color", hex_color)
            
            # Update marker combo box if fill color changed
            self.update_marker_combo_box()

    def update_marker_combo_box(self):
        """Update marker combo box when fill color changes"""
        # Find marker shape combo box
        for i in range(self.tree.topLevelItemCount()):
            group = self.tree.topLevelItem(i)
            if group.text(0) == "Data Points":
                for j in range(group.childCount()):
                    item = group.child(j)
                    if item.text(0) == "Marker Shape":
                        combo = self.tree.itemWidget(item, 1)
                        if combo:
                            # Update model data with new color
                            if self.marker_fill_color:
                                container = self.marker_fill_color
                                color_preview = container.findChild(QFrame)
                                if color_preview:
                                    new_color = color_preview.property("color")
                                    model = combo.model()
                                    for row in range(model.rowCount()):
                                        model.item(row).setData(QColor(new_color), Qt.ItemDataRole.UserRole)
                            
                            # Trigger repaint
                            combo.update()
                        break
                break

    # ... (остальные методы остаются без изменений: validate_x_limits, validate_y_limits, 
    # update_grid_step_state, toggle_all_groups, expand_all_groups, collapse_all_groups)

    def apply_settings(self):
        """Apply settings handler"""
        # First validate all limits
        self.validate_x_limits()
        self.validate_y_limits()
        
        print("Settings applied!")
        # Collect all settings
        settings = {}
        for group_idx in range(self.tree.topLevelItemCount()):
            group = self.tree.topLevelItem(group_idx)
            group_name = group.text(0)
            settings[group_name] = {}
            
            for param_idx in range(group.childCount()):
                param_item = group.child(param_idx)
                param_name = param_item.text(0)
                editor = self.tree.itemWidget(param_item, 1)
                
                if isinstance(editor, (QDoubleSpinBox, QSpinBox)):
                    value = editor.value()
                elif isinstance(editor, QComboBox):
                    value = editor.currentText()
                elif isinstance(editor, QLineEdit):
                    value = editor.text()
                elif isinstance(editor, QWidget):  # For color container
                    # Find the color preview widget
                    color_preview = editor.findChild(QFrame)
                    if color_preview:
                        value = color_preview.property("color")
                    else:
                        value = None
                else:
                    value = None
                
                settings[group_name][param_name] = value
        
        # Print to console for demonstration
        print("Collected settings:")
        for group, params in settings.items():
            print(f"[{group}]")
            for param, value in params.items():
                print(f"  {param}: {value}")
        
        # Special handling for logarithmic scales
        if "Axes" in settings:
            axes_settings = settings["Axes"]
            if "X Scale" in axes_settings and axes_settings["X Scale"] == "Logarithmic":
                print("\nNote: Using fixed grid step (1 decade) for logarithmic X-axis")
            if "Y Scale" in axes_settings and axes_settings["Y Scale"] == "Logarithmic":
                print("Note: Using fixed grid step (1 decade) for logarithmic Y-axis")
        
        print("\n")

    def validate_x_limits(self):
        """Ensure X Min < X Max"""
        if not self.x_min_editor or not self.x_max_editor:
            return
            
        x_min = self.x_min_editor.value()
        x_max = self.x_max_editor.value()
        
        if x_min >= x_max:
            # Adjust min/max to maintain valid range
            if self.x_min_editor.hasFocus():
                # If user is editing min, adjust max
                self.x_max_editor.setValue(x_min + 0.1)
            else:
                # If user is editing max, adjust min
                self.x_min_editor.setValue(x_max - 0.1)
                
            # Highlight problematic fields
            self.highlight_invalid(self.x_min_editor)
            self.highlight_invalid(self.x_max_editor)
        else:
            # Reset highlighting if valid
            self.reset_highlight(self.x_min_editor)
            self.reset_highlight(self.x_max_editor)

    def validate_y_limits(self):
        """Ensure Y Min < Y Max"""
        if not self.y_min_editor or not self.y_max_editor:
            return
            
        y_min = self.y_min_editor.value()
        y_max = self.y_max_editor.value()
        
        if y_min >= y_max:
            # Adjust min/max to maintain valid range
            if self.y_min_editor.hasFocus():
                # If user is editing min, adjust max
                self.y_max_editor.setValue(y_min + 0.1)
            else:
                # If user is editing max, adjust min
                self.y_min_editor.setValue(y_max - 0.1)
                
            # Highlight problematic fields
            self.highlight_invalid(self.y_min_editor)
            self.highlight_invalid(self.y_max_editor)
        else:
            # Reset highlighting if valid
            self.reset_highlight(self.y_min_editor)
            self.reset_highlight(self.y_max_editor)

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
            editor.setStyleSheet("QLineEdit { border: 1px solid #ccc; }")

    def update_grid_step_state(self):
        """Update grid step editors based on scale selection"""
        if self.x_scale_combo and self.x_grid_step_editor:
            is_log = self.x_scale_combo.currentText() == "Logarithmic"
            self.x_grid_step_editor.setEnabled(not is_log)
            if is_log:
                # For logarithmic scale, set fixed grid step (1 decade)
                self.x_grid_step_editor.setValue(1.0)
                
        if self.y_scale_combo and self.y_grid_step_editor:
            is_log = self.y_scale_combo.currentText() == "Logarithmic"
            self.y_grid_step_editor.setEnabled(not is_log)
            if is_log:
                # For logarithmic scale, set fixed grid step (1 decade)
                self.y_grid_step_editor.setValue(1.0)

    def toggle_all_groups(self):
        """Toggle expand/collapse all groups"""
        all_expanded = all(
            self.tree.topLevelItem(i).isExpanded()
            for i in range(self.tree.topLevelItemCount())
        )
        
        if all_expanded:
            self.collapse_all_groups()
            self.toggle_button.setText("Expand All")
        else:
            self.expand_all_groups()
            self.toggle_button.setText("Collapse All")

    def expand_all_groups(self):
        """Expand all groups"""
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setExpanded(True)

    def collapse_all_groups(self):
        """Collapse all groups"""
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setExpanded(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set light color palette
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(240, 240, 240))
    app.setPalette(palette)
    
    widget = SettingsWidget()
    widget.show()
    sys.exit(app.exec())