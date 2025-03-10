from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QMenuBar, QAction, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QDialog, 
                             QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, 
                             QFormLayout, QSpinBox, QDialogButtonBox)
from PyQt5.QtCore import Qt

from ZAVLAB.spreadsheet_generator import *




class AddExperimentDialog(QDialog):

    # ---------------------------------------------------------------------------
    def __init__(self):

        # Initializing window layout
        super().__init__()
        self.setWindowTitle("Add Experiment")
        layout = QFormLayout()


        # Input fields
        self.title_input = QLineEdit()
        self.amount_input = QSpinBox()
        self.amount_input.setValue(DEFAULT_EXPERIMENT_AMOUNT)

        layout.addRow("Title:", self.title_input)
        layout.addRow("Amount:", self.amount_input)


        # "OK" and "Cancel" buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


        self.setLayout(layout)
    # ---------------------------------------------------------------------------



    # -----------------------------------------------------------
    def get_data(self):
        return self.title_input.text(), self.amount_input.value()
    # -----------------------------------------------------------





class AddFieldDialog(QDialog):

    # ---------------------------------------------------------------------------
    def __init__(self):

        # Initializing window layout
        super().__init__()
        self.setWindowTitle("Add Field")
        layout = QFormLayout()


        # Input fields
        self.type_input = QComboBox()
        self.type_input.addItems(['gathered', 'calculated', 'const'])
        self.label_input = QLineEdit()
        self.unit_input = QLineEdit()
        self.error_input = QLineEdit()
        self.formula_input = QLineEdit()
        self.value_input = QLineEdit()

        layout.addRow("Type:", self.type_input)
        layout.addRow("Label:", self.label_input)
        layout.addRow("Unit:", self.unit_input)
        layout.addRow("Error:", self.error_input)
        self.formula_input.setVisible(False)
        layout.addRow("Formula:", self.formula_input)
        self.value_input.setVisible(False)
        layout.addRow("Value:", self.value_input)


        # Make input visibility update on field type change
        self.type_input.currentTextChanged.connect(self.update_fields)


        # "OK" and "Cancel" buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


        self.setLayout(layout)
    # ---------------------------------------------------------------------------



    # ------------------------------------------------------------------
    def update_fields(self):

        # Get selected field type
        field_type = self.type_input.currentText()

        # Make corresponding input fields visible
        self.error_input.setVisible(field_type in ('gathered', 'const'))
        self.formula_input.setVisible(field_type == 'calculated')
        self.value_input.setVisible(field_type == 'const')
    # ------------------------------------------------------------------



    # -----------------------------------------------------------------------------
    def get_data(self):

        field_type = self.type_input.currentText()
        label = self.label_input.text()
        unit = self.unit_input.text()
        error = self.error_input.text() if field_type == 'gathered' or 'const' else None
        formula = self.formula_input.text() if field_type == 'calculated' else None
        value = self.value_input.text() if field_type == 'const' else None

        return field_type, label, unit, error, formula, value
    # -----------------------------------------------------------------------------





