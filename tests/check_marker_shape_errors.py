import sys
sys.path.insert(1, './../src')
from graph_plotting import Earl

example_graph = Earl()

#marker_shape parameter
possible_marker_shape = [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4",
    "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", 
    "d", "|", "_", ""]
for i in possible_marker_shape:
    print('-----')
    print(i)
    example_graph.check_parameters(marker_shape=i)
    example_graph.check_parameters(marker_shape=[i, i])
    example_graph.check_parameters(marker_shape=[i, 'asdl'])
    example_graph.check_parameters(marker_shape=['fghj', i])
    example_graph.check_parameters(marker_shape=1)
    example_graph.check_parameters(marker_shape=[i, 1])
    example_graph.check_parameters(marker_shape=[1, i])
    print('-----')
# print("Curves structures:")
# for i in range(example_graph.quant):
#     example_graph.print_curve_settings(i)
# print('--------')
# print("Subplots structure:")
# for i in range(example_graph.number_of_subplots):
#     example_graph.print_subplot_settings(i)
# print('--------')