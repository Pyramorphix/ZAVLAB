import numpy as np
from ZAVLAB.graph_plotting import Earl

# Create an instance of Earl
graph = Earl(file_path_name_to_conf="custom_config.json", file_path_name_to_line_conf="custom_config_for_lines.json", verbose=True)
# or you can write:
'''
graph = Earl()
...some lines...
graph.change_config_file(file_path_name_to_conf="custom_config.json")
graph.change_config_for_lines_file(name_of_config_file="custom_config_for_lines.json")
'''
#or you can write:
'''
graph = Earl(file_path_name_to_conf="custom_config.json")
...some lines...
graph.draw_lines(file_path_name_to_line_conf="custom_config_for_lines.json")

'''

# Define data
data_array = [
    [[np.linspace(1, 10, 10)], [np.linspace(10, 100, 10)]],  # 2D dataset - number 0
    [[np.linspace(1, 10, 10), np.linspace(1, 10, 10) * 0.05], [np.linspace(20, 103, 10), np.linspace(20, 103, 10) * 0.01]],  # 2D dataset with errors - number 1
    [np.linspace(-10, 10, 100), np.linspace(-10, 10, 100), np.random.rand(100, 100)],  # 3D dataset - number 2
    [[np.linspace(1, 10, 10)], [np.linspace(-5, 10, 10)]],  # 2D dataset - number 3
]

#plottinf data and lines
graph.change_config_file(file_path_name_to_conf="custom_config.json")
graph.change_config_for_lines_file(name_of_config_file="custom_config_for_lines.json")
graph.plot_graph(data_array=data_array)
graph.draw_lines()
graph.show_plot()