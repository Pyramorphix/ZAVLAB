"""
Contains all dialog windows used in the application:
- Data series configuration
- Axis configuration
- Subplot positioning
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QPushButton, QComboBox,
                              QDoubleSpinBox, QFormLayout, QDialogButtonBox, QColorDialog, 
                              QLineEdit, QMessageBox, QGridLayout, QSpinBox)
from PyQt6.QtGui import QColor
import numpy as np
from matplotlib.axes import Axes


class DataSeriesDialog(QDialog):
    """
    Dialog for configuring data series in plots:
    - Add/remove multiple data series
    - Set X/Y data columns
    - Configure line styles (color, width)
    """


    def __init__(self, headers: list[str], parent=None) -> None:
        """
        Initialize data series dialog
        
        Args:
            headers: List of available column headers
            parent: Parent Qt widget
        """

        super().__init__(parent)
        self.__init_dialog_window__()
        self.__init_dialog_ui__(headers=headers)

    def __init_dialog_window__(self) -> None:
        """Initialize Dialog window for configuring data series."""
        self.setWindowTitle("Data Series Configuration")

    def __init_dialog_ui__(self, headers: list[str]) -> None:
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
        self.data_combo_y: QComboBox = QComboBox()
        self.data_combo_y.addItems(["None"] + headers)
        
        # Style controls
        self.color_btn: QPushButton = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.__choose_color__)
        self.line_width: QDoubleSpinBox = QDoubleSpinBox()
        self.line_width.setRange(0.1, 5.0)
        self.line_width.setValue(1.0)
        
        #design window
        form: QFormLayout = QFormLayout()
        form.addRow("X Data:", self.data_combo_x)
        form.addRow("Y Data:", self.data_combo_y)
        form.addRow("Line Color:", self.color_btn)
        form.addRow("Line Width:", self.line_width)
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


        series: dict = {
            'x': self.data_combo_x.currentText(),
            'y': self.data_combo_y.currentText(),
            'color': self.line_color,
            'width': self.line_width.value()
        }
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

    def get_subplot_info(self) -> dict:
        """
        Return subplot information
        """


        return {"x-label": self.x_line_edit.text(), "y-label": self.y_line_edit.text()}

    
class AxisConfigDialog(QDialog):
    """
    Dialog for configuring axis properties:
    - Min/max range values
    - Axis title/label
    - Number of tick marks
    - Applies settings to matplotlib axis
    """


    def __init__(self, axis_type: str, ax: Axes, parent=None):
        """
        Initialize axis configuration dialog
        
        Args:
            axis_type: 'x' or 'y' axis
            ax: Matplotlib axis object to configure
            parent: Parent Qt widget
        """


        super().__init__(parent)
        self.__init_dialog_window__(ax=ax, axis_type=axis_type)
        self.__init_dialog_ui__()
    
    def __init_dialog_window__(self, ax: Axes, axis_type: str = 'x') -> None:
        """Initialize Dialog window for configuring data series."""


        self.ax: Axes = ax
        self.axis_type: str = axis_type
        self.setWindowTitle(f"Настройка оси {'X' if axis_type == 'x' else 'Y'}")

    def __init_dialog_ui__(self) -> None:
        """Initialize UI for data series dialog window"""


        #main layout        
        layout = QFormLayout()

        min_val, max_val, title = self.__define_axes_init_info__()

        #Ax boundary values
        self.min_edit = QLineEdit()
        self.min_edit.setText(str(min_val))
        layout.addRow("Minimum:", self.min_edit)
        self.max_edit = QLineEdit()
        self.max_edit.setText(str(max_val))
        layout.addRow("Maximum:", self.max_edit)
        
        #Ax title
        self.title_edit = QLineEdit(title)
        layout.addRow("Title:", self.title_edit)

        #Ax ticks
        self.ticks = QLineEdit()
        self.ticks.setText("2")
        layout.addRow("Number of divisions on the axis:", self.ticks)
        
        #Dialog button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.__accept_new_axes_info__)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        #set main layout
        self.setLayout(layout)

    def __define_axes_init_info__(self) -> tuple[float, float, str]:
        """Define axes initial information"""

        #get x-axis info
        if self.axis_type == 'x':
            min_val, max_val = self.ax.get_xlim()
            title = self.ax.get_xlabel()
        #get y-axis info
        else:
            min_val, max_val = self.ax.get_ylim()
            title = self.ax.get_ylabel() 

        return (min_val, max_val, title)

    def __accept_new_axes_info__(self):
        """Check entered information for correctness"""


        try:
            min_val = float(self.min_edit.text())
            max_val = float(self.max_edit.text())
            ticks = int(self.ticks.text())
            title = self.title_edit.text()
            
            if min_val >= max_val:
                QMessageBox.warning(self, "Error", "The minimum value must be less than the maximum.")
                raise ValueError("The minimum should be less than the maximum.")
            
            if ticks < 0:
                QMessageBox.warning(self, "Error", "The number of divisions must be greater than 0.")
                raise ValueError("The number of divisions must be greater than 0.")
            
            #x-axis configuration
            if self.axis_type == 'x':
                self.ax.yaxis.set_ticks_position("left")
                self.ax.set_xlim(min_val, max_val)
                self.ax.spines["left"].set_position(("data", min_val))
                self.ax.set(xlim=(min_val, max_val))
                self.ax.set_xticks(np.linspace(min_val, max_val, ticks))
                self.ax.set_xlabel(title)
            
            #y-axis configuration
            else:
                self.ax.xaxis.set_ticks_position("bottom")
                self.ax.set_ylim(min_val, max_val)
                self.ax.spines["bottom"].set_position(("data", min_val))
                self.ax.set(ylim=(min_val, max_val))
                self.ax.set_yticks(np.linspace(min_val, max_val, ticks))
                self.ax.set_ylabel(title)

            self.ax.figure.canvas.draw()
            super().accept()

        except Exception as e:
            QMessageBox.warning(self, "Error", "Make sure that the numbers are entered everywhere. In the input field, x, y can be integers or fractional values (separated by dots). The ticks field must contain a positive integer.")
            print(f"Error: {e}")

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

