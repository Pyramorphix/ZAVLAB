"""
Contains all dialog windows used in the application:
- Data series configuration
- Axis configuration
- Subplot positioning
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QPushButton, QComboBox,
                              QDoubleSpinBox, QFormLayout, QDialogButtonBox, QColorDialog, 
                              QLineEdit, QMessageBox, QGridLayout, QSpinBox, QCheckBox, QWidget, QScrollArea,
                              QTabWidget, QFrame)
from PyQt6.QtGui import QColor
import numpy as np
from matplotlib.axes import Axes
import matplotlib.ticker as ticker


class DataSeriesDialog(QDialog):
    """
    Dialog for configuring data series in plots:
    - Add/remove multiple data series
    - Set X/Y data columns
    - Configure line styles (color, width)
    """


    def __init__(self, headers: list[str], max_id:int=0, parent=None) -> None:
        """
        Initialize data series dialog
        
        Args:
            headers: List of available column 
            parent: Parent Qt widget
        """

        super().__init__(parent)
        self.__init_dialog_window__()
        self.__init_dialog_ui__(headers=headers, max_id=max_id)

    def __init_dialog_window__(self) -> None:
        """Initialize Dialog window for configuring data series."""
        self.setWindowTitle("Data Series Configuration")

    def __init_dialog_ui__(self, headers: list[str], max_id:int = 0) -> None:
        """Initialize UI for data series dialog window"""


        #main layout
        layout: QVBoxLayout = QVBoxLayout()

        # Data series list
        self.series_list: QListWidget = QListWidget()
        layout.addWidget(QLabel("Data Series:"))
        layout.addWidget(self.series_list)
        
        # Controls
        btn_layout: QHBoxLayout = QHBoxLayout()
        self.add_btn: QPushButton = QPushButton("+")
        self.add_btn.clicked.connect(self.__add_series__)
        self.remove_btn: QPushButton = QPushButton("-")
        self.remove_btn.clicked.connect(self.__remove_series__)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)
        
        # Data selection
        self.data_combo_x: QComboBox = QComboBox()
        self.data_combo_x.addItems(["None"] + headers)
        self.data_combo_xerr: QComboBox = QComboBox()
        self.data_combo_xerr.addItems(["None"] + headers)
        self.data_combo_y: QComboBox = QComboBox()
        self.data_combo_y.addItems(["None"] + headers)
        self.data_combo_yerr: QComboBox = QComboBox()
        self.data_combo_yerr.addItems(["None"] + headers)
        
        # Style controls
        self.color_btn: QPushButton = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.__choose_color__)
        self.line_width: QDoubleSpinBox = QDoubleSpinBox()
        self.line_width.setMinimum(0)
        self.line_width.setValue(1.0)
        self.line_style_spin = QComboBox()
        self.line_style_spin.addItems(["Nothing", "- (solid)", ": (solid)", "-- (dashed)", "-. (dashdot)"])
        self.line_style_spin.setCurrentIndex(0)

        
        #design window
        form: QFormLayout = QFormLayout()
        form.addRow("X Data:", self.data_combo_x)
        form.addRow("X Error:", self.data_combo_xerr)
        form.addRow("Y Data:", self.data_combo_y)
        form.addRow("Y Error:", self.data_combo_yerr)
        form.addRow("Line Color:", self.color_btn)
        form.addRow("Line Width:", self.line_width)
        form.addRow("Line style:", self.line_style_spin)
        layout.addLayout(form)

        #subplot preset
        layout_x = QHBoxLayout()
        layout_y = QHBoxLayout()
        self.x_line_edit = QLineEdit("x")
        self.y_line_edit = QLineEdit("y") 
        layout_x.addWidget(QLabel("x axis label:"))
        layout_x.addWidget(self.x_line_edit)
        layout_y.addWidget(QLabel("y axis label:"))  
        layout_y.addWidget(self.y_line_edit)     
        layout.addLayout(layout_x)
        layout.addLayout(layout_y)
        
        # Dialog buttons
        buttons: QDialogButtonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        #set main layout
        self.setLayout(layout)

        #plot variables
        self.line_color: str = "#1f77b4"
        self.series: list[dict] = []
        self.current_data_index = max_id
        self.standart_colors = ["#1B1F3B",
        "#FF5733",
        "#2ECC71",
        "#8E44AD",
        "#3498DB",
        "#D35400",
        "#16A085",
        "#C0392B",
        "#5DADE2",
        "#900C3F",
        "#27AE60",
        "#34495E",
        "#E74C3C",
        "#2C3E50",
        "#58D68D",
        "#6C3483",
        "#1ABC9C",
        "#E67E22",
        "#2980B9",
        "#922B21",
        "#45B39D",
        "#A569BD",
        "#154360",
        "#F39C12",
        "#2E86C1",
        "#7D3C98",
        "#138D75",
        "#B03A2E",
        "#2471A3",
        "#117A65",
        "#641E16"
        ]

    def __choose_color__(self) -> None:
        """
        Open dialog window to choose color.
        self.line_color as initial color.
        """


        color: QColor = QColorDialog.getColor(initial=QColor(self.line_color))
        if color.isValid():
            self.line_color = color.name()
    
    def __add_series__(self) -> None:
        """"
        Add new data series with all correlated information about data to self.series
        """
        ls = self.line_style_spin.currentText()
        if ls == "Nothing":
            ls = ""
        series: dict = {
            'id': self.current_data_index,
            'x': self.data_combo_x.currentText(),
            'xerr': self.data_combo_xerr.currentText(),
            'y': self.data_combo_y.currentText(),
            'yerr': self.data_combo_yerr.currentText(),
            'color': self.standart_colors[self.current_data_index],
            'width': self.line_width.value(),
            'label': f"{self.data_combo_y.currentText()}({self.data_combo_x.currentText()})",
            "ls": ls,
            "alpha": 1.0,
            "marker": "o",
            "marker size": 3
        }
        self.color = self.standart_colors[self.current_data_index]
        self.current_data_index += 1
        self.series.append(series)
        self.series_list.addItem(f"{series['x']} vs {series['y']}")
    
    def __remove_series__(self) -> None:
        """"
        Remove selected data series with all correlated information about data from self.series
        """
        

        if self.series_list.currentRow() >= 0:
            self.series.pop(self.series_list.currentRow())
            self.series_list.takeItem(self.series_list.currentRow())
    
    def get_series(self) -> list[dict]:
        """
        Return all data series that have been added to this subplot.
        """

        return self.series

    def get_axes_info(self) -> dict:
        """
        Return subplot information
        """


        return {"x-label": self.x_line_edit.text(),
                "x min": 0,
                "x max": 1,
                "x ticks": 10,
                "x small ticks": 5,
                "x label fs": 14,
                "x scale": 0,
                "x round accuracy": 1,
                "y-label":self.data_combo_y.currentText(),
                "y min": 0,
                "y max": 1,
                "y ticks": 10,
                "y small ticks": 5,
                "y label fs": 14,
                "y scale": 0,
                "y round accuracy": 1,
                }
    
    def get_title_info(self) -> dict:
        return {"title": f"{self.data_combo_y.currentText()}({self.data_combo_x.currentText()})",
                "title fs": 14}


class AxisConfigDialog(QDialog):
    """
    Dialog for configuring axis properties with full styling options:
    - Min/max range values with automatic decimals calculation
    - Axis title/label and font size
    - Number of major and minor tick marks
    - Scale type (linear/log)
    - Rounding digits for labels
    - Applies settings to matplotlib axis and updates subplot configuration
    """

    def __init__(self, axis_type: str, ax: Axes, subplot: dict, parent=None):
        """
        Initialize axis configuration dialog
        
        Args:
            axis_type: 'x' or 'y' axis
            ax: Matplotlib axis object to configure
            subplots_config: Reference to the subplot configuration
            parent: Parent Qt widget
        """
        super().__init__(parent)
        self.ax = ax
        self.axis_type = axis_type
        self.subplot_config = subplot
        self.setWindowTitle(f"{'X' if axis_type == 'x' else 'Y'} Axis Configuration")
        self.setMinimumWidth(400)
        self.__init_dialog_ui__()
    
    def __calculate_decimals__(self, value: float|int) -> int:
        """Calculate appropriate number of decimals based on value magnitude"""
        
        return self.find_first_nonzero_digit(value) + 3
    
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
    
    def __update_decimals__(self) -> None:
        """Update decimals for min/max spinboxes based on current values"""

        shift = (self.max_edit.value() - self.min_edit.value()) / 20

        min_decimals = self.__calculate_decimals__(self.min_edit.value() - shift)
        max_decimals = self.__calculate_decimals__(self.max_edit.value() + shift)
        
        self.min_edit.setDecimals(min_decimals)
        self.max_edit.setDecimals(max_decimals)
        
        # Update single step based on value magnitude
        min_step = 10 ** -min_decimals
        max_step = 10 ** -max_decimals
        
        self.min_edit.setSingleStep(min_step)
        self.max_edit.setSingleStep(max_step)
    
    def __init_dialog_ui__(self) -> None:
        """Initialize UI for axis configuration dialog"""
        layout = QVBoxLayout(self)
        
        # Create scroll area for better handling of many options
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        
        
        if self.subplot_config is None:
            QMessageBox.warning(self, "Error", "Subplot configuration not found!")
            self.reject()
            return
        
        # Get axis configuration from subplot
        axes_config = self.subplot_config[6]["axes"]
        
        # Get current axis values
        if self.axis_type == 'x':
            min_val = axes_config["x min"]
            max_val = axes_config["x max"]
            title = axes_config["x-label"]
            scale_type = "Logarithmic" if axes_config["x scale"] else "Linear"
            major_ticks = axes_config["x ticks"]
            minor_ticks = axes_config["x small ticks"]
            rounding_digits = axes_config["x number of rounding digits"]
            title_font_size = axes_config["x label fs"]
        else:
            min_val = axes_config["y min"]
            max_val = axes_config["y max"]
            title = axes_config["y-label"]
            scale_type = "Logarithmic" if axes_config["y scale"] else "Linear"
            major_ticks = axes_config["y ticks"]
            minor_ticks = axes_config["y small ticks"]
            rounding_digits = axes_config["y number of rounding digits"]
            title_font_size = axes_config["y label fs"]
        
        # Axis title
        self.title_edit = QLineEdit(title)
        form_layout.addRow("Title:", self.title_edit)
        
        # Title font size
        self.title_font_size = QSpinBox()
        self.title_font_size.setRange(6, 24)
        self.title_font_size.setValue(title_font_size)
        form_layout.addRow("Title Font Size:", self.title_font_size)
        
        # Min value
        self.min_edit = QDoubleSpinBox()
        self.min_edit.setRange(-1e9, 1e9)
        self.min_edit.setValue(min_val)
        self.min_edit.valueChanged.connect(self.__update_decimals__)
        form_layout.addRow("Minimum:", self.min_edit)
        
        # Max value
        self.max_edit = QDoubleSpinBox()
        self.max_edit.setRange(-1e9, 1e9)
        self.max_edit.setValue(max_val)
        self.max_edit.valueChanged.connect(self.__update_decimals__)
        form_layout.addRow("Maximum:", self.max_edit)
        
        # Set initial decimals
        self.__update_decimals__()
        
        # Number of major ticks
        self.major_ticks_spin = QSpinBox()
        self.major_ticks_spin.setRange(2, 100)
        self.major_ticks_spin.setValue(major_ticks)
        form_layout.addRow("Major Ticks:", self.major_ticks_spin)
        
        # Number of minor ticks
        self.minor_ticks_spin = QSpinBox()
        self.minor_ticks_spin.setRange(0, 10)
        self.minor_ticks_spin.setValue(minor_ticks)
        form_layout.addRow("Minor Ticks:", self.minor_ticks_spin)
        
        # Scale type
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Linear", "Logarithmic"])
        self.scale_combo.setCurrentText(scale_type)
        form_layout.addRow("Scale:", self.scale_combo)
        
        # Rounding digits
        self.rounding_spin = QSpinBox()
        self.rounding_spin.setRange(0, 10)
        self.rounding_spin.setValue(rounding_digits)
        form_layout.addRow("Rounding Digits:", self.rounding_spin)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.__accept_new_axes_info__)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def __accept_new_axes_info__(self):
        """Validate and apply new axis configuration"""
        try:
            # Get all values
            min_val = self.min_edit.value()
            max_val = self.max_edit.value()
            title = self.title_edit.text()
            title_font_size = self.title_font_size.value()
            major_ticks = self.major_ticks_spin.value()
            minor_ticks = self.minor_ticks_spin.value()
            scale_type = self.scale_combo.currentIndex()
            rounding_digits = self.rounding_spin.value()
            
            # Validate values
            if min_val >= max_val:
                QMessageBox.warning(self, "Error", "Minimum value must be less than maximum.")
                return
            
            if major_ticks < 2:
                QMessageBox.warning(self, "Error", "Must have at least 2 major ticks.")
                return
            if scale_type and min_val <= 0:
                QMessageBox.warning(self, "Error", "Min value has to be more than zero for log scaling.")
                return

            # Update subplot configuration
    
            if self.axis_type == 'x':
                self.subplot_config[6]["axes"]["x min"] = min_val
                self.subplot_config[6]["axes"]["x max"] = max_val
                self.subplot_config[6]["axes"]["x-label"] = title
                self.subplot_config[6]["axes"]["x label fs"] = title_font_size
                self.subplot_config[6]["axes"]["x ticks"] = major_ticks
                self.subplot_config[6]["axes"]["x small ticks"] = minor_ticks
                self.subplot_config[6]["axes"]["x scale"] = scale_type
                self.subplot_config[6]["axes"]["x number of rounding digits"] = rounding_digits
            else:
                self.subplot_config[6]["axes"]["y min"] = min_val
                self.subplot_config[6]["axes"]["y max"] = max_val
                self.subplot_config[6]["axes"]["y-label"] = title
                self.subplot_config[6]["axes"]["y label fs"] = title_font_size
                self.subplot_config[6]["axes"]["y ticks"] = major_ticks
                self.subplot_config[6]["axes"]["y small ticks"] = minor_ticks
                self.subplot_config[6]["axes"]["y scale"] = scale_type
                self.subplot_config[6]["axes"]["y number of rounding digits"] = rounding_digits
            
            super().accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")

    def get_data(self) -> dict:
        return self.subplot_config


class SubplotPositionDialog(QDialog):
    """
    Dialog for modifying subplot position/size:
    - Adjusts grid location and span
    - Validates against grid boundaries
    - Checks for overlaps with existing subplots
    """


    def __init__(self, base_info: list[int], subs: list, max_row: int, max_col: int, parent=None):
        """
        Initialize subplot position dialog
        
        Args:
            base_info: Current subplot config (row, col, spans, id)
            subs: List of all subplot configurations
            max_row: Maximum grid rows
            max_col: Maximum grid columns
            parent: Parent Qt widget
        """


        super().__init__(parent)
        self.__init_all_sub_config(subs=subs, max_row=max_row, max_col=max_col, base_info=base_info)
        self.__init_dialog_window__()
        self.__init_dialog_ui__()
    
    def __init_all_sub_config(self, subs: list, max_row: int, max_col: int, base_info: list) -> None:
        """Initialize all needed information."""


        self.subs: list = subs
        self.max_row: int = max_row
        self.max_col: int = max_col
        self.id: int = base_info[4]
        self.base_info: list = base_info[:-1]

    def __init_dialog_window__(self) -> None:
        """Initialize dialog window for subplot poisitioning dialog."""


        self.setWindowTitle(f"Change subplot {self.id} configuration")

    def __init_dialog_ui__(self) -> None:
        """Initialize UI for subplot poisitioning dialog window"""

        #main layout        
        layout = QGridLayout()
        self.setLayout(layout)
        
        #Subplot position
        layout.addWidget(QLabel("Row position:"), 0, 0)
        self.row_spin = QSpinBox()
        self.row_spin.setRange(0, 7)
        self.row_spin.setValue(self.base_info[0])
        layout.addWidget(self.row_spin, 0, 1)
        
        layout.addWidget(QLabel("Column position:"), 0, 2)
        self.col_spin = QSpinBox()
        self.col_spin.setRange(0, 7)
        self.col_spin.setValue(self.base_info[1])
        layout.addWidget(self.col_spin, 0, 3)
        
        #subplot size
        layout.addWidget(QLabel("Row Span:"), 1, 0)
        self.row_span_spin = QSpinBox()
        self.row_span_spin.setRange(1, 8)
        self.row_span_spin.setValue(self.base_info[2])
        layout.addWidget(self.row_span_spin, 1, 1)
        
        layout.addWidget(QLabel("Col Span:"), 1, 2)
        self.col_span_spin = QSpinBox()
        self.col_span_spin.setRange(1, 8)
        self.col_span_spin.setValue(self.base_info[3])
        layout.addWidget(self.col_span_spin, 1, 3)

        #Dialog button
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(self.button_box, 2, 0, 1, 2)
        self.button_box.accepted.connect(self.validate_input)
        self.button_box.rejected.connect(self.reject)

    def __validate_col__(self) -> bool:
        """ Validate entered column position. Column and column span are counted.
        true if invalide col (col_span), false if valide col(col_span).
        """


        return self.row_spin.value() + self.row_span_spin.value() > self.max_row
    
    def __validate_row__(self) -> bool:
        """ Validate entered row position. Row and row span are counted.
        true if invalide row (row_span), false if valide row(row_span).
        """


        return self.col_spin.value() + self.col_span_spin.value() > self.max_col
    
    def __rectangles_overlap__(self, rect1, rect2) -> bool:
        """Check if two rectangles overlap."""


        r1_row, r1_col, r1_row_span, r1_col_span = rect1
        r2_row, r2_col, r2_row_span, r2_col_span = rect2
        return not (r1_col + r1_col_span <= r2_col or 
                   r1_col >= r2_col + r2_col_span or 
                   r1_row + r1_row_span <= r2_row or 
                   r1_row >= r2_row + r2_row_span)
    
    def validate_ovelaps(self):
        """Check if current subplot overlaps wit other subplots."""


        for subplot in self.subs:
            s_id, s_row, s_col, s_row_span, s_col_span, *_ = subplot
            if s_id == self.id:
                continue
            if self.__rectangles_overlap__(
                (self.row_spin.value(), self.col_spin.value(), self.row_span_spin.value(), self.col_span_spin.value()),
                (s_row, s_col, s_row_span, s_col_span)
            ):
                return True #overlaps
        return False #there are now overlaps
        
    def validate_input(self):
        """Validate all data entered in dialog window."""


        if self.__validate_col__():
            QMessageBox.warning(self, "Invalid Position", 
                                f"Row span exceeds grid height (max row: {self.max_row-1})")
        elif self.__validate_row__():
            QMessageBox.warning(self, "Invalid Position", 
                                f"Column span exceeds grid width (max col: {self.max_col-1})")
        elif self.validate_ovelaps():
            QMessageBox.warning(self, "Overlap Detected", 
                                "This position overlaps with another subplot")
        else:
            self.accept() 
    
    def get_data(self):
        """Return new subplot poisition and size."""


        return (self.row_spin.value(), self.row_span_spin.value(), self.col_spin.value(), self.col_span_spin.value())


class LegendConfigDialog(QDialog):
    def __init__(self, ax, subplot_config, parent=None):
        super().__init__(parent)
        self.ax = ax
        self.subplot_config = subplot_config
        self.setWindowTitle("Setting up a Legend")
        layout = QFormLayout(self)
        
        self.position_combo = QComboBox()
        self.position_combo.addItems(['best', 'upper right', 'upper left', 'lower left', 
                                      'lower right', 'right', 'center left', 'center right', 
                                      'lower center', 'upper center', 'center'])
        
        # Get current values from subplot_config
        legend_config = self.subplot_config[6]["legend"]
        current_position = legend_config.get("legend position", "best")
        current_font_size = legend_config.get("legend fs", 14)
        
        self.position_combo.setCurrentText(current_position)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 24)
        self.font_size_spin.setValue(current_font_size)
        
        layout.addRow("Position:", self.position_combo)
        layout.addRow("Font size:", self.font_size_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.__accept_new_legend_info__)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def __accept_new_legend_info__(self):
        legend_config = self.subplot_config[6]["legend"]
        legend_config["legend position"] = self.position_combo.currentText()
        legend_config["legend fs"] = self.font_size_spin.value()
        self.accept()

    def get_data(self):
        return self.subplot_config

class TitleConfigDialog(QDialog):
    def __init__(self, ax, subplot_config, parent=None):
        super().__init__(parent)
        self.ax = ax
        self.subplot_config = subplot_config
        self.setWindowTitle("Configuring the title")
        layout = QFormLayout(self)
        
        # Get current values from subplot_config
        title_config = self.subplot_config[6]["title"]
        current_title = title_config.get("title", "")
        current_font_size = title_config.get("title fs", 14)
        
        self.title_edit = QLineEdit(current_title)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 24)
        self.font_size_spin.setValue(current_font_size)
        
        layout.addRow("Title:", self.title_edit)
        layout.addRow("Font size:", self.font_size_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.__accept_new_title_info__)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def __accept_new_title_info__(self):
        title_config = self.subplot_config[6]["title"]
        title_config["title"] = self.title_edit.text()
        title_config["title fs"] = self.font_size_spin.value()
        self.accept()

    def get_data(self):
        return self.subplot_config

# Changes to GridConfigDialog
class GridConfigDialog(QDialog):
    def __init__(self, subplot_config, parent=None):
        super().__init__(parent)
        self.subplot_config = subplot_config
        self.setWindowTitle("Setting up the Grid")
        layout = QVBoxLayout(self)
        
        # Get current value from subplot_config
        grid_config = self.subplot_config[6]["grid"]
        current_grid_state = grid_config.get("show grid", True)
        
        self.grid_checkbox = QCheckBox("Show the grid")
        self.grid_checkbox.setChecked(current_grid_state)
        layout.addWidget(self.grid_checkbox)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.__accept_new_grid_info__)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def __accept_new_grid_info__(self):
        grid_config = self.subplot_config[6]["grid"]
        grid_config["show grid"] = self.grid_checkbox.isChecked()
        self.accept()

    def get_data(self):
        return self.subplot_config

class LineLabelDialog(QDialog):


    def __init__(self, line_params, parent=None):
        super().__init__(parent)
        self.line_params = line_params
        self.setWindowTitle("Line Label Configuration")
        layout = QFormLayout(self)
        
        # Get current values from line_params
        current_text = self.line_params.get('label', "")
        current_position = self.line_params.get('label_position', "Above the middle of the line")
        current_font_size = self.line_params.get('label_font_size', 10)
        
        # Text input
        self.text_edit = QLineEdit(current_text)
        layout.addRow("Label Text:", self.text_edit)
        
        # Position selection
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "Top Center", "Top Left", "Top Right",
            "Bottom Center", "Bottom Left", "Bottom Right",
            "Middle Left", "Middle Right"
        ])
        self.position_combo.setCurrentText(current_position)
        layout.addRow("Position:", self.position_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 24)
        self.font_size_spin.setValue(current_font_size)
        layout.addRow("Font Size:", self.font_size_spin)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.__accept_new_label_info__)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def __accept_new_label_info__(self):
        self.line_params['label'] = self.text_edit.text()
        self.line_params['label_position'] = self.position_combo.currentText()
        self.line_params['label_font_size'] = self.font_size_spin.value()
        self.accept()

    def get_data(self):
        return self.line_params
    def __init__(self, parent=None):
        """
        Dialog for configuring line labels:
        - Text content
        - Position relative to line
        - Font size
        """
        super().__init__(parent)
        self.setWindowTitle("Line Label Configuration")
        layout = QFormLayout(self)
        
        # Text input
        self.text_edit = QLineEdit()
        layout.addRow("Label Text:", self.text_edit)
        
        # Position selection
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "Top Center", "Top Left", "Top Right",
            "Bottom Center", "Bottom Left", "Bottom Right",
            "Middle Left", "Middle Right"
        ])
        layout.addRow("Position:", self.position_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 24)
        self.font_size_spin.setValue(10)
        layout.addRow("Font Size:", self.font_size_spin)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_text(self):
        """Get entered label text"""
        return self.text_edit.text()
    
    def get_position(self):
        """Get selected label position"""
        return self.position_combo.currentText()
    
    def get_font_size(self):
        """Get selected font size"""
        return self.font_size_spin.value()
    

class DataStyleDialog(QDialog):
    """Dialog for editing data series style properties"""
    
    def __init__(self, series_data, parent=None):
        super().__init__(parent)
        self.series_data = series_data.copy()  # Make a copy for editing
        self.setWindowTitle("Edit Data Style")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create tab widget similar to DataStyleTab
        self.tabs = QTabWidget()
        
        # Basic style settings
        self.style_tab = QWidget()
        self.setup_style_tab()
        self.tabs.addTab(self.style_tab, "Style")
        
        # Line settings
        self.line_tab = QWidget()
        self.setup_line_tab()
        self.tabs.addTab(self.line_tab, "Line")
        
        # Marker settings
        self.marker_tab = QWidget()
        self.setup_marker_tab()
        self.tabs.addTab(self.marker_tab, "Marker")
        
        layout.addWidget(self.tabs)
        
        # OK/Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Populate fields with current values
        self.populate_fields()

    def setup_style_tab(self):
        """Setup the style tab with basic styling options"""
        layout = QFormLayout(self.style_tab)
        
        # Label
        self.label_edit = QLineEdit()
        layout.addRow("Label:", self.label_edit)
        
        # Color
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.clicked.connect(self.choose_color)
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(24, 24)
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.color_button)
        layout.addRow("Color:", color_layout)
        
        # Alpha
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.0, 1.0)
        self.alpha_spin.setSingleStep(0.1)
        layout.addRow("Alpha:", self.alpha_spin)

    def setup_line_tab(self):
        """Setup the line tab with line styling options"""
        layout = QFormLayout(self.line_tab)
        
        # Line width
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 10.0)
        self.width_spin.setSingleStep(0.1)
        layout.addRow("Width:", self.width_spin)
        
        # Line style
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Solid", "Dashed", "Dotted", "DashDot", "None"])
        layout.addRow("Style:", self.style_combo)

    def setup_marker_tab(self):
        """Setup the marker tab with marker styling options"""
        layout = QFormLayout(self.marker_tab)
        
        # Marker style
        self.marker_combo = QComboBox()
        self.marker_combo.addItems(["None", "Circle", "Square", "Diamond", "Triangle", "Plus", "Cross"])
        layout.addRow("Marker:", self.marker_combo)
        
        # Marker size
        self.marker_size_spin = QSpinBox()
        self.marker_size_spin.setRange(1, 20)
        layout.addRow("Size:", self.marker_size_spin)

    def populate_fields(self):
        """Populate fields with current values from series data"""
        # Fill fields with current values
        self.label_edit.setText(self.series_data.get('label', ''))
        
        # Color
        color = self.series_data.get('color', '#000000')
        self.color_preview.setStyleSheet(f"background-color: {color}; border: 1px solid #888;")
        self.color_button.setText(color)
        
        # Other parameters
        self.alpha_spin.setValue(self.series_data.get('alpha', 1.0))
        self.width_spin.setValue(self.series_data.get('width', 1.0))
        
        # Line style
        style_map = {"-": "Solid", "--": "Dashed", ":": "Dotted", "-.": "DashDot", "": "None"}
        current_style = self.series_data.get('ls', '-')
        self.style_combo.setCurrentText(style_map.get(current_style, "Solid"))
        
        # Marker
        marker_map = {"": "None", "o": "Circle", "s": "Square", "D": "Diamond", "^": "Triangle", "+": "Plus", "x": "Cross"}
        current_marker = self.series_data.get('marker', 'o')
        self.marker_combo.setCurrentText(marker_map.get(current_marker, "Circle"))
        
        self.marker_size_spin.setValue(self.series_data.get('marker size', 5))

    def choose_color(self):
        """Open color dialog to choose a new color"""
        color = QColorDialog.getColor(QColor(self.series_data.get('color', '#000000')), self)
        if color.isValid():
            color_name = color.name()
            self.series_data['color'] = color_name
            self.color_preview.setStyleSheet(f"background-color: {color_name}; border: 1px solid #888;")
            self.color_button.setText(color_name)

    def get_updated_data(self):
        """Get updated series data based on form values"""
        # Update data based on selected values
        self.series_data['label'] = self.label_edit.text()
        self.series_data['alpha'] = self.alpha_spin.value()
        self.series_data['width'] = self.width_spin.value()
        
        # Line style
        style_map_reverse = {"Solid": "-", "Dashed": "--", "Dotted": ":", "DashDot": "-.", "None": ""}
        self.series_data['ls'] = style_map_reverse[self.style_combo.currentText()]
        
        # Marker
        marker_map_reverse = {"None": "", "Circle": "o", "Square": "s", "Diamond": "D", "Triangle": "^", "Plus": "+", "Cross": "x"}
        self.series_data['marker'] = marker_map_reverse[self.marker_combo.currentText()]
        
        self.series_data['marker size'] = self.marker_size_spin.value()
        
        return self.series_data