from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QLabel,
                             QHeaderView, QMenu, QMessageBox, QInputDialog, QFileDialog,
                             QTableWidgetItem, QMenuBar, QDialog, QDialogButtonBox, QLineEdit,
                               QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QGridLayout,
                               QSpinBox, QPushButton)
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

import json
import os
import logging
import csv
import numpy as np

from theme_manager import ThemeManager
from plot_manager import SubplotEditor
from core import AutoSaveManager
from table import ExcelLikeModel, ExcelTableView, FormulaLineEdit



class ZAVLABMainWindow(QMainWindow):
    """Main application window for ZAVLAB scientific data analysis tool.
    Handles UI layout, table management, plotting, and file operations."""

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
        """Initialize the main window with all components and UI setup."""
        super().__init__()

        self.theme = 'default'
        
        self._configure_window()
        self._initialize_components()
        self._setup_ui()
        self._connect_signals()

    def _configure_window(self) -> None:
        """Set up basic window properties like title and size."""

        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def _initialize_components(self) -> None:
        """Initialize all application components including table, plotter, and menu."""

        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Central widget (splitter)
        self.central_widget_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.central_widget_splitter)

        # Data-related widgets
        self.setupTable()  # Initializes self.table
        self.label = QLabel("Plot will be here soon!")
        self.setupMenuBar()  # Initializes self.menu_bar

        # Vizualization-related widgets
        self.plotter = SubplotEditor(parent=self)
        self.data_updated.connect(self.plotter.update_column_data)

        #auto save manager
        self.auto_save_manager = AutoSaveManager(parent=self)
        self.restore_state()

        # Initial data update
        self._initialize_plot_data()

    def _initialize_plot_data(self) -> None:
        """Initialize plot with column headers from the table"""
        
        column_headers: list[str] = [self.table.model().headerData(col, Qt.Orientation.Horizontal) 
                                        if col < self.table.model().columnCount() 
                                        else f"Column {col+1}" 
                                        for col in range(self.table.model().columnCount())]
        self.plotter.update_column_data(column_headers)

    def _setup_ui(self) -> None:
        """Set up the user interface layout and styling."""

        self._attach_elements()
        self._configure_main_splitter()
        # self._apply_styles()

    def _attach_elements(self) -> None:
        """Add widgets to main layout."""

        self.central_widget_splitter.addWidget(self.plotter)

    def _configure_main_splitter(self) -> None:
        """Set main splitter properties and stretch factors."""

        # Stretch factors of elements
        self.central_widget_splitter.setStretchFactor(0, 1)  # 1 for data table
        self.central_widget_splitter.setStretchFactor(1, 3)  # 3 for plot area
        # |  Data  |          Plot          |
        # |   1    |           3            |

        self.central_widget_splitter.setChildrenCollapsible(False)  # Disallow element collapsing
        self.central_widget_splitter.setHandleWidth(self.SPLITTER_HANDLE_WIDTH) 
 
    def _apply_styles(self) -> None:
        """Get and apply CSS styling based on current theme."""

        stylesheet = ThemeManager.get_stylesheet(self.theme)
        self.central_widget_splitter.setStyleSheet(stylesheet)

    def _connect_signals(self) -> None:
        """Connect internal signals between components."""

        self.data_updated.connect(self.plotter.update_column_data)

    def set_theme(self, theme_name: str) -> None:
        """Change application theme."""

        if theme_name in ThemeManager.get_available_themes():
            self.theme = theme_name
            self._apply_styles()

    def setupTable(self) -> None:
        """Initialize table with formula bar and decimal control."""

        # Decimal places control
        decimal_label = QtWidgets.QLabel("Decimal Places:")
        self.decimal_spin = QtWidgets.QSpinBox()
        self.decimal_spin.setRange(0, 10)
        self.decimal_spin.setValue(2)
        self.decimal_spin.setMinimumWidth(60)
        self.decimal_spin.valueChanged.connect(self.change_decimal_places)
        
        # Create formula bar
        formula_layout = QHBoxLayout()
        formula_label = QLabel("Formula:")
        self.formula_edit = FormulaLineEdit()
        self.apply_button = QPushButton("Apply Formula")
        self.apply_button.clicked.connect(self.apply_formula)

        # Add relative reference button
        self.relative_button = QtWidgets.QPushButton("Apply with Relative Refs")
        self.relative_button.clicked.connect(self.apply_formula_with_relative_refs)

        formula_layout.addWidget(formula_label)
        formula_layout.addWidget(self.formula_edit)
        formula_layout.addWidget(self.apply_button)
        formula_layout.addWidget(self.relative_button)
        
        #create table
        self.table: ExcelTableView = ExcelTableView()  
        self.table.table_headers_signal.connect(self.update_headers) 
        self.model: ExcelLikeModel = ExcelLikeModel(20, 2)  # 10 rows, 2 columns initially
        self.table.setModel(self.model)
        
        # Add widgets to splitter
        decimal_layout = QHBoxLayout()
        decimal_layout.addWidget(decimal_label)
        decimal_layout.addWidget(self.decimal_spin)
        decimal_layout.addStretch()

        table_layout = QVBoxLayout()
        table_widget = QWidget()
        table_widget.setMinimumWidth(100)
        table_layout.addLayout(decimal_layout)
        table_layout.addLayout(formula_layout)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        self.central_widget_splitter.addWidget(table_widget)
    

        # Set up headers
        self.table_headers_h: QHeaderView = self.table.horizontalHeader() 
        self.table_headers_v: QHeaderView = self.table.verticalHeader() 

        # Set resize modes
        self.table_headers_h.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_headers_v.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Connect context menus
        self.table_headers_h.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_headers_h.customContextMenuRequested.connect(self.tableDroppedHMenu)

        self.table_headers_v.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_headers_v.customContextMenuRequested.connect(self.tableDroppedVMenu)

        # Connect signals for header changes
        self.table_headers_h.sectionCountChanged.connect(self.update_headers)
        self.table_headers_h.geometriesChanged.connect(self.update_headers)
        
        # Set selection behavior
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)

        # Connect selection change signal to update formula bar
        self.table.selectionModel().selectionChanged.connect(self.update_formula_bar)

    def setupMenuBar(self) -> None:
        """Create application menu bar with file operations and help sections."""

        self.menu_bar: QMenuBar = self.menuBar()
        self.help_menu: QMenu = self.menu_bar.addMenu("Help")
        self.files: QMenu = self.menu_bar.addMenu("File")

        #Help
        appInfo_action: QAction = QAction("Main information", self)
        appInfo_action.triggered.connect(self._mainAppInfo)
        self.help_menu.addAction(appInfo_action)

        tableinfo_action: QAction = QAction("Table guide", self)
        tableinfo_action.triggered.connect(self._tableGuide)
        self.help_menu.addAction(tableinfo_action) 
        
        plotinfo_action: QAction = QAction("Plot guide", self)
        plotinfo_action.triggered.connect(self._plotGuide)
        self.help_menu.addAction(plotinfo_action)

        editorguide_action: QAction = QAction("Editor guide", self)
        editorguide_action.triggered.connect(self._editorGuide)
        self.help_menu.addAction(editorguide_action) 

        lineguide_action: QAction = QAction("Line guide", self)
        lineguide_action.triggered.connect(self._LinesGuide)
        self.help_menu.addAction(lineguide_action)  

        example_action: QAction = QAction("Example", self)
        example_action.triggered.connect(self._example)
        self.help_menu.addAction(example_action)  

        #работа с файлами
        #новый эксперимент
        # new_action: QAction = QAction("New table", self)
        # new_action.setShortcut(QKeySequence("Ctrl+N"))
        # new_action.triggered.connect(self._new_file)
        # self.files.addAction(new_action)
        
        # Save table as JSON (with formulas)
        save_json_action: QAction = QAction("Save table (JSON with formulas)", self)
        save_json_action.setShortcut(QKeySequence("Ctrl+Shift+J"))
        save_json_action.triggered.connect(self._save_json)
        self.files.addAction(save_json_action)
        
        # Load table from JSON (with formulas)
        load_json_action: QAction = QAction("Load table (JSON with formulas)", self)
        load_json_action.setShortcut(QKeySequence("Ctrl+J"))
        load_json_action.triggered.connect(self._load_json)
        self.files.addAction(load_json_action)
        
        # Keep the existing CSV options but rename them
        save_action: QAction = QAction("Save table as CSV (values only)", self)  # Renamed
        save_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_action.triggered.connect(self._save_csv)  # Changed to _save_csv
        self.files.addAction(save_action)

        load_action: QAction = QAction("Load table from CSV (values only)", self)  # Renamed
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self._load_csv)  # Changed to _load_csv
        self.files.addAction(load_action)

        # save plots settings
        save_plot_settings = QAction("Save plots settings", self)
        save_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        save_plot_settings.triggered.connect(self._save_plot_settings)
        self.files.addAction(save_plot_settings)

        # Import plots settings
        load_plot_settings = QAction("Import plots settings", self)
        save_action.setShortcut(QKeySequence("Ctrl+Shift+I"))
        load_plot_settings.triggered.connect(self._load_plot_settings)
        self.files.addAction(load_plot_settings)

        # Save plots images
        save_plot_image = QAction("Save plots image", self)
        save_action.setShortcut(QKeySequence("Ctrl+Shift+M"))
        save_plot_image.triggered.connect(self._save_plot_image)
        self.files.addAction(save_plot_image)

    def tableDroppedHMenu(self, pos: QPoint) -> None:
        """Context menu for horizontal headers (column management)."""  
        
        col: int = self.table_headers_h.logicalIndexAt(pos)

        menu: QMenu = QMenu(self)
        add_left: QAction = menu.addAction("Add column left")
        add_right: QAction = menu.addAction("Add column right")
        add_left_multiple: QAction = menu.addAction("Add multiple columns left")
        add_right_multiple: QAction = menu.addAction("Add multiple columns right")
        menu.addSeparator()
        delete_action: QAction = menu.addAction("Delete column")

        action: QAction = menu.exec(self.table_headers_h.mapToGlobal(pos))
        if action == add_left:
            self.model.insertColumn(col)
        elif action == add_right:
            self.model.insertColumn(col + 1)
        elif action == add_left_multiple:
            self.addMultipleColumnsLeft(col)
        elif action == add_right_multiple:
            self.addMultipleColumnsRight(col)
        elif action == delete_action and self.model.columnCount() > 0:
            self.deleteTableColumn(col)
    
    def tableDroppedVMenu(self, pos: QPoint) -> None:
        """Context menu for vertical headers (row management)."""

        row: int = self.table_headers_v.logicalIndexAt(pos)

        menu: QMenu = QMenu(self)
        add_above: QAction = menu.addAction("Add row above")
        add_below: QAction = menu.addAction("Add row below")
        add_above_multiple: QAction = menu.addAction("Add multiple rows above")
        add_below_multiple: QAction = menu.addAction("Add multiple rows below")
        menu.addSeparator()
        delete_action: QAction = menu.addAction("Delete row")

        action: QAction = menu.exec(self.table_headers_v.mapToGlobal(pos))
        if action == add_above:
            self.model.insertRow(row)
        elif action == add_below:
            self.model.insertRow(row + 1)
        elif action == add_above_multiple:
            self.addMultipleRowsAbove(row)
        elif action == add_below_multiple:
            self.addMultipleRowsBelow(row)
        elif action == delete_action and self.model.columnCount() > 0:
            self.deleteTableRow(row)
      
    def addMultipleColumnsLeft(self, position: int) -> None:
        """Add multiple columns to the left of the specified position."""
        
        # Request count
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Add columns left",
            "Number of columns:",
            value=1,
            min=1,
            max=100
        )
        
        # Insert columns
        if ok and count > 0:
            for _ in range(count):
                self.model.insertColumn(position)
            
            # Update display
            self.table_headers_h.resizeSections(QHeaderView.ResizeMode.Stretch)

    def addMultipleColumnsRight(self, position: int) -> None:
        """Add multiple columns to the right of the specified position."""
        
        # Request count
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Add columns right",
            "Number of columns:",
            value=1,
            min=1,
            max=100
        )
        
        # Insert columns
        if ok and count > 0:
            for _ in range(count):
                self.model.insertColumn(position + 1)
            
            # Update display
            self.table_headers_h.resizeSections(QHeaderView.ResizeMode.Stretch)

    def addMultipleRowsAbove(self, position: int) -> None:
        """Add multiple rows above the specified position."""
        
        # Request count
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Add rows above",
            "Number of rows:",
            value=1,
            min=1,
            max=100
        )
        
        # Insert rows
        if ok and count > 0:
            for _ in range(count):
                self.model.insertRow(position)
            # Update display
            self.table_headers_v.resizeSections(QHeaderView.ResizeMode.Stretch)

    def addMultipleRowsBelow(self, position: int) -> None:
        """Add multiple rows below the specified position."""
        
        # Request count
        count: int
        ok: bool
        count, ok = QInputDialog.getInt(
            self,
            "Add rows below",
            "Number of rows:",
            value=1,
            min=1,
            max=100
        )
        
        # Insert rows
        if ok and count > 0:
            for _ in range(count):
                self.model.insertRow(position + 1)
            # Update display
            self.table_headers_v.resizeSections(QHeaderView.ResizeMode.Stretch)

    def deleteTableColumn(self, col: int) -> None:
        """Delete specified column with confirmation."""
        
        reply: QMessageBox.StandardButton = QMessageBox.question(self, "Confirmation", "Are you sure you want to delete this column?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.model.removeColumn(col)
            self.update_headers()

    def deleteTableRow(self, row: int) -> None:
        """Delete specified row with confirmation."""
        
        reply: QMessageBox.StandardButton = QMessageBox.question(self, "Confirmation", "Are you sure you want to delete this row?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.model.removeRow(row)
    
    def _new_file(self) -> None:
        """Clear the table for a new experiment."""
        self.table.clear()
        self.statusBar().showMessage("Table ready for new experiment", 2000)
        self.update_headers()

    def _save_csv(self, file_name=None) -> None:
        """Save table data to CSV file."""
        
        file_name: str
        _: str
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save as CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not file_name:
            return  # User cancelled
        
        try:
            if not file_name.endswith(".csv"):
                file_name += ".csv"
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Write headers
                headers: list[str] = []
                for col in range(self.table.model().columnCount()):
                    header = self.table.model().headerData(col, Qt.Orientation.Horizontal)
                    headers.append(header if header else f"{col+1}")
                writer.writerow(headers)
                
                # Write headers
                for row in range(self.table.model().rowCount()):
                    row_data: list[str] = []
                    for col in range(self.table.model().columnCount()):
                        index = self.table.model().index(row, col)
                        value = self.table.model().data(index, Qt.ItemDataRole.DisplayRole)
                        if value is not None:
                            row_data.append(str(value))
                        else:
                            row_data.append("")  # Пустая строка для отсутствующей ячейки
                    writer.writerow(row_data)
            
            self.statusBar().showMessage(f"File saved: {file_name}", 5000)
            QMessageBox.information(self, "Success", "Data successfully exported to CSV!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def _load_csv(self) -> None:
        """Load data from CSV file into table."""
        
        file_name: str
        _: str
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV file",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_name:
            return  # User cancelled
        
        try:
            with open(file_name, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                
                # Read headers
                headers: list[str] = next(reader)
                
                # Set column count in model
                self.model.setColumnCount(len(headers))
                
                # Set column names
                for col, header in enumerate(headers):
                    self.model.setHeaderData(col, Qt.Orientation.Horizontal, header)
                
                # Read data
                data: list[list[str]] = list(reader)
                
                # Set row count in model
                self.model.setRowCount(len(data))
                
                # Fill data
                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        if col < self.model.columnCount():  # Protection against extra columns
                            index = self.model.index(row, col)
                            self.model.setData(index, value, Qt.ItemDataRole.EditRole)
                
                # Update headers and redraw table
                self.update_headers()
                self.table.viewport().update()
                
                self.statusBar().showMessage(f"File loaded: {file_name}", 5000)
                QMessageBox.information(self, "Success", "Data successfully loaded from CSV!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def _save_json(self) -> None:
        """Save table data to JSON file (including formulas)."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save as JSON",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if not file_name:
            return  # User cancelled
        
        try:
            if not file_name.endswith(".json"):
                file_name += ".json"
            
            # Get the complete table state including formulas
            table_state = {
                "decimal_places": self.model.decimal_places,
                "column_names": self.model._column_names,
                "formulas": self.model._formulas,
                "row_count": self.model.rowCount(),
                "column_count": self.model.columnCount(),
                "data": []  # We'll also store the evaluated data for compatibility
            }
            
            # Store the evaluated data as well for compatibility with other apps
            for row in range(self.model.rowCount()):
                row_data = []
                for col in range(self.model.columnCount()):
                    index = self.model.index(row, col)
                    value = self.table.model().data(index, Qt.ItemDataRole.DisplayRole)
                    row_data.append(value if value is not None else "")
                table_state["data"].append(row_data)
            
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(table_state, f, indent=4)
            
            self.statusBar().showMessage(f"Table with formulas saved: {file_name}", 5000)
            QMessageBox.information(self, "Success", "Table with formulas successfully saved!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def _load_json(self) -> None:
        """Load table data from JSON file (including formulas)."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON file",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_name:
            return  # User cancelled
        
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                table_state = json.load(f)
            
            # Set row and column count
            self.model.setRowCount(table_state["row_count"])
            self.model.setColumnCount(table_state["column_count"])
            
            # Restore column names
            for col, name in enumerate(table_state["column_names"]):
                self.model.setHeaderData(col, Qt.Orientation.Horizontal, name)
            
            # Restore formulas
            for row in range(table_state["row_count"]):
                for col in range(table_state["column_count"]):
                    if row < len(table_state["formulas"]) and col < len(table_state["formulas"][row]):
                        index = self.model.index(row, col)
                        formula = table_state["formulas"][row][col]
                        if formula:  # Only set if there's a formula
                            self.model.setData(index, formula, Qt.ItemDataRole.EditRole)
            
            # Restore decimal places
            if "decimal_places" in table_state:
                self.model.decimal_places = table_state["decimal_places"]
                self.decimal_spin.setValue(table_state["decimal_places"])
            
            # Update headers and redraw table
            self.update_headers()
            self.table.viewport().update()
            
            self.statusBar().showMessage(f"Table with formulas loaded: {file_name}", 5000)
            QMessageBox.information(self, "Success", "Table with formulas successfully loaded!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def get_column_index(self, column_name:str) -> int:
        """Find column index by name"""

        for col in range(self.table.model().columnCount()):
            header = self.table.model().headerData(col, Qt.Orientation.Horizontal)
            if header and header == column_name:
                return col
        return -1

    def get_data(self, x:int|str, y:int|str, lenght : int|None = None) -> np.ndarray:
        """Extract data from table for plotting."""

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
            lenght = self.table.model().rowCount() - 1
        
        for i in range(lenght + 1):
            # Get X value
            x_index = self.table.model().index(i, x)
            item_x = self.table.model().data(x_index, Qt.ItemDataRole.DisplayRole)
            x_flag = item_x is not None and item_x != ""
            
            # Get Y value
            y_index = self.table.model().index(i, y)
            item_y = self.table.model().data(y_index, Qt.ItemDataRole.DisplayRole)
            y_flag = item_y is not None and item_y != ""
            
            try:
                if x_flag:
                    item_x = float(item_x)
                else:
                    item_x = 0
                    x_flag = False
            except ValueError:
                item_x = 0
                x_flag = False
                
            try:
                if y_flag:
                    item_y = float(item_y)
                else:
                    item_y = 0
                    y_flag = False
            except ValueError:
                item_y = 0
                y_flag = False 
            
            if x_flag and y_flag:
                data[0].append(item_x)
                data[1].append(item_y)
        
        return np.array(data)

    def get_error_data(self, x:int|str, xerr:int|str, y:int|str, yerr:int|str, lenght : int|None = None) -> np.ndarray:
        """Extract data with errors for error bar plotting."""

        data = [[], [], [], []]
        
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
            lenght = self.table.model().rowCount() - 1
        
        for i in range(lenght + 1):
            # Get X value
            x_index = self.table.model().index(i, x)
            item_x = self.table.model().data(x_index, Qt.ItemDataRole.DisplayRole)
            x_flag = item_x is not None and item_x != ""
            
            # Get Y value
            y_index = self.table.model().index(i, y)
            item_y = self.table.model().data(y_index, Qt.ItemDataRole.DisplayRole)
            y_flag = item_y is not None and item_y != ""
            
            try:
                if x_flag:
                    item_x = float(item_x)
                else:
                    x_flag = False
            except ValueError:
                x_flag = False
                
            try:
                if y_flag:
                    item_y = float(item_y)
                else:
                    y_flag = False
            except ValueError:
                y_flag = False 
            
            if x_flag and y_flag:
                data[0].append(item_x)
                data[2].append(item_y)
                
                # Get X error
                if xerr != -1:
                    xerr_index = self.table.model().index(i, xerr)
                    item_xerr = self.table.model().data(xerr_index, Qt.ItemDataRole.DisplayRole)
                    try:
                        item_xerr = float(item_xerr) if item_xerr else 0
                    except ValueError:
                        item_xerr = 0
                else:
                    item_xerr = 0
                
                # Get Y error
                if yerr != -1:
                    yerr_index = self.table.model().index(i, yerr)
                    item_yerr = self.table.model().data(yerr_index, Qt.ItemDataRole.DisplayRole)
                    try:
                        item_yerr = float(item_yerr) if item_yerr else 0
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
        for col in range(self.table.model().columnCount()):
            header = self.table.model().headerData(col, Qt.Orientation.Horizontal)
            headers.append(header if header else f"Column {col+1}")
        self.data_updated.emit(headers)
    
    def get_headers(self):
        """Return all column headers."""

        return [self.table.model().headerData(col, Qt.Orientation.Horizontal) 
                if self.table.model().headerData(col, Qt.Orientation.Horizontal) 
                else f"Column {col+1}" for col in range(self.table.model().columnCount())]
  
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
            state = self.convert_numpy_types(state) 
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

    def _mainAppInfo(self) -> None:
        overview_text = """
                        <h2>ZAVLAB - Zingy Arina and Vladislav Laboratory Bot Assitant - Scientific Data Analysis and Visualization Tool</h2>
                        
                        <p>ZAVLAB provides a comprehensive environment for scientific data analysis 
                        and publication-quality visualization with an intuitive interface.</p>
                        
                        <p>This application combines powerful data management capabilities with 
                        advanced plotting features, allowing researchers to efficiently analyze 
                        and present their experimental results.</p>
                        
                        <p>Key strengths include Excel-like data manipulation, customizable multi-panel 
                        visualizations, and extensive export options for both data and graphics.</p>

                        <h3>Support and Resources</h3>
                        <p>For technical support, documentation, or to report issues, please contact:</p>
                        Email: zavlab.dev@yandex.ru
                        """
        QMessageBox.information(self, "About ZAVLAB", overview_text)

    def _tableGuide(self) -> None:
        overview_text = """
                        <b>1. Key information:</b>
                        <ul>
                        <li>Excel-like table with formula support and relative references</li>
                        <li>Import/export CSV datasets</li>
                        <li>Dynamic table editing with context menu controls</li>
                        <li>Add/remove rows and columns with multi-selection support</li>
                        <li>Decimal places control for numeric formatting</li>
                        </ul>
                        <b>2. Table Operations:</b>
                        <ul>
                        <li><b>Add/Remove Rows/Columns:</b> Right-click on row or column headers to access context menus</li>
                        <li><b>Multiple Selection:</b> Select multiple cells, rows, or columns for batch operations</li>
                        <li><b>Data Entry:</b> Direct cell editing with support for numeric and text data</li>
                        <li><b>Decimal Control:</b> Set the number of decimal places displayed for numeric data</li>
                        </ul>
                        
                        <b>3. Formula Support:</b>
                        <ul>
                        <li><b>Formulas:</b> to use values from other cells use this syntaxis: [column_name]index (e.g., =[Temp_1]1+[EDS]2 * 30 + 273)</li>
                        <li><b>Relative References:</b> Apply formulas with relative cell references across selections</li>
                        <li><b>Formula Bar:</b> Use the formula bar at the top to enter and edit formulas</li>
                        </ul>
                        
                        <b>4. Import/Export:</b>
                        <ul>
                        <li><b>CSV Import/Export:</b> Load/save data from/to CSV files (values only, no formulas)</li>
                        <li><b>JSON Import/Export:</b> Load/save complete table state including formulas</li>
                        <li><b>Header Preservation:</b> Column headers are preserved during import/export operations</li>
                        </ul>
                        """
        QMessageBox.information(self, "Table Guide", overview_text)

    def _plotGuide(self) -> None:
        overview_text = """
        <h3>Plotting System</h3>
        
        <p>ZAVLAB's advanced plotting system allows you to create complex multi-panel figures:</p>
        
        <b>Subplot Grid:</b>
        <ul>
        <li><b>Grid Creation:</b> Define rows and columns for your plot layout (up to 8x8)</li>
        <li><b>Subplot Placement:</b> Position subplots anywhere in the grid with row and column spans</li>
        <li><b>Visual Layout Editor:</b> See a visual representation of your subplot arrangement</li>
        <li><b>Overlap Prevention:</b> System prevents subplots from overlapping</li>
        </ul>
        
        <b>Data Series:</b>
        <ul>
        <li><b>Multiple Series:</b> Add multiple data series to a single subplot</li>
        <li><b>Error Bars:</b> Support for X and Y error bars with dedicated data columns</li>
        <li><b>Data Selection:</b> Choose X, Y, X-error, and Y-error data from your table columns</li>
        <li><b>Series Management:</b> Add (push button '+'), remove (push button '-'), and configure multiple data series in dialog</li>
        </ul>
        
        <b>Interactive Plot Features:</b>
        <ul>
        <li><b>Axis Configuration:</b> Click near axes to open configuration dialogs</li>
        <li><b>Title Editing:</b> Click on plot titles to edit them directly</li>
        <li><b>Legend Interaction:</b> Click on legends to configure their appearance and position</li>
        <li><b>Data Inspection:</b> Right-click on data points to view values and edit series properties</li>
        <li><b>Context Menus:</b> Right-click on plots for quick access to common options</li>
        </ul>
        
        <b>Plot Generation:</b>
        <ul>
        <li><b>Live Updates:</b> Plots update automatically after pushing 'Update something' button.</li>
        <li><b>Grid Display:</b> Toggle grid visibility with context menu options</li>
        <li><b>High-Quality Rendering:</b> Matplotlib-based rendering for publication-quality output</li>
        </ul>
        """
        QMessageBox.information(self, "Plot Guide", overview_text)

    def _editorGuide(self) -> None:
        overview_text = """
                <h3>Plot Customization Options</h3>
                
                <p>Extensive customization options allow you to create publication-ready figures:</p>
                
                <b>Axis Customization:</b>
                <ul>
                <li><b>Scale Selection:</b> Choose between linear and logarithmic scales for each axis</li>
                <li><b>Range Control:</b> Set precise minimum and maximum values for axis ranges</li>
                <li><b>Tick Control:</b> Customize the number of major and minor ticks</li>
                <li><b>Label Formatting:</b> Control decimal precision and formatting of axis labels</li>
                <li><b>Label Text:</b> Add descriptive axis labels with LaTeX support for mathematical notation</li>
                </ul>
                
                <b>Data Series Styling:</b>
                <ul>
                <li><b>Line Properties:</b> Control color, width, style, and transparency of data lines</li>
                <li><b>Marker Options:</b> Choose from various marker shapes and control their size</li>
                <li><b>Error Bar Styling:</b> Customize the appearance of error bars</li>
                <li><b>Series Labels:</b> Assign descriptive labels for legend entries</li>
                </ul>
                
                <b>Subplot Appearance:</b>
                <ul>
                <li><b>Title Formatting:</b> Customize subplot titles with font size control</li>
                <li><b>Legend Options:</b> Control legend position, font size, and frame visibility</li>
                <li><b>Grid Customization:</b> Toggle grid visibility and customize grid appearance</li>
                <li><b>Color Scheme:</b> Consistent color scheme across all plot elements</li>
                </ul>
            """
        QMessageBox.information(self, "Setting Guide", overview_text)

    def _LinesGuide(self) -> None:
        overview_text = """
    <h3>Lines and Annotations</h3>
    
    <p>Add analytical lines and annotations to your plots for better data interpretation:</p>
    
    <b>Line Creation Methods:</b>
    <ul>
    <li><b>Two Points:</b> Define a line by specifying two points (x1,y1) and (x2,y2)</li>
    <li><b>Equation:</b> Create a line from slope-intercept form (y = kx + b)</li>
    <li><b>Point and Angle:</b> Define a line by a point and an angle (in radians)</li>
    <li><b>Interactive Drawing:</b> Use the drawing tool to click and create lines directly on plots</li>
    </ul>
    
    <b>Line Styling:</b>
    <ul>
    <li><b>Color Selection:</b> Choose any color for your lines</li>
    <li><b>Width Control:</b> Adjust line thickness for visibility</li>
    <li><b>Style Options:</b> Select from solid, dashed, dash-dot, or dotted line styles</li>
    </ul>
    
    <b>Labels and Annotations:</b>
    <ul>
    <li><b>Text Labels:</b> Add descriptive labels to lines with LaTeX support</li>
    <li><b>Positioning:</b> Choose from 12 different label positions relative to the line</li>
    <li><b>Font Control:</b> Adjust label font size for optimal readability</li>
    <li><b>Background:</b> Labels have semi-transparent backgrounds for better visibility</li>
    </ul>
    
    <b>Line Management:</b>
    <ul>
    <li><b>Line Table:</b> View and manage all lines in a convenient table</li>
    <li><b>Selection:</b> Select lines to modify their properties</li>
    <li><b>Deletion:</b> Remove lines that are no longer needed</li>
    <li><b>Persistence:</b> Lines are saved with your plot configuration</li>
    </ul>
    """
        QMessageBox.information(self, "Lines Guide", overview_text)

    def _example(self) -> None:
        overview_text = """
    <h3>Recommended Workflow</h3>
    
    <p>Follow this workflow for efficient data analysis and visualization:</p>
    
    <ol>
    <li><b>Data Preparation:</b>
        <ul>
        <li>Import your data from CSV or enter manually</li>
        <li>Use formulas to calculate derived quantities</li>
        <li>Set appropriate decimal precision for display</li>
        </ul>
    </li>
    
    <li><b>Plot Setup:</b>
        <ul>
        <li>Define your plot grid dimensions (rows × columns)</li>
        <li>Add subplots to the grid at desired positions</li>
        <li>Assign data series to each subplot with error bars if needed</li>
        </ul>
    </li>
    
    <li><b>Plot Customization:</b>
        <ul>
        <li>Adjust axis ranges, scales, and labels</li>
        <li>Customize data series appearance (colors, markers, line styles)</li>
        <li>Add titles and configure legends</li>
        <li>Add analytical lines and annotations where needed</li>
        </ul>
    </li>
    
    <li><b>Interactive Refinement:</b>
        <ul>
        <li>Use click interactions to fine-tune axis settings</li>
        <li>Right-click on data points to inspect values and edit series properties</li>
        <li>Adjust subplot positions if needed</li>
        </ul>
    </li>
    
    <li><b>Export and Save:</b>
        <ul>
        <li>Save your plot configuration for future use</li>
        <li>Export high-quality images in various formats</li>
        <li>Export processed data if needed</li>
        </ul>
    </li>
    </ol>
    
    <p><b>Pro Tips:</b></p>
    <ul>
    <li>Use the auto-save feature to avoid losing work</li>
    <li>Save plot configurations at different stages of your analysis</li>
    <li>Use consistent styling across related plots for publication figures</li>
    <li>Take advantage of LaTeX formatting for professional-looking mathematical notation</li>
    </ul>
    """
        QMessageBox.information(self, "Example", overview_text)

    def get_min_max_from_column(self, x:int|str, lenght:None|int = None)->list[float]:
        """Get minimum and maximum values from a column."""
        
        data = []
        if type(x) == str:
            x = self.get_column_index(x)
        if lenght == None:
            lenght = self.table.model().rowCount() - 1
        
        for i in range(lenght + 1):
            index = self.table.model().index(i, x)
            item_x = self.table.model().data(index, Qt.ItemDataRole.DisplayRole)
            
            if item_x:
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
        """Get min/max values for all columns."""

        headers = self.get_headers()
        min_max = []
        for head in headers:
            min_max.append(self.get_min_max_from_column(head))
        return min_max
        
    def update_formula_bar(self):
        """Update the formula bar with the formula of the currently selected cell"""
        
        selected_indexes = self.table.selectionModel().selectedIndexes()
        current_index = self.table.selectionModel().currentIndex()
        
        if not current_index.isValid():
            self.formula_edit.clear()
            return
        
        # Display the formula of the current cell
        formula = self.table.model().data(current_index, Qt.ItemDataRole.EditRole)
        self.formula_edit.setText(formula)

    def apply_formula(self):
        """Apply the formula from the formula bar to the selected cells."""

        selected_indexes = self.table.selectionModel().selectedIndexes()
        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "No cells selected")
            return
        
        formula = self.formula_edit.text()
        count = 0
        
        for index in selected_indexes:
            if self.table.model().setData(index, formula, Qt.ItemDataRole.EditRole):
                count += 1
        
        self.statusBar().showMessage(f"Formula applied to {count} cells", 3000)

    def refresh_table(self):
        """Refresh the table view after data changes"""
        
        self.table.viewport().update()

    def change_decimal_places(self, value):
        """Change decimal places setting and refresh display."""

        # Update the decimal places setting
        self.model.decimal_places = value
        # Refresh the view to show the new formatting
        self.model.evaluate_all()
    
    def show_decimal_dialog(self):
        """Show dialog to set decimal places."""
        
        # Show a dialog to set decimal places
        value, ok = QtWidgets.QInputDialog.getInt(
            self, 
            "Decimal Places", 
            "Enter number of decimal places:", 
            value=self.model.decimal_places,
            min=0, 
            max=10
        )
        
        if ok:
            self.model.decimal_places = value
            self.decimal_spin.setValue(value)
            # Refresh the view to show the new formatting
            self.model.evaluate_all()

    def apply_formula_with_relative_refs(self):
        """Apply formula with relative references to selected cells."""

        selected_indexes = self.table.selectionModel().selectedIndexes()
        if not selected_indexes:
            self.statusBar().showMessage("No cells selected")
            return
        
        base_formula = self.formula_edit.text()
        if not base_formula:
            self.statusBar().showMessage("No formula entered")
            return
        
        base_index = self.table.selectionModel().currentIndex()
        if not base_index.isValid():
            self.statusBar().showMessage("No base cell selected")
            return
        
        count = 0
        
        for index in selected_indexes:
            row_offset = index.row() - base_index.row()
            col_offset = index.column() - base_index.column()
            
            # Adjust the formula for relative references
            adjusted_formula = self.model.adjust_formula_references(base_formula, row_offset, col_offset)
            if self.model.setData(index, adjusted_formula):
                count += 1
        
        self.statusBar().showMessage(f"Formula with relative references applied to {count} cells")


    def restore_state(self):
        """Try to load last autosave state."""

        (state, sub_state) = self.auto_save_manager.load_backup()
        if state:
            reply = QMessageBox.question(
                self, 
                "Restoring settings",
                "Saved settings are detected. Restore them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.apply_state(state)
                self.plotter.set_state(sub_state)
    
    def closeEvent(self, event):
        """Handle application close event with autosave."""
        try:
            # Get the complete state including formulas
            state = self.get_state()
            sub_state = self.plotter.get_state()  
            
            # Save with formulas
            self.auto_save_manager.save_to_file(
                sub_state, 
                state, 
                "./files/sub_setting_final.json",
                "./files/settings_final.json"
            )
        except Exception as e:
            logging.error(f"Saving error when closing: {str(e)}")
        
        event.accept()


    def get_state(self):
        """Return complete application state for saving."""

        state = {
            "table": {
                "decimal_places": self.model.decimal_places,
                "column_names": self.model._column_names,
                "formulas": self.model._formulas,
                "row_count": self.model.rowCount(),
                "column_count": self.model.columnCount()
            },
            "window": {
                "geometry": self.saveGeometry().toHex().data().decode(),
                "state": self.saveState().toHex().data().decode()
            },
            "splitter_sizes": [size for size in self.central_widget_splitter.sizes()],
            "plotter": self.convert_numpy_types(self.plotter.get_state()) if hasattr(self, 'plotter') else None
        }
        return state

    def apply_state(self, state):
        """Restore application state from saved data."""

        if not state:
            return
        
        try:
            # Restore table state
            if "table" in state:
                table_state = state["table"]
                
                # Set row and column count
                self.model.setRowCount(table_state["row_count"])
                self.model.setColumnCount(table_state["column_count"])
                
                # Restore column names
                for col, name in enumerate(table_state["column_names"]):
                    self.model.setHeaderData(col, Qt.Orientation.Horizontal, name)
                
                # Restore formulas
                for row in range(table_state["row_count"]):
                    for col in range(table_state["column_count"]):
                        if row < len(table_state["formulas"]) and col < len(table_state["formulas"][row]):
                            index = self.model.index(row, col)
                            formula = table_state["formulas"][row][col]
                            self.model.setData(index, formula, Qt.ItemDataRole.EditRole)
                
                # Restore decimal places
                if "decimal_places" in table_state:
                    self.model.decimal_places = table_state["decimal_places"]
                    self.decimal_spin.setValue(table_state["decimal_places"])
            
            # Restore splitter sizes
            if "splitter_sizes" in state:
                self.central_widget_splitter.setSizes(state["splitter_sizes"])
            
            # Restore window state
            if "window" in state:
                window_state = state["window"]
                if "geometry" in window_state:
                    self.restoreGeometry(bytes.fromhex(window_state["geometry"]))
                if "state" in window_state:
                    self.restoreState(bytes.fromhex(window_state["state"]))
            
            # Restore plotter state
            if "plotter" in state and state["plotter"] and hasattr(self, 'plotter'):
                self.plotter.set_state(state["plotter"])
                
            # Update headers
            self.update_headers()
            
        except Exception as e:
            logging.error(f"Status recovery error: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to restore state: {str(e)}")


    def convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization."""
        
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_numpy_types(item) for item in obj]
        return obj

