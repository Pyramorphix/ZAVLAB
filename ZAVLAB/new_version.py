import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as ticker 

colors_palete = ["#f00a19", "#0879c9", "#36053d", "#000", "#09998f"]



def minElem(data=[], quant=0):
    if quant == 0:
        return 0
    if quant == 1:
        return np.min(data[0])
    min_elements = []
    for i in range(quant):
        min_elements.append(np.min(data[i]))
    return min(min_elements)

def maxElem(data=[], quant=0):
    if quant == 0:
        return 0
    if quant == 1:
        return np.max(data[0])
    max_elements = []
    for i in range(quant):
        max_elements.append(np.max(data[i]))
    return max(max_elements)

def returnMinAndMaxElementForData(data, quant, stretch_graph_coefficients):
    minimalElement_x = []
    minimalElement_y = []
    maximumElement_x = []
    maximumElement_y = []
    for i in range(quant):
        if  data[i].shape[0] == 4:
            minimalElement_x.append(np.min(data[i][0] - data[i][1]))
            minimalElement_y.append(np.min(data[i][2] - data[i][3]))
            maximumElement_x.append(np.max(data[i][0] + data[i][1]))
            maximumElement_y.append(np.max(data[i][2] + data[i][3]))

        elif  data[i].shape[0] == 3:
            minimalElement_x.append(np.min(data[i][0] - data[i][1]))
            minimalElement_y.append(np.min(data[i][2]))
            maximumElement_x.append(np.max(data[i][0] - data[i][1]))
            maximumElement_y.append(np.max(data[i][2]))

        elif  data[i].shape[0] == 2:
            minimalElement_x.append(np.min(data[i][0]))
            minimalElement_y.append(np.min(data[i][1]))
            maximumElement_x.append(np.max(data[i][0]))
            maximumElement_y.append(np.max(data[i][1]))
    if(quant == 1):
        minEl = [minimalElement_x[0], minimalElement_y[0]] 
        maxEl = [maximumElement_x[0], maximumElement_y[0]]
    else:
        minEl = [min(minimalElement_x), min(minimalElement_y)]    
        maxEl = [max(maximumElement_x), max(maximumElement_y)]
    minEl[0] *= stretch_graph_coefficients[0]
    minEl[1] *= stretch_graph_coefficients[2]
    maxEl[0] *= stretch_graph_coefficients[1]
    maxEl[1] *= stretch_graph_coefficients[3]
    return (minEl, maxEl)

def extend_parameters(parameter, quant, element_extend_by):
    if len(parameter) < quant and len(parameter) > 0:
        for i in range(len(parameter), quant):
            parameter.append(parameter[i - 1])
    elif len(parameter) == 0:
        parameter = [element_extend_by] * quant
    return parameter

