import sys
import re
import ast
import operator as op
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import math
import statistics
import random
from PyQt6.QtCore import pyqtSignal

class ExcelLikeModel(QtCore.QAbstractTableModel):
    """Excel-like table model with formula support and relative references."""
    
    def __init__(self, rows=20, cols=10):
        """Initialize the table model with data, formulas, and dependencies."""
        super().__init__()
        self._data = [['' for _ in range(cols)] for _ in range(rows)]
        self._formulas = [['' for _ in range(cols)] for _ in range(rows)]
        self._dependencies = {}  # Track cell dependencies: {source: [dependents]}
        
        # Initialize custom column names (default to Excel-style: A, B, C, ...)
        self._column_names = [self.index_to_column_name(i) for i in range(cols)]
        self.last_columnn_name = cols
        # Decimal places setting (default to 2)
        self.decimal_places = 2
        
        # Safe evaluation operators
        self._safe_operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.FloorDiv: op.floordiv,
            ast.Mod: op.mod,
            ast.Pow: op.pow,
            ast.USub: op.neg,
            ast.UAdd: op.pos,
            ast.Eq: op.eq,
            ast.NotEq: op.ne,
            ast.Lt: op.lt,
            ast.LtE: op.le,
            ast.Gt: op.gt,
            ast.GtE: op.ge,
        }
        
        # Mathematical functions
        self._safe_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e,
            'rand': random.random,
            'randint': random.randint,
            'mean': statistics.mean,
            'median': statistics.median,
            'stdev': statistics.stdev,
            'len': len,
            'int': int,
            'float': float,
            'str': str
        }
        self.cell_patern = r'(\[([A-Za-z_][A-Za-z0-9_]*)\])(\d+)'

    def rowCount(self, parent=None):
        """Return number of rows in the model."""
        
        return len(self._data)

    def columnCount(self, parent=None):
        """Return number of columns in the model."""
        
        return len(self._data[0])
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return header data for the given section and orientation."""        
        
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Return custom column name
                return self._column_names[section]
            else:
                # Return row numbers (starting from 1)
                return str(section + 1)
        elif role == Qt.ItemDataRole.EditRole and orientation == Qt.Orientation.Horizontal:
            # Return current column name for editing
            return self._column_names[section]
        return None

    def setHeaderData(self, section, orientation, value, role=Qt.ItemDataRole.EditRole):
        """Set header data for the given section and orientation."""
        
        if (orientation == Qt.Orientation.Horizontal and 
            role == Qt.ItemDataRole.EditRole and 
            0 <= section < len(self._column_names)):
            # Update the column name
            self._column_names[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False

    def flags(self, index):
        """Return the item flags for the given index."""
        
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        
        # Make cells editable
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return data for the given role and index."""
        
        if not index.isValid():
            return None
            
        if role == Qt.ItemDataRole.DisplayRole:
            # Evaluate the cell for display
            result = self.evaluate_cell(index.row(), index.column())
            
            # Format numbers with the specified decimal places
            try:
                # Try to convert to float and format
                num_value = float(result)
                return f"{num_value:.{self.decimal_places}f}"
            except (ValueError, TypeError):
                # If it's not a number, return as is
                return str(result)
                
        elif role == Qt.ItemDataRole.EditRole:
            # Return the formula for editing
            return self._formulas[index.row()][index.column()]
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Right-align numbers, left-align text
            try:
                float(self.evaluate_cell(index.row(), index.column()))
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            except (ValueError, TypeError):
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Set data at index to value for the given role."""

        if role == Qt.ItemDataRole.EditRole:
            row, col = index.row(), index.column()
            
            # Clear previous dependencies for this cell
            self.clear_dependencies(row, col)
            
            # Set the formula
            self._formulas[row][col] = value
            
            # If it's a formula, parse and set up dependencies
            if value.startswith('='):
                try:
                    # Find all cell references in the formula
                    pattern = self.cell_patern
                    matches = re.findall(pattern, value)
                    for col_ref, row_ref in matches:
                        # Find column index by name
                        col_idx = self.column_name_to_index(col_ref)
                        ref_row_idx = int(row_ref) - 1
                        
                        # Add dependency tracking
                        ref_key = (ref_row_idx, col_idx)
                        if ref_key not in self._dependencies:
                            self._dependencies[ref_key] = []
                        if (row, col) not in self._dependencies[ref_key]:
                            self._dependencies[ref_key].append((row, col))
                except:
                    pass
            
            # Recalculate all formulas
            self.evaluate_all()
            
            # Notify the view that data has changed
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self.rowCount() - 1, self.columnCount() - 1)
            )
            return True
        return False

    def evaluate_cell(self, row, col):
        """Evaluate the formula in the specified cell."""

        formula = self._formulas[row][col]
        if not formula.startswith('='):
            return formula

        try:
            # Remove the equals sign and any spaces
            expression = formula[1:].replace(' ', '')
            expression = expression.split(", ")[0]

            # Replace Excel-style power operator (^) with Python-style (**)
            expression = expression.replace('^', '**')

            # Convert cell references (e.g., A1, B2) to their values
            pattern = self.cell_patern
            
            def replace_match(match):
                full_match = match.group(1)
                col_ref = match.group(2).upper()
                row_ref = int(match.group(3)) - 1 
                
                # Find column index by name
                col_index = self.column_name_to_index(col_ref)

                # Check if the reference is within bounds
                if 0 <= row_ref < self.rowCount() and 0 <= col_index < self.columnCount():
                    cell_value = self.evaluate_cell(row_ref, col_index)
                    if self.is_number(cell_value):
                        return str(float(cell_value))
                    else:
                        # If it's a string, wrap it in quotes for the expression
                        return f'"{cell_value}"'
                else:
                    return '0'  # Out of bounds reference becomes 0
            
            # Replace all cell references with their values
            expression = re.sub(pattern, replace_match, expression)
            
            # Use safe evaluation
            return self._safe_eval(expression)
            
        except Exception as e:
            return f"#ERROR! ({str(e)})"

    def _safe_eval(self, expr):
        """Safely evaluate a mathematical expression"""
        
        try:
            # Parse the expression into an AST
            tree = ast.parse(expr, mode='eval')
            
            # Define a function to recursively evaluate the AST
            def _eval(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.Str):
                    return node.s
                elif isinstance(node, ast.BinOp):
                    left = _eval(node.left)
                    right = _eval(node.right)
                    operator_type = type(node.op)
                    
                    if operator_type in self._safe_operators:
                        # Handle power operator specifically
                        if operator_type is ast.Pow:
                            # Ensure we don't allow very large exponents for safety
                            if abs(right) > 1000:
                                raise ValueError("Exponent too large")
                            return self._safe_operators[operator_type](left, right)
                        else:
                            return self._safe_operators[operator_type](left, right)
                    else:
                        raise ValueError(f"Unsupported operator: {operator_type}")
                elif isinstance(node, ast.UnaryOp):
                    operand = _eval(node.operand)
                    operator_type = type(node.op)
                    
                    if operator_type in self._safe_operators:
                        return self._safe_operators[operator_type](operand)
                    else:
                        raise ValueError(f"Unsupported operator: {operator_type}")
                elif isinstance(node, ast.Call):
                    # Handle function calls
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in self._safe_functions:
                            args = [_eval(arg) for arg in node.args]
                            return self._safe_functions[func_name](*args)
                        else:
                            raise ValueError(f"Unsupported function: {func_name}")
                    else:
                        raise ValueError("Unsupported function call type")
                elif isinstance(node, ast.Name):
                    # Handle named constants
                    if node.id in self._safe_functions and not callable(self._safe_functions[node.id]):
                        return self._safe_functions[node.id]
                    else:
                        raise ValueError(f"Unknown name: {node.id}")
                else:
                    raise ValueError(f"Unsupported expression type: {type(node)}")
            
            return _eval(tree.body)
        except Exception as e:
            raise ValueError(f"Evaluation error: {str(e)}")

    def evaluate_all(self):
        """Recalculate all formulas in the table."""

        # Recalculate all formulas
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1)
        )
    
    def is_number(self, s):
        """Check if a string can be converted to a number."""

        try:
            float(s)
            return True
        except ValueError:
            return False

    def column_name_to_index(self, name):
        """Convert column name to index (supports both default and custom names)."""

        try:
            # First try to find by custom name (case-insensitive)
            name_upper = name.upper()
            for i, col_name in enumerate(self._column_names):
                if col_name.upper() == name_upper:
                    return i
            # If not found, try Excel-style conversion for backward compatibility
            index = 0
            for char in name.upper():
                if 'A' <= char <= 'Z':
                    index = index * 26 + (ord(char) - ord('A') + 1)
                else:
                    # If we encounter a non-letter character, it's not a valid Excel-style name
                    raise ValueError(f"Invalid column name: {name}")
            return index - 1
        except ValueError:
            # If the name doesn't match any pattern, return -1 (invalid)
            return -1

    def index_to_column_name(self, index):
        """Convert zero-based column index to Excel-style name (A, B, ...)."""
        
        name = ""
        index += 1
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            name = chr(65 + remainder) + name
        return name

    def clear_dependencies(self, row, col):
        """Remove this cell from all dependency lists."""

        for key in list(self._dependencies.keys()):
            if (row, col) in self._dependencies[key]:
                self._dependencies[key].remove((row, col))
                if not self._dependencies[key]:
                    del self._dependencies[key]
                    
    def adjust_formula_references(self, formula, row_offset, col_offset):
        """Adjust formula references based on row and column offsets."""
        
        if not formula.startswith('='):
            return formula
        
        # Pattern to match cell references (e.g., A1, BC23)
        pattern = self.cell_patern
        
        def adjust_match(match):
            full_match = match.group(1)
            col_name = match.group(2)
            row_num = int(match.group(3))
            
            # Convert column name to index, adjust, then back to name
            col_idx = self.column_name_to_index(col_name)
            if col_idx == -1:
                return full_match
            
            adjusted_col_idx = col_idx + col_offset
            adjusted_row = row_num + row_offset
            
            # Check if adjusted indices are valid
            if (0 <= adjusted_col_idx < self.columnCount() and 
                1 <= adjusted_row <= self.rowCount()):  # Note: row numbers are 1-based
                adjusted_col_name = self._column_names[adjusted_col_idx]
                return f"[{adjusted_col_name}]{adjusted_row}"
            else:
                # Return original reference if adjusted is out of bounds
                return full_match
        
        try:
            adjusted_formula = re.sub(pattern, adjust_match, formula)
            return adjusted_formula
        except:
            return formula

    def insertColumn(self, column, parent=QtCore.QModelIndex()):
        """Insert a new column at the specified position"""
        
        self.beginInsertColumns(parent, column, column)
        for row in self._data:
            row.insert(column, '')
        for row in self._formulas:
            row.insert(column, '')
        self._column_names.insert(column, self.index_to_column_name(self.last_columnn_name))
        self.last_columnn_name += 1
        self.endInsertColumns()
        return True

    def removeColumn(self, column, parent=QtCore.QModelIndex()):
        """Remove the column at the specified position"""
        
        if column < 0 or column >= self.columnCount():
            return False
            
        self.beginRemoveColumns(parent, column, column)
        for row in self._data:
            del row[column]
        for row in self._formulas:
            del row[column]
        del self._column_names[column]
        self.endRemoveColumns()
        return True

    def insertRow(self, row, parent=QtCore.QModelIndex()):
        """Insert a new row at the specified position"""
        
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, [''] * self.columnCount())
        self._formulas.insert(row, [''] * self.columnCount())
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        """Remove the row at the specified position"""
        
        if row < 0 or row >= self.rowCount():
            return False
            
        self.beginRemoveRows(parent, row, row)
        del self._data[row]
        del self._formulas[row]
        self.endRemoveRows()
        return True
    
    def setColumnCount(self, cols):
        """Set the number of columns in the model"""
        
        current_cols = self.columnCount()
        if cols > current_cols:
            # Add columns
            for _ in range(cols - current_cols):
                self.insertColumn(current_cols)
        elif cols < current_cols:
            # Remove columns
            for _ in range(current_cols - cols):
                self.removeColumn(current_cols - 1)
        return True

    def setRowCount(self, rows):
        """Set the number of rows in the model"""
        
        current_rows = self.rowCount()
        if rows > current_rows:
            # Add rows
            for _ in range(rows - current_rows):
                self.insertRow(current_rows)
        elif rows < current_rows:
            # Remove rows
            for _ in range(current_rows - rows):
                self.removeRow(current_rows - 1)
        return True

class FormulaLineEdit(QtWidgets.QLineEdit):
    """Line edit widget specialized for formula input."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enter formula (e.g., =[A]1+[B]2). Column name should be placed in sqaure brackets.")


