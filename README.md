# ZAVLAB
Zingy Arina and Vladislav's Laboratory Assistant Bot

## About
ZAVLAB is a Python-based project designed for automatic experimental data processing. It provides tools for generating spreadsheets, calculating errors, and plotting graphs for laboratory data collection and analysis.

## Installation
To install and set up ZAVLAB, follow these steps:

1. **Clone the repository**:
```shell
git clone https://github.com/Pyramorphix/ZAVLAB
```
2. **Navigate to cloned folder**:
```shell
cd ZAVLAB
```
3. **Initialize a virtual environment**:
```shell
python -m venv venv
```
4. **Activate the virtual environment**:
- on Windows
```shell
venv\Scripts\activate
```
- on Linux/MacOS
```shell
source venv/bin/activate
```
5. **Install the required dependencies**:
```shell
pip install -r requirements.txt
```
6. **Install the ZAVLAB package locally** (we plan to port it as a global package in the future):
```shell
pip install -e .
```

## Usage
ZAVLAB provides tools for generating spreadsheets, calculating errors, and plotting graphs. Below are examples of how to use the library.

### Spreadsheet Generation
ZAVLAB can create spreadsheets for laboratory data collection. Here’s an example of how to generate a spreadsheet (for detailed comments see [example](examples/spreadsheet_generation.py)):
```python
from pathlib import Path
from ZAVLAB.spreadsheet_generator import get_spreadsheet_generator

if __name__ == "__main__":

    # Get spreadsheet generator (defaults to XLSXGenerator)
    spreadsheet = get_spreadsheet_generator()

    # Add an experiment titled "Ohm's law" with 16 rows
    spreadsheet.add_experiment(title="Ohm's law", amount=16)

    # Add fields to the experiment
    spreadsheet.add_field(experiment=1, field_type="gathered", label="V", unit="mV", error="3% + 0.01")
    spreadsheet.add_field(experiment=1, field_type="gathered", label="I", unit="mA", error="lsd")
    spreadsheet.add_field(experiment=1, field_type="calculated", label="R_mes", unit="Ohm", formula="V / I")
    spreadsheet.add_field(experiment=1, field_type="const", label="Konst?", value="NO")
    spreadsheet.add_field(experiment=1, field_type="const", label="tau", value="6.28")
    spreadsheet.add_field(experiment=1, field_type="const", label="mass", unit="kg")

    # Add a second experiment titled "Kinetic energy" with 10 rows (default)
    spreadsheet.add_experiment(title="Kinetic energy")

    # Add fields to the second experiment
    spreadsheet.add_field(experiment="Kinetic energy", label="m", unit="kg", field_type="gathered", error="4 * lsd")
    spreadsheet.add_field(experiment="Kinetic energy", label="v", unit="m/s", field_type="gathered", error="2% + .05")
    spreadsheet.add_field(experiment="Kinetic energy", label="K", unit="J", field_type="calculated", formula="m*v^2/2")
    spreadsheet.add_field(experiment="Kinetic energy", label="g", unit="m/s^2", field_type="const", value="9.81", error=0.01)

    # Print the spreadsheet generator (has a nice __str__ representation)
    print(spreadsheet)

    # Set the output path to ../output/
    path = Path().parent.absolute() / "output"

    # Generate the spreadsheet at output/spreadsheet.xlsx
    spreadsheet.generate(f"{path}/spreadsheet")
```

### Error Calculation
Coming soon...

### Graph plotting
My part is done here. This is to be written by Arina

## Contributing
Contributions are welcome! If you’d like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push your branch and submit a pull request.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Contact

We're planning to create an e-mail for the project. For now, write to `Issues` section.


## Acknowledgements

We highly thank Maxim Paukov for consulting us on scientific subjects.
