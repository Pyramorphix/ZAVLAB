
import sys
import os
neighbor_dir = os.path.join(os.path.dirname(__file__), '../')
sys.path.insert(0, neighbor_dir)
from ZAVLAB.graph_plotting import Earl
import numpy as np

data_array = [0, 0, 0, 0, 0, 0, 0, 0]
labels = ['', '', '', '']
x = np.logspace(0, 6, 10)
y = x * 10
xerr = x * 0.1
yerr = y * 0.5
data_array[0] = [[x, xerr], [y, yerr]]
labels[0] = "xerr, yerr"
data_array[1] = [[x * 1e-2, xerr * 1e-2], [y * 1e2]]
labels[1] = "only xerr"
data_array[2] = [[x * 1e-3], [y * 10**1.5, yerr * 10**1.5]]
labels[2] = "only yerr"
data_array[3] = [[x * 1e2], [y]]
labels[3] = "no errors"

a = lambda x, y: x**2 + y ** 2
x = np.linspace(-10, 10, 101)
y = np.linspace(-10, 10, 101)
z = np.array(
        [[a(x, y) for y in np.linspace(-10, 10, 101)] for x in np.linspace(-10, 10, 101)]
    )
data_array[4] = [x, y, z]
labels.append('')


def approximation(x, Q, omega_0, delta, tau):
    return Q *(np.sin(delta) - (tau * omega_0) * (x - 1) * np.cos(delta)) / (x * (1 + (tau * omega_0 * (x - 1)) ** 2))

x = np.linspace(0.89, 1.11, 23)
y = approximation(x, 24.5, 31.3, 1.5,0.5)
xerr = x * 0.001
yerr = np.abs(y) * 0.01
data_array[5] = [[x, xerr], [y, yerr]]
labels.append("data")
x = np.linspace(0.89, 1.11, 1000)
y = approximation(x, 24.5, 31.3, 1.5,0.5)
data_array[6] = [[x], [y]]
labels.append("approxim")

x = np.linspace(-9, 9, 1000)
y = np.arctan(x)
data_array[7] = [[x], [y]]
labels.append(r"$y=arctan(x)$")

k = 1 / (1 + 2**2)
b = 1.1 - 2 * k

example_graph = Earl(verbose=False)

example_graph.plot_graph(data_array=data_array, rows_cols=[2, 2],labels=labels, subplots_distribution=[0, 0, 0, 0, 1, 2, 2, 3],
                         ls=['-'] * 5 + [''] + ['-'] * 2, logarithmic_scaling=[[0, [1, 1]]], line_width=[1] * 4, marker_size=3, marker_shape=["P"] * 6 + [""] * 2, axes_titles=[["some X title", "some Y title"], ["x", "y", "some cbar title"], [r"$\nu$, Гц", "U, Вт"]], axes_round_accuracy=[[0, ["%0.0f", "%0.0f"]], [1, ["%0.0f", "%0.0f"]], [2, ["%0.2f", "%0.0f"]], [3, ["%0.0f", "%0.2f"]]],
                         colormap=[[1, "Spectral"]], axes_scaling=[[1, "divide", [[-10, 10, 11], [-10, 10, 11]]], [2, "divide", [[0.88, 1.12, 4], [3, 27, 4]]], [3, "divide", [[-10, 10, 11],[-np.pi / 2 - 0.1, np.pi / 2 + 0.1, 11]]]], graph_types=["2D"] * 4 + ["3D"] + ["2D"] * 2)
example_graph.draw_lines(start_point=[[1, 3], [0.88, 24.58], [-10, k * -10 + b]], end_point=[[1, 24.58], [1, 24.58], [2, 1.1]], text=[r"$\nu=31.3$Гц", "Q=24.5", "касательная к точке 2"], subplot_pos_line=[2, 2, 3], text_pos=[[False, False], [0.9, 25], [-6, -0.33]], text_rotation=[0, 0, 47])
example_graph.show_plot()
example_graph.save_plot(name="../examples/example.png")
example_graph.save_config(name="../examples/new_config.json")
example_graph.save_config_for_lines(name="../examples/new_config_for_lines.json")
example_graph.change_config_file(file_path_name_to_conf="../examples/new_config.json")
example_graph.plot_graph(data_array=data_array)
example_graph.show_plot()
