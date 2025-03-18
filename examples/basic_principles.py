import numpy as np
from ZAVLAB.graph_plotting import Earl

# Create an instance of Earl
graph = Earl()

# Define data
data_array = [
    [[np.linspace(1, 10, 10)], [np.linspace(10, 100, 10)]],  # 2D dataset - number 0
    [[np.linspace(1, 10, 10), np.linspace(1, 10, 10) * 0.05], [np.linspace(20, 103, 10), np.linspace(20, 103, 10) * 0.01]],  # 2D dataset with errors - number 1
    [np.linspace(-10, 10, 100), np.linspace(-10, 10, 100), np.random.rand(100, 100)],  # 3D dataset - number 2
    [[np.linspace(1, 10, 10)], [np.linspace(-5, 10, 10)]],  # 2D dataset - number 3
]

# Plot the data
graph.plot_graph(
    data_array=data_array,
    subplots_distribution=[0, 0, 1, 1], # <= Here we explain to function which how to place data in subplots:
    #subplots number 0 and 1 will be placed in the first subplot (index 0), subplots 2 and 3 will be placed in the second subplot (index 1)
    line_style=["-", ":", "", "--"],
    label=["First 2D Line", "Second 2D Line", "3D Surface", "2D Line on 3D Surface"],
    rows_cols=[1, 2],
    fig_size=[12, 6],
    data_type=["2D", "2D", "3D", "2D"],
    colormap=[[1, "YlGn"]],
    axes_title=[["X-axis", "Y-axis"], ["X", "Y", "Colorbar"]],
    axes_scaling = [[1, "divide", [[-10, 10, 11], [-10, 10, 11]]]],
    marker_size = [10, 10, 10, 10],
    color=["#FF5733", "#2ECC71", "#000000", "#FF5733",]
)

# Add a line and annotation
graph.draw_lines(
    start_point=[1, 10],
    end_point=[5, 50],
    text="Example Line",
    subplot_line=0,
)

# Display the plot
graph.show_plot()

# Save the plot and configuration
graph.save_plot(name="custom_plot.svg")
graph.save_config(name="custom_config.json")
graph.save_config_for_lines(name="custom_config_for_lines.json")