#data is a massive where each data is different element.
#each element has a structure: index = 0 - x_data, index=1 - sigma_x_data, index=2, y_data, index=3 - sigma_y_data
#if lenght of the element is three then it's structure is: index = 0 - x_data, index=1 - sigma_x_data, index=2, y_data
#if lenght of the element is two then it's structure is: index = 0 - x_data, index=1 - y_data
#first title is x-axis, second - y-axis, third - graph title
# point_start_to_end has tree elements x and y parameters, step
#horizontal_vertical_lines structure for each element: 0 index is 'h' (horizontal) or 'v' (vertical) line, 1 index is respictively y or x coordinate of the line, 2 index is color of the dasshed line, 3 index is (title, pos) for the line (if vertical, position is y, if horizontal, position is x ), 4 index is for title fontsize
#points_draw_lines_to structure for each element: (0, 1) indexes are (x, y) coordinates of the point, 2 index is color of the dasshed line, (3, 4) are fontsize for (x, y) coordinate respectively (can be only one index or no index for fontsize). If value of 3 or 4 indexe is None then there will be no title respectively. THE LENGHT MUST BE 5, otherwise it won't work
#ticks_and_font_size structure: (0, 1) indexes are (x, y) axes ticks labels fontsize, 2 index is title fontsize
def plot_graph(data,quant=None, titles=['X', 'Y', 'title'], colors=['r'], stretch_graph_coefficients=[0, 1.1, 0, 1.1],
                lses=[''], labels=[''], markersizes=[3], legend_position='upper right', axes_round=['%0.2f', '%0.2f'],
                  name_fig='graph.svg', markers=["o"], save_flag=True, points_draw_lines_to=[], point_start_to_end=[None, None],
                    ticks_and_font_size=[8, 8, 10], horizontal_vertical_lines=[], alphas=[1], legend_font_size=10):
    if(quant == None):
        quant = len(data)
    fig, ax = plt.subplots() #+
    plt.xlabel(titles[0], fontsize=ticks_and_font_size[0]) #+
    plt.ylabel(titles[1], fontsize=ticks_and_font_size[1])#+
    ticks_and_font_size = extend_parameters(ticks_and_font_size, 3, element_extend_by=10)
    fig.suptitle(titles[2], fontsize=ticks_and_font_size[2], fontweight="bold") #+

    if point_start_to_end[0] == None and point_start_to_end[1] == None:
        minEl, maxEl = returnMinAndMaxElementForData(data, quant, stretch_graph_coefficients)

        ax.xaxis.set_ticks_position("bottom") #+
        ax.yaxis.set_ticks_position("left") #+
        ax.spines["left"].set_position(("data", minEl[0])) #+
        ax.spines["bottom"].set_position(("data", minEl[1])) #+
        ax.set(xlim=(minEl[0], maxEl[0]),ylim=(minEl[1], maxEl[1])) #+
        plt.xticks(np.linspace(minEl[0], maxEl[0], 8), rotation=0, size=ticks_and_font_size[0]) #+
        plt.yticks(np.linspace(minEl[1], maxEl[1], 8),size=ticks_and_font_size[1]) #+
        x_steps = (maxEl[0] - minEl[0])/ 8 / 20
        y_steps = (maxEl[1] - minEl[1])/ 8 / 20
    elif point_start_to_end[0] == None and point_start_to_end[1] != None:
        minEl, maxEl = returnMinAndMaxElementForData(data, quant, stretch_graph_coefficients)
        ax.xaxis.set_ticks_position("bottom") #+
        ax.yaxis.set_ticks_position("left")
        ax.spines["left"].set_position(("data", minEl[0]))
        ax.spines["bottom"].set_position(("data", point_start_to_end[1][0]))
        ax.set(xlim=(minEl[0], maxEl[0]),ylim=(point_start_to_end[1][0], point_start_to_end[1][1]))
        plt.xticks(np.linspace(minEl[0], maxEl[0], 8), rotation=0, size=ticks_and_font_size[0])
        plt.yticks(np.linspace(point_start_to_end[1][0], point_start_to_end[1][1], point_start_to_end[1][2]),size=ticks_and_font_size[1]) 
        minEl[1], maxEl[1] = point_start_to_end[1][0], point_start_to_end[1][1]
        x_steps = (maxEl[0] - minEl[0])/ 8 / 20
        y_steps = (maxEl[1] - minEl[1])/ point_start_to_end[1][2] / 20

    elif point_start_to_end[0] != None and point_start_to_end[1] == None:
        minEl, maxEl = returnMinAndMaxElementForData(data, quant, stretch_graph_coefficients)
        ax.xaxis.set_ticks_position("bottom")
        ax.yaxis.set_ticks_position("left")
        ax.spines["left"].set_position(("data", point_start_to_end[0][0]))
        ax.spines["bottom"].set_position(("data", minEl[1]))
        ax.set(xlim=(point_start_to_end[0][0], point_start_to_end[0][1]),ylim=(minEl[1], maxEl[1]))
        plt.xticks(np.linspace(point_start_to_end[0][0], point_start_to_end[0][1], point_start_to_end[0][2]), rotation=0, size=ticks_and_font_size[0])
        plt.yticks(np.linspace(minEl[1], maxEl[1], 8),size=ticks_and_font_size[1])
        minEl[0], maxEl[0] = point_start_to_end[0][0], point_start_to_end[0][1]
        x_steps = (maxEl[0] - minEl[0])/ point_start_to_end[0][2] / 20
        y_steps = (maxEl[1] - minEl[1])/ 8 / 20

    elif point_start_to_end[0] != None and point_start_to_end[1] != None:
        ax.xaxis.set_ticks_position("bottom")
        ax.yaxis.set_ticks_position("left")
        ax.spines["left"].set_position(("data", point_start_to_end[0][0]))
        ax.spines["bottom"].set_position(("data", point_start_to_end[1][0]))
        ax.set(xlim=(point_start_to_end[0][0], point_start_to_end[0][1]),ylim=(point_start_to_end[1][0], point_start_to_end[1][1]))
        plt.xticks(np.linspace(point_start_to_end[0][0], point_start_to_end[0][1], point_start_to_end[0][2]), rotation=0, size=ticks_and_font_size[0])
        plt.yticks(np.linspace(point_start_to_end[1][0], point_start_to_end[1][1], point_start_to_end[1][2]),size=ticks_and_font_size[1]) 
        minEl, maxEl = [point_start_to_end[0][0], point_start_to_end[1][0]], [point_start_to_end[0][1], point_start_to_end[1][1]]
        x_steps = (maxEl[0] - minEl[0])/ point_start_to_end[0][2] / 20
        y_steps = (maxEl[1] - minEl[1])/ point_start_to_end[1][2] / 20



    colors = extend_parameters(colors, quant, 'r')
    lses = extend_parameters(lses, quant, '')
    labels = extend_parameters(labels, quant, '')
    markersizes = extend_parameters(markersizes, quant, 3)
    markers = extend_parameters(markers, quant, 'o')
    alphas = extend_parameters(alphas, quant, 1)

    for i in range(quant):
        if(data[i].shape[0] == 4):
            ax.errorbar(x=data[i][0], y=data[i][2], xerr=data[i][1], yerr=data[i][3], lw=0.5, color=colors[i], marker=markers[i], label=labels[i], markersize=markersizes[i], ls=lses[i], alpha=alphas[i])
        elif(data[i].shape[0] == 3):
            ax.errorbar(x=data[i][0], y=data[i][2], xerr=data[i][1], lw=0.5, color=colors[i], marker=markers[i], label=labels[i], markersize=markersizes[i], ls=lses[i],alpha=alphas[i])
        elif(data[i].shape[0] == 2):
            ax.plot(data[i][0], data[i][1], lw=0.5, color=colors[i], marker=markers[i], label=labels[i], markersize=markersizes[i], ls=lses[i],alpha=alphas[i])
    
    if(len(axes_round) == 1):
        ax.yaxis.set_major_formatter(FormatStrFormatter(axes_round[0]))
        ax.xaxis.set_major_formatter(FormatStrFormatter(axes_round[0]))
    elif(len(axes_round) == 2):
        ax.yaxis.set_major_formatter(FormatStrFormatter(axes_round[1]))
        ax.xaxis.set_major_formatter(FormatStrFormatter(axes_round[0]))
    
    ax.tick_params(direction ='in', length=5, width=1.5) #+
    ax.legend(loc=legend_position, frameon=False, prop={'size': legend_font_size}) #+
    ax.grid(color="#7a7c7d", linewidth=0.3) #+
    ax.grid(which='minor', color='#7a7c7d', linestyle=':', linewidth=0.2)#+
    ax.minorticks_on() #+
    ax.tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black') #+
    ax.tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black') #+
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5)) #+
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5)) #+
    for i in range(len(points_draw_lines_to)):
        ax.axvline(x = points_draw_lines_to[i][0], ymax = (points_draw_lines_to[i][1] - minEl[1])/ (maxEl[1] - minEl[1]), color = points_draw_lines_to[i][2], linestyle='dashed') 
        ax.axhline(y = points_draw_lines_to[i][1], xmax = (points_draw_lines_to[i][0] - minEl[0]) / (maxEl[0] - minEl[0]), color = points_draw_lines_to[i][2], linestyle='dashed')
        if(points_draw_lines_to[i][3] != None):
            ax.text(x=points_draw_lines_to[i][0] + x_steps, y = minEl[1] + y_steps, s=str(round(points_draw_lines_to[i][0], 2)), fontsize = points_draw_lines_to[i][3])
        if(points_draw_lines_to[i][4] != None):
            ax.text(x=minEl[0] + x_steps, y = points_draw_lines_to[i][1] + y_steps, s=str(round(points_draw_lines_to[i][1], 2)), fontsize = points_draw_lines_to[i][4])
        # elif len(points_draw_lines_to[i]) == 3: 
        #     ax.text(x=points_draw_lines_to[i][0] + x_steps, y = minEl[1] + y_steps, s=str(round(points_draw_lines_to[i][0], 2)), fontsize = ticks_and_font_size[0])
        #     ax.text(x=minEl[0] + x_steps, y = points_draw_lines_to[i][1] + y_steps, s=str(round(points_draw_lines_to[i][1], 2)), fontsize = ticks_and_font_size[1])
        # elif len(points_draw_lines_to[i]) == 4: 
        #     ax.text(x=points_draw_lines_to[i][0] + x_steps, y = minEl[1] + y_steps, s=str(round(points_draw_lines_to[i][0], 2)), fontsize = points_draw_lines_to[i][3])
        #     ax.text(x=minEl[0] + x_steps, y = points_draw_lines_to[i][1] + y_steps, s=str(round(points_draw_lines_to[i][1], 2)), fontsize = points_draw_lines_to[i][3])
    for i in range(len(horizontal_vertical_lines)):
        if(horizontal_vertical_lines[i][0] == 'h'):
            ax.axhline(y = horizontal_vertical_lines[i][1], xmax = 1, color = horizontal_vertical_lines[i][2], linestyle='dashed')
            if(len(horizontal_vertical_lines[i]) >= 5):
                ax.text(x=horizontal_vertical_lines[i][3][1], y = horizontal_vertical_lines[i][1] + y_steps * 4, s=horizontal_vertical_lines[i][3][0], fontsize = horizontal_vertical_lines[i][4])
            elif(len(horizontal_vertical_lines[i]) == 4):
                ax.text(x=horizontal_vertical_lines[i][3][1], y = horizontal_vertical_lines[i][1] + y_steps * 4, s=horizontal_vertical_lines[i][3][0], fontsize = ticks_and_font_size[2])
        if(horizontal_vertical_lines[i][0] == 'v'):
            ax.axvline(x = horizontal_vertical_lines[i][1], ymax = 1, color = horizontal_vertical_lines[i][2], linestyle='dashed')
            if(len(horizontal_vertical_lines[i]) >= 5):
                ax.text(x=horizontal_vertical_lines[i][1] + x_steps * 4, y = horizontal_vertical_lines[i][3][1], s=horizontal_vertical_lines[i][3][0], fontsize = horizontal_vertical_lines[i][4])
            elif(len(horizontal_vertical_lines[i]) == 4):
                ax.text(x=horizontal_vertical_lines[i][1] + x_steps * 4, y = horizontal_vertical_lines[i][3][1], s=horizontal_vertical_lines[i][3][0], fontsize = ticks_and_font_size[2])
    if save_flag:
        plt.savefig(name_fig)
    return fig, ax

