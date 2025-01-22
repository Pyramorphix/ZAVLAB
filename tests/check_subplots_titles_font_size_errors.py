import sys
sys.path.insert(1, './../src')
from graph_plotting import Earl

example_graph = Earl()

#subplots_titles_font_size parameter
#Это было написано под серию смешариков "Вид сверху. Часть 2"
print('-----')
example_graph.check_parameters(subplots_titles_font_size=1)
example_graph.check_parameters(subplots_titles_font_size=[1, 2])
example_graph.check_parameters(subplots_titles_font_size=-1)
example_graph.check_parameters(subplots_titles_font_size=[1, -1])
example_graph.check_parameters(subplots_titles_font_size=[-1, 1])
example_graph.check_parameters(subplots_titles_font_size=0)
example_graph.check_parameters(subplots_titles_font_size=[1, 0])
example_graph.check_parameters(subplots_titles_font_size=[0, 1])
example_graph.check_parameters(subplots_titles_font_size=[[1, [2, 3.3]]])
print('-----')