class MainWindow(QMainWindow):

    # ----------------------------------
    def __init__(self):
        super().__init__()
        self.spreadsheet = Spreadsheet()
        self.initUI()
    # ----------------------------------

    # --------------------------------------------------------------
    def initUI(self):

        # Window params
        self.setWindowTitle("ZAVLAB")  # Tiling WMs ignore this lol
        self.setGeometry(100, 100,  800,   600)  # And this :)
        #                 x    y   width  height

        # Experiment tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)


        # Top-left menu buttons
        # File | Experiment | Field
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        experiment_menu = menubar.addMenu("Experiment")
        field_menu = menubar.addMenu("Field")

        # save_action = QAction("Open", self)
        # save_action.triggered.connect()
        # file_menu.addAction(save_action)

        add_experiment_action = QAction("Add Experiment", self)
        add_experiment_action.triggered.connect(self.add_experiment)
        experiment_menu.addAction(add_experiment_action)

        add_field_action = QAction("Add Field", self)
        add_field_action.triggered.connect(self.add_field)
        field_menu.addAction(add_field_action)
    # --------------------------------------------------------------



    # ---------------------------------------------------------
    def add_experiment(self):

        # Call the dialog window
        dialog = AddExperimentDialog()


        # If user pressed "OK"
        if dialog.exec_() == QDialog.Accepted:

            # Extract data from user input
            title, amount = dialog.get_data()

            # Add experiment to spreadsheet
            experiment = Experiment(title=title, amount=amount)
            self.spreadsheet.add_experiment(experiment)

            # Make a table for the experiment
            table = QTableWidget()

            # Make a tab for the table
            self.tabs.addTab(table, experiment.title)

            # Write experiment data to the table
            self.update_table(table, 'experiment', experiment)
    # ---------------------------------------------------------



    # ------------------------------------------------------------------------
    def add_field(self):

        # Get current experiment
        current_table = self.tabs.currentWidget()
        if not current_table:
            QMessageBox.warning(self, "Error", "Create an experiment first.")
            return

        current_index = self.tabs.currentIndex()
        experiment = self.spreadsheet.experiments[current_index]


        # Call the dialog window
        dialog = AddFieldDialog()


        # If user pressed "OK"
        if dialog.exec_() == QDialog.Accepted:

            # Extract data
            field_type, label, unit, error, formula, value = dialog.get_data()
            field = Field(label=label,
                          unit=unit,
                          field_type=field_type,
                          error=error,
                          formula=formula,
                          value=value)

            # Add field to the experiment
            self.spreadsheet.add_field(experiment.id, field)

            # Write field data to the table
            if field_type == 'const':
                self.update_table(current_table, 'const', experiment)
            else:
                self.update_table(current_table, 'field', experiment)
    # ------------------------------------------------------------------------



    # -----------------------------------------------------------------------------------------------
    def update_table(self, table, what, experiment):

        match what:
            case 'experiment':
                # Calculate total columns 
                const_amount = len(experiment.constants)
                num_fields = len(experiment.fields)
                total_rows = max(const_amount, experiment.amount)
                total_cols = 1  # Constants column

                for field in experiment.fields:
                    if field.field_type == 'gathered':
                        total_cols += 2
                    else:
                        total_cols += 1


                # Update row and column amount
                table.setRowCount(total_rows)
                table.setColumnCount(total_cols)


                # Label "Constants" column
                table.setHorizontalHeaderItem(0, QTableWidgetItem(f"constants"))


                # Update constants
                for i, const in enumerate(experiment.constants):
                    item = QTableWidgetItem(f"{const.label} = {const.value} {const.unit}")
                    table.setItem(i, 0, item)


                # Write data fields
                col = 1
                for field in experiment.fields:

                    if field.field_type == 'gathered':

                        # Add "{label} ({unit})" and "{label} error" columns
                        table.setHorizontalHeaderItem(col, QTableWidgetItem(f"{field.label} ({field.unit})"))
                        table.setHorizontalHeaderItem(col+1, QTableWidgetItem(f"{field.label} error"))

                        # Make editable cells
                        for row in range(total_rows):
                            value_edit = QLineEdit()
                            table.setCellWidget(row, col, value_edit)
                            error_edit = QLineEdit()
                            table.setCellWidget(row, col+1, error_edit)

                        # We took two columns
                        col += 2


                    elif field.field_type == 'calculated':

                        # Add "{label} ({unit})" column 
                        table.setHorizontalHeaderItem(col, QTableWidgetItem(f"{field.label} ({field.unit})"))

                        # Make non-editable cells (TODO: add formulas)
                        for row in range(const_amount, total_rows):
                            item = QTableWidgetItem()
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            table.setItem(row, col, item)

                        # We took one column
                        col += 1


            case 'field':
                total_rows = experiment.amount
                total_cols = 1  # Constants column

                for field in experiment.fields[:-1]:
                    if field.field_type == 'gathered':
                        total_cols += 2
                    else:
                        total_cols += 1

                col = total_cols
                
                new_field = experiment.fields[-1]

                match new_field.field_type:
                    case 'gathered':
                        # Update cloumn count
                        table.setColumnCount(total_cols + 2)

                        # Add "{label} ({unit})" and "{label} error" columns
                        table.setHorizontalHeaderItem(col, QTableWidgetItem(f"{new_field.label} ({new_field.unit})"))
                        table.setHorizontalHeaderItem(col+1, QTableWidgetItem(f"{new_field.label} error"))

                        # Make editable cells
                        for row in range(total_rows):
                            value_edit = QLineEdit()
                            table.setCellWidget(row, col, value_edit)
                            error_edit = QLineEdit()
                            table.setCellWidget(row, col+1, error_edit)

                    case 'calculated':
                        # Update cloumn count
                        table.setColumnCount(total_cols + 1)

                        # Add "{label} ({unit})" column 
                        table.setHorizontalHeaderItem(col, QTableWidgetItem(f"{new_field.label} ({new_field.unit})"))

                        # Make non-editable cells (TODO: add formulas)
                        for row in range(total_rows):
                            item = QTableWidgetItem()
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            table.setItem(row, col, item)

            case 'const':
                # Update row count
                table.setRowCount(max(experiment.amount, len(experiment.constants)))

                # Update constants
                for i, const in enumerate(experiment.constants):
                    item = QTableWidgetItem(f"{const.label} = {const.value} {const.unit}")
                    table.setItem(i, 0, item)



    # -----------------------------------------------------------------------------------------------


