'''ToDo: 
1. add comments for __check_logarithmic_scaling
2. add possible arguments for subpplots_settings parameters (so we can change only one of them) (functions to change __check_...)
3. add figure_size to subpplots_settings parameter
4. rewrite the comment for __check_axes_titles (now we have option for barcharts).
5. rewrite the comment for __check_subplots_titles_font_size, __check_axes_number_of_small_ticks, __check_axes_font_size. (and some others)
10.make check for number of titles for axes if one of the data presented on them is 3d graph
11. make option to choose colormap
'''
import json as js
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as ticker

class Earl:
    def __init__(self, file_path_name_to_conf="./../settings/configuration.json", verbose=True, **kwargs):
        self.file_path_name_to_conf = file_path_name_to_conf
        with open(self.file_path_name_to_conf, 'r', encoding='utf-8') as file:
            self.config = js.load(file)
        self.plt = plt
        self.fig, self.axes = self.plt.subplots(nrows=self.config['subplots_settings'][0]['rows_cols'][0], ncols=self.config['subplots_settings'][0]['rows_cols'][1])
        self.quant = 0
        self.number_of_subplots = 0
        self.curves_settings = []
        self.subplots_settings = []
        self.verbose = verbose
    def save_plot(self, name="graph.png"):
        self.fig.savefig(name)

    def prepare_input(self, data_array, **kwargs):
        self.quant = len(data_array)
        self.check_parameters(**kwargs)
        self.number_of_subplots = self.config['subplots_settings'][0]['rows_cols'][0] * self.config['subplots_settings'][0]['rows_cols'][1]
        self.prepare_config()
        self.construct_structure_curve(data_array)
        self.construct_structure_subplots()
    
    def plot_graph(self, data_array, **kwargs):
        self.prepare_input(data_array=data_array, **kwargs)
        #self.print_config()
        for i in range(self.number_of_subplots):
            self.print_subplot_settings(i)
        self.initial_preparation_for_subplots()
        self.plot_data_on_subplots()
        self.config_cubplots_after_plotting_data()

    def initial_preparation_for_subplots(self):
        self.plt.close()
        self.fig, self.ax = self.plt.subplots(nrows=self.config['subplots_settings'][0]['rows_cols'][0], ncols=self.config['subplots_settings'][0]['rows_cols'][1], figsize=(12, 10))
        self.colorbars = []
        for i in range(self.number_of_subplots):
            x = (i) % self.config['subplots_settings'][0]['rows_cols'][0]
            y = (i) // self.config['subplots_settings'][0]['rows_cols'][0]
            # try:
            #     fontsizes_for_axes = self.__find_proper_axes_font_size(i)
            #     fontsize_for_title_subplot = self.__find_proper_subplots_titles_font_size(i)
            #     number_axes_number_of_small_ticks = self.__find_proper_axes_number_of_small_ticks(i)
            #     fontsize_legend_font_size = self.__find_proper_legends_font_size(i)
            #     position_legend_position = self.__find_proper_legend_position(i)
            #     round_axes_round_accuracy = self.__find_proper_axes_round_accuracy(i)
            #     scaling_logarithmic_scaling = self.__find_proper_logarithmic_scaling(i)
            #     scaling_axes_scaling = self.__find_proper_axes_scaling(i)
            # except ValueError as e:
            #     print(f"You have an error: {e}")
            #     sys.exit(1)
            #set titles and their sizes
            self.ax[y][x].set_xlabel(self.subplots_settings[i]["axes_titles"][0], loc="center", fontsize=self.subplots_settings[i]["axes_font_size"][0])
            self.ax[y][x].set_ylabel(self.subplots_settings[i]["axes_titles"][1], loc="center", fontsize=self.subplots_settings[i]["axes_font_size"][1])
            self.ax[y][x].set_title(self.subplots_settings[i]["subplots_titles_text"], loc="center", fontsize=self.subplots_settings[i]["subplots_titles_font_size"])

            #set legend properties
            self.ax[y][x].legend(loc=self.subplots_settings[i]["legend_position"], frameon=False, prop={'size': self.subplots_settings[i]["legends_font_size"]})

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

            if self.subplots_settings[i]["logarithmic_scaling"][0]:
                self.ax[y][x].set_xscale("log")
            if self.subplots_settings[i]["logarithmic_scaling"][1]:
                self.ax[y][x].set_yscale("log")
            self.ax[y][x].xaxis.set_major_formatter(FormatStrFormatter(self.subplots_settings[i]["axes_round_accuracy"][0]))
            self.ax[y][x].yaxis.set_major_formatter(FormatStrFormatter(self.subplots_settings[i]["axes_round_accuracy"][1]))

            #set inital ticks properties
            self.ax[y][x].minorticks_on()
            self.ax[y][x].tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black')
            self.ax[y][x].tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black')
            self.ax[y][x].xaxis.set_minor_locator(ticker.AutoMinorLocator(self.subplots_settings[i]["axes_number_of_small_ticks"][0]))
            self.ax[y][x].yaxis.set_minor_locator(ticker.AutoMinorLocator(self.subplots_settings[i]["axes_number_of_small_ticks"][1]))
            self.ax[y][x].tick_params(direction ='in', length=5, width=1.5)

            #set grid
            self.ax[y][x].grid(color="#7a7c7d", linewidth=0.3)
            self.ax[y][x].grid(which='minor', color='#7a7c7d', linestyle=':', linewidth=0.2)

        self.fig.align_labels()
        self.fig.align_titles()
        self.fig.tight_layout()
    
    def plot_data_on_subplots(self):
        for i in range(self.quant):
            x = (self.curves_settings[i]["subplot_position"]) % self.config['subplots_settings'][0]['rows_cols'][0]
            y = (self.curves_settings[i]["subplot_position"]) // self.config['subplots_settings'][0]['rows_cols'][0]
            if self.curves_settings[i]["graph_type"] == 1:
                self.plot_2d_graph(i, x, y)
            elif self.curves_settings[i]["graph_type"] == 2:
                self.plot_3d_graph(i, x, y)
    
    def plot_2d_graph(self, index, x, y):
        x_data = self.curves_settings[index]["data"][0][0]
        y_data = self.curves_settings[index]["data"][1][0]
        color = self.curves_settings[index]["color"]
        ls = self.curves_settings[index]["ls"]
        marker_shape = self.curves_settings[index]["marker_shape"]
        marker_size = self.curves_settings[index]["marker_size"]
        lw = self.curves_settings[index]["line_width"]
        alpha = self.curves_settings[index]["line_alpha"]
        label = self.curves_settings[index]["label"]
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
    
    def plot_3d_graph(self, index, x, y):
        self.colorbars.append([0, 0])
        self.colorbars[-1][0] = self.ax[y][x].pcolormesh(self.curves_settings[index]["data"][0], self.curves_settings[index]["data"][1], self.curves_settings[index]["data"][2], vmin=np.min(self.curves_settings[index]["data"][2]), vmax=np.max(self.curves_settings[index]["data"][2]), shading='gouraud', cmap='plasma')
        self.colorbars[-1][1] = self.fig.colorbar(self.colorbars[-1][0], ax=self.ax[y][x], label=self.subplots_settings[self.curves_settings[index]["subplot_position"]]["axes_titles"][2])
        #b.set_label(titles[2])
    def config_cubplots_after_plotting_data(self):
        for i in range(self.number_of_subplots):
            x = (i) % self.config['subplots_settings'][0]['rows_cols'][0]
            y = (i) // self.config['subplots_settings'][0]['rows_cols'][0]
            try:
                fontsize_legend_font_size = self.__find_proper_legends_font_size(i)
                position_legend_position = self.__find_proper_legend_position(i)
            except ValueError as e:
                print(f"You have an error: {e}")
                sys.exit(1)
            #set legend properties
            self.ax[y][x].legend(loc=position_legend_position, frameon=False, prop={'size': fontsize_legend_font_size})

    
    def __config_parameters_for_stretch_option(self, index): #Inspiration: songs from author Nico Santos
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
        self.min_number[0] = self.subplots_settings[index]["axes_scaling"][1][0][0]
        self.min_number[1] = self.subplots_settings[index]["axes_scaling"][1][1][0]
        self.max_number[0] = self.subplots_settings[index]["axes_scaling"][1][0][1]
        self.max_number[1] = self.subplots_settings[index]["axes_scaling"][1][1][1]
        self.steps[0] = self.subplots_settings[index]["axes_scaling"][1][0][2]
        self.steps[1] = self.subplots_settings[index]["axes_scaling"][1][1][2]

    def __find_min_max_element(self, index):
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
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_font_size"][i][0] == index:
                return self.config["axes_font_size"][i][1]
            elif self.config["axes_font_size"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have fontsize for these axes titles of subplot {i} or fontsize for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_font_size"][flag_minus_one][1]
    
    def __find_proper_subplots_titles_font_size(self, index):
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["subplots_titles_font_size"][i][0] == index:
                return self.config["subplots_titles_font_size"][i][1]
            elif self.config["subplots_titles_font_size"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have fontsize for title for these subplot {i} or fontsize for all subplots. ([x, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["subplots_titles_font_size"][flag_minus_one][1]        
    
    def __find_proper_axes_number_of_small_ticks(self, index):
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_number_of_small_ticks"][i][0] == index:
                return self.config["axes_number_of_small_ticks"][i][1]
            elif self.config["axes_number_of_small_ticks"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have number of small ticks for these axes titles of subplot {i} or number of small ticks for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_number_of_small_ticks"][flag_minus_one][1]

    def __find_proper_legends_font_size(self, index):
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["legends_font_size"][i][0] == index:
                return self.config["legends_font_size"][i][1]
            elif self.config["legends_font_size"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have legend fontsize for these subplot {i} or legend fontsize for all subplots. ([x, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["legends_font_size"][flag_minus_one][1] 

    def __find_proper_legend_position(self, index):
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["subplots_legend_position"][i][0] == index:
                return self.config["subplots_legend_position"][i][1]
            elif self.config["subplots_legend_position"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have legend position for title for these subplot {i} or legend position for all subplots. ([x, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["subplots_legend_position"][flag_minus_one][1] 

    def __find_proper_axes_round_accuracy(self, index):
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_round_accuracy"][i][0] == index:
                return self.config["axes_round_accuracy"][i][1]
            elif self.config["axes_round_accuracy"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have element axes_round_accuracy for these subplot {i} or axes_round_accuracy for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_round_accuracy"][flag_minus_one][1]

    def __find_proper_logarithmic_scaling(self, index):
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["logarithmic_scaling"][i][0] == index:
                return self.config["logarithmic_scaling"][i][1]
            elif self.config["logarithmic_scaling"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have argument for logarithmic_scaling for these axes titles of subplot {i} or one logarithmic_scaling argument for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["logarithmic_scaling"][flag_minus_one][1]
        
    def __find_proper_axes_scaling(self, index):
        flag_minus_one = -1 #-1 meens that there is no item with value -1 in position of subplot index
        for i in range(self.number_of_subplots):
            if self.config["axes_scaling"][i][0] == index:
                return self.config["axes_scaling"][i][1:]
            elif self.config["axes_scaling"][i][0] == -1:
                flag_minus_one = i
        if flag_minus_one == -1:
            raise ValueError(f"you don't have argument for axes_scaling for these axes titles of subplot {i} or one logarithmic_scaling argument for all subplots. ([x, [y, y]] x - is index of subplot, if x == -1 these means that it will be used for all subplots that don't have theor own settings. To overcome these problem you have to check you arguments.)")
        else:
            return self.config["axes_scaling"][flag_minus_one][1:]
            
    def check_parameters(self, **kwargs):
        """
        Validate plot parameters passed as keyword arguments against predefined checks.

        This method iterates through the provided keyword arguments, ensuring each parameter 
        exists in the configuration and then validates its value using specific check functions.

        Args:
            **kwargs: Arbitrary keyword arguments representing plot parameters to be validated.

        Raises:
            KeyError: If a provided parameter key does not exist in the configuration.
            TypeError or ValueError: If the parameter value fails validation by its check function.

        Note:
            - `self.config.keys()` contains all acceptable parameter keys from the configuration.
            - `self.verbose` when True, prints validation results for each parameter.
        """
        json_keys = self.config.keys()
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
            "logarithmic_scaling": self.__check_logarithmic_scaling
        }

        for key, value in kwargs.items():
            try:
                # Check if the key exists in the configuration
                if key not in json_keys:
                    raise KeyError(f"{key} is not an argument in configuration file. Maybe you should check your spelling :)")
                
                # Attempt to validate the value with the appropriate check function
                try:
                    result = check_functions[key](value)
                    if self.verbose:
                        print(result[0])  # Print the validation result if verbose mode is on
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

        Args:
            colors: Either a string representing a single color or a list of strings for multiple colors.

        Returns:
            tuple: A tuple containing a success message and a list with the validated color(s).

        Raises:
            TypeError: If the color(s) provided are not in the expected format (str or list of str).
            ValueError: If any color string does not adhere to the hex color format.

        Inspiration: Bi-2's "Event Horizon" playlist.
        """
        if not isinstance(colors, (list, str)):
            raise TypeError(f"Color argument is incorrect. It should be a list with color codes as string or one color as string for all data.")
        if isinstance(colors, str):
            if colors[0] == "#" and len(colors) == 7:
                return [f"Color argument is correct", [colors]]
            else:
                raise ValueError(f"Color has incorrect code. It should be presented in the way like #XXXXXX, where X is numbers (0, ... 9) or letters from A to F. You can use this site https://csscolor.ru/ to get the right colot code.")
        elif isinstance(colors, list):
            for i in range(len(colors)):
                if not isinstance(colors[i], str):
                    raise TypeError(f"Color argument number {i} ({colors[i]}) is incorrect. It should be a string.")
                if not (colors[i][0] == "#" and len(colors[i]) == 7):
                    raise ValueError(f"Color number {i} ({colors[i]}) has incorrect code. It should be presented in the way like #XXXXXX, where X is numbers (0, ... 9) or letters from A to F. You can use this site https://csscolor.ru/ to get the right colot code.")
            return [f"Color argument is correct", colors]
        
    def __check_ls(self, ls):
        """
        Validate line style (ls) for plotting, ensuring it's a recognized matplotlib style.

        This function verifies if the line style input is either a string for a single style 
        or a list of strings for multiple styles. Accepted styles are "-", "--", "-.", ":", and "".

        Args:
            ls: Either a string representing a single line style or a list of strings for multiple styles.

        Returns:
            tuple: A tuple containing a success message and a list with the validated line style(s).

        Raises:
            TypeError: If the line style(s) provided are not in the expected format (str or list of str).
            ValueError: If any line style does not match the recognized styles.

        Inspiration: Bi-2's "Event Horizon" playlist.
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

        Args:
            marker_shape: Either a string for a single marker shape or a list of strings for multiple shapes.

        Returns:
            tuple: A tuple containing a success message and the validated marker shape(s) as a list.

        Raises:
            TypeError: If the marker shape(s) provided are not in the expected format (str or list of str).
            ValueError: If any marker shape does not match the recognized marker styles.

        Inspiration: Bi-2's "Event Horizon" playlist.
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
        a list specifying font sizes for individual subplots in the format [subplot_number, [x_axis_size, y_axis_size]].

        Args:
            axes_font_size: An integer for uniform font size or a list for customized sizes per subplot.

        Returns:
            tuple: A tuple with a success message and the validated font size configuration.

        Raises:
            TypeError: If the axes_font_size argument is not in the correct format.
            ValueError: If the structure or values within axes_font_size are incorrect.

        Inspiration: "Kukoriki" series, episodes "Syr-Bor, New Year's", "A Place in History".
        """
        text_that_explain_structure = " The structure of one element is [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot)"
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
                elif len(axes_font_size[i][1]) != 2:
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i][1]}) should have two elements.' + text_that_explain_structure)
                elif len(axes_font_size[i][1]) == 2:
                    for j in range(2):
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

        Args:
            subplots_titles_font_size: An integer for uniform title font size or a list for varied sizes.

        Returns:
            tuple: A tuple with a success message and the validated font sizes.

        Raises:
            TypeError: If subplots_titles_font_size is not an integer or list of integers.
            ValueError: If any font size provided is not positive or if the list contains non-integer values.

        Inspiration: "Kukoriki" series, episode "The case of the missing rake".
        """
        text_that_explain_structure = '''The structure is [x, y] (x - number of subplot or -1 (for all subplots that aren't called), y - number - size of font for title for x subplot)'''
        if not isinstance(subplots_titles_font_size, (list, int)):
            raise TypeError(f"legends_font_size argument is incorrect. It should be a list with elements like [x, y] (x - number of subplot, y - number - size of font for title for x subplot) or one number for all titles fonts")
        if isinstance(subplots_titles_font_size, int):
            return (f"legend argument is correct", [-1, subplots_titles_font_size])
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

        Args:
            subplots_titles_text: A string for a uniform title or a list of strings for varied titles.

        Returns:
            tuple: A tuple with a confirmation message and the list of validated titles.

        Raises:
            TypeError: If subplots_titles_text is not a string or list of strings.
            ValueError: If any element in the list is not a string.

        Inspiration: From various music tracks discovered via Spotify.
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

        Args:
            legends_font_size: An integer for uniform legend font size or a list for customized sizes per subplot.

        Returns:
            tuple: A tuple with a success message and the validated legend font size configuration.

        Raises:
            TypeError: If legends_font_size or its elements are not in the expected format.
            ValueError: If the structure or values within legends_font_size are incorrect or invalid.
        
        Inspiration: From various music tracks discovered via Spotify.
        """
        text_that_explain_structure = '''The structure is [x, y] (x - number of subplot or -1 (for all subplots that aren't called), y - number - size of font for legend for x subplot)'''
        if not isinstance(legends_font_size, (list, int)):
            raise TypeError(f"legends_font_size argument is incorrect." + text_that_explain_structure)
        if isinstance(legends_font_size, int):
            return (f"legend argument is correct", [-1, legends_font_size])
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

        Args:
            marker_size: An integer for uniform marker size or a list of integers for varied sizes.

        Returns:
            tuple: A tuple with a success message and the validated marker sizes.

        Raises:
            TypeError: If marker_size is not an integer or list of integers.
            ValueError: If any marker size provided is not positive or if the list contains non-integer values.

        Inspiration: From various music tracks discovered via Spotify.
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

        Checks if line widths are provided as a single positive float for all lines or 
        a list of positive floats for individual line widths.

        Args:
            line_width: A float for uniform line width or a list of floats for varied widths.

        Returns:
            tuple: A tuple with a success message and the validated line widths.

        Raises:
            TypeError: If line_width is not a float or list of floats.
            ValueError: If any line width provided is not positive or if the list contains non-float values.
        
        Inspiration: From various music tracks discovered via Spotify.
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

        Args:
            alpha: A float/int or list of floats/ints representing line transparency (0.0 to 1.0).

        Returns:
            tuple: A tuple with a success message and the validated alpha value(s).

        Raises:
            TypeError: If alpha is not a float, int, or list of these types.
            ValueError: If any alpha value is not within the range of 0 to 1.

        Inspiration: From various music tracks discovered via Spotify.
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
        for uniform rounding or a list specifying rounding for individual subplots.

        Args:
            axes_round_accuracy: A string for uniform rounding or a list for customized rounding per subplot.

        Returns:
            tuple: A tuple with a success message and the validated rounding configuration.

        Raises:
            TypeError: If axes_round_accuracy or its elements are not in the expected format.
            ValueError: If the structure or values within axes_round_accuracy are incorrect.

        Inspiration: From various music tracks discovered via Spotify.
        """
        text_to_explain_structure = '''The structure is [x, [y, y]] (x - number of subplot, y - string like "%0.xf", where x shows to which decimal number should be rounded)'''
        if not isinstance(axes_round_accuracy, (list, str)):
            raise TypeError(f"axes_round_accuracy argument is incorrect." + text_to_explain_structure +  " or one number for all axes fonts")
        if isinstance(axes_round_accuracy, str):
            if not all([axes_round_accuracy[0] == '%' and axes_round_accuracy[1] == '0' and axes_round_accuracy[2] == '.']):
                    raise ValueError(f'axes_round_accuracy argument number should be presented like y - string like "%0.xf", where x shows to which decimal number should be rounded')
            return (f"axes_round_accuracy argument is correct", [-1, [axes_round_accuracy, axes_round_accuracy]])
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

        Args:
            subplots_settings: A list containing a dictionary with subplot configuration.

        Returns:
            tuple: A tuple with a success message and the validated subplot settings.

        Raises:
            TypeError: If subplots_settings is not a dictionary or if its elements are not in the expected format.
            ValueError: If required keys are missing or if the values do not match expected types or ranges.
        
        Inspiration: From various music tracks discovered via Spotify.
        """
        subplots_settings = subplots_settings[0]
        if not isinstance(subplots_settings, dict):
            raise TypeError(f"subplots_settings should be dictionary.")
        if not ("rows_cols" in subplots_settings.keys()):
            raise ValueError(f"rows_cols should be a key in subplots_settings")
        elif not ("subplots_distribution" in subplots_settings.keys()):
            raise ValueError(f"subplots_distribution should be a key in subplots_settings")
        elif not isinstance(subplots_settings["rows_cols"], list):
            raise ValueError(f"rows_cols should be a list with two integer elements: numbers of rows and number of columns in your subplot.")
        elif len(subplots_settings["rows_cols"]) != 2:
            raise ValueError(f"rows_cols should have two integer elements: numbers of rows and number of columns in your subplot.")
        elif not (isinstance(subplots_settings["rows_cols"][0], int) and isinstance(subplots_settings["rows_cols"][1], int)):
            raise ValueError(f"rows_cols elements should be integer.")
        elif not isinstance(subplots_settings["subplots_distribution"], list):
            raise ValueError(f"subplots_distribution should be a list with elements (0, 1, ... ). The index of the element responds to the index of the the data in your data_array, the value of the element responds to the index of the subplot.")
        elif isinstance(subplots_settings["subplots_distribution"], list):
            for i in range(len(subplots_settings["subplots_distribution"])):
                if not isinstance(subplots_settings["subplots_distribution"][i], int):
                    raise ValueError(f"subplots_distribution elements should be integer (problem with element {i} ({subplots_settings['subplots_distribution'][i]})).")
                elif subplots_settings["subplots_distribution"][i] < 0:
                    raise ValueError(f"subplots_distribution elements should be more than 0 (problem with element {i} ({subplots_settings['subplots_distribution'][i]})).")
        return (f"subplots_settings argument is correct", [subplots_settings])
    
    def __check_graph_types(self, graph_types):
        """
        Validate the type of graph for plotting.

        Checks if the graph type is either a single string or a list of strings representing 
        whether the graph should be 2D or 3D.

        Args:
            graph_types: A string or list of strings indicating graph types ('2D' or '3D').

        Returns:
            tuple: A tuple with a success message and the validated graph type(s).

        Raises:
            TypeError: If graph_types is not a string or list of strings.
            ValueError: If any graph type provided is not '2D' or '3D'.

        Inspiration: From various music tracks discovered via Spotify.
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

        Args:
            axes_scaling: A list where each element describes the scaling for one subplot.

        Returns:
            tuple: A tuple with a confirmation message and the validated axes_scaling configuration.

        Raises:
            TypeError: If axes_scaling is not a list or if its elements are not structured as expected.
            ValueError: If the structure or values within axes_scaling do not match the defined format.
        
        Inspiration: From various music tracks discovered via Spotify.
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

        Args:
            axes_number_of_small_ticks: An integer or a list of lists [x, y] where x and y are integers.

        Returns:
            tuple: A tuple with a success message and the validated configuration.

        Raises:
            TypeError: If axes_number_of_small_ticks is not an integer or list, or contains non-integer values.
            ValueError: If any number of small ticks is less than 1 or if the list structure is incorrect.
        
        Inspiration: From various music tracks discovered via Spotify. (Sia, Diplo, Labrinth, LSD "Genius"; Normal Tale "Кисточка")
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

        Args:
            labels: A string or list of strings representing labels for data series.

        Returns:
            tuple: A tuple with a confirmation message and the validated labels.

        Raises:
            TypeError: If labels is neither a string nor a list of strings.

        Inspiration: From various music tracks discovered via Spotify.
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

        Args:
            axes_titles: A string or list where each element is a list of two strings for axis titles.

        Returns:
            tuple: A tuple with a success message and the validated axes titles configuration.

        Raises:
            TypeError: If axes_titles is not a string or list.
            ValueError: If the structure within the list does not match the expected format.

        Inspiration: From various music tracks discovered via Spotify.
        """
        if not isinstance(axes_titles, (list, str)):
            raise TypeError(f"axes_titles should be a list, where each element is a list [\"X\", \"Y\"], \"X\"(\"Y\") ([\"X\", \"Y\", \"B\"])- titles for axes (\"B\" - title for barchart). Index of the element is relevant to the index of the plot is the same as the index of each list.")
        if isinstance(axes_titles, str):
            return (f"axes_titles argument is correct.", [axes_titles])
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
        acceptable legend position strings.

        Args:
            subplots_legend_position: A string or list of strings representing legend positions.

        Returns:
            tuple: A tuple with a confirmation message and the validated legend positions.

        Raises:
            TypeError: If subplots_legend_position is not a string or list of strings.
            ValueError: If any legend position string is not among the recognized positions.

        Possible legend positions include:
        - 'best'
        - 'upper right', 'upper left', 'lower left', 'lower right'
        - 'right', 'center left', 'center right'
        - 'lower center', 'upper center', 'center'
        - 'outside' (interpreted as 'center right' for placement outside the plot)
        
        Inspiration: "Kukoriki" series, episode "Mr. Window Dresser".
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
            return (f"subplots_legend_position argument is correct", [-1, subplots_legend_position])
        
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
        text_that_explain_structure = '''The structure of one element is [x, [y, y]] (x - number of subplot, y - number - 0 or 1 (0 - normal scaling, 1 - logarithmic scaling))'''
        if not isinstance(logarithmic_scaling, (list, int)):
            raise TypeError(f"logarithmic_scaling argument is incorrect." + text_that_explain_structure + " or one number (0 / 1) for all axes.")
        if isinstance(logarithmic_scaling, int):
            return (f"logarithmic_scaling argument is correct", [-1, logarithmic_scaling])
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
        
    def __check_data_and_graph_type_are_correlated(self, index):
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
                    
    def construct_structure_curve(self, data_array):
        """Constructs and populates the structure for curve settings.

        This method iterates through the specified number of curves (`self.quant`)
        and creates a dictionary for each curve to store its visual settings.
        These settings are derived from the provided `data_array` and the
        configuration dictionary `self.config`. The constructed dictionaries are
        appended to the `self.curves_settings` list.

        Args:
            data_array (list or numpy.ndarray): A list or array containing the data for each curve.
                Each element in `data_array` corresponds to the data for a single curve,
                and the order should align with the curve configurations in `self.config`.

        Returns:
            None. The method modifies the `self.curves_settings` attribute in place.

        Attributes:
            quant (int): The number of curves to be plotted.
            config (dict): A dictionary containing configuration settings for curves and subplots.
                It is expected to have keys such as "graph_types", "color", "ls", "marker_shape",
                "marker_size", "labels", "line_width", "line_alpha", and "subplots_settings".
            curves_settings (list): A list to store dictionaries, where each dictionary holds
                the settings for a single curve. This list is populated by this method.
        """
        graph_pos_types = {"2D":1, "3D":2}
        index = 0
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
                    print(f'Error: {e}')  # Print any validation errors

            
    def construct_structure_subplots(self):
        """Constructs and populates the structure for subplot settings.

        This method iterates through the specified number of subplots
        (`self.number_of_subplots`) and creates a dictionary for each subplot
        to store its visual settings. These settings are derived from the
        configuration dictionary `self.config`. The constructed dictionaries are
        appended to the `self.subplots_settings` list.

        Args:
            None.

        Returns:
            None. The method modifies the `self.subplots_settings` attribute in place.

        Attributes:
            number_of_subplots (int): The number of subplots to be created.
            config (dict): A dictionary containing configuration settings for subplots.
                It is expected to have keys such as "axes_font_size", "subplots_titles_font_size",
                "subplots_titles_text", "legends_font_size", "axes_scaling",
                "axes_round_accuracy", "axes_number_of_small_ticks", "axes_titles",
                and "subplots_legend_position".
            subplots_settings (list): A list to store dictionaries, where each dictionary holds
                the settings for a single subplot. This list is populated by this method.
        """
        for i in range(self.number_of_subplots):
            x = (i) % self.config['subplots_settings'][0]['rows_cols'][0]
            y = (i) // self.config['subplots_settings'][0]['rows_cols'][0]
            try:
                fontsizes_for_axes = self.__find_proper_axes_font_size(i)
                fontsize_for_title_subplot = self.__find_proper_subplots_titles_font_size(i)
                number_axes_number_of_small_ticks = self.__find_proper_axes_number_of_small_ticks(i)
                fontsize_legend_font_size = self.__find_proper_legends_font_size(i)
                position_legend_position = self.__find_proper_legend_position(i)
                round_axes_round_accuracy = self.__find_proper_axes_round_accuracy(i)
                scaling_logarithmic_scaling = self.__find_proper_logarithmic_scaling(i)
                scaling_axes_scaling = self.__find_proper_axes_scaling(i)
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
                                         "logarithmic_scaling": scaling_logarithmic_scaling
                                         }

            
    def prepare_config(self):
        """
        Prepares and extends the configuration parameters for plotting.

        This method takes the initial configuration (`self.config`) and extends or initializes 
        each parameter to ensure all plots have defined settings. It uses default values when 
        specific settings are not provided in the initial configuration.

        Note:
        - `self.quant` is assumed to be the quantity of data series or plots.
        - `self.number_of_subplots` is assumed to be the number of subplot areas defined in the plot layout.
        - `self.extend_parameters` is a method that extends a list to a given length with a default value if needed.
        
        Inspiration: "Kukoriki" series, episode "Oh Ye Grateful".
        """
        with open(self.file_path_name_to_conf, 'r', encoding='utf-8') as file:
            config = js.load(file)
        # Color for each data series, defaulting to a dark red if not specified
        self.config["color"] = self.extend_parameters(self.config["color"], self.quant, config["color"][0])
        
        # Line style for each data series, defaulting to solid line if not specified
        self.config["ls"] = self.extend_parameters(self.config["ls"], self.quant, config["ls"][0])
        
        # Marker shape for each data series, defaulting to circle 'o'
        self.config["marker_shape"] = self.extend_parameters(self.config["marker_shape"], self.quant, config["marker_shape"][0])
        
        # Font size for axes labels, default uniform size for all subplots
        self.config["axes_font_size"] = self.extend_parameters(self.config["axes_font_size"], self.number_of_subplots, config["axes_font_size"][0])
        
        # Font size for subplot titles, default size for all
        self.config["subplots_titles_font_size"] = self.extend_parameters(self.config["subplots_titles_font_size"], self.number_of_subplots, config["subplots_titles_font_size"][0])
        
        # Titles for subplots, with a humorous default message for many subplots
        self.config["subplots_titles_text"] = self.extend_parameters(self.config["subplots_titles_text"], self.number_of_subplots, "You are crazy if you have more than 26 subplots.")
        
        # Font size for legends, default uniform size for all subplots
        self.config["legends_font_size"] = self.extend_parameters(self.config["legends_font_size"], self.number_of_subplots, config["legends_font_size"][0])
        
        # Size of markers for each data series, default size
        self.config["marker_size"] = self.extend_parameters(self.config["marker_size"], self.quant, config["marker_size"][0])
        
        # Width of lines for each data series, default width
        self.config["line_width"] = self.extend_parameters(self.config["line_width"], self.quant, config["line_width"][0])
        
        # Transparency (alpha) for lines, default fully opaque
        self.config["line_alpha"] = self.extend_parameters(self.config["line_alpha"], self.quant, config["line_alpha"][0])
        
        # Rounding accuracy for axes numbers, default to two decimal places
        self.config["axes_round_accuracy"] = self.extend_parameters(self.config["axes_round_accuracy"], self.number_of_subplots, config["axes_round_accuracy"][0])
        
        # Distribution of subplots, default to 1 plot per subplot
        self.config["subplots_settings"][0]["subplots_distribution"] = self.extend_parameters(self.config["subplots_settings"][0]["subplots_distribution"], self.quant, config["subplots_settings"][0]["subplots_distribution"][0])
        
        # Type of graph for each data series, default to 2D
        self.config["graph_types"] = self.extend_parameters(self.config["graph_types"], self.quant, config["graph_types"][0])
        # Scaling of axes, default to slight stretch in both directions
        self.config["axes_scaling"] = self.extend_parameters(self.config["axes_scaling"], self.number_of_subplots, config["axes_scaling"][0])
        
        # Number of small ticks between major ticks, default for both axes
        self.config["axes_number_of_small_ticks"] = self.extend_parameters(self.config["axes_number_of_small_ticks"], self.number_of_subplots, config["axes_number_of_small_ticks"][0])
        
        # Labels for data series, empty by default
        self.config["labels"] = self.extend_parameters(self.config["labels"], self.quant, config["labels"][0])
        
        # Titles for axes in each subplot, default to 'X' and 'Y'
        self.config["axes_titles"] = self.extend_parameters(self.config["axes_titles"], self.number_of_subplots, config["axes_titles"][0])
        
        # Position of the legend in each subplot, default to 'best'
        self.config["subplots_legend_position"] = self.extend_parameters(self.config["subplots_legend_position"], self.number_of_subplots, config["subplots_legend_position"][0])

        #logarithmic scaling of the axes for each subplot, default not logarithm
        self.config["logarithmic_scaling"] = self.extend_parameters(self.config["logarithmic_scaling"], self.number_of_subplots, config["logarithmic_scaling"][0])
        del config

    def extend_parameters(self, parameter, quant, element_extend_by):
        if len(parameter) < quant and len(parameter) > 0:
            for i in range(len(parameter), quant):
                parameter.append(element_extend_by)
        elif len(parameter) == 0:
            parameter = [element_extend_by] * quant
        return parameter
    
    def print_curve_settings(self, curve_index):
        print(self.curves_settings[curve_index])
    def print_subplot_settings(self, subplot_index):
        print(self.subplots_settings[subplot_index])
    def print_config(self):
        print(js.dumps(self.config, indent=4, ensure_ascii=False))