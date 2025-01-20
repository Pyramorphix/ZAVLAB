from graph_plotting import Earl

example_graph = Earl(color=['#B03A2E'], ls='-', marker_shape=['o', '^'], axes_font_size=10, line_width=[1, 0.5], line_alpha=1, colros=['l'])
print("Curves structures:")
for i in range(example_graph.quant):
    example_graph.print_curve_settings(i)
print('--------')
print("Subplots structure:")
for i in range(example_graph.number_of_subplots):
    example_graph.print_subplot_settings(i)
print('--------')