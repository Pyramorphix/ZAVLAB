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
ZAVLAB provides tools for generating spreadsheets, calculating errors, and plotting graphs. You can get all the documentation from [wiki](https://github.com/Pyramorphix/ZAVLAB/wiki).

Below are some examples of how to use the library.

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


### Error Calculation and data approximation
Coming soon...

### Graph plotting
ZAVLAB also can help you with making plots. Here is an example how to make few plots in one place. (for detailed comments see [basic_principles](examples/basic_principles.py), [importing_configs](examples/importing_configs.py) or [all_in](examples/all_in.py)): (here is basic_principles):
```python
import numpy as np
from ZAVLAB.graph_plotting import Earl

# Create an instance of Earl
graph = Earl()

# Define data
data_array = [
    [[np.linspace(1, 10, 10)], [np.linspace(10, 100, 10)]],  # 2D dataset - number 0
    [[np.linspace(1, 10, 10), np.linspace(1, 10, 10) * 0.05], [np.linspace(20, 103, 10), np.linspace(20, 103, 10) * 0.01]],  # 2D dataset with errors - number 1
    [np.linspace(-10, 10, 100), np.linspace(-10, 10, 100), np.random.rand(100, 100)],  # 3D dataset - number 2
    [[np.linspace(1, 10, 10)], [np.linspace(-5, 10, 10)]],  # 2D dataset - number 3
]

# Plot the data
graph.plot_graph(
    data_array=data_array,
    subplots_distribution=[0, 0, 1, 1], # <= Here we explain to function which how to place data in subplots:
    #subplots number 0 and 1 will be placed in the first subplot (index 0), subplots 2 and 3 will be placed in the second subplot (index 1)
    ls=["-", ":", "", "--"],
    labels=["First 2D Line", "Second 2D Line", "3D Surface", "2D Line on 3D Surface"],
    rows_cols=[1, 2],
    figure_size=[12, 6],
    graph_types=["2D", "2D", "3D", "2D"],
    colormap=[[1, "YlGn"]],
    axes_titles=[["X-axis", "Y-axis"], ["X", "Y", "Colorbar"]],
    axes_scaling = [[1, "divide", [[-10, 10, 11], [-10, 10, 11]]]],
    marker_size = [10, 10, 10, 10],
    color=["#FF5733", "#2ECC71", "#000000", "#FF5733",]
)

# Add a line and annotation
graph.draw_lines(
    start_point=[1, 10],
    end_point=[5, 50],
    text="Example Line",
    subplot_pos_line=0,
)

# Display the plot
graph.show_plot()

# Save the plot and configuration
graph.save_plot(name="custom_plot.svg")
graph.save_config(name="custom_config.json")
graph.save_config_for_lines(name="custom_config_for_lines.json")
```


## Contributing
Contributions are welcome! If you’d like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push your branch and submit a pull request.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Contact
Feel free to contact us by email:
zavlab.dev@yandex.ru


## Acknowledgements

We highly thank Maksim Paukov for consulting us on scientific subjects.
