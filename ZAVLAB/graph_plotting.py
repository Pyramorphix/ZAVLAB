import json as js
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as ticker
from matplotlib.colors import Colormap
from pathlib import Path

"""
This part was made by Arina.
In this file, all "inspiration" comments are just my attempt to make this work a little more lively!
I tried to take into account all the possibilities of breaking class Earl.
If you do it, then your stupidity level is genious.
Also in this case DON'T bother yourself to email us to report an issue. 
Now, let's go!
"""
'''
And don't forget:
"To make something special you just have to believe that it is special." from Kung Fu panda.
'''

class Earl:
    """
    A class to manage and plot data using matplotlib, based on configuration settings from a JSON file.

    Attributes:
    ----------
    file_path_name_to_conf : str
        The file path to the configuration file containing plot settings.
    config : dict
        A dictionary containing the configuration settings loaded from the JSON file.
    plt : module
        The matplotlib.pyplot module for plotting.
    fig : Figure
        The matplotlib Figure object representing the entire plot.
    ax : list of list of Axes
        A 2D list of matplotlib Axes objects representing the subplots.
    quant : int
        A counter or quantity tracker (default is 0).
    number_of_subplots : int
        The total number of subplots (default is 0).
    curves_settings : list
        A list to store settings for curves (default is an empty list).
    subplots_settings : list
        A list to store settings for subplots (default is an empty list).
    verbose : bool
        A flag indicating whether to print verbose output (default is True).

    Methods:
    -------
    __init__(file_path_name_to_conf="./settings/config.json", verbose=True)
        Initializes the Earl class with the given configuration file and sets up the plot.
    save_plot(name="graph.png")
        Saves the current plot to a file with the specified name.

    Inspiration:
    ------------
    From various music tracks discovered via Spotify.
    """

    def __init__(self, file_path_name_to_conf=Path(__file__).parent.parent / "settings/config.json", file_path_name_to_line_conf=None, verbose=False):
        """
        Initializes the Earl class with the given configuration file and sets up the plot.

        This method reads the configuration file, sets up the plot with the specified number of subplots,
        and prepares the axes for plotting.

        Arguments:
        ----------
        file_path_name_to_conf : str, optional
            The file path to the configuration file containing plot settings (default is "../settings/config.json").
        file_path_name_to_line_conf : str, optional
            The file path to the line configuration file (default is None).
        verbose : bool, optional
            A flag indicating whether to print verbose output (default is True).

        Returns:
        -------
        None

        Raises:
        -------
        FileNotFoundError
            If the configuration file specified by `file_path_name_to_conf` does not exist.
        json.JSONDecodeError
            If the configuration file is not a valid JSON file.

        Notes:
        ------
        - The method reads the configuration file specified by `file_path_name_to_conf` and loads plot settings.
        - It also reads an optional line configuration file specified by `file_path_name_to_line_conf`.
        - The plot is set up with the number of subplots defined in the configuration.
        - If there's only one subplot, `self.ax` is adjusted to be a 2D array for consistent indexing.
        - The `__prepare_axes` method is called to further configure the plot axes.

        Example:
        --------
        ```python
        earl = Earl(file_path_name_to_conf="../settings/config.json", verbose=True)
        ```

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.file_path_name_to_conf = file_path_name_to_conf
        with open(self.file_path_name_to_conf, "r", encoding="utf-8") as file:
            self.config = js.load(file)
        self.file_path_name_to_conf_for_line = file_path_name_to_line_conf
        self.config_for_line = {}
        if not (self.file_path_name_to_conf_for_line is None):
            with open(self.file_path_name_to_conf_for_line, "r", encoding="utf-8") as file:
                self.config_for_line = js.load(file)
        self.plt = plt
        self.fig, self.ax = self.plt.subplots(nrows=self.config['subplots_settings'][0]['rows_cols'][0], ncols=self.config['subplots_settings'][0]['rows_cols'][1])
        self.__prepare_axes()
        
        self.quant = 0
        self.number_of_subplots = 0
        self.curves_settings = []
        self.subplots_settings = []
        self.verbose = verbose
        self.colorbars = []
        self.__labels_was_printed = False
        self.__config_files_changes = [False, False]

    def save_plot(self, name="graph.png"):
        """
        Saves the current plot to a file with the specified name.

        Arguments:
        ----------
        name : str, optional
            The name of the file to save the plot (default is "graph.png").

        Returns:
        -------
        None

        Raises:
        -------
        FileNotFoundError
            If the directory specified in the file name does not exist.

        Notes:
        ------
        - The method saves the current plot to a file with the specified name.
        - The file format is determined by the file extension in the `name` argument.

        Example:
        --------
        ```python
        earl.save_plot(name="my_plot.png")
        ```
        """

        self.fig.savefig(name)

    def __prepare_input(self, data_array=[[]], **kwargs):
        """
        Prepares the input data and configuration for plotting.

        This method sets the quantity of data points, checks the provided parameters,
        calculates the number of subplots, prepares the configuration, and constructs
        the structure for curves and subplots based on the input data.

        Arguments:
        ----------
        data_array : list of data, optional
            The input data array containing the data points to be plotted (default is an empty list of lists).
        **kwargs : dict
            Arbitrary keyword arguments representing additional configuration parameters.

        Returns:
        -------
        None

        Notes:
        ------
        - The method sets `self.quant` to the length of the input data array.
        - It calls `self.__check_parameters` to validate the provided keyword arguments.
        - It calculates the total number of subplots based on the configuration settings.
        - It calls `self.__prepare_config` to prepare the configuration for plotting.
        - It calls `self.__construct_structure_curve` to construct the structure for curves based on the input data.
        - It calls `self.__construct_structure_subplots` to construct the structure for subplots.

        Example:
        --------
        Assuming `data_array` is a valid array of data points and `kwargs` contains additional
        configuration parameters, calling:
        ```python
        earl.__prepare_input(data_array=[[1, 2, 3], [4, 5, 6]], line_color="red", line_ls="solid")
        ```
        will prepare the input data and configuration for plotting.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.quant = len(data_array)
        self.__check_parameters(**kwargs)
        self.number_of_subplots = self.config['subplots_settings'][0]['rows_cols'][0] * self.config['subplots_settings'][0]['rows_cols'][1]
        self.__prepare_config()
        self.__construct_structure_curve(data_array)
        self.__construct_structure_subplots()
    
    def plot_graph(self, data_array=[[]], **kwargs):
        """
        Plots the graph based on the input data and configuration parameters.

        This method prepares the input data and configuration, performs initial preparations for subplots,
        plots the data on the subplots, and configures the subplots after plotting the data.

        Arguments:
        ----------
        data_array : list of data, optional
            The input data array containing the data points to be plotted (default is an empty list of lists).
        **kwargs : dict
            Arbitrary keyword arguments representing additional configuration parameters.

        Returns:
        -------
        None

        Notes:
        ------
        - The method calls `self.__prepare_input` to prepare the input data and configuration.
        - It calls `self.__initial_preparation_for_subplots` to perform initial preparations for the subplots.
        - It calls `self.__plot_data_on_subplots` to plot the data on the subplots.
        - It calls `self.__config_subplots_after_plotting_data` to configure the subplots after plotting the data.

        Example:
        --------
        Assuming `data_array` is a valid array of data points and `kwargs` contains additional
        configuration parameters, calling:
        ```python
        earl.plot_graph(data_array=[[1, 2, 3], [4, 5, 6]], line_color="#101010", line_ls="-")
        ```
        will plot the graph based on the input data and configuration parameters.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.__prepare_input(data_array=data_array, **kwargs)
        self.__initial_preparation_for_subplots()
        self.__plot_data_on_subplots()
        self.__config_subplots_after_plotting_data()

    def __initial_preparation_for_subplots(self):
        """
        Performs initial preparations for the subplots based on the configuration settings.

        This method closes any existing plots, creates a new figure and subplots, sets titles and their sizes,
        configures legend properties, sets initial axes properties, and configures ticks and grid settings.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Raises:
        -------
        ValueError
            If there is an error in setting the logarithmic scaling for the axes.

        Notes:
        ------
        - The method closes any existing plots using `self.plt.close()`.
        - It creates a new figure and subplots with the specified number of rows and columns, and figure size.
        - It calls `self.__prepare_axes` to prepare the axes for plotting.
        - It iterates through each subplot to set titles, legend properties, initial axes properties,
          ticks properties, and grid settings.
        - It configures the axes scaling based on the settings in `self.subplots_settings`.
        - It sets the major and minor ticks properties, including their format and locators.
        - It configures the grid for both major and minor ticks.
        - It aligns the labels and titles and applies a tight layout to the figure.

        Example:
        --------
        Assuming the configuration settings are properly set, calling:
        ```python
        earl.__initial_preparation_for_subplots()
        ```
        will perform the initial preparations for the subplots based on the configuration settings.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.plt.close()
        self.fig, self.ax = self.plt.subplots(nrows=self.config['subplots_settings'][0]['rows_cols'][0], ncols=self.config['subplots_settings'][0]['rows_cols'][1], figsize=(self.config['subplots_settings'][0]['figure_size'][0], self.config['subplots_settings'][0]['figure_size'][1]))
        self.__prepare_axes()
        self.colorbars = []
        for i in range(self.number_of_subplots):
            x = (i) % self.config['subplots_settings'][0]['rows_cols'][1]
            y = (i) // self.config['subplots_settings'][0]['rows_cols'][1]
            #set titles and their sizes
            self.ax[y][x].set_xlabel(self.subplots_settings[i]["axes_titles"][0], loc="center", fontsize=self.subplots_settings[i]["axes_font_size"][0])
            self.ax[y][x].set_ylabel(self.subplots_settings[i]["axes_titles"][1], loc="center", fontsize=self.subplots_settings[i]["axes_font_size"][1])
            self.ax[y][x].set_title(self.subplots_settings[i]["subplots_titles_text"], loc="center", fontsize=self.subplots_settings[i]["subplots_titles_font_size"])

            #set inital axes properties
            self.min_number, self.max_number = [1, 1], [10, 10]
            self.steps = [9, 9]
            if self.subplots_settings[i]["axes_scaling"][0] == "stretch":
                self.__config_parameters_for_stretch_option(i)
            elif self.subplots_settings[i]["axes_scaling"][0] == "divide":
                self.__config_parameters_for_dividing_option(i)
            self.ax[y][x].xaxis.set_ticks_position("bottom")
            self.ax[y][x].yaxis.set_ticks_position("left")
            self.ax[y][x].spines["left"].set_position(("data", self.min_number[0]))
            self.ax[y][x].spines["bottom"].set_position(("data", self.min_number[1]))
            self.ax[y][x].set(xlim=(self.min_number[0], self.max_number[0]), ylim=(self.min_number[1], self.max_number[1]))
            self.ax[y][x].set_xticks(np.linspace(self.min_number[0], self.max_number[0], self.steps[0]))
            self.ax[y][x].set_yticks(np.linspace(self.min_number[1], self.max_number[1], self.steps[1]))
            self.ax[y][x].tick_params(axis='x', length=4, width=2)
            self.ax[y][x].tick_params(axis='y', length=4, width=2)
            
            self.logscaling = [0, 0]
            try:
                result = self.__try_put_log_scaling_x(i, x, y)
                if self.verbose and not (result is None):
                    print(result)
                result = self.__try_put_log_scaling_y(i, x, y)
                if self.verbose and not (result is None):
                    print(result)                
            except ValueError as e:
                print(f"Error is {e}")

            self.ax[y][x].xaxis.set_major_formatter(FormatStrFormatter(self.subplots_settings[i]["axes_round_accuracy"][0]))
            self.ax[y][x].yaxis.set_major_formatter(FormatStrFormatter(self.subplots_settings[i]["axes_round_accuracy"][1]))

            #set inital ticks properties
            self.ax[y][x].minorticks_on()
            if not self.logscaling[0]:
                self.ax[y][x].tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black')
                self.ax[y][x].xaxis.set_minor_locator(ticker.AutoMinorLocator(self.subplots_settings[i]["axes_number_of_small_ticks"][0]))
            if not self.logscaling[1]:
                self.ax[y][x].tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black')
                self.ax[y][x].yaxis.set_minor_locator(ticker.AutoMinorLocator(self.subplots_settings[i]["axes_number_of_small_ticks"][1]))
            self.ax[y][x].tick_params(direction ='in', length=5, width=1.5)

            #set grid
            self.ax[y][x].grid(color="#7a7c7d", linewidth=0.3)
            self.ax[y][x].grid(which='minor', color='#7a7c7d', linestyle=':', linewidth=0.2)

        self.fig.align_labels()
        self.fig.align_titles()
        self.fig.tight_layout()
    
    def __plot_data_on_subplots(self):
        """
        Plots the data on the specified subplots based on the curve settings.

        This method iterates through the curve settings and plots the data on the corresponding subplots.
        It supports both 2D and 3D graphs based on the `graph_type` specified in the curve settings.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Notes:
        ------
        - The method iterates through each curve setting in `self.curves_settings`.
        - It calculates the subplot position (x, y) based on the `subplot_position` parameter.
        - It checks the `graph_type` to determine whether to plot a 2D or 3D graph.
        - It calls `self.__plot_2d_graph` to plot a 2D graph or `self.__plot_3d_graph` to plot a 3D graph.

        Example:
        --------
        Assuming `self.curves_settings` is properly configured, calling:
        ```python
        earl.__plot_data_on_subplots()
        ```
        will plot the data on the specified subplots based on the curve settings.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        for i in range(self.quant):
            if self.curves_settings[i]["subplot_position"] < self.number_of_subplots:
                x = (self.curves_settings[i]["subplot_position"]) % self.config['subplots_settings'][0]['rows_cols'][1]
                y = (self.curves_settings[i]["subplot_position"]) // self.config['subplots_settings'][0]['rows_cols'][1]
                if self.curves_settings[i]["graph_type"] == 1:
                    self.__plot_2d_graph(i, x, y)
                elif self.curves_settings[i]["graph_type"] == 2:
                    self.__plot_3d_graph(i, x, y, self.curves_settings[i]["subplot_position"])
    
    def __plot_2d_graph(self, index, x, y):
        """
        Plots a 2D graph on the specified subplot based on the curve settings.

        This method extracts the data and plotting parameters from the curve settings and plots a 2D graph
        on the specified subplot. It supports plotting with error bars if the data includes error information.

        Arguments:
        ----------
        index : int
            The index of the curve setting in `self.curves_settings`.
        x : int
            The x-coordinate of the subplot in the grid.
        y : int
            The y-coordinate of the subplot in the grid.

        Returns:
        -------
        None

        Notes:
        ------
        - The method extracts the x and y data, color, line style, marker shape, marker size, line width,
          alpha (transparency), and label from the curve settings.
        - It checks the length of the data arrays to determine if error bars should be plotted.
        - It uses the `errorbar` method of the matplotlib Axes object to plot the data with error bars if available.
        - If no error bars are specified, it uses the `plot` method to plot the data.

        Example:
        --------
        Assuming `self.curves_settings` is properly configured, calling:
        ```python
        earl.__plot_2d_graph(index, x, y)
        ```
        will plot a 2D graph on the specified subplot based on the curve settings.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        x_data = self.curves_settings[index]["data"][0][0]
        y_data = self.curves_settings[index]["data"][1][0]
        color = self.curves_settings[index]["color"]
        ls = self.curves_settings[index]["ls"]
        marker_shape = self.curves_settings[index]["marker_shape"]
        marker_size = self.curves_settings[index]["marker_size"]
        lw = self.curves_settings[index]["line_width"]
        alpha = self.curves_settings[index]["line_alpha"]
        label = self.curves_settings[index]["label"]
        if label != "":
            if label[0] != '_':
                self.__labels_was_printed = True
        if len(self.curves_settings[index]["data"][0]) == 2 and len(self.curves_settings[index]["data"][1]) == 2:
            xerr_data = self.curves_settings[index]["data"][0][1]
            yerr_data = self.curves_settings[index]["data"][1][1]
            self.ax[y][x].errorbar(x=x_data, y=y_data, xerr=xerr_data, yerr=yerr_data, lw=lw, color=color, marker=marker_shape, markersize=marker_size, ls=ls, alpha=alpha, label=label)
        elif len(self.curves_settings[index]["data"][0]) == 2 and len(self.curves_settings[index]["data"][1]) == 1:
            xerr_data = self.curves_settings[index]["data"][0][1]
            self.ax[y][x].errorbar(x=x_data, y=y_data, xerr=xerr_data, lw=lw, color=color, marker=marker_shape, markersize=marker_size, ls=ls, alpha=alpha, label=label)
        elif len(self.curves_settings[index]["data"][0]) == 1 and len(self.curves_settings[index]["data"][1]) == 2:
            yerr_data = self.curves_settings[index]["data"][1][1]
            self.ax[y][x].errorbar(x=x_data, y=y_data, yerr=yerr_data, lw=lw, color=color, marker=marker_shape, markersize=marker_size, ls=ls, alpha=alpha, label=label)
        elif len(self.curves_settings[index]["data"][0]) == 1 and len(self.curves_settings[index]["data"][1]) == 1:
            self.ax[y][x].plot(x_data, y_data, lw=lw, color=color, marker=marker_shape, markersize=marker_size, ls=ls, alpha=alpha, label=label)
    
    def __plot_3d_graph(self, index, x, y, sub_index):
        """
        Plots a 3D graph on the specified subplot based on the curve settings.

        This method extracts the data and plotting parameters from the curve settings and plots a 3D graph
        on the specified subplot using a colormap. It also adds a colorbar to the subplot.

        Arguments:
        ----------
        index : int
            The index of the curve setting in `self.curves_settings`.
        x : int
            The x-coordinate of the subplot in the grid.
        y : int
            The y-coordinate of the subplot in the grid.
        sub_index : int
            The index of the subplot in the `self.subplots_settings`.

        Returns:
        -------
        None

        Raises:
        -------
        IndexError
            If the subplot index is out of range.
        KeyError
            If a required key is missing in the configuration.

        Notes:
        ------
        - The method extracts the x, y, and z data from the curve settings.
        - It uses the `pcolormesh` method of the matplotlib Axes object to plot the 3D data with a colormap.
        - It sets the minimum and maximum values for the colormap based on the z data.
        - It adds a colorbar to the subplot and sets its label and font size based on the subplot settings.
        - The colorbar is stored in the `self.colorbars` list for later reference.

        Example:
        --------
        Assuming `self.curves_settings` and `self.subplots_settings` are properly configured, calling:
        ```python
        earl.__plot_3d_graph(index, x, y, sub_index)
        ```
        will plot a 3D graph on the specified subplot based on the curve settings.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.colorbars.append([0, 0])
        self.colorbars[-1][0] = self.ax[y][x].pcolormesh(self.curves_settings[index]["data"][0], self.curves_settings[index]["data"][1], self.curves_settings[index]["data"][2], vmin=np.min(self.curves_settings[index]["data"][2]), vmax=np.max(self.curves_settings[index]["data"][2]), shading='gouraud', cmap=self.subplots_settings[sub_index]["colormap"])
        self.colorbars[-1][1] = self.fig.colorbar(self.colorbars[-1][0], ax=self.ax[y][x])
        self.colorbars[-1][1].set_label(size=self.subplots_settings[self.curves_settings[index]["subplot_position"]]["axes_font_size"][2], label=self.subplots_settings[self.curves_settings[index]["subplot_position"]]["axes_titles"][2])

    def __config_subplots_after_plotting_data(self):
        """
        Configures the subplots after plotting the data.

        This method iterates through each subplot and configures the legend properties based on the
        configuration settings. It uses helper methods to find the appropriate legend font size and position.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Raises:
        -------
        ValueError
            If there is an error in finding the proper legend font size or position.

        Notes:
        ------
        - The method iterates through each subplot to configure its legend properties.
        - It calculates the subplot position (x, y) based on the subplot index.
        - It uses the `__find_proper_legends_font_size` and `__find_proper_legend_position` methods to determine
          the appropriate legend font size and position.
        - It sets the legend properties using the `legend` method of the matplotlib Axes object.
        - If a `ValueError` is raised during the configuration, it prints an error message and exits the program.

        Example:
        --------
        Assuming the configuration settings are properly set, calling:
        ```python
        earl.config_cubplots_after_plotting_data()
        ```
        will configure the subplots after plotting the data.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        for i in range(self.number_of_subplots):
            x = (i) % self.config['subplots_settings'][0]['rows_cols'][1]
            y = (i) // self.config['subplots_settings'][0]['rows_cols'][1]
            try:
                fontsize_legend_font_size = self.__find_proper_legends_font_size(i)
                position_legend_position = self.__find_proper_legend_position(i)
            except ValueError as e:
                print(f"You have an error: {e}")
                sys.exit(1)
            #set legend properties
            if self.__labels_was_printed:
                self.ax[y][x].legend(loc=position_legend_position, frameon=False, prop={'size': fontsize_legend_font_size})

    def __prepare_axes(self):
        """
        Prepares the axes for plotting based on the number of rows and columns specified in the configuration.

        This method adjusts the `self.ax` attribute to ensure it is a 2D array, even if there is only one subplot.
        It handles different configurations of rows and columns to ensure consistency in the structure of `self.ax`.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Raises:
        -------
        None

        Notes:
        ------
        - The method checks the number of rows and columns specified in the configuration.
        - If there is only one subplot (1 row and 1 column), it wraps `self.ax` in a 2D array.
        - If there is one row and multiple columns, it wraps `self.ax` in a 2D array.
        - If there are multiple rows and one column, it wraps `self.ax` in a 2D array and transposes it.
        - This ensures that `self.ax` is always a 2D array, making it easier to handle subplots consistently.

        Example:
        --------
        Assuming the configuration settings are properly set, calling:
        ```python
        earl.__prepare_axes()
        ```
        will prepare the axes for plotting based on the number of rows and columns specified in the configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if self.config['subplots_settings'][0]['rows_cols'][0] == 1 and self.config['subplots_settings'][0]['rows_cols'][1] == 1:
            self.ax = np.array([[self.ax]])
        elif self.config['subplots_settings'][0]['rows_cols'][0] == 1 and self.config['subplots_settings'][0]['rows_cols'][1] > 1:
            self.ax = np.array([self.ax])
        elif self.config['subplots_settings'][0]['rows_cols'][0] > 1 and self.config['subplots_settings'][0]['rows_cols'][1] == 1:
            self.ax = np.array([self.ax]).T
            
    def __try_put_log_scaling_x(self, index, x, y):
        """
        Attempts to set logarithmic scaling for the x-axis of the specified subplot.

        This method checks the configuration settings for logarithmic scaling on the x-axis and applies it
        if the conditions are met. It raises a `ValueError` if logarithmic scaling is attempted on data with
        negative values.

        Arguments:
        ----------
        index : int
            The index of the subplot setting in `self.subplots_settings`.
        x : int
            The x-coordinate of the subplot in the grid.
        y : int
            The y-coordinate of the subplot in the grid.

        Returns:
        -------
        str or None
            A confirmation message if logarithmic scaling is successfully applied, or None if not.

        Raises:
        -------
        ValueError
            If logarithmic scaling is attempted on data with negative values.

        Notes:
        ------
        - The method checks if logarithmic scaling is enabled for the x-axis in the subplot settings.
        - It verifies that the minimum value on the x-axis is greater than zero before applying logarithmic scaling.
        - If the conditions are met, it sets the x-axis scale to logarithmic and updates the `self.logscaling` attribute.
        - If the minimum value is less than or equal to zero, it raises a `ValueError`.
        - If logarithmic scaling is not enabled or the conditions are not met, it sets `self.logscaling[0]` to 0.

        Example:
        --------
        Assuming `self.subplots_settings` is properly configured, calling:
        ```python
        result = earl.__try_put_log_scaling_x(index, x, y)
        ```
        will attempt to set logarithmic scaling for the x-axis of the specified subplot and return a confirmation message if successful.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if self.subplots_settings[index]["logarithmic_scaling"][0] and self.min_number[0] > 0:
            self.ax[y][x].set_xscale("log")
            self.logscaling[0] = 1
            return f"logarithmic_scaling for x subplot {index} is done"
        elif self.subplots_settings[index]["logarithmic_scaling"][0] and self.min_number[0] <= 0:
            self.logscaling[0] = 0
            raise ValueError(f"you can not use logarithmic scaling for negative data. The problem is for subplot {index} (x scale).")
        self.logscaling[0] = 0

    def __try_put_log_scaling_y(self, index, x, y):
        """
        Attempts to set logarithmic scaling for the y-axis of the specified subplot.

        This method checks the configuration settings for logarithmic scaling on the y-axis and applies it
        if the conditions are met. It raises a `ValueError` if logarithmic scaling is attempted on data with
        negative values.

        Arguments:
        ----------
        index : int
            The index of the subplot setting in `self.subplots_settings`.
        x : int
            The x-coordinate of the subplot in the grid.
        y : int
            The y-coordinate of the subplot in the grid.

        Returns:
        -------
        str or None
            A confirmation message if logarithmic scaling is successfully applied, or None if not.

        Raises:
        -------
        ValueError
            If logarithmic scaling is attempted on data with negative values.

        Notes:
        ------
        - The method checks if logarithmic scaling is enabled for the y-axis in the subplot settings.
        - It verifies that the minimum value on the y-axis is greater than zero before applying logarithmic scaling.
        - If the conditions are met, it sets the y-axis scale to logarithmic and updates the `self.logscaling` attribute.
        - If the minimum value is less than or equal to zero, it raises a `ValueError`.
        - If logarithmic scaling is not enabled or the conditions are not met, it sets `self.logscaling[1]` to 0.

        Example:
        --------
        Assuming `self.subplots_settings` is properly configured, calling:
        ```python
        result = earl.__try_put_log_scaling_y(index, x, y)
        ```
        will attempt to set logarithmic scaling for the y-axis of the specified subplot and return a confirmation message if successful.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        if self.subplots_settings[index]["logarithmic_scaling"][1] and self.min_number[1] > 0:
            self.logscaling[1] = 1
            self.ax[y][x].set_yscale("log")
            return f"logarithmic_scaling for y subplot {index} is done"
        if self.subplots_settings[index]["logarithmic_scaling"][1] and self.min_number[1] <= 0:
            self.logscaling[1] = 0
            raise ValueError(f"you can not use logarithmic scaling for negative data. The problem is for subplot {index} (y scale).")
        self.logscaling[1] = 0

    def __check_3d_graphs_in_this_subplot(self, index):
        """
        Checks if there are any 3D graphs in the specified subplot.

        This method iterates over the range defined by `self.quant` and checks if any of the
        curves have a `subplot_position` equal to the given `index` and a `graph_type` of 2 (indicating a 3D graph).

        Arguments:
        ----------
        index : int
            The position of the subplot to check.

        Returns:
        -------
        bool
            True if there is at least one 3D graph in the specified subplot, False otherwise.

        Attributes:
        ----------
        self.quant : int
            The number of data curves to check.
        self.curves_settings : list of dict
            A list of dictionaries where each dictionary contains settings for a curve.
            Each dictionary should have the following keys:
            - "subplot_position": int, the position of the subplot.
            - "graph_type": int, the type of graph (1 for 2D, 2 for 3D).

        Example:
        --------
        Assuming `self.quant` is 3, `self.curves_settings` is:
        [
            {"subplot_position": 0, "graph_type": 1},
            {"subplot_position": 1, "graph_type": 2},
            {"subplot_position": 2, "graph_type": 1}
        ]
        and `index` is 1, this method will return True because there is a 3D graph at subplot position 1.
        """
        for i in range(self.quant):
            if self.curves_settings[i]["subplot_position"] == index and self.curves_settings[i]["graph_type"] == 2:
                return True
        return False   

    def __config_parameters_for_stretch_option(self, index):
        """
        Configures the parameters for the stretch option for a specified subplot.

        This method iterates over the range defined by `self.quant` and configures the minimum
        and maximum values for the specified subplot based on the curves' settings. It also
        applies scaling factors to these values.

        Arguments:
        ----------
        index : int
            The position of the subplot to configure.

        Returns:
        -------
        None

        Attributes:
        ----------
        self.quant : int
            The number of data curves to check.
        self.curves_settings : list of dict
            A list of dictionaries where each dictionary contains settings for a curve.
            Each dictionary should have the following keys:
            - "subplot_position": int, the position of the subplot.
        self.min_number : list of float
            The minimum values for the subplot axes.
        self.max_number : list of float
            The maximum values for the subplot axes.
        self.subplots_settings : list of dict
            A list of dictionaries where each dictionary contains settings for a subplot.
            Each dictionary should have the following keys:
            - "axes_scaling": list of list of float, the scaling factors for the axes.
        self.steps : list of int
            The number of steps for the axes, set to [11, 11] by default.

        Methods:
        -------
        self.__find_min_max_element(i)
            Finds the minimum and maximum elements for the curve at index `i`.

        Notes:
        ------
        - The method updates `self.min_number` and `self.max_number` based on the minimum and
        maximum values found for each curve in the specified subplot.
        - Scaling factors from `self.subplots_settings` are applied to `self.min_number` and
        `self.max_number`.

        Example:
        --------
        Assuming `self.quant` is 3, `self.curves_settings` is:
            {"subplot_position": 0, "graph_type": 1, ...other settings...},
            {"subplot_position": 1, "graph_type": 2, ...other settings...},
        and `self.subplots_settings` is:
        [
            {"axes_scaling": ["stretch", [0.9, 1.1, 0.9, 1.1]], ...other settings...},
            {"axes_scaling": ["stretch", [0.8, 1.2, 0.7, 1.5]], ...other settings...}
        ]
        and `index` is 1, this method will configure the parameters for the subplot at position 1.
        
        Inspiration:
        --------
        Songs from author Nico Santos.
        """
        flag = True
        for i in range(self.quant):
            if self.curves_settings[i]["subplot_position"] == index:
                result_min, result_max = self.__find_min_max_element(i)
                if flag:
                    self.min_number, self.max_number = result_min, result_max
                    flag = False
                else:
                    if result_min[0] < self.min_number[0]:
                        self.min_number[0] = result_min[0]
                    if result_min[1] < self.min_number[1]:
                        self.min_number[1] = result_min[1]
                    if result_max[0] > self.max_number[0]:
                        self.max_number[0] = result_max[0]
                    if result_max[1] > self.max_number[1]:
                        self.max_number[1] = result_max[1]

        self.min_number[0] *= self.subplots_settings[index]["axes_scaling"][1][0]
        self.min_number[1] *= self.subplots_settings[index]["axes_scaling"][1][2]
        self.max_number[0] *= self.subplots_settings[index]["axes_scaling"][1][1]
        self.max_number[1] *= self.subplots_settings[index]["axes_scaling"][1][3]
        self.steps = [11, 11]

    def __config_parameters_for_dividing_option(self, index):
        """
        Configures the parameters for the dividing option for a specified subplot.

        This method sets the minimum and maximum values, as well as the number of steps,
        for the specified subplot based on the axes scaling settings.

        Arguments:
        ----------
        index : int
            The position of the subplot to configure.

        Returns:
        -------
        None

        Attributes:
        ----------
        self.min_number : list of float
            The minimum values for the subplot axes.
        self.max_number : list of float
            The maximum values for the subplot axes.
        self.steps : list of int
            The number of steps for the subplot axes.
        self.subplots_settings : list of dict
            A list of dictionaries where each dictionary contains settings for a subplot.
            Each dictionary should have the following keys:
            - "axes_scaling": list of list of list of float, the scaling factors for the axes.

        Notes:
        ------
        - The method updates `self.min_number`, `self.max_number`, and `self.steps` based on
        the axes scaling settings for the specified subplot.

        Example:
        --------
        Assuming `self.subplots_settings[index]` is:
        {
            "axes_scaling": ["divide", [[0, 7, 8], [-10, 10, 11]]],
            ...other settings...
        }
        and `index` is 1, this method will configure the parameters for the subplot at position 1
        with the following values:
        - `self.min_number[0]` = 0
        - `self.min_number[1]` = -10
        - `self.max_number[0]` = 7
        - `self.max_number[1]` = 10
        - `self.steps[0]` = 8
        - `self.steps[1]` = 11
        """
        self.min_number[0] = self.subplots_settings[index]["axes_scaling"][1][0][0]
        self.min_number[1] = self.subplots_settings[index]["axes_scaling"][1][1][0]
        self.max_number[0] = self.subplots_settings[index]["axes_scaling"][1][0][1]
        self.max_number[1] = self.subplots_settings[index]["axes_scaling"][1][1][1]
        self.steps[0] = self.subplots_settings[index]["axes_scaling"][1][0][2]
        self.steps[1] = self.subplots_settings[index]["axes_scaling"][1][1][2]

    def __find_min_max_element(self, index):
        """
        Finds the minimum and maximum elements for the curve at the specified index.

        This method determines the minimum and maximum values for the data associated with
        the curve at the given index based on the graph type specified in `self.curves_settings`.

        Arguments:
        ----------
        index : int
            The index of the curve to find the minimum and maximum elements for.

        Returns:
        -------
        tuple
            A tuple containing two lists:
            - min_el: A list of the minimum values for the curve's data.
            - max_el: A list of the maximum values for the curve's data.

        Attributes:
        ----------
        self.curves_settings : list of dict
            A list of dictionaries where each dictionary contains settings for a curve.
            Each dictionary should have the following keys:
            - "graph_type": int, the type of graph (1 for 2D, 2 for 3D).
            - "data": list of list, the data associated with the curve.

        Notes:
        ------
        - For 3D graphs (graph_type == 2), the method finds the minimum and maximum values
        directly from the data.
        - For 2D graphs (graph_type == 1), the method handles different data structures:
            - If the data has two elements, it calculates the minimum and maximum values
            considering the difference and sum of the elements.
            - If the data has one element, it directly finds the minimum and maximum values.

        Example:
        --------
        Assuming `self.curves_settings` is:
        [
            {"graph_type": 2, "data": [x, y, z]},
            {"graph_type": 1, "data": [[x, xerr], [y, yerr]]},
            {"graph_type": 1, "data": [[x, xerr], [y]]}
        ]
        and `index` is 1, this method will return the minimum and maximum elements for the
        2D graph at index 1.
        """
        min_el = [0, 0]
        max_el = [0, 0]
        if self.curves_settings[index]["graph_type"] == 2:
            min_el[0] = np.min(self.curves_settings[index]["data"][0])
            min_el[1] = np.min(self.curves_settings[index]["data"][1])
            max_el[0] = np.max(self.curves_settings[index]["data"][0])
            max_el[1] = np.max(self.curves_settings[index]["data"][1])                        
        elif self.curves_settings[index]["graph_type"] == 1:
            if len(self.curves_settings[index]["data"][0]) == 2:
                min_el[0] = np.min(self.curves_settings[index]["data"][0][0] - self.curves_settings[index]["data"][0][1])
                max_el[0] = np.max(self.curves_settings[index]["data"][0][0] + self.curves_settings[index]["data"][0][1])
            elif len(self.curves_settings[index]["data"][0]) == 1:
                min_el[0] = np.min(self.curves_settings[index]["data"][0][0])
                max_el[0] = np.max(self.curves_settings[index]["data"][0][0])
            if len(self.curves_settings[index]["data"][1]) == 2:
                min_el[1] = np.min(self.curves_settings[index]["data"][1][0] - self.curves_settings[index]["data"][1][1])
                max_el[1] = np.max(self.curves_settings[index]["data"][1][0] + self.curves_settings[index]["data"][1][1])
            elif len(self.curves_settings[index]["data"][1]) == 1:
                min_el[1] = np.min(self.curves_settings[index]["data"][1][0])
                max_el[1] = np.max(self.curves_settings[index]["data"][1][0])
        return min_el, max_el

    def __find_proper_axes_font_size(self, index):
        """
        Finds the appropriate axes font size for the specified subplot index.

        This method searches through the axes font size settings in `self.config` to find the
        appropriate font size for the given subplot index. If a specific font size is not found,
        it checks for a default font size setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the axes font size for.

        Returns:
        -------
        list of two int
            The font size for the axes of the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default font size setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "axes_font_size": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The font size for the axes of the subplot.

        Notes:
        ------
        - The method first searches for a specific font size setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "axes_font_size": [[0, [12, 12]], [1, [14, 13]], [-1, [10, 10]]]
        }
        and `index` is 2, this method will return [10, 10] because there is no specific setting for
        subplot index 2, but there is a default setting of [10, 10]. If `index` is 1, this method will return [14, 13].
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_font_size"][i][0] == index:
                return self.config["axes_font_size"][i][1]
            elif self.config["axes_font_size"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have fontsize for these axes titles of subplot {i} or fontsize for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_font_size"][flag_minus_one][1]
    
    def __find_proper_subplots_titles_font_size(self, index):
        """
        Finds the appropriate title font size for the specified subplot index.

        This method searches through the subplot titles font size settings in `self.config` to find the
        appropriate font size for the given subplot index. If a specific font size is not found,
        it checks for a default font size setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the title font size for.

        Returns:
        -------
        int
            The font size for the title of the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default font size setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "subplots_titles_font_size": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The font size for the title of the subplot.

        Notes:
        ------
        - The method first searches for a specific font size setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "subplots_titles_font_size": [[0, 12], [1, 14], [-1, 10]]
        }
        and `index` is 2, this method will return 10 because there is no specific setting for
        subplot index 2, but there is a default setting of 10. If `index` is 1, this method will return 14.
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["subplots_titles_font_size"][i][0] == index:
                return self.config["subplots_titles_font_size"][i][1]
            elif self.config["subplots_titles_font_size"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have fontsize for title for these subplot {i} or fontsize for all subplots. ([x, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["subplots_titles_font_size"][flag_minus_one][1]        
    
    def __find_proper_axes_number_of_small_ticks(self, index):
        """
        Finds the appropriate number of small ticks for the axes of the specified subplot index.

        This method searches through the axes number of small ticks settings in `self.config` to find the
        appropriate number of small ticks for the given subplot index. If a specific setting is not found,
        it checks for a default setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the number of small ticks for.

        Returns:
        -------
        list of two int
            The number of small ticks for the axes of the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default number of small ticks setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "axes_number_of_small_ticks": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The number of small ticks for the axes of the subplot.

        Notes:
        ------
        - The method first searches for a specific number of small ticks setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "axes_number_of_small_ticks": [[0, [5, 5]], [1, [7, 4]], [-1, [5, 5]]
        }
        and `index` is 2, this method will return [5, 5] because there is no specific setting for
        subplot index 2, but there is a default setting of [5, 5]. If `index` is 1, this method will return [7, 4].
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_number_of_small_ticks"][i][0] == index:
                return self.config["axes_number_of_small_ticks"][i][1]
            elif self.config["axes_number_of_small_ticks"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have number of small ticks for these axes titles of subplot {i} or number of small ticks for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_number_of_small_ticks"][flag_minus_one][1]

    def __find_proper_legends_font_size(self, index):
        """
        Finds the appropriate legend font size for the specified subplot index.

        This method searches through the legend font size settings in `self.config` to find the
        appropriate font size for the given subplot index. If a specific font size is not found,
        it checks for a default font size setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the legend font size for.

        Returns:
        -------
        int
            The font size for the legend of the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default font size setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "legends_font_size": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The font size for the legend of the subplot.

        Notes:
        ------
        - The method first searches for a specific font size setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "legends_font_size": [[0, 12], [1, 14], [-1, 10]]
        }
        and `index` is 2, this method will return 10 because there is no specific setting for
        subplot index 2, but there is a default setting of 10. If `index` is 1, this method will return 14.
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["legends_font_size"][i][0] == index:
                return self.config["legends_font_size"][i][1]
            elif self.config["legends_font_size"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have legend fontsize for these subplot {i} or legend fontsize for all subplots. ([x, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["legends_font_size"][flag_minus_one][1] 

    def __find_proper_legend_position(self, index):
        """
        Finds the appropriate legend position for the specified subplot index.

        This method searches through the legend position settings in `self.config` to find the
        appropriate position for the given subplot index. If a specific position is not found,
        it checks for a default position setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the legend position for.

        Returns:
        -------
        str
            The position for the legend of the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default legend position setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "subplots_legend_position": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The position for the legend of the subplot.

        Notes:
        ------
        - The method first searches for a specific legend position setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "subplots_legend_position": [[0, "upper right"], [1, "lower left"], [-1, "best"]]
        }
        and `index` is 2, this method will return "best" because there is no specific setting for
        subplot index 2, but there is a default setting of "best". If `index` is 0, this method will return "upper right".
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["subplots_legend_position"][i][0] == index:
                return self.config["subplots_legend_position"][i][1]
            elif self.config["subplots_legend_position"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have legend position for title for these subplot {i} or legend position for all subplots. ([x, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["subplots_legend_position"][flag_minus_one][1] 

    def __find_proper_axes_round_accuracy(self, index):
        """
        Finds the appropriate rounding accuracy for the axes of the specified subplot index.

        This method searches through the axes rounding accuracy settings in `self.config` to find the
        appropriate rounding accuracy for the given subplot index. If a specific setting is not found,
        it checks for a default setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the axes rounding accuracy for.

        Returns:
        -------
        list of two strings
            The rounding accuracy for the axes of the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default rounding accuracy setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "axes_round_accuracy": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The rounding accuracy for the axes of the subplot.

        Notes:
        ------
        - The method first searches for a specific rounding accuracy setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "axes_round_accuracy": [[0, ["%0.2f", "%0.2f"]], [1, ["%0.2f", "%0.1f"]], [-1, ["%0.0f", "%0.1f"]]]
        }
        and `index` is 2, this method will return ["%0.0f", "%0.1f"] because there is no specific setting for
        subplot index 2, but there is a default setting of ["%0.0f", "%0.1f"]. If `index` is 1, method will return ["%0.2f", "%0.1f"]. 
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_round_accuracy"][i][0] == index:
                return self.config["axes_round_accuracy"][i][1]
            elif self.config["axes_round_accuracy"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have element axes_round_accuracy for these subplot {i} or axes_round_accuracy for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_round_accuracy"][flag_minus_one][1]

    def __find_proper_logarithmic_scaling(self, index):
        """
        Finds the appropriate logarithmic scaling for the specified subplot index.

        This method searches through the logarithmic scaling settings in `self.config` to find the
        appropriate scaling for the given subplot index. If a specific setting is not found,
        it checks for a default setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the logarithmic scaling for.

        Returns:
        -------
        list of two int (0 or 1)
            The logarithmic scaling for both axes setting for the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default logarithmic scaling setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "logarithmic_scaling": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The logarithmic scaling setting for the subplot.

        Notes:
        ------
        - The method first searches for a specific logarithmic scaling setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "logarithmic_scaling": [[0, [0, 1]], [1, [1, 0]], [-1, [1, 1]]]
        }
        and `index` is 2, this method will return [1, 1] because there is no specific setting for
        subplot index 2, but there is a default setting of [1, 1]. If `index` is 0, this method will return [0, 1].
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["logarithmic_scaling"][i][0] == index:
                return self.config["logarithmic_scaling"][i][1]
            elif self.config["logarithmic_scaling"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have argument for logarithmic_scaling for these axes titles of subplot {i} or one logarithmic_scaling argument for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["logarithmic_scaling"][flag_minus_one][1]
        
    def __find_proper_axes_scaling(self, index):
        """
        Finds the appropriate axes scaling for the specified subplot index.

        This method searches through the axes scaling settings in `self.config` to find the
        appropriate scaling for the given subplot index. If a specific setting is not found,
        it checks for a default setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the axes scaling for.

        Returns:
        -------
        list
            The axes scaling settings for the specified subplot.

        Raises:
        -------
        ValueError
            If no specific or default axes scaling setting is found for the subplot.

        Attributes:
        ----------
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "axes_scaling": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The axes scaling settings for the subplot.

        Notes:
        ------
        - The method first searches for a specific axes scaling setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, a ValueError is raised.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3 and `self.config` is:
        {
            "axes_scaling": [[0, "stretch", [0.9, 1.1, 0.8, 1]], [2, "divide", [[0, 1.2, 7], [-1.4, 1.4, 8]]], [-1, "stretch", [0.99, 1.01, 0.85, 1.15]]
        }
        and `index` is 2, this method will return ["stretch", [0.99, 1.01, 0.85, 1.15]] because there is no specific setting for
        subplot index 2, but there is a default setting of ["stretch", [0.99, 1.01, 0.85, 1.15]]. If `index` is 2, this method will return ["divide", [[0, 1.2, 7], [-1.4, 1.4, 8]]].
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_scaling"][i][0] == index:
                return self.config["axes_scaling"][i][1:]
            elif self.config["axes_scaling"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have argument for axes_scaling for these axes titles of subplot {i} or one logarithmic_scaling argument for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_scaling"][flag_minus_one][1:]
        
    def __find_proper_colormap(self, index):
        """
        Finds the appropriate colormap for the specified subplot index.

        This method searches through the colormap settings in `self.config` to find the
        appropriate colormap for the given subplot index. If a specific setting is not found,
        it checks for a default setting that applies to all subplots.

        Arguments:
        ----------
        index : int
            The index of the subplot to find the colormap for.

        Returns:
        -------
        str
            The colormap for the specified subplot. If no specific or default colormap is found,
            it returns "plasma".

        Raises:
        -------
        None

        Attributes:
        ----------
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - "colormap": list of list, where each inner list contains:
                - The subplot index or -1 (indicating a default setting for all subplots).
                - The colormap setting for the subplot.

        Notes:
        ------
        - The method first searches for a specific colormap setting for the given subplot index.
        - If no specific setting is found, it looks for a default setting (indicated by -1).
        - If neither a specific nor a default setting is found, it returns "plasma".

        Example:
        --------
        Assuming `self.config` is:
        {
            "colormap": [[0, "viridis"], [1, "inferno"], [-1, "magma"]]
        }
        and `index` is 2, this method will return "magma" because there is no specific setting for
        subplot index 2, but there is a default setting of "magma". If `index` is 0, this method will return "viridis".
        """
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(len(self.config["colormap"])):
            if self.config["colormap"][i][0] == index:
                return self.config["colormap"][i][1]
            elif self.config["colormap"][i][0] == -1 and flag_minus_one == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            return  "plasma" #raise ValueError(f"you don't have colormap for these subplot {i} or colormap for all subplots. ([x, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["colormap"][flag_minus_one][1] 
        
    def __check_parameters(self, **kwargs):
        """
        Validate plot parameters passed as keyword arguments against predefined checks.

        This method iterates through the provided keyword arguments, ensuring each parameter
        exists in the configuration and then validates its value using specific check functions.

        Arguments:
        ----------
        **kwargs : dict
            Arbitrary keyword arguments representing plot parameters to be validated.

        Raises:
        -------
        KeyError
            If a provided parameter key does not exist in the configuration.
        TypeError or ValueError
            If the parameter value fails validation by its check function.

        Attributes:
        ----------
        self.config : dict
            A dictionary containing configuration settings. It should have the following structure:
            - Keys represent acceptable parameter names.
        self.verbose : bool
            When True, prints validation results for each parameter.

        Notes:
        ------
        - The method first checks if each provided parameter key exists in the configuration.
        - It then validates the value of each parameter using a corresponding check function.
        - If `self.verbose` is True, the method prints the validation results for each parameter.
        - If a parameter key is not found in the configuration, a KeyError is raised.
        - If a parameter value fails validation, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `self.config` is:
        {
            "color": ["#1B1F3B"],
            "ls": ["-"],
            "marker_shape": ["o"],
            "axes_font_size": [[-1, [12, 12]]],
            "subplots_titles_font_size": [[-1, 14]],
            "subplots_titles_text": ["a"],
            "legends_font_size": [[-1, 10]],
            "marker_size": [3],
            "line_width": [1],
            "line_alpha": [1.0],
            "axes_round_accuracy": [[-1, ["%0.2f", "%0.2f"]]],
            "subplots_settings": [{"rows_cols": [2, 2], "figure_size": [10, 8], "subplots_distribution": [1, 1]}],
            "graph_types": ["2D", "3D"],
            "axes_scaling": [[-1, "stretch", [0.9, 1.1, 0.9, 1.1]]],
            "axes_number_of_small_ticks": [[-1, [5, 5]]],
            "labels": ["exp", "scaling"],
            "axes_titles": [["X-axis", "Y-axis"]],
            "subplots_legend_position": [[-1, "best"]],
            "logarithmic_scaling": [[-1, [0, 0]]],
            "colormap": [[-1, "plasma"]]
        }
        and `kwargs` is:
        {
            "color": "#3498DB",
            "marker_shape": "s",
            "axes_font_size": [-1, [16, 16]]
        }
        This method will validate the provided parameters and update `self.config` accordingly.
        """
        # Dictionary mapping each parameter to its corresponding validation function
        check_functions = {
            "color": self.__check_color, 
            "ls": self.__check_ls,
            "marker_shape": self.__check_marker_shape, 
            "axes_font_size": self.__check_axes_font_size, 
            "subplots_titles_font_size": self.__check_subplots_titles_font_size, 
            "subplots_titles_text": self.__check_subplots_titles_text,
            "legends_font_size": self.__check_legends_font_size, 
            "marker_size": self.__check_marker_size,
            "line_width": self.__check_line_width, 
            "line_alpha": self.__check_line_alpha, 
            "axes_round_accuracy": self.__check_axes_round_accuracy, 
            "subplots_settings": self.__check_subplots_settings,
            "graph_types": self.__check_graph_types, 
            "axes_scaling": self.__check_axes_scaling,
            "axes_number_of_small_ticks": self.__check_axes_number_of_small_ticks, 
            "labels": self.__check_labels,
            "axes_titles": self.__check_axes_titles, 
            "subplots_legend_position": self.__check_subplots_legend_position,
            "logarithmic_scaling": self.__check_logarithmic_scaling,
            "rows_cols": self.__check_rows_cols,
            "figure_size": self.__check_figure_size,
            "subplots_distribution": self.__check_subplots_distribution,
            "colormap": self.__check_colormap
        }

        for key, value in kwargs.items():
            try:
                # Check if the key exists in the configuration
                if key not in check_functions.keys():
                    raise KeyError(f"{key} is not an argument in configuration file. Maybe you should check your spelling :)")
                
                # Attempt to validate the value with the appropriate check function
                try:
                    result = check_functions[key](value)
                    if self.verbose:
                        print(result[0])  # Print the validation result if verbose mode is on
                    if key in ["rows_cols", "figure_size", "subplots_distribution"]:
                        self.config["subplots_settings"][0][key] = result[1]
                    else:
                        self.config[key] = result[1]
                except (TypeError, ValueError) as e:
                    print(f'Error: {e}')  # Print any validation errors
                
            except KeyError as e:
                # This catches the KeyError from above if the key is not in json_keys
                print(f"Error has occurred. \n {e}")
                
    def __check_color(self, colors):
        """
        Validate the color input for plotting, ensuring it matches hex color format.

        This function checks if the provided colors are either a single hex color string
        or a list of hex color strings. Each color must start with '#' followed by 6 characters
        (0-9, A-F).

        Arguments:
        ----------
        colors : str or list of str
            Either a string representing a single color or a list of strings for multiple colors for all data.

        Returns:
        -------
        tuple
            A tuple containing a success message and a list with the validated color(s).

        Raises:
        -------
        TypeError
            If the color(s) provided are not in the expected format (str or list of str).
        ValueError
            If any color string does not adhere to the hex color format.

        Notes:
        ------
        - The method first checks if the input is a string or a list of strings.
        - For a single color string, it validates the format (starts with '#' and is 7 characters long).
        - For a list of color strings, it iterates through each string and validates the format.
        - If any color string does not match the expected format, a ValueError is raised.
        - If the input is not a string or a list of strings, a TypeError is raised.

        Example:
        --------
        Assuming `colors` is:
        - "red" (incorrect format)
        - "#FF5733" (correct format)
        - ["#FF5733", "#33FF57"] (correct format)
        - ["#FF5733", "blue"] (incorrect format)

        This method will validate the provided colors and return a success message along with the validated colors.
        Inspiration:
        --------
        Bi-2's "Event Horizon" playlist.
        """
        if not isinstance(colors, (list, str)):
            raise TypeError(f"Color argument is incorrect. It should be a list with color codes as string or one color as string for all data.")
        if isinstance(colors, str):
            if colors[0] == "#" and len(colors) == 7:
                return (f"Color argument is correct", [colors])
            else:
                raise ValueError(f"Color has incorrect code. It should be presented in the way like #XXXXXX, where X is numbers (0, ... 9) or letters from A to F. You can use this site https://csscolor.ru/ to get the right colot code.")
        elif isinstance(colors, list):
            for i in range(len(colors)):
                if not isinstance(colors[i], str):
                    raise TypeError(f"Color argument number {i} ({colors[i]}) is incorrect. It should be a string.")
                if not (colors[i][0] == "#" and len(colors[i]) == 7):
                    raise ValueError(f"Color number {i} ({colors[i]}) has incorrect code. It should be presented in the way like #XXXXXX, where X is numbers (0, ... 9) or letters from A to F. You can use this site https://csscolor.ru/ to get the right colot code.")
            return (f"Color argument is correct", colors)
        
    def __check_ls(self, ls):
        """
        Validate line style (ls) for plotting, ensuring it's a recognized matplotlib style.

        This function verifies if the line style input is either a string for a single style
        or a list of strings for multiple styles. Accepted styles are "-", "--", "-.", ":", and "".

        Arguments:
        ----------
        ls : str or list of str
            Either a string representing a single line style or a list of strings for multiple styles.

        Returns:
        -------
        tuple
            A tuple containing a success message and a list with the validated line style(s).

        Raises:
        -------
        TypeError
            If the line style(s) provided are not in the expected format (str or list of str).
        ValueError
            If any line style does not match the recognized styles.

        Notes:
        ------
        - The method first checks if the input is a string or a list of strings.
        - For a single line style string, it validates the format against the accepted styles.
        - For a list of line style strings, it iterates through each string and validates the format.
        - If any line style does not match the accepted styles, a ValueError is raised.
        - If the input is not a string or a list of strings, a TypeError is raised.

        Example:
        --------
        Assuming `ls` is:
        - "solid" (incorrect format)
        - "-" (correct format)
        - ["-", "--"] (correct format)
        - ["-", "dotted"] (incorrect format)

        This method will validate the provided line styles and return a success message along with the validated line styles.

        Inspiration:
        ------------
        Bi-2's "Event Horizon" playlist.
        """
        if not isinstance(ls, (list, str)):
            raise TypeError(f"ls argument is incorrect. It should be a list with ls types as string or one ls type as string for all data.")
        if isinstance(ls, str):
            if ls in ["-", "--", "-.", ":", ""]:
                return (f"ls argument is correct", [ls])
            else:
                raise ValueError(f"ls has incorrect code. It should be one element from this list [\"-\", \"--\", \"-.\", \":\", \"\"]")
        elif isinstance(ls, list):
            for i in range(len(ls)):
                if not isinstance(ls[i], str):
                    raise TypeError(f"ls argument number {i} ({ls[i]}) is incorrect. It should be a string.")
                if not (ls[i] in ["-", "--", "-.", ":", ""]):
                    raise ValueError(f"ls argument number {i} ({ls[i]}) has incorrect code. It should be one element from this list [\"-\", \"--\", \"-.\", \":\", \"\"]")
            return (f"ls argument is correct", ls)
        
    def __check_marker_shape(self, marker_shape): 
        """
        Validate marker shapes for plotting, ensuring they are recognized matplotlib markers.

        This function checks if the marker shape input is either a single string representing
        a marker type or a list of strings for multiple marker types. It validates against
        a predefined set of acceptable marker shapes.

        Arguments:
        ----------
        marker_shape : str or list of str
            Either a string for a single marker shape or a list of strings for multiple shapes.

        Returns:
        -------
        tuple
            A tuple containing a success message and the validated marker shape(s) as a list.

        Raises:
        -------
        TypeError
            If the marker shape(s) provided are not in the expected format (str or list of str).
        ValueError
            If any marker shape does not match the recognized marker styles.

        Notes:
        ------
        - The method first checks if the input is a string or a list of strings.
        - For a single marker shape string, it validates the format against the accepted marker shapes.
        - For a list of marker shape strings, it iterates through each string and validates the format.
        - If any marker shape does not match the accepted marker shapes, a ValueError is raised.
        - If the input is not a string or a list of strings, a TypeError is raised.

        Example:
        --------
        Assuming `marker_shape` is:
        - "circle" (incorrect format)
        - "o" (correct format)
        - [".", "o"] (correct format)
        - ["o", "square"] (incorrect format)

        This method will validate the provided marker shapes and return a success message along with the validated marker shapes.

        Inspiration:
        ------------
        Bi-2's "Event Horizon" playlist.
        """
        if not isinstance(marker_shape, (list, str)):
            raise TypeError(f"marker_shape argument is incorrect. It should be a list with marker_shape types as string or one marker_shape type as string for all data.")
        if isinstance(marker_shape, str):
            if marker_shape in [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", "d", "|", "_", ""]:
                return (f"marker_shape argument is correct", [marker_shape])
            else:
                raise ValueError(f"marker_shape has incorrect code. It should be one element from this list [\".\", \",\", \"o\", \"v\", \"^\", \"<\", \">\", \"1\", \"2\", \"3\", \"4\", \"8\", \"s\", \"p\", \"P\", \"*\", \"h\", \"H\", \"+\", \"x\", \"X\", \"D\", \"d\", \"|\", \"_\", \"\"]")
        elif isinstance(marker_shape, list):
            for i in range(len(marker_shape)):
                if not isinstance(marker_shape[i], str):
                    raise TypeError(f"marker_shape argument number {i} ({marker_shape[i]}) is incorrect. It should be a string.")
                if not (marker_shape[i] in [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", "d", "|", "_", ""]):
                    raise ValueError(f"marker_shape argument number {i} ({marker_shape[i]}) has incorrect code. It should be one element from this list [\".\", \",\", \"o\", \"v\", \"^\", \"<\", \">\", \"1\", \"2\", \"3\", \"4\", \"8\", \"s\", \"p\", \"P\", \"*\", \"h\", \"H\", \"+\", \"x\", \"X\", \"D\", \"d\", \"|\", \"_\", \"\"]")
            return (f"marker_shape argument is correct", marker_shape)
    
    def __check_axes_font_size(self, axes_font_size):
        """
        Validate the font size for axes labels in subplots.

        Ensures that the font size for axes is either a single integer for all subplots or
        a list specifying font sizes for individual subplots in the format [subplot_number, [x_axis_fontsize, y_axis_fontsize]] or [subplot_number, [x_axis_fontsize, y_axis_fontsize, cbar_axis_fontsize]].

        Arguments:
        ----------
        axes_font_size : int or list
            An integer for uniform font size or a list for customized sizes per subplot.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated font size configuration.

        Raises:
        -------
        TypeError
            If the axes_font_size argument is not in the correct format.
        ValueError
            If the structure or values within axes_font_size are incorrect.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a default configuration.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot number and a list of font sizes.
        - The subplot number should be an integer and can be -1 for a default setting.
        - The list of font sizes should contain either two or three integers, each representing the font size for the x-axis, y-axis, and optionally the colorbar title.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `axes_font_size` is:
        - 12 (correct format)
        - [[0, [10, 12]]] (correct format)
        - [[0, [10, 12]], [-1, [8, 8]]] (correct format)
        - [[0, [10, 12, 14]]] (correct format)
        - [[0, [10, 12, 14]], [1, [10, 12]], [-1, [8, 8]]] (correct format)
        - [[0, [10]]] (incorrect format)
        - [0, [10]] (incorrect format)
        - [0, 12] (incorrect format)

        This method will validate the provided font sizes and return a success message along with the validated font size configuration.

        Inspiration:
        ------------
        "Kukoriki" series, episodes "Syr-Bor, New Year's", "A Place in History".
        """
        text_that_explain_structure = " The structure of one element is [x, [y, y]] ([x, [y, y, y]]) (x - number of subplot, y - number - size of font for axes (and colorbar title) for x subplot)"
        if not isinstance(axes_font_size, (list, int)):
            raise TypeError(f"axes_font_size argument is incorrect. It should be a list with elements." +text_that_explain_structure)
        if isinstance(axes_font_size, int):
            return (f"axes_font_size argument is correct", [[-1, [axes_font_size, axes_font_size]]])
        elif isinstance(axes_font_size, list):
            for i in range(len(axes_font_size)):
                if not isinstance(axes_font_size[i], list):
                    raise TypeError(f'axes_font_size argument number {i} ({axes_font_size[i]}) should be list.')
                elif len(axes_font_size[i]) != 2:
                    raise TypeError(f'axes_font_size argument number {i} ({axes_font_size[i]}) should have two elements.')
                elif not isinstance(axes_font_size[i][0], int):
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i][0]}) should be int.' + text_that_explain_structure)
                elif axes_font_size[i][0] < 0 and axes_font_size[i] != -1:
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i][0]}) should be positive or -1.' + text_that_explain_structure)
                elif not isinstance(axes_font_size[i][1], list):
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i][1]}) should be list.' + text_that_explain_structure)
                elif len(axes_font_size[i][1]) not in [2, 3]:
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i][1]}) should have two elements.' + text_that_explain_structure)
                elif len(axes_font_size[i][1]) in [2, 3]:
                    for j in range(len(axes_font_size[i][1])):
                        if not (isinstance(axes_font_size[i][1][j], int)):
                            raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i][1][j]}) should be int.' + text_that_explain_structure)
                        elif axes_font_size[i][1][j] < 1:
                            raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i][1][j]}) should be more than zero.' + text_that_explain_structure)
            return (f"axes_font_size argument is correct.", axes_font_size)
        
    def  __check_subplots_titles_font_size(self, subplots_titles_font_size): 
        """
        Validate the font size for subplot titles.

        Checks if the font size for subplot titles is either a single positive integer
        for all plots or a list of positive integers for individual plot title font sizes.

        Arguments:
        ----------
        subplots_titles_font_size : int or list
            An integer for uniform title font size or a list for varied sizes.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated font sizes.

        Raises:
        -------
        TypeError
            If subplots_titles_font_size is not an integer or list of integers.
        ValueError
            If any font size provided is not positive or if the list contains non-integer values.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a default configuration.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot number and the font size.
        - The subplot number should be an integer and can be -1 for a default setting.
        - The font size should be a positive integer.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `subplots_titles_font_size` is:
        - 12 (correct format)
        - [[0, 12]] (correct format)
        - [[0, 12], [1, 10], [-1, 8]] (correct format)
        - [[0, -1]] or [0, -1] (incorrect format)
        - [[0, 12, 14]] or [0, 12, 14] (incorrect format)
        - [[0, "12"]] or [0, "12"] (incorrect format)
        - [[-5, 10]] or [-5, 10] (incorrect format)

        This method will validate the provided font sizes and return a success message along with the validated font size configuration.

        Inspiration:
        ------------
        "Kukoriki" series, episode "The case of the missing rake".
        """
        text_that_explain_structure = '''The structure is [x, y] (x - number of subplot or -1 (for all subplots that aren't called), y - number - size of font for title for x subplot)'''
        if not isinstance(subplots_titles_font_size, (list, int)):
            raise TypeError(f"legends_font_size argument is incorrect. It should be a list with elements like [x, y] (x - number of subplot, y - number - size of font for title for x subplot) or one number for all titles fonts")
        if isinstance(subplots_titles_font_size, int):
            return (f"legend argument is correct", [[-1, subplots_titles_font_size]])
        elif isinstance(subplots_titles_font_size, list):
            for i in range(len(subplots_titles_font_size)):
                if not isinstance(subplots_titles_font_size[i], list):
                    raise TypeError(f'subplots_titles_font_size argument number {i} ({subplots_titles_font_size[i]}) should be list.' + text_that_explain_structure)
                elif len(subplots_titles_font_size[i]) != 2:
                    raise TypeError(f'subplots_titles_font_size argument number {i} ({subplots_titles_font_size[i]}) should have two elements. The structure is [x, y] (x - number of subplot, y - number - size of font for title for x subplot)')
                elif not isinstance(subplots_titles_font_size[i][0], int):
                    raise ValueError(f'subplots_titles_font_size argument number {i} ({subplots_titles_font_size[i][0]}) should be int.' + text_that_explain_structure)
                elif subplots_titles_font_size[i][0] < 0 and subplots_titles_font_size[i][0] != -1:
                    raise ValueError(f'subplots_titles_font_size argument number {i} ({subplots_titles_font_size[i][0]}) should be positive or -1.' + text_that_explain_structure)
                elif not isinstance(subplots_titles_font_size[i][1], int):
                    raise ValueError(f'subplots_titles_font_size argument number {i} ({subplots_titles_font_size[i][1]}) should be int.' + text_that_explain_structure)
                elif subplots_titles_font_size[i][1] < 1:
                    raise ValueError(f'subplots_titles_font_size argument number {i} ({subplots_titles_font_size[i][1]}) should be more than 0.' + text_that_explain_structure)
            return (f"subplots_titles_font_size argument is correct.", subplots_titles_font_size)
        
    def __check_subplots_titles_text(self, subplots_titles_text):
        """
        Validate the titles for subplots.

        This function ensures that subplot titles are provided either as a single string
        for all plots or as a list of strings for individual plot titles.

        Arguments:
        ----------
        subplots_titles_text : str or list of str
            A string for a uniform title or a list of strings for varied titles.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the list of validated titles.

        Raises:
        -------
        TypeError
            If subplots_titles_text is not a string or list of strings.
        ValueError
            If any element in the list is not a string.

        Notes:
        ------
        - The method first checks if the input is a string or a list.
        - For a single string, it validates the format and returns a list containing the string.
        - For a list, it iterates through each element and validates the format.
        - If any element in the list is not a string, a ValueError is raised.
        - If the input is not a string or a list of strings, a TypeError is raised.

        Example:
        --------
        Assuming `subplots_titles_text` is:
        - "Main Title" (correct format)
        - ["Title 1", "Title 2"] (correct format)
        - ["Title 1", 123] (incorrect format)
        - 123 (incorrect format)

        This method will validate the provided titles and return a confirmation message along with the validated titles.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        if not isinstance(subplots_titles_text, (list, str)):
            raise TypeError(f"subplots_titles_text argument is incorrect. It should be a list with string elements which are subplots titles or one string for all plots.")
        if isinstance(subplots_titles_text, str):
            return (f"subplots_titles_text argument is correct.", [subplots_titles_text])
        elif isinstance(subplots_titles_text, list):
            for i in range(len(subplots_titles_text)):
                if not isinstance(subplots_titles_text[i], str):
                    raise ValueError(f"subplots_titles_text argument {i} ({subplots_titles_text[i]}) should be a string.")
            return (f"subplots_titles_text argument is correct.", subplots_titles_text)
        
    def __check_legends_font_size(self, legends_font_size):
        """
        Validate the font size for legends in subplots.

        Checks if the legend font size is either a single number for all legends or
        a list specifying font sizes for legends in individual subplots with the format [subplot_number, font_size].

        Arguments:
        ----------
        legends_font_size : int or list
            An integer for uniform legend font size or a list for customized sizes per subplot.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated legend font size configuration.

        Raises:
        -------
        TypeError
            If legends_font_size or its elements are not in the expected format.
        ValueError
            If the structure or values within legends_font_size are incorrect or invalid.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a default configuration.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot number and the font size.
        - The subplot number should be an integer and can be -1 for a default setting.
        - The font size should be a positive integer.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `legends_font_size` is:
        - 12 (correct format)
        - [[0, 12]], or [[-1, 12]], or [[0, 12], [1, 10], [-1, 8]](correct format)
        - [0, -1]  or [[0, -1]](incorrect format)
        - [0, 12, 14] or  [[0, 12, 14]] (incorrect format)
        - [0, "12"] or [[0, "12"]] (incorrect format)
        - [-4, 12] or [[-4, 12]] (incorrect format)

        This method will validate the provided font sizes and return a success message along with the validated legend font size configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        text_that_explain_structure = '''The structure is [x, y] (x - number of subplot or -1 (for all subplots that aren't called), y - number - size of font for legend for x subplot)'''
        if not isinstance(legends_font_size, (list, int)):
            raise TypeError(f"legends_font_size argument is incorrect." + text_that_explain_structure)
        if isinstance(legends_font_size, int):
            return (f"legend argument is correct", [[-1, legends_font_size]])
        elif isinstance(legends_font_size, list):
            for i in range(len(legends_font_size)):
                if not isinstance(legends_font_size[i], list):
                    raise TypeError(f'legends_font_size argument number {i} ({legends_font_size[i]}) should be list.' + text_that_explain_structure)
                elif len(legends_font_size[i]) != 2:
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i]}) should have two elements.' + text_that_explain_structure)
                elif not isinstance(legends_font_size[i][0], int):
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i][0]}) should be int.' + text_that_explain_structure)
                elif legends_font_size[i][0] < 0 and legends_font_size[i][0] != -1:
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i][0]}) should be positive or -1.' + text_that_explain_structure)
                elif not isinstance(legends_font_size[i][1], int):
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i][1]}) should int.' + text_that_explain_structure)
                elif legends_font_size[i][1] < 1:
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i][1]}) should be more than zero.' + text_that_explain_structure)
            return (f"legends_font_size argument is correct.", legends_font_size)
        
    def __check_marker_size(self, marker_size):
        """
        Validate the size of markers for plotting.

        Ensures that marker sizes are provided as either a single positive integer
        for all data points or a list of positive integers for individual marker sizes.

        Arguments:
        ----------
        marker_size : int or list of int
            An integer for uniform marker size or a list of integers for varied sizes.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated marker sizes.

        Raises:
        -------
        TypeError
            If marker_size is not an integer or list of integers.
        ValueError
            If any marker size provided is not positive or if the list contains non-integer values.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a list containing the integer.
        - For a list, it iterates through each element and validates the format.
        - If any element in the list is not a positive integer, a ValueError is raised.
        - If the input is not an integer or a list of integers, a TypeError is raised.

        Example:
        --------
        Assuming `marker_size` is:
        - 10 (correct format)
        - [5, 10, 15] (correct format)
        - [5, -10, 15] (incorrect format)
        - [5, 10, 0] (incorrect format)
        - [5, "10", 15] (incorrect format)
        - "10" (incorrect format)

        This method will validate the provided marker sizes and return a success message along with the validated marker sizes.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """       
        if not isinstance(marker_size, (int, list)):
            raise TypeError(f'marker_size argument is incorrect. It should be a list with integer elements which are markers size or one integer for all data.')
        if isinstance(marker_size, int):
            if marker_size > 0:
                return (f"marker_size argument is correct.", [marker_size])
            else:
                raise ValueError(f"marker_size argument should be more than 0.")
        elif isinstance(marker_size, list):
            for i in range(len(marker_size)):
                if not isinstance(marker_size[i], int):
                    raise ValueError(f"marker_size argument {i} ({marker_size[i]}) should be an integer.")
                elif marker_size[i] < 1:
                    raise ValueError(f"marker_size argument {i} ({marker_size[i]}) should be more than 0.")
            return (f"marker_size argument is correct.", marker_size)
        
    def __check_line_width(self, line_width):
        """
        Validate the width of lines for plotting.

        Checks if line widths are provided as a single positive float or int for all lines or
        a list of positive floats or ints for individual line widths.

        Arguments:
        ----------
        line_width : float, int, or list of float, int
            A float for uniform line width or a list of floats for varied widths.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated line widths.

        Raises:
        -------
        TypeError
            If line_width is not a float, int, or list of floats, ints.
        ValueError
            If any line width provided is not positive or if the list contains non-float, non-int values.

        Notes:
        ------
        - The method first checks if the input is a float, int, or a list.
        - For a single float or int, it validates the format and returns a list containing the value.
        - For a list, it iterates through each element and validates the format.
        - If any element in the list is not a positive float or int, a ValueError is raised.
        - If the input is not a float, int, or a list of floats, ints, a TypeError is raised.

        Example:
        --------
        Assuming `line_width` is:
        - 2.5 (correct format)
        - [0.5, 1, 1.8] (correct format)
        - [0.5, -1.2, 1.8] (incorrect format)
        - [0.5, "1.2", 1.8] (incorrect format)
        - "2.5" (incorrect format)

        This method will validate the provided line widths and return a success message along with the validated line widths.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        if not isinstance(line_width, (float, int, list)):
            raise TypeError(f'line_width argument is incorrect. It should be a list width float (int) elements which are line width or one float number for all data.')
        if isinstance(line_width, (float, int)):
            if line_width > 0:
                return (f"line_width argument is correct.", [line_width])
            else:
                raise ValueError(f"line_width argument should be more than 0.")
        elif isinstance(line_width, list):
            for i in range(len(line_width)):
                if not isinstance(line_width[i], (float, int)):
                    raise ValueError(f"line_width argument {i} ({line_width[i]}) should be a float (int).")
                elif line_width[i] < 0:
                    raise ValueError(f"line_width argument {i} ({line_width[i]}) should be more than 0.")
            return (f"line_width argument is correct.", line_width)
        
    def __check_line_alpha(self, alpha):
        """
        Validate the alpha (transparency) values for lines in plotting.

        Ensures that alpha values are provided as either a single float/int between 0 and 1
        for uniform transparency or a list of floats/ints for individual line transparencies.

        Arguments:
        ----------
        alpha : float, int, or list of float, int
            A float/int or list of floats/ints representing line transparency (0.0 to 1.0).

        Returns:
        -------
        tuple
            A tuple with a success message and the validated alpha value(s).

        Raises:
        -------
        TypeError
            If alpha is not a float, int, or list of these types.
        ValueError
            If any alpha value is not within the range of 0 to 1.

        Notes:
        ------
        - The method first checks if the input is a float, int, or a list.
        - For a single float or int, it validates the format and returns a list containing the value.
        - For a list, it iterates through each element and validates the format.
        - If any element in the list is not a float or int within the range of 0 to 1, a ValueError is raised.
        - If the input is not a float, int, or a list of floats, ints, a TypeError is raised.

        Example:
        --------
        Assuming `alpha` is:
        - 0.5 (correct format)
        - [0.2, 0.5, 0.8] (correct format)
        - [0.2, 0.5, 1] (correct format)
        - [0.2, -0.5, 0.8] (incorrect format)
        - [0.2, "0.5", 0.8] (incorrect format)
        - "0.5" (incorrect format)

        This method will validate the provided alpha values and return a success message along with the validated alpha values.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        if not isinstance(alpha, (float, int, list)):
            raise TypeError(f'alpha argument is incorrect. It should be a list width float (int) elements from 0 to 1 which are line transparency or one float (int) number for all data.')
        if isinstance(alpha, (float, int)):
            if alpha > 0:
                return (f"alpha argument is correct.", [alpha])
            else:
                raise ValueError(f"alpha argument should be more than 0.")
        elif isinstance(alpha, list):
            for i in range(len(alpha)):
                if not isinstance(alpha[i], (float, int)):
                    raise ValueError(f"alpha argument {i} ({alpha[i]}) should be a float (int) from 0 to 1.")
                elif alpha[i] < 0 or alpha[i] > 1:
                    raise ValueError(f"alpha argument {i} ({alpha[i]}) should be from 0 to 1.")
            return (f"alpha argument is correct.", alpha)
        
    def __check_axes_round_accuracy(self, axes_round_accuracy):
        """
        Validate the rounding accuracy for axes labels.

        Checks if the rounding accuracy for axes labels is provided as either a string
        for uniform rounding or a list specifying rounding in individual subplots with the format [subplot_number, [axes_round_accuracy_x_axes, axes_round_accuracy_x_axes]]

        Arguments:
        ----------
        axes_round_accuracy : str or list
            A string for uniform rounding or a list for customized rounding per subplot.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated rounding configuration.

        Raises:
        -------
        TypeError
            If axes_round_accuracy or its elements are not in the expected format.
        ValueError
            If the structure or values within axes_round_accuracy are incorrect.

        Notes:
        ------
        - The method first checks if the input is a string or a list.
        - For a single string, it validates the format and returns a default configuration.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot number and a list of rounding strings.
        - The subplot number should be an integer and can be -1 for a default setting.
        - The list of rounding strings should contain two strings, each representing the rounding format.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `axes_round_accuracy` is:
        - "%0.2f" (correct format)
        - [[0, ["%0.2f", "%0.3f"]]], or  [[0, ["%0.2f", "%0.3f"]], [2, ["%0.2f", "%0.2f"]]], or [[0, ["%0.1f", "%0.1f"]], [-1, ["%0.1f", "%0.1f"]]] (correct format)
        - [0, ["%0.2f"]], or [[0, ["%0.2f"]]] (incorrect format)
        - [0, "%0.2f"], or [[0, "%0.2f"]], or [0, "%0.2f", "%0.2f"], or [[0, "%0.2f", "%0.2f"], [2, ["%0.2f", "%0.2f"]]](incorrect format)
        - [0, ["%0.2f", 0.3]] (incorrect format)

        This method will validate the provided rounding accuracy and return a success message along with the validated rounding configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        text_to_explain_structure = '''The structure is [x, [y, y]] (x - number of subplot, y - string like "%0.xf", where x shows to which decimal number should be rounded)'''
        if not isinstance(axes_round_accuracy, (list, str)):
            raise TypeError(f"axes_round_accuracy argument is incorrect." + text_to_explain_structure +  " or one number for all axes fonts")
        if isinstance(axes_round_accuracy, str):
            if not all([axes_round_accuracy[0] == '%' and axes_round_accuracy[1] == '0' and axes_round_accuracy[2] == '.']):
                    raise ValueError(f'axes_round_accuracy argument number should be presented like y - string like "%0.xf", where x shows to which decimal number should be rounded')
            return (f"axes_round_accuracy argument is correct", [[-1, [axes_round_accuracy, axes_round_accuracy]]])
        elif isinstance(axes_round_accuracy, list):
            for i in range(len(axes_round_accuracy)):
                if not isinstance(axes_round_accuracy[i], list):
                    raise TypeError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i][0]}) should be a list.' + text_to_explain_structure)
                elif len(axes_round_accuracy[i]) != 2:
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should have two elements.' + text_to_explain_structure)                    
                elif not isinstance(axes_round_accuracy[i][0], int):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i][0]}) should be an integer.' + text_to_explain_structure)
                elif axes_round_accuracy[i][0] < 0 and axes_round_accuracy[i][0] != -1:
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i][0]}) should be positive or -1.' + text_to_explain_structure)
                elif not isinstance(axes_round_accuracy[i][1], list):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i][1]}) should be a list.' + text_to_explain_structure)
                elif len(axes_round_accuracy[i][1]) != 2:
                    raise ValueError(f'axes_font_size argument number {i} ({axes_round_accuracy[i][1]}) should have two elements.' + text_to_explain_structure)
                elif not (isinstance(axes_round_accuracy[i][1][0], str) and isinstance(axes_round_accuracy[i][1][1], str)):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should have strings as elements of the second element.' + text_to_explain_structure)
                elif not all([axes_round_accuracy[i][1][j][0] == '%' and axes_round_accuracy[i][1][j][1] == '0' and axes_round_accuracy[i][1][j][2] == '.' for j in range(2)]):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should be presented diffently.' + text_to_explain_structure)
            return (f"axes_round_accuracy argument is correct.", axes_round_accuracy)

    def __check_subplots_settings(self, subplots_settings):
        """
        Validate the settings for subplot configuration.

        Ensures that subplot settings are provided as a dictionary with specific keys
        for rows/columns configuration and subplot distribution.

        Arguments:
        ----------
        subplots_settings : list
            A list containing a dictionary with subplot configuration.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated subplot settings.

        Raises:
        -------
        TypeError
            If subplots_settings is not a dictionary or if its elements are not in the expected format.
        ValueError
            If required keys are missing or if the values do not match expected types or ranges.

        Notes:
        ------
        - The method first checks if the input is a list containing a dictionary.
        - It then validates the presence of required keys: "rows_cols", "subplots_distribution", and "figure_size".
        - For "rows_cols", it checks if the value is a list of two integers representing the number of rows and columns.
        - For "figure_size", it checks if the value is a list of two integers or floats representing the width and height of the figure.
        - For "subplots_distribution", it checks if the value is a list of integers, where each integer corresponds to the index of the subplot.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `subplots_settings` is:
        - [{"rows_cols": [2, 2], "figure_size": [10, 8], "subplots_distribution": [0, 1, 2, 3]}] (correct format)
        - [{"rows_cols": [1, 2], "figure_size": [10, 8], "subplots_distribution": [0, 1, 2, 3]}] (correct format)
        - [{"rows_cols": [2], "figure_size": [10, 8], "subplots_distribution": [0, 1, 2, 3]}] (incorrect format)
        - [{"rows_cols": [2, 2], "figure_size": [10], "subplots_distribution": [0, 1, 2, 3]}] (incorrect format)
        - [{"rows_cols": [2, 2], "figure_size": [10, 8], "subplots_distribution": [0, -1, 2, 3]}] (incorrect format)

        This method will validate the provided subplot settings and return a success message along with the validated subplot settings.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        subplots_settings = subplots_settings[0]
        if not isinstance(subplots_settings, dict):
            raise TypeError(f"subplots_settings should be dictionary.")
        if not ("rows_cols" in subplots_settings.keys()):
            raise ValueError(f"rows_cols should be a key in subplots_settings")
        elif not ("subplots_distribution" in subplots_settings.keys()):
            raise ValueError(f"subplots_distribution should be a key in subplots_settings")
        elif not ("figure_size" in subplots_settings.keys()):
            raise ValueError(f"figure_size should be a key in subplots_settings")
        
        elif not isinstance(subplots_settings["rows_cols"], list):
            raise ValueError(f"rows_cols should be a list with two integer elements: numbers of rows and number of columns in your subplot.")
        elif len(subplots_settings["rows_cols"]) != 2:
            raise ValueError(f"rows_cols should have two integer elements: numbers of rows and number of columns in your subplot.")
        elif not (isinstance(subplots_settings["rows_cols"][0], int) and isinstance(subplots_settings["rows_cols"][1], int)):
            raise ValueError(f"rows_cols elements should be integer: numbers of rows and number of columns in your subplot.")
        
        elif not isinstance(subplots_settings["figure_size"], list):
            raise ValueError(f"figure_size should be a list with two integer (float) elements: width and height of your figure.")
        elif len(subplots_settings["figure_size"]) != 2:
            raise ValueError(f"figure_size should have two integer (float) elements: width and height of your figure.")
        elif not (isinstance(subplots_settings["figure_size"][0], (int, float)) and isinstance(subplots_settings["figure_size"][1], (int, float))):
            raise ValueError(f"figure_size elements should be integer (float): width and height of your figure.")    
            
        elif not isinstance(subplots_settings["subplots_distribution"], list):
            raise ValueError(f"subplots_distribution should be a list with elements (0, 1, ... ). The index of the element responds to the index of the the data in your data_array, the value of the element responds to the index of the subplot.")
        elif isinstance(subplots_settings["subplots_distribution"], list):
            for i in range(len(subplots_settings["subplots_distribution"])):
                if not isinstance(subplots_settings["subplots_distribution"][i], int):
                    raise ValueError(f"subplots_distribution elements should be integer (problem with element {i} ({subplots_settings['subplots_distribution'][i]})).")
                elif subplots_settings["subplots_distribution"][i] < 0:
                    raise ValueError(f"subplots_distribution elements should be more than 0 (problem with element {i} ({subplots_settings['subplots_distribution'][i]})).")
        return (f"subplots_settings argument is correct", [subplots_settings])
    
    def __check_rows_cols(self, rows_cols):
        """
        Validate the rows and columns configuration for subplots.

        Ensures that the rows and columns configuration is provided as a list with two positive integers,
        where the first element represents the number of rows and the second element represents the number of columns.

        Arguments:
        ----------
        rows_cols : list
            A list containing two integers representing the number of rows and columns.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated rows and columns configuration.

        Raises:
        -------
        TypeError
            If rows_cols is not a list.
        ValueError
            If rows_cols does not have exactly two elements or if the elements are not positive integers.

        Notes:
        ------
        - The method first checks if the input is a list.
        - It then validates that the list contains exactly two elements.
        - Each element in the list should be a positive integer.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `rows_cols` is:
        - [2, 3] (correct format)
        - [2] (incorrect format)
        - [2, -1] or [-1, 2] (incorrect format)
        - [2, 0] or [0, 2] (incorrect format)
        - [2, "3"] (incorrect format)

        This method will validate the provided rows and columns configuration and return a success message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_to_explain_structure = ''' The structure is [x, y] where x is a number rows, y is number of cols on plot presented'''
        if not isinstance(rows_cols, list):
            raise TypeError(f"rows_cols argument should be list." + text_to_explain_structure)
        elif len(rows_cols) != 2:
            raise ValueError(f"rows_cols argument should have two elements (x, y)." + text_to_explain_structure)
        elif len(rows_cols) == 2:
            for j in range(2):
                if (not isinstance(rows_cols[j], int)) or (rows_cols[j] < 1):
                    raise ValueError(f"rows_cols {j} argument should be integer and positive." + text_to_explain_structure)
            return (f'rows_cols argument is correct. ', rows_cols)
        
    def __check_figure_size(self, figure_size):
        """
        Validate the size of the entire figure.

        Ensures that the figure size is provided as a list with two positive integers or floats,
        where the first element represents the width and the second element represents the height of the figure.

        Arguments:
        ----------
        figure_size : list
            A list containing two integers or floats representing the width and height of the figure.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated figure size configuration.

        Raises:
        -------
        TypeError
            If figure_size is not a list.
        ValueError
            If figure_size does not have exactly two elements or if the elements are not positive integers or floats.

        Notes:
        ------
        - The method first checks if the input is a list.
        - It then validates that the list contains exactly two elements.
        - Each element in the list should be a positive integer or float.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `figure_size` is:
        - [10, 8.5] (correct format)
        - [10] (incorrect format)
        - [10, -8] (incorrect format)
        - [10, "8"] (incorrect format)

        This method will validate the provided figure size configuration and return a success message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_to_explain_structure = ''' Structure is [x, y] where x is width, y is height of the entire figure (all subplots).'''
        if not isinstance(figure_size, list):
            raise TypeError(f"figure_size argument should be list." + text_to_explain_structure)
        elif len(figure_size) != 2:
            raise ValueError(f"figure_size argument should have two elements (x, y)." + text_to_explain_structure)
        elif len(figure_size) == 2:
            for j in range(2):
                if (not isinstance(figure_size[j], (int, float))) or (figure_size[j] < 1):
                    raise ValueError(f"figure_size {j} argument should be integer or float and positive." + text_to_explain_structure)
            return (f"figure_size argument is correct", figure_size)
        
    def __check_subplots_distribution(self, subplots_distribution):
        """
        Validate the distribution of data across subplots.

        Ensures that the subplot distribution is provided as either a single integer
        for all data or a list of integers specifying the subplot index for each data point.

        The structure is [x_0, x_1, x_2, ...] where x_j is a number of a subplot
        (counting from left to right from top to bottom, starting from 0).
        j represents the index of data from data_array. Or it can be one number (index of a subplot) for all data.

        Arguments:
        ----------
        subplots_distribution : int or list of int
            A single integer or a list of integers representing the subplot indices for data distribution.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated subplot distribution configuration.

        Raises:
        -------
        TypeError
            If subplots_distribution is not an integer or a list of integers.
        ValueError
            If any element in the list is not a positive integer.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a list containing the integer.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a positive integer.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `subplots_distribution` is:
        - 0 (correct format)
        - [0, 1, 2] (correct format)
        - [-1] (incorrect format)
        - [0, "1", 2] (incorrect format)
        - "0" (incorrect format)

        This method will validate the provided subplot distribution and return a success message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_to_explain_structure = ''' The structure is [x_0, x_1, x_2, ...] where x_j is a number of a subplot (counting from left to right from top to bottom, starting from 0). j represents the index of data from data_array. Or it can be one number (index of a subplot) for all data.'''
        if not isinstance(subplots_distribution, (list, int)):
            raise TypeError(f"subplots_distribution should be a list or integer." + text_to_explain_structure)
        if isinstance(subplots_distribution, int):
            if subplots_distribution < 0:
                raise TypeError(f"subplots_distribution should be positive." + text_to_explain_structure)
            return (f"subplots_distribution argument is correct", [subplots_distribution])
        elif isinstance(subplots_distribution, list):
            for i in range(len(subplots_distribution)):
                if not isinstance(subplots_distribution[i],  int):
                    raise TypeError(f"subplots_distribution {i} should be integer." + text_to_explain_structure)
                elif subplots_distribution[i] < 0:
                    raise ValueError(f"subplots_distribution {i} should be positive (>= 0)." + text_to_explain_structure)
            return (f"subplots_distribution argument is correct", subplots_distribution)
        
    def __check_graph_types(self, graph_types):
        """
        Validate the type of graph for plotting.

        Checks if the graph type is either a single string or a list of strings representing
        whether the graph should be 2D or 3D.

        Arguments:
        ----------
        graph_types : str or list of str
            A string or list of strings indicating graph types ('2D' or '3D').

        Returns:
        -------
        tuple
            A tuple with a success message and the validated graph type(s).

        Raises:
        -------
        TypeError
            If graph_types is not a string or list of strings.
        ValueError
            If any graph type provided is not '2D' or '3D'.

        Notes:
        ------
        - The method first checks if the input is a string or a list.
        - For a single string, it validates the format and returns a list containing the string.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a string representing either '2D' or '3D'.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `graph_types` is:
        - "2D" (correct format)
        - ["2D", "3D"] (correct format)
        - ["2D", "4D"] (incorrect format)
        - ["2D", 3] (incorrect format)
        - 2 (incorrect format)

        This method will validate the provided graph types and return a success message along with the validated graph types.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        graph_pos_types = ["2D", "3D"]
        if not isinstance(graph_types, (list, str)):
            raise TypeError(f"graph_types argument is incorrect. It should be a list with graph_types as string or one graph_types type as string for all data. (Possible graph_types are \"2D\", \"3D\")")
        if isinstance(graph_types, str):
            if graph_types in graph_pos_types:
                return (f"graph_types argument is correct", [graph_types])
            else:
                raise ValueError(f"graph_type argument is incorrect. (Possible graph_types are \"2D\", \"3D\")")
        elif isinstance(graph_types, list):
            for i in range(len(graph_types)):
                if not isinstance(graph_types, (list, str)):
                    raise TypeError(f"graph_types argument {i} ({graph_types[i]}) is incorrect. It should be a list with graph_types as string or one graph_types type as string for all data. (Possible graph_types are \"2D\", \"3D\")")
                if isinstance(graph_types, str):
                    if graph_types in graph_pos_types:
                        return (f"graph_types argument  {i} ({graph_types[i]}) is correct", [graph_types])
                    else:
                        raise ValueError(f"graph_type argument {i} ({graph_types[i]}) is incorrect. (Possible graph_types are \"2D\", \"3D\")")
            return (f"graph_types argument is correct", graph_types)
        
    def __check_axes_scaling(self, axes_scaling):
        """
        Validate the scaling options for plot axes.

        This function checks if the axes scaling configuration is correctly formatted.
        It supports two types of scaling: 'stretch' for proportional scaling, and 'divide' for custom tick spacing.

        Arguments:
        ----------
        axes_scaling : list
            A list where each element describes the scaling for one subplot.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated axes_scaling configuration.

        Raises:
        -------
        TypeError
            If axes_scaling is not a list or if its elements are not structured as expected.
        ValueError
            If the structure or values within axes_scaling do not match the defined format.

        Notes:
        ------
        - The method first checks if the input is a list.
        - It then iterates through each element and validates the format.
        - Each element in the list should be a list of three elements:
            - The first element is an integer representing the subplot index.
            - The second element is a string representing the scaling type ("stretch" or "divide").
            - The third element is a list representing the scaling parameters (XY).
        - For "stretch", XY should be a list of four floats or integers.
        - For "divide", XY should be a list of two lists, each containing three elements: two floats or integers and one integer.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `axes_scaling` is:
        - [[0, "stretch", [0.5, 1.5, 0.5, 1.5]]] or [[0, "stretch", [0.5, 1.5, 0.5, 1.5]], [1, "stretch", [0.8, 1.1, 0.9, 1.2]], [-1, "stretch", [0.5, 1.5, 0.5, 1.5]]] (correct format)
        - [[0, "divide", [[0.5, 1.5, 5], [0.5, 1.5, 5]]]] or [[0, "divide", [[0.5, 1.5, 5], [0.5, 1.5, 5]]], [2, "divide", [[-0.5, 1.5, 5], [0, 1.5, 5]]], [-1, "divide", [[-0.5, 1.5, 5], [0, 1.5, 5]]]] (correct format)
        - [[0, "divide", [[0.5, 1.5, 5], [0.5, 1.5, 5]]], [-1, "stretch", [0.5, 1.5, 0.5, 1.5]]] (correct format)    
        - [[0, "stretch", [0.5, 1.5]]] (incorrect format)
        - [[0, "divide", [0.5, 1.5, 5]]] (incorrect format)
        - [[0, "stretch", [0.5, "1.5", 0.5, 1.5]]] (incorrect format)

        This method will validate the provided axes scaling configuration and return a success message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_for_explaining_structure = ''' The structure of the element is [n, x, XY], where n is a number of a subplot, x can be \"stretch\" or \"divide\". If an option is \"stretch\" then XY=[x1, x2, y1, y2], 
                where x1(y1) / x2(y2) is number that minimal / maximal x(y) value of data on the subplot will be multiplied by.
                If an option is \"divide\" then XY = [[x1, x2, nx], [y1, y2, ny]], where x1(y1) / x2(y2) is a minimal / maximal number in x(y) axes,
                nx(ny) is number of tiks in x(y) axes (ticks for minimal and maximal numbers is included). '''
        if not isinstance(axes_scaling, list):
            raise TypeError(f"axes_scaling should be a list with elements." + text_for_explaining_structure)
        elif isinstance(axes_scaling, list):
            for i in range(len(axes_scaling)):
                if not isinstance(axes_scaling[i], list):
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i]}) should a list." + text_for_explaining_structure)
                elif len(axes_scaling[i]) != 3:
                    raise ValueError(f"axes_scaling don't have enough elements (or there are too many of them)." + text_for_explaining_structure)
                elif not isinstance(axes_scaling[i][0], int):
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][0]}) should be int." + text_for_explaining_structure)
                elif axes_scaling[i][0] < 0 and axes_scaling[i][0] != -1:
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][0]}) should be positive or -1." + text_for_explaining_structure)
                elif not (isinstance(axes_scaling[i][1], str) and axes_scaling[i][1] in ["stretch", "divide"]):
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1]}) should be a string. Possible options are \"stretch\" or \"divide\"." + text_for_explaining_structure)
                elif not isinstance(axes_scaling[i][2], list):
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][2]}) should be a list with structure of XY." + text_for_explaining_structure)
                elif axes_scaling[i][1] == "stretch" and len(axes_scaling[i][2]) != 4:
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][2]}) should be a list with four float coefficients." + text_for_explaining_structure)
                elif axes_scaling[i][1] == "stretch" and len(axes_scaling[i][2]) == 4:
                    for j in range(4):
                        if not isinstance(axes_scaling[i][2][j], (int, float)):
                            raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][2][j]}) should be a float or integer number." + text_for_explaining_structure)
                elif axes_scaling[i][1] == "divide" and len(axes_scaling[i][2]) == 2:
                    if not all([(isinstance(axes_scaling[i][2][j], list)) for j in range(2)]):
                        raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][2][j]}) should be a list." + text_for_explaining_structure)
                    elif all([(isinstance(axes_scaling[i][2][j], list)) for j in range(2)]):
                        for j in range(2):
                            if len(axes_scaling[i][2][j]) != 3:
                                raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][2][j]}) should have lenght 3, see structure." + text_for_explaining_structure)
                            elif not all([isinstance(axes_scaling[i][2][j][k], (int, float)) for k in range(2)]):
                                raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][2][j]}) should have integer or float edge numbers, see structure." + text_for_explaining_structure)
                            elif not (isinstance(axes_scaling[i][2][j][2], int) and axes_scaling[i][2][j][2] > 1):
                                raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][2][j]}) should have integer numbers of ticks and these numbers should be more or equal than 2, see structure." + text_for_explaining_structure)
            return (f"axes_scaling argument is correct", axes_scaling)
        
    def __check_axes_number_of_small_ticks(self, axes_number_of_small_ticks):
        """
        Validate the number of small ticks between major ticks on axes.

        Ensures that the number of small ticks provided is either a uniform integer for all axes or
        a list specifying the number for X and Y axes per subplot.

        Arguments:
        ----------
        axes_number_of_small_ticks : int or list
            An integer or a list of lists [x, y] where x and y are integers.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated configuration.

        Raises:
        -------
        TypeError
            If axes_number_of_small_ticks is not an integer or list, or contains non-integer values.
        ValueError
            If any number of small ticks is less than 1 or if the list structure is incorrect.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a default configuration.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot index and a list of integers representing the number of small ticks for X and Y axes.
        - The subplot index should be an integer and can be -1 for a default setting.
        - The list of integers should contain two positive integers.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `axes_number_of_small_ticks` is:
        - 5 (correct format)
        - [[0, [3, 4]], [1, [2, 5]]] (correct format)
        - [[0, [3]], [1, [2, 5]]] (incorrect format)
        - [[0, [3, 4]], [1, [2, -1]]] (incorrect format)
        - [[0, [3, 4]], [1, ["2", 5]]] (incorrect format)

        This method will validate the provided number of small ticks and return a success message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify. (Sia, Diplo, Labrinth, LSD "Genius"; Normal Tale "Кисточка")
        """

        text_that_explains_structure = ''' The structure of one element of the list is [n, [x, y]] where n - index of subplot, x(y) is a number of small ticks in X(Y) axes between two big ticks. x(y) >= 1. The number of tikcs between two big is equal to x(y) - 1.'''

        if not isinstance(axes_number_of_small_ticks, (list, int)):
            raise TypeError(f"axes_number_of_small_ticks should be presented as list of elements (see structure) or one number for all subplots and axes." + text_that_explains_structure)
        if isinstance(axes_number_of_small_ticks, int):
            return (f"axes_font_size argument is correct", [[-1, [axes_number_of_small_ticks, axes_number_of_small_ticks]]])
        elif isinstance(axes_number_of_small_ticks, list):
            for i in range(len(axes_number_of_small_ticks)):
                if not isinstance(axes_number_of_small_ticks[i], list):
                    raise TypeError(f'axes_number_of_small_ticks argument number {i} ({axes_number_of_small_ticks[i]}) should be list.' + text_that_explains_structure)
                elif len(axes_number_of_small_ticks[i]) != 2:
                    raise ValueError(f'axes_number_of_small_ticks argument number {i} ({axes_number_of_small_ticks[i]}) should have two elements.' + text_that_explains_structure)
                elif not isinstance(axes_number_of_small_ticks[i][0], int):
                    raise ValueError(f'axes_number_of_small_ticks argument number {i} ({axes_number_of_small_ticks[i][0]}) should be int.' + text_that_explains_structure)
                elif axes_number_of_small_ticks[i][0] < 0 and axes_number_of_small_ticks[i][0] != -1:
                    raise ValueError(f'axes_number_of_small_ticks argument number {i} ({axes_number_of_small_ticks[i][0]}) should be positive or -1.' + text_that_explains_structure)
                elif not isinstance(axes_number_of_small_ticks[i][1], list):
                    raise ValueError(f'axes_number_of_small_ticks argument number {i} ({axes_number_of_small_ticks[i][1]}) should be list.' + text_that_explains_structure)
                elif len(axes_number_of_small_ticks[i][1]) != 2:
                    raise ValueError(f'axes_number_of_small_ticks argument number {i} ({axes_number_of_small_ticks[i][1]}) should have two elements.' + text_that_explains_structure)
                elif len(axes_number_of_small_ticks[i][1]) == 2:
                    for j in range(2):
                        if not isinstance(axes_number_of_small_ticks[i][1][j], int):
                            raise ValueError(f"axes_number_of_small_ticks element {i} ({axes_number_of_small_ticks[i][1][j]}) should be an integer number." + text_that_explains_structure)
                        elif axes_number_of_small_ticks[i][1][j] < 1:
                            raise ValueError(f"axes_number_of_small_ticks element {i} ({axes_number_of_small_ticks[i][1][j]}) should be at least 1." + text_that_explains_structure)   
            return (f"axes_font_size argument is correct.", axes_number_of_small_ticks)
        
    def __check_labels(self, labels):
        """
        Validate the labels for data series in the plot.

        Checks if labels are provided as a single string for all data or a list of strings for individual data series.

        Arguments:
        ----------
        labels : str or list of str
            A string or list of strings representing labels for data series.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated labels.

        Raises:
        -------
        TypeError
            If labels is neither a string nor a list of strings.

        Notes:
        ------
        - The method first checks if the input is a string or a list.
        - For a single string, it validates the format and returns a list containing the string.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a string.
        - If any element does not match the expected format, a TypeError is raised.

        Example:
        --------
        Assuming `labels` is:
        - "Main Label" (correct format)
        - ["Label 1", "Label 2"] (correct format)
        - ["Label 1", 123] (incorrect format)
        - 123 (incorrect format)

        This method will validate the provided labels and return a confirmation message along with the validated labels.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if not isinstance(labels, (list, str)):
            raise TypeError(f"labels should be a list with strings(labels) or one string for all data.")
        if isinstance(labels, str):
            return (f"labels argument is correct", [labels])
        elif isinstance(labels, list):
            for i in range(len(labels)):
                if not isinstance(labels[i], str):
                    raise TypeError(f"labels element {i} ({labels[i]}) should be a list with strings(labels).")
            return  (f"labels argument is correct", labels)
        
    def __check_axes_titles(self, axes_titles):
        """
        Validate titles for axes in subplots.

        Ensures that axes titles are provided either as a single string for all axes or
        as a list where each element is a list containing strings for X and Y axis titles.
        If subplot has colorbar the third element of the list containing strings for X and Y axis titles
        also contain cbar title.

        Arguments:
        ----------
        axes_titles : str or list
            A string or list where each element is a list of two strings for axis titles.

        Returns:
        -------
        tuple
            A tuple with a success message and the validated axes titles configuration.

        Raises:
        -------
        TypeError
            If axes_titles is not a string or list.
        ValueError
            If the structure within the list does not match the expected format.

        Notes:
        ------
        - The method first checks if the input is a string or a list.
        - For a single string, it validates the format and returns a list containing the string.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two or three strings representing the X, Y, and optionally the colorbar axis titles.
        - If any element does not match the expected format, a ValueError is raised.

        Example:
        --------
        Assuming `axes_titles` is:
        - "Main Title" (correct format)
        - [["X-axis", "Y-axis"], ["X-axis", "Y-axis", "Colorbar"]] (correct format)
        - [["X-axis", "Y-axis"], ["X-axis", 123]] (incorrect format)
        - [["X-axis", "Y-axis"], ["X-axis"]] (incorrect format)
        - 123 (incorrect format)

        This method will validate the provided axes titles and return a success message along with the validated axes titles configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if not isinstance(axes_titles, (list, str)):
            raise TypeError(f"axes_titles should be a list, where each element is a list [\"X\", \"Y\"], \"X\"(\"Y\") ([\"X\", \"Y\", \"B\"])- titles for axes (\"B\" - title for barchart). Index of the element is relevant to the index of the plot is the same as the index of each list.")
        if isinstance(axes_titles, str):
            return (f"axes_titles argument is correct.", [[axes_titles, axes_titles]])
        elif isinstance(axes_titles, list):
            for i in range(len(axes_titles)):
                if not isinstance(axes_titles[i], list):
                    raise ValueError(f"axes_titles element {i} ({axes_titles[i]}) should be a list, where each element is a list [\"X\", \"Y\"], \"X\"(\"Y\") ([\"X\", \"Y\", \"B\"])- titles for axes (\"B\" - title for barchart). Index of the element is relevant to the index of the plot is the same as the index of each list.")
                elif not (len(axes_titles[i]) in [2, 3]):
                    raise ValueError(f"axes_titles element {i} ({axes_titles[i]}) should have two or three strings elements (titles for axes) [if ypu have 3d option for a graph third title if for colorbar].")
                for j in range(len(axes_titles[i])):
                    if not isinstance(axes_titles[i][j], str):
                        raise ValueError(f"axes_titles element {i} ({axes_titles[i][j]}) should be a string.")
            return (f"axes_titles argument is correct.", axes_titles)
    
    def __check_subplots_legend_position(self, subplots_legend_position):
        """
        Validate the position of legends in subplots.

        Checks if the legend position is provided as a single string for all plots or
        a list of strings for individual subplot legend positions. Adds validation for
        acceptable legend position strings. If legend position is for all subplots index is equal to -1.

        Arguments:
        ----------
        subplots_legend_position : str or list of str
            A string or list of strings representing legend positions.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated legend positions.

        Raises:
        -------
        TypeError
            If subplots_legend_position is not a string or list of strings.
        ValueError
            If any legend position string is not among the recognized positions.

        Notes:
        ------
        - The method first checks if the input is a string or a list.
        - For a single string, it validates the format and returns a list containing the string.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot index and a string representing the legend position.
        - The subplot index should be an integer and can be -1 for a default setting.
        - The legend position string should be one of the recognized positions.
        - If any element does not match the expected format, a TypeError or ValueError is raised.
        - Possible legend positions include:
            o 'best'
            o 'upper right', 'upper left', 'lower left', 'lower right'
            o 'right', 'center left', 'center right'
            o 'lower center', 'upper center', 'center'
            o 'outside' (interpreted as 'center right' for placement outside the plot)

        Example:
        --------
        Assuming `subplots_legend_position` is:
        - "upper right" (correct format)
        - [[0, "upper right"], [1, "lower left"], [-1, "best"]] (correct format)
        - [[0, "upper right"], [1, "invalid"]] (incorrect format)
        - [[0, "upper right"], [1, 123]] (incorrect format)
        - [[-4, "upper right"], [1, 123]] (incorrect format)
        - 123 (incorrect format)

        This method will validate the provided legend positions and return a success message along with the validated legend positions.

        Inspiration:
        ------------
        "Kukoriki" series, episode "Mr. Window Dresser".
        """

        text_that_explains_structure = "The structure of each elements is [x, y], where x is number of subplot or -1 for all subplots (that are not called), y - position for legend. Valid options: 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'lower center', 'upper center', 'center', 'outside' (interpreted as 'center right' for placement outside the plot)."
        valid_positions = ['best', 'upper right', 'upper left', 'lower left', 'lower right', 
                           'right', 'center left', 'center right', 'lower center', 
                           'upper center', 'center', 'outside']
        
        if not isinstance(subplots_legend_position, (list, str)):
            raise TypeError(f"subplots_legend_position should be a list with strings(subplots legend position) or one string for all data.")
        if isinstance(subplots_legend_position, str):
            if subplots_legend_position == 'outside':
                subplots_legend_position = 'center right'  # Adjust 'outside' to a valid matplotlib position
            if subplots_legend_position not in valid_positions:
                raise ValueError(f"Legend position '{subplots_legend_position}' is not recognized. Use one of {valid_positions}")
            return (f"subplots_legend_position argument is correct", [[-1, subplots_legend_position]])
        
        elif isinstance(subplots_legend_position, list):
            for i in range(len(subplots_legend_position)):
                if not isinstance(subplots_legend_position[i], list):
                    raise TypeError(f'subplots_legend_position argument number {i} ({subplots_legend_position[i]}) should be list.' + text_that_explains_structure)
                elif len(subplots_legend_position[i]) != 2:
                    raise ValueError(f'subplots_legend_position argument number {i} ({subplots_legend_position[i]}) should have two elements.' + text_that_explains_structure)
                elif not isinstance(subplots_legend_position[i][0], int):
                    raise ValueError(f'subplots_legend_position argument number {i} ({subplots_legend_position[i][0]}) should be int.' + text_that_explains_structure)
                elif subplots_legend_position[i][0] < 0 and subplots_legend_position[i][0] != -1:
                    raise ValueError(f'subplots_legend_position argument number {i} ({subplots_legend_position[i][0]}) should be positive or -1.' + text_that_explains_structure)
                elif not isinstance(subplots_legend_position[i][1], str):
                    raise ValueError(f'subplots_legend_position argument number {i} ({subplots_legend_position[i][1]}) should string.' + text_that_explains_structure)
                elif isinstance(subplots_legend_position[i][1], str):
                    if subplots_legend_position[i][1] == 'outside':
                        subplots_legend_position[i][1] = 'center right'  # Adjust 'outside' to a valid matplotlib position
                    if subplots_legend_position[i][1] not in valid_positions:
                        raise ValueError(f"Legend position '{subplots_legend_position[i][1]}' at index {i} is not recognized. Use one of {valid_positions}")
            return (f"subplots_legend_position argument is correct.", subplots_legend_position)
        
    def __check_logarithmic_scaling(self, logarithmic_scaling):
        """
        Validate the logarithmic scaling configuration for plot axes.

        Checks if the logarithmic scaling configuration is provided as a single integer for all axes or
        a list specifying the scaling for individual subplots. If logarithmic scaling is for all subplots index is equal to -1.

        Arguments:
        ----------
        logarithmic_scaling : int or list
            An integer (0 or 1) for uniform scaling or a list where each element is a list containing the subplot index and a list of two integers (0 or 1) representing the scaling for X and Y axes.
            0 means normal scsaling, 1 means logarithmic scaling.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated logarithmic scaling configuration.

        Raises:
        -------
        TypeError
            If logarithmic_scaling is not an integer or list.
        ValueError
            If the structure or values within logarithmic_scaling do not match the expected format.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a default configuration.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot index and a list of two integers (0 or 1) representing the scaling for X and Y axes.
        - The subplot index should be an integer and can be -1 for a default setting.
        - The list of integers should contain two integers (0 or 1).
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `logarithmic_scaling` is:
        - 1 (correct format)
        - [[0, [1, 0]], [1, [0, 1]], [-1, [0, 0]]] (correct format)
        - [[0, [1]], [1, [0, 1]]] (incorrect format)
        - [[0, [1, 0]], [1, [0, 2]]] (incorrect format)
        - [[0, [1, 0]], [1, "0, 1"]] (incorrect format)

        This method will validate the provided logarithmic scaling configuration and return a success message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        text_that_explain_structure = '''The structure of one element is [x, [y, y]] (x - number of subplot, y - number - 0 or 1 (0 - normal scaling, 1 - logarithmic scaling))'''
        if not isinstance(logarithmic_scaling, (list, int)):
            raise TypeError(f"logarithmic_scaling argument is incorrect." + text_that_explain_structure + " or one number (0 / 1) for all axes.")
        if isinstance(logarithmic_scaling, int):
            return (f"logarithmic_scaling argument is correct", [[-1, [logarithmic_scaling, logarithmic_scaling]]])
        elif isinstance(logarithmic_scaling, list):
            for i in range(len(logarithmic_scaling)):
                if not isinstance(logarithmic_scaling[i], list):
                    raise TypeError(f'logarithmic_scaling argument number {i} ({logarithmic_scaling[i]}) should be list.' + text_that_explain_structure)
                elif not isinstance(logarithmic_scaling[i][0], int):
                    raise ValueError(f'logarithmic_scaling argument number {i} ({logarithmic_scaling[i][0]}) should be int.' + text_that_explain_structure)
                elif not isinstance(logarithmic_scaling[i][1], list):
                    raise ValueError(f'logarithmic_scaling argument number {i} ({logarithmic_scaling[i][1]}) should be list.' + text_that_explain_structure)
                elif len(logarithmic_scaling[i][1]) != 2:
                    raise ValueError(f'logarithmic_scaling argument number {i} ({logarithmic_scaling[i][1]}) should have two elements.' + text_that_explain_structure)
                elif not ((logarithmic_scaling[i][1][0] in [0, 1]) and (logarithmic_scaling[i][1][1] in [0, 1])):
                    raise ValueError(f'logarithmic_scaling argument number {i} ({logarithmic_scaling[i][1]}) should be 0 or 1.' + text_that_explain_structure)
            return (f"logarithmic_scaling argument is correct.", logarithmic_scaling)
    
    def __check_colormap(self, colormap):
        """
        Validate the colormap configuration for subplots.

        Checks if the colormap configuration is provided as a single string or Colormap class for all subplots or
        a list specifying the colormap for individual subplots. If colormap is for all subplots index is equal to -1.

        Arguments:
        ----------
        colormap : str, Colormap, or list
            A string, Colormap class, or list where each element is a list containing the subplot index and a string or Colormap class representing the colormap.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated colormap configuration.

        Raises:
        -------
        TypeError
            If colormap is not a string, Colormap class, or list.
        ValueError
            If the structure or values within colormap do not match the expected format.

        Notes:
        ------
        - The method first checks if the input is a string, Colormap class, or a list.
        - For a single string or Colormap class, it validates the format and returns a default configuration.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: the subplot index and a string or Colormap class representing the colormap.
        - The subplot index should be an integer and can be -1 for a default setting.
        - The string or Colormap class should be one of the recognized colormaps.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `colormap` is:
        - "viridis" (correct format)
        - Colormap("viridis") (correct format)
        - [[0, "viridis"], [1, Colormap("plasma")], [-1, Colormap("plasma")]] (correct format)
        - [[0, "viridis"], [1, "invalid"]] (incorrect format)
        - [[0, "viridis"], [1, 123]] (incorrect format)
        - 123 (incorrect format)

        This method will validate the provided colormap configuration and return a success message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_that_explain_structure = '''The structure is [x, y] (x - number of subplot or -1 (for all subplots that aren't called), y - string or Colormap class. Possible options for colormap presented on this site https://matplotlib.org/stable/users/explain/colors/colormaps.html . Remember!!! we do NOT take responsibility if you have made a mistake in colormap spelling.'''
        if not isinstance(colormap, (list, str, Colormap)):
            raise TypeError(f"colormap argument is incorrect." + text_that_explain_structure)
        if isinstance(colormap, (str, Colormap)):
            return (f"colormap argument is correct", [[-1, colormap]])
        elif isinstance(colormap, list):
            for i in range(len(colormap)):
                if not isinstance(colormap[i], list):
                    raise TypeError(f'colormap argument number {i} ({colormap[i]}) should be list.' + text_that_explain_structure)
                elif len(colormap[i]) != 2:
                    raise TypeError(f'colormap argument number {i} ({colormap[i]}) should have two elements.' + text_that_explain_structure)
                elif not isinstance(colormap[i][0], int):
                    raise ValueError(f'colormap argument number {i} ({colormap[i][0]}) should be int.' + text_that_explain_structure)
                elif colormap[i][0] < 0 and colormap[i][0] != -1:
                    raise ValueError(f'colormap argument number {i} ({colormap[i][0]}) should be positive or -1.' + text_that_explain_structure)
                elif not isinstance(colormap[i][1], (str, Colormap)):
                    raise ValueError(f'colormap argument number {i} ({colormap[i][1]}) should be int.' + text_that_explain_structure)
            return (f"colormap argument is correct.", colormap)
     
    def __check_data_and_graph_type_are_correlated(self, index):
        """
        Validate the correlation between data and graph type for plotting.

        Ensures that the data structure matches the specified graph type (2D or 3D).
        For 2D plots, the data should be in the format [[x, xerr], [y, yerr]].
        For 3D plots, the data should be in the format [x, y, z], where z is a 2D array.

        Arguments:
        ----------
        index : int
            The index of the subplot to check.

        Returns:
        -------
        str
            A confirmation message indicating that the data is correct.

        Raises:
        -------
        ValueError
            If the data structure does not match the expected format for the specified graph type.

        Notes:
        ------
        - The method first checks the graph type for the specified subplot.
        - For 2D plots, it validates that the data has exactly two elements (x and y), each of which can have up to two elements (data and error).
        - For 3D plots, it validates that the data has exactly three elements (x, y, and z), where z is a 2D array.
        - It also checks that all data arrays are of type numpy.ndarray and have the correct dimensions.
        - If any element does not match the expected format, a ValueError is raised.

        Example:
        --------
        Assuming `self.curves_settings` is:
        - {"graph_type": 1, "data": [[np.array([1, 2, 3]), np.array([0.1, 0.2, 0.3])], [np.array([4, 5, 6]), np.array([0.4, 0.5, 0.6])]]} (correct format for 2D)
        - {"graph_type": 2, "data": [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([[1, 2], [3, 4], [5, 6]])]} (correct format for 3D)
        - {"graph_type": 1, "data": [[np.array([1, 2, 3])], [np.array([4, 5, 6]), np.array([0.4, 0.5, 0.6])]]} (incorrect format for 2D)
        - {"graph_type": 2, "data": [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([1, 2, 3])]} (incorrect format for 3D)

        This method will validate the provided data structure and return a confirmation message if the data is correct.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_to_explain_structure = ''' The structure of the data has two different options. If data type is "2D" then the structure is [[x, xerr], [y, yerr]] (xerr, yerr are not necessarily included). If data type is "3D" (z coordinate is vizualizated by color) then the structure is [x, y, z]. Note: z array is two dimensional len(y) elements in each rows and len(x) rows. All data (x, y, z, xerr, yerr) have to have type numpy.ndarray. If structure or data is incorrect it won't be vizualized'''
        if self.curves_settings[index]["graph_type"] == 1:
            if len(self.curves_settings[index]["data"]) != 2:
                raise ValueError(f"data {index} for 2D plot should have 2 elements." + text_to_explain_structure)
            elif len(self.curves_settings[index]["data"]) == 2:
                if len(self.curves_settings[index]["data"][0]) > 2:
                    raise ValueError(f"data {index} for x (first element) for 2D type maximum has two elements." + text_to_explain_structure)
                elif len(self.curves_settings[index]["data"][1]) > 2:
                    raise ValueError(f"data {index} for y (first element) for 2D type maximum has two elements." + text_to_explain_structure)
                elif len(self.curves_settings[index]["data"][0]) <= 2 and len(self.curves_settings[index]["data"][1]) <= 2:
                    lenght = self.curves_settings[index]["data"][0][0].shape[0]
                    for i in range(2):
                        for j in range(len(self.curves_settings[index]["data"][i])):
                            if self.curves_settings[index]["data"][i][j].shape[0] != lenght:
                                raise ValueError(f"data {i} x, y (xerr, yerr) should have the same lenght." + text_to_explain_structure)
                    return f"data {index} is correct."
        elif self.curves_settings[index]["graph_type"] == 2:
            if len(self.curves_settings[index]["data"]) != 3:
                raise ValueError(f"data {index} for 3D plot should have 3 elements." + text_to_explain_structure)
            elif len(self.curves_settings[index]["data"]) == 3:
                for i in range(3):
                    if not isinstance(self.curves_settings[index]["data"][i], np.ndarray):
                        raise ValueError(f"data {index} should have type numpy.ndarray." + text_to_explain_structure)
                if self.curves_settings[index]["data"][0].ndim != 1 or self.curves_settings[index]["data"][1].ndim != 1:
                    raise ValueError(f"data {i} (x and y elements) should be one dimensional array." + text_to_explain_structure)
                elif self.curves_settings[index]["data"][0].shape[0] != self.curves_settings[index]["data"][1].shape[0]:
                    raise ValueError(f"data {i} x and y elements should  have the same number of points." + text_to_explain_structure)       
                elif self.curves_settings[index]["data"][2].ndim != 2:
                    raise ValueError(f"data {i} (z) should be two dimensional array." + text_to_explain_structure)
                elif self.curves_settings[index]["data"][0].shape[0] * self.curves_settings[index]["data"][1].shape[0] != self.curves_settings[index]["data"][2].shape[0] * self.curves_settings[index]["data"][2].shape[1]:
                    raise ValueError(f"data {i} z elemnts should have number of points equal to x * y (number of elements from them)." + text_to_explain_structure)
                return f"data {index} is correct."
            
    def __check_start_point(self, start_point):
        """
        Validate the start point coordinates for plotting.

        Ensures that the start point is provided as a list of coordinates [x, y] where x and y can be integers or floats.
        If there is only one line, the start point can be provided as a list [x, y] instead of a list of lists.

        Arguments:
        ----------
        start_point : list
            A list containing the start point coordinates. Each element can be a list [x, y] or a single list [x, y] for one line.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated start point coordinates.

        Raises:
        -------
        TypeError
            If start_point is not a list or if the elements do not match the expected format.

        Notes:
        ------
        - The method first checks if the input is a list.
        - For a single line, it validates the format and returns a list containing the coordinates.
        - For multiple lines, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: x and y, which should be integers or floats.
        - If any element does not match the expected format, a TypeError is raised.

        Example:
        --------
        Assuming `start_point` is:
        - [1.0, 2.0] (correct format for a single line)
        - [[1.0, 2.0]] (correct format for a single line)
        - [[1.2, 2], [3, 4.2]] (correct format for multiple lines)
        - [[1.0, 2.0], 3.0] (incorrect format)
        - [1.0, [2.0, 3.0]] (incorrect format)
        - 1.0 (incorrect format)

        This method will validate the provided start point coordinates and return a confirmation message along with the validated coordinates.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_to_explain_structure = ''' The structure is list of elements like [x, y] where x(y) is x(y) choord of start point. x(y) can be int or float. If you have only one line, you can write not a list of [x, y] but just [x, y].'''
        if not isinstance(start_point, list):
            raise TypeError(f"Start_point should be a list with x, y choords or list of [x, y]. " + text_to_explain_structure)
        elif isinstance(start_point, list):
            if len(start_point) == 2: #check for second option (only one line)
                if not isinstance(start_point[0], (list, int, float)):
                    raise TypeError(f"Start_point 0 should be a list with x, y choords or list of [x, y]. " + text_to_explain_structure)
                elif not isinstance(start_point[1], (list, int, float)):
                    raise TypeError(f"Start_point 1 should be a list with x, y choords or list of [x, y]. " + text_to_explain_structure)
                elif isinstance(start_point[0], (int, float)) and isinstance(start_point[1], (int, float)):
                    return (f"Start_point argument is correct.", [start_point])
                elif (isinstance(start_point[0], list) and isinstance(start_point[1], (int, float))) or (isinstance(start_point[1], list) and isinstance(start_point[0], (int, float))):
                    raise TypeError(f"Start_point elements should have the same type. Options are [x, y] (x and are int or float) or list of [x, y]." + text_to_explain_structure)
            for i in range(len(start_point)):
                if not isinstance(start_point[i], list):
                    raise TypeError(f"Start_point {i} ({start_point[i]}) should be a list of [x, y]." + text_to_explain_structure)
                elif isinstance(start_point[i], list):
                    if len(start_point[i]) != 2:
                        raise TypeError(f"Start_point {i} ({start_point[i]}) should have to be int(float) elements." + text_to_explain_structure)
                    elif not isinstance(start_point[i][0], (int, float)):
                        raise TypeError(f"Start_point {i} index 0 ({start_point[i][0]}) should be an int(float) element." + text_to_explain_structure)
                    elif not isinstance(start_point[i][1], (int, float)):
                        raise TypeError(f"Start_point {i} index 1 ({start_point[i][1]}) should be an int(float) element." + text_to_explain_structure)
            return (f"Start_point argument is correct.", start_point)
        
    def __check_end_point(self, end_point):
        """
        Validate the end point coordinates for plotting.

        Ensures that the end point is provided as a list of coordinates [x, y] where x and y can be integers or floats.
        If there is only one line, the end point can be provided as a list [x, y] instead of a list of lists.

        Arguments:
        ----------
        end_point : list
            A list containing the end point coordinates. Each element can be a list [x, y] or a single list [x, y] for one line.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated end point coordinates.

        Raises:
        -------
        TypeError
            If end_point is not a list or if the elements do not match the expected format.

        Notes:
        ------
        - The method first checks if the input is a list.
        - For a single line, it validates the format and returns a list containing the coordinates.
        - For multiple lines, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: x and y, which should be integers or floats.
        - If any element does not match the expected format, a TypeError is raised.

        Example:
        --------
        Assuming `end_point` is:
        - [1.0, 2.0] (correct format for a single line)
        - [[1.0, 2.0]] (correct format for a single line)
        - [[1.2, 2], [3, 4.2]] (correct format for multiple lines)
        - [[1.0, 2.0], 3.0] (incorrect format)
        - [1.0, [2.0, 3.0]] (incorrect format)
        - 1.0 (incorrect format)

        This method will validate the provided end point coordinates and return a confirmation message along with the validated coordinates.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_to_explain_structure = ''' The structure is list of elements like [x, y] where x(y) is x(y) choord of end point. x(y) can be int or float. If you have only one line, you can write not a list of [x, y] but just [x, y].'''
        if not isinstance(end_point, list):
            raise TypeError(f"end_point should be a list with x, y choords or list of [x, y]. " + text_to_explain_structure)
        elif isinstance(end_point, list):
            if len(end_point) == 2: #check for second option (only one line)
                if not isinstance(end_point[0], (list, int, float)):
                    raise TypeError(f"end_point 0 should be a list with x, y choords or list of [x, y]. " + text_to_explain_structure)
                elif not isinstance(end_point[1], (list, int, float)):
                    raise TypeError(f"end_point 1 should be a list with x, y choords or list of [x, y]. " + text_to_explain_structure)
                elif isinstance(end_point[0], (int, float)) and isinstance(end_point[1], (int, float)):
                    return (f"end_point argument is correct.", [end_point])
                elif (isinstance(end_point[0], list) and isinstance(end_point[1], (int, float))) or (isinstance(end_point[1], list) and isinstance(end_point[0], (int, float))):
                    raise TypeError(f"end_point elements should have the same type. Options are [x, y] (x and y are int or float) or list of [x, y]." + text_to_explain_structure)
            for i in range(len(end_point)):
                if not isinstance(end_point[i], list):
                    raise TypeError(f"end_point {i} ({end_point[i]}) should be a list of [x, y]." + text_to_explain_structure)
                elif isinstance(end_point[i], list):
                    if len(end_point[i]) != 2:
                        raise TypeError(f"end_point {i} ({end_point[i]}) should have to be int(float) elements." + text_to_explain_structure)
                    elif not isinstance(end_point[i][0], (int, float)):
                        raise TypeError(f"end_point {i} index 0 ({end_point[i][0]}) should be an int(float) element." + text_to_explain_structure)
                    elif not isinstance(end_point[i][1], (int, float)):
                        raise TypeError(f"end_point {i} index 1 ({end_point[i][1]}) should be an int(float) element." + text_to_explain_structure)
            return (f"end_point argument is correct.", end_point)    
    
    def __check_text_position(self, text_position):
        """
        Validate the text position coordinates for plotting.

        Ensures that the text position is provided as a list of coordinates [x, y] where x and y can be integers, floats, or False.
        If there is only one line, the text position can be provided as a list [x, y] instead of a list of lists.
        If x or y is False, the text will be located in the middle of the graph with a slight offset from the straight line.

        Arguments:
        ----------
        text_position : list
            A list containing the text position coordinates. Each element can be a list [x, y] or a single list [x, y] for one line.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated text position coordinates.

        Raises:
        -------
        TypeError
            If text_position is not a list or if the elements do not match the expected format.
        ValueError
            If x or y is True, which is not allowed.

        Notes:
        ------
        - The method first checks if the input is a list.
        - For a single line, it validates the format and returns a list containing the coordinates.
        - For multiple lines, it iterates through each element and validates the format.
        - Each element in the list should be a list of two elements: x and y, which should be integers, floats, or False.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `text_position` is:
        - [1.0, 2.0] (correct format for a single line)
        - [[1, 2.0]] (correct format for a single line)
        - [[1.2, 2], [3, 4.1]] (correct format for multiple lines)
        - [False, 2.0] (correct format for a single line)
        - [[1.2, 2], [False, False]] (correct format for multiple lines)
        - [[1.0, 2.0], 3.0] (incorrect format)
        - [1.0, [2.0, 3.0]] (incorrect format)
        - [1.0, True] (incorrect format)
        - 1.0 (incorrect format)

        This method will validate the provided text position coordinates and return a confirmation message along with the validated coordinates.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        text_to_explain_structure = ''' The structure is list of elements like [x, y] where x(y) is x(y) choord of lower left part of text.
        x(y) can be int or float. If you have only one line, you can write not a list of [x, y] but just [x, y].
        If x(y) argument is False, then this coordinate will be such that the text will be located in the middle of the graph
        with a slight offset from the straight line.'''
        if not isinstance(text_position, list):
            raise TypeError(f"text_position should be a list with x, y choords or list of [x, y], where x(y) can be int(float) or False." + text_to_explain_structure)
        elif isinstance(text_position, list):
            if len(text_position) == 2: #check for second option (only one line)
                if not isinstance(text_position[0], (list, int, float, bool)):
                    raise TypeError(f"text_position 0 should be a list with x, y choords (or False) or list of [x, y]. " + text_to_explain_structure)
                elif not isinstance(text_position[1], (list, int, float, bool)):
                    raise TypeError(f"text_position 1 should be a list with x, y choords or list of [x, y]. " + text_to_explain_structure)
                elif isinstance(text_position[0], (int, float, bool)) and isinstance(text_position[1], (int, float, bool)):
                    if isinstance(text_position[0], bool) and text_position[0]:
                        raise ValueError(f"text_position 0 ({text_position[0]}) can be False, int or float." + text_to_explain_structure)
                    return (f"text_position argument is correct.", [text_position])
                elif (isinstance(text_position[0], list) and isinstance(text_position[1], (int, float, bool))) or (isinstance(text_position[1], list) and isinstance(text_position[0], (int, float, bool))):
                    raise TypeError(f"text_position elements should have the same type. Options are [x, y] (x and y are int, float or False) or list of [x, y]." + text_to_explain_structure)
            for i in range(len(text_position)):
                if not isinstance(text_position[i], list):
                    raise TypeError(f"text_position {i} ({text_position[i]}) should be a list of [x, y]." + text_to_explain_structure)
                elif isinstance(text_position[i], list):
                    if len(text_position[i]) != 2:
                        raise TypeError(f"text_position {i} ({text_position[i]}) should have to be int(float or False) elements." + text_to_explain_structure)
                    elif not isinstance(text_position[i][0], (int, float, bool)):
                        raise TypeError(f"text_position {i} index 0 ({text_position[i][0]}) should be an int(float or False) element." + text_to_explain_structure)
                    elif isinstance(text_position[i][0], bool) and text_position[i][0]:
                        raise ValueError(f"text_position {i} 0 ({text_position[i][0]}) can be False, int or float." + text_to_explain_structure)
                    elif not isinstance(text_position[i][1], (int, float, bool)):
                        raise TypeError(f"text_position {i} index 1 ({text_position[i][1]}) should be an int(float or False) element." + text_to_explain_structure)
                    elif isinstance(text_position[i][1], bool) and text_position[i][1]:
                        raise ValueError(f"text_position {i} 1 ({text_position[i][1]}) can be False, int or float." + text_to_explain_structure)                    
            return (f"text_position argument is correct.", text_position)  

    def __check_subplot_pos_line(self, subplot_pos_line):
        """
        Validate the subplot position for lines in plotting.

        Ensures that the subplot position is provided as a single integer for all lines or
        a list of integers specifying the subplot index for each line.

        Arguments:
        ----------
        subplot_pos_line : int or list of int
            A single integer or a list of integers representing the subplot index where each line is located.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated subplot position configuration.

        Raises:
        -------
        TypeError
            If subplot_pos_line is not an integer or list of integers.
        ValueError
            If any subplot position is not a non-negative integer.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a list containing the integer.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a non-negative integer.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `subplot_pos_line` is:
        - 0 (correct format)
        - [0, 1, 2] (correct format)
        - [-1] (incorrect format)
        - -1 (incorrect format)
        - [0, "1", 2] (incorrect format)
        - "0" (incorrect format)

        This method will validate the provided subplot position configuration and return a confirmation message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        
        if not isinstance(subplot_pos_line, (int, list)):
            raise TypeError(f'subplot_pos_line argument is incorrect. It should be a list with integer elements which are number of subplot where line is located (starting from 0) or one integer for all lines.')
        if isinstance(subplot_pos_line, int):
            if subplot_pos_line >= 0:
                return (f"subplot_pos_line argument is correct.", [subplot_pos_line])
            else:
                raise ValueError(f"subplot_pos_line argument should be more or equal to 0.")
        elif isinstance(subplot_pos_line, list):
            for i in range(len(subplot_pos_line)):
                if not isinstance(subplot_pos_line[i], int):
                    raise ValueError(f"subplot_pos_line argument {i} ({subplot_pos_line[i]}) should be an integer.")
                elif subplot_pos_line[i] < 0:
                    raise ValueError(f"subplot_pos_line argument {i} ({subplot_pos_line[i]}) should be more or equal to 0.")
            return (f"subplot_pos_line argument is correct.", subplot_pos_line)
        
    def __check_text_rotation(self, text_rotatation):
        """
        Validate the text rotation angles for plotting.

        Ensures that the text rotation angles are provided as a single float or integer for all lines or
        a list of floats or integers specifying the rotation angle for each line.

        Arguments:
        ----------
        text_rotation : float, int, or list of float, int
            A single float or integer or a list of floats or integers representing the text rotation angles.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated text rotation configuration.

        Raises:
        -------
        TypeError
            If text_rotation is not a float, integer, or list of floats or integers.

        Notes:
        ------
        - The method first checks if the input is a float, integer, or a list.
        - For a single float or integer, it validates the format and returns a list containing the value.
        - For a list, it iterates through each element and validates the format.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `text_rotation` is:
        - 45.0 (correct format)
        - -45.0 (correct format)
        - 45 (correct format)
        - -45 (correct format)
        - 45.4 (correct format)
        - -45.4 (correct format)
        - [30.7, 45.0, -60] (correct format)
        - [10.0] (correct format)
        - [30.0, "45.0", 60.0] (incorrect format)
        - "45.0" (incorrect format)

        This method will validate the provided text rotation configuration and return a confirmation message along with the validated configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if not isinstance(text_rotatation, (float, int, list)):
            raise TypeError(f'text_rotatation argument is incorrect. It should be a list width float (int) elements which are angles of textes rotation or one float number for all lines.')
        if isinstance(text_rotatation, (float, int)):
            return (f"text_rotatation argument is correct.", [text_rotatation])
        elif isinstance(text_rotatation, list):
            for i in range(len(text_rotatation)):
                if not isinstance(text_rotatation[i], (float, int)):
                    raise ValueError(f"text_rotatation argument {i} ({text_rotatation[i]}) should be a float (int).")
            return (f"text_rotatation argument is correct.", text_rotatation)
        
    def __check_text(self, text):
        """
        Validate the text labels for plotting.

        Ensures that the text labels are provided as a single string for all data or a list of strings for individual data series.

        Arguments:
        ----------
        text : str or list of str
            A string or list of strings representing the text labels for the data series.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated text labels.

        Raises:
        -------
        TypeError
            If text is neither a string nor a list of strings.

        Notes:
        ------
        - The method first checks if the input is a string or a list.
        - For a single string, it validates the format and returns a list containing the string.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a string.
        - If any element does not match the expected format, a TypeError is raised.

        Example:
        --------
        Assuming `text` is:
        - "Main Label" (correct format)
        - ["Label 1", "Label 2"] (correct format)
        - ["Label 1", 123] (incorrect format)
        - 123 (incorrect format)

        This method will validate the provided text labels and return a confirmation message along with the validated text labels.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if not isinstance(text, (list, str)):
            raise TypeError(f"text should be a list with strings(text as a label for the line) or one string for all data.")
        if isinstance(text, str):
            return (f"text argument is correct", [text])
        elif isinstance(text, list):
            for i in range(len(text)):
                if not isinstance(text[i], str):
                    raise TypeError(f"text element {i} ({text[i]}) should be a list with strings(text as a label for the line).")
            return  (f"text argument is correct", text)
    
    def __check_text_font_size(self, text_fontsize):
        """
        Validate the font size for text labels in plotting.

        Ensures that the text font size is provided as a single integer for all data or
        a list of integers specifying the font size for individual data series.

        Arguments:
        ----------
        text_fontsize : int or list of int
            An integer or list of integers representing the font size for text labels.

        Returns:
        -------
        tuple
            A tuple with a confirmation message and the validated font sizes.

        Raises:
        -------
        TypeError
            If text_fontsize is not an integer or list of integers.
        ValueError
            If any font size provided is not a positive integer.

        Notes:
        ------
        - The method first checks if the input is an integer or a list.
        - For a single integer, it validates the format and returns a list containing the integer.
        - For a list, it iterates through each element and validates the format.
        - Each element in the list should be a positive integer.
        - If any element does not match the expected format, a TypeError or ValueError is raised.

        Example:
        --------
        Assuming `text_fontsize` is:
        - 12 (correct format)
        - [10, 12, 14] (correct format)
        - [10, -12, 14] (incorrect format)
        - [0, 12, 14] (incorrect format)
        - [10, "12", 14] (incorrect format)
        - "12" (incorrect format)

        This method will validate the provided font sizes and return a confirmation message along with the validated font sizes.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if not isinstance(text_fontsize, (int, list)):
            raise TypeError(f'text_fontsize argument is incorrect. It should be a list with integer elements which are text fontsize or one integer for all data.')
        if isinstance(text_fontsize, int):
            if text_fontsize > 0:
                return (f"text_fontsize argument is correct.", [text_fontsize])
            else:
                raise ValueError(f"text_fontsize argument should be more than 0.")
        elif isinstance(text_fontsize, list):
            for i in range(len(text_fontsize)):
                if not isinstance(text_fontsize[i], int):
                    raise ValueError(f"text_fontsize argument {i} ({text_fontsize[i]}) should be an integer.")
                elif text_fontsize[i] < 1:
                    raise ValueError(f"text_fontsize argument {i} ({text_fontsize[i]}) should be more than 0.")
            return (f"text_fontsize argument is correct.", text_fontsize)
        
    def __prepare_axes_titles_for_subplots(self, index):
        """
        Prepare the axes titles for subplots.

        Ensures that the axes titles are correctly set for each subplot based on the graph type.
        For 3D plots, it ensures that the axes titles list contains three elements: titles for X, Y, and Z axes.
        If the list does not contain three elements, it appends an empty string for the missing titles.
        Similarly, it ensures that the axes font size list contains three elements, appending a default font size if necessary.

        Arguments:
        ----------
        index : int
            The index of the subplot to prepare the axes titles for.

        Returns:
        -------
        None

        Raises:
        -------
        None

        Notes:
        ------
        - The method iterates through the curves settings to find the subplot with the specified index and graph type 2 (3D plot).
        - It checks the length of the axes titles and font size lists for the subplot.
        - If the lists do not contain three elements, it appends an empty string for the titles and a default font size for the font sizes.

        Example:
        --------
        Assuming `self.curves_settings` and `self.subplots_settings` are properly initialized:
        - If `self.curves_settings[i]["subplot_position"] == index` and `self.curves_settings[i]["graph_type"] == 2`,
        the method will ensure that `self.subplots_settings[index]["axes_titles"]` and `self.subplots_settings[index]["axes_font_size"]`
        each contain three elements.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        for i in range(self.quant):
            if self.curves_settings[i]["subplot_position"] == index and self.curves_settings[i]["graph_type"] == 2:
                if len(self.subplots_settings[index]["axes_titles"]) != 3:
                    self.subplots_settings[index]["axes_titles"].append("")
                if len(self.subplots_settings[index]["axes_font_size"]) != 3:
                    self.subplots_settings[index]["axes_font_size"].append(10)

    def __construct_structure_curve(self, data_array):
        """
        Constructs and populates the structure for curve settings.

        This method iterates through the specified number of curves (`self.quant`)
        and creates a dictionary for each curve to store its visual settings.
        These settings are derived from the provided `data_array` and the
        configuration dictionary `self.config`. The constructed dictionaries are
        appended to the `self.curves_settings` list.

        Arguments:
        ----------
        data_array : list or numpy.ndarray
            A list or array containing the data for each curve.
            Each element in `data_array` corresponds to the data for a single curve,
            and the order should align with the curve configurations in `self.config`.

        Returns:
        -------
        None
            The method modifies the `self.curves_settings` attribute in place.

        Attributes:
        ----------
        quant : int
            The number of curves to be plotted.
        config : dict
            A dictionary containing configuration settings for curves and subplots.
            It is expected to have keys such as "graph_types", "color", "ls", "marker_shape",
            "marker_size", "labels", "line_width", "line_alpha", and "subplots_settings".
        curves_settings : list
            A list to store dictionaries, where each dictionary holds
            the settings for a single curve. This list is populated by this method.

        Methods:
        -------
        self.__check_data_and_graph_type_are_correlated(index)
            Checks if the data and graph type are correlated for the curve at index `index`.

        Notes:
        ------
        - The method updates `self.curves_settings` with dictionaries containing the settings for each curve.
        - If any validation errors occur during the construction of a curve's settings, the curve is removed from `self.curves_settings` and an error message is printed.

        Example:
        --------
        Assuming `self.quant` is 3, `self.config` is:
            {
                "graph_types": ["2D", "3D", "2D"],
                "color": ["#FF5733", "#2ECC71", "#8E44AD"],
                "ls": ["-", "--", "-."],
                "marker_shape": ["o", "s", "^"],
                "marker_size": [5, 7, 9],
                "labels": ["Curve 1", "Curve 2", "Curve 3"],
                "line_width": [1, 2, 3],
                "line_alpha": [1.0, 0.8, 0.6],
                "subplots_settings": [{"rows_cols": [3, 3], "figure_size": [14, 14], "subplots_distribution": [0, 1, 2]}]
            }
        and `data_array` is:
            [
                [[x, xerr], [y, yerr]],
                [x, y, z],
                [[x], [y]]
            ]
        This method will populate `self.curves_settings` with the appropriate settings for each curve.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        graph_pos_types = {"2D":1, "3D":2}
        index = 0
        count = 0
        for i in range(self.quant):
            self.curves_settings.append(dict())
            self.curves_settings[-1] = {"data": data_array[i],
                                      "graph_type": graph_pos_types[self.config["graph_types"][i]],
                                      "color": self.config["color"][i],
                                      "ls": self.config["ls"][i],
                                      "marker_shape": self.config["marker_shape"][i],
                                      "marker_size": self.config["marker_size"][i], 
                                      "subplot_position": self.config["subplots_settings"][0]["subplots_distribution"][i],
                                      "line_width": self.config["line_width"][i],
                                      "line_alpha": self.config["line_alpha"][i],
                                      "label": self.config["labels"][i]}
            try:
                result = self.__check_data_and_graph_type_are_correlated(index)
                index += 1
                if self.verbose:
                    print(result)
            except (TypeError, ValueError) as e:
                    del self.curves_settings[-1]
                    count += 1
                    print(f'Error: {e}')  # Print any validation errors
        self.quant = len(self.curves_settings)

    def __construct_structure_subplots(self):
        """
        Constructs and populates the structure for subplot settings.

        This method iterates through the specified number of subplots
        (`self.number_of_subplots`) and creates a dictionary for each subplot
        to store its visual settings. These settings are derived from the
        configuration dictionary `self.config`. The constructed dictionaries are
        appended to the `self.subplots_settings` list.

        Arguments:
        ----------
        None

        Returns:
        -------
        None
            The method modifies the `self.subplots_settings` attribute in place.

        Attributes:
        ----------
        number_of_subplots : int
            The number of subplots to be created.
        config : dict
            A dictionary containing configuration settings for subplots.
            It is expected to have keys such as "axes_font_size", "subplots_titles_font_size",
            "subplots_titles_text", "legends_font_size", "axes_scaling",
            "axes_round_accuracy", "axes_number_of_small_ticks", "axes_titles",
            and "subplots_legend_position".
        subplots_settings : list
            A list to store dictionaries, where each dictionary holds
            the settings for a single subplot. This list is populated by this method.

        Methods:
        -------
        self.__find_proper_axes_font_size(i)
            Finds the proper font size for the axes of the subplot at index `i`.
        self.__find_proper_subplots_titles_font_size(i)
            Finds the proper font size for the titles of the subplot at index `i`.
        self.__find_proper_axes_number_of_small_ticks(i)
            Finds the proper number of small ticks for the axes of the subplot at index `i`.
        self.__find_proper_legends_font_size(i)
            Finds the proper font size for the legends of the subplot at index `i`.
        self.__find_proper_legend_position(i)
            Finds the proper position for the legend of the subplot at index `i`.
        self.__find_proper_axes_round_accuracy(i)
            Finds the proper rounding accuracy for the axes of the subplot at index `i`.
        self.__find_proper_logarithmic_scaling(i)
            Finds the proper logarithmic scaling for the axes of the subplot at index `i`.
        self.__find_proper_axes_scaling(i)
            Finds the proper scaling for the axes of the subplot at index `i`.
        self.__find_proper_colormap(i)
            Finds the proper colormap for the subplot at index `i`.
        self.__prepare_axes_titles_for_subplots(i)
            Prepares the axes titles for the subplot at index `i`.

        Notes:
        ------
        - The method updates `self.subplots_settings` with dictionaries containing the settings for each subplot.
        - If any validation errors occur during the construction of a subplot's settings, an error message is printed and the program exits.

        Example:
        --------
        Assuming `self.number_of_subplots` is 3, `self.config` is:
            {
                "axes_font_size": [10, 12, 14],
                "subplots_titles_font_size": [12, 14, 16],
                "subplots_titles_text": ["Subplot 1", "Subplot 2", "Subplot 3"],
                "legends_font_size": [8, 10, 12],
                "axes_scaling": [[-1, "stretch", [0.9, 1.1, 0.9, 1.1]], [-1, "stretch", [0.9, 1.1, 0.9, 1.1]], [-1, "stretch", [0.9, 1.1, 0.9, 1.1]]],
                "axes_round_accuracy": [[-1, ["%0.2f", "%0.2f"]], [-1, ["%0.2f", "%0.2f"]], [-1, ["%0.2f", "%0.2f"]]],
                "axes_number_of_small_ticks": [[-1, [5, 5]], [-1, [5, 5]], [-1, [5, 5]]],
                "axes_titles": [["X", "Y"], ["X", "Y"], ["X", "Y"]],
                "subplots_legend_position": [[-1, "best"], [-1, "best"], [-1, "best"]],
                "subplots_settings": [
                    {
                    "rows_cols": [1, 1],
                    "figure_size": [12, 10],
                    "subplots_distribution": [0]
                    }
                ] 
            }
        This method will populate `self.subplots_settings` with the appropriate settings for each subplot.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        for i in range(self.number_of_subplots):
            try:
                fontsizes_for_axes = self.__find_proper_axes_font_size(i)
                fontsize_for_title_subplot = self.__find_proper_subplots_titles_font_size(i)
                number_axes_number_of_small_ticks = self.__find_proper_axes_number_of_small_ticks(i)
                fontsize_legend_font_size = self.__find_proper_legends_font_size(i)
                position_legend_position = self.__find_proper_legend_position(i)
                round_axes_round_accuracy = self.__find_proper_axes_round_accuracy(i)
                scaling_logarithmic_scaling = self.__find_proper_logarithmic_scaling(i)
                scaling_axes_scaling = self.__find_proper_axes_scaling(i)
                color_colormap = self.__find_proper_colormap(i)
            except ValueError as e:
                print(f"You have an error: {e}")
                sys.exit(1)

            self.subplots_settings.append(dict())
            self.subplots_settings[i] = {
                                         "axes_font_size": fontsizes_for_axes, 
                                         "subplots_titles_font_size": fontsize_for_title_subplot,
                                         "subplots_titles_text": self.config["subplots_titles_text"][i],
                                         "legends_font_size": fontsize_legend_font_size,
                                         "axes_scaling": scaling_axes_scaling,
                                         "axes_round_accuracy": round_axes_round_accuracy,
                                         "axes_number_of_small_ticks": number_axes_number_of_small_ticks,
                                         "axes_titles": self.config["axes_titles"][i],
                                         "legend_position": position_legend_position,
                                         "logarithmic_scaling": scaling_logarithmic_scaling,
                                         "colormap": color_colormap
                                         }
            self.__prepare_axes_titles_for_subplots(i)
            
    def __prepare_config(self):
        """
        Prepares and extends the configuration parameters for plotting.

        This method takes the initial configuration (`self.config`) and extends or initializes
        each parameter to ensure all plots have defined settings. It uses default values when
        specific settings are not provided in the initial configuration.

        Arguments:
        ----------
        None.

        Returns:
        -------
        None
            The method modifies the `self.config` attribute in place.

        Attributes:
        ----------
        quant : int
            The quantity of data series or plots.
        number_of_subplots : int
            The number of subplot areas defined in the plot layout.
        file_path_name_to_conf : str
            The file path to the configuration file.
        config : dict
            A dictionary containing configuration settings for plots and subplots.
            It is expected to have keys such as "color", "ls", "marker_shape", "axes_font_size",
            "subplots_titles_font_size", "subplots_titles_text", "legends_font_size",
            "marker_size", "line_width", "line_alpha", "axes_round_accuracy",
            "subplots_settings", "graph_types", "axes_scaling", "axes_number_of_small_ticks",
            "labels", "axes_titles", "subplots_legend_position", and "logarithmic_scaling".

        Methods:
        -------
        self.__extend_parameters(list, int, default_value)
            Extends a list to a given length with a default value if needed.

        Notes:
        ------
        - The method reads the configuration from a file specified by `self.file_path_name_to_conf`.
        - It extends or initializes each parameter in `self.config` to ensure all plots have defined settings.
        - Default values are used when specific settings are not provided in the initial configuration.

        Example:
        --------
        Assuming `self.file_path_name_to_conf` points to a valid configuration file,
        `self.quant` is 3, and `self.number_of_subplots` is 2, this method will read the configuration
        file and extend the settings in `self.config` to ensure all parameters are defined for each plot and subplot.

        Inspiration:
        ------------
        "Kukoriki" series, episode "Oh Ye Grateful".
        """

        with open(self.file_path_name_to_conf, "r", encoding="utf-8") as file:
            config = js.load(file)
        # Color for each data series, defaulting to a dark red if not specified
        self.config["color"] = self.__extend_parameters(self.config["color"], self.quant, config["color"][0])
        
        # Line style for each data series, defaulting to solid line if not specified
        self.config["ls"] = self.__extend_parameters(self.config["ls"], self.quant, config["ls"][0])
        
        # Marker shape for each data series, defaulting to circle 'o'
        self.config["marker_shape"] = self.__extend_parameters(self.config["marker_shape"], self.quant, config["marker_shape"][0])
        
        # Font size for axes labels, default uniform size for all subplots
        self.config["axes_font_size"] = self.__extend_parameters(self.config["axes_font_size"], self.number_of_subplots, config["axes_font_size"][0])
        
        # Font size for subplot titles, default size for all
        self.config["subplots_titles_font_size"] = self.__extend_parameters(self.config["subplots_titles_font_size"], self.number_of_subplots, config["subplots_titles_font_size"][0])
        
        # Titles for subplots, with a humorous default message for many subplots
        self.config["subplots_titles_text"] = self.__extend_parameters(self.config["subplots_titles_text"], self.number_of_subplots, "You are crazy if you have more than 26 subplots.")
        
        # Font size for legends, default uniform size for all subplots
        self.config["legends_font_size"] = self.__extend_parameters(self.config["legends_font_size"], self.number_of_subplots, config["legends_font_size"][0])
        
        # Size of markers for each data series, default size
        self.config["marker_size"] = self.__extend_parameters(self.config["marker_size"], self.quant, config["marker_size"][0])
        
        # Width of lines for each data series, default width
        self.config["line_width"] = self.__extend_parameters(self.config["line_width"], self.quant, config["line_width"][0])
        
        # Transparency (alpha) for lines, default fully opaque
        self.config["line_alpha"] = self.__extend_parameters(self.config["line_alpha"], self.quant, config["line_alpha"][0])
        
        # Rounding accuracy for axes numbers, default to two decimal places
        self.config["axes_round_accuracy"] = self.__extend_parameters(self.config["axes_round_accuracy"], self.number_of_subplots, config["axes_round_accuracy"][0])
        
        # Distribution of subplots, default to 1 plot per subplot
        self.config["subplots_settings"][0]["subplots_distribution"] = self.__extend_parameters(self.config["subplots_settings"][0]["subplots_distribution"], self.quant, config["subplots_settings"][0]["subplots_distribution"][0])
        
        # Type of graph for each data series, default to 2D
        self.config["graph_types"] = self.__extend_parameters(self.config["graph_types"], self.quant, config["graph_types"][0])
        
        # Scaling of axes, default to slight stretch in both directions
        self.config["axes_scaling"] = self.__extend_parameters(self.config["axes_scaling"], self.number_of_subplots, config["axes_scaling"][0])
        
        # Number of small ticks between major ticks, default for both axes
        self.config["axes_number_of_small_ticks"] = self.__extend_parameters(self.config["axes_number_of_small_ticks"], self.number_of_subplots, config["axes_number_of_small_ticks"][0])
        
        # Labels for data series, empty by default
        self.config["labels"] = self.__extend_parameters(self.config["labels"], self.quant, config["labels"][0])
        
        # Titles for axes in each subplot, default to 'X' and 'Y'
        self.config["axes_titles"] = self.__extend_parameters(self.config["axes_titles"], self.number_of_subplots, config["axes_titles"][0])
        
        # Position of the legend in each subplot, default to 'best'
        self.config["subplots_legend_position"] = self.__extend_parameters(self.config["subplots_legend_position"], self.number_of_subplots, config["subplots_legend_position"][0])

        #logarithmic scaling of the axes for each subplot, default not logarithm
        self.config["logarithmic_scaling"] = self.__extend_parameters(self.config["logarithmic_scaling"], self.number_of_subplots, config["logarithmic_scaling"][0])
        
        del config

    def __extend_parameters(self, parameter, quant, element_extend_by):
        """
        Extends a list to a specified length with a default value.

        This method ensures that the given list (`parameter`) has at least `quant` elements.
        If the list is shorter than `quant`, it appends the `element_extend_by` value until
        the list reaches the desired length. If the list is empty, it initializes the list
        with `quant` elements, all set to `element_extend_by`.

        Arguments:
        ----------
        parameter : list
            The list to be extended.
        quant : int
            The desired length of the list.
        element_extend_by : any
            The value to be appended to the list until it reaches the desired length.

        Returns:
        -------
        list
            The extended list with at least `quant` elements.

        Notes:
        ------
        - If the list is shorter than `quant`, the method appends `element_extend_by` until the list reaches the desired length.
        - If the list is empty, it initializes the list with `quant` elements, all set to `element_extend_by`.

        Example:
        --------
        Assuming `parameter` is [1, 2], `quant` is 5, and `element_extend_by` is 0,
        this method will extend `parameter` to [1, 2, 0, 0, 0].

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if len(parameter) < quant and len(parameter) > 0:
            for i in range(len(parameter), quant):
                parameter.append(element_extend_by)
        elif len(parameter) == 0:
            parameter = [element_extend_by] * quant
        return parameter
    
    
    def save_config(self, name="New_config.json"):
        """
        Saves the current configuration to a JSON file.

        This method writes the current configuration stored in `self.config` to a JSON file
        with the specified name. The file is saved with an indentation of 2 spaces and
        ensures that non-ASCII characters are preserved.

        Arguments:
        ----------
        name : str, optional
            The name of the JSON file to save the configuration to. Defaults to "New_config.json".

        Returns:
        -------
        None

        Attributes:
        ----------
        config : dict
            A dictionary containing the current configuration settings to be saved.

        Notes:
        ------
        - The method uses the `json` module to serialize the configuration dictionary to a JSON file.
        - The file is saved with an indentation of 2 spaces for better readability.
        - Non-ASCII characters are preserved in the JSON file.

        Example:
        --------
        Assuming `self.config` contains the current configuration settings, calling `save_config("my_config.json")`
        will save the configuration to a file named "my_config.json".

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        with open(name, "w") as json_file:
            js.dump(self.config, json_file, 
                    indent=2, 
                    ensure_ascii=False)
            
            
    def save_config_for_lines(self, name="New_config_for_lines.json"):
        """
        Saves the current line configuration to a JSON file.

        This method writes the current line configuration stored in `self.config_for_line` to a JSON file
        with the specified name. The file is saved with an indentation of 2 spaces and
        ensures that non-ASCII characters are preserved.

        Arguments:
        ----------
        name : str, optional
            The name of the JSON file to save the line configuration to. Defaults to "New_config_for_lines.json".

        Returns:
        -------
        None

        Attributes:
        ----------
        config_for_line : dict
            A dictionary containing the current line configuration settings to be saved.

        Notes:
        ------
        - The method uses the `json` module to serialize the line configuration dictionary to a JSON file.
        - The file is saved with an indentation of 2 spaces for better readability.
        - Non-ASCII characters are preserved in the JSON file.

        Example:
        --------
        Assuming `self.config_for_line` contains the current line configuration settings, calling `save_config_for_lines("my_line_config.json")`
        will save the line configuration to a file named "my_line_config.json".

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        with open(name, "w") as json_file:
            js.dump(self.config_for_line, json_file, 
                    indent=2, 
                    ensure_ascii=False)
            

    def show_plot(self):
        """
        Displays the plot.

        This method calls the `show` method from the `matplotlib.pyplot` module to display the plot.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Attributes:
        ----------
        plt : matplotlib.pyplot
            The `matplotlib.pyplot` module used for plotting.

        Notes:
        ------
        - This method assumes that the plot has already been configured and is ready to be displayed.
        - The `show` method from `matplotlib.pyplot` is used to render the plot in a window.

        Example:
        --------
        Assuming the plot has been configured with data and settings, calling `show_plot()`
        will display the plot in a new window.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.plt.show()


    def print_curve_settings(self, curve_index):
        """
        Prints the settings for a specific curve.

        This method prints the settings for the curve at the specified index in the `self.curves_settings` list.

        Arguments:
        ----------
        curve_index : int
            The index of the curve whose settings are to be printed.

        Returns:
        -------
        None

        Attributes:
        ----------
        curves_settings : list of dict
            A list of dictionaries where each dictionary contains settings for a single curve.

        Notes:
        ------
        - This method assumes that `self.curves_settings` is a list of dictionaries, where each dictionary
        contains the settings for a single curve.
        - The method prints the settings for the curve at the specified index.

        Example:
        --------
        Assuming `self.curves_settings` is a list of dictionaries with curve settings, calling `print_curve_settings(0)`
        will print the settings for the curve at index 0.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        print(self.curves_settings[curve_index])


    def print_subplot_settings(self, subplot_index):
        """
        Prints the settings for the specified subplot index.

        This method retrieves and prints the settings for the subplot corresponding to the given index
        from the `self.subplots_settings` dictionary.

        Arguments:
        ----------
        subplot_index : int
            The index of the subplot whose settings are to be printed.

        Returns:
        --------
        None

        Raises:
        -------
        KeyError
            If the specified subplot index does not exist in `self.subplots_settings`.

        Attributes:
        ----------
        self.subplots_settings : dict
            A dictionary containing the settings for each subplot. The keys are subplot indices,
            and the values are the settings for the corresponding subplots.

        Notes:
        ------
        - The method assumes that `self.subplots_settings` is a dictionary where the keys are
        subplot indices and the values are the settings for those subplots.
        - If the specified subplot index does not exist in the dictionary, a `KeyError` will be raised.

        Example:
        --------
        Assuming `self.subplots_settings` is:
        [
            {"title": "Subplot 0", "font_size": 12},
            {"title": "Subplot 1", "font_size": 14}
        ]
        and `subplot_index` is 1, this method will print:
        {"title": "Subplot 1", "font_size": 14}

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
            
        print(self.subplots_settings[subplot_index])


    def print_config(self):
        """
        Prints the configuration settings in a formatted JSON string.

        This method retrieves the configuration settings from `self.config` and prints them
        as a formatted JSON string with an indentation of 4 spaces and ensuring that non-ASCII
        characters are not escaped.

        Arguments:
        ----------
        None

        Returns:
        --------
        None

        Attributes:
        ----------
        self.config : dict
            A dictionary containing the configuration settings.

        Notes:
        ------
        - The method uses the `json.dumps` function to convert the configuration dictionary
        into a JSON string.
        - The `indent` parameter is set to 4 to format the JSON string with an indentation of 4 spaces.
        - The `ensure_ascii` parameter is set to `False` to ensure that non-ASCII characters are not escaped.

        Example:
        --------
        Assuming `self.config` is:
        {
            "axes_font_size": [[0, [12, 12]], [1, [14, 13]], [-1, [10, 10]]],
            "title": ["a", "b", "c"],
            ...
        }
        This method will print:
        {
            "axes_font_size": [[0, [12, 12]], [1, [14, 13]], [-1, [10, 10]]],
            "title": ["a", "b", "c"],
            ...
        }

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        print(js.dumps(self.config, indent=4, ensure_ascii=False))
        print(js.dumps(self.config_for_line, indent=4, ensure_ascii=False))

    def draw_lines(self, file_path_name_to_line_conf=Path(__file__).parent.parent / "settings/config_for_lines.json", **kwargs):
        """
        Draws lines based on the configuration file and additional keyword arguments.

        This method reads the configuration from a specified JSON file, prepares the input for drawing lines,
        extends the line configuration, and then draws the lines and associated text based on the configuration.

        Arguments:
        ----------
        file_path_name_to_line_conf : str, optional
            The path to the configuration file for drawing lines. Defaults to "../settings/config_for_lines.json".
        **kwargs : dict
            Additional keyword arguments that can be used to customize the drawing of lines.

        Returns:
        --------
        None

        Attributes:
        ----------
        self.file_path_name_to_conf_for_line : str
            The path to the configuration file for drawing lines.
        self.config_for_line : dict
            A dictionary containing the configuration settings for drawing lines, loaded from the configuration file.

        Notes:
        ------
        - The method reads the configuration file specified by `file_path_name_to_line_conf` and loads it into `self.config_for_line`.
        - The method then calls `self.__prepare_lines_input(**kwargs)` to prepare the input for drawing lines.
        - The method extends the line configuration by calling `self.__extend_line_config()`.
        - Finally, the method draws the lines and associated text by calling `self.__draw_lines_after_conf()` and `self.__draw_text_efter_conf()`.

        Example:
        --------
        Assuming the configuration file "../settings/config_for_lines.json" contains:
        {
            "line_ls": ["-", "--", "-.", ":", ""],
            "line_alpha": [1],
            "line_width": [1],
            ...
        }
        and additional keyword arguments are provided as:
        {
            "custom_line_style": "dashed",
            "custom_text_style": "italic"
        }
        This method will read the configuration, prepare the input, extend the configuration, and draw the lines and text accordingly.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
        if not self.__config_files_changes[1]:
            self.file_path_name_to_conf_for_line = file_path_name_to_line_conf
            with open(self.file_path_name_to_conf_for_line, "r", encoding="utf-8") as file:
                self.config_for_line = js.load(file)
        self.__prepare_lines_input(**kwargs)
        self.__extend_line_config()
        self.__draw_lines_after_conf()
        self.__draw_text_efter_conf()
    
    def __prepare_lines_input(self, **kwargs):
        """
        Prepares the input for line configurations by validating and setting the provided keyword arguments.

        This method iterates through the provided keyword arguments and validates them using predefined
        check functions. If a keyword argument is not recognized, a KeyError is raised. Validation errors
        are caught and printed. If verbose mode is enabled, the validation results are printed.

        Arguments:
        ----------
        **kwargs : dict
            Arbitrary keyword arguments representing the line configuration parameters.

        Returns:
        -------
        None

        Raises:
        -------
        KeyError
            If a keyword argument is not recognized in the configuration.
        TypeError, ValueError
            If a validation error occurs during the checking of a keyword argument.

        Attributes:
        ----------
        self.verbose : bool
            A flag indicating whether to print verbose output.
        self.config_for_line : dict
            A dictionary to store the validated line configuration parameters.

        Notes:
        ------
        - The method uses a dictionary of check functions to validate each keyword argument.
        - If a keyword argument is not recognized, a KeyError is raised with a descriptive message.
        - Validation errors (TypeError, ValueError) are caught and printed.
        - If verbose mode is enabled, the validation results are printed.

        Example:
        --------
        Assuming `self.verbose` is True and `self.config_for_line` is an empty dictionary, calling:
        ```python
        self.__prepare_lines_input(line_color="red", line_ls="solid", labels=["Label1", "Label2"])
        ```
        will validate and set the `line_color`, `line_ls`, and `labels` in `self.config_for_line`.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """
            
        check_functions = {
                           "line_color": self.__check_color,
                           "line_ls": self.__check_ls,
                           "labels": self.__check_labels,
                           "text": self.__check_text,
                           "start_point": self.__check_start_point,
                           "end_point": self.__check_end_point,
                           "text_pos": self.__check_text_position,
                           "subplot_pos_line": self.__check_subplot_pos_line,
                           "line_alpha": self.__check_line_alpha,
                           "line_width": self.__check_line_width,
                           "text_rotation": self.__check_text_rotation,
                           "text_color": self.__check_color,
                           "text_font_size": self.__check_text_font_size
                           }
        for key, value in kwargs.items():
            try:
                # Check if the key exists in the configuration
                if key not in check_functions.keys():
                    raise KeyError(f"{key} is not an argument in configuration file. Maybe you should check your spelling :)")
                try:
                    result = check_functions[key](value)
                    if self.verbose:
                        print(result[0])  # Print the validation result if verbose mode is on
                    self.config_for_line[key] = result[1]
                except (TypeError, ValueError) as e:
                    print(f'Error: {e}')  # Print any validation errors

            except KeyError as e:
                # This catches the KeyError from above if the key is not in json_keys
                print(f"Error has occurred. \n {e}")
    
    def __extend_line_config(self):
        """
        Extends the line configuration parameters by reading from a configuration file and applying default values where necessary.

        This method reads a configuration file specified by `self.file_path_name_to_conf_for_line`,
        and extends the line configuration parameters in `self.config_for_line` to match the length
        of the `end_point` parameter. If a parameter is not fully specified, it uses default values
        from the configuration file.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Raises:
        -------
        FileNotFoundError
            If the configuration file specified by `self.file_path_name_to_conf_for_line` does not exist.
        json.JSONDecodeError
            If the configuration file is not a valid JSON file.

        Attributes:
        ----------
        self.file_path_name_to_conf_for_line : str
            The file path to the configuration file containing default line configuration parameters.
        self.config_for_line : dict
            A dictionary containing the current line configuration parameters.

        Notes:
        ------
        - The method reads the configuration file and extends each parameter in `self.config_for_line`
        to match the length of the `end_point` parameter.
        - If a parameter is not fully specified, it uses the default value from the configuration file.
        - The `__extend_parameters` method is used to extend each parameter.

        Example:
        --------
        Assuming `self.file_path_name_to_conf_for_line` points to a valid JSON configuration file and
        `self.config_for_line` is partially populated, calling `self.__extend_line_config()` will extend
        all parameters in `self.config_for_line` to match the length of `end_point`, using default values
        from the configuration file where necessary.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        with open(self.file_path_name_to_conf_for_line, "r", encoding="utf-8") as file:
            config = js.load(file)
        quant = len(self.config_for_line["end_point"])
        self.config_for_line["start_point"] = self.__extend_parameters(self.config_for_line["start_point"], quant, config["start_point"][0])
        self.config_for_line["line_color"] = self.__extend_parameters(self.config_for_line["line_color"], quant, config["line_color"][0])
        self.config_for_line["line_ls"] = self.__extend_parameters(self.config_for_line["line_ls"], quant, config["line_ls"][0])
        self.config_for_line["labels"] = self.__extend_parameters(self.config_for_line["labels"], quant, config["labels"][0])
        self.config_for_line["text"] = self.__extend_parameters(self.config_for_line["text"], quant, config["text"][0])
        self.config_for_line["text_pos"] = self.__extend_parameters(self.config_for_line["text_pos"], quant, config["text_pos"][0])
        self.config_for_line["subplot_pos_line"] = self.__extend_parameters(self.config_for_line["subplot_pos_line"], quant, config["subplot_pos_line"][0])
        self.config_for_line["line_alpha"] = self.__extend_parameters(self.config_for_line["line_alpha"], quant, config["line_alpha"][0])
        self.config_for_line["line_width"] = self.__extend_parameters(self.config_for_line["line_width"], quant, config["line_width"][0])
        self.config_for_line["text_rotation"] = self.__extend_parameters(self.config_for_line["text_rotation"], quant, config["text_rotation"][0])
        self.config_for_line["text_color"] = self.__extend_parameters(self.config_for_line["text_color"], quant, config["text_color"][0])
        self.config_for_line["text_font_size"] = self.__extend_parameters(self.config_for_line["text_font_size"], quant, config["text_font_size"][0])

    def __draw_lines_after_conf(self):
        """
        Draws lines on the specified subplots based on the configured line parameters.

        This method iterates through the configured line parameters in `self.config_for_line` and draws
        lines on the corresponding subplots. It skips any lines that are configured for subplots that
        do not exist.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Attributes:
        ----------
        self.config_for_line : dict
            A dictionary containing the line configuration parameters.
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings, including subplot settings.
        self.ax : list of list of Axes
            A 2D list of matplotlib Axes objects representing the subplots.

        Notes:
        ------
        - The method iterates through the `end_point` parameter to determine the number of lines to draw.
        - It calculates the subplot position (x, y) based on the `subplot_pos_line` parameter.
        - It uses the `plot` method of the matplotlib Axes object to draw the lines with the specified parameters.
        - If the `subplot_pos_line` index is greater than or equal to the number of subplots, the line is skipped.

        Example:
        --------
        Assuming `self.config_for_line` is properly configured and `self.ax` is a 2D list of Axes objects,
        calling `self.__draw_lines_after_conf()` will draw lines on the corresponding subplots based on the
        configured parameters.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        for i in range(len(self.config_for_line["end_point"])):
            if self.config_for_line["subplot_pos_line"][i] >= self.number_of_subplots:
                continue
            x = (self.config_for_line["subplot_pos_line"][i]) % self.config['subplots_settings'][0]['rows_cols'][1]
            y = (self.config_for_line["subplot_pos_line"][i]) // self.config['subplots_settings'][0]['rows_cols'][1]
            self.ax[y][x].plot([self.config_for_line["start_point"][i][0], self.config_for_line["end_point"][i][0]],
                                [self.config_for_line["start_point"][i][1], self.config_for_line["end_point"][i][1]],
                                 color=self.config_for_line["line_color"][i], alpha=self.config_for_line["line_alpha"][i],
                                 lw=self.config_for_line["line_width"][i], ls=self.config_for_line["line_ls"][i], label=self.config_for_line["labels"][i])
    
    def __draw_text_efter_conf(self):
        """
        Draws text on the specified subplots based on the configured text parameters.

        This method iterates through the configured text parameters in `self.config_for_line` and draws
        text on the corresponding subplots. It skips any text that is configured for subplots that
        do not exist.

        Arguments:
        ----------
        None

        Returns:
        -------
        None

        Attributes:
        ----------
        self.config_for_line : dict
            A dictionary containing the text configuration parameters.
        self.number_of_subplots : int
            The total number of subplots available.
        self.config : dict
            A dictionary containing configuration settings, including subplot settings.
        self.ax : list of list of Axes
            A 2D list of matplotlib Axes objects representing the subplots.

        Notes:
        ------
        - The method iterates through the `end_point` parameter to determine the number of text elements to draw.
        - It calculates the subplot position (x, y) based on the `subplot_pos_line` parameter.
        - It uses the `text` method of the matplotlib Axes object to draw the text with the specified parameters.
        - If the `subplot_pos_line` index is greater than or equal to the number of subplots, the text is skipped.
        - The `__prepare_text_position` method is called to prepare the text position before drawing.

        Example:
        --------
        Assuming `self.config_for_line` is properly configured and `self.ax` is a 2D list of Axes objects,
        calling `self.__draw_text_efter_conf()` will draw text on the corresponding subplots based on the
        configured parameters.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        for i in range(len(self.config_for_line["end_point"])):
            if self.config_for_line["subplot_pos_line"][i] >= self.number_of_subplots:
                continue
            x = (self.config_for_line["subplot_pos_line"][i]) % self.config['subplots_settings'][0]['rows_cols'][1]
            y = (self.config_for_line["subplot_pos_line"][i]) // self.config['subplots_settings'][0]['rows_cols'][1]
            self.__prepare_text_position(i, x, y)
            self.ax[y][x].text(x=self.config_for_line["text_pos"][i][0], y=self.config_for_line["text_pos"][i][1],
                                rotation=self.config_for_line["text_rotation"][i], s=self.config_for_line["text"][i],
                                fontsize=self.config_for_line["text_font_size"][i], color=self.config_for_line["text_color"][i])
    
    def __prepare_text_position(self, index, x, y):
        """
        Prepares the text position for a given subplot based on the configured parameters.

        This method calculates the appropriate x and y positions for the text based on the current
        configuration and the limits of the subplot axes. If the x or y position is not specified
        (i.e., set to `False`), it calculates a default position.

        Arguments:
        ----------
        index : int
            The index of the text configuration in `self.config_for_line`.
        x : int
            The x-coordinate of the subplot in the grid.
        y : int
            The y-coordinate of the subplot in the grid.

        Returns:
        -------
        None

        Attributes:
        ----------
        self.config_for_line : dict
            A dictionary containing the text configuration parameters.
        self.ax : list of list of Axes
            A 2D list of matplotlib Axes objects representing the subplots.

        Notes:
        ------
        - If the x position is not specified (`False`), it sets the x position to the midpoint of the x-axis limits.
        - If the y position is not specified (`False`), it calculates the y position based on the slope and intercept
        of the line defined by the start and end points. If the line is vertical, it sets the y position to the
        midpoint of the y-axis limits.
        - The method adjusts the y position by a small step to ensure the text is not placed directly on the line.

        Example:
        --------
        Assuming `self.config_for_line` is properly configured and `self.ax` is a 2D list of Axes objects,
        calling `self.__prepare_text_position(index, x, y)` will prepare the text position for the specified
        subplot based on the configured parameters.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        if self.config_for_line["text_pos"][index][0] == False:
            xlims = self.ax[y][x].get_xlim()
            self.config_for_line["text_pos"][index][0] = (xlims[1] + xlims[0]) / 2
        ylims = self.ax[y][x].get_ylim()
        if self.config_for_line["text_pos"][index][1] == False:
            if self.config_for_line["end_point"][index][0] - self.config_for_line["start_point"][index][0] != 0:
                k = (self.config_for_line["end_point"][index][1] - self.config_for_line["start_point"][index][1]) / (self.config_for_line["end_point"][index][0] - self.config_for_line["start_point"][index][0])
                b = self.config_for_line["end_point"][index][1] - k * self.config_for_line["end_point"][index][0]
                step = (ylims[1] - ylims[0]) / len(self.ax[y][x].get_yticks())
                step /= 4
                self.config_for_line["text_pos"][index][1] = k * self.config_for_line["text_pos"][index][0] + b + step
            else:
                self.config_for_line["text_pos"][index][1] = (ylims[1] + ylims[0]) / 2
    
    def change_config_file(self, file_path_name_to_conf):
        """
        Changes the configuration file for the plot settings.

        This method updates the configuration file path and loads the new configuration settings from the specified file.
        It then closes the current plot, creates new subplots based on the new configuration, and prepares the axes.

        Arguments:
        ----------
        file_path_name_to_conf : str
            The path to the new configuration file.

        Returns:
        -------
        None

        Attributes:
        ----------
        self.file_path_name_to_conf : str
            The path to the current configuration file.
        self.config : dict
            The dictionary containing the configuration settings loaded from the file.
        self.plt : matplotlib.pyplot
            The matplotlib pyplot object used for plotting.
        self.fig : matplotlib.figure.Figure
            The figure object containing the subplots.
        self.ax : numpy.ndarray
            The array of Axes objects in the figure.

        Notes:
        ------
        - The method reads the configuration file using the `json` module.
        - It closes the current plot using `self.plt.close()`.
        - It creates new subplots based on the 'rows_cols' settings in the configuration file.
        - It calls the `__prepare_axes` method to prepare the axes for the new subplots.

        Example:
        --------
        ```python
        self.change_config_file('new_config.json')
        ```
        This will update the configuration file to 'new_config.json', close the current plot, create new subplots,
        and prepare the axes based on the new configuration.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.file_path_name_to_conf = file_path_name_to_conf
        with open(self.file_path_name_to_conf, "r", encoding="utf-8") as file:
            self.config = js.load(file)
        self.plt.close()
        self.fig, self.ax = self.plt.subplots(nrows=self.config['subplots_settings'][0]['rows_cols'][0], ncols=self.config['subplots_settings'][0]['rows_cols'][1])
        self.__prepare_axes()
        self.curves_settings = []
        self.subplots_settings = []
        self.colorbars = []
        self.__config_files_changes[0] = True

    def change_config_for_lines_file(self, name_of_config_file):
        """
        Changes the configuration file for the line settings.

        This method updates the configuration file path for line settings and loads the new configuration settings from the specified file.

        Arguments:
        ----------
        name_of_config_file : str
            The path to the new configuration file for line settings.

        Returns:
        -------
        None

        Attributes:
        ----------
        self.file_path_name_to_conf_for_line : str
            The path to the current configuration file for line settings.
        self.config_for_line : dict
            The dictionary containing the configuration settings for lines loaded from the file.

        Notes:
        ------
        - The method reads the configuration file using the `json` module.

        Example:
        --------
        ```python
        self.change_config_for_lines_file('new_line_config.json')
        ```
        This will update the configuration file for line settings to 'new_line_config.json' and load the new settings.

        Inspiration:
        ------------
        From various music tracks discovered via Spotify.
        """

        self.file_path_name_to_conf_for_line = name_of_config_file
        with open(self.file_path_name_to_conf_for_line, "r", encoding="utf-8") as file:
            self.config_for_line = js.load(file)  
        self.__config_files_changes[1] = True