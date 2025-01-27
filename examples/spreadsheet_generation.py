from pathlib import Path
from ZAVLAB.spreadsheet_generator import get_spreadsheet_generator

if __name__ == "__main__":

    filetype = "xlsx"
    spreadsheet = get_spreadsheet_generator(filetype)

    # Add experiment with fields
    spreadsheet.add_experiment(
        title="Ohm's law",
        fields=[
            {'type': "gathered",   'label': "V",     'unit': "mV",  'error': "3% + 0.01"},
            {'type': "gathered",   'label': "I",     'unit': "mA",  'error': "0.1"},
            {'type': "calculated", 'label': "R_mes", 'unit': "Ohm", 'formula': "V / I"},
            {'type': "calculated", 'label': "R_act", 'unit': "Ohm", 'formula': "20"},
            {'type': "const", 'label': "Konst", 'value': "NO"},  # НЕ БРАТЬ КОНСТА!
            {'type': "const", 'label': "tau", 'value': "6.28"},
            {'type': "const", 'label': "mass", 'unit': "kg", 'value': "200"},
            {'type': "calculated", 'label': "test", 'formula': "tau * mass"},
            {'type': "calculated", 'label': "Брать конста?", 'formula': "Konst"}
        ],

    )

    # Add experiment and then fields
    spreadsheet.add_experiment(title="Kinetic energy")

    spreadsheet.add_field(experiment="Kinetic energy", label="m", unit="kg", field_type="gathered", error="0.04 * lsd")
    spreadsheet.add_field(experiment="Kinetic energy", label="v", unit="m/s", field_type="gathered", error="2% + .05")
    spreadsheet.add_field(experiment="Kinetic energy", label="K", unit="J", field_type="calculated", formula="m*v^2/2")
    spreadsheet.add_field(experiment="Kinetic energy", label="g", unit="m/s^2", field_type="const", value="9.81")

    print(spreadsheet)

    # Setting path to ../output/
    path = Path().parent.absolute() / "output"


    spreadsheet.generate(f"{path}/spreadsheet")
