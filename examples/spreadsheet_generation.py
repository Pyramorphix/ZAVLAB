from pathlib import Path
from ZAVLAB.spreadsheet_generator import get_spreadsheet_generator

if __name__ == "__main__":

	# Get spreadsheet generator.
	# We haven't specified file extension, so by default it will be XLSXGenerator
    spreadsheet = get_spreadsheet_generator()


	# Add empty experiment with title "Ohm's law" and 16 rows.
	# It's the first experiment in the spreadsheet, so its id will be set to 1
    spreadsheet.add_experiment(title="Ohm's law", amount=16)


	# Add fields to the experiment. We pass
	# experiment=1 which will be treated as the id

	# Good!
	# Field "V, mV" for voltage measurement.
	# The error is 0.01 mV + 0.03 * value
    spreadsheet.add_field(experiment=1, field_type="gathered",   label="V",     unit="mV",  error="3% + 0.01")
    
    # Good!
    # Field "I, mA" for current measurement.
	# The error is last significant digit of the first value
    spreadsheet.add_field(experiment=1, field_type="gathered",   label="I",     unit="mA",  error="lsd")

	# Good!
    # Field "R, Ohm" for resistance calculating.
	# The formula is V / I
    spreadsheet.add_field(experiment=1, field_type="calculated", label="R_mes", unit="Ohm", formula="V / I")
    
    # Bad!
    # Field "R_act, Ohm" for actual resistance (20 Ohm).
	# Use "const" field instead for this purpose
    spreadsheet.add_field(experiment=1, field_type="calculated", label="R_act", unit="Ohm", formula="20")

	# Okay!
    # Field "Konst?" with text value.
	# Will work fine, but can cause problems if you'll try passing it to a formula like "Konst? / 2"
    spreadsheet.add_field(experiment=1, field_type="const", label="Konst?", value="NO")  # НЕ БРАТЬ КОНСТА!

	# Good!
    # Constant tau = 2 * pi.
	# Can be used for calculations
    spreadsheet.add_field(experiment=1, field_type="const", label="tau", value="6.28")

	# Good!
    # Mass of experimental body.
	# Value is not specified, so the cell will be empty
    spreadsheet.add_field(experiment=1, field_type="const", label="mass", unit="kg")

    # An example showing we can pass constants to formulas
    spreadsheet.add_field(experiment=1, field_type="calculated", label="test", formula="tau * mass")

	# We can also pass text fields to formulas,
	# but this is kinda useless and can cause some errors
    spreadsheet.add_field(experiment=1, field_type="calculated", label="Брать Конста?", formula="Konst?")


	# Add empty experiment with title "Kinetic energy" with 10 rows (default).
	# It's the second experiment in the spreadsheet, so its id will be set to 2
    spreadsheet.add_experiment(title="Kinetic energy")
    

	# Add fields to the experiment. We pass experiment="Kinetic energy"
	# which will be treated as the label.
	# We can just as well pass experiment=2

	# Good!
    # Field "m, kg" for object mass.
	# The error is 4 * least significant digit of the first value
    spreadsheet.add_field(experiment="Kinetic energy", label="m", unit="kg", field_type="gathered", error="4 * lsd")

	# Good!
    # Field "v, m/s" for object speed.
	# The error is 0.05 m/s + 0.02 * value
    spreadsheet.add_field(experiment="Kinetic energy", label="v", unit="m/s", field_type="gathered", error="2% + .05")

	# Okay!
    # Gathered field with no error.
	# We set error=0, so no error column will be generated for this.
    spreadsheet.add_field(experiment="Kinetic energy", label="no_err", field_type="gathered", error=0)

	# Good!
    # Field "K, J" for kinetic energy calculating.
	# The formula is m * v^2 / 2
    spreadsheet.add_field(experiment="Kinetic energy", label="K", unit="J", field_type="calculated", formula="m*v^2/2")

	# Good!
    # Constant field "g, m/s^2" for gravitational acceleration.
    # Has error of 0.01 m/s^2
    spreadsheet.add_field(experiment="Kinetic energy", label="g", unit="m/s^2", field_type="const", value="9.81", error=0.01)


	# Printing the spreadsheet generator
	# (It has nice __str__ representation)
    print(spreadsheet)

    # Setting path to ../output/
    path = Path().parent.absolute() / "output"

	# Generating output/spreadsheet.xlsx
    spreadsheet.generate(f"{path}/spreadsheet")

