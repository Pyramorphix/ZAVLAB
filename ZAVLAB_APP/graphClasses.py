from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, 
                             QDialogButtonBox, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QMessageBox, QFrame, 
                             QGridLayout, QWidget, QSplitter, QGroupBox, QSpinBox, QPushButton,
                             QComboBox, QTabWidget, QDoubleSpinBox, QCheckBox, QListWidget, QListWidgetItem,
                             QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import sys
import matplotlib.ticker as ticker
import matplotlib.gridspec as gridspec

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
        self.axes = []
        self.subplots = []
        self.gs = gridspec.GridSpec(
            1, 1, 
            figure=self.fig,
            width_ratios=[1]*1,
            height_ratios=[1]*1,
            wspace=0.5,
            hspace=0.7
        )
        super().__init__(self.fig)
        self.setParent(parent)
        self.canvas = FigureCanvas(self.fig)
        self.data = None

        self.mpl_connect("button_press_event", self.on_click)
        # self.plot_data(data=None,labels=["x", "y"])

    def on_click(self, event):
        if not event.inaxes:
            return
        
        # Определяем, на каком графике произошел клик
        for i, ax in enumerate(self.axes):
            if event.inaxes == ax:
                # Определяем параметры для конкретного графика
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                tolerance = 0.05  # 5% от диапазона
                
                # Клик по оси X (нижняя часть)
                if event.ydata < y_min + tolerance * (y_max - y_min):
                    dialog = AxisConfigDialog('x', ax, self)
                    dialog.exec()
                    return
                
                # Клик по оси Y (левая часть)
                if event.xdata < x_min + tolerance * (x_max - x_min):
                    dialog = AxisConfigDialog('y', ax, self)
                    dialog.exec()
                    return
    
    def plot_data(self, win, rows_spin, cols_spin):
        """Generate the plot based on current configuration"""
        if not self.subplots:
            QMessageBox.warning(self, "No Subplots", "Please add at least one subplot")
            return
        rows = rows_spin
        cols = cols_spin
        
        # Create GridSpec
        self.gs = gridspec.GridSpec(
            rows, cols, 
            figure=self.fig,
            width_ratios=[1]*cols,
            height_ratios=[1]*rows,
            wspace=0.5,
            hspace=0.7
        )
        # Create a grid to track occupied cells
        occupied = [[False] * cols for _ in range(rows)]

        # Create axes for each subplot
        for subplot in self.subplots:
            plot_id, s_row, s_col, s_row_span, s_col_span, *_ = subplot
            ax = self.fig.add_subplot(self.gs[s_row:s_row+s_row_span, s_col:s_col+s_col_span])
            self.axes.append(ax)
            self.update_one_plot(subplot, win)
            
            # Mark occupied cells
            for r in range(s_row, s_row+s_row_span):
                for c in range(s_col, s_col+s_col_span):
                    if r < rows and c < cols:
                        occupied[r][c] = True

        # Add empty cells
        for r in range(rows):
            for c in range(cols):
                if not occupied[r][c]:
                    ax = self.fig.add_subplot(self.gs[r, c])
                    ax.text(0.5, 0.5, "Empty Cell", 
                            ha='center', va='center', fontsize=10,
                            transform=ax.transAxes, alpha=0.5)
                    ax.axis('off')
        
        self.fig.tight_layout()
        self.canvas.draw()
        self.draw()
    
    def create_axes(self):
        for subplot in self.subplots:
                plot_id, s_row, s_col, s_row_span, s_col_span, data_x, data_y, color, line_width, show_grid = subplot
                # Create subplot with specified span
                ax = self.fig.add_subplot(self.gs[s_row:s_row+s_row_span, s_col:s_col+s_col_span])
                self.axes.append(ax)
  
    
    def update_one_plot(self, subplot, win):
        plot_id, s_row, s_col, s_row_span, s_col_span, data_x, data_y, color, line_width, show_grid = subplot
        # Create subplot with specified span
        ax = self.axes[plot_id]#self.fig.add_subplot(self.gs[s_row:s_row+s_row_span, s_col:s_col+s_col_span])
        ax.clear()
        # Plot data if selected
        if data_x != "None" and data_y != "None":
            data = win.get_data(data_x, data_y)
            ax.plot(data[0], data[1], linewidth=line_width, color=color)
            ax.set_title(f"Subplot {plot_id}: {data[0][0]}({data[1][0]})", fontsize=10)
            ax.set_xlabel(str(data_x[0]))
            ax.set_ylabel(str(data_y[0]))
        if show_grid:
            #ax.grid(True, linestyle='--', alpha=0.7)
            ax.grid(color="#7a7c7d", linewidth=0.3)
            ax.grid(which='minor', color='#7a7c7d', linestyle=':', linewidth=0.2)
        else:
            ax.text(0.5, 0.5, f"Subplot {plot_id}", 
                    ha='center', va='center', fontsize=12,
                    transform=ax.transAxes)
            ax.set_title(f"Subplot {plot_id}", fontsize=10)
        ax.minorticks_on()
        ax.tick_params(axis='x', length=4, width=2, labelsize=14, direction ='in')
        ax.tick_params(axis='y', length=4, width=2, labelsize=14, direction ='in')
        ax.tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black')
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        ax.tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black')
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        return ax

class SubplotEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Sample datasets
        self.datasets = {
            "Sine Wave": np.sin(np.linspace(0, 4 * np.pi, 100)),
            "Cosine Wave": np.cos(np.linspace(0, 4 * np.pi, 100)),
            "Random Walk": np.random.randn(100).cumsum(),
            "Quadratic": np.square(np.linspace(-2, 2, 100)),
            "Exponential": np.exp(np.linspace(0, 2, 100)),
            "Logarithm": np.log(np.linspace(1, 10, 100)),
            "Sawtooth": np.linspace(0, 1, 100) % 0.2 * 5,
            "Linear": np.linspace(0, 10, 100),
            "Square Wave": np.sign(np.sin(np.linspace(0, 4 * np.pi, 100)))
        }
        
        # Initialize UI
        self.initUI()
        
        # Current subplot configuration
        self.subplots = []  # [id, row, col, row_span, col_span, data, properties]
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
        creation_layout = QGridLayout()
        creation_group.setLayout(creation_layout)
        
        creation_layout.addWidget(QLabel("Row position:"), 0, 0)
        self.row_spin = QSpinBox()
        self.row_spin.setRange(0, 7)
        creation_layout.addWidget(self.row_spin, 0, 1)
        
        creation_layout.addWidget(QLabel("Column position:"), 0, 2)
        self.col_spin = QSpinBox()
        self.col_spin.setRange(0, 7)
        creation_layout.addWidget(self.col_spin, 0, 3)
        
        creation_layout.addWidget(QLabel("Row Span:"), 1, 0)
        self.row_span_spin = QSpinBox()
        self.row_span_spin.setRange(1, 8)
        self.row_span_spin.setValue(1)
        creation_layout.addWidget(self.row_span_spin, 1, 1)
        
        creation_layout.addWidget(QLabel("Col Span:"), 1, 2)
        self.col_span_spin = QSpinBox()
        self.col_span_spin.setRange(1, 8)
        self.col_span_spin.setValue(1)
        creation_layout.addWidget(self.col_span_spin, 1, 3)
        
        creation_layout.addWidget(QLabel("Data x:"), 2, 0)
        self.data_combo_x = QComboBox()
        self.data_combo_x.addItems(["None"])
        creation_layout.addWidget(self.data_combo_x, 2, 1, 1, 3)
        creation_layout.addWidget(QLabel("Data y:"), 3, 0)
        self.data_combo_y = QComboBox()
        self.data_combo_y.addItems(["None"])
        creation_layout.addWidget(self.data_combo_y, 3, 1, 1, 3)
        
        self.add_subplot_btn = QPushButton("Add Subplot")
        self.add_subplot_btn.clicked.connect(self.add_subplot)
        creation_layout.addWidget(self.add_subplot_btn, 4, 0, 1, 2)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_subplots)
        creation_layout.addWidget(self.clear_btn, 4, 2, 1, 2)
        
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
        
        data_layout.addWidget(QLabel("Data x:"))
        self.edit_data_combo_x = QComboBox()
        self.edit_data_combo_x.addItems(["None"])
        data_layout.addWidget(self.edit_data_combo_x)

        data_layout.addWidget(QLabel("Data y:"))
        self.edit_data_combo_y = QComboBox()
        self.edit_data_combo_y.addItems(["None"])
        data_layout.addWidget(self.edit_data_combo_y)

        self.update_data_btn = QPushButton("Update Data")
        self.update_data_btn.clicked.connect(self.update_subplot_data)
        data_layout.addWidget(self.update_data_btn)
        
        self.editor_tabs.addTab(data_tab, "Data")
        
        # Styling tab
        style_tab = QWidget()
        style_layout = QFormLayout(style_tab)
        
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
        self.update_style_btn.clicked.connect(self.update_subplot_style)
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
            s_row, s_col, s_row_span, s_col_span, _, _, _ = subplot[1:8]
            
            # Check if rectangles overlap
            if self.rectangles_overlap(
                (row, col, row_span, col_span),
                (s_row, s_col, s_row_span, s_col_span)
            ):
                QMessageBox.warning(self, "Overlap Detected", 
                                    "This subplot overlaps with an existing one")
                return
        
        # Add subplot
        plot_id = self.current_plot_id
        self.plot_canvas.subplots.append([
            plot_id,
            row,
            col,
            row_span,
            col_span,
            self.data_combo_x.currentText(),  # Data
            self.data_combo_y.currentText(),  # Data
            self.line_color,  # Line color
            1.0,  # Line width
            True   # Show grid
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
            plot_id, row, col, row_span, col_span, data_x, data_y, _, _, _ = subplot
            item = QListWidgetItem(f"Subplot {plot_id}: {row},{col} [{row_span}x{col_span}] - {data_x}, {data_y}")
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
                _, row, col, row_span, col_span, data_x, data_y, color, line_width, show_grid = subplot
                self.edit_row_spin.setValue(row)
                self.edit_col_spin.setValue(col)
                self.edit_row_span_spin.setValue(row_span)
                self.edit_col_span_spin.setValue(col_span)
                
                # Populate data controls
                self.edit_data_combo_x.setCurrentText(data_x)
                self.edit_data_combo_y.setCurrentText(data_y)
                
                # Populate style controls
                self.line_width_spin.setValue(line_width)
                self.grid_checkbox.setChecked(show_grid)
                self.line_color = color
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
            QMessageBox.warning(self, "Invalid Position", 
                                f"Row span exceeds grid height (max row: {max_rows-1})")
            return
            
        if new_col + new_col_span > max_cols:
            QMessageBox.warning(self, "Invalid Position", 
                                f"Column span exceeds grid width (max col: {max_cols-1})")
            return
            
        # Check for overlaps with other subplots
        for subplot in self.plot_canvas.subplots:
            s_id, s_row, s_col, s_row_span, s_col_span, _, _, _, _ = subplot
            if s_id == self.selected_subplot_id:
                continue
                
            if self.rectangles_overlap(
                (new_row, new_col, new_row_span, new_col_span),
                (s_row, s_col, s_row_span, s_col_span)
            ):
                QMessageBox.warning(self, "Overlap Detected", 
                                    "This position overlaps with another subplot")
                return
        
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
                self.plot_canvas.subplots[i][5] = new_data_x
                self.plot_canvas.subplots[i][6] = new_data_y
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
    
    def update_subplot_style(self):
        """Update the style properties for a subplot"""
        if self.selected_subplot_id is None:
            return
            
        new_color = self.line_color
        new_width = self.line_width_spin.value()
        new_grid = self.grid_checkbox.isChecked()
        
        # Update the subplot
        for i, subplot in enumerate(self.plot_canvas.subplots):
            if subplot[0] == self.selected_subplot_id:
                self.plot_canvas.subplots[i][7] = new_color
                self.plot_canvas.subplots[i][8] = new_width
                self.plot_canvas.subplots[i][9] = new_grid
                self.plot_canvas.update_one_plot(subplot, self.window())
                self.plot_canvas.canvas.draw()
                self.plot_canvas.draw()
                break
    
    # Updated plot_graphs method in the SubplotEditor class
    def plot_graphs(self):
        self.plot_canvas.fig.clear()
        self.plot_canvas.canvas.draw()
        self.plot_canvas.plot_data(self.window(),  self.rows_spin.value(), self.cols_spin.value())
        # """Generate the plot based on current configuration"""
        # if not self.plot_canvas.subplots:
        #     QMessageBox.warning(self, "No Subplots", "Please add at least one subplot")
        #     return
            
        # self.plot_canvas.fig.clear()
        
        # rows = self.rows_spin.value()
        # cols = self.cols_spin.value()
        
        # # Create GridSpec
        # gs = gridspec.GridSpec(
        #     rows, cols, 
        #     figure=self.plot_canvas.fig,
        #     width_ratios=[1]*cols,
        #     height_ratios=[1]*rows,
        #     wspace=0.5,
        #     hspace=0.7
        # )
        
        # # Create axes for each subplot
        # for subplot in self.plot_canvas.subplots:
        #     plot_id, s_row, s_col, s_row_span, s_col_span, data_x, data_y, color, line_width, show_grid = subplot
            
        #     # Create subplot with specified span
        #     ax = self.plot_canvas.fig.add_subplot(gs[s_row:s_row+s_row_span, s_col:s_col+s_col_span])
            
        #     # Plot data if selected
        #     if data_x != "None":
        #         data = self.window().get_data(data_x, data_y)
        #         ax.plot(data[0], data[1], linewidth=line_width, color=color)
        #         ax.set_title(f"Subplot {plot_id}: {data[0][0]}({data[1][0]})", fontsize=10)
        #         if show_grid:
        #             ax.grid(True, linestyle='--', alpha=0.7)
        #     else:
        #         ax.text(0.5, 0.5, f"Subplot {plot_id}", 
        #                 ha='center', va='center', fontsize=12,
        #                 transform=ax.transAxes)
        #         ax.set_title(f"Subplot {plot_id}", fontsize=10)
        
        # # Add descriptive text for empty grid cells
        # for r in range(rows):
        #     for c in range(cols):
        #         cell_occupied = False
        #         for subplot in self.plot_canvas.subplots:
        #             # CORRECTED UNPACKING HERE
        #             plot_id, s_row, s_col, s_row_span, s_col_span, *_ = subplot
        #             if (s_row <= r < s_row + s_row_span and 
        #                 s_col <= c < s_col + s_col_span):
        #                 cell_occupied = True
        #                 break
                
        #         if not cell_occupied:
        #             ax = self.plot_canvas.fig.add_subplot(gs[r, c])
        #             ax.text(0.5, 0.5, "Empty Cell", 
        #                     ha='center', va='center', fontsize=10,
        #                     transform=ax.transAxes, alpha=0.5)
        #             ax.axis('off')
        
        # self.plot_canvas.fig.tight_layout()
        # self.plot_canvas.canvas.draw()