def mnk(x, y):
    k = (np.mean(x * y) - np.mean(x) * np.mean(y)) / (np.mean(x ** 2) - np.mean(x) ** 2)
    b = np.mean(y) - k * np.mean(x)
    dxx = np.mean(x ** 2) - np.mean(x) ** 2
    dyy = np.mean(y ** 2) - np.mean(y) ** 2
    errK = np.sqrt((dyy / dxx - k**2) / (x.shape[0] - 2))
    errB = errK * np.sqrt(np.mean(x ** 2))
    coef = np.array([k, b])
    error = np.array([errK, errB])
    return (coef, error)

def nice_print(data, names):
    print(end="\t")
    for i in range(len(names)):
        print(i, end="\t")
    print(end="\n \t")

    for i in range(len(names)):
        print(names[i], end="\t")
    print(end="\n")
    for i in range(data.shape[1]):
        print(i, end="\t")
        for j in range(data.shape[0]):
            print(np.round(data[j][i], decimals=5), end="\t")
        print(end="\n")


    # if len(lses) < quant and len(lses) > 0:
    #     for i in range(len(lses), quant):
    #         lses.append(lses[i - 1])
    # elif len(lses) == 0:
    #     lses = [''] * quant
    # if len(labels) < quant and len(labels) > 0:
    #     for i in range(len(labels), quant):
    #         labels.append(labels[i - 1])
    # elif len(labels) == 0:
    #     labels = [''] * quant

    # if len(markersizes) < quant and len(markersizes) > 0:
    #     for i in range(len(markersizes), quant):
    #         markersizes.append(markersizes[i - 1])
    # elif len(markersizes) == 0:
    #     markersizes = [3] * quant

    # if len(markers) < quant and len(markers) > 0:
    #     for i in range(len(markers), quant):
    #         markers.append(markers[i - 1])
    # elif len(markers) == 0:
    #     markers = ["o"] * quant

