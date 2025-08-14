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
        plot_id, s_row, s_col, s_row_span, s_col_span, data_series, axes_info, title_info, legend_info = subplot
        ax: Axes = self.axes[plot_id]
        ax.clear()
    
        # Plot all series
        for series in data_series:
            if series['x'] != "None" and series['y'] != "None":
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
            pass

        ax.minorticks_on()
        
        #set x axis
        ax.set_xlabel(axes_info["x-label"], loc="center", fontsize=axes_info["x label fs"])
        self.number_of_accuracy_x = axes_info["x number of accuracy"]
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.__zero_formatter_x))
        ax.xaxis.set_ticks_position("bottom")
        ax.tick_params(axis='x', length=4, width=2, labelsize=axes_info["x label fs"], direction ='in')
        if not axes_info["x scale"]:
            ax.tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black')
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(axes_info["x small ticks"]))
        ax.set_xlim(axes_info["x min"], axes_info["x max"])
        ax.spines["left"].set_position(("data", axes_info["x min"]))
        ax.set_xticks(np.linspace(axes_info["x min"], axes_info["x max"], axes_info["x ticks"]))

        #set y axis
        ax.set_ylabel(axes_info["y-label"], loc="center", fontsize=axes_info["y label fs"])
        self.number_of_accuracy_y = axes_info["y number of accuracy"]
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(self.__zero_formatter_y))
        ax.yaxis.set_ticks_position("left")
        ax.tick_params(axis='y', length=4, width=2, labelsize=axes_info["y label fs"], direction ='in')
        if not axes_info["y scale"]:
            ax.tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black')
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(axes_info["y small ticks"]))
        ax.set_ylim(axes_info["y min"], axes_info["y max"])
        ax.spines["bottom"].set_position(("data", axes_info["y min"]))
        ax.set_yticks(np.linspace(axes_info["y min"], axes_info["y max"], axes_info["y ticks"]))
        
        #set legend
        ax.legend(loc=legend_info["legend position"], frameon=False, prop={"size": legend_info["legend fs"]})


        return ax

    def __zero_formatter_x(self, x, pos):
        """
        Format numerical values for axis label with zero approximation handling.

        Provides clean numerical formatting by:
        1. Rounding values to a specified decimal precision
        2. Replacing near-zero values with exact "0" string
        3. Maintaining standard decimal formatting for other values

        Arguments:
        ----------
        x : float
            The raw numerical value to be formatted
        pos : int
            Position parameter (required by matplotlib formatter API, not used here)

        Returns:
        -------
        str
            Formatted string representation of the value:
            - "0" for values near zero after rounding
            - Standard decimal format otherwise

        Notes:
        ------
        - Uses `self.number_of_accuracy` to determine decimal places
        - Considers values with absolute magnitude < 1e-8 as effectively zero
        - Implements rounding before zero-check for accurate representation
        - Designed for use with matplotlib tick formatting (hence unused pos parameter)

        Example:
        --------
        With number_of_accuracy = 2:
        - 0.00000004 → "0"
        - 1.23456789 → "1.23"
        - -0.0000001 → "0"
        - 3.14159265 → "3.14"

        Inspiration:
        ------------
        nothing
        """
        # Round the value to 2 decimal places first
        rounded_x = round(x, self.number_of_accuracy_x)
        # Check if the rounded value is effectively zero
        if abs(rounded_x) < 1e-8:
            return "0" 
        else:
            return f"{x:.{self.number_of_accuracy_x}f}"

    def __zero_formatter_y(self, y, pos):
        """
        Format numerical values for axis label with zero approximation handling.

        Provides clean numerical formatting by:
        1. Rounding values to a specified decimal precision
        2. Replacing near-zero values with exact "0" string
        3. Maintaining standard decimal formatting for other values

        Arguments:
        ----------
        x : float
            The raw numerical value to be formatted
        pos : int
            Position parameter (required by matplotlib formatter API, not used here)

        Returns:
        -------
        str
            Formatted string representation of the value:
            - "0" for values near zero after rounding
            - Standard decimal format otherwise

        Notes:
        ------
        - Uses `self.number_of_accuracy` to determine decimal places
        - Considers values with absolute magnitude < 1e-8 as effectively zero
        - Implements rounding before zero-check for accurate representation
        - Designed for use with matplotlib tick formatting (hence unused pos parameter)

        Example:
        --------
        With number_of_accuracy = 2:
        - 0.00000004 → "0"
        - 1.23456789 → "1.23"
        - -0.0000001 → "0"
        - 3.14159265 → "3.14"

        Inspiration:
        ------------
        nothing
        """
        # Round the value to 2 decimal places first
        rounded_y = round(y, self.number_of_accuracy_y)
        # Check if the rounded value is effectively zero
        if abs(rounded_y) < 1e-8:
            return "0" 
        else:
            return f"{y:.{self.number_of_accuracy_y}f}"