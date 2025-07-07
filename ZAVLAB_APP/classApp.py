from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QTableWidget, QLabel, QHeaderView, QMenu, QMessageBox, QInputDialog, QFileDialog, QTableWidgetItem
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QKeySequence
import csv

class ZAVLAB(QMainWindow):
    def __init__(self) -> None:
        super(ZAVLAB, self).__init__()
        self.setWindowTitle("ZAVLAB")
        self.resize(1200, 800)

        #centreal widget
        self.central_widget: QSplitter = QSplitter(Qt.Orientation.Horizontal)

        #make all widgets
        self.setupTable()   
        self.label: QLabel = QLabel("Plot will be here soon!")
        self.setupMenuBar()

        #design
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.table)
        self.central_widget.addWidget(self.label)
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

    def setupMenuBar(self) -> None:
        self.menu_bar = self.menuBar()
        self.help_menu = self.menu_bar.addMenu("Справка")
        self.plot_graph = self.menu_bar.addMenu("Построить график")
        self.files = self.menu_bar.addMenu("Файл")

        #Справка
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._showAbout)
        self.help_menu.addAction(about_action)

        #работа с файлами
        #новый эксперимент
        new_action = QAction("Новый эксперимент", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._new_file)
        self.files.addAction(new_action)
        
        #сохранить эксперимент
        save_action = QAction("Сохранить эксперимент", self)
        save_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_action.triggered.connect(self._save_file)
        self.files.addAction(save_action)

        #загрузить эксперимент
        load_action = QAction("Загрузить эксперимент", self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self._load_data)
        self.files.addAction(load_action)

        #построение графика
        plot_action = QAction("Построить график", self)
        plot_action.setShortcut(QKeySequence("Ctrl+P"))
        plot_action.triggered.connect(self._prepare_plotting_data)


    def tableDroppedHMenu(self, pos: QPoint):
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
    
    def tableDroppedVMenu(self, pos: QPoint):
        row = self.table_headers_v.logicalIndexAt(pos)

        menu = QMenu(self)
        add_above = menu.addAction("Добавить строку выше")
        add_below = menu.addAction("Добавить строку ниже")
        add_above_multiple: QAction = menu.addAction("Добавить несколько строк выше")
        add_below_multiple: QAction = menu.addAction("Добавить несколько строк ниже")
        menu.addSeparator()
        delete_action: QAction = menu.addAction("Удалить строку")

        action = menu.exec(self.table_headers_v.mapToGlobal(pos))
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
        QMessageBox.information(
            self,
            "О программе",
            "Чтобы добавить столбец/строку нажмите на заголовок (цифру соответсвующего столбца/строки), появится контекстное меню с вариантами по добавляению столбца/строки.\n"
        )
    
    def addMultipleColumnsLeft(self, position):
        # Запрос количества
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

    def addMultipleColumnsRight(self, position):
        # Запрос количества
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

    def addMultipleRowsAbove(self, position):
        # Запрос количества
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

    def addMultipleRowsBelow(self, position):
        # Запрос количества
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

    def deleteTableColumn(self, col):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот столбец?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeColumn(col)
            self.table_headers_h.resizeSections(QHeaderView.ResizeMode.Stretch)

    def deleteTableRow(self, row):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить эту строку?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(row)
            self.table_headers_v.resizeSections(QHeaderView.ResizeMode.Stretch)

    def _new_file(self):
        self.table.clear()
        self.statusBar().showMessage("Таблица готова к новому эксперименту", 2000)


    def _save_file(self):
        """Сохраняем данные таблицы в CSV файл"""
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
                headers = []
                for col in range(self.table.columnCount()):
                    header_item = self.table.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"{col+1}")
                writer.writerow(headers)
                # Записываем данные
                for row in range(self.table.rowCount()):
                    row_data = []
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
    
    def _load_data(self):
        """Загружаем данные из CSV файла в таблицу"""
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
                headers = next(reader)
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                
                # Читаем данные
                data = list(reader)
                self.table.setRowCount(len(data))
                
                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        if col < self.table.columnCount():  # Защита от лишних колонок
                            item = QTableWidgetItem(value)
                            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                            self.table.setItem(row, col, item)
            
            self.statusBar().showMessage(f"Файл загружен: {file_name}", 5000)
            QMessageBox.information(self, "Успех", "Данные успешно загружены из CSV!")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def _prepare_plotting_data(self):
        pass

if __name__ == "__main__":
    app = QApplication([])
    my_app = ZAVLAB()
    my_app.show()
    app.exec()