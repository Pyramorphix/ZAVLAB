from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import sys


class PREPARE_DATA(QDialog):
    """Диалоговое окно для ввода данных"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбрать данные для графика")
        self.setFixedSize(400, 200)
        
        # Создаем элементы формы
        self.explanation = QLabel("Введите номера столбцов,\n которые будут соответсвовать x и y координате.")
        self.x_axis = QLineEdit()
        self.y_axis = QLineEdit()
        self.lenght = QLineEdit()
        # Создаем кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Размещаем элементы в layout
        layout = QVBoxLayout()
        col_x = QHBoxLayout()
        col_y = QHBoxLayout()
        lenght = QHBoxLayout()

        col_x.addWidget(QLabel("x-axis:"), 20)
        col_x.addWidget(self.x_axis, 80)
        col_y.addWidget(QLabel("y-axis:"), 20)
        col_y.addWidget(self.y_axis, 80)
        lenght.addWidget(QLabel("number of data to plot:"), 20)
        lenght.addWidget(self.lenght, 80)
        layout.addWidget(self.explanation)
        layout.addLayout(col_x)
        layout.addLayout(col_y)
        layout.addLayout(lenght)
        layout.addWidget(button_box)       
        self.setLayout(layout)
    
    def get_inputs(self):
        """Возвращает введенные значения"""
        return (
            self.x_axis.text(),
            self.y_axis.text(),
            self.lenght.text(),
        )

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

class INTERACTIVE_PLOT(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, data=[]):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = None
        super().__init__(self.fig)
        self.setParent(parent)

        self.data = None

        self.mpl_connect("button_press_event", self.on_click)
        # self.plot_data(data=None,labels=["x", "y"])

    def on_click(self, event):
        if not event.inaxes:
            return
        
        x, y = event.xdata, event.ydata

        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        x_threshold = 0.2 * (x_max - x_min)
        y_threshold = 0.2 * (y_max - y_min)

        if y is not None and y < y_min + y_threshold:
            dialog = AxisConfigDialog('x', self.ax, self)
            dialog.exec()
            return
        
        # Проверяем клик по оси Y (левая часть)
        if x is not None and x < x_min + x_threshold:
            dialog = AxisConfigDialog('y', self.ax, self)
            dialog.exec()
            return
    
    def plot_data(self, data, labels):
        self.ax = self.figure.subplots()
        if data is not None:
            self.data = data
            self.ax.plot(self.data[0], self.data[1])
        self.ax.set_xlabel(labels[0])
        self.ax.set_ylabel(labels[1])
        self.ax.set_title("Here will be your title.")
        self.draw()
