import json as js
import numpy as np
import matplotlib.pyplot as plt

class Earl:
    def __init__(self, file_path_name_to_conf="configuration.json", **kwargs):
        with open(file_path_name_to_conf, 'r', encoding='utf-8') as file:
            config = js.load(file)
        config = self.check_parameters(config, kwargs)   
        self.fig, self.axes = plt.subplots(nrows=config['subplots_settings'][0]['nrows'], ncols=config['subplots_settings'][0]['ncols'])
        self.quant = 1
        self.number_of_subplots = config['subplots_settings'][0]['nrows'] * config['subplots_settings'][0]['ncols']
        config = self.check_config(config)
        self.curves_settings = []
        self.subplots_settings = []
        self.construct_structure_for_plotting_subplots(config, [[]])
        del config
    
    def plot_graph(self, data_array, **kwargs):
        pass

    def check_parameters(self, config, kwargs):
        json_keys = config.keys()
        for key, value in kwargs.items():
            try:
                if not  (key in json_keys):
                    raise KeyError(f"{key} is not an argument in configuration file. Maybe you should check your spelling :)")
                if key in ["color", "ls", "marker_shape", "labels"]:
                    try:
                        result = self.check_variable_c_l_ms(value, key)
                        if(result[1]):
                            config[key] = value
                        else:
                            config[key] = list([value])
                    except TypeError as e:
                        print(f"Error: {e}")
                elif key in ["legend_font_size"]:
                    try:
                        print(self.check_variable_sizes(value, key))

                    except TypeError as e:
                        print(f"Error: {e}")
                elif key in ["line_width", "line_alpha", "axes_font_size", "subplots_titles_font_size", "markers_size"]:
                    try:
                        result = self.check_variable_list_int(value, key)
                        if(result[1]):
                            config[key] = value
                        else:
                            config[key] = list([value])
                        print(result[0])
                    except TypeError as e:
                        print(f"Error: {e}")
            except KeyError as e:
                print(f"Error has occured. \n {e}")
        return config
                    
    def check_variable_c_l_ms(self, variable, key):
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
    def check_config(self, config):
        config["color"] = self.extend_parameters(config['color'], self.quant, "#C0392B")
        config["ls"] = self.extend_parameters(config["ls"], self.quant, '')
        config["labels"] = self.extend_parameters(config["labels"], self.quant, '')
        config["marker_size"] = self.extend_parameters(config["marker_size"], self.quant, 3)
        config["marker_shape"] = self.extend_parameters(config["marker_shape"], self.quant, 'o')
        config["line_alpha"] = self.extend_parameters(config["line_alpha"], self.quant, 1)
        config["axes_font_size"] = self.extend_parameters(config["axes_font_size"], self.number_of_subplots, [8, 8])
        config["axes_round_accuracy"] = self.extend_parameters(config["axes_round_accuracy"], self.number_of_subplots, ["%0.2f", "%0.2f"])
        config["subplots_settings"][0]["subplots_distribution"] = self.extend_parameters(config["subplots_settings"][0]["subplots_distribution"], self.quant, 1)
        config["axes_scaling"] = self.extend_parameters(config["axes_scaling"], self.number_of_subplots, ["multiplication", [0.9, 1.1, 0.9, 1.1]])
        config["legends_font_size"] = self.extend_parameters(config["legends_font_size"], self.number_of_subplots, 8)
        config["subplots_legend_position"] = self.extend_parameters(config["subplots_legend_position"], self.number_of_subplots, "best")
        config["axes_titles"] = self.extend_parameters(config["axes_titles"], self.number_of_subplots, ["X", "Y"])
        config["graph_types"] = self.extend_parameters(config["graph_types"], self.quant, "2D")
        #print(js.dumps(config, indent=4, ensure_ascii=False))
        return config

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