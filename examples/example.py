import numpy as np
from ZAVLAB.graph_plotting import Earl

# Create an instance of Earl
graph = Earl()

# Define data
data_array = [
    [[np.linspace(1, 10, 10)], [np.linspace(10, 100, 10)]],  # 2D dataset
    [np.linspace(-10, 10, 100), np.linspace(-10, 10, 100), np.random.rand(100, 100)],  # 3D dataset
]

# Plot the data
graph.plot_graph(
    data_array=data_array,
    ls=["-", ""],
    labels=["2D Line", "3D Surface"],
    rows_cols=[1, 2],
    figure_size=[12, 6],
    graph_types=["2D", "3D"],
    colormap=[[1, "Spectral"]],
    axes_titles=[["X-axis", "Y-axis"], ["X", "Y", "Colorbar"]],
)

# Add a line and annotation
graph.draw_lines(
    start_point=[1, 10],
    end_point=[5, 50],
    text="Example Line",
    subplot_pos_line=0,
)

# Display the plot
graph.show_plot()

# Save the plot and configuration
graph.save_plot(name="custom_plot.png")
graph.save_config(name="custom_config.json")