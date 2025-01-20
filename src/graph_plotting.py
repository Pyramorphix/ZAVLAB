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
        for key, value in kwargs.items():
            try:
                if not (key in json_keys):
                    raise KeyError(f"{key} is not an argument in configuration file. Maybe you should check your spelling :)")
                if key == 'color':
                    try:
                        result = self.__check_color(value)
                        if self.verbose:
                            print(result)
                    except (TypeError, ValueError) as e:
                        print(f'Error: {e}')
                elif key == 'ls':
                    try:
                        result = self.__check_ls(value)
                        if self.verbose:
                            print(result)
                    except (TypeError, ValueError) as e:
                        print(f'Error: {e}')
                elif key == 'marker_shape':
                    try:
                        result = self.__check_marker_shape(value)
                        if self.verbose:
                            print(result)
                    except (TypeError, ValueError) as e:
                        print(f'Error: {e}')
                elif key == 'axes_font_size':
                    try:
                        result = self.__check_axes_font_size(value)
                        if self.verbose:
                            print(result)
                    except (TypeError, ValueError) as e:
                        print(f'Error: {e}')    
            except KeyError as e:
                print(f"Error has occured. \n {e}")

    def __check_color(self, colors): #данная функция была написана под песни Би-2, плейлист "горизонт событий"
        if not isinstance(colors, (list, str)):
            raise TypeError(f"Color argument is incorrect. It should be a list with color codes as string or one color as string.")
        if isinstance(colors, str):
            if colors[0] == "#" and len(colors) == 7:
                return f"Color argument is correct"
            else:
                raise ValueError(f"Color has incorrect code. It should be presented in the way like #XXXXXX, where X is numbers (0, ... 9) or letters from A to F. You can use this site https://csscolor.ru/ to get the right colot code.")
        elif isinstance(colors, list):
            for i in range(len(colors)):
                if not isinstance(colors[i], str):
                    raise TypeError(f"Color argument number {i} ({colors[i]}) is incorrect. It should be a string.")
                if not (colors[i][0] == "#" and len(colors[i]) == 7):
                    raise ValueError(f"Color number {i} ({colors[i]}) has incorrect code. It should be presented in the way like #XXXXXX, where X is numbers (0, ... 9) or letters from A to F. You can use this site https://csscolor.ru/ to get the right colot code.")
            return f"Color argument is correct"
        
    def __check_ls(self, ls): #данная функция была написана под песни Би-2, плейлист "горизонт событий"
        if not isinstance(ls, (list, str)):
            raise TypeError(f"ls argument is incorrect. It should be a list with ls types as string or one ls type as string.")
        if isinstance(ls, str):
            if ls in ["-", "--", "-.", ":", ""]:
                return f"ls argument is correct"
            else:
                raise ValueError(f"ls has incorrect code. It should be one element from this list [\"-\", \"--\", \"-.\", \":\", \"\"]")
        elif isinstance(ls, list):
            for i in range(len(ls)):
                if not isinstance(ls[i], str):
                    raise TypeError(f"ls argument number {i} ({ls[i]}) is incorrect. It should be a string.")
                if not (ls[i] in ["-", "--", "-.", ":", ""]):
                    raise ValueError(f"ls argument number {i} ({ls[i]}) has incorrect code. It should be one element from this list [\"-\", \"--\", \"-.\", \":\", \"\"]")
            return f"ls argument is correct"
        
    def __check_marker_shape(self, marker_shape): #данная функция была написана под песни Би-2, плейлист "горизонт событий"
        if not isinstance(marker_shape, (list, str)):
            raise TypeError(f"marker_shape argument is incorrect. It should be a list with marker_shape types as string or one marker_shape type as string.")
        if isinstance(marker_shape, str):
            if marker_shape in [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", "d", "|", "_", ""]:
                return f"marker_shape argument is correct"
            else:
                raise ValueError(f"marker_shape has incorrect code. It should be one element from this list [\".\", \",\", \"o\", \"v\", \"^\", \"<\", \">\", \"1\", \"2\", \"3\", \"4\", \"8\", \"s\", \"p\", \"P\", \"*\", \"h\", \"H\", \"+\", \"x\", \"X\", \"D\", \"d\", \"|\", \"_\", \"\"]")
        elif isinstance(marker_shape, list):
            for i in range(len(marker_shape)):
                if not isinstance(marker_shape[i], str):
                    raise TypeError(f"marker_shape argument number {i} ({marker_shape[i]}) is incorrect. It should be a string.")
                if not (marker_shape[i] in [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", "d", "|", "_", ""]):
                    raise ValueError(f"marker_shape argument number {i} ({marker_shape[i]}) has incorrect code. It should be one element from this list [\".\", \",\", \"o\", \"v\", \"^\", \"<\", \">\", \"1\", \"2\", \"3\", \"4\", \"8\", \"s\", \"p\", \"P\", \"*\", \"h\", \"H\", \"+\", \"x\", \"X\", \"D\", \"d\", \"|\", \"_\", \"\"]")
            return f"marker_shape argument is correct"
    
    def __check_axes_font_size(self, axes_font_size): #данная функция была написана под серии смешариков "Сыр-бор Новый год", "Место истории"
        if not isinstance(axes_font_size, (list, int)):
            raise TypeError(f"axes_font_size argument is incorrect. It should be a list with elemts like [x, [y, y]] (x - number of subplot, y - number - size of font for axes for x subplot) or one number for all axes fonts")
        if isinstance(axes_font_size, int):
            return f"axes_font_size argument is correct"
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
            return f"axes_font_size argument is correct"
                
    def check_variable_list_str(self, variable, key):
        if not isinstance(variable, (list, str)):
            raise TypeError(f"{key} must be a list or string, but received type: {type(variable).__name__}")
        # If it's a list, check that all elements are strings
        if isinstance(variable, list):
            if not all(isinstance(item, str) for item in variable):
                raise TypeError(f"All elements in the {key} list must be strings")
        return (f"Variable {key} is set correctly", isinstance(variable, (list)))

    def check_variable_sizes(self, variable, key):
        if not isinstance(variable, int):
            raise TypeError(f"{key} must be a list or string, but received type: {type(variable).__name__}")
        return f"Variable {key} is set correctly"

    def check_variable_list_int(self, variable, key):
        if not isinstance(variable, (list, float, int)):
            raise TypeError(f"{key} must be a list or number, but received type: {type(variable).__name__}")
        # If it's a list, check that all elements are numbers
        if isinstance(variable, list):
            if not all(isinstance(item, (int, float)) for item in variable):
                raise TypeError(f"All elements in the {key} list must be strings")
        return (f"Variable {key} is set correctly", isinstance(variable, list))

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