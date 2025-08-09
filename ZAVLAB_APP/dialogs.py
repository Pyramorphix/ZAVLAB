"""
Contains all dialog windows used in the application:
- Data selection dialogs
- Axis configuration
- Subplot positioning
- Data series configuration
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QPushButton, QComboBox,
                              QDoubleSpinBox, QFormLayout, QDialogButtonBox, QColorDialog, 
                              QLineEdit, QMessageBox)
from PyQt6.QtGui import QColor
import numpy as np


class DataSeriesDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Series Configuration")
        layout = QVBoxLayout()
        
        # Data series list
        self.series_list = QListWidget()
        layout.addWidget(QLabel("Data Series:"))
        layout.addWidget(self.series_list)
        
        # Controls
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.add_btn.clicked.connect(self.add_series)
        self.remove_btn = QPushButton("-")
        self.remove_btn.clicked.connect(self.remove_series)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)
        
        # Data selection
        self.data_combo_x = QComboBox()
        self.data_combo_x.addItems(["None"] + headers)
        self.data_combo_y = QComboBox()
        self.data_combo_y.addItems(["None"] + headers)
        
        # Style controls
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        self.line_width = QDoubleSpinBox()
        self.line_width.setRange(0.1, 5.0)
        self.line_width.setValue(1.0)
        
        form = QFormLayout()
        form.addRow("X Data:", self.data_combo_x)
        form.addRow("Y Data:", self.data_combo_y)
        form.addRow("Line Color:", self.color_btn)
        form.addRow("Line Width:", self.line_width)
        layout.addLayout(form)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.line_color = "#1f77b4"
        self.series = []
    
    def choose_color(self):
        color = QColorDialog.getColor(initial=QColor(self.line_color))
        if color.isValid():
            self.line_color = color.name()
    
    def add_series(self):
        series = {
            'x': self.data_combo_x.currentText(),
            'y': self.data_combo_y.currentText(),
            'color': self.line_color,
            'width': self.line_width.value()
        }
        self.series.append(series)
        self.series_list.addItem(f"{series['x']} vs {series['y']}")
    
    def remove_series(self):
        if self.series_list.currentRow() >= 0:
            self.series.pop(self.series_list.currentRow())
            self.series_list.takeItem(self.series_list.currentRow())
    
    def get_series(self):
        return self.series
    
class AxisConfigDialog(QDialog):
    def __init__(self, axis_type, ax, parent=None):
        super().__init__(parent)
        self.ax = ax
        self.axis_type = axis_type
        self.setWindowTitle(f"Настройка оси {'X' if axis_type == 'x' else 'Y'}")
        
        layout = QFormLayout()

        if axis_type == 'x':
            min_val, max_val = ax.get_xlim()
            title = ax.get_xlabel()
        else:
            min_val, max_val = ax.get_ylim()
            title = ax.get_ylabel() 

        self.min_edit = QLineEdit()
        self.min_edit.setText(str(min_val))
        layout.addRow("Минимум:", self.min_edit)
        
        self.max_edit = QLineEdit()
        self.max_edit.setText(str(max_val))
        layout.addRow("Максимум:", self.max_edit)
        
        self.title_edit = QLineEdit(title)
        layout.addRow("Заголовок:", self.title_edit)

        self.ticks = QLineEdit()
        self.ticks.setText("0")
        layout.addRow("Количество делений на оси:", self.ticks)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    def accept(self):
        try:
            min_val = float(self.min_edit.text())
            max_val = float(self.max_edit.text())
            ticks = int(self.ticks.text())
            title = self.title_edit.text()
            
            if min_val >= max_val:
                QMessageBox.warning(self, "Ошибка", "Миниамальное значение должно быть меньше максимального.")
                raise ValueError("Минимум должен быть меньше максимума")
            if ticks < 0:
                QMessageBox.warning(self, "Ошибка", "Количество делений должно быть больше 0.")
                raise ValueError("Количество делений должно быть больше 0.")
            if self.axis_type == 'x':
                self.ax.xaxis.set_ticks_position("bottom")
                self.ax.set_xlim(min_val, max_val)
                self.ax.spines["bottom"].set_position(("data", min_val))
                self.ax.set(xlim=(min_val, max_val))
                self.ax.set_xticks(np.linspace(min_val, max_val, ticks))
                self.ax.set_xlabel(title)
            else:
                self.ax.yaxis.set_ticks_position("left")
                self.ax.set_ylim(min_val, max_val)
                self.ax.spines["left"].set_position(("data", min_val))
                self.ax.set(ylim=(min_val, max_val))
                self.ax.set_yticks(np.linspace(min_val, max_val, ticks))
                self.ax.set_ylabel(title)

            
            self.ax.figure.canvas.draw()
            super().accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", "Проверьте, что везде ввели числа. В поле ввода x, y могу быть целые или дробные значения (написаны через точку). В поле ticks должно быть целое положительное число.")
            print(f"Ошибка: {e}")