def calculate_lines_parameters(data, p1, p2, p3, p4, flag1,flag2, flag3, flag4):
    point1 = data[:, p1]
    point2 = data[:, p2]
    y1, y2, x1, x2 = 0, 0, 0, 0
    match flag1:
        case 0: 
            x1 = point1[0]
            y1 = point1[2] + point1[3]
        case 1: 
            x1 = point1[0] + point1[1]
            y1 = point1[2]
        case 2: 
            x1 = point1[0]
            y1 = point1[2] - point1[3]
        case 3: 
            x1 = point1[0] - point1[1]
            y1 = point1[2]
    match flag2:
        case 0: 
            x2 = point2[0]
            y2 = point2[2] + point2[3]
        case 1: 
            x2 = point2[0] + point2[1]
            y2 = point2[2]
        case 2: 
            x2 = point2[0]
            y2 = point2[2] - point2[3]
        case 3: 
            x2 = point2[0] - point2[1]
            y2 = point2[2]
    k1 = (y2 - y1) / (x2 - x1)
    b1 = (y1 * x2 - y2 * x1) / (x2 - x1)
    point1 = data[:, p3]
    point2 = data[:, p4]
    match flag3:
        case 0: 
            x1 = point1[0]
            y1 = point1[2] + point1[3]
        case 1: 
            x1 = point1[0] + point1[1]
            y1 = point1[2]
        case 2: 
            x1 = point1[0]
            y1 = point1[2] - point1[3]
        case 3: 
            x1 = point1[0] - point1[1]
            y1 = point1[2]
    match flag4:
        case 0: 
            x2 = point2[0]
            y2 = point2[2] + point2[3]
        case 1: 
            x2 = point2[0] + point2[1]
            y2 = point2[2]
        case 2: 
            x2 = point2[0]
            y2 = point2[2] - point2[3]
        case 3: 
            x2 = point2[0] - point2[1]
            y2 = point2[2]
    k2 = (y2 - y1) / (x2 - x1)
    b2 = (y1 * x2 - y2 * x1) / (x2 - x1)
    k_par = [(k1 + k2) / 2, np.abs(k1 - k2) / 2]
    b_par = [(b1 + b2) / 2, np.abs(b1 - b2) / 2]
    return (k_par, b_par)
 


def calculate_slope_and_shift_for_points(x, y):
    """
    Вычисляет коэффициенты наклона (dy/dx) кривой в каждой точке.
    :param points: numpy.ndarray, массив точек, где первая строка - x, вторая - y.
    :return: numpy.ndarray, массив пар (x, y, slope) для каждой точки.
    """    
    
    # Проверяем, что массивы x и y имеют одинаковую длину
    if len(x) != len(y):
        raise ValueError("Массивы x и y должны быть одинаковой длины.")
    
    slopes = np.gradient(y, x) 
    shifts = y - slopes * x  # b = y - k * x    
    result = np.array([slopes, shifts]).T  # Транспонируем, чтобы каждая строка соответствовала точке
    return result
