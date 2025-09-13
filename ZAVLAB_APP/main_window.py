from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QGroupBox,
                             QHBoxLayout, QGridLayout, QSplitter,
                             QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMenu, QMenuBar,
                             QMessageBox, QDialog, QInputDialog, QFileDialog)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

# Shouldn't be here
# -----------------
import csv
import numpy as np
# -----------------

from theme_manager import ThemeManager
from graphClasses import PREPARE_DATA, SubplotEditor



class ZAVLABMainWindow(QMainWindow):

    """TODO: docs"""

    # Constant sector
    # ----------------------------
    WINDOW_TITLE: str = "ZAVLAB"
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    SPLITTER_HANDLE_WIDTH: int = 5
    # ----------------------------


    # Signals
    # -----------------------------
    data_updated = pyqtSignal(list) 
    # -----------------------------


    def __init__(self) -> None:
        super().__init__()

        self.theme = 'default'
        
        self._configure_window()
        self._initialize_components()
        self._setup_ui()
        self._connect_signals()



    def _configure_window(self) -> None:
        """Set up basic window properties."""

        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)


    def _initialize_components(self) -> None:
        """Initialize all application components"""

        # Central widget (splitter)
        self.central_widget = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.central_widget)

        # Data-related widgets
        self.setupTable()  # Initializes self.table
        self.label = QLabel("Plot will be here soon!")
        self.setupMenuBar()  # Initializes self.menu_bar

        # Vizualization-related widgets
        self.plotter = SubplotEditor()

        # Initial data update
        self._initialize_plot_data()


    def _initialize_plot_data(self) -> None:
        """Initialize plot with column headers from the table"""
        
        column_headers: List[str] = [
            self.table.item(0, col).text() if self.table.item(0, col) 
            else f"Column {col + 1}" 
            for col in range(self.table.columnCount())
        ]
        self.plotter.update_column_data(column_headers)


    def _setup_ui(self) -> None:
        """Set up the user interface layout"""

        self._attach_elements()
        self._configure_main_splitter()
        self._apply_styles()


    def _attach_elements(self) -> None:
        """Add widgets to main layout"""

        self.central_widget.addWidget(self.table)
        self.central_widget.addWidget(self.plotter)


    def _configure_main_splitter(self) -> None:
        """Set main splitter properties"""

        # Stretch factors of elements
        self.central_widget.setStretchFactor(0, 1)  # 1 for data table
        self.central_widget.setStretchFactor(1, 3)  # 3 for plot area
        # |  Data  |          Plot          |
        # |   1    |           3            |

        self.central_widget.setChildrenCollapsible(False)  # Disallow element collapsing
        self.central_widget.setHandleWidth(self.SPLITTER_HANDLE_WIDTH) 

    
    def _apply_styles(self) -> None:
        """Get and apply CSS"""

        stylesheet = ThemeManager.get_stylesheet(self.theme)
        self.central_widget.setStyleSheet(stylesheet)


    def _connect_signals(self) -> None:
        """Connect internal signals"""

        self.data_updated.connect(self.plotter.update_column_data)



    def set_theme(self, theme_name: str) -> None:
        """Change app theme"""

        if theme_name in ThemeManager.get_available_themes():
            self.theme = theme_name
            self._apply_styles()








    def setPlottingPart(self) -> None:
        self.config_panel: QWidget = QWidget()
        self.config_layout: QHBoxLayout = QHBoxLayout()
        self.config_panel.setLayout(self.config_layout)
        self.central_widget.setLayout(self.config_panel)

        #make grid
        self.grid_group: QGroupBox = QGroupBox("Grid Configuration")
        self.grid_layout: QGridLayout = QGridLayout()

        self.grid_layout.addWidget(QLabel("Rows:"), 0, 0)
        self.row_spin: QSpinBox = QSpinBox()
        self.row_spin.setRange(1, 8)
        self.row_spin.setValue(1)
        self.grid_layout.addWidget(self.row_spin, 0, 1)

        self.grid_layout.addWidget(QLabel("Cols:"), 0, 2)
        self.col_spin: QSpinBox = QSpinBox()
        self.col_spin.setRange(1, 8)
        self.col_spin.setValue(1)
        self.grid_layout.addWidget(self.col_spin, 0, 3)

        self.create_grid_btn = QPushButton("Create Grid")
        self.create_grid_btn.clicked.connect(self.create_grid)
        self.grid_layout.addWidget(self.create_grid_btn)

        self.grid_group.setLayout(self.grid_layout)
        self.config_layout.addWidget(self.grid_group)

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
            "О программе",
            "Программа ZAVLAB - инструмент для анализа экспериментальных данных\n\n"
        
        "Основные возможности:\n"
        "1. Управление данными:\n"
        "   - Добавление/удаление строк и столбцов через контекстное меню (ПКМ на заголовках)\n"
        "   - Редактирование данных напрямую в таблице\n"
        "   - Импорт/экспорт данных в формате CSV\n\n"
        
        "2. Построение графиков:\n"
        "   - Выбор столбцов для осей X и Y\n"
        "   - Указание количества точек для построения\n"
        "   - Автоматическое обновление графика при изменении данных\n"
        "   - Интерактивная настройка осей графика\n\n"
        
        "3. Интерактивные возможности графика:\n"
        "   - Клик в нижней части графика (вблизи оси X) открывает настройки оси X\n"
        "   - Клик в левой части графика (вблизи оси Y) открывает настройки оси Y\n"
        "   - В настройках можно изменить:\n"
        "        * Минимальное и максимальное значение оси\n"
        "        * Количество делений (тиков) на оси\n"
        "        * Заголовок оси\n\n"
        
        "4. Горячие клавиши:\n"
        "   Ctrl+N - Новый эксперимент\n"
        "   Ctrl+O - Загрузить данные из CSV\n"
        "   Ctrl+Shift+S - Сохранить данные в CSV\n"
        "   Ctrl+P - Построить график\n\n"
        
        "Инструкция по использованию:\n"
        "1. Введите данные в таблицу или загрузите из CSV-файла\n"
        "2. Настройте структуру таблицы (добавьте нужные столбцы и строки)\n"
        "3. Выберите 'Построить график' в меню\n"
        "4. Укажите номера столбцов для осей X и Y\n"
        "5. При необходимости укажите количество точек для отображения\n"
        "6. График автоматически построится в правой части окна\n"
        "7. Для настройки осей кликните вблизи соответствующей оси\n\n"
        
        "Примечания:\n"
        "- Первая строка таблицы интерпретируется как заголовки столбцов\n"
        "- Для построения графика используются только числовые данные\n"
        "- Ячейки, не заполненные числами (целыми или дробными, написанными через точку), игнорируются при построении графика\n"
        "- В настройках осей минимум должен быть меньше максимума, иначе настройка не применится"
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

    def _prepare_plotting_data(self) -> None:
        """Открывает диалоговое окно для ввода данных"""
        dialog: PREPARE_DATA = PREPARE_DATA(self)
        # Если пользователь нажал OK
        if dialog.exec() == QDialog.DialogCode.Accepted:
            x, y, lenght = dialog.get_inputs()
            # Проверяем, что все поля заполнены
            if (not x.isdigit() or int(x) > self.table.columnCount()) or (not y.isdigit() or int(y) > self.table.columnCount()):
                QMessageBox.warning(self, "Ошибка", "x, y должны быть целыми числами от 1 до n, где n - количество столбцов.")
                return
            elif (not lenght.isdigit() and lenght != ""):
                QMessageBox.warning(self, "Ошибка", "количество данных должны быть целым числом от 1 до n, где n - количество строк.")
                return
            elif lenght.isdigit() and int(lenght) >= self.table.rowCount():
                QMessageBox.warning(self, "Ошибка", "количество данных должны быть целым числом от 1 до n, где n - количество строк.")
                return
            else:
                if lenght.isdigit():
                    lenght = int(lenght)
                else:
                    lenght = self.table.rowCount()

                self.plot_data(int(x) - 1, int(y) - 1, lenght)

    def plot_data(self, x:int, y:int, lenght: int) -> None:
        """Строит график по выбранным данным"""
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
        """Извлекает данные из таблицы для построения графика"""
        data = [[], []]
        x_flag = True
        y_flag = True
        if type(x) == str:
            x = self.get_column_index(x)
        if type(y) == str:
            y = self.get_column_index(y)
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
            except:
                x_flag = False
            if self.table.item(i, y):
                item_y = self.table.item(i, y).text()
                y_flag = True
            else:
                y_flag = False
            try:
                item_y = float(item_y)
                y_flag = True
            except:
                y_flag = False 
            if x_flag and y_flag:
                data[0].append(item_x)
                data[1].append(item_y)
        return np.array(data)
    
    def update_headers(self) -> None:
        """Extract headers and emit them as a list"""
        headers = []
        for col in range(self.table.columnCount()):
            header_item = self.table.item(0, col)
            headers.append(header_item.text() if header_item else f"Column {col+1}")
        self.data_updated.emit(headers)
    
    def get_headers(self):
        return [self.table.item(0, col).text() if self.table.item(0, col) 
                else f"Column {col+1}" for col in range(self.table.columnCount())]