class ExcelTableView(QtWidgets.QTableView):
    """Excel-like table view with extended selection and header editing."""
    
    table_headers_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize the table ui"""

        super().__init__(parent)
        # Set selection mode for Excel-like extended selection
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        
        # Enable dragging and set appropriate drag drop mode
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        
        # Enable column header editing
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().sectionDoubleClicked.connect(self.editColumnHeader)
        self.horizontalHeader().setToolTip("To change column name click the cell with label two times.\n"
                                            "If you want to enter units according to the values, enter them after comma.\n"
                                            "For example: \"lenght, m\"")
        
    def editColumnHeader(self, section):
        """Edit the column header at the given section."""
        
        # Get the current column name
        current_name = self.model().headerData(section, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        
        # Show a dialog to edit the column name
        new_name, ok = QtWidgets.QInputDialog.getText(
            self, 
            "Edit Column Name", 
            "Enter new column name:", 
            text=current_name
        )
        
        if ok and new_name:
            # Validate the column name
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', new_name):
                # Set the new column name
                self.model().setHeaderData(section, Qt.Orientation.Horizontal, new_name)
            else:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Invalid Column Name", 
                    "Column names must start with a letter or underscore and can only contain letters, numbers, and underscores."
                )
        self.table_headers_signal.emit("change headers")
        
    def mousePressEvent(self, event):
        """Handle mouse press events for selection."""
        
        index = self.indexAt(event.pos())
        selection_model = self.selectionModel()
        modifiers = event.modifiers()
        
        if not index.isValid():
            selection_model.clearSelection()
            return super().mousePressEvent(event)
        
        # Handle different selection modes based on modifier keys
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Click: Toggle selection of individual cells
            if selection_model.isSelected(index):
                selection_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.Deselect)
            else:
                selection_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.Select)
        elif modifiers & Qt.KeyboardModifier.ShiftModifier:
            # Shift+Click: Select range from current to clicked cell
            current_index = selection_model.currentIndex()
            if current_index.isValid():
                top = min(current_index.row(), index.row())
                bottom = max(current_index.row(), index.row())
                left = min(current_index.column(), index.column())
                right = max(current_index.column(), index.column())
                
                selection = QtCore.QItemSelection(
                    self.model().index(top, left),
                    self.model().index(bottom, right)
                )
                selection_model.select(selection, QtCore.QItemSelectionModel.SelectionFlag.Select)
        else:
            # Regular click: Select single cell and set as current
            selection_model.setCurrentIndex(index, QtCore.QItemSelectionModel.SelectionFlag.NoUpdate)
            selection_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.Select | 
                                                  QtCore.QItemSelectionModel.SelectionFlag.Current)
        
        # Call parent to handle other events
        super().mousePressEvent(event)
