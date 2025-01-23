from graph_plotting import Earl
import matplotlib.pyplot as plt
import numpy as np
example_graph = Earl()
# print('--------')
# print(example_graph.print_config())
# print("Curves structures:")
# for i in range(example_graph.quant):
#     example_graph.print_curve_settings(i)
# print('--------')
# print("Subplots structure:")
# for i in range(example_graph.number_of_subplots):
#     example_graph.print_subplot_settings(i)
# print('--------')
data_array = []
label = 0
labels = []
for i in range(4):
    data_array.append([])
    x = np.linspace(1, 11, 11)
    xerr = x * 0.1
    y = x ** 2
    yerr = y * 0.1
    data_array[-1] = [
        [x, xerr],
        [y, yerr],
    ]
    data_array.append([])
    data_array[-1] = [
        [x, xerr],
        [y]
    ]
    data_array.append([])
    data_array[-1] = [
        [x],
        [y, yerr],
    ]
    data_array.append([])
    data_array[-1] = [
        [x],
        [y],
    ]
    for j in range(4):
        labels.append(str(label))
        label += 1
print(data_array)
example_graph.plot_graph(data_array, color=['#B03A2E'], ls='-', marker_shape=['o', '^'],
                          axes_font_size=[[0, [16, 16]]], subplots_titles_font_size=[[1, 20]], axes_number_of_small_ticks=[[2, [1, 1]]], axes_round_accuracy=[[3, ["%0.0f", "%0.1f"]]], 
                          logarithmic_scaling=[[0, [1, 0]], [1, [0, 1]]], axes_scaling=[[2, "divide", [[1, 11, 11], [1, 140, 8]]]],
                          line_width=[1, 0.5], line_alpha=1, colros=['l'],  subplots_settings = [
        {
        "rows_cols": [2, 2],
        "subplots_distribution": [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
        }
    ])
# print('--------')
# print(example_graph.print_config())
# print("Curves structures:")
# for i in range(example_graph.quant):
#     example_graph.print_curve_settings(i)
# print('--------')
# print("Subplots structure:")
# for i in range(example_graph.number_of_subplots):
#     example_graph.print_subplot_settings(i)
# print('--------')
#example_graph.save_plot()
example_graph.plt.show()