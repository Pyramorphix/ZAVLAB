import openpyxl
from openpyxl.utils import get_column_letter
from pathlib import Path

MAX_ROW_COUNT = 100


"""
Here we make the basement for out spreadsheet. It's basically a list consisting of fields.

Each field is either for user input (type='gathered') or for calculated values (type='calculated').
Every field has the label and measure unit.

User input fields additionally have the 'error' element for entering the experimental error.
It can be either a certain value (e.g. '0.005') or a formula depending on measured value (e.g. '2% + 0.04')

Calculated values have the 'formula' element for the calculation formula.
It should be typed in using excel-readable format with field labels (e.g. 'm*v^2/2')
"""
# =====================================================================================================================

class Spreadsheet:

    # Making an empty list and initializing file type (e.g. 'xlsx' or 'ods') for further file assembling
    # ----------------------------------------
    def __init__(self, filetype: str) -> None:

        self.filetype: str = filetype
        self.fields: list = []
    # ----------------------------------------



    # Method to add specified field to the list
    # --------------------------------------------------------------------------------------------
    def add_field(self, label: str, unit: str, field_type: str, error=None, formula=None) -> None:

        id_: int = len(self.fields) + 1  # Auto-incrementing ID

        # Check if field type is correct
        if field_type not in {'gathered', 'calculated'}:
            raise ValueError(f"Field {id_}: invalid field type.\n" +
                             f"Expected: 'gathered' or 'calculated'\n" +
                             f"Got: '{field_type}'")

        field = {
            "id": id_,
            "label": label,
            "unit": unit,
            "type": field_type,
            "error": error,
            "formula": formula,
        }

        self.fields.append(field)
    # --------------------------------------------------------------------------------------------



    # Nice little string representation in case we ever want to print out our spreadsheet
    # --------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        
        string: str = f"{type(self)}\nFields:"
        
        for field in self.fields:
            string += f"\n{field['id']}. {field['label']}, {field['unit']} ({field['type']}); " + \
            f"{'error: ' + field['error'] if field['type'] == 'gathered' else 'formula: ' + field['formula']}"

        return string
    # --------------------------------------------------------------------------------------------------------



    # If someone decides to call .generate() method from Spreadsheet object instead of Generator,
    # we gently remind him of it instead of bashing him in the head with the hammer
    # --------------------------------------------------------------------------------------------
    def generate(self, output_file) -> None:

        raise NotImplementedError("This method should be implemented by a generator subclasses " +
        "(e.g. XLSXGenerator) and not the Spreadsheet class itself")
    # --------------------------------------------------------------------------------------------

# =====================================================================================================================





"""
Now, as we have the basement, we can make generators which assemble the spreadsheet file.
There are different python libraries for working with different file types,
therefore we need to make an individual generator for each type.
"""
# =====================================================================================================================

class XLSXGenerator(Spreadsheet):

    def generate(self, output_file) -> None:

        # Initializing the spreadsheet (workbook) and the sheet
        # ----------------------------
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        # ----------------------------



        # Generating and writing headers
        # ----------------------------------------------------------------------------------------------------------
        header_row: list = []

        # For matching excel column labels to field labels (e.g. m_1 -> A, v -> C etc.)
        # which will be needed to convert formulas into excel format
        column_labels: dict[str, str] = {}
        column: int = 1    # In openpyxl column numeration starts with 1
        

        for field in self.fields:
            
            # Add the column label (notice that we don't add err field labels 'cause we don't need them)
            column_labels[field['label']] = get_column_letter(column)

            match field['type']:

                # For user input fields we make two columns: value and error
                case "gathered":

                    header_row.append(f"{field['label']}, {field['unit']}")

                    header_row.append(f"{field['label']} err, {field['unit']}")

                    # Keeping the track of the column number
                    column += 2
        

                # For calculated fields we make only one column
                case "calculated":

                    header_row.append(f"{field['label']}, {field['unit']}")

                    # Keeping the track of the column number
                    column += 1


                # If field type is somtehing other, we return an error
                case _:

                    raise ValueError(f"Field {field['id']}: invalid field type.\n" +
                                     f"Expected: 'gathered' or 'calculated'\n" +
                                     f"Got: '{field['type']}'")
        
        sheet.append(header_row)
        # ----------------------------------------------------------------------------------------------------------



        # Writing rows:
        for row_number in range(2, MAX_ROW_COUNT + 2):
        
            data_row = []
            
            for field in self.fields:

                match field['type']:

                    case "gathered":

                        # Leave the column for the gathered data empty
                        data_row.append(None)

                        # Format error formula to a function of 'val'
                        # e.g. 5% + 0.001  ->  0.05 * val + 0.001
                        err_formula = format_error(field['error'])

                        # Replace 'val' with cell coordinates of gathered data
                        err_formula = err_formula.replace('val', column_labels[field['label']] + str(row_number))

                        # And, finally, write the formula to the cell
                        data_row.append(f"={err_formula}")
                    

                    case "calculated":

                        formula = field["formula"]

                        # Change all labels in the formula to the coordinates of corresponding values
                        for label, col_number in column_labels.items():
                            formula = formula.replace(label, f"{col_number}{row_number}")

                        # Write the formula to the cell
                        data_row.append(f"={formula}")
            

                    # If field type is somtehing other, we return an error
                    case _:

                        raise ValueError(f"Field {field['id']}: invalid field type.\n" +
                                         f"Expected: 'gathered' or 'calculated'\n" +
                                         f"Got: '{field['type']}'")
        
            sheet.append(data_row)


        # Saving the spreadsheet
        # ------------------------
        workbook.save(output_file)
        # ------------------------



# Error formula formatting. The output is excel-style formula of 'val'
# ---------------------------------------
def format_error(expr: str) -> str:

    # Formatting percentages
    expr = expr.replace('%', '*0.01*val')

    # TODO: Add lsd formatting

    return expr
# ---------------------------------------

# =====================================================================================================================





# Function to choose the appropriate generator based on chosen filetype
# (Currently supported: .xlsx)
# ----------------------------------------------------------------------------
def get_spreadsheet_generator(filetype: str) -> XLSXGenerator:

    match filetype:

        case "xlsx":
            return XLSXGenerator(filetype)
    
        # TODO: maybe add .ods support

        case _:
            raise ValueError(f"Unsupported spreadsheet file type: {filetype}")
# ----------------------------------------------------------------------------





# Example Usage
# ---------------------------------------------------------------------
filetype = "xlsx"
spreadsheet = get_spreadsheet_generator(filetype)

# Add fields
spreadsheet.add_field("m", "kg", "gathered", error="0.001")
spreadsheet.add_field("v", "m/s", "gathered", error="2% + .05")
spreadsheet.add_field("K", "J", "calculated", formula="m*v^2/2")

print(spreadsheet)

# Setting path to ../output/
path = Path().parent.absolute() / "output"


spreadsheet.generate(f"{path}/spreadsheet.{filetype}")
# ---------------------------------------------------------------------
