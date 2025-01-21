import json as js
import numpy as np
import matplotlib.pyplot as plt

class Earl:
    def __init__(self, file_path_name_to_conf="./../settings/configuration.json", verbose=True, **kwargs):
        with open(file_path_name_to_conf, 'r', encoding='utf-8') as file:
            self.config = js.load(file)
        self.fig, self.axes = plt.subplots(nrows=self.config['subplots_settings'][0]['nrows'], ncols=self.config['subplots_settings'][0]['ncols'])
        self.quant = 0
        self.number_of_subplots = 0
        self.curves_settings = dict()
        self.subplots_settings = dict()
        self.verbose = verbose

        #self.construct_structure_for_plotting_subplots(self.config, [[]])

    def plot_graph(self, data_array, **kwargs):
        self.quant = len(data_array)
        self.number_of_subplots = self.config['subplots_settings'][0]['nrows'] * self.config['subplots_settings'][0]['ncols']
        self.config = self.check_parameters(self.config, kwargs)
        self.config = self.check_config()   
        pass

    def check_parameters(self, **kwargs):
        json_keys = self.config.keys()
        check_functions = {"color": self.__check_color, "ls": self.__check_ls,
                           "marker_shape": self.__check_marker_shape, "axes_font_size": self.__check_axes_font_size, 
                           "subplots_titles_font_size": self.__check_subplots_titles_font_size, "subplots_titles_text": self.__check_subplots_titles_text,
                           "legends_font_size": self.__check_legends_font_size, "marker_size": self.__check_marker_size,
                           "line_width": self.__check_line_width, "line_alpha": self.__check_line_alpha, 
                           "axes_round_accuracy": self.__check_axes_round_accuracy, "subplots_settings": self.__check_subplots_settings,
                           "graph_types": self.__check_graph_types, "axes_scaling": self.__check_axes_scaling,
                           "axes_number_of_small_ticks": self.__check_axes_number_of_small_ticks, "labels": self.__check_labels,
                           "axes_titles": self.__check_axes_titles, "subplots_legend_position": self.__check_subplots_legend_position}
        for key, value in kwargs.items():
            try:
                if not (key in json_keys):
                    raise KeyError(f"{key} is not an argument in configuration file. Maybe you should check your spelling :)")
                try:
                    result = check_functions[key](value)
                    if self.verbose:
                        print(result[0])
                except (TypeError, ValueError) as e:
                    print(f'Error: {e}')  
            except KeyError as e:
                print(f"Error has occured. \n {e}")

    def __check_color(self, colors): #Written with inspiration from Bi-2's "Event Horizon" playlist.
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
        
    def __check_ls(self, ls): #Written with inspiration from Bi-2's "Event Horizon" playlist.
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
        
    def __check_marker_shape(self, marker_shape): #Written with inspiration from Bi-2's "Event Horizon" playlist.
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
    
    def __check_axes_font_size(self, axes_font_size): #Written with inspiration from "Kukoriki" series, specifically episodes "Syr-Bor, New Year's", "A Place in History".
        if not isinstance(axes_font_size, (list, int)):
            raise TypeError(f"axes_font_size argument is incorrect. It should be a list with elements like [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot) or one number for all axes fonts")
        if isinstance(axes_font_size, int):
            return (f"axes_font_size argument is correct", [axes_font_size])
        elif isinstance(axes_font_size, list):
            for i in range(len(axes_font_size)):
                if not isinstance(axes_font_size[i], list):
                    raise TypeError(f'axes_font_size argument number {i} ({axes_font_size[i]}) should be list')
                elif not isinstance(axes_font_size[i][0], int):
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i]}) should have structure [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot)')
                elif not isinstance(axes_font_size[i][1], list):
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i]}) should have structure [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot)')
                elif len(axes_font_size[i][1]) != 2:
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i]}) should have structure [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot)')
                elif not (isinstance(axes_font_size[i][1][0], int) and isinstance(axes_font_size[i][1][1], int)):
                    raise ValueError(f'axes_font_size argument number {i} ({axes_font_size[i]}) should have structure [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot)')
            return (f"axes_font_size argument is correct.", axes_font_size)
    def  __check_subplots_titles_font_size(self, subplots_titles_font_size): #Written with inspiration from "Kukoriki" series, specifically episode "The case of the missing rake"
        if not isinstance(subplots_titles_font_size, (int, list)):
            raise TypeError(f'subplots_titles_font_size argument is incorrect. It should be a list with integer elements which are subplots titles font size or one integer for all plots.')
        if isinstance(subplots_titles_font_size, int):
            if subplots_titles_font_size > 0:
                return (f"subplots_titles_font_size argument is correct.", [subplots_titles_font_size])
            else:
                raise ValueError(f"subplots_titles_font_size argument should be more than 0.")
        elif isinstance(subplots_titles_font_size, list):
            for i in range(len(subplots_titles_font_size)):
                if not isinstance(subplots_titles_font_size[i], int):
                    raise ValueError(f"subplots_titles_font_size argument {i} ({subplots_titles_font_size[i]}) should be an integer.")
                elif subplots_titles_font_size[i] < 1:
                    raise ValueError(f"subplots_titles_font_size argument {i} ({subplots_titles_font_size[i]}) should be more than 0.")
            return (f"subplots_titles_font_size argument is correct.", subplots_titles_font_size)
    def __check_subplots_titles_text(self, subplots_titles_text):
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
        if not isinstance(legends_font_size, (list, int)):
            raise TypeError(f"legends_font_size argument is incorrect. It should be a list with elements like [x, y] (x - number of subplot, y - number - size of font for legend for x subplot) or one number for all legend fonts")
        if isinstance(legends_font_size, int):
            return (f"legend argument is correct", [-1, legends_font_size])
        elif isinstance(legends_font_size, list):
            for i in range(len(legends_font_size)):
                if not isinstance(legends_font_size[i], list):
                    raise TypeError(f'legends_font_size argument number {i} ({legends_font_size[i]}) should be list. The structure is [x, y] (x - number of subplot, y - number - size of font for legend for x subplot)')
                elif not isinstance(legends_font_size[i][0], int):
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i]}) should have structure [x, y] (x - number of subplot or -1, y - number - size of font for legend for x subplot)')
                elif legends_font_size[i][0] < 0 and legends_font_size[i][0] != -1:
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i]}) should have structure [x, y] (x - number of subplot or -1, y - number - size of font for legend for x subplot)')
                elif not isinstance(legends_font_size[i][1], int):
                    raise ValueError(f'legends_font_size argument number {i} ({legends_font_size[i]}) should have structure [x, y] (x - number of subplot or -1, y - number - size of font for legend for x subplot)')
            return (f"legends_font_size argument is correct.", legends_font_size)
    def __check_marker_size(self, marker_size):
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
        if not isinstance(line_width, (float, list)):
            raise TypeError(f'line_width argument is incorrect. It should be a list width float elements which are line width or one float number for all data.')
        if isinstance(line_width, float):
            if line_width > 0:
                return (f"line_width argument is correct.", [line_width])
            else:
                raise ValueError(f"line_width argument should be more than 0.")
        elif isinstance(line_width, list):
            for i in range(len(line_width)):
                if not isinstance(line_width[i], float):
                    raise ValueError(f"line_width argument {i} ({line_width[i]}) should be a float.")
                elif line_width[i] < 0:
                    raise ValueError(f"line_width argument {i} ({line_width[i]}) should be more than 0.")
            return (f"line_width argument is correct.", line_width)
    def __check_line_alpha(self, alpha):
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
        if not isinstance(axes_round_accuracy, (list, str)):
            raise TypeError(f"axes_round_accuracy argument is incorrect. It should be a list with elements like [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot) or one number for all axes fonts")
        if isinstance(axes_round_accuracy, str):
            if not all([axes_round_accuracy[0] == '%' and axes_round_accuracy[1] == '0' and axes_round_accuracy[2] == '.']):
                    raise ValueError(f'axes_round_accuracy argument number should be presented like y - string like "%0.xf", where x shows to which decimal number should be rounded')
            return (f"axes_round_accuracy argument is correct", [-1, [axes_round_accuracy, axes_round_accuracy]])
        elif isinstance(axes_round_accuracy, list):
            for i in range(len(axes_round_accuracy)):
                if not isinstance(axes_round_accuracy[i], list):
                    raise TypeError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should be list')
                elif not isinstance(axes_round_accuracy[i][0], int):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should have integer number as first element. The structure is [x, [y, y]] (x - number of subplot, y - string like "%0.xf", where x shows to which decimal number should be rounded)')
                elif not isinstance(axes_round_accuracy[i][1], list):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should have list as second element. The structure is [x, [y, y]] (x - number of subplot, y - string like "%0.xf", where x shows to which decimal number should be rounded')
                elif len(axes_round_accuracy[i][1]) != 2:
                    raise ValueError(f'axes_font_size argument number {i} ({axes_round_accuracy[i]}) should have two strings as elements. The structure is [x, [y, y]] (x - number of subplot, y - string like "%0.xf", where x shows to which decimal number should be rounded')
                elif not (isinstance(axes_round_accuracy[i][1][0], str) and isinstance(axes_round_accuracy[i][1][1], str)):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should have strings as elements of the second element. The structure is [x, [y, y]] (x - number of subplot, y - string like "%0.xf", where x shows to which decimal number should be rounded')
                elif not all([axes_round_accuracy[i][1][j][0] == '%' and axes_round_accuracy[i][1][j][1] == '0' and axes_round_accuracy[i][1][j][2] == '.' for j in range(2)]):
                    raise ValueError(f'axes_round_accuracy argument number {i} ({axes_round_accuracy[i]}) should be presented like [x, [y, y]] (x - number of subplot, y - string like "%0.xf", where x shows to which decimal number should be rounded')
            return (f"axes_round_accuracy argument is correct.", axes_round_accuracy)

    def __check_subplots_settings(self, subplots_settings):
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
                    raise ValueError(f"subplots_distribution elements should be integer (problem with element {i} ({subplots_settings["subplots_distribution"][i]})).")
                elif subplots_settings["subplots_distribution"][i] < 0:
                    raise ValueError(f"subplots_distribution elements should be more than 0 (problem with element {i} ({subplots_settings["subplots_distribution"][i]})).")
        return (f"subplots_settings argument is correct", subplots_settings)
    
    def __check_graph_types(self, graph_types):
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
        text_for_explaining_structure = ''' The structure of the element is [x, XY], where x can be \"stretch\" or \"divide\". If an option is \"stretch\" then XY=[x1, x2, y1, y2], 
                where x1(y1) / x2(y2) is number that minimal / maximal x(y) value of data on the subplot will be multiplied by.
                If an option is \"divide\" then XY = [[x1, x2, nx], [y1, y2, ny]], where x1(y1) / x2(y2) is a minimal / maximal number in x(y) axes,
                nx(ny) is number of tiks in x(y) axes (ticks for minimal and maximal numbers is included). 
                If you don't want to "divide" one of the axes, write replace relevant element with None Index of the plot is the same as the index of each list.'''
        if not isinstance(axes_scaling, list):
            raise TypeError(f"axes_scaling should be a list with elements." + text_for_explaining_structure)
        elif isinstance(axes_scaling, list):
            for i in range(len(axes_scaling)):
                if not isinstance(axes_scaling[i], list):
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i]}) should a list." + text_for_explaining_structure)
                elif len(axes_scaling[i]) != 2:
                    raise ValueError(f"axes_scaling don't have enough elements (or there are too many of them)." + text_for_explaining_structure)
                elif not (isinstance(axes_scaling[i][0], str) and axes_scaling[i][0] in ["stretch", "divide"]):
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][0]}) should be a string.Possible options are \"stretch\" or \"divide\".")
                elif not isinstance(axes_scaling[i][1], list):
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1]}) should be a list with structure of XY." + text_for_explaining_structure)
                elif axes_scaling[i][0] == "stretch" and len(axes_scaling[i][1]) != 4:
                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1]}) should be a list with four float coefficients.")
                elif axes_scaling[i][0] == "stretch" and len(axes_scaling[i][1]) == 4:
                    for j in range(4):
                        if not isinstance(axes_scaling[i][1][j], (int, float)):
                            raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1][j]}) should be a float or integer number.")
                elif axes_scaling[i][0] == "divide" and len(axes_scaling[i][1]) == 2:
                    if not all([(isinstance(axes_scaling[i][1][j], list) or axes_scaling[i][1][j] is None) for j in range(2)]):
                        raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1][j]}) should be a list or None.")
                    elif not all([(axes_scaling[i][1][j] is None) for j in range(2)]):
                        raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1]}) can not be both None.")
                    elif all([(axes_scaling[i][1][j] is None) for j in range(2)]):
                        for j in range(2):
                            if not (axes_scaling[i][1][j] is None):
                                if len(axes_scaling[i][1][j]) != 3:
                                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1][j]}) should have lenght 3, see structure." + text_for_explaining_structure)
                                elif not all([isinstance(axes_scaling[i][1][j][k], (int, float)) for k in range(2)]):
                                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1][j]}) should have integer or float edge numbers, see structure." + text_for_explaining_structure)
                                elif not (isinstance(axes_scaling[i][1][j][2], int) and axes_scaling[i][1][j][2] > 1):
                                    raise ValueError(f"axes_scaling element {i} ({axes_scaling[i][1][j]}) should have integer numbers of ticks and these numbers should be more or equal than 2, see structure." + text_for_explaining_structure)
            return (f"axes_scaling argument is correct", axes_scaling)
        
    def __check_axes_number_of_small_ticks(self, axes_number_of_small_ticks):
        text_that_explains_structure = ''' The structure of one element is [x, y] where x(y) is a number of small ticks in X(Y) axes between two big ticks. x(y) >= 1. The number of tikcs between two big is equal to x(y) - 1.'''
        if not isinstance(axes_number_of_small_ticks, (list, int)):
            raise TypeError(f"axes_number_of_small_ticks should be presented as list of elements (see structure) or one number for all subplots and axes." + text_that_explains_structure)
        if isinstance(axes_number_of_small_ticks, int):
            if axes_number_of_small_ticks >= 1:
                return (f"axes_number_of_small_ticks argument is correct. ", [[axes_number_of_small_ticks, axes_number_of_small_ticks]])
            else:
                raise ValueError(f"axes_number_of_small_ticks should be more than 0." + text_that_explains_structure)
        elif isinstance(axes_number_of_small_ticks, list):
            for i in range(len(axes_number_of_small_ticks)):
                if not isinstance(axes_number_of_small_ticks[i], list):
                    raise ValueError(f"axes_number_of_small_ticks element {i} ({axes_number_of_small_ticks[i]}) should have different structure." + text_that_explains_structure)
                elif len(axes_number_of_small_ticks[i]) != 2:
                    raise ValueError(f"axes_number_of_small_ticks element {i} ({axes_number_of_small_ticks[i]}) should have different structure." + text_that_explains_structure)
                for j in range(2):
                    if not isinstance(axes_number_of_small_ticks[i][j], int):
                        raise ValueError(f"axes_number_of_small_ticks element {i} ({axes_number_of_small_ticks[i][j]}) should be an integer number." + text_that_explains_structure)
                    elif axes_number_of_small_ticks[i][j] < 1:
                        raise ValueError(f"axes_number_of_small_ticks element {i} ({axes_number_of_small_ticks[i][j]}) should be at least 1." + text_that_explains_structure)   
            return (f"axes_number_of_small_ticks argument is correct. ", axes_number_of_small_ticks)
    def __check_labels(self, labels):
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
        if not isinstance(axes_titles, (list, str)):
            raise TypeError(f"axes_titles should be a list, where each element is a list [\"X\", \"Y\"], \"X\"(\"Y\") - titles for axes. Index of the element is relevant to the index of the plot is the same as the index of each list.")
        if isinstance(axes_titles, str):
            return (f"axes_titles argument is correct.", [axes_titles])
        elif isinstance(axes_titles, list):
            for i in range(len(axes_titles)):
                if not isinstance(axes_titles[i], list):
                    raise ValueError(f"axes_titles element {i} ({axes_titles[i]}) should be a list, where each element is a list [\"X\", \"Y\"], \"X\"(\"Y\") - titles for axes. Index of the element is relevant to the index of the plot is the same as the index of each list.")
                elif len(axes_titles[i]) != 2:
                    raise ValueError(f"axes_titles element {i} ({axes_titles[i]}) should have two strings elements (titles for axes).")
                for j in range(2):
                    if not isinstance(axes_titles[i][j], str):
                        raise ValueError(f"axes_titles element {i} ({axes_titles[i][j]}) should be a string.")
            return (f"axes_titles argument is correct.", axes_titles)
    
    def __check_subplots_legend_position(self, subplots_legend_position): #надо добавить возможные варианты для legend position
        if not isinstance(subplots_legend_position, (list, str)):
            raise TypeError(f"subplots_legend_position should be a list with strings(subplots legend position) or one string for all data.")
        if isinstance(subplots_legend_position, str):
            return (f"subplots_legend_position argument is correct", [subplots_legend_position])
        elif isinstance(subplots_legend_position, list):
            for i in range(len(subplots_legend_position)):
                if not isinstance(subplots_legend_position[i], str):
                    raise TypeError(f"subplots_legend_position element {i} ({subplots_legend_position[i]}) should be a list with strings(subplots_legend_position).")
            return  (f"subplots_legend_position argument is correct", subplots_legend_position)

    def construct_structure_for_plotting_subplots(self, config, data_array):
        graph_pos_types = {"2D":1, "3D":2}
        for i in range(self.quant):
            self.curves_settings.append(dict())
            self.curves_settings[i] = {"data": data_array[i],
                                      "graph_type": graph_pos_types[config["graph_types"][i]],
                                      "color": config["color"][i],
                                      "ls": config["ls"][i],
                                      "marker_shape": config["marker_shape"][i],
                                      "marker_sizes": config["marker_size"][i], 
                                      "subplot_position": config["subplots_settings"][0]["subplots_distribution"][i],
                                      "label": config["labels"][i]}
        for i in range(self.number_of_subplots):
            self.subplots_settings.append(dict())
            self.subplots_settings[i] = {"axes_font_size": config["axes_font_size"][i], 
                                         "subplots_titles_font_size": config["subplots_titles_font_size"][i],
                                         "axes_scaling": config["axes_scaling"][i],
                                         "axes_round_accuracy": config["axes_round_accuracy"][i],
                                         "axes_titles": config["axes_titles"][i],
                                         ##"subplot_title": a, b, c
                                         "legend_position": config["subplots_legend_position"][i],
                                         "legend_font_size": config["legends_font_size"][i]}
    def check_config(self):
        self.config["color"] = self.extend_parameters(self.config['color'], self.quant, "#C0392B")
        self.config["ls"] = self.extend_parameters(self.config["ls"], self.quant, '')
        self.config["labels"] = self.extend_parameters(self.config["labels"], self.quant, '')
        self.config["marker_size"] = self.extend_parameters(self.config["marker_size"], self.quant, 3)
        self.config["marker_shape"] = self.extend_parameters(self.config["marker_shape"], self.quant, 'o')
        self.config["line_alpha"] = self.extend_parameters(self.config["line_alpha"], self.quant, 1)
        self.config["axes_font_size"] = self.extend_parameters(self.config["axes_font_size"], self.number_of_subplots, [8, 8])
        self.config["axes_round_accuracy"] = self.extend_parameters(self.config["axes_round_accuracy"], self.number_of_subplots, ["%0.2f", "%0.2f"])
        self.config["subplots_settings"][0]["subplots_distribution"] = self.extend_parameters(self.config["subplots_settings"][0]["subplots_distribution"], self.quant, 1)
        self.config["axes_scaling"] = self.extend_parameters(self.config["axes_scaling"], self.number_of_subplots, ["multiplication", [0.9, 1.1, 0.9, 1.1]])
        self.config["legends_font_size"] = self.extend_parameters(self.config["legends_font_size"], self.number_of_subplots, 8)
        self.config["subplots_legend_position"] = self.extend_parameters(self.config["subplots_legend_position"], self.number_of_subplots, "best")
        self.config["axes_titles"] = self.extend_parameters(self.config["axes_titles"], self.number_of_subplots, ["X", "Y"])
        self.config["graph_types"] = self.extend_parameters(self.config["graph_types"], self.quant, "2D")
        #print(js.dumps(self.config, indent=4, ensure_ascii=False))

    def extend_parameters(self, parameter, quant, element_extend_by):
        if len(parameter) < quant and len(parameter) > 0:
            for i in range(len(parameter), quant):
                parameter.append(parameter[i - 1])
        elif len(parameter) == 0:
            parameter = [element_extend_by] * quant
        return parameter
    
    def print_curve_settings(self, curve_index):
        print(self.curves_settings[curve_index])
    def print_subplot_settings(self, subplot_index):
        print(self.subplots_settings[subplot_index])