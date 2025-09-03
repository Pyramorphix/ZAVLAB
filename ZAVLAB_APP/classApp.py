from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QTableWidget, QLabel,
                             QHeaderView, QMenu, QMessageBox, QInputDialog, QFileDialog,
                             QTableWidgetItem, QMenuBar, QDialog, QDialogButtonBox, QLineEdit,
                               QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QGridLayout,
                               QSpinBox, QPushButton)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
import csv
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas   
import numpy as np
from plot_manager import SubplotEditor
import json
import os

class ZAVLAB(QMainWindow):
    """Основной класс приложения - главное окно"""
    signals = pyqtSignal(list) 

    def __init__(self) -> None:
        super(ZAVLAB, self).__init__()
        self.setWindowTitle("ZAVLAB")
        self.resize(100, 100)

        #centreal widget
        self.central_widget: QSplitter = QSplitter(Qt.Orientation.Horizontal)

        #make all widgets
        self.setupTable()   
        self.label: QLabel = QLabel("Plot will be here soon!")
        self.setupMenuBar()

        #plotting info

        self.plotter = SubplotEditor()
        self.signals.connect(self.plotter.update_column_data)
        self.plotter.update_column_data([self.table.item(0, col).text() if self.table.item(0, col) else f"Column {col+1}" for col in range(self.table.columnCount())])
        #design
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.table)
        self.central_widget.addWidget(self.plotter)
        self.central_widget.setStretchFactor(0, 1)
        self.central_widget.setStretchFactor(1, 3)

        #set some properties
        self.central_widget.setChildrenCollapsible(False)
        self.central_widget.setHandleWidth(5)

        # styles
        self.central_widget.setStyleSheet("""
            QSplitter::handle:horizontal {
                background-color: #ccc;
                border: 1px solid #999;
                height: 12px;  /* Высота ручки */
                margin: 0px;
            }
        """)

    def setupTable(self) -> None:
        """Инициализация таблицы данных"""
        self.table: QTableWidget = QTableWidget()   
        self.table_headers_h: QHeaderView = self.table.horizontalHeader() 
        self.table_headers_v: QHeaderView = self.table.verticalHeader() 

        self.table.setRowCount(10)
        self.table.setColumnCount(2)
        self.table_headers_h.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_headers_v.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table_headers_h.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_headers_h.customContextMenuRequested.connect(self.tableDroppedHMenu)

        self.table_headers_v.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_headers_v.customContextMenuRequested.connect(self.tableDroppedVMenu)

        self.table_headers_h.sectionCountChanged.connect(self.update_headers)
        self.table_headers_h.geometriesChanged.connect(self.update_headers)

    def setupMenuBar(self) -> None:
        """Создание меню приложения"""
        self.menu_bar: QMenuBar = self.menuBar()
        self.help_menu: QMenu = self.menu_bar.addMenu("Справка")
        self.files: QMenu = self.menu_bar.addMenu("Файл")

        #Справка
        about_action: QAction = QAction("О программе", self)
        about_action.triggered.connect(self._showAbout)
        self.help_menu.addAction(about_action)

        #работа с файлами
        #новый эксперимент
        new_action: QAction = QAction("Новый эксперимент", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._new_file)
        self.files.addAction(new_action)
        
        #сохранить эксперимент
        save_action: QAction = QAction("Сохранить эксперимент", self)
        save_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_action.triggered.connect(self._save_file)
        self.files.addAction(save_action)

        #загрузить эксперимент
        load_action: QAction = QAction("Загрузить эксперимент", self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self._load_data)
        self.files.addAction(load_action)

        # save plots settings
        save_plot_settings = QAction("Save plots settings", self)
        save_action.setShortcut(QKeySequence("Ctrl+S+P"))
        save_plot_settings.triggered.connect(self._save_plot_settings)
        self.files.addAction(save_plot_settings)

        # Import plots settings
        load_plot_settings = QAction("Import plots settings", self)
        save_action.setShortcut(QKeySequence("Ctrl+I"))
        load_plot_settings.triggered.connect(self._load_plot_settings)
        self.files.addAction(load_plot_settings)

        # Save plots images
        save_plot_image = QAction("Save plots image", self)
        save_action.setShortcut(QKeySequence("Ctrl+S+I"))
        save_plot_image.triggered.connect(self._save_plot_image)
        self.files.addAction(save_plot_image)

    def _save_plot_settings(self) -> None:
        """"Saves the graph configuration to a JSON file"""


        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save plots settings",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_name:
            return
        try:
            # Get state from SubplotEditor
            state = self.plotter.get_state()

            # File type
            ext = os.path.splitext(file_name)[1].lower()
            if not ext:
                file_name += ".json"
                ext = ".json"

            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=4)
            
            self.statusBar().showMessage(f"Plots settings are saved: {file_name}", 5000)
            QMessageBox.information(self, "Success", "Plots settings have been successfully exported!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Couldn't save settings:\n{str(e)}")

    def _load_plot_settings(self) -> None:
        """Loads the graph configuration from a JSON file"""


        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Download Plot Settings",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_name:
            return
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # reset status
            self.plotter.set_state(state)
            
            self.statusBar().showMessage(f"Chart settings are loaded: {file_name}", 5000)
            QMessageBox.information(self, "Success", "Chart settings have been uploaded successfully!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings:\n{str(e)}")

    def _save_plot_image(self) -> None:
        """Saves the current graph as an image"""


        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save the graph image",
            "",
            "PNG (*.png);;JPEG (*.jpg);;SVG (*.svg);;PDF (*.pdf);;All Files (*)"
        )
        
        if not file_name:
            return
        
        try:
            # get format of the file
            ext = os.path.splitext(file_name)[1].lower()
            if not ext:
                file_name += ".png"
                ext = ".png"
            
            # save image
            self.plotter.plot_canvas.fig.savefig(file_name, dpi=300)
            
            self.statusBar().showMessage(f"The graph is saved: {file_name}", 5000)
            QMessageBox.information(self, "Success", "The graph has been successfully exported!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"The graph could not be saved:\n{str(e)}")

    def tableDroppedHMenu(self, pos: QPoint) -> None:
        """Контекстное меню для горизонтальных заголовков (управление столбцами)"""
        col: int = self.table_headers_h.logicalIndexAt(pos)

        menu: QMenu = QMenu(self)
        add_left: QAction = menu.addAction("Добавить столбец слева")
        add_right: QAction = menu.addAction("Добавить столбец справа")
        add_left_multiple: QAction = menu.addAction("Добавить несколько столбцов слева")
        add_right_multiple: QAction = menu.addAction("Добавить несколько столбцов справа")
        menu.addSeparator()
        delete_action: QAction = menu.addAction("Удалить столбец")

        action: QAction = menu.exec(self.table_headers_h.mapToGlobal(pos))
        if action == add_left:
            self.table.insertColumn(col)
        elif action == add_right:
            self.table.insertColumn(col + 1)
        elif action == add_left_multiple:
            self.addMultipleColumnsLeft(col)
        elif action == add_right_multiple:
            self.addMultipleColumnsRight(col)
        elif action == delete_action and self.table.columnCount() > 0:
            self.deleteTableColumn(col)
    
    def tableDroppedVMenu(self, pos: QPoint) -> None:
        """Контекстное меню для вертикальных заголовков (управление строками)"""
        row: int = self.table_headers_v.logicalIndexAt(pos)

        menu: QMenu = QMenu(self)
        add_above: QAction = menu.addAction("Добавить строку выше")
        add_below: QAction = menu.addAction("Добавить строку ниже")
        add_above_multiple: QAction = menu.addAction("Добавить несколько строк выше")
        add_below_multiple: QAction = menu.addAction("Добавить несколько строк ниже")
        menu.addSeparator()
        delete_action: QAction = menu.addAction("Удалить строку")

        action: QAction = menu.exec(self.table_headers_v.mapToGlobal(pos))
        if action == add_above:
            self.table.insertRow(row)
        elif action == add_below:
            self.table.insertRow(row + 1)
        elif action == add_above_multiple:
            self.addMultipleRowsAbove(row)
        elif action == add_below_multiple:
            self.addMultipleRowsBelow(row)
        elif action == delete_action and self.table.columnCount() > 0:
            self.deleteTableRow(row)
    
    def _showAbout(self) -> None:
        """Показывает диалоговое окно 'О программе' с подробной справкой"""
        QMessageBox.information(
            self,
            "About ZAVLAB",
        "ZAVLAB - Scientific Data Analysis and Visualization Tool\n\n"
        
        "Core Functionality:\n"
        "1. Data Management:\n"
        "   - Import/export CSV datasets\n"
        "   - Dynamic table editing with context menu controls\n"
        "   - Add/remove rows and columns with multi-selection support\n\n"
        
        "2. Advanced Plotting System:\n"
        "   - Multi-panel subplot layouts (up to 8x8 grid)\n"
        "   - Customizable subplot positioning and sizing\n"
        "   - Multiple data series per subplot\n"
        "   - Error bar support for both X and Y axes\n"
        "   - Interactive axis configuration through plot clicks\n\n"
        
        "3. Plot Customization:\n"
        "   - Line styles, colors, widths, and transparency\n"
        "   - Marker types and sizing\n"
        "   - Axis titles, ranges, and scaling (linear/log)\n"
        "   - Grid customization with major/minor ticks\n"
        "   - Legend positioning and font controls\n\n"
        
        "4. Project Management:\n"
        "   - Save/load plot configurations (JSON format)\n"
        "   - Export high-quality images (PNG, JPEG, SVG, PDF)\n"
        "   - Preserve data-table relationships\n\n"
        
        "5. Interactive Features:\n"
        "   - Click near axes to configure settings\n"
        "   - Real-time plot updates on data changes\n"
        "   - Dynamic axis range validation\n"
        "   - Smart default values based on dataset\n\n"
        
        "Keyboard Shortcuts:\n"
        "   Ctrl+N - New experiment\n"
        "   Ctrl+O - Load CSV data\n"
        "   Ctrl+Shift+S - Save data to CSV\n"
        "   Ctrl+S+P - Save plot settings\n"
        "   Ctrl+S+I - Export plot image\n\n"
        
        "Usage Workflow:\n"
        "1. Load data (File → Load Experiment)\n"
        "2. Configure plot grid dimensions (Rows/Columns)\n"
        "3. Add subplots with data assignments\n"
        "4. Customize plots using the 4 configuration tabs\n"
        "5. Export results (images/data/configurations)\n\n"
        
        "Technical Notes:\n"
        "- First row is treated as column headers\n"
        "- Only numeric data is plotted (non-numeric cells ignored)\n"
        "- Logarithmic scales auto-adjust negative/zero values\n"
        "- Axis limits must satisfy min < max to apply changes"
        )
    
    def addMultipleColumnsLeft(self, position: int) -> None:
        """Добавляет несколько столбцов слева от указанной позиции"""
        # Запрос количества
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Добавить столбцы слева",
            "Количество столбцов:",
            value=1,
            min=1,
            max=100
        )
        
        # Вставка столбцов
        if ok and count > 0:
            for _ in range(count):
                self.table.insertColumn(position)
            
            # Обновление отображения
            self.table_headers_h.resizeSections(QHeaderView.ResizeMode.Stretch)

    def addMultipleColumnsRight(self, position: int) -> None:
        """Добавляет несколько столбцов справа от указанной позиции"""
        # Запрос количества
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Добавить столбцы справа",
            "Количество столбцов:",
            value=1,
            min=1,
            max=100
        )
        
        # Вставка столбцов
        if ok and count > 0:
            for _ in range(count):
                self.table.insertColumn(position + 1)
            
            # Обновление отображения
            self.table_headers_h.resizeSections(QHeaderView.ResizeMode.Stretch)

    def addMultipleRowsAbove(self, position: int) -> None:
        """Добавляет несколько строк выше указанной позиции"""
        # Запрос количества
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Добавить строки сверху",
            "Количество строк:",
            value=1,
            min=1,
            max=100
        )
        
        # Вставка столбцов
        if ok and count > 0:
            for _ in range(count):
                self.table.insertRow(position)
            # Обновление отображения
            self.table_headers_v.resizeSections(QHeaderView.ResizeMode.Stretch)

    def addMultipleRowsBelow(self, position: int) -> None:
        """Добавляет несколько строк ниже указанной позиции"""
        # Запрос количества
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Добавить строки снизу",
            "Количество строк:",
            value=1,
            min=1,
            max=100
        )
        
        # Вставка столбцов
        if ok and count > 0:
            for _ in range(count):
                self.table.insertRow(position + 1)
            # Обновление отображения
            self.table_headers_v.resizeSections(QHeaderView.ResizeMode.Stretch)

    def deleteTableColumn(self, col: int) -> None:
        """Удаляет указанный столбец с подтверждением"""
        reply: QMessageBox.StandardButton = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот столбец?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeColumn(col)
            self.table_headers_h.resizeSections(QHeaderView.ResizeMode.Stretch)

    def deleteTableRow(self, row: int) -> None:
        """Удаляет указанную строку с подтверждением"""
        reply: QMessageBox.StandardButton = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить эту строку?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(row)
            self.table_headers_v.resizeSections(QHeaderView.ResizeMode.Stretch)

    def _new_file(self) -> None:
        """Очищает таблицу для нового эксперимента"""
        self.table.clear()
        self.statusBar().showMessage("Таблица готова к новому эксперименту", 2000)
        self.update_headers()


    def _save_file(self) -> None:
        """Сохраняем данные таблицы в CSV файл"""
        file_name: str
        _: str
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_name:
            return  # Пользователь отменил
        
        try:
            if not file_name.endswith(".csv"):
                file_name += ".csv"
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Записываем заголовки
                headers: list[str] = []
                for col in range(self.table.columnCount()):
                    header_item = self.table.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"{col+1}")
                writer.writerow(headers)
                # Записываем данные
                for row in range(self.table.rowCount()):
                    row_data: list[str] = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append("")  # Пустая строка для отсутствующей ячейки
                    writer.writerow(row_data)
            
            self.statusBar().showMessage(f"Файл сохранен: {file_name}", 5000)
            QMessageBox.information(self, "Успех", "Данные успешно экспортированы в CSV!")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def _load_data(self) -> None:
        """Загружаем данные из CSV файла в таблицу"""
        file_name: str
        _: str
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть CSV файл",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_name:
            return  # Пользователь отменил
        
        try:
            with open(file_name, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                
                # Читаем заголовки
                headers: list[str] = next(reader)
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                
                # Читаем данные
                data: list[list[str]] = list(reader)
                self.table.setRowCount(len(data))
                
                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        if col < self.table.columnCount():  # Защита от лишних колонок
                            item: QTableWidgetItem = QTableWidgetItem(value)
                            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                            self.table.setItem(row, col, item)
            self.update_headers()
            self.statusBar().showMessage(f"Файл загружен: {file_name}", 5000)
            QMessageBox.information(self, "Успех", "Данные успешно загружены из CSV!")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def plot_data(self, x:int, y:int, lenght: int) -> None:
        """Plot data by chosen data"""

        data = self.get_data(x, y, lenght)
        labels = [f"{self.table.item(0, x).text() if self.table.item(0, x) else ''}", f"{self.table.item(0, y).text() if self.table.item(0, y) else ''}"]
        self.plotter.plot_data(data, labels)

    def get_column_index(self, column_name:str) -> int:
        """Find column index by name"""
        for col in range(self.table.columnCount()):
            header = self.table.item(0, col)
            if header and header.text() == column_name:
                return col
        return -1

    def get_data(self, x:int|str, y:int|str, lenght : int|None = None) -> np.ndarray:
        """get data from table to plot them"""

        data = [[], []]
        x_flag = True
        y_flag = True
        if type(x) == str:
            x = self.get_column_index(x)
        if type(y) == str:
            y = self.get_column_index(y)
        if x == -1 or y == -1:
            return np.array(data)
        if lenght == None:
            lenght = self.table.rowCount() - 1
        for i in range(lenght + 1):
            if self.table.item(i, x):
                item_x = self.table.item(i, x).text()
                x_flag = True
            else:
                item_x = 0
                x_flag = False
            try:
                item_x = float(item_x)
                x_flag = True
            except ValueError:
                item_x = 0
                x_flag = False
            if self.table.item(i, y):
                item_y = self.table.item(i, y).text()
                y_flag = True
            else:
                item_y = 0
                y_flag = False
            try:
                item_y = float(item_y)
                y_flag = True
            except ValueError:
                item_y = 0
                y_flag = False 
            if x_flag and y_flag:
                data[0].append(item_x)
                data[1].append(item_y)
        return np.array(data)
    
    def get_error_data(self, x:int|str, xerr:int|str, y:int|str, yerr:int|str, lenght : int|None = None) -> np.ndarray:
        """Extract data with errors"""

        data = [[], [], [], []]
        x_flag = True
        y_flag = True
        if type(x) == str:
            x = self.get_column_index(x)
        if type(y) == str:
            y = self.get_column_index(y)
        if type(xerr) == str:
            xerr = self.get_column_index(xerr)
        if type(yerr) == str:
            yerr = self.get_column_index(yerr)
        if x == -1 or y == -1:
            return np.array(data)
        if lenght == None:
            lenght = self.table.rowCount() - 1
        for i in range(lenght + 1):
            if self.table.item(i, x):
                item_x = self.table.item(i, x).text()
                x_flag = True
            else:
                x_flag = False
            try:
                item_x = float(item_x)
                x_flag = True
            except ValueError:
                x_flag = False
            if self.table.item(i, y):
                item_y = self.table.item(i, y).text()
                y_flag = True
            else:
                y_flag = False
            try:
                item_y = float(item_y)
                y_flag = True
            except ValueError:
                y_flag = False 
            if x_flag and y_flag:
                data[0].append(item_x)
                data[2].append(item_y)
                if xerr != -1 and self.table.item(i, xerr):
                    item_xerr = self.table.item(i, xerr).text()
                    try:
                        item_xerr = float(item_xerr)
                    except ValueError:
                        item_xerr = 0
                else:
                    item_xerr = 0
                if yerr != -1 and self.table.item(i, yerr):
                    item_yerr = self.table.item(i, yerr).text()
                    try:
                        item_yerr = float(item_yerr)
                    except ValueError:
                        item_yerr = 0 
                else:
                    item_yerr = 0
                data[1].append(item_xerr)
                data[3].append(item_yerr)     
        return np.array(data)

    def update_headers(self) -> None:
        """Extract headers and emit them as a list"""
        
        headers = []
        for col in range(self.table.columnCount()):
            header_item = self.table.item(0, col)
            headers.append(header_item.text() if header_item else f"Column {col+1}")
        self.signals.emit(headers)
    
    def get_headers(self):
        return [self.table.item(0, col).text() if self.table.item(0, col) 
                else f"Column {col+1}" for col in range(self.table.columnCount())]
    
    def get_min_max_from_column(self, x:int|str, lenght:None|int = None)->list[float]:
        data = []
        if type(x) == str:
            x = self.get_column_index(x)
        if lenght == None:
            lenght = self.table.rowCount() - 1
        for i in range(lenght + 1):
            if self.table.item(i, x):
                item_x = self.table.item(i, x).text()   
                try:
                    item_x = float(item_x)
                    data.append(item_x)
                except ValueError:
                    pass
        data = np.array(data)
        if data.size == 0:
            return [0.0, 1.0]
        if np.min(data) == np.max(data):
            return [np.min(data), np.max(data) * 2]
        return [np.min(data), np.max(data)]

    def get_min_max_value(self):
        headers = self.get_headers()
        min_max = []
        for head in headers:
            min_max.append(self.get_min_max_from_column(head))
        return min_max

if __name__ == "__main__":
    app = QApplication([])
    my_app = ZAVLAB()
    my_app.show()
    app.exec()