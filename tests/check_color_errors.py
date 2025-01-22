import sys
sys.path.insert(1, './../src')
from graph_plotting import Earl

example_graph = Earl()

#color parameter
example_graph.check_parameters(color='#123456')
example_graph.check_parameters(color='123456')
example_graph.check_parameters(color='#12345')
example_graph.check_parameters(color=["#123456", "#123456"])
example_graph.check_parameters(color=["#123456", "123456"])
example_graph.check_parameters(color=["123456", "#123456"])
example_graph.check_parameters(color=["#123456", "12345"])
example_graph.check_parameters(color=["12345", "#123456"])
example_graph.check_parameters(color=["#123456", "#12345"])
example_graph.check_parameters(color=["#12345", "#123456"])
example_graph.check_parameters(color=["#123456", "sdfghjg"])
example_graph.check_parameters(color=["sdfghjg", "#123456"])
example_graph.check_parameters(color=12)
