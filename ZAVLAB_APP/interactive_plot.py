"""
Interactive plotting canvas with click handling:
- Handles axis configuration clicks
- Manages subplot layout
- Renders matplotlib figures
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from dialogs import AxisConfigDialog
from PyQt6.QtWidgets import QMessageBox
import matplotlib.ticker as ticker
from matplotlib.axes import Axes
import numpy as np
import matplotlib as plt

#Check if LaTeX is availability
try:
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "text.latex.preamble": 
            r"\usepackage[T2A]{fontenc}" 
            r"\usepackage[utf8]{inputenc}"
            r"\usepackage[russian]{babel}"
            r"\usepackage{amsmath}"
    })
except:
    plt.rcParams['mathtext.fontset'] = 'cm' 


class INTERACTIVE_PLOT(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, data=[]):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = []
        self.subplots = []
        self.gs = gridspec.GridSpec(
            1, 1, 
            figure=self.fig,
            width_ratios=[1]*1,
            height_ratios=[1]*1,
            wspace=0.5,
            hspace=0.7
        )
        super().__init__(self.fig)
        self.setParent(parent)
        self.canvas = FigureCanvas(self.fig)
        self.data = None

        self.mpl_connect("button_press_event", self.on_click)
        # self.plot_data(data=None,labels=["x", "y"])

    def on_click(self, event):
        if not event.inaxes:
            return
        
        # Определяем, на каком графике произошел клик
        for i, ax in enumerate(self.axes):
            if event.inaxes == ax:
                # Определяем параметры для конкретного графика
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                tolerance = 0.05  # 5% от диапазона
                
                # Клик по оси X (нижняя часть)
                if event.ydata < y_min + tolerance * (y_max - y_min):
                    dialog = AxisConfigDialog('x', ax, self)
                    dialog.exec()
                    return
                
                # Клик по оси Y (левая часть)
                if event.xdata < x_min + tolerance * (x_max - x_min):
                    dialog = AxisConfigDialog('y', ax, self)
                    dialog.exec()
                    return
    
    def plot_all_data(self, win, rows, cols):
        """Generate the plot based on current configuration"""

        if not self.subplots:
            QMessageBox.warning(self, "No Subplots", "Please add at least one subplot")
            return
        
        del self.gs
        self.fig.clear()
        del self.axes
        self.axes = []
        # Create GridSpec
        self.gs = gridspec.GridSpec(
            rows, cols, 
            figure=self.fig,
            width_ratios=[1]*cols,
            height_ratios=[1]*rows,
            wspace=0.5,
            hspace=0.7
        )
        # Create a grid to track occupied cells
        occupied = [[False] * cols for _ in range(rows)]

        # Create axes for each subplot
        for subplot in self.subplots:
            plot_id, s_row, s_col, s_row_span, s_col_span, *_ = subplot
            ax = self.fig.add_subplot(self.gs[s_row:s_row+s_row_span, s_col:s_col+s_col_span])
            self.axes.append(ax)
            self.update_one_plot(subplot, win)
            
            # Mark occupied cells
            for r in range(s_row, s_row+s_row_span):
                for c in range(s_col, s_col+s_col_span):
                    if r < rows and c < cols:
                        occupied[r][c] = True
        # Add empty cells
        for r in range(rows):
            for c in range(cols):
                if not occupied[r][c]:
                    ax = self.fig.add_subplot(self.gs[r, c])
                    ax.text(0.5, 0.5, "Empty Cell", 
                            ha='center', va='center', fontsize=10,
                            transform=ax.transAxes, alpha=0.5)
                    ax.axis('off')
        
        self.fig.tight_layout()
        self.canvas.draw()
        self.draw()
    
    def update_one_plot(self, subplot, win):
        plot_id, s_row, s_col, s_row_span, s_col_span, data_series, axes_info, title_info, legend_info, lines = subplot
        ax: Axes = self.axes[plot_id]
        ax.clear()
    
        # Plot all series
        for series in data_series:
            if series['x'] != "None" and series['y'] != "None":
                if series['xerr'] != "None" or series['yerr'] != "None":
                    data = win.get_error_data(x=series['x'], y=series['y'], xerr=series['xerr'], yerr=series['yerr'])
                    ax.errorbar(x=data[0], y=data[2],xerr=data[1], yerr=data[3],
                        linewidth=series['width'], 
                        color=series['color'],
                        label=series['label'], 
                        ls=series["ls"],
                        alpha=series["alpha"],
                        marker=series["marker"],
                        markersize=series["marker size"])
                else:
                    data = win.get_data(series['x'], series['y'])
                    ax.plot(data[0], data[1], 
                            linewidth=series['width'], 
                            color=series['color'],
                            label=series['label'], 
                            ls=series["ls"],
                            alpha=series["alpha"],
                            marker=series["marker"],
                            markersize=series["marker size"])
    
        ax.set_title(title_info["title"], fontsize=title_info["title fs"])
        if axes_info["show grid"]:
            #ax.grid(True, linestyle='--', alpha=0.7)
            ax.grid(color="#7a7c7d", linewidth=0.3)
            ax.grid(which='minor', color='#7a7c7d', linestyle=':', linewidth=0.2)
        else:
            # ax.text(0.5, 0.5, f"Subplot {plot_id}", 
            #         ha='center', va='center', fontsize=12,
            #         transform=ax.transAxes)
            ax.grid(visible=False)
            pass

        ax.minorticks_on()
        

        #local functions for rounding labels
        def zero_formatter_x(x, pos, acc=axes_info["x number of accuracy"]):
            rounded_x = round(x, acc)
            if abs(rounded_x) < 1e-8:
                return "0" 
            else:
                return f"{x:.{acc}f}"
    
        def zero_formatter_y(y, pos, acc=axes_info["y number of accuracy"]):
            rounded_y = round(y, acc)
            if abs(rounded_y) < 1e-8:
                return "0" 
            else:
                return f"{y:.{acc}f}"
            
        #set x axis
        ax.set_xlabel(axes_info["x-label"], loc="center", fontsize=axes_info["x label fs"])
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(zero_formatter_x))
        ax.xaxis.set_ticks_position("bottom")
        ax.tick_params(axis='x', length=4, width=2, labelsize=axes_info["x label fs"], direction ='in')
        if not axes_info["x scale"]:
            ax.tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black')
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(axes_info["x small ticks"]))
        else:
            ax.set_xscale("log")
        ax.set_xlim(axes_info["x min"], axes_info["x max"])
        ax.spines["left"].set_position(("data", axes_info["x min"]))
        ax.set_xticks(np.linspace(axes_info["x min"], axes_info["x max"], axes_info["x ticks"]))

        #set y axis
        ax.set_ylabel(axes_info["y-label"], loc="center", fontsize=axes_info["y label fs"])
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(zero_formatter_y))        
        ax.yaxis.set_ticks_position("left")
        ax.tick_params(axis='y', length=4, width=2, labelsize=axes_info["y label fs"], direction ='in')
        if not axes_info["y scale"]:
            ax.tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black')
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(axes_info["y small ticks"]))
        else:
            ax.set_yscale("log")
        ax.set_ylim(axes_info["y min"], axes_info["y max"])
        ax.spines["bottom"].set_position(("data", axes_info["y min"]))
        ax.set_yticks(np.linspace(axes_info["y min"], axes_info["y max"], axes_info["y ticks"]))
        
        #set legend
        ax.legend(loc=legend_info["legend position"], frameon=False, prop={"size": legend_info["legend fs"]})

        #draw lines
        for line in lines:
            self.draw_line(line, ax)

        return ax

    def draw_line(self, params, ax=None):
        """Draws a line on the graph"""
        if not ax:
            ax = self.figure.gca()
        
        # Calculate the coordinates depending on the type
        if params['type'] == 0:  # Two points
            x = [params['x1'], params['x2']]
            y = [params['y1'], params['y2']]
        elif params['type'] == 1:  # equation
            x_min, x_max = ax.get_xlim()
            x = [x_min, x_max]
            y = [params['k'] * x_min + params['b'], params['k'] * x_max + params['b']]
        else:  # point and angle
            rad = params['angle']
            k = np.tan(rad)
            x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
            length = x_range * 0.5
            dx = length * np.cos(rad)
            dy = length * np.sin(rad)
            x = [params['px'] - dx, params['px'] + dx]
            y = [params['py'] - dy, params['py'] + dy]
        
        # draw line
        line = ax.plot(x, y, 
                color=params['color'], 
                linewidth=params['width'], 
                linestyle=params['style'])
        
        # add labels to lines
        print(params)
        if 'label' in params and params['label']:
            self.add_line_label(ax, line, params)

        self.canvas.draw()
        self.draw()

    def add_line_label(self, ax, line, params):
        """Add label to line."""

        # Define label position
        position = params.get('label_position', 'Above the middle of the line')
        fontsize = params.get('label_font_size', 10)
        
        # choordinates of start, end and middle of the line
        x0, y0 = params['x1'], params['y1']
        x1, y1 = params['x2'], params['y2']
        x_mid = (x0 + x1) / 2
        y_mid = (y0 + y1) / 2
        
        # shift for label
        offset_y = 0
        offset_x = 0
        
        # define choordinates for label
        if position == "Above the beginning of the line":
            x, y = x0, y0
            ha = 'center'
            va = 'bottom'
            y += offset_y
        elif position == "Above the middle of the line":
            x, y = x_mid, y_mid
            ha = 'center'
            va = 'bottom'
            y += offset_y
        elif position == "Above the end of the line":
            x, y = x1, y1
            ha = 'center'
            va = 'bottom'
            y += offset_y
        elif position == "Under the beginning of the line":
            x, y = x0, y0
            ha = 'center'
            va = 'top'
            y -= offset_y
        elif position == "Under the middle of the line":
            x, y = x_mid, y_mid
            ha = 'center'
            va = 'top'
            y -= offset_y
        elif position == "Under the end of the line":
            x, y = x1, y1
            ha = 'center'
            va = 'top'
            y -= offset_y
        elif position == "To the left of the beginning":
            x, y = x0, y0
            ha = 'right'
            va = 'center'
            x -= offset_y
        elif position == "To the left of the middle":
            x, y = x_mid, y_mid
            ha = 'right'
            va = 'center'
            x -= offset_x
        elif position == "To the left of the end":
            x, y = x1, y1
            ha = 'right'
            va = 'center'
            x -= offset_x
        elif position == "To the right of the beginning":
            x, y = x0, y0
            ha = 'left'
            va = 'center'
            x += offset_x
        elif position == "To the right of the middle":
            x, y = x_mid, y_mid
            ha = 'left'
            va = 'center'
            x += offset_x
        else:  # "To the right of the end"
            x, y = x1, y1
            ha = 'left'
            va = 'center'
            x += offset_x
        print(x, y, params['label'])
        # add label
        ax.text(x, y, params['label'], 
                fontsize=fontsize, 
                color=params['color'],
                horizontalalignment=ha,
                verticalalignment=va,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))