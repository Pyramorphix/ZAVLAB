import sys
import pandas as pd
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QToolBar, QStatusBar, QFileDialog, QInputDialog, QMessageBox, 
                             QVBoxLayout, QWidget, QHeaderView)
from PyQt6.QtGui import QAction, QIcon, QFont, QColor
from PyQt6.QtCore import Qt
import sympy as sp
from sympy.parsing.latex import parse_latex

class SpreadsheetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('LaTeX Spreadsheet with Cell References')
        self.setGeometry(100, 100, 900, 650)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create table widget
        self.table = QTableWidget()
        self.table.setRowCount(10)
        self.table.setColumnCount(2)
        layout.addWidget(self.table)
        
        # Set column headers to numbers initially
        self.table.setHorizontalHeaderLabels(['1', '2'])
        
        # Enable editing of headers
        self.table.horizontalHeader().sectionDoubleClicked.connect(self.edit_header)
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Connect cell changed signal
        self.table.cellChanged.connect(self.on_cell_changed)
        
        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add actions
        add_row_action = QAction('Add Row', self)
        add_row_action.triggered.connect(self.add_row)
        toolbar.addAction(add_row_action)
        
        add_col_action = QAction('Add Column', self)
        add_col_action.triggered.connect(self.add_column)
        toolbar.addAction(add_col_action)
        
        add_multiple_rows_action = QAction('Add Multiple Rows', self)
        add_multiple_rows_action.triggered.connect(self.add_multiple_rows)
        toolbar.addAction(add_multiple_rows_action)
        
        add_multiple_cols_action = QAction('Add Multiple Columns', self)
        add_multiple_cols_action.triggered.connect(self.add_multiple_columns)
        toolbar.addAction(add_multiple_cols_action)
        
        import_action = QAction('Import', self)
        import_action.triggered.connect(self.import_file)
        toolbar.addAction(import_action)
        
        export_action = QAction('Export', self)
        export_action.triggered.connect(self.export_file)
        toolbar.addAction(export_action)
        
        # Add evaluate all formulas action
        evaluate_action = QAction('Evaluate All', self)
        evaluate_action.triggered.connect(self.evaluate_all_formulas)
        toolbar.addAction(evaluate_action)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Show initial status
        self.update_status()
        
        # Add some sample data and formulas
        self.initialize_sample_data()
        
    def initialize_sample_data(self):
        # Set some sample values
        sample_items = [
            (0, 0, "5"),
            (1, 0, "10"),
            (2, 0, "15"),
            (0, 1, "=1*2"),  # Simple formula without reference
            (1, 1, "=5+10"),  # Another simple formula
        ]
        
        for row, col, value in sample_items:
            item = QTableWidgetItem(value)
            self.table.setItem(row, col, item)
            
            # If it's a formula, evaluate it
            if value.startswith('='):
                self.evaluate_cell(row, col)
        
    def update_status(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        self.statusBar.showMessage(f"Rows: {rows}, Columns: {cols}")
        
    def add_row(self):
        current_row_count = self.table.rowCount()
        self.table.setRowCount(current_row_count + 1)
        self.update_status()
        
    def add_column(self):
        current_col_count = self.table.columnCount()
        self.table.setColumnCount(current_col_count + 1)
        # Update column header with numeric value
        self.table.setHorizontalHeaderItem(current_col_count, QTableWidgetItem(str(current_col_count + 1)))
        self.update_status()
        
    def add_multiple_rows(self):
        num, ok = QInputDialog.getInt(self, 'Add Rows', 'How many rows to add?', 1, 1, 100, 1)
        if ok:
            current_row_count = self.table.rowCount()
            self.table.setRowCount(current_row_count + num)
            self.update_status()
        
    def add_multiple_columns(self):
        num, ok = QInputDialog.getInt(self, 'Add Columns', 'How many columns to add?', 1, 1, 100, 1)
        if ok:
            current_col_count = self.table.columnCount()
            self.table.setColumnCount(current_col_count + num)
            # Update column headers with numeric values
            for i in range(current_col_count, current_col_count + num):
                self.table.setHorizontalHeaderItem(i, QTableWidgetItem(str(i + 1)))
            self.update_status()
    
    def edit_header(self, index):
        # Get current header text
        current_text = self.table.horizontalHeaderItem(index).text()
        
        # Ask user for new header text
        new_text, ok = QInputDialog.getText(self, 'Edit Column Header', 
                                           'Enter new column title:', 
                                           text=current_text)
        if ok and new_text:
            self.table.setHorizontalHeaderItem(index, QTableWidgetItem(new_text))
    
    def on_cell_changed(self, row, column):
        item = self.table.item(row, column)
        if item is not None:
            text = item.text().strip()
            # Check if the text starts with '=' (formula)
            if text.startswith('='):
                item.setData(Qt.ItemDataRole.UserRole, text)  # Store original formula
                self.evaluate_cell(row, column)
            else:
                item.setData(Qt.ItemDataRole.UserRole, None)  # Clear formula storage
                item.setForeground(QColor(0, 0, 0))  # Regular text color
                
                # If this cell might be referenced by other formulas, update them
                self.update_dependent_formulas(row, column)
    
    def evaluate_cell(self, row, column):
        """Evaluate the formula in a specific cell"""
        item = self.table.item(row, column)
        if item is None:
            return
            
        formula = item.data(Qt.ItemDataRole.UserRole)
        if not formula or not formula.startswith('='):
            return
            
        formula = formula[1:].strip()  # Remove the '=' prefix
        
        try:
            # Try to parse as LaTeX, handling cell references
            result = self.evaluate_formula_with_references(formula)
            self.table.blockSignals(True)
            item.setText(str(result))
            self.table.blockSignals(False)
            item.setForeground(QColor(0, 0, 255))  # Blue color for formula results
        except Exception as e:
            item.setForeground(QColor(0, 0, 0))  # Revert to black on error
            self.statusBar.showMessage(f"Error in formula: {str(e)}")
            # Show the error in the cell
            self.table.blockSignals(True)
            item.setText(f"Error: {str(e)}")
            self.table.blockSignals(False)
    
    def update_dependent_formulas(self, changed_row, changed_col):
        """Update all formulas that might reference the changed cell"""
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and item.data(Qt.ItemDataRole.UserRole):
                    formula = item.data(Qt.ItemDataRole.UserRole)[1:]  # Remove '='
                    # Check if this formula references the changed cell
                    if self.does_formula_reference_cell(formula, changed_row, changed_col):
                        # Re-evaluate the formula
                        self.evaluate_cell(row, col)
    
    def does_formula_reference_cell(self, formula, row, col):
        """Check if a formula references a specific cell"""
        # Get column header (might be text or number)
        col_header = self.table.horizontalHeaderItem(col).text()
        
        # Pattern to match cell references (like A1, B2, etc.)
        pattern = r'([A-Za-z]+)(\d+)'
        matches = re.findall(pattern, formula)
        
        for col_ref, row_ref in matches:
            if col_ref == col_header and int(row_ref) == row + 1:  # +1 because rows are 1-indexed in references
                return True
        
        return False
    
    def evaluate_formula_with_references(self, formula):
        """Evaluate a formula that may contain cell references"""
        # Replace cell references with their values
        processed_formula = self.replace_cell_references(formula)
        
        # Now evaluate as LaTeX
        return self.evaluate_latex(processed_formula)
    
    def replace_cell_references(self, formula):
        """Replace Excel-style cell references (A1, B2) with their values"""
        # Pattern to match cell references (like A1, B2, etc.)
        pattern = r'([A-Za-z]+)(\d+)'
        matches = re.findall(pattern, formula)
        
        for col_ref, row_ref in matches:
            # Find the column index from the header text
            col_index = -1
            for j in range(self.table.columnCount()):
                header_item = self.table.horizontalHeaderItem(j)
                if header_item and header_item.text() == col_ref:
                    col_index = j
                    break
            
            if col_index == -1:
                raise Exception(f"Column '{col_ref}' not found")
            
            # Convert row reference to index (1-based to 0-based)
            row_index = int(row_ref) - 1
            
            if row_index < 0 or row_index >= self.table.rowCount():
                raise Exception(f"Row {row_ref} is out of range")
            
            # Get the cell value
            cell_item = self.table.item(row_index, col_index)
            if cell_item is None:
                cell_value = "0"
            else:
                cell_value = cell_item.text()
            
            # Try to convert to number if possible
            try:
                # If it's a number, use it directly
                float_value = float(cell_value)
                formula = formula.replace(f"{col_ref}{row_ref}", str(float_value))
            except ValueError:
                # If it's not a number, keep it as is (might be text or another formula)
                formula = formula.replace(f"{col_ref}{row_ref}", cell_value)
        
        return formula
    
    def evaluate_latex(self, latex_str):
        try:
            # Parse LaTeX to sympy expression
            expr = parse_latex(latex_str)
            # Evaluate the expression
            result = expr.evalf()
            return result
        except Exception as e:
            # If LaTeX parsing fails, try to evaluate as a regular expression
            try:
                # This handles simple arithmetic expressions
                result = eval(latex_str, {"__builtins__": None}, {})
                return result
            except:
                raise Exception(f"Evaluation error: {str(e)}")
    
    def evaluate_all_formulas(self):
        """Re-evaluate all formulas in the spreadsheet"""
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and item.data(Qt.ItemDataRole.UserRole):
                    self.evaluate_cell(row, col)
        
        self.statusBar.showMessage("All formulas evaluated")
    
    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.table.setRowCount(df.shape[0])
                self.table.setColumnCount(df.shape[1])
                
                # Set column headers (use numeric if no header exists)
                for i in range(df.shape[1]):
                    col_name = str(df.columns[i]) if i < len(df.columns) else str(i + 1)
                    self.table.setHorizontalHeaderItem(i, QTableWidgetItem(col_name))
                
                # Populate table
                for i in range(df.shape[0]):
                    for j in range(df.shape[1]):
                        value = str(df.iat[i, j]) if pd.notna(df.iat[i, j]) else ""
                        item = QTableWidgetItem(value)
                        self.table.setItem(i, j, item)
                        
                        # If it's a formula, evaluate it
                        if value.startswith('='):
                            item.setData(Qt.ItemDataRole.UserRole, value)
                            self.evaluate_cell(i, j)
                
                self.update_status()
                self.statusBar.showMessage(f"Imported successfully from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import file: {str(e)}")
    
    def export_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                # Ensure file has the correct extension
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                
                # Collect data from table
                data = []
                for i in range(self.table.rowCount()):
                    row_data = []
                    for j in range(self.table.columnCount()):
                        item = self.table.item(i, j)
                        if item is not None:
                            # Use stored formula if available, otherwise use displayed text
                            formula = item.data(Qt.ItemDataRole.UserRole)
                            if formula:
                                row_data.append(formula)
                            else:
                                row_data.append(item.text())
                        else:
                            row_data.append("")
                    data.append(row_data)
                
                # Get column headers
                headers = []
                for j in range(self.table.columnCount()):
                    header_item = self.table.horizontalHeaderItem(j)
                    headers.append(header_item.text() if header_item else str(j + 1))
                
                # Create DataFrame and save
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_path, index=False)
                
                self.statusBar.showMessage(f"Exported successfully to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = SpreadsheetApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()