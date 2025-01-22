import sys
sys.path.insert(1, './../src')
from graph_plotting import Earl

example_graph = Earl()

#axes_font_size parameter
#Это было написано под серию смешариков "Вид сверху. Часть 2"
print('-----')
example_graph.check_parameters(axes_font_size=1)
example_graph.check_parameters(axes_font_size=[[1, [2, 3]]])
example_graph.check_parameters(axes_font_size=[1, [2, 3]])
example_graph.check_parameters(axes_font_size=['ad'])
example_graph.check_parameters(axes_font_size=[['ad', [2, 3]]])
example_graph.check_parameters(axes_font_size=[[1, 'aad']])
example_graph.check_parameters(axes_font_size=[[1, [2, 3, 3]]])
example_graph.check_parameters(axes_font_size=[[1, [1.2, 3]]])
example_graph.check_parameters(axes_font_size=[[1, [2, 3.3]]])
print('-----')
