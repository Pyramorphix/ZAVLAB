import sys
sys.path.insert(1, './../src')
from graph_plotting import Earl

example_graph = Earl()

#ls parameter
possible_ls = ["-", "--", "-.", ":", ""]
for i in possible_ls:
    print('-----')
    print(i)
    example_graph.check_parameters(ls=i)
    example_graph.check_parameters(ls=[i, i])
    example_graph.check_parameters(ls=[i, 'asdl'])
    example_graph.check_parameters(ls=['fghj', i])
    example_graph.check_parameters(ls=1)
    example_graph.check_parameters(ls=[i, 1])
    example_graph.check_parameters(ls=[1, i])
    print('-----')
# print("Curves structures:")
# for i in range(example_graph.quant):
#     example_graph.print_curve_settings(i)
# print('--------')
# print("Subplots structure:")
# for i in range(example_graph.number_of_subplots):
#     example_graph.print_subplot_settings(i)
# print('--------')