from pathlib import Path
from ZAVLAB.spreadsheet_generator import get_spreadsheet_generator

if __name__ == "__main__":

    spreadsheet = get_spreadsheet_generator()


    spreadsheet.add_experiment(title="Ohm's law")

    spreadsheet.add_field(experiment=1, field_type="gathered",   label="V",     unit="mV",  error="3% + 0.01")
    spreadsheet.add_field(experiment=1, field_type="gathered",   label="I",     unit="mA",  error="lsd")
    spreadsheet.add_field(experiment=1, field_type="calculated", label="R_mes", unit="Ohm", formula="V / I")
    spreadsheet.add_field(experiment=1, field_type="calculated", label="R_act", unit="Ohm", formula="20")
    spreadsheet.add_field(experiment=1, field_type="const", label="Konst", value="NO")  # НЕ БРАТЬ КОНСТА!
    spreadsheet.add_field(experiment=1, field_type="const", label="tau", value="6.28")
    spreadsheet.add_field(experiment=1, field_type="const", label="mass", unit="kg", value=200)
    spreadsheet.add_field(experiment=1, field_type="calculated", label="test", formula="tau * mass")
    spreadsheet.add_field(experiment=1, field_type="calculated", label="Брать конста?", formula="Konst")


    spreadsheet.add_experiment(title="Kinetic energy")

    spreadsheet.add_field(experiment="Kinetic energy", label="m", unit="kg", field_type="gathered", error="0.04 * lsd")
    spreadsheet.add_field(experiment="Kinetic energy", label="v", unit="m/s", field_type="gathered", error="2% + .05")
    spreadsheet.add_field(experiment="Kinetic energy", label="K", unit="J", field_type="calculated", formula="m*v^2/2")
    spreadsheet.add_field(experiment="Kinetic energy", label="g", unit="m/s^2", field_type="const", value="9.81")

    print(spreadsheet)

    # Setting path to ../output/
    path = Path().parent.absolute() / "output"


    spreadsheet.generate(f"{path}/spreadsheet")